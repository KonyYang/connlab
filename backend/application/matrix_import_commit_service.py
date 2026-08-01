"""Atomic Import Matrix Replace commit orchestration."""

from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext
from dataclasses import dataclass, replace
from datetime import UTC, datetime
import json
from typing import Any, Callable, Protocol

from backend.application.matrix_import_draft_builder import build_selected_only_draft
from backend.application.matrix_import_method_authority import (
    _context_identity,
    fingerprint_draft_methods,
    fingerprint_draft_snapshot,
    MatrixImportMethodAuthorityError,
    MatrixImportMethodAuthorityConflictError,
    MatrixImportMethodAuthorityResolver,
    MatrixImportMethodAuthorityResult,
    MatrixImportMethodAuthoritySummary,
    MatrixImportStandardVersionActionRequiredError,
    StandardVersionUnavailableAction,
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


class MatrixImportCommitStandardVersionActionRequiredError(MatrixImportCommitConflictError):
    """Raised when Matrix Replace needs an explicit Standard version choice."""

    def __init__(self, reason_code: str) -> None:
        super().__init__("Standard version file unavailable.")
        self.reason_code = reason_code


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
    standard_version_unavailable_action: StandardVersionUnavailableAction = (
        "prompt_if_unavailable"
    )


@dataclass(frozen=True, slots=True)
class MatrixImportCommitResult:
    source_import_id: str
    source_snapshot_id: str
    selected_group_keys_committed: tuple[str, ...]
    commit_status: str
    project_matrix_draft: ProjectMatrixDraftSnapshot
    method_authority_sync: MatrixImportMethodAuthoritySummary


def verify_reusable_method_authority(
    *,
    current: MatrixImportMethodAuthorityResult,
    existing_import: SourceMatrixImportRecord,
    existing_source: SourceMatrixSnapshot,
    existing_draft: ProjectMatrixDraftSnapshot,
) -> MatrixImportMethodAuthoritySummary:
    """Fail closed unless a persisted import exactly matches current authority."""
    try:
        existing = json.loads(existing_draft.record.method_sync_context_json or "")
        current_context = json.loads(current.context_json)
    except (TypeError, json.JSONDecodeError) as exc:
        raise MatrixImportMethodAuthorityConflictError(
            "Existing Matrix import Method authority context is missing or malformed."
        ) from exc
    if not isinstance(existing, dict) or not isinstance(current_context, dict):
        raise MatrixImportMethodAuthorityConflictError(
            "Existing Matrix import Method authority context is invalid."
        )
    if existing.get("context_identity_fingerprint") != _context_identity(existing):
        raise MatrixImportMethodAuthorityConflictError(
            "Existing Matrix import Method authority context fingerprint is invalid."
        )
    stored_facts = {
        "task261_commit_fingerprint": existing_import.task261_commit_fingerprint,
        "source_locator_fingerprint": fingerprint(
            {
                "path": canonical_windows_path(existing_import.source_document_path),
                "name": existing_import.source_document_name.strip(),
                "format": existing_import.source_format.strip().casefold(),
            }
        ),
        "payload_fingerprint": fingerprint(existing_import.source_preview_payload)
        if existing_import.source_preview_payload
        else None,
        "selected_group_fingerprint": fingerprint(
            list(existing_import.selected_group_keys_at_import)
        ),
    }
    if any(existing.get(key) != value for key, value in stored_facts.items()):
        raise MatrixImportMethodAuthorityConflictError(
            "Existing Source Matrix import facts diverge from Method authority context."
        )
    expected_ids = {
        "project_id": existing_draft.record.project_id,
        "source_import_id": existing_import.import_id,
        "source_snapshot_id": existing_source.snapshot_id,
        "project_matrix_draft_id": existing_draft.record.project_matrix_draft_id,
    }
    if any(existing.get(key) != value for key, value in expected_ids.items()):
        raise MatrixImportMethodAuthorityConflictError(
            "Existing Matrix import lineage does not match its Method authority context."
        )
    if (
        existing_source.import_id != existing_import.import_id
        or existing_source.project_id != existing_import.project_id
        or existing_draft.record.source_import_id != existing_import.import_id
        or existing_draft.record.source_snapshot_id != existing_source.snapshot_id
    ):
        raise MatrixImportMethodAuthorityConflictError(
            "Existing Source Matrix and editable draft lineage is inconsistent."
        )
    ignored = {*expected_ids, "context_identity_fingerprint", "applied_at"}
    existing_comparable = {key: value for key, value in existing.items() if key not in ignored}
    current_comparable = {
        key: value for key, value in current_context.items() if key not in ignored
    }
    if existing_comparable != current_comparable:
        raise MatrixImportMethodAuthorityConflictError(
            "Matrix import or Standard authority changed. Replace cannot reuse the prior import."
        )
    _verify_persisted_fingerprints(existing, existing_source, existing_draft)
    return replace(
        current.summary,
        context_fingerprint=str(existing["context_identity_fingerprint"]),
    )


def verify_new_method_authority(
    *,
    expected: MatrixImportMethodAuthorityResult,
    persisted_source: SourceMatrixSnapshot,
    persisted_draft: ProjectMatrixDraftSnapshot,
) -> None:
    """Read-verify one newly persisted source/draft aggregate before commit."""
    if persisted_draft.record.method_sync_context_json != expected.context_json:
        raise MatrixImportMethodAuthorityConflictError(
            "Persisted Matrix Method authority context could not be verified."
        )
    _verify_persisted_fingerprints(
        json.loads(expected.context_json), persisted_source, persisted_draft
    )


def _verify_persisted_fingerprints(context, source, draft) -> None:
    checks = {
        "source_root_fingerprint": fingerprint_source_snapshot(source),
        "source_row_fingerprint": fingerprint_source_rows(source),
        "post_method_fingerprint": fingerprint_draft_methods(draft, source),
        "result_fingerprint": fingerprint_draft_snapshot(draft, source),
    }
    if any(context.get(key) != value for key, value in checks.items()):
        raise MatrixImportMethodAuthorityConflictError(
            "Persisted Matrix import authority could not be read-verified."
        )


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
                standard_version_unavailable_action=(
                    command.standard_version_unavailable_action
                ),
            )
        except MatrixImportStandardVersionActionRequiredError as exc:
            raise MatrixImportCommitStandardVersionActionRequiredError(
                exc.reason_code
            ) from exc
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
