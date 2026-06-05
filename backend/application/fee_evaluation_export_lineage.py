"""Lineage helpers for Fee Evaluation workbook exports."""

from __future__ import annotations

from dataclasses import dataclass
import json

from backend.application.confirmed_matrix_fee_draft_service import FeeEvaluationDraft
from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    MatrixBasicFillWorkbook,
)


@dataclass(frozen=True, slots=True)
class FeeEvaluationExportLineTrace:
    """Traceability metadata for one exported fee draft line."""

    line_id: str
    group_key: str
    group_label: str
    confirmed_group_id: str
    confirmed_row_id: str
    source_row_id: str | None
    row_order: int
    matched_rule_id: str | None
    matched_rule_version_id: str | None
    step_tokens: tuple[str, ...]
    cell_value: str | None = None


def line_traceability(
    draft: FeeEvaluationDraft,
) -> tuple[FeeEvaluationExportLineTrace, ...]:
    """Return stable line-level export lineage from a fee draft."""
    return tuple(
        FeeEvaluationExportLineTrace(
            line_id=line.line_id,
            group_key=line.group_key,
            group_label=line.group_label,
            confirmed_group_id=line.confirmed_group_id,
            confirmed_row_id=line.confirmed_row_id,
            source_row_id=line.source_row_id,
            row_order=line.row_order,
            matched_rule_id=line.matched_rule_id,
            matched_rule_version_id=line.matched_rule_version_id,
            step_tokens=line.step_tokens,
            cell_value=None,
        )
        for group in draft.groups
        for line in group.line_items
    )


def lineage_note(draft: FeeEvaluationDraft) -> str:
    """Build an output-record note with header and line-level lineage."""
    parts = [
        f"confirmed_matrix_id={draft.header.confirmed_matrix_id}",
        f"confirmed_revision={draft.header.confirmed_revision}",
        f"fee_rule_version_id={draft.header.pricing_rule_version_id}",
        f"pricing_effective_from={draft.header.pricing_effective_from or ''}",
    ]
    for trace in line_traceability(draft):
        parts.append(
            "line_trace="
            f"line_id={trace.line_id},"
            f"group_key={trace.group_key},"
            f"confirmed_group_id={trace.confirmed_group_id},"
            f"confirmed_row_id={trace.confirmed_row_id},"
            f"source_row_id={trace.source_row_id or ''},"
            f"row_order={trace.row_order},"
            f"matched_rule_id={trace.matched_rule_id or ''},"
            f"matched_rule_version_id={trace.matched_rule_version_id or ''},"
            f"step_tokens={'|'.join(trace.step_tokens)}"
        )
    return "; ".join(parts)


def matrix_basic_line_traceability(
    basic_fill: MatrixBasicFillWorkbook,
) -> tuple[FeeEvaluationExportLineTrace, ...]:
    """Return line-level lineage for Matrix basic-fill rows."""
    return tuple(
        FeeEvaluationExportLineTrace(
            line_id=line.line_id,
            group_key=line.group_key,
            group_label=line.group_label,
            confirmed_group_id=line.confirmed_group_id,
            confirmed_row_id=line.confirmed_row_id,
            source_row_id=line.source_row_id,
            row_order=line.row_order,
            matched_rule_id=None,
            matched_rule_version_id=None,
            step_tokens=line.step_tokens,
            cell_value=line.cell_value,
        )
        for group in basic_fill.groups
        for line in group.lines
    )


def matrix_basic_lineage_note(
    *,
    basic_fill: MatrixBasicFillWorkbook,
    pricing_requires_review: bool,
) -> str:
    """Build an output-record note for Matrix basic-fill exports."""
    parts = [
        "fill_mode=matrix_basic",
        "source=active_confirmed_matrix_authority",
        "matrix_basic_fill_only=true",
        f"pricing_requires_review={str(pricing_requires_review).lower()}",
        f"confirmed_matrix_id={basic_fill.header.confirmed_matrix_id}",
        f"confirmed_revision={basic_fill.header.confirmed_revision}",
    ]
    for trace in matrix_basic_line_traceability(basic_fill):
        parts.append(
            "line_trace="
            f"line_id={trace.line_id},"
            f"group_key={trace.group_key},"
            f"confirmed_group_id={trace.confirmed_group_id},"
            f"confirmed_row_id={trace.confirmed_row_id},"
            f"source_row_id={trace.source_row_id or ''},"
            f"row_order={trace.row_order},"
            f"cell_value={_note_json(trace.cell_value or '')},"
            "matched_rule_id=,"
            "matched_rule_version_id=,"
            "step_tokens="
        )
    return "; ".join(parts)


def _note_json(value: str) -> str:
    """Return delimiter-safe JSON text for one note field value."""
    return json.dumps(value, ensure_ascii=False)
