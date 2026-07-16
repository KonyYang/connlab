"""Load source-faithful Unit Price Reference snapshots from reviewed JSON."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


EXPECTED_SOURCE_FILE_NAME = "FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls"
EXPECTED_SOURCE_SHEET = "Unit Price Reference"
EXPECTED_SOURCE_HASH = "sha256:fb788038631aa0a12f1a052b630513718d9fa1bb64bae647e897e18529ef8a5d"
EXPECTED_EFFECTIVE_ROWS = frozenset(range(4, 48))
EXPECTED_POLICY_ROWS = frozenset({49})
_SOURCE_HASH_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


class FeeReferenceSnapshotError(ValueError):
    """Base error for an unreadable or invalid fee reference snapshot."""


class FeeReferenceSnapshotLoadError(FeeReferenceSnapshotError):
    """Raised when a fee reference snapshot cannot be read or decoded."""


class FeeReferenceSnapshotValidationError(FeeReferenceSnapshotError):
    """Raised when a fee reference snapshot violates its authority contract."""


@dataclass(frozen=True, slots=True)
class FeeReferenceSource:
    """Identity of the workbook source captured by a snapshot."""

    source_file_name: str
    source_sheet: str
    source_hash: str
    captured_at: str


@dataclass(frozen=True, slots=True)
class FeeReferenceRow:
    """Raw source fields from one effective Unit Price Reference row."""

    source_row: int
    english_description: str
    chinese_description: str
    base_fee_text: str
    unit_price_text: str
    applicable_standard: str
    range_condition: str
    chamber_or_note: str


@dataclass(frozen=True, slots=True)
class FeeReferencePolicy:
    """Non-automatic policy metadata captured from the reference sheet."""

    source_row: int
    policy_type: str
    text: str


@dataclass(frozen=True, slots=True)
class FeeReferenceSnapshot:
    """Validated source identity, effective rows, and policy metadata."""

    source: FeeReferenceSource
    rows: tuple[FeeReferenceRow, ...]
    policies: tuple[FeeReferencePolicy, ...]


def load_fee_reference_snapshot(path: Path) -> FeeReferenceSnapshot:
    """Load and strictly validate one reviewed Unit Price Reference snapshot."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise FeeReferenceSnapshotLoadError(f"Unable to read fee reference snapshot: {path}") from exc
    except json.JSONDecodeError as exc:
        raise FeeReferenceSnapshotLoadError(f"Invalid JSON in fee reference snapshot: {path}") from exc

    root = _require_mapping(payload, "snapshot")
    source = _parse_source(root.get("source"))
    rows = _parse_rows(root.get("rows"))
    policies = _parse_policies(root.get("policies"))
    _validate_source(source)
    _validate_row_coverage(rows)
    _validate_policy_coverage(policies)
    return FeeReferenceSnapshot(source=source, rows=rows, policies=policies)


def _parse_source(payload: Any) -> FeeReferenceSource:
    """Parse source identity without changing source text."""
    source = _require_mapping(payload, "source")
    return FeeReferenceSource(
        source_file_name=_require_string(source.get("source_file_name"), "source.source_file_name"),
        source_sheet=_require_string(source.get("source_sheet"), "source.source_sheet"),
        source_hash=_require_string(source.get("source_hash"), "source.source_hash").lower(),
        captured_at=_require_string(source.get("captured_at"), "source.captured_at"),
    )


def _parse_rows(payload: Any) -> tuple[FeeReferenceRow, ...]:
    """Parse source rows in their committed order."""
    entries = _require_list(payload, "rows")
    rows: list[FeeReferenceRow] = []
    for index, entry in enumerate(entries):
        context = f"rows[{index}]"
        row = _require_mapping(entry, context)
        english_description = _require_string(
            row.get("english_description"),
            f"{context}.english_description",
        )
        if not english_description.strip():
            raise FeeReferenceSnapshotValidationError(
                f"English description is required for {context}."
            )
        rows.append(
            FeeReferenceRow(
                source_row=_require_int(row.get("source_row"), f"{context}.source_row"),
                english_description=english_description,
                chinese_description=_require_string(
                    row.get("chinese_description"),
                    f"{context}.chinese_description",
                ),
                base_fee_text=_require_string(row.get("base_fee_text"), f"{context}.base_fee_text"),
                unit_price_text=_require_string(
                    row.get("unit_price_text"),
                    f"{context}.unit_price_text",
                ),
                applicable_standard=_require_string(
                    row.get("applicable_standard"),
                    f"{context}.applicable_standard",
                ),
                range_condition=_require_string(
                    row.get("range_condition"),
                    f"{context}.range_condition",
                ),
                chamber_or_note=_require_string(
                    row.get("chamber_or_note"),
                    f"{context}.chamber_or_note",
                ),
            )
        )
    return tuple(rows)


