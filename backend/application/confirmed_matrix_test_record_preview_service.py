"""Build read-only Test Record preview from active Confirmed Matrix authority."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from backend.domain import ConfirmedMatrixSnapshot
from backend.modules.test_plan.matrix_step_sequence_validation import parse_step_tokens


class ConfirmedMatrixTestRecordPreviewError(ValueError):
    """Raised when confirmed authority data cannot be mapped into preview output."""


class ConfirmedMatrixTestRecordPreviewNotFoundError(LookupError):
    """Raised when no active confirmed Matrix authority exists for a project."""


class ConfirmedMatrixAuthorityStore(Protocol):
    """Confirmed Matrix authority read operations required by this consumer."""

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        """Return one active confirmed authority aggregate in one project."""


@dataclass(frozen=True, slots=True)
class BuildConfirmedMatrixTestRecordPreviewCommand:
    """Input payload for confirmed-authority Test Record preview building."""

    project_id: str


@dataclass(frozen=True, slots=True)
class ConfirmedMatrixTestRecordPreviewStep:
    """One preview step row derived from a parsed confirmed sparse cell token."""

    sequence: int
    raw_token: str
    test_item: str
    section: str
    method: str
    condition: str
    requirement: str


@dataclass(frozen=True, slots=True)
class ConfirmedMatrixTestRecordPreviewGroup:
    """One preview group with ordered step rows."""

    group_key: str
    group_label: str
    sample_quantity_expression: str
    step_count: int
    steps: tuple[ConfirmedMatrixTestRecordPreviewStep, ...]


@dataclass(frozen=True, slots=True)
class ConfirmedMatrixTestRecordPreview:
    """Top-level read-only Test Record preview payload."""

    project_id: str
    confirmed_matrix_id: str
    preview_status: str
    groups: tuple[ConfirmedMatrixTestRecordPreviewGroup, ...]


class ConfirmedMatrixTestRecordPreviewService:
    """Map active confirmed Matrix authority into Test Record preview rows."""

    def __init__(self, *, confirmed_store: ConfirmedMatrixAuthorityStore) -> None:
        self._confirmed = confirmed_store

    def build_preview(
        self,
        command: BuildConfirmedMatrixTestRecordPreviewCommand,
    ) -> ConfirmedMatrixTestRecordPreview:
        """Return one Test Record preview snapshot for a project."""
        snapshot = self._confirmed.get_active_by_project(command.project_id)
        if snapshot is None:
            raise ConfirmedMatrixTestRecordPreviewNotFoundError(
                "Active confirmed matrix not found."
            )

        groups_by_id = {group.confirmed_group_id: group for group in snapshot.groups}
        rows_by_id = {row.confirmed_row_id: row for row in snapshot.rows}
        cell_lookup = _build_cell_lookup(snapshot=snapshot, groups_by_id=groups_by_id, rows_by_id=rows_by_id)

        preview_groups: list[ConfirmedMatrixTestRecordPreviewGroup] = []
        for group in snapshot.groups:
            steps = _build_group_steps(group_id=group.confirmed_group_id, snapshot=snapshot, cell_lookup=cell_lookup)
            if not steps:
                continue
            preview_groups.append(
                ConfirmedMatrixTestRecordPreviewGroup(
                    group_key=group.group_key.strip(),
                    group_label=group.group_label.strip(),
                    sample_quantity_expression=_normalize_text(group.sample_quantity_expression),
                    step_count=len(steps),
                    steps=tuple(steps),
                )
            )

        return ConfirmedMatrixTestRecordPreview(
            project_id=snapshot.version.project_id,
            confirmed_matrix_id=snapshot.version.confirmed_matrix_id,
            preview_status="ready" if preview_groups else "empty",
            groups=tuple(preview_groups),
        )


def _build_cell_lookup(
    *,
    snapshot: ConfirmedMatrixSnapshot,
    groups_by_id: dict[str, object],
    rows_by_id: dict[str, object],
) -> dict[tuple[str, str], str]:
    lookup: dict[tuple[str, str], str] = {}
    for cell in snapshot.cells:
        if cell.confirmed_group_id not in groups_by_id or cell.confirmed_row_id not in rows_by_id:
            raise ConfirmedMatrixTestRecordPreviewError(
                "Confirmed matrix cell lineage is invalid."
            )
        lookup[(cell.confirmed_group_id, cell.confirmed_row_id)] = cell.cell_value
    return lookup


def _build_group_steps(
    *,
    group_id: str,
    snapshot: ConfirmedMatrixSnapshot,
    cell_lookup: dict[tuple[str, str], str],
) -> list[ConfirmedMatrixTestRecordPreviewStep]:
    steps: list[ConfirmedMatrixTestRecordPreviewStep] = []
    for row in snapshot.rows:
        cell_value = _normalize_text(cell_lookup.get((group_id, row.confirmed_row_id)))
        if not cell_value:
            continue
        parsed_tokens, _warnings = parse_step_tokens(cell_value)
        for token in parsed_tokens:
            steps.append(
                ConfirmedMatrixTestRecordPreviewStep(
                    sequence=token.sequence,
                    raw_token=token.raw_token,
                    test_item=_normalize_text(row.test_item),
                    section=_normalize_text(row.source_section),
                    method=_normalize_text(row.method),
                    condition=_normalize_text(row.condition),
                    requirement=_normalize_text(row.requirement),
                )
            )
    return steps


def _normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip()
