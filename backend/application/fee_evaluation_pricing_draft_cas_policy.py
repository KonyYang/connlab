"""Pure compare-and-swap expectation checks for Fee pricing drafts."""

from __future__ import annotations


def save_cas_conflict_message(command: object, existing: object | None) -> str | None:
    """Return a readable conflict message without coupling policy to persistence types."""
    expected_id = getattr(command, "expected_pricing_draft_edit_id", None)
    if existing is None:
        return "Pricing draft no longer exists. Reload before saving." if expected_id else None
    checks = (
        (expected_id, getattr(existing, "draft_edit_id", None), "Pricing draft changed before save. Reload before saving."),
        (getattr(command, "expected_generation", None), getattr(existing, "generation", None), "Pricing draft generation changed before save. Reload before saving."),
        (getattr(command, "expected_payload_fingerprint", None), getattr(existing, "payload_fingerprint", None), "Pricing draft payload changed before save. Reload before saving."),
        (getattr(command, "expected_updated_at", None), getattr(existing, "updated_at", None), "Pricing draft changed before save. Reload before saving."),
    )
    for expected, actual, message in checks:
        if expected is not None and expected != actual:
            return message
    return None
