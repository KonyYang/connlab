from __future__ import annotations

from pathlib import Path

from backend.infrastructure.office.excel_com_readonly_tabular_gateway import (
    ExcelComReadonlyTabularGateway,
)
from backend.infrastructure.office.excel_tabular_layout import ExcelTabularLayout


def test_com_explicit_layout_matches_chinese_catalog_without_saving(tmp_path: Path) -> None:
    path = tmp_path / "standard.xls"
    path.touch()
    used = _UsedRange(
        (
            ("Standard record", None, None, None),
            (None, "文 件 编 号", "文 件 名 称", "备注"),
            (None, "EIA-364-04B", "Contact resistance", "Current"),
        )
    )
    lifecycle = _Lifecycle(_Sheet(" 认可标准 ", used))

    result = ExcelComReadonlyTabularGateway(lifecycle).read_tabular_rows(
        path,
        expected_headers=("文 件 编 号",),
        expected_sheet_names=("认可标准",),
        layout=ExcelTabularLayout(
            header_row_number=2,
            required_header_columns=(("文 件 编 号", 2),),
            optional_headers=("文 件 名 称", "备注"),
            include_row_number=True,
            require_unique_sheet_match=True,
        ),
    )

    assert result.rows[0]["文 件 编 号"] == "EIA-364-04B"
    assert result.rows[0]["__row_number"] == "3"
    assert lifecycle.handle.close_calls == [False]


class _Count:
    def __init__(self, value: int) -> None:
        self.Count = value


class _UsedRange:
    def __init__(self, values: tuple[tuple[object, ...], ...]) -> None:
        self.Rows = _Count(len(values))
        self.Columns = _Count(len(values[0]))
        self.Value = values


class _Sheet:
    def __init__(self, name: str, used_range: _UsedRange) -> None:
        self.Name = name
        self.UsedRange = used_range


class _Worksheets:
    def __init__(self, sheet: _Sheet) -> None:
        self.Count = 1
        self._sheet = sheet

    def Item(self, index: int) -> _Sheet:
        assert index == 1
        return self._sheet


class _Workbook:
    def __init__(self, sheet: _Sheet) -> None:
        self.Worksheets = _Worksheets(sheet)


class _Handle:
    def __init__(self, sheet: _Sheet) -> None:
        self.workbook = _Workbook(sheet)
        self.close_calls: list[bool] = []

    def close(self, *, save_changes: bool = False) -> None:
        self.close_calls.append(save_changes)


class _Lifecycle:
    def __init__(self, sheet: _Sheet) -> None:
        self.handle = _Handle(sheet)

    def open_excel_workbook(self, _path, modify_password=None, read_only=False):
        assert modify_password is None
        assert read_only is True
        return self.handle
