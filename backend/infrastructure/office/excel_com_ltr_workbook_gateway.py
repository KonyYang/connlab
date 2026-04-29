"""Excel COM LTR workbook write gateway."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from backend.infrastructure.office.office_facade import OfficeFacade
from backend.modules.ltr import next_monthly_dl_number, parse_ltr_number


class LtrWorkbookWriteError(RuntimeError):
    """Raised when an LTR workbook write operation cannot proceed."""


class LtrWorkbookWriteDisabledError(LtrWorkbookWriteError):
    """Raised when workbook write is disabled by configuration."""


class LtrWorkbookReadOnlyError(LtrWorkbookWriteError):
    """Raised when Excel opens the workbook read-only."""


@dataclass(frozen=True, slots=True)
class LtrWorkbookWriteConfig:
    """Configuration required for an LTR workbook write session."""

    path: Path | None
    write_enabled: bool = False
    modify_password: str | None = None


@dataclass(frozen=True, slots=True)
class LtrWorkbookRowData:
    """One row of LTR workbook registration data for columns A:Q."""

    month: str
    total: int
    monthly_number: int
    dl_number: str
    project_type: str | None = None
    description_pn: str | None = None
    test_item: str | None = None
    test_type: str | None = None
    requested_by: str | None = None
    location: str | None = None
    project_leader: str | None = None
    test_result: str | None = None
    failed_item: str | None = None
    sample_deposition: str | None = None
    sub_contract: str | None = None
    test_fee: str | None = None
    remarks_po: str | None = None

    def as_excel_row(self) -> list[object]:
        """Return values ordered for columns A:Q."""
        return [
            self.month,
            self.total,
            self.monthly_number,
            self.dl_number,
            self.project_type,
            self.description_pn,
            self.test_item,
            self.test_type,
            self.requested_by,
            self.location,
            self.project_leader,
            self.test_result,
            self.failed_item,
            self.sample_deposition,
            self.sub_contract,
            self.test_fee,
            self.remarks_po,
        ]


@dataclass(frozen=True, slots=True)
class LtrWorkbookRowPointer:
    """Pointer to a written workbook row."""

    sheet_name: str
    row_number: int
    dl_number: str


class ExcelComLTRWorkbookGateway:
    """Open `.xls` LTR workbooks through OfficeFacade and Excel COM."""

    def __init__(
        self,
        office: OfficeFacade,
        config: LtrWorkbookWriteConfig,
    ) -> None:
        """Create the gateway."""
        self._office = office
        self._config = config

    def open_write_session(self) -> "ExcelComLTRWorkbookWriteSession":
        """Open a write session through the Office facade."""
        if not self._config.write_enabled:
            raise LtrWorkbookWriteDisabledError("LTR workbook write is disabled.")
        if self._config.path is None:
            raise LtrWorkbookWriteError("LTR workbook path is not configured.")
        if not self._config.modify_password:
            raise LtrWorkbookWriteError("LTR workbook modify password is not configured.")

        handle = self._office.open_excel_workbook(
            self._config.path,
            modify_password=self._config.modify_password,
            read_only=False,
        )
        return ExcelComLTRWorkbookWriteSession(handle)


class ExcelComLTRWorkbookWriteSession:
    """Context-manager write session for one LTR workbook transaction."""

    def __init__(self, handle) -> None:
        """Create a write session from an OfficeFacade workbook handle."""
        self._handle = handle
        self._closed = False

    def __enter__(self) -> "ExcelComLTRWorkbookWriteSession":
        try:
            self.assert_not_read_only()
        except Exception:
            self.close(save_changes=False)
            raise
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close(save_changes=False)

    def assert_not_read_only(self) -> None:
        """Block write operations if Excel opened the workbook read-only."""
        if bool(getattr(self._handle.workbook, "ReadOnly", False)):
            raise LtrWorkbookReadOnlyError(
                "LTR workbook opened read-only; check password or file lock."
            )

    def list_sheets(self) -> list[str]:
        """Return workbook sheet names."""
        return [sheet.Name for sheet in self._handle.workbook.Worksheets]

    def read_annual_sheet(self, sheet_name: str) -> tuple[tuple[object, ...], ...]:
        """Read annual sheet A:Q data in one batch range call."""
        sheet = self._handle.workbook.Worksheets.Item(sheet_name)
        last_row = int(sheet.UsedRange.Rows.Count)
        if last_row < 2:
            return ()
        values = sheet.Range(f"A2:Q{last_row}").Value
        return _tuple_rows(values)

    def append_registration_row(
        self,
        sheet_name: str,
        row_data: LtrWorkbookRowData,
    ) -> LtrWorkbookRowPointer:
        """Append one registration row using a single row-range assignment."""
        sheet = self._handle.workbook.Worksheets.Item(sheet_name)
        target_row = int(sheet.UsedRange.Rows.Count) + 1
        sheet.Range(f"A{target_row}:Q{target_row}").Value = [row_data.as_excel_row()]
        return LtrWorkbookRowPointer(
            sheet_name=sheet_name,
            row_number=target_row,
            dl_number=row_data.dl_number,
        )

    def append_next_normal_registration(
        self,
        sheet_name: str,
        year: int,
        month: int,
        row_data: LtrWorkbookRowData,
    ) -> LtrWorkbookRowPointer:
        """Calculate the final normal DL inside the write session and append it."""
        existing_numbers = [
            str(row[3])
            for row in self.read_annual_sheet(sheet_name)
            if len(row) >= 4 and row[3]
        ]
        final_number = next_monthly_dl_number(
            year=year,
            month=month,
            existing_numbers=existing_numbers,
        )
        parsed = parse_ltr_number(final_number)
        return self.append_registration_row(
            sheet_name,
            replace(
                row_data,
                monthly_number=parsed.sequence or row_data.monthly_number,
                dl_number=final_number,
            ),
        )

    def save(self) -> None:
        """Save the workbook."""
        self._handle.save()

    def close(self, save_changes: bool = False) -> None:
        """Close the workbook handle once."""
        if self._closed:
            return
        self._closed = True
        self._handle.close(save_changes=save_changes)


def _tuple_rows(values) -> tuple[tuple[object, ...], ...]:
    """Normalize Excel range values to tuple rows."""
    if values is None:
        return ()
    if not isinstance(values, tuple):
        return ((values,),)
    if values and not isinstance(values[0], tuple):
        return (values,)
    return tuple(tuple(row) for row in values)
