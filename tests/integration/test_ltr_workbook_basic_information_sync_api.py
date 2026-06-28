from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.dependencies import get_ltr_workbook_basic_information_sync_service
from backend.api.main import app
from backend.application.ltr_workbook_basic_information_sync_service import (
    LtrWorkbookBasicInformationSyncError,
    LtrWorkbookBasicInformationSyncComparisonValue,
    LtrWorkbookBasicInformationSyncPreview,
    LtrWorkbookBasicInformationReadonlyOpenResult,
    LtrWorkbookBasicInformationSyncResult,
)
from backend.application.ltr_workbook_write_preview_service import (
    LtrWorkbookWriteColumnPreview,
)
from backend.application.project_lifecycle_write_guard import (
    ProjectLifecycleReadonlyError,
    ProjectLifecycleWriteGuardNotFoundError,
)
from backend.domain import ProjectClosureType, ProjectLifecycleState
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
            "changed": True,
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


def test_ltr_workbook_basic_information_sync_commit_stopped_returns_structured_409_without_mutation() -> None:
    service = _FakeSyncService(lifecycle_state=ProjectLifecycleState.STOPPED)
    app.dependency_overrides[get_ltr_workbook_basic_information_sync_service] = lambda: service
    client = TestClient(app, raise_server_exceptions=False)

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
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == "project_lifecycle_readonly"
    assert detail["project_id"] == "P1"
    assert detail["lifecycle_state"] == "stopped"
    assert detail["closure_type"] is None
    assert detail["close_reason_category"] is None
    assert detail["close_reason_label"] is None
    assert detail["message"] == "This project is stopped. Activate it before making changes."
    assert detail["allowed_actions"] == ["activate"]
    assert service.commit_command is None


def test_ltr_workbook_basic_information_sync_commit_closed_returns_structured_409_without_mutation() -> None:
    service = _FakeSyncService(
        lifecycle_state=ProjectLifecycleState.CLOSED,
        closure_type=ProjectClosureType.COMPLETED,
    )
    app.dependency_overrides[get_ltr_workbook_basic_information_sync_service] = lambda: service
    client = TestClient(app, raise_server_exceptions=False)

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
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == "project_lifecycle_readonly"
    assert detail["lifecycle_state"] == "closed"
    assert detail["closure_type"] == "completed"
    assert detail["close_reason_category"] == "completed"
    assert detail["close_reason_label"] == "Completed"
    assert detail["message"] == "This project is closed. Activate it before making changes."
    assert detail["allowed_actions"] == ["activate"]
    assert service.commit_command is None


