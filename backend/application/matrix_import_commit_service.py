"""Atomic Import Matrix Replace commit orchestration."""

from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext
from dataclasses import dataclass
from datetime import UTC, datetime
import json
from typing import Any, Callable, Protocol

from backend.application.matrix_import_draft_builder import build_selected_only_draft
from backend.application.matrix_import_method_authority import (
    MatrixImportMethodAuthorityError,
    MatrixImportMethodAuthorityResolver,
    MatrixImportMethodAuthorityResult,
    MatrixImportMethodAuthoritySummary,
    verify_new_method_authority,
    verify_reusable_method_authority,
)
from backend.application.source_matrix_import_builder import (
    canonical_windows_path,
    fingerprint,
    fingerprint_source_rows,
    fingerprint_source_snapshot,
)
from backend.application.source_matrix_import_persistence_service import (
    PersistSourceMatrixFromPreviewCommand,
    SourceMatrixImportPersistenceError,
    SourceMatrixImportPersistenceService,
)
from backend.domain import (
    Project,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftSnapshot,
    SourceMatrixImportRecord,
    SourceMatrixSnapshot,
)


class MatrixImportCommitError(ValueError):
    """Raised when Matrix import commit input or authority is invalid."""


class MatrixImportCommitNotFoundError(LookupError):
    """Raised when required project resources are not found."""


class MatrixImportCommitConflictError(MatrixImportCommitError):
    """Raised when replay or persistence cannot be safely completed."""


class ProjectStore(Protocol):
    def get(self, project_id: str) -> Project | None: ...


class SourceImportStore(Protocol):
    def get_import_by_project_and_fingerprint(
        self, *, project_id: str, task261_commit_fingerprint: str
    ) -> SourceMatrixImportRecord | None: ...

    def get_snapshot_by_import(self, import_id: str) -> SourceMatrixSnapshot | None: ...


class ProjectMatrixDraftStore(Protocol):
    def create_snapshot(self, snapshot: ProjectMatrixDraftSnapshot) -> ProjectMatrixDraftSnapshot: ...

    def get_by_project_and_source_import(
        self, project_id: str, source_import_id: str
    ) -> ProjectMatrixDraftRecord | None: ...

    def get(self, project_matrix_draft_id: str) -> ProjectMatrixDraftSnapshot | None: ...


@dataclass(frozen=True, slots=True)
class MatrixImportCommitCommand:
    project_id: str
    source_document_path: str
    source_document_name: str
    source_format: str
    preview_payload: dict[str, Any]
    selected_group_keys: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MatrixImportCommitResult:
    source_import_id: str
    source_snapshot_id: str
    selected_group_keys_committed: tuple[str, ...]
    commit_status: str
    project_matrix_draft: ProjectMatrixDraftSnapshot
    method_authority_sync: MatrixImportMethodAuthoritySummary


