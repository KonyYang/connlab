"""Read-only Project registry summary rows for the frontend registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from backend.application.project_identity import resolve_project_identity
from backend.domain import LtrRecord, Project, ProjectTemporaryContext


class ProjectRegistryProjectStore(Protocol):
    """Project read behavior required by the registry summary service."""

    def list(self) -> list[Project]:
        """Return all projects."""


class ProjectRegistryLtrStore(Protocol):
    """LTR read behavior required by the registry summary service."""

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        """Return LTR records linked to a project."""


class ProjectRegistryTemporaryContextStore(Protocol):
    """Temporary context read behavior required by the registry summary service."""

    def get_by_project(self, project_id: str) -> ProjectTemporaryContext | None:
        """Return temporary planning context linked to a project."""


@dataclass(frozen=True, slots=True)
class ProjectRegistryRow:
    """Single read-only row for the Project registry table."""

    project_id: str
    ltr_number: str | None
    sample_description: str | None
    test_item: str | None
    requestor: str
    business_unit: str | None
    status: str
    progress: int
    notes: str | None
    display_project_id: str
    display_project_id_kind: str
    has_registered_ltr: bool
    temporary_project_id: str | None
    registered_ltr_number: str | None
    temporary_source_asset_ids: tuple[str, ...] = ()


class ProjectRegistrySummaryService:
    """Build display-ready registry rows without frontend data parsing."""

    def __init__(
        self,
        *,
        project_store: ProjectRegistryProjectStore,
        ltr_store: ProjectRegistryLtrStore,
        temporary_context_store: ProjectRegistryTemporaryContextStore | None = None,
    ) -> None:
        """Create the service with read-only stores."""
        self._projects = project_store
        self._ltrs = ltr_store
        self._temporary_contexts = temporary_context_store

    def list_rows(self) -> list[ProjectRegistryRow]:
        """Return registry summary rows for all projects."""
        rows: list[ProjectRegistryRow] = []
        for project in self._projects.list():
            identity = resolve_project_identity(
                project,
                self._ltrs.list_by_project(project.project_id),
            )
            temporary_context = (
                self._temporary_contexts.get_by_project(project.project_id)
                if self._temporary_contexts is not None
                else None
            )
            rows.append(
                ProjectRegistryRow(
                    project_id=project.project_id,
                    ltr_number=identity.ltr_number,
                    sample_description=_first_text(
                        temporary_context.sample_description if temporary_context else None,
                        identity.sample_description,
                    ),
                    test_item=_first_text(
                        temporary_context.test_item if temporary_context else None,
                        identity.test_item,
                    ),
                    requestor=project.requestor,
                    business_unit=project.business_unit,
                    status=project.status.value,
                    progress=_status_progress(project.status.value),
                    notes=_first_text(
                        temporary_context.notes if temporary_context else None,
                        identity.operator_note,
                    ),
                    display_project_id=identity.display_project_id,
                    display_project_id_kind=identity.display_project_id_kind,
                    has_registered_ltr=identity.has_registered_ltr,
                    temporary_project_id=identity.temporary_project_id,
                    registered_ltr_number=identity.registered_ltr_number,
                    temporary_source_asset_ids=(
                        temporary_context.source_asset_ids if temporary_context else ()
                    ),
                )
            )
        return rows

    def get_row(self, project_id: str) -> ProjectRegistryRow | None:
        """Return one registry summary row by project id."""
        for row in self.list_rows():
            if row.project_id == project_id:
                return row
        return None


def _status_progress(status: str) -> int:
    """Return display progress for a Project lifecycle status."""
    values = {
        "cancelled": 0,
        "closed": 100,
        "confirmed": 45,
        "draft": 10,
        "folder_created": 100,
        "intake_received": 25,
        "ltr_registered": 70,
        "precheck_failed": 35,
        "precheck_passed": 55,
        "precheck_pending": 30,
    }
    return values.get(status, 20)


def _first_text(*values: str | None) -> str | None:
    for value in values:
        if not isinstance(value, str):
            continue
        text = value.strip()
        if text:
            return text
    return None