def test_ltr_workbook_basic_information_sync_commit_lifecycle_guard_missing_maps_to_404() -> None:
    service = _FakeSyncService(lifecycle_guard_not_found=True)
    app.dependency_overrides[get_ltr_workbook_basic_information_sync_service] = lambda: service
    client = TestClient(app, raise_server_exceptions=False)

    try:
        response = client.post(
            "/api/projects/NOPE/ltr-workbook/basic-information-sync/commit",
            json={
                "operator_confirmed": True,
                "preview_acknowledged": True,
                "expected_confirmed_basic_information_version": 7,
                "expected_confirmed_basic_information_source_signature_hash": "hash-7",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found: NOPE"
    assert service.commit_command is None


def test_ltr_workbook_basic_information_sync_open_readonly_api_returns_selected_cell() -> None:
    fake = _FakeSyncService()
    app.dependency_overrides[get_ltr_workbook_basic_information_sync_service] = lambda: fake
    client = TestClient(app)

    try:
        response = client.post(
            "/api/projects/P1/ltr-workbook/basic-information-sync/open-readonly"
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["project_id"] == "P1"
        assert payload["ltr_number"] == "DL-2026-05-011"
        assert payload["workbook_path"] == "LTR_number.xls"
        assert payload["sheet_name"] == "2026"
        assert payload["row_number"] == 3
        assert payload["column_number"] == 4
        assert payload["selected_cell"] == "D3"
        assert fake.open_command.project_id == "P1"
    finally:
        app.dependency_overrides.clear()


def test_ltr_workbook_basic_information_sync_open_readonly_api_maps_open_workbook_to_conflict() -> None:
    app.dependency_overrides[get_ltr_workbook_basic_information_sync_service] = (
        lambda: _FakeSyncService(
            error="The LTR workbook is already open in Excel. Close it and retry."
        )
    )
    client = TestClient(app)

    try:
        response = client.post(
            "/api/projects/P1/ltr-workbook/basic-information-sync/open-readonly"
        )

        assert response.status_code == 409
        assert "already open" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


class _FakeSyncService:
    def __init__(
        self,
        error: str | None = None,
        lock_timeout: bool = False,
        blocked: bool = False,
        lifecycle_state: ProjectLifecycleState | None = None,
        closure_type: ProjectClosureType | None = None,
        lifecycle_guard_not_found: bool = False,
    ) -> None:
        self.error = error
        self.lock_timeout = lock_timeout
        self.blocked = blocked
        self.lifecycle_state = lifecycle_state
        self.closure_type = closure_type
        self.lifecycle_guard_not_found = lifecycle_guard_not_found
        self.preview_project_id = ""
        self.commit_command = None
        self.open_command = None

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
        if self.lifecycle_guard_not_found:
            raise ProjectLifecycleWriteGuardNotFoundError(
                f"Project not found: {command.project_id}"
            )
        if self.lifecycle_state is not None:
            raise ProjectLifecycleReadonlyError(
                project_id=command.project_id,
                lifecycle_state=self.lifecycle_state,
                closure_type=self.closure_type,
                message=_lifecycle_message(self.lifecycle_state, self.closure_type),
                allowed_actions=(
                    ("activate",)
                    if self.lifecycle_state is not ProjectLifecycleState.ACTIVE
                    else ()
                ),
            )
        if self.lock_timeout:
            raise LtrWorkbookLockTimeoutError("LTR workbook is locked: test.lock")
        if self.error:
            raise LtrWorkbookBasicInformationSyncError(self.error)
        self.commit_command = command
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

    def open_readonly_at_ltr(self, command):
        self.open_command = command
        if self.lock_timeout:
            raise LtrWorkbookLockTimeoutError("LTR workbook is locked: test.lock")
        if self.error:
            raise LtrWorkbookBasicInformationSyncError(self.error)
        return LtrWorkbookBasicInformationReadonlyOpenResult(
            project_id=command.project_id,
            ltr_number="DL-2026-05-011",
            workbook_path=Path("LTR_number.xls"),
            sheet_name="2026",
            row_number=3,
            column_number=4,
            selected_cell="D3",
            message="Opened LTR workbook read-only at D3.",
        )


def _lifecycle_message(
    lifecycle_state: ProjectLifecycleState,
    closure_type: ProjectClosureType | None,
) -> str:
    if lifecycle_state is ProjectLifecycleState.STOPPED:
        return "This project is stopped. Activate it before making changes."
    return "This project is closed. Activate it before making changes."


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
                changed=False,
            ),
            LtrWorkbookBasicInformationSyncComparisonValue(
                field_name="description_pn",
                label="Description P/N",
                current_value="Old P/N",
                pending_value="Coolpower HDF 3.40mm pin",
                changed=True,
            ),
            LtrWorkbookBasicInformationSyncComparisonValue(
                field_name="test_item",
                label="Test Item",
                current_value="Old testing",
                pending_value="Qualification Testing",
                changed=True,
            ),
            LtrWorkbookBasicInformationSyncComparisonValue(
                field_name="test_type_in_sheet",
                label="Test Type",
                current_value="Old type",
                pending_value="Partial Qualification",
                changed=True,
            ),
            LtrWorkbookBasicInformationSyncComparisonValue(
                field_name="test_result",
                label="Test Result",
                current_value="In progress",
                pending_value="OK",
                changed=True,
            ),
        ),
        confirmed_basic_information_version=7,
        confirmed_basic_information_source_signature_hash="hash-7",
    )
