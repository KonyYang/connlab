from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.application.external_excel_read_service import (
    StandardRecordReadResult,
    StandardRecordRow,
)
from backend.application.matrix_editor_session_service import (
    build_project_matrix_draft_payload_signature,
)
from backend.application.matrix_method_version_sync_service import (
    ApplyMatrixMethodVersionSyncCommand,
    MatrixMethodVersionSyncConflictError,
    MatrixMethodVersionSyncService,
    PreviewMatrixMethodVersionSyncCommand,
)
from backend.domain import (
    ExternalResource,
    ExternalResourceType,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftRow,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStatus,
)


def test_preview_is_zero_write_and_reports_safe_method_update() -> None:
    store = _Drafts(_snapshot())
    service = _service(store)

    preview = service.preview(
        PreviewMatrixMethodVersionSyncCommand(
            project_id="P1",
            project_matrix_draft_id="D1",
            expected_saved_payload_signature=build_project_matrix_draft_payload_signature(
                store.snapshot
            ),
        )
    )

    assert store.apply_calls == []
    assert preview.rows[0].status == "update_available"
    assert preview.rows[0].proposed_method == "EIA-364-04B"
    assert preview.rows[0].selectable is True
    assert preview.rows[1].status == "current"


def test_apply_updates_only_selected_method_and_persists_context() -> None:
    store = _Drafts(_snapshot())
    service = _service(store)
    signature = build_project_matrix_draft_payload_signature(store.snapshot)
    preview = service.preview(
        PreviewMatrixMethodVersionSyncCommand("P1", "D1", signature)
    )

    result = service.apply(
        ApplyMatrixMethodVersionSyncCommand(
            project_id="P1",
            project_matrix_draft_id="D1",
            expected_saved_payload_signature=signature,
            preview_fingerprint=preview.preview_fingerprint,
            selected_draft_row_ids=("R1",),
            applied_by="operator",
        )
    )

    assert store.snapshot.rows[0].method == "EIA-364-04B"
    assert store.snapshot.rows[0].requirement == "Keep this"
    assert store.snapshot.rows[1].method == "EIA-364-18C"
    assert '"schema":"matrix-method-sync:v1"' in (
        store.snapshot.record.method_sync_context_json or ""
    )
    assert result.saved_payload_signature == build_project_matrix_draft_payload_signature(
        store.snapshot
    )


def test_stale_saved_signature_is_conflict_and_no_write() -> None:
    store = _Drafts(_snapshot())
    service = _service(store)

    with pytest.raises(MatrixMethodVersionSyncConflictError):
        service.preview(PreviewMatrixMethodVersionSyncCommand("P1", "D1", "stale"))

    assert store.apply_calls == []


def test_apply_uses_verified_preview_root_version_for_cas() -> None:
    store = _Drafts(_snapshot())
    service = _service(store)
    signature = build_project_matrix_draft_payload_signature(store.snapshot)
    preview = service.preview(
        PreviewMatrixMethodVersionSyncCommand("P1", "D1", signature)
    )
    store.simulate_toctou = True

    with pytest.raises(MatrixMethodVersionSyncConflictError, match="draft changed"):
        service.apply(
            ApplyMatrixMethodVersionSyncCommand(
                project_id="P1",
                project_matrix_draft_id="D1",
                expected_saved_payload_signature=signature,
                preview_fingerprint=preview.preview_fingerprint,
                selected_draft_row_ids=("R1",),
                applied_by="operator",
            )
        )

    assert store.snapshot.rows[0].method == "EIA-364-04A"
    assert store.successful_apply_count == 0


def test_apply_rejects_identical_catalog_rows_from_changed_source_context() -> None:
    store = _Drafts(_snapshot())
    resources = _Resources(_standard_resource())
    service = _service(store, resources)
    signature = build_project_matrix_draft_payload_signature(store.snapshot)
    preview = service.preview(
        PreviewMatrixMethodVersionSyncCommand("P1", "D1", signature)
    )
    resources.resource = _standard_resource(
        resource_id="STD2",
        path="replacement.xlsx",
        worksheet_name="Replacement",
    )

    with pytest.raises(MatrixMethodVersionSyncConflictError, match="preview changed"):
        service.apply(
            ApplyMatrixMethodVersionSyncCommand(
                project_id="P1",
                project_matrix_draft_id="D1",
                expected_saved_payload_signature=signature,
                preview_fingerprint=preview.preview_fingerprint,
                selected_draft_row_ids=("R1",),
                applied_by="operator",
            )
        )

    assert store.apply_calls == []


