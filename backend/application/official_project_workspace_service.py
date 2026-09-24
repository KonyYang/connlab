"""Application service for local official project workspace creation."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from backend.application.official_project_workspace_naming import (
    OfficialWorkspaceNamingError,
    build_official_project_folder_name,
)
from backend.application.project_identity import (
    display_identity_override_from_values,
    resolve_project_identity,
)
from backend.application.project_basic_information_output import ConfirmedBasicInformationReader
from backend.application.project_lifecycle_write_guard import (
    LifecycleWriteOperation,
    ProjectLifecycleWriteGuard,
)
from backend.domain import ApplicationForm, LtrRecord, Project
from backend.infrastructure.official_workspace_manifest import (
    OfficialWorkspaceManifest,
    OfficialWorkspaceManifestGateway,
)
from backend.shared.config import OfficialWorkspaceSettings


REQUIRED_TEMPLATE_PATHS = (
    Path("E-mail"),
    Path("Submitted Material"),
    Path("Photos"),
    Path("Test results"),
    Path("Test results") / "Final Examination",
)


class OfficialWorkspaceError(ValueError):
    """Base error for official workspace workflows."""


class OfficialWorkspaceNotFoundError(LookupError):
    """Raised when an official workspace input record is missing."""


class OfficialWorkspaceCreateError(OfficialWorkspaceError):
    """Raised when local official workspace creation cannot safely proceed."""


class ProjectRepositoryPort(Protocol):
    """Project lookup operations required by this service."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by id."""


class OfficialWorkspaceRepositoryPort(Protocol):
    """Persistence operations for local official workspace records."""

    def get_by_project(self, project_id: str) -> "OfficialWorkspaceRecord | None":
        """Return a workspace record for a project when one exists."""

    def save(self, record: "OfficialWorkspaceRecord") -> "OfficialWorkspaceRecord":
        """Create or update a workspace record."""


class LtrRecordRepositoryPort(Protocol):
    """LTR lookup operations required for legacy project identity fallback."""

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        """Return LTR records for a project."""


class ApplicationFormRepositoryPort(Protocol):
    """Application form lookup operations required for naming metadata."""

    def list_by_project(self, project_id: str) -> list[ApplicationForm]:
        """Return application forms for a project."""


@dataclass(frozen=True, slots=True)
class OfficialWorkspaceConflictOption:
    """One operator choice for resolving an existing local project folder."""

    key: str
    label: str
    description: str


@dataclass(frozen=True, slots=True)
class OfficialWorkspaceRecord:
    """ConnLab application index record for an official project workspace."""

    workspace_id: str
    project_id: str
    dl_number: str
    local_workspace_path: Path
    source_book_path: Path
    official_folder_path: Path
    manifest_path: Path
    template_source_path: Path
    created_at: str


@dataclass(frozen=True, slots=True)
class OfficialWorkspacePreview:
    """Preview of local official project workspace creation."""

    project_id: str
    dl_number: str | None
    local_workspace_root: Path | None
    local_workspace_path: Path | None
    source_book_path: Path | None
    template_path: Path | None
    official_folder_path: Path | None
    manifest_path: Path | None
    template_root_mode: str | None
    status: str
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    planned_paths: tuple[Path, ...]
    conflict_paths: tuple[Path, ...] = tuple()
    conflict_options: tuple[OfficialWorkspaceConflictOption, ...] = tuple()


@dataclass(frozen=True, slots=True)
class OfficialWorkspaceCreateResult:
    """Result of creating or continuing a local official project workspace."""

    record: OfficialWorkspaceRecord
    created_paths: tuple[Path, ...]
    warnings: tuple[str, ...]

    @property
    def official_folder_path(self) -> Path:
        """Return the created official project folder path."""
        return self.record.official_folder_path


@dataclass(frozen=True, slots=True)
class OfficialWorkspaceConflictResolution:
    """Paths moved while resolving a local project folder conflict."""

    created_paths: tuple[Path, ...]
    restore_path: Path | None
    restore_target: Path | None


@dataclass(frozen=True, slots=True)
class OfficialTemplateRoot:
    """Resolved official project folder template root."""

    path: Path
    mode: str


