"""Backend-managed lookup option API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.api.dependencies import get_lookup_option_service
from backend.application.lookup_options_service import LookupOptionService
from backend.domain.lookup_options import LookupOption


router = APIRouter(tags=["lookup-options"])


class LookupOptionResponse(BaseModel):
    """One lookup option returned to the UI."""

    value: str
    label: str


class IntakePrecheckLookupOptionsResponse(BaseModel):
    """Lookup option groups required by Intake/Precheck."""

    business_unit: list[LookupOptionResponse]
    manufacturing_site: list[LookupOptionResponse]
    results_format: list[LookupOptionResponse]
    test_type: list[LookupOptionResponse]
    sample_status: list[LookupOptionResponse]
    project_type: list[LookupOptionResponse]
    post_testing_disposition: list[LookupOptionResponse]


@router.get(
    "/api/lookups/intake-precheck",
    response_model=IntakePrecheckLookupOptionsResponse,
)
def get_intake_precheck_lookup_options(
    service: LookupOptionService = Depends(get_lookup_option_service),
) -> IntakePrecheckLookupOptionsResponse:
    """Return backend-managed lookup options for Intake/Precheck review."""
    groups = service.intake_precheck_options()
    return IntakePrecheckLookupOptionsResponse(
        business_unit=_option_responses(groups["business_unit"]),
        manufacturing_site=_option_responses(groups["manufacturing_site"]),
        results_format=_option_responses(groups["results_format"]),
        test_type=_option_responses(groups["test_type"]),
        sample_status=_option_responses(groups["sample_status"]),
        project_type=_option_responses(groups["project_type"]),
        post_testing_disposition=_option_responses(groups["post_testing_disposition"]),
    )


def _option_responses(options: tuple[LookupOption, ...]) -> list[LookupOptionResponse]:
    """Convert lookup options to API response models."""
    return [
        LookupOptionResponse(value=option.value, label=option.label)
        for option in options
    ]
