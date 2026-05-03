"""Deterministic SECTION 1 pre-project precheck rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class DraftPrecheckIssue:
    """One draft-level precheck issue before Project creation."""

    level: str
    field_key: str
    message: str


REQUIRED_SECTION1_FIELDS: tuple[tuple[str, str], ...] = (
    ("form_no", "Form No."),
    ("revision", "Revision"),
    ("product_name", "Product Name"),
    ("requester", "Requested By"),
    ("phone", "Phone #"),
    ("request_date", "Date"),
    ("email", "Email"),
    ("business_unit", "Business Unit"),
    ("manufacturing_site", "Mfg. Site"),
    ("results_format", "Results Format"),
    ("requested_completion_date", "Requested Testing Completion Date"),
    ("test_type", "Test Type"),
    ("sample_status", "Test Sample Status"),
    ("project_type", "Project Type"),
    ("requested_testing", "Description of Requested Testing"),
    ("post_testing_disposition", "Post-Testing Sample Disposition"),
    ("confidential", "Confidential tests or samples?"),
    ("subcontract", "Can testing be subcontracted?"),
    ("send_copies_recipients", "Send copies of test results/reports to"),
)

SAMPLE_REQUIRED_FIELDS: tuple[tuple[str, str], ...] = (
    ("product_name", "Product Name"),
    ("part_number", "Part Number / Revision"),
    ("lot_or_traceability", "Traceability Manufacturing Lot Info"),
    ("material", "Contact Base Material"),
    ("plating", "Contact Plating"),
    ("housing_material", "Housing Material"),
    ("quantity", "Quantity"),
)


def evaluate_section1_precheck(data: dict[str, Any]) -> tuple[DraftPrecheckIssue, ...]:
    """Return deterministic SECTION 1 blockers and warnings."""
    issues: list[DraftPrecheckIssue] = []
    for key, label in REQUIRED_SECTION1_FIELDS:
        if not _text(data.get(key)):
            issues.append(
                DraftPrecheckIssue(
                    level="error",
                    field_key=key,
                    message=f"{label} is required before Project creation.",
                )
            )

    _append_expected_value_issue(issues, data, "form_no", "Form No.", "E-3718")
    _append_expected_value_issue(issues, data, "revision", "Revision", "H")

    if not _text(data.get("project_no")):
        issues.append(
            DraftPrecheckIssue(
                level="warning",
                field_key="project_no",
                message="Project # is blank. ConnLab can continue because LTR Number becomes the project identity later.",
            )
        )
    if _text(data.get("lab_test_request_number")):
        issues.append(
            DraftPrecheckIssue(
                level="warning",
                field_key="lab_test_request_number",
                message="Lab Test Request Number was pre-filled in the source form and is cleared from the draft before Project creation.",
            )
        )

    _append_sample_issues(issues, data.get("samples"))
    return tuple(issues)


def clear_disallowed_section1_values(data: dict[str, Any]) -> dict[str, Any]:
    """Return draft data with disallowed pre-project source values cleared."""
    if not _text(data.get("lab_test_request_number")):
        return data
    return {**data, "lab_test_request_number": ""}


def blocking_issue_fields(issues: tuple[DraftPrecheckIssue, ...]) -> tuple[str, ...]:
    """Return field keys that have blocking errors."""
    return tuple(issue.field_key for issue in issues if issue.level == "error")


def _append_expected_value_issue(
    issues: list[DraftPrecheckIssue],
    data: dict[str, Any],
    key: str,
    label: str,
    expected: str,
) -> None:
    """Append an error when a present metadata value does not match the expected value."""
    value = _text(data.get(key))
    if value and value.upper() != expected.upper():
        issues.append(
            DraftPrecheckIssue(
                level="error",
                field_key=key,
                message=f"{label} must be {expected} before Project creation.",
            )
        )


def _append_sample_issues(issues: list[DraftPrecheckIssue], samples: object) -> None:
    """Append sample row required-field issues."""
    if not isinstance(samples, list) or not samples:
        issues.append(
            DraftPrecheckIssue(
                level="error",
                field_key="samples",
                message="At least one sample row is required before Project creation.",
            )
        )
        return
    for row_index, row in enumerate(samples, start=1):
        if not isinstance(row, dict):
            issues.append(
                DraftPrecheckIssue(
                    level="error",
                    field_key="samples",
                    message=f"Sample row {row_index} is invalid.",
                )
            )
            continue
        for key, label in SAMPLE_REQUIRED_FIELDS:
            if not _text(row.get(key)):
                issues.append(
                    DraftPrecheckIssue(
                        level="error",
                        field_key=f"samples.{key}",
                        message=f"Sample row {row_index}: {label} is required.",
                    )
                )


def _text(value: object) -> str | None:
    """Return stripped text or None."""
    if value in (None, ""):
        return None
    text = str(value).strip()
    return text or None