class OfficialProjectWorkspaceService:
    """Coordinate local official project workspace preview and creation."""

    def __init__(
        self,
        project_repository: ProjectRepositoryPort,
        workspace_repository: OfficialWorkspaceRepositoryPort,
        settings: OfficialWorkspaceSettings,
        ltr_repository: LtrRecordRepositoryPort | None = None,
        application_form_repository: ApplicationFormRepositoryPort | None = None,
        manifest_gateway: OfficialWorkspaceManifestGateway | None = None,
        basic_information_reader: ConfirmedBasicInformationReader | None = None,
    ) -> None:
        """Create the workspace service."""
        self._projects = project_repository
        self._workspaces = workspace_repository
        self._ltrs = ltr_repository
        self._forms = application_form_repository
        self._settings = settings
        self._manifests = manifest_gateway or OfficialWorkspaceManifestGateway()
        self._basic_information = basic_information_reader

    def preview(self, project_id: str) -> OfficialWorkspacePreview:
        """Return a safe preview for local official project workspace creation."""
        project = self._get_project(project_id)
        ltrs = self._ltrs.list_by_project(project.project_id) if self._ltrs else []
        confirmed_basic = (
            self._basic_information.get_latest_confirmed(project_id)
            if self._basic_information else None
        )
        identity = resolve_project_identity(
            project, ltrs,
            identity_override=display_identity_override_from_values(
                confirmed_basic.values if confirmed_basic else None
            ),
        )
        dl_number = identity.ltr_number
        blockers: list[str] = []
        warnings: list[str] = []
        if not dl_number:
            blockers.append("DL number is required before creating a local project workspace.")
        local_root = self._settings.local_workspace_root
        template_setting = self._settings.template_path
        if local_root is None:
            blockers.append("Project default save location is not configured.")
        elif not local_root.is_dir():
            blockers.append(f"Project default save location does not exist: {local_root}")
        if self._settings.public_drive_root is None:
            warnings.append("Public Project locations is not configured; upload readiness will be checked later.")
        elif not self._settings.public_drive_root.is_dir():
            warnings.append(
                f"Public Project locations is not available; local workspace can still be created: "
                f"{self._settings.public_drive_root}"
            )

        template_root: OfficialTemplateRoot | None = None
        template_blockers: list[str] = []
        if template_setting is None:
            template_blockers.append("Template folder is not configured.")
        if template_setting is not None:
            try:
                template_root = resolve_official_template_root(template_setting)
            except OfficialWorkspaceError as exc:
                template_blockers.append(str(exc))
        if template_blockers:
            template_blockers = [
                f"{detail} Open Settings > External Resources and select an existing Project Folder Template folder."
                for detail in template_blockers
            ]

        if blockers or not dl_number or local_root is None:
            return OfficialWorkspacePreview(
                project_id=project_id,
                dl_number=dl_number,
                local_workspace_root=local_root,
                local_workspace_path=None,
                source_book_path=None,
                template_path=template_root.path if template_root else template_setting,
                official_folder_path=None,
                manifest_path=None,
                template_root_mode=template_root.mode if template_root else None,
                status="blocked",
                blockers=tuple(blockers),
                warnings=tuple(warnings),
                planned_paths=tuple(),
            )

        try:
            folder_name = build_official_project_folder_name(
                dl_number=dl_number,
                product_description=identity.sample_description or project.product_name,
                test_description=identity.test_item or self._latest_requested_testing(project_id),
            )
        except OfficialWorkspaceNamingError as exc:
            return _blocked_preview(project_id, dl_number, local_root, template_root, [str(exc)], warnings)

        workspace_path = local_root / dl_number
        source_book_path = workspace_path / "Source Book"
        official_folder_path = workspace_path / folder_name
        manifest_path = workspace_path / ".connlab" / "manifest.json"
        completed_record = self._workspaces.get_by_project(project_id)
        recorded_path_exists = completed_record is not None and any(
            path.exists() for path in (
                completed_record.local_workspace_path,
                completed_record.source_book_path,
                completed_record.official_folder_path,
                completed_record.manifest_path,
            )
        )
        if not workspace_path.exists() and not recorded_path_exists:
            legacy_candidates = self._legacy_workspace_candidates(
                local_root, project_id, dl_number
            )
            if len(legacy_candidates) > 1:
                return OfficialWorkspacePreview(
                    project_id=project_id,
                    dl_number=dl_number,
                    local_workspace_root=local_root,
                    local_workspace_path=None,
                    source_book_path=None,
                    template_path=template_root.path if template_root else template_setting,
                    official_folder_path=None,
                    manifest_path=None,
                    template_root_mode=template_root.mode if template_root else None,
                    status="blocked",
                    blockers=("Multiple same-project legacy workspaces match this DL number. Review their manifests before linking a folder.",),
                    warnings=tuple(warnings),
                    planned_paths=tuple(),
                    conflict_paths=tuple(path for path, _ in legacy_candidates),
                )
            if legacy_candidates:
                workspace_path, official_folder_path = legacy_candidates[0]
                source_book_path = workspace_path / "Source Book"
                manifest_path = workspace_path / ".connlab" / "manifest.json"
                warnings.append("A same-project legacy workspace was found under the configured save location; link it explicitly before generating outputs.")
        planned_paths = (workspace_path, source_book_path, official_folder_path, manifest_path)

        redirected_path = self._manifests.first_redirected_path(
            local_root,
            workspace_path,
            source_book_path,
            official_folder_path,
            manifest_path.parent,
            manifest_path,
        )
        if redirected_path is not None:
            return OfficialWorkspacePreview(
                project_id=project_id,
                dl_number=dl_number,
                local_workspace_root=local_root,
                local_workspace_path=workspace_path,
                source_book_path=source_book_path,
                template_path=_adoption_template_metadata(
                    None, template_setting, official_folder_path
                ),
                official_folder_path=official_folder_path,
                manifest_path=manifest_path,
                template_root_mode=template_root.mode if template_root else None,
                status="conflict",
                blockers=(
                    "Project workspace identity cannot be linked through a symbolic link "
                    f"or junction: {redirected_path}",
                ),
                warnings=tuple(warnings),
                planned_paths=planned_paths,
                conflict_paths=(workspace_path,),
                conflict_options=_conflict_options(),
            )

        if (
            completed_record is not None
            and completed_record.local_workspace_path != workspace_path
            and not any(
                path.exists()
                for path in (
                    completed_record.local_workspace_path,
                    completed_record.source_book_path,
                    completed_record.official_folder_path,
                    completed_record.manifest_path,
                )
            )
        ):
            warnings.append(
                "The previous workspace record has no remaining files; ConnLab will "
                "use the current Project default save location."
            )
            completed_record = None
        if completed_record is not None:
            record_inconsistency = self._workspace_record_inconsistency(
                completed_record,
                project_id=project_id,
                dl_number=dl_number,
            )
            record_warnings = list(warnings)
            if completed_record.official_folder_path != official_folder_path:
                record_warnings.append(
                    "Existing local project workspace uses a different official folder "
                    "name than the current naming rule; repair or rename can be handled "
                    "separately."
                )
            if record_inconsistency is None:
                return OfficialWorkspacePreview(
                    project_id=project_id,
                    dl_number=dl_number,
                    local_workspace_root=local_root,
                    local_workspace_path=completed_record.local_workspace_path,
                    source_book_path=completed_record.source_book_path,
                    template_path=completed_record.template_source_path,
                    official_folder_path=completed_record.official_folder_path,
                    manifest_path=completed_record.manifest_path,
                    template_root_mode=template_root.mode if template_root else None,
                    status="completed",
                    blockers=tuple(),
                    warnings=tuple(record_warnings),
                    planned_paths=(
                        completed_record.local_workspace_path,
                        completed_record.source_book_path,
                        completed_record.official_folder_path,
                        completed_record.manifest_path,
                    ),
                )
            if record_inconsistency == (
                f"Official project folder is missing: {completed_record.official_folder_path}"
            ):
                record_warnings.append(
                    "Previous local project workspace record points to a missing "
                    "official project folder; its identity must be reviewed before repair."
                )
                payload, manifest_error = self._read_manifest_identity(
                    manifest_path=completed_record.manifest_path,
                    project_id=project_id, dl_number=dl_number,
                )
                candidates = self._renamed_official_candidates(workspace_path, dl_number)
                recorded_leaf = completed_record.official_folder_path.name
                manifest_folder = (
                    _portable_official_folder_path(workspace_path, payload)
                    if payload is not None else None
                )
                if payload is not None and (
                    payload.get("dl_number") != dl_number
                    or manifest_folder is None
                    or manifest_folder.name != recorded_leaf
                ):
                    manifest_error = "Workspace manifest does not match the recorded official folder and DL number."
                if candidates:
                    status = "inconsistent"
                    selected_folder = completed_record.official_folder_path
                    detail = (
                        f"{manifest_error} " if manifest_error else ""
                    ) + (
                        "Possible renamed official folder(s) need manual review; "
                        "folder names alone do not prove identity: "
                        + ", ".join(str(candidate) for candidate in candidates)
                    )
                elif manifest_error or payload is not None or official_folder_path.exists():
                    status = "inconsistent"
                    selected_folder = completed_record.official_folder_path
                    detail = manifest_error or (
                        "Recorded official folder is missing; its manifest identity requires manual review."
                    )
                else:
                    status = "ready" if template_root is not None else "blocked"
                    selected_folder = official_folder_path
                    detail = template_blockers[0] if template_blockers else None
                    record_warnings.append(
                        "ConnLab can generate a new official folder from the standard template."
                    )
                return OfficialWorkspacePreview(
                    project_id=project_id,
                    dl_number=dl_number,
                    local_workspace_root=local_root,
                    local_workspace_path=completed_record.local_workspace_path,
                    source_book_path=completed_record.source_book_path,
                    template_path=template_root.path if template_root else template_setting,
                    official_folder_path=selected_folder,
                    manifest_path=manifest_path,
                    template_root_mode=template_root.mode if template_root else None,
                    status=status,
                    blockers=(detail,) if detail else tuple(),
                    warnings=tuple(record_warnings),
                    planned_paths=(workspace_path, source_book_path, selected_folder, manifest_path),
                )
            return OfficialWorkspacePreview(
                project_id=project_id,
                dl_number=dl_number,
                local_workspace_root=local_root,
                local_workspace_path=completed_record.local_workspace_path,
                source_book_path=completed_record.source_book_path,
                template_path=completed_record.template_source_path,
                official_folder_path=completed_record.official_folder_path,
                manifest_path=completed_record.manifest_path,
                template_root_mode=template_root.mode if template_root else None,
                status="inconsistent",
                blockers=(record_inconsistency,),
                warnings=tuple(record_warnings),
                planned_paths=planned_paths,
            )

        manifest_payload, manifest_error = self._read_manifest_identity(
            manifest_path=manifest_path,
            project_id=project_id,
            dl_number=dl_number,
        )
        if manifest_error is not None:
            warnings.append(
                "The existing local workspace identity cannot be linked. Review it "
                "before using the advanced Backup and Rebuild action."
            )
            return OfficialWorkspacePreview(
                project_id=project_id,
                dl_number=dl_number,
                local_workspace_root=local_root,
                local_workspace_path=workspace_path,
                source_book_path=source_book_path,
                        template_path=template_root.path if template_root else template_setting,
                official_folder_path=official_folder_path,
                manifest_path=manifest_path,
                        template_root_mode=template_root.mode if template_root else None,
                status="conflict",
                blockers=(manifest_error,),
                warnings=tuple(warnings),
                planned_paths=planned_paths,
                conflict_paths=(workspace_path,),
                conflict_options=_conflict_options(),
            )

        if manifest_payload is not None:
            rebound = _portable_official_folder_path(workspace_path, manifest_payload)
            if rebound is None or not rebound.is_dir() or not source_book_path.is_dir():
                detail = (
                    "Workspace manifest belongs to this project, but its current "
                    "official folder or Source Book cannot be verified."
                )
                return OfficialWorkspacePreview(
                    project_id=project_id,
                    dl_number=dl_number,
                    local_workspace_root=local_root,
                    local_workspace_path=workspace_path,
                    source_book_path=source_book_path,
                    template_path=template_root.path if template_root else template_setting,
                    official_folder_path=rebound or official_folder_path,
                    manifest_path=manifest_path,
                    template_root_mode=template_root.mode if template_root else None,
                    status="conflict",
                    blockers=(detail,),
                    warnings=tuple(warnings),
                    planned_paths=planned_paths,
                    conflict_paths=(workspace_path,),
                    conflict_options=_conflict_options(),
                )
            return OfficialWorkspacePreview(
                project_id=project_id,
                dl_number=dl_number,
                local_workspace_root=local_root,
                local_workspace_path=workspace_path,
                source_book_path=source_book_path,
                template_path=_adoption_template_metadata(
                    manifest_payload, template_setting, rebound
                ),
                official_folder_path=rebound,
                manifest_path=manifest_path,
                template_root_mode=template_root.mode if template_root else None,
                status="adoptable",
                blockers=tuple(),
                warnings=tuple(warnings),
                planned_paths=(workspace_path, source_book_path, rebound, manifest_path),
            )

        if official_folder_path.exists():
            status = "adoptable" if source_book_path.is_dir() else "conflict"
            blockers = tuple() if status == "adoptable" else (
                "Existing project folder cannot be linked because Source Book is missing.",
            )
            return OfficialWorkspacePreview(
                project_id=project_id,
                dl_number=dl_number,
                local_workspace_root=local_root,
                local_workspace_path=workspace_path,
                source_book_path=source_book_path,
                template_path=_adoption_template_metadata(
                    None, template_setting, official_folder_path
                ),
                official_folder_path=official_folder_path,
                manifest_path=manifest_path,
                template_root_mode=template_root.mode if template_root else None,
                status=status,
                blockers=blockers,
                warnings=tuple(warnings),
                planned_paths=planned_paths,
                conflict_paths=(official_folder_path,),
                conflict_options=_conflict_options() if status == "conflict" else tuple(),
            )

        status = "ready"
        if workspace_path.exists():
            if _workspace_has_business_content(workspace_path):
                return OfficialWorkspacePreview(
                    project_id=project_id,
                    dl_number=dl_number,
                    local_workspace_root=local_root,
                    local_workspace_path=workspace_path,
                    source_book_path=source_book_path,
                    template_path=template_root.path if template_root else template_setting,
                    official_folder_path=official_folder_path,
                    manifest_path=manifest_path,
                    template_root_mode=template_root.mode if template_root else None,
                    status="conflict",
                    blockers=(f"Local project workspace already exists: {workspace_path}",),
                    warnings=tuple(warnings),
                    planned_paths=planned_paths,
                    conflict_paths=(workspace_path,),
                    conflict_options=_conflict_options(),
                )
            status = "ready"
            warnings.append("An empty local project workspace already exists and can be created safely.")

        if template_root is None:
            return OfficialWorkspacePreview(
                project_id=project_id,
                dl_number=dl_number,
                local_workspace_root=local_root,
                local_workspace_path=workspace_path,
                source_book_path=source_book_path,
                template_path=template_setting,
                official_folder_path=official_folder_path,
                manifest_path=manifest_path,
                template_root_mode=None,
                status="blocked",
                blockers=tuple(template_blockers),
                warnings=tuple(warnings),
                planned_paths=planned_paths,
            )

        return OfficialWorkspacePreview(
            project_id=project_id,
            dl_number=dl_number,
            local_workspace_root=local_root,
            local_workspace_path=workspace_path,
            source_book_path=source_book_path,
            template_path=template_root.path,
            official_folder_path=official_folder_path,
            manifest_path=manifest_path,
            template_root_mode=template_root.mode,
            status=status,
            blockers=tuple(),
            warnings=tuple(warnings),
            planned_paths=planned_paths,
        )

    def _legacy_workspace_candidates(
        self, root: Path, project_id: str, dl_number: str
    ) -> list[tuple[Path, Path]]:
        """Find only direct, non-redirected folders with matching portable identity."""
        candidates: list[tuple[Path, Path]] = []
        try:
            children = sorted(root.iterdir())
        except OSError as exc:
            raise OfficialWorkspaceError(
                f"Cannot inspect the configured project save location: {root}"
            ) from exc
        for workspace in children:
            manifest_path = workspace / ".connlab" / "manifest.json"
            source_book_path = workspace / "Source Book"
            if self._manifests.first_redirected_path(
                root, workspace, source_book_path, manifest_path.parent, manifest_path
            ) is not None or not manifest_path.is_file() or not source_book_path.is_dir():
                continue
            payload, error = self._read_manifest_identity(
                manifest_path=manifest_path, project_id=project_id,
                dl_number=dl_number,
            )
            if (
                error is not None or payload is None
                or payload.get("dl_number") != dl_number
            ):
                continue
            official_folder = _portable_official_folder_path(workspace, payload)
            if (
                official_folder is None or not official_folder.is_dir()
                or self._manifests.first_redirected_path(official_folder) is not None
            ):
                continue
            candidates.append((workspace, official_folder))
        return candidates

    def _renamed_official_candidates(self, workspace: Path, dl_number: str) -> list[Path]:
        """Only direct DL-named folders inside the indexed workspace can be reviewed."""
        try:
            children = sorted(workspace.iterdir())
        except OSError:
            return []
        return [
            child for child in children
            if child.name.startswith(f"{dl_number} ")
            and self._manifests.first_redirected_path(child) is None
            and child.is_dir()
        ]

    def create(
        self,
        project_id: str,
        conflict_strategy: str | None = None,
        recovery=None,
    ) -> OfficialWorkspaceCreateResult:
        """Create or continue the local official project workspace."""
        if recovery is None and conflict_strategy in {"continue_existing", "overwrite_rebuild"}:
            raise OfficialWorkspaceCreateError(
                f"{conflict_strategy} is not available for new project folder operations."
            )
        preview = self.preview(project_id)
        ProjectLifecycleWriteGuard(self._projects).require_write_allowed(
            project_id, LifecycleWriteOperation.REQUIRED_FORMS_GENERATE
        )
        if preview.status == "completed" and conflict_strategy is None:
            record = self._workspaces.get_by_project(project_id)
            if record is None:
                raise OfficialWorkspaceCreateError("Local project workspace record is missing.")
            if recovery is not None:
                recovery.remember_existing(record)
            return OfficialWorkspaceCreateResult(
                record=record,
                created_paths=tuple(),
                warnings=preview.warnings,
            )
        allowed_conflict_strategies = {option.key for option in preview.conflict_options}
        if recovery is not None:
            # Historical journal recovery may finish an already-authorized operation;
            # new requests cannot select these legacy strategies.
            allowed_conflict_strategies.update({"continue_existing", "overwrite_rebuild"})
        if preview.status == "completed" and recovery is not None:
            allowed_conflict_strategies = {
                "continue_existing",
                "backup_and_recreate",
                "overwrite_rebuild",
            }
        elif preview.status == "completed":
            allowed_conflict_strategies = {"backup_and_recreate"}
        if preview.status in {"conflict", "exists", "completed"} and conflict_strategy in allowed_conflict_strategies:
            pass
        elif preview.status not in {"ready", "adoptable"}:
            detail = preview.blockers[0] if preview.blockers else preview.status
            raise OfficialWorkspaceCreateError(detail)
        assert preview.dl_number is not None
        assert preview.local_workspace_path is not None
        assert preview.source_book_path is not None
        assert preview.official_folder_path is not None
        assert preview.manifest_path is not None
        if preview.status == "adoptable" and preview.official_folder_path.is_dir():
            raise OfficialWorkspaceCreateError(
                "Existing project folder is ready to link. Use Link existing folder; "
                "Create will not modify operator-owned content."
            )
        template_root = self._template_root_for_generation(
            preview.template_path, preview.local_workspace_path
        )
        preview = replace(
            preview,
            template_path=template_root.path,
            template_root_mode=template_root.mode,
        )

        if recovery is not None:
            return recovery.create(preview, conflict_strategy, self._workspaces)

        created_paths: list[Path] = []
        restore_path: Path | None = None
        restore_target: Path | None = None
        workspace_path = preview.local_workspace_path
        source_book_path = preview.source_book_path
        workspace_conflict = preview.conflict_paths == (workspace_path,)
        tmp_root = (
            workspace_path.parent / ".connlab" / "tmp"
            if workspace_conflict
            else workspace_path / ".connlab" / "tmp"
        )
        operation_tmp = tmp_root / f"create-official-folder-{uuid4().hex}"
        copied_root = operation_tmp / preview.template_path.name
        try:
            operation_tmp.mkdir(parents=True, exist_ok=True)
            if conflict_strategy == "continue_existing":
                workspace_path.mkdir(parents=True, exist_ok=True)
                source_book_path.mkdir(parents=True, exist_ok=True)
                merge_missing_workspace_tree(preview.template_path, preview.official_folder_path)
            elif preview.status in {"conflict", "exists"} and workspace_conflict:
                assert conflict_strategy is not None
                resolution = _resolve_existing_path(
                    existing_path=workspace_path,
                    conflict_strategy=conflict_strategy,
                    operation_tmp=operation_tmp,
                )
                created_paths.extend(resolution.created_paths)
                restore_path = resolution.restore_path
                restore_target = resolution.restore_target
            if conflict_strategy != "continue_existing" and not workspace_path.exists():
                workspace_path.mkdir(parents=True)
                created_paths.append(workspace_path)
            if conflict_strategy != "continue_existing" and not source_book_path.exists():
                source_book_path.mkdir(parents=True)
                created_paths.append(source_book_path)
            if conflict_strategy != "continue_existing":
                _copytree_no_overwrite(preview.template_path, copied_root)
            if (
                conflict_strategy != "continue_existing"
                and preview.status in {"conflict", "exists", "completed"}
                and not workspace_conflict
            ):
                assert conflict_strategy is not None
                resolution = _resolve_existing_path(
                    existing_path=preview.official_folder_path,
                    conflict_strategy=conflict_strategy,
                    operation_tmp=operation_tmp,
                )
                created_paths.extend(resolution.created_paths)
                restore_path = resolution.restore_path
                restore_target = resolution.restore_target
            if conflict_strategy != "continue_existing":
                shutil.move(str(copied_root), str(preview.official_folder_path))
                created_paths.append(preview.official_folder_path)
        except Exception as exc:
            _restore_overwrite_source(restore_path, restore_target)
            shutil.rmtree(operation_tmp, ignore_errors=True)
            raise OfficialWorkspaceCreateError(str(exc)) from exc
        finally:
            if operation_tmp.exists():
                shutil.rmtree(operation_tmp, ignore_errors=True)

        now = datetime.now(UTC).replace(microsecond=0).isoformat()
        record = OfficialWorkspaceRecord(
            workspace_id=uuid4().hex,
            project_id=project_id,
            dl_number=preview.dl_number,
            local_workspace_path=workspace_path,
            source_book_path=source_book_path,
            official_folder_path=preview.official_folder_path,
            manifest_path=preview.manifest_path,
            template_source_path=preview.template_path,
            created_at=now,
        )
        try:
            self._manifests.write_adoption(
                preview.manifest_path,
                OfficialWorkspaceManifest(
                schema_version=1,
                project_id=record.project_id,
                dl_number=record.dl_number,
                local_workspace_path=str(record.local_workspace_path),
                source_book_path=str(record.source_book_path),
                official_project_folder_path=str(record.official_folder_path),
                template_source_path=str(record.template_source_path),
                created_at=record.created_at,
                ),
            )
        except (OSError, ValueError) as exc:
            raise OfficialWorkspaceCreateError(str(exc)) from exc
        saved = self._workspaces.save(record)
        return OfficialWorkspaceCreateResult(
            record=saved,
            created_paths=tuple(created_paths),
            warnings=preview.warnings,
        )

    def _template_root_for_generation(
        self,
        retained_template_path: Path | None,
        local_workspace_path: Path,
    ) -> OfficialTemplateRoot:
        """Resolve a real template only for an operation that will generate files."""
        workspace_root = self._settings.local_workspace_root
        candidates = [self._settings.template_path, retained_template_path]
        errors: list[str] = []
        for candidate in dict.fromkeys(path for path in candidates if path is not None):
            if (
                candidate.is_relative_to(local_workspace_path)
                or workspace_root is not None
                and candidate.is_relative_to(workspace_root)
            ):
                errors.append(
                    "Template source cannot be inside the configured project workspace root."
                )
                continue
            try:
                return resolve_official_template_root(candidate)
            except OfficialWorkspaceError as exc:
                errors.append(str(exc))
        detail = errors[0] if errors else "Template folder is not configured."
        raise OfficialWorkspaceCreateError(detail)

    def adopt_existing(self, project_id: str) -> OfficialWorkspaceCreateResult:
        """Link an existing same-project workspace without touching business content."""
        preview = self.preview(project_id)
        ProjectLifecycleWriteGuard(self._projects).require_write_allowed(
            project_id, LifecycleWriteOperation.REQUIRED_FORMS_GENERATE
        )
        if preview.status == "completed":
            record = self._workspaces.get_by_project(project_id)
            if record is None:
                raise OfficialWorkspaceCreateError("Local project workspace record is missing.")
            return OfficialWorkspaceCreateResult(record, tuple(), preview.warnings)
        if preview.status != "adoptable":
            detail = preview.blockers[0] if preview.blockers else preview.status
            raise OfficialWorkspaceCreateError(
                f"Existing project folder cannot be linked: {detail}"
            )
        assert preview.dl_number is not None
        assert preview.local_workspace_root is not None
        assert preview.local_workspace_path is not None
        assert preview.source_book_path is not None
        assert preview.official_folder_path is not None
        assert preview.manifest_path is not None
        assert preview.template_path is not None
        if not preview.local_workspace_path.is_dir():
            raise OfficialWorkspaceCreateError("Existing local project workspace is missing.")
        if not preview.source_book_path.is_dir():
            raise OfficialWorkspaceCreateError("Existing Source Book folder is missing.")
        if not preview.official_folder_path.is_dir():
            raise OfficialWorkspaceCreateError("Existing official project folder is missing.")
        redirected = self._manifests.first_redirected_path(
            preview.local_workspace_root,
            preview.local_workspace_path,
            preview.source_book_path,
            preview.official_folder_path,
            preview.manifest_path.parent,
            preview.manifest_path,
        )
        if redirected is not None:
            raise OfficialWorkspaceCreateError(
                f"Project workspace identity cannot be linked through a symbolic link or junction: {redirected}"
            )
        now = datetime.now(UTC).replace(microsecond=0).isoformat()
        record = OfficialWorkspaceRecord(
            workspace_id=uuid4().hex,
            project_id=project_id,
            dl_number=preview.dl_number,
            local_workspace_path=preview.local_workspace_path,
            source_book_path=preview.source_book_path,
            official_folder_path=preview.official_folder_path,
            manifest_path=preview.manifest_path,
            template_source_path=preview.template_path,
            created_at=now,
        )
        existed = preview.manifest_path.exists()
        try:
            self._manifests.write_adoption(
                preview.manifest_path,
                OfficialWorkspaceManifest(
                    schema_version=1,
                    project_id=record.project_id,
                    dl_number=record.dl_number,
                    local_workspace_path=str(record.local_workspace_path),
                    source_book_path=str(record.source_book_path),
                    official_project_folder_path=str(record.official_folder_path),
                    template_source_path=str(record.template_source_path),
                    created_at=record.created_at,
                ),
            )
            saved = self._workspaces.save(record)
        except Exception as exc:
            raise OfficialWorkspaceCreateError(str(exc)) from exc
        return OfficialWorkspaceCreateResult(
            record=saved,
            created_paths=tuple() if existed else (preview.manifest_path,),
            warnings=preview.warnings,
        )

    def _get_project(self, project_id: str) -> Project:
        """Load a project or raise a not-found error."""
        project = self._projects.get(project_id)
        if project is None:
            raise OfficialWorkspaceNotFoundError(f"Project not found: {project_id}")
        return project

    def _latest_requested_testing(self, project_id: str) -> str | None:
        """Return the latest requested testing description for official folder naming."""
        if self._forms is None:
            return None
        forms = self._forms.list_by_project(project_id)
        for form in reversed(forms):
            requested_testing = _clean_text(form.requested_testing)
            if requested_testing:
                return requested_testing
        return None

    def _read_manifest_identity(
        self,
        *,
        manifest_path: Path,
        project_id: str,
        dl_number: str,
    ) -> tuple[dict[str, object] | None, str | None]:
        """Read only portable identity fields; never authorize a manifest absolute path."""
        if not manifest_path.exists():
            return None, None
        try:
            payload = self._manifests.read(manifest_path)
        except Exception:
            return None, (
                "Workspace manifest does not match current project or cannot be read: "
                f"{manifest_path}"
            )
        if not isinstance(payload, dict):
            return None, (
                "Workspace manifest does not match current project or cannot be read: "
                f"{manifest_path}"
            )
        if payload.get("project_id") != project_id:
            return None, f"Workspace manifest does not match current project: {manifest_path}"
        manifest_dl = payload.get("dl_number")
        if manifest_dl not in {None, "", dl_number}:
            return None, f"Workspace manifest does not match current DL number: {manifest_path}"
        return payload, None

    def _workspace_record_inconsistency(
        self,
        record: OfficialWorkspaceRecord,
        *,
        project_id: str,
        dl_number: str,
    ) -> str | None:
        """Return a repairable inconsistency when an existing workspace record is broken."""
        if record.project_id != project_id:
            return "Local project workspace record does not match current project."
        if record.dl_number != dl_number:
            return "Local project workspace record does not match current DL number."
        local_root = self._settings.local_workspace_root
        if (
            local_root is None
            or record.local_workspace_path == local_root
            or not record.local_workspace_path.is_relative_to(local_root)
        ):
            return "Local project workspace record is outside the configured workspace root."
        if record.source_book_path != record.local_workspace_path / "Source Book":
            return "Local project workspace record has an invalid Source Book path."
        if record.official_folder_path.parent != record.local_workspace_path:
            return "Local project workspace record has an invalid official folder path."
        if record.manifest_path != record.local_workspace_path / ".connlab" / "manifest.json":
            return "Local project workspace record has an invalid manifest path."
        redirected = self._manifests.first_redirected_path(
            local_root,
            record.local_workspace_path,
            record.source_book_path,
            record.official_folder_path,
            record.manifest_path.parent,
            record.manifest_path,
        )
        if redirected is not None:
            return (
                "Local project workspace record cannot use a symbolic link or junction: "
                f"{redirected}"
            )
        if not record.local_workspace_path.is_dir():
            return f"Local project workspace path is missing: {record.local_workspace_path}"
        if not record.source_book_path.is_dir():
            return f"Source Book folder is missing: {record.source_book_path}"
        if not record.official_folder_path.is_dir():
            return f"Official project folder is missing: {record.official_folder_path}"
        if not record.manifest_path.is_file():
            return f"Workspace manifest is missing: {record.manifest_path}"
        return self._manifest_inconsistency(
            manifest_path=record.manifest_path,
            project_id=project_id,
            official_folder_path=record.official_folder_path,
        )

    def _manifest_inconsistency(
        self,
        *,
        manifest_path: Path,
        project_id: str,
        official_folder_path: Path,
    ) -> str | None:
        """Return a repairable inconsistency message when manifest state conflicts."""
        if not manifest_path.exists():
            return None
        try:
            payload = self._manifests.read(manifest_path)
        except Exception:
            return f"Workspace manifest does not match current project or cannot be read: {manifest_path}"
        if not isinstance(payload, dict):
            return f"Workspace manifest does not match current project or cannot be read: {manifest_path}"
        if payload.get("project_id") != project_id:
            return f"Workspace manifest does not match current project: {manifest_path}"
        if payload.get("official_project_folder_path") != str(official_folder_path):
            return f"Workspace manifest does not match planned official folder: {manifest_path}"
        return None


