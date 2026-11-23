"""Read-only structured models for external standard/equipment Excel resources."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
from stat import S_ISREG
from typing import Protocol

from backend.domain import ExternalResource, ExternalResourceType
from backend.infrastructure.office import OfficeFacade
from backend.application.external_resource_service import (
    LEGACY_EQUIPMENT_HEADERS,
    LEGACY_EQUIPMENT_SHEET_NAMES,
    effective_standard_worksheet_name,
    legacy_equipment_excel_layout,
)
from backend.infrastructure.office.excel_com_readonly_tabular_gateway import (
    LegacyExcelComUnavailableError,
    LegacyExcelReadOnlyOpenError,
)
from backend.infrastructure.office.excel_tabular_layout import ExcelTabularLayout
from backend.infrastructure.office.excel_workbook_gateway import UnreadableLtrWorkbookError


logger = logging.getLogger(__name__)
_EQUIPMENT_SETTINGS = "In Settings, check Equipment calibration Excel."


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
    manufacturer: str | None
    last_calibration_date: str | None
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
        path = self._equipment_workbook_path()
        try:
            return self._read_equipment_rows(path, query)
        except (
            OSError, RuntimeError, UnreadableLtrWorkbookError,
            LegacyExcelReadOnlyOpenError, LegacyExcelComUnavailableError,
        ) as exc:
            logger.warning("Could not read the equipment calibration workbook: %s", exc, exc_info=True)
            raise ExternalExcelReadError(
                f"This computer could not read the equipment calibration workbook. {_EQUIPMENT_SETTINGS} "
                "Verify that the file opens and that you have read access."
            ) from exc
        except ValueError as exc:
            logger.warning("Could not use the configured equipment calibration workbook: %s", exc, exc_info=True)
            raise ExternalExcelReadError(
                f"The configured workbook could not be read as a supported equipment table. {_EQUIPMENT_SETTINGS} "
                "Validate the file or select the lab's equipment calibration workbook."
            ) from exc

    def _equipment_workbook_path(self) -> Path:
        resource = self._resources.get_by_type(ExternalResourceType.EQUIPMENT_CALIBRATION_EXCEL)
        if resource is None:
            raise ExternalExcelReadNotFoundError(
                "No equipment calibration workbook is configured. In Settings, select Equipment calibration Excel."
            )
        if not resource.active:
            raise ExternalExcelReadError(
                "The equipment calibration workbook is inactive. In Settings, enable Equipment calibration Excel."
            )
        path = Path(resource.path)
        try:
            mode = path.stat().st_mode
        except FileNotFoundError as exc:
            logger.warning("Configured equipment calibration workbook was not found: %s", exc)
            raise ExternalExcelReadError(
                "This computer cannot find the configured equipment calibration workbook. "
                "In Settings, select a workbook this computer can access."
            ) from exc
        except OSError as exc:
            logger.warning("Configured equipment calibration workbook could not be accessed: %s", exc)
            raise ExternalExcelReadError(
                f"This computer cannot access the equipment calibration workbook. {_EQUIPMENT_SETTINGS} "
                "Check the network connection or file permissions."
            ) from exc
        if not S_ISREG(mode) or path.suffix.lower() not in {".xls", ".xlsx"}:
            raise ExternalExcelReadError(
                "In Settings, select an .xls or .xlsx file for Equipment calibration Excel."
            )
        return path

    def _read_equipment_rows(self, path: Path, query: str | None) -> EquipmentCalibrationReadResult:
        try:
            table = self._office.read_excel_tabular_rows(
                path,
                expected_headers=(
                    "Equipment ID",
                    "Equipment Name",
                    "Manufacturer",
                    "Last Calibration Date",
                    "Calibration Due Date",
                ),
                expected_sheet_name_patterns=(r".*calibration.*", r".*equipment.*"),
                prefer_offline=True,
            )
            field_names = {
                "equipment_id": "Equipment ID",
                "equipment_name": "Equipment Name",
                "manufacturer": "Manufacturer",
                "last_calibration": "Last Calibration Date",
                "calibration_due": "Calibration Due Date",
            }
        except ValueError:
            try:
                table = self._office.read_excel_tabular_rows(
                    path,
                    expected_headers=(
                        "Equipment ID",
                        "Equipment Name",
                        "Calibration Due Date",
                    ),
                    expected_sheet_name_patterns=(r".*calibration.*", r".*equipment.*"),
                    prefer_offline=True,
                )
                field_names = {
                    "equipment_id": "Equipment ID",
                    "equipment_name": "Equipment Name",
                    "manufacturer": "Manufacturer",
                    "last_calibration": "Last Calibration Date",
                    "calibration_due": "Calibration Due Date",
                }
            except ValueError:
                table = self._office.read_excel_tabular_rows(
                    path,
                    expected_headers=LEGACY_EQUIPMENT_HEADERS,
                    expected_sheet_names=LEGACY_EQUIPMENT_SHEET_NAMES,
                    layout=legacy_equipment_excel_layout(),
                    prefer_offline=True,
                )
                field_names = {
                    "equipment_id": "ID Number",
                    "equipment_name": "Item (Equipment Name)",
                    "manufacturer": "Manufacturer",
                    "last_calibration": "Last Cal.",
                    "calibration_due": "Cal. Due",
                }
        rows: list[EquipmentCalibrationRow] = []
        for row in table.rows:
            equipment_id = row.get(field_names["equipment_id"], "").strip()
            equipment_name = row.get(field_names["equipment_name"], "").strip() or None
            manufacturer = row.get(field_names["manufacturer"], "").strip() or None
            last_calibration = (
                row.get(field_names["last_calibration"], "").strip() or None
            )
            due_date = row.get(field_names["calibration_due"], "").strip() or None
            if not equipment_id:
                continue
            mapped = EquipmentCalibrationRow(
                equipment_id=equipment_id,
                equipment_name=equipment_name,
                manufacturer=manufacturer,
                last_calibration_date=last_calibration,
                calibration_due_date=due_date,
                source_sheet=row.get("__sheet_name", ""),
            )
            if _matched_query(
                query,
                mapped.equipment_id,
                mapped.equipment_name or "",
                mapped.manufacturer or "",
                mapped.last_calibration_date or "",
                mapped.calibration_due_date or "",
            ):
                rows.append(mapped)
        return EquipmentCalibrationReadResult(
            resource_path=str(path),
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
