"""Typed request and response DTOs for Matrix Editor sessions."""

from __future__ import annotations

from decimal import Decimal
from pydantic import BaseModel, Field

from backend.api.project_matrix_draft_dtos import ConfirmedMatrixSnapshotResponse


class MatrixEditorSessionGroupResponse(BaseModel):
    """Session editor group response model."""

    draft_group_id: str
    source_group_snapshot_id: str | None
    group_order: int
    group_key: str
    group_label: str
    is_selected: bool
    sample_quantity_expression: str | None
    sample_note: str | None


class MatrixEditorSessionRowResponse(BaseModel):
    """Session editor row response model."""

    draft_row_id: str
    source_row_snapshot_id: str | None
    row_order: int
    test_item: str
    source_section: str | None
    method: str | None
    condition: str | None
    requirement: str | None
    day_expression: str | None
    is_sample_row: bool


class MatrixEditorSessionCellResponse(BaseModel):
    """Session editor sparse cell response model."""

    draft_row_id: str
    draft_group_id: str
    cell_value: str


class MatrixEditorSessionDurationAuthorityResponse(BaseModel):
    """Normalized Matrix Editor duration authority response."""

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
    status: str


class MatrixEditorSessionDraftResponse(BaseModel):
    """Session editor snapshot response model."""

    groups: list[MatrixEditorSessionGroupResponse]
    rows: list[MatrixEditorSessionRowResponse]
    cells: list[MatrixEditorSessionCellResponse]
    duration_authorities: list[MatrixEditorSessionDurationAuthorityResponse] = Field(
        default_factory=list
    )


class MatrixEditorSessionSeedResponse(BaseModel):
    """Matrix Editor session seed response model."""

    project_id: str
    active_confirmed_matrix_id: str | None
    active_confirmed_revision: int | None
    active_source_import_id: str | None
    active_source_snapshot_id: str | None
    editor_source_import_id: str | None = None
    editor_source_snapshot_id: str | None = None
    editor_draft: MatrixEditorSessionDraftResponse | None
    source_preview_payload: dict | None
    source_status: str
    source_unavailable_message: str | None
    pre_test_buffer_days: str | None = None
    post_test_buffer_days: str | None = None
    sample_received_date: str | None = None
    planned_test_start_date: str | None = None
    planned_test_complete_date: str | None = None
    estimated_completion_date: str | None = None
    editor_draft_id: str | None = None
    draft_status: str = "missing"
    loaded_source: str = "authority"
    stale_draft_present: bool = False
    draft_updated_at: str | None = None
    saved_payload_signature: str | None = None


class MatrixEditorSessionGroupRequest(BaseModel):
    """Session editor group request model."""

    draft_group_id: str
    source_group_snapshot_id: str | None = None
    group_order: int
    group_key: str
    group_label: str
    is_selected: bool
    sample_quantity_expression: str | None = None
    sample_note: str | None = None


class MatrixEditorSessionRowRequest(BaseModel):
    """Session editor row request model."""

    draft_row_id: str
    source_row_snapshot_id: str | None = None
    row_order: int
    test_item: str
    source_section: str | None = None
    method: str | None = None
    condition: str | None = None
    requirement: str | None = None
    day_expression: str | None = None
    is_sample_row: bool = False


class MatrixEditorSessionCellRequest(BaseModel):
    """Session editor sparse cell request model."""

    draft_row_id: str
    draft_group_id: str
    cell_value: str


class MatrixEditorSessionDurationAuthorityRequest(BaseModel):
    """Full normalized duration authority request."""

    draft_duration_authority_id: str | None = None
    draft_group_id: str
    draft_row_id: str
    step_sequence: int
    step_suffix_note: str = ""
    duration_value: Decimal
    duration_unit: str
    normalized_hours: Decimal
    source_kind: str
    source_field: str
    source_import_id: str | None = None
    source_fingerprint: str
    lineage_fingerprint: str
    authority_revision: str
    status: str = "usable"


class MatrixEditorSessionConfirmRequest(BaseModel):
    """Session confirm request model."""

    expected_active_confirmed_matrix_id: str | None = None
    expected_active_confirmed_revision: int | None = None
    source_document_path: str | None = None
    source_document_name: str | None = None
    source_format: str | None = None
    source_import_id: str | None = None
    source_snapshot_id: str | None = None
    confirmed_by: str
    groups: list[MatrixEditorSessionGroupRequest]
    rows: list[MatrixEditorSessionRowRequest]
    cells: list[MatrixEditorSessionCellRequest]
    duration_authorities: list[MatrixEditorSessionDurationAuthorityRequest] = Field(
        default_factory=list
    )
    pre_test_buffer_days: str | None = None
    post_test_buffer_days: str | None = None
    sample_received_date: str | None = None
    planned_test_start_date: str | None = None
    planned_test_complete_date: str | None = None
    estimated_completion_date: str | None = None
    expected_editor_draft_id: str | None = None
    expected_saved_payload_signature: str | None = None


class MatrixEditorSessionDraftSaveRequest(BaseModel):
    """Session draft autosave request model."""

    expected_active_confirmed_matrix_id: str | None = None
    expected_active_confirmed_revision: int | None = None
    source_document_path: str | None = None
    source_document_name: str | None = None
    source_format: str | None = None
    source_import_id: str | None = None
    source_snapshot_id: str | None = None
    groups: list[MatrixEditorSessionGroupRequest]
    rows: list[MatrixEditorSessionRowRequest]
    cells: list[MatrixEditorSessionCellRequest]
    duration_authorities: list[MatrixEditorSessionDurationAuthorityRequest] = Field(
        default_factory=list
    )
    pre_test_buffer_days: str | None = None
    post_test_buffer_days: str | None = None
    sample_received_date: str | None = None
    planned_test_start_date: str | None = None
    planned_test_complete_date: str | None = None
    estimated_completion_date: str | None = None


class MatrixEditorSessionDraftSaveResponse(BaseModel):
    """Session draft autosave response model."""

    editor_draft_id: str
    draft_status: str
    draft_updated_at: str
    saved_payload_signature: str
    active_confirmed_matrix_id: str
    active_confirmed_revision: int
    fee_rebase_status: str = "not_required"
    fee_rebase_summary: "MatrixFeeRebaseSummaryResponse | None" = None
    fee_rebase_error: str | None = None


class MatrixFeeRebaseSummaryResponse(BaseModel):
    """Pending Matrix-to-Fee rebase summary returned by autosave."""

    preserved_count: int
    added_count: int
    removed_count: int
    preserved_manual_count: int = 0
    removed_manual_count: int = 0


class MatrixEditorSessionDraftDiscardRequest(BaseModel):
    """Session draft discard request model."""

    expected_editor_draft_id: str | None = None
    expected_saved_payload_signature: str | None = None


class MatrixEditorSessionDraftDiscardResponse(BaseModel):
    """Session draft discard response model."""

    discarded: bool
    active_confirmed_matrix_id: str | None
    active_confirmed_revision: int | None


class MatrixEditorSessionConfirmResponse(BaseModel):
    """Session confirm response model."""

    publish_status: str
    message: str
    confirmed_snapshot: ConfirmedMatrixSnapshotResponse | None
    fee_rebase_promotion_status: str = "not_required"
    fee_rebase_promotion_summary: MatrixFeeRebaseSummaryResponse | None = None
    fee_rebase_promotion_error: str | None = None