def resolve_official_template_root(path: Path) -> OfficialTemplateRoot:
    """Resolve configured template path to exactly one official project template root."""
    if not path.exists():
        raise OfficialWorkspaceError(f"Template folder does not exist: {path}")
    if not path.is_dir():
        raise OfficialWorkspaceError(f"Template folder is not a folder: {path}")
    if _looks_like_template_root(path):
        return OfficialTemplateRoot(path=path, mode="template_root")
    candidates = _template_root_candidates(path)
    if len(candidates) == 1:
        mode = "single_child_template_root"
        if candidates[0].parent.parent == path:
            mode = "workspace_template_child_root"
        return OfficialTemplateRoot(path=candidates[0], mode=mode)
    raise OfficialWorkspaceError(
        "Choose the official project folder template root; configured path does not contain exactly one template."
    )


def _template_root_candidates(path: Path) -> list[Path]:
    """Return immediate or workspace-template child roots that match the official folder structure."""
    candidates: list[Path] = []
    for child in path.iterdir():
        if not child.is_dir():
            continue
        if _looks_like_template_root(child):
            candidates.append(child)
            continue
        for grandchild in child.iterdir():
            if grandchild.is_dir() and _looks_like_template_root(grandchild):
                candidates.append(grandchild)
    return candidates


