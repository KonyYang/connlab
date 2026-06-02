"""Application service for Matrix Editor temporary session seed/confirm flow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from typing import Any, Literal, Protocol
from uuid import uuid4

from backend.application.confirmed_matrix_authority_service import (
    ConfirmProjectMatrixDraftCommand,
    ConfirmedMatrixAuthorityConflictError,
    ConfirmedMatrixAuthorityError,
    ConfirmedMatrixAuthorityNotFoundError,
    ConfirmedMatrixAuthorityService,
)
from backend.application.matrix_import_commit_service import (
    MatrixImportCommitCommand,
    MatrixImportCommitError,
    MatrixImportCommitNotFoundError,
    MatrixImportCommitService,
)
from backend.application.matrix_schedule_planning import (
    MatrixScheduleFields,
    MatrixScheduleValidationError,
    calculate_group_test_days,
    validate_planned_schedule,
)
from backend.application.matrix_sample_quantity_guard import (
    find_selected_sample_quantity_violations,
    format_sample_quantity_violation_message,
)
from backend.application.matrix_revision_flow_service import (
    CreateMatrixRevisionDraftCommand,
    MatrixRevisionFlowConflictError,
    MatrixRevisionFlowService,
)
from backend.application.project_matrix_draft_persistence_service import (
    ProjectMatrixDraftCellInput,
    ProjectMatrixDraftGroupInput,
    ProjectMatrixDraftPersistenceError,
    ProjectMatrixDraftPersistenceNotFoundError,
    ProjectMatrixDraftPersistenceService,
    ProjectMatrixDraftRowInput,
    UpdateProjectMatrixDraftCommand,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
    Project,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftGroup,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftRow,
    SourceMatrixImportRecord,
    SourceMatrixSnapshot,
)


SOURCE_UNAVAILABLE_MESSAGE = (
    "Original source Matrix is unavailable. Use Import Matrix to reselect groups."
)


class MatrixEditorSessionError(ValueError):
    """Raised when Matrix Editor session input is invalid."""


class MatrixEditorSessionNotFoundError(LookupError):
    """Raised when required project resources are not found."""


class MatrixEditorSessionActiveChangedError(MatrixEditorSessionError):
    """Raised when active matrix changed while a session was open."""


class ProjectStore(Protocol):
    """Project lookup operations required by this service."""

    def get(self, project_id: str) -> Project | None:
        """Return one project by id."""


class ConfirmedStore(Protocol):
    """Confirmed matrix lookup operations required by this service."""

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        """Return one active confirmed matrix snapshot."""

    def supersede_active_and_create_snapshot(
        self,
        *,
        previous_active_confirmed_matrix_id: str,
        snapshot: ConfirmedMatrixSnapshot,
        superseded_reason: str | None = None,
    ) -> ConfirmedMatrixSnapshot:
        """Supersede active authority and persist new active snapshot atomically."""


class SourceStore(Protocol):
    """Source matrix lookup operations required by this service."""

    def get_import(self, import_id: str) -> SourceMatrixImportRecord | None:
        """Return one source import by id."""

    def get_snapshot(self, snapshot_id: str) -> SourceMatrixSnapshot | None:
        """Return one source snapshot by id."""


class DraftStore(Protocol):
    """Draft lookup operations required by this service."""

    def get_by_project_and_base_confirmed_matrix(
        self,
        project_id: str,
        base_confirmed_matrix_id: str,
    ) -> ProjectMatrixDraftRecord | None:
        """Return one draft record by project/base confirmed matrix id."""

    def get_by_project_and_source_import(
        self,
        project_id: str,
        source_import_id: str,
    ) -> ProjectMatrixDraftRecord | None:
        """Return one draft record by project/source import lineage."""


@dataclass(frozen=True, slots=True)
class MatrixEditorSessionGroup:
    """Session editor group payload."""

    draft_group_id: str
    source_group_snapshot_id: str | None
    group_order: int
    group_key: str
    group_label: str
    is_selected: bool
    sample_quantity_expression: str | None
    sample_note: str | None


@dataclass(frozen=True, slots=True)
class MatrixEditorSessionRow:
    """Session editor row payload."""

    draft_row_id: str
    source_row_snapshot_id: str | None
    row_order: int
    test_item: str
    source_section: str | None
    method: str | None
    condition: str | None
    requirement: str | None
    is_sample_row: bool
    day_expression: str | None = None


@dataclass(frozen=True, slots=True)
class MatrixEditorSessionCell:
    """Session editor sparse cell payload."""

    draft_row_id: str
    draft_group_id: str
    cell_value: str


@dataclass(frozen=True, slots=True)
class MatrixEditorSessionDraft:
    """Session editor snapshot payload."""

    groups: tuple[MatrixEditorSessionGroup, ...]
    rows: tuple[MatrixEditorSessionRow, ...]
    cells: tuple[MatrixEditorSessionCell, ...]


@dataclass(frozen=True, slots=True)
class MatrixEditorSessionSeed:
    """Session seed response payload."""

    project_id: str
    active_confirmed_matrix_id: str | None
    active_confirmed_revision: int | None
    active_source_import_id: str | None
    active_source_snapshot_id: str | None
    editor_draft: MatrixEditorSessionDraft | None
    source_preview_payload: dict[str, Any] | None
    source_status: Literal["available", "unavailable", "not_required"]
    source_unavailable_message: str | None
    pre_test_buffer_days: str | None = None
    post_test_buffer_days: str | None = None
    sample_received_date: str | None = None
    planned_test_start_date: str | None = None
    planned_test_complete_date: str | None = None
    estimated_completion_date: str | None = None


@dataclass(frozen=True, slots=True)
class MatrixEditorSessionConfirmCommand:
    """Input payload for session confirm API."""

    project_id: str
    expected_active_confirmed_matrix_id: str | None
    expected_active_confirmed_revision: int | None
    source_document_path: str | None
    source_document_name: str | None
    source_format: str | None
    source_import_id: str | None
    source_snapshot_id: str | None
    confirmed_by: str
    groups: tuple[MatrixEditorSessionGroup, ...]
    rows: tuple[MatrixEditorSessionRow, ...]
    cells: tuple[MatrixEditorSessionCell, ...]
    pre_test_buffer_days: str | None = None
    post_test_buffer_days: str | None = None
    sample_received_date: str | None = None
    planned_test_start_date: str | None = None
    planned_test_complete_date: str | None = None
    estimated_completion_date: str | None = None


@dataclass(frozen=True, slots=True)
class MatrixEditorSessionConfirmResult:
    """Session confirm response payload."""

    publish_status: Literal["published", "no_change"]
    message: str
    confirmed_snapshot: ConfirmedMatrixSnapshot | None


class MatrixEditorSessionService:
    """Load and publish temporary Matrix Editor sessions."""

    def __init__(
        self,
        *,
        project_store: ProjectStore,
        confirmed_store: ConfirmedStore,
        source_store: SourceStore,
        draft_store: DraftStore,
        draft_persistence_service: ProjectMatrixDraftPersistenceService,
        matrix_import_commit_service: MatrixImportCommitService,
        matrix_revision_flow_service: MatrixRevisionFlowService,
        confirmed_matrix_authority_service: ConfirmedMatrixAuthorityService,
    ) -> None:
        self._projects = project_store
        self._confirmed = confirmed_store
        self._sources = source_store
        self._drafts = draft_store
        self._draft_persistence = draft_persistence_service
        self._matrix_import_commit = matrix_import_commit_service
        self._matrix_revision = matrix_revision_flow_service
        self._confirmed_authority = confirmed_matrix_authority_service

    def get_seed(self, *, project_id: str) -> MatrixEditorSessionSeed:
        """Build one Matrix Editor seed from active authority and source snapshot lineage."""
        self._require_project(project_id)
        active = self._confirmed.get_active_by_project(project_id)
        if active is None:
            return MatrixEditorSessionSeed(
                project_id=project_id,
                active_confirmed_matrix_id=None,
                active_confirmed_revision=None,
                active_source_import_id=None,
                active_source_snapshot_id=None,
                editor_draft=None,
                source_preview_payload=None,
                source_status="not_required",
                source_unavailable_message=None,
            )
        editor_draft = _build_editor_draft_from_active(active)
        source_snapshot = self._sources.get_snapshot(active.version.source_snapshot_id)
        if source_snapshot is None:
            return MatrixEditorSessionSeed(
                project_id=project_id,
                active_confirmed_matrix_id=active.version.confirmed_matrix_id,
                active_confirmed_revision=active.version.confirmed_revision,
                active_source_import_id=active.version.source_import_id,
                active_source_snapshot_id=active.version.source_snapshot_id,
                editor_draft=editor_draft,
                source_preview_payload=None,
                source_status="unavailable",
                source_unavailable_message=SOURCE_UNAVAILABLE_MESSAGE,
                pre_test_buffer_days=active.version.pre_test_buffer_days,
                post_test_buffer_days=active.version.post_test_buffer_days,
                sample_received_date=active.version.sample_received_date,
                planned_test_start_date=active.version.planned_test_start_date,
                planned_test_complete_date=active.version.planned_test_complete_date,
                estimated_completion_date=active.version.estimated_completion_date,
            )
        import_record = self._sources.get_import(active.version.source_import_id)
        source_preview_payload = _resolve_source_preview_payload(
            source_snapshot=source_snapshot,
            import_record=import_record,
        )
        return MatrixEditorSessionSeed(
            project_id=project_id,
            active_confirmed_matrix_id=active.version.confirmed_matrix_id,
            active_confirmed_revision=active.version.confirmed_revision,
            active_source_import_id=active.version.source_import_id,
            active_source_snapshot_id=active.version.source_snapshot_id,
            editor_draft=editor_draft,
            source_preview_payload=source_preview_payload,
            source_status="available",
            source_unavailable_message=None,
            pre_test_buffer_days=active.version.pre_test_buffer_days,
            post_test_buffer_days=active.version.post_test_buffer_days,
            sample_received_date=active.version.sample_received_date,
            planned_test_start_date=active.version.planned_test_start_date,
            planned_test_complete_date=active.version.planned_test_complete_date,
            estimated_completion_date=active.version.estimated_completion_date,
        )

    def confirm_session(
        self,
        command: MatrixEditorSessionConfirmCommand,
    ) -> MatrixEditorSessionConfirmResult:
        """Confirm one temporary Matrix Editor session into active authority."""
        self._require_project(command.project_id)
        confirmed_by = command.confirmed_by.strip()
        if not confirmed_by:
            raise MatrixEditorSessionError("confirmed_by is required.")
        active = self._confirmed.get_active_by_project(command.project_id)
        self._validate_expected_active(command, active)
        if len(command.groups) == 0:
            raise MatrixEditorSessionError("At least one group is required.")
        if len(command.rows) == 0:
            raise MatrixEditorSessionError("At least one row is required.")
        selected_group_keys = tuple(
            group.group_key.strip()
            for group in command.groups
            if group.is_selected and group.group_key.strip()
        )
        if len(selected_group_keys) == 0:
            raise MatrixEditorSessionError("At least one selected group is required.")
        sample_violations = find_selected_sample_quantity_violations(command.groups)
        if sample_violations:
            raise MatrixEditorSessionError(
                format_sample_quantity_violation_message(sample_violations)
            )
        if not _has_any_step_tokens(command.cells):
            raise MatrixEditorSessionError("At least one step token is required.")
        _validate_session_schedule(command)
        payload_signature = _build_signature_from_session_payload(command)
        if active is not None:
            active_signature = _build_signature_from_confirmed(active)
            if payload_signature == active_signature:
                return MatrixEditorSessionConfirmResult(
                    publish_status="no_change",
                    message="No Matrix changes to confirm.",
                    confirmed_snapshot=None,
                )
            if _is_source_lineage_replaced(command, active):
                confirmed = self._publish_with_source_replacement(
                    command=command,
                    active=active,
                    confirmed_by=confirmed_by,
                )
                return MatrixEditorSessionConfirmResult(
                    publish_status="published",
                    message=f"Matrix confirmed (v{confirmed.version.confirmed_revision}).",
                    confirmed_snapshot=confirmed,
                )
            confirmed = self._publish_as_revision(command, active, confirmed_by)
            return MatrixEditorSessionConfirmResult(
                publish_status="published",
                message=f"Matrix confirmed (v{confirmed.version.confirmed_revision}).",
                confirmed_snapshot=confirmed,
            )
        confirmed = self._publish_as_first_authority(command, selected_group_keys, confirmed_by)
        return MatrixEditorSessionConfirmResult(
            publish_status="published",
            message=f"Matrix confirmed (v{confirmed.version.confirmed_revision}).",
            confirmed_snapshot=confirmed,
        )

    def _publish_as_revision(
        self,
        command: MatrixEditorSessionConfirmCommand,
        active: ConfirmedMatrixSnapshot,
        confirmed_by: str,
    ) -> ConfirmedMatrixSnapshot:
        draft_record = self._drafts.get_by_project_and_base_confirmed_matrix(
            command.project_id,
            active.version.confirmed_matrix_id,
        )
        if draft_record is None:
            try:
                created = self._matrix_revision.create_revision_draft(
                    CreateMatrixRevisionDraftCommand(project_id=command.project_id)
                )
            except MatrixRevisionFlowConflictError as exc:
                raise MatrixEditorSessionActiveChangedError(
                    "Matrix was updated. Reload the latest Matrix to continue."
                ) from exc
            draft_id = created.record.project_matrix_draft_id
        else:
            draft_id = draft_record.project_matrix_draft_id
        saved_snapshot = self._save_payload_to_draft(command, draft_id)
        revision_snapshot = _build_confirmed_snapshot_from_session_draft(
            draft=saved_snapshot,
            confirmed_by=confirmed_by,
            confirmed_revision=active.version.confirmed_revision + 1,
            source_import_id=active.version.source_import_id,
            source_snapshot_id=active.version.source_snapshot_id,
        )
        try:
            return self._confirmed.supersede_active_and_create_snapshot(
                previous_active_confirmed_matrix_id=active.version.confirmed_matrix_id,
                snapshot=revision_snapshot,
                superseded_reason="Matrix Editor session confirm.",
            )
        except LookupError as exc:
            raise MatrixEditorSessionActiveChangedError(
                "Matrix was updated. Reload the latest Matrix to continue."
            ) from exc

    def _publish_with_source_replacement(
        self,
        *,
        command: MatrixEditorSessionConfirmCommand,
        active: ConfirmedMatrixSnapshot,
        confirmed_by: str,
    ) -> ConfirmedMatrixSnapshot:
        source_import_id = (command.source_import_id or "").strip()
        source_snapshot_id = (command.source_snapshot_id or "").strip()
        if not source_import_id or not source_snapshot_id:
            raise MatrixEditorSessionError(
                "Source matrix lineage is required after changing source."
            )
        draft_record = self._drafts.get_by_project_and_source_import(
            command.project_id,
            source_import_id,
        )
        if draft_record is None:
            raise MatrixEditorSessionError(
                "Source matrix draft is not available. Re-import and select groups again."
            )
        saved_snapshot = self._save_payload_to_draft(
            command,
            draft_record.project_matrix_draft_id,
        )
        replacement_snapshot = _build_confirmed_snapshot_from_session_draft(
            draft=saved_snapshot,
            confirmed_by=confirmed_by,
            confirmed_revision=active.version.confirmed_revision + 1,
            source_import_id=source_import_id,
            source_snapshot_id=source_snapshot_id,
        )
        try:
            return self._confirmed.supersede_active_and_create_snapshot(
                previous_active_confirmed_matrix_id=active.version.confirmed_matrix_id,
                snapshot=replacement_snapshot,
                superseded_reason="Matrix Editor source replacement confirm.",
            )
        except LookupError as exc:
            raise MatrixEditorSessionActiveChangedError(
                "Matrix was updated. Reload the latest Matrix to continue."
            ) from exc

    def _publish_as_first_authority(
        self,
        command: MatrixEditorSessionConfirmCommand,
        selected_group_keys: tuple[str, ...],
        confirmed_by: str,
    ) -> ConfirmedMatrixSnapshot:
        preview_payload = _build_manual_preview_payload(command)
        source_document_path = (
            (command.source_document_path or "").strip() or "manual://matrix-editor"
        )
        source_document_name = (
            (command.source_document_name or "").strip() or "Matrix Editor Manual Draft"
        )
        source_format = (command.source_format or "").strip() or "manual"
        try:
            committed = self._matrix_import_commit.commit(
                MatrixImportCommitCommand(
                    project_id=command.project_id,
                    source_document_path=source_document_path,
                    source_document_name=source_document_name,
                    source_format=source_format,
                    preview_payload=preview_payload,
                    selected_group_keys=selected_group_keys,
                )
            )
        except (MatrixImportCommitError, MatrixImportCommitNotFoundError) as exc:
            raise MatrixEditorSessionError(str(exc)) from exc
        draft_id = committed.project_matrix_draft.record.project_matrix_draft_id
        self._save_payload_to_draft(command, draft_id)
        try:
            return self._confirmed_authority.confirm_draft(
                ConfirmProjectMatrixDraftCommand(
                    project_id=command.project_id,
                    project_matrix_draft_id=draft_id,
                    confirmed_by=confirmed_by,
                )
            )
        except (
            ConfirmedMatrixAuthorityError,
            ConfirmedMatrixAuthorityConflictError,
            ConfirmedMatrixAuthorityNotFoundError,
        ) as exc:
            raise MatrixEditorSessionError(str(exc)) from exc

    def _save_payload_to_draft(
        self,
        command: MatrixEditorSessionConfirmCommand,
        draft_id: str,
    ) -> ProjectMatrixDraftSnapshot:
        try:
            return self._draft_persistence.update_draft(
                UpdateProjectMatrixDraftCommand(
                    project_id=command.project_id,
                    project_matrix_draft_id=draft_id,
                    groups=tuple(
                        ProjectMatrixDraftGroupInput(
                            draft_group_id=group.draft_group_id,
                            source_group_snapshot_id=group.source_group_snapshot_id,
                            group_order=group.group_order,
                            group_key=group.group_key,
                            group_label=_normalize_group_label(
                                group.group_label, fallback=str(group.group_order)
                            ),
                            is_selected=group.is_selected,
                            sample_quantity_expression=group.sample_quantity_expression,
                            sample_note=group.sample_note,
                        )
                        for group in command.groups
                    ),
                    rows=tuple(
                        ProjectMatrixDraftRowInput(
                            draft_row_id=row.draft_row_id,
                            source_row_snapshot_id=row.source_row_snapshot_id,
                            row_order=row.row_order,
                            test_item=row.test_item,
                            source_section=row.source_section,
                            method=row.method,
                            condition=row.condition,
                            requirement=row.requirement,
                            day_expression=row.day_expression,
                            is_sample_row=row.is_sample_row,
                        )
                        for row in command.rows
                    ),
                    cells=tuple(
                        ProjectMatrixDraftCellInput(
                            draft_row_id=cell.draft_row_id,
                            draft_group_id=cell.draft_group_id,
                            cell_value=cell.cell_value,
                        )
                        for cell in command.cells
                    ),
                    pre_test_buffer_days=command.pre_test_buffer_days,
                    post_test_buffer_days=command.post_test_buffer_days,
                    sample_received_date=command.sample_received_date,
                    planned_test_start_date=command.planned_test_start_date,
                    planned_test_complete_date=command.planned_test_complete_date,
                    estimated_completion_date=command.estimated_completion_date,
                )
            )
        except (
            ProjectMatrixDraftPersistenceError,
            ProjectMatrixDraftPersistenceNotFoundError,
            LookupError,
        ) as exc:
            raise MatrixEditorSessionError(str(exc)) from exc

    def _validate_expected_active(
        self,
        command: MatrixEditorSessionConfirmCommand,
        active: ConfirmedMatrixSnapshot | None,
    ) -> None:
        expected_active_id = (command.expected_active_confirmed_matrix_id or "").strip()
        if not expected_active_id:
            if active is not None:
                raise MatrixEditorSessionActiveChangedError(
                    "Matrix was updated. Reload the latest Matrix to continue."
                )
            return
        if active is None:
            raise MatrixEditorSessionActiveChangedError(
                "Matrix was updated. Reload the latest Matrix to continue."
            )
        if active.version.confirmed_matrix_id != expected_active_id:
            if _is_same_source_lineage(command, active):
                return
            raise MatrixEditorSessionActiveChangedError(
                "Matrix was updated. Reload the latest Matrix to continue."
            )
        if (
            command.expected_active_confirmed_revision is not None
            and active.version.confirmed_revision
            != command.expected_active_confirmed_revision
        ):
            if _is_same_source_lineage(command, active):
                return
            raise MatrixEditorSessionActiveChangedError(
                "Matrix was updated. Reload the latest Matrix to continue."
            )

    def _require_project(self, project_id: str) -> None:
        project = self._projects.get(project_id)
        if project is None:
            raise MatrixEditorSessionNotFoundError(f"Project not found: {project_id}")


def _build_editor_draft_from_active(
    active: ConfirmedMatrixSnapshot,
) -> MatrixEditorSessionDraft:
    groups = tuple(
        MatrixEditorSessionGroup(
            draft_group_id=group.draft_group_id,
            source_group_snapshot_id=group.source_group_snapshot_id,
            group_order=group.group_order,
            group_key=group.group_key,
            group_label=_normalize_group_label(
                group.group_label, fallback=str(group.group_order)
            ),
            is_selected=True,
            sample_quantity_expression=group.sample_quantity_expression,
            sample_note=group.sample_note,
        )
        for group in sorted(active.groups, key=lambda item: item.group_order)
    )
    rows = tuple(
        MatrixEditorSessionRow(
            draft_row_id=row.draft_row_id,
            source_row_snapshot_id=row.source_row_snapshot_id,
            row_order=row.row_order,
            test_item=row.test_item,
            source_section=row.source_section,
            method=row.method,
            condition=row.condition,
            requirement=row.requirement,
            day_expression=row.day_expression,
            is_sample_row=False,
        )
        for row in sorted(active.rows, key=lambda item: item.row_order)
    )
    cells = tuple(
        MatrixEditorSessionCell(
            draft_row_id=cell.draft_row_id,
            draft_group_id=cell.draft_group_id,
            cell_value=cell.cell_value,
        )
        for cell in active.cells
    )
    return MatrixEditorSessionDraft(groups=groups, rows=rows, cells=cells)


def _build_source_preview_payload(
    *,
    source_snapshot: SourceMatrixSnapshot,
    import_record: SourceMatrixImportRecord | None,
) -> dict[str, Any]:
    sorted_groups = sorted(source_snapshot.groups, key=lambda item: item.group_order)
    sorted_rows = sorted(source_snapshot.rows, key=lambda item: item.row_order)
    token_map: dict[tuple[str, str], str] = {}
    for cell in source_snapshot.cells:
        token_map[(cell.row_snapshot_id, cell.group_snapshot_id)] = cell.cell_value
    rows: list[dict[str, Any]] = []
    for row in sorted_rows:
        row_tokens: dict[str, str] = {}
        for group in sorted_groups:
            value = token_map.get((row.row_snapshot_id, group.group_snapshot_id), "")
            row_tokens[group.group_label] = value
            row_tokens[group.group_key] = value
        rows.append(
            {
                "source_row_index": row.source_row_index if row.source_row_index is not None else row.row_order,
                "test_item": row.test_item,
                "source_section": row.source_section,
                "method": row.method,
                "condition": row.condition,
                "requirement": row.requirement,
                "group_tokens": row_tokens,
                "is_sample_row": bool(row.is_sample_row),
            }
        )
    groups = [
        {
            "group_key": group.group_key,
            "group_label": group.group_label,
            "source_table_index": source_snapshot.source_table_index or 0,
            "extraction_status": "loaded",
            "sample_size": group.sample_size,
            "sample_quantity_expression": group.sample_quantity_expression,
            "sample_note": group.sample_note,
            "steps": [],
        }
        for group in sorted_groups
    ]
    return {
        "project_id": source_snapshot.project_id,
        "source_document_path": import_record.source_document_path if import_record else "unknown://source",
        "source_document_name": import_record.source_document_name if import_record else "Source Matrix",
        "source_format": import_record.source_format if import_record else "unknown",
        "capability_status": "supported",
        "generated_at": _utc_now(),
        "selected_table_index": source_snapshot.source_table_index,
        "selected_page_number": None,
        "selected_page_table_index": None,
        "candidate_tables": [],
        "preview_pdf_token": None,
        "rows": rows,
        "groups": groups,
        "warnings": [],
        "blockers": [],
    }


def _resolve_source_preview_payload(
    *,
    source_snapshot: SourceMatrixSnapshot,
    import_record: SourceMatrixImportRecord | None,
) -> dict[str, Any]:
    cached_payload = _normalize_cached_source_preview_payload(import_record)
    if cached_payload is not None:
        return cached_payload
    return _build_source_preview_payload(
        source_snapshot=source_snapshot,
        import_record=import_record,
    )


def _normalize_cached_source_preview_payload(
    import_record: SourceMatrixImportRecord | None,
) -> dict[str, Any] | None:
    if import_record is None or import_record.source_preview_payload is None:
        return None
    payload = import_record.source_preview_payload
    groups = payload.get("groups")
    rows = payload.get("rows")
    if not isinstance(groups, list) or not isinstance(rows, list):
        return None
    try:
        normalized = json.loads(json.dumps(payload, ensure_ascii=False))
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    if not isinstance(normalized, dict):
        return None
    normalized.setdefault("source_document_path", import_record.source_document_path)
    normalized.setdefault("source_document_name", import_record.source_document_name)
    normalized.setdefault("source_format", import_record.source_format)
    normalized.setdefault("warnings", [])
    normalized.setdefault("blockers", [])
    normalized.setdefault("candidate_tables", [])
    return normalized


def _has_any_step_tokens(cells: tuple[MatrixEditorSessionCell, ...]) -> bool:
    return any((cell.cell_value or "").strip() for cell in cells)


def _validate_session_schedule(command: MatrixEditorSessionConfirmCommand) -> None:
    selected_group_ids = [
        group.draft_group_id
        for group in command.groups
        if group.is_selected and group.draft_group_id.strip()
    ]
    try:
        totals = calculate_group_test_days(
            rows=(
                {
                    "row_id": row.draft_row_id,
                    "day_expression": row.day_expression,
                    "is_sample_row": row.is_sample_row,
                }
                for row in command.rows
            ),
            cells=(
                {
                    "row_id": cell.draft_row_id,
                    "group_id": cell.draft_group_id,
                    "cell_value": cell.cell_value,
                }
                for cell in command.cells
            ),
            selected_group_ids=selected_group_ids,
        )
        validate_planned_schedule(
            fields=MatrixScheduleFields(
                pre_test_buffer_days=command.pre_test_buffer_days,
                post_test_buffer_days=command.post_test_buffer_days,
                sample_received_date=command.sample_received_date,
                planned_test_start_date=command.planned_test_start_date,
                planned_test_complete_date=command.planned_test_complete_date,
                estimated_completion_date=command.estimated_completion_date,
            ),
            group_test_days=totals,
        )
    except MatrixScheduleValidationError as exc:
        raise MatrixEditorSessionError(str(exc)) from exc


def _build_signature_from_session_payload(
    command: MatrixEditorSessionConfirmCommand,
) -> str:
    groups = sorted(
        (group for group in command.groups if group.is_selected),
        key=lambda item: item.group_order,
    )
    rows = sorted(
        (row for row in command.rows if not row.is_sample_row),
        key=lambda item: item.row_order,
    )
    group_index = {group.draft_group_id: idx for idx, group in enumerate(groups)}
    row_index = {row.draft_row_id: idx for idx, row in enumerate(rows)}
    cell_map: dict[tuple[int, int], str] = {}
    for cell in command.cells:
        r_index = row_index.get(cell.draft_row_id)
        g_index = group_index.get(cell.draft_group_id)
        if r_index is None or g_index is None:
            continue
        value = (cell.cell_value or "").strip()
        if not value:
            continue
        cell_map[(r_index, g_index)] = value
    payload = {
        "groups": [
            {
                "group_order": group_index + 1,
                "group_key": group.group_key.strip(),
                "group_label": _normalize_group_label(
                    group.group_label, fallback=str(group_index + 1)
                ),
                "sample_quantity_expression": (group.sample_quantity_expression or "").strip(),
                "sample_note": (group.sample_note or "").strip(),
                "is_selected": True,
            }
            for group_index, group in enumerate(groups)
        ],
        "rows": [
            {
                "row_order": row.row_order,
                "test_item": row.test_item.strip(),
                "source_section": (row.source_section or "").strip(),
                "method": (row.method or "").strip(),
                "condition": (row.condition or "").strip(),
                "requirement": (row.requirement or "").strip(),
                "day_expression": (row.day_expression or "").strip(),
                "cells": [
                    cell_map.get((row_idx, group_idx), "")
                    for group_idx, _ in enumerate(groups)
                ],
            }
            for row_idx, row in enumerate(rows)
        ],
        "schedule": _schedule_signature_from_command(command),
    }
    return repr(payload)


def _schedule_signature_from_command(
    command: MatrixEditorSessionConfirmCommand,
) -> dict[str, str]:
    return {
        "pre_test_buffer_days": (command.pre_test_buffer_days or "").strip(),
        "post_test_buffer_days": (command.post_test_buffer_days or "").strip(),
        "sample_received_date": (command.sample_received_date or "").strip(),
        "planned_test_start_date": (command.planned_test_start_date or "").strip(),
        "planned_test_complete_date": (command.planned_test_complete_date or "").strip(),
        "estimated_completion_date": (command.estimated_completion_date or "").strip(),
    }


def _schedule_signature_from_confirmed(
    snapshot: ConfirmedMatrixSnapshot,
) -> dict[str, str]:
    return {
        "pre_test_buffer_days": (snapshot.version.pre_test_buffer_days or "").strip(),
        "post_test_buffer_days": (snapshot.version.post_test_buffer_days or "").strip(),
        "sample_received_date": (snapshot.version.sample_received_date or "").strip(),
        "planned_test_start_date": (snapshot.version.planned_test_start_date or "").strip(),
        "planned_test_complete_date": (
            snapshot.version.planned_test_complete_date or ""
        ).strip(),
        "estimated_completion_date": (snapshot.version.estimated_completion_date or "").strip(),
    }


def _build_signature_from_confirmed(snapshot: ConfirmedMatrixSnapshot) -> str:
    groups = sorted(snapshot.groups, key=lambda item: item.group_order)
    rows = sorted(snapshot.rows, key=lambda item: item.row_order)
    group_index = {group.confirmed_group_id: idx for idx, group in enumerate(groups)}
    row_index = {row.confirmed_row_id: idx for idx, row in enumerate(rows)}
    cell_map: dict[tuple[int, int], str] = {}
    for cell in snapshot.cells:
        r_index = row_index.get(cell.confirmed_row_id)
        g_index = group_index.get(cell.confirmed_group_id)
        if r_index is None or g_index is None:
            continue
        value = (cell.cell_value or "").strip()
        if not value:
            continue
        cell_map[(r_index, g_index)] = value
    payload = {
        "groups": [
            {
                "group_order": group.group_order,
                "group_key": group.group_key.strip(),
                "group_label": _normalize_group_label(
                    group.group_label, fallback=str(group.group_order)
                ),
                "sample_quantity_expression": (group.sample_quantity_expression or "").strip(),
                "sample_note": (group.sample_note or "").strip(),
                "is_selected": True,
            }
            for group in groups
        ],
        "rows": [
            {
                "row_order": row.row_order,
                "test_item": row.test_item.strip(),
                "source_section": (row.source_section or "").strip(),
                "method": (row.method or "").strip(),
                "condition": (row.condition or "").strip(),
                "requirement": (row.requirement or "").strip(),
                "day_expression": (row.day_expression or "").strip(),
                "cells": [
                    cell_map.get((row_idx, group_idx), "")
                    for group_idx, _ in enumerate(groups)
                ],
            }
            for row_idx, row in enumerate(rows)
        ],
        "schedule": _schedule_signature_from_confirmed(snapshot),
    }
    return repr(payload)


def _build_manual_preview_payload(
    command: MatrixEditorSessionConfirmCommand,
) -> dict[str, Any]:
    sorted_groups = sorted(command.groups, key=lambda item: item.group_order)
    sorted_rows = sorted(command.rows, key=lambda item: item.row_order)
    cell_map: dict[tuple[str, str], str] = {}
    for cell in command.cells:
        value = (cell.cell_value or "").strip()
        if not value:
            continue
        cell_map[(cell.draft_row_id, cell.draft_group_id)] = value
    groups: list[dict[str, Any]] = []
    for group in sorted_groups:
        groups.append(
            {
                "group_key": group.group_key,
                "group_label": _normalize_group_label(
                    group.group_label, fallback=str(group.group_order)
                ),
                "source_table_index": 0,
                "extraction_status": "manual",
                "sample_size": None,
                "sample_quantity_expression": group.sample_quantity_expression,
                "sample_note": group.sample_note,
                "steps": [],
            }
        )
    rows: list[dict[str, Any]] = []
    for row in sorted_rows:
        row_tokens: dict[str, str] = {}
        for group in sorted_groups:
            value = cell_map.get((row.draft_row_id, group.draft_group_id), "")
            normalized_label = _normalize_group_label(
                group.group_label, fallback=str(group.group_order)
            )
            row_tokens[normalized_label] = value
            row_tokens[group.group_key] = value
        rows.append(
            {
                "source_row_index": row.row_order,
                "test_item": row.test_item,
                "source_section": row.source_section,
                "group_tokens": row_tokens,
                "is_sample_row": bool(row.is_sample_row),
            }
        )
    return {
        "project_id": command.project_id,
        "source_document_path": command.source_document_path or "manual://matrix-editor",
        "source_document_name": command.source_document_name
        or "Matrix Editor Manual Draft",
        "source_format": command.source_format or "manual",
        "capability_status": "supported",
        "generated_at": _utc_now(),
        "selected_table_index": 0,
        "selected_page_number": 1,
        "selected_page_table_index": 1,
        "candidate_tables": [],
        "preview_pdf_token": None,
        "rows": rows,
        "groups": groups,
        "warnings": [],
        "blockers": [],
    }


def _is_source_lineage_replaced(
    command: MatrixEditorSessionConfirmCommand,
    active: ConfirmedMatrixSnapshot,
) -> bool:
    source_import_id = (command.source_import_id or "").strip()
    source_snapshot_id = (command.source_snapshot_id or "").strip()
    if not source_import_id or not source_snapshot_id:
        return False
    return (
        source_import_id != active.version.source_import_id
        or source_snapshot_id != active.version.source_snapshot_id
    )


def _is_same_source_lineage(
    command: MatrixEditorSessionConfirmCommand,
    active: ConfirmedMatrixSnapshot,
) -> bool:
    source_import_id = (command.source_import_id or "").strip()
    source_snapshot_id = (command.source_snapshot_id or "").strip()
    if not source_import_id or not source_snapshot_id:
        return False
    return (
        source_import_id == active.version.source_import_id
        and source_snapshot_id == active.version.source_snapshot_id
    )


def _build_confirmed_snapshot_from_session_draft(
    *,
    draft: ProjectMatrixDraftSnapshot,
    confirmed_by: str,
    confirmed_revision: int,
    source_import_id: str,
    source_snapshot_id: str,
) -> ConfirmedMatrixSnapshot:
    confirmed_matrix_id = f"cmv-{uuid4().hex}"
    confirmed_at = _utc_now()
    selected_groups = tuple(group for group in draft.groups if bool(group.is_selected))
    if not selected_groups:
        raise MatrixEditorSessionError(
            "At least one selected group is required for confirmation."
        )
    version = ConfirmedMatrixVersion(
        confirmed_matrix_id=confirmed_matrix_id,
        project_id=draft.record.project_id,
        project_matrix_draft_id=draft.record.project_matrix_draft_id,
        source_import_id=source_import_id,
        source_snapshot_id=source_snapshot_id,
        confirmed_revision=confirmed_revision,
        is_active_authority=True,
        status=ConfirmedMatrixStatus.CONFIRMED,
        confirmed_by=confirmed_by,
        confirmed_at=confirmed_at,
        pre_test_buffer_days=_normalize_optional_text(draft.record.pre_test_buffer_days),
        post_test_buffer_days=_normalize_optional_text(draft.record.post_test_buffer_days),
        sample_received_date=_normalize_optional_text(draft.record.sample_received_date),
        planned_test_start_date=_normalize_optional_text(draft.record.planned_test_start_date),
        planned_test_complete_date=_normalize_optional_text(
            draft.record.planned_test_complete_date
        ),
        estimated_completion_date=_normalize_optional_text(draft.record.estimated_completion_date),
    )
    sorted_groups = sorted(selected_groups, key=lambda item: item.group_order)
    groups: list[ConfirmedMatrixGroup] = []
    confirmed_group_id_by_draft_group: dict[str, str] = {}
    for index, group in enumerate(sorted_groups, start=1):
        confirmed_group_id = f"cmg-{uuid4().hex}"
        confirmed_group_id_by_draft_group[group.draft_group_id] = confirmed_group_id
        groups.append(
            ConfirmedMatrixGroup(
                confirmed_group_id=confirmed_group_id,
                confirmed_matrix_id=confirmed_matrix_id,
                draft_group_id=group.draft_group_id,
                source_group_snapshot_id=group.source_group_snapshot_id,
                group_order=index,
                group_key=group.group_key.strip(),
                group_label=_normalize_group_label(
                    group.group_label, fallback=str(index)
                ),
                sample_quantity_expression=(group.sample_quantity_expression or "").strip(),
                sample_note=_normalize_optional_text(group.sample_note),
            )
        )
    non_sample_rows = sorted(
        (row for row in draft.rows if not bool(row.is_sample_row)),
        key=lambda item: item.row_order,
    )
    rows: list[ConfirmedMatrixRow] = []
    confirmed_row_id_by_draft_row: dict[str, str] = {}
    for index, row in enumerate(non_sample_rows, start=1):
        confirmed_row_id = f"cmr-{uuid4().hex}"
        confirmed_row_id_by_draft_row[row.draft_row_id] = confirmed_row_id
        rows.append(
            ConfirmedMatrixRow(
                confirmed_row_id=confirmed_row_id,
                confirmed_matrix_id=confirmed_matrix_id,
                draft_row_id=row.draft_row_id,
                source_row_snapshot_id=row.source_row_snapshot_id,
                row_order=index,
                test_item=row.test_item,
                source_section=_normalize_optional_text(row.source_section),
                method=_normalize_optional_text(row.method),
                condition=_normalize_optional_text(row.condition),
                requirement=_normalize_optional_text(row.requirement),
                day_expression=_normalize_optional_text(row.day_expression),
            )
        )
    cells: list[ConfirmedMatrixCell] = []
    seen_identity: set[tuple[str, str]] = set()
    for cell in draft.cells:
        confirmed_group_id = confirmed_group_id_by_draft_group.get(cell.draft_group_id)
        confirmed_row_id = confirmed_row_id_by_draft_row.get(cell.draft_row_id)
        if confirmed_group_id is None or confirmed_row_id is None:
            continue
        cell_value = cell.cell_value.strip()
        if not cell_value:
            continue
        identity = (confirmed_row_id, confirmed_group_id)
        if identity in seen_identity:
            continue
        seen_identity.add(identity)
        cells.append(
            ConfirmedMatrixCell(
                confirmed_cell_id=f"cmc-{uuid4().hex}",
                confirmed_matrix_id=confirmed_matrix_id,
                confirmed_row_id=confirmed_row_id,
                confirmed_group_id=confirmed_group_id,
                draft_row_id=cell.draft_row_id,
                draft_group_id=cell.draft_group_id,
                cell_value=cell_value,
            )
        )
    return ConfirmedMatrixSnapshot(
        version=version,
        groups=tuple(groups),
        rows=tuple(rows),
        cells=tuple(cells),
    )


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _normalize_group_label(value: str | None, *, fallback: str) -> str:
    text = (value or "").strip()
    if not text:
        return fallback
    normalized = text
    if len(text) >= 5 and text[:5].lower() == "group":
        normalized = text[5:].lstrip(" _-")
    normalized = normalized.strip()
    return normalized or fallback


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
