from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.dependencies import get_ltr_workbook_basic_information_sync_service
from backend.api.main import app
from backend.application.ltr_workbook_basic_information_sync_service import (
    LtrWorkbookBasicInformationSyncError,
    LtrWorkbookBasicInformationSyncComparisonValue,
    LtrWorkbookBasicInformationSyncPreview,
    LtrWorkbookBasicInformationSyncResult,
)
from backend.application.ltr_workbook_write_preview_service import (
    LtrWorkbookWriteColumnPreview,
)
from backend.infrastructure.office import LtrWorkbookLockTimeoutError, LtrWorkbookRowData


def test_ltr_workbook_basic_information_sync_preview_api_returns_context() -> None:
    fake = _FakeSyncService()
    app.dependency_overrides[get_ltr_workbook_basic_information_sync_service] = lambda: fake
    client = TestClient(app)

    try:
        response = client.get("/api/projects/P1/ltr-workbook/basic-information-sync/preview")

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ready"
        assert payload["project_id"] == "P1"
        assert payload["ltr_number"] == "DL-2026-05-011"
        assert payload["target_sheet"] == "2026"
        assert payload["target_row"] == 3
        assert payload["confirmed_basic_information_version"] == 7
        assert payload["confirmed_basic_information_source_signature_hash"] == "hash-7"
        assert payload["columns"][3]["field_name"] == "dl_number"
        assert [value["field_name"] for value in payload["comparison_values"][:4]] == [
            "project_type",
            "description_pn",
            "test_item",
            "test_type_in_sheet",
        ]
        assert payload["comparison_values"][1] == {
            "field_name": "description_pn",
            "label": "Description P/N",
            "current_value": "Old P/N",
            "pending_value": "Coolpower HDF 3.40mm pin",
        }
        assert fake.preview_project_id == "P1"
    finally:
        app.dependency_overrides.clear()


