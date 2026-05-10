from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.dependencies import get_ltr_workbook_write_commit_service
from backend.api.main import app
from backend.application.ltr_workbook_write_commit_service import (
    LtrWorkbookWriteCommitError,
    LtrWorkbookWriteCommitResult,
)
from backend.domain import LtrRecord, LtrStatus
from backend.infrastructure.office import LtrWorkbookRowPointer
from backend.infrastructure.office import LtrWorkbookLockTimeoutError


def test_ltr_workbook_write_commit_api_requires_service_confirmation_contract() -> None:
    """The commit API delegates to the commit service and returns write metadata."""
    fake = _FakeCommitService()
    app.dependency_overrides[get_ltr_workbook_write_commit_service] = lambda: fake
    client = TestClient(app)

    try:
        response = client.post(
            "/api/projects/P1/ltr-workbook/write-commit",
            json={
                "plan_date": "2026-05-07",
                "operator_confirmed": True,
                "preview_acknowledged": True,
                "allow_year_sheet_bootstrap": True,
                "number_input": "A9",
                "test_item": "Qualification bend testing",
                "sample_description": "CoolPower connector samples",
                "location": "AIPG Guangzhou",
                "test_type_in_sheet": "Qualification",
                "project_leader": "Alice",
                "requested_by": "Alice",
            },
        )

        assert response.status_code == 201
        payload = response.json()
        assert payload["action"] == "append_auto_suffix"
        assert payload["sheet_name"] == "2026"
        assert payload["row_number"] == 3
        assert payload["ltr_number"] == "DL-2026-05-002A9"
        assert fake.received_project_id == "P1"
        assert fake.received_command.preview_acknowledged is True
        assert fake.received_command.allow_year_sheet_bootstrap is True
    finally:
        app.dependency_overrides.clear()


def test_ltr_workbook_write_commit_api_returns_business_error() -> None:
    """Commit service validation errors are returned as HTTP 400."""
    app.dependency_overrides[get_ltr_workbook_write_commit_service] = (
        lambda: _FakeCommitService(error="Operator confirmation is required.")
    )
    client = TestClient(app)

    try:
        response = client.post(
            "/api/projects/P1/ltr-workbook/write-commit",
            json={
                "plan_date": "2026-05-07",
                "operator_confirmed": False,
                "preview_acknowledged": True,
                "test_item": "Qualification bend testing",
                "sample_description": "CoolPower connector samples",
                "location": "AIPG Guangzhou",
                "test_type_in_sheet": "Qualification",
                "project_leader": "Alice",
            },
        )

        assert response.status_code == 400
        assert "Operator confirmation" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_ltr_workbook_write_commit_api_returns_conflict_for_lock_timeout() -> None:
    """Lock-timeout errors are returned as HTTP 409 conflict."""
    app.dependency_overrides[get_ltr_workbook_write_commit_service] = (
        lambda: _FakeCommitService(lock_timeout=True)
    )
    client = TestClient(app)

    try:
        response = client.post(
            "/api/projects/P1/ltr-workbook/write-commit",
            json={
                "plan_date": "2026-05-07",
                "operator_confirmed": True,
                "preview_acknowledged": True,
                "test_item": "Qualification bend testing",
                "sample_description": "CoolPower connector samples",
                "location": "AIPG Guangzhou",
                "test_type_in_sheet": "Qualification",
                "project_leader": "Alice",
            },
        )

        assert response.status_code == 409
        assert "locked" in response.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()


class _FakeCommitService:
    def __init__(self, error: str | None = None, lock_timeout: bool = False) -> None:
        self.error = error
        self.lock_timeout = lock_timeout
        self.received_project_id = ""
        self.received_command = None

    def commit_project(self, project_id: str, command):
        self.received_project_id = project_id
        self.received_command = command
        if self.lock_timeout:
            raise LtrWorkbookLockTimeoutError("LTR workbook is locked: test.lock")
        if self.error:
            raise LtrWorkbookWriteCommitError(self.error)
        ltr = LtrRecord(
            ltr_id="L1",
            project_id=project_id,
            ltr_number="DL-2026-05-002A9",
            status=LtrStatus.REGISTERED,
            registered_on=date(2026, 5, 7),
            requested_by=command.requested_by,
            requested_date=command.requested_date,
        )
        return LtrWorkbookWriteCommitResult(
            ltr=ltr,
            pointer=LtrWorkbookRowPointer(
                sheet_name="2026",
                row_number=3,
                dl_number="DL-2026-05-002A9",
            ),
            action="append_auto_suffix",
            workbook_path=Path("LTR_number.xls"),
            backup_path=Path("backups/LTR_number.xls"),
            ltr_number="DL-2026-05-002A9",
        )
