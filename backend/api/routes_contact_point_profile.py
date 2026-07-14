"""Typed project Point Profile API boundary."""

from __future__ import annotations

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


class PointProfileRevisionResponse(BaseModel):
    revision_id: str
    revision_sequence: int
    state: str
    fingerprint: str
    created_at: str
    confirmed_at: str | None = None
    categories: list[PointProfileCategoryResponse] = Field(default_factory=list)
    points_per_sample: int


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
def save_draft(project_id: str, request: PointProfileCommandRequest, service=Depends(get_contact_point_profile_lifecycle_service)):
    try:
        result = service.save_draft(
            project_id, request.expected_revision_id, request.expected_revision_fingerprint,
            [item.model_dump() for item in request.categories], request.actor,
        )
    except (ContactPointProfileLifecycleError, ValueError) as exc:
        _raise_command_error(exc)
    return _command_response(result, "draft")


@router.post("/confirm", response_model=PointProfileRevisionResponse)
def confirm(project_id: str, request: PointProfileCommandRequest, service=Depends(get_contact_point_profile_lifecycle_service)):
    if request.expected_revision_id is None or request.expected_revision_fingerprint is None:
        raise HTTPException(422, detail={"code": "contact_point_profile_validation", "message": "Editable revision and fingerprint are required."})
    try:
        result = service.confirm(
            project_id, request.expected_revision_id, request.expected_revision_fingerprint,
            [item.model_dump() for item in request.categories], request.actor,
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
    }


def _raise_command_error(exc: ValueError) -> None:
    message = str(exc)
    if "stale" in message.lower():
        raise HTTPException(409, detail={"code": "contact_point_profile_stale", "message": message}) from exc
    raise HTTPException(422, detail={"code": "contact_point_profile_validation", "message": message}) from exc
