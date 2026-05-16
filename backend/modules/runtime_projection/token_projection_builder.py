"""Token reference and projection builder using existing Matrix token parsing."""

from __future__ import annotations

from backend.modules.runtime_projection.models import (
    DEFAULT_FAKE_PROJECTION_STATE,
    InteractiveStepTokenProjection,
    MatrixRowTechnicalContext,
    ProjectionState,
    TokenReference,
)
from backend.modules.test_plan.matrix_step_sequence_validation import parse_step_tokens


def build_token_reference(
    *,
    project_reference: str,
    matrix_reference: str,
    group_identity: str,
    group_label: str,
    raw_token: str,
    sequence_number: int,
    suffix_note: str | None,
) -> TokenReference:
    """Build one stable token reference from parsed token data."""
    stable_reference = (
        f"{project_reference}|{matrix_reference}|{group_identity}|{sequence_number}|"
        f"{suffix_note or ''}"
    )
    return TokenReference(
        project_reference=project_reference,
        matrix_reference=matrix_reference,
        group_identity=group_identity,
        group_label=group_label,
        raw_token=raw_token,
        sequence_number=sequence_number,
        suffix_note=suffix_note,
        stable_reference=stable_reference,
    )


def build_step_token_projections(
    *,
    project_reference: str,
    matrix_reference: str,
    group_identity: str,
    group_label: str,
    row_context: MatrixRowTechnicalContext,
    raw_step_token_value: str | None,
    projection_state: ProjectionState | None = None,
) -> tuple[tuple[InteractiveStepTokenProjection, ...], tuple[str, ...]]:
    """Build minimal Interactive Step Token projections from parsed tokens."""
    parsed_tokens, warnings = parse_step_tokens(raw_step_token_value)
    if not parsed_tokens:
        return (), warnings

    state = projection_state or DEFAULT_FAKE_PROJECTION_STATE
    projections: list[InteractiveStepTokenProjection] = []
    for token in parsed_tokens:
        reference = build_token_reference(
            project_reference=project_reference,
            matrix_reference=matrix_reference,
            group_identity=group_identity,
            group_label=group_label,
            raw_token=token.raw_token,
            sequence_number=token.sequence,
            suffix_note=token.suffix_note,
        )
        projections.append(
            InteractiveStepTokenProjection(
                project_reference=reference.project_reference,
                matrix_reference=reference.matrix_reference,
                group_identity=reference.group_identity,
                group_label=reference.group_label,
                raw_token=reference.raw_token,
                sequence_number=reference.sequence_number,
                suffix_note=reference.suffix_note,
                token_reference=reference.stable_reference,
                test_item_label=row_context.test_item_label,
                section=row_context.section,
                method=row_context.method,
                condition=row_context.condition,
                requirement=row_context.requirement,
                lifecycle_projection=state.lifecycle,
                evidence_projection=state.evidence,
                report_sync_projection=state.report_sync,
                stale_projection=state.stale,
                attention_projection=state.attention,
            )
        )
    return tuple(projections), warnings

