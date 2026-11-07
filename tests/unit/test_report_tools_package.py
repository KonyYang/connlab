"""Portable Tools results are recomputed from their retained source bytes."""
from io import BytesIO
import json
from zipfile import ZipFile, ZIP_DEFLATED

import pytest

from backend.api.temperature_schemas import DownloadTemperatureRequest
from backend.application.report_tools_package import ReportToolsPackage
from backend.application.tools_temperature_service import ToolsTemperatureService
from backend.infrastructure.files.mechanical_summary_folder import analyze_folder
from backend.infrastructure.office.temperature_workbook_gateway import TemperatureWorkbookGateway


def service():
    return ReportToolsPackage(
        ToolsTemperatureService(TemperatureWorkbookGateway()), analyze_folder,
        temperature_request_validator=lambda value: DownloadTemperatureRequest.model_validate(value).model_dump(),
    )


def temperature_input():
    raw = b'Current,Ambient,S1,S2\n100,20,25,26\n100,20,26,27\n200,20,40,42\n200,20,42,44\n'
    table = service().temperature.import_workbook(raw, 'scanner.csv').table
    from dataclasses import asdict
    request = {'table': asdict(table), 'selection': {'header_row': 1, 'start_row': 2, 'end_row': 5,
        'ambient_column': 2, 'current_column': 1, 'temperature_columns': [3, 4],
        'thermocouples_per_sample': 1}, 'zero_intercept': True, 'acknowledge_warnings': True,
        'maximum_coefficients': {'a': 0.0005, 'b': 0.01, 'c': 0},
        'report_metadata': {'ltr_number': 'DL-2026-09-032'}}
    return raw, request


def test_temperature_package_preserves_raw_source_and_effective_coefficients_without_changing_fit():
    source, request = temperature_input()
    name, content = service().export_temperature(source, 'scanner.csv', request)
    result = service().inspect(content)
    assert name.endswith('_ReportResults.zip')
    assert result['sources'][0]['content'] == source
    assert result['project_hint'] == 'DL-2026-09-032'
    entry = result['entries'][0]
    assert entry['supported_for_report'] is True
    assert entry['data']['analysis']['points'][-1]['maximum'] == 24
    assert entry['data']['effective_maximum_coefficients'] == {'a': 0.0005, 'b': 0.01, 'c': 0}
    assert entry['data']['analysis']['maximum_fit']['fitted_coefficients'] != entry['data']['effective_maximum_coefficients']
    assert entry['data']['raw_rows'][-1]['source_row'] == 5


def test_temperature_export_rejects_table_values_that_no_longer_match_source():
    source, request = temperature_input()
    request['table']['rows'] = [list(row) for row in request['table']['rows']]
    request['table']['rows'][-1][-1] = 999
    with pytest.raises(ValueError, match='source'):
        service().export_temperature(source, 'scanner.csv', request)


def test_temperature_source_comparison_accepts_browser_json_number_normalization():
    from openpyxl import Workbook
    from dataclasses import asdict
    book = Workbook()
    for row in [['Current', 'Ambient', 'S1', 'S2'], [100, 20, 25, 26], [100, 20, 26, 27],
                [200, 20, 40, 42], [200, 20, 42, 44]]:
        book.active.append(row)
    stream = BytesIO(); book.save(stream); book.close()
    source = stream.getvalue()
    _, request = temperature_input()
    request['table'] = asdict(service().temperature.workbook.read_upload(source, 'scanner.xlsx'))
    request['table']['rows'] = [[float(v) if isinstance(v, int) else v for v in row] for row in request['table']['rows']]
    _, content = service().export_temperature(source, 'scanner.xlsx', request)
    assert service().inspect(content)['entries'][0]['data']['analysis']['points'][-1]['maximum'] == 24


def test_temperature_package_reuses_existing_import_filename_normalization():
    from dataclasses import asdict
    source, request = temperature_input()
    name = 'long-scanner-name-' * 10 + '.csv'
    request['table'] = asdict(service().temperature.import_workbook(source, name).table)
    _, content = service().export_temperature(source, name, request)
    imported = service().inspect(content)
    assert imported['sources'][0]['name'] == name
    assert imported['entries'][0]['data']['analysis']['points'][-1]['maximum'] == 24


def instrument_pdf(lines):
    from reportlab.pdfgen.canvas import Canvas
    stream = BytesIO()
    canvas = Canvas(stream)
    for index, line in enumerate(lines):
        canvas.drawString(35, 790 - index * 18, line)
    canvas.save()
    return stream.getvalue()


def workbook_bytes(*_args):
    # Native Excel is an external rendering boundary; no Office process in unit tests.
    from openpyxl import Workbook
    book = Workbook()
    book.active['A1'] = 'Isolated Summary'
    stream = BytesIO()
    book.save(stream)
    book.close()
    return stream.getvalue()


def test_mechanical_package_reparses_signed_withdrawal_and_keeps_explicit_magnitude_decision():
    raw = instrument_pdf(['DL-2026-09-032', 'MF UMF Fmax', '72 1 107 -310 107 15.2', '73 1 109 -330 109 16.2'])
    files = [('Test results/mating.pdf', raw)]
    analysis = analyze_folder(files)
    section = analysis['sections'][0]
    review = {'project': analysis['project'], 'sections': {section['id']: {
        'rows': [{'curve': '72', 'sample': '#1', 'colour': 'Orange', 'part': ''},
                 {'curve': '73', 'sample': '#1', 'colour': 'Black', 'part': ''}],
        'withdraw_magnitude': True}}}
    package = service()
    package.mechanical_renderer = workbook_bytes
    _, zipped = package.export_mechanical(files, review)
    imported = package.inspect(zipped)
    withdraw = next(entry for entry in imported['entries'] if entry['data'].get('test_type') == 'unmating')
    assert withdraw['data']['rows'][0]['raw_value'] == '-310.0'
    assert withdraw['data']['rows'][0]['value'] == '310.0'
    assert withdraw['data']['rows'][1]['color'] == 'Black'
    assert withdraw['data']['summary']['average'] == '320.0'
    assert withdraw['data']['withdraw_magnitude'] is True
    assert imported['sources'][0]['content'] == raw


