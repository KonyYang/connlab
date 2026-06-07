"""API route for completing the New Project single-page workflow."""

from __future__ import annotations

import getpass
import logging
import traceback
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from backend.api.dependencies import (
    get_lookup_option_service,
    get_new_project_completion_service,
)
from backend.application.intake_confirmation_service import (
    IntakeConfirmationError,
    IntakeConfirmationNotFoundError,
)
from backend.application.ltr_authority import LtrAuthorityCommitError
from backend.application.ltr_registration_preview_service import LtrPreviewError
from backend.application.ltr_readiness_service import LtrReadinessError
from backend.application.ltr_service import DuplicateActiveLtrError, LtrError
from backend.application.new_project_completion_service import (
    CompleteNewProjectCommand,
    NewProjectCompletionError,
    NewProjectCompletionNotFoundError,
    NewProjectCompletionResult,
    NewProjectCompletionService,
    NewProjectLtrMode,
)
from backend.application.lookup_options_service import LookupOptionService
from backend.domain.lookup_options import LookupOption
from backend.application.project_lifecycle_service import (
    ProjectLifecycleError,
    ProjectLifecycleNotFoundError,
)


router = APIRouter(tags=["new-project"])
logger = logging.getLogger(__name__)


class CompleteNewProjectRequest(BaseModel):
    """Request body for completing New Project creation."""

    ltr_mode: NewProjectLtrMode
    specified_ltr_number: str | None = None
    operator_confirmed: bool = True
    plan_date: date | None = None
    test_item: str | None = None
    sample_description: str | None = None
    location: str | None = None
    test_type_in_sheet: str | None = None
    project_leader: str | None = None
    lab_performing_tests: str | None = None


class NewProjectCompletionOptionsResponse(BaseModel):
    """Options and defaults for New Project setup confirmation."""

    location_options: list[str]
    test_type_in_sheet_options: list[str]
    default_project_leader: str


class CompleteNewProjectResponse(BaseModel):
    """Response after New Project business completion."""

    project_id: str
    project_status: str
    ltr_number: str
    workbook_path: str | None = None
    workbook_sheet_name: str | None = None
    workbook_row_number: int | None = None
    workbook_backup_path: str | None = None


@router.get(
    "/api/new-project/completion-options",
    response_model=NewProjectCompletionOptionsResponse,
)
def get_new_project_completion_options(
    service: LookupOptionService = Depends(get_lookup_option_service),
) -> NewProjectCompletionOptionsResponse:
    """Return setup confirmation options for New Project completion."""
    groups = service.project_setup_options()
    return NewProjectCompletionOptionsResponse(
        location_options=_option_values(groups["project_setup_location"]),
        test_type_in_sheet_options=_option_values(groups["project_setup_test_type_in_sheet"]),
        default_project_leader=getpass.getuser(),
    )


@router.post(
    "/api/intake-cases/{case_id}/complete-new-project",
    response_model=CompleteNewProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def complete_new_project(
    case_id: str,
    request: CompleteNewProjectRequest,
    service: NewProjectCompletionService = Depends(get_new_project_completion_service),
) -> CompleteNewProjectResponse:
    """Confirm New Project data and apply an LTR before workspace handoff."""
    try:
        return _to_response(
            service.complete(
                CompleteNewProjectCommand(
                    case_id=case_id,
                    ltr_mode=request.ltr_mode,
                    specified_ltr_number=request.specified_ltr_number,
                    operator_confirmed=request.operator_confirmed,
                    plan_date=request.plan_date,
                    test_item=request.test_item,
                    sample_description=request.sample_description,
                    location=request.location,
                    test_type_in_sheet=request.test_type_in_sheet,
                    project_leader=request.project_leader,
                    lab_performing_tests=request.lab_performing_tests,
                )
            )
        )
    except (
        IntakeConfirmationNotFoundError,
        NewProjectCompletionNotFoundError,
        ProjectLifecycleNotFoundError,
    ) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DuplicateActiveLtrError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail="LTR number already exists in local records. Refresh and retry with the next available number.",
        ) from exc
    except (
        IntakeConfirmationError,
        LtrAuthorityCommitError,
        LtrPreviewError,
        LtrReadinessError,
        LtrError,
        NewProjectCompletionError,
        ProjectLifecycleError,
        ValueError,
        FileNotFoundError,
    ) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected New Project LTR completion failure for case_id=%s", case_id)
        _write_unexpected_error_log(case_id, exc)
        raise HTTPException(
            status_code=500,
            detail=_unexpected_error_detail(exc),
        ) from exc


def _to_response(result: NewProjectCompletionResult) -> CompleteNewProjectResponse:
    """Convert completion result to API response."""
    return CompleteNewProjectResponse(
        project_id=result.project.project_id,
        project_status=result.project.status.value,
        ltr_number=result.ltr.ltr_number,
        workbook_path=result.workbook_path,
        workbook_sheet_name=result.workbook_sheet_name,
        workbook_row_number=result.workbook_row_number,
        workbook_backup_path=result.workbook_backup_path,
    )


def _option_values(options: tuple[LookupOption, ...]) -> list[str]:
    """Return option values for New Project setup dropdowns."""
    return [option.value for option in options]


def _unexpected_error_detail(exc: Exception) -> str:
    """Return a compact diagnostic message for local operator troubleshooting."""
    text = str(exc).strip() or exc.__class__.__name__
    return f"Unexpected LTR application failure: {exc.__class__.__name__}: {text[:500]}"


def _write_unexpected_error_log(case_id: str, exc: Exception) -> None:
    """Write local troubleshooting details when the hidden backend has no console."""
    try:
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        with (log_dir / "new_project_ltr_errors.log").open("a", encoding="utf-8") as handle:
            handle.write(f"\ncase_id={case_id}\n")
            handle.write(f"error={exc.__class__.__name__}: {exc}\n")
            handle.write(traceback.format_exc())
            handle.write("\n")
    except Exception:
        logger.exception("Failed to write New Project LTR diagnostic log.")
