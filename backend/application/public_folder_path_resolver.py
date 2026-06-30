"""Resolve public Open/Closed folder paths under the configured public root."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class PublicFolderPathError(ValueError):
    """Raised when public-folder paths cannot be safely resolved."""


@dataclass(frozen=True, slots=True)
class PublicFolderPaths:
    """Resolved public-folder workflow paths."""

    public_root: Path
    public_root_class: str
    year: int
    project_folder_name: str
    open_year_path: Path
    closed_year_path: Path
    public_open_path: Path
    public_closed_path: Path
    missing_directories: tuple[Path, ...]


class PublicFolderPathResolver:
    """Resolve workflow paths and keep them inside the configured root."""

    def resolve(
        self,
        *,
        public_root: Path | None,
        year: int | None,
        project_folder_name: str,
    ) -> PublicFolderPaths:
        """Return Open/Closed paths or raise a business-safe path error."""
        if public_root is None:
            raise PublicFolderPathError("Public Project locations is not configured.")
        if not public_root.is_dir():
            raise PublicFolderPathError("Public Project locations must be an existing directory.")
        if year is None:
            raise PublicFolderPathError("Public folder year is unresolved.")
        name = project_folder_name.strip()
        if not name:
            raise PublicFolderPathError("Project folder name is unavailable.")

        root = public_root.resolve()
        open_year = root / "Open" / str(year)
        closed_year = root / "Closed" / str(year)
        public_open = open_year / name
        public_closed = closed_year / name
        for candidate in (open_year, closed_year, public_open, public_closed):
            _ensure_under_root(root, candidate)
        missing = tuple(path for path in (root / "Open", open_year, root / "Closed", closed_year) if not path.exists())
        return PublicFolderPaths(
            public_root=root,
            public_root_class=_classify_root(root),
            year=year,
            project_folder_name=name,
            open_year_path=open_year,
            closed_year_path=closed_year,
            public_open_path=public_open,
            public_closed_path=public_closed,
            missing_directories=missing,
        )


def _ensure_under_root(root: Path, candidate: Path) -> None:
    try:
        candidate.resolve().relative_to(root)
    except ValueError as exc:
        raise PublicFolderPathError(f"Resolved path escapes Public Project locations: {candidate}") from exc


def _classify_root(root: Path) -> str:
    text = str(root).lower()
    if str(root).startswith("\\\\"):
        return "public_like_root"
    if "publicproject" in text or "public project" in text:
        return "local_development_root"
    return "ambiguous_local_root"
