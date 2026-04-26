"""Deterministic precheck rule functions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.domain import IssueCategory, IssueLevel, PrecheckIssue
from backend.modules.intake import ParsedSampleInfo

if TYPE_CHECKING:
    from backend.modules.precheck.precheck_engine import Rule, RuleContext


EXPECTED_FORM_NO = "E-3718"
EXPECTED_FORM_REV = "H"


def check_form_number(context: "RuleContext") -> list[PrecheckIssue]:
    """Validate expected form number."""
    if _normalize(context.form.form_no) == _normalize(EXPECTED_FORM_NO):
        return []
    return [_make_issue("FORM-001: Form No. must be E-3718.", "form_no")]


def check_form_revision(context: "RuleContext") -> list[PrecheckIssue]:
    """Validate expected form revision."""
    if _normalize(context.form.form_rev) == _normalize(EXPECTED_FORM_REV):
        return []
    return [_make_issue("FORM-002: Form Rev must be H.", "form_rev")]


def check_requestor_fields(context: "RuleContext") -> list[PrecheckIssue]:
    """Validate required requestor fields."""
    required = {
        "requested_by": context.form.requested_by,
        "phone": context.form.phone,
        "request_date": context.form.request_date,
        "email": context.form.email,
        "business_unit": context.form.business_unit,
        "manufacturing_site": context.form.manufacturing_site,
        "project_number": context.form.project_number,
    }
    return [
        _make_issue(
            f"REQUESTOR: Required field is missing: {field_name}.",
            field_name,
            IssueCategory.REQUESTOR,
        )
        for field_name, value in required.items()
        if _is_blank(value)
    ]


def check_sample_rows(context: "RuleContext") -> list[PrecheckIssue]:
    """Validate required fields for non-empty sample rows."""
    issues: list[PrecheckIssue] = []
    if not context.form.samples:
        return [
            _make_issue(
                "SAMPLE: At least one test sample row is required.",
                "samples",
                IssueCategory.SAMPLE,
            )
        ]
    for index, sample in enumerate(context.form.samples, start=1):
        issues.extend(_check_one_sample(sample, index))
    return issues


def check_testing_description(context: "RuleContext") -> list[PrecheckIssue]:
    """Validate requested testing description and attachment references."""
    description = context.form.requested_testing_description
    if _is_blank(description):
        return [
            _make_issue(
                "TESTING: Description of requested testing is required.",
                "requested_testing_description",
                IssueCategory.TESTING_REQUEST,
            )
        ]
    if _references_attachment(description) and not context.registered_attachments:
        return [
            _make_issue(
                "TESTING: Requested testing references an attachment, "
                "but no attachment is registered.",
                "registered_attachments",
                IssueCategory.ATTACHMENT,
                IssueLevel.WARNING,
            )
        ]
    return []


def check_subcontract(context: "RuleContext") -> list[PrecheckIssue]:
    """Warn when subcontract permission is missing."""
    if not _is_blank(context.form.subcontract):
        return []
    return [
        _make_issue(
            "SUBCONTRACT: Subcontract permission should be specified.",
            "subcontract",
            IssueCategory.SUBCONTRACT,
            IssueLevel.WARNING,
        )
    ]


def check_lab_section(context: "RuleContext") -> list[PrecheckIssue]:
    """Warn when lab estimated completion date is missing."""
    if not _is_blank(context.form.lab_section.estimated_completion_date):
        return []
    return [
        _make_issue(
            "LAB_SECTION: Estimated completion date should be specified.",
            "lab_section.estimated_completion_date",
            IssueCategory.LAB_SECTION,
            IssueLevel.WARNING,
        )
    ]


DEFAULT_RULES: tuple["Rule", ...] = (
    check_form_number,
    check_form_revision,
    check_requestor_fields,
    check_sample_rows,
    check_testing_description,
    check_subcontract,
    check_lab_section,
)


def _check_one_sample(sample: ParsedSampleInfo, index: int) -> list[PrecheckIssue]:
    """Validate a single parsed sample row."""
    if not _sample_has_any_value(sample):
        return []
    issues = [
        _make_issue(
            f"SAMPLE: Row {index} is missing required field {field_name}.",
            f"samples[{index}].{field_name}",
            IssueCategory.SAMPLE,
        )
        for field_name, value in _required_sample_fields(sample).items()
        if _is_blank(value)
    ]
    if _has_quantity_expression(sample.quantity):
        issues.append(
            _make_issue(
                f"SAMPLE: Row {index} quantity should be reviewed because it "
                "contains an expression or free text.",
                f"samples[{index}].quantity",
                IssueCategory.SAMPLE,
                IssueLevel.WARNING,
            )
        )
    return issues


def _required_sample_fields(sample: ParsedSampleInfo) -> dict[str, str | None]:
    """Return required sample fields and parsed values."""
    return {
        "product_name": sample.product_name,
        "part_number": sample.part_number,
        "lot_or_traceability": sample.lot_or_traceability,
        "material": sample.material,
        "plating": sample.plating,
        "housing_material": sample.housing_material,
        "quantity": sample.quantity,
    }


def _make_issue(
    message: str,
    field_name: str,
    category: IssueCategory = IssueCategory.FORM_METADATA,
    level: IssueLevel = IssueLevel.ERROR,
) -> PrecheckIssue:
    """Create a precheck issue with a placeholder ID."""
    return PrecheckIssue(
        issue_id="pending",
        category=category,
        level=level,
        message=message,
        field_name=field_name,
    )


def _sample_has_any_value(sample: ParsedSampleInfo) -> bool:
    """Return whether a parsed sample row contains any value."""
    return any(not _is_blank(value) for value in _all_sample_values(sample))


def _all_sample_values(sample: ParsedSampleInfo) -> tuple[str | None, ...]:
    """Return all parsed sample values."""
    return (
        sample.product_name,
        sample.part_number,
        sample.revision,
        sample.lot_or_traceability,
        sample.material,
        sample.plating,
        sample.housing_material,
        sample.quantity,
    )


def _has_quantity_expression(value: str | None) -> bool:
    """Return whether quantity contains operators or non-numeric free text."""
    if _is_blank(value):
        return False
    text = value.strip()
    return "+" in text or "/" in text or not text.isdigit()


def _references_attachment(value: str) -> bool:
    """Return whether requested testing text references an attachment."""
    text = value.lower()
    return any(token in text for token in ("attachment", "see attached", "依附件", "见附件"))


def _normalize(value: str | None) -> str:
    """Normalize a scalar value for rule comparisons."""
    return "" if value is None else value.strip().upper()


def _is_blank(value: str | None) -> bool:
    """Return whether a parsed scalar value is missing or blank."""
    return value is None or not value.strip()
