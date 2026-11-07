"""Serialize retained folder writers with the backend generation operation."""

from collections.abc import Iterator
from contextlib import ExitStack

from fastapi import Depends, HTTPException, Request

from backend.api.dependencies import get_settings
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.shared.config import Settings


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
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except OSError as exc:
            raise HTTPException(status_code=503, detail="Generation storage is unavailable. Retry when it is accessible.") from exc
        if operation is not None and operation["status"] != "completed":
            raise HTTPException(status_code=409,
                detail="Project folder generation is unfinished. Resume that operation before making separate folder changes.")
        from backend.infrastructure.files.report_delivery_receipt import ReportDeliveryReceipts
        try:
            delivery = ReportDeliveryReceipts(settings.data_dir / 'report_delivery').active(project_id)
        except (ValueError, OSError, RuntimeError) as exc:
            raise HTTPException(409, 'Report save recovery needs review. Retain report files and check the diagnostic record.') from exc
        from backend.infrastructure.storage.repositories.report_authoring import ReportAuthoringRepository
        try:
            projected = ReportAuthoringRepository.read_delivery_projection(settings, project_id)
        except Exception as exc:
            raise HTTPException(503, 'Report save recovery state cannot be read. Restore database access before writing project files.') from exc
        if (delivery is not None or (projected and projected.get('status') != 'completed')) and not request.url.path.endswith('/report-workspace/authoring/delivery/resume'):
            raise HTTPException(409, 'A reviewed report save is unfinished. Resume that save before changing project files.')
        yield