def _looks_like_template_root(path: Path) -> bool:
    """Return whether a folder contains the required official project structure."""
    return all((path / required).is_dir() for required in REQUIRED_TEMPLATE_PATHS)


def _copytree_no_overwrite(source: Path, target: Path) -> None:
    """Copy a directory tree and fail if the target exists."""
    shutil.copytree(source, target)


def merge_missing_workspace_tree(source: Path, target: Path) -> None:
    """Add missing template entries without replacing operator-owned content."""
    if source.is_symlink() or target.is_symlink():
        raise OfficialWorkspaceCreateError(
            "Project folder templates and targets cannot be symbolic links."
        )
    target.mkdir(parents=True, exist_ok=True)
    for source_path in sorted(source.rglob("*")):
        if source_path.is_symlink():
            raise OfficialWorkspaceCreateError("Project folder template contains a symbolic link.")
        destination = target / source_path.relative_to(source)
        if source_path.is_dir():
            if destination.exists() and not destination.is_dir():
                raise OfficialWorkspaceCreateError(
                    f"Existing project content conflicts with a required folder: {destination}"
                )
            destination.mkdir(parents=True, exist_ok=True)
            continue
        if destination.exists():
            if not destination.is_file():
                raise OfficialWorkspaceCreateError(
                    f"Existing project content conflicts with a required file: {destination}"
                )
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            with (
                source_path.open("rb") as source_handle,
                destination.open("xb") as target_handle,
            ):
                shutil.copyfileobj(source_handle, target_handle)
        except FileExistsError:
            if not destination.is_file():
                raise OfficialWorkspaceCreateError(
                    f"Existing project content conflicts with a required file: {destination}"
                )


