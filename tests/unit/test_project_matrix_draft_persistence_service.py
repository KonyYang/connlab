from __future__ import annotations

from copy import deepcopy

import pytest

from backend.application.project_matrix_draft_persistence_service import (
    CreateProjectMatrixDraftFromSourceImportCommand,
    ProjectMatrixDraftCellInput,
    ProjectMatrixDraftGroupInput,
    ProjectMatrixDraftPersistenceConflictError,
    ProjectMatrixDraftPersistenceError,
    ProjectMatrixDraftPersistenceNotFoundError,
    ProjectMatrixDraftPersistenceService,
    ProjectMatrixDraftRowInput,
    UpdateProjectMatrixDraftCommand,
)
from backend.domain import (
    Project,
    ProjectMatrixDraftSnapshot,
    ProjectStatus,
    SourceMatrixCellSnapshot,
    SourceMatrixGroupSnapshot,
    SourceMatrixImportRecord,
    SourceMatrixImportStatus,
    SourceMatrixRowSnapshot,
    SourceMatrixSnapshot,
)


def test_project_matrix_draft_service_uses_import_selected_groups_by_default() -> None:
    service, store = _service()
    draft = service.create_from_source_import(
        CreateProjectMatrixDraftFromSourceImportCommand(
            project_id="P1",
            source_import_id="smi-1",
            selected_group_keys=None,
        )
    )
    selected = [group.group_key for group in draft.groups if group.is_selected]
    assert selected == ["g2"]
    assert len(draft.cells) == 2
    assert store.created_snapshots[-1].record.source_import_id == "smi-1"


def test_project_matrix_draft_service_defaults_to_all_groups_when_import_selection_empty() -> None:
    service, _ = _service(import_selected_keys=())
    draft = service.create_from_source_import(
        CreateProjectMatrixDraftFromSourceImportCommand(
            project_id="P1",
            source_import_id="smi-1",
            selected_group_keys=None,
        )
    )
    selected = {group.group_key for group in draft.groups if group.is_selected}
    assert selected == {"g1", "g2"}


def test_project_matrix_draft_service_uses_explicit_selected_group_subset() -> None:
    service, _ = _service()
    draft = service.create_from_source_import(
        CreateProjectMatrixDraftFromSourceImportCommand(
            project_id="P1",
            source_import_id="smi-1",
            selected_group_keys=("g1",),
        )
    )
    selected = [group.group_key for group in draft.groups if group.is_selected]
    assert selected == ["g1"]


def test_project_matrix_draft_service_rejects_unknown_selected_group() -> None:
    service, _ = _service()
    with pytest.raises(ProjectMatrixDraftPersistenceError, match="Unknown selected group keys"):
        service.create_from_source_import(
            CreateProjectMatrixDraftFromSourceImportCommand(
                project_id="P1",
                source_import_id="smi-1",
                selected_group_keys=("g9",),
            )
        )


def test_project_matrix_draft_service_rejects_duplicate_project_and_source_import() -> None:
    service, store = _service()
    service.create_from_source_import(
        CreateProjectMatrixDraftFromSourceImportCommand(
            project_id="P1",
            source_import_id="smi-1",
            selected_group_keys=("g1",),
        )
    )
    with pytest.raises(ProjectMatrixDraftPersistenceConflictError):
        service.create_from_source_import(
            CreateProjectMatrixDraftFromSourceImportCommand(
                project_id="P1",
                source_import_id="smi-1",
            )
        )
    assert len(store.created_snapshots) == 1


def test_project_matrix_draft_service_keeps_source_snapshot_immutable() -> None:
    service, _ = _service()
    before = deepcopy(service._source.source_snapshot)
    service.create_from_source_import(
        CreateProjectMatrixDraftFromSourceImportCommand(
            project_id="P1",
            source_import_id="smi-1",
        )
    )
    after = service._source.source_snapshot
    assert after == before


def test_project_matrix_draft_service_rejects_missing_project() -> None:
    service, _ = _service(project_exists=False)
    with pytest.raises(ProjectMatrixDraftPersistenceNotFoundError, match="Project not found"):
        service.create_from_source_import(
            CreateProjectMatrixDraftFromSourceImportCommand(
                project_id="P1",
                source_import_id="smi-1",
            )
        )


