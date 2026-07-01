"""Open the backend-resolved local project folder without mutating files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol


ProjectFolderOpenStatus = Literal["opened", "blocked", "unsupported"]


@dataclass(frozen=True, slots=True)
class ProjectFolderOpenResult:
    """Result of a local project folder open attempt."""

    project_id: str
    status: ProjectFolderOpenStatus
    message: str
    local_official_folder_path: Path | None


class ProjectFolderOpenGatewayPort(Protocol):
    """Non-mutating local folder open operation."""

    def open_directory(self, path: Path) -> ProjectFolderOpenResult:
        """Open an existing local directory or return a safe status."""


class ProjectFolderOpenWorkflowPort(Protocol):
    """Read-only workflow context needed to resolve the local folder."""

    def context(self, project_id: str):
        """Return the public folder workflow context for a project."""


class ProjectFolderOpenService:
    """Open only the trusted folder path resolved from project context."""

    def __init__(
        self,
        *,
        workflow_service: ProjectFolderOpenWorkflowPort,
        gateway: ProjectFolderOpenGatewayPort,
    ) -> None:
        """Create the project folder open service."""
        self._workflow_service = workflow_service
        self._gateway = gateway

    def open_local_project_folder(self, project_id: str) -> ProjectFolderOpenResult:
        """Open the local official folder for a project."""
        context = self._workflow_service.context(project_id)
        path = context.local_official_folder_path
        if path is None:
            return ProjectFolderOpenResult(
                project_id=project_id,
                status="blocked",
                message="Project folder is not available yet.",
                local_official_folder_path=None,
            )
        gateway_result = self._gateway.open_directory(path)
        return ProjectFolderOpenResult(
            project_id=project_id,
            status=gateway_result.status,
            message=gateway_result.message,
            local_official_folder_path=path,
        )
