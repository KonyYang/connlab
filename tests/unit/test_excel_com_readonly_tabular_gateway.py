from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from backend.infrastructure.office.excel_com_readonly_tabular_gateway import (
    ExcelComReadonlyTabularGateway,
    LegacyExcelCleanupError,
    LegacyExcelComUnavailableError,
    LegacyExcelRangeError,
    LegacyExcelReadError,
    LegacyExcelReadOnlyOpenError,
    UnsupportedExternalExcelTabularFormatError,
)
from backend.infrastructure.office.models import ExcelStructureProbeResult
from backend.infrastructure.office.models import ExcelTabularReadResult
from backend.infrastructure.office.office_facade import OfficeFacade
from backend.infrastructure.office.office_lifecycle import OfficeAutomationUnavailable


def test_reads_xls_rows_with_xlsx_compatible_header_semantics(tmp_path: Path) -> None:
    path = _xls_file(tmp_path)
    used_range = _FakeUsedRange(
        3,
        3,
        ((" Part No ", "Qty", "Date"), ("P-1", 4, None), ("", "", "")),
    )
    lifecycle = _FakeLifecycle([_FakeSheet("Records 2026", used_range)])

    result = ExcelComReadonlyTabularGateway(lifecycle).read_tabular_rows(
        path,
        expected_headers=("Part No", "Qty", "Date"),
        expected_sheet_name_patterns=(r"Records \d{4}",),
    )

    assert lifecycle.open_calls == [(path, None, True)]
    assert lifecycle.handle.close_calls == [False]
    assert result == ExcelTabularReadResult(
        workbook_path=path,
        matched_sheet_names=("Records 2026",),
        headers=("Part No", "Qty", "Date"),
        rows=(
            {
                "Part No": "P-1",
                "Qty": "4",
                "Date": "",
                "__sheet_name": "Records 2026",
            },
        ),
    )


def test_probe_uses_value2_only_when_value_read_fails(tmp_path: Path) -> None:
    path = _xls_file(tmp_path)
    used_range = _FakeUsedRange(
        1,
        2,
        (("Equipment ID", "Calibration Date"),),
        value_error=_ComReadCompatibilityError("Value unavailable"),
    )
    lifecycle = _FakeLifecycle([_FakeSheet("Calibration", used_range)])

    result = ExcelComReadonlyTabularGateway(lifecycle).probe_structure(
        path,
        expected_headers=("Equipment ID",),
        expected_date_headers=("Calibration Date",),
        expected_sheet_names=("calibration",),
    )

    assert result == ExcelStructureProbeResult(
        workbook_path=path,
        sheet_names=("Calibration",),
        matched_sheet_names=("Calibration",),
        observed_headers=("Equipment ID", "Calibration Date"),
        missing_headers=(),
        missing_date_headers=(),
        valid=True,
        failure_reason=None,
    )
    assert used_range.value_accesses == 1
    assert used_range.value2_accesses == 1


def test_arbitrary_value_failure_does_not_read_value2(tmp_path: Path) -> None:
    path = _xls_file(tmp_path)
    used_range = _FakeUsedRange(
        1,
        1,
        "Value2 must not be read",
        value_error=RuntimeError("programming failure"),
    )
    lifecycle = _FakeLifecycle([_FakeSheet("Data", used_range)])

    with pytest.raises(LegacyExcelReadError, match="programming failure"):
        ExcelComReadonlyTabularGateway(lifecycle).probe_structure(
            path,
            expected_headers=("Header",),
        )

    assert used_range.value_accesses == 1
    assert used_range.value2_accesses == 0
    assert lifecycle.handle.close_calls == [False]


def test_arbitrary_value_failure_wins_over_cleanup_failure(tmp_path: Path) -> None:
    path = _xls_file(tmp_path)
    used_range = _FakeUsedRange(
        1,
        1,
        "Value2 must not be read",
        value_error=RuntimeError("primary read failure"),
    )
    lifecycle = _FakeLifecycle(
        [_FakeSheet("Data", used_range)],
        close_error=RuntimeError("cleanup failure"),
    )

    with pytest.raises(LegacyExcelReadError, match="primary read failure") as exc_info:
        ExcelComReadonlyTabularGateway(lifecycle).probe_structure(
            path,
            expected_headers=("Header",),
        )

    assert used_range.value2_accesses == 0
    assert "cleanup failure" in " ".join(exc_info.value.__notes__)


