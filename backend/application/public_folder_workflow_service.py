"""Backend service for preview-first public folder workflow operations."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol
from uuid import uuid4
import hashlib

from backend.application.official_project_folder_check_service import (
    OfficialFolderCheckPreview,
)
from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.application.public_folder_path_resolver import (
    PublicFolderPathError,
    PublicFolderPathResolver,
    PublicFolderPaths,
)
from backend.application.public_folder_year_resolver import (
    PublicFolderYearResolution,
    PublicFolderYearResolver,
)
from backend.domain import Project


class PublicFolderWorkflowError(ValueError):
    """Base error for public folder workflow failures."""


class PublicFolderWorkflowNotFoundError(LookupError):
    """Raised when a project cannot be found."""


class PublicFolderWorkflowBlockedError(PublicFolderWorkflowError):
    """Raised when execute is blocked by business prerequisites."""


class PublicFolderWorkflowConflictError(PublicFolderWorkflowError):
    """Raised when a conflict or stale preview prevents execute."""


class ProjectRepositoryPort(Protocol):
    """Project lookup operations."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by id."""


class OfficialWorkspaceRepositoryPort(Protocol):
    """Official workspace lookup operations."""

    def get_by_project(self, project_id: str) -> OfficialWorkspaceRecord | None:
        """Return the official workspace for a project."""


class FolderCheckPort(Protocol):
    """Read-only Official project folder check operations."""

    def preview(self, project_id: str) -> OfficialFolderCheckPreview:
        """Return the folder check preview."""


class PublicFolderWorkflowGatewayPort(Protocol):
    """Filesystem operations required by the workflow."""

    def fingerprint(self, path: Path) -> str:
        """Return a file fingerprint."""

    def list_files(self, root: Path) -> tuple[Path, ...]:
        """Return all files under a root."""

    def list_directories(self, root: Path) -> tuple[Path, ...]:
        """Return all directories under a root."""

    def create_directory(self, target: Path) -> None:
        """Create a directory."""

    def copy_new_file(self, source: Path, target: Path) -> None:
        """Copy a new file without overwrite."""

    def replace_managed_file(
        self,
        source: Path,
        target: Path,
        *,
        expected_public_fingerprint: str | None,
    ) -> None:
        """Replace a managed file after fingerprint validation."""

    def move_directory_no_overwrite(self, source: Path, target: Path) -> None:
        """Move a directory without overwrite."""

    def copy_tree_no_overwrite(self, source: Path, target: Path) -> None:
        """Copy a directory tree without overwrite."""

    def unique_history_target(self, current_local_folder: Path, timestamp: str) -> Path:
        """Return a unique local pull target."""


class PublicFolderWorkflowRepositoryPort(Protocol):
    """Persistence required by public folder workflow operations."""

    def get_state(self, project_id: str) -> "PublicFolderWorkflowState":
        """Return existing or default state."""

    def save_state(self, state: "PublicFolderWorkflowState") -> "PublicFolderWorkflowState":
        """Persist workflow state."""

    def get_file(
        self,
        project_id: str,
        relative_path: Path,
    ) -> "PublicFolderWorkflowFileRecord | None":
        """Return managed file state."""

    def save_file(
        self,
        record: "PublicFolderWorkflowFileRecord",
    ) -> "PublicFolderWorkflowFileRecord":
        """Create or update managed file state."""

    def rebase_files(
        self,
        *,
        project_id: str,
        old_root: Path,
        new_root: Path,
        operation_id: str,
        updated_at: str,
    ) -> None:
        """Update managed file public paths after Submit move."""

    def save_operation(
        self,
        record: "PublicFolderWorkflowOperationRecord",
    ) -> "PublicFolderWorkflowOperationRecord":
        """Persist an operation audit record."""


@dataclass(frozen=True, slots=True)
class PublicFolderWorkflowState:
    """Per-project workflow state."""

    project_id: str
    auto_sync_enabled: bool = False
    sync_locked: bool = False
    submitted_at: str | None = None
    submit_operation_id: str | None = None
    last_sync_operation_id: str | None = None
    last_pull_operation_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


@dataclass(frozen=True, slots=True)
class PublicFolderWorkflowFileRecord:
    """Managed public workflow file state."""

    project_id: str
    relative_path: Path
    public_path: Path
    local_fingerprint: str
    public_fingerprint: str
    updated_at: str
    operation_id: str


