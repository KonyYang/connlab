"""Minimal runtime projection composition helpers for TASK_202."""

from __future__ import annotations

from collections import Counter
from collections import defaultdict

from backend.modules.runtime_projection.models import (
    GroupRuntimeProjection,
    InteractiveStepTokenProjection,
    ProjectionAggregationSummary,
    RuntimeProjectionSummary,
)


def _to_value_counts(values: tuple[str | None, ...]) -> tuple[tuple[str | None, int], ...]:
    counter = Counter(values)
    return tuple(
        (value, counter[value])
        for value in sorted(counter, key=lambda item: (item is not None, item or ""))
    )


def compose_runtime_projection_summary(
    projections: tuple[InteractiveStepTokenProjection, ...],
) -> RuntimeProjectionSummary:
    """Aggregate already-supplied projection dimensions into read-model summaries."""
    if not projections:
        return RuntimeProjectionSummary(total_tokens=0, group_count=0, groups=())

    grouped: dict[tuple[str, str], list[InteractiveStepTokenProjection]] = defaultdict(list)
    for projection in projections:
        grouped[(projection.group_identity, projection.group_label)].append(projection)

    groups: list[GroupRuntimeProjection] = []
    for group_key in sorted(grouped):
        group_projections = grouped[group_key]
        sequences = {item.sequence_number for item in group_projections}
        aggregation_summary = ProjectionAggregationSummary(
            lifecycle_counts=_to_value_counts(
                tuple(item.lifecycle_projection for item in group_projections)
            ),
            evidence_counts=_to_value_counts(
                tuple(item.evidence_projection for item in group_projections)
            ),
            report_sync_counts=_to_value_counts(
                tuple(item.report_sync_projection for item in group_projections)
            ),
            stale_counts=_to_value_counts(
                tuple(item.stale_projection for item in group_projections)
            ),
            attention_counts=_to_value_counts(
                tuple(item.attention_projection for item in group_projections)
            ),
        )
        groups.append(
            GroupRuntimeProjection(
                group_identity=group_key[0],
                group_label=group_key[1],
                total_tokens=len(group_projections),
                unique_sequences=len(sequences),
                aggregation_summary=aggregation_summary,
            )
        )

    return RuntimeProjectionSummary(
        total_tokens=len(projections),
        group_count=len(groups),
        groups=tuple(groups),
    )
