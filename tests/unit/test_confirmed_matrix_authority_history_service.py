from __future__ import annotations

from backend.application.confirmed_matrix_authority_history_service import (
    BuildConfirmedMatrixAuthorityHistoryCommand,
    ConfirmedMatrixAuthorityHistoryService,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
)


def test_history_service_returns_empty_when_no_snapshots() -> None:
    service = ConfirmedMatrixAuthorityHistoryService(confirmed_store=_Store(()))
    history = service.build_history(
        BuildConfirmedMatrixAuthorityHistoryCommand(project_id="P1")
    )
    assert history.project_id == "P1"
    assert history.entries == ()


def test_history_service_builds_desc_entries_with_initial_summary() -> None:
    s1 = _snapshot("cmv-1", 1, True)
    service = ConfirmedMatrixAuthorityHistoryService(confirmed_store=_Store((s1,)))
    history = service.build_history(
        BuildConfirmedMatrixAuthorityHistoryCommand(project_id="P1")
    )
    assert len(history.entries) == 1
    entry = history.entries[0]
    assert entry.confirmed_matrix_id == "cmv-1"
    assert entry.change_summary == "Initial confirmed Matrix authority."
    assert entry.record_regeneration_recommended is False


def test_history_service_counts_changes_and_marks_recommended() -> None:
    s1 = _snapshot("cmv-1", 1, False)
    s2 = _snapshot(
        "cmv-2",
        2,
        True,
        source_snapshot_id="sms-2",
        groups=(("g1", "G1", "5"), ("g3", "G3", "7")),
        rows=(
            ("Visual", "6.1", "M1", "C1", "R1"),
            ("LLCR", "6.2", "M2", "C2", "R2"),
            ("DWV", "6.3", "M3", "C3", "R3"),
        ),
        cells=(("g1", "Visual", "1"), ("g3", "DWV", "6")),
    )
    service = ConfirmedMatrixAuthorityHistoryService(confirmed_store=_Store((s1, s2)))
    history = service.build_history(
        BuildConfirmedMatrixAuthorityHistoryCommand(project_id="P1")
    )
    assert len(history.entries) == 2
    newest = history.entries[0]
    oldest = history.entries[1]

    assert newest.confirmed_revision == 2
    assert newest.source_snapshot_changed is True
    assert newest.group_change_count > 0
    assert newest.step_change_count > 0
    assert newest.token_change_count > 0
    assert newest.record_regeneration_recommended is True
    assert "Revision 2 changed" in newest.change_summary
    assert "Source snapshot changed." in newest.change_summary

    assert oldest.confirmed_revision == 1
    assert oldest.record_regeneration_recommended is True


def test_history_service_detects_token_move_between_duplicate_test_item_rows() -> None:
    s1 = _snapshot(
        "cmv-1",
        1,
        False,
        rows=(
            ("Visual", "6.1", "M1", "C1", "R1"),
            ("Visual", "6.2", "M2", "C2", "R2"),
        ),
        cells=(("g1", "Visual#1", "1"),),
    )
    s2 = _snapshot(
        "cmv-2",
        2,
        True,
        rows=(
            ("Visual", "6.1", "M1", "C1", "R1"),
            ("Visual", "6.2", "M2", "C2", "R2"),
        ),
        cells=(("g1", "Visual#2", "1"),),
    )
    service = ConfirmedMatrixAuthorityHistoryService(confirmed_store=_Store((s1, s2)))
    history = service.build_history(
        BuildConfirmedMatrixAuthorityHistoryCommand(project_id="P1")
    )
    newest = history.entries[0]
    assert newest.confirmed_revision == 2
    assert newest.token_change_count > 0
    assert newest.record_regeneration_recommended is True


class _Store:
    def __init__(self, snapshots: tuple[ConfirmedMatrixSnapshot, ...]) -> None:
        self._snapshots = snapshots

    def list_by_project(self, project_id: str) -> tuple[ConfirmedMatrixSnapshot, ...]:
        return self._snapshots


