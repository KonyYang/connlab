"""Typed request and response DTOs for Project Matrix drafts."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel


class ProjectMatrixDraftCreateRequest(BaseModel):
    source_import_id: str
    selected_group_keys: list[str] | None = None


class ProjectMatrixDraftRecordResponse(BaseModel):
    project_matrix_draft_id: str
    project_id: str
    source_import_id: str | None
    source_snapshot_id: str
    base_confirmed_matrix_id: str | None
    status: str
    created_at: str
    updated_at: str
    pre_test_buffer_days: str | None = None
    post_test_buffer_days: str | None = None
    sample_received_date: str | None = None
    planned_test_start_date: str | None = None
    planned_test_complete_date: str | None = None
    estimated_completion_date: str | None = None


class ProjectMatrixDraftGroupResponse(BaseModel):
    draft_group_id: str
    source_group_snapshot_id: str | None
    group_order: int
    group_key: str
    group_label: str
    is_selected: bool
    sample_quantity_expression: str | None
    sample_note: str | None


class ProjectMatrixDraftRowResponse(BaseModel):
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


class ProjectMatrixDraftCellResponse(BaseModel):
    draft_cell_id: str
    draft_row_id: str
    draft_group_id: str
    cell_value: str


class MatrixDurationAuthorityResponse(BaseModel):
    duration_authority_id: str
    group_id: str
    row_id: str
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
    diagnostic_code: str | None
    diagnostic_message: str | None


class ProjectMatrixDraftResponse(BaseModel):
    record: ProjectMatrixDraftRecordResponse
    groups: list[ProjectMatrixDraftGroupResponse]
    rows: list[ProjectMatrixDraftRowResponse]
    cells: list[ProjectMatrixDraftCellResponse]
    duration_authorities: list[MatrixDurationAuthorityResponse]


class ProjectMatrixDraftSummaryResponse(ProjectMatrixDraftRecordResponse):
    pass


class ProjectMatrixDraftGroupSaveRequest(BaseModel):
    draft_group_id: str | None = None
    source_group_snapshot_id: str | None = None
    group_order: int
    group_key: str
    group_label: str
    is_selected: bool
    sample_quantity_expression: str | None = None
    sample_note: str | None = None


class ProjectMatrixDraftRowSaveRequest(BaseModel):
    draft_row_id: str | None = None
    source_row_snapshot_id: str | None = None
    row_order: int
    test_item: str
    source_section: str | None = None
    method: str | None = None
    condition: str | None = None
    requirement: str | None = None
    day_expression: str | None = None
    is_sample_row: bool = False


class ProjectMatrixDraftCellSaveRequest(BaseModel):
    draft_row_id: str
    draft_group_id: str
    cell_value: str


class ProjectMatrixDurationAuthoritySaveRequest(BaseModel):
    draft_duration_authority_id: str | None = None
    draft_group_id: str
    draft_row_id: str
    step_sequence: int
    step_suffix_note: str | None = None
    duration_value: Decimal
    duration_unit: str
    source_kind: str
    source_field: str
    source_import_id: str | None = None
    source_fingerprint: str
    lineage_fingerprint: str
    authority_revision: str


class ProjectMatrixDraftSaveRequest(BaseModel):
    groups: list[ProjectMatrixDraftGroupSaveRequest]
    rows: list[ProjectMatrixDraftRowSaveRequest]
    cells: list[ProjectMatrixDraftCellSaveRequest]
    pre_test_buffer_days: str | None = None
    post_test_buffer_days: str | None = None
    sample_received_date: str | None = None
    planned_test_start_date: str | None = None
    planned_test_complete_date: str | None = None
    estimated_completion_date: str | None = None
    duration_authorities: list[ProjectMatrixDurationAuthoritySaveRequest] | None = None


class ConfirmProjectMatrixDraftRequest(BaseModel):
    confirmed_by: str


class ConfirmMatrixRevisionDraftRequest(BaseModel):
    confirmed_by: str
    superseded_reason: str | None = None


class ConfirmedMatrixVersionResponse(BaseModel):
    confirmed_matrix_id: str
    project_id: str
    project_matrix_draft_id: str
    source_import_id: str
    source_snapshot_id: str
    confirmed_revision: int
    is_active_authority: bool
    status: str
    confirmed_by: str
    confirmed_at: str
    superseded_by_confirmed_matrix_id: str | None
    superseded_at: str | None
    superseded_reason: str | None
    pre_test_buffer_days: str | None = None
    post_test_buffer_days: str | None = None
    sample_received_date: str | None = None
    planned_test_start_date: str | None = None
    planned_test_complete_date: str | None = None
    estimated_completion_date: str | None = None


class ConfirmedMatrixGroupResponse(BaseModel):
    confirmed_group_id: str
    draft_group_id: str
    source_group_snapshot_id: str | None
    group_order: int
    group_key: str
    group_label: str
    sample_quantity_expression: str
    sample_note: str | None


class ConfirmedMatrixRowResponse(BaseModel):
    confirmed_row_id: str
    draft_row_id: str
    source_row_snapshot_id: str | None
    row_order: int
    test_item: str
    source_section: str | None
    method: str | None
    condition: str | None
    requirement: str | None
    day_expression: str | None


class ConfirmedMatrixCellResponse(BaseModel):
    confirmed_cell_id: str
    confirmed_row_id: str
    confirmed_group_id: str
    draft_row_id: str
    draft_group_id: str
    cell_value: str


class ConfirmedMatrixSnapshotResponse(BaseModel):
    version: ConfirmedMatrixVersionResponse
    groups: list[ConfirmedMatrixGroupResponse]
    rows: list[ConfirmedMatrixRowResponse]
    cells: list[ConfirmedMatrixCellResponse]
    duration_authorities: list[MatrixDurationAuthorityResponse]
