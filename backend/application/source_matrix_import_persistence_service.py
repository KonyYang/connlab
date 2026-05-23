"""Application service for Source Matrix import snapshot persistence."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
import hashlib
import json
from typing import Any, Protocol
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


class SourceMatrixImportPersistenceError(ValueError):
    """Raised when source matrix snapshot persistence input is invalid."""


class SourceMatrixImportStore(Protocol):
    """Persistence operations required by source matrix import service."""

    def create_import_snapshot(
        self,
        import_record: SourceMatrixImportRecord,
        snapshot: SourceMatrixSnapshot,
    ) -> None:
        """Persist one immutable source matrix import snapshot."""


@dataclass(frozen=True, slots=True)
class PersistSourceMatrixImportCommand:
    """Command payload for persisting one Source Matrix import snapshot."""

    project_id: str
    draft_id: str
    source_document_path: str
    source_document_name: str
    source_format: str
    source_asset_id: str | None
    source_case_id: str | None
    source_draft_id: str | None
    payload: dict[str, Any]
    created_at: str
    task261_commit_fingerprint: str | None = None


@dataclass(frozen=True, slots=True)
class PersistSourceMatrixFromPreviewCommand:
    """Command payload for persisting Source Matrix import from preview payload."""

    project_id: str
    source_document_path: str
    source_document_name: str
    source_format: str
    payload: dict[str, Any]
    selected_group_keys: tuple[str, ...]
    created_at: str
    task261_commit_fingerprint: str | None = None


@dataclass(frozen=True, slots=True)
class SourceMatrixPersistResult:
    """Persisted Source Matrix lineage identifiers."""

    import_id: str
    snapshot_id: str


@dataclass(slots=True)
class _DerivedRow:
    source_row_index: int | None
    sort_priority: tuple[int, int]
    test_item: str
    source_section: str | None
    is_sample_row: bool
    tokens_by_group: dict[int, list[str]] = field(default_factory=dict)


class SourceMatrixImportPersistenceService:
    """Persist immutable Source Matrix import snapshots from draft commit payloads."""

    def __init__(self, *, store: SourceMatrixImportStore) -> None:
        self._store = store

    def persist_from_draft(self, command: PersistSourceMatrixImportCommand) -> str:
        """Persist source matrix import metadata and sparse snapshot body."""
        if not isinstance(command.payload, dict):
            raise SourceMatrixImportPersistenceError("Source matrix payload must be an object.")
        result = self._persist_import_snapshot(
            project_id=command.project_id,
            draft_id=command.draft_id,
            source_document_path=command.source_document_path,
            source_document_name=command.source_document_name,
            source_format=command.source_format,
            source_asset_id=command.source_asset_id,
            source_case_id=command.source_case_id,
            source_draft_id=command.source_draft_id,
            payload=command.payload,
            created_at=command.created_at,
            selected_group_keys_override=None,
            task261_commit_fingerprint=command.task261_commit_fingerprint,
        )
        return result.import_id

    def persist_from_preview(
        self,
        command: PersistSourceMatrixFromPreviewCommand,
    ) -> SourceMatrixPersistResult:
        """Persist source matrix import lineage from preview payload for TASK_261."""
        if len(command.selected_group_keys) == 0:
            raise SourceMatrixImportPersistenceError(
                "selected_group_keys is required for preview persistence."
            )
        return self._persist_import_snapshot(
            project_id=command.project_id,
            draft_id=None,
            source_document_path=command.source_document_path,
            source_document_name=command.source_document_name,
            source_format=command.source_format,
            source_asset_id=None,
            source_case_id=None,
            source_draft_id=None,
            payload=command.payload,
            created_at=command.created_at,
            selected_group_keys_override=command.selected_group_keys,
            task261_commit_fingerprint=command.task261_commit_fingerprint,
        )

    def compute_task261_fingerprint(
        self,
        *,
        payload: dict[str, Any],
        selected_group_keys: tuple[str, ...],
    ) -> str:
        """Return stable TASK_261 fingerprint from canonical payload and selected keys."""
        canonical_payload = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        canonical_selected = json.dumps(list(selected_group_keys), ensure_ascii=False, separators=(",", ":"))
        digest = hashlib.sha256(
            f"{canonical_payload}|{canonical_selected}".encode("utf-8")
        ).hexdigest()
        return digest

    def _persist_import_snapshot(
        self,
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
    ) -> SourceMatrixPersistResult:
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
        import_record = SourceMatrixImportRecord(
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
            warnings=metadata["warnings"],
            blockers=metadata["blockers"],
            selected_group_keys_at_import=metadata["selected_group_keys_at_import"],
            task261_commit_fingerprint=task261_commit_fingerprint,
            created_at=created_at,
        )
        snapshot = SourceMatrixSnapshot(
            snapshot_id=snapshot_id,
            import_id=import_id,
            project_id=project_id,
            source_table_index=_first_int(
                (
                    payload.get("selected_table_index"),
                    _group_source_table_index(payload),
                )
            ),
            rows=rows,
            groups=groups,
            cells=cells,
            created_at=created_at,
        )
        self._store.create_import_snapshot(import_record, snapshot)
        return SourceMatrixPersistResult(import_id=import_id, snapshot_id=snapshot_id)


def _build_groups(payload: dict[str, Any]) -> tuple[SourceMatrixGroupSnapshot, ...]:
    raw_groups = payload.get("groups")
    if not isinstance(raw_groups, list):
        return ()
    groups: list[SourceMatrixGroupSnapshot] = []
    for index, raw_group in enumerate(raw_groups, start=1):
        if not isinstance(raw_group, dict):
            continue
        group_key = _text(raw_group.get("group_key")) or f"group_{index}"
        group_label = _text(raw_group.get("group_label")) or f"Group {index}"
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


def _build_rows_and_cells_from_rows(
    raw_rows: list[Any],
    groups: tuple[SourceMatrixGroupSnapshot, ...],
) -> tuple[tuple[SourceMatrixRowSnapshot, ...], tuple[SourceMatrixCellSnapshot, ...]]:
    rows: list[SourceMatrixRowSnapshot] = []
    cells: list[SourceMatrixCellSnapshot] = []
    for row_order, raw_row in enumerate(raw_rows, start=1):
        if not isinstance(raw_row, dict):
            continue
        row_snapshot_id = f"smr-{uuid4().hex}"
        row = SourceMatrixRowSnapshot(
            row_snapshot_id=row_snapshot_id,
            row_order=row_order,
            source_row_index=_int_or_none(raw_row.get("source_row_index")),
            test_item=_text(raw_row.get("test_item")) or "",
            source_section=_text(raw_row.get("source_section")),
            is_sample_row=bool(raw_row.get("is_sample_row")),
        )
        rows.append(row)
        group_tokens = raw_row.get("group_tokens")
        if not isinstance(group_tokens, dict):
            continue
        for group in groups:
            raw_value = group_tokens.get(group.group_label, group_tokens.get(group.group_key))
            text = _text(raw_value)
            if not text:
                continue
            cells.append(
                SourceMatrixCellSnapshot(
                    cell_snapshot_id=f"smc-{uuid4().hex}",
                    row_snapshot_id=row_snapshot_id,
                    group_snapshot_id=group.group_snapshot_id,
                    cell_value=text,
                )
            )
    return tuple(rows), tuple(cells)


def _build_rows_and_cells_from_steps(
    payload: dict[str, Any],
    groups: tuple[SourceMatrixGroupSnapshot, ...],
) -> tuple[tuple[SourceMatrixRowSnapshot, ...], tuple[SourceMatrixCellSnapshot, ...]]:
    group_entries = payload.get("groups")
    if not isinstance(group_entries, list):
        return (), ()
    derived_rows: dict[tuple[int, int], _DerivedRow] = {}
    auto_index = 0
    for group_index, raw_group in enumerate(group_entries, start=1):
        if not isinstance(raw_group, dict):
            continue
        steps = raw_group.get("steps")
        if not isinstance(steps, list):
            continue
        for step_index, raw_step in enumerate(steps, start=1):
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
                )
            row = derived_rows[row_key]
            raw_token = _text(raw_step.get("raw_token"))
            if raw_token:
                row.tokens_by_group.setdefault(group_index, []).append(raw_token)
    ordered = sorted(derived_rows.values(), key=lambda row: row.sort_priority)
    rows: list[SourceMatrixRowSnapshot] = []
    row_id_by_position: dict[int, str] = {}
    for row_order, row in enumerate(ordered, start=1):
        row_snapshot_id = f"smr-{uuid4().hex}"
        row_id_by_position[row_order] = row_snapshot_id
        rows.append(
            SourceMatrixRowSnapshot(
                row_snapshot_id=row_snapshot_id,
                row_order=row_order,
                source_row_index=row.source_row_index,
                test_item=row.test_item,
                source_section=row.source_section,
                is_sample_row=row.is_sample_row,
            )
        )
    cells: list[SourceMatrixCellSnapshot] = []
    for row_order, row in enumerate(ordered, start=1):
        row_snapshot_id = row_id_by_position[row_order]
        for group_index, group in enumerate(groups, start=1):
            token_list = row.tokens_by_group.get(group_index, [])
            if not token_list:
                continue
            cell_value = ", ".join(token_list).strip()
            if not cell_value:
                continue
            cells.append(
                SourceMatrixCellSnapshot(
                    cell_snapshot_id=f"smc-{uuid4().hex}",
                    row_snapshot_id=row_snapshot_id,
                    group_snapshot_id=group.group_snapshot_id,
                    cell_value=cell_value,
                )
            )
    return tuple(rows), tuple(cells)


def _extract_import_metadata(
    payload: dict[str, Any],
    groups: tuple[SourceMatrixGroupSnapshot, ...],
    created_at: str,
    *,
    selected_group_keys_override: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    metadata = payload.get("source_metadata")
    metadata_dict = metadata if isinstance(metadata, dict) else {}
    warnings = _string_list(payload.get("warnings"))
    blockers = _string_list(payload.get("blockers"))
    selected_group_keys = [item for item in (selected_group_keys_override or ()) if item.strip()]
    if not selected_group_keys:
        selected_group_keys = _string_list(payload.get("selected_group_keys_at_import"))
    if not selected_group_keys:
        selected_group_keys = [group.group_key for group in groups]
    parse_time = (
        _text(metadata_dict.get("parse_time"))
        or _text(payload.get("parse_time"))
        or created_at
    )
    parser_version = (
        _text(metadata_dict.get("parser_version"))
        or _text(payload.get("parser_version"))
        or DEFAULT_MATRIX_PARSER_VERSION
    )
    payload_schema_version = (
        _text(metadata_dict.get("payload_schema_version"))
        or _text(payload.get("payload_schema_version"))
        or DEFAULT_MATRIX_PAYLOAD_SCHEMA_VERSION
    )
    source_spec_number = (
        _text(metadata_dict.get("source_spec_number"))
        or _text(payload.get("source_spec_number"))
    )
    source_spec_revision = (
        _text(metadata_dict.get("source_spec_revision"))
        or _text(payload.get("source_spec_revision"))
    )
    return {
        "warnings": tuple(warnings),
        "blockers": tuple(blockers),
        "selected_group_keys_at_import": tuple(selected_group_keys),
        "parse_time": parse_time,
        "parser_version": parser_version,
        "payload_schema_version": payload_schema_version,
        "source_spec_number": source_spec_number,
        "source_spec_revision": source_spec_revision,
        "import_status": SourceMatrixImportStatus.BLOCKED if blockers else SourceMatrixImportStatus.IMPORTED,
    }


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        if isinstance(item, str):
            text = item.strip()
            if text:
                result.append(text)
    return result


def _text(value: Any) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return None


def _int_or_none(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def _first_int(values: tuple[Any, ...]) -> int | None:
    for value in values:
        parsed = _int_or_none(value)
        if parsed is not None:
            return parsed
    return None


def _group_source_table_index(payload: dict[str, Any]) -> int | None:
    raw_groups = payload.get("groups")
    if not isinstance(raw_groups, list):
        return None
    for group in raw_groups:
        if not isinstance(group, dict):
            continue
        parsed = _int_or_none(group.get("source_table_index"))
        if parsed is not None:
            return parsed
    return None


def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(UTC).isoformat()
