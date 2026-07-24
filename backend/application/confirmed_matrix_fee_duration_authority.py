"""Resolve exact confirmed Matrix duration authority for one Fee line."""

from __future__ import annotations

from decimal import Decimal

from backend.domain.confirmed_matrix_authority_models import (
    ConfirmedMatrixDurationAuthority,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
)
from backend.modules.fee_evaluation.fee_default_fill_models import (
    FeeDurationAuthority,
)


def resolve_confirmed_duration_authority(
    *,
    group: ConfirmedMatrixGroup,
    row: ConfirmedMatrixRow,
    step_sequence: int,
    step_suffix_note: str | None,
    authorities: tuple[ConfirmedMatrixDurationAuthority, ...],
    expected_confirmed_matrix_id: str,
) -> FeeDurationAuthority:
    """Return one exact usable authority or a typed fail-closed diagnostic."""
    suffix = _canonical_suffix(step_suffix_note)
    matches = tuple(
        authority
        for authority in authorities
        if authority.confirmed_matrix_id == expected_confirmed_matrix_id
        and authority.confirmed_group_id == group.confirmed_group_id
        and authority.confirmed_row_id == row.confirmed_row_id
        and authority.step_sequence == step_sequence
        and _canonical_suffix(authority.step_suffix_note) == suffix
    )
    if not matches:
        diagnostic = _identity_diagnostic(
            group=group,
            row=row,
            matrix_id=expected_confirmed_matrix_id,
            sequence=step_sequence,
            suffix=suffix,
            authorities=authorities,
        )
        return _invalid(
            group=group,
            row=row,
            matrix_id=expected_confirmed_matrix_id,
            sequence=step_sequence,
            suffix=suffix,
            diagnostic=diagnostic,
        )
    canonical_values = {
        (
            item.duration_value,
            item.duration_unit,
            item.normalized_hours,
            item.authority_revision,
            item.lineage_fingerprint,
            item.status,
        )
        for item in matches
    }
    if len(canonical_values) != 1:
        return _invalid(
            group=group,
            row=row,
            matrix_id=expected_confirmed_matrix_id,
            sequence=step_sequence,
            suffix=suffix,
            diagnostic="conflict",
        )
    authority = matches[0]
    diagnostic = _authority_diagnostic(authority)
    return FeeDurationAuthority(
        confirmed_matrix_id=authority.confirmed_matrix_id,
        confirmed_group_id=authority.confirmed_group_id,
        confirmed_row_id=authority.confirmed_row_id,
        step_sequence=authority.step_sequence,
        step_suffix_note=suffix,
        duration_value=authority.duration_value,
        duration_unit=authority.duration_unit,
        normalized_hours=authority.normalized_hours,
        authority_revision=authority.authority_revision,
        lineage_fingerprint=authority.lineage_fingerprint,
        status=authority.status,
        diagnostic=diagnostic,
    )


def _authority_diagnostic(authority: ConfirmedMatrixDurationAuthority) -> str | None:
    if authority.status != "usable":
        return authority.diagnostic_code or authority.status
    if not authority.authority_revision or not authority.lineage_fingerprint:
        return "missing_lineage"
    if (
        not isinstance(authority.normalized_hours, Decimal)
        or not authority.normalized_hours.is_finite()
        or authority.normalized_hours <= 0
    ):
        return "invalid"
    return authority.diagnostic_code


def _identity_diagnostic(
    *,
    group: ConfirmedMatrixGroup,
    row: ConfirmedMatrixRow,
    matrix_id: str,
    sequence: int,
    suffix: str,
    authorities: tuple[ConfirmedMatrixDurationAuthority, ...],
) -> str:
    same_step = tuple(
        item
        for item in authorities
        if item.confirmed_matrix_id == matrix_id
        and item.step_sequence == sequence
        and _canonical_suffix(item.step_suffix_note) == suffix
    )
    if any(
        item.confirmed_group_id == group.confirmed_group_id
        and item.confirmed_row_id != row.confirmed_row_id
        for item in same_step
    ):
        return "wrong_row"
    if any(
        item.confirmed_row_id == row.confirmed_row_id
        and item.confirmed_group_id != group.confirmed_group_id
        for item in same_step
    ):
        return "wrong_group"
    return "missing"


def _invalid(
    *,
    group: ConfirmedMatrixGroup,
    row: ConfirmedMatrixRow,
    matrix_id: str,
    sequence: int,
    suffix: str,
    diagnostic: str,
) -> FeeDurationAuthority:
    return FeeDurationAuthority(
        confirmed_matrix_id=matrix_id,
        confirmed_group_id=group.confirmed_group_id,
        confirmed_row_id=row.confirmed_row_id,
        step_sequence=sequence,
        step_suffix_note=suffix,
        duration_value=None,
        duration_unit=None,
        normalized_hours=None,
        authority_revision=None,
        lineage_fingerprint=None,
        status="review_required",
        diagnostic=diagnostic,
    )


def _canonical_suffix(value: str | None) -> str:
    return (value or "").strip()
