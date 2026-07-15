"""Current-V2 persistence bridge for Matrix Fee rebase promotion."""

from __future__ import annotations

from typing import Protocol

from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportValues,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftSnapshot,
    SaveFeeEvaluationPricingDraftCommand,
)


class FeePricingDraftPersistencePort(Protocol):
    """Narrow persistence port used after a Matrix Fee rebase."""

    def save(self, command: SaveFeeEvaluationPricingDraftCommand):
        """Persist one reviewed pricing draft and return its classified result."""


def persist_current_v2_pricing_draft(
    *,
    persistence_service: FeePricingDraftPersistencePort | None,
    project_id: str,
    edited_values: FeeEvaluationEditedExportValues,
) -> FeeEvaluationPricingDraftSnapshot | None:
    """Persist rebased values only when the V2 result is consumable."""
    if persistence_service is None:
        return None

    result = persistence_service.save(
        SaveFeeEvaluationPricingDraftCommand(
            project_id=project_id,
            edited_values=edited_values,
        )
    )
    if result.status != "current_v2" or result.saved_snapshot is None:
        raise ValueError("Matrix Fee rebase did not persist a current V2 pricing draft.")
    return result.saved_snapshot
