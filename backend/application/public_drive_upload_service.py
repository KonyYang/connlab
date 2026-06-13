"""Application service for preview-first public-drive Project Folder upload."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from backend.application.official_project_folder_check_service import (
    OfficialFolderCheckPreview,
)
from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.domain import Project


class PublicDriveUploadError(ValueError):
    """Base error for public-drive upload workflows."""


class PublicDriveUploadNotFoundError(LookupError):
    """Raised when a public-drive upload project cannot be found."""


class PublicDriveUploadBlockedError(PublicDriveUploadError):
    """Raised when public-drive upload prerequisites are missing."""


class PublicDriveUploadConflictError(PublicDriveUploadError):
    """Raised when public-drive upload would overwrite unsafe targets."""


class PublicDriveUploadTargetChangedError(PublicDriveUploadError):
    """Raised when a public-drive target changes between preview and write."""


class ProjectRepositoryPort(Protocol):
    """Project lookup operations required by public-drive upload."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by id."""


class OfficialWorkspaceRepositoryPort(Protocol):
    """Local official workspace lookup operations."""

    def get_by_project(self, project_id: str) -> OfficialWorkspaceRecord | None:
        """Return the local official workspace for a project."""


class OfficialFolderCheckPreviewerPort(Protocol):
    """Read-only local Project Folder check dependency."""

    def preview(self, project_id: str) -> OfficialFolderCheckPreview:
        """Return the TASK_318 Official project folder check preview."""


class PublicDriveUploadRepositoryPort(Protocol):
    """Persistence operations for uploaded public-drive files."""

    def get_file(
        self,
        project_id: str,
        relative_path: Path,
    ) -> "PublicDriveUploadFileRecord | None":
        """Return the previous upload record for a file."""

    def save_file(
        self,
        record: "PublicDriveUploadFileRecord",
    ) -> "PublicDriveUploadFileRecord":
        """Create or update one upload record."""


class PublicDriveUploadGatewayPort(Protocol):
    """Filesystem operations for safe public-drive upload."""

    def fingerprint(self, path: Path) -> str:
        """Return a content fingerprint for a file."""

    def list_files(self, root: Path) -> tuple[Path, ...]:
        """Return all local files under a root."""

    def list_directories(self, root: Path) -> tuple[Path, ...]:
        """Return all local directories under a root, excluding the root itself."""

    def create_directory(self, target: Path) -> None:
        """Create a target directory."""

    def copy_new_file(self, source: Path, target: Path) -> None:
        """Copy a file when the public target does not already exist."""

    def replace_managed_file(
        self,
        source: Path,
        target: Path,
        *,
        expected_public_fingerprint: str | None,
    ) -> None:
        """Replace a managed public file after verifying its current fingerprint."""


@dataclass(frozen=True, slots=True)
class PublicDriveUploadFileRecord:
    """Persisted state for one ConnLab-managed public-drive file."""

    project_id: str
    relative_path: Path
    public_path: Path
    local_fingerprint: str
    public_fingerprint: str
    uploaded_at: str
    operation_id: str


@dataclass(frozen=True, slots=True)
class PublicDriveUploadItem:
    """One file or directory considered for public-drive upload."""

    kind: str
    relative_path: Path
    local_path: Path | None
    public_path: Path
    action: str
    status: str
    message: str


