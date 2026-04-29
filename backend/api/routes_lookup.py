"""Read-only project lookup API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from backend.api.dependencies import get_lookup_service
from backend.application.lookup_service import (
    LookupNotFoundError,
    LookupService,
    ProjectLookupRow,
    SampleSummary,
    SampleSummaryRow,
    TestingSummary,
)


router = APIRouter(tags=["lookup"])


class ProjectLookupResponse(BaseModel):
    """One project lookup response row."""

    project_id: str
    project_no: str | None = None
    product_name: str
    requestor: str
    status: str
    ltr_numbers: list[str]
    sample_part_numbers: list[str]
    matched_fields: list[str]


class SampleSummaryRowResponse(BaseModel):
    """One sample summary row response."""

    sample_id: str
    product_name: str
    part_number: str
    revision: str | None = None
    lot_or_traceability: str | None = None
    material: str | None = None
    plating: str | None = None
    housing_material: str | None = None
    quantity: int | None = None


class SampleSummaryResponse(BaseModel):
    """Project sample summary response."""

    project_id: str
    project_no: str | None = None
    product_name: str
    requestor: str
    ltr_numbers: list[str]
    samples: list[SampleSummaryRowResponse]


class TestingSummaryResponse(BaseModel):
    """Project testing condition/method summary response."""

    project_id: str
    project_no: str | None = None
    requested_testing: str | None = None
    test_type: str | None = None
    sample_condition: str | None = None
    requested_completion_date: str | None = None
    applicable_specifications: list[str]
    lab: str | None = None
    assigned_personnel: str | None = None


@router.get("/api/projects/lookup", response_model=list[ProjectLookupResponse])
def lookup_projects(
    query: str = Query(min_length=1),
    service: LookupService = Depends(get_lookup_service),
) -> list[ProjectLookupResponse]:
    """Search structured project, sample, and LTR records."""
    return [_lookup_response(row) for row in service.search_projects(query)]


@router.get(
    "/api/projects/{project_id}/sample-summary",
    response_model=SampleSummaryResponse,
)
def get_sample_summary(
    project_id: str,
    service: LookupService = Depends(get_lookup_service),
) -> SampleSummaryResponse:
    """Return structured sample information for one project."""
    try:
        return _sample_summary_response(service.sample_summary(project_id))
    except LookupNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/api/projects/{project_id}/testing-summary",
    response_model=TestingSummaryResponse,
)
def get_testing_summary(
    project_id: str,
    service: LookupService = Depends(get_lookup_service),
) -> TestingSummaryResponse:
    """Return structured testing condition and method text for one project."""
    try:
        return _testing_summary_response(service.testing_summary(project_id))
    except LookupNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _lookup_response(row: ProjectLookupRow) -> ProjectLookupResponse:
    """Convert a lookup row to API response."""
    return ProjectLookupResponse(
        project_id=row.project_id,
        project_no=row.project_no,
        product_name=row.product_name,
        requestor=row.requestor,
        status=row.status,
        ltr_numbers=list(row.ltr_numbers),
        sample_part_numbers=list(row.sample_part_numbers),
        matched_fields=list(row.matched_fields),
    )


def _sample_summary_response(summary: SampleSummary) -> SampleSummaryResponse:
    """Convert sample summary to API response."""
    return SampleSummaryResponse(
        project_id=summary.project_id,
        project_no=summary.project_no,
        product_name=summary.product_name,
        requestor=summary.requestor,
        ltr_numbers=list(summary.ltr_numbers),
        samples=[_sample_row_response(sample) for sample in summary.samples],
    )


def _sample_row_response(sample: SampleSummaryRow) -> SampleSummaryRowResponse:
    """Convert one sample summary row to API response."""
    return SampleSummaryRowResponse(
        sample_id=sample.sample_id,
        product_name=sample.product_name,
        part_number=sample.part_number,
        revision=sample.revision,
        lot_or_traceability=sample.lot_or_traceability,
        material=sample.material,
        plating=sample.plating,
        housing_material=sample.housing_material,
        quantity=sample.quantity,
    )


def _testing_summary_response(summary: TestingSummary) -> TestingSummaryResponse:
    """Convert testing summary to API response."""
    return TestingSummaryResponse(
        project_id=summary.project_id,
        project_no=summary.project_no,
        requested_testing=summary.requested_testing,
        test_type=summary.test_type,
        sample_condition=summary.sample_condition,
        requested_completion_date=summary.requested_completion_date,
        applicable_specifications=list(summary.applicable_specifications),
        lab=summary.lab,
        assigned_personnel=summary.assigned_personnel,
    )
