"""Ordinary report shortcut metadata; never report authority."""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from backend.api.dependencies import get_session, get_settings, get_project_registry_summary_service
from backend.api.routes_material_receipts import checked
from backend.application.project_library.report_shortcuts import ReportShortcutService
from backend.infrastructure.storage.repositories.report_shortcuts import ReportShortcutRepository
from backend.infrastructure.storage.repositories.library_search import LibrarySearchRepository
from backend.infrastructure.project_library.material_receipt_files import MaterialReceiptFiles

router = APIRouter(prefix="/api/project-library/report-shortcuts", tags=["material-reports"])


def get_report_shortcut_service(session=Depends(get_session), settings=Depends(get_settings)):
    return ReportShortcutService(ReportShortcutRepository(session), MaterialReceiptFiles(settings),
        LibrarySearchRepository(session, get_project_registry_summary_service(session)))


class ClearShortcutRequest(BaseModel):
    key: str = Field(min_length=1, max_length=256)
    role: str = Field(pattern="^(internal|customer)$")
    expected_path: str | None = Field(default=None, max_length=4096)


class SetShortcutRequest(ClearShortcutRequest):
    relative_path: str = Field(min_length=1, max_length=4096)
    replacement_confirmed: bool = False


@router.get("")
def list_shortcuts(key: str = Query(..., min_length=1, max_length=256), service=Depends(get_report_shortcut_service)):
    return checked(lambda: service.list(key))


@router.post("/set")
def set_shortcut(request: SetShortcutRequest, service=Depends(get_report_shortcut_service)):
    return checked(lambda: service.set(**request.model_dump()))


@router.post("/clear")
def clear_shortcut(request: ClearShortcutRequest, service=Depends(get_report_shortcut_service)):
    return checked(lambda: service.clear(**request.model_dump()))
