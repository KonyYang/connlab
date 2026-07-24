"""Normalize structured duration authority from Source Matrix payloads."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
import hashlib
import json
from typing import Any
from uuid import uuid4

from backend.domain import SourceMatrixGroupSnapshot
from backend.domain.source_matrix_models import SourceMatrixDurationAuthority


def build_source_duration_authorities(
    *,
    raw_row: dict[str, Any],
    row_snapshot_id: str,
    groups_by_key: dict[str, SourceMatrixGroupSnapshot],
    snapshot_id: str,
    import_id: str,
    created_at: str,
) -> list[SourceMatrixDurationAuthority]:
    """Validate a full per-row authority collection without text inference."""
    raw_items = raw_row.get("duration_authorities")
    if raw_items is None:
        return []
    if not isinstance(raw_items, list):
        raise ValueError("duration_authorities must be an array or null.")
    result: list[SourceMatrixDurationAuthority] = []
    identities: set[tuple[str, int, str]] = set()
    for raw in raw_items:
        if not isinstance(raw, dict):
            raise ValueError("Each duration authority must be an object.")
        group_key = _text(raw.get("owning_group_key"))
        group = groups_by_key.get(group_key or "")
        if group is None:
            raise ValueError("Duration authority references an unknown group.")
        sequence = _positive_int(raw.get("step_sequence"))
        suffix = _text(raw.get("step_suffix_note")) or ""
        identity = (group.group_snapshot_id, sequence, suffix)
        if identity in identities:
            raise ValueError("Duplicate duration authority identity.")
        identities.add(identity)
        value, unit, hours = _normalized_duration(
            raw.get("duration_value"),
            raw.get("duration_unit"),
        )
        source_field = _text(raw.get("source_field"))
        source_identity = raw.get("source_identity")
        if not source_field or len(source_field) > 128:
            raise ValueError("Duration authority source_field is required.")
        if not isinstance(source_identity, dict):
            raise ValueError("Duration authority source_identity is required.")
        if _text(source_identity.get("row_snapshot_id")) not in {
            None,
            row_snapshot_id,
        }:
            raise ValueError("Duration authority row identity is stale.")
        if _text(source_identity.get("group_key")) not in {None, group.group_key}:
            raise ValueError("Duration authority group identity is stale.")
        authority_fingerprint = _fingerprint(
            {
                "group_key": group.group_key,
                "row_snapshot_id": row_snapshot_id,
                "step_sequence": sequence,
                "step_suffix_note": suffix,
                "duration_value": format(value, "f"),
                "duration_unit": unit,
                "source_field": source_field,
            }
        )
        result.append(
            SourceMatrixDurationAuthority(
                source_duration_authority_id=f"smda-{uuid4().hex}",
                source_snapshot_id=snapshot_id,
                source_group_snapshot_id=group.group_snapshot_id,
                source_row_snapshot_id=row_snapshot_id,
                step_sequence=sequence,
                step_suffix_note=suffix,
                duration_value=value,
                duration_unit=unit,
                normalized_hours=hours,
                source_kind="import_structured",
                source_field=source_field,
                source_import_id=import_id,
                source_fingerprint=authority_fingerprint,
                lineage_fingerprint=authority_fingerprint,
                authority_revision="1",
                status="usable",
                diagnostic_code=None,
                diagnostic_message=None,
                created_at=created_at,
                updated_at=created_at,
            )
        )
    return result


def _normalized_duration(raw_value: Any, raw_unit: Any) -> tuple[Decimal, str, Decimal]:
    if isinstance(raw_value, bool):
        raise ValueError("Duration authority value must be numeric.")
    try:
        value = Decimal(str(raw_value))
    except (InvalidOperation, ValueError):
        raise ValueError("Duration authority value must be numeric.") from None
    if not value.is_finite() or value <= 0:
        raise ValueError("Duration authority value must be positive and finite.")
    unit = (_text(raw_unit) or "").lower()
    if unit not in {"hour", "hours", "hr", "hrs", "day", "days"}:
        raise ValueError("Unsupported duration authority unit.")
    return value, unit, value * Decimal("24") if unit in {"day", "days"} else value


def _positive_int(value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError("Duration authority step_sequence must be positive.")
    return value


def _text(value: Any) -> str | None:
    return value.strip() or None if isinstance(value, str) else None


def _fingerprint(value: object) -> str:
    canonical = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
