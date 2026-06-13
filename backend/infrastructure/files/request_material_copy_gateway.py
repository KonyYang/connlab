"""Safe staged file copying for request-material collection."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Sequence

from backend.application.project_request_material_collection_service import (
    ProjectRequestMaterialCollectionConflictError,
    RequestMaterialPreviewItem,
)


class RequestMaterialCopyGateway:
    """Copy request material through a ConnLab-owned staging directory."""

    def copy_items(
        self,
        *,
        items: Sequence[RequestMaterialPreviewItem],
        staging_root: Path,
    ) -> tuple[Path, ...]:
        """Copy planned items without overwriting existing target files."""
        copied: list[Path] = []
        try:
            staging_root.mkdir(parents=True, exist_ok=False)
            for index, item in enumerate(items):
                if item.action != "copy":
                    continue
                if item.target_path.exists():
                    raise ProjectRequestMaterialCollectionConflictError(
                        f"Target file already exists: {item.target_path}"
                    )
                staged = staging_root / f"{index}-{item.target_path.name}"
                shutil.copy2(item.source_path, staged)
                item.target_path.parent.mkdir(parents=True, exist_ok=True)
                staged.replace(item.target_path)
                copied.append(item.target_path)
        finally:
            if staging_root.exists():
                shutil.rmtree(staging_root, ignore_errors=True)
        return tuple(copied)
