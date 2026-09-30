"""Pure Matrix-to-Fee draft rebase helpers for TASK_315A."""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re

from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedManualRow,
)


class MatrixFeeRebaseKeyConflictError(ValueError):
    """Raised when rebase identities are ambiguous and would lose Fee edits."""


@dataclass(frozen=True, slots=True)
class MatrixFeeRebaseKey:
    """Stable V1 key used to match one Matrix Fee row across draft changes."""

    group_identity: str
    row_identity: str
    step_token: str
    step_index: int


@dataclass(frozen=True, slots=True)
class MatrixFeeRebaseLineage:
    """Matrix row/group metadata needed to build a Fee rebase key."""

    group_key: str
    group_label: str
    confirmed_group_id: str
    confirmed_row_id: str
    source_row_snapshot_id: str | None
    draft_row_id: str | None
    step_token: str
    step_index: int
    test_item: str
    source_section: str | None = None
    method: str | None = None
    condition: str | None = None
    requirement: str | None = None


@dataclass(frozen=True, slots=True)
class MatrixFeeRebaseSourceRow:
    """One source Fee row plus the Matrix lineage it came from."""

    lineage: MatrixFeeRebaseLineage
    edited_row: FeeEvaluationEditedExportRow
    rebase_key: MatrixFeeRebaseKey | None = None
    default_row: FeeEvaluationEditedExportRow | None = None


@dataclass(frozen=True, slots=True)
class MatrixFeeRebaseTargetRow:
    """One target Matrix row plus its default Fee values."""

    lineage: MatrixFeeRebaseLineage
    default_row: FeeEvaluationEditedExportRow


@dataclass(frozen=True, slots=True)
class MatrixFeeRebaseTargetGroup:
    """One target Matrix group available for manual-row rebasing."""

    confirmed_group_id: str
    group_key: str
    group_label: str


@dataclass(frozen=True, slots=True)
class MatrixFeeInactiveRemovedRow:
    """Review-only previous Fee row whose Matrix source no longer exists."""

    previous_row: FeeEvaluationEditedExportRow
    rebase_key: MatrixFeeRebaseKey
    previous_group_key: str
    previous_group_label: str
    previous_row_signature: str
    inactive_reason: str = "removed_from_matrix"


@dataclass(frozen=True, slots=True)
class MatrixFeeRebaseSummary:
    """Counts produced by one pure Matrix-to-Fee rebase run."""

    preserved_count: int
    added_count: int
    removed_count: int
    preserved_manual_count: int = 0
    removed_manual_count: int = 0


@dataclass(frozen=True, slots=True)
class MatrixFeeRebaseResult:
    """Complete in-memory output of TASK_315A rebase core."""

    active_rows: tuple[FeeEvaluationEditedExportRow, ...]
    inactive_removed_rows: tuple[MatrixFeeInactiveRemovedRow, ...]
    manual_rows: tuple[FeeEvaluationEditedManualRow, ...]
    summary: MatrixFeeRebaseSummary
    warnings: tuple[str, ...] = ()


class MatrixFeeDraftRebaseService:
    """Rebase Fee draft edits from source Matrix rows to target Matrix rows."""

    def rebase(
        self,
        *,
        source_rows: tuple[MatrixFeeRebaseSourceRow, ...],
        target_rows: tuple[MatrixFeeRebaseTargetRow, ...],
        source_manual_rows: tuple[FeeEvaluationEditedManualRow, ...],
        target_groups: tuple[MatrixFeeRebaseTargetGroup, ...],
        source_manual_defaults: tuple[FeeEvaluationEditedManualRow, ...] = (),
        target_manual_defaults: tuple[FeeEvaluationEditedManualRow, ...] = (),
    ) -> MatrixFeeRebaseResult:
        """Return rebased active rows, inactive rows, and manual rows."""
        source_lookup = _index_source_rows(source_rows)
        _assert_unique_target_rows(target_rows)
        unique_sources = _unique_strong_row_sources(source_rows)
        target_row_counts: dict[tuple[str, str], int] = {}
        for target in target_rows:
            target_key = _key_for(target.lineage)
            bucket = (target_key.group_identity, target_key.row_identity)
            target_row_counts[bucket] = target_row_counts.get(bucket, 0) + 1
        used_source_keys: set[MatrixFeeRebaseKey] = set()
        active_rows: list[FeeEvaluationEditedExportRow] = []
        preserved_count = 0
        added_count = 0

        for target in target_rows:
            key = _key_for(target.lineage)
            source = source_lookup.get(key)
            if source is None and target_row_counts[(key.group_identity, key.row_identity)] == 1:
                source = unique_sources.get((key.group_identity, key.row_identity))
            if source is None:
                active_rows.append(target.default_row)
                added_count += 1
                continue
            active_rows.append(
                _copy_editable_fee_values(
                    source=source.edited_row,
                    target_default=target.default_row,
                    source_default=source.default_row,
                )
            )
            used_source_keys.add(_source_key(source))
            preserved_count += 1

        inactive_removed_rows = tuple(
            MatrixFeeInactiveRemovedRow(
                previous_row=row.edited_row,
                rebase_key=_source_key(row),
                previous_group_key=row.lineage.group_key,
                previous_group_label=row.lineage.group_label,
                previous_row_signature=_row_signature(row.lineage),
            )
            for row in source_rows
            if _source_key(row) not in used_source_keys
        )
        manual_rows, preserved_manual_count, removed_manual_count = _rebase_manual_rows(
            source_manual_rows=source_manual_rows,
            target_groups=target_groups,
            source_manual_defaults=source_manual_defaults,
            target_manual_defaults=target_manual_defaults,
        )
        return MatrixFeeRebaseResult(
            active_rows=tuple(active_rows),
            inactive_removed_rows=inactive_removed_rows,
            manual_rows=manual_rows,
            summary=MatrixFeeRebaseSummary(
                preserved_count=preserved_count,
                added_count=added_count,
                removed_count=len(inactive_removed_rows),
                preserved_manual_count=preserved_manual_count,
                removed_manual_count=removed_manual_count,
            ),
        )