def test_cell_values_are_rendered_deterministically(tmp_path: Path) -> None:
    path = _xls_file(tmp_path)
    values = (
        ("Date", "Time", "Flag", "Float", "Decimal"),
        (
            date(2026, 7, 20),
            datetime(2026, 7, 20, 13, 14, 15),
            True,
            12.5,
            Decimal("3.2500"),
        ),
    )
    lifecycle = _FakeLifecycle(
        [_FakeSheet("Data", _FakeUsedRange(2, 5, values))]
    )

    result = ExcelComReadonlyTabularGateway(lifecycle).read_tabular_rows(
        path,
        expected_headers=("Date", "Time", "Flag", "Float", "Decimal"),
    )

    assert result.rows[0] == {
        "Date": "2026-07-20",
        "Time": "2026-07-20T13:14:15",
        "Flag": "TRUE",
        "Float": "12.5",
        "Decimal": "3.25",
        "__sheet_name": "Data",
    }


@pytest.mark.parametrize(
    ("open_error", "error_type"),
    [
        (OfficeAutomationUnavailable("missing COM"), LegacyExcelComUnavailableError),
        (RuntimeError("damaged workbook"), LegacyExcelReadOnlyOpenError),
    ],
)
def test_open_failures_are_wrapped_as_clear_value_errors(
    tmp_path: Path,
    open_error: Exception,
    error_type: type[Exception],
) -> None:
    path = _xls_file(tmp_path)

    with pytest.raises(error_type):
        ExcelComReadonlyTabularGateway(_FakeLifecycle([], open_error=open_error)).probe_structure(
            path,
            expected_headers=("Header",),
        )


def test_successful_read_with_cleanup_failure_is_typed(tmp_path: Path) -> None:
    path = _xls_file(tmp_path)
    lifecycle = _FakeLifecycle(
        [_FakeSheet("Data", _FakeUsedRange(1, 1, "Header"))],
        close_error=RuntimeError("quit failed"),
    )

    with pytest.raises(LegacyExcelCleanupError, match="quit failed"):
        ExcelComReadonlyTabularGateway(lifecycle).probe_structure(
            path,
            expected_headers=("Header",),
        )


def test_primary_read_error_wins_over_cleanup_failure(tmp_path: Path) -> None:
    path = _xls_file(tmp_path)
    lifecycle = _FakeLifecycle(
        [_FakeSheet("Data", _FakeUsedRange(1, 1, object()))],
        close_error=RuntimeError("quit failed"),
    )

    with pytest.raises(LegacyExcelReadError, match="Unsupported value") as exc_info:
        ExcelComReadonlyTabularGateway(lifecycle).probe_structure(
            path,
            expected_headers=("Header",),
        )

    assert "quit failed" in " ".join(exc_info.value.__notes__)


def test_sheet_and_header_mismatch_diagnostics_are_stable(tmp_path: Path) -> None:
    path = _xls_file(tmp_path)
    lifecycle = _FakeLifecycle(
        [_FakeSheet("Other", _FakeUsedRange(1, 1, "Wrong"))]
    )
    gateway = ExcelComReadonlyTabularGateway(lifecycle)

    with pytest.raises(LegacyExcelReadError, match="No worksheet matched"):
        gateway.read_tabular_rows(
            path,
            expected_headers=("Header",),
            expected_sheet_names=("Data",),
        )

    lifecycle = _FakeLifecycle(
        [_FakeSheet("Data", _FakeUsedRange(1, 1, "Wrong"))]
    )
    with pytest.raises(LegacyExcelReadError, match="Expected headers were not found"):
        ExcelComReadonlyTabularGateway(lifecycle).read_tabular_rows(
            path,
            expected_headers=("Header",),
        )


@pytest.mark.parametrize(
    ("rows", "columns"),
    [(65_536, 1), (1, 256), (4_000, 250)],
)
def test_inclusive_used_range_limits_reach_value_accessor(
    tmp_path: Path,
    rows: int,
    columns: int,
) -> None:
    path = _xls_file(tmp_path)
    used_range = _FakeUsedRange(rows, columns, (("Header",),))
    lifecycle = _FakeLifecycle([_FakeSheet("Data", used_range)])

    with pytest.raises(LegacyExcelReadError, match="shape"):
        ExcelComReadonlyTabularGateway(lifecycle).probe_structure(
            path,
            expected_headers=("Header",),
        )

    assert used_range.value_accesses == 1


