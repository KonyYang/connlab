from backend.application.mechanical_summary import parse_pdf_rows, verify_reviewed_pdf
from backend.infrastructure.files.mechanical_summary_pdf import inspect_pdf
from backend.infrastructure.office.mechanical_summary_workbook import inspect_workbook
import pytest
from io import BytesIO
from reportlab.pdfgen import canvas
from openpyxl import Workbook


def test_hold_force_keeps_identifier_precision_and_uses_end_force():
    rows = parse_pdf_rows('1.20 3#-Rec 241.07 241.07 241 5.2', 'hold')
    assert rows == [{'curve': '1.20', 'sample': '3#-Rec', 'value': 241.07}]


def test_hold_force_fields_are_separate_and_never_confused_with_peak():
    text = '1.20 3#-Rec 241.07 242.50 300 5.2'
    assert parse_pdf_rows(text, 'hold')[0]['value'] == 241.07
    assert parse_pdf_rows(text, 'hold_end1')[0]['value'] == 242.50


def test_repeated_curve_identifiers_are_not_silently_accepted():
    with pytest.raises(ValueError, match='[Dd]uplicate'):
        parse_pdf_rows('1 #1-Orange 2930 7.0\n1 #1-Black 2760 12.4', 'retention')


def test_curve_axis_labels_do_not_become_measurements():
    text = '72 1 107 -310 107 15.2\n序列曲线:\n0 1 2 3 4 5'
    assert parse_pdf_rows(text, 'mating') == [
        {'curve': '72', 'sample': '', 'mating': 107.0, 'withdraw': -310.0}
    ]


def test_pdf_preview_requires_review_and_preserves_source_values():
    stream = BytesIO()
    pdf = canvas.Canvas(stream)
    pdf.drawString(40, 760, '1.20 3#-Rec 241.07 241.07 241 5.2')
    pdf.save()
    result = inspect_pdf(stream.getvalue(), 'hold')
    assert result['rows'] == [{'curve': '1.20', 'sample': '3#-Rec', 'value': 241.07}]
    assert result['requires_review'] is True
    assert '1.20 3#-Rec' in result['source_text']


def test_pdf_preview_includes_result_rows_on_later_pages():
    stream = BytesIO()
    pdf = canvas.Canvas(stream)
    pdf.drawString(40, 760, '1.20 first 241.07 241.07 241 5.2')
    pdf.showPage()
    pdf.drawString(40, 760, '1.21 second 242.00 242.00 242 5.2')
    pdf.save()
    result = inspect_pdf(stream.getvalue(), 'hold')
    assert [row['curve'] for row in result['rows']] == ['1.20', '1.21']
    assert '1.21 second' in result['source_text']


def test_workbook_preview_retains_original_values_and_source_rows():
    book = Workbook()
    sheet = book.active
    sheet.title = 'Instrument'
    sheet.append(['Curve', 'Force (N)'])
    sheet.append(['1.20', -241.07])
    stream = BytesIO()
    book.save(stream)
    book.close()
    preview = inspect_workbook(stream.getvalue(), 'source.xlsx')
    assert preview['sheets'][0]['rows'] == [['Curve', 'Force (N)'], ['1.20', -241.07]]
    assert preview['requires_review'] is True


def test_reviewed_pdf_values_must_still_match_source():
    source = [{'curve': '1.20', 'sample': '3#-Rec', 'value': 241.07}]
    reviewed = [{'curve': '1.20', 'sample': '3#-Rec', 'value': 241.07}]
    assert verify_reviewed_pdf(source, reviewed, 'hold') == reviewed
    reviewed[0]['value'] = 241.0
    with pytest.raises(ValueError, match='source'):
        verify_reviewed_pdf(source, reviewed, 'hold')


def test_review_must_include_all_rows_and_explicit_sample():
    source = [{'curve': '72', 'sample': '', 'mating': 107.0, 'withdraw': -310.0}]
    with pytest.raises(ValueError, match='sample'):
        verify_reviewed_pdf(source, source, 'mating')
    with pytest.raises(ValueError, match='rows'):
        verify_reviewed_pdf(source, [], 'mating')