@dataclass(frozen=True, slots=True)
class PublicFolderWorkflowOperationRecord:
    """Operation audit record for Sync, Submit, and Pull."""

    operation_id: str
    project_id: str
    operation_type: str
    status: str
    preview_hash: str
    requested_at: str
    started_at: str
    completed_at: str
    operator: str | None
    public_root: Path | None
    public_root_class: str | None
    public_folder_year: int | None
    year_source: str | None
    local_official_folder_path: Path | None
    public_open_path: Path | None
    public_closed_path: Path | None
    target_path: Path | None
    counts: dict[str, int]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    conflicts: tuple[str, ...]
    snapshot_json: str
    metadata_json: str | None = None


@dataclass(frozen=True, slots=True)
class PublicFolderWorkflowItem:
    """One previewed workflow item."""

    kind: str
    relative_path: Path
    local_path: Path | None
    public_path: Path | None
    action: str
    status: str
    message: str


@dataclass(frozen=True, slots=True)
class PublicFolderWorkflowPreview:
    """Read-only preview of one workflow operation."""

    project_id: str
    operation_type: str
    status: str
    local_official_folder_path: Path | None
    public_root: Path | None
    public_root_class: str | None
    public_folder_year: int | None
    year_source: str | None
    year_evidence: str | None
    public_open_path: Path | None
    public_closed_path: Path | None
    target_path: Path | None
    items: tuple[PublicFolderWorkflowItem, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    conflicts: tuple[str, ...]
    required_confirmations: tuple[str, ...]
    counts: dict[str, int]
    preview_hash: str
    next_action: str
    auto_sync_enabled: bool
    sync_locked: bool


@dataclass(frozen=True, slots=True)
class PublicFolderWorkflowContext:
    """Public folder workflow context for UI wiring."""

    project_id: str
    auto_sync_enabled: bool
    sync_locked: bool
    submitted_at: str | None
    public_root: Path | None
    public_root_class: str | None
    public_folder_year: int | None
    year_source: str | None
    year_evidence: str | None
    local_official_folder_path: Path | None
    public_open_path: Path | None
    public_closed_path: Path | None
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PublicFolderWorkflowExecuteCommand:
    """Execute command carrying explicit operator confirmation."""

    preview_hash: str
    confirmed: bool
    confirm_directory_creation: bool = False
    operator: str | None = None


@dataclass(frozen=True, slots=True)
class PublicFolderAutoSyncCommand:
    """Persisted auto-sync preference command."""

    auto_sync_enabled: bool


@dataclass(frozen=True, slots=True)
class PublicFolderWorkflowResult:
    """Result of one executed workflow operation."""

    project_id: str
    operation_id: str
    operation_type: str
    status: str
    counts: dict[str, int]
    errors: tuple[str, ...]
    preview: PublicFolderWorkflowPreview


class PublicFolderWorkflowService:
    """Preview and execute public folder workflow operations."""

    def __init__(
        self,
        *,
        project_repository: ProjectRepositoryPort,
        workspace_repository: OfficialWorkspaceRepositoryPort,
        year_resolver: PublicFolderYearResolver,
        workflow_repository: PublicFolderWorkflowRepositoryPort,
        folder_check_service: FolderCheckPort,
        public_root: Path | None,
        path_resolver: PublicFolderPathResolver | None = None,
        gateway: PublicFolderWorkflowGatewayPort | None = None,
    ) -> None:
        """Create the workflow service."""
        self._projects = project_repository
        self._workspaces = workspace_repository
        self._year_resolver = year_resolver
        self._repository = workflow_repository
        self._folder_check = folder_check_service
        self._public_root = public_root
        self._path_resolver = path_resolver or PublicFolderPathResolver()
        if gateway is None:
            from backend.infrastructure.files.public_folder_workflow_gateway import (
                PublicFolderWorkflowGateway,
            )

            gateway = PublicFolderWorkflowGateway()
        self._gateway = gateway

    def context(self, project_id: str) -> PublicFolderWorkflowContext:
        """Return workflow context without mutating files."""
        self._require_project(project_id)
        state = self._repository.get_state(project_id)
        workspace = self._workspaces.get_by_project(project_id)
        year = self._resolve_year(project_id)
        blockers = list(year.blockers)
        warnings = list(year.warnings)
        paths = self._resolve_paths(workspace, year, blockers)
        return PublicFolderWorkflowContext(
            project_id=project_id,
            auto_sync_enabled=state.auto_sync_enabled,
            sync_locked=state.sync_locked,
            submitted_at=state.submitted_at,
            public_root=paths.public_root if paths else self._public_root,
            public_root_class=paths.public_root_class if paths else None,
            public_folder_year=year.year,
            year_source=year.source,
            year_evidence=year.evidence,
            local_official_folder_path=workspace.official_folder_path if workspace else None,
            public_open_path=paths.public_open_path if paths else None,
            public_closed_path=paths.public_closed_path if paths else None,
            blockers=tuple(blockers),
            warnings=tuple(warnings),
        )

    def set_auto_sync(
        self,
        project_id: str,
        command: PublicFolderAutoSyncCommand,
    ) -> PublicFolderWorkflowState:
        """Persist the backend-owned auto-sync preference."""
        self._require_project(project_id)
        now = _now()
        current = self._repository.get_state(project_id)
        state = replace(
            current,
            auto_sync_enabled=command.auto_sync_enabled,
            created_at=current.created_at or now,
            updated_at=now,
        )
        return self._repository.save_state(state)

    def preview_sync(self, project_id: str) -> PublicFolderWorkflowPreview:
        """Preview Sync from local official folder to public Open."""
        base = self._base_preview(project_id, "sync")
        if base.blockers:
            return base
        assert base.local_official_folder_path is not None
        assert base.public_open_path is not None

        items = list(base.items)
        local_root = base.local_official_folder_path
        public_open = base.public_open_path
        for directory in self._gateway.list_directories(local_root):
            relative = directory.relative_to(local_root)
            items.append(_directory_item(relative, public_open / relative))
        for local_file in self._gateway.list_files(local_root):
            relative = local_file.relative_to(local_root)
            items.append(self._sync_file_item(project_id, relative, local_file, public_open / relative))

        warnings = list(base.warnings)
        if _extra_public_files(public_open, {item.relative_path for item in items if item.kind == "file"}):
            warnings.append("Public Open folder contains extra unmanaged files.")
        return self._final_preview(replace(base, items=tuple(items), warnings=tuple(warnings)))

    def execute_sync(
        self,
        project_id: str,
        command: PublicFolderWorkflowExecuteCommand,
    ) -> PublicFolderWorkflowResult:
        """Execute Sync after validating a fresh preview hash."""
        preview = self.preview_sync(project_id)
        self._validate_execute_preview(preview, command)
        operation_id = uuid4().hex
        errors: list[str] = []
        for item in preview.items:
            if item.kind == "directory" and item.action == "add":
                self._gateway.create_directory(_required_public_path(item))
        for item in preview.items:
            if item.kind != "file" or item.action not in {"add", "update"}:
                continue
            local_path = _required_local_path(item)
            public_path = _required_public_path(item)
            previous = self._repository.get_file(project_id, item.relative_path)
            try:
                if item.action == "add":
                    self._gateway.copy_new_file(local_path, public_path)
                else:
                    self._gateway.replace_managed_file(
                        local_path,
                        public_path,
                        expected_public_fingerprint=(
                            previous.public_fingerprint if previous else None
                        ),
                    )
            except (OSError, RuntimeError) as exc:
                errors.append(str(exc))
                break
            self._repository.save_file(
                PublicFolderWorkflowFileRecord(
                    project_id=project_id,
                    relative_path=item.relative_path,
                    public_path=public_path,
                    local_fingerprint=self._gateway.fingerprint(local_path),
                    public_fingerprint=self._gateway.fingerprint(public_path),
                    updated_at=_now(),
                    operation_id=operation_id,
                )
            )
        status = "failed" if errors else "completed"
        self._save_operation(operation_id, preview, status, command.operator, errors)
        if not errors:
            state = self._repository.get_state(project_id)
            self._repository.save_state(
                replace(
                    state,
                    last_sync_operation_id=operation_id,
                    created_at=state.created_at or _now(),
                    updated_at=_now(),
                )
            )
        return PublicFolderWorkflowResult(
            project_id=project_id,
            operation_id=operation_id,
            operation_type="sync",
            status=status,
            counts=dict(preview.counts),
            errors=tuple(errors),
            preview=self.preview_sync(project_id),
        )

    def preview_submit(self, project_id: str) -> PublicFolderWorkflowPreview:
        """Preview Submit from public Open to public Closed."""
        base = self._base_preview(project_id, "submit")
        if base.blockers:
            return base
        folder_blockers = _folder_check_blockers(self._folder_check.preview(project_id))
        blockers = list(base.blockers) + list(folder_blockers)
        items = list(base.items)
        if not blockers:
            assert base.public_open_path is not None
            assert base.public_closed_path is not None
            if not base.public_open_path.is_dir():
                blockers.append("Sync public working copy before Submit.")
            elif base.public_closed_path.exists():
                items.append(
                    PublicFolderWorkflowItem(
                        kind="directory",
                        relative_path=Path("."),
                        local_path=None,
                        public_path=base.public_closed_path,
                        action="conflict",
                        status="conflict",
                        message="Public Closed target already exists.",
                    )
                )
            else:
                unmanaged_items = self._unmanaged_public_open_submit_items(
                    project_id,
                    base.public_open_path,
                )
                if unmanaged_items:
                    items.extend(unmanaged_items)
                else:
                    items.append(
                        PublicFolderWorkflowItem(
                            kind="directory",
                            relative_path=Path("."),
                            local_path=base.public_open_path,
                            public_path=base.public_closed_path,
                            action="move",
                            status="ready",
                            message="Public Open working copy will move to Closed.",
                        )
                    )
        return self._final_preview(
            replace(
                base,
                items=tuple(items),
                blockers=tuple(blockers),
                required_confirmations=("submit_to_closed", "no_encryption_or_permissions_v1"),
            )
        )

    def execute_submit(
        self,
        project_id: str,
        command: PublicFolderWorkflowExecuteCommand,
    ) -> PublicFolderWorkflowResult:
        """Execute Submit and persist the backend sync lock."""
        preview = self.preview_submit(project_id)
        self._validate_execute_preview(preview, command)
        operation_id = uuid4().hex
        errors: list[str] = []
        try:
            assert preview.public_open_path is not None
            assert preview.public_closed_path is not None
            self._gateway.create_directory(preview.public_closed_path.parent)
            self._gateway.move_directory_no_overwrite(
                preview.public_open_path,
                preview.public_closed_path,
            )
            self._repository.rebase_files(
                project_id=project_id,
                old_root=preview.public_open_path,
                new_root=preview.public_closed_path,
                operation_id=operation_id,
                updated_at=_now(),
            )
        except (OSError, RuntimeError) as exc:
            errors.append(str(exc))
        status = "failed" if errors else "completed"
        self._save_operation(operation_id, preview, status, command.operator, errors)
        if not errors:
            state = self._repository.get_state(project_id)
            now = _now()
            self._repository.save_state(
                replace(
                    state,
                    sync_locked=True,
                    submitted_at=now,
                    submit_operation_id=operation_id,
                    created_at=state.created_at or now,
                    updated_at=now,
                )
            )
        return PublicFolderWorkflowResult(
            project_id=project_id,
            operation_id=operation_id,
            operation_type="submit",
            status=status,
            counts=dict(preview.counts),
            errors=tuple(errors),
            preview=self.preview_submit(project_id),
        )

    def preview_pull(self, project_id: str) -> PublicFolderWorkflowPreview:
        """Preview Pull from public Closed back to a local history target."""
        base = self._base_preview(project_id, "pull")
        if base.blockers:
            return base
        blockers = list(base.blockers)
        items = list(base.items)
        assert base.local_official_folder_path is not None
        assert base.public_closed_path is not None
        if not base.public_closed_path.is_dir():
            blockers.append("Public Closed folder is not available for Pull.")
        else:
            target = self._gateway.unique_history_target(
                base.local_official_folder_path,
                "Closed",
            )
            items.append(
                PublicFolderWorkflowItem(
                    kind="directory",
                    relative_path=Path("."),
                    local_path=base.public_closed_path,
                    public_path=target,
                    action="copy_to_history",
                    status="ready",
                    message="Closed folder will be copied to a local history folder.",
                )
            )
            base = replace(base, target_path=target)
        return self._final_preview(
            replace(base, items=tuple(items), blockers=tuple(blockers), required_confirmations=("pull_to_history",))
        )

    def execute_pull(
        self,
        project_id: str,
        command: PublicFolderWorkflowExecuteCommand,
    ) -> PublicFolderWorkflowResult:
        """Execute Pull to a unique local history folder."""
        preview = self.preview_pull(project_id)
        self._validate_execute_preview(preview, command)
        operation_id = uuid4().hex
        errors: list[str] = []
        try:
            assert preview.public_closed_path is not None
            assert preview.target_path is not None
            self._gateway.copy_tree_no_overwrite(preview.public_closed_path, preview.target_path)
        except (OSError, RuntimeError) as exc:
            errors.append(str(exc))
        status = "failed" if errors else "completed"
        self._save_operation(operation_id, preview, status, command.operator, errors)
        if not errors:
            state = self._repository.get_state(project_id)
            self._repository.save_state(
                replace(
                    state,
                    last_pull_operation_id=operation_id,
                    created_at=state.created_at or _now(),
                    updated_at=_now(),
                )
            )
        return PublicFolderWorkflowResult(
            project_id=project_id,
            operation_id=operation_id,
            operation_type="pull",
            status=status,
            counts=dict(preview.counts),
            errors=tuple(errors),
            preview=self.preview_pull(project_id),
        )

    def _base_preview(
        self,
        project_id: str,
        operation_type: str,
    ) -> PublicFolderWorkflowPreview:
        self._require_project(project_id)
        state = self._repository.get_state(project_id)
        workspace = self._workspaces.get_by_project(project_id)
        year = self._resolve_year(project_id)
        blockers = list(year.blockers)
        if workspace is None or not workspace.official_folder_path.is_dir():
            blockers.append("Create local project folder before public folder workflow.")
        if operation_type == "sync" and state.sync_locked:
            blockers.append("Sync is locked after Submit.")
        paths = self._resolve_paths(workspace, year, blockers)
        items = tuple(_missing_directory_item(path, paths.public_root) for path in paths.missing_directories) if paths else tuple()
        return self._final_preview(
            PublicFolderWorkflowPreview(
                project_id=project_id,
                operation_type=operation_type,
                status="blocked" if blockers else "current",
                local_official_folder_path=workspace.official_folder_path if workspace else None,
                public_root=paths.public_root if paths else self._public_root,
                public_root_class=paths.public_root_class if paths else None,
                public_folder_year=year.year,
                year_source=year.source,
                year_evidence=year.evidence,
                public_open_path=paths.public_open_path if paths else None,
                public_closed_path=paths.public_closed_path if paths else None,
                target_path=None,
                items=items,
                blockers=tuple(blockers),
                warnings=year.warnings,
                conflicts=tuple(),
                required_confirmations=("create_missing_public_directories",) if items else tuple(),
                counts=_counts(items),
                preview_hash="",
                next_action="none",
                auto_sync_enabled=state.auto_sync_enabled,
                sync_locked=state.sync_locked,
            )
        )

    def _sync_file_item(
        self,
        project_id: str,
        relative: Path,
        local_path: Path,
        public_path: Path,
    ) -> PublicFolderWorkflowItem:
        local_fingerprint = self._gateway.fingerprint(local_path)
        previous = self._repository.get_file(project_id, relative)
        if not public_path.exists():
            return _file_item(relative, local_path, public_path, "add", "ready", "Will be copied to public Open.")
        if not public_path.is_file():
            return _file_item(relative, local_path, public_path, "conflict", "conflict", "Public Open path is not a file.")
        public_fingerprint = self._gateway.fingerprint(public_path)
        if public_fingerprint == local_fingerprint:
            return _file_item(relative, local_path, public_path, "skip", "current", "Public Open file is current.")
        if previous is None:
            return _file_item(relative, local_path, public_path, "conflict", "conflict", "Public Open file is not managed by ConnLab.")
        if public_fingerprint != previous.public_fingerprint:
            return _file_item(relative, local_path, public_path, "conflict", "conflict", "Public Open file changed outside ConnLab.")
        return _file_item(relative, local_path, public_path, "update", "ready", "Managed public Open file will be updated.")

    def _unmanaged_public_open_submit_items(
        self,
        project_id: str,
        public_open_path: Path,
    ) -> tuple[PublicFolderWorkflowItem, ...]:
        conflicts: list[PublicFolderWorkflowItem] = []
        for public_file in self._gateway.list_files(public_open_path):
            relative = public_file.relative_to(public_open_path)
            record = self._repository.get_file(project_id, relative)
            if record is None or record.public_path.resolve() != public_file.resolve():
                conflicts.append(
                    PublicFolderWorkflowItem(
                        kind="file",
                        relative_path=relative,
                        local_path=None,
                        public_path=public_file,
                        action="conflict",
                        status="conflict",
                        message="Public Open file is not managed by ConnLab; remove or sync through ConnLab before Submit.",
                    )
                )
        return tuple(conflicts)

    def _validate_execute_preview(
        self,
        preview: PublicFolderWorkflowPreview,
        command: PublicFolderWorkflowExecuteCommand,
    ) -> None:
        if not command.confirmed:
            raise PublicFolderWorkflowBlockedError("Operator confirmation is required.")
        if preview.preview_hash != command.preview_hash:
            raise PublicFolderWorkflowConflictError("Public folder preview is stale.")
        if preview.blockers:
            raise PublicFolderWorkflowBlockedError(preview.blockers[0])
        if preview.conflicts or preview.status == "conflict":
            detail = preview.conflicts[0] if preview.conflicts else "Resolve public folder conflicts."
            raise PublicFolderWorkflowConflictError(detail)
        if any(item.action == "add" and item.kind == "directory" for item in preview.items):
            if not command.confirm_directory_creation:
                raise PublicFolderWorkflowBlockedError("Directory creation confirmation is required.")

    def _save_operation(
        self,
        operation_id: str,
        preview: PublicFolderWorkflowPreview,
        status: str,
        operator: str | None,
        errors: list[str],
    ) -> None:
        now = _now()
        self._repository.save_operation(
            PublicFolderWorkflowOperationRecord(
                operation_id=operation_id,
                project_id=preview.project_id,
                operation_type=preview.operation_type,
                status=status,
                preview_hash=preview.preview_hash,
                requested_at=now,
                started_at=now,
                completed_at=now,
                operator=operator,
                public_root=preview.public_root,
                public_root_class=preview.public_root_class,
                public_folder_year=preview.public_folder_year,
                year_source=preview.year_source,
                local_official_folder_path=preview.local_official_folder_path,
                public_open_path=preview.public_open_path,
                public_closed_path=preview.public_closed_path,
                target_path=preview.target_path,
                counts=dict(preview.counts),
                blockers=preview.blockers,
                warnings=preview.warnings,
                conflicts=tuple(preview.conflicts) + tuple(errors),
                snapshot_json=json.dumps(_preview_snapshot(preview), sort_keys=True),
            )
        )

    def _final_preview(self, preview: PublicFolderWorkflowPreview) -> PublicFolderWorkflowPreview:
        items = tuple(sorted(preview.items, key=lambda item: (item.kind, item.relative_path.as_posix(), item.action)))
        counts = _counts(items)
        conflicts = tuple(item.message for item in items if item.status == "conflict")
        if preview.blockers:
            status = "blocked"
            next_action = "none"
        elif conflicts:
            status = "conflict"
            next_action = "none"
        elif any(action in counts and counts[action] for action in ("add", "update", "move", "copy_to_history")):
            status = "ready"
            next_action = preview.operation_type
        else:
            status = "current"
            next_action = "none"
        normalized = replace(
            preview,
            status=status,
            items=items,
            conflicts=conflicts,
            counts=counts,
            next_action=next_action,
            preview_hash="",
        )
        return replace(normalized, preview_hash=_preview_hash(normalized))

    def _resolve_year(self, project_id: str) -> PublicFolderYearResolution:
        try:
            return self._year_resolver.resolve(project_id)
        except LookupError as exc:
            raise PublicFolderWorkflowNotFoundError(str(exc)) from exc

    def _resolve_paths(
        self,
        workspace: OfficialWorkspaceRecord | None,
        year: PublicFolderYearResolution,
        blockers: list[str],
    ) -> PublicFolderPaths | None:
        if workspace is None:
            return None
        try:
            return self._path_resolver.resolve(
                public_root=self._public_root,
                year=year.year,
                project_folder_name=workspace.official_folder_path.name,
            )
        except PublicFolderPathError as exc:
            blockers.append(str(exc))
            return None

    def _require_project(self, project_id: str) -> Project:
        project = self._projects.get(project_id)
        if project is None:
            raise PublicFolderWorkflowNotFoundError(f"Project not found: {project_id}")
        return project


def _folder_check_blockers(preview: OfficialFolderCheckPreview) -> tuple[str, ...]:
    if preview.status in {"blocked", "conflict"}:
        return preview.blockers or ("Project Folder check must be resolved before Submit.",)
    if preview.status == "missing":
        return ("Complete required Project Folder items before Submit.",)
    return tuple()


def _missing_directory_item(path: Path, root: Path) -> PublicFolderWorkflowItem:
    return PublicFolderWorkflowItem(
        kind="directory",
        relative_path=path.relative_to(root),
        local_path=None,
        public_path=path,
        action="add",
        status="ready",
        message="Directory will be created after confirmation.",
    )


def _directory_item(relative: Path, public_path: Path) -> PublicFolderWorkflowItem:
    if not public_path.exists():
        return PublicFolderWorkflowItem("directory", relative, None, public_path, "add", "ready", "Directory will be created.")
    if public_path.is_dir():
        return PublicFolderWorkflowItem("directory", relative, None, public_path, "skip", "current", "Directory already exists.")
    return PublicFolderWorkflowItem("directory", relative, None, public_path, "conflict", "conflict", "Public Open path is a file, expected directory.")


def _file_item(
    relative: Path,
    local_path: Path,
    public_path: Path,
    action: str,
    status: str,
    message: str,
) -> PublicFolderWorkflowItem:
    return PublicFolderWorkflowItem("file", relative, local_path, public_path, action, status, message)


def _extra_public_files(public_folder: Path, planned_files: set[Path]) -> tuple[Path, ...]:
    if not public_folder.is_dir():
        return tuple()
    return tuple(
        path.relative_to(public_folder)
        for path in public_folder.rglob("*")
        if path.is_file() and path.relative_to(public_folder) not in planned_files
    )


def _counts(items: tuple[PublicFolderWorkflowItem, ...]) -> dict[str, int]:
    counts = {key: 0 for key in ("add", "update", "skip", "conflict", "move", "copy_to_history")}
    for item in items:
        counts[item.action] = counts.get(item.action, 0) + 1
    return counts


def _preview_hash(preview: PublicFolderWorkflowPreview) -> str:
    payload = _preview_snapshot(preview)
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def _preview_snapshot(preview: PublicFolderWorkflowPreview) -> dict[str, object]:
    return {
        "project_id": preview.project_id,
        "operation_type": preview.operation_type,
        "public_root": _path(preview.public_root),
        "public_root_class": preview.public_root_class,
        "public_folder_year": preview.public_folder_year,
        "year_source": preview.year_source,
        "local_official_folder_path": _path(preview.local_official_folder_path),
        "public_open_path": _path(preview.public_open_path),
        "public_closed_path": _path(preview.public_closed_path),
        "target_path": _path(preview.target_path),
        "items": [
            {
                "kind": item.kind,
                "relative_path": item.relative_path.as_posix(),
                "local_path": _path(item.local_path),
                "public_path": _path(item.public_path),
                "action": item.action,
                "status": item.status,
                "message": item.message,
            }
            for item in preview.items
        ],
        "blockers": list(preview.blockers),
        "warnings": list(preview.warnings),
        "conflicts": list(preview.conflicts),
        "required_confirmations": list(preview.required_confirmations),
        "auto_sync_enabled": preview.auto_sync_enabled,
        "sync_locked": preview.sync_locked,
    }


def _path(path: Path | None) -> str | None:
    return str(path) if path is not None else None


def _required_local_path(item: PublicFolderWorkflowItem) -> Path:
    if item.local_path is None:
        raise PublicFolderWorkflowBlockedError("Preview item is missing a local path.")
    return item.local_path


def _required_public_path(item: PublicFolderWorkflowItem) -> Path:
    if item.public_path is None:
        raise PublicFolderWorkflowBlockedError("Preview item is missing a public path.")
    return item.public_path


def _now() -> str:
    return datetime.now(UTC).isoformat()
