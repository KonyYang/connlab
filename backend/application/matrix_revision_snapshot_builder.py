"""Pure snapshot builders for Matrix revision flow."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from backend.application.matrix_step_quantity_authority_builder import (
    build_confirmed_step_quantities,
    carry_forward_step_quantities,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
    ProjectMatrixDraftCell,
    ProjectMatrixDraftGroup,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftRow,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStatus,
)
from backend.domain.confirmed_matrix_authority_models import (
    ConfirmedMatrixDurationAuthority,
)
from backend.domain.project_matrix_draft_models import (
    ProjectMatrixDraftDurationAuthority,
)


def _build_revision_draft_from_active(
    active: ConfirmedMatrixSnapshot,
) -> ProjectMatrixDraftSnapshot:
    draft_id = f"pmd-{uuid4().hex}"
    now = _utc_now()
    record = ProjectMatrixDraftRecord(
        project_matrix_draft_id=draft_id,
        project_id=active.version.project_id,
        source_import_id=None,
        source_snapshot_id=active.version.source_snapshot_id,
        status=ProjectMatrixDraftStatus.DRAFT,
        created_at=now,
        updated_at=now,
        base_confirmed_matrix_id=active.version.confirmed_matrix_id,
        pre_test_buffer_days=active.version.pre_test_buffer_days,
        post_test_buffer_days=active.version.post_test_buffer_days,
        sample_received_date=active.version.sample_received_date,
        planned_test_start_date=active.version.planned_test_start_date,
        planned_test_complete_date=active.version.planned_test_complete_date,
        estimated_completion_date=active.version.estimated_completion_date,
    )
    groups = tuple(
        ProjectMatrixDraftGroup(
            draft_group_id=f"pmdg-{uuid4().hex}",
            project_matrix_draft_id=draft_id,
            source_group_snapshot_id=group.source_group_snapshot_id,
            group_order=index,
            group_key=group.group_key,
            group_label=group.group_label,
            is_selected=True,
            sample_quantity_expression=group.sample_quantity_expression,
            sample_note=group.sample_note,
        )
        for index, group in enumerate(
            sorted(active.groups, key=lambda item: item.group_order),
            start=1,
        )
    )
    rows = tuple(
        ProjectMatrixDraftRow(
            draft_row_id=f"pmdr-{uuid4().hex}",
            project_matrix_draft_id=draft_id,
            source_row_snapshot_id=row.source_row_snapshot_id,
            row_order=index,
            test_item=row.test_item,
            source_section=row.source_section,
            method=row.method,
            condition=row.condition,
            requirement=row.requirement,
            day_expression=row.day_expression,
            is_sample_row=False,
        )
        for index, row in enumerate(
            sorted(active.rows, key=lambda item: item.row_order),
            start=1,
        )
    )
    group_id_map = {
        group_from_active.confirmed_group_id: draft_group.draft_group_id
        for group_from_active, draft_group in zip(
            sorted(active.groups, key=lambda item: item.group_order),
            groups,
            strict=False,
        )
    }
    row_id_map = {
        row_from_active.confirmed_row_id: draft_row.draft_row_id
        for row_from_active, draft_row in zip(
            sorted(active.rows, key=lambda item: item.row_order),
            rows,
            strict=False,
        )
    }
    cells: list[ProjectMatrixDraftCell] = []
    seen_identity: set[tuple[str, str]] = set()
    for cell in active.cells:
        draft_row_id = row_id_map.get(cell.confirmed_row_id)
        draft_group_id = group_id_map.get(cell.confirmed_group_id)
        if draft_row_id is None or draft_group_id is None:
            continue
        cell_value = cell.cell_value.strip()
        if not cell_value:
            continue
        identity = (draft_row_id, draft_group_id)
        if identity in seen_identity:
            continue
        seen_identity.add(identity)
        cells.append(
            ProjectMatrixDraftCell(
                draft_cell_id=f"pmdc-{uuid4().hex}",
                project_matrix_draft_id=draft_id,
                draft_row_id=draft_row_id,
                draft_group_id=draft_group_id,
                cell_value=cell_value,
            )
        )
    step_quantities = carry_forward_step_quantities(
        active=active,
        draft_id=draft_id,
        group_id_map=group_id_map,
        row_id_map=row_id_map,
        updated_at=now,
    )
    return ProjectMatrixDraftSnapshot(
        record=record,
        groups=groups,
        rows=rows,
        cells=tuple(cells),
        step_quantities=tuple(step_quantities),
        duration_authorities=carry_forward_duration_authorities(
            active=active,
            draft_id=draft_id,
            group_id_map=group_id_map,
            row_id_map=row_id_map,
            updated_at=now,
        ),
    )


def _build_confirmed_snapshot_from_revision_draft(
    *,
    draft: ProjectMatrixDraftSnapshot,
    selected_groups: tuple[ProjectMatrixDraftGroup, ...],
    confirmed_by: str,
    confirmed_revision: int,
    source_import_id: str,
) -> ConfirmedMatrixSnapshot:
    confirmed_matrix_id = f"cmv-{uuid4().hex}"
    confirmed_at = _utc_now()
    version = ConfirmedMatrixVersion(
        confirmed_matrix_id=confirmed_matrix_id,
        project_id=draft.record.project_id,
        project_matrix_draft_id=draft.record.project_matrix_draft_id,
        source_import_id=source_import_id,
        source_snapshot_id=draft.record.source_snapshot_id,
        confirmed_revision=confirmed_revision,
        is_active_authority=True,
        status=ConfirmedMatrixStatus.CONFIRMED,
        confirmed_by=confirmed_by,
        confirmed_at=confirmed_at,
        pre_test_buffer_days=_normalize_optional_text(draft.record.pre_test_buffer_days),
        post_test_buffer_days=_normalize_optional_text(draft.record.post_test_buffer_days),
        sample_received_date=_normalize_optional_text(draft.record.sample_received_date),
        planned_test_start_date=_normalize_optional_text(draft.record.planned_test_start_date),
        planned_test_complete_date=_normalize_optional_text(
            draft.record.planned_test_complete_date
        ),
        estimated_completion_date=_normalize_optional_text(draft.record.estimated_completion_date),
    )
    sorted_groups = sorted(selected_groups, key=lambda item: item.group_order)
    groups: list[ConfirmedMatrixGroup] = []
    confirmed_group_id_by_draft_group: dict[str, str] = {}
    for index, group in enumerate(sorted_groups, start=1):
        confirmed_group_id = f"cmg-{uuid4().hex}"
        confirmed_group_id_by_draft_group[group.draft_group_id] = confirmed_group_id
        groups.append(
            ConfirmedMatrixGroup(
                confirmed_group_id=confirmed_group_id,
                confirmed_matrix_id=confirmed_matrix_id,
                draft_group_id=group.draft_group_id,
                source_group_snapshot_id=group.source_group_snapshot_id,
                group_order=index,
                group_key=group.group_key.strip(),
                group_label=group.group_label.strip(),
                sample_quantity_expression=(group.sample_quantity_expression or "").strip(),
                sample_note=_normalize_optional_text(group.sample_note),
            )
        )
    non_sample_rows = sorted(
        (row for row in draft.rows if not bool(row.is_sample_row)),
        key=lambda item: item.row_order,
    )
    rows: list[ConfirmedMatrixRow] = []
    confirmed_row_id_by_draft_row: dict[str, str] = {}
    for index, row in enumerate(non_sample_rows, start=1):
        confirmed_row_id = f"cmr-{uuid4().hex}"
        confirmed_row_id_by_draft_row[row.draft_row_id] = confirmed_row_id
        rows.append(
            ConfirmedMatrixRow(
                confirmed_row_id=confirmed_row_id,
                confirmed_matrix_id=confirmed_matrix_id,
                draft_row_id=row.draft_row_id,
                source_row_snapshot_id=row.source_row_snapshot_id,
                row_order=index,
                test_item=row.test_item,
                source_section=_normalize_optional_text(row.source_section),
                method=_normalize_optional_text(row.method),
                condition=_normalize_optional_text(row.condition),
                requirement=_normalize_optional_text(row.requirement),
                day_expression=_normalize_optional_text(row.day_expression),
            )
        )
    cells: list[ConfirmedMatrixCell] = []
    seen_identity: set[tuple[str, str]] = set()
    for cell in draft.cells:
        confirmed_group_id = confirmed_group_id_by_draft_group.get(cell.draft_group_id)
        confirmed_row_id = confirmed_row_id_by_draft_row.get(cell.draft_row_id)
        if confirmed_group_id is None or confirmed_row_id is None:
            continue
        cell_value = cell.cell_value.strip()
        if not cell_value:
            continue
        identity = (confirmed_row_id, confirmed_group_id)
        if identity in seen_identity:
            continue
        seen_identity.add(identity)
        cells.append(
            ConfirmedMatrixCell(
                confirmed_cell_id=f"cmc-{uuid4().hex}",
                confirmed_matrix_id=confirmed_matrix_id,
                confirmed_row_id=confirmed_row_id,
                confirmed_group_id=confirmed_group_id,
                draft_row_id=cell.draft_row_id,
                draft_group_id=cell.draft_group_id,
                cell_value=cell_value,
            )
        )
    step_quantities = build_confirmed_step_quantities(
        draft=draft,
        confirmed_matrix_id=confirmed_matrix_id,
        confirmed_at=confirmed_at,
        confirmed_group_id_by_draft_group=confirmed_group_id_by_draft_group,
        confirmed_row_id_by_draft_row=confirmed_row_id_by_draft_row,
    )
    return ConfirmedMatrixSnapshot(
        version=version,
        groups=tuple(groups),
        rows=tuple(rows),
        cells=tuple(cells),
        step_quantities=tuple(step_quantities),
        duration_authorities=build_confirmed_duration_authorities(
            draft=draft,
            confirmed_matrix_id=confirmed_matrix_id,
            confirmed_at=confirmed_at,
            confirmed_group_id_by_draft_group=confirmed_group_id_by_draft_group,
            confirmed_row_id_by_draft_row=confirmed_row_id_by_draft_row,
        ),
    )


def carry_forward_duration_authorities(
    *,
    active: ConfirmedMatrixSnapshot,
    draft_id: str,
    group_id_map: dict[str, str],
    row_id_map: dict[str, str],
    updated_at: str,
) -> tuple[ProjectMatrixDraftDurationAuthority, ...]:
    result: list[ProjectMatrixDraftDurationAuthority] = []
    for item in active.duration_authorities:
        group_id = group_id_map.get(item.confirmed_group_id)
        row_id = row_id_map.get(item.confirmed_row_id)
        if group_id is None or row_id is None:
            raise ValueError("Confirmed duration authority lineage is incomplete.")
        result.append(
            ProjectMatrixDraftDurationAuthority(
                draft_duration_authority_id=f"pmda-{uuid4().hex}",
                project_matrix_draft_id=draft_id,
                draft_group_id=group_id,
                draft_row_id=row_id,
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
                created_at=updated_at,
                updated_at=updated_at,
            )
        )
    return tuple(result)


def build_confirmed_duration_authorities(
    *,
    draft: ProjectMatrixDraftSnapshot,
    confirmed_matrix_id: str,
    confirmed_at: str,
    confirmed_group_id_by_draft_group: dict[str, str],
    confirmed_row_id_by_draft_row: dict[str, str],
) -> tuple[ConfirmedMatrixDurationAuthority, ...]:
    result: list[ConfirmedMatrixDurationAuthority] = []
    for item in draft.duration_authorities:
        group_id = confirmed_group_id_by_draft_group.get(item.draft_group_id)
        row_id = confirmed_row_id_by_draft_row.get(item.draft_row_id)
        if group_id is None or row_id is None:
            raise ValueError("Draft duration authority references an unpublished row.")
        result.append(
            ConfirmedMatrixDurationAuthority(
                confirmed_duration_authority_id=f"cmda-{uuid4().hex}",
                confirmed_matrix_id=confirmed_matrix_id,
                confirmed_group_id=group_id,
                confirmed_row_id=row_id,
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
                created_at=confirmed_at,
                updated_at=confirmed_at,
            )
        )
    return tuple(result)


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
