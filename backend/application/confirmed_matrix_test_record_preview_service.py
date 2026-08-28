"""Build read-only Test Record preview from active Confirmed Matrix authority."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Protocol

from backend.application.confirmed_matrix_step_quantity_projection import (
    ConfirmedMatrixTestRecordStepQuantity,
    StepQuantityProjectionLookup,
    build_step_quantity_projection_lookup,
    project_test_record_step_quantity,
)
from backend.domain import ConfirmedMatrixGroup, ConfirmedMatrixRow
from backend.domain import ConfirmedMatrixSnapshot
from backend.modules.test_plan.matrix_step_sequence_validation import parse_step_tokens


class ConfirmedMatrixTestRecordPreviewError(ValueError):
    """Raised when confirmed authority data cannot be mapped into preview output."""


class ConfirmedMatrixTestRecordPreviewNotFoundError(LookupError):
    """Raised when no active confirmed Matrix authority exists for a project."""


class ConfirmedMatrixAuthorityStore(Protocol):
    """Confirmed Matrix authority read operations required by this consumer."""

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        """Return one active confirmed authority aggregate in one project."""


@dataclass(frozen=True, slots=True)
class BuildConfirmedMatrixTestRecordPreviewCommand:
    """Input payload for confirmed-authority Test Record preview building."""

    project_id: str


@dataclass(frozen=True, slots=True)
class ConfirmedMatrixTestRecordPreviewStep:
    """One preview step row derived from a parsed confirmed sparse cell token."""

    sequence: int
    raw_token: str
    test_item: str
    section: str
    method: str
    condition: str
    requirement: str
    suffix_note: str | None = None
    quantity: ConfirmedMatrixTestRecordStepQuantity | None = None


@dataclass(frozen=True, slots=True)
class ConfirmedMatrixTestRecordPreviewGroup:
    """One preview group with ordered step rows."""

    group_key: str
    group_label: str
    sample_quantity_expression: str
    step_count: int
    steps: tuple[ConfirmedMatrixTestRecordPreviewStep, ...]


@dataclass(frozen=True, slots=True)
class ConfirmedMatrixTestRecordPreview:
    """Top-level read-only Test Record preview payload."""

    project_id: str
    confirmed_matrix_id: str
    preview_status: str
    groups: tuple[ConfirmedMatrixTestRecordPreviewGroup, ...]


class ConfirmedMatrixTestRecordPreviewService:
    """Map active confirmed Matrix authority into Test Record preview rows."""

    def __init__(self, *, confirmed_store: ConfirmedMatrixAuthorityStore) -> None:
        self._confirmed = confirmed_store

    def build_preview(
        self,
        command: BuildConfirmedMatrixTestRecordPreviewCommand,
    ) -> ConfirmedMatrixTestRecordPreview:
        """Return one Test Record preview snapshot for a project."""
        snapshot = self._confirmed.get_active_by_project(command.project_id)
        if snapshot is None:
            raise ConfirmedMatrixTestRecordPreviewNotFoundError(
                "Active confirmed matrix not found."
            )

        groups_by_id = {group.confirmed_group_id: group for group in snapshot.groups}
        rows_by_id = {row.confirmed_row_id: row for row in snapshot.rows}
        cell_lookup = _build_cell_lookup(snapshot=snapshot, groups_by_id=groups_by_id, rows_by_id=rows_by_id)
        quantity_lookup = build_step_quantity_projection_lookup(snapshot)

        preview_groups: list[ConfirmedMatrixTestRecordPreviewGroup] = []
        for group in snapshot.groups:
            steps = _build_group_steps(
                group=group,
                snapshot=snapshot,
                cell_lookup=cell_lookup,
                quantity_lookup=quantity_lookup,
            )
            if not steps:
                continue
            preview_groups.append(
                ConfirmedMatrixTestRecordPreviewGroup(
                    group_key=group.group_key.strip(),
                    group_label=group.group_label.strip(),
                    sample_quantity_expression=_normalize_text(group.sample_quantity_expression),
                    step_count=len(steps),
                    steps=tuple(steps),
                )
            )

        return ConfirmedMatrixTestRecordPreview(
            project_id=snapshot.version.project_id,
            confirmed_matrix_id=snapshot.version.confirmed_matrix_id,
            preview_status="ready" if preview_groups else "empty",
            groups=tuple(preview_groups),
        )


def _build_cell_lookup(
    *,
    snapshot: ConfirmedMatrixSnapshot,
    groups_by_id: dict[str, object],
    rows_by_id: dict[str, object],
) -> dict[tuple[str, str], str]:
    lookup: dict[tuple[str, str], str] = {}
    for cell in snapshot.cells:
        if cell.confirmed_group_id not in groups_by_id or cell.confirmed_row_id not in rows_by_id:
            raise ConfirmedMatrixTestRecordPreviewError(
                "Confirmed matrix cell lineage is invalid."
            )
        lookup[(cell.confirmed_group_id, cell.confirmed_row_id)] = cell.cell_value
    return lookup


def _build_group_steps(
    *,
    group: ConfirmedMatrixGroup,
    snapshot: ConfirmedMatrixSnapshot,
    cell_lookup: dict[tuple[str, str], str],
    quantity_lookup: StepQuantityProjectionLookup,
) -> list[ConfirmedMatrixTestRecordPreviewStep]:
    steps: list[ConfirmedMatrixTestRecordPreviewStep] = []
    for row in snapshot.rows:
        cell_value = _normalize_text(cell_lookup.get((group.confirmed_group_id, row.confirmed_row_id)))
        if not cell_value:
            continue
        parsed_tokens, _warnings = parse_step_tokens(cell_value)
        for token in parsed_tokens:
            steps.append(
                ConfirmedMatrixTestRecordPreviewStep(
                    sequence=token.sequence,
                    raw_token=token.raw_token,
                    suffix_note=token.suffix_note,
                    test_item=_normalize_text(row.test_item),
                    section=_normalize_text(row.source_section),
                    method=_normalize_text(row.method),
                    condition=_normalize_text(row.condition),
                    requirement=_normalize_text(row.requirement),
                    quantity=project_test_record_step_quantity(
                        group=group,
                        row=row,
                        token=token,
                        lookup=quantity_lookup,
                    ),
                )
            )
    steps.sort(key=lambda step: (step.sequence, step.raw_token))
    _apply_llcr_step_requirement_mapping(steps)
    return steps


def _apply_llcr_step_requirement_mapping(steps: list[ConfirmedMatrixTestRecordPreviewStep]) -> None:
    llcr_indexes = [
        index
        for index, step in enumerate(steps)
        if is_llcr_test_item(step.test_item)
    ]
    if not llcr_indexes:
        return
    split = _split_llcr_requirement(steps[llcr_indexes[0]].requirement)
    if split is None:
        return
    initial_value, delta_value = split
    if initial_value:
        first_index = llcr_indexes[0]
        first_step = steps[first_index]
        steps[first_index] = ConfirmedMatrixTestRecordPreviewStep(
            sequence=first_step.sequence,
            raw_token=first_step.raw_token,
            suffix_note=first_step.suffix_note,
            test_item=first_step.test_item,
            section=first_step.section,
            method=first_step.method,
            condition=first_step.condition,
            requirement=initial_value,
            quantity=first_step.quantity,
        )
    if delta_value:
        for index in llcr_indexes[1:]:
            step = steps[index]
            steps[index] = ConfirmedMatrixTestRecordPreviewStep(
                sequence=step.sequence,
                raw_token=step.raw_token,
                suffix_note=step.suffix_note,
                test_item=step.test_item,
                section=step.section,
                method=step.method,
                condition=step.condition,
                requirement=delta_value,
                quantity=step.quantity,
            )


def is_llcr_test_item(test_item: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]+", " ", test_item.strip().lower()).strip()
    if not normalized:
        return False
    if "llcr" in normalized:
        return True
    if normalized in {
        "contact resistance low level",
        "low level contact resistance",
    }:
        return True
    return "contact resistance" in normalized and "low level" in normalized


def _split_llcr_requirement(requirement: str) -> tuple[str, str | None] | None:
    normalized = " ".join(requirement.replace("\n", " ").split())
    if not normalized:
        return None
    initial_match = re.search(r"initial\b[\s:,-]*(?P<value>(?:<=|≤)\s*[^;,]+)", normalized, re.IGNORECASE)
    delta_match = re.search(r"(?:Δ\s*R|delta\s*r|r)\s*(?:<=|≤)\s*(?P<value>[^;,]+)", normalized, re.IGNORECASE)
    if initial_match:
        initial = initial_match.group("value").strip()
    else:
        initial = ""
    if delta_match:
        delta = f"ΔR ≤ {delta_match.group('value').strip()}"
    else:
        delta = None
    if not initial:
        return None
    return (initial, delta)


def _normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip()
