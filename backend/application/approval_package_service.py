"""Application service for approval package preview and placement."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from backend.application.project_lifecycle_service import (
    LifecycleOperation,
    ProjectLifecycleService,
)
from backend.domain import Project


class ApprovalPackageError(ValueError):
    """Raised when approval package input or state is invalid."""


class ApprovalPackageNotFoundError(LookupError):
    """Raised when project or required files cannot be found."""


class ApprovalPackageConflictError(ApprovalPackageError):
    """Raised when preview detects copy conflicts."""


class ProjectRepositoryPort(Protocol):
    """Project repository operations required by approval package service."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by id."""


@dataclass(frozen=True, slots=True)
class ApprovalPackageCommand:
    """Input for approval-package preview and execute workflow."""

    project_id: str
    project_folder_path: Path
    completed_application_form_path: Path
    test_record_output_path: Path
    fee_evaluation_output_path: Path | None = None
    evidence_source_paths: tuple[Path, ...] = ()
    overwrite: bool = False


@dataclass(frozen=True, slots=True)
class ApprovalPackageItem:
    """One planned approval-package item."""

    source_path: Path
    target_relative_path: Path
    target_path: Path
    classification: str
    status: str
    warnings: tuple[str, ...] = ()

    @property
    def blocked(self) -> bool:
        """Return whether the item blocks execution."""
        return self.status in {"missing_source", "target_exists"}


@dataclass(frozen=True, slots=True)
class ApprovalPackageResult:
    """Preview or execution result for approval package placement."""

    project_id: str
    project_folder_path: Path
    mode: str
    items: tuple[ApprovalPackageItem, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]


class ApprovalPackageService:
    """Build and execute approval-package placement for one project."""

    def __init__(
        self,
        project_repository: ProjectRepositoryPort,
        lifecycle_guard: ProjectLifecycleService | None = None,
    ) -> None:
        """Create service with required repositories and optional lifecycle guard."""
        self._projects = project_repository
        self._lifecycle = lifecycle_guard

    def preview(self, command: ApprovalPackageCommand) -> ApprovalPackageResult:
        """Return a read-only approval package plan without copying files."""
        if self._lifecycle is not None:
            self._lifecycle.require_allowed(
                command.project_id,
                LifecycleOperation.EVIDENCE_PREVIEW,
            )
        self._require_project(command.project_id)
        project_folder = _require_directory(command.project_folder_path, "Project folder")
        items, warnings = _build_items(command, project_folder)
        blockers = tuple(_collect_blockers(items))
        return ApprovalPackageResult(
            project_id=command.project_id,
            project_folder_path=project_folder,
            mode="preview",
            items=tuple(items),
            warnings=tuple(warnings),
            blockers=blockers,
        )

    def execute(self, command: ApprovalPackageCommand) -> ApprovalPackageResult:
        """Copy files according to approval package plan when no blockers exist."""
        if self._lifecycle is not None:
            self._lifecycle.require_allowed(
                command.project_id,
                LifecycleOperation.EVIDENCE_PLACE,
            )
        preview = self.preview(command)
        if preview.blockers:
            raise ApprovalPackageConflictError("; ".join(preview.blockers))
        copied: list[ApprovalPackageItem] = []
        for item in preview.items:
            if item.status == "already_in_place":
                copied.append(item)
                continue
            item.target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item.source_path, item.target_path)
            copied.append(
                ApprovalPackageItem(
                    source_path=item.source_path,
                    target_relative_path=item.target_relative_path,
                    target_path=item.target_path,
                    classification=item.classification,
                    status="copied",
                    warnings=item.warnings,
                )
            )
        return ApprovalPackageResult(
            project_id=preview.project_id,
            project_folder_path=preview.project_folder_path,
            mode="execute",
            items=tuple(copied),
            warnings=preview.warnings,
            blockers=(),
        )

    def _require_project(self, project_id: str) -> Project:
        """Load project or raise not found."""
        project = self._projects.get(project_id)
        if project is None:
            raise ApprovalPackageNotFoundError(f"Project not found: {project_id}")
        return project


def _build_items(
    command: ApprovalPackageCommand,
    project_folder: Path,
) -> tuple[list[ApprovalPackageItem], list[str]]:
    """Build deterministic approval package plan items."""
    submitted = project_folder / "Submitted Material"
    email_dir = project_folder / "E-mail"
    warnings: list[str] = []
    items: list[ApprovalPackageItem] = []
    seen_targets: set[Path] = set()

    required = (
        ("application_form", command.completed_application_form_path, submitted),
        ("test_record", command.test_record_output_path, submitted),
    )
    optional = (
        ("fee_evaluation", command.fee_evaluation_output_path, submitted),
    )
    for classification, source, target_dir in required:
        items.append(
            _build_item(
                source_path=source,
                target_dir=target_dir,
                project_folder=project_folder,
                classification=classification,
                overwrite=command.overwrite,
                seen_targets=seen_targets,
            )
        )
    for classification, source, target_dir in optional:
        if source is None:
            warnings.append(
                "Fee evaluation output path is not provided; fee file is skipped."
            )
            continue
        items.append(
            _build_item(
                source_path=source,
                target_dir=target_dir,
                project_folder=project_folder,
                classification=classification,
                overwrite=command.overwrite,
                seen_targets=seen_targets,
            )
        )

    for source in command.evidence_source_paths:
        target_dir = email_dir if source.suffix.lower() == ".msg" else submitted
        classification = "email" if source.suffix.lower() == ".msg" else "submitted_material"
        items.append(
            _build_item(
                source_path=source,
                target_dir=target_dir,
                project_folder=project_folder,
                classification=classification,
                overwrite=command.overwrite,
                seen_targets=seen_targets,
            )
        )
    return items, warnings


def _build_item(
    *,
    source_path: Path,
    target_dir: Path,
    project_folder: Path,
    classification: str,
    overwrite: bool,
    seen_targets: set[Path],
) -> ApprovalPackageItem:
    """Build one item with source/target conflict status."""
    source = Path(source_path)
    target = target_dir / source.name
    relative = target.relative_to(project_folder)
    warnings: list[str] = []
    if not source.exists():
        status = "missing_source"
        warnings.append(f"Source file does not exist: {source}")
    elif source.resolve() == target.resolve():
        status = "already_in_place"
    elif target in seen_targets:
        status = "target_exists"
        warnings.append(f"Duplicate target in approval package plan: {target}")
    elif target.exists() and not overwrite:
        status = "target_exists"
        warnings.append(f"Target already exists and overwrite is false: {target}")
    else:
        status = "planned"
    seen_targets.add(target)
    return ApprovalPackageItem(
        source_path=source,
        target_relative_path=relative,
        target_path=target,
        classification=classification,
        status=status,
        warnings=tuple(warnings),
    )


def _collect_blockers(items: list[ApprovalPackageItem]) -> list[str]:
    """Collect all blocker messages from item statuses."""
    blockers: list[str] = []
    for item in items:
        if item.status == "missing_source":
            blockers.append(f"Missing source file: {item.source_path}")
        elif item.status == "target_exists":
            blockers.append(f"Target conflict: {item.target_path}")
    return blockers


def _require_directory(path: Path, label: str) -> Path:
    """Require an existing directory for a command path."""
    directory = Path(path)
    if not directory.exists() or not directory.is_dir():
        raise ApprovalPackageNotFoundError(f"{label} does not exist: {directory}")
    return directory

