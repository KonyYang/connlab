"""Typed HTTP mapping shared by Fee Evaluation pricing-draft consumers."""

from __future__ import annotations

from typing import NoReturn

from fastapi import HTTPException
from pydantic import BaseModel

from backend.application.fee_evaluation_current_pricing_draft_guard import (
    CurrentFeePricingDraftRequiredError,
)


class FeePricingDraftAttestationRequest(BaseModel):
    """Optional V2 pricing-draft attestation carried by Fee export requests."""

    pricing_draft_edit_id: str | None = None
    pricing_draft_generation: int | None = None
    pricing_draft_payload_fingerprint: str | None = None
    pricing_draft_validation_token: str | None = None


def raise_fee_pricing_draft_not_current(
    exc: CurrentFeePricingDraftRequiredError,
) -> NoReturn:
    """Return the stable conflict response for stale or missing V2 pricing drafts."""
    raise HTTPException(
        status_code=409,
        detail={"code": "fee_pricing_draft_not_current", "message": str(exc)},
    ) from exc
