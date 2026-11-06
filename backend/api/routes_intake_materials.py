"""Request-material folder operations; no project creation or registration."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.api.dependencies import get_session
from backend.application.intake_materials_service import IntakeMaterialsService
from backend.infrastructure.files.materials_copy_gateway import MaterialsCopyGateway
from backend.infrastructure.storage.repositories.intake_package import IntakePackageRepository, IntakeAssetRepository
from backend.infrastructure.storage.repositories.external_resources import ExternalResourceRepository
from backend.infrastructure.files.local_folder_open_gateway import LocalFolderOpenGateway

router = APIRouter(tags=['intake-materials'])

def get_materials_service(session: Session = Depends(get_session)):
    return IntakeMaterialsService(IntakePackageRepository(session), IntakeAssetRepository(session), ExternalResourceRepository(session), MaterialsCopyGateway())

class FolderRequest(BaseModel):
    folder_name: str

def checked(operation):
    try:
        return operation()
    except (ValueError, OSError) as exc:
        raise HTTPException(409, str(exc)) from exc

@router.get('/api/intake/packages/{package_id}/materials')
def preview(package_id: str, service=Depends(get_materials_service)):
    return checked(lambda: service.preview(package_id))

@router.post('/api/intake/packages/{package_id}/materials')
def save(package_id: str, request: FolderRequest, service=Depends(get_materials_service)):
    return checked(lambda: service.save(package_id, request.folder_name))

@router.post('/api/intake/materials/open-folder')
def open_folder(request: FolderRequest, service=Depends(get_materials_service)):
    return checked(lambda: LocalFolderOpenGateway().open_directory(service.folder(request.folder_name)))
