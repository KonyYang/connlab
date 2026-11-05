"""Formal registration for an existing no-LTR project."""

from datetime import date
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import get_temporary_project_registration_service
from backend.application.temporary_project_registration_service import TemporaryProjectRegistrationService

router = APIRouter(prefix='/api/projects/{project_id}/ltr-registration', tags=['ltr'])
logger = logging.getLogger(__name__)


class RegistrationPreviewRequest(BaseModel):
    values: dict[str, str]
    plan_date: date = Field(default_factory=date.today)
    mode: str = 'auto'
    specified_number: str | None = None
    intake_source_id: str | None = None


class RegistrationCommitRequest(BaseModel):
    preview_token: str = Field(min_length=1)
    operator_confirmed: bool


def _invoke(operation):
    try:
        return operation()
    except LookupError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception('Current-project LTR registration failed')
        raise HTTPException(500, detail=(
            'LTR registration could not be completed. Your project is retained. '
            'Check the workbook is available and writable, then retry this registration; '
            'any pending workbook write will be checked before continuing.'
        )) from exc


@router.get('')
def prepare_registration(project_id: str, service: TemporaryProjectRegistrationService = Depends(get_temporary_project_registration_service)):
    return _invoke(lambda: service.prepare(project_id))


@router.post('/preview')
def preview_registration(project_id: str, request: RegistrationPreviewRequest,
                         service: TemporaryProjectRegistrationService = Depends(get_temporary_project_registration_service)):
    return _invoke(lambda: service.preview(project_id, request.values, plan_date=request.plan_date,
        mode=request.mode, specified_number=request.specified_number, intake_source_id=request.intake_source_id))


@router.post('/commit')
def commit_registration(project_id: str, request: RegistrationCommitRequest,
                        service: TemporaryProjectRegistrationService = Depends(get_temporary_project_registration_service)):
    return _invoke(lambda: service.commit(project_id, request.preview_token, operator_confirmed=request.operator_confirmed))
