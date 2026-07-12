"""Canonical identities for independent contact-measurement plan authority."""

from __future__ import annotations

from dataclasses import dataclass


class ContactMeasurementPlanIdentityError(ValueError):
    """Raised when a stored or requested authority identity is not canonical."""


@dataclass(frozen=True, slots=True)
class ContactMeasurementTargetIdentity:
    group_anchor: str
    row_anchor: str
    step_sequence: int
    step_suffix_note: str


def build_target_key(
    source_group_snapshot_id: str | None,
    manual_group_anchor_id: str | None,
    source_row_snapshot_id: str | None,
    manual_row_anchor_id: str | None,
    step_sequence: int,
    suffix_note: str | None,
) -> str:
    """Build the immutable target key after validating lineage XOR axes."""
    group = _axis("group", source_group_snapshot_id, manual_group_anchor_id)
    row = _axis("row", source_row_snapshot_id, manual_row_anchor_id)
    if step_sequence <= 0:
        raise ContactMeasurementPlanIdentityError("Step sequence must be positive.")
    suffix = _suffix(suffix_note)
    return f"cmp-target:v1|group:{group}|row:{row}|step:{step_sequence}|suffix:{suffix}"


def parse_target_key(value: str) -> ContactMeasurementTargetIdentity:
    """Parse and validate an already canonical target key."""
    parts = value.split("|")
    if len(parts) != 5 or parts[0] != "cmp-target:v1":
        raise ContactMeasurementPlanIdentityError("Target key is not cmp-target:v1.")
    try:
        group = parts[1].removeprefix("group:")
        row = parts[2].removeprefix("row:")
        step = int(parts[3].removeprefix("step:"))
        suffix = parts[4].removeprefix("suffix:")
    except ValueError as exc:
        raise ContactMeasurementPlanIdentityError("Target key is malformed.") from exc
    if not group or not row or step <= 0 or _suffix(suffix) != suffix:
        raise ContactMeasurementPlanIdentityError("Target key is not canonical.")
    return ContactMeasurementTargetIdentity(group, row, step, suffix)


def build_impact_identity_key(
    category: str,
    subject_key: str,
    before_fingerprint: str | None,
    after_fingerprint: str | None,
) -> str:
    """Return the non-null SQLite dedupe key for one classifier impact."""
    category = _required(category, "Impact category")
    subject_key = _required(subject_key, "Impact subject key")
    before = _text(before_fingerprint) or "none"
    after = _text(after_fingerprint) or "none"
    return f"cmp-impact:v1|category:{category}|subject:{subject_key}|before:{before}|after:{after}"


def build_candidate_subject_key(
    confirmed_matrix_id: str,
    confirmed_group_id: str,
    confirmed_row_id: str,
    step_sequence: int,
    suffix_note: str | None,
) -> str:
    """Build the canonical subject for a current Matrix candidate not yet bound."""
    matrix = _required(confirmed_matrix_id, "Confirmed Matrix id")
    group = _required(confirmed_group_id, "Confirmed group id")
    row = _required(confirmed_row_id, "Confirmed row id")
    if step_sequence <= 0:
        raise ContactMeasurementPlanIdentityError("Step sequence must be positive.")
    return (
        "cmp-candidate:v1"
        f"|matrix:{matrix}|group:{group}|row:{row}"
        f"|step:{step_sequence}|suffix:{_suffix(suffix_note)}"
    )


def _axis(kind: str, source_id: str | None, manual_id: str | None) -> str:
    source, manual = _text(source_id), _text(manual_id)
    if bool(source) == bool(manual):
        raise ContactMeasurementPlanIdentityError(f"{kind.title()} lineage requires exactly one anchor.")
    return source or manual


def _suffix(value: str | None) -> str:
    return _text(value).lower()


def _required(value: str | None, label: str) -> str:
    text = _text(value)
    if not text:
        raise ContactMeasurementPlanIdentityError(f"{label} is required.")
    return text


def _text(value: str | None) -> str:
    return (value or "").strip()
