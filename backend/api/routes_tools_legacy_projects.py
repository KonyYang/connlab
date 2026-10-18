"""Read-only previews stay database-free; registration is an explicit separate action."""
from collections.abc import Callable
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.application.legacy_project_preview_service import LegacyProjectPreviewService
from backend.infrastructure.files.legacy_project_preview_gateway import LegacyProjectPreviewGateway
from backend.infrastructure.files.windows_path_picker import WindowsPathPicker
from backend.api.routes_legacy_projects import get_legacy_registration_service


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
        raise HTTPException(422, "Cannot open the folder picker. Enter the folder path manually.") from exc


@router.post("/preview")
def preview(request: PreviewRequest):
    if any(not path.strip() or len(path) > 4096 for path in request.roots):
        raise HTTPException(422, "Choose a valid project folder.")
    return LegacyProjectPreviewService(LegacyProjectPreviewGateway()).preview(request.roots)


class RegistrationPlanRequest(BaseModel):
    folders: list[str] = Field(min_length=1, max_length=1000)


class RegistrationChoice(BaseModel):
    folder: str = Field(min_length=1, max_length=4096)
    fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    keep_separate: bool = False


class RegistrationRequest(RegistrationPlanRequest):
    selected: list[RegistrationChoice] = Field(min_length=1, max_length=1000)


def validate_folders(folders):
    if any(not path.strip() or len(path) > 4096 for path in folders):
        raise HTTPException(422, "Choose valid project folders.")


@router.post("/registration-plan")
def registration_plan(request: RegistrationPlanRequest, service=Depends(get_legacy_registration_service)):
    validate_folders(request.folders)
    plan = service.plan(request.folders)
    return {"projects": [{key: value for key, value in row.items() if key not in {"source_id", "identity"}}
                         for row in plan["projects"]]}


@router.post("/import")
def import_projects(request: RegistrationRequest, service=Depends(get_legacy_registration_service)):
    validate_folders(request.folders)
    if any(choice.folder not in request.folders for choice in request.selected):
        raise HTTPException(422, "Selected projects must belong to the registration plan.")
    return service.register(request.folders, [choice.model_dump() for choice in request.selected])
