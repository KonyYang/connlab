"""Helpers for copying Matrix Step quantities into authority snapshots."""

from __future__ import annotations

from uuid import uuid4

from backend.domain import (
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStepQuantity,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStepQuantity,
)
from backend.modules.test_plan.matrix_step_sequence_validation import parse_step_tokens


def carry_forward_step_quantities(
    *,
    active: ConfirmedMatrixSnapshot,
    draft_id: str,
    group_id_map: dict[str, str],
    row_id_map: dict[str, str],
    updated_at: str,
) -> list[ProjectMatrixDraftStepQuantity]:
    """Carry confirmed Step quantities into a revision draft when lineage is stable."""
    carried: list[ProjectMatrixDraftStepQuantity] = []
    for quantity in active.step_quantities:
        draft_group_id = group_id_map.get(quantity.confirmed_group_id)
        draft_row_id = row_id_map.get(quantity.confirmed_row_id)
        if draft_group_id is None or draft_row_id is None:
            continue
        carried.append(
            ProjectMatrixDraftStepQuantity(
                draft_step_quantity_id=f"pmdsq-{uuid4().hex}",
                project_matrix_draft_id=draft_id,
                draft_group_id=draft_group_id,
                draft_row_id=draft_row_id,
                step_sequence=quantity.step_sequence,
                step_suffix_note=quantity.step_suffix_note,
                raw_token=quantity.raw_token,
                test_points_per_sample=quantity.test_points_per_sample,
                readings_per_point=quantity.readings_per_point,
                contact_points_per_sample=quantity.contact_points_per_sample,
                source="confirmed_matrix_carry_forward",
                review_required=quantity.review_required,
                review_reason=quantity.review_reason,
                updated_at=updated_at,
                contact_plan=quantity.contact_plan,
            )
        )
    return carried


def build_confirmed_step_quantities(
    *,
    draft: ProjectMatrixDraftSnapshot,
    confirmed_matrix_id: str,
    confirmed_at: str,
    confirmed_group_id_by_draft_group: dict[str, str],
    confirmed_row_id_by_draft_row: dict[str, str],
) -> list[ConfirmedMatrixStepQuantity]:
    """Copy draft Step quantity setup into confirmed authority records."""
    quantity_by_identity = {
        (
            item.draft_group_id,
            item.draft_row_id,
            item.step_sequence,
            item.step_suffix_note,
        ): item
        for item in draft.step_quantities
    }
    rows_by_id = {row.draft_row_id: row for row in draft.rows if not row.is_sample_row}
    confirmed: list[ConfirmedMatrixStepQuantity] = []
    seen: set[tuple[str, str, int, str | None]] = set()
    for cell in draft.cells:
        confirmed_group_id = confirmed_group_id_by_draft_group.get(cell.draft_group_id)
        confirmed_row_id = confirmed_row_id_by_draft_row.get(cell.draft_row_id)
        if confirmed_group_id is None or confirmed_row_id is None:
            continue
        if cell.draft_row_id not in rows_by_id:
            continue
        parsed_tokens, _warnings = parse_step_tokens(cell.cell_value)
        for token in parsed_tokens:
            identity = (
                cell.draft_group_id,
                cell.draft_row_id,
                token.sequence,
                token.suffix_note,
            )
            if identity in seen:
                continue
            seen.add(identity)
            draft_quantity = quantity_by_identity.get(identity)
            confirmed.append(
                ConfirmedMatrixStepQuantity(
                    confirmed_step_quantity_id=f"cmsq-{uuid4().hex}",
                    confirmed_matrix_id=confirmed_matrix_id,
                    confirmed_group_id=confirmed_group_id,
                    confirmed_row_id=confirmed_row_id,
                    draft_group_id=cell.draft_group_id,
                    draft_row_id=cell.draft_row_id,
                    step_sequence=token.sequence,
                    step_suffix_note=token.suffix_note,
                    raw_token=token.raw_token,
                    test_points_per_sample=draft_quantity.test_points_per_sample
                    if draft_quantity
                    else None,
                    readings_per_point=draft_quantity.readings_per_point
                    if draft_quantity
                    else None,
                    contact_points_per_sample=(
                        draft_quantity.contact_points_per_sample if draft_quantity else None
                    ),
                    source=draft_quantity.source if draft_quantity else "manual_required",
                    review_required=draft_quantity.review_required if draft_quantity else True,
                    review_reason=draft_quantity.review_reason
                    if draft_quantity
                    else "Quantity setup not confirmed.",
                    confirmed_at=confirmed_at,
                    contact_plan=draft_quantity.contact_plan if draft_quantity else None,
                )
            )
    return confirmed
