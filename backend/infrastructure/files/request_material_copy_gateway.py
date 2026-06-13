"""Safe staged file copying for request-material collection."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Sequence

from backend.application.project_request_material_collection_types import (
    ProjectRequestMaterialCollectionConflictError,
    ProjectRequestMaterialCollectionCopyFailureError,
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
                try:
                    staged.replace(item.target_path)
                except OSError as exc:
                    raise ProjectRequestMaterialCollectionCopyFailureError(
                        f"Request material file copy failure: {item.target_path}",
                        copied_paths=tuple(copied),
                        failed_path=item.target_path,
                    ) from exc
                copied.append(item.target_path)
        except ProjectRequestMaterialCollectionCopyFailureError:
            raise
        except OSError as exc:
            failed_path = None
            if "item" in locals():
                failed_path = item.target_path
            raise ProjectRequestMaterialCollectionCopyFailureError(
                f"Request material file copy failure: {failed_path or staging_root}",
                copied_paths=tuple(copied),
                failed_path=failed_path,
            ) from exc
        finally:
            if staging_root.exists():
                shutil.rmtree(staging_root, ignore_errors=True)
        return tuple(copied)
