"""Customer Feedback Form generation API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict

from backend.api.dependencies import get_customer_feedback_form_generation_service
from backend.application.customer_feedback_form_generation_service import (
    CustomerFeedbackFormGenerationCommand,
    CustomerFeedbackFormGenerationResult,
    CustomerFeedbackFormGenerationService,
    CustomerFeedbackGenerationError,
    CustomerFeedbackProjectNotFoundError,
    CustomerFeedbackReadinessError,
)


router = APIRouter(
    prefix="/api/projects/{project_id}/customer-feedback",
    tags=["customer-feedback"],
)


class CustomerFeedbackFormGenerationRequest(BaseModel):
    """Request body for Customer Feedback Form generation."""

    model_config = ConfigDict(extra="forbid")

    operator: str | None = None


class CustomerFeedbackFormGenerationResponse(BaseModel):
    """Generated Customer Feedback Form metadata."""

    project_id: str
    template_path: str
    output_path: str
    output_file_name: str
    warnings: list[str]


@router.post("/generate", response_model=CustomerFeedbackFormGenerationResponse)
def generate_customer_feedback_form(
    project_id: str,
    request: CustomerFeedbackFormGenerationRequest | None = None,
    service: CustomerFeedbackFormGenerationService = Depends(
        get_customer_feedback_form_generation_service
    ),
) -> CustomerFeedbackFormGenerationResponse:
    """Generate a Customer Feedback Form workbook for a project."""
    request = request or CustomerFeedbackFormGenerationRequest()
    try:
        result = service.generate(
            CustomerFeedbackFormGenerationCommand(
                project_id=project_id,
                operator=request.operator,
            )
        )
    except CustomerFeedbackProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except CustomerFeedbackReadinessError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except CustomerFeedbackGenerationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return _to_response(result)


def _to_response(
    result: CustomerFeedbackFormGenerationResult,
) -> CustomerFeedbackFormGenerationResponse:
    return CustomerFeedbackFormGenerationResponse(
        project_id=result.project_id,
        template_path=str(result.template_path),
        output_path=str(result.output_path),
        output_file_name=result.output_file_name,
        warnings=list(result.warnings),
    )