def test_project_matrix_draft_service_update_replaces_sparse_cells_and_keeps_source_immutable() -> None:
    service, store = _service()
    created = service.create_from_source_import(
        CreateProjectMatrixDraftFromSourceImportCommand(
            project_id="P1",
            source_import_id="smi-1",
        )
    )
    before_source = deepcopy(service._source.source_snapshot)
    updated = service.update_draft(
        UpdateProjectMatrixDraftCommand(
            project_id="P1",
            project_matrix_draft_id=created.record.project_matrix_draft_id,
            pre_test_buffer_days="1",
            post_test_buffer_days="2",
            sample_received_date="2026-06-01",
            planned_test_start_date="2026-06-02",
            planned_test_complete_date="2026-06-05",
            estimated_completion_date="2026-06-07",
            groups=tuple(
                ProjectMatrixDraftGroupInput(
                    draft_group_id=group.draft_group_id,
                    source_group_snapshot_id=group.source_group_snapshot_id,
                    group_order=group.group_order,
                    group_key=group.group_key,
                    group_label=group.group_label,
                    is_selected=group.is_selected,
                    sample_quantity_expression=group.sample_quantity_expression,
                    sample_note=group.sample_note,
                )
                for group in created.groups
            ),
            rows=tuple(
                ProjectMatrixDraftRowInput(
                    draft_row_id=row.draft_row_id,
                    source_row_snapshot_id=row.source_row_snapshot_id,
                    row_order=row.row_order,
                    test_item=row.test_item,
                    source_section=row.source_section,
                    method="M1" if row.row_order == 1 else "M2",
                    condition="C1" if row.row_order == 1 else "C2",
                    requirement="R1" if row.row_order == 1 else "R2",
                    day_expression="0.5x" if row.row_order == 1 else "1",
                    is_sample_row=row.is_sample_row,
                )
                for row in created.rows
            ),
            cells=(
                ProjectMatrixDraftCellInput(
                    draft_row_id=created.rows[0].draft_row_id,
                    draft_group_id=created.groups[0].draft_group_id,
                    cell_value="",
                ),
                ProjectMatrixDraftCellInput(
                    draft_row_id=created.rows[1].draft_row_id,
                    draft_group_id=created.groups[1].draft_group_id,
                    cell_value="7",
                ),
            ),
        )
    )
    assert len(updated.cells) == 1
    assert updated.cells[0].cell_value == "7"
    assert updated.rows[0].method == "M1"
    assert updated.rows[0].condition == "C1"
    assert updated.rows[0].requirement == "R1"
    assert updated.rows[0].day_expression == "0.5x"
    assert updated.record.pre_test_buffer_days == "1"
    assert updated.record.post_test_buffer_days == "2"
    assert updated.record.sample_received_date == "2026-06-01"
    assert updated.record.planned_test_start_date == "2026-06-02"
    assert updated.record.planned_test_complete_date == "2026-06-05"
    assert updated.record.estimated_completion_date == "2026-06-07"
    assert service._source.source_snapshot == before_source
    assert store.replaced_snapshots[-1].record.project_matrix_draft_id == created.record.project_matrix_draft_id


def test_project_matrix_draft_service_rejects_duplicate_source_row_lineage_before_persistence() -> None:
    service, store = _service()
    created = service.create_from_source_import(
        CreateProjectMatrixDraftFromSourceImportCommand(
            project_id="P1",
            source_import_id="smi-1",
        )
    )
    source_row = created.rows[0]
    other_row = created.rows[1]

    with pytest.raises(
        ProjectMatrixDraftPersistenceError,
        match="Duplicate source row lineage",
    ):
        service.update_draft(
            _update_command_with_rows(
                created,
                (
                    ProjectMatrixDraftRowInput(
                        draft_row_id=source_row.draft_row_id,
                        source_row_snapshot_id=source_row.source_row_snapshot_id,
                        row_order=1,
                        test_item=source_row.test_item,
                    ),
                    ProjectMatrixDraftRowInput(
                        draft_row_id=other_row.draft_row_id,
                        source_row_snapshot_id=source_row.source_row_snapshot_id,
                        row_order=2,
                        test_item=other_row.test_item,
                    ),
                ),
            )
        )

    assert len(store.replaced_snapshots) == 0