def _parse_policies(payload: Any) -> tuple[FeeReferencePolicy, ...]:
    """Parse non-automatic policy rows."""
    entries = _require_list(payload, "policies")
    policies: list[FeeReferencePolicy] = []
    for index, entry in enumerate(entries):
        context = f"policies[{index}]"
        policy = _require_mapping(entry, context)
        policies.append(
            FeeReferencePolicy(
                source_row=_require_int(policy.get("source_row"), f"{context}.source_row"),
                policy_type=_require_string(policy.get("policy_type"), f"{context}.policy_type"),
                text=_require_string(policy.get("text"), f"{context}.text"),
            )
        )
    return tuple(policies)


def _validate_source(source: FeeReferenceSource) -> None:
    """Require the approved workbook identity and an ISO capture timestamp."""
    if source.source_file_name != EXPECTED_SOURCE_FILE_NAME:
        raise FeeReferenceSnapshotValidationError("Unexpected source file name.")
    if source.source_sheet != EXPECTED_SOURCE_SHEET:
        raise FeeReferenceSnapshotValidationError("Unexpected source sheet.")
    if not _SOURCE_HASH_PATTERN.fullmatch(source.source_hash):
        raise FeeReferenceSnapshotValidationError("Invalid source hash format.")
    if source.source_hash != EXPECTED_SOURCE_HASH:
        raise FeeReferenceSnapshotValidationError("Unexpected source hash.")
    try:
        datetime.fromisoformat(source.captured_at)
    except ValueError as exc:
        raise FeeReferenceSnapshotValidationError("source.captured_at must be ISO-8601 compatible.") from exc


def _validate_row_coverage(rows: tuple[FeeReferenceRow, ...]) -> None:
    """Require exactly one effective source row for every row from 4 through 47."""
    row_numbers = [row.source_row for row in rows]
    duplicate = _first_duplicate(row_numbers)
    if duplicate is not None:
        raise FeeReferenceSnapshotValidationError(f"Duplicate source row: {duplicate}")
    actual = set(row_numbers)
    missing = sorted(EXPECTED_EFFECTIVE_ROWS - actual)
    if missing:
        raise FeeReferenceSnapshotValidationError(f"Missing effective source rows: {_join_rows(missing)}")
    unexpected = sorted(actual - EXPECTED_EFFECTIVE_ROWS)
    if unexpected:
        raise FeeReferenceSnapshotValidationError(
            f"Unexpected effective source rows: {_join_rows(unexpected)}"
        )


def _validate_policy_coverage(policies: tuple[FeeReferencePolicy, ...]) -> None:
    """Require exactly the approved policy row and complete policy text."""
    row_numbers = [policy.source_row for policy in policies]
    duplicate = _first_duplicate(row_numbers)
    if duplicate is not None:
        raise FeeReferenceSnapshotValidationError(f"Duplicate policy row: {duplicate}")
    actual = set(row_numbers)
    missing = sorted(EXPECTED_POLICY_ROWS - actual)
    if missing:
        raise FeeReferenceSnapshotValidationError(f"Missing policy rows: {_join_rows(missing)}")
    unexpected = sorted(actual - EXPECTED_POLICY_ROWS)
    if unexpected:
        raise FeeReferenceSnapshotValidationError(f"Unexpected policy rows: {_join_rows(unexpected)}")
    policy = policies[0]
    if policy.policy_type != "discount_principles":
        raise FeeReferenceSnapshotValidationError("Unexpected policy type for row 49.")
    if not policy.text.strip():
        raise FeeReferenceSnapshotValidationError("Policy row 49 text is required.")


def _first_duplicate(values: list[int]) -> int | None:
    """Return the first duplicated integer while preserving input order."""
    seen: set[int] = set()
    for value in values:
        if value in seen:
            return value
        seen.add(value)
    return None


def _join_rows(values: list[int]) -> str:
    """Format row numbers for stable validation messages."""
    return ", ".join(str(value) for value in values)


def _require_mapping(value: Any, context: str) -> dict[str, Any]:
    """Require a JSON object."""
    if not isinstance(value, dict):
        raise FeeReferenceSnapshotValidationError(f"{context} must be a JSON object.")
    return value


def _require_list(value: Any, context: str) -> list[Any]:
    """Require a JSON array."""
    if not isinstance(value, list):
        raise FeeReferenceSnapshotValidationError(f"{context} must be a JSON array.")
    return value


def _require_string(value: Any, context: str) -> str:
    """Require a JSON string while preserving its exact content."""
    if not isinstance(value, str):
        raise FeeReferenceSnapshotValidationError(f"{context} must be a string.")
    return value


def _require_int(value: Any, context: str) -> int:
    """Require a JSON integer but reject booleans."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise FeeReferenceSnapshotValidationError(f"{context} must be an integer.")
    return value
