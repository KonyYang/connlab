"""Portable Tools evidence: retained bytes and decisions, never trusted result numbers.

Workbook/PDF IO and Office rendering are injected. Import never starts Office or
writes a project file; the caller owns report mapping and its existing revision.
"""
from dataclasses import asdict
from decimal import Decimal
from hashlib import sha256
from io import BytesIO
import json
from pathlib import PurePosixPath
import re
import zlib
from zipfile import BadZipFile, ZipFile, ZIP_DEFLATED

from backend.application.tools_temperature_service import DeratingParameters, safe_workbook_name
from backend.application.mechanical_summary_folder import apply_review
from backend.domain.temperature_data import DataSelection
from backend.domain.temperature_rise import Coefficients


FORMAT = 'connlab.report-results'
MAX_SOURCE = 25 * 1024 * 1024
MAX_TOTAL = 220 * 1024 * 1024
MAX_MANIFEST = 8 * 1024 * 1024


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def _load_json(content):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate package metadata fields.')
            result[key] = value
        return result
    def constant(_value):
        raise ValueError('Package numbers must be finite.')
    try:
        return json.loads(content, object_pairs_hook=pairs, parse_constant=constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError('The report result package metadata is unreadable.') from exc


def _keys(value, fields):
    if not isinstance(value, dict) or set(value) != set(fields):
        raise ValueError('Unsupported report result package fields.')


def _relative_name(name):
    if not isinstance(name, str) or not 1 <= len(name) <= 1000:
        raise ValueError('Invalid package source name.')
    name = name.replace('\\', '/')
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in {'', '.', '..'} for part in name.split('/')) or re.search(r'[:\x00-\x1f]', name):
        raise ValueError('Package names must be safe relative paths.')
    return name


def _selection(value):
    return DataSelection(**{**value, 'temperature_columns': tuple(value['temperature_columns']),
        'excluded_rows': tuple(value.get('excluded_rows', [])),
        'sample_groups': tuple(tuple(group) for group in value['sample_groups']) if value.get('sample_groups') else None,
        'channel_names': tuple((int(key), label) for key, label in value.get('channel_names', {}).items())})


def _same_table(supplied, actual):
    """JSON may render 100.0 as 100, but booleans and edited cells are not readings."""
    if not isinstance(supplied, dict) or set(supplied) != {'file_name', 'sheet_names', 'sheet_name', 'rows'}:
        return False
    if any(supplied[key] != getattr(actual, key) for key in ('file_name', 'sheet_name')):
        return False
    if supplied['sheet_names'] not in (list(actual.sheet_names), actual.sheet_names):
        return False
    rows = supplied['rows']
    if not isinstance(rows, (list, tuple)) or len(rows) != len(actual.rows):
        return False
    for selected, source in zip(rows, actual.rows):
        if not isinstance(selected, (list, tuple)) or len(selected) != len(source):
            return False
        for left, right in zip(selected, source):
            if left != right or (isinstance(left, bool) != isinstance(right, bool)):
                return False
    return True