def _conflict_options() -> tuple[OfficialWorkspaceConflictOption, ...]:
    """Return the operator choices for an existing official project folder."""
    return (
        OfficialWorkspaceConflictOption(
            key="backup_and_recreate",
            label="Backup and Rebuild",
            description="Move the existing project folder to a timestamped backup, then create a fresh folder.",
        ),
    )


def _resolve_existing_path(
    *,
    existing_path: Path,
    conflict_strategy: str,
    operation_tmp: Path,
) -> OfficialWorkspaceConflictResolution:
    """Move an existing project path according to an explicit strategy."""
    if conflict_strategy == "backup_and_recreate":
        backup_path = _unique_backup_path(existing_path)
        shutil.move(str(existing_path), str(backup_path))
        return OfficialWorkspaceConflictResolution(
            created_paths=(backup_path,),
            restore_path=None,
            restore_target=None,
        )
    if conflict_strategy == "overwrite_rebuild":
        old_path = operation_tmp / f"overwrite-old-{existing_path.name}"
        shutil.move(str(existing_path), str(old_path))
        return OfficialWorkspaceConflictResolution(
            created_paths=tuple(),
            restore_path=old_path,
            restore_target=existing_path,
        )
    raise OfficialWorkspaceCreateError(f"Unsupported project folder conflict strategy: {conflict_strategy}")


