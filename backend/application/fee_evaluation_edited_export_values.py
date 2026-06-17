"""Edited Fee Evaluation export values shared by API, service, and gateway."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    MatrixBasicFillGroup,
    MatrixBasicFillLine,
    MatrixBasicFillWorkbook,
)


@dataclass(frozen=True, slots=True)
class FeeEvaluationEditedExportRow:
    """One editable Matrix step row to carry into a generated Fee Form."""

    source_line_id: str
    confirmed_group_id: str
    confirmed_row_id: str
    step_token: str
    step_index: int
    spend_time: str
    unit_price: str
    unit_type: str
    units: str
    base_fee: str
    discount: str
    testing_fee: str
    notes: str


@dataclass(frozen=True, slots=True)
class FeeEvaluationEditedManualRow:
    """One editable manual Fee Form row that is not a Matrix authority row."""

    row_kind: str
    spend_time: str
    unit_price: str
    unit_type: str
    units: str
    base_fee: str
    discount: str
    testing_fee: str
    notes: str
    confirmed_group_id: str = ""
    group_key: str = ""
    group_label: str = ""


@dataclass(frozen=True, slots=True)
class FeeEvaluationEditedExportSummary:
    """Editable summary values that map to manual/template anchors."""

    condition_confirmation_spend_time: str
    external_cost: str
    external_cost_note: str
    lab_manpower_hourly_rate: str


@dataclass(frozen=True, slots=True)
class FeeEvaluationEditedInactiveRowKey:
    """Serializable rebase identity for one hidden inactive Fee row."""

    group_identity: str
    row_identity: str
    step_token: str
    step_index: int


@dataclass(frozen=True, slots=True)
class FeeEvaluationEditedInactiveRow:
    """Hidden Fee row preserved for Matrix soft-remove restoration."""

    previous_row: FeeEvaluationEditedExportRow
    rebase_key: FeeEvaluationEditedInactiveRowKey
    group_key: str
    group_label: str
    group_signature: str
    inactive_reason: str = "removed_from_matrix"


@dataclass(frozen=True, slots=True)
class FeeEvaluationEditedExportValues:
    """Complete edited export payload for one Fee Form generation."""

    rows: tuple[FeeEvaluationEditedExportRow, ...]
    summary: FeeEvaluationEditedExportSummary
    manual_rows: tuple[FeeEvaluationEditedManualRow, ...] = ()
    inactive_rows: tuple[FeeEvaluationEditedInactiveRow, ...] = ()


FeeEvaluationEditedRowIdentity = tuple[str, str, str, str, int]
FeeEvaluationManualRowIdentity = tuple[str, str, str, str]
REPORT_PREPARATION_MANUAL_IDENTITY: FeeEvaluationManualRowIdentity = (
    "report_preparation",
    "",
    "",
    "",
)


def edited_row_identity(
    row: FeeEvaluationEditedExportRow,
) -> FeeEvaluationEditedRowIdentity:
    """Return the stable identity used to match a frontend edit to a basic-fill line."""
    return (
        row.source_line_id.strip(),
        row.confirmed_group_id.strip(),
        row.confirmed_row_id.strip(),
        row.step_token.strip(),
        row.step_index,
    )


def basic_fill_line_identity(
    line: MatrixBasicFillLine,
) -> FeeEvaluationEditedRowIdentity:
    """Return the stable identity for one backend Matrix basic-fill line."""
    step_token = line.step_tokens[0].strip() if line.step_tokens else ""
    return (
        line.line_id,
        line.confirmed_group_id,
        line.confirmed_row_id,
        step_token,
        line.step_index,
    )


def edited_row_lookup(
    edited_values: FeeEvaluationEditedExportValues | None,
    basic_fill: MatrixBasicFillWorkbook,
) -> dict[FeeEvaluationEditedRowIdentity, FeeEvaluationEditedExportRow]:
    """Validate and index edited rows against backend Matrix basic-fill lineage."""
    if edited_values is None:
        return {}
    lookup: dict[FeeEvaluationEditedRowIdentity, FeeEvaluationEditedExportRow] = {}
    duplicates: list[FeeEvaluationEditedRowIdentity] = []
    for row in edited_values.rows:
        identity = edited_row_identity(row)
        if identity in lookup:
            duplicates.append(identity)
        lookup[identity] = row
    if duplicates:
        raise ValueError("Duplicate Fee Evaluation edited row identity.")

    allowed = {
        basic_fill_line_identity(line)
        for group in basic_fill.groups
        for line in group.lines
    }
    extra = sorted(identity for identity in lookup if identity not in allowed)
    if extra:
        raise ValueError("Fee Evaluation edited row identity was not found in Matrix basic fill.")
    return lookup


def manual_row_lookup(
    edited_values: FeeEvaluationEditedExportValues | None,
) -> dict[FeeEvaluationManualRowIdentity, FeeEvaluationEditedManualRow]:
    """Index manual edited rows by kind, rejecting duplicates."""
    if edited_values is None:
        return {}
    lookup: dict[FeeEvaluationManualRowIdentity, FeeEvaluationEditedManualRow] = {}
    for row in edited_values.manual_rows:
        key = manual_row_identity(row)
        if key in lookup:
            raise ValueError(f"Duplicate Fee Evaluation manual row identity: {key}")
        lookup[key] = row
    return lookup


def manual_row_identity(row: FeeEvaluationEditedManualRow) -> FeeEvaluationManualRowIdentity:
    """Return the stable identity for one manual Fee Evaluation row."""
    row_kind = row.row_kind.strip()
    if row_kind == "sample_preparation":
        return (
            row_kind,
            row.confirmed_group_id.strip(),
            row.group_key.strip(),
            row.group_label.strip(),
        )
    return (row_kind, "", "", "")


def sample_preparation_group_identity(
    group: MatrixBasicFillGroup,
) -> FeeEvaluationManualRowIdentity:
    """Return the manual-row identity for a group's Sample preparation row."""
    return (
        "sample_preparation",
        group.confirmed_group_id.strip(),
        group.group_key.strip(),
        group.group_label.strip(),
    )


def validate_supported_manual_rows(
    rows: Iterable[FeeEvaluationEditedManualRow],
    basic_fill: MatrixBasicFillWorkbook | None = None,
) -> None:
    """Reject manual rows that are not supported by the active Matrix basic-fill view."""
    allowed = {"report_preparation", "sample_preparation"}
    allowed_sample_identities: set[FeeEvaluationManualRowIdentity] = set()
    if basic_fill is not None:
        allowed_sample_identities = {
            sample_preparation_group_identity(group) for group in basic_fill.groups
        }
    for row in rows:
        row_kind = row.row_kind.strip()
        if row_kind not in allowed:
            raise ValueError(f"Unsupported Fee Evaluation manual row: {row.row_kind}")
        if row_kind != "sample_preparation":
            continue
        identity = manual_row_identity(row)
        if not all(identity[index] for index in (1, 2, 3)):
            raise ValueError(
                "Sample preparation manual row requires complete group identity."
            )
        if basic_fill is not None and identity not in allowed_sample_identities:
            raise ValueError(
                "Sample preparation manual row identity was not found in Matrix basic fill."
            )
