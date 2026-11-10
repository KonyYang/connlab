"""Serialize retained folder writers with the backend generation operation."""

from collections.abc import Iterator
from contextlib import ExitStack

from fastapi import Depends, HTTPException, Request

from backend.api.dependencies import get_settings
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.shared.config import Settings
from backend.application.project_file_generation_guard import require_project_file_generation_clear
from backend.infrastructure.files.project_file_generation_journal import ProjectFileGenerationJournal


def require_project_folder_write_slot(
    project_id: str, request: Request, settings: Settings = Depends(get_settings),
) -> Iterator[None]:
    """Acquire before service/session dependencies; release after their commit.

    A queued or interrupted operation retains its files even without a live worker,
    so acquiring the OS lock alone does not authorize a separate legacy write.
    """
    journal = GenerationJournal(settings.data_dir / "project_folder_generation")
    with ExitStack() as stack:
        try:
            stack.enter_context(journal.lock(project_id))
            operation = journal.read(project_id)
            require_project_file_generation_clear(ProjectFileGenerationJournal(settings.data_dir / "project_file_generation"), project_id)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except OSError as exc:
            raise HTTPException(status_code=503, detail="Generation storage is unavailable. Retry when it is accessible.") from exc
        if operation is not None and operation["status"] != "completed":
            raise HTTPException(status_code=409,
                detail="Project folder generation is unfinished. Resume that operation before making separate folder changes.")
        basic = GenerationJournal(settings.data_dir / "basic_project_workspace").read(project_id)
        if basic and basic["status"] != "completed":
            raise HTTPException(409, "Basic project folder creation is unfinished. Resume it before changing project files.")
        if not request.url.path.endswith('/report-workspace/authoring/delivery/resume'):
            try:
                require_report_delivery_clear(settings, project_id)
            except ValueError as exc:
                raise HTTPException(409, str(exc)) from exc
        yield


def require_report_delivery_clear(settings, project_id):
    from backend.infrastructure.files.report_delivery_receipt import ReportDeliveryReceipts
    from backend.infrastructure.storage.repositories.report_authoring import ReportAuthoringRepository
    try:
        delivery = ReportDeliveryReceipts(settings.data_dir / 'report_delivery').active(project_id)
        projected = ReportAuthoringRepository.read_delivery_projection(settings, project_id)
    except (ValueError, OSError, RuntimeError) as exc:
        raise ValueError("Report save recovery state cannot be read. Retain files and restore access before writing.") from exc
    if delivery is not None or (projected and projected.get('status') != 'completed'):
        raise ValueError("A reviewed report save is unfinished. Resume that save before changing project files.")
