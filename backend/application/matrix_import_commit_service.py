"""Application service for TASK_261 matrix import group-selection commit."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import uuid4

from backend.application.source_matrix_import_persistence_service import (
    PersistSourceMatrixFromPreviewCommand,
    SourceMatrixImportPersistenceError,
    SourceMatrixImportPersistenceService,
)
from backend.domain import (
    Project,
    ProjectMatrixDraftCell,
    ProjectMatrixDraftGroup,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftRow,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStatus,
    SourceMatrixImportRecord,
    SourceMatrixSnapshot,
)


class MatrixImportCommitError(ValueError):
    """Raised when matrix import commit input is invalid."""


class MatrixImportCommitNotFoundError(LookupError):
    """Raised when required project/lineage resources are not found."""


class MatrixImportCommitConflictError(MatrixImportCommitError):
    """Raised when idempotent reuse cannot resolve to an existing draft."""


class ProjectStore(Protocol):
    """Project lookup operations required by this service."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by id."""


class SourceImportStore(Protocol):
    """Source import lookup operations required by this service."""

    def get_import_by_project_and_fingerprint(
        self,
        *,
        project_id: str,
        task261_commit_fingerprint: str,
    ) -> SourceMatrixImportRecord | None:
        """Return one Source Matrix import record by project/fingerprint."""

    def get_snapshot_by_import(self, import_id: str) -> SourceMatrixSnapshot | None:
        """Return one Source Matrix snapshot by import id."""


class ProjectMatrixDraftStore(Protocol):
    """Project Matrix draft persistence operations required by this service."""

    def create_snapshot(self, snapshot: ProjectMatrixDraftSnapshot) -> ProjectMatrixDraftSnapshot:
        """Persist one draft aggregate."""

    def get_by_project_and_source_import(
        self,
        project_id: str,
        source_import_id: str,
    ) -> ProjectMatrixDraftRecord | None:
        """Return one draft record by project/source import."""

    def get(self, project_matrix_draft_id: str) -> ProjectMatrixDraftSnapshot | None:
        """Return one draft aggregate by id."""


@dataclass(frozen=True, slots=True)
class MatrixImportCommitCommand:
    """Input payload for matrix import commit."""

    project_id: str
    source_document_path: str
    source_document_name: str
    source_format: str
    preview_payload: dict[str, Any]
    selected_group_keys: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MatrixImportCommitResult:
    """Result payload for matrix import commit."""

    source_import_id: str
    source_snapshot_id: str
    selected_group_keys_committed: tuple[str, ...]
    commit_status: str
    project_matrix_draft: ProjectMatrixDraftSnapshot


