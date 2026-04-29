"""Application service for safe project evidence placement."""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from backend.application.project_lifecycle_service import LifecycleOperation
from backend.domain import FileAsset, Project, ProjectFolderRecord
from backend.modules.folder import (
    EvidencePlacementItem,
    EvidencePlacementPlan,
    EvidencePlacementPlanner,
)


class EvidencePlacementError(ValueError):
    """Base error for evidence placement failures."""


class EvidencePlacementNotFoundError(LookupError):
    """Raised when required project or folder records are missing."""


class EvidencePlacementConflictError(EvidencePlacementError):
    """Raised when planned copy operations are not safe to execute."""


class ProjectRepositoryPort(Protocol):
    """Project repository operations required by evidence placement."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by ID."""


class ProjectFolderRecordRepositoryPort(Protocol):
    """Project folder record repository operations required by evidence placement."""

    def list_by_project(self, project_id: str) -> list[ProjectFolderRecord]:
        """Return generated folder records for a project."""


class FileAssetRepositoryPort(Protocol):
    """File asset repository operations required by evidence placement."""

    def list_by_project(self, project_id: str) -> list[FileAsset]:
        """Return project file assets."""


class ProjectLifecycleGuardPort(Protocol):
    """Lifecycle guard behavior required by evidence placement."""

    def require_allowed(
        self,
        project_id: str,
        operation: LifecycleOperation,
    ) -> None:
        """Raise when an operation is not allowed."""


@dataclass(frozen=True, slots=True)
class EvidencePlacementResult:
    """Result of safely copying evidence into a project folder."""

    plan: EvidencePlacementPlan
    copied_paths: tuple[Path, ...]


class EvidencePlacementService:
    """Coordinate evidence placement preview and safe copy execution."""

    def __init__(
        self,
        project_repository: ProjectRepositoryPort,
        folder_repository: ProjectFolderRecordRepositoryPort,
        file_asset_repository: FileAssetRepositoryPort,
        planner: EvidencePlacementPlanner | None = None,
        lifecycle_guard: ProjectLifecycleGuardPort | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """Create an evidence placement service."""
        self._projects = project_repository
        self._folders = folder_repository
        self._assets = file_asset_repository
        self._planner = planner or EvidencePlacementPlanner()
        self._lifecycle = lifecycle_guard
        self._logger = logger or logging.getLogger("connlab.evidence")

    def preview_project(self, project_id: str) -> EvidencePlacementPlan:
        """Return the evidence placement preview for a project."""
        if self._lifecycle is not None:
            self._lifecycle.require_allowed(project_id, LifecycleOperation.EVIDENCE_PREVIEW)
        project = self._get_project(project_id)
        folder = self._latest_folder(project.project_id)
        assets = self._assets.list_by_project(project.project_id)
        return self._planner.preview(
            project_id=project.project_id,
            project_folder_path=folder.folder_path,
            assets=assets,
        )

    def place_project(self, project_id: str) -> EvidencePlacementResult:
        """Copy project evidence according to a safe preview plan."""
        if self._lifecycle is not None:
            self._lifecycle.require_allowed(project_id, LifecycleOperation.EVIDENCE_PLACE)
        plan = self.preview_project(project_id)
        conflicts = self._conflict_messages(plan)
        if conflicts:
            raise EvidencePlacementConflictError("; ".join(conflicts))
        copied_paths = tuple(self._copy_item(item) for item in plan.items)
        self._logger.info(
            "Placed %s evidence files for project %s",
            len(copied_paths),
            project_id,
        )
        return EvidencePlacementResult(plan=plan, copied_paths=copied_paths)

    def _get_project(self, project_id: str) -> Project:
        """Load a project or raise not found."""
        project = self._projects.get(project_id)
        if project is None:
            raise EvidencePlacementNotFoundError(f"Project not found: {project_id}")
        return project

    def _latest_folder(self, project_id: str) -> ProjectFolderRecord:
        """Return the latest generated folder record for a project."""
        folders = self._folders.list_by_project(project_id)
        if not folders:
            raise EvidencePlacementNotFoundError(
                f"Project folder record not found for project: {project_id}"
            )
        return folders[-1]

    def _conflict_messages(self, plan: EvidencePlacementPlan) -> list[str]:
        """Return blocking conflict messages for a placement plan."""
        messages = list(plan.conflicts)
        for item in plan.items:
            if item.missing_source:
                messages.append(f"Missing source file: {item.source_path}")
            if item.target_exists:
                messages.append(f"Target already exists: {item.target_path}")
            if item.duplicate_target:
                messages.append(f"Duplicate target in placement plan: {item.target_path}")
        return messages

    def _copy_item(self, item: EvidencePlacementItem) -> Path:
        """Copy one file or directory without overwriting."""
        if item.target_path.exists():
            raise EvidencePlacementConflictError(
                f"Target already exists: {item.target_path}"
            )
        item.target_path.parent.mkdir(parents=True, exist_ok=True)
        if item.source_path.is_dir():
            shutil.copytree(item.source_path, item.target_path)
        else:
            shutil.copy2(item.source_path, item.target_path)
        return item.target_path