def test_mechanical_package_retains_only_actual_sources_not_ignored_reference_files():
    raw = instrument_pdf(['DL-2026-09-032', 'Retention Force', 'Fmax', '1 #1 2890 11.6'])
    files = [('Test results/retention.pdf', raw), ('History/private.xlsx', workbook_bytes())]
    package = service(); package.mechanical_renderer = workbook_bytes
    _, content = package.export_mechanical(files, None)
    assert [item['name'] for item in package.inspect(content)['sources']] == ['Test results/retention.pdf']


def test_qualitative_package_keeps_explicit_matrix_without_fake_numeric_application():
    from openpyxl import Workbook
    book = Workbook(); sheet = book.active
    for name, value in {'D8': 'Max', 'D9': '[N]', 'A13': '1', 'D13': '105.13'}.items():
        sheet[name] = value
    stream = BytesIO(); book.save(stream); book.close()
    files = [('DL-2026-09-032 polarisation.xlsx', stream.getvalue())]
    analysis = analyze_folder(files); section = analysis['sections'][0]
    table = {'title': 'Polarisation', 'row_heading': 'Receptacle', 'column_heading': 'Header',
        'columns': ['#1'], 'samples': ['#1'], 'results': [['Pass']], 'diagonal': True, 'curves': ['1']}
    review = {'project': analysis['project'], 'sections': {section['id']: {'tables': [table], 'qualitative_confirmed': True}}}
    package = service(); package.mechanical_renderer = workbook_bytes
    _, content = package.export_mechanical(files, review)
    entry = package.inspect(content)['entries'][0]
    assert entry['supported_for_report'] is True
    assert entry['kind'] == 'mechanical_qualitative'
    assert entry['data']['tables'][0]['results'] == [['Pass']]
    assert 'summary' not in entry['data']


@pytest.mark.parametrize('condition,supported', [('240 N for 6 seconds', True), ('Not recorded', False)])
def test_hold_duration_is_explicit_and_not_guessed_from_filename(condition, supported):
    raw = instrument_pdf(['DL-2026-09-032', 'Retention Force End section', '1.20 #1 240 246 245 6.0'])
    files = [('DL-2026-09-032 hold 6sec.pdf', raw)]
    analysis = analyze_folder(files); section = analysis['sections'][0]
    review = {'project': analysis['project'], 'sections': {section['id']: {
        'force_field': 'FEnd section', 'information': {'Test Condition': condition}}}}
    package = service(); package.mechanical_renderer = workbook_bytes
    _, content = package.export_mechanical(files, review)
    entry = package.inspect(content)['entries'][0]
    assert entry['supported_for_report'] is supported
    assert entry['data']['rows'][0]['value'] == '240.0'
    assert entry['data']['rows'][0]['hold_seconds'] == ('6' if supported else '')


def rewrite_package(content, transform):
    with ZipFile(BytesIO(content)) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    transform(entries)
    stream = BytesIO()
    with ZipFile(stream, 'w', ZIP_DEFLATED) as archive:
        for name, raw in entries.items():
            archive.writestr(name, raw)
    return stream.getvalue()


@pytest.mark.parametrize('target', ['source', 'summary', 'path', 'version', 'profile', 'projection'])
def test_package_rejects_changed_bytes_unsafe_entries_and_untrusted_projection(target):
    source, request = temperature_input()
    _, zipped = service().export_temperature(source, 'scanner.csv', request)
    def change(entries):
        manifest = json.loads(entries['manifest.json'])
        if target in {'source', 'summary'}:
            record = manifest['sources'][0] if target == 'source' else manifest['summary']
            entries[record['entry']] += b'changed'
        elif target == 'path':
            entries['../outside'] = b'no'
        elif target == 'version':
            manifest['version'] = 2
        elif target == 'profile':
            manifest['profile_version'] = 'temperature.v99'
        else:
            manifest['results'] = [{'maximum': 999}]
        entries['manifest.json'] = json.dumps(manifest).encode()
    with pytest.raises(ValueError):
        service().inspect(rewrite_package(zipped, change))


@pytest.mark.parametrize('target', ['duplicate', 'link', 'oversized', 'duplicate_metadata'])
def test_package_refuses_ambiguous_or_unbounded_container_entries(target):
    from zipfile import ZipInfo
    source, request = temperature_input()
    _, zipped = service().export_temperature(source, 'scanner.csv', request)
    with ZipFile(BytesIO(zipped)) as archive:
        entries = {item.filename: archive.read(item) for item in archive.infolist()}
    if target == 'duplicate_metadata':
        entries['manifest.json'] = b'{"format":"connlab.report-results","format":"other"}'
    stream = BytesIO()
    with ZipFile(stream, 'w', ZIP_DEFLATED) as archive:
        for name, raw in entries.items():
            info = ZipInfo(name)
            if target == 'link' and name == 'manifest.json':
                info.create_system = 3; info.external_attr = 0o120777 << 16
            archive.writestr(info, raw)
        if target == 'duplicate':
            with pytest.warns(UserWarning):
                archive.writestr('manifest.json', entries['manifest.json'])
        if target == 'oversized':
            for index in range(201):
                archive.writestr(f'extra{index}.txt', b'x')
    with pytest.raises(ValueError):
        service().inspect(stream.getvalue())
