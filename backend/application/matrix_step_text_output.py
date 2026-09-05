"""Exact per-step text projection shared by draft and confirmed outputs."""

from dataclasses import dataclass, replace

from backend.modules.test_plan.matrix_step_sequence_validation import parse_step_tokens


@dataclass(frozen=True, slots=True)
class MatrixStepTextOutputOverride:
    group_key: str
    row_order: int
    step_sequence: int
    step_suffix_note: str = ""
    description: str | None = None
    requirement: str | None = None


def confirmed_step_text_lookup(snapshot):
    return {
        (item.confirmed_group_id, item.confirmed_row_id, item.step_sequence,
         (item.step_suffix_note or "").strip()): item
        for item in getattr(snapshot, "step_text_overrides", ())
    }


def draft_step_text_lookup(*, groups, rows, overrides):
    """Validate original row positions before any sample-row filtering."""
    group_keys = {group.group_key for group in groups}
    lookup = {}
    for item in overrides:
        key = (item.group_key, item.row_order, item.step_sequence,
               (item.step_suffix_note or "").strip())
        if key in lookup:
            raise ValueError("Duplicate Matrix step text override.")
        if item.group_key not in group_keys or not 1 <= item.row_order <= len(rows):
            raise ValueError("Matrix step text override references an unknown group or row.")
        row = rows[item.row_order - 1]
        tokens, _ = parse_step_tokens((row.group_values or {}).get(item.group_key))
        if row.is_sample_row or not any(
            token.sequence == item.step_sequence and (token.suffix_note or "").strip() == key[3]
            for token in tokens
        ):
            raise ValueError("Matrix step text override references an unknown step.")
        lookup[key] = item
    return lookup


def apply_step_text(step, override):
    """Overlay display text after defaults; keep the canonical test-item classification."""
    if override is None:
        return step
    return replace(
        step,
        description=override.description,
        requirement=step.requirement if override.requirement is None else override.requirement,
        requirement_is_override=override.requirement is not None,
    )
