"""Project identity helpers shared by read models and workspace planning."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from backend.domain import LtrRecord, LtrStatus, Project


@dataclass(frozen=True, slots=True)
class ProjectIdentity:
    """Business-readable project identity resolved from project and LTR setup data."""

    ltr_number: str | None
    sample_description: str | None
    test_item: str | None
    operator_note: str | None
    display_project_id: str
    display_project_id_kind: str
    has_registered_ltr: bool
    temporary_project_id: str | None
    registered_ltr_number: str | None


@dataclass(frozen=True, slots=True)
class ProjectDisplayIdentityOverride:
    """Local display identity override from confirmed Basic Information."""

    sample_description: str | None = None
    test_item: str | None = None


def resolve_project_identity(
    project: Project,
    ltrs: list[LtrRecord],
    *,
    identity_override: ProjectDisplayIdentityOverride | None = None,
) -> ProjectIdentity:
    """Resolve display and folder-naming identity from the current registered LTR."""
    ltr = select_registered_ltr(ltrs)
    setup = setup_payload_from_ltr_notes(ltr.notes if ltr else None)
    ltr_number = _text(ltr.ltr_number) if ltr else None
    temporary_project_id = _temporary_project_id(project.project_id)
    return ProjectIdentity(
        ltr_number=ltr_number,
        sample_description=(
            _text(identity_override.sample_description) if identity_override else None
        )
        or _text(project.product_name)
        or _text(setup.get("sample_description")),
        test_item=(
            _text(identity_override.test_item) if identity_override else None
        )
        or _text(setup.get("test_item")),
        operator_note=operator_note_from_ltr_notes(ltr.notes if ltr else None),
        display_project_id=ltr_number or temporary_project_id,
        display_project_id_kind="registered" if ltr_number else "temporary",
        has_registered_ltr=bool(ltr_number),
        temporary_project_id=None if ltr_number else temporary_project_id,
        registered_ltr_number=ltr_number,
    )


def display_identity_override_from_values(
    values: dict[str, str] | None,
) -> ProjectDisplayIdentityOverride | None:
    """Return a display identity override from confirmed Basic Information values."""
    if not values:
        return None
    override = ProjectDisplayIdentityOverride(
        sample_description=_text(values.get("product_description")),
        test_item=_text(values.get("test_item")),
    )
    if override.sample_description is None and override.test_item is None:
        return None
    return override


def select_registered_ltr(records: list[LtrRecord]) -> LtrRecord | None:
    """Return the latest registered LTR, falling back to the first available record."""
    registered = [record for record in records if record.status is LtrStatus.REGISTERED]
    candidates = registered or records
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda record: (
            getattr(record, "registered_on", None) is not None,
            getattr(record, "registered_on", None) or datetime.min.date(),
            _text(getattr(record, "ltr_number", None)) or "",
        ),
    )


def setup_payload_from_ltr_notes(notes: str | None) -> dict[str, Any]:
    """Return controlled New Project setup payload from an LTR audit note."""
    operator_note = _operator_note_payload(notes)
    if not isinstance(operator_note, dict):
        return {}
    if operator_note.get("source") != "new_project_setup_confirmation":
        return {}
    return operator_note


def operator_note_from_ltr_notes(notes: str | None) -> str | None:
    """Return plain operator note text without leaking structured audit JSON."""
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
    outer = _json_object(notes)
    if outer is None:
        return None
    raw = outer.get("operator_note")
    if not isinstance(raw, str):
        return None
    parsed = _json_object(raw)
    return parsed if isinstance(parsed, dict) else None


def _json_object(value: str | None) -> dict[str, Any] | None:
    if not value:
        return None
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    return text or None


def _temporary_project_id(project_id: str) -> str:
    return f"TMP-{project_id[:8].upper()}"
