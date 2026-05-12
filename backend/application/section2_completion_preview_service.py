"""Read-only Section 2 completion preview from Project test-plan drafts."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Protocol

from backend.domain import Project, ProjectTestPlanDraft, ProjectTestPlanDraftStatus


class Section2CompletionPreviewError(ValueError):
    """Raised when a Section 2 preview request is invalid."""


class Section2CompletionPreviewNotFoundError(LookupError):
    """Raised when Project or draft data cannot be found."""


class Section2ProjectStore(Protocol):
    """Project lookup operations needed by the Section 2 preview service."""

    def get(self, project_id: str) -> Project | None:
        """Return a Project by id."""


class Section2DraftStore(Protocol):
    """Project test-plan draft lookup operations needed by the preview service."""

    def get(self, draft_id: str) -> ProjectTestPlanDraft | None:
        """Return a Project test-plan draft by id."""


@dataclass(frozen=True, slots=True)
class Section2CompletionPreviewCommand:
    """Input for computing a read-only Section 2 completion preview."""

    project_id: str
    draft_id: str
    received_date: date
    lab: str | None = None
    assigned_personnel: str | None = None
    sample_condition: str | None = None
    sample_preparation_days: int = 1
    test_group_scheduling_buffer_days: int = 1
    report_drafting_days: int = 3
    review_days: int = 1


@dataclass(frozen=True, slots=True)
class Section2DurationSummary:
    """Duration components used by the Section 2 preview."""

    sample_preparation_days: int
    test_group_scheduling_buffer_days: int
    explicit_test_duration_days: int
    report_drafting_days: int
    review_days: int
    total_estimated_days: int
    duration_basis: str


@dataclass(frozen=True, slots=True)
class Section2CompletionPreview:
    """Read-only preview of application-form Section 2 values."""

    project_id: str
    draft_id: str
    source_document_name: str
    received_date: date
    estimated_completion_date: date
    lab: str | None
    assigned_personnel: str | None
    sample_condition: str | None
    test_demand_summary: str
    duration_summary: Section2DurationSummary
    warnings: tuple[str, ...]


class Section2CompletionPreviewService:
    """Compute Section 2 preview fields from Project-stage planning data."""

    def __init__(
        self,
        *,
        project_store: Section2ProjectStore,
        draft_store: Section2DraftStore,
    ) -> None:
        """Create the service with repository ports."""
        self._projects = project_store
        self._drafts = draft_store

    def preview(self, command: Section2CompletionPreviewCommand) -> Section2CompletionPreview:
        """Compute Section 2 values without mutating source files or drafts."""
        self._require_project(command.project_id)
        draft = self._require_draft(command.project_id, command.draft_id)
        payload = _load_payload(draft.payload_json)
        warnings: list[str] = []
        test_demand_summary = _build_test_demand_summary(payload)
        if not test_demand_summary:
            warnings.append("No test groups or steps were available for Section 2 summary.")
            test_demand_summary = "No test demand summary available."
        explicit_days, duration_warnings = _extract_explicit_duration_days(payload)
        warnings.extend(duration_warnings)
        duration_summary = _build_duration_summary(command, explicit_days)
        estimated_completion_date = command.received_date + timedelta(
            days=duration_summary.total_estimated_days
        )
        return Section2CompletionPreview(
            project_id=command.project_id,
            draft_id=command.draft_id,
            source_document_name=draft.source_document_name,
            received_date=command.received_date,
            estimated_completion_date=estimated_completion_date,
            lab=_optional_text(command.lab),
            assigned_personnel=_optional_text(command.assigned_personnel),
            sample_condition=_optional_text(command.sample_condition),
            test_demand_summary=test_demand_summary,
            duration_summary=duration_summary,
            warnings=tuple(warnings),
        )

    def _require_project(self, project_id: str) -> Project:
        project = self._projects.get(project_id)
        if project is None:
            raise Section2CompletionPreviewNotFoundError(f"Project not found: {project_id}")
        return project

    def _require_draft(self, project_id: str, draft_id: str) -> ProjectTestPlanDraft:
        draft = self._drafts.get(draft_id)
        if draft is None or draft.project_id != project_id:
            raise Section2CompletionPreviewNotFoundError(
                f"Project test-plan draft not found for project: {project_id}"
            )
        if draft.status is ProjectTestPlanDraftStatus.SUPERSEDED:
            raise Section2CompletionPreviewError("Superseded drafts cannot be used for Section 2 preview.")
        return draft


def _build_duration_summary(
    command: Section2CompletionPreviewCommand,
    explicit_test_duration_days: int,
) -> Section2DurationSummary:
    """Build a validated duration summary."""
    sample_preparation_days = _non_negative_int(
        command.sample_preparation_days,
        "sample_preparation_days",
    )
    test_group_scheduling_buffer_days = _non_negative_int(
        command.test_group_scheduling_buffer_days,
        "test_group_scheduling_buffer_days",
    )
    report_drafting_days = _non_negative_int(
        command.report_drafting_days,
        "report_drafting_days",
    )
    review_days = _non_negative_int(command.review_days, "review_days")
    total = (
        sample_preparation_days
        + test_group_scheduling_buffer_days
        + explicit_test_duration_days
        + report_drafting_days
        + review_days
    )
    return Section2DurationSummary(
        sample_preparation_days=sample_preparation_days,
        test_group_scheduling_buffer_days=test_group_scheduling_buffer_days,
        explicit_test_duration_days=explicit_test_duration_days,
        report_drafting_days=report_drafting_days,
        review_days=review_days,
        total_estimated_days=total,
        duration_basis="calendar_days_preview",
    )


def _build_test_demand_summary(payload: dict[str, Any]) -> str:
    """Build a compact operator-readable summary from draft groups and steps."""
    groups = payload.get("groups")
    if not isinstance(groups, list):
        return ""
    parts: list[str] = []
    for group in groups:
        if not isinstance(group, dict):
            continue
        group_label = _first_text(group.get("group_label"), group.get("group_key"), default="Group")
        step_labels = _step_labels(group.get("steps"))
        if step_labels:
            parts.append(f"{group_label}: {', '.join(step_labels)}")
        else:
            parts.append(group_label)
    return "; ".join(parts)


def _step_labels(steps: Any) -> list[str]:
    """Return stable step labels from a group payload."""
    if not isinstance(steps, list):
        return []
    labels: list[str] = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        label = _first_text(
            step.get("test_item"),
            step.get("step_label"),
            step.get("method_summary"),
            step.get("reference_standard"),
        )
        if label:
            labels.append(label)
    return labels


def _extract_explicit_duration_days(payload: dict[str, Any]) -> tuple[int, list[str]]:
    """Extract deterministic duration-day hints already present in draft payload."""
    duration_values: list[float] = []
    groups = payload.get("groups")
    if isinstance(groups, list):
        for group in groups:
            if not isinstance(group, dict):
                continue
            steps = group.get("steps")
            if not isinstance(steps, list):
                continue
            for step in steps:
                if isinstance(step, dict):
                    value = _duration_days_from_step(step)
                    if value is not None:
                        duration_values.append(value)
    if not duration_values:
        return 0, ["No explicit test duration was found in the Project test-plan draft."]
    return math.ceil(sum(duration_values)), []


def _duration_days_from_step(step: dict[str, Any]) -> float | None:
    """Read a duration day value from known draft payload keys."""
    for key in ("estimated_duration_days", "duration_days"):
        value = step.get(key)
        if isinstance(value, int | float) and value >= 0:
            return float(value)
    hours = step.get("estimated_duration_hours")
    if isinstance(hours, int | float) and hours >= 0:
        return float(hours) / 24
    return None


def _load_payload(payload_json: str) -> dict[str, Any]:
    """Load a JSON object payload from a persisted draft."""
    try:
        payload = json.loads(payload_json)
    except json.JSONDecodeError as exc:
        raise Section2CompletionPreviewError("Project test-plan draft payload is not valid JSON.") from exc
    if not isinstance(payload, dict):
        raise Section2CompletionPreviewError("Project test-plan draft payload must be an object.")
    return payload


def _first_text(*values: Any, default: str = "") -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return default


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _non_negative_int(value: int, field_name: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise Section2CompletionPreviewError(f"{field_name} must be a non-negative integer.")
    return value
