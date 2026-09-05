"""Serialize retained folder writers with the backend generation operation."""

from collections.abc import Iterator
from contextlib import ExitStack

from fastapi import Depends, HTTPException

from backend.api.dependencies import get_settings
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.shared.config import Settings


def require_project_folder_write_slot(
    project_id: str, settings: Settings = Depends(get_settings),
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
        yield
