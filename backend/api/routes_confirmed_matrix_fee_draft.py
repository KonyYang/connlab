"""Confirmed-Matrix-backed Fee Evaluation draft read-only API route."""

from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import get_confirmed_matrix_fee_draft_service
from backend.application.confirmed_matrix_fee_draft_service import (
    BuildConfirmedMatrixFeeDraftCommand,
    ConfirmedMatrixFeeDraftError,
    ConfirmedMatrixFeeDraftNotFoundError,
    ConfirmedMatrixFeeDraftService,
    FeeEvaluationDraft,
    FeeEvaluationGroup,
    FeeEvaluationLineItem,
    FeeEvaluationWarning,
)


router = APIRouter(tags=["confirmed-matrix-fee-draft"])


class FeeEvaluationWarningResponse(BaseModel):
    code: str
    message: str
    scope: str


class FeeEvaluationLineItemResponse(BaseModel):
    line_id: str
    status: str
    review_required: bool
    review_reason: str | None
    confirmed_matrix_id: str
    confirmed_revision: int
    group_key: str
    group_label: str
    confirmed_group_id: str
    sample_quantity_expression: str
    confirmed_row_id: str
    source_row_id: str | None
    row_order: int
    test_item: str
    section: str
    method: str
    condition: str
    requirement: str
    step_tokens: list[str]
    matched_rule_id: str | None
    matched_rule_version_id: str | None
    matched_rule_name: str | None
    match_reason: str
    calculation_strategy: str | None
    unit_label: str
    unit_price: str | None
    units: str | None
    base_fee: str | None
    discount_percent: str | None
    testing_fee: str | None
    warnings: list[FeeEvaluationWarningResponse]


class FeeEvaluationGroupResponse(BaseModel):
    group_key: str
    group_label: str
    sample_quantity_expression: str
    line_items: list[FeeEvaluationLineItemResponse]


class FeeEvaluationHeaderResponse(BaseModel):
    project_id: str
    confirmed_matrix_id: str
    confirmed_revision: int
    pricing_rule_version_id: str
    pricing_source_file_name: str
    pricing_source_hash: str
    pricing_effective_from: str | None
    generated_at: str


class FeeEvaluationDraftResponse(BaseModel):
    header: FeeEvaluationHeaderResponse
    draft_status: str
    total_fee: str | None
    review_required_count: int
    groups: list[FeeEvaluationGroupResponse]
    warnings: list[FeeEvaluationWarningResponse]


@router.get(
    "/api/projects/{project_id}/confirmed-matrix/fee-draft",
    response_model=FeeEvaluationDraftResponse,
)
def get_confirmed_matrix_fee_draft(
    project_id: str,
    service: ConfirmedMatrixFeeDraftService = Depends(get_confirmed_matrix_fee_draft_service),
) -> FeeEvaluationDraftResponse:
    """Return Fee Evaluation draft rows derived from active confirmed Matrix authority."""
    try:
        draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id=project_id))
    except ConfirmedMatrixFeeDraftNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ConfirmedMatrixFeeDraftError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _to_response(draft)


def _to_response(draft: FeeEvaluationDraft) -> FeeEvaluationDraftResponse:
    return FeeEvaluationDraftResponse(
        header=FeeEvaluationHeaderResponse(
            project_id=draft.header.project_id,
            confirmed_matrix_id=draft.header.confirmed_matrix_id,
            confirmed_revision=draft.header.confirmed_revision,
            pricing_rule_version_id=draft.header.pricing_rule_version_id,
            pricing_source_file_name=draft.header.pricing_source_file_name,
            pricing_source_hash=draft.header.pricing_source_hash,
            pricing_effective_from=draft.header.pricing_effective_from,
            generated_at=draft.header.generated_at,
        ),
        draft_status=draft.draft_status,
        total_fee=_decimal_or_none(draft.total_fee),
        review_required_count=draft.review_required_count,
        groups=[_to_group_response(group) for group in draft.groups],
        warnings=[_to_warning_response(warning) for warning in draft.warnings],
    )


def _to_group_response(group: FeeEvaluationGroup) -> FeeEvaluationGroupResponse:
    return FeeEvaluationGroupResponse(
        group_key=group.group_key,
        group_label=group.group_label,
        sample_quantity_expression=group.sample_quantity_expression,
        line_items=[_to_line_response(line) for line in group.line_items],
    )


def _to_line_response(line: FeeEvaluationLineItem) -> FeeEvaluationLineItemResponse:
    return FeeEvaluationLineItemResponse(
        line_id=line.line_id,
        status=line.status,
        review_required=line.review_required,
        review_reason=line.review_reason,
        confirmed_matrix_id=line.confirmed_matrix_id,
        confirmed_revision=line.confirmed_revision,
        group_key=line.group_key,
        group_label=line.group_label,
        confirmed_group_id=line.confirmed_group_id,
        sample_quantity_expression=line.sample_quantity_expression,
        confirmed_row_id=line.confirmed_row_id,
        source_row_id=line.source_row_id,
        row_order=line.row_order,
        test_item=line.test_item,
        section=line.section,
        method=line.method,
        condition=line.condition,
        requirement=line.requirement,
        step_tokens=list(line.step_tokens),
        matched_rule_id=line.matched_rule_id,
        matched_rule_version_id=line.matched_rule_version_id,
        matched_rule_name=line.matched_rule_name,
        match_reason=line.match_reason,
        calculation_strategy=line.calculation_strategy,
        unit_label=line.unit_label,
        unit_price=_decimal_or_none(line.unit_price),
        units=_decimal_or_none(line.units),
        base_fee=_decimal_or_none(line.base_fee),
        discount_percent=_decimal_or_none(line.discount_percent),
        testing_fee=_decimal_or_none(line.testing_fee),
        warnings=[_to_warning_response(warning) for warning in line.warnings],
    )


def _to_warning_response(warning: FeeEvaluationWarning) -> FeeEvaluationWarningResponse:
    return FeeEvaluationWarningResponse(
        code=warning.code,
        message=warning.message,
        scope=warning.scope,
    )


def _decimal_or_none(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return format(value, "f")
