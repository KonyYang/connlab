from io import BytesIO
import pytest
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from backend.infrastructure.files.mechanical_summary_folder import analyze_folder


def pdf(lines):
    out = BytesIO()
    page = canvas.Canvas(out)
    for i, line in enumerate(lines):
        page.drawString(35, 790 - i * 18, line)
    page.save()
    return out.getvalue()


def test_folder_identifies_content_and_keeps_unknown_mating_mapping_unresolved():
    content = pdf(['LTR No : DL-2026-09-032', 'Test Date : 2026/09/22', 'Tester : Even',
                   'Temperature/humidity : 23C&46%RH', 'Test Group : Group Ab',
                   'Test Condition : 50mm/min', 'MF UMF Fmax', '72 1 107 -310 107 15.2'])
    result = analyze_folder([('Project/Test results/instrument.pdf', content),
                             ('Project/source/old.pdf', content),
                             ('Project/Mechanical Force Summary.xlsx', b'not an input')])
    assert len(result['sections']) == 1
    section = result['sections'][0]
    assert section['kind'] == 'mating'
    assert section['rows'] == [{'curve': '72', 'sample': '', 'colour': '', 'part': '', 'mating': 107.0, 'withdraw': -310.0}]
    assert section['information']['Test Date'] == '2026-09-22'
    assert section['information']['Tested By'] == 'Even'
    assert section['information']['Test Equipment ID'] == 'Not recorded'
    assert section['information']['Amb Temp. and Rel. Hum.'] == '23 °C / 46% RH'
    assert result['project'] == 'DL-2026-09-032'
    assert result['ready'] is False
    assert len(result['ignored']) == 2


def test_folder_retention_has_explicit_sample_and_does_not_copy_print_date():
    content = pdf(['Printed : 2026/11/06', 'DL-2026-09-031', 'Retention Force',
                   'Sample ID Fmax', '1 #1-Orange 2930 7.0', '2 #1-Black 2760 12.4'])
    result = analyze_folder([('DL-2026-09-031 retention.pdf', content)])
    section = result['sections'][0]
    assert section['rows'][0] == {'curve': '1', 'sample': '#1', 'colour': 'Orange', 'part': '', 'value': 2930.0}
    assert section['information']['Test Date'] == 'Not recorded'
    assert result['ready'] is True


def test_qualitative_keeps_only_effective_cells_and_never_infers_pass_from_force():
    book = Workbook()
    s = book.active
    for cell, value in {'A1': 'Company heading', 'A4': 'Operator:', 'A8': 'Specification',
                        'D8': 'Max', 'E8': 'Max', 'D9': '[N]', 'E9': '[mm]',
                        'A10': 'Upper', 'A11': 'Lower', 'A13': '1', 'D13': ' 105.13',
                        'E13': ' 12.627', 'A15': 'Maxi', 'D15': '105.13', 'E15': '12.627',
                        'A16': 'Cpk'}.items():
        s[cell] = value
    out = BytesIO(); book.save(out); book.close()
    result = analyze_folder([('DL-2026-09-031 polarisation.xlsx', out.getvalue())])
    section = result['sections'][0]
    assert section['kind'] == 'polarisation'
    cells = {c['source']: c['value'] for c in section['raw_cells']}
    assert cells == {'D8': 'Max', 'E8': 'Max', 'D9': '[N]', 'E9': '[mm]',
                     'A13': '1', 'D13': ' 105.13', 'E13': ' 12.627',
                     'A15': 'Maxi', 'D15': '105.13', 'E15': '12.627'}
    assert section['tables'] == []
    assert result['ready'] is False


def test_mixed_projects_are_not_silently_combined():
    sources = [(f'DL-2026-09-{p} retention.pdf', pdf([f'DL-2026-09-{p}', 'Retention Force',
               'Sample ID Fmax', '1 #1 2930 7.0'])) for p in ('031', '032')]
    with pytest.raises(ValueError, match='project'):
        analyze_folder(sources)


def test_review_is_bound_to_source_and_cannot_replace_measurements():
    from backend.application.mechanical_summary_folder import apply_review
    content = pdf(['DL-2026-09-032', 'MF UMF Fmax', '72 1 107 -310 107 15.2'])
    analysis = analyze_folder([('mating.pdf', content)])
    section = analysis['sections'][0]
    review = {'project': 'DL-2026-09-032', 'sections': {
        section['id']: {'rows': [{'curve': '72', 'sample': '#1', 'colour': 'Orange', 'part': ''}],
                        'withdraw_magnitude': True}}}
    ready = apply_review(analysis, review)
    assert ready['ready'] is True
    assert ready['sections'][0]['rows'][0]['withdraw'] == -310.0
    assert ready['sections'][0]['withdraw_magnitude'] is True
    assert analysis['sections'][0]['rows'][0]['sample'] == ''
    review['sections'][section['id']]['rows'][0]['withdraw'] = 1
    with pytest.raises(ValueError, match='measurement|field'):
        apply_review(analysis, review)
    review['project'] = 'DL-2026-09-031'
    with pytest.raises(ValueError, match='project'):
        apply_review(analysis, review)


