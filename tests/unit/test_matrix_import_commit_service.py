from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pytest

from backend.application.external_excel_read_service import (
    StandardRecordReadResult,
    StandardRecordRow,
)
from backend.application.matrix_import_commit_service import (
    MatrixImportCommitCommand,
    MatrixImportCommitError,
    MatrixImportCommitService,
)
from backend.application.matrix_import_method_authority import (
    MatrixImportMethodAuthorityResolver,
)
from backend.application.source_matrix_import_persistence_service import (
    SourceMatrixImportPersistenceService,
)
from backend.domain import (
    ExternalResource,
    ExternalResourceType,
    Project,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStatus,
    ProjectStatus,
    SourceMatrixCellSnapshot,
    SourceMatrixGroupSnapshot,
    SourceMatrixImportRecord,
    SourceMatrixImportStatus,
    SourceMatrixRowSnapshot,
    SourceMatrixSnapshot,
)


def test_commit_creates_selected_only_draft_and_persists_full_source() -> None:
    project_store = _ProjectStore(
        {
            "P1": Project(
                project_id="P1",
                project_no="DL-2026-05-001",
                product_name="Connector",
                requestor="Alice",
                status=ProjectStatus.LTR_REGISTERED,
                created_on=date(2026, 5, 23),
            )
        }
    )
    source_store = _SourceStore()
    draft_store = _DraftStore()
    source_persistence = SourceMatrixImportPersistenceService(store=source_store)
    service = MatrixImportCommitService(
        project_store=project_store,
        source_store=source_store,
        draft_store=draft_store,
        source_persistence_service=source_persistence,
        method_authority=_method_authority(),
    )

    result = service.commit(
        MatrixImportCommitCommand(
            project_id="P1",
            source_document_path="C:/spec.docx",
            source_document_name="spec.docx",
            source_format=".docx",
            preview_payload=_payload(),
            selected_group_keys=("g1",),
        )
    )

    assert result.commit_status == "created"
    assert [group.group_key for group in result.project_matrix_draft.groups] == ["g1"]
    assert all(cell.draft_group_id == result.project_matrix_draft.groups[0].draft_group_id for cell in result.project_matrix_draft.cells)
    assert result.project_matrix_draft.rows[0].method == "EIA-364-18B"
    assert result.project_matrix_draft.rows[0].condition == "10x min magnification"
    assert result.project_matrix_draft.rows[0].requirement == "No detrimental condition"
    source_snapshot = source_store.get_snapshot_by_import(result.source_import_id)
    assert source_snapshot is not None
    assert len(source_snapshot.groups) == 2


def test_commit_reuses_existing_commit_for_same_fingerprint() -> None:
    project_store = _ProjectStore(
        {
            "P1": Project(
                project_id="P1",
                project_no="DL-2026-05-001",
                product_name="Connector",
                requestor="Alice",
                status=ProjectStatus.LTR_REGISTERED,
            )
        }
    )
    source_store = _SourceStore()
    draft_store = _DraftStore()
    source_persistence = SourceMatrixImportPersistenceService(store=source_store)
    service = MatrixImportCommitService(
        project_store=project_store,
        source_store=source_store,
        draft_store=draft_store,
        source_persistence_service=source_persistence,
        method_authority=_method_authority(),
    )

    first = service.commit(
        MatrixImportCommitCommand(
            project_id="P1",
            source_document_path="C:/spec.docx",
            source_document_name="spec.docx",
            source_format=".docx",
            preview_payload=_payload(),
            selected_group_keys=("g1",),
        )
    )
    second = service.commit(
        MatrixImportCommitCommand(
            project_id="P1",
            source_document_path="C:/spec.docx",
            source_document_name="spec.docx",
            source_format=".docx",
            preview_payload=_payload(),
            selected_group_keys=("g1",),
        )
    )

    assert first.commit_status == "created"
    assert second.commit_status == "reused"
    assert first.source_import_id == second.source_import_id
    assert (
        first.project_matrix_draft.record.project_matrix_draft_id
        == second.project_matrix_draft.record.project_matrix_draft_id
    )


def test_commit_rejects_invalid_selected_group_keys() -> None:
    service = MatrixImportCommitService(
        project_store=_ProjectStore(
            {
                "P1": Project(
                    project_id="P1",
                    project_no="DL-2026-05-001",
                    product_name="Connector",
                    requestor="Alice",
                    status=ProjectStatus.LTR_REGISTERED,
                )
            }
        ),
        source_store=_SourceStore(),
        draft_store=_DraftStore(),
        source_persistence_service=SourceMatrixImportPersistenceService(
            store=_SourceStore()
        ),
        method_authority=_method_authority(),
    )
    base = MatrixImportCommitCommand(
        project_id="P1",
        source_document_path="C:/spec.docx",
        source_document_name="spec.docx",
        source_format=".docx",
        preview_payload=_payload(),
        selected_group_keys=("g1",),
    )

    with pytest.raises(MatrixImportCommitError, match="selected_group_keys is required"):
        service.commit(
            MatrixImportCommitCommand(
                project_id=base.project_id,
                source_document_path=base.source_document_path,
                source_document_name=base.source_document_name,
                source_format=base.source_format,
                preview_payload=base.preview_payload,
                selected_group_keys=(),
            )
        )
    with pytest.raises(MatrixImportCommitError, match="Duplicate selected group key"):
        service.commit(
            MatrixImportCommitCommand(
                project_id=base.project_id,
                source_document_path=base.source_document_path,
                source_document_name=base.source_document_name,
                source_format=base.source_format,
                preview_payload=base.preview_payload,
                selected_group_keys=("g1", "g1"),
            )
        )
    with pytest.raises(MatrixImportCommitError, match="Unknown selected group keys"):
        service.commit(
            MatrixImportCommitCommand(
                project_id=base.project_id,
                source_document_path=base.source_document_path,
                source_document_name=base.source_document_name,
                source_format=base.source_format,
                preview_payload=base.preview_payload,
                selected_group_keys=("g3",),
            )
        )


