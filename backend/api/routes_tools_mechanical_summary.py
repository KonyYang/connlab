"""Project-independent mechanical summary tools."""

from pathlib import PurePath
from hashlib import sha256
from io import BytesIO
import json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Response
from fastapi.encoders import jsonable_encoder
from openpyxl import Workbook

from backend.application.mechanical_summary import verify_reviewed_pdf
from backend.infrastructure.files.mechanical_summary_pdf import inspect_pdf
from backend.infrastructure.office.mechanical_summary_excel_copy import copy_instrument_workbooks, add_reviewed_results
from backend.infrastructure.office.mechanical_summary_workbook import inspect_workbook

router = APIRouter(prefix='/api/tools/mechanical-summary', tags=['tools'])


@router.post('/preview')
def preview(file: UploadFile = File(...), kind: str = Form(...)):
    content = file.file.read(25 * 1024 * 1024 + 1)
    if not content or len(content) > 25 * 1024 * 1024:
        raise HTTPException(status_code=422, detail='Select a nonempty file smaller than 25 MB.')
    name = file.filename or ''
    try:
        suffix = PurePath(name).suffix.lower()
        if suffix == '.pdf':
            result = inspect_pdf(content, kind)
        elif suffix in {'.xls', '.xlsx'}:
            result = inspect_workbook(content, name)
        else:
            raise ValueError('Select a PDF, XLS or XLSX file.')
        return jsonable_encoder({**result, 'sha256': sha256(content).hexdigest()})
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post('/generate')
def generate(files: list[UploadFile] = File(...), manifest: str = Form(...)):
    try:
        selections = json.loads(manifest)
        if not isinstance(selections, list) or len(selections) != len(files) or not 1 <= len(files) <= 20:
            raise ValueError('Review every selected source before generating.')
        workbook_sources = []
        sections = []
        sheet_offset = 0
        for file, selection in zip(files, selections):
            if not isinstance(selection, dict) or selection.get('confirmed') is not True:
                raise ValueError('Confirm each source before generating.')
            content = file.file.read(25 * 1024 * 1024 + 1)
            if not content or len(content) > 25 * 1024 * 1024:
                raise ValueError('Each source must be nonempty and smaller than 25 MB.')
            if sha256(content).hexdigest() != selection.get('sha256'):
                raise ValueError('A source changed since preview; review it again.')
            name = file.filename or ''
            suffix = PurePath(name).suffix.lower()
            kind = selection.get('kind')
            section = {'kind': kind, 'name': PurePath(name).stem, 'source': name,
                       'group': selection.get('group'), 'information': selection.get('information') or {},
                       'rows': selection.get('rows')}
            if suffix == '.pdf':
                original = inspect_pdf(content, kind)
                section['rows'] = verify_reviewed_pdf(original['rows'], section['rows'], kind)
                section['pdf_content'] = content
            elif suffix in {'.xls', '.xlsx'}:
                if kind != 'qualitative':
                    raise ValueError('Choose a qualitative test type for this workbook.')
                book = inspect_workbook(content, name)
                sheet = selection.get('sheet')
                if type(sheet) is not int or not 1 <= sheet <= len(book['sheets']):
                    raise ValueError('Select a valid worksheet for each workbook.')
                section['target_sheet_index'] = sheet_offset + sheet
                sheet_offset += len(book['sheets'])
                workbook_sources.append((name, content))
            else:
                raise ValueError('Select PDF, XLS or XLSX sources.')
            sections.append(section)
        if workbook_sources:
            copied = copy_instrument_workbooks(workbook_sources)
        else:
            book = Workbook()
            stream = BytesIO()
            book.save(stream)
            book.close()
            copied = stream.getvalue()
        output = add_reviewed_results(copied, sections, remove_placeholder=not workbook_sources)
        return Response(content=output, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        headers={'Content-Disposition': 'attachment; filename="Mechanical_Summary.xlsx"'})
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
