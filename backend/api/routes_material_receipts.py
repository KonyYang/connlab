"""Receipt-only HTTP boundary; no import/adoption/portable dependencies."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from backend.api.dependencies import get_session, get_settings, get_project_registry_summary_service
from backend.application.project_library.material_receipt import MaterialReceiptService
from backend.infrastructure.storage.repositories.material_receipt import MaterialReceiptRepository
from backend.infrastructure.storage.repositories.library_search import LibrarySearchRepository
from backend.infrastructure.project_library.material_receipt_files import MaterialReceiptFiles

router = APIRouter(prefix="/api/material-receipts", tags=["material-receipts"])


def get_material_receipt_service(session=Depends(get_session), settings=Depends(get_settings)):
    return MaterialReceiptService(MaterialReceiptRepository(session), MaterialReceiptFiles(settings),
        LibrarySearchRepository(session, get_project_registry_summary_service(session)))


def checked(action):
    try:
        return action()
    except LookupError as error:
        raise HTTPException(404, str(error)) from error
    except ValueError as error:
        raise HTTPException(409, str(error)) from error
    except OSError as error:
        raise HTTPException(422, "The material location is unavailable or cannot be written. Check access and preview again.") from error


class FolderRequest(BaseModel):
    folder: str = Field(min_length=1, max_length=4096)


class PreviewRequest(BaseModel):
    source: str = Field(min_length=1, max_length=4096)
    number: str = Field(default="", max_length=128)
    product_name: str = Field(default="", max_length=2048)
    test_keywords: str = Field(default="", max_length=2048)
    target_key: str = Field(default="", max_length=256)
    separate_description: str = Field(default="", max_length=256)
    material_state: str | None = None


class ConfirmRequest(BaseModel):
    plan_id: str = Field(pattern="^[a-f0-9]{32}$")
    fingerprint: str = Field(pattern="^[a-f0-9]{64}$")


class MetadataRequest(BaseModel):
    revision: int = Field(ge=1)
    product_name: str = Field(min_length=1, max_length=2048)
    test_keywords: str = Field(default="", max_length=2048)
    material_state: str | None = None


@router.get("/runtime")
def runtime(service=Depends(get_material_receipt_service)):
    return checked(service.runtime)


@router.post("/destination")
def destination(request: FolderRequest, service=Depends(get_material_receipt_service)):
    return checked(lambda: service.configure_root(request.folder))


@router.post("/preview")
def preview(request: PreviewRequest, service=Depends(get_material_receipt_service)):
    return checked(lambda: service.preview(**request.model_dump()))


@router.post("/confirm")
def confirm(request: ConfirmRequest, service=Depends(get_material_receipt_service)):
    return checked(lambda: service.confirm(request.plan_id, request.fingerprint))


@router.get("/batches/{batch_id}")
def batch(batch_id: str, service=Depends(get_material_receipt_service)):
    return checked(lambda: service.batch(batch_id))


@router.post("/batches/{batch_id}/retry")
def retry(batch_id: str, service=Depends(get_material_receipt_service)):
    return checked(lambda: service.retry(batch_id))


@router.get("/entries/{receipt_id}")
def detail(receipt_id: str, service=Depends(get_material_receipt_service)):
    return checked(lambda: service.detail(receipt_id))


@router.post("/entries/{receipt_id}/metadata")
def metadata(receipt_id: str, request: MetadataRequest, service=Depends(get_material_receipt_service)):
    return checked(lambda: service.edit(receipt_id, **request.model_dump()))


@router.post("/entries/{receipt_id}/location-preview")
def location_preview(receipt_id: str, request: FolderRequest, service=Depends(get_material_receipt_service)):
    return checked(lambda: service.locate_preview(receipt_id, request.folder))


@router.post("/entries/{receipt_id}/location")
def location(receipt_id: str, request: ConfirmRequest, service=Depends(get_material_receipt_service)):
    return checked(lambda: service.locate(receipt_id, request.plan_id, request.fingerprint))


class CatalogLocationPreviewRequest(FolderRequest):
    key: str = Field(min_length=1, max_length=256)


class CatalogLocationRequest(ConfirmRequest):
    key: str = Field(min_length=1, max_length=256)


@router.post("/catalog-location-preview")
def catalog_location_preview(request: CatalogLocationPreviewRequest, service=Depends(get_material_receipt_service)):
    return checked(lambda: service.catalog_location_preview(request.key, request.folder))


@router.post("/catalog-location")
def catalog_location(request: CatalogLocationRequest, service=Depends(get_material_receipt_service)):
    return checked(lambda: service.catalog_location(request.key, request.plan_id, request.fingerprint))
