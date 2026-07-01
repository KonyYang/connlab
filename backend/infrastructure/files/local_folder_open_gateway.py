"""Local folder open gateway for operator workstation actions."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Callable

from backend.application.project_folder_open_service import ProjectFolderOpenResult


class LocalFolderOpenGateway:
    """Open an existing directory without creating or modifying files."""

    def __init__(self, *, launcher: Callable[[str], None] | None = None) -> None:
        """Create the gateway with an optional launcher for tests."""
        self._launcher = launcher or _windows_startfile

    def open_directory(self, path: Path) -> ProjectFolderOpenResult:
        """Open an existing local directory if the environment supports it."""
        if not path.exists() or not path.is_dir():
            return ProjectFolderOpenResult(
                project_id="",
                status="blocked",
                message="Project folder is not available yet.",
                local_official_folder_path=path,
            )
        try:
            self._launcher(str(path))
        except RuntimeError as exc:
            return ProjectFolderOpenResult(
                project_id="",
                status="unsupported",
                message=str(exc),
                local_official_folder_path=path,
            )
        except OSError as exc:
            return ProjectFolderOpenResult(
                project_id="",
                status="blocked",
                message=str(exc),
                local_official_folder_path=path,
            )
        return ProjectFolderOpenResult(
            project_id="",
            status="opened",
            message="Project folder opened.",
            local_official_folder_path=path,
        )


def _windows_startfile(path: str) -> None:
    launcher = getattr(os, "startfile", None)
    if launcher is None:
        raise RuntimeError("Open folder is only available on the local Windows workstation.")
    launcher(path)
