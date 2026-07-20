from __future__ import annotations

from pathlib import Path

import pytest

from backend.application.external_resource_service import (
    ExternalResourceService,
    ExternalResourceWorksheetNameError,
    WorksheetNameUpdate,
)
from backend.domain import ExternalResource, ExternalResourceType


class _Resources:
    def __init__(self) -> None:
        self.items: dict[ExternalResourceType, ExternalResource] = {}
        self.writes = 0

    def list_all(self) -> list[ExternalResource]:
        return list(self.items.values())

    def get_by_type(self, resource_type: ExternalResourceType) -> ExternalResource | None:
        return self.items.get(resource_type)

    def upsert(self, resource: ExternalResource) -> ExternalResource:
        self.writes += 1
        self.items[resource.resource_type] = resource
        return resource


def test_standard_sheet_omission_preserves_and_reset_stores_null() -> None:
    resources = _Resources()
    service = ExternalResourceService(resources)

    saved = service.upsert_resource(
        ExternalResourceType.STANDARD_RECORD_EXCEL,
        Path("standard.xlsx"),
        True,
        worksheet_name=WorksheetNameUpdate(supplied=True, value="  Methods  "),
    )
    preserved = service.upsert_resource(
        ExternalResourceType.STANDARD_RECORD_EXCEL,
        Path("standard-2.xlsx"),
        True,
    )
    reset = service.upsert_resource(
        ExternalResourceType.STANDARD_RECORD_EXCEL,
        Path("standard-2.xlsx"),
        True,
        worksheet_name=WorksheetNameUpdate(supplied=True, value="   "),
    )

    assert saved.worksheet_name == "Methods"
    assert preserved.worksheet_name == "Methods"
    assert reset.worksheet_name is None
    assert service.effective_worksheet_name(reset) == "认可标准"


@pytest.mark.parametrize("value", ["bad/name", "bad:name", "x" * 32, "bad\nname"])
def test_invalid_standard_sheet_is_no_write(value: str) -> None:
    resources = _Resources()
    service = ExternalResourceService(resources)
    service.upsert_resource(
        ExternalResourceType.STANDARD_RECORD_EXCEL,
        Path("standard.xlsx"),
        True,
        worksheet_name=WorksheetNameUpdate(supplied=True, value="Methods"),
    )
    writes = resources.writes

    with pytest.raises(ExternalResourceWorksheetNameError):
        service.upsert_resource(
            ExternalResourceType.STANDARD_RECORD_EXCEL,
            Path("changed.xlsx"),
            True,
            worksheet_name=WorksheetNameUpdate(supplied=True, value=value),
        )

    assert resources.writes == writes
    assert resources.items[ExternalResourceType.STANDARD_RECORD_EXCEL].path == Path(
        "standard.xlsx"
    )


def test_non_standard_rejects_supplied_sheet_even_null() -> None:
    resources = _Resources()
    service = ExternalResourceService(resources)

    with pytest.raises(ExternalResourceWorksheetNameError):
        service.upsert_resource(
            ExternalResourceType.EQUIPMENT_CALIBRATION_EXCEL,
            Path("equipment.xlsx"),
            True,
            worksheet_name=WorksheetNameUpdate(supplied=True, value=None),
        )

    assert resources.writes == 0
