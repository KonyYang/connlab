"""Best-effort portable snapshot refresh after committed lifecycle changes."""

from __future__ import annotations

from dataclasses import dataclass
import logging


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class AutomaticSnapshotResult:
    status: str
    message: str = ""


class AutomaticPortableSnapshotService:
    def __init__(self, store, portability) -> None:
        self._store = store
        self._portability = portability

    def refresh(self, project_id: str, *, locked=False, project_locked=False) -> AutomaticSnapshotResult:
        member = self._store.member_for_project(project_id)
        if member is None or self._store.workspace(project_id) is None:
            return AutomaticSnapshotResult("skipped")
        try:
            self._portability.prepare_latest(
                member,
                locked=locked,
                project_locked=project_locked,
                persist_member=False,
            )
        except Exception as exc:  # Business data is already committed; snapshot remains retryable.
            message = str(exc) or exc.__class__.__name__
            logger.warning("Automatic portable snapshot failed for project %s: %s", project_id, message)
            return AutomaticSnapshotResult("failed", message)
        return AutomaticSnapshotResult("updated")
