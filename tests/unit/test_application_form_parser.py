from pathlib import Path

from docx import Document

from backend.modules.intake import ApplicationFormParser
from tests.fixtures.real_style_application_forms import build_real_style_application_form


def test_application_form_parser_extracts_fields_and_sample_row(tmp_path: Path) -> None:
    docx_path = tmp_path / "application-form.docx"
    document = Document()
    document.add_paragraph("Form No.: E-3718")
    document.add_paragraph("Form Rev: H")
    _add_key_value_table(
        document,
        [
            ("Reference Doc", "LAB-QA-001"),
            ("Lab Test Request Number", "LTR-001"),
            ("Requested By", "Alice"),
            ("Phone", "555-0100"),
            ("Date", "2026-04-26"),
            ("Email", "alice@example.com"),
            ("Business Unit", "BU-1"),
            ("Mfg. Site", "Plant 1"),
            ("Project #", "PRJ-001"),
            ("Requested Testing Completion Date", "2026-05-01"),
            ("Results Format", "PDF"),
            ("Test Type", "Qualification"),
            ("Sample Status", "Prototype"),
            ("Project Type", "New Product"),
            ("Post-testing disposition", "Return samples"),
            ("Description of Requested Testing", "Salt spray test"),
            ("Confidential", "Yes"),
            ("Subcontract", "No"),
            ("Additional Information", "Handle with care"),
            ("Send Copies", "bob@example.com"),
            ("Lab", "Connector Lab"),
            ("Assigned Personnel", "Charlie"),
            ("Received Date", "2026-04-27"),
            ("Estimated Completion Date", "2026-05-02"),
            ("Sample Condition", "Good"),
        ],
    )
    sample_table = document.add_table(rows=2, cols=8)
    headers = [
        "Product Name",
        "Part Number",
        "Revision",
        "Lot/Traceability",
        "Material",
        "Plating",
        "Housing Material",
        "Quantity",
    ]
    values = [
        "Connector",
        "PN-001",
        "A",
        "LOT-1",
        "Copper",
        "Tin",
        "LCP",
        "12",
    ]
    for index, header in enumerate(headers):
        sample_table.cell(0, index).text = header
        sample_table.cell(1, index).text = values[index]
    document.save(docx_path)

    parsed = ApplicationFormParser().parse(docx_path)

    assert parsed.form_no == "E-3718"
    assert parsed.form_rev == "H"
    assert parsed.reference_doc == "LAB-QA-001"
    assert parsed.lab_test_request_number == "LTR-001"
    assert parsed.requested_by == "Alice"
    assert parsed.project_number == "PRJ-001"
    assert parsed.requested_testing_description == "Salt spray test"
    assert parsed.lab_section.assigned_personnel == "Charlie"
    assert len(parsed.samples) == 1
    assert parsed.samples[0].part_number == "PN-001"
    assert parsed.samples[0].quantity == "12"


def test_application_form_parser_tolerates_missing_optional_fields(
    tmp_path: Path,
) -> None:
    docx_path = tmp_path / "minimal-form.docx"
    document = Document()
    _add_key_value_table(
        document,
        [
            ("Form No.", "E-3718"),
            ("Requested By", "Alice"),
        ],
    )
    document.save(docx_path)

    parsed = ApplicationFormParser().parse(docx_path)

    assert parsed.form_no == "E-3718"
    assert parsed.requested_by == "Alice"
    assert parsed.email is None
    assert parsed.samples == ()
    assert parsed.lab_section.lab is None


def test_application_form_parser_extracts_real_style_applicant_fixture(
    tmp_path: Path,
) -> None:
    docx_path = build_real_style_application_form(tmp_path / "real-style-applicant.docx")

    parsed = ApplicationFormParser().parse(docx_path)

    assert parsed.form_no == "E-3718"
    assert parsed.form_rev == "H"
    assert parsed.requested_by == "Alice Requestor"
    assert parsed.phone == "555-0100"
    assert parsed.request_date == "2026-04-27"
    assert parsed.email == "alice.requestor@example.com"
    assert parsed.business_unit == "Industrial"
    assert parsed.manufacturing_site == "Plant 7"
    assert parsed.project_number == "PRJ-038-A"
    assert parsed.project_type == "Qualification"
    assert parsed.subcontract == "No"
    assert parsed.requested_testing_description == "Thermal cycling and contact resistance"
    assert parsed.lab_section.lab == "Connector Lab"
    assert parsed.lab_section.assigned_personnel == "Charlie Tester"
    assert parsed.lab_section.received_date == "2026-04-28"
    assert parsed.lab_section.estimated_completion_date == "2026-05-15"
    assert parsed.lab_section.sample_condition == "Good"
    assert len(parsed.samples) == 1
    assert parsed.samples[0].product_name == "Synthetic Connector"
    assert parsed.samples[0].part_number == "PN-038-A"
    assert parsed.samples[0].revision == "A"
    assert parsed.samples[0].lot_or_traceability == "LOT-038"
    assert parsed.samples[0].quantity == "24"


def test_application_form_parser_extracts_comparable_tester_modified_fixture(
    tmp_path: Path,
) -> None:
    applicant_path = build_real_style_application_form(
        tmp_path / "real-style-applicant.docx",
    )
    tester_path = build_real_style_application_form(
        tmp_path / "real-style-tester.docx",
        tester_modified=True,
    )

    applicant = ApplicationFormParser().parse(applicant_path)
    tester = ApplicationFormParser().parse(tester_path)

    assert applicant.form_no == tester.form_no == "E-3718"
    assert applicant.form_rev == tester.form_rev == "H"
    assert applicant.requested_by == tester.requested_by == "Alice Requestor"
    assert applicant.requested_testing_description == tester.requested_testing_description
    assert applicant.project_number == "PRJ-038-A"
    assert tester.project_number == "PRJ-038-T"
    assert applicant.samples[0].part_number == "PN-038-A"
    assert tester.samples[0].part_number == "PN-038-T"
    assert tester.lab_section.sample_condition == "Good, tester reviewed"


def _add_key_value_table(document: Document, pairs: list[tuple[str, str]]) -> None:
    table = document.add_table(rows=len(pairs), cols=2)
    for row_index, (label, value) in enumerate(pairs):
        table.cell(row_index, 0).text = label
        table.cell(row_index, 1).text = value
