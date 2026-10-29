"""Thin HTTP boundary for reviewed, local project-library operations."""
from pathlib import Path
from dataclasses import replace
from fastapi import APIRouter, Depends, HTTPException, Query
from backend.api.dependencies import get_session, get_settings
from backend.api.project_library_schemas import (
    RestoreFolderRequest, RestoreConfirmRequest, RuntimeResponse, MembersResponse, MemberResponse, RootsRequest, ScanResponse,
    IntakeRequest, IntakePlanResponse, BatchRequest, BatchResponse, TitleRequest,
    FolderRequest, ChangePlanResponse, ConfirmRequest, FilesResponse, FingerprintRequest,
    PortableInfoResponse, RestorePlanResponse, RestoreResponse, TakeoverPlanResponse, TakeoverResponse,
)
from backend.domain.project_library import ProjectLibraryError, ProjectLibraryConflict
from backend.application.project_library.service import ProjectLibraryService
from backend.infrastructure.project_library.files import LibraryFiles
from backend.infrastructure.storage.repositories.project_library import ProjectLibraryRepository
from backend.infrastructure.files.local_folder_open_gateway import LocalFolderOpenGateway
from backend.infrastructure.storage.repositories import ExternalResourceRepository
from backend.application.external_resource_service import ExternalResourceService
from backend.domain import ExternalResourceType

router = APIRouter(prefix="/api/project-library", tags=["project-library"])


def get_project_library_service(session=Depends(get_session), settings=Depends(get_settings)):
    from backend.infrastructure.project_library.portability import ProjectPortability
    resources = ExternalResourceRepository(session)
    registered = resources.get_by_type(ExternalResourceType.PROJECT_OUTPUT_ROOT)
    selected = registered.path if registered and registered.active else None
    # Explicit managed-library bindings stay authoritative. Ordinary instances
    # reuse their existing Settings location without relocating their database.
    if not settings.library_root and selected is not None:
        settings = replace(settings, projects_dir=selected)
    store = ProjectLibraryRepository(session)
    files = LibraryFiles(settings, destination_configured=bool(settings.library_root or selected))
    portability = ProjectPortability(store, files, settings)
    return ProjectLibraryService(store, settings, files=files, portability=portability,
        opener=lambda value: LocalFolderOpenGateway().open_directory(Path(value)),
        destination_writer=lambda root: ExternalResourceService(resources).upsert_resource(
            ExternalResourceType.PROJECT_OUTPUT_ROOT, root, True))


def checked(action):
    try:
        return action()
    except LookupError as error:
        raise HTTPException(404, str(error)) from error
    except (ProjectLibraryConflict, ValueError) as error:
        raise HTTPException(409, str(error)) from error
    except OSError as error:
        raise HTTPException(422, "The project location cannot be read or written. Check its connection and access, then review again.") from error


@router.get("/runtime", response_model=RuntimeResponse)
def runtime(service=Depends(get_project_library_service)):
    return checked(service.runtime)


@router.post("/destination", response_model=RuntimeResponse)
def destination(request: FolderRequest, service=Depends(get_project_library_service)):
    return checked(lambda: service.configure_destination(request.folder))


@router.post("/open-destination")
def open_destination(service=Depends(get_project_library_service)):
    return checked(service.open_destination)


@router.get("/members", response_model=MembersResponse)
def members(q: str = Query("", max_length=4096), batch_id: str | None = None, service=Depends(get_project_library_service)):
    return checked(lambda: service.members(q, batch_id))


@router.post("/scan", response_model=ScanResponse)
def scan(request: RootsRequest, service=Depends(get_project_library_service)):
    return checked(lambda: service.scan(request.roots))


@router.post("/intake-plan", response_model=IntakePlanResponse)
def intake_plan(request: IntakeRequest, service=Depends(get_project_library_service)):
    return checked(lambda: service.intake_plan(request.sources, [item.model_dump() for item in request.assignments]))


@router.post("/batches", response_model=BatchResponse)
def create_batch(request: BatchRequest, service=Depends(get_project_library_service)):
    return checked(lambda: service.create_batch(request.plan_id, request.fingerprint, request.selected, request.keep_separate, request.batch_id))


@router.get("/batches/{batch_id}", response_model=BatchResponse)
def batch(batch_id: str, service=Depends(get_project_library_service)):
    return checked(lambda: service.batch(batch_id))


@router.post("/batches/{batch_id}/resume", response_model=BatchResponse)
def resume(batch_id: str, service=Depends(get_project_library_service)):
    return checked(lambda: service.resume_batch(batch_id))


@router.get("/members/{member_id}", response_model=MemberResponse)
def member(member_id: str, service=Depends(get_project_library_service)):
    return checked(lambda: service.member(member_id))


@router.get("/members/{member_id}/files", response_model=FilesResponse)
def files(member_id: str, relative_path: str = Query("", max_length=4096), service=Depends(get_project_library_service)):
    return checked(lambda: service.files_list(member_id, relative_path))


@router.post("/members/{member_id}/open-folder")
def open_folder(member_id: str, service=Depends(get_project_library_service)):
    return checked(lambda: service.open_folder(member_id))


@router.post("/members/{member_id}/title-plan", response_model=ChangePlanResponse)
def title_plan(member_id: str, request: TitleRequest, service=Depends(get_project_library_service)):
    return checked(lambda: service.title_plan(member_id, request.title))


@router.post("/members/{member_id}/title", response_model=MemberResponse)
def title(member_id: str, request: ConfirmRequest, service=Depends(get_project_library_service)):
    return checked(lambda: service.change(member_id, request.plan_id, request.fingerprint, "title"))


@router.post("/members/{member_id}/location-plan", response_model=ChangePlanResponse)
def location_plan(member_id: str, request: FolderRequest, service=Depends(get_project_library_service)):
    return checked(lambda: service.location_plan(member_id, request.folder))


@router.post("/members/{member_id}/location", response_model=MemberResponse)
def location(member_id: str, request: ConfirmRequest, service=Depends(get_project_library_service)):
    return checked(lambda: service.change(member_id, request.plan_id, request.fingerprint, "location"))


@router.get("/members/{member_id}/portable", response_model=PortableInfoResponse)
def portable(member_id: str, service=Depends(get_project_library_service)):
    return checked(lambda: service.portable(member_id))


@router.post("/members/{member_id}/prepare", response_model=PortableInfoResponse)
def prepare(member_id: str, request: FingerprintRequest, service=Depends(get_project_library_service)):
    return checked(lambda: service.prepare(member_id, request.fingerprint))


@router.post("/inspect-portable", response_model=RestorePlanResponse)
@router.post("/restore-plan", response_model=RestorePlanResponse)
def restore_plan(request: RestoreFolderRequest, service=Depends(get_project_library_service)):
    return checked(lambda: service.restore_plan(request.folder, request.resolution))


@router.post("/restore", response_model=RestoreResponse)
def restore(request: RestoreConfirmRequest, service=Depends(get_project_library_service)):
    return checked(lambda: service.restore(request.plan_id, request.fingerprint, request.resolution))


@router.get("/members/{member_id}/takeover-plan", response_model=TakeoverPlanResponse)
def takeover_plan(member_id: str, service=Depends(get_project_library_service)):
    return checked(lambda: service.takeover_plan(member_id))


@router.post("/members/{member_id}/takeover", response_model=TakeoverResponse)
def takeover(member_id: str, request: ConfirmRequest, service=Depends(get_project_library_service)):
    return checked(lambda: service.takeover(member_id, request.plan_id, request.fingerprint))
