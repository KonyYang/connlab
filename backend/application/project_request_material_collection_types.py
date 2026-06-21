"""Types for request-material collection workflows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence

from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.domain import FileAsset, Project


class ProjectRequestMaterialCollectionError(ValueError):
    """Base error for request-material collection workflows."""


class ProjectRequestMaterialCollectionNotFoundError(LookupError):
    """Raised when a project required for collection cannot be found."""


class ProjectRequestMaterialCollectionConflictError(ProjectRequestMaterialCollectionError):
    """Raised when request material cannot be safely copied."""


class ProjectRequestMaterialCollectionCopyFailureError(ProjectRequestMaterialCollectionError):
    """Raised when final placement fails after one or more files may have copied."""

    def __init__(
        self,
        message: str,
        *,
        copied_paths: tuple[Path, ...] = tuple(),
        failed_path: Path | None = None,
    ) -> None:
        super().__init__(message)
        self.copied_paths = copied_paths
        self.failed_path = failed_path


class ProjectRepositoryPort(Protocol):
    """Project lookup required for request-material collection."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by id."""


class OfficialWorkspaceRepositoryPort(Protocol):
    """Official project folder lookup required by request-material collection."""

    def get_by_project(self, project_id: str) -> OfficialWorkspaceRecord | None:
        """Return a completed local official workspace record."""


class FileAssetRepositoryPort(Protocol):
    """Project file-asset lookup required by request-material collection."""

    def list_by_project(self, project_id: str) -> list[FileAsset]:
        """Return file assets for a project."""


class RequestMaterialCollectionRepositoryPort(Protocol):
    """Persistence operations for request-material collection records."""

    def save_collection(
        self,
        collection: "ProjectRequestMaterialCollectionRecord",
        items: tuple["ProjectRequestMaterialCollectionItemRecord", ...],
    ) -> "ProjectRequestMaterialCollectionRecord":
        """Persist a collection run and item rows."""

    def latest_by_project(
        self,
        project_id: str,
    ) -> "ProjectRequestMaterialCollectionRecord | None":
        """Return the latest collection record for a project."""

    def list_items(
        self,
        collection_id: str,
    ) -> tuple["ProjectRequestMaterialCollectionItemRecord", ...]:
        """Return persisted items for one collection run."""


class RequestMaterialCopyGatewayPort(Protocol):
    """File-copy operations used by the collection service."""

    def copy_items(
        self,
        *,
        items: Sequence["RequestMaterialPreviewItem"],
        staging_root: Path,
    ) -> tuple[Path, ...]:
        """Copy planned request-material items and return final target paths."""


@dataclass(frozen=True, slots=True)
class RequestMaterialPreviewItem:
    """One planned request-material target."""

    source_asset_id: str
    source_asset_type: str
    source_role: str | None
    source_name: str
    source_path: Path
    dedupe_key: str
    target_area: str
    target_path: Path
    action: str
    status: str
    message: str
    review_required: bool = False
    size_bytes: int | None = None
    sha256: str | None = None


@dataclass(frozen=True, slots=True)
class RequestMaterialPreview:
    """Preview of request-material collection for a project."""

    project_id: str
    local_workspace_path: Path | None
    source_book_path: Path | None
    official_project_folder_path: Path | None
    status: str
    items: tuple[RequestMaterialPreviewItem, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RequestMaterialCollectResult:
    """Result of collecting request material into the Project Folder."""

    project_id: str
    local_workspace_path: Path | None
    source_book_path: Path | None
    official_project_folder_path: Path | None
    collection_id: str
    status: str
    items: tuple[RequestMaterialPreviewItem, ...]
    copied_paths: tuple[Path, ...]
    already_present_paths: tuple[Path, ...]
    skipped_paths: tuple[Path, ...]
    missing_source_paths: tuple[Path, ...]
    conflict_paths: tuple[Path, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ProjectRequestMaterialCollectionRecord:
    """Persisted summary for one request-material collection run."""

    collection_id: str
    project_id: str
    workspace_id: str | None
    status: str
    item_count: int
    copied_count: int
    already_present_count: int
    conflict_count: int
    skipped_count: int
    missing_source_count: int
    created_at: str
    updated_at: str
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ProjectRequestMaterialCollectionItemRecord:
    """Persisted item for one request-material target."""

    item_id: str
    collection_id: str
    project_id: str
    source_asset_id: str
    source_asset_type: str
    source_role: str | None
    dedupe_key: str
    source_path: Path
    original_name: str | None
    target_area: str
    target_path: Path
    status: str
    action: str
    review_required: bool
    size_bytes: int | None
    sha256: str | None


@dataclass(frozen=True, slots=True)
class SourceCandidate:
    """Deduplicated request-material source candidate."""

    asset: FileAsset
    dedupe_key: str
    role: str | None
    name: str
    path: Path
    source_exists: bool
    size_bytes: int | None
    sha256: str | None


@dataclass(frozen=True, slots=True)
class PlannedTarget:
    """One planned target path for a request-material source candidate."""

    candidate: SourceCandidate
    target_area: str
    target_path: Path
    review_required: bool
    message: str