def _service(
    store: "_Drafts", resources: "_Resources | None" = None
) -> MatrixMethodVersionSyncService:
    return MatrixMethodVersionSyncService(
        draft_store=store,
        confirmed_store=_Confirmed(),
        resource_store=resources or _Resources(_standard_resource()),
        catalog_reader=_Catalog(),
        now=lambda: "2026-07-20T12:00:00+00:00",
    )


def _standard_resource(
    *,
    resource_id: str = "STD1",
    path: str = "standard.xlsx",
    worksheet_name: str = "认可标准",
) -> ExternalResource:
    return ExternalResource(
        resource_id=resource_id,
        resource_type=ExternalResourceType.STANDARD_RECORD_EXCEL,
        path=Path(path),
        worksheet_name=worksheet_name,
    )


def _snapshot() -> ProjectMatrixDraftSnapshot:
    return ProjectMatrixDraftSnapshot(
        record=ProjectMatrixDraftRecord(
            project_matrix_draft_id="D1",
            project_id="P1",
            source_import_id=None,
            source_snapshot_id="S1",
            base_confirmed_matrix_id="CM1",
            status=ProjectMatrixDraftStatus.DRAFT,
            created_at="2026-07-20T00:00:00+00:00",
            updated_at="2026-07-20T00:00:00+00:00",
        ),
        rows=(
            ProjectMatrixDraftRow(
                draft_row_id="R1",
                project_matrix_draft_id="D1",
                source_row_snapshot_id="SR1",
                row_order=1,
                test_item="Contact resistance",
                method="EIA-364-04A",
                requirement="Keep this",
            ),
            ProjectMatrixDraftRow(
                draft_row_id="R2",
                project_matrix_draft_id="D1",
                source_row_snapshot_id="SR2",
                row_order=2,
                test_item="Other",
                method="EIA-364-18C",
            ),
        ),
    )


class _Drafts:
    def __init__(self, snapshot: ProjectMatrixDraftSnapshot) -> None:
        self.snapshot = snapshot
        self.apply_calls = []
        self.get_calls = 0
        self.simulate_toctou = False
        self.successful_apply_count = 0

    def get(self, draft_id: str):
        self.get_calls += 1
        if self.simulate_toctou and self.get_calls == 3:
            self.snapshot = replace(
                self.snapshot,
                record=replace(self.snapshot.record, updated_at="concurrent"),
            )
        return self.snapshot if draft_id == "D1" else None

    def apply_method_sync(self, **kwargs) -> bool:
        if self.simulate_toctou and self.snapshot.record.updated_at != "concurrent":
            self.snapshot = replace(
                self.snapshot,
                record=replace(self.snapshot.record, updated_at="concurrent"),
            )
        if kwargs["expected_updated_at"] != self.snapshot.record.updated_at:
            return False
        self.apply_calls.append(kwargs)
        self.successful_apply_count += 1
        updates = {row_id: new for row_id, _old, new in kwargs["updates"]}
        rows = tuple(
            replace(row, method=updates.get(row.draft_row_id, row.method))
            for row in self.snapshot.rows
        )
        record = replace(
            self.snapshot.record,
            updated_at=kwargs["updated_at"],
            method_sync_context_json=kwargs["method_sync_context_json"],
        )
        self.snapshot = replace(self.snapshot, record=record, rows=rows)
        return True


class _Confirmed:
    def get_active_by_project(self, _project_id: str):
        return SimpleNamespace(version=SimpleNamespace(confirmed_matrix_id="CM1"))


class _Resources:
    def __init__(self, resource: ExternalResource) -> None:
        self.resource = resource

    def get_by_type(self, _resource_type):
        return self.resource


class _Catalog:
    def read_standard_records(self):
        return StandardRecordReadResult(
            resource_path="standard.xlsx",
            matched_sheets=("认可标准",),
            rows=(
                StandardRecordRow("EIA-364-04B-2015", "CR", None, "认可标准", 3),
                StandardRecordRow("EIA-364-18C", "Other", None, "认可标准", 4),
            ),
        )
