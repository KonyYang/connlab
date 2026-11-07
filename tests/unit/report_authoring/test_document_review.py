from io import BytesIO
from hashlib import sha256
from zipfile import ZipFile

from docx import Document
from docx.shared import Inches
from PIL import Image
from docx.oxml import OxmlElement

from backend.infrastructure.office.report_authoring.document_review import ReportDocumentInspector


def illustrated_report(tmp_path):
    image = BytesIO()
    Image.new('RGB', (80, 60), 'blue').save(image, format='PNG')
    document = Document()
    document.sections[0].header.paragraphs[0].text = 'DL-2026-09-021'
    document.add_paragraph('Specification Rev.2 date: 2026-08-01')
    document.add_paragraph('Authorization date: 2026-09-01')
    document.add_paragraph('Group Ab Test Results')
    document.add_picture(BytesIO(image.getvalue()), width=Inches(2))
    document.add_picture(BytesIO(image.getvalue()), width=Inches(2))
    document.add_paragraph('Figure 7: Group Ab SN1 and SN2 after test')
    document.add_paragraph('See Figure 7 for the specimen.')
    document.add_paragraph('*** End of Report ***')
    path = tmp_path / 'source.docx'
    document.save(path)
    return path


def test_inspection_and_numbering_are_local_and_shared_caption_is_numbered_once(tmp_path):
    source = illustrated_report(tmp_path)
    before = source.read_bytes()
    inspector = ReportDocumentInspector()
    review = inspector.inspect(source)
    assert len(review['figures']) == 1
    assert review['figures'][0]['slot_ids'] == ['photo-1', 'photo-2']
    assert review['figures'][0]['number'] == 7
    assert {'revision_date', 'authorization_date'} <= {item['kind'] for item in review['regions']}
    numbering = inspector.numbering(source)
    assert [change['new'] for change in numbering['replacements']] == ['Figure 1', 'Figure 1']
    output = tmp_path / 'numbered.docx'
    inspector.apply_numbering(source, output, numbering)
    assert source.read_bytes() == before
    assert Document(output).paragraphs[-1].text == '*** End of Report ***'
    with ZipFile(source) as original, ZipFile(output) as changed:
        assert all(original.read(name) == changed.read(name) for name in original.namelist() if name != 'word/document.xml')


def test_dangling_reference_is_reported_and_not_silently_renumbered(tmp_path):
    source = illustrated_report(tmp_path)
    document = Document(source)
    document.add_paragraph('See Figure 99 for results.')
    document.save(source)
    review = ReportDocumentInspector().numbering(source)
    assert not review['ready']
    assert any(item['code'] == 'dangling_figure_reference' for item in review['issues'])


def test_compound_caption_preserves_subfigure_count_and_nonlabel_runs(tmp_path):
    source = illustrated_report(tmp_path)
    document = Document(source)
    paragraph = document.paragraphs[-3]
    paragraph.clear()
    paragraph.add_run('Figure 7~9').bold = True
    paragraph.add_run(': Black / Orange specimens').italic = True
    document.paragraphs[-2].text = 'See Figure 7~9.'
    document.save(source)
    inspector = ReportDocumentInspector()
    plan = inspector.numbering(source)
    assert plan['ready']
    assert [item['new'] for item in plan['replacements']] == ['Figure 1~3', 'Figure 1~3']
    output = tmp_path / 'compound.docx'
    inspector.apply_numbering(source, output, plan)
    changed = Document(output).paragraphs[-3]
    assert changed.runs[0].bold
    assert changed.runs[1].text == ': Black / Orange specimens'
    assert changed.runs[1].italic


def test_only_figure_digits_change_even_when_label_and_digits_have_different_styles(tmp_path):
    source = illustrated_report(tmp_path)
    document = Document(source)
    paragraph = document.paragraphs[-3]; paragraph.clear()
    paragraph.add_run('Figure ').italic = True
    paragraph.add_run('7').bold = True
    paragraph.add_run(': SN7 coating is unchanged').underline = True
    document.save(source)
    inspector = ReportDocumentInspector(); plan = inspector.numbering(source)
    target = tmp_path / 'digits.docx'; inspector.apply_numbering(source, target, plan)
    runs = Document(target).paragraphs[-3].runs
    assert [(item.text, item.italic, item.bold, item.underline) for item in runs] == [
        ('Figure ', True, None, None), ('1', None, True, None), (': SN7 coating is unchanged', None, None, True)]


