"""Typed API boundary for independent contact-measurement plan authority."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import (
    get_contact_measurement_plan_lifecycle_service,
    get_contact_measurement_plan_projection_service,
)
from backend.application.contact_measurement_plan_lifecycle_service import (
    ContactMeasurementPlanLifecycleError,
    ContactMeasurementPlanLifecycleService,
)
from backend.application.contact_measurement_plan_projection_service import (
    ContactMeasurementPlanProjectionService,
)

router = APIRouter(
    prefix="/api/projects/{project_id}/contact-measurement-plan",
    tags=["contact-measurement-plan"],
)


class ContactMeasurementPlanFamilyResponse(BaseModel):
    family_id: str
    family_ordinal: int
    label: str
    count_per_sample: int
    record_label: str
    record_prefix: str
    included: bool
    is_custom: bool


class ContactMeasurementPlanTargetResponse(BaseModel):
    stable_target_key: str
    contact_kind: str
    included: bool
    readings_per_sample: int
    families: list[ContactMeasurementPlanFamilyResponse]


class EffectiveContactMeasurementPlanProjectionResponse(BaseModel):
    status: str
    project_id: str
    revision_id: str | None = None
    revision_sequence: int | None = None
    targets: list[ContactMeasurementPlanTargetResponse]
    diagnostics: list[str] = Field(default_factory=list)


class ContactMeasurementPlanWorkspaceResponse(BaseModel):
    status: str
    project_id: str
    active_confirmed_revision_id: str | None = None
    editable_revision_id: str | None = None
    editable_revision_state: str | None = None
    editable_revision_fingerprint: str | None = None
    targets: list[ContactMeasurementPlanTargetResponse] = Field(default_factory=list)


class ContactMeasurementPlanSummaryResponse(BaseModel):
    status: str
    project_id: str
    revision_id: str | None = None
    revision_sequence: int | None = None
    diagnostics: list[str] = Field(default_factory=list)


class ContactMeasurementPlanActorRequest(BaseModel):
    actor: str = Field(min_length=1, max_length=255)
    expected_revision_fingerprint: str | None = None


class ContactMeasurementPlanRevisionResponse(BaseModel):
    status: str
    revision_id: str


class ContactMeasurementPlanImpactRefreshRequest(BaseModel):
    actor: str = Field(min_length=1, max_length=255)
    expected_matrix_binding_fingerprint: str = Field(min_length=1)


class ContactMeasurementPlanTargetPatchRequest(BaseModel):
    actor: str = Field(min_length=1, max_length=255)
    expected_revision_fingerprint: str = Field(min_length=1)
    stable_target_key: str = Field(min_length=1)
    included: bool
    exclusion_reason: str | None = None
    families: list["ContactMeasurementPlanFamilyInput"] | None = None


class ContactMeasurementPlanFamilyInput(BaseModel):
    family_id: str = Field(min_length=1, max_length=64)
    label: str = Field(min_length=1, max_length=255)
    count_per_sample: int = Field(ge=0)
    record_label: str = Field(min_length=1, max_length=255)
    record_prefix: str = Field(min_length=1, max_length=64)
    included: bool
    is_custom: bool


class ContactMeasurementPlanTargetRebindRequest(BaseModel):
    actor: str = Field(min_length=1, max_length=255)
    expected_revision_fingerprint: str = Field(min_length=1)
    stable_target_key: str = Field(min_length=1)
    candidate_subject_key: str = Field(min_length=1)


@router.get("/summary", response_model=ContactMeasurementPlanSummaryResponse)
def get_summary(
    project_id: str,
    service: ContactMeasurementPlanProjectionService = Depends(
        get_contact_measurement_plan_projection_service
    ),
) -> ContactMeasurementPlanSummaryResponse:
    """Return a small read-only authority status summary."""
    result = service.get_effective(project_id)
    return ContactMeasurementPlanSummaryResponse(
        status=result.status,
        project_id=result.project_id,
        revision_id=result.revision_id,
        revision_sequence=result.revision_sequence,
        diagnostics=list(result.diagnostics),
    )


@router.get("/workspace", response_model=ContactMeasurementPlanWorkspaceResponse)
def get_workspace(
    project_id: str,
    service: ContactMeasurementPlanProjectionService = Depends(
        get_contact_measurement_plan_projection_service
    ),
) -> ContactMeasurementPlanWorkspaceResponse:
    """Read the draft or confirmed authority workspace without mutating Matrix."""
    return ContactMeasurementPlanWorkspaceResponse(**service.get_workspace(project_id))


@router.get(
    "/effective-projection",
    response_model=EffectiveContactMeasurementPlanProjectionResponse,
)
def get_effective_projection(
    project_id: str,
    service: ContactMeasurementPlanProjectionService = Depends(
        get_contact_measurement_plan_projection_service
    ),
) -> EffectiveContactMeasurementPlanProjectionResponse:
    """Expose only compatible confirmed authority, never an editable draft."""
    result = service.get_effective(project_id)
    return EffectiveContactMeasurementPlanProjectionResponse(**asdict(result))


@router.post("/revisions", response_model=ContactMeasurementPlanRevisionResponse)
def open_revision(
    project_id: str,
    request: ContactMeasurementPlanActorRequest,
    service: ContactMeasurementPlanLifecycleService = Depends(
        get_contact_measurement_plan_lifecycle_service
    ),
) -> ContactMeasurementPlanRevisionResponse:
    """Open one idempotent editable authority revision."""
    try:
        revision_id = service.open_draft(project_id, request.actor)
    except ContactMeasurementPlanLifecycleError as exc:
        _raise_lifecycle_error(exc)
    return ContactMeasurementPlanRevisionResponse(status="draft", revision_id=revision_id)


@router.post(
    "/revisions/{revision_id}/confirm",
    response_model=ContactMeasurementPlanRevisionResponse,
)
def confirm_revision(
    project_id: str,
    revision_id: str,
    request: ContactMeasurementPlanActorRequest,
    service: ContactMeasurementPlanLifecycleService = Depends(
        get_contact_measurement_plan_lifecycle_service
    ),
) -> ContactMeasurementPlanRevisionResponse:
    """Promote an unchanged, current editable revision into confirmed authority."""
    if not request.expected_revision_fingerprint:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "expected_revision_fingerprint_required",
                "message": "expected_revision_fingerprint is required.",
            },
        )
    try:
        service.confirm(
            project_id,
            revision_id,
            request.expected_revision_fingerprint,
            request.actor,
        )
    except ContactMeasurementPlanLifecycleError as exc:
        _raise_lifecycle_error(exc)
    return ContactMeasurementPlanRevisionResponse(status="confirmed", revision_id=revision_id)


@router.put(
    "/revisions/{revision_id}",
    response_model=ContactMeasurementPlanRevisionResponse,
)
def save_revision(
    project_id: str,
    revision_id: str,
    request: ContactMeasurementPlanActorRequest,
    service: ContactMeasurementPlanLifecycleService = Depends(
        get_contact_measurement_plan_lifecycle_service
    ),
) -> ContactMeasurementPlanRevisionResponse:
    """Save an unchanged editable revision with its optimistic-lock token."""
    if not request.expected_revision_fingerprint:
        _raise_missing_revision_fingerprint()
    try:
        service.save_revision(
            project_id,
            revision_id,
            request.expected_revision_fingerprint,
            request.actor,
        )
    except ContactMeasurementPlanLifecycleError as exc:
        _raise_lifecycle_error(exc)
    return ContactMeasurementPlanRevisionResponse(status="saved", revision_id=revision_id)


@router.post(
    "/revisions/{revision_id}/impacts/refresh",
    response_model=ContactMeasurementPlanRevisionResponse,
)
def refresh_impacts(
    project_id: str,
    revision_id: str,
    request: ContactMeasurementPlanImpactRefreshRequest,
    service: ContactMeasurementPlanLifecycleService = Depends(
        get_contact_measurement_plan_lifecycle_service
    ),
) -> ContactMeasurementPlanRevisionResponse:
    """Refresh pure Matrix impact classification for one editable revision."""
    try:
        status = service.refresh_impacts(
            project_id,
            revision_id,
            request.expected_matrix_binding_fingerprint,
            request.actor,
        )
    except ContactMeasurementPlanLifecycleError as exc:
        _raise_lifecycle_error(exc)
    return ContactMeasurementPlanRevisionResponse(status=status, revision_id=revision_id)


@router.post(
    "/revisions/{revision_id}/suggestions/accept-compatible",
    response_model=ContactMeasurementPlanRevisionResponse,
)
def accept_compatible_suggestions(
    project_id: str,
    revision_id: str,
    request: ContactMeasurementPlanActorRequest,
    service: ContactMeasurementPlanLifecycleService = Depends(
        get_contact_measurement_plan_lifecycle_service
    ),
) -> ContactMeasurementPlanRevisionResponse:
    """Record explicit acceptance of only already-compatible suggestions."""
    if not request.expected_revision_fingerprint:
        _raise_missing_revision_fingerprint()
    try:
        service.accept_compatible_suggestions(
            project_id,
            revision_id,
            request.expected_revision_fingerprint,
            request.actor,
        )
    except ContactMeasurementPlanLifecycleError as exc:
        _raise_lifecycle_error(exc)
    return ContactMeasurementPlanRevisionResponse(status="accepted", revision_id=revision_id)


@router.patch(
    "/revisions/{revision_id}/targets",
    response_model=ContactMeasurementPlanRevisionResponse,
)
def patch_target(
    project_id: str,
    revision_id: str,
    request: ContactMeasurementPlanTargetPatchRequest,
    service: ContactMeasurementPlanLifecycleService = Depends(
        get_contact_measurement_plan_lifecycle_service
    ),
) -> ContactMeasurementPlanRevisionResponse:
    """Apply one explicit draft-only target inclusion decision."""
    try:
        service.set_target_inclusion(
            project_id,
            revision_id,
            request.stable_target_key,
            request.included,
            request.exclusion_reason,
            (
                tuple(family.model_dump() for family in request.families)
                if request.families is not None
                else None
            ),
            request.expected_revision_fingerprint,
            request.actor,
        )
    except ContactMeasurementPlanLifecycleError as exc:
        _raise_lifecycle_error(exc)
    return ContactMeasurementPlanRevisionResponse(status="updated", revision_id=revision_id)


@router.post(
    "/revisions/{revision_id}/targets/rebind",
    response_model=ContactMeasurementPlanRevisionResponse,
)
def rebind_target(
    project_id: str,
    revision_id: str,
    request: ContactMeasurementPlanTargetRebindRequest,
    service: ContactMeasurementPlanLifecycleService = Depends(
        get_contact_measurement_plan_lifecycle_service
    ),
) -> ContactMeasurementPlanRevisionResponse:
    """Rebind one explicit draft target to a current canonical Matrix target."""
    try:
        service.rebind_target(
            project_id,
            revision_id,
            request.stable_target_key,
            request.candidate_subject_key,
            request.expected_revision_fingerprint,
            request.actor,
        )
    except ContactMeasurementPlanLifecycleError as exc:
        _raise_lifecycle_error(exc)
    return ContactMeasurementPlanRevisionResponse(status="rebound", revision_id=revision_id)


def _raise_lifecycle_error(error: ContactMeasurementPlanLifecycleError) -> None:
    message = str(error)
    if message.startswith("authority_disabled:"):
        raise HTTPException(
            status_code=503,
            detail={
                "code": "contact_measurement_plan_authority_disabled",
                "message": message.split(": ", 1)[1],
            },
        ) from error
    status_code = 409 if "stale" in message or "not found" in message else 422
    raise HTTPException(
        status_code=status_code,
        detail={"code": "contact_measurement_plan_conflict", "message": message},
    ) from error


def _raise_missing_revision_fingerprint() -> None:
    raise HTTPException(
        status_code=422,
        detail={
            "code": "expected_revision_fingerprint_required",
            "message": "expected_revision_fingerprint is required.",
        },
    )
