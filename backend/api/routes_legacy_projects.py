"""Dedicated historical browsing; IDs cannot enter business Project writes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend.api.dependencies import get_session
from backend.application.legacy_project_registration_service import LegacyProjectRegistrationService
from backend.infrastructure.files.legacy_project_preview_gateway import LegacyProjectPreviewGateway
from backend.infrastructure.files.local_folder_open_gateway import LocalFolderOpenGateway
from backend.infrastructure.storage.repositories.legacy_projects import LegacyProjectRepository

router = APIRouter(prefix="/api/legacy-projects", tags=["legacy-projects"])


def get_legacy_registration_service(session=Depends(get_session)):
    return LegacyProjectRegistrationService(LegacyProjectRepository(session),
        LegacyProjectPreviewGateway(), LocalFolderOpenGateway())


def checked(action):
    try:
        return action()
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    except OSError as exc:
        raise HTTPException(422, "Folder is unavailable or redirected. Choose an accessible original folder.") from exc


class ChangeLocationRequest(BaseModel):
    folder: str = Field(min_length=1, max_length=4096)
    expected_revision: int = Field(ge=1)


@router.get("")
def list_records(q: str = Query(default="", max_length=4096), service=Depends(get_legacy_registration_service)):
    return service.search(q)


@router.get("/{record_id}")
def get_record(record_id: str, service=Depends(get_legacy_registration_service)):
    return checked(lambda: service.get(record_id))


@router.post("/{record_id}/open-folder")
def open_folder(record_id: str, service=Depends(get_legacy_registration_service)):
    return checked(lambda: service.open_folder(record_id))


@router.post("/{record_id}/location")
def change_location(record_id: str, request: ChangeLocationRequest, service=Depends(get_legacy_registration_service)):
    return checked(lambda: service.change_location(record_id, request.folder, request.expected_revision))
