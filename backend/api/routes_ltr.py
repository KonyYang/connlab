"""LTR API routes."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.application.ltr_local_commit_service import (
    CommitLocalLtrCommand,
    LtrLocalCommitError,
    LtrLocalCommitResult,
    LtrLocalCommitService,
)
from backend.application.ltr_renumber_preview_service import (
    LtrRenumberPreview,
    LtrRenumberPreviewError,
    LtrRenumberPreviewNotFoundError,
    LtrRenumberPreviewService,
    PreviewLtrRenumberCommand,
    RenameImpact,
)
from backend.application.ltr_registration_preview_service import (
    LtrPreviewError,
    LtrPreviewMode,
    LtrRegistrationPreview,
    LtrRegistrationPreviewService,
    LtrRegistrationType,
    PreviewLtrRegistrationCommand,
)
from backend.application.ltr_readiness_service import (
    LtrReadinessError,
    LtrReadinessField,
    LtrReadinessNotFoundError,
    LtrReadinessResult,
    LtrReadinessService,
)
from backend.application.ltr_service import (
    DuplicateActiveLtrError,
    LtrError,
    LtrNotFoundError,
    LtrService,
    RegisterLtrCommand,
)
from backend.application.project_lifecycle_service import (
    ProjectLifecycleError,
    ProjectLifecycleNotFoundError,
)
from backend.api.dependencies import (
    get_ltr_local_commit_service,
    get_ltr_readiness_service,
    get_ltr_renumber_preview_service,
    get_ltr_registration_preview_service,
    get_ltr_service,
)
from backend.domain import LtrRecord


router = APIRouter(tags=["ltr"])


class LtrRegisterRequest(BaseModel):
    """Request body for LTR registration."""

    ltr_number: str = Field(min_length=1)
    requested_by: str | None = None
    requested_date: date | None = None
    notes: str | None = None


class LtrRecordResponse(BaseModel):
    """LTR record API response."""

    ltr_id: str
    project_id: str
    ltr_number: str
    status: str
    registered_on: date | None = None
    requested_by: str | None = None
    requested_date: date | None = None
    notes: str | None = None


class LtrReadinessFieldResponse(BaseModel):
    """Readiness state for one LTR field."""

    key: str
    label: str
    value: str | None = None
    source: str | None = None
    severity: str
    state: str
    operator_action: str
    placeholder_policy: str | None = None


class LtrReadinessResponse(BaseModel):
    """LTR readiness API response."""

    project_id: str
    status: str
    fields: list[LtrReadinessFieldResponse]
    blockers: list[LtrReadinessFieldResponse]
    warnings: list[LtrReadinessFieldResponse]


class LtrRegistrationPreviewResponse(BaseModel):
    """LTR registration preview API response."""

    project_id: str
    status: str
    proposed_ltr_number: str | None = None
    registration_type: str
    mode: str
    target_write_year_sheet: str
    number_preflight_required: bool
    number_preview_allowed: bool
    final_number_reserved: bool
    target_sheet: str | None = None
    target_row: int | None = None
    snapshot_fingerprint: str | None = None
    source_numbers: list[str]
    readiness: LtrReadinessResponse
    conflicts: list[str]
    warnings: list[str]
    parsed_base_number: str | None = None
    base_year_sheet: str | None = None
    family_numbers: list[str]


class LtrLocalCommitRequest(BaseModel):
    """Request body for local-only LTR commit."""

    year: int = Field(ge=2000, le=9999)
    month: int = Field(ge=1, le=12)
    operator_confirmed: bool
    registration_type: LtrRegistrationType = LtrRegistrationType.NORMAL
    mode: LtrPreviewMode = LtrPreviewMode.LOCAL_ONLY
    proposed_ltr_number: str | None = None
    requested_by: str | None = None
    requested_date: date | None = None
    operator_note: str | None = None


class LtrLocalCommitResponse(BaseModel):
    """Local-only LTR commit API response."""

    ltr: LtrRecordResponse
    preview: LtrRegistrationPreviewResponse


class LtrRenumberPreviewRequest(BaseModel):
    """Request body for LTR renumber preview."""

    old_ltr_number: str = Field(min_length=1)
    new_ltr_number: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    operator_confirmed: bool = False


class RenameImpactResponse(BaseModel):
    """One projected rename impact response."""

    record_type: str
    record_id: str
    current_path: str
    target_path: str
    target_exists: bool
    rename_required: bool


class LtrRenumberPreviewResponse(BaseModel):
    """LTR renumber preview API response."""

    project_id: str
    old_ltr_number: str
    new_ltr_number: str
    reason: str
    operator_confirmation_required: bool
    operator_confirmed: bool
    ltr_record_id: str
    impacts: list[RenameImpactResponse]
    conflicts: list[str]
    warnings: list[str]
    audit_summary: str


@router.post(
    "/api/projects/{project_id}/ltr",
    response_model=LtrRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_ltr(
    project_id: str,
    request: LtrRegisterRequest,
    service: LtrService = Depends(get_ltr_service),
) -> LtrRecordResponse:
    """Register an LTR for a project."""
    try:
        return _to_response(
            service.register_ltr(
                project_id,
                RegisterLtrCommand(
                    ltr_number=request.ltr_number,
                    requested_by=request.requested_by,
                    requested_date=request.requested_date,
                    notes=request.notes,
                ),
            )
        )
    except (LtrNotFoundError, ProjectLifecycleNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DuplicateActiveLtrError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except (LtrError, ProjectLifecycleError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/projects/{project_id}/ltr", response_model=list[LtrRecordResponse])
def list_project_ltrs(
    project_id: str,
    service: LtrService = Depends(get_ltr_service),
) -> list[LtrRecordResponse]:
    """Return LTR records for a project."""
    try:
        return [_to_response(ltr) for ltr in service.list_project_ltrs(project_id)]
    except LtrNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/api/projects/{project_id}/ltr/readiness",
    response_model=LtrReadinessResponse,
)
def get_ltr_readiness(
    project_id: str,
    proposed_ltr_number: str | None = Query(default=None),
    service: LtrReadinessService = Depends(get_ltr_readiness_service),
) -> LtrReadinessResponse:
    """Return LTR readiness for a project."""
    try:
        return _readiness_to_response(
            service.evaluate_project(project_id, proposed_ltr_number)
        )
    except LtrReadinessNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except LtrReadinessError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get(
    "/api/projects/{project_id}/ltr/preview",
    response_model=LtrRegistrationPreviewResponse,
)
def preview_ltr_registration(
    project_id: str,
    year: int = Query(ge=2000, le=9999),
    month: int = Query(ge=1, le=12),
    registration_type: LtrRegistrationType = Query(default=LtrRegistrationType.NORMAL),
    mode: LtrPreviewMode = Query(default=LtrPreviewMode.LOCAL_ONLY),
    proposed_ltr_number: str | None = Query(default=None),
    service: LtrRegistrationPreviewService = Depends(
        get_ltr_registration_preview_service
    ),
) -> LtrRegistrationPreviewResponse:
    """Return a no-write LTR registration preview."""
    try:
        return _preview_to_response(
            service.preview_project(
                project_id,
                PreviewLtrRegistrationCommand(
                    year=year,
                    month=month,
                    registration_type=registration_type,
                    mode=mode,
                    proposed_ltr_number=proposed_ltr_number,
                ),
            )
        )
    except (LtrReadinessNotFoundError, ProjectLifecycleNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (LtrPreviewError, LtrReadinessError, ProjectLifecycleError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/api/projects/{project_id}/ltr/commit",
    response_model=LtrLocalCommitResponse,
    status_code=status.HTTP_201_CREATED,
)
def commit_ltr_locally(
    project_id: str,
    request: LtrLocalCommitRequest,
    service: LtrLocalCommitService = Depends(get_ltr_local_commit_service),
) -> LtrLocalCommitResponse:
    """Commit an approved LTR preview to local ConnLab records only."""
    try:
        return _local_commit_to_response(
            service.commit_project(
                project_id,
                CommitLocalLtrCommand(
                    year=request.year,
                    month=request.month,
                    operator_confirmed=request.operator_confirmed,
                    registration_type=request.registration_type,
                    mode=request.mode,
                    proposed_ltr_number=request.proposed_ltr_number,
                    requested_by=request.requested_by,
                    requested_date=request.requested_date,
                    operator_note=request.operator_note,
                ),
            )
        )
    except (LtrReadinessNotFoundError, ProjectLifecycleNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DuplicateActiveLtrError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except (
        LtrLocalCommitError,
        LtrPreviewError,
        LtrReadinessError,
        ProjectLifecycleError,
    ) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/api/projects/{project_id}/ltr/renumber-preview",
    response_model=LtrRenumberPreviewResponse,
)
def preview_ltr_renumber(
    project_id: str,
    request: LtrRenumberPreviewRequest,
    service: LtrRenumberPreviewService = Depends(get_ltr_renumber_preview_service),
) -> LtrRenumberPreviewResponse:
    """Preview LTR renumber and path rename impacts without mutation."""
    try:
        return _renumber_preview_to_response(
            service.preview_project(
                project_id,
                PreviewLtrRenumberCommand(
                    old_ltr_number=request.old_ltr_number,
                    new_ltr_number=request.new_ltr_number,
                    reason=request.reason,
                    operator_confirmed=request.operator_confirmed,
                ),
            )
        )
    except LtrRenumberPreviewNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except LtrRenumberPreviewError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/ltr-records", response_model=list[LtrRecordResponse])
def search_ltr_records(
    query: str = Query(default=""),
    service: LtrService = Depends(get_ltr_service),
) -> list[LtrRecordResponse]:
    """Search LTR records by query string."""
    return [_to_response(ltr) for ltr in service.search_ltrs(query)]


def _renumber_preview_to_response(
    preview: LtrRenumberPreview,
) -> LtrRenumberPreviewResponse:
    """Convert renumber preview to API response."""
    return LtrRenumberPreviewResponse(
        project_id=preview.project_id,
        old_ltr_number=preview.old_ltr_number,
        new_ltr_number=preview.new_ltr_number,
        reason=preview.reason,
        operator_confirmation_required=preview.operator_confirmation_required,
        operator_confirmed=preview.operator_confirmed,
        ltr_record_id=preview.ltr_record_id,
        impacts=[_rename_impact_to_response(impact) for impact in preview.impacts],
        conflicts=list(preview.conflicts),
        warnings=list(preview.warnings),
        audit_summary=preview.audit_summary,
    )


def _rename_impact_to_response(impact: RenameImpact) -> RenameImpactResponse:
    """Convert one rename impact to API response."""
    return RenameImpactResponse(
        record_type=impact.record_type,
        record_id=impact.record_id,
        current_path=str(impact.current_path),
        target_path=str(impact.target_path),
        target_exists=impact.target_exists,
        rename_required=impact.rename_required,
    )


def _local_commit_to_response(
    result: LtrLocalCommitResult,
) -> LtrLocalCommitResponse:
    """Convert local commit result to API response."""
    return LtrLocalCommitResponse(
        ltr=_to_response(result.ltr),
        preview=_preview_to_response(result.preview),
    )


def _preview_to_response(
    preview: LtrRegistrationPreview,
) -> LtrRegistrationPreviewResponse:
    """Convert preview result to API response."""
    return LtrRegistrationPreviewResponse(
        project_id=preview.project_id,
        status=preview.status,
        proposed_ltr_number=preview.proposed_ltr_number,
        registration_type=preview.registration_type.value,
        mode=preview.mode.value,
        target_write_year_sheet=preview.target_write_year_sheet,
        number_preflight_required=preview.number_preflight_required,
        number_preview_allowed=preview.number_preview_allowed,
        final_number_reserved=preview.final_number_reserved,
        target_sheet=preview.target_sheet,
        target_row=preview.target_row,
        snapshot_fingerprint=preview.snapshot_fingerprint,
        source_numbers=list(preview.source_numbers),
        readiness=_readiness_to_response(preview.readiness),
        conflicts=list(preview.conflicts),
        warnings=list(preview.warnings),
        parsed_base_number=preview.parsed_base_number,
        base_year_sheet=preview.base_year_sheet,
        family_numbers=list(preview.family_numbers),
    )


def _readiness_to_response(result: LtrReadinessResult) -> LtrReadinessResponse:
    """Convert readiness result to API response."""
    return LtrReadinessResponse(
        project_id=result.project_id,
        status=result.status,
        fields=[_readiness_field_to_response(field) for field in result.fields],
        blockers=[_readiness_field_to_response(field) for field in result.blockers],
        warnings=[_readiness_field_to_response(field) for field in result.warnings],
    )


def _readiness_field_to_response(
    field: LtrReadinessField,
) -> LtrReadinessFieldResponse:
    """Convert one readiness field to API response."""
    return LtrReadinessFieldResponse(
        key=field.key,
        label=field.label,
        value=field.value,
        source=field.source,
        severity=field.severity.value,
        state=field.state,
        operator_action=field.operator_action,
        placeholder_policy=field.placeholder_policy,
    )


def _to_response(ltr: LtrRecord) -> LtrRecordResponse:
    """Convert an LTR domain record to API response."""
    return LtrRecordResponse(
        ltr_id=ltr.ltr_id,
        project_id=ltr.project_id,
        ltr_number=ltr.ltr_number,
        status=ltr.status.value,
        registered_on=ltr.registered_on,
        requested_by=ltr.requested_by,
        requested_date=ltr.requested_date,
        notes=ltr.notes,
    )
