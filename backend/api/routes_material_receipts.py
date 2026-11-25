"""Receipt-only HTTP boundary; no import/adoption/portable dependencies."""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from backend.api.dependencies import get_session, get_settings, get_project_registry_summary_service
from backend.application.project_library.material_receipt import MaterialReceiptService
from backend.infrastructure.storage.repositories.material_receipt import MaterialReceiptRepository
from backend.infrastructure.storage.repositories.library_search import LibrarySearchRepository
from backend.infrastructure.project_library.material_receipt_files import MaterialReceiptFiles

router = APIRouter(prefix="/api/material-receipts", tags=["material-receipts"])


def get_material_receipt_service(session=Depends(get_session), settings=Depends(get_settings)):
    return MaterialReceiptService(MaterialReceiptRepository(session), MaterialReceiptFiles(settings),
        LibrarySearchRepository(session, get_project_registry_summary_service(session), settings.data_dir))


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


class CopyContextRequest(BaseModel):
    session_id: str = Field(pattern="^[a-f0-9]{32}$")
    token: str = Field(pattern="^[a-f0-9]{32}$")


class CopyConfirmRequest(ConfirmRequest):
    context: CopyContextRequest


class RetryRequest(BaseModel):
    context: CopyContextRequest | None = None


class ContextUpdateRequest(BaseModel):
    session_id: str = Field(pattern="^[a-f0-9]{32}$")
    intent: int = Field(ge=1, le=9007199254740991)
    project_id: str | None = Field(default=None, min_length=1, max_length=128)


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
def retry(batch_id: str, request: RetryRequest | None = None, service=Depends(get_material_receipt_service)):
    return checked(lambda: service.retry(batch_id, request.context.model_dump() if request and request.context else None))


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


class CopyPreviewRequest(BaseModel):
    model_config = {"extra": "forbid"}
    context: CopyContextRequest
    source_key: str = Field(min_length=1, max_length=256)
    relative_path: str = Field(min_length=1, max_length=4096)
    target_relative_directory: str = Field(default="Reference materials", max_length=4096)


@router.post("/copy-preview")
def copy_preview(request: CopyPreviewRequest, service=Depends(get_material_receipt_service)):
    return checked(lambda: service.copy_preview(**request.model_dump()))


@router.post("/copy-confirm")
def copy_confirm(request: CopyConfirmRequest, service=Depends(get_material_receipt_service)):
    return checked(lambda: service.copy_confirm(request.plan_id, request.fingerprint, request.context.model_dump()))


@router.get("/catalog-history")
def catalog_history(key: str = Query(..., min_length=1, max_length=256),
                    service=Depends(get_material_receipt_service)):
    return checked(lambda: service.catalog_history(key))


@router.post("/copy-context/session")
def create_copy_context(service=Depends(get_material_receipt_service)):
    return service.create_copy_context()


@router.post("/copy-context")
def update_copy_context(request: ContextUpdateRequest, service=Depends(get_material_receipt_service)):
    return checked(lambda: service.update_copy_context(request.session_id, request.intent, request.project_id))


class ArchivePreviewRequest(BaseModel):
    source: str = Field(min_length=1,max_length=4096)
    independent: bool = False


def archive_service(session,settings):
    from backend.application.project_library.material_archive import MaterialArchiveService
    from backend.infrastructure.project_library.material_archive_files import MaterialArchiveFiles
    from backend.infrastructure.storage.repositories.material_archive import MaterialArchiveRepository
    return MaterialArchiveService(MaterialArchiveRepository(session),MaterialArchiveFiles(settings),
        LibrarySearchRepository(session, get_project_registry_summary_service(session), settings.data_dir))


def start_archive_job(session,settings,action):
    from sqlalchemy.orm import Session
    from backend.infrastructure.project_library.material_archive_files import archive_jobs
    engine=session.get_bind()
    def worker(cancellation):
        with Session(engine) as fresh:
            service=archive_service(fresh,settings)
            service.files.cancellation=cancellation
            return action(service)
    return checked(lambda:archive_jobs.start(worker))


@router.post('/archive/refresh',status_code=202)
def refresh_archive(session=Depends(get_session),settings=Depends(get_settings)):
    return start_archive_job(session,settings,lambda service:service.refresh())


@router.post('/archive/preview',status_code=202)
def preview_archive(request:ArchivePreviewRequest,session=Depends(get_session),settings=Depends(get_settings)):
    return start_archive_job(session,settings,lambda service:service.preview(request.source,request.independent))


@router.post('/archive/confirm',status_code=202)
def confirm_archive(request:ConfirmRequest,session=Depends(get_session),settings=Depends(get_settings)):
    return start_archive_job(session,settings,lambda service:service.confirm(request.plan_id,request.fingerprint))


@router.get('/archive/jobs/{job_id}')
def archive_job(job_id:str):
    from backend.infrastructure.project_library.material_archive_files import archive_jobs
    return checked(lambda:archive_jobs.get(job_id))


@router.post('/archive/jobs/{job_id}/cancel')
def cancel_archive_job(job_id:str):
    from backend.infrastructure.project_library.material_archive_files import archive_jobs
    return checked(lambda:archive_jobs.cancel(job_id))


@router.get('/archive/operations/{operation_id}')
def archive_operation(operation_id:str,session=Depends(get_session),settings=Depends(get_settings)):
    return checked(lambda:archive_service(session,settings).operation(operation_id))


@router.post('/archive/operations/{operation_id}/retry',status_code=202)
def retry_archive(operation_id:str,session=Depends(get_session),settings=Depends(get_settings)):
    return start_archive_job(session,settings,lambda service:service.retry(operation_id))
