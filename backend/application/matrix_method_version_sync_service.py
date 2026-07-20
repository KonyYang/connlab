"""Preview and apply Standard catalog Method revisions to an editable Matrix draft."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, Protocol

from backend.application.external_excel_read_service import StandardRecordReadResult
from backend.application.external_resource_service import effective_standard_worksheet_name
from backend.application.matrix_editor_session_service import (
    build_project_matrix_draft_payload_signature,
)
from backend.domain import (
    ExternalResource,
    ExternalResourceType,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStatus,
)
from backend.modules.test_plan.standard_method_version_parser import (
    build_method_proposal,
    parse_catalog_method,
    parse_matrix_method,
)


class MatrixMethodVersionSyncError(ValueError):
    """Base typed error for Method version synchronization."""


class MatrixMethodVersionSyncNotFoundError(LookupError):
    """Raised when a project-scoped draft or source resource is missing."""


class MatrixMethodVersionSyncConflictError(MatrixMethodVersionSyncError):
    """Raised when source or draft state changed before preview/apply."""


class DraftStore(Protocol):
    def get(self, draft_id: str) -> ProjectMatrixDraftSnapshot | None: ...
    def apply_method_sync(self, **kwargs) -> bool: ...


class ConfirmedStore(Protocol):
    def get_active_by_project(self, project_id: str): ...


class ResourceStore(Protocol):
    def get_by_type(self, resource_type: ExternalResourceType) -> ExternalResource | None: ...


class CatalogReader(Protocol):
    def read_standard_records(self) -> StandardRecordReadResult: ...


@dataclass(frozen=True, slots=True)
class PreviewMatrixMethodVersionSyncCommand:
    project_id: str
    project_matrix_draft_id: str
    expected_saved_payload_signature: str


@dataclass(frozen=True, slots=True)
class ApplyMatrixMethodVersionSyncCommand:
    project_id: str
    project_matrix_draft_id: str
    expected_saved_payload_signature: str
    preview_fingerprint: str
    selected_draft_row_ids: tuple[str, ...]
    applied_by: str


@dataclass(frozen=True, slots=True)
class MatrixMethodVersionSyncRow:
    draft_row_id: str
    row_order: int
    test_item: str
    current_method: str | None
    method_core: str | None
    matched_standard_code: str | None
    catalog_revision: str | None
    catalog_year: int | None
    source_row_number: int | None
    proposed_method: str | None
    status: str
    reason: str | None
    selectable: bool


@dataclass(frozen=True, slots=True)
class MatrixMethodVersionSyncPreview:
    project_id: str
    project_matrix_draft_id: str
    base_confirmed_matrix_id: str | None
    resource_id: str
    resource_path: str
    worksheet_name: str
    catalog_fingerprint: str
    target_fingerprint: str
    preview_fingerprint: str
    generated_at: str
    rows: tuple[MatrixMethodVersionSyncRow, ...]


@dataclass(frozen=True, slots=True)
class _MatrixMethodVersionSyncBuild:
    preview: MatrixMethodVersionSyncPreview
    draft: ProjectMatrixDraftSnapshot


@dataclass(frozen=True, slots=True)
class MatrixMethodVersionSyncApplyResult:
    project_matrix_draft_id: str
    saved_payload_signature: str
    applied_row_ids: tuple[str, ...]
    method_sync_context_json: str


class MatrixMethodVersionSyncService:
    """Coordinate one-read preview and method-only CAS apply."""

    def __init__(
        self,
        *,
        draft_store: DraftStore,
        confirmed_store: ConfirmedStore,
        resource_store: ResourceStore,
        catalog_reader: CatalogReader,
        now: Callable[[], str] | None = None,
    ) -> None:
        self._drafts = draft_store
        self._confirmed = confirmed_store
        self._resources = resource_store
        self._catalog = catalog_reader
        self._now = now or (lambda: datetime.now(UTC).isoformat())

    def preview(
        self, command: PreviewMatrixMethodVersionSyncCommand
    ) -> MatrixMethodVersionSyncPreview:
        return self._build_preview(command).preview

    def apply(
        self, command: ApplyMatrixMethodVersionSyncCommand
    ) -> MatrixMethodVersionSyncApplyResult:
        built = self._build_preview(
            PreviewMatrixMethodVersionSyncCommand(
                command.project_id,
                command.project_matrix_draft_id,
                command.expected_saved_payload_signature,
            )
        )
        preview = built.preview
        draft = built.draft
        if preview.preview_fingerprint != command.preview_fingerprint:
            raise MatrixMethodVersionSyncConflictError(
                "Method sync preview changed. Reload and check again."
            )
        selected_ids = tuple(command.selected_draft_row_ids)
        if not selected_ids or len(set(selected_ids)) != len(selected_ids):
            raise MatrixMethodVersionSyncError(
                "Select one or more distinct safe Method updates."
            )
        actor = command.applied_by.strip()
        if not actor:
            raise MatrixMethodVersionSyncError("applied_by is required.")
        selectable = {row.draft_row_id: row for row in preview.rows if row.selectable}
        if any(row_id not in selectable for row_id in selected_ids):
            raise MatrixMethodVersionSyncError(
                "Selection contains an unknown or blocked Method update."
            )
        updates = tuple(
            (
                row_id,
                selectable[row_id].current_method,
                selectable[row_id].proposed_method or "",
            )
            for row_id in selected_ids
        )
        post_methods = {
            row.draft_row_id: next(
                (new for row_id, _old, new in updates if row_id == row.draft_row_id),
                row.method,
            )
            for row in draft.rows
        }
        post_method_fingerprint = _fingerprint(
            [[row.draft_row_id, post_methods[row.draft_row_id]] for row in draft.rows]
        )
        updated_at = self._now()
        context = _canonical_json(
            {
                "schema": "matrix-method-sync:v1",
                "resource_id": preview.resource_id,
                "resource_path": preview.resource_path,
                "worksheet_name": preview.worksheet_name,
                "catalog_fingerprint": preview.catalog_fingerprint,
                "target_fingerprint": preview.target_fingerprint,
                "preview_fingerprint": preview.preview_fingerprint,
                "pre_apply_saved_payload_signature": command.expected_saved_payload_signature,
                "post_apply_method_fingerprint": post_method_fingerprint,
                "applied_by": actor,
                "applied_at": updated_at,
                "selected_rows": [
                    {
                        "draft_row_id": row_id,
                        "old_method": old,
                        "new_method": new,
                        "source_code": selectable[row_id].matched_standard_code,
                        "source_row_number": selectable[row_id].source_row_number,
                    }
                    for row_id, old, new in updates
                ],
            }
        )
        changed = self._drafts.apply_method_sync(
            project_matrix_draft_id=draft.record.project_matrix_draft_id,
            expected_updated_at=draft.record.updated_at,
            expected_status=ProjectMatrixDraftStatus.DRAFT.value,
            expected_base_confirmed_matrix_id=draft.record.base_confirmed_matrix_id,
            updated_at=updated_at,
            method_sync_context_json=context,
            updates=updates,
        )
        if not changed:
            raise MatrixMethodVersionSyncConflictError(
                "Matrix draft changed. Reload and check again."
            )
        saved = self._load_draft(command.project_id, command.project_matrix_draft_id)
        persisted_methods = _fingerprint(
            [[row.draft_row_id, row.method] for row in saved.rows]
        )
        if persisted_methods != post_method_fingerprint:
            raise MatrixMethodVersionSyncConflictError(
                "Matrix Method update could not be verified."
            )
        return MatrixMethodVersionSyncApplyResult(
            project_matrix_draft_id=saved.record.project_matrix_draft_id,
            saved_payload_signature=build_project_matrix_draft_payload_signature(saved),
            applied_row_ids=selected_ids,
            method_sync_context_json=context,
        )

    def _build_preview(
        self, command: PreviewMatrixMethodVersionSyncCommand
    ) -> _MatrixMethodVersionSyncBuild:
        draft = self._load_draft(command.project_id, command.project_matrix_draft_id)
        current_signature = build_project_matrix_draft_payload_signature(draft)
        if current_signature != command.expected_saved_payload_signature.strip():
            raise MatrixMethodVersionSyncConflictError(
                "Saved Matrix draft changed. Reload before checking Method versions."
            )
        active = self._confirmed.get_active_by_project(command.project_id)
        active_id = active.version.confirmed_matrix_id if active is not None else None
        if draft.record.base_confirmed_matrix_id != active_id:
            raise MatrixMethodVersionSyncConflictError(
                "Matrix draft is stale relative to the active confirmed Matrix."
            )
        resource = self._resources.get_by_type(
            ExternalResourceType.STANDARD_RECORD_EXCEL
        )
        if resource is None or not resource.active:
            raise MatrixMethodVersionSyncNotFoundError(
                "Active Standard record Excel resource is not configured."
            )
        resource_path = str(Path(resource.path))
        worksheet_name = effective_standard_worksheet_name(resource) or "认可标准"
        catalog = self._catalog.read_standard_records()
        candidates = tuple(
            parse_catalog_method(
                row.standard_code, source_row_number=row.source_row_number
            )
            for row in catalog.rows
        )
        rows = tuple(
            _preview_row(row, candidates)
            for row in sorted(draft.rows, key=lambda item: item.row_order)
        )
        catalog_fingerprint = _fingerprint(
            {
                "source": {
                    "resource_id": resource.resource_id,
                    "resource_path": resource_path,
                    "worksheet_name": worksheet_name,
                },
                "rows": [
                    [
                        row.source_row_number,
                        row.standard_code,
                        row.test_item,
                        row.sample_description,
                    ]
                    for row in catalog.rows
                ],
            }
        )
        target_fingerprint = _fingerprint(
            {
                "draft_id": draft.record.project_matrix_draft_id,
                "base_confirmed_matrix_id": draft.record.base_confirmed_matrix_id,
                "updated_at": draft.record.updated_at,
                "rows": [[row.draft_row_id, row.method] for row in draft.rows],
            }
        )
        preview_fingerprint = _fingerprint(
            {
                "schema": "matrix-method-sync-preview:v1",
                "catalog": catalog_fingerprint,
                "target": target_fingerprint,
                "rows": [
                    [row.draft_row_id, row.status, row.proposed_method] for row in rows
                ],
            }
        )
        return _MatrixMethodVersionSyncBuild(
            preview=MatrixMethodVersionSyncPreview(
                project_id=command.project_id,
                project_matrix_draft_id=draft.record.project_matrix_draft_id,
                base_confirmed_matrix_id=draft.record.base_confirmed_matrix_id,
                resource_id=resource.resource_id,
                resource_path=resource_path,
                worksheet_name=worksheet_name,
                catalog_fingerprint=catalog_fingerprint,
                target_fingerprint=target_fingerprint,
                preview_fingerprint=preview_fingerprint,
                generated_at=self._now(),
                rows=rows,
            ),
            draft=draft,
        )

    def _load_draft(self, project_id: str, draft_id: str) -> ProjectMatrixDraftSnapshot:
        draft = self._drafts.get(draft_id)
        if draft is None or draft.record.project_id != project_id:
            raise MatrixMethodVersionSyncNotFoundError("Matrix draft not found.")
        if draft.record.status is not ProjectMatrixDraftStatus.DRAFT:
            raise MatrixMethodVersionSyncConflictError("Matrix draft is not editable.")
        return draft


def _preview_row(row, candidates) -> MatrixMethodVersionSyncRow:
    proposal = build_method_proposal(parse_matrix_method(row.method), candidates)
    selectable = proposal.status in {"update_available", "revision_missing"}
    return MatrixMethodVersionSyncRow(
        draft_row_id=row.draft_row_id,
        row_order=row.row_order,
        test_item=row.test_item,
        current_method=row.method,
        method_core=proposal.method_core,
        matched_standard_code=proposal.matched_standard_code,
        catalog_revision=proposal.catalog_revision,
        catalog_year=proposal.catalog_year,
        source_row_number=proposal.source_row_number,
        proposed_method=proposal.proposed_method,
        status=proposal.status,
        reason=proposal.reason,
        selectable=selectable,
    )


def _fingerprint(value) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _canonical_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