def _restore_overwrite_source(restore_path: Path | None, restore_target: Path | None) -> None:
    """Restore an overwritten source path after a failed staged replacement."""
    if restore_path is None or restore_target is None or not restore_path.exists():
        return
    if restore_target.exists():
        return
    shutil.move(str(restore_path), str(restore_target))


def _workspace_has_business_content(workspace_path: Path) -> bool:
    """Return whether an existing LTR workspace contains operator-created content."""
    ignored_names = {".connlab"}
    return any(child.name not in ignored_names for child in workspace_path.iterdir())


def _portable_official_folder_path(
    workspace_path: Path,
    manifest: dict[str, object],
) -> Path | None:
    """Rebind only a manifest folder leaf under the current configured workspace."""
    raw_path = manifest.get("official_project_folder_path")
    if not isinstance(raw_path, str) or not raw_path.strip():
        return None
    folder_name = Path(raw_path).name
    if folder_name in {"", ".", ".."}:
        return None
    candidate = workspace_path / folder_name
    try:
        candidate.relative_to(workspace_path)
    except ValueError:
        return None
    return candidate


def _adoption_template_metadata(
    manifest: dict[str, object] | None,
    configured_template: Path | None,
    official_folder_path: Path,
) -> Path:
    """Retain template provenance without requiring that source to be reachable."""
    if manifest is not None:
        retained = manifest.get("template_source_path")
        if isinstance(retained, str) and retained.strip():
            return Path(retained)
    if configured_template is not None:
        return configured_template
    # Legacy folders may predate template provenance. The adopted official folder
    # is retained as the only defensible source metadata; generation still resolves
    # and validates a configured template before it can mutate this workspace.
    return official_folder_path


