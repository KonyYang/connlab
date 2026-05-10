from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.dependencies import get_ltr_workbook_compatibility_service
from backend.api.main import app
from backend.application.ltr_workbook_compatibility_service import (
    LtrWorkbookCompatibilityNotFoundError,
    LtrWorkbookCompatibilityResult,
)


def test_ltr_workbook_compatibility_api_returns_report() -> None:
    app.dependency_overrides[get_ltr_workbook_compatibility_service] = (
        lambda: _FakeCompatibilityService()
    )
    client = TestClient(app)

    try:
        response = client.get("/api/external-resources/ltr-workbook/compatibility-baseline")

        assert response.status_code == 200
        payload = response.json()
        assert payload["compatible"] is True
        assert payload["annual_sheet_names"] == ["2026"]
    finally:
        app.dependency_overrides.clear()


def test_ltr_workbook_compatibility_api_returns_404_when_missing() -> None:
    app.dependency_overrides[get_ltr_workbook_compatibility_service] = (
        lambda: _MissingCompatibilityService()
    )
    client = TestClient(app)

    try:
        response = client.get("/api/external-resources/ltr-workbook/compatibility-baseline")

        assert response.status_code == 404
        assert "not registered" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


class _FakeCompatibilityService:
    def check(self) -> LtrWorkbookCompatibilityResult:
        return LtrWorkbookCompatibilityResult(
            compatible=True,
            resource_path=str(Path("D:/Public/LTR.XLS")),
            extension=".xls",
            workbook_open_read_ok=True,
            workbook_read_only=True,
            sheet_names=("2026",),
            annual_sheet_names=("2026",),
            write_enabled=True,
            modify_password_configured=True,
            lock_dir_configured=True,
            backup_dir_configured=True,
            blockers=(),
            notes=(f"checked_at:{datetime.now().isoformat()}",),
        )


class _MissingCompatibilityService:
    def check(self) -> LtrWorkbookCompatibilityResult:
        raise LtrWorkbookCompatibilityNotFoundError(
            "External resource is not registered: ltr_workbook"
        )
