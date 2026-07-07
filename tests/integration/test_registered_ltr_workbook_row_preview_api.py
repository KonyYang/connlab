from __future__ import annotations

from pathlib import Path
from datetime import date

from fastapi.testclient import TestClient

from backend.api.dependencies import get_registered_ltr_workbook_row_preview_service
from backend.api.main import app
from backend.application.registered_ltr_workbook_row_preview_service import (
    RegisteredLtrWorkbookRowPreview,
    RegisteredLtrWorkbookRowPreviewRowValue,
    RegisteredLtrWorkbookRowPreviewService,
)
from backend.domain import LtrRecord, LtrStatus


def test_registered_ltr_workbook_row_preview_api_returns_read_only_row_values() -> None:
    fake = _FakeRegisteredRowPreviewService()
    app.dependency_overrides[get_registered_ltr_workbook_row_preview_service] = (
        lambda: fake
    )
    client = TestClient(app)

    try:
        response = client.get("/api/projects/P1/ltr-workbook/registered-row-preview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "found"
    assert payload["project_id"] == "P1"
    assert payload["ltr_number"] == "DL-2026-05-011"
    assert payload["workbook_path"] == "D:\\PublicProject\\LTR.xlsx"
    assert payload["sheet_name"] == "2026"
    assert payload["row_number"] == 42
    assert payload["row_values"] == [
        {
            "field_name": "project_type",
            "label": "Project Type",
            "value": "NPD",
            "is_blank": False,
        },
        {
            "field_name": "description_pn",
            "label": "Description P/N",
            "value": "Coolpower HDF",
            "is_blank": False,
        },
    ]
    assert "preview_ack" not in payload
    assert "backup_path" not in payload
    assert fake.project_id == "P1"


def test_registered_ltr_workbook_row_preview_api_returns_blocked_state() -> None:
    app.dependency_overrides[get_registered_ltr_workbook_row_preview_service] = (
        lambda: _FakeRegisteredRowPreviewService(blocked=True)
    )
    client = TestClient(app)

    try:
        response = client.get("/api/projects/P1/ltr-workbook/registered-row-preview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "blocked"
    assert payload["blockers"] == ["Registered LTR is required for workbook row preview."]
    assert payload["row_values"] == []


def test_registered_ltr_workbook_row_preview_api_maps_workbook_read_failure() -> None:
    service = RegisteredLtrWorkbookRowPreviewService(
        ltr_store=_FakeLtrStore(),
        transaction_gateway=_FailingTransactionGateway(RuntimeError("Excel is locked")),
    )
    app.dependency_overrides[get_registered_ltr_workbook_row_preview_service] = (
        lambda: service
    )
    client = TestClient(app)

    try:
        response = client.get("/api/projects/P1/ltr-workbook/registered-row-preview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "blocked"
    assert payload["ltr_number"] == "DL-2026-05-011"
    assert payload["blockers"] == [
        "Unable to read LTR workbook for preview: Excel is locked"
    ]
    assert payload["row_values"] == []


class _FakeRegisteredRowPreviewService:
    def __init__(self, *, blocked: bool = False) -> None:
        self.blocked = blocked
        self.project_id: str | None = None

    def preview(self, command):
        self.project_id = command.project_id
        if self.blocked:
            return RegisteredLtrWorkbookRowPreview(
                status="blocked",
                project_id=command.project_id,
                ltr_number=None,
                message="Registered LTR is required for workbook row preview.",
                workbook_path=None,
                sheet_name=None,
                row_number=None,
                row_values=(),
                blockers=("Registered LTR is required for workbook row preview.",),
            )
        return RegisteredLtrWorkbookRowPreview(
            status="found",
            project_id=command.project_id,
            ltr_number="DL-2026-05-011",
            message="LTR workbook row found.",
            workbook_path=Path("D:/PublicProject/LTR.xlsx"),
            sheet_name="2026",
            row_number=42,
            row_values=(
                RegisteredLtrWorkbookRowPreviewRowValue(
                    field_name="project_type",
                    label="Project Type",
                    value="NPD",
                    is_blank=False,
                ),
                RegisteredLtrWorkbookRowPreviewRowValue(
                    field_name="description_pn",
                    label="Description P/N",
                    value="Coolpower HDF",
                    is_blank=False,
                ),
            ),
        )


class _FakeLtrStore:
    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        return [
            LtrRecord(
                ltr_id="LTR1",
                project_id=project_id,
                ltr_number="DL-2026-05-011",
                status=LtrStatus.REGISTERED,
                registered_on=date(2026, 5, 11),
            )
        ]


class _FailingTransactionGateway:
    def __init__(self, error: Exception) -> None:
        self.error = error

    def open_read_only_transaction(self):
        raise self.error