def _unique_backup_path(existing_path: Path) -> Path:
    """Return a timestamped sibling backup path that does not already exist."""
    timestamp = datetime.fromtimestamp(existing_path.stat().st_mtime).strftime("%Y%m%d%H%M%S")
    base = existing_path.with_name(f"{existing_path.name} {timestamp}")
    if not base.exists() and not base.is_symlink():
        return base
    for index in range(1, 1000):
        candidate = existing_path.with_name(f"{base.name}-{index}")
        if not candidate.exists() and not candidate.is_symlink():
            return candidate
    raise OfficialWorkspaceCreateError("Unable to create a unique backup folder name.")


def _clean_text(value: str | None) -> str | None:
    """Return a stripped non-empty string or None."""
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _blocked_preview(
    project_id: str,
    dl_number: str | None,
    local_root: Path | None,
    template_root: OfficialTemplateRoot | None,
    blockers: list[str],
    warnings: list[str],
) -> OfficialWorkspacePreview:
    """Build a blocked preview for late validation failures."""
    return OfficialWorkspacePreview(
        project_id=project_id,
        dl_number=dl_number,
        local_workspace_root=local_root,
        local_workspace_path=None,
        source_book_path=None,
        template_path=template_root.path if template_root else None,
        official_folder_path=None,
        manifest_path=None,
        template_root_mode=template_root.mode if template_root else None,
        status="blocked",
        blockers=tuple(blockers),
        warnings=tuple(warnings),
        planned_paths=tuple(),
    )