def _mechanical_entries(analysis):
    entries = []
    for section in analysis['sections']:
        kind = section['kind']
        qualitative = kind in {'polarisation', 'protection'}
        measurements = ('qualitative',) if qualitative else ('mating', 'withdraw') if kind == 'mating' else ('value',)
        for field in measurements:
            identity = sha256(f'{section["id"]}:{field}'.encode()).hexdigest()[:24]
            entry = {'entry_id': identity, 'label': section['name'] + (f' — {field}' if kind == 'mating' else ''),
                'kind': 'mechanical_qualitative' if qualitative else 'mechanical',
                'supported_for_report': not qualitative,
                'reason': 'Qualitative matrices are retained as evidence; report application needs a supported mapping.' if qualitative else '',
                'source_names': [section['source']]}
            if qualitative:
                entry['data'] = {'tables': section['tables'], 'raw_cells': section['raw_cells'],
                    'raw_curves': section['raw_curves'], 'information': section['information']}
                entries.append(entry)
                continue
            hold = kind in {'hold', 'hold_end1', 'clamp'}
            duration = re.findall(r'(?<![\d.])(\d+(?:\.\d+)?)\s*(?:seconds?|secs?|s)\b',
                section['information'].get('Test Condition', ''), re.I) if hold else []
            duration = duration[0] if len(set(duration)) == 1 and Decimal(duration[0]) > 0 else None
            if hold and duration is None:
                entry.update(supported_for_report=False,
                    reason='The hold force is retained, but its duration needs an explicit Test Condition in seconds.')
            rows, values = [], []
            for source_row in section['rows']:
                raw = Decimal(str(source_row[field]))
                if not raw.is_finite():
                    raise ValueError('Mechanical source measurements must be finite.')
                value = abs(raw) if field == 'withdraw' and section['withdraw_magnitude'] else raw
                row = {'sample_id': source_row['sample'], 'record_id': source_row['curve'],
                    'color': source_row['colour'], 'part': source_row['part'],
                    'value': str(value), 'raw_value': str(raw), 'unit': 'N',
                    'source_locator': f'{section["source"]} / curve {source_row["curve"]} / {field}'}
                if hold:
                    row['hold_seconds'] = duration or ''
                rows.append(row)
                values.append(value)
            mean = sum(values) / len(values)
            stdev = (sum((value - mean) ** 2 for value in values) / (len(values) - 1)).sqrt() if len(values) > 1 else None
            entry['data'] = {'rows': rows, 'unit': 'N', 'quantity': 'hold' if hold else 'peak',
                'test_type': ('unmating' if field == 'withdraw' else field) if kind == 'mating' else 'clamp' if kind == 'clamp' else 'retention',
                'force_field': section.get('force_field', ''),
                'withdraw_magnitude': section.get('withdraw_magnitude', False), 'information': section['information'],
                'summary': {'min': str(min(values)), 'max': str(max(values)), 'average': str(mean),
                            'stdev': str(stdev) if stdev is not None else None}}
            entries.append(entry)
    return entries


