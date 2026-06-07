"""Read-only Project registry summary rows for the frontend registry."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol

from backend.domain import LtrRecord, LtrStatus, Project


class ProjectRegistryProjectStore(Protocol):
    """Project read behavior required by the registry summary service."""

    def list(self) -> list[Project]:
        """Return all projects."""


class ProjectRegistryLtrStore(Protocol):
    """LTR read behavior required by the registry summary service."""

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        """Return LTR records linked to a project."""


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


class ProjectRegistrySummaryService:
    """Build display-ready registry rows without frontend data parsing."""

    def __init__(
        self,
        *,
        project_store: ProjectRegistryProjectStore,
        ltr_store: ProjectRegistryLtrStore,
    ) -> None:
        """Create the service with read-only stores."""
        self._projects = project_store
        self._ltrs = ltr_store

    def list_rows(self) -> list[ProjectRegistryRow]:
        """Return registry summary rows for all projects."""
        rows: list[ProjectRegistryRow] = []
        for project in self._projects.list():
            ltr = _registered_ltr(self._ltrs.list_by_project(project.project_id))
            setup = _setup_payload(ltr.notes if ltr else None)
            rows.append(
                ProjectRegistryRow(
                    project_id=project.project_id,
                    ltr_number=ltr.ltr_number if ltr else None,
                    sample_description=_text(setup.get("sample_description")),
                    test_item=_text(setup.get("test_item")),
                    requestor=project.requestor,
                    business_unit=project.business_unit,
                    status=project.status.value,
                    progress=_status_progress(project.status.value),
                    notes=_operator_note(ltr.notes if ltr else None),
                )
            )
        return rows


def _registered_ltr(records: list[LtrRecord]) -> LtrRecord | None:
    """Return the first registered LTR record for a project."""
    for record in records:
        if record.status is LtrStatus.REGISTERED:
            return record
    return records[0] if records else None


def _setup_payload(notes: str | None) -> dict[str, Any]:
    """Return controlled New Project setup payload from LTR notes."""
    operator_note = _operator_note_payload(notes)
    if not isinstance(operator_note, dict):
        return {}
    if operator_note.get("source") != "new_project_setup_confirmation":
        return {}
    return operator_note


def _operator_note(notes: str | None) -> str | None:
    """Return only operator-facing note text from LTR audit notes."""
    outer = _json_object(notes)
    if outer is None:
        return _text(notes)
    raw = outer.get("operator_note")
    if not isinstance(raw, str):
        return None
    if isinstance(_json_object(raw), dict):
        return None
    return _text(raw)


def _operator_note_payload(notes: str | None) -> dict[str, Any] | None:
    """Return parsed operator note payload when it is structured JSON."""
    outer = _json_object(notes)
    if outer is None:
        return None
    raw = outer.get("operator_note")
    if not isinstance(raw, str):
        return None
    parsed = _json_object(raw)
    return parsed if isinstance(parsed, dict) else None


def _json_object(value: str | None) -> dict[str, Any] | None:
    """Parse a JSON object, returning None for non-object or invalid values."""
    if not value:
        return None
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _text(value: Any) -> str | None:
    """Return stripped non-empty text."""
    if not isinstance(value, str):
        return None
    text = value.strip()
    return text or None


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