class MatrixImportCommitService:
    """Persist full source lineage and create selected-only Project Matrix draft."""

    def __init__(
        self,
        *,
        project_store: ProjectStore,
        source_store: SourceImportStore,
        draft_store: ProjectMatrixDraftStore,
        source_persistence_service: SourceMatrixImportPersistenceService,
    ) -> None:
        self._projects = project_store
        self._source_imports = source_store
        self._drafts = draft_store
        self._source_persistence = source_persistence_service

    def commit(self, command: MatrixImportCommitCommand) -> MatrixImportCommitResult:
        """Commit matrix preview payload and selected groups into source + draft lineage."""
        self._require_project(command.project_id)
        payload = _normalize_payload(command.preview_payload)
        _validate_payload_minimum(payload)
        selected_keys = _normalize_selected_group_keys(command.selected_group_keys)
        _validate_selected_group_keys(selected_keys, payload)
        fingerprint = self._source_persistence.compute_task261_fingerprint(
            payload=payload,
            selected_group_keys=selected_keys,
        )
        existing_import = self._source_imports.get_import_by_project_and_fingerprint(
            project_id=command.project_id,
            task261_commit_fingerprint=fingerprint,
        )
        if existing_import is not None:
            existing_draft = self._drafts.get_by_project_and_source_import(
                command.project_id,
                existing_import.import_id,
            )
            if existing_draft is None:
                raise MatrixImportCommitConflictError(
                    "Fingerprint matched existing source import, but project matrix draft is missing."
                )
            existing_snapshot = self._drafts.get(existing_draft.project_matrix_draft_id)
            if existing_snapshot is None:
                raise MatrixImportCommitConflictError(
                    "Existing project matrix draft record was found, but draft snapshot is missing."
                )
            return MatrixImportCommitResult(
                source_import_id=existing_import.import_id,
                source_snapshot_id=existing_draft.source_snapshot_id,
                selected_group_keys_committed=selected_keys,
                commit_status="reused",
                project_matrix_draft=existing_snapshot,
            )
        now = _utc_now()
        try:
            persist_result = self._source_persistence.persist_from_preview(
                PersistSourceMatrixFromPreviewCommand(
                    project_id=command.project_id,
                    source_document_path=command.source_document_path,
                    source_document_name=command.source_document_name,
                    source_format=command.source_format,
                    payload=payload,
                    selected_group_keys=selected_keys,
                    created_at=now,
                    task261_commit_fingerprint=fingerprint,
                )
            )
        except SourceMatrixImportPersistenceError as exc:
            raise MatrixImportCommitError(str(exc)) from exc
        source_snapshot = self._source_imports.get_snapshot_by_import(persist_result.import_id)
        if source_snapshot is None:
            raise MatrixImportCommitNotFoundError(
                f"Source matrix snapshot not found for import: {persist_result.import_id}"
            )
        _validate_persisted_source_snapshot(source_snapshot)
        draft_snapshot = _build_selected_only_draft(
            project_id=command.project_id,
            source_import_id=persist_result.import_id,
            source_snapshot_id=persist_result.snapshot_id,
            selected_group_keys=selected_keys,
            source_snapshot=source_snapshot,
            created_at=now,
        )
        _validate_selected_only_draft_snapshot(draft_snapshot)
        created = self._drafts.create_snapshot(draft_snapshot)
        return MatrixImportCommitResult(
            source_import_id=persist_result.import_id,
            source_snapshot_id=persist_result.snapshot_id,
            selected_group_keys_committed=selected_keys,
            commit_status="created",
            project_matrix_draft=created,
        )

    def _require_project(self, project_id: str) -> Project:
        project = self._projects.get(project_id)
        if project is None:
            raise MatrixImportCommitNotFoundError(f"Project not found: {project_id}")
        return project


