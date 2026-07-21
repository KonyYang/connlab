"""Pure construction of Source Matrix import aggregates."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import ntpath
from typing import Any
from uuid import uuid4

from backend.domain import (
    SourceMatrixCellSnapshot,
    SourceMatrixGroupSnapshot,
    SourceMatrixImportRecord,
    SourceMatrixImportStatus,
    SourceMatrixRowSnapshot,
    SourceMatrixSnapshot,
)

DEFAULT_MATRIX_PARSER_VERSION = "product_spec_matrix_parser:v1"
DEFAULT_MATRIX_PAYLOAD_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True, slots=True)
class PreparedSourceMatrixImport:
    import_record: SourceMatrixImportRecord
    snapshot: SourceMatrixSnapshot


@dataclass(slots=True)
class _DerivedRow:
    source_row_index: int | None
    sort_priority: tuple[int, int]
    test_item: str
    source_section: str | None
    is_sample_row: bool
    method: str | None = None
    condition: str | None = None
    requirement: str | None = None
    tokens_by_group: dict[int, list[str]] = field(default_factory=dict)


def prepare_source_matrix_import(
    *,
    project_id: str,
    draft_id: str | None,
    source_document_path: str,
    source_document_name: str,
    source_format: str,
    source_asset_id: str | None,
    source_case_id: str | None,
    source_draft_id: str | None,
    payload: dict[str, Any],
    created_at: str,
    selected_group_keys_override: tuple[str, ...] | None,
    task261_commit_fingerprint: str | None,
) -> PreparedSourceMatrixImport:
    """Build an immutable import record and snapshot without repository access."""
    import_id = f"smi-{uuid4().hex}"
    snapshot_id = f"sms-{uuid4().hex}"
    groups = _build_groups(payload)
    rows, cells = _build_rows_and_cells(payload, groups)
    metadata = _extract_import_metadata(
        payload,
        groups,
        created_at,
        selected_group_keys_override=selected_group_keys_override,
    )
    return PreparedSourceMatrixImport(
        import_record=SourceMatrixImportRecord(
            import_id=import_id,
            project_id=project_id,
            draft_id=draft_id,
            source_document_path=source_document_path,
            source_document_name=source_document_name,
            source_format=source_format,
            source_asset_id=source_asset_id,
            source_case_id=source_case_id,
            source_draft_id=source_draft_id,
            import_status=metadata["import_status"],
            source_spec_number=metadata["source_spec_number"],
            source_spec_revision=metadata["source_spec_revision"],
            parse_time=metadata["parse_time"],
            parser_version=metadata["parser_version"],
            payload_schema_version=metadata["payload_schema_version"],
            source_preview_payload=_serialize_payload(payload),
            warnings=metadata["warnings"],
            blockers=metadata["blockers"],
            selected_group_keys_at_import=metadata["selected_group_keys_at_import"],
            task261_commit_fingerprint=task261_commit_fingerprint,
            created_at=created_at,
        ),
        snapshot=SourceMatrixSnapshot(
            snapshot_id=snapshot_id,
            import_id=import_id,
            project_id=project_id,
            source_table_index=_first_int(
                (payload.get("selected_table_index"), _group_source_table_index(payload))
            ),
            rows=rows,
            groups=groups,
            cells=cells,
            created_at=created_at,
        ),
    )


def canonical_windows_path(value: str) -> str:
    """Return a lexical Windows source path identity without filesystem access."""
    return ntpath.normcase(ntpath.normpath(value.strip()))


def fingerprint_source_snapshot(snapshot: SourceMatrixSnapshot) -> str:
    """Fingerprint source structure and values without generated record IDs."""
    row_keys = {
        row.row_snapshot_id: [row.row_order, row.source_row_index]
        for row in snapshot.rows
    }
    group_keys = {
        group.group_snapshot_id: [group.group_order, group.group_key]
        for group in snapshot.groups
    }
    return fingerprint(
        {
            "table": snapshot.source_table_index,
            "groups": [
                [
                    group.group_order,
                    group.group_key,
                    group.group_label,
                    group.sample_size,
                    group.sample_quantity_expression,
                    group.sample_note,
                ]
                for group in snapshot.groups
            ],
            "rows": [_source_row_identity(row) for row in snapshot.rows],
            "cells": sorted(
                [
                    row_keys[cell.row_snapshot_id],
                    group_keys[cell.group_snapshot_id],
                    cell.cell_value,
                ]
                for cell in snapshot.cells
            ),
        }
    )


def fingerprint_source_rows(snapshot: SourceMatrixSnapshot) -> str:
    return fingerprint([_source_row_identity(row) for row in snapshot.rows])


def fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _source_row_identity(row: SourceMatrixRowSnapshot) -> list[object]:
    return [
        row.row_order,
        row.source_row_index,
        row.test_item,
        row.source_section,
        row.is_sample_row,
        row.method,
        row.condition,
        row.requirement,
    ]


def _build_groups(payload: dict[str, Any]) -> tuple[SourceMatrixGroupSnapshot, ...]:
    raw_groups = payload.get("groups")
    if not isinstance(raw_groups, list):
        return ()
    groups: list[SourceMatrixGroupSnapshot] = []
    for index, raw_group in enumerate(raw_groups, start=1):
        if not isinstance(raw_group, dict):
            continue
        group_key = _text(raw_group.get("group_key")) or f"group_{index}"
        group_label = _normalize_group_label(
            _text(raw_group.get("group_label")), fallback=str(index)
        )
        groups.append(
            SourceMatrixGroupSnapshot(
                group_snapshot_id=f"smg-{uuid4().hex}",
                group_order=index,
                group_key=group_key,
                group_label=group_label,
                sample_size=_int_or_none(raw_group.get("sample_size")),
                sample_quantity_expression=_text(raw_group.get("sample_quantity_expression")),
                sample_note=_text(raw_group.get("sample_note")),
            )
        )
    return tuple(groups)


def _build_rows_and_cells(
    payload: dict[str, Any],
    groups: tuple[SourceMatrixGroupSnapshot, ...],
) -> tuple[tuple[SourceMatrixRowSnapshot, ...], tuple[SourceMatrixCellSnapshot, ...]]:
    raw_rows = payload.get("rows")
    if isinstance(raw_rows, list) and raw_rows:
        return _build_rows_and_cells_from_rows(raw_rows, groups)
    return _build_rows_and_cells_from_steps(payload, groups)


def _build_rows_and_cells_from_rows(raw_rows, groups):
    rows: list[SourceMatrixRowSnapshot] = []
    cells: list[SourceMatrixCellSnapshot] = []
    for row_order, raw_row in enumerate(raw_rows, start=1):
        if not isinstance(raw_row, dict):
            continue
        row_snapshot_id = f"smr-{uuid4().hex}"
        rows.append(
            SourceMatrixRowSnapshot(
                row_snapshot_id=row_snapshot_id,
                row_order=row_order,
                source_row_index=_int_or_none(raw_row.get("source_row_index")),
                test_item=_text(raw_row.get("test_item")) or "",
                source_section=_text(raw_row.get("source_section")),
                is_sample_row=bool(raw_row.get("is_sample_row")),
                method=_text(raw_row.get("method")),
                condition=_text(raw_row.get("condition")),
                requirement=_text(raw_row.get("requirement")),
            )
        )
        group_tokens = raw_row.get("group_tokens")
        if not isinstance(group_tokens, dict):
            continue
        for group in groups:
            text = _group_token_text(group_tokens, group)
            if text:
                cells.append(
                    SourceMatrixCellSnapshot(
                        cell_snapshot_id=f"smc-{uuid4().hex}",
                        row_snapshot_id=row_snapshot_id,
                        group_snapshot_id=group.group_snapshot_id,
                        cell_value=text,
                    )
                )
    return tuple(rows), tuple(cells)


def _group_token_text(group_tokens, group) -> str | None:
    candidates = (
        group.group_label,
        group.group_key,
        f"Group {group.group_label}",
        f"group {group.group_label}",
    )
    for candidate in candidates:
        text = _text(group_tokens.get(candidate))
        if text:
            return text
    normalized_label = _normalize_group_label(
        group.group_label, fallback=group.group_label
    ).casefold()
    for key, raw_value in group_tokens.items():
        if isinstance(key, str) and _normalize_group_label(
            key, fallback=key
        ).casefold() == normalized_label:
            text = _text(raw_value)
            if text:
                return text
    return None


def _build_rows_and_cells_from_steps(payload, groups):
    group_entries = payload.get("groups")
    if not isinstance(group_entries, list):
        return (), ()
    derived_rows: dict[tuple[int, int], _DerivedRow] = {}
    auto_index = 0
    for group_index, raw_group in enumerate(group_entries, start=1):
        if not isinstance(raw_group, dict) or not isinstance(raw_group.get("steps"), list):
            continue
        for raw_step in raw_group["steps"]:
            if not isinstance(raw_step, dict):
                continue
            source_row_index = _int_or_none(raw_step.get("source_row_index"))
            row_key = (0, source_row_index) if source_row_index is not None else (1, auto_index)
            if source_row_index is None:
                auto_index += 1
            if row_key not in derived_rows:
                derived_rows[row_key] = _DerivedRow(
                    source_row_index=source_row_index,
                    sort_priority=(
                        0 if source_row_index is not None else 1,
                        source_row_index if source_row_index is not None else auto_index,
                    ),
                    test_item=_text(raw_step.get("test_item")) or "",
                    source_section=_text(raw_step.get("source_section")),
                    is_sample_row=False,
                    method=_text(raw_step.get("method")),
                    condition=_text(raw_step.get("condition")),
                    requirement=_text(raw_step.get("requirement")),
                )
            raw_token = _text(raw_step.get("raw_token"))
            if raw_token:
                derived_rows[row_key].tokens_by_group.setdefault(group_index, []).append(raw_token)
    ordered = sorted(derived_rows.values(), key=lambda row: row.sort_priority)
    rows: list[SourceMatrixRowSnapshot] = []
    row_ids: dict[int, str] = {}
    for row_order, row in enumerate(ordered, start=1):
        row_ids[row_order] = f"smr-{uuid4().hex}"
        rows.append(
            SourceMatrixRowSnapshot(
                row_snapshot_id=row_ids[row_order],
                row_order=row_order,
                source_row_index=row.source_row_index,
                test_item=row.test_item,
                source_section=row.source_section,
                is_sample_row=row.is_sample_row,
                method=row.method,
                condition=row.condition,
                requirement=row.requirement,
            )
        )
    cells: list[SourceMatrixCellSnapshot] = []
    for row_order, row in enumerate(ordered, start=1):
        for group_index, group in enumerate(groups, start=1):
            value = ", ".join(row.tokens_by_group.get(group_index, [])).strip()
            if value:
                cells.append(
                    SourceMatrixCellSnapshot(
                        cell_snapshot_id=f"smc-{uuid4().hex}",
                        row_snapshot_id=row_ids[row_order],
                        group_snapshot_id=group.group_snapshot_id,
                        cell_value=value,
                    )
                )
    return tuple(rows), tuple(cells)


def _extract_import_metadata(payload, groups, created_at, *, selected_group_keys_override):
    metadata = payload.get("source_metadata")
    metadata_dict = metadata if isinstance(metadata, dict) else {}
    warnings = _string_list(payload.get("warnings"))
    blockers = _string_list(payload.get("blockers"))
    selected = [item for item in (selected_group_keys_override or ()) if item.strip()]
    if not selected:
        selected = _string_list(payload.get("selected_group_keys_at_import"))
    if not selected:
        selected = [group.group_key for group in groups]
    return {
        "warnings": tuple(warnings),
        "blockers": tuple(blockers),
        "selected_group_keys_at_import": tuple(selected),
        "parse_time": _text(metadata_dict.get("parse_time")) or _text(payload.get("parse_time")) or created_at,
        "parser_version": _text(metadata_dict.get("parser_version")) or _text(payload.get("parser_version")) or DEFAULT_MATRIX_PARSER_VERSION,
        "payload_schema_version": _text(metadata_dict.get("payload_schema_version")) or _text(payload.get("payload_schema_version")) or DEFAULT_MATRIX_PAYLOAD_SCHEMA_VERSION,
        "source_spec_number": _text(metadata_dict.get("source_spec_number")) or _text(payload.get("source_spec_number")),
        "source_spec_revision": _text(metadata_dict.get("source_spec_revision")) or _text(payload.get("source_spec_revision")),
        "import_status": SourceMatrixImportStatus.BLOCKED if blockers else SourceMatrixImportStatus.IMPORTED,
    }


def _string_list(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [text for item in value if isinstance(item, str) and (text := item.strip())]


def _text(value: Any) -> str | None:
    return value.strip() or None if isinstance(value, str) else None


def _normalize_group_label(value: str | None, *, fallback: str) -> str:
    text = (value or "").strip()
    if not text:
        return fallback
    normalized = text[5:].lstrip(" _-") if text[:5].lower() == "group" else text
    return normalized.strip() or fallback


def _int_or_none(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _first_int(values: tuple[Any, ...]) -> int | None:
    return next((parsed for value in values if (parsed := _int_or_none(value)) is not None), None)


def _group_source_table_index(payload: dict[str, Any]) -> int | None:
    groups = payload.get("groups")
    if not isinstance(groups, list):
        return None
    return next(
        (
            parsed
            for group in groups
            if isinstance(group, dict)
            and (parsed := _int_or_none(group.get("source_table_index"))) is not None
        ),
        None,
    )


def _serialize_payload(payload: dict[str, Any]) -> dict[str, Any] | None:
    try:
        decoded = json.loads(json.dumps(payload, ensure_ascii=False))
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    return decoded if isinstance(decoded, dict) else None