def test_project_matrix_draft_service_rejects_duplicate_draft_row_identity_before_persistence() -> None:
    service, store = _service()
    created = service.create_from_source_import(
        CreateProjectMatrixDraftFromSourceImportCommand(
            project_id="P1",
            source_import_id="smi-1",
        )
    )
    source_row = created.rows[0]

    with pytest.raises(
        ProjectMatrixDraftPersistenceError,
        match="Duplicate draft row identity",
    ):
        service.update_draft(
            _update_command_with_rows(
                created,
                (
                    ProjectMatrixDraftRowInput(
                        draft_row_id=source_row.draft_row_id,
                        source_row_snapshot_id=None,
                        row_order=1,
                        test_item=source_row.test_item,
                    ),
                    ProjectMatrixDraftRowInput(
                        draft_row_id=source_row.draft_row_id,
                        source_row_snapshot_id=None,
                        row_order=2,
                        test_item=source_row.test_item,
                    ),
                ),
            )
        )

    assert len(store.replaced_snapshots) == 0


def _update_command_with_rows(
    created: ProjectMatrixDraftSnapshot,
    rows: tuple[ProjectMatrixDraftRowInput, ...],
) -> UpdateProjectMatrixDraftCommand:
    return UpdateProjectMatrixDraftCommand(
        project_id="P1",
        project_matrix_draft_id=created.record.project_matrix_draft_id,
        groups=tuple(
            ProjectMatrixDraftGroupInput(
                draft_group_id=group.draft_group_id,
                source_group_snapshot_id=group.source_group_snapshot_id,
                group_order=group.group_order,
                group_key=group.group_key,
                group_label=group.group_label,
                is_selected=group.is_selected,
                sample_quantity_expression=group.sample_quantity_expression,
                sample_note=group.sample_note,
            )
            for group in created.groups
        ),
        rows=rows,
        cells=(),
    )


def test_project_matrix_draft_service_update_uses_last_write_wins() -> None:
    service, _ = _service()
    created = service.create_from_source_import(
        CreateProjectMatrixDraftFromSourceImportCommand(
            project_id="P1",
            source_import_id="smi-1",
        )
    )
    updated = service.update_draft(
        UpdateProjectMatrixDraftCommand(
            project_id="P1",
            project_matrix_draft_id=created.record.project_matrix_draft_id,
            groups=tuple(
                ProjectMatrixDraftGroupInput(
                    draft_group_id=group.draft_group_id,
                    source_group_snapshot_id=group.source_group_snapshot_id,
                    group_order=group.group_order,
                    group_key=group.group_key,
                    group_label=group.group_label,
                    is_selected=group.is_selected,
                    sample_quantity_expression=group.sample_quantity_expression,
                    sample_note=group.sample_note,
                )
                for group in created.groups
            ),
            rows=tuple(
                ProjectMatrixDraftRowInput(
                    draft_row_id=row.draft_row_id,
                    source_row_snapshot_id=row.source_row_snapshot_id,
                    row_order=row.row_order,
                    test_item=row.test_item,
                    source_section=row.source_section,
                    is_sample_row=row.is_sample_row,
                )
                for row in created.rows
            ),
            cells=tuple(),
        )
    )
    assert updated.record.project_matrix_draft_id == created.record.project_matrix_draft_id


