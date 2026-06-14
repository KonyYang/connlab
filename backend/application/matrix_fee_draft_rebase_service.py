"""Pure Matrix-to-Fee draft rebase helpers for TASK_315A."""

from __future__ import annotations

from dataclasses import dataclass, replace
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
    ) -> MatrixFeeRebaseResult:
        """Return rebased active rows, inactive rows, and manual rows."""
        source_lookup = _index_source_rows(source_rows)
        _assert_unique_target_rows(target_rows)
        used_source_keys: set[MatrixFeeRebaseKey] = set()
        active_rows: list[FeeEvaluationEditedExportRow] = []
        preserved_count = 0
        added_count = 0

        for target in target_rows:
            key = _key_for(target.lineage)
            source = source_lookup.get(key)
            if source is None:
                active_rows.append(target.default_row)
                added_count += 1
                continue
            active_rows.append(
                _copy_editable_fee_values(
                    source=source.edited_row,
                    target_default=target.default_row,
                )
            )
            used_source_keys.add(key)
            preserved_count += 1

        inactive_removed_rows = tuple(
            MatrixFeeInactiveRemovedRow(
                previous_row=row.edited_row,
                previous_group_key=row.lineage.group_key,
                previous_group_label=row.lineage.group_label,
                previous_row_signature=_row_signature(row.lineage),
            )
            for row in source_rows
            if _key_for(row.lineage) not in used_source_keys
        )
        manual_rows, preserved_manual_count, removed_manual_count = _rebase_manual_rows(
            source_manual_rows=source_manual_rows,
            target_groups=target_groups,
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
    source: FeeEvaluationEditedExportRow,
    target_default: FeeEvaluationEditedExportRow,
) -> FeeEvaluationEditedExportRow:
    """Copy only editable pricing fields from source onto target lineage."""
    return replace(
        target_default,
        spend_time=source.spend_time,
        unit_price=source.unit_price,
        unit_type=source.unit_type,
        units=source.units,
        base_fee=source.base_fee,
        discount=source.discount,
        testing_fee=source.testing_fee,
        notes=source.notes,
    )


def _rebase_manual_rows(
    *,
    source_manual_rows: tuple[FeeEvaluationEditedManualRow, ...],
    target_groups: tuple[MatrixFeeRebaseTargetGroup, ...],
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
        rows.append(
            replace(
                row,
                confirmed_group_id=target_group.confirmed_group_id,
                group_key=target_group.group_key,
                group_label=target_group.group_label,
            )
        )
        preserved_count += 1
    return tuple(rows), preserved_count, removed_count


def _index_source_rows(
    source_rows: tuple[MatrixFeeRebaseSourceRow, ...],
) -> dict[MatrixFeeRebaseKey, MatrixFeeRebaseSourceRow]:
    lookup: dict[MatrixFeeRebaseKey, MatrixFeeRebaseSourceRow] = {}
    for row in source_rows:
        key = _key_for(row.lineage)
        if key in lookup:
            raise MatrixFeeRebaseKeyConflictError(
                "Duplicate source Matrix-to-Fee rebase key."
            )
        lookup[key] = row
    return lookup


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
