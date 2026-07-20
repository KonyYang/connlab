from __future__ import annotations

from pathlib import Path

from backend.application.external_excel_read_service import ExternalExcelReadService
from backend.domain import ExternalResource, ExternalResourceType
from backend.infrastructure.office.models import ExcelTabularReadResult


def test_standard_catalog_uses_effective_sheet_and_chinese_columns(tmp_path: Path) -> None:
    workbook = tmp_path / "standard.xls"
    workbook.touch()
    office = _Office(
        ExcelTabularReadResult(
            workbook_path=workbook,
            matched_sheet_names=("认可标准",),
            headers=("文 件 编 号", "文 件 名 称", "备注"),
            rows=(
                {
                    "文 件 编 号": "EIA-364-04B",
                    "文 件 名 称": "Contact resistance",
                    "备注": "current",
                    "__sheet_name": "认可标准",
                    "__row_number": "3",
                },
            ),
        )
    )
    service = ExternalExcelReadService(
        _Store(
            ExternalResource(
                resource_id="R1",
                resource_type=ExternalResourceType.STANDARD_RECORD_EXCEL,
                path=workbook,
                worksheet_name=None,
            )
        ),
        office=office,
    )

    result = service.read_standard_records()

    assert office.kwargs["expected_sheet_names"] == ("认可标准",)
    assert office.kwargs["layout"].header_row_number == 2
    assert result.rows[0].standard_code == "EIA-364-04B"
    assert result.rows[0].test_item == "Contact resistance"


class _Store:
    def __init__(self, resource: ExternalResource) -> None:
        self.resource = resource

    def get_by_type(self, resource_type):
        return self.resource if resource_type is self.resource.resource_type else None


class _Office:
    def __init__(self, result: ExcelTabularReadResult) -> None:
        self.result = result
        self.kwargs = {}

    def read_excel_tabular_rows(self, _path, **kwargs):
        self.kwargs = kwargs
        return self.result