class MatrixImportCommitService:
    """Preflight all authority, then atomically persist source plus editable draft."""

    def __init__(
        self,
        *,
        project_store: ProjectStore,
        source_store: SourceImportStore,
        draft_store: ProjectMatrixDraftStore,
        source_persistence_service: SourceMatrixImportPersistenceService,
        method_authority: MatrixImportMethodAuthorityResolver,
        transaction_scope: Callable[[], AbstractContextManager] | None = None,
        now: Callable[[], str] | None = None,
    ) -> None:
        self._projects = project_store
        self._source_imports = source_store
        self._drafts = draft_store
        self._source_persistence = source_persistence_service
        self._method_authority = method_authority
        self._transaction_scope = transaction_scope or nullcontext
        self._now = now or (lambda: datetime.now(UTC).isoformat())

    def commit(self, command: MatrixImportCommitCommand) -> MatrixImportCommitResult:
        self._require_project(command.project_id)
        payload, payload_fingerprint = _freeze_payload(command.preview_payload)
        _validate_payload_minimum(payload)
        selected_keys = _normalize_selected_group_keys(command.selected_group_keys)
        _validate_selected_group_keys(selected_keys, payload)
        task261_fingerprint = self._source_persistence.compute_task261_fingerprint(
            payload=payload, selected_group_keys=selected_keys
        )
        now = self._now()
        try:
            prepared = self._source_persistence.prepare_from_preview(
                PersistSourceMatrixFromPreviewCommand(
                    project_id=command.project_id,
                    source_document_path=command.source_document_path,
                    source_document_name=command.source_document_name,
                    source_format=command.source_format,
                    payload=payload,
                    selected_group_keys=selected_keys,
                    created_at=now,
                    task261_commit_fingerprint=task261_fingerprint,
                )
            )
        except SourceMatrixImportPersistenceError as exc:
            raise MatrixImportCommitError(str(exc)) from exc
        _validate_source_snapshot(prepared.snapshot)
        draft = build_selected_only_draft(
            project_id=command.project_id,
            source_import_id=prepared.import_record.import_id,
            source_snapshot_id=prepared.snapshot.snapshot_id,
            selected_group_keys=selected_keys,
            source_snapshot=prepared.snapshot,
            preview_payload=payload,
            created_at=now,
        )
        _validate_draft(draft)
        source_locator_fingerprint = fingerprint(
            {
                "path": canonical_windows_path(command.source_document_path),
                "name": command.source_document_name.strip(),
                "format": command.source_format.strip().casefold(),
            }
        )
        try:
            authority = self._method_authority.resolve(
                draft=draft,
                source_snapshot=prepared.snapshot,
                project_id=command.project_id,
                source_import_id=prepared.import_record.import_id,
                source_snapshot_id=prepared.snapshot.snapshot_id,
                task261_commit_fingerprint=task261_fingerprint,
                source_locator_fingerprint=source_locator_fingerprint,
                payload_fingerprint=payload_fingerprint,
                selected_group_fingerprint=fingerprint(list(selected_keys)),
                source_root_fingerprint=fingerprint_source_snapshot(prepared.snapshot),
                source_row_fingerprint=fingerprint_source_rows(prepared.snapshot),
            )
        except MatrixImportMethodAuthorityError as exc:
            raise MatrixImportCommitError(str(exc)) from exc
        existing = self._source_imports.get_import_by_project_and_fingerprint(
            project_id=command.project_id,
            task261_commit_fingerprint=task261_fingerprint,
        )
        if existing is not None:
            return self._reuse(command.project_id, selected_keys, existing, authority)
        return self._persist_new(selected_keys, prepared, authority)

    def _reuse(self, project_id, selected_keys, existing, authority):
        source = self._source_imports.get_snapshot_by_import(existing.import_id)
        draft_record = self._drafts.get_by_project_and_source_import(project_id, existing.import_id)
        draft = self._drafts.get(draft_record.project_matrix_draft_id) if draft_record else None
        if source is None or draft_record is None or draft is None:
            raise MatrixImportCommitConflictError(
                "Existing Matrix import aggregate is incomplete and cannot be reused."
            )
        try:
            summary = verify_reusable_method_authority(
                current=authority,
                existing_import=existing,
                existing_source=source,
                existing_draft=draft,
            )
        except MatrixImportMethodAuthorityError as exc:
            raise MatrixImportCommitConflictError(str(exc)) from exc
        return MatrixImportCommitResult(
            source_import_id=existing.import_id,
            source_snapshot_id=source.snapshot_id,
            selected_group_keys_committed=selected_keys,
            commit_status="reused",
            project_matrix_draft=draft,
            method_authority_sync=summary,
        )

    def _persist_new(self, selected_keys, prepared, authority):
        try:
            with self._transaction_scope():
                persisted = self._source_persistence.persist_prepared(prepared)
                self._drafts.create_snapshot(authority.draft)
                stored_import = self._source_imports.get_import_by_project_and_fingerprint(
                    project_id=prepared.import_record.project_id,
                    task261_commit_fingerprint=(
                        prepared.import_record.task261_commit_fingerprint or ""
                    ),
                )
                source = self._source_imports.get_snapshot_by_import(persisted.import_id)
                draft = self._drafts.get(authority.draft.record.project_matrix_draft_id)
                if (
                    stored_import is None
                    or stored_import.import_id != persisted.import_id
                    or source is None
                    or source.snapshot_id != persisted.snapshot_id
                    or draft is None
                ):
                    raise MatrixImportCommitConflictError(
                        "Persisted Matrix import lineage could not be read-verified."
                    )
                verify_new_method_authority(
                    expected=authority,
                    persisted_source=source,
                    persisted_draft=draft,
                )
        except MatrixImportCommitConflictError:
            raise
        except Exception as exc:
            raise MatrixImportCommitConflictError(
                "Matrix import persistence conflicted and was rolled back."
            ) from exc
        return MatrixImportCommitResult(
            source_import_id=persisted.import_id,
            source_snapshot_id=persisted.snapshot_id,
            selected_group_keys_committed=selected_keys,
            commit_status="created",
            project_matrix_draft=draft,
            method_authority_sync=authority.summary,
        )

    def _require_project(self, project_id: str) -> Project:
        project = self._projects.get(project_id)
        if project is None:
            raise MatrixImportCommitNotFoundError(f"Project not found: {project_id}")
        return project


