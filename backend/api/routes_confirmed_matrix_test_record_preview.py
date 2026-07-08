"""Confirmed-Matrix-backed Test Record preview read-only API route."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import get_confirmed_matrix_test_record_preview_service
from backend.application.confirmed_matrix_test_record_preview_service import (
    BuildConfirmedMatrixTestRecordPreviewCommand,
    ConfirmedMatrixTestRecordPreview,
    ConfirmedMatrixTestRecordPreviewError,
    ConfirmedMatrixTestRecordPreviewGroup,
    ConfirmedMatrixTestRecordPreviewNotFoundError,
    ConfirmedMatrixTestRecordPreviewService,
    ConfirmedMatrixTestRecordPreviewStep,
    ConfirmedMatrixTestRecordStepQuantity,
)


router = APIRouter(tags=["confirmed-matrix-test-record-preview"])


class ConfirmedMatrixTestRecordPreviewStepResponse(BaseModel):
    sequence: int
    raw_token: str
    test_item: str
    section: str
    method: str
    condition: str
    requirement: str
    quantity: "ConfirmedMatrixTestRecordStepQuantityResponse | None" = None


class ConfirmedMatrixTestRecordStepQuantityResponse(BaseModel):
    test_points_per_sample: str | None
    readings_per_point: str | None
    contact_points_per_sample: str | None
    total_readings: str | None
    status: str
    source: str | None
    review_reason: str | None


class ConfirmedMatrixTestRecordPreviewGroupResponse(BaseModel):
    group_key: str
    group_label: str
    sample_quantity_expression: str
    step_count: int
    steps: list[ConfirmedMatrixTestRecordPreviewStepResponse]


class ConfirmedMatrixTestRecordPreviewResponse(BaseModel):
    project_id: str
    confirmed_matrix_id: str
    preview_status: str
    groups: list[ConfirmedMatrixTestRecordPreviewGroupResponse]


@router.get(
    "/api/projects/{project_id}/confirmed-matrix/test-record-preview",
    response_model=ConfirmedMatrixTestRecordPreviewResponse,
)
def get_confirmed_matrix_test_record_preview(
    project_id: str,
    service: ConfirmedMatrixTestRecordPreviewService = Depends(
        get_confirmed_matrix_test_record_preview_service
    ),
) -> ConfirmedMatrixTestRecordPreviewResponse:
    """Return Test Record preview rows derived from active confirmed Matrix authority."""
    try:
        preview = service.build_preview(
            BuildConfirmedMatrixTestRecordPreviewCommand(project_id=project_id)
        )
    except ConfirmedMatrixTestRecordPreviewNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ConfirmedMatrixTestRecordPreviewError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _to_response(preview)


def _to_response(
    preview: ConfirmedMatrixTestRecordPreview,
) -> ConfirmedMatrixTestRecordPreviewResponse:
    return ConfirmedMatrixTestRecordPreviewResponse(
        project_id=preview.project_id,
        confirmed_matrix_id=preview.confirmed_matrix_id,
        preview_status=preview.preview_status,
        groups=[_to_group_response(group) for group in preview.groups],
    )


def _to_group_response(
    group: ConfirmedMatrixTestRecordPreviewGroup,
) -> ConfirmedMatrixTestRecordPreviewGroupResponse:
    return ConfirmedMatrixTestRecordPreviewGroupResponse(
        group_key=group.group_key,
        group_label=group.group_label,
        sample_quantity_expression=group.sample_quantity_expression,
        step_count=group.step_count,
        steps=[_to_step_response(step) for step in group.steps],
    )


def _to_step_response(
    step: ConfirmedMatrixTestRecordPreviewStep,
) -> ConfirmedMatrixTestRecordPreviewStepResponse:
    return ConfirmedMatrixTestRecordPreviewStepResponse(
        sequence=step.sequence,
        raw_token=_display_step_token(step.raw_token, step.suffix_note),
        test_item=step.test_item,
        section=step.section,
        method=step.method,
        condition=step.condition,
        requirement=step.requirement,
        quantity=_to_quantity_response(step.quantity),
    )


def _display_step_token(raw_token: str, suffix_note: str | None) -> str:
    suffix = suffix_note.strip() if suffix_note else ""
    return f"{raw_token}{suffix}" if suffix else raw_token


def _to_quantity_response(
    quantity: ConfirmedMatrixTestRecordStepQuantity | None,
) -> ConfirmedMatrixTestRecordStepQuantityResponse | None:
    if quantity is None:
        return None
    return ConfirmedMatrixTestRecordStepQuantityResponse(
        test_points_per_sample=quantity.test_points_per_sample,
        readings_per_point=quantity.readings_per_point,
        contact_points_per_sample=quantity.contact_points_per_sample,
        total_readings=quantity.total_readings,
        status=quantity.status,
        source=quantity.source,
        review_reason=quantity.review_reason,
    )
