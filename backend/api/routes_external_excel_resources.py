"""Read-only API routes for external standard/equipment Excel resources."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from backend.api.dependencies import get_external_excel_read_service
from backend.application.external_excel_read_service import (
    EquipmentCalibrationReadResult,
    ExternalExcelReadError,
    ExternalExcelReadNotFoundError,
    ExternalExcelReadService,
    StandardRecordReadResult,
)


router = APIRouter(tags=["external-excel-read"])


class StandardRecordRowResponse(BaseModel):
    """Standard record row response."""

    standard_code: str
    test_item: str
    sample_description: str | None
    source_sheet: str


class EquipmentCalibrationRowResponse(BaseModel):
    """Equipment calibration row response."""

    equipment_id: str
    equipment_name: str | None
    calibration_due_date: str | None
    source_sheet: str


class StandardRecordReadResponse(BaseModel):
    """Standard record read response."""

    resource_path: str
    matched_sheets: list[str]
    rows: list[StandardRecordRowResponse]


class EquipmentCalibrationReadResponse(BaseModel):
    """Equipment calibration read response."""

    resource_path: str
    matched_sheets: list[str]
    rows: list[EquipmentCalibrationRowResponse]


@router.get(
    "/api/external-resources/standard-record/rows",
    response_model=StandardRecordReadResponse,
)
def read_standard_record_rows(
    query: str | None = Query(default=None),
    service: ExternalExcelReadService = Depends(get_external_excel_read_service),
) -> StandardRecordReadResponse:
    """Read structured rows from configured standard-record workbook."""
    try:
        return _standard_response(service.read_standard_records(query))
    except ExternalExcelReadNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ExternalExcelReadError, FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get(
    "/api/external-resources/equipment-calibration/rows",
    response_model=EquipmentCalibrationReadResponse,
)
def read_equipment_calibration_rows(
    query: str | None = Query(default=None),
    service: ExternalExcelReadService = Depends(get_external_excel_read_service),
) -> EquipmentCalibrationReadResponse:
    """Read structured rows from configured equipment-calibration workbook."""
    try:
        return _equipment_response(service.read_equipment_calibrations(query))
    except ExternalExcelReadNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ExternalExcelReadError, FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _standard_response(result: StandardRecordReadResult) -> StandardRecordReadResponse:
    """Convert standard-record read result to API response."""
    return StandardRecordReadResponse(
        resource_path=result.resource_path,
        matched_sheets=list(result.matched_sheets),
        rows=[
            StandardRecordRowResponse(
                standard_code=row.standard_code,
                test_item=row.test_item,
                sample_description=row.sample_description,
                source_sheet=row.source_sheet,
            )
            for row in result.rows
        ],
    )


def _equipment_response(
    result: EquipmentCalibrationReadResult,
) -> EquipmentCalibrationReadResponse:
    """Convert equipment-calibration read result to API response."""
    return EquipmentCalibrationReadResponse(
        resource_path=result.resource_path,
        matched_sheets=list(result.matched_sheets),
        rows=[
            EquipmentCalibrationRowResponse(
                equipment_id=row.equipment_id,
                equipment_name=row.equipment_name,
                calibration_due_date=row.calibration_due_date,
                source_sheet=row.source_sheet,
            )
            for row in result.rows
        ],
    )