def _snapshot(
    confirmed_matrix_id: str,
    revision: int,
    is_active: bool,
    *,
    source_snapshot_id: str = "sms-1",
    groups: tuple[tuple[str, str, str], ...] = (("g1", "G1", "5"), ("g2", "G2", "6")),
    rows: tuple[tuple[str, str, str, str, str], ...] = (
        ("Visual", "6.1", "M1", "C1", "R1"),
        ("LLCR", "6.2", "M2", "C2", "R2"),
    ),
    cells: tuple[tuple[str, str, str], ...] = (("g1", "Visual", "1"), ("g2", "LLCR", "2")),
) -> ConfirmedMatrixSnapshot:
    group_models = tuple(
        ConfirmedMatrixGroup(
            confirmed_group_id=f"{confirmed_matrix_id}-{index}-g",
            confirmed_matrix_id=confirmed_matrix_id,
            draft_group_id=f"dg-{index}",
            source_group_snapshot_id=f"sg-{index}",
            group_order=index,
            group_key=group_key,
            group_label=group_label,
            sample_quantity_expression=sample_qty,
        )
        for index, (group_key, group_label, sample_qty) in enumerate(groups, start=1)
    )
    row_models = tuple(
        ConfirmedMatrixRow(
            confirmed_row_id=f"{confirmed_matrix_id}-{index}-r",
            confirmed_matrix_id=confirmed_matrix_id,
            draft_row_id=f"dr-{index}",
            source_row_snapshot_id=f"sr-{index}",
            row_order=index,
            test_item=test_item,
            source_section=section,
            method=method,
            condition=condition,
            requirement=requirement,
        )
        for index, (test_item, section, method, condition, requirement) in enumerate(rows, start=1)
    )
    group_by_key = {group.group_key: group for group in group_models}
    row_by_alias: dict[str, ConfirmedMatrixRow] = {}
    for row in row_models:
        row_by_alias[row.test_item] = row
    duplicate_counts: dict[str, int] = {}
    for row in row_models:
        duplicate_counts[row.test_item] = duplicate_counts.get(row.test_item, 0) + 1
    seen: dict[str, int] = {}
    for row in row_models:
        current = seen.get(row.test_item, 0) + 1
        seen[row.test_item] = current
        if duplicate_counts[row.test_item] > 1:
            row_by_alias[f"{row.test_item}#{current}"] = row
    cell_models = tuple(
        ConfirmedMatrixCell(
            confirmed_cell_id=f"{confirmed_matrix_id}-{index}-c",
            confirmed_matrix_id=confirmed_matrix_id,
            confirmed_row_id=row_by_alias[test_item].confirmed_row_id,
            confirmed_group_id=group_by_key[group_key].confirmed_group_id,
            draft_row_id=row_by_alias[test_item].draft_row_id,
            draft_group_id=group_by_key[group_key].draft_group_id,
            cell_value=cell_value,
        )
        for index, (group_key, test_item, cell_value) in enumerate(cells, start=1)
    )
    return ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id=confirmed_matrix_id,
            project_id="P1",
            project_matrix_draft_id="pmd-1",
            source_import_id="smi-1",
            source_snapshot_id=source_snapshot_id,
            confirmed_revision=revision,
            is_active_authority=is_active,
            status=ConfirmedMatrixStatus.CONFIRMED if is_active else ConfirmedMatrixStatus.SUPERSEDED,
            confirmed_by="operator",
            confirmed_at=f"2026-05-26T0{revision}:00:00+00:00",
            superseded_by_confirmed_matrix_id=None if is_active else "cmv-2",
            superseded_at=None if is_active else "2026-05-26T02:00:00+00:00",
            superseded_reason=None if is_active else "Revision confirmed",
        ),
        groups=group_models,
        rows=row_models,
        cells=cell_models,
    )
