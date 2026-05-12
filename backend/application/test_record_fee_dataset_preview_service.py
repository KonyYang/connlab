"""Read-only dataset preview for test records and fee evaluation inputs."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any, Protocol

from backend.domain import Project, ProjectTestPlanDraft, ProjectTestPlanDraftStatus


class TestRecordFeeDatasetPreviewError(ValueError):
    """Raised when a dataset preview request is invalid."""


class TestRecordFeeDatasetPreviewNotFoundError(LookupError):
    """Raised when Project or draft data cannot be found."""


class TestRecordFeeProjectStore(Protocol):
    """Project lookup operations needed by the dataset preview service."""

    def get(self, project_id: str) -> Project | None:
        """Return a Project by id."""


class TestRecordFeeDraftStore(Protocol):
    """Project test-plan draft lookup operations needed by the preview service."""

    def get(self, draft_id: str) -> ProjectTestPlanDraft | None:
        """Return a Project test-plan draft by id."""


@dataclass(frozen=True, slots=True)
class TestRecordFeeDatasetPreviewCommand:
    """Input for building test record and fee dataset previews."""

    project_id: str
    draft_id: str
    include_test_record_dataset: bool = True
    include_fee_dataset: bool = True


@dataclass(frozen=True, slots=True)
class TestRecordStepDataset:
    """One test step row for future test record generation."""

    sequence: int | None
    test_item: str | None
    condition_summary: str | None
    method_summary: str | None
    reference_standard: str | None
    judgement_criteria: str | None
    duration_hint: str | None
    source_section: str | None
    source_table_index: int | None
    source_row_index: int | None
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TestRecordGroupDataset:
    """One test group dataset for future test record generation."""

    group_key: str
    group_label: str
    source_table_index: int | None
    steps: tuple[TestRecordStepDataset, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TestRecordDataset:
    """Structured test record input dataset preview."""

    groups: tuple[TestRecordGroupDataset, ...]


@dataclass(frozen=True, slots=True)
class FeeDatasetSummary:
    """Summary fields for fee evaluation input preview."""

    group_count: int
    step_count: int
    explicit_duration_days: int


@dataclass(frozen=True, slots=True)
class FeeLineItemDataset:
    """One fee evaluation line candidate."""

    group_label: str
    sequence: int | None
    description: str
    duration_hint: str | None
    quantity_basis: str
    pricing_status: str
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FeeDataset:
    """Structured fee evaluation input dataset preview."""

    summary: FeeDatasetSummary
    line_items: tuple[FeeLineItemDataset, ...]


@dataclass(frozen=True, slots=True)
class TestRecordFeeDatasetPreview:
    """Read-only dataset preview for downstream document generation."""

    project_id: str
    draft_id: str
    source_document_name: str
    test_record_dataset: TestRecordDataset | None
    fee_dataset: FeeDataset | None
    warnings: tuple[str, ...]


class TestRecordFeeDatasetPreviewService:
    """Build template-neutral test record and fee input datasets from a draft."""

    def __init__(
        self,
        *,
        project_store: TestRecordFeeProjectStore,
        draft_store: TestRecordFeeDraftStore,
    ) -> None:
        """Create the service with repository ports."""
        self._projects = project_store
        self._drafts = draft_store

    def preview(
        self,
        command: TestRecordFeeDatasetPreviewCommand,
    ) -> TestRecordFeeDatasetPreview:
        """Build read-only datasets without generating or writing files."""
        if not command.include_test_record_dataset and not command.include_fee_dataset:
            raise TestRecordFeeDatasetPreviewError(
                "At least one dataset must be requested."
            )
        project = self._require_project(command.project_id)
        draft = self._require_draft(command.project_id, command.draft_id)
        payload = _load_payload(draft.payload_json)
        groups, warnings = _groups_from_payload(payload)
        test_record_dataset = TestRecordDataset(groups=tuple(groups)) if command.include_test_record_dataset else None
        fee_dataset = _fee_dataset(project, groups) if command.include_fee_dataset else None
        if not groups:
            warnings.append("No test groups were available for dataset preview.")
        return TestRecordFeeDatasetPreview(
            project_id=command.project_id,
            draft_id=command.draft_id,
            source_document_name=draft.source_document_name,
            test_record_dataset=test_record_dataset,
            fee_dataset=fee_dataset,
            warnings=tuple(warnings),
        )

    def _require_project(self, project_id: str) -> Project:
        project = self._projects.get(project_id)
        if project is None:
            raise TestRecordFeeDatasetPreviewNotFoundError(f"Project not found: {project_id}")
        return project

    def _require_draft(self, project_id: str, draft_id: str) -> ProjectTestPlanDraft:
        draft = self._drafts.get(draft_id)
        if draft is None or draft.project_id != project_id:
            raise TestRecordFeeDatasetPreviewNotFoundError(
                f"Project test-plan draft not found for project: {project_id}"
            )
        if draft.status is ProjectTestPlanDraftStatus.SUPERSEDED:
            raise TestRecordFeeDatasetPreviewError(
                "Superseded drafts cannot be used for dataset preview."
            )
        return draft


def _groups_from_payload(
    payload: dict[str, Any],
) -> tuple[list[TestRecordGroupDataset], list[str]]:
    """Build test-record groups from a draft payload."""
    raw_groups = payload.get("groups")
    if not isinstance(raw_groups, list):
        return [], ["Draft payload does not contain a groups list."]
    groups: list[TestRecordGroupDataset] = []
    warnings: list[str] = []
    for group_index, raw_group in enumerate(raw_groups, start=1):
        if not isinstance(raw_group, dict):
            warnings.append(f"Group entry {group_index} is not an object.")
            continue
        group_label = _text(raw_group.get("group_label")) or f"Group {group_index}"
        group_key = _text(raw_group.get("group_key")) or _group_key(group_label)
        steps, step_warnings = _steps_from_group(raw_group, group_label)
        warnings.extend(step_warnings)
        group_warnings: list[str] = []
        if not steps:
            group_warnings.append(f"{group_label} has no test steps.")
        groups.append(
            TestRecordGroupDataset(
                group_key=group_key,
                group_label=group_label,
                source_table_index=_int_or_none(raw_group.get("source_table_index")),
                steps=tuple(steps),
                warnings=tuple(group_warnings),
            )
        )
    return groups, warnings


def _steps_from_group(
    group: dict[str, Any],
    group_label: str,
) -> tuple[list[TestRecordStepDataset], list[str]]:
    """Build step datasets for one group."""
    raw_steps = group.get("steps")
    if not isinstance(raw_steps, list):
        return [], [f"{group_label} does not contain a steps list."]
    steps: list[TestRecordStepDataset] = []
    warnings: list[str] = []
    for index, raw_step in enumerate(raw_steps, start=1):
        if not isinstance(raw_step, dict):
            warnings.append(f"{group_label} step entry {index} is not an object.")
            continue
        step = _step_from_payload(raw_step)
        if step.warnings:
            warnings.extend(f"{group_label} step {index}: {item}" for item in step.warnings)
        steps.append(step)
    return steps, warnings


def _step_from_payload(step: dict[str, Any]) -> TestRecordStepDataset:
    """Build one test-record step dataset row."""
    missing: list[str] = []
    condition_summary = _text(step.get("condition_summary"))
    method_summary = _text(step.get("method_summary"))
    reference_standard = _text(step.get("reference_standard"))
    judgement_criteria = _text(step.get("judgement_criteria"))
    for key, value in (
        ("condition_summary", condition_summary),
        ("method_summary", method_summary),
        ("reference_standard", reference_standard),
        ("judgement_criteria", judgement_criteria),
    ):
        if not value:
            missing.append(f"{key} is missing.")
    duration_hint = _duration_hint(step)
    if duration_hint is None:
        missing.append("duration_hint is missing.")
    return TestRecordStepDataset(
        sequence=_int_or_none(step.get("sequence")),
        test_item=_text(step.get("test_item")) or _text(step.get("step_label")),
        condition_summary=condition_summary,
        method_summary=method_summary,
        reference_standard=reference_standard,
        judgement_criteria=judgement_criteria,
        duration_hint=duration_hint,
        source_section=_text(step.get("source_section")),
        source_table_index=_int_or_none(step.get("source_table_index")),
        source_row_index=_int_or_none(step.get("source_row_index")),
        warnings=tuple(missing),
    )


def _fee_dataset(project: Project, groups: list[TestRecordGroupDataset]) -> FeeDataset:
    """Build fee line candidates without calculating prices."""
    line_items: list[FeeLineItemDataset] = []
    explicit_duration = 0.0
    for group in groups:
        for step in group.steps:
            explicit_duration += _duration_days_from_hint(step.duration_hint)
            description = step.test_item or step.method_summary or "Unspecified test step"
            warnings = ["No pricing source is configured for this fee line."]
            if step.duration_hint is None:
                warnings.append("Duration is missing for this fee line.")
            line_items.append(
                FeeLineItemDataset(
                    group_label=group.group_label,
                    sequence=step.sequence,
                    description=description,
                    duration_hint=step.duration_hint,
                    quantity_basis=_quantity_basis(project),
                    pricing_status="price_source_missing",
                    warnings=tuple(warnings),
                )
            )
    return FeeDataset(
        summary=FeeDatasetSummary(
            group_count=len(groups),
            step_count=sum(len(group.steps) for group in groups),
            explicit_duration_days=math.ceil(explicit_duration),
        ),
        line_items=tuple(line_items),
    )


def _duration_hint(step: dict[str, Any]) -> str | None:
    """Return a stable duration hint string from known payload keys."""
    for key in ("estimated_duration_hint", "duration_hint"):
        value = _text(step.get(key))
        if value:
            return value
    days = step.get("estimated_duration_days", step.get("duration_days"))
    if isinstance(days, int | float) and days >= 0:
        return f"{days:g} day(s)"
    hours = step.get("estimated_duration_hours")
    if isinstance(hours, int | float) and hours >= 0:
        return f"{hours:g} hour(s)"
    return None


def _duration_days_from_hint(value: str | None) -> float:
    """Extract duration days from simple duration hint strings."""
    if not value:
        return 0.0
    parts = value.split()
    if not parts:
        return 0.0
    try:
        amount = float(parts[0])
    except ValueError:
        return 0.0
    unit = value.lower()
    if "hour" in unit:
        return amount / 24
    if "day" in unit:
        return amount
    return 0.0


def _quantity_basis(project: Project) -> str:
    """Return a conservative quantity basis for fee line candidates."""
    product = project.product_name.strip() if project.product_name else "project sample"
    return f"Review required for {product} sample quantity."


def _load_payload(payload_json: str) -> dict[str, Any]:
    """Load a JSON object payload from a persisted draft."""
    try:
        payload = json.loads(payload_json)
    except json.JSONDecodeError as exc:
        raise TestRecordFeeDatasetPreviewError(
            "Project test-plan draft payload is not valid JSON."
        ) from exc
    if not isinstance(payload, dict):
        raise TestRecordFeeDatasetPreviewError(
            "Project test-plan draft payload must be an object."
        )
    return payload


def _text(value: Any) -> str | None:
    if isinstance(value, str):
        text = value.strip()
        return text or None
    return None


def _int_or_none(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def _group_key(label: str) -> str:
    return "_".join(part for part in label.lower().split() if part) or "group"
