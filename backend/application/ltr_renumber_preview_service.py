"""Application service for non-destructive LTR renumber preview."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from backend.domain import FileAsset, LtrRecord, Project, ProjectFolderRecord
from backend.modules.ltr import LtrNumberError, parse_ltr_number, validate_new_registration_number


class LtrRenumberPreviewError(ValueError):
    """Raised when an LTR renumber preview request is invalid."""


class LtrRenumberPreviewNotFoundError(LookupError):
    """Raised when preview input records cannot be found."""


@dataclass(frozen=True, slots=True)
class PreviewLtrRenumberCommand:
    """Input for previewing an LTR renumber impact plan."""

    old_ltr_number: str
    new_ltr_number: str
    reason: str
    operator_confirmed: bool = False


@dataclass(frozen=True, slots=True)
class RenameImpact:
    """One projected path rename impact."""

    record_type: str
    record_id: str
    current_path: Path
    target_path: Path
    target_exists: bool
    rename_required: bool


@dataclass(frozen=True, slots=True)
class LtrRenumberPreview:
    """Non-destructive preview of LTR renumber impacts."""

    project_id: str
    old_ltr_number: str
    new_ltr_number: str
    reason: str
    operator_confirmation_required: bool
    operator_confirmed: bool
    ltr_record_id: str
    impacts: tuple[RenameImpact, ...]
    conflicts: tuple[str, ...]
    warnings: tuple[str, ...]
    audit_summary: str


class ProjectRepositoryPort(Protocol):
    """Project repository behavior required by renumber preview."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by ID."""


class LtrRepositoryPort(Protocol):
    """LTR repository behavior required by renumber preview."""

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        """Return LTR records for a project."""

    def search(self, query: str) -> list[LtrRecord]:
        """Search LTR records."""


class ProjectFolderRecordRepositoryPort(Protocol):
    """Project folder repository behavior required by renumber preview."""

    def list_by_project(self, project_id: str) -> list[ProjectFolderRecord]:
        """Return project folder records."""


class FileAssetRepositoryPort(Protocol):
    """File asset repository behavior required by renumber preview."""

    def list_by_project(self, project_id: str) -> list[FileAsset]:
        """Return file assets for a project."""


class LtrRenumberPreviewService:
    """Build a non-destructive plan for LTR renumbering impacts."""

    def __init__(
        self,
        project_repository: ProjectRepositoryPort,
        ltr_repository: LtrRepositoryPort,
        folder_repository: ProjectFolderRecordRepositoryPort,
        file_asset_repository: FileAssetRepositoryPort,
    ) -> None:
        """Create a renumber preview service."""
        self._projects = project_repository
        self._ltrs = ltr_repository
        self._folders = folder_repository
        self._assets = file_asset_repository

    def preview_project(
        self,
        project_id: str,
        command: PreviewLtrRenumberCommand,
    ) -> LtrRenumberPreview:
        """Return a non-destructive LTR renumber impact preview."""
        project = self._projects.get(project_id)
        if project is None:
            raise LtrRenumberPreviewNotFoundError(f"Project not found: {project_id}")
        old_number = _normalize_existing_ltr(command.old_ltr_number)
        new_number = _normalize_new_ltr(command.new_ltr_number)
        reason = command.reason.strip()
        if not reason:
            raise LtrRenumberPreviewError("Renumber reason is required.")
        if old_number == new_number:
            raise LtrRenumberPreviewError("New LTR number must differ from old LTR number.")

        ltr_record = _find_project_ltr(self._ltrs.list_by_project(project_id), old_number)
        duplicates = [
            ltr
            for ltr in self._ltrs.search(new_number)
            if ltr.ltr_number == new_number and ltr.ltr_id != ltr_record.ltr_id
        ]
        impacts = (
            *_folder_impacts(
                self._folders.list_by_project(project_id),
                old_number,
                new_number,
            ),
            *_asset_impacts(
                self._assets.list_by_project(project_id),
                old_number,
                new_number,
            ),
        )
        conflicts = _conflicts(new_number, duplicates, impacts)
        warnings = _warnings(impacts)
        return LtrRenumberPreview(
            project_id=project_id,
            old_ltr_number=old_number,
            new_ltr_number=new_number,
            reason=reason,
            operator_confirmation_required=True,
            operator_confirmed=command.operator_confirmed,
            ltr_record_id=ltr_record.ltr_id,
            impacts=impacts,
            conflicts=conflicts,
            warnings=warnings,
            audit_summary=(
                f"Renumber {old_number} -> {new_number}; reason: {reason}; "
                f"impacts: {len(impacts)}; conflicts: {len(conflicts)}"
            ),
        )


def _normalize_existing_ltr(value: str) -> str:
    """Normalize an existing LTR number."""
    try:
        return parse_ltr_number(value).normalized
    except LtrNumberError as exc:
        raise LtrRenumberPreviewError(str(exc)) from exc


def _normalize_new_ltr(value: str) -> str:
    """Normalize and validate a new LTR number."""
    try:
        validate_new_registration_number(value)
        return parse_ltr_number(value).normalized
    except LtrNumberError as exc:
        raise LtrRenumberPreviewError(str(exc)) from exc


def _find_project_ltr(records: list[LtrRecord], old_number: str) -> LtrRecord:
    """Find the project LTR record being renumbered."""
    for record in records:
        if record.ltr_number == old_number:
            return record
    raise LtrRenumberPreviewNotFoundError(
        f"LTR record not found for project: {old_number}"
    )


def _folder_impacts(
    records: list[ProjectFolderRecord],
    old_number: str,
    new_number: str,
) -> tuple[RenameImpact, ...]:
    """Return folder record path impacts."""
    return tuple(
        impact
        for record in records
        if (
            impact := _path_impact(
                record_type="project_folder",
                record_id=record.folder_id,
                path=record.folder_path,
                old_number=old_number,
                new_number=new_number,
            )
        )
    )


def _asset_impacts(
    assets: list[FileAsset],
    old_number: str,
    new_number: str,
) -> tuple[RenameImpact, ...]:
    """Return file asset path impacts."""
    return tuple(
        impact
        for asset in assets
        if (
            impact := _path_impact(
                record_type=f"file_asset:{asset.asset_type.value}",
                record_id=asset.asset_id,
                path=asset.path,
                old_number=old_number,
                new_number=new_number,
            )
        )
    )


def _path_impact(
    *,
    record_type: str,
    record_id: str,
    path: Path,
    old_number: str,
    new_number: str,
) -> RenameImpact | None:
    """Return path replacement impact when the old number appears in a path."""
    path_text = str(path)
    if old_number not in path_text:
        return None
    target_path = Path(path_text.replace(old_number, new_number))
    return RenameImpact(
        record_type=record_type,
        record_id=record_id,
        current_path=path,
        target_path=target_path,
        target_exists=target_path.exists(),
        rename_required=target_path != path,
    )


def _conflicts(
    new_number: str,
    duplicates: list[LtrRecord],
    impacts: tuple[RenameImpact, ...],
) -> tuple[str, ...]:
    """Return conflicts that block future renumber execution."""
    conflicts = [
        f"LTR number already exists in local records: {new_number}"
        for _ in duplicates
    ]
    conflicts.extend(
        f"Target path already exists: {impact.target_path}"
        for impact in impacts
        if impact.target_exists
    )
    return tuple(conflicts)


def _warnings(impacts: tuple[RenameImpact, ...]) -> tuple[str, ...]:
    """Return non-blocking renumber preview warnings."""
    if impacts:
        return ()
    return ("No folder or file asset path currently contains the old LTR number.",)