def test_project_matrix_draft_service_update_new_local_row_group_use_nullable_lineage() -> None:
    service, _ = _service()
    created = service.create_from_source_import(
        CreateProjectMatrixDraftFromSourceImportCommand(
            project_id="P1",
            source_import_id="smi-1",
        )
    )
    updated = service.update_draft(
        UpdateProjectMatrixDraftCommand(
            project_id="P1",
            project_matrix_draft_id=created.record.project_matrix_draft_id,
            groups=(
                ProjectMatrixDraftGroupInput(
                    draft_group_id=created.groups[0].draft_group_id,
                    source_group_snapshot_id=created.groups[0].source_group_snapshot_id,
                    group_order=1,
                    group_key=created.groups[0].group_key,
                    group_label=created.groups[0].group_label,
                    is_selected=True,
                ),
                ProjectMatrixDraftGroupInput(
                    draft_group_id=None,
                    source_group_snapshot_id=None,
                    group_order=2,
                    group_key="new_group",
                    group_label="N",
                    is_selected=True,
                ),
            ),
            rows=(
                ProjectMatrixDraftRowInput(
                    draft_row_id=created.rows[0].draft_row_id,
                    source_row_snapshot_id=created.rows[0].source_row_snapshot_id,
                    row_order=1,
                    test_item=created.rows[0].test_item,
                ),
                ProjectMatrixDraftRowInput(
                    draft_row_id=None,
                    source_row_snapshot_id=None,
                    row_order=2,
                    test_item="Added Row",
                ),
            ),
            cells=tuple(),
        )
    )
    local_group = next(group for group in updated.groups if group.group_key == "new_group")
    local_row = next(row for row in updated.rows if row.test_item == "Added Row")
    assert local_group.source_group_snapshot_id is None
    assert local_row.source_row_snapshot_id is None


def test_project_matrix_draft_service_update_remaps_foreign_raw_row_group_ids() -> None:
    service, _ = _service()
    created = service.create_from_source_import(
        CreateProjectMatrixDraftFromSourceImportCommand(
            project_id="P1",
            source_import_id="smi-1",
        )
    )
    updated = service.update_draft(
        UpdateProjectMatrixDraftCommand(
            project_id="P1",
            project_matrix_draft_id=created.record.project_matrix_draft_id,
            groups=(
                ProjectMatrixDraftGroupInput(
                    draft_group_id="foreign-group-id",
                    source_group_snapshot_id=None,
                    group_order=1,
                    group_key="foreign",
                    group_label="Foreign",
                    is_selected=True,
                    sample_quantity_expression="3",
                    sample_note=None,
                ),
            ),
            rows=(
                ProjectMatrixDraftRowInput(
                    draft_row_id="foreign-row-id",
                    source_row_snapshot_id=None,
                    row_order=1,
                    test_item="Transferred row",
                    source_section="9.1",
                    method="M",
                    condition="C",
                    requirement="R",
                    is_sample_row=False,
                ),
            ),
            cells=(
                ProjectMatrixDraftCellInput(
                    draft_row_id="foreign-row-id",
                    draft_group_id="foreign-group-id",
                    cell_value="4",
                ),
            ),
        )
    )
    assert updated.groups[0].draft_group_id != "foreign-group-id"
    assert updated.rows[0].draft_row_id != "foreign-row-id"
    assert updated.cells[0].draft_group_id == updated.groups[0].draft_group_id
    assert updated.cells[0].draft_row_id == updated.rows[0].draft_row_id


class _ProjectStore:
    def __init__(self, *, exists: bool) -> None:
        self._project = (
            Project(
                project_id="P1",
                project_no="DL-2026-05-001",
                product_name="Connector",
                requestor="Alice",
                status=ProjectStatus.LTR_REGISTERED,
            )
            if exists
            else None
        )

    def get(self, project_id: str) -> Project | None:
        if self._project and self._project.project_id == project_id:
            return self._project
        return None


