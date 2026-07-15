"""Server-side guard for consumers of reviewed Fee pricing-draft V2 values."""

from __future__ import annotations

from dataclasses import replace

from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftLoadResult,
    FeeEvaluationPricingDraftSnapshot,
)


class CurrentFeePricingDraftRequiredError(ValueError):
    """Raised when a downstream consumer is not bound to current reviewed V2 data."""


class CurrentFeePricingDraftGuard:
    """Reject stale, legacy, blocked, or client-only Fee export inputs."""

    def __init__(self, *, pricing_draft_loader: object) -> None:
        self._pricing_draft_loader = pricing_draft_loader

    def require_current(
        self,
        *,
        project_id: str,
        draft_edit_id: str | None,
        generation: int | None,
        payload_fingerprint: str | None,
        validation_token: str | None,
    ) -> FeeEvaluationPricingDraftSnapshot:
        result: FeeEvaluationPricingDraftLoadResult = getattr(
            self._pricing_draft_loader, "load"
        )(project_id)
        snapshot = result.saved_snapshot
        if result.status != "current_v2" or snapshot is None:
            raise CurrentFeePricingDraftRequiredError(
                "Save and review the current Fee Evaluation pricing draft before continuing."
            )
        checks = (
            (draft_edit_id, snapshot.draft_edit_id),
            (generation, snapshot.generation),
            (payload_fingerprint, snapshot.payload_fingerprint),
            (validation_token, snapshot.validation_token),
        )
        if any(expected is None or expected != actual for expected, actual in checks):
            raise CurrentFeePricingDraftRequiredError(
                "Fee Evaluation pricing draft changed. Reload and review before continuing."
            )
        return snapshot


def bind_command_to_current_pricing_draft(command: object, guard: CurrentFeePricingDraftGuard | None):
    """Replace client supplied edited values with the exact server-loaded V2 snapshot."""
    if guard is None:
        return command
    snapshot = guard.require_current(
        project_id=getattr(command, "project_id"),
        draft_edit_id=getattr(command, "pricing_draft_edit_id"),
        generation=getattr(command, "pricing_draft_generation"),
        payload_fingerprint=getattr(command, "pricing_draft_payload_fingerprint"),
        validation_token=getattr(command, "pricing_draft_validation_token"),
    )
    return replace(command, edited_values=snapshot.edited_values)
