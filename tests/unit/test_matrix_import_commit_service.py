from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pytest

from backend.application.matrix_import_commit_service import (
    MatrixImportCommitCommand,
    MatrixImportCommitError,
    MatrixImportCommitService,
)
from backend.application.source_matrix_import_persistence_service import (
    SourceMatrixPersistResult,
)
from backend.domain import (
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
    source_persistence = _SourcePersistence(source_store)
    service = MatrixImportCommitService(
        project_store=project_store,
        source_store=source_store,
        draft_store=draft_store,
        source_persistence_service=source_persistence,
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
    source_persistence = _SourcePersistence(source_store)
    service = MatrixImportCommitService(
        project_store=project_store,
        source_store=source_store,
        draft_store=draft_store,
        source_persistence_service=source_persistence,
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
        source_persistence_service=_SourcePersistence(_SourceStore()),
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


class _SourcePersistence:
    def __init__(self, source_store: _SourceStore) -> None:
        self._source_store = source_store
        self._counter = 0

    def compute_task261_fingerprint(
        self,
        *,
        payload: dict,
        selected_group_keys: tuple[str, ...],
    ) -> str:
        return f"{payload['groups'][0]['group_key']}|{','.join(selected_group_keys)}"

    def persist_from_preview(self, command):  # noqa: ANN001
        self._counter += 1
        import_id = f"smi-{self._counter}"
        snapshot_id = f"sms-{self._counter}"
        groups = tuple(
            SourceMatrixGroupSnapshot(
                group_snapshot_id=f"smg-{index}",
                group_order=index,
                group_key=group["group_key"],
                group_label=group["group_label"],
                sample_quantity_expression=group.get("sample_quantity_expression"),
            )
            for index, group in enumerate(command.payload["groups"], start=1)
        )
        rows = (
            SourceMatrixRowSnapshot(
                row_snapshot_id="smr-1",
                row_order=1,
                source_row_index=1,
                test_item="Visual",
                source_section="6.1",
                is_sample_row=False,
            ),
        )
        cells = (
            SourceMatrixCellSnapshot(
                cell_snapshot_id="smc-1",
                row_snapshot_id="smr-1",
                group_snapshot_id="smg-1",
                cell_value="1",
            ),
            SourceMatrixCellSnapshot(
                cell_snapshot_id="smc-2",
                row_snapshot_id="smr-1",
                group_snapshot_id="smg-2",
                cell_value="2",
            ),
        )
        snapshot = SourceMatrixSnapshot(
            snapshot_id=snapshot_id,
            import_id=import_id,
            project_id=command.project_id,
            source_table_index=1,
            rows=rows,
            groups=groups,
            cells=cells,
            created_at=command.created_at,
        )
        import_record = SourceMatrixImportRecord(
            import_id=import_id,
            project_id=command.project_id,
            draft_id=None,
            source_document_path=command.source_document_path,
            source_document_name=command.source_document_name,
            source_format=command.source_format,
            source_asset_id=None,
            source_case_id=None,
            source_draft_id=None,
            import_status=SourceMatrixImportStatus.IMPORTED,
            source_spec_number=None,
            source_spec_revision=None,
            parse_time=command.created_at,
            parser_version="parser-v1",
            payload_schema_version="1.0",
            warnings=(),
            blockers=(),
            selected_group_keys_at_import=command.selected_group_keys,
            task261_commit_fingerprint=command.task261_commit_fingerprint,
            created_at=command.created_at,
        )
        self._source_store.imports_by_id[import_id] = import_record
        self._source_store.imports_by_fingerprint[
            (command.project_id, command.task261_commit_fingerprint)
        ] = import_record
        self._source_store.snapshots_by_import[import_id] = snapshot
        return SourceMatrixPersistResult(import_id=import_id, snapshot_id=snapshot_id)
