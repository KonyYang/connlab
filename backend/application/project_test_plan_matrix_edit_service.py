"""Application service for Matrix draft edit, validate, and confirm."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from backend.application.project_test_plan_draft_service import (
    CreateProjectTestPlanDraftCommand,
    ProjectTestPlanDraftError,
    ProjectTestPlanDraftNotFoundError,
    ProjectTestPlanDraftService,
    UpdateProjectTestPlanDraftCommand,
)
from backend.domain import ProjectTestPlanDraft, ProjectTestPlanDraftStatus
from backend.modules.test_plan.matrix_step_sequence_validation import (
    parse_step_tokens,
    validate_group_step_sequences,
)


class ProjectTestPlanMatrixEditError(ValueError):
    """Raised when Matrix edit/confirm payload is invalid."""


class ProjectTestPlanMatrixEditNotFoundError(LookupError):
    """Raised when Project or draft cannot be found."""


@dataclass(frozen=True, slots=True)
class UpdateProjectTestPlanMatrixCommand:
    """Input for persisted Matrix draft edit."""

    project_id: str
    draft_id: str
    groups: list[dict[str, Any]]


@dataclass(frozen=True, slots=True)
class ValidateProjectTestPlanMatrixCommand:
    """Input for Matrix draft validation."""

    project_id: str
    draft_id: str
    groups: list[dict[str, Any]] | None = None


@dataclass(frozen=True, slots=True)
class ConfirmProjectTestPlanMatrixCommand:
    """Input for Matrix draft confirmation."""

    project_id: str
    draft_id: str
    groups: list[dict[str, Any]] | None = None


@dataclass(frozen=True, slots=True)
class MatrixValidationSummary:
    """Matrix validation summary used by API/frontend."""

    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    group_count: int
    step_count: int


@dataclass(frozen=True, slots=True)
class MatrixDraftEditResult:
    """Result for Matrix edit/confirm operations."""

    draft: ProjectTestPlanDraft
    validation: MatrixValidationSummary
    created_new_draft: bool


class ProjectTestPlanMatrixEditService:
    """Edit, validate, and confirm Project Matrix draft payload."""

    def __init__(self, *, draft_service: ProjectTestPlanDraftService) -> None:
        self._drafts = draft_service

    def update_matrix_draft(
        self,
        command: UpdateProjectTestPlanMatrixCommand,
    ) -> MatrixDraftEditResult:
        draft = self._require_draft(command.project_id, command.draft_id)
        summary, normalized_groups = _normalize_and_validate_groups(command.groups)
        payload = {
            "groups": normalized_groups,
            "warnings": list(summary.warnings),
            "blockers": list(summary.blockers),
        }
        try:
            if draft.status is ProjectTestPlanDraftStatus.REVIEWED:
                updated = self._drafts.create_draft(
                    CreateProjectTestPlanDraftCommand(
                        project_id=command.project_id,
                        source_document_path=draft.source_document_path,
                        source_document_name=draft.source_document_name,
                        source_format=draft.source_format,
                        source_asset_id=draft.source_asset_id,
                        source_case_id=draft.source_case_id,
                        source_draft_id=draft.source_draft_id,
                        status=ProjectTestPlanDraftStatus.DRAFT,
                        supersede_existing_active=False,
                        payload=payload,
                    )
                )
                return MatrixDraftEditResult(
                    draft=updated,
                    validation=summary,
                    created_new_draft=True,
                )
            updated = self._drafts.update_draft(
                UpdateProjectTestPlanDraftCommand(
                    project_id=command.project_id,
                    draft_id=command.draft_id,
                    payload=payload,
                )
            )
            return MatrixDraftEditResult(
                draft=updated,
                validation=summary,
                created_new_draft=False,
            )
        except ProjectTestPlanDraftNotFoundError as exc:
            raise ProjectTestPlanMatrixEditNotFoundError(str(exc)) from exc
        except ProjectTestPlanDraftError as exc:
            raise ProjectTestPlanMatrixEditError(str(exc)) from exc

    def validate_matrix_draft(
        self,
        command: ValidateProjectTestPlanMatrixCommand,
    ) -> MatrixValidationSummary:
        draft = self._require_draft(command.project_id, command.draft_id)
        groups = command.groups if command.groups is not None else _groups_from_payload(draft.payload_json)
        summary, _ = _normalize_and_validate_groups(groups)
        return summary

    def confirm_matrix_draft(
        self,
        command: ConfirmProjectTestPlanMatrixCommand,
    ) -> MatrixDraftEditResult:
        created_new_draft = False
        draft_id = command.draft_id
        if command.groups is not None:
            updated = self.update_matrix_draft(
                UpdateProjectTestPlanMatrixCommand(
                    project_id=command.project_id,
                    draft_id=command.draft_id,
                    groups=command.groups,
                )
            )
            created_new_draft = updated.created_new_draft
            draft_id = updated.draft.draft_id
        summary = self.validate_matrix_draft(
            ValidateProjectTestPlanMatrixCommand(
                project_id=command.project_id,
                draft_id=draft_id,
            )
        )
        if summary.blockers:
            raise ProjectTestPlanMatrixEditError(
                "Matrix draft cannot be confirmed because validation blockers exist."
            )
        draft = self._require_draft(command.project_id, draft_id)
        if draft.status is ProjectTestPlanDraftStatus.REVIEWED:
            return MatrixDraftEditResult(
                draft=draft,
                validation=summary,
                created_new_draft=created_new_draft,
            )
        try:
            confirmed = self._drafts.update_draft(
                UpdateProjectTestPlanDraftCommand(
                    project_id=command.project_id,
                    draft_id=draft.draft_id,
                    status=ProjectTestPlanDraftStatus.REVIEWED,
                )
            )
            for reviewed in self._drafts.list_by_project(command.project_id):
                if reviewed.draft_id == confirmed.draft_id:
                    continue
                if (
                    reviewed.source_document_path == confirmed.source_document_path
                    and reviewed.status is ProjectTestPlanDraftStatus.REVIEWED
                ):
                    self._drafts.update_draft(
                        UpdateProjectTestPlanDraftCommand(
                            project_id=command.project_id,
                            draft_id=reviewed.draft_id,
                            status=ProjectTestPlanDraftStatus.SUPERSEDED,
                        )
                    )
            return MatrixDraftEditResult(
                draft=confirmed,
                validation=summary,
                created_new_draft=created_new_draft,
            )
        except ProjectTestPlanDraftNotFoundError as exc:
            raise ProjectTestPlanMatrixEditNotFoundError(str(exc)) from exc
        except ProjectTestPlanDraftError as exc:
            raise ProjectTestPlanMatrixEditError(str(exc)) from exc

    def _require_draft(self, project_id: str, draft_id: str) -> ProjectTestPlanDraft:
        try:
            return self._drafts.get_draft(project_id, draft_id)
        except ProjectTestPlanDraftNotFoundError as exc:
            raise ProjectTestPlanMatrixEditNotFoundError(str(exc)) from exc


def _normalize_and_validate_groups(
    groups: list[dict[str, Any]],
) -> tuple[MatrixValidationSummary, list[dict[str, Any]]]:
    if not isinstance(groups, list):
        raise ProjectTestPlanMatrixEditError("groups must be an array.")
    normalized_groups: list[dict[str, Any]] = []
    blockers: list[str] = []
    warnings: list[str] = []
    total_steps = 0
    for group_index, group in enumerate(groups, start=1):
        if not isinstance(group, dict):
            blockers.append(f"Group {group_index}: group entry must be an object.")
            continue
        if not _has_explicit_group_identity(group):
            blockers.append(
                f"Group {group_index}: explicit stable group identity is required."
            )
        group_label = _text(group.get("group_label")) or f"Group {group_index}"
        group_key = _text(group.get("group_key")) or _group_key(group_label)
        raw_steps = group.get("steps")
        if not isinstance(raw_steps, list):
            blockers.append(f"{group_label}: steps must be an array.")
            continue
        normalized_steps: list[dict[str, Any]] = []
        for step_index, step in enumerate(raw_steps, start=1):
            if not isinstance(step, dict):
                blockers.append(f"{group_label} step {step_index}: step entry must be an object.")
                continue
            token_input = _token_input(step)
            parsed_tokens, token_warnings = parse_step_tokens(token_input)
            for warning in token_warnings:
                blockers.append(f"{group_label} step {step_index}: {warning}")
            for token in parsed_tokens:
                normalized = _normalized_step(step, token.sequence, token.raw_token, token.suffix_note)
                normalized_steps.append(normalized)
        sequences = [int(step["sequence"]) for step in normalized_steps]
        blockers.extend(validate_group_step_sequences(group_label, sequences))
        for step in normalized_steps:
            sequence = int(step["sequence"])
            if not _text(step.get("test_item")):
                blockers.append(f"{group_label} step {sequence}: test item is required.")
            if not _text(step.get("method_summary")):
                warnings.append(f"{group_label} step {sequence}: method is missing.")
            if not _text(step.get("judgement_criteria")):
                warnings.append(f"{group_label} step {sequence}: requirement is missing.")
            if not _text(step.get("condition_summary")):
                warnings.append(f"{group_label} step {sequence}: condition is missing.")
            if step.get("duration_value") is None and not _text(step.get("duration_hint")):
                warnings.append(f"{group_label} step {sequence}: duration is missing.")
            if not _text(step.get("source_trace")):
                warnings.append(f"{group_label} step {sequence}: source trace is missing.")
            if not _text(step.get("step_description")):
                warnings.append(f"{group_label} step {sequence}: step description is missing.")
        normalized_groups.append(
            {
                "group_key": group_key,
                "group_label": group_label,
                "sample_size": _number_or_none(group.get("sample_size")),
                "source_table_index": _int_or_none(group.get("source_table_index")),
                "steps": normalized_steps,
            }
        )
        total_steps += len(normalized_steps)
    summary = MatrixValidationSummary(
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
        group_count=len(normalized_groups),
        step_count=total_steps,
    )
    return summary, normalized_groups


def _normalized_step(
    step: dict[str, Any],
    sequence: int,
    raw_token: str,
    suffix_note: str | None,
) -> dict[str, Any]:
    condition_summary = _text(step.get("condition_summary")) or _text(step.get("condition"))
    method_summary = _text(step.get("method_summary")) or _text(step.get("method"))
    reference_standard = _text(step.get("reference_standard"))
    judgement_criteria = _text(step.get("judgement_criteria")) or _text(step.get("requirement"))
    duration_value, duration_unit = _duration_value_and_unit(step)
    estimated_days, estimated_hours, duration_hint = _duration_compatibility_fields(
        step,
        duration_value,
        duration_unit,
    )
    return {
        "sequence": sequence,
        "raw_token": raw_token,
        "suffix_note": suffix_note,
        "test_item": _text(step.get("test_item")) or _text(step.get("step_label")),
        "step_label": _text(step.get("step_label")),
        "source_section": _text(step.get("source_section")) or _text(step.get("section")),
        "condition_summary": condition_summary,
        "method_summary": method_summary,
        "reference_standard": reference_standard,
        "judgement_criteria": judgement_criteria,
        "step_description": _text(step.get("step_description")),
        "duration_value": duration_value,
        "duration_unit": duration_unit,
        "duration_hint": duration_hint,
        "estimated_duration_hint": duration_hint,
        "estimated_duration_days": estimated_days,
        "duration_days": estimated_days,
        "estimated_duration_hours": estimated_hours,
        "source_table_index": _int_or_none(step.get("source_table_index")),
        "source_row_index": _int_or_none(step.get("source_row_index")),
        "source_trace": _text(step.get("source_trace")),
        "note": _text(step.get("note")),
        "duration_authorities": _structured_duration_authorities(
            step.get("duration_authorities")
        ),
    }


def _structured_duration_authorities(value: Any) -> list[dict[str, Any]] | None:
    """Preserve only a typed collection; duration prose is never promoted."""
    if value is None:
        return None
    if not isinstance(value, list):
        raise ProjectTestPlanMatrixEditError(
            "duration_authorities must be an array or null."
        )
    if not all(isinstance(item, dict) for item in value):
        raise ProjectTestPlanMatrixEditError(
            "Each duration authority must be an object."
        )
    return [dict(item) for item in value]


def _duration_value_and_unit(step: dict[str, Any]) -> tuple[float | None, str | None]:
    value = _number_or_none(step.get("duration_value"))
    unit = _text(step.get("duration_unit"))
    if value is not None and unit:
        return value, unit.lower()
    days = _number_or_none(step.get("estimated_duration_days"))
    if days is None:
        days = _number_or_none(step.get("duration_days"))
    if days is not None:
        return days, "day"
    hours = _number_or_none(step.get("estimated_duration_hours"))
    if hours is not None:
        return hours, "hour"
    return None, None


def _duration_compatibility_fields(
    step: dict[str, Any],
    duration_value: float | None,
    duration_unit: str | None,
) -> tuple[float | None, float | None, str | None]:
    if duration_value is not None and duration_unit:
        if duration_unit.startswith("hour"):
            return duration_value / 24, duration_value, f"{duration_value:g} hour(s)"
        return duration_value, None, f"{duration_value:g} day(s)"
    days = _number_or_none(step.get("estimated_duration_days"))
    if days is None:
        days = _number_or_none(step.get("duration_days"))
    hours = _number_or_none(step.get("estimated_duration_hours"))
    hint = _text(step.get("estimated_duration_hint")) or _text(step.get("duration_hint"))
    return days, hours, hint


def _groups_from_payload(payload_json: str) -> list[dict[str, Any]]:
    try:
        payload = json.loads(payload_json)
    except json.JSONDecodeError as exc:
        raise ProjectTestPlanMatrixEditError("Draft payload is not valid JSON.") from exc
    if not isinstance(payload, dict):
        raise ProjectTestPlanMatrixEditError("Draft payload must be a JSON object.")
    groups = payload.get("groups", [])
    if not isinstance(groups, list):
        raise ProjectTestPlanMatrixEditError("Draft payload groups must be an array.")
    return groups


def _token_input(step: dict[str, Any]) -> str | None:
    raw = _text(step.get("raw_token"))
    if raw:
        return raw
    if isinstance(step.get("sequence"), int):
        return str(step["sequence"])
    return _text(step.get("step_label"))


def _group_key(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_") or "group"


def _has_explicit_group_identity(group: dict[str, Any]) -> bool:
    explicit_key = _text(group.get("group_key"))
    if explicit_key:
        return True
    group_number = group.get("group_number")
    if isinstance(group_number, int | float) and not isinstance(group_number, bool):
        return True
    explicit_label = _text(group.get("group_label"))
    if explicit_label:
        return True
    return False


def _text(value: Any) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return None


def _int_or_none(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def _number_or_none(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None