def _key_for(lineage: MatrixFeeRebaseLineage) -> MatrixFeeRebaseKey:
    """Build the V1 Matrix-to-Fee rebase key for one row lineage."""
    return matrix_fee_rebase_key_for_lineage(lineage)


def matrix_fee_rebase_key_for_lineage(
    lineage: MatrixFeeRebaseLineage,
) -> MatrixFeeRebaseKey:
    """Build the stable Matrix-to-Fee rebase key for one row lineage."""
    return MatrixFeeRebaseKey(
        group_identity=_group_identity(lineage.group_key, lineage.group_label),
        row_identity=_row_identity(lineage),
        step_token=_normalize(lineage.step_token),
        step_index=lineage.step_index,
    )


def _group_identity(group_key: str, group_label: str) -> str:
    key = _normalize(group_key)
    if key:
        return f"key:{key}"
    return f"label:{_normalize(group_label)}"


def _row_identity(lineage: MatrixFeeRebaseLineage) -> str:
    source_id = _normalize(lineage.source_row_snapshot_id)
    if source_id:
        return f"source:{source_id}"
    draft_id = _normalize(lineage.draft_row_id)
    if draft_id:
        return f"draft:{draft_id}"
    return f"signature:{_row_signature(lineage)}"


def _row_signature(lineage: MatrixFeeRebaseLineage) -> str:
    parts = (
        lineage.test_item,
        lineage.source_section or "",
        lineage.method or "",
        lineage.condition or "",
        lineage.requirement or "",
    )
    return "|".join(_normalize(part) for part in parts)


def _copy_editable_fee_values(
    *,
    source: FeeEvaluationEditedExportRow | FeeEvaluationEditedManualRow,
    target_default: FeeEvaluationEditedExportRow | FeeEvaluationEditedManualRow,
    source_default: FeeEvaluationEditedExportRow | FeeEvaluationEditedManualRow | None,
) -> FeeEvaluationEditedExportRow | FeeEvaluationEditedManualRow:
    """Copy only editable pricing fields from source onto target lineage."""
    units = source.units
    testing_fee = source.testing_fee
    if (
        source_default is not None
        and _quantity_changed(source_default.units, target_default.units)
        and _quantity_dependent(source.unit_type)
        and _unit_type_key(source.unit_type) == _unit_type_key(target_default.unit_type)
    ):
        units = target_default.units
        testing_fee = _recalculate_testing_fee(source, units) or target_default.testing_fee
    return replace(
        target_default,
        spend_time=source.spend_time,
        unit_price=source.unit_price,
        unit_type=source.unit_type,
        units=units,
        base_fee=source.base_fee,
        discount=source.discount,
        testing_fee=testing_fee,
        notes=source.notes,
    )


def _quantity_changed(previous: str, current: str) -> bool:
    try:
        return Decimal(previous) != Decimal(current)
    except InvalidOperation:
        return False


def _quantity_dependent(unit_type: str) -> bool:
    return _unit_type_key(unit_type) in {
        "sample", "specimen", "reading", "point", "hour", "day", "cycle"
    }


def _unit_type_key(unit_type: str) -> str:
    return _normalize(unit_type).removeprefix("per ")


def _recalculate_testing_fee(
    row: FeeEvaluationEditedExportRow | FeeEvaluationEditedManualRow, units: str,
) -> str | None:
    try:
        price = Decimal(row.unit_price)
        quantity = Decimal(units)
        base_fee = Decimal(row.base_fee)
        discount = Decimal(row.discount.strip().rstrip("%"))
    except InvalidOperation:
        return None
    amount = (
        price * quantity * (Decimal("1") - discount / Decimal("100")) + base_fee
    ).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return format(amount, "f")


