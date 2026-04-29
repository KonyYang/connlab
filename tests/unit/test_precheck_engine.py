from dataclasses import replace

from backend.domain import IssueCategory, IssueLevel, PrecheckStatus
from backend.modules.intake import ParsedApplicationForm, ParsedLabSection, ParsedSampleInfo
from backend.modules.precheck import PrecheckEngine


def test_valid_application_form_produces_passed_result() -> None:
    result = PrecheckEngine().run(_valid_form(), registered_attachments=("plan.pdf",))

    assert result.status is PrecheckStatus.PASSED
    assert result.issues == ()
    assert result.has_errors() is False


def test_missing_project_number_does_not_block_precheck() -> None:
    form = replace(_valid_form(), project_number=None)

    result = PrecheckEngine().run(form, registered_attachments=("plan.pdf",))

    assert result.status is PrecheckStatus.PASSED
    assert not any(issue.field_name == "project_number" for issue in result.issues)


def test_missing_sample_field_produces_error_issue() -> None:
    form = _valid_form(
        samples=(
            ParsedSampleInfo(
                product_name="Connector",
                part_number="PN-001",
                lot_or_traceability="LOT-1",
                material="Copper",
                plating=None,
                housing_material="LCP",
                quantity="12",
            ),
        )
    )

    result = PrecheckEngine().run(form)

    assert result.status is PrecheckStatus.FAILED
    assert any(
        issue.category is IssueCategory.SAMPLE
        and issue.level is IssueLevel.ERROR
        and "plating" in issue.message
        for issue in result.issues
    )


def test_attachment_reference_without_registered_attachment_produces_warning() -> None:
    form = _valid_form(requested_testing_description="依附件")

    result = PrecheckEngine().run(form, registered_attachments=())

    assert result.status is PrecheckStatus.WARNING
    assert any(
        issue.category is IssueCategory.ATTACHMENT
        and issue.level is IssueLevel.WARNING
        for issue in result.issues
    )


def test_wrong_revision_produces_form_metadata_issue() -> None:
    form = _valid_form(form_rev="G")

    result = PrecheckEngine().run(form)

    assert result.status is PrecheckStatus.FAILED
    assert any(
        issue.category is IssueCategory.FORM_METADATA
        and issue.field_name == "form_rev"
        and "FORM-002" in issue.message
        for issue in result.issues
    )


def test_quantity_expression_produces_warning() -> None:
    form = _valid_form(
        samples=(
            ParsedSampleInfo(
                product_name="Connector",
                part_number="PN-001",
                lot_or_traceability="LOT-1",
                material="Copper",
                plating="Tin",
                housing_material="LCP",
                quantity="6+6",
            ),
        )
    )

    result = PrecheckEngine().run(form)

    assert result.status is PrecheckStatus.WARNING
    assert any(
        issue.category is IssueCategory.SAMPLE
        and issue.level is IssueLevel.WARNING
        and "quantity" in issue.message
        for issue in result.issues
    )


def _valid_form(
    *,
    form_rev: str = "H",
    requested_testing_description: str = "Salt spray test",
    samples: tuple[ParsedSampleInfo, ...] | None = None,
) -> ParsedApplicationForm:
    return ParsedApplicationForm(
        form_no="E-3718",
        form_rev=form_rev,
        requested_by="Alice",
        phone="555-0100",
        request_date="2026-04-26",
        email="alice@example.com",
        business_unit="BU-1",
        manufacturing_site="Plant 1",
        project_number="PRJ-001",
        requested_testing_description=requested_testing_description,
        subcontract="No",
        lab_section=ParsedLabSection(estimated_completion_date="2026-05-01"),
        samples=samples
        or (
            ParsedSampleInfo(
                product_name="Connector",
                part_number="PN-001",
                lot_or_traceability="LOT-1",
                material="Copper",
                plating="Tin",
                housing_material="LCP",
                quantity="12",
            ),
        ),
    )