def _payload() -> dict:
    return {
        "groups": [
            {
                "group_key": "g1",
                "group_label": "Group 1",
                "sample_quantity_expression": "5",
                "steps": [
                    {
                        "sequence": 1,
                        "raw_token": "1",
                        "source_row_index": 1,
                        "method_summary": "EIA-364-18B",
                        "condition_summary": "10x min magnification",
                        "judgement_criteria": "No detrimental condition",
                    }
                ],
            },
            {"group_key": "g2", "group_label": "Group 2", "sample_quantity_expression": "6", "steps": []},
        ],
        "rows": [
            {
                "source_row_index": 1,
                "test_item": "Visual",
                "source_section": "6.1",
                "group_tokens": {"g1": "1", "g2": "2"},
                "is_sample_row": False,
            }
        ],
        "warnings": [],
        "blockers": [],
    }


class _ProjectStore:
    def __init__(self, projects: dict[str, Project]) -> None:
        self._projects = projects

    def get(self, project_id: str) -> Project | None:
        return self._projects.get(project_id)


class _DraftStore:
    def __init__(self) -> None:
        self._records: dict[str, ProjectMatrixDraftRecord] = {}
        self._snapshots: dict[str, ProjectMatrixDraftSnapshot] = {}

    def create_snapshot(self, snapshot: ProjectMatrixDraftSnapshot) -> ProjectMatrixDraftSnapshot:
        self._records[snapshot.record.project_matrix_draft_id] = snapshot.record
        self._snapshots[snapshot.record.project_matrix_draft_id] = snapshot
        return snapshot

    def get_by_project_and_source_import(
        self,
        project_id: str,
        source_import_id: str,
    ) -> ProjectMatrixDraftRecord | None:
        for record in self._records.values():
            if record.project_id == project_id and record.source_import_id == source_import_id:
                return record
        return None

    def get(self, project_matrix_draft_id: str) -> ProjectMatrixDraftSnapshot | None:
        return self._snapshots.get(project_matrix_draft_id)


@dataclass
class _SourceStore:
    imports_by_id: dict[str, SourceMatrixImportRecord] = None  # type: ignore[assignment]
    imports_by_fingerprint: dict[tuple[str, str], SourceMatrixImportRecord] = None  # type: ignore[assignment]
    snapshots_by_import: dict[str, SourceMatrixSnapshot] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self.imports_by_id = {}
        self.imports_by_fingerprint = {}
        self.snapshots_by_import = {}

    def get_import_by_project_and_fingerprint(
        self,
        *,
        project_id: str,
        task261_commit_fingerprint: str,
    ) -> SourceMatrixImportRecord | None:
        return self.imports_by_fingerprint.get((project_id, task261_commit_fingerprint))

    def get_snapshot_by_import(self, import_id: str) -> SourceMatrixSnapshot | None:
        return self.snapshots_by_import.get(import_id)

    def create_import_snapshot(
        self,
        import_record: SourceMatrixImportRecord,
        snapshot: SourceMatrixSnapshot,
    ) -> None:
        self.imports_by_id[import_record.import_id] = import_record
        if import_record.task261_commit_fingerprint:
            self.imports_by_fingerprint[
                (import_record.project_id, import_record.task261_commit_fingerprint)
            ] = import_record
        self.snapshots_by_import[import_record.import_id] = snapshot


def _method_authority() -> MatrixImportMethodAuthorityResolver:
    return MatrixImportMethodAuthorityResolver(
        resource_store=_ResourceStore(),
        catalog_reader=_CatalogReader(),
        now=lambda: "2026-07-21T00:00:00+00:00",
    )


class _ResourceStore:
    def get_by_type(self, resource_type: ExternalResourceType) -> ExternalResource | None:
        return ExternalResource(
            resource_id="standard-1",
            resource_type=resource_type,
            path=Path("C:/standards.xlsx"),
            worksheet_name="认可标准",
        )


class _CatalogReader:
    def read_standard_records(self) -> StandardRecordReadResult:
        return StandardRecordReadResult(
            resource_path="C:/standards.xlsx",
            matched_sheets=("认可标准",),
            rows=(
                StandardRecordRow(
                    standard_code="EIA-364-18B-2020",
                    test_item="Visual",
                    sample_description=None,
                    source_sheet="认可标准",
                    source_row_number=3,
                ),
            ),
        )
