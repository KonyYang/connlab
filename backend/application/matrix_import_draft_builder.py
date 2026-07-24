"""Pure selected-only editable Matrix draft construction."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from backend.domain import (
    ProjectMatrixDraftCell,
    ProjectMatrixDraftGroup,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftRow,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStatus,
    SourceMatrixSnapshot,
)
from backend.domain.project_matrix_draft_models import (
    ProjectMatrixDraftDurationAuthority,
)


def build_selected_only_draft(
    *,
    project_id: str,
    source_import_id: str,
    source_snapshot_id: str,
    selected_group_keys: tuple[str, ...],
    source_snapshot: SourceMatrixSnapshot,
    preview_payload: dict[str, Any],
    created_at: str,
) -> ProjectMatrixDraftSnapshot:
    draft_id = f"pmd-{uuid4().hex}"
    record = ProjectMatrixDraftRecord(
        project_matrix_draft_id=draft_id,
        project_id=project_id,
        source_import_id=source_import_id,
        source_snapshot_id=source_snapshot_id,
        status=ProjectMatrixDraftStatus.DRAFT,
        created_at=created_at,
        updated_at=created_at,
        base_confirmed_matrix_id=None,
    )
    selected = set(selected_group_keys)
    group_id_by_source: dict[str, str] = {}
    groups: list[ProjectMatrixDraftGroup] = []
    for order, source_group in enumerate(
        (group for group in source_snapshot.groups if group.group_key in selected),
        start=1,
    ):
        draft_group_id = f"pmdg-{uuid4().hex}"
        group_id_by_source[source_group.group_snapshot_id] = draft_group_id
        groups.append(
            ProjectMatrixDraftGroup(
                draft_group_id=draft_group_id,
                project_matrix_draft_id=draft_id,
                source_group_snapshot_id=source_group.group_snapshot_id,
                group_order=order,
                group_key=source_group.group_key,
                group_label=source_group.group_label,
                is_selected=True,
                sample_quantity_expression=source_group.sample_quantity_expression,
                sample_note=source_group.sample_note,
            )
        )
    details = _row_details(preview_payload)
    row_id_by_source: dict[str, str] = {}
    rows: list[ProjectMatrixDraftRow] = []
    for order, source_row in enumerate(source_snapshot.rows, start=1):
        draft_row_id = f"pmdr-{uuid4().hex}"
        row_id_by_source[source_row.row_snapshot_id] = draft_row_id
        detail = details.get(source_row.source_row_index)
        rows.append(
            ProjectMatrixDraftRow(
                draft_row_id=draft_row_id,
                project_matrix_draft_id=draft_id,
                source_row_snapshot_id=source_row.row_snapshot_id,
                row_order=order,
                test_item=source_row.test_item,
                source_section=source_row.source_section,
                method=detail["method"] if detail else source_row.method,
                condition=detail["condition"] if detail else source_row.condition,
                requirement=detail["requirement"] if detail else source_row.requirement,
                is_sample_row=source_row.is_sample_row,
            )
        )
    cells: list[ProjectMatrixDraftCell] = []
    for source_cell in source_snapshot.cells:
        draft_group_id = group_id_by_source.get(source_cell.group_snapshot_id)
        draft_row_id = row_id_by_source.get(source_cell.row_snapshot_id)
        value = source_cell.cell_value.strip()
        if draft_group_id and draft_row_id and value:
            cells.append(
                ProjectMatrixDraftCell(
                    draft_cell_id=f"pmdc-{uuid4().hex}",
                    project_matrix_draft_id=draft_id,
                    draft_row_id=draft_row_id,
                    draft_group_id=draft_group_id,
                    cell_value=value,
                )
            )
    return ProjectMatrixDraftSnapshot(
        record=record,
        groups=tuple(groups),
        rows=tuple(rows),
        cells=tuple(cells),
        duration_authorities=tuple(
            ProjectMatrixDraftDurationAuthority(
                draft_duration_authority_id=f"pmda-{uuid4().hex}",
                project_matrix_draft_id=draft_id,
                draft_group_id=group_id_by_source[item.source_group_snapshot_id],
                draft_row_id=row_id_by_source[item.source_row_snapshot_id],
                step_sequence=item.step_sequence,
                step_suffix_note=item.step_suffix_note,
                duration_value=item.duration_value,
                duration_unit=item.duration_unit,
                normalized_hours=item.normalized_hours,
                source_kind=item.source_kind,
                source_field=item.source_field,
                source_import_id=item.source_import_id,
                source_fingerprint=item.source_fingerprint,
                lineage_fingerprint=item.lineage_fingerprint,
                authority_revision=item.authority_revision,
                status=item.status,
                diagnostic_code=item.diagnostic_code,
                diagnostic_message=item.diagnostic_message,
                created_at=created_at,
                updated_at=created_at,
            )
            for item in source_snapshot.duration_authorities
            if item.source_group_snapshot_id in group_id_by_source
            and item.source_row_snapshot_id in row_id_by_source
        ),
    )


def _row_details(payload: dict[str, Any]) -> dict[int, dict[str, str | None]]:
    details: dict[int, dict[str, str | None]] = {}
    raw_rows = payload.get("rows")
    if isinstance(raw_rows, list):
        for raw_row in raw_rows:
            if not isinstance(raw_row, dict):
                continue
            index = _int(raw_row.get("source_row_index"))
            if index is not None:
                details[index] = {
                    "method": _text(raw_row.get("method")),
                    "condition": _text(raw_row.get("condition")),
                    "requirement": _text(raw_row.get("requirement")),
                }
    raw_groups = payload.get("groups")
    if not isinstance(raw_groups, list):
        return details
    for group in raw_groups:
        if not isinstance(group, dict) or not isinstance(group.get("steps"), list):
            continue
        for step in group["steps"]:
            if not isinstance(step, dict):
                continue
            index = _int(step.get("source_row_index"))
            if index is None:
                continue
            current = details.setdefault(
                index, {"method": None, "condition": None, "requirement": None}
            )
            candidates = {
                "method": ("method_summary", "method", "reference_standard"),
                "condition": ("condition_summary", "condition"),
                "requirement": ("judgement_criteria", "requirement"),
            }
            for field, keys in candidates.items():
                value = next((_text(step.get(key)) for key in keys if _text(step.get(key))), None)
                if value and not current[field]:
                    current[field] = value
    return details


def _text(value: Any) -> str | None:
    return value.strip() or None if isinstance(value, str) else None


def _int(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None
