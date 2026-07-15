"""Optimistic context checks shared by Fee pricing-draft commands."""

from __future__ import annotations


def context_conflict_message(command: object, context: object, *, operation: str) -> str | None:
    """Return the first authority-context mismatch without coupling command DTOs."""
    checks = (
        ("expected_confirmed_matrix_id", "confirmed_matrix_id", "Matrix context"),
        ("expected_confirmed_revision", "confirmed_revision", "Matrix revision"),
        ("expected_fee_rule_version_id", "fee_rule_version_id", "fee rule version"),
    )
    for expected_name, actual_name, label in checks:
        expected = getattr(command, expected_name, None)
        if expected is not None and expected != getattr(context, actual_name):
            return f"Pricing draft {label} changed before {operation}."
    return None


def discard_conflict_message(command: object, snapshot: object) -> str | None:
    """Validate the optional draft-id token required by destructive discard."""
    expected = getattr(command, "expected_pricing_draft_edit_id", None)
    if expected and expected != getattr(snapshot, "draft_edit_id", None):
        return "Pricing draft changed before discard. Reload Fee Evaluation."
    return None
