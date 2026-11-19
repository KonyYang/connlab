"""Shared directory picker for reconnecting existing library folders."""
from collections.abc import Callable
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from backend.infrastructure.files.windows_path_picker import WindowsPathPicker


router = APIRouter(prefix="/api/tools/legacy-projects", tags=["tools"])


def get_directory_picker() -> Callable[[], Path | None]:
    return WindowsPathPicker().pick_legacy_project_directory


@router.post("/pick-directory")
def pick_directory(picker=Depends(get_directory_picker)):
    try:
        path = picker()
        return {"path": str(path) if path else None}
    except (OSError, RuntimeError) as exc:
        raise HTTPException(422, "Cannot open the folder picker. Enter the folder path manually.") from exc