def test_qualitative_report_matrix_can_have_different_coverage_than_raw_curves():
    from backend.application.mechanical_summary_folder import apply_review
    analysis = {'project': 'DL-2026-09-032', 'errors': [], 'ignored': [], 'sections': [{
        'id': 'hash:1', 'kind': 'protection', 'rows': [], 'raw_curves': ['1','2','3'],
        'information': {}, 'tables': []}]}
    table = {'title': 'contact not touched by test finger', 'row_heading': 'C-Key',
             'column_heading': '', 'columns': ['Board / Orange', 'Board / Black', 'Busbar / Orange', 'Busbar / Black'],
             'samples': ['#1', '#2', '#3'], 'results': [['Pass'] * 4 for _ in range(3)],
             'diagonal': False, 'curves': []}
    reviewed = apply_review(analysis, {'project': analysis['project'], 'sections': {
        'hash:1': {'tables': [table], 'qualitative_confirmed': True}}})
    assert reviewed['ready'] is True
    assert reviewed['sections'][0]['raw_curves'] == ['1','2','3']
    assert reviewed['sections'][0]['tables'][0]['results'] == [['Pass'] * 4] * 3
    table['results'][0][0] = 'Pass*'
    with pytest.raises(ValueError, match='Pass'):
        apply_review(analysis, {'project': analysis['project'], 'sections': {'hash:1': {'tables': [table], 'qualitative_confirmed': True}}})


def test_retention_pdf_with_wrapped_instrument_headers_is_recognized():
    content = pdf(['DL-2026-09-031 Rec. Connector Retention test', 'F dL(F )', 'max max', '1 #1 2890 11.6'])
    result = analyze_folder([('DL-2026-09-031 Connector Retention Force.pdf', content)])
    assert result['sections'][0]['rows'][0]['value'] == 2890


def test_known_mechanical_file_with_unreadable_results_is_not_silently_excluded():
    result = analyze_folder([('DL-2026-09-031 Connector Retention Force.pdf', pdf(['scanned or unsupported results']))])
    assert result['ready'] is False
    assert result['errors']


def test_duplicate_relative_names_cannot_swap_sources_at_generation():
    first = pdf(['DL-2026-09-031', 'Retention Force', 'Fmax', '1 #1 2890 11.6'])
    second = pdf(['DL-2026-09-031', 'Retention Force', 'Fmax', '1 #1 9999 11.6'])
    with pytest.raises(ValueError, match='[Dd]uplicate'):
        analyze_folder([('test.pdf', first), ('test.pdf', second)])


def test_empty_metadata_columns_do_not_consume_measurement_rows_as_personnel():
    from backend.application.mechanical_summary_folder import source_information
    text = 'Test date :\nTemperature/Humidity :\nTester :\nCustomer :\nLoad cell :\nResults\n1 #1 2890 11.6\n2 #2 2970 11.5\n3 #3 3050 11.7\nStatistics'
    info = source_information(text, 'DL-2026-09-031', 'retention')
    assert info['Tested By'] == 'Not recorded'


def test_changed_record_invalidates_previously_confirmed_mapping():
    from backend.application.mechanical_summary_folder import apply_review
    before = analyze_folder([('source.pdf', pdf(['DL-2026-09-032','MF UMF Fmax','72 1 107 -310 107 15.2']))])
    after = analyze_folder([('source.pdf', pdf(['DL-2026-09-032','MF UMF Fmax','72 1 108 -310 108 15.2']))])
    with pytest.raises(ValueError, match='changed'):
        apply_review(after, {'project':before['project'],'sections':{before['sections'][0]['id']:{'rows':[{'curve':'72','sample':'#1'}]}}})


def test_unnamed_instrument_workbook_requests_type_instead_of_disappearing():
    from backend.application.mechanical_summary_folder import apply_review
    book=Workbook(); s=book.active
    for cell,value in {'D8':'Max','E8':'Max','D9':'[N]','E9':'[mm]','A13':'1','D13':' 20.25','E13':' 8.031'}.items():s[cell]=value
    out=BytesIO();book.save(out);book.close()
    analysis=analyze_folder([('DL-2026-09-032/instrument.xlsx',out.getvalue())])
    section=analysis['sections'][0]
    assert section['kind']=='qualitative'
    assert analysis['ready'] is False
    updated=apply_review(analysis,{'project':analysis['project'],'sections':{section['id']:{'kind':'protection'}}})
    assert updated['sections'][0]['name']=='Protection electric shock'
    assert updated['ready'] is False


def test_pdf_instrument_sample_count_prevents_partial_row_extraction():
    content=pdf(['DL-2026-09-031','Retention Force','Fmax','1 #1 2890 11.6','2 #2 UNREADABLE 11.5','n = 2'])
    result=analyze_folder([('retention.pdf',content)])
    assert result['ready'] is False
    assert 'count' in result['errors'][0]['message'].lower()


def test_workbook_metadata_uses_labelled_values_and_ignores_unlabelled_header_date():
    book=Workbook();s=book.active
    for cell,value in {'L1':'2026-11-06','A6':'Operator:','D6':'Even','G6':'Test Date:','J6':'2026/10/21',
                       'D8':'Max','E8':'Max','D9':'[N]','E9':'[mm]','A13':'1','D13':' 20.25','E13':' 8.031'}.items():s[cell]=value
    out=BytesIO();book.save(out);book.close()
    section=analyze_folder([('DL-2026-09-032 protection electric shock.xlsx',out.getvalue())])['sections'][0]
    assert section['information']['Tested By']=='Even'
    assert section['information']['Test Date']=='2026-10-21'