class ReportToolsPackage:
    """Export and inspect the two supported Tools result families."""

    def __init__(self, temperature_service, mechanical_analyzer, mechanical_renderer=None,
                 temperature_request_validator=None):
        self.temperature = temperature_service
        self.mechanical_analyzer = mechanical_analyzer
        self.mechanical_renderer = mechanical_renderer
        self.temperature_request_validator = temperature_request_validator

    def _temperature_data(self, source, name, request, *, check_table=False):
        if not isinstance(request, dict) or self.temperature_request_validator is None:
            raise ValueError('The temperature package reader is unavailable.')
        review = dict(request)
        supplied = review.pop('table', None)
        sheet_name = supplied.get('sheet_name') if isinstance(supplied, dict) else review.pop('source_sheet', None)
        table = self.temperature.workbook.read_upload(source, safe_workbook_name(name), sheet_name=sheet_name)
        normalized = self.temperature_request_validator({'table': asdict(table), **review})
        if check_table and not _same_table(supplied, table):
            raise ValueError('Temperature table no longer matches its original source. Import the source again.')
        selection = _selection(normalized['selection'])
        analysis = self.temperature.analyze(table, selection, zero_intercept=normalized['zero_intercept'],
            acknowledge_warnings=normalized['acknowledge_warnings'])
        maximum = normalized.get('maximum_coefficients') or asdict(analysis.maximum_fit.coefficients)
        average = normalized.get('average_coefficients') or asdict(analysis.average_fit.coefficients)
        if normalized['zero_intercept'] and (maximum['c'] != 0 or average['c'] != 0):
            raise ValueError('Zero Intercept requires both c coefficients to be zero.')
        data = {'sheet_name': table.sheet_name, 'analysis': asdict(analysis),
            'raw_rows': [{'source_row': index, 'values': list(table.rows[index - 1])}
                for index in range(selection.start_row, selection.end_row + 1) if index not in selection.excluded_rows],
            'selection': normalized['selection'], 'sample_ids': [], 'unit': '°C', 'quantity': 'measured_temperature_rise',
            'effective_maximum_coefficients': maximum, 'effective_average_coefficients': average,
            'report_metadata': normalized['report_metadata'], 'target_rise': normalized.get('target_rise'),
            'derating': normalized.get('derating')}
        retained = {key: value for key, value in normalized.items() if key != 'table'}
        retained['source_sheet'] = table.sheet_name
        return table, selection, normalized, retained, data

    def export_temperature(self, source: bytes, name: str, request: dict) -> tuple[str, bytes]:
        name = _relative_name(name)
        if not source or len(source) > MAX_SOURCE:
            raise ValueError('Select a nonempty temperature source smaller than 25 MB.')
        table, selection, normalized, review, _ = self._temperature_data(source, name, request, check_table=True)
        from backend.application.temperature_report_metadata import TemperatureReportMetadata
        output_name, summary = self.temperature.download(table, selection,
            zero_intercept=normalized['zero_intercept'], acknowledge_warnings=normalized['acknowledge_warnings'],
            maximum_coefficients=Coefficients(**normalized['maximum_coefficients']) if normalized.get('maximum_coefficients') else None,
            average_coefficients=Coefficients(**normalized['average_coefficients']) if normalized.get('average_coefficients') else None,
            target_rise=normalized.get('target_rise'),
            derating_parameters=DeratingParameters(**normalized['derating']) if normalized.get('derating') else None,
            report_metadata=TemperatureReportMetadata(**normalized['report_metadata']))
        project = normalized['report_metadata'].get('ltr_number', '').strip()
        content = self._pack('temperature', [(name, source)], output_name, summary, review, project)
        return PurePosixPath(safe_workbook_name(name)).stem + '_ReportResults.zip', content

    def export_mechanical(self, files: list[tuple[str, bytes]], review: dict | None) -> tuple[str, bytes]:
        analysis = apply_review(self.mechanical_analyzer(files), review)
        if not analysis['ready']:
            raise ValueError('Complete the unresolved mechanical source mappings before exporting.')
        if self.mechanical_renderer is None:
            raise ValueError('The mechanical workbook renderer is unavailable.')
        _mechanical_entries(analysis)
        summary = self.mechanical_renderer(files, analysis)
        prefix = analysis['project'] + ' ' if analysis['project'] else ''
        used = {section['source'] for section in analysis['sections']}
        retained = [(name, raw) for name, raw in files if name in used]
        content = self._pack('mechanical', retained, prefix + 'Mechanical Force Summary.xlsx', summary,
            review, analysis['project'])
        return prefix + 'Mechanical_ReportResults.zip', content

    @staticmethod
    def _pack(kind, sources, summary_name, summary, review, project):
        if not 1 <= len(sources) <= 200 or not summary or len(summary) > 60 * 1024 * 1024:
            raise ValueError('Report result package exceeds its file limits.')
        entries = {}
        records = []
        names = set()
        for index, (name, content) in enumerate(sources, 1):
            name = _relative_name(name)
            if name.casefold() in names or not content or len(content) > MAX_SOURCE:
                raise ValueError('Package sources must be unique, nonempty and smaller than 25 MB.')
            names.add(name.casefold())
            entry = f'sources/{index:04d}/{PurePosixPath(name).name}'
            entries[entry] = content
            records.append({'name': name, 'entry': entry, 'sha256': sha256(content).hexdigest(), 'size': len(content)})
        summary_entry = 'summary/' + PurePosixPath(_relative_name(summary_name)).name
        entries[summary_entry] = summary
        manifest = {'format': FORMAT, 'version': 1, 'kind': kind, 'profile_version': f'{kind}.v1', 'project_hint': project,
            'sources': records, 'summary': {'name': PurePosixPath(summary_entry).name, 'entry': summary_entry,
                'sha256': sha256(summary).hexdigest(), 'size': len(summary)}, 'review': review}
        entries['manifest.json'] = _json(manifest)
        if len(entries['manifest.json']) > MAX_MANIFEST or sum(map(len, entries.values())) > MAX_TOTAL:
            raise ValueError('Report result package is too large.')
        stream = BytesIO()
        with ZipFile(stream, 'w', ZIP_DEFLATED) as archive:
            for path, content in entries.items():
                archive.writestr(path, content)
        return stream.getvalue()

    @staticmethod
    def _unpack(content):
        if not content or len(content) > MAX_TOTAL:
            raise ValueError('Select a supported report result package smaller than 220 MB.')
        try:
            with ZipFile(BytesIO(content)) as archive:
                infos = archive.infolist()
                if not 3 <= len(infos) <= 202 or sum(item.file_size for item in infos) > MAX_TOTAL:
                    raise ValueError('Expanded report result package exceeds its limits.')
                names = [_relative_name(item.filename) for item in infos]
                if len({name.casefold() for name in names}) != len(names) or 'manifest.json' not in names:
                    raise ValueError('Duplicate or missing package entries.')
                if any(item.is_dir() or item.flag_bits & 1 or (item.external_attr >> 16) & 0o170000 == 0o120000 for item in infos):
                    raise ValueError('Package directories, links and encryption are not supported.')
                if archive.getinfo('manifest.json').file_size > MAX_MANIFEST:
                    raise ValueError('Package metadata exceeds its limit.')
                manifest = _load_json(archive.read('manifest.json'))
                _keys(manifest, {'format', 'version', 'kind', 'profile_version', 'project_hint', 'sources', 'summary', 'review'})
                if manifest['format'] != FORMAT or type(manifest['version']) is not int or manifest['version'] != 1:
                    raise ValueError('Unsupported report result package version.')
                if manifest['kind'] not in {'temperature', 'mechanical'} or not isinstance(manifest['project_hint'], str):
                    raise ValueError('Unsupported report result package kind.')
                if manifest['profile_version'] != f'{manifest["kind"]}.v1':
                    raise ValueError('Unsupported report result parser profile. Re-export using a compatible Tools version.')
                if not isinstance(manifest['sources'], list) or not 1 <= len(manifest['sources']) <= 200:
                    raise ValueError('Package sources are missing or exceed their limit.')
                expected = {'manifest.json'}
                retained = []
                source_names = set()
                for index, record in enumerate([*manifest['sources'], manifest['summary']]):
                    _keys(record, {'name', 'entry', 'sha256', 'size'})
                    name, entry = _relative_name(record['name']), _relative_name(record['entry'])
                    source = index < len(manifest['sources'])
                    prefix = 'sources/' if source else 'summary/'
                    limit = MAX_SOURCE if source else 60 * 1024 * 1024
                    if not entry.startswith(prefix) or entry in expected or entry not in names:
                        raise ValueError('Package entry identity does not match its manifest.')
                    if source and name.casefold() in source_names:
                        raise ValueError('Duplicate package source names.')
                    source_names.add(name.casefold())
                    if type(record['size']) is not int or not 0 < record['size'] <= limit or archive.getinfo(entry).file_size != record['size']:
                        raise ValueError('Package file size does not match its manifest.')
                    if not isinstance(record['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', record['sha256']):
                        raise ValueError('Invalid package file fingerprint.')
                    raw = archive.read(entry)
                    if sha256(raw).hexdigest() != record['sha256']:
                        raise ValueError('Package source or summary changed. Export it again after review.')
                    expected.add(entry)
                    retained.append({'name': name, 'content': raw, 'sha256': record['sha256']})
                if expected != set(names) or not retained[-1]['name'].lower().endswith('.xlsx'):
                    raise ValueError('Unexpected package content or summary format.')
                return manifest, retained[:-1], retained[-1]
        except (BadZipFile, KeyError, RuntimeError, NotImplementedError, EOFError, zlib.error) as exc:
            raise ValueError('The report result package is unreadable or incomplete.') from exc

    def inspect(self, content: bytes) -> dict:
        manifest, sources, summary = self._unpack(content)
        if manifest['kind'] == 'temperature':
            if len(sources) != 1 or not isinstance(manifest['review'], dict) or 'table' in manifest['review']:
                raise ValueError('Invalid temperature package review.')
            _, _, normalized, _, data = self._temperature_data(sources[0]['content'], sources[0]['name'], manifest['review'])
            project = normalized['report_metadata'].get('ltr_number', '').strip()
            entries = [{'entry_id': 'temperature', 'label': 'Temperature rise', 'kind': 'temperature',
                'supported_for_report': True, 'reason': '', 'data': data, 'source_names': [sources[0]['name']]}]
        else:
            analysis = apply_review(self.mechanical_analyzer([(item['name'], item['content']) for item in sources]), manifest['review'])
            if not analysis['ready']:
                raise ValueError('Mechanical package source decisions no longer validate. Review the sources again.')
            project = analysis['project']
            entries = _mechanical_entries(analysis)
        if project != manifest['project_hint']:
            raise ValueError('Package project hint differs from its source review.')
        return {'kind': manifest['kind'], 'profile_version': manifest['profile_version'], 'project_hint': project, 'sources': sources,
            'summary': summary, 'entries': entries, 'review': manifest['review']}