def test_ltr_workbook_basic_information_sync_commit_api_requires_context() -> None:
    fake = _FakeSyncService()
    app.dependency_overrides[get_ltr_workbook_basic_information_sync_service] = lambda: fake
    client = TestClient(app)

    try:
        response = client.post(
            "/api/projects/P1/ltr-workbook/basic-information-sync/commit",
            json={
                "operator_confirmed": True,
                "preview_acknowledged": True,
                "expected_confirmed_basic_information_version": 7,
                "expected_confirmed_basic_information_source_signature_hash": "hash-7",
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["sheet_name"] == "2026"
        assert payload["row_number"] == 3
        assert fake.commit_command.expected_confirmed_basic_information_version == 7
    finally:
        app.dependency_overrides.clear()


def test_ltr_workbook_basic_information_sync_commit_api_maps_errors() -> None:
    app.dependency_overrides[get_ltr_workbook_basic_information_sync_service] = (
        lambda: _FakeSyncService(error="Basic Information changed after preview.")
    )
    client = TestClient(app)

    try:
        response = client.post(
            "/api/projects/P1/ltr-workbook/basic-information-sync/commit",
            json={
                "operator_confirmed": True,
                "preview_acknowledged": True,
                "expected_confirmed_basic_information_version": 1,
                "expected_confirmed_basic_information_source_signature_hash": "old",
            },
        )

        assert response.status_code == 409
        assert "Basic Information changed" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_ltr_workbook_basic_information_sync_preview_api_returns_blocked_business_preview() -> None:
    app.dependency_overrides[get_ltr_workbook_basic_information_sync_service] = (
        lambda: _FakeSyncService(blocked=True)
    )
    client = TestClient(app)

    try:
        response = client.get("/api/projects/P1/ltr-workbook/basic-information-sync/preview")

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "blocked"
        assert payload["blockers"] == [
            "Confirm Basic Information before synchronizing LTR workbook."
        ]
        assert payload["columns"] == []
        assert payload["confirmed_basic_information_version"] is None
    finally:
        app.dependency_overrides.clear()


def test_ltr_workbook_basic_information_sync_preview_api_maps_missing_ltr_to_not_found() -> None:
    app.dependency_overrides[get_ltr_workbook_basic_information_sync_service] = (
        lambda: _FakeSyncService(error="Registered LTR is required before workbook sync.")
    )
    client = TestClient(app)

    try:
        response = client.get("/api/projects/P1/ltr-workbook/basic-information-sync/preview")

        assert response.status_code == 404
        assert "Registered LTR is required" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_ltr_workbook_basic_information_sync_commit_api_maps_lock_timeout() -> None:
    app.dependency_overrides[get_ltr_workbook_basic_information_sync_service] = (
        lambda: _FakeSyncService(lock_timeout=True)
    )
    client = TestClient(app)

    try:
        response = client.post(
            "/api/projects/P1/ltr-workbook/basic-information-sync/commit",
            json={
                "operator_confirmed": True,
                "preview_acknowledged": True,
                "expected_confirmed_basic_information_version": 7,
                "expected_confirmed_basic_information_source_signature_hash": "hash-7",
            },
        )

        assert response.status_code == 409
        assert "locked" in response.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()


class _FakeSyncService:
    def __init__(
        self,
        error: str | None = None,
        lock_timeout: bool = False,
        blocked: bool = False,
    ) -> None:
        self.error = error
        self.lock_timeout = lock_timeout
        self.blocked = blocked
        self.preview_project_id = ""
        self.commit_command = None

    def preview(self, command):
        self.preview_project_id = command.project_id
        if self.error:
            raise LtrWorkbookBasicInformationSyncError(self.error)
        if self.blocked:
            return LtrWorkbookBasicInformationSyncPreview(
                project_id=command.project_id,
                ltr_number="DL-2026-05-011",
                workbook_path=None,
                target_sheet=None,
                target_row=None,
                row_data=None,
                columns=(),
                comparison_values=(),
                confirmed_basic_information_version=None,
                confirmed_basic_information_source_signature_hash=None,
                blockers=(
                    "Confirm Basic Information before synchronizing LTR workbook.",
                ),
            )
        return _preview(command.project_id)

    def commit(self, command):
        self.commit_command = command
        if self.lock_timeout:
            raise LtrWorkbookLockTimeoutError("LTR workbook is locked: test.lock")
        if self.error:
            raise LtrWorkbookBasicInformationSyncError(self.error)
        return LtrWorkbookBasicInformationSyncResult(
            project_id=command.project_id,
            ltr_number="DL-2026-05-011",
            workbook_path=Path("LTR_number.xls"),
            backup_path=Path("backups/LTR_number.xls"),
            sheet_name="2026",
            row_number=3,
            confirmed_basic_information_version=7,
            confirmed_basic_information_source_signature_hash="hash-7",
        )


def _preview(project_id: str) -> LtrWorkbookBasicInformationSyncPreview:
    row_data = LtrWorkbookRowData(
        month="May",
        total=1,
        monthly_number=11,
        dl_number="DL-2026-05-011",
        project_type="NPD",
        description_pn="Coolpower HDF 3.40mm pin",
        test_item="Qualification Testing",
        test_type="Partial Qualification",
        requested_by="MP Cao",
        location="Dongguan",
        project_leader="Even Yang",
    )
    return LtrWorkbookBasicInformationSyncPreview(
        project_id=project_id,
        ltr_number="DL-2026-05-011",
        workbook_path=Path("LTR_number.xls"),
        target_sheet="2026",
        target_row=3,
        row_data=row_data,
        columns=tuple(
            LtrWorkbookWriteColumnPreview(
                column=chr(ord("A") + index),
                field_name=field_name,
                value=value,
            )
            for index, (field_name, value) in enumerate(
                zip(
                    (
                        "month",
                        "total",
                        "monthly_number",
                        "dl_number",
                        "project_type",
                        "description_pn",
                        "test_item",
                        "test_type",
                        "requested_by",
                        "location",
                        "project_leader",
                        "test_result",
                        "failed_item",
                        "sample_deposition",
                        "sub_contract",
                        "test_fee",
                        "remarks_po",
                    ),
                    row_data.as_excel_row(),
                    strict=True,
                )
            )
        ),
        comparison_values=(
            LtrWorkbookBasicInformationSyncComparisonValue(
                field_name="project_type",
                label="Project Type",
                current_value="NPD",
                pending_value="NPD",
            ),
            LtrWorkbookBasicInformationSyncComparisonValue(
                field_name="description_pn",
                label="Description P/N",
                current_value="Old P/N",
                pending_value="Coolpower HDF 3.40mm pin",
            ),
            LtrWorkbookBasicInformationSyncComparisonValue(
                field_name="test_item",
                label="Test Item",
                current_value="Old testing",
                pending_value="Qualification Testing",
            ),
            LtrWorkbookBasicInformationSyncComparisonValue(
                field_name="test_type_in_sheet",
                label="Test Type",
                current_value="Old type",
                pending_value="Partial Qualification",
            ),
            LtrWorkbookBasicInformationSyncComparisonValue(
                field_name="test_result",
                label="Test Result",
                current_value="In progress",
                pending_value="OK",
            ),
        ),
        confirmed_basic_information_version=7,
        confirmed_basic_information_source_signature_hash="hash-7",
    )
