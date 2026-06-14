"""Filesystem gateway for Project Folder Required forms placement."""

from __future__ import annotations

import os
from pathlib import Path
import shutil

from backend.application.project_folder_required_forms_service import (
    RequiredFormsTargetChangedError,
    compute_sha256,
)


class ProjectFolderRequiredFormsFileGateway:
    """Safely place generated Required forms into the Official project folder."""

    def create_new(self, source: Path, target: Path, *, key: str) -> None:
        """Copy a new file to target and fail if the target already exists."""
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as output:
            with source.open("rb") as input_file:
                shutil.copyfileobj(input_file, output)

    def update_managed(
        self,
        source: Path,
        target: Path,
        *,
        key: str,
        expected_existing_sha256: str,
    ) -> None:
        """Replace a ConnLab-managed target only if it is still unchanged."""
        if compute_sha256(target) != expected_existing_sha256:
            raise RequiredFormsTargetChangedError(str(target))
        temporary = target.with_name(f".{target.name}.connlab-tmp")
        try:
            shutil.copyfile(source, temporary)
            if compute_sha256(target) != expected_existing_sha256:
                raise RequiredFormsTargetChangedError(str(target))
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
