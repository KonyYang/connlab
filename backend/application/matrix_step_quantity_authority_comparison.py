"""Canonical comparison for Matrix Step quantity authority."""

from __future__ import annotations

from backend.domain import (
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStepQuantity,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStepQuantity,
)
from backend.modules.test_plan.matrix_step_sequence_validation import parse_step_tokens


def step_quantity_authority_matches(
    draft: ProjectMatrixDraftSnapshot,
    confirmed: ConfirmedMatrixSnapshot,
) -> bool:
    """Compare meaningful quantity/contact authority without storage identity noise."""
    return canonical_draft_step_quantities(draft) == canonical_confirmed_step_quantities(
        confirmed
    )


def canonical_draft_step_quantities(
    draft: ProjectMatrixDraftSnapshot,
) -> tuple[tuple[object, ...], ...]:
    """Return canonical persisted draft quantities that can promote to authority."""
    group_orders = {
        group.draft_group_id: group.group_order
        for group in draft.groups
        if group.is_selected
    }
    row_orders = {
        row.draft_row_id: row.row_order for row in draft.rows if not row.is_sample_row
    }
    valid_identities = _draft_step_identities(draft, group_orders, row_orders)
    entries = (
        _canonical_quantity(
            group_order=group_orders.get(quantity.draft_group_id),
            row_order=row_orders.get(quantity.draft_row_id),
            quantity=quantity,
        )
        for quantity in draft.step_quantities
        if (
            group_orders.get(quantity.draft_group_id),
            row_orders.get(quantity.draft_row_id),
            quantity.step_sequence,
            _normalized_optional_text(quantity.step_suffix_note),
        )
        in valid_identities
    )
    return tuple(sorted(entries))


def canonical_confirmed_step_quantities(
    confirmed: ConfirmedMatrixSnapshot,
) -> tuple[tuple[object, ...], ...]:
    """Return canonical active authority quantities without generated ids or timestamps."""
    group_orders = {
        group.confirmed_group_id: group.group_order for group in confirmed.groups
    }
    row_orders = {row.confirmed_row_id: row.row_order for row in confirmed.rows}
    entries = (
        _canonical_quantity(
            group_order=group_orders.get(quantity.confirmed_group_id),
            row_order=row_orders.get(quantity.confirmed_row_id),
            quantity=quantity,
        )
        for quantity in confirmed.step_quantities
        if group_orders.get(quantity.confirmed_group_id) is not None
        and row_orders.get(quantity.confirmed_row_id) is not None
    )
    return tuple(sorted(entries))


def _draft_step_identities(
    draft: ProjectMatrixDraftSnapshot,
    group_orders: dict[str, int],
    row_orders: dict[str, int],
) -> set[tuple[int, int, int, str]]:
    identities: set[tuple[int, int, int, str]] = set()
    for cell in draft.cells:
        group_order = group_orders.get(cell.draft_group_id)
        row_order = row_orders.get(cell.draft_row_id)
        if group_order is None or row_order is None:
            continue
        tokens, _warnings = parse_step_tokens(cell.cell_value)
        for token in tokens:
            identities.add(
                (
                    group_order,
                    row_order,
                    token.sequence,
                    _normalized_optional_text(token.suffix_note),
                )
            )
    return identities


def _canonical_quantity(
    *,
    group_order: int | None,
    row_order: int | None,
    quantity: ProjectMatrixDraftStepQuantity | ConfirmedMatrixStepQuantity,
) -> tuple[object, ...]:
    if group_order is None or row_order is None:
        raise ValueError("Quantity authority identity is incomplete.")
    return (
        group_order,
        row_order,
        quantity.step_sequence,
        _normalized_optional_text(quantity.step_suffix_note),
        _normalized_optional_text(quantity.test_points_per_sample),
        _normalized_optional_text(quantity.readings_per_point),
        _normalized_optional_text(quantity.contact_points_per_sample),
        quantity.source.strip(),
        bool(quantity.review_required),
        _normalized_optional_text(quantity.review_reason),
        _canonical_contact_plan(quantity.contact_plan),
    )


def _canonical_contact_plan(plan: object | None) -> tuple[object, ...] | None:
    if plan is None:
        return None
    families = tuple(
        (
            family.family_id.strip(),
            family.family_label.strip(),
            _normalized_optional_text(family.count_per_sample),
            family.record_label.strip(),
            family.record_prefix.strip(),
            bool(family.included),
            bool(family.is_custom),
        )
        for family in plan.families
    )
    return (
        plan.contact_kind.strip(),
        plan.coverage_status.strip(),
        bool(plan.included),
        _normalized_optional_text(plan.exclusion_reason),
        bool(plan.is_override),
        _normalized_optional_text(plan.readings_per_sample),
        families,
    )


def _normalized_optional_text(value: str | None) -> str:
    return (value or "").strip()