def _normalize_payload(preview_payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(preview_payload, dict):
        raise MatrixImportCommitError("preview_payload must be an object.")
    return preview_payload


def _normalize_selected_group_keys(selected_group_keys: tuple[str, ...]) -> tuple[str, ...]:
    if len(selected_group_keys) == 0:
        raise MatrixImportCommitError("selected_group_keys is required.")
    normalized: list[str] = []
    seen: set[str] = set()
    for item in selected_group_keys:
        text = item.strip()
        if not text:
            raise MatrixImportCommitError("selected_group_keys contains an empty key.")
        if text in seen:
            raise MatrixImportCommitError(
                f"Duplicate selected group key is not allowed: {text}"
            )
        seen.add(text)
        normalized.append(text)
    return tuple(normalized)


def _validate_selected_group_keys(
    selected_group_keys: tuple[str, ...],
    payload: dict[str, Any],
) -> None:
    groups = payload.get("groups")
    if not isinstance(groups, list) or len(groups) == 0:
        raise MatrixImportCommitError("preview_payload must include a non-empty groups list.")
    available_keys: set[str] = set()
    for index, group in enumerate(groups, start=1):
        if not isinstance(group, dict):
            continue
        key = str(group.get("group_key", "")).strip()
        if not key:
            key = f"group_{index}"
        available_keys.add(key)
    unknown = sorted(set(selected_group_keys) - available_keys)
    if unknown:
        raise MatrixImportCommitError(
            f"Unknown selected group keys: {', '.join(unknown)}"
        )


def _validate_payload_minimum(payload: dict[str, Any]) -> None:
    groups = payload.get("groups")
    if not isinstance(groups, list) or len(groups) == 0:
        raise MatrixImportCommitError("preview_payload must include a non-empty groups list.")
    rows = payload.get("rows")
    if isinstance(rows, list) and len(rows) > 0:
        if any(not isinstance(row, dict) for row in rows):
            raise MatrixImportCommitError(
                "preview_payload rows list contains non-object entries."
            )
        return
    has_steps = False
    for group in groups:
        if not isinstance(group, dict):
            continue
        steps = group.get("steps")
        if isinstance(steps, list) and len(steps) > 0:
            has_steps = True
            break
    if not has_steps:
        raise MatrixImportCommitError(
            "preview_payload must include rows or group steps for source persistence."
        )


def _validate_persisted_source_snapshot(source_snapshot: SourceMatrixSnapshot) -> None:
    if len(source_snapshot.groups) == 0:
        raise MatrixImportCommitError("Persisted source snapshot has no groups.")
    if len(source_snapshot.rows) == 0:
        raise MatrixImportCommitError("Persisted source snapshot has no rows.")
    if len(source_snapshot.cells) == 0:
        raise MatrixImportCommitError("Persisted source snapshot has no sparse cells.")


def _validate_selected_only_draft_snapshot(
    draft_snapshot: ProjectMatrixDraftSnapshot,
) -> None:
    if len(draft_snapshot.groups) == 0:
        raise MatrixImportCommitError("Selected-only draft has no groups.")
    if len(draft_snapshot.rows) == 0:
        raise MatrixImportCommitError("Selected-only draft has no rows.")
    if len(draft_snapshot.cells) == 0:
        raise MatrixImportCommitError(
            "Selected-only draft has no sparse cells for selected groups."
        )


def _build_selected_only_draft(
    *,
    project_id: str,
    source_import_id: str,
    source_snapshot_id: str,
    selected_group_keys: tuple[str, ...],
    source_snapshot: SourceMatrixSnapshot,
    created_at: str,
) -> ProjectMatrixDraftSnapshot:
    draft_id = f"pmd-{uuid4().hex}"
    record = ProjectMatrixDraftRecord(
        project_matrix_draft_id=draft_id,
        project_id=project_id,
        source_import_id=source_import_id,
        source_snapshot_id=source_snapshot_id,
        status=ProjectMatrixDraftStatus.DRAFT,
        created_at=created_at,
        updated_at=created_at,
        base_confirmed_matrix_id=None,
    )
    selected_set = set(selected_group_keys)
    selected_source_groups = tuple(
        group for group in source_snapshot.groups if group.group_key in selected_set
    )
    group_id_by_source: dict[str, str] = {}
    groups: list[ProjectMatrixDraftGroup] = []
    for order, source_group in enumerate(selected_source_groups, start=1):
        draft_group_id = f"pmdg-{uuid4().hex}"
        group_id_by_source[source_group.group_snapshot_id] = draft_group_id
        groups.append(
            ProjectMatrixDraftGroup(
                draft_group_id=draft_group_id,
                project_matrix_draft_id=draft_id,
                source_group_snapshot_id=source_group.group_snapshot_id,
                group_order=order,
                group_key=source_group.group_key,
                group_label=source_group.group_label,
                is_selected=True,
                sample_quantity_expression=source_group.sample_quantity_expression,
                sample_note=source_group.sample_note,
            )
        )
    row_id_by_source: dict[str, str] = {}
    rows: list[ProjectMatrixDraftRow] = []
    for order, source_row in enumerate(source_snapshot.rows, start=1):
        draft_row_id = f"pmdr-{uuid4().hex}"
        row_id_by_source[source_row.row_snapshot_id] = draft_row_id
        rows.append(
            ProjectMatrixDraftRow(
                draft_row_id=draft_row_id,
                project_matrix_draft_id=draft_id,
                source_row_snapshot_id=source_row.row_snapshot_id,
                row_order=order,
                test_item=source_row.test_item,
                source_section=source_row.source_section,
                method=None,
                condition=None,
                requirement=None,
                is_sample_row=source_row.is_sample_row,
            )
        )
    cells: list[ProjectMatrixDraftCell] = []
    for source_cell in source_snapshot.cells:
        draft_group_id = group_id_by_source.get(source_cell.group_snapshot_id)
        draft_row_id = row_id_by_source.get(source_cell.row_snapshot_id)
        if draft_group_id is None or draft_row_id is None:
            continue
        cell_value = source_cell.cell_value.strip()
        if not cell_value:
            continue
        cells.append(
            ProjectMatrixDraftCell(
                draft_cell_id=f"pmdc-{uuid4().hex}",
                project_matrix_draft_id=draft_id,
                draft_row_id=draft_row_id,
                draft_group_id=draft_group_id,
                cell_value=cell_value,
            )
        )
    return ProjectMatrixDraftSnapshot(
        record=record,
        groups=tuple(groups),
        rows=tuple(rows),
        cells=tuple(cells),
    )


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
