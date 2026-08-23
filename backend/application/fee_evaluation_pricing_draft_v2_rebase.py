"""Reviewed V2 Fee pricing-draft merge helpers."""

from __future__ import annotations

from dataclasses import replace
from collections.abc import Mapping

from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedManualRow,
    FeeEvaluationEditedExportValues,
    edited_row_identity,
    manual_row_identity,
)

_MANUAL_FIELDS = ("spend_time", "unit_price", "unit_type", "base_fee", "discount", "notes")


def rebase_reviewed_values(
    *, saved: FeeEvaluationEditedExportValues,
    current_defaults: FeeEvaluationEditedExportValues,
    row_provenance: Mapping[str, tuple[str, ...]] | None = None,
) -> FeeEvaluationEditedExportValues:
    """Refresh automatic units/testing fees while retaining compatible manual fields."""
    saved_rows = {edited_row_identity(row): row for row in saved.rows}
    rows = tuple(
        _merge_row(
            default_row,
            saved_rows.get(edited_row_identity(default_row)),
            preserved_fields=(
                row_provenance.get(default_row.source_line_id)
                if row_provenance is not None
                else None
            ),
        )
        for default_row in current_defaults.rows
    )
    saved_manual = {manual_row_identity(row): row for row in saved.manual_rows}
    manual_rows = tuple(
        _merge_manual_row(
            default_row,
            saved_manual.get(manual_row_identity(default_row)),
        )
        for default_row in current_defaults.manual_rows
    )
    return FeeEvaluationEditedExportValues(
        rows=rows,
        summary=saved.summary,
        manual_rows=manual_rows,
        inactive_rows=saved.inactive_rows,
    )


def _merge_row(
    default: FeeEvaluationEditedExportRow,
    saved: FeeEvaluationEditedExportRow | None,
    preserved_fields: tuple[str, ...] | None,
) -> FeeEvaluationEditedExportRow:
    if saved is None:
        return default
    fields = preserved_fields if preserved_fields is not None else _MANUAL_FIELDS
    return replace(
        default,
        **{field: getattr(saved, field) for field in _MANUAL_FIELDS if field in fields},
    )


def _merge_manual_row(
    default: FeeEvaluationEditedManualRow,
    saved: FeeEvaluationEditedManualRow | None,
) -> FeeEvaluationEditedManualRow:
    if saved is None or default.row_kind.strip() != "sample_preparation":
        return saved if saved is not None else default
    return replace(
        default,
        **{field: getattr(saved, field) for field in _MANUAL_FIELDS},
    )
