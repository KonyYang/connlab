"""Read-only legacy folder previews; intentionally no database dependencies."""
from collections.abc import Callable
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.application.legacy_project_preview_service import LegacyProjectPreviewService
from backend.infrastructure.files.legacy_project_preview_gateway import LegacyProjectPreviewGateway
from backend.infrastructure.files.windows_path_picker import WindowsPathPicker


router = APIRouter(prefix="/api/tools/legacy-projects", tags=["tools"])


class PreviewRequest(BaseModel):
    roots: list[str] = Field(min_length=1, max_length=20)


def get_directory_picker() -> Callable[[], Path | None]:
    return WindowsPathPicker().pick_legacy_project_directory


@router.post("/pick-directory")
def pick_directory(picker=Depends(get_directory_picker)):
    try:
        path = picker()
        return {"path": str(path) if path else None}
    except (OSError, RuntimeError) as exc:
        raise HTTPException(422, "无法打开目录选择窗口，请使用手动填写目录。") from exc


@router.post("/preview")
def preview(request: PreviewRequest):
    if any(not path.strip() or len(path) > 4096 for path in request.roots):
        raise HTTPException(422, "请选择有效的项目目录。")
    return LegacyProjectPreviewService(LegacyProjectPreviewGateway()).preview(request.roots)