@pytest.mark.parametrize(
    ("rows", "columns"),
    [(65_537, 1), (1, 257), (4_001, 250), (True, 1), (1.5, 1), (-1, 1)],
)
def test_invalid_or_oversized_used_range_is_rejected_before_values(
    tmp_path: Path,
    rows: object,
    columns: object,
) -> None:
    path = _xls_file(tmp_path)
    used_range = _FakeUsedRange(rows, columns, (("Header",),))
    lifecycle = _FakeLifecycle([_FakeSheet("Data", used_range)])

    with pytest.raises(LegacyExcelRangeError):
        ExcelComReadonlyTabularGateway(lifecycle).probe_structure(
            path,
            expected_headers=("Header",),
        )

    assert used_range.value_accesses == 0
    assert used_range.value2_accesses == 0


def test_facade_routes_only_xls_to_legacy_gateway(tmp_path: Path) -> None:
    xls = _xls_file(tmp_path)
    xlsx = tmp_path / "current.xlsx"
    xlsx.touch()
    accepted = _RecordingGateway("xlsx")
    legacy = _RecordingGateway("xls")
    facade = OfficeFacade(excel_gateway=accepted, legacy_excel_gateway=legacy)

    facade.probe_excel_structure(xlsx, expected_headers=("A",))
    facade.read_excel_tabular_rows(xls, expected_headers=("A",))

    assert accepted.calls == [("probe", xlsx)]
    assert legacy.calls == [("read", xls)]


def test_facade_rejects_other_tabular_suffixes(tmp_path: Path) -> None:
    path = tmp_path / "legacy.csv"
    path.touch()

    with pytest.raises(
        UnsupportedExternalExcelTabularFormatError,
        match=r"Expected an Excel file \(\.xlsx or \.xls\)",
    ):
        OfficeFacade().probe_excel_structure(path, expected_headers=("A",))


class _FakeCount:
    def __init__(self, count: object) -> None:
        self.Count = count


class _ComReadCompatibilityError(Exception):
    pass


_ComReadCompatibilityError.__name__ = "com_error"
_ComReadCompatibilityError.__module__ = "pywintypes"


class _FakeUsedRange:
    def __init__(
        self,
        rows: object,
        columns: object,
        value: object,
        *,
        value_error: Exception | None = None,
    ) -> None:
        self.Rows = _FakeCount(rows)
        self.Columns = _FakeCount(columns)
        self._value = value
        self._value_error = value_error
        self.value_accesses = 0
        self.value2_accesses = 0

    @property
    def Value(self):
        self.value_accesses += 1
        if self._value_error is not None:
            raise self._value_error
        return self._value

    @property
    def Value2(self):
        self.value2_accesses += 1
        return self._value


class _FakeSheet:
    def __init__(self, name: str, used_range: _FakeUsedRange) -> None:
        self.Name = name
        self.UsedRange = used_range


class _FakeWorksheets:
    def __init__(self, sheets: list[_FakeSheet]) -> None:
        self._sheets = sheets
        self.Count = len(sheets)

    def Item(self, index: int) -> _FakeSheet:
        return self._sheets[index - 1]


class _FakeWorkbook:
    def __init__(self, sheets: list[_FakeSheet]) -> None:
        self.Worksheets = _FakeWorksheets(sheets)


class _FakeHandle:
    def __init__(
        self,
        sheets: list[_FakeSheet],
        close_error: Exception | None = None,
    ) -> None:
        self.workbook = _FakeWorkbook(sheets)
        self.close_calls: list[bool] = []
        self._close_error = close_error

    def close(self, save_changes: bool = False) -> None:
        self.close_calls.append(save_changes)
        if self._close_error is not None:
            raise self._close_error


class _FakeLifecycle:
    def __init__(
        self,
        sheets: list[_FakeSheet],
        *,
        open_error: Exception | None = None,
        close_error: Exception | None = None,
    ) -> None:
        self.handle = _FakeHandle(sheets, close_error)
        self._open_error = open_error
        self.open_calls: list[tuple[Path, str | None, bool]] = []

    def open_excel_workbook(
        self,
        path: Path,
        modify_password: str | None = None,
        read_only: bool = False,
    ) -> _FakeHandle:
        self.open_calls.append((path, modify_password, read_only))
        if self._open_error is not None:
            raise self._open_error
        return self.handle


class _RecordingGateway:
    def __init__(self, name: str) -> None:
        self.name = name
        self.calls: list[tuple[str, Path]] = []

    def probe_structure(self, path: Path, **_kwargs):
        self.calls.append(("probe", path))
        return object()

    def read_tabular_rows(self, path: Path, **_kwargs):
        self.calls.append(("read", path))
        return object()


def _xls_file(tmp_path: Path) -> Path:
    path = tmp_path / "legacy.xls"
    path.touch()
    return path
