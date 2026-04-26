"""Mapping helpers for intake/precheck application workflow."""

from __future__ import annotations

from datetime import date
from uuid import uuid4

from backend.domain import ApplicationForm, PrecheckIssue, PrecheckResult, SampleInfo
from backend.modules.intake import ParsedApplicationForm, ParsedLabSection, ParsedSampleInfo


def to_application_form(
    form_id: str,
    project_id: str,
    parsed: ParsedApplicationForm,
) -> ApplicationForm:
    """Convert parsed form output to the persisted domain form."""
    return ApplicationForm(
        form_id=form_id,
        project_id=project_id,
        form_no=parsed.form_no or "",
        revision=parsed.form_rev or "",
        requester=parsed.requested_by or "",
        phone=parsed.phone,
        email=parsed.email,
        business_unit=parsed.business_unit,
        manufacturing_site=parsed.manufacturing_site,
        requested_testing=parsed.requested_testing_description,
        subcontract_allowed=parse_yes_no(parsed.subcontract),
        reference_doc=parsed.reference_doc,
        lab_test_request_number=parsed.lab_test_request_number,
        project_number=parsed.project_number,
        requested_completion_date=parsed.requested_completion_date,
        results_format=parsed.results_format,
        test_type=parsed.test_type,
        sample_status=parsed.sample_status,
        project_type=parsed.project_type,
        post_testing_disposition=parsed.post_testing_disposition,
        confidential=parsed.confidential,
        subcontract=parsed.subcontract,
        additional_information=parsed.additional_information,
        send_copies_recipients=parsed.send_copies_recipients,
        lab=parsed.lab_section.lab,
        assigned_personnel=parsed.lab_section.assigned_personnel,
        received_date=parsed.lab_section.received_date,
        estimated_completion_date=parsed.lab_section.estimated_completion_date,
        sample_condition=parsed.lab_section.sample_condition,
    )


def to_sample_infos(
    project_id: str,
    samples: tuple[ParsedSampleInfo, ...],
) -> tuple[SampleInfo, ...]:
    """Convert parsed sample rows to persisted domain sample records."""
    return tuple(
        SampleInfo(
            sample_id=uuid4().hex,
            project_id=project_id,
            product_name=sample.product_name or "",
            part_number=sample.part_number or "",
            revision=sample.revision,
            lot_or_traceability=sample.lot_or_traceability,
            material=sample.material,
            plating=sample.plating,
            housing_material=sample.housing_material,
            quantity=parse_int(sample.quantity),
        )
        for sample in samples
    )


def from_application_form(
    form: ApplicationForm,
    samples: list[SampleInfo],
) -> ParsedApplicationForm:
    """Reconstruct parsed-form input from persisted domain rows."""
    return ParsedApplicationForm(
        form_no=form.form_no,
        form_rev=form.revision,
        reference_doc=form.reference_doc,
        lab_test_request_number=form.lab_test_request_number,
        requested_by=form.requester,
        phone=form.phone,
        request_date=str(form.request_date) if form.request_date else None,
        email=form.email,
        business_unit=form.business_unit,
        manufacturing_site=form.manufacturing_site,
        project_number=form.project_number,
        requested_completion_date=form.requested_completion_date,
        requested_testing_description=form.requested_testing,
        subcontract=form.subcontract,
        lab_section=ParsedLabSection(estimated_completion_date=form.estimated_completion_date),
        samples=tuple(from_sample(sample) for sample in samples),
    )


def from_sample(sample: SampleInfo) -> ParsedSampleInfo:
    """Convert persisted sample row to parser sample DTO."""
    return ParsedSampleInfo(
        product_name=sample.product_name,
        part_number=sample.part_number,
        revision=sample.revision,
        lot_or_traceability=sample.lot_or_traceability,
        material=sample.material,
        plating=sample.plating,
        housing_material=sample.housing_material,
        quantity=str(sample.quantity) if sample.quantity is not None else None,
    )


def with_persistent_ids(
    result: PrecheckResult,
    application_form_id: str,
) -> PrecheckResult:
    """Assign persistent IDs and the stored application form ID."""
    issues = tuple(
        PrecheckIssue(
            issue_id=uuid4().hex,
            category=issue.category,
            level=issue.level,
            message=issue.message,
            field_name=issue.field_name,
            resolved=issue.resolved,
        )
        for issue in result.issues
    )
    return PrecheckResult(
        result_id=uuid4().hex,
        application_form_id=application_form_id,
        status=result.status,
        issues=issues,
        checked_on=result.checked_on or date.today(),
    )


def parse_yes_no(value: str | None) -> bool | None:
    """Parse simple Yes/No subcontract values."""
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"yes", "y", "true", "1", "是"}:
        return True
    if normalized in {"no", "n", "false", "0", "否"}:
        return False
    return None


def parse_int(value: str | None) -> int | None:
    """Parse a simple integer quantity."""
    return int(value) if value and value.strip().isdigit() else None
