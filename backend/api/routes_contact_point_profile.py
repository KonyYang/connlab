"""Typed project Point Profile API boundary."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import (
    get_contact_point_profile_lifecycle_service,
    get_contact_point_profile_read_service,
)
from backend.application.contact_point_profile_lifecycle_service import (
    ContactPointProfileLifecycleError,
)


router = APIRouter(prefix="/api/projects/{project_id}/contact-point-profile", tags=["contact-point-profile"])


class PointProfileCategoryInput(BaseModel):
    category_id: str | None = Field(default=None, max_length=64)
    label: str = Field(min_length=1, max_length=255)
    count_per_sample: int = Field(ge=0)
    record_prefix: str = Field(default="", max_length=64)
    included: bool = True


class PointProfileCommandRequest(BaseModel):
    actor: str = Field(min_length=1, max_length=255)
    expected_revision_id: str | None = Field(default=None, max_length=64)
    expected_revision_fingerprint: str | None = Field(default=None, max_length=128)
    categories: list[PointProfileCategoryInput] = Field(default_factory=list)


class PointProfileCategoryResponse(BaseModel):
    category_id: str
    category_ordinal: int
    label: str
    count_per_sample: int
    record_prefix: str
    included: bool
    point_expression: str | None = None
    expression_status: str = "legacy_count_only"
    legacy_contiguous_suggestion: str | None = None


class PointProfileDirectCategoryInput(BaseModel):
    category_id: str | None = Field(default=None, max_length=64)
    prefix: str = Field(min_length=1, max_length=64)
    point_expression: str = Field(min_length=1, max_length=1024)
    cr_selected: bool = False


class PointProfileDirectConfirmRequest(BaseModel):
    actor: str = Field(min_length=1, max_length=255)
    expected_confirmed_revision_id: str | None = Field(default=None, max_length=64)
    expected_confirmed_revision_fingerprint: str | None = Field(default=None, max_length=128)
    cr_coverage_mode: Literal["follow_llcr", "custom"] = "follow_llcr"
    categories: list[PointProfileDirectCategoryInput] = Field(default_factory=list, max_length=256)


class PointProfileCrCoverageResponse(BaseModel):
    mode: Literal["follow_llcr", "custom"]
    selected_category_ids: list[str] = Field(default_factory=list)
    points_per_sample: int


class PointProfileRevisionResponse(BaseModel):
    revision_id: str
    revision_sequence: int
    state: str
    fingerprint: str
    created_at: str
    confirmed_at: str | None = None
    categories: list[PointProfileCategoryResponse] = Field(default_factory=list)
    points_per_sample: int
    cr_coverage: PointProfileCrCoverageResponse


class PointProfileWorkspaceResponse(BaseModel):
    status: str
    project_id: str
    editable_revision: PointProfileRevisionResponse | None = None
    confirmed_revision: PointProfileRevisionResponse | None = None
    has_unconfirmed_draft: bool
    legacy_uniform_suggestion: list[PointProfileCategoryResponse] | None = None
    diagnostics: list[str] = Field(default_factory=list)


class PointProfileSummaryResponse(BaseModel):
    status: str
    project_id: str
    confirmed_revision: PointProfileRevisionResponse | None = None
    points_per_sample: int | None = None
    has_unconfirmed_draft: bool
    diagnostics: list[str] = Field(default_factory=list)


@router.get("/workspace", response_model=PointProfileWorkspaceResponse)
def get_workspace(project_id: str, service=Depends(get_contact_point_profile_read_service)):
    return service.get_workspace(project_id)


@router.get("/summary", response_model=PointProfileSummaryResponse)
def get_summary(project_id: str, service=Depends(get_contact_point_profile_read_service)):
    return service.get_summary(project_id)


@router.put("/draft", response_model=PointProfileRevisionResponse)
def save_draft(project_id: str, request: PointProfileCommandRequest):
    raise HTTPException(410, detail={"code": "contact_point_profile_draft_disabled", "message": "Point Profile drafts are no longer available."})


@router.post("/confirm", response_model=PointProfileRevisionResponse)
def confirm(project_id: str, request: PointProfileDirectConfirmRequest, service=Depends(get_contact_point_profile_lifecycle_service)):
    try:
        result = service.confirm_direct(
            project_id, request.expected_confirmed_revision_id, request.expected_confirmed_revision_fingerprint,
            [item.model_dump() for item in request.categories], request.actor,
            cr_coverage_mode=request.cr_coverage_mode,
        )
    except (ContactPointProfileLifecycleError, ValueError) as exc:
        _raise_command_error(exc)
    return _command_response(result, "confirmed")


def _command_response(result: dict[str, object], state: str) -> dict[str, object]:
    return {
        "revision_id": result["revision_id"], "revision_sequence": result.get("revision_sequence", 1),
        "state": state, "fingerprint": result["fingerprint"], "created_at": result.get("created_at", ""),
        "confirmed_at": result.get("confirmed_at"), "categories": result["categories"],
        "points_per_sample": result["points_per_sample"],
        "cr_coverage": result["cr_coverage"],
    }


def _raise_command_error(exc: ValueError) -> None:
    message = str(exc)
    if "stale" in message.lower():
        raise HTTPException(409, detail={"code": "contact_point_profile_stale", "message": message}) from exc
    raise HTTPException(422, detail={"code": "contact_point_profile_validation", "message": message}) from exc