def _freeze_payload(preview_payload: dict[str, Any]) -> tuple[dict[str, Any], str]:
    if not isinstance(preview_payload, dict):
        raise MatrixImportCommitError("preview_payload must be an object.")
    try:
        canonical = json.dumps(
            preview_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        payload = json.loads(canonical)
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise MatrixImportCommitError("preview_payload must contain JSON values.") from exc
    return payload, fingerprint(payload)


def _normalize_selected_group_keys(values: tuple[str, ...]) -> tuple[str, ...]:
    if not values:
        raise MatrixImportCommitError("selected_group_keys is required.")
    normalized = tuple(value.strip() for value in values)
    if any(not value for value in normalized):
        raise MatrixImportCommitError("selected_group_keys contains an empty key.")
    if len(set(normalized)) != len(normalized):
        raise MatrixImportCommitError("Duplicate selected group key is not allowed.")
    return normalized


def _validate_selected_group_keys(selected: tuple[str, ...], payload: dict[str, Any]) -> None:
    groups = payload.get("groups")
    available = {
        str(group.get("group_key") or f"group_{index}").strip()
        for index, group in enumerate(groups if isinstance(groups, list) else (), start=1)
        if isinstance(group, dict)
    }
    unknown = sorted(set(selected) - available)
    if unknown:
        raise MatrixImportCommitError(f"Unknown selected group keys: {', '.join(unknown)}")


def _validate_payload_minimum(payload: dict[str, Any]) -> None:
    groups = payload.get("groups")
    if not isinstance(groups, list) or not groups:
        raise MatrixImportCommitError("preview_payload must include a non-empty groups list.")
    rows = payload.get("rows")
    if isinstance(rows, list) and rows:
        if any(not isinstance(row, dict) for row in rows):
            raise MatrixImportCommitError("preview_payload rows list contains non-object entries.")
        return
    if not any(
        isinstance(group, dict) and isinstance(group.get("steps"), list) and group["steps"]
        for group in groups
    ):
        raise MatrixImportCommitError(
            "preview_payload must include rows or group steps for source persistence."
        )


def _validate_source_snapshot(snapshot: SourceMatrixSnapshot) -> None:
    if not snapshot.groups or not snapshot.rows or not snapshot.cells:
        raise MatrixImportCommitError("Prepared source snapshot is incomplete.")


def _validate_draft(draft: ProjectMatrixDraftSnapshot) -> None:
    if not draft.groups or not draft.rows or not draft.cells:
        raise MatrixImportCommitError("Selected-only draft is incomplete.")
