"""Pure builders for Project Matrix draft payloads."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import uuid4

from backend.domain import (
    ProjectMatrixDraftCell,
    ProjectMatrixDraftGroup,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftRow,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStatus,
    SourceMatrixImportRecord,
    SourceMatrixSnapshot,
)
from backend.domain.project_matrix_draft_models import (
    ProjectMatrixDraftDurationAuthority,
)

if TYPE_CHECKING:
    from backend.application.project_matrix_draft_persistence_service import (
        CreateProjectMatrixDraftFromSourceImportCommand,
        ProjectMatrixDraftGroupInput,
        ProjectMatrixDraftRowInput,
        ProjectMatrixDurationAuthorityInput,
        UpdateProjectMatrixDraftCommand,
    )


class ProjectMatrixDraftPersistenceError(ValueError):
    """Raised when a Project Matrix draft payload is invalid."""


def _resolve_selected_group_keys(
    command: CreateProjectMatrixDraftFromSourceImportCommand,
    import_record: SourceMatrixImportRecord,
    source_snapshot: SourceMatrixSnapshot,
) -> set[str]:
    available_keys = {group.group_key for group in source_snapshot.groups}
    explicit = command.selected_group_keys
    if explicit is not None:
        selected = {item.strip() for item in explicit if item.strip()}
        unknown = sorted(selected - available_keys)
        if unknown:
            raise ProjectMatrixDraftPersistenceError(
                f"Unknown selected group keys: {', '.join(unknown)}"
            )
        return selected
    imported_keys = {item.strip() for item in import_record.selected_group_keys_at_import if item.strip()}
    if imported_keys:
        return imported_keys & available_keys
    return available_keys


def _build_draft_snapshot(
    command: CreateProjectMatrixDraftFromSourceImportCommand,
    source_snapshot: SourceMatrixSnapshot,
    selected_keys: set[str],
) -> ProjectMatrixDraftSnapshot:
    now = _utc_now()
    draft_id = f"pmd-{uuid4().hex}"
    record = ProjectMatrixDraftRecord(
        project_matrix_draft_id=draft_id,
        project_id=command.project_id,
        source_import_id=command.source_import_id,
        source_snapshot_id=source_snapshot.snapshot_id,
        status=ProjectMatrixDraftStatus.DRAFT,
        created_at=now,
        updated_at=now,
        base_confirmed_matrix_id=None,
    )
    groups = tuple(
        ProjectMatrixDraftGroup(
            draft_group_id=f"pmdg-{uuid4().hex}",
            project_matrix_draft_id=draft_id,
            source_group_snapshot_id=group.group_snapshot_id,
            group_order=group.group_order,
            group_key=group.group_key,
            group_label=group.group_label,
            is_selected=group.group_key in selected_keys,
            sample_quantity_expression=group.sample_quantity_expression,
            sample_note=group.sample_note,
        )
        for group in source_snapshot.groups
    )
    rows = tuple(
        ProjectMatrixDraftRow(
            draft_row_id=f"pmdr-{uuid4().hex}",
            project_matrix_draft_id=draft_id,
            source_row_snapshot_id=row.row_snapshot_id,
            row_order=row.row_order,
            test_item=row.test_item,
            source_section=row.source_section,
            method=None,
            condition=None,
            requirement=None,
            day_expression=None,
            is_sample_row=row.is_sample_row,
        )
        for row in source_snapshot.rows
    )
    row_by_source = {row.source_row_snapshot_id: row.draft_row_id for row in rows}
    group_by_source = {group.source_group_snapshot_id: group.draft_group_id for group in groups}
    cells: list[ProjectMatrixDraftCell] = []
    for source_cell in source_snapshot.cells:
        cell_value = source_cell.cell_value.strip()
        if not cell_value:
            continue
        mapped_row = row_by_source.get(source_cell.row_snapshot_id)
        mapped_group = group_by_source.get(source_cell.group_snapshot_id)
        if mapped_row is None or mapped_group is None:
            continue
        cells.append(
            ProjectMatrixDraftCell(
                draft_cell_id=f"pmdc-{uuid4().hex}",
                project_matrix_draft_id=draft_id,
                draft_row_id=mapped_row,
                draft_group_id=mapped_group,
                cell_value=cell_value,
            )
        )
    return ProjectMatrixDraftSnapshot(
        record=record,
        groups=groups,
        rows=rows,
        cells=tuple(cells),
        duration_authorities=_draft_authorities_from_source(
            source_snapshot=source_snapshot,
            draft_id=draft_id,
            group_by_source=group_by_source,
            row_by_source=row_by_source,
            selected_group_ids={
                group.draft_group_id for group in groups if group.is_selected
            },
            now=now,
        ),
    )


def _build_updated_snapshot(
    existing: ProjectMatrixDraftSnapshot,
    command: UpdateProjectMatrixDraftCommand,
) -> ProjectMatrixDraftSnapshot:
    _reject_duplicate_row_identities(command.rows)
    draft_id = existing.record.project_matrix_draft_id
    existing_group_by_id = {group.draft_group_id: group for group in existing.groups}
    existing_row_by_id = {row.draft_row_id: row for row in existing.rows}
    existing_group_by_source = {
        group.source_group_snapshot_id: group
        for group in existing.groups
        if group.source_group_snapshot_id
    }
    existing_row_by_source = {
        row.source_row_snapshot_id: row
        for row in existing.rows
        if row.source_row_snapshot_id
    }
    group_id_map: dict[str, str] = {}
    row_id_map: dict[str, str] = {}
    groups: list[ProjectMatrixDraftGroup] = []
    rows: list[ProjectMatrixDraftRow] = []
    for index, group_input in enumerate(command.groups, start=1):
        group = _normalized_group(
            draft_id=draft_id,
            index=index,
            group_input=group_input,
            group_id_map=group_id_map,
            existing_group_by_id=existing_group_by_id,
            existing_group_by_source=existing_group_by_source,
        )
        groups.append(group)
    for index, row_input in enumerate(command.rows, start=1):
        row = _normalized_row(
            draft_id=draft_id,
            index=index,
            row_input=row_input,
            row_id_map=row_id_map,
            existing_row_by_id=existing_row_by_id,
            existing_row_by_source=existing_row_by_source,
        )
        rows.append(row)
    row_ids = {row.draft_row_id for row in rows}
    group_ids = {group.draft_group_id for group in groups}
    cells: list[ProjectMatrixDraftCell] = []
    seen_cell_identity: set[tuple[str, str]] = set()
    for cell_input in command.cells:
        raw_row_id = cell_input.draft_row_id.strip()
        raw_group_id = cell_input.draft_group_id.strip()
        mapped_row_id = row_id_map.get(raw_row_id, raw_row_id)
        mapped_group_id = group_id_map.get(raw_group_id, raw_group_id)
        if mapped_row_id not in row_ids:
            raise ProjectMatrixDraftPersistenceError(
                f"Cell references unknown row id: {cell_input.draft_row_id}"
            )
        if mapped_group_id not in group_ids:
            raise ProjectMatrixDraftPersistenceError(
                f"Cell references unknown group id: {cell_input.draft_group_id}"
            )
        cell_value = cell_input.cell_value.strip()
        if not cell_value:
            continue
        identity = (mapped_row_id, mapped_group_id)
        if identity in seen_cell_identity:
            continue
        seen_cell_identity.add(identity)
        cells.append(
            ProjectMatrixDraftCell(
                draft_cell_id=f"pmdc-{uuid4().hex}",
                project_matrix_draft_id=draft_id,
                draft_row_id=mapped_row_id,
                draft_group_id=mapped_group_id,
                cell_value=cell_value,
            )
        )
    now = _utc_now()
    updated_record = ProjectMatrixDraftRecord(
        project_matrix_draft_id=existing.record.project_matrix_draft_id,
        project_id=existing.record.project_id,
        source_import_id=existing.record.source_import_id,
        source_snapshot_id=existing.record.source_snapshot_id,
        status=existing.record.status,
        created_at=existing.record.created_at,
        updated_at=now,
        base_confirmed_matrix_id=existing.record.base_confirmed_matrix_id,
        pre_test_buffer_days=_normalize_optional_text(command.pre_test_buffer_days),
        post_test_buffer_days=_normalize_optional_text(command.post_test_buffer_days),
        sample_received_date=_normalize_optional_text(command.sample_received_date),
        planned_test_start_date=_normalize_optional_text(command.planned_test_start_date),
        planned_test_complete_date=_normalize_optional_text(command.planned_test_complete_date),
        estimated_completion_date=_normalize_optional_text(command.estimated_completion_date),
    )
    return ProjectMatrixDraftSnapshot(
        record=updated_record,
        groups=tuple(groups),
        rows=tuple(rows),
        cells=tuple(cells),
        step_quantities=existing.step_quantities,
        duration_authorities=_updated_duration_authorities(
            existing=existing,
            command=command,
            group_id_map=group_id_map,
            row_id_map=row_id_map,
            valid_group_ids=group_ids,
            valid_row_ids=row_ids,
            now=now,
        ),
    )


def _reject_duplicate_row_identities(
    rows: tuple[ProjectMatrixDraftRowInput, ...],
) -> None:
    seen_draft_row_ids: set[str] = set()
    seen_source_ids: set[str] = set()
    for row in rows:
        draft_row_id = (row.draft_row_id or "").strip()
        if draft_row_id:
            if draft_row_id in seen_draft_row_ids:
                raise ProjectMatrixDraftPersistenceError(
                    f"Duplicate draft row identity: {draft_row_id}"
                )
            seen_draft_row_ids.add(draft_row_id)
        source_id = (row.source_row_snapshot_id or "").strip()
        if not source_id:
            continue
        if source_id in seen_source_ids:
            raise ProjectMatrixDraftPersistenceError(
                f"Duplicate source row lineage: {source_id}"
            )
        seen_source_ids.add(source_id)


def _draft_authorities_from_source(
    *,
    source_snapshot: SourceMatrixSnapshot,
    draft_id: str,
    group_by_source: dict[str | None, str],
    row_by_source: dict[str | None, str],
    selected_group_ids: set[str],
    now: str,
) -> tuple[ProjectMatrixDraftDurationAuthority, ...]:
    result: list[ProjectMatrixDraftDurationAuthority] = []
    for item in source_snapshot.duration_authorities:
        group_id = group_by_source.get(item.source_group_snapshot_id)
        row_id = row_by_source.get(item.source_row_snapshot_id)
        if group_id is None or row_id is None:
            raise ProjectMatrixDraftPersistenceError(
                "Duration authority source identity is not present in the Matrix draft."
            )
        if group_id not in selected_group_ids:
            continue
        result.append(
            ProjectMatrixDraftDurationAuthority(
                draft_duration_authority_id=f"pmda-{uuid4().hex}",
                project_matrix_draft_id=draft_id,
                draft_group_id=group_id,
                draft_row_id=row_id,
                step_sequence=item.step_sequence,
                step_suffix_note=_canonical_suffix(item.step_suffix_note),
                duration_value=item.duration_value,
                duration_unit=item.duration_unit,
                normalized_hours=item.normalized_hours,
                source_kind=item.source_kind,
                source_field=item.source_field,
                source_import_id=item.source_import_id,
                source_fingerprint=item.source_fingerprint,
                lineage_fingerprint=item.lineage_fingerprint,
                authority_revision=item.authority_revision,
                status="usable",
                diagnostic_code=None,
                diagnostic_message=None,
                created_at=now,
                updated_at=now,
            )
        )
    return tuple(result)


def _updated_duration_authorities(
    *,
    existing: ProjectMatrixDraftSnapshot,
    command: UpdateProjectMatrixDraftCommand,
    group_id_map: dict[str, str],
    row_id_map: dict[str, str],
    valid_group_ids: set[str],
    valid_row_ids: set[str],
    now: str,
) -> tuple[ProjectMatrixDraftDurationAuthority, ...]:
    if not command.duration_authorities_present:
        return tuple(
            item
            for item in existing.duration_authorities
            if item.draft_group_id in valid_group_ids
            and item.draft_row_id in valid_row_ids
        )
    if command.duration_authorities is None:
        return ()
    result: list[ProjectMatrixDraftDurationAuthority] = []
    identities: set[tuple[str, str, int, str]] = set()
    for item in command.duration_authorities:
        group_id = group_id_map.get(item.draft_group_id, item.draft_group_id)
        row_id = row_id_map.get(item.draft_row_id, item.draft_row_id)
        if group_id not in valid_group_ids or row_id not in valid_row_ids:
            raise ProjectMatrixDraftPersistenceError(
                "Duration authority references an unknown Matrix row or group."
            )
        suffix = _canonical_suffix(item.step_suffix_note)
        identity = (group_id, row_id, item.step_sequence, suffix)
        if identity in identities:
            raise ProjectMatrixDraftPersistenceError(
                "Duplicate duration authority identity."
            )
        identities.add(identity)
        unit, hours = _normalize_duration(item.duration_value, item.duration_unit)
        source_field = item.source_field.strip()
        if not source_field or len(source_field) > 128:
            raise ProjectMatrixDraftPersistenceError(
                "Duration authority source field is required and limited to 128 characters."
            )
        if item.source_kind not in {"import_structured", "manual_edit"}:
            raise ProjectMatrixDraftPersistenceError(
                "Unsupported duration authority source kind."
            )
        result.append(
            ProjectMatrixDraftDurationAuthority(
                draft_duration_authority_id=(
                    (item.draft_duration_authority_id or "").strip()
                    or f"pmda-{uuid4().hex}"
                ),
                project_matrix_draft_id=existing.record.project_matrix_draft_id,
                draft_group_id=group_id,
                draft_row_id=row_id,
                step_sequence=item.step_sequence,
                step_suffix_note=suffix,
                duration_value=item.duration_value,
                duration_unit=unit,
                normalized_hours=hours,
                source_kind=item.source_kind,
                source_field=source_field,
                source_import_id=_normalize_optional_text(item.source_import_id),
                source_fingerprint=item.source_fingerprint.strip(),
                lineage_fingerprint=item.lineage_fingerprint.strip(),
                authority_revision=item.authority_revision.strip(),
                status="usable",
                diagnostic_code=None,
                diagnostic_message=None,
                created_at=now,
                updated_at=now,
            )
        )
    return tuple(result)


def _normalize_duration(value: Decimal, unit: str) -> tuple[str, Decimal]:
    if not isinstance(value, Decimal) or not value.is_finite() or value <= 0:
        raise ProjectMatrixDraftPersistenceError(
            "Duration authority value must be a positive finite number."
        )
    normalized_unit = unit.strip().lower()
    if normalized_unit not in {"hour", "hours", "hr", "hrs", "day", "days"}:
        raise ProjectMatrixDraftPersistenceError(
            "Unsupported duration authority unit."
        )
    hours = value * Decimal("24") if normalized_unit in {"day", "days"} else value
    return normalized_unit, hours


def _canonical_suffix(value: str | None) -> str:
    return (value or "").strip()


def _normalized_group(
    *,
    draft_id: str,
    index: int,
    group_input: ProjectMatrixDraftGroupInput,
    group_id_map: dict[str, str],
    existing_group_by_id: dict[str, ProjectMatrixDraftGroup],
    existing_group_by_source: dict[str, ProjectMatrixDraftGroup],
) -> ProjectMatrixDraftGroup:
    raw_group_id = (group_input.draft_group_id or "").strip()
    raw_source_id = (group_input.source_group_snapshot_id or "").strip()
    candidate = existing_group_by_id.get(raw_group_id) if raw_group_id else None
    if candidate is None and raw_source_id:
        candidate = existing_group_by_source.get(raw_source_id)
    draft_group_id = candidate.draft_group_id if candidate else f"pmdg-{uuid4().hex}"
    source_group_snapshot_id = candidate.source_group_snapshot_id if candidate else (raw_source_id or None)
    if raw_group_id:
        group_id_map[raw_group_id] = draft_group_id
    normalized_group_key = group_input.group_key.strip() or f"group_{index}"
    normalized_group_label = group_input.group_label.strip() or normalized_group_key
    sample_quantity_expression = _normalize_optional_text(group_input.sample_quantity_expression)
    sample_note = _normalize_optional_text(group_input.sample_note)
    return ProjectMatrixDraftGroup(
        draft_group_id=draft_group_id,
        project_matrix_draft_id=draft_id,
        source_group_snapshot_id=source_group_snapshot_id,
        group_order=index,
        group_key=normalized_group_key,
        group_label=normalized_group_label,
        is_selected=bool(group_input.is_selected),
        sample_quantity_expression=sample_quantity_expression,
        sample_note=sample_note,
    )


def _normalized_row(
    *,
    draft_id: str,
    index: int,
    row_input: ProjectMatrixDraftRowInput,
    row_id_map: dict[str, str],
    existing_row_by_id: dict[str, ProjectMatrixDraftRow],
    existing_row_by_source: dict[str, ProjectMatrixDraftRow],
) -> ProjectMatrixDraftRow:
    raw_row_id = (row_input.draft_row_id or "").strip()
    raw_source_id = (row_input.source_row_snapshot_id or "").strip()
    candidate = existing_row_by_id.get(raw_row_id) if raw_row_id else None
    if candidate is None and raw_source_id:
        candidate = existing_row_by_source.get(raw_source_id)
    draft_row_id = candidate.draft_row_id if candidate else f"pmdr-{uuid4().hex}"
    source_row_snapshot_id = candidate.source_row_snapshot_id if candidate else (raw_source_id or None)
    if raw_row_id:
        row_id_map[raw_row_id] = draft_row_id
    test_item = row_input.test_item.strip()
    source_section = _normalize_optional_text(row_input.source_section)
    method = _normalize_optional_text(row_input.method)
    condition = _normalize_optional_text(row_input.condition)
    requirement = _normalize_optional_text(row_input.requirement)
    day_expression = _normalize_optional_text(row_input.day_expression)
    return ProjectMatrixDraftRow(
        draft_row_id=draft_row_id,
        project_matrix_draft_id=draft_id,
        source_row_snapshot_id=source_row_snapshot_id,
        row_order=index,
        test_item=test_item,
        source_section=source_section,
        method=method,
        condition=condition,
        requirement=requirement,
        day_expression=day_expression,
        is_sample_row=bool(row_input.is_sample_row),
    )


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
