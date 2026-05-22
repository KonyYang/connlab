from __future__ import annotations

from copy import deepcopy

import pytest

from backend.application.project_matrix_draft_persistence_service import (
    CreateProjectMatrixDraftFromSourceImportCommand,
    ProjectMatrixDraftPersistenceConflictError,
    ProjectMatrixDraftPersistenceError,
    ProjectMatrixDraftPersistenceNotFoundError,
    ProjectMatrixDraftPersistenceService,
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
