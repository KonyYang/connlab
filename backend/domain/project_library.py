"""Stable project identity and portable-library contracts."""
from dataclasses import dataclass, field
from typing import Protocol

FORMAT_VERSION = 1


class ProjectLibraryError(ValueError):
    """The requested library operation cannot safely proceed."""


class ProjectLibraryConflict(ProjectLibraryError):
    """The reviewed source, target or project state changed."""


@dataclass(frozen=True)
class LibraryPaths:
    library_root: str
    projects_root: str
    data_root: str
    database_path: str
    configured: bool
    format_version: int = FORMAT_VERSION


class ProjectLibraryStore(Protocol):
    def members(self, query: str = "", batch_id: str | None = None) -> list[dict]: ...
    def member(self, member_id: str) -> dict: ...
    def add_member(self, data: dict) -> dict: ...
    def update_member(self, member_id: str, changes: dict) -> dict: ...
    def save_batch(self, batch: dict) -> None: ...
    def batch(self, batch_id: str) -> dict: ...
    def project_exists(self, project_id: str) -> bool: ...
    def project_numbers(self) -> list[dict]: ...
    def create_planning_project(self, member: dict) -> str: ...


class ProjectFolderOpener(Protocol):
    def open_directory(self, path): ...
