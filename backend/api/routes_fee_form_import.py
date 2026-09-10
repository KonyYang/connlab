"""Inspection only: importing a workbook does not save or confirm Fee authority."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session, ProjectRepository
from backend.infrastructure.office.fee_form_import_gateway import read_fee_form, MAX_FILE_BYTES

router = APIRouter(prefix="/api/projects/{project_id}/fee-evaluation", tags=["Fee Evaluation"])


@router.post("/import/inspect")
def inspect_fee_form(project_id: str, file: UploadFile, session: Session = Depends(get_session)):
    if ProjectRepository(session).get(project_id) is None:
        raise HTTPException(404, "Project not found.")
    try:
        data = file.file.read(MAX_FILE_BYTES + 1)
        return read_fee_form(data, file.filename or "")
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    finally:
        file.file.close()
