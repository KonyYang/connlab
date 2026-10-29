"""Public DTOs for explicit project-library preview and confirmation."""
from typing import Literal
from pydantic import BaseModel, Field


class RuntimeResponse(BaseModel):
    library_root: str
    projects_root: str
    data_root: str
    database_path: str
    configured: bool
    format_version: int = 1
    destination_editable: bool = True
    location_error: str | None = None


class MemberResponse(BaseModel):
    member_id: str
    project_id: str | None
    ltr_number: str | None
    title: str
    folder_path: str
    revision: int
    batch_id: str | None
    snapshot_status: Literal["not_checked", "missing", "current", "stale", "unavailable"]
    snapshot_created_at: str | None
    warnings: list[str]
    can_continue: bool
    is_history: bool = False


class MembersResponse(BaseModel):
    items: list[MemberResponse]


class RootsRequest(BaseModel):
    roots: list[str] = Field(min_length=1, max_length=1000)


class CandidateResponse(BaseModel):
    source_path: str
    title: str
    ltr_number: str | None
    kind: Literal["project", "file"]
    warnings: list[str]
    child_folders: list[str]
    has_portable: bool = False


class ScanResponse(BaseModel):
    items: list[CandidateResponse]
    boundary_roots: list[CandidateResponse]
    warnings: list[str]
    truncated: bool


class IntakeAssignment(BaseModel):
    source_path: str
    target_member_id: str | None = None
    new_project_title: str | None = None


class IntakeRequest(BaseModel):
    sources: list[str] = Field(min_length=1, max_length=1000)
    assignments: list[IntakeAssignment] = Field(default_factory=list, max_length=1000)


class IntakeItemResponse(BaseModel):
    source_path: str
    target_path: str
    title: str
    ltr_number: str | None
    status: Literal["ready", "conflict", "already_added", "unavailable"]
    warnings: list[str]
    can_keep_separate: bool
    target_member_id: str | None = None
    existing_member_id: str | None = None
    new_project_title: str | None = None


class IntakePlanResponse(BaseModel):
    plan_id: str
    fingerprint: str
    items: list[IntakeItemResponse]
    warnings: list[str]
    projects_root: str | None = None


class ConfirmRequest(BaseModel):
    plan_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")


class BatchRequest(ConfirmRequest):
    batch_id: str | None = Field(default=None, pattern=r"^[a-f0-9]{32}$")
    selected: list[str] = Field(min_length=1, max_length=1000)
    keep_separate: list[str] = Field(default_factory=list, max_length=1000)


class BatchItemResponse(BaseModel):
    source_path: str
    status: str
    message: str
    member_id: str | None


class BatchResponse(BaseModel):
    batch_id: str
    status: Literal["completed", "interrupted", "running"]
    counts: dict[str, int]
    items: list[BatchItemResponse]


class FileResponse(BaseModel):
    name: str
    relative_path: str
    is_directory: bool
    size_bytes: int | None


class FilesResponse(BaseModel):
    items: list[FileResponse]
    warnings: list[str]


class TitleRequest(BaseModel):
    title: str = Field(min_length=1, max_length=240)


class FolderRequest(BaseModel):
    folder: str = Field(min_length=1, max_length=4096)


class ChangePlanResponse(ConfirmRequest):
    source_path: str
    target_path: str
    warnings: list[str]


class FingerprintRequest(BaseModel):
    fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")


class PortableInfoResponse(BaseModel):
    status: Literal["missing", "current", "stale", "unavailable"]
    fingerprint: str
    created_at: str | None
    format_version: int = 1
    record_counts: dict[str, int]
    file_count: int
    warnings: list[str]
    blockers: list[str]


class RestoreFolderRequest(FolderRequest):
    resolution: Literal["replace_working_copy", "keep_as_history"] | None = None


class RestoreConfirmRequest(ConfirmRequest):
    resolution: Literal["replace_working_copy", "keep_as_history"] | None = None


class RestorePlanResponse(ConfirmRequest):
    projects_root: str | None = None
    resolution_options: list[str] = Field(default_factory=list)
    resolution: str | None = None
    target_revision: int | None = None
    backup_path: str | None = None
    source_signature: str | None = None
    project_id: str | None
    ltr_number: str | None
    title: str
    source_path: str
    target_path: str
    status: Literal["ready", "already_added", "conflict", "unavailable"]
    created_at: str | None
    record_counts: dict[str, int]
    file_count: int
    warnings: list[str]
    blockers: list[str]


class RestoreResponse(BaseModel):
    status: Literal["restored", "already_added", "history_kept"]
    backup_member_id: str | None = None
    member: MemberResponse
    warnings: list[str]


class TakeoverPlanResponse(ConfirmRequest):
    project_id: str | None
    ltr_number: str | None
    title: str
    status: Literal["ready", "needs_information", "already_managed", "conflict"]
    missing: list[str]
    warnings: list[str]
    blockers: list[str]


class TakeoverResponse(BaseModel):
    member: MemberResponse
    project_id: str
    warnings: list[str]
