"""Build Matrix basic-fill Fee Evaluation workbook rows from confirmed authority."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, Protocol

from backend.domain import ConfirmedMatrixGroup, ConfirmedMatrixRow, ConfirmedMatrixSnapshot
from backend.modules.test_plan.matrix_step_sequence_validation import parse_step_tokens

MatrixBasicFillStatus = Literal["ready", "empty"]


class ConfirmedMatrixFeeTemplateBasicFillNotFoundError(LookupError):
    """Raised when no active confirmed Matrix authority exists for a project."""


class ConfirmedMatrixFeeTemplateBasicFillError(ValueError):
    """Raised when confirmed Matrix basic-fill data cannot be built."""


class ConfirmedMatrixAuthorityStore(Protocol):
    """Confirmed Matrix authority read operations required by basic-fill service."""

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        """Return one active confirmed authority aggregate in one project."""


@dataclass(frozen=True, slots=True)
class BuildMatrixBasicFeeTemplateCommand:
    """Input payload for Matrix basic-fill fee template generation."""

    project_id: str


@dataclass(frozen=True, slots=True)
class MatrixBasicFillHeader:
    """Top-level Matrix authority metadata for one basic-fill workbook."""

    project_id: str
    confirmed_matrix_id: str
    confirmed_revision: int
    generated_at: str


@dataclass(frozen=True, slots=True)
class MatrixBasicFillLine:
    """One selected/non-empty Matrix cell row for fee template basic fill."""

    line_id: str
    group_key: str
    group_label: str
    confirmed_group_id: str
    confirmed_row_id: str
    source_row_id: str | None
    row_order: int
    step_index: int
    test_item: str
    cell_value: str
    step_tokens: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MatrixBasicFillGroup:
    """One selected Confirmed Matrix group with basic-fill rows."""

    group_key: str
    group_label: str
    confirmed_group_id: str
    sample_quantity_expression: str
    lines: tuple[MatrixBasicFillLine, ...]


@dataclass(frozen=True, slots=True)
class MatrixBasicFillWorkbook:
    """Workbook-ready Matrix basic-fill content."""

    header: MatrixBasicFillHeader
    status: MatrixBasicFillStatus
    groups: tuple[MatrixBasicFillGroup, ...]


class ConfirmedMatrixFeeTemplateBasicFillService:
    """Build Matrix basic-fill rows directly from active Confirmed Matrix authority."""

    def __init__(self, *, confirmed_store: ConfirmedMatrixAuthorityStore) -> None:
        self._confirmed = confirmed_store

    def build(
        self, command: BuildMatrixBasicFeeTemplateCommand
    ) -> MatrixBasicFillWorkbook:
        """Return workbook-ready Matrix basic-fill content for a project."""
        snapshot = self._confirmed.get_active_by_project(command.project_id)
        if snapshot is None:
            raise ConfirmedMatrixFeeTemplateBasicFillNotFoundError(
                "Active confirmed matrix not found."
            )
        return build_basic_fill_from_confirmed_snapshot(snapshot)


def build_basic_fill_from_confirmed_snapshot(
    snapshot: ConfirmedMatrixSnapshot,
) -> MatrixBasicFillWorkbook:
    """Build Matrix basic-fill rows from an explicit Confirmed Matrix snapshot."""
    groups = _build_groups(snapshot)
    return MatrixBasicFillWorkbook(
        header=MatrixBasicFillHeader(
            project_id=snapshot.version.project_id,
            confirmed_matrix_id=snapshot.version.confirmed_matrix_id,
            confirmed_revision=snapshot.version.confirmed_revision,
            generated_at=datetime.now(timezone.utc).isoformat(),
        ),
        status="ready" if groups else "empty",
        groups=groups,
    )


def _build_groups(
    snapshot: ConfirmedMatrixSnapshot,
) -> tuple[MatrixBasicFillGroup, ...]:
    groups_by_id = {group.confirmed_group_id: group for group in snapshot.groups}
    rows_by_id = {row.confirmed_row_id: row for row in snapshot.rows}
    cell_lookup = _build_cell_lookup(
        snapshot=snapshot,
        groups_by_id=groups_by_id,
        rows_by_id=rows_by_id,
    )
    groups: list[MatrixBasicFillGroup] = []
    for group in snapshot.groups:
        lines = sorted(
            [
                line
                for row, value in _selected_rows_for_group(
                    group=group,
                    rows=snapshot.rows,
                    cell_lookup=cell_lookup,
                )
                for line in _lines_from_authority(
                    snapshot=snapshot, group=group, row=row, cell=value
                )
            ],
            key=_line_sort_key,
        )
        if not lines:
            continue
        groups.append(
            MatrixBasicFillGroup(
                group_key=group.group_key.strip(),
                group_label=group.group_label.strip(),
                confirmed_group_id=group.confirmed_group_id,
                sample_quantity_expression=_text(group.sample_quantity_expression),
                lines=tuple(lines),
            )
        )
    return tuple(groups)


def _build_cell_lookup(
    *,
    snapshot: ConfirmedMatrixSnapshot,
    groups_by_id: dict[str, ConfirmedMatrixGroup],
    rows_by_id: dict[str, ConfirmedMatrixRow],
) -> dict[tuple[str, str], str]:
    lookup: dict[tuple[str, str], str] = {}
    for cell in snapshot.cells:
        if cell.confirmed_group_id not in groups_by_id or cell.confirmed_row_id not in rows_by_id:
            raise ConfirmedMatrixFeeTemplateBasicFillError(
                "Confirmed matrix cell lineage is invalid."
            )
        value = _text(cell.cell_value)
        if value:
            lookup[(cell.confirmed_group_id, cell.confirmed_row_id)] = value
    return lookup


def _selected_rows_for_group(
    *,
    group: ConfirmedMatrixGroup,
    rows: tuple[ConfirmedMatrixRow, ...],
    cell_lookup: dict[tuple[str, str], str],
) -> list[tuple[ConfirmedMatrixRow, str]]:
    selected: list[tuple[ConfirmedMatrixRow, str]] = []
    for row in rows:
        value = cell_lookup.get((group.confirmed_group_id, row.confirmed_row_id))
        if value:
            selected.append((row, value))
    return selected


def _lines_from_authority(
    *,
    snapshot: ConfirmedMatrixSnapshot,
    group: ConfirmedMatrixGroup,
    row: ConfirmedMatrixRow,
    cell: str,
) -> tuple[MatrixBasicFillLine, ...]:
    parsed_tokens, _warnings = parse_step_tokens(cell)
    if not parsed_tokens:
        return (
            _line_from_authority(
                snapshot=snapshot,
                group=group,
                row=row,
                cell=cell,
                step_token=None,
                token_index=0,
            ),
        )
    return tuple(
        _line_from_authority(
            snapshot=snapshot,
            group=group,
            row=row,
            cell=cell,
            step_token=token.raw_token,
            token_index=index,
        )
        for index, token in enumerate(parsed_tokens)
    )


def _line_from_authority(
    *,
    snapshot: ConfirmedMatrixSnapshot,
    group: ConfirmedMatrixGroup,
    row: ConfirmedMatrixRow,
    cell: str,
    step_token: str | None,
    token_index: int,
) -> MatrixBasicFillLine:
    token_suffix = f":{step_token}:{token_index}" if step_token else ""
    return MatrixBasicFillLine(
        line_id=(
            f"{snapshot.version.confirmed_matrix_id}:"
            f"{group.group_key.strip()}:{row.confirmed_row_id}{token_suffix}"
        ),
        group_key=group.group_key.strip(),
        group_label=group.group_label.strip(),
        confirmed_group_id=group.confirmed_group_id,
        confirmed_row_id=row.confirmed_row_id,
        source_row_id=row.source_row_snapshot_id,
        row_order=row.row_order,
        step_index=token_index,
        test_item=_text(row.test_item),
        cell_value=cell,
        step_tokens=(step_token,) if step_token else (),
    )


def _line_sort_key(line: MatrixBasicFillLine) -> tuple[int, int, str]:
    if line.step_tokens:
        token = line.step_tokens[0].strip()
        if token.isdigit():
            return (int(token), line.row_order, line.line_id)
    return (10_000 + line.row_order, line.row_order, line.line_id)

def _text(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip()
