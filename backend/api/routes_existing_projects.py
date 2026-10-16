"""Thin HTTP seam for reviewed local associations; no source-folder writes."""
from typing import Literal
from urllib.parse import quote

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.api.dependencies import get_session, get_settings
from backend.api.routes_project_registry_management import _call
from backend.application.existing_project_service import ExistingProjectService
from backend.infrastructure.files.existing_project_gateway import ExistingProjectGateway
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.infrastructure.storage.repositories.existing_project import ExistingProjectRepository
from backend.infrastructure.storage.repositories.project_registry import ProjectRegistryRepository

router = APIRouter(prefix="/api/existing-projects", tags=["existing-projects"])


class _OpenedFileResponse(StreamingResponse):
    """Own the handle even when response.start fails before iteration begins."""

    def __init__(self, content, *, opened_file, **kwargs):
        self._opened_file = opened_file
        super().__init__(content, **kwargs)

    async def __call__(self, scope, receive, send):
        try:
            await super().__call__(scope, receive, send)
        finally:
            self._opened_file.close()


def get_service(session=Depends(get_session), settings=Depends(get_settings)):
    return ExistingProjectService(ExistingProjectRepository(session), ProjectRegistryRepository(session),
        ExistingProjectGateway(), GenerationJournal(settings.data_dir / "project_folder_generation"))


class PathRequest(BaseModel):
    path: str = Field(min_length=1, max_length=4096)


class ScanRequest(BaseModel):
    roots: list[str] = Field(min_length=1, max_length=10)
    depth: int = Field(default=1, ge=0, le=3)


class RegisterRequest(PathRequest):
    token: str = Field(min_length=1, max_length=128)
    action: Literal["register", "independent", "link", "skip"]
    management_number: str = Field(default="", max_length=128)
    target_project_id: str | None = Field(default=None, max_length=64)
    ignore_manifest: bool = False


class RelocateRequest(PathRequest):
    token: str = Field(min_length=1, max_length=128)


def _safe(action):
    def run():
        try:
            return action()
        except OSError as exc:
            raise ValueError("Folder or file is unavailable. Check its location and permissions, then retry or review relocation.") from exc
    return _call(run)


@router.post("/scan")
def scan(request: ScanRequest, service=Depends(get_service)):
    return _safe(lambda: service.scan(**request.model_dump()))


@router.post("/preview")
def preview(request: PathRequest, service=Depends(get_service)):
    return _safe(lambda: service.preview(request.path))


@router.post("/register")
def register(request: RegisterRequest, service=Depends(get_service)):
    return _safe(lambda: service.register(**request.model_dump()))


@router.get("/locations")
def locations(project_id: str | None = None, service=Depends(get_service)):
    return _safe(lambda: service.list_locations(project_id))


@router.get("/locations/{location_id}/files")
def files(location_id: str, relative: str = "", service=Depends(get_service)):
    return _safe(lambda: service.files(location_id, relative))


@router.get("/locations/{location_id}/download")
def download(location_id: str, relative: str, service=Depends(get_service)):
    opened, filename = _safe(lambda: service.open_file(location_id, relative))
    def chunks():
        try:
            while data := opened.read(65536):
                yield data
        finally:
            opened.close()
    return _OpenedFileResponse(chunks(), opened_file=opened, media_type="application/octet-stream", headers={
        "Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}", "X-Content-Type-Options": "nosniff"})


@router.post("/locations/{location_id}/relocation-preview")
def relocation_preview(location_id: str, request: PathRequest, service=Depends(get_service)):
    return _safe(lambda: service.preview_relocation(location_id, request.path))


@router.post("/locations/{location_id}/relocate")
def relocate(location_id: str, request: RelocateRequest, service=Depends(get_service)):
    return _safe(lambda: service.relocate(location_id, **request.model_dump()))
