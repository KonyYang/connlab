"""Build lightweight read-only ConfirmedMatrix authority history."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from backend.domain import ConfirmedMatrixSnapshot


class ConfirmedMatrixAuthorityHistoryStore(Protocol):
    """ConfirmedMatrix snapshot listing required by history read service."""

    def list_by_project(self, project_id: str) -> tuple[ConfirmedMatrixSnapshot, ...]:
        """Return all confirmed snapshots for one project ordered by revision ascending."""


@dataclass(frozen=True, slots=True)
class BuildConfirmedMatrixAuthorityHistoryCommand:
    """Input payload for building authority history."""

    project_id: str


@dataclass(frozen=True, slots=True)
class ConfirmedMatrixAuthorityHistoryEntry:
    confirmed_matrix_id: str
    confirmed_revision: int
    is_active_authority: bool
    status: str
    confirmed_by: str
    confirmed_at: str
    superseded_at: str | None
    superseded_reason: str | None
    source_snapshot_changed: bool
    group_change_count: int
    step_change_count: int
    token_change_count: int
    record_regeneration_recommended: bool
    change_summary: str


@dataclass(frozen=True, slots=True)
class ConfirmedMatrixAuthorityHistory:
    project_id: str
    entries: tuple[ConfirmedMatrixAuthorityHistoryEntry, ...]


class ConfirmedMatrixAuthorityHistoryService:
    """Derive a compact authority change history from immutable snapshots."""

    def __init__(self, *, confirmed_store: ConfirmedMatrixAuthorityHistoryStore) -> None:
        self._confirmed_store = confirmed_store

    def build_history(
        self, command: BuildConfirmedMatrixAuthorityHistoryCommand
    ) -> ConfirmedMatrixAuthorityHistory:
        snapshots = self._confirmed_store.list_by_project(command.project_id)
        if not snapshots:
            return ConfirmedMatrixAuthorityHistory(project_id=command.project_id, entries=())

        entries_asc: list[ConfirmedMatrixAuthorityHistoryEntry] = []
        previous: ConfirmedMatrixSnapshot | None = None
        for snapshot in snapshots:
            entry = self._build_entry(snapshot=snapshot, previous=previous)
            entries_asc.append(entry)
            previous = snapshot

        # repository remains asc; service/API output desc for operator readability
        return ConfirmedMatrixAuthorityHistory(
            project_id=command.project_id,
            entries=tuple(reversed(entries_asc)),
        )

    def _build_entry(
        self, *, snapshot: ConfirmedMatrixSnapshot, previous: ConfirmedMatrixSnapshot | None
    ) -> ConfirmedMatrixAuthorityHistoryEntry:
        source_changed = False
        group_changes = 0
        step_changes = 0
        token_changes = 0
        has_content_change = False
        if previous is not None:
            source_changed = (
                snapshot.version.source_snapshot_id != previous.version.source_snapshot_id
            )
            group_changes = _symmetric_change_count(
                _group_keys(snapshot), _group_keys(previous)
            )
            step_changes = _symmetric_change_count(_row_keys(snapshot), _row_keys(previous))
            token_changes = _symmetric_change_count(
                _cell_keys(snapshot), _cell_keys(previous)
            )
            has_content_change = source_changed or any(
                value > 0 for value in (group_changes, step_changes, token_changes)
            )

        summary = _build_summary(
            revision=snapshot.version.confirmed_revision,
            source_changed=source_changed,
            group_changes=group_changes,
            step_changes=step_changes,
            token_changes=token_changes,
            initial=previous is None,
        )
        recommended = (
            (not snapshot.version.is_active_authority)
            or (snapshot.version.is_active_authority and has_content_change)
        )
        return ConfirmedMatrixAuthorityHistoryEntry(
            confirmed_matrix_id=snapshot.version.confirmed_matrix_id,
            confirmed_revision=snapshot.version.confirmed_revision,
            is_active_authority=snapshot.version.is_active_authority,
            status=snapshot.version.status.value,
            confirmed_by=snapshot.version.confirmed_by,
            confirmed_at=snapshot.version.confirmed_at,
            superseded_at=snapshot.version.superseded_at,
            superseded_reason=snapshot.version.superseded_reason,
            source_snapshot_changed=source_changed,
            group_change_count=group_changes,
            step_change_count=step_changes,
            token_change_count=token_changes,
            record_regeneration_recommended=recommended,
            change_summary=summary,
        )


def _symmetric_change_count(left: set[tuple], right: set[tuple]) -> int:
    return len(left.symmetric_difference(right))


def _group_keys(snapshot: ConfirmedMatrixSnapshot) -> set[tuple[str, str, str]]:
    return {
        (group.group_key, group.group_label, group.sample_quantity_expression)
        for group in snapshot.groups
    }


def _row_keys(snapshot: ConfirmedMatrixSnapshot) -> set[tuple[str, str, str, str, str]]:
    return {
        (
            row.test_item or "",
            row.source_section or "",
            row.method or "",
            row.condition or "",
            row.requirement or "",
        )
        for row in snapshot.rows
    }


def _cell_keys(snapshot: ConfirmedMatrixSnapshot) -> set[tuple[str, str, str]]:
    groups_by_id = {group.confirmed_group_id: group for group in snapshot.groups}
    rows_by_id = {row.confirmed_row_id: row for row in snapshot.rows}
    keys: set[tuple[str, str, str]] = set()
    for cell in snapshot.cells:
        group_key = groups_by_id.get(cell.confirmed_group_id).group_key if cell.confirmed_group_id in groups_by_id else ""
        row_key = ""
        if cell.confirmed_row_id in rows_by_id:
            row = rows_by_id[cell.confirmed_row_id]
            row_key = "|".join(
                [
                    row.test_item or "",
                    row.source_section or "",
                    row.method or "",
                    row.condition or "",
                    row.requirement or "",
                ]
            )
        keys.add((group_key, row_key, cell.cell_value or ""))
    return keys


def _build_summary(
    *,
    revision: int,
    source_changed: bool,
    group_changes: int,
    step_changes: int,
    token_changes: int,
    initial: bool,
) -> str:
    if initial:
        return "Initial confirmed Matrix authority."
    if not source_changed and group_changes == 0 and step_changes == 0 and token_changes == 0:
        return f"Revision {revision} confirmed with no Matrix content changes detected."
    source_text = " Source snapshot changed." if source_changed else ""
    return (
        f"Revision {revision} changed {group_changes} groups, {step_changes} steps, and {token_changes} matrix tokens."
        f"{source_text}"
    )
