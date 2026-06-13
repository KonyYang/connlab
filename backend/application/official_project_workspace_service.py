"""Application service for local official project workspace creation."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from backend.application.official_project_workspace_naming import (
    OfficialWorkspaceNamingError,
    build_official_project_folder_name,
)
from backend.application.project_identity import resolve_project_identity
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
    ) -> None:
        """Create the workspace service."""
        self._projects = project_repository
        self._workspaces = workspace_repository
        self._ltrs = ltr_repository
        self._forms = application_form_repository
        self._settings = settings
        self._manifests = manifest_gateway or OfficialWorkspaceManifestGateway()

    def preview(self, project_id: str) -> OfficialWorkspacePreview:
        """Return a safe preview for local official project workspace creation."""
        project = self._get_project(project_id)
        ltrs = self._ltrs.list_by_project(project.project_id) if self._ltrs else []
        identity = resolve_project_identity(project, ltrs)
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
        if template_setting is None:
            blockers.append("Template folder is not configured.")
        if self._settings.public_drive_root is None:
            warnings.append("Public Project locations is not configured; upload readiness will be checked later.")
        elif not self._settings.public_drive_root.is_dir():
            warnings.append(
                f"Public Project locations is not available; local workspace can still be created: "
                f"{self._settings.public_drive_root}"
            )

        template_root: OfficialTemplateRoot | None = None
        if template_setting is not None:
            try:
                template_root = resolve_official_template_root(template_setting)
            except OfficialWorkspaceError as exc:
                blockers.append(str(exc))

        if blockers or not dl_number or local_root is None or template_root is None:
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
        planned_paths = (workspace_path, source_book_path, official_folder_path, manifest_path)

        completed_record = self._workspaces.get_by_project(project_id)
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
                    template_root_mode=template_root.mode,
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
            return OfficialWorkspacePreview(
                project_id=project_id,
                dl_number=dl_number,
                local_workspace_root=local_root,
                local_workspace_path=completed_record.local_workspace_path,
                source_book_path=completed_record.source_book_path,
                template_path=completed_record.template_source_path,
                official_folder_path=completed_record.official_folder_path,
                manifest_path=completed_record.manifest_path,
                template_root_mode=template_root.mode,
                status="inconsistent",
                blockers=(record_inconsistency,),
                warnings=tuple(record_warnings),
                planned_paths=planned_paths,
            )

        manifest_inconsistency = self._manifest_without_record_inconsistency(
            project_id=project_id,
            official_folder_path=official_folder_path,
            manifest_path=manifest_path,
        )
        if manifest_inconsistency:
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
                status="inconsistent",
                blockers=(manifest_inconsistency,),
                warnings=tuple(warnings),
                planned_paths=planned_paths,
            )

        inconsistency = self._manifest_inconsistency(
            manifest_path=manifest_path,
            project_id=project_id,
            official_folder_path=official_folder_path,
        )
        if inconsistency:
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
                status="inconsistent",
                blockers=(inconsistency,),
                warnings=tuple(warnings),
                planned_paths=planned_paths,
            )

        if official_folder_path.exists():
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
                status="exists",
                blockers=(f"Official project folder already exists: {official_folder_path}",),
                warnings=tuple(warnings),
                planned_paths=planned_paths,
            )

        status = "ready"
        if workspace_path.exists():
            status = "adoptable"
            warnings.append("Local project workspace already exists and can be continued.")

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

    def create(self, project_id: str) -> OfficialWorkspaceCreateResult:
        """Create or continue the local official project workspace."""
        preview = self.preview(project_id)
        if preview.status == "completed":
            record = self._workspaces.get_by_project(project_id)
            if record is None:
                raise OfficialWorkspaceCreateError("Local project workspace record is missing.")
            return OfficialWorkspaceCreateResult(
                record=record,
                created_paths=tuple(),
                warnings=preview.warnings,
            )
        if preview.status not in {"ready", "adoptable"}:
            detail = preview.blockers[0] if preview.blockers else preview.status
            raise OfficialWorkspaceCreateError(detail)
        assert preview.dl_number is not None
        assert preview.local_workspace_path is not None
        assert preview.source_book_path is not None
        assert preview.template_path is not None
        assert preview.official_folder_path is not None
        assert preview.manifest_path is not None

        created_paths: list[Path] = []
        workspace_path = preview.local_workspace_path
        source_book_path = preview.source_book_path
        tmp_root = workspace_path / ".connlab" / "tmp"
        operation_tmp = tmp_root / f"create-official-folder-{uuid4().hex}"
        copied_root = operation_tmp / preview.template_path.name
        try:
            if not workspace_path.exists():
                workspace_path.mkdir(parents=True)
                created_paths.append(workspace_path)
            if not source_book_path.exists():
                source_book_path.mkdir(parents=True)
                created_paths.append(source_book_path)
            operation_tmp.mkdir(parents=True)
            _copytree_no_overwrite(preview.template_path, copied_root)
            copied_root.replace(preview.official_folder_path)
            created_paths.append(preview.official_folder_path)
        except Exception as exc:
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
        self._manifests.write(
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
        return OfficialWorkspaceCreateResult(
            record=saved,
            created_paths=tuple(created_paths),
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

    def _manifest_without_record_inconsistency(
        self,
        *,
        project_id: str,
        official_folder_path: Path,
        manifest_path: Path,
    ) -> str | None:
        """Return a repairable inconsistency when a manifest exists without SQLite index."""
        if not manifest_path.exists():
            return None
        inconsistency = self._manifest_inconsistency(
            manifest_path=manifest_path,
            project_id=project_id,
            official_folder_path=official_folder_path,
        )
        if inconsistency:
            return inconsistency
        return (
            "Workspace manifest exists but ConnLab workspace index record is missing: "
            f"{manifest_path}"
        )

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
