"""Application service for project folder preview and generation."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from backend.application.project_lifecycle_service import LifecycleOperation
from backend.domain import (
    FileAsset,
    FileAssetType,
    Project,
    ProjectFolderRecord,
    ProjectStatus,
)
from backend.modules.folder import FolderGenerationResult, FolderPlan, FolderTemplateService


class FolderError(ValueError):
    """Base error for folder workflow failures."""


class FolderNotFoundError(LookupError):
    """Raised when folder workflow input records are missing."""


class FolderConflictError(FolderError):
    """Raised when safe generation would overwrite existing content."""


class ProjectRepositoryPort(Protocol):
    """Project repository operations required by folder service."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by ID."""

    def update(self, project: Project) -> Project:
        """Update a project."""


class ProjectFolderRecordRepositoryPort(Protocol):
    """Project folder record repository operations."""

    def create(self, folder: ProjectFolderRecord) -> ProjectFolderRecord:
        """Persist a project folder record."""

    def list_by_project(self, project_id: str) -> list[ProjectFolderRecord]:
        """Return folder records for a project."""


class FileAssetRepositoryPort(Protocol):
    """File asset repository operations required by folder service."""

    def list_by_project(self, project_id: str) -> list[FileAsset]:
        """Return file assets for a project."""


class ProjectLifecycleGuardPort(Protocol):
    """Lifecycle guard behavior required by folder service."""

    def require_allowed(
        self,
        project_id: str,
        operation: LifecycleOperation,
    ) -> None:
        """Raise when an operation is not allowed."""


@dataclass(frozen=True, slots=True)
class FolderCommand:
    """Input command for folder preview/generation."""

    template_path: Path
    target_root: Path
    dl_number: str | None = None
    plan_date: date | None = None


@dataclass(frozen=True, slots=True)
class FolderGenerationRecord:
    """Generated folder result and persisted record."""

    result: FolderGenerationResult
    record: ProjectFolderRecord


class FolderService:
    """Coordinate folder preview and safe generation use cases."""

    def __init__(
        self,
        project_repository: ProjectRepositoryPort,
        folder_repository: ProjectFolderRecordRepositoryPort,
        file_asset_repository: FileAssetRepositoryPort,
        lifecycle_guard: ProjectLifecycleGuardPort | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """Create a folder service."""
        self._projects = project_repository
        self._folders = folder_repository
        self._assets = file_asset_repository
        self._lifecycle = lifecycle_guard
        self._templates = FolderTemplateService()
        self._logger = logger or logging.getLogger("connlab.folder")

    def preview_folder(self, project_id: str, command: FolderCommand) -> FolderPlan:
        """Return a folder generation preview plan."""
        if self._lifecycle is not None:
            self._lifecycle.require_allowed(project_id, LifecycleOperation.FOLDER_PREVIEW)
        project = self._get_project(project_id)
        return self._templates.preview(
            project=project,
            template_path=command.template_path,
            target_root=command.target_root,
            dl_number=command.dl_number,
            plan_date=command.plan_date,
        )

    def generate_folder(self, project_id: str, command: FolderCommand) -> FolderGenerationRecord:
        """Generate project folders from a safe preview plan."""
        if self._lifecycle is not None:
            self._lifecycle.require_allowed(project_id, LifecycleOperation.FOLDER_GENERATE)
        project = self._get_project(project_id)
        plan = self.preview_folder(project_id, command)
        if plan.conflict or any(item.conflict for item in plan.items):
            raise FolderConflictError(f"Target folder already exists: {plan.project_folder_path}")
        asset = self._latest_application_form_asset(project_id)
        result = self._templates.generate(plan, application_form_asset=asset)
        record = ProjectFolderRecord(
            folder_id=uuid4().hex,
            project_id=project.project_id,
            folder_path=result.project_folder_path,
            created_on=date.today(),
        )
        self._folders.create(record)
        self._projects.update(project.with_status(ProjectStatus.FOLDER_CREATED))
        self._logger.info("Generated project folder at %s", result.project_folder_path)
        return FolderGenerationRecord(result=result, record=record)

    def latest_folder(self, project_id: str) -> ProjectFolderRecord:
        """Return the latest generated folder record for a project."""
        self._get_project(project_id)
        folders = self._folders.list_by_project(project_id)
        if not folders:
            raise FolderNotFoundError(
                f"Project folder record not found for project: {project_id}"
            )
        return max(
            folders,
            key=lambda folder: (folder.created_on or date.min, folder.folder_id),
        )

    def _get_project(self, project_id: str) -> Project:
        """Load a project or raise not found."""
        project = self._projects.get(project_id)
        if project is None:
            raise FolderNotFoundError(f"Project not found: {project_id}")
        return project

    def _latest_application_form_asset(self, project_id: str) -> FileAsset | None:
        """Return the latest application form asset for a project."""
        assets = [
            asset
            for asset in self._assets.list_by_project(project_id)
            if asset.asset_type is FileAssetType.APPLICATION_FORM
        ]
        return assets[-1] if assets else None
