"""File gateway for missing Official project folder creation."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from backend.application.official_project_folder_check_service import (
    OfficialFolderRepairFailureError,
)


class OfficialProjectFolderRepairGateway:
    """Create missing folders for the Official project folder repair flow."""

    def create_missing_folders(self, paths: Sequence[Path]) -> tuple[Path, ...]:
        """Create folders in order and report partial failures."""
        created: list[Path] = []
        for path in paths:
            try:
                if path.exists() and not path.is_dir():
                    raise OfficialFolderRepairFailureError(
                        f"Expected a folder, but a file exists at this path: {path}",
                        created_paths=tuple(created),
                        failed_path=path,
                    )
                path.mkdir(parents=True, exist_ok=True)
                created.append(path)
            except OfficialFolderRepairFailureError:
                raise
            except OSError as exc:
                raise OfficialFolderRepairFailureError(
                    str(exc),
                    created_paths=tuple(created),
                    failed_path=path,
                ) from exc
        return tuple(created)
