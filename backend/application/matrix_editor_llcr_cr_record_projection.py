"""Project the current Matrix Editor state into LLCR/CR draft records."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Mapping

from backend.application.confirmed_matrix_llcr_cr_record_projection import (
    LlcrCrRecordProjection,
    build_point_profile_llcr_cr_record_projection,
)
from backend.domain import (
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixStepQuantity,
    ConfirmedMatrixVersion,
)
from backend.modules.test_plan.matrix_step_sequence_validation import parse_step_tokens

_DRAFT_MATRIX_ID = "Unconfirmed Matrix draft"


@dataclass(frozen=True, slots=True)
class MatrixEditorLlcrCrRecordGroupInput:
    """One selected group from the current Matrix Editor state."""

    group_key: str
    group_label: str
    sample_quantity_expression: str
    sample_note: str | None = None


@dataclass(frozen=True, slots=True)
class MatrixEditorLlcrCrRecordRowInput:
    """One row from the current Matrix Editor state."""

    test_item: str
    section: str = ""
    method: str = ""
    condition: str = ""
    requirement: str = ""
    is_sample_row: bool = False
    group_values: Mapping[str, str] | None = None


def build_matrix_editor_llcr_cr_record_projection(
    *,
    project_id: str,
    record_type: str,
    groups: tuple[MatrixEditorLlcrCrRecordGroupInput, ...],
    rows: tuple[MatrixEditorLlcrCrRecordRowInput, ...],
    point_profile,
) -> LlcrCrRecordProjection:
    """Build a no-authority workbook projection from the supplied live draft."""
    snapshot = _draft_snapshot(
        project_id=project_id,
        groups=groups,
        rows=rows,
    )
    projection = build_point_profile_llcr_cr_record_projection(
        snapshot,
        point_profile,
        record_type,
    )
    return replace(
        projection,
        confirmed_matrix_id=_DRAFT_MATRIX_ID,
        confirmed_revision=0,
        matrix_source="matrix_editor_current_ui_state",
    )


def _draft_snapshot(
    *,
    project_id: str,
    groups: tuple[MatrixEditorLlcrCrRecordGroupInput, ...],
    rows: tuple[MatrixEditorLlcrCrRecordRowInput, ...],
) -> ConfirmedMatrixSnapshot:
    version = ConfirmedMatrixVersion(
        confirmed_matrix_id=_DRAFT_MATRIX_ID,
        project_id=project_id,
        project_matrix_draft_id="matrix-editor-current-ui-state",
        source_import_id="matrix-editor-current-ui-state",
        source_snapshot_id="matrix-editor-current-ui-state",
        confirmed_revision=0,
        is_active_authority=False,
        status=ConfirmedMatrixStatus.SUPERSEDED,
        confirmed_by="matrix-editor-preview",
        confirmed_at="",
    )
    projected_groups = tuple(
        ConfirmedMatrixGroup(
            confirmed_group_id=f"draft-group-{index}",
            confirmed_matrix_id=_DRAFT_MATRIX_ID,
            draft_group_id=f"draft-group-{index}",
            source_group_snapshot_id=None,
            group_order=index,
            group_key=group.group_key.strip(),
            group_label=group.group_label.strip(),
            sample_quantity_expression=group.sample_quantity_expression.strip(),
            sample_note=(group.sample_note or "").strip() or None,
        )
        for index, group in enumerate(groups, start=1)
    )
    group_by_key = {
        source.group_key.strip(): projected
        for source, projected in zip(groups, projected_groups, strict=True)
    }
    projected_rows: list[ConfirmedMatrixRow] = []
    quantities: list[ConfirmedMatrixStepQuantity] = []
    for row_index, row in enumerate(rows, start=1):
        if row.is_sample_row:
            continue
        row_id = f"draft-row-{row_index}"
        projected_row = ConfirmedMatrixRow(
            confirmed_row_id=row_id,
            confirmed_matrix_id=_DRAFT_MATRIX_ID,
            draft_row_id=row_id,
            source_row_snapshot_id=None,
            row_order=row_index,
            test_item=row.test_item.strip(),
            source_section=row.section.strip() or None,
            method=row.method.strip() or None,
            condition=row.condition.strip() or None,
            requirement=row.requirement.strip() or None,
        )
        projected_rows.append(projected_row)
        for group_key, cell_value in (row.group_values or {}).items():
            group = group_by_key.get(group_key.strip())
            if group is None or not str(cell_value or "").strip():
                continue
            parsed, _warnings = parse_step_tokens(cell_value)
            for token_index, token in enumerate(parsed, start=1):
                quantities.append(
                    ConfirmedMatrixStepQuantity(
                        confirmed_step_quantity_id=(
                            f"draft-quantity-{row_index}-{group.group_order}-{token_index}"
                        ),
                        confirmed_matrix_id=_DRAFT_MATRIX_ID,
                        confirmed_group_id=group.confirmed_group_id,
                        confirmed_row_id=row_id,
                        draft_group_id=group.draft_group_id,
                        draft_row_id=row_id,
                        step_sequence=token.sequence,
                        step_suffix_note=token.suffix_note,
                        raw_token=token.raw_token,
                        test_points_per_sample=None,
                        readings_per_point=None,
                        contact_points_per_sample=None,
                        source="matrix_editor_current_ui_state",
                        review_required=False,
                        review_reason=None,
                        confirmed_at="",
                    )
                )
    return ConfirmedMatrixSnapshot(
        version=version,
        groups=projected_groups,
        rows=tuple(projected_rows),
        step_quantities=tuple(quantities),
    )
