"""Backend-managed lookup option API routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import get_lookup_option_service, get_settings
from backend.application.lookup_options_service import LookupOptionService
from backend.domain.lookup_options import LookupOption
from backend.shared.config import Settings


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


class LookupOptionImportRequest(BaseModel):
    """Request to import lookup options from a local configuration file."""

    config_path: str
    backup_dir: str | None = None


class LookupOptionImportResponse(BaseModel):
    """Response after importing lookup options."""

    backup_path: str | None
    imported_count: int
    disabled_count: int
    group_keys: list[str]


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


@router.post(
    "/api/lookups/import-config",
    response_model=LookupOptionImportResponse,
)
def import_lookup_options_from_config(
    request: LookupOptionImportRequest,
    service: LookupOptionService = Depends(get_lookup_option_service),
    settings: Settings = Depends(get_settings),
) -> LookupOptionImportResponse:
    """Import lookup options from a local TOML config after backing up SQLite."""
    try:
        result = service.import_from_config(
            Path(request.config_path),
            database_path=settings.database_path,
            backup_dir=Path(request.backup_dir) if request.backup_dir else settings.data_dir / "backups" / "lookup_options",
        )
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return LookupOptionImportResponse(
        backup_path=str(result.backup_path) if result.backup_path else None,
        imported_count=result.imported_count,
        disabled_count=result.disabled_count,
        group_keys=list(result.group_keys),
    )


def _option_responses(options: tuple[LookupOption, ...]) -> list[LookupOptionResponse]:
    """Convert lookup options to API response models."""
    return [
        LookupOptionResponse(value=option.value, label=option.label)
        for option in options
    ]
