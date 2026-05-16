"""Read-only runtime projection consumer views for TASK_204."""

from __future__ import annotations

from dataclasses import dataclass

from backend.modules.runtime_projection.models import InteractiveStepTokenProjection


@dataclass(frozen=True, slots=True)
class MatrixOverviewTokenView:
    """Token-level read-only consumer view for Matrix Overview."""

    token_reference: str
    raw_token: str
    sequence_number: int
    suffix_note: str | None
    lifecycle_projection: str | None
    evidence_projection: str | None
    report_sync_projection: str | None
    stale_projection: str | None
    attention_projection: str | None


@dataclass(frozen=True, slots=True)
class MatrixOverviewGroupView:
    """Group-level read-only consumer view for Matrix Overview."""

    group_identity: str
    group_label: str
    total_tokens: int
    unique_sequences: int
    tokens: tuple[MatrixOverviewTokenView, ...]


@dataclass(frozen=True, slots=True)
class MatrixOverviewConsumerView:
    """Top-level Matrix Overview read-only consumer view."""

    total_tokens: int
    group_count: int
    groups: tuple[MatrixOverviewGroupView, ...]


@dataclass(frozen=True, slots=True)
class SelectedStepTokenView:
    """Selected token read-only consumer view for Step Workspace."""

    token_reference: str
    raw_token: str
    sequence_number: int
    suffix_note: str | None
    lifecycle_projection: str | None
    evidence_projection: str | None
    report_sync_projection: str | None
    stale_projection: str | None
    attention_projection: str | None
    test_item_label: str
    section: str
    method: str
    condition: str
    requirement: str


@dataclass(frozen=True, slots=True)
class StepWorkspaceConsumerView:
    """Read-only consumer view for Step Workspace token selection."""

    selected_token_reference: str
    found: bool
    group_identity: str | None
    group_label: str | None
    group_token_references: tuple[str, ...]
    previous_token_reference: str | None
    next_token_reference: str | None
    selected_token: SelectedStepTokenView | None


def _projection_sort_key(projection: InteractiveStepTokenProjection) -> tuple[int, str, str]:
    return (
        projection.sequence_number,
        projection.suffix_note or "",
        projection.token_reference,
    )


def build_matrix_overview_consumer_view(
    projections: tuple[InteractiveStepTokenProjection, ...],
) -> MatrixOverviewConsumerView:
    """Build immutable Matrix Overview consumer output from token projections."""
    if not projections:
        return MatrixOverviewConsumerView(total_tokens=0, group_count=0, groups=())

    grouped: dict[tuple[str, str], list[InteractiveStepTokenProjection]] = {}
    for projection in projections:
        key = (projection.group_identity, projection.group_label)
        grouped.setdefault(key, []).append(projection)

    groups: list[MatrixOverviewGroupView] = []
    for group_key in sorted(grouped):
        items = sorted(grouped[group_key], key=_projection_sort_key)
        tokens = tuple(
            MatrixOverviewTokenView(
                token_reference=item.token_reference,
                raw_token=item.raw_token,
                sequence_number=item.sequence_number,
                suffix_note=item.suffix_note,
                lifecycle_projection=item.lifecycle_projection,
                evidence_projection=item.evidence_projection,
                report_sync_projection=item.report_sync_projection,
                stale_projection=item.stale_projection,
                attention_projection=item.attention_projection,
            )
            for item in items
        )
        groups.append(
            MatrixOverviewGroupView(
                group_identity=group_key[0],
                group_label=group_key[1],
                total_tokens=len(items),
                unique_sequences=len({item.sequence_number for item in items}),
                tokens=tokens,
            )
        )

    return MatrixOverviewConsumerView(
        total_tokens=len(projections),
        group_count=len(groups),
        groups=tuple(groups),
    )


def build_step_workspace_consumer_view(
    projections: tuple[InteractiveStepTokenProjection, ...],
    selected_token_reference: str,
) -> StepWorkspaceConsumerView:
    """Build immutable Step Workspace consumer output for one selected token."""
    selected_projection = next(
        (item for item in projections if item.token_reference == selected_token_reference),
        None,
    )
    if selected_projection is None:
        return StepWorkspaceConsumerView(
            selected_token_reference=selected_token_reference,
            found=False,
            group_identity=None,
            group_label=None,
            group_token_references=(),
            previous_token_reference=None,
            next_token_reference=None,
            selected_token=None,
        )

    group_items = sorted(
        (
            item
            for item in projections
            if item.group_identity == selected_projection.group_identity
            and item.group_label == selected_projection.group_label
        ),
        key=_projection_sort_key,
    )
    references = tuple(item.token_reference for item in group_items)
    selected_index = references.index(selected_projection.token_reference)
    previous_reference = references[selected_index - 1] if selected_index > 0 else None
    next_reference = (
        references[selected_index + 1] if selected_index < len(references) - 1 else None
    )

    return StepWorkspaceConsumerView(
        selected_token_reference=selected_token_reference,
        found=True,
        group_identity=selected_projection.group_identity,
        group_label=selected_projection.group_label,
        group_token_references=references,
        previous_token_reference=previous_reference,
        next_token_reference=next_reference,
        selected_token=SelectedStepTokenView(
            token_reference=selected_projection.token_reference,
            raw_token=selected_projection.raw_token,
            sequence_number=selected_projection.sequence_number,
            suffix_note=selected_projection.suffix_note,
            lifecycle_projection=selected_projection.lifecycle_projection,
            evidence_projection=selected_projection.evidence_projection,
            report_sync_projection=selected_projection.report_sync_projection,
            stale_projection=selected_projection.stale_projection,
            attention_projection=selected_projection.attention_projection,
            test_item_label=selected_projection.test_item_label,
            section=selected_projection.section,
            method=selected_projection.method,
            condition=selected_projection.condition,
            requirement=selected_projection.requirement,
        ),
    )