@dataclass(frozen=True, slots=True)
class PublicDriveUploadPreview:
    """Read-only public-drive upload preview."""

    project_id: str
    status: str
    local_official_folder_path: Path | None
    public_project_folder_path: Path | None
    items: tuple[PublicDriveUploadItem, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    counts: dict[str, int]
    next_action: str


@dataclass(frozen=True, slots=True)
class PublicDriveUploadResult:
    """Result of one explicit public-drive upload attempt."""

    project_id: str
    upload_status: str
    copied: tuple[PublicDriveUploadItem, ...]
    updated: tuple[PublicDriveUploadItem, ...]
    skipped: tuple[PublicDriveUploadItem, ...]
    conflicts: tuple[PublicDriveUploadItem, ...]
    failed: tuple[PublicDriveUploadItem, ...]
    errors: tuple[str, ...]
    preview: PublicDriveUploadPreview


class PublicDriveUploadService:
    """Preview and execute safe public-drive Project Folder uploads."""

    def __init__(
        self,
        *,
        project_repository: ProjectRepositoryPort,
        workspace_repository: OfficialWorkspaceRepositoryPort,
        public_drive_root: Path | None,
        folder_check_service: OfficialFolderCheckPreviewerPort,
        upload_repository: PublicDriveUploadRepositoryPort,
        gateway: PublicDriveUploadGatewayPort | None = None,
    ) -> None:
        """Create the public-drive upload service."""
        self._projects = project_repository
        self._workspaces = workspace_repository
        self._public_drive_root = public_drive_root
        self._folder_check_service = folder_check_service
        self._upload_repository = upload_repository
        if gateway is None:
            from backend.infrastructure.files.public_drive_upload_gateway import (
                PublicDriveUploadGateway,
            )

            gateway = PublicDriveUploadGateway()
        self._gateway = gateway

    def preview(self, project_id: str) -> PublicDriveUploadPreview:
        """Return a conservative upload preview without writing files."""
        self._require_project(project_id)
        workspace = self._workspaces.get_by_project(project_id)
        if workspace is None or not workspace.official_folder_path.is_dir():
            return _blocked(project_id, "Create local project folder before public-drive upload.")
        if self._public_drive_root is None or not self._public_drive_root.is_dir():
            return _blocked(
                project_id,
                "Public Project locations is not configured.",
                local_path=workspace.official_folder_path,
            )
        folder_check = self._folder_check_service.preview(project_id)
        blockers = _folder_check_blockers(folder_check)
        if blockers:
            return _blocked(
                project_id,
                *blockers,
                local_path=workspace.official_folder_path,
                public_path=self._public_project_folder(workspace),
            )
        return self._build_preview(project_id, workspace, folder_check)

    def upload(self, project_id: str) -> PublicDriveUploadResult:
        """Execute add/update items from a fresh preview."""
        preview = self.preview(project_id)
        if preview.status == "blocked":
            detail = preview.blockers[0] if preview.blockers else "Public-drive upload is blocked."
            raise PublicDriveUploadBlockedError(detail)
        if preview.status == "conflict":
            raise PublicDriveUploadConflictError("Resolve public-drive conflicts before upload.")

        operation_id = uuid4().hex
        copied: list[PublicDriveUploadItem] = []
        updated: list[PublicDriveUploadItem] = []
        skipped = [item for item in preview.items if item.action == "skip"]
        failed: list[PublicDriveUploadItem] = []
        errors: list[str] = []
        for item in preview.items:
            if item.kind == "directory" and item.action == "add":
                try:
                    self._gateway.create_directory(item.public_path)
                except OSError as exc:
                    failed.append(_failed_item(item, str(exc)))
                    errors.append(str(exc))
                    return self._partial_result(project_id, copied, updated, skipped, failed, errors)
                copied.append(item)
                continue
            if item.kind != "file" or item.action not in {"add", "update"}:
                continue
            assert item.local_path is not None
            try:
                if item.action == "add":
                    self._gateway.copy_new_file(item.local_path, item.public_path)
                else:
                    previous = self._upload_repository.get_file(project_id, item.relative_path)
                    self._gateway.replace_managed_file(
                        item.local_path,
                        item.public_path,
                        expected_public_fingerprint=(
                            previous.public_fingerprint if previous else None
                        ),
                    )
            except (OSError, PublicDriveUploadTargetChangedError) as exc:
                failed.append(_failed_item(item, str(exc)))
                errors.append(str(exc))
                return self._partial_result(project_id, copied, updated, skipped, failed, errors)
            record = self._uploaded_record(project_id, item, operation_id)
            self._upload_repository.save_file(record)
            if item.action == "add":
                copied.append(item)
            else:
                updated.append(item)

        after = self.preview(project_id)
        return PublicDriveUploadResult(
            project_id=project_id,
            upload_status="completed",
            copied=tuple(copied),
            updated=tuple(updated),
            skipped=tuple(skipped),
            conflicts=tuple(),
            failed=tuple(),
            errors=tuple(),
            preview=after,
        )

    def _build_preview(
        self,
        project_id: str,
        workspace: OfficialWorkspaceRecord,
        folder_check: OfficialFolderCheckPreview,
    ) -> PublicDriveUploadPreview:
        public_folder = self._public_project_folder(workspace)
        items: list[PublicDriveUploadItem] = []
        warnings = list(folder_check.warnings)
        local_directories = self._gateway.list_directories(workspace.official_folder_path)
        local_files = self._gateway.list_files(workspace.official_folder_path)
        planned_relatives = {
            path.relative_to(workspace.official_folder_path) for path in local_directories
        } | {path.relative_to(workspace.official_folder_path) for path in local_files}

        for local_directory in local_directories:
            relative = local_directory.relative_to(workspace.official_folder_path)
            public_path = public_folder / relative
            items.append(self._directory_item(relative, public_path))
        for local_path in local_files:
            relative = local_path.relative_to(workspace.official_folder_path)
            public_path = public_folder / relative
            items.append(self._file_item(project_id, relative, local_path, public_path))

        extra_public_files = _extra_public_files(public_folder, planned_relatives)
        if extra_public_files:
            warnings.append("Public project folder contains extra unmanaged files.")

        return _preview(
            project_id=project_id,
            local_path=workspace.official_folder_path,
            public_path=public_folder,
            items=tuple(sorted(items, key=lambda item: (str(item.relative_path), item.kind))),
            blockers=tuple(),
            warnings=tuple(dict.fromkeys(warnings)),
        )

    def _directory_item(self, relative: Path, public_path: Path) -> PublicDriveUploadItem:
        if not public_path.exists():
            return PublicDriveUploadItem(
                kind="directory",
                relative_path=relative,
                local_path=None,
                public_path=public_path,
                action="add",
                status="ready",
                message="Directory will be created.",
            )
        if public_path.is_dir():
            return PublicDriveUploadItem(
                kind="directory",
                relative_path=relative,
                local_path=None,
                public_path=public_path,
                action="skip",
                status="current",
                message="Directory already exists.",
            )
        return PublicDriveUploadItem(
            kind="directory",
            relative_path=relative,
            local_path=None,
            public_path=public_path,
            action="conflict",
            status="conflict",
            message="Public-drive path is a file, expected directory.",
        )

    def _file_item(
        self,
        project_id: str,
        relative: Path,
        local_path: Path,
        public_path: Path,
    ) -> PublicDriveUploadItem:
        local_fingerprint = self._gateway.fingerprint(local_path)
        previous = self._upload_repository.get_file(project_id, relative)
        if not public_path.exists():
            return PublicDriveUploadItem(
                kind="file",
                relative_path=relative,
                local_path=local_path,
                public_path=public_path,
                action="add",
                status="ready",
                message="Will be added.",
            )
        if not public_path.is_file():
            return PublicDriveUploadItem(
                kind="file",
                relative_path=relative,
                local_path=local_path,
                public_path=public_path,
                action="conflict",
                status="conflict",
                message="Public-drive path is not a file.",
            )
        public_fingerprint = self._gateway.fingerprint(public_path)
        if public_fingerprint == local_fingerprint:
            return PublicDriveUploadItem(
                kind="file",
                relative_path=relative,
                local_path=local_path,
                public_path=public_path,
                action="skip",
                status="current",
                message="Already current.",
            )
        if previous is None:
            return PublicDriveUploadItem(
                kind="file",
                relative_path=relative,
                local_path=local_path,
                public_path=public_path,
                action="conflict",
                status="conflict",
                message="Public-drive file is not managed by ConnLab.",
            )
        if public_fingerprint != previous.public_fingerprint:
            return PublicDriveUploadItem(
                kind="file",
                relative_path=relative,
                local_path=local_path,
                public_path=public_path,
                action="conflict",
                status="conflict",
                message="Public-drive file was changed outside ConnLab.",
            )
        return PublicDriveUploadItem(
            kind="file",
            relative_path=relative,
            local_path=local_path,
            public_path=public_path,
            action="update",
            status="ready",
            message="Will be updated.",
        )

    def _public_project_folder(self, workspace: OfficialWorkspaceRecord) -> Path:
        assert self._public_drive_root is not None
        return self._public_drive_root / workspace.dl_number / workspace.official_folder_path.name

    def _require_project(self, project_id: str) -> Project:
        project = self._projects.get(project_id)
        if project is None:
            raise PublicDriveUploadNotFoundError(f"Project not found: {project_id}")
        return project

    def _uploaded_record(
        self,
        project_id: str,
        item: PublicDriveUploadItem,
        operation_id: str,
    ) -> PublicDriveUploadFileRecord:
        assert item.local_path is not None
        return PublicDriveUploadFileRecord(
            project_id=project_id,
            relative_path=item.relative_path,
            public_path=item.public_path,
            local_fingerprint=self._gateway.fingerprint(item.local_path),
            public_fingerprint=self._gateway.fingerprint(item.public_path),
            uploaded_at=datetime.now(UTC).isoformat(),
            operation_id=operation_id,
        )

    def _partial_result(
        self,
        project_id: str,
        copied: list[PublicDriveUploadItem],
        updated: list[PublicDriveUploadItem],
        skipped: list[PublicDriveUploadItem],
        failed: list[PublicDriveUploadItem],
        errors: list[str],
    ) -> PublicDriveUploadResult:
        after = self.preview(project_id)
        return PublicDriveUploadResult(
            project_id=project_id,
            upload_status="partial",
            copied=tuple(copied),
            updated=tuple(updated),
            skipped=tuple(skipped),
            conflicts=tuple(item for item in after.items if item.action == "conflict"),
            failed=tuple(failed),
            errors=tuple(errors),
            preview=after,
        )


def _folder_check_blockers(preview: OfficialFolderCheckPreview) -> tuple[str, ...]:
    """Return public-drive blockers derived from TASK_318 check status."""
    if preview.status in {"blocked", "conflict"}:
        return preview.blockers or ("Project Folder check must be resolved before upload.",)
    if preview.status == "missing":
        return ("Complete required Project Folder items before public-drive upload.",)
    return tuple()


def _extra_public_files(public_folder: Path, planned_relatives: set[Path]) -> tuple[Path, ...]:
    """Return unmanaged public files that do not collide with planned local items."""
    if not public_folder.is_dir():
        return tuple()
    extra: list[Path] = []
    for path in public_folder.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(public_folder)
        if relative not in planned_relatives:
            extra.append(relative)
    return tuple(extra)


def _preview(
    *,
    project_id: str,
    local_path: Path | None,
    public_path: Path | None,
    items: tuple[PublicDriveUploadItem, ...],
    blockers: tuple[str, ...],
    warnings: tuple[str, ...],
) -> PublicDriveUploadPreview:
    counts = _counts(items)
    if blockers:
        status = "blocked"
        next_action = "none"
    elif counts["conflict"]:
        status = "conflict"
        next_action = "none"
    elif warnings and (counts["add"] or counts["update"]):
        status = "warning"
        next_action = "upload"
    elif warnings:
        status = "warning"
        next_action = "none"
    elif counts["add"] or counts["update"]:
        status = "ready"
        next_action = "upload"
    else:
        status = "current"
        next_action = "none"
    return PublicDriveUploadPreview(
        project_id=project_id,
        status=status,
        local_official_folder_path=local_path,
        public_project_folder_path=public_path,
        items=items,
        blockers=blockers,
        warnings=warnings,
        counts=counts,
        next_action=next_action,
    )


def _blocked(
    project_id: str,
    *blockers: str,
    local_path: Path | None = None,
    public_path: Path | None = None,
) -> PublicDriveUploadPreview:
    """Return a blocked preview."""
    return PublicDriveUploadPreview(
        project_id=project_id,
        status="blocked",
        local_official_folder_path=local_path,
        public_project_folder_path=public_path,
        items=tuple(),
        blockers=tuple(blockers),
        warnings=tuple(),
        counts=_counts(tuple()),
        next_action="none",
    )


def _counts(items: tuple[PublicDriveUploadItem, ...]) -> dict[str, int]:
    """Return preview item action counts."""
    counts = {key: 0 for key in ("add", "update", "skip", "conflict", "deferred")}
    for item in items:
        counts[item.action] = counts.get(item.action, 0) + 1
    return counts


def _failed_item(item: PublicDriveUploadItem, message: str) -> PublicDriveUploadItem:
    """Return a failed version of one upload item."""
    return PublicDriveUploadItem(
        kind=item.kind,
        relative_path=item.relative_path,
        local_path=item.local_path,
        public_path=item.public_path,
        action=item.action,
        status="failed",
        message=message,
    )