class _SourceStore:
    def __init__(self, *, import_selected_keys: tuple[str, ...]) -> None:
        self.import_record = SourceMatrixImportRecord(
            import_id="smi-1",
            project_id="P1",
            draft_id="ptpd-1",
            source_document_path="C:/spec.docx",
            source_document_name="spec.docx",
            source_format=".docx",
            source_asset_id=None,
            source_case_id=None,
            source_draft_id=None,
            import_status=SourceMatrixImportStatus.IMPORTED,
            source_spec_number=None,
            source_spec_revision=None,
            parse_time="2026-05-22T09:00:00+00:00",
            parser_version="parser-v1",
            payload_schema_version="1.0",
            warnings=(),
            blockers=(),
            selected_group_keys_at_import=import_selected_keys,
            created_at="2026-05-22T09:00:00+00:00",
        )
        self.source_snapshot = SourceMatrixSnapshot(
            snapshot_id="sms-1",
            import_id="smi-1",
            project_id="P1",
            source_table_index=21,
            groups=(
                SourceMatrixGroupSnapshot(
                    group_snapshot_id="smg-1",
                    group_order=1,
                    group_key="g1",
                    group_label="G1",
                    sample_quantity_expression="5",
                ),
                SourceMatrixGroupSnapshot(
                    group_snapshot_id="smg-2",
                    group_order=2,
                    group_key="g2",
                    group_label="G2",
                    sample_quantity_expression="6",
                ),
            ),
            rows=(
                SourceMatrixRowSnapshot(
                    row_snapshot_id="smr-1",
                    row_order=1,
                    source_row_index=3,
                    test_item="Visual",
                    source_section="6.1",
                ),
                SourceMatrixRowSnapshot(
                    row_snapshot_id="smr-2",
                    row_order=2,
                    source_row_index=4,
                    test_item="LLCR",
                    source_section="6.2",
                ),
            ),
            cells=(
                SourceMatrixCellSnapshot(
                    cell_snapshot_id="smc-1",
                    row_snapshot_id="smr-1",
                    group_snapshot_id="smg-1",
                    cell_value="1",
                ),
                SourceMatrixCellSnapshot(
                    cell_snapshot_id="smc-2",
                    row_snapshot_id="smr-2",
                    group_snapshot_id="smg-2",
                    cell_value="2",
                ),
            ),
            created_at="2026-05-22T09:00:00+00:00",
        )

    def get_import(self, import_id: str) -> SourceMatrixImportRecord | None:
        return self.import_record if import_id == self.import_record.import_id else None

    def get_snapshot_by_import(self, import_id: str) -> SourceMatrixSnapshot | None:
        return self.source_snapshot if import_id == self.import_record.import_id else None


class _DraftStore:
    def __init__(self) -> None:
        self.created_snapshots: list[ProjectMatrixDraftSnapshot] = []
        self.replaced_snapshots: list[ProjectMatrixDraftSnapshot] = []

    def create_snapshot(self, snapshot: ProjectMatrixDraftSnapshot) -> ProjectMatrixDraftSnapshot:
        self.created_snapshots.append(snapshot)
        return snapshot

    def get_by_project_and_source_import(self, project_id: str, source_import_id: str):
        for snapshot in self.created_snapshots:
            if (
                snapshot.record.project_id == project_id
                and snapshot.record.source_import_id == source_import_id
            ):
                return snapshot.record
        return None

    def get(self, project_matrix_draft_id: str) -> ProjectMatrixDraftSnapshot | None:
        for snapshot in self.created_snapshots:
            if snapshot.record.project_matrix_draft_id == project_matrix_draft_id:
                return snapshot
        return None

    def list_by_project(self, project_id: str):
        return [
            snapshot.record
            for snapshot in self.created_snapshots
            if snapshot.record.project_id == project_id
        ]

    def replace_snapshot(self, snapshot: ProjectMatrixDraftSnapshot) -> ProjectMatrixDraftSnapshot:
        for index, current in enumerate(self.created_snapshots):
            if current.record.project_matrix_draft_id == snapshot.record.project_matrix_draft_id:
                self.created_snapshots[index] = snapshot
                self.replaced_snapshots.append(snapshot)
                return snapshot
        raise LookupError("Project matrix draft record not found.")


def _service(
    *,
    project_exists: bool = True,
    import_selected_keys: tuple[str, ...] = ("g2",),
) -> tuple[ProjectMatrixDraftPersistenceService, _DraftStore]:
    source_store = _SourceStore(import_selected_keys=import_selected_keys)
    draft_store = _DraftStore()
    return (
        ProjectMatrixDraftPersistenceService(
            project_store=_ProjectStore(exists=project_exists),
            source_store=source_store,
            draft_store=draft_store,
        ),
        draft_store,
    )