def test_range_cannot_include_a_reserved_chart_number_after_renumbering(tmp_path):
    source = illustrated_report(tmp_path)
    document = Document(source)
    document.paragraphs[-3].text = 'Figure 7~9: Three specimen views'
    document.paragraphs[-2].text = 'See Figure 7~9.'
    document.add_paragraph('Unnumbered temperature curve context')
    document.add_paragraph('Figure 2: A curve (not a photo slot)')
    document.save(source)
    plan = ReportDocumentInspector().numbering(source)
    assert not plan['ready']
    assert any(item['code'] == 'noncontiguous_figure_range' for item in plan['issues'])


def test_adjacent_captions_with_unproven_image_split_stay_pending(tmp_path):
    source = illustrated_report(tmp_path)
    document = Document(source)
    document.paragraphs[-2].text = 'Figure 8: Another specimen caption without a separate image group'
    document.save(source)
    plan = ReportDocumentInspector().numbering(source)
    assert not plan['ready']
    assert any(item['code'] == 'ambiguous_shared_caption' for item in plan['issues'])


def test_floating_arrow_text_does_not_hide_its_host_photo_caption(tmp_path):
    source = illustrated_report(tmp_path)
    document = Document(source)
    paragraph = document.paragraphs[-3]
    box = OxmlElement('w:txbxContent'); nested = OxmlElement('w:p'); run = OxmlElement('w:r'); text = OxmlElement('w:t')
    text.text = 'Unmated annotation'; run.append(text); nested.append(run); box.append(nested); paragraph._p.insert(0, box)
    document.save(source)
    review = ReportDocumentInspector().inspect(source)
    assert review['figures'][0]['numbers'] == [7]
    assert len(review['figures'][0]['slot_ids']) == 2
    assert review['figures'][0]['automatic_order']


def test_old_mating_single_color_heading_is_checked_against_its_adjacent_result_not_unrelated_text(tmp_path):
    from dataclasses import asdict
    from types import SimpleNamespace
    from backend.application.report_authoring.document_review import ReportDocumentReview
    from backend.application.report_authoring.service import ReportAuthoringService
    from backend.domain.report_authoring import ReportAuthoringState, ReportSource
    from backend.infrastructure.office.report_authoring.results_document import ReportResultsDocument
    from tests.unit.report_authoring.test_results_document import fixture_report, mechanical
    original, working = tmp_path / 'original.docx', tmp_path / 'working.docx'
    fixture_report(original)
    result = mechanical(); result.update(source_id='measurements', matrix_id='M1')
    ReportResultsDocument().update(original, working, result, result_table=0, result_row=1, appendix_table=1, appendix_title='Appendix B')
    document = Document(working)
    document.paragraphs[0].text = 'Unrelated Orange Mating description (not a result heading)'
    next(item for item in document.paragraphs if item.text.startswith('Appendix B')).text = 'Appendix B: Old Orange Mating Force'
    document.save(working)
    base = ReportSource('base', 'original', 'original.docx', 'b' * 64, 1, 'now')
    source = ReportSource('measurements', 'mechanical', 'force.csv', 'a' * 64, 1, 'now')
    artifact = ReportSource('out', 'working_copy', 'working.docx', sha256(working.read_bytes()).hexdigest(), working.stat().st_size, 'now')
    output = {'output_id': 'out', 'artifact': asdict(artifact), 'base_source_id': 'base', 'operation': 'batch_assembly', 'evidence': {'result_ids': ['r1']}}
    state = ReportAuthoringState('P1', sources=(base, source), outputs=(output,), results=(result,))
    context = {'dl_number': 'DL-2026-09-032', 'matrix_id': 'M1'}
    service = SimpleNamespace(_editable=lambda *_: (state, context), _current_output=lambda *_: output,
        assets=SimpleNamespace(read=lambda *_: b'valid', path=lambda *_: working),
        _source=ReportAuthoringService._source, _source_family=ReportAuthoringService._source_family,
        active_result_ids=lambda _: ['r1'], _confirmed_result=lambda *_: result, coverage=lambda _: {'complete': False})
    review = ReportDocumentReview(service, ReportDocumentInspector(), None).inspect('P1', 'out', 0)
    title = next(item for item in review['regions'] if item['text'].startswith('Appendix B'))
    assert title['status'] == 'conflict'
    assert any('Mating' in reason for reason in title['reasons'])
    assert any('single-color' in reason for reason in title['reasons'])
    assert next(item for item in review['regions'] if item['text'].startswith('Unrelated'))['status'] != 'conflict'