def _rebase_manual_rows(
    *,
    source_manual_rows: tuple[FeeEvaluationEditedManualRow, ...],
    target_groups: tuple[MatrixFeeRebaseTargetGroup, ...],
    source_manual_defaults: tuple[FeeEvaluationEditedManualRow, ...],
    target_manual_defaults: tuple[FeeEvaluationEditedManualRow, ...],
) -> tuple[tuple[FeeEvaluationEditedManualRow, ...], int, int]:
    target_by_key, target_by_label = _index_target_groups(target_groups)
    rows: list[FeeEvaluationEditedManualRow] = []
    preserved_count = 0
    removed_count = 0
    for row in source_manual_rows:
        row_kind = row.row_kind.strip()
        if row_kind == "report_preparation":
            rows.append(row)
            preserved_count += 1
            continue
        if row_kind != "sample_preparation":
            continue
        target_group = _find_target_group(row, target_by_key, target_by_label)
        if target_group is None:
            removed_count += 1
            continue
        target_row = replace(
            row,
            confirmed_group_id=target_group.confirmed_group_id,
            group_key=target_group.group_key,
            group_label=target_group.group_label,
        )
        source_default = _manual_default_for(row, source_manual_defaults)
        target_default = _manual_default_for(target_row, target_manual_defaults)
        if source_default is not None and target_default is not None:
            target_row = _copy_editable_fee_values(
                source=target_row, target_default=target_default,
                source_default=source_default,
            )
        rows.append(target_row)
        preserved_count += 1
    return tuple(rows), preserved_count, removed_count


def _manual_default_for(
    row: FeeEvaluationEditedManualRow,
    candidates: tuple[FeeEvaluationEditedManualRow, ...],
) -> FeeEvaluationEditedManualRow | None:
    identity = _normalize(row.group_key) or _normalize(row.group_label)
    return next(
        (candidate for candidate in candidates
         if candidate.row_kind == row.row_kind
         and (_normalize(candidate.group_key) or _normalize(candidate.group_label)) == identity),
        None,
    )


def _index_source_rows(
    source_rows: tuple[MatrixFeeRebaseSourceRow, ...],
) -> dict[MatrixFeeRebaseKey, MatrixFeeRebaseSourceRow]:
    lookup: dict[MatrixFeeRebaseKey, MatrixFeeRebaseSourceRow] = {}
    for row in source_rows:
        key = _source_key(row)
        if key in lookup:
            raise MatrixFeeRebaseKeyConflictError(
                "Duplicate source Matrix-to-Fee rebase key."
            )
        lookup[key] = row
    return lookup


def _unique_strong_row_sources(
    source_rows: tuple[MatrixFeeRebaseSourceRow, ...],
) -> dict[tuple[str, str], MatrixFeeRebaseSourceRow]:
    grouped: dict[tuple[str, str], list[MatrixFeeRebaseSourceRow]] = {}
    for source in source_rows:
        key = _source_key(source)
        if key.row_identity.startswith(("source:", "draft:")):
            grouped.setdefault((key.group_identity, key.row_identity), []).append(source)
    return {key: rows[0] for key, rows in grouped.items() if len(rows) == 1}


def _source_key(row: MatrixFeeRebaseSourceRow) -> MatrixFeeRebaseKey:
    """Return explicit or lineage-derived source rebase key."""
    return row.rebase_key or _key_for(row.lineage)


def _assert_unique_target_rows(
    target_rows: tuple[MatrixFeeRebaseTargetRow, ...],
) -> None:
    seen: set[MatrixFeeRebaseKey] = set()
    for row in target_rows:
        key = _key_for(row.lineage)
        if key in seen:
            raise MatrixFeeRebaseKeyConflictError(
                "Duplicate target Matrix-to-Fee rebase key."
            )
        seen.add(key)


def _index_target_groups(
    target_groups: tuple[MatrixFeeRebaseTargetGroup, ...],
) -> tuple[
    dict[str, MatrixFeeRebaseTargetGroup],
    dict[str, MatrixFeeRebaseTargetGroup],
]:
    target_by_key: dict[str, MatrixFeeRebaseTargetGroup] = {}
    target_by_label: dict[str, MatrixFeeRebaseTargetGroup] = {}
    for group in target_groups:
        key = _normalize(group.group_key)
        if key:
            if key in target_by_key:
                raise MatrixFeeRebaseKeyConflictError(
                    "Duplicate target Matrix group key for manual-row rebase."
                )
            target_by_key[key] = group

        label = _normalize(group.group_label)
        if label:
            if label in target_by_label:
                raise MatrixFeeRebaseKeyConflictError(
                    "Duplicate target Matrix group label for manual-row rebase."
                )
            target_by_label[label] = group
    return target_by_key, target_by_label


def _find_target_group(
    row: FeeEvaluationEditedManualRow,
    target_by_key: dict[str, MatrixFeeRebaseTargetGroup],
    target_by_label: dict[str, MatrixFeeRebaseTargetGroup],
) -> MatrixFeeRebaseTargetGroup | None:
    row_key = _normalize(row.group_key)
    if row_key and row_key in target_by_key:
        return target_by_key[row_key]
    row_label = _normalize(row.group_label)
    if row_label:
        return target_by_label.get(row_label)
    return None


def _normalize(value: str | None) -> str:
    """Normalize human-entered identity text for deterministic matching."""
    if value is None:
        return ""
    return re.sub(r"\s+", " ", value.strip()).casefold()
