"""Independent temperature-data tools; no project identity or filesystem paths in inputs."""

from dataclasses import asdict
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Response

from backend.api.dependencies import get_tools_temperature_service
from backend.api.temperature_schemas import (
    CurrentRequest, DeratingRequest, DownloadTemperatureRequest, PreparationRequest,
)
from backend.application.temperature_data_preparation import prepare_data
from backend.application.tools_temperature_service import DeratingParameters, ToolsTemperatureService
from backend.domain.temperature_rise import calculate_current, generate_derating

router = APIRouter(prefix='/api/tools/temperature-rise', tags=['tools'])


def _call(operation):
    try:
        return operation()
    except (ValueError, OverflowError) as exc:
        message = str(exc) if isinstance(exc, ValueError) else 'The entered values are too large. Check readings, units and coefficients.'
        raise HTTPException(status_code=422, detail=message) from exc


@router.post('/import')
def import_temperature_workbook(file: UploadFile = File(...), sheet_name: str | None = Form(None),
                                service: ToolsTemperatureService = Depends(get_tools_temperature_service)):
    content = file.file.read(25 * 1024 * 1024 + 1)
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(status_code=422, detail='Select a workbook smaller than 25 MB.')
    table, selection = _call(lambda: service.import_workbook(content, file.filename or 'Scanner.xlsx', sheet_name))
    return {'table': asdict(table), 'selection': asdict(selection)}


@router.post('/prepare')
def prepare_temperature_data(request: PreparationRequest):
    return _call(lambda: prepare_data(request.table.domain(), request.selection.domain(),
                                     acknowledge_warnings=request.acknowledge_warnings))


@router.post('/analyze')
def analyze_temperature_data(request: PreparationRequest,
                             service: ToolsTemperatureService = Depends(get_tools_temperature_service)):
    return _call(lambda: service.analyze(request.table.domain(), request.selection.domain(),
        acknowledge_warnings=request.acknowledge_warnings, zero_intercept=request.zero_intercept))


@router.post('/current')
def calculate_temperature_current(request: CurrentRequest):
    return {'current': _call(lambda: calculate_current(request.coefficients.domain(), request.target_rise))}


@router.post('/derating')
def generate_temperature_derating(request: DeratingRequest):
    return _call(lambda: generate_derating(request.coefficients.domain(), max_temperature=request.max_temperature,
                                          step=request.step, ambient_point=request.ambient_point))


@router.post('/download')
def download_temperature_workbook(request: DownloadTemperatureRequest,
                                  service: ToolsTemperatureService = Depends(get_tools_temperature_service)):
    name, content = _call(lambda: service.download(request.table.domain(), request.selection.domain(),
        acknowledge_warnings=request.acknowledge_warnings, zero_intercept=request.zero_intercept,
        maximum_coefficients=request.maximum_coefficients.domain() if request.maximum_coefficients else None,
        average_coefficients=request.average_coefficients.domain() if request.average_coefficients else None,
        target_rise=request.target_rise,
        derating_parameters=DeratingParameters(**request.derating.model_dump()) if request.derating else None))
    return Response(content, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    headers={'Content-Disposition': f"attachment; filename*=UTF-8''{quote(name)}"})
