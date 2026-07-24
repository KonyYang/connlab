"""Contracts and DTOs for Matrix Editor sessions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
import json
from typing import Any, Callable, Literal, Protocol
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
from backend.application.matrix_step_quantity_authority_builder import (
    build_confirmed_step_quantities,
)
from backend.application.matrix_step_quantity_authority_comparison import (
    step_quantity_authority_matches,
)
from backend.application.matrix_revision_flow_service import (
    CreateMatrixRevisionDraftCommand,
    MatrixRevisionFlowConflictError,
    MatrixRevisionFlowService,
)
from backend.application.matrix_fee_draft_rebase_service import MatrixFeeRebaseSummary
from backend.application.matrix_fee_pending_rebase_service import (
    DeletePendingRebaseForMatrixDraftCommand,
    MatrixFeePendingRebaseResult,
    RebaseAfterMatrixAutosaveCommand,
)
from backend.application.matrix_fee_rebase_promotion_service import (
    MatrixFeeRebasePromotionResult,
    MatrixFeeRebasePromotionStatus,
    PromoteMatrixFeeRebaseCommand,
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
from backend.application.project_lifecycle_write_guard import (
    LifecycleWriteOperation,
    ProjectLifecycleWriteGuard,
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
    ProjectMatrixDraftStatus,
    SourceMatrixImportRecord,
    SourceMatrixSnapshot,
)
from backend.modules.fee_evaluation import load_active_fee_rule_library



SOURCE_UNAVAILABLE_MESSAGE = (
    "Original source Matrix is unavailable. Use Import Matrix to reselect groups."
)


class MatrixEditorSessionError(ValueError):
    """Raised when Matrix Editor session input is invalid."""


class MatrixEditorSessionNotFoundError(LookupError):
    """Raised when required project resources are not found."""


class MatrixEditorSessionActiveChangedError(MatrixEditorSessionError):
    """Raised when active matrix changed while a session was open."""


class MatrixEditorSessionDraftConflictError(MatrixEditorSessionError):
    """Raised when saved editor draft tokens are missing or stale."""


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

    def list_by_project(self, project_id: str) -> tuple[ConfirmedMatrixSnapshot, ...]:
        """Return confirmed authority snapshots by project."""


class SourceStore(Protocol):
    """Source matrix lookup operations required by this service."""

    def get_import(self, import_id: str) -> SourceMatrixImportRecord | None:
        """Return one source import by id."""

    def get_snapshot(self, snapshot_id: str) -> SourceMatrixSnapshot | None:
        """Return one source snapshot by id."""


class DraftStore(Protocol):
    """Draft lookup operations required by this service."""

    def get(self, project_matrix_draft_id: str) -> ProjectMatrixDraftSnapshot | None:
        """Return one draft aggregate by id."""

    def list_by_project(self, project_id: str) -> list[ProjectMatrixDraftRecord]:
        """Return draft records by project."""

    def delete(self, project_matrix_draft_id: str) -> bool:
        """Delete one draft aggregate by id."""

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


class PendingFeeRebaseService(Protocol):
    """Pending Matrix-to-Fee rebase lifecycle hooks used by Matrix Editor."""

    def rebase_after_matrix_autosave(
        self, command: RebaseAfterMatrixAutosaveCommand
    ) -> MatrixFeePendingRebaseResult:
        """Persist pending Fee rebase output after Matrix autosave."""

    def delete_for_matrix_draft(
        self, command: DeletePendingRebaseForMatrixDraftCommand
    ) -> object:
        """Delete pending Fee rebase output for a discarded Matrix draft."""


class FeeRebasePromotionService(Protocol):
    """Matrix Confirm hook for promoting pending Fee rebase output."""

    def initialize_after_first_matrix_confirm(
        self,
        *,
        project_id: str,
        new_confirmed_matrix: ConfirmedMatrixSnapshot,
        fee_rule_version_id: str,
    ) -> MatrixFeeRebasePromotionResult:
        """Create the initial Fee draft/authority after first Matrix Confirm."""

    def promote_after_matrix_confirm(
        self, command: PromoteMatrixFeeRebaseCommand
    ) -> MatrixFeeRebasePromotionResult:
        """Promote pending/fallback Fee rebase output after Matrix Confirm."""


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
class MatrixEditorSessionDurationAuthority:
    """Normalized duration authority carried through Matrix Editor."""

    draft_duration_authority_id: str | None
    draft_group_id: str
    draft_row_id: str
    step_sequence: int
    step_suffix_note: str
    duration_value: Decimal
    duration_unit: str
    normalized_hours: Decimal
    source_kind: str
    source_field: str
    source_import_id: str | None
    source_fingerprint: str
    lineage_fingerprint: str
    authority_revision: str
    status: str = "usable"


@dataclass(frozen=True, slots=True)
class MatrixEditorSessionDraft:
    """Session editor snapshot payload."""

    groups: tuple[MatrixEditorSessionGroup, ...]
    rows: tuple[MatrixEditorSessionRow, ...]
    cells: tuple[MatrixEditorSessionCell, ...]
    duration_authorities: tuple[MatrixEditorSessionDurationAuthority, ...] = ()


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
    editor_draft_id: str | None = None
    draft_status: Literal["missing", "current", "stale"] = "missing"
    loaded_source: Literal["authority", "draft"] = "authority"
    stale_draft_present: bool = False
    draft_updated_at: str | None = None
    saved_payload_signature: str | None = None


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
    duration_authorities: tuple[MatrixEditorSessionDurationAuthority, ...] = ()
    pre_test_buffer_days: str | None = None
    post_test_buffer_days: str | None = None
    sample_received_date: str | None = None
    planned_test_start_date: str | None = None
    planned_test_complete_date: str | None = None
    estimated_completion_date: str | None = None
    expected_editor_draft_id: str | None = None
    expected_saved_payload_signature: str | None = None


@dataclass(frozen=True, slots=True)
class MatrixEditorSessionDraftSaveCommand:
    """Input payload for Matrix Editor background draft autosave."""

    project_id: str
    expected_active_confirmed_matrix_id: str | None
    expected_active_confirmed_revision: int | None
    source_document_path: str | None
    source_document_name: str | None
    source_format: str | None
    source_import_id: str | None
    source_snapshot_id: str | None
    groups: tuple[MatrixEditorSessionGroup, ...]
    rows: tuple[MatrixEditorSessionRow, ...]
    cells: tuple[MatrixEditorSessionCell, ...]
    duration_authorities: tuple[MatrixEditorSessionDurationAuthority, ...] = ()
    pre_test_buffer_days: str | None = None
    post_test_buffer_days: str | None = None
    sample_received_date: str | None = None
    planned_test_start_date: str | None = None
    planned_test_complete_date: str | None = None
    estimated_completion_date: str | None = None


@dataclass(frozen=True, slots=True)
class MatrixEditorSessionDraftSaveResult:
    """Result payload for Matrix Editor background draft autosave."""

    editor_draft_id: str
    draft_status: Literal["current"]
    draft_updated_at: str
    saved_payload_signature: str
    active_confirmed_matrix_id: str
    active_confirmed_revision: int
    fee_rebase_status: Literal["not_required", "current", "failed"] = "not_required"
    fee_rebase_summary: MatrixFeeRebaseSummary | None = None
    fee_rebase_error: str | None = None


@dataclass(frozen=True, slots=True)
class MatrixEditorSessionDraftDiscardCommand:
    """Input payload for Matrix Editor draft discard."""

    project_id: str
    expected_editor_draft_id: str | None = None
    expected_saved_payload_signature: str | None = None


@dataclass(frozen=True, slots=True)
class MatrixEditorSessionDraftDiscardResult:
    """Result payload for Matrix Editor draft discard."""

    discarded: bool
    active_confirmed_matrix_id: str | None
    active_confirmed_revision: int | None


@dataclass(frozen=True, slots=True)
class MatrixEditorSessionConfirmResult:
    """Session confirm response payload."""

    publish_status: Literal["published", "no_change"]
    message: str
    confirmed_snapshot: ConfirmedMatrixSnapshot | None
    fee_rebase_promotion_status: MatrixFeeRebasePromotionStatus = "not_required"
    fee_rebase_promotion_summary: MatrixFeeRebaseSummary | None = None
    fee_rebase_promotion_error: str | None = None
