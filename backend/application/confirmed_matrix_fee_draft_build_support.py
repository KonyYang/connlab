"""Behavior-preserving status helpers for confirmed Matrix Fee builds."""

from __future__ import annotations

from datetime import datetime, timezone

from backend.application.confirmed_matrix_fee_draft_models import (
    FeeDraftStatus,
    FeeEvaluationGroup,
    FeeEvaluationWarning,
)
from backend.domain import ConfirmedMatrixSnapshot


def now_iso() -> str:
    """Return the current UTC timestamp in the existing display format."""
    return datetime.now(timezone.utc).isoformat()


def root_warnings(snapshot: ConfirmedMatrixSnapshot) -> list[FeeEvaluationWarning]:
    """Return authority-level Fee warnings for one confirmed Matrix."""
    if snapshot.version.sample_received_date:
        return []
    return [
        FeeEvaluationWarning(
            code="missing_pricing_effective_from",
            message="Sample received date is missing from active Confirmed Matrix authority.",
            scope="confirmed_matrix",
        )
    ]


def draft_status(
    groups: tuple[FeeEvaluationGroup, ...],
    warnings: list[FeeEvaluationWarning],
) -> FeeDraftStatus:
    """Return the existing aggregate Fee draft status."""
    if warnings:
        return "needs_review"
    if not groups:
        return "empty"
    if any(
        item.review_required
        for group in groups
        for item in (*group.manual_line_items, *group.line_items)
    ):
        return "needs_review"
    return "ready"
