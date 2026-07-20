"""Read-only structured models for external standard/equipment Excel resources."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from backend.domain import ExternalResource, ExternalResourceType
from backend.infrastructure.office import OfficeFacade
from backend.application.external_resource_service import effective_standard_worksheet_name
from backend.infrastructure.office.excel_tabular_layout import ExcelTabularLayout


class ExternalExcelReadError(ValueError):
    """Raised when external Excel read models cannot be loaded."""


class ExternalExcelReadNotFoundError(LookupError):
    """Raised when a required external Excel resource is not registered."""


class ExternalResourceStorePort(Protocol):
    """Registry lookup behavior required by external Excel read service."""

    def get_by_type(
        self,
        resource_type: ExternalResourceType,
    ) -> ExternalResource | None:
        """Return one configured external resource by type."""


@dataclass(frozen=True, slots=True)
class StandardRecordRow:
    """One structured row from the standard record workbook."""

    standard_code: str
    test_item: str
    sample_description: str | None
    source_sheet: str
    source_row_number: int | None = None


@dataclass(frozen=True, slots=True)
class EquipmentCalibrationRow:
    """One structured row from the equipment calibration workbook."""

    equipment_id: str
    equipment_name: str | None
    calibration_due_date: str | None
    source_sheet: str


@dataclass(frozen=True, slots=True)
class StandardRecordReadResult:
    """Structured standard-record read result."""

    resource_path: str
    matched_sheets: tuple[str, ...]
    rows: tuple[StandardRecordRow, ...]


@dataclass(frozen=True, slots=True)
class EquipmentCalibrationReadResult:
    """Structured equipment-calibration read result."""

    resource_path: str
    matched_sheets: tuple[str, ...]
    rows: tuple[EquipmentCalibrationRow, ...]


class ExternalExcelReadService:
    """Provide read-only structured models for configured external Excel files."""

    def __init__(
        self,
        resource_store: ExternalResourceStorePort,
        office: OfficeFacade | None = None,
    ) -> None:
        self._resources = resource_store
        self._office = office or OfficeFacade()

    def read_standard_records(self, query: str | None = None) -> StandardRecordReadResult:
        """Read configured standard record Excel rows with optional query filter."""
        resource = self._require_resource(ExternalResourceType.STANDARD_RECORD_EXCEL)
        worksheet_name = effective_standard_worksheet_name(resource) or "认可标准"
        table = self._office.read_excel_tabular_rows(
            resource.path,
            expected_headers=("文 件 编 号",),
            expected_sheet_names=(worksheet_name,),
            layout=ExcelTabularLayout(
                header_row_number=2,
                required_header_columns=(("文 件 编 号", 2),),
                optional_headers=("文 件 名 称", "备注"),
                include_row_number=True,
                require_unique_sheet_match=True,
            ),
        )
        rows: list[StandardRecordRow] = []
        for row in table.rows:
            code = row.get("文 件 编 号", "").strip()
            item = row.get("文 件 名 称", "").strip()
            sample = row.get("备注", "").strip() or None
            if not code:
                continue
            mapped = StandardRecordRow(
                standard_code=code,
                test_item=item,
                sample_description=sample,
                source_sheet=row.get("__sheet_name", ""),
                source_row_number=(
                    int(row["__row_number"]) if row.get("__row_number") else None
                ),
            )
            if _matched_query(query, mapped.standard_code, mapped.test_item, sample or ""):
                rows.append(mapped)
        return StandardRecordReadResult(
            resource_path=str(resource.path),
            matched_sheets=table.matched_sheet_names,
            rows=tuple(rows),
        )

    def read_equipment_calibrations(
        self,
        query: str | None = None,
    ) -> EquipmentCalibrationReadResult:
        """Read configured equipment calibration Excel rows with optional query filter."""
        resource = self._require_resource(ExternalResourceType.EQUIPMENT_CALIBRATION_EXCEL)
        table = self._office.read_excel_tabular_rows(
            resource.path,
            expected_headers=("Equipment ID", "Equipment Name", "Calibration Due Date"),
            expected_sheet_name_patterns=(r".*calibration.*", r".*equipment.*"),
        )
        rows: list[EquipmentCalibrationRow] = []
        for row in table.rows:
            equipment_id = row.get("Equipment ID", "").strip()
            equipment_name = row.get("Equipment Name", "").strip() or None
            due_date = row.get("Calibration Due Date", "").strip() or None
            if not equipment_id:
                continue
            mapped = EquipmentCalibrationRow(
                equipment_id=equipment_id,
                equipment_name=equipment_name,
                calibration_due_date=due_date,
                source_sheet=row.get("__sheet_name", ""),
            )
            if _matched_query(
                query,
                mapped.equipment_id,
                mapped.equipment_name or "",
                mapped.calibration_due_date or "",
            ):
                rows.append(mapped)
        return EquipmentCalibrationReadResult(
            resource_path=str(resource.path),
            matched_sheets=table.matched_sheet_names,
            rows=tuple(rows),
        )

    def _require_resource(self, resource_type: ExternalResourceType) -> ExternalResource:
        """Load one configured, active external resource path."""
        resource = self._resources.get_by_type(resource_type)
        if resource is None:
            raise ExternalExcelReadNotFoundError(
                f"External resource is not registered: {resource_type.value}"
            )
        if not resource.active:
            raise ExternalExcelReadError(
                f"External resource is inactive: {resource_type.value}"
            )
        if not Path(resource.path).is_file():
            raise ExternalExcelReadError(f"External resource file does not exist: {resource.path}")
        return resource


def _matched_query(query: str | None, *fields: str) -> bool:
    """Return whether any field contains the query text."""
    if not query or not query.strip():
        return True
    lowered = query.strip().lower()
    return any(lowered in field.lower() for field in fields if field)
