"""Per-step text ownership, validation and identity remapping across Matrix revisions."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import replace
from typing import TYPE_CHECKING

from backend.domain.project_matrix_draft_models import ProjectMatrixDraftStepTextOverride
from backend.domain.confirmed_matrix_authority_models import ConfirmedMatrixStepTextOverride
from backend.modules.test_plan.matrix_step_sequence_validation import parse_step_tokens

if TYPE_CHECKING:
    from backend.domain.project_matrix_draft_models import ProjectMatrixDraftCell, ProjectMatrixDraftGroup, ProjectMatrixDraftRow
    from backend.application.matrix_editor_session_contracts import MatrixEditorSessionCell, MatrixEditorSessionGroup, MatrixEditorSessionRow


def updated_step_text_overrides(
    *, existing: Iterable[ProjectMatrixDraftStepTextOverride],
    incoming: Iterable[ProjectMatrixDraftStepTextOverride] | None,
    groups: Iterable[ProjectMatrixDraftGroup | MatrixEditorSessionGroup],
    rows: Iterable[ProjectMatrixDraftRow | MatrixEditorSessionRow],
    cells: Iterable[ProjectMatrixDraftCell | MatrixEditorSessionCell],
    group_id_map: Mapping[str, str], row_id_map: Mapping[str, str],
) -> tuple[ProjectMatrixDraftStepTextOverride, ...]:
    """Preserve omitted legacy fields, replace explicit lists, reject foreign tokens."""
    group_ids = {item.draft_group_id for item in groups}
    non_sample = {item.draft_row_id for item in rows if not item.is_sample_row}
    valid = set()
    for cell in cells:
        if cell.draft_group_id not in group_ids or cell.draft_row_id not in non_sample:
            continue
        tokens, _ = parse_step_tokens(cell.cell_value)
        valid.update((cell.draft_group_id, cell.draft_row_id, token.sequence,
                      (token.suffix_note or "").strip()) for token in tokens)
    result = []
    seen = set()
    for item in existing if incoming is None else incoming:
        mapped = replace(item,
            draft_group_id=group_id_map.get(item.draft_group_id, item.draft_group_id),
            draft_row_id=row_id_map.get(item.draft_row_id, item.draft_row_id),
            step_suffix_note=(item.step_suffix_note or "").strip())
        identity = (mapped.draft_group_id, mapped.draft_row_id, mapped.step_sequence, mapped.step_suffix_note)
        if identity not in valid:
            if incoming is None:
                continue  # Removed rows/tokens cannot retain dangling draft text.
            raise ValueError("Step text references an unknown group, row or step token.")
        if identity in seen:
            raise ValueError("Duplicate step text override identity.")
        seen.add(identity)
        if mapped.description is not None or mapped.requirement is not None:
            result.append(mapped)
    return tuple(result)


def confirmed_step_text_overrides(
    items: Iterable[ProjectMatrixDraftStepTextOverride],
    group_id_map: Mapping[str, str], row_id_map: Mapping[str, str],
) -> tuple[ConfirmedMatrixStepTextOverride, ...]:
    return tuple(ConfirmedMatrixStepTextOverride(
        confirmed_group_id=group_id_map[item.draft_group_id],
        confirmed_row_id=row_id_map[item.draft_row_id],
        step_sequence=item.step_sequence, step_suffix_note=item.step_suffix_note,
        description=item.description, requirement=item.requirement,
    ) for item in items if item.draft_group_id in group_id_map and item.draft_row_id in row_id_map)


def draft_step_text_overrides(
    items: Iterable[ConfirmedMatrixStepTextOverride],
    group_id_map: Mapping[str, str], row_id_map: Mapping[str, str],
) -> tuple[ProjectMatrixDraftStepTextOverride, ...]:
    return tuple(ProjectMatrixDraftStepTextOverride(
        draft_group_id=group_id_map[item.confirmed_group_id],
        draft_row_id=row_id_map[item.confirmed_row_id],
        step_sequence=item.step_sequence, step_suffix_note=item.step_suffix_note,
        description=item.description, requirement=item.requirement,
    ) for item in items if item.confirmed_group_id in group_id_map and item.confirmed_row_id in row_id_map)


def step_text_signature(
    items: Iterable[ProjectMatrixDraftStepTextOverride | ConfirmedMatrixStepTextOverride] | None,
    group_index: Mapping[str, int], row_index: Mapping[str, int], *, confirmed: bool = False,
) -> list[tuple[int, int, int, str, str | None, str | None]]:
    prefix = "confirmed" if confirmed else "draft"
    return sorted(((group_index[getattr(item, f"{prefix}_group_id")],
                   row_index[getattr(item, f"{prefix}_row_id")], item.step_sequence,
                   item.step_suffix_note.strip(), item.description, item.requirement)
                  for item in items or ()
                  if getattr(item, f"{prefix}_group_id") in group_index
                  and getattr(item, f"{prefix}_row_id") in row_index
                  and (item.description is not None or item.requirement is not None)), key=lambda item: item[:4])
