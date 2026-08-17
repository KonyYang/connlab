"""Application service for Project-scoped Matrix source candidate selection."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import stat
from typing import Protocol

from backend.domain import FileAsset, FileAssetType, Project


class ProjectTestPlanSourceCandidateError(ValueError):
    """Raised when source candidate input is invalid."""


class ProjectTestPlanSourceCandidateNotFoundError(LookupError):
    """Raised when project or candidate source cannot be found."""


class ProjectStore(Protocol):
    """Project lookup operations needed by source candidate service."""

    def get(self, project_id: str) -> Project | None:
        """Return one project by id."""


class FileAssetStore(Protocol):
    """Project file-asset operations needed by source candidate service."""

    def get(self, asset_id: str) -> FileAsset | None:
        """Return one file asset by id."""

    def list_by_project(self, project_id: str) -> list[FileAsset]:
        """Return file assets registered for one project."""


class OfficialWorkspaceStore(Protocol):
    """Official workspace lookup needed for the preferred import directory."""

    def get_by_project(self, project_id: str) -> object | None:
        """Return the official workspace record when one exists."""


@dataclass(frozen=True, slots=True)
class ProjectTestPlanSourceCandidate:
    """One candidate Matrix source file derived from Project file assets."""

    source_asset_id: str
    original_name: str
    extension: str
    asset_type: FileAssetType
    candidate_kind: str
    reason: str
    stored_file_available: bool


@dataclass(frozen=True, slots=True)
class ProjectTestPlanSourceCandidatesResult:
    """Project-scoped candidate source list and operator warnings."""

    project_id: str
    candidates: tuple[ProjectTestPlanSourceCandidate, ...]
    warnings: tuple[str, ...]
    preferred_import_directory: Path | None
    preferred_import_directory_source: str


@dataclass(frozen=True, slots=True)
class ProjectTestPlanResolvedDirectoryCandidate:
    """One path-free file candidate from the currently resolved source directory."""

    candidate_id: str
    file_name: str


@dataclass(frozen=True, slots=True)
class ProjectTestPlanResolvedDirectoryCandidatesResult:
    """Bounded direct-file view for the ordinary-browser source picker."""

    project_id: str
    source_title: str
    source_directory_kind: str
    candidates: tuple[ProjectTestPlanResolvedDirectoryCandidate, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class _ResolvedDirectoryEntry:
    candidate: ProjectTestPlanResolvedDirectoryCandidate
    path: Path


class ProjectTestPlanSourceCandidateService:
    """Build and resolve Project Matrix source candidates from file assets."""

    _SPEC_KEYWORDS = (
        "spec",
        "specification",
        "matrix",
        "qualification",
        "test",
        "product",
    )
    _RESOLVED_DIRECTORY_EXTENSIONS = frozenset({".doc", ".docx", ".pdf"})

    def __init__(
        self,
        *,
        project_store: ProjectStore,
        file_asset_store: FileAssetStore,
        official_workspace_store: OfficialWorkspaceStore | None = None,
    ) -> None:
        """Create the service with repository ports."""
        self._projects = project_store
        self._assets = file_asset_store
        self._workspaces = official_workspace_store

    def list_source_candidates(
        self,
        project_id: str,
    ) -> ProjectTestPlanSourceCandidatesResult:
        """List candidate `.docx` Matrix source files for one project."""
        self._require_project(project_id)
        assets = self._assets.list_by_project(project_id)
        preferred_directory, preferred_source = self._preferred_import_directory(
            project_id, assets
        )
        if not assets:
            return ProjectTestPlanSourceCandidatesResult(
                project_id=project_id,
                candidates=(),
                warnings=("No project source files are registered yet.",),
                preferred_import_directory=preferred_directory,
                preferred_import_directory_source=preferred_source,
            )

        ranked: list[tuple[int, ProjectTestPlanSourceCandidate]] = []
        missing_count = 0
        for asset in assets:
            extension = _asset_extension(asset)
            if extension != ".docx":
                continue
            stored_file_available = asset.path.is_file()
            if not stored_file_available:
                missing_count += 1
            score, candidate_kind, reason = _candidate_profile(asset)
            ranked.append(
                (
                    score,
                    ProjectTestPlanSourceCandidate(
                        source_asset_id=asset.asset_id,
                        original_name=_display_name(asset),
                        extension=extension,
                        asset_type=asset.asset_type,
                        candidate_kind=candidate_kind,
                        reason=reason,
                        stored_file_available=stored_file_available,
                    ),
                )
            )

        warnings: list[str] = []
        if not ranked:
            warnings.append(
                "No `.docx` project source candidates were found. Use external source fallback."
            )
        if missing_count > 0:
            warnings.append(
                f"{missing_count} candidate source file(s) are missing from local storage."
            )
        ranked.sort(
            key=lambda item: (
                -item[0],
                item[1].original_name.lower(),
                item[1].source_asset_id,
            )
        )
        return ProjectTestPlanSourceCandidatesResult(
            project_id=project_id,
            candidates=tuple(candidate for _, candidate in ranked),
            warnings=tuple(warnings),
            preferred_import_directory=preferred_directory,
            preferred_import_directory_source=preferred_source,
        )

    def _preferred_import_directory(
        self, project_id: str, assets: list[FileAsset]
    ) -> tuple[Path | None, str]:
        workspace = (
            self._workspaces.get_by_project(project_id) if self._workspaces is not None else None
        )
        official_folder = getattr(workspace, "official_folder_path", None)
        if official_folder is not None:
            submitted_material = Path(official_folder) / "Submitted Material"
            if submitted_material.is_dir():
                return submitted_material, "submitted_material"
        parents = {
            asset.path.parent
            for asset in assets
            if asset.asset_type is FileAssetType.ATTACHMENT
            and asset.source_intake_asset_id
            and (asset.source_role or "").casefold() != "email_source"
            and asset.path.is_file()
            and asset.path.parent.is_dir()
        }
        if parents:
            return min(parents, key=lambda path: str(path.resolve()).casefold()), "intake_attachments"
        return None, "unavailable"

    def list_resolved_directory_candidates(
        self,
        project_id: str,
    ) -> ProjectTestPlanResolvedDirectoryCandidatesResult:
        """List direct supported files without exposing their local directory."""
        self._require_project(project_id)
        directory, source = self._preferred_import_directory(
            project_id,
            self._assets.list_by_project(project_id),
        )
        if directory is None:
            return ProjectTestPlanResolvedDirectoryCandidatesResult(
                project_id=project_id,
                source_title="Project source files",
                source_directory_kind="unavailable",
                candidates=(),
                warnings=("No project source folder is available.",),
            )
        entries = self._resolved_directory_entries(project_id, directory, source)
        return ProjectTestPlanResolvedDirectoryCandidatesResult(
            project_id=project_id,
            source_title=_resolved_directory_title(source),
            source_directory_kind=source,
            candidates=tuple(entry.candidate for entry in entries),
            warnings=(),
        )

    def get_resolved_directory_candidate_source_path(
        self,
        project_id: str,
        candidate_id: str,
    ) -> Path:
        """Re-resolve the current directory and accept only a still-current opaque id."""
        self._require_project(project_id)
        opaque_id = candidate_id.strip()
        if not opaque_id:
            raise ProjectTestPlanSourceCandidateError("candidate_id is required.")
        directory, source = self._preferred_import_directory(
            project_id,
            self._assets.list_by_project(project_id),
        )
        if directory is not None:
            for entry in self._resolved_directory_entries(project_id, directory, source):
                if entry.candidate.candidate_id == opaque_id:
                    return entry.path
        raise ProjectTestPlanSourceCandidateNotFoundError(
            "Project Matrix source candidate is no longer available."
        )

    def _resolved_directory_entries(
        self,
        project_id: str,
        directory: Path,
        source: str,
    ) -> tuple[_ResolvedDirectoryEntry, ...]:
        try:
            canonical_directory = directory.resolve(strict=True)
            entries: list[_ResolvedDirectoryEntry] = []
            for path in directory.iterdir():
                if (
                    path.is_symlink()
                    or path.suffix.casefold() not in self._RESOLVED_DIRECTORY_EXTENSIONS
                ):
                    continue
                file_fingerprint = _regular_file_fingerprint(path)
                if file_fingerprint is None:
                    continue
                if path.resolve(strict=True).parent != canonical_directory:
                    continue
                candidate_id = _opaque_candidate_id(
                    project_id=project_id,
                    source=source,
                    canonical_directory=canonical_directory,
                    file_name=path.name,
                    file_fingerprint=file_fingerprint,
                )
                entries.append(
                    _ResolvedDirectoryEntry(
                        candidate=ProjectTestPlanResolvedDirectoryCandidate(
                            candidate_id=candidate_id,
                            file_name=path.name,
                        ),
                        path=path,
                    )
                )
        except OSError as exc:
            raise ProjectTestPlanSourceCandidateError(
                "Unable to read the current project source folder."
            ) from exc
        entries.sort(
            key=lambda entry: (
                entry.candidate.file_name.casefold(),
                entry.candidate.file_name,
            )
        )
        return tuple(entries)

    def get_candidate_source_path(
        self,
        project_id: str,
        source_asset_id: str,
    ) -> Path:
        """Resolve one project-owned candidate source path by asset id."""
        self._require_project(project_id)
        asset_id = source_asset_id.strip()
        if not asset_id:
            raise ProjectTestPlanSourceCandidateError("source_asset_id is required.")
        asset = self._assets.get(asset_id)
        if asset is None or asset.project_id != project_id:
            raise ProjectTestPlanSourceCandidateNotFoundError(
                f"Project Matrix source candidate not found: {source_asset_id}"
            )
        extension = _asset_extension(asset)
        if extension != ".docx":
            raise ProjectTestPlanSourceCandidateError(
                f"Unsupported candidate source format: {extension or 'unknown'}."
            )
        if not asset.path.is_file():
            raise ProjectTestPlanSourceCandidateNotFoundError(
                f"Candidate source file not found: {asset.path}"
            )
        return asset.path

    def _require_project(self, project_id: str) -> Project:
        project = self._projects.get(project_id)
        if project is None:
            raise ProjectTestPlanSourceCandidateNotFoundError(
                f"Project not found: {project_id}"
            )
        return project


def _asset_extension(asset: FileAsset) -> str:
    return (asset.path.suffix or Path(_display_name(asset)).suffix).lower()


def _display_name(asset: FileAsset) -> str:
    return asset.original_name or asset.path.name or asset.asset_id


def _candidate_profile(asset: FileAsset) -> tuple[int, str, str]:
    name = _display_name(asset).lower()
    score = 0
    if asset.asset_type is FileAssetType.ATTACHMENT:
        score += 40
    elif asset.asset_type is FileAssetType.APPLICATION_FORM:
        score -= 20
    keyword_hits = [word for word in ProjectTestPlanSourceCandidateService._SPEC_KEYWORDS if word in name]
    if keyword_hits:
        score += 60 + len(keyword_hits)
        return (
            score,
            "likely_spec_or_matrix",
            "Name suggests product specification or Matrix content.",
        )
    if asset.asset_type is FileAssetType.APPLICATION_FORM:
        return (
            score,
            "application_form_docx",
            "Word application form is available but may not contain Matrix details.",
        )
    return (
        score,
        "supporting_docx_attachment",
        "Word attachment is available as fallback source candidate.",
    )


def _resolved_directory_title(source: str) -> str:
    if source == "submitted_material":
        return "Submitted Material files"
    if source == "intake_attachments":
        return "Email attachment files"
    return "Project source files"


def _regular_file_fingerprint(path: Path) -> str | None:
    before = path.stat(follow_symlinks=False)
    if not stat.S_ISREG(before.st_mode):
        return None
    content_digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            content_digest.update(chunk)
    after = path.stat(follow_symlinks=False)
    before_identity = _stat_identity(before)
    if before_identity != _stat_identity(after):
        raise ProjectTestPlanSourceCandidateError(
            "A project source file changed while it was being inspected."
        )
    return ":".join((*before_identity, content_digest.hexdigest()))


def _stat_identity(value: object) -> tuple[str, ...]:
    return tuple(
        str(getattr(value, field))
        for field in ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
    )


def _opaque_candidate_id(
    *,
    project_id: str,
    source: str,
    canonical_directory: Path,
    file_name: str,
    file_fingerprint: str,
) -> str:
    digest = hashlib.sha256()
    for value in (
        project_id,
        source,
        str(canonical_directory),
        file_name,
        file_fingerprint,
    ):
        encoded = value.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, byteorder="big"))
        digest.update(encoded)
    return digest.hexdigest()
