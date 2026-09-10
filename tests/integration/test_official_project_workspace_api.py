from __future__ import annotations

from pathlib import Path
import runpy

from fastapi.testclient import TestClient
import pytest

from backend.api.dependencies import get_official_project_workspace_service, get_settings
from backend.shared.config import Settings
from backend.api.main import app
from backend.api import dependencies as deps
from backend.domain import ExternalResource, ExternalResourceType, LtrRecord, LtrStatus
from backend.application.official_project_workspace_service import (
    OfficialWorkspaceConflictOption,
    OfficialWorkspaceCreateError,
    OfficialWorkspaceCreateResult,
    OfficialWorkspaceNotFoundError,
    OfficialWorkspacePreview,
    OfficialWorkspaceRecord,
)


@pytest.fixture(autouse=True)
def _isolated_generation_storage(tmp_path):
    app.dependency_overrides[get_settings] = lambda: Settings(
        data_dir=tmp_path / "data", projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates", database_path=tmp_path / "fixture.sqlite")
    yield
    app.dependency_overrides.pop(get_settings, None)


def test_real_workspace_preview_tracks_confirmations_not_basic_drafts(tmp_path):
    fixture = runpy.run_path(str(Path(__file__).with_name("test_matrix_editor_session_api.py")))
    client, engine, sessions = fixture["_client"](tmp_path)
    try:
        fixture["_seed_project"]("P1", tmp_path)
        template, output = tmp_path / "template", tmp_path / "output"
        output.mkdir()
        for name in ("E-mail", "Submitted Material", "Photos", "Test results/Final Examination"):
            (template / name).mkdir(parents=True)
        with sessions() as session:
            deps.LtrRecordRepository(session).create(
                LtrRecord("ltr", "P1", "DL-2026-08-079", LtrStatus.REGISTERED)
            )
            resources = deps.ExternalResourceRepository(session)
            resources.upsert(ExternalResource("root", ExternalResourceType.PROJECT_OUTPUT_ROOT, output))
            resources.upsert(ExternalResource("template", ExternalResourceType.PROJECT_FOLDER_TEMPLATE, template))
            session.commit()
        values = {
            "dl_number": "DL-2026-08-079", "project_type": "NPD",
            "product_description": "Confirmed connector", "test_item": "Mechanical Testing",
            "tests_to_be_performed": "Mechanical Testing",
            "requested_by": "Alice", "project_leader": "Engineer", "lab_performing_tests": "Dongguan",
        }
        response = client.post("/api/projects/P1/basic-information/confirm", json={"values": values, "confirmed_by": "operator"})
        assert response.status_code == 200, response.text

        def folder_name():
            response = client.get("/api/projects/P1/official-workspace/preview")
            assert response.status_code == 200, response.text
            return Path(response.json()["official_project_folder_path"]).name

        original = "DL-2026-08-079 Confirmed connector Mechanical Testing"
        assert folder_name() == original
        revised = {**values, "product_description": "Customized PBU Connector with 14P",
                   "test_item": "Solderability  and Mechanical Testing"}
        response = client.put("/api/projects/P1/basic-information/draft", json={"values": revised})
        assert response.status_code == 200, response.text
        assert folder_name() == original
        response = client.post("/api/projects/P1/basic-information/confirm", json={"values": revised, "confirmed_by": "operator"})
        assert response.status_code == 200, response.text
        assert folder_name() == (
            "DL-2026-08-079 Customized PBU Connector with 14P Solderability and Mechanical Testing"
        )
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_official_workspace_preview_api_returns_typed_preview() -> None:
    service = _FakeWorkspaceService(
        preview=OfficialWorkspacePreview(
            project_id="P1",
            dl_number="DL-2025-11-074",
            local_workspace_root=Path("D:/Projects"),
            local_workspace_path=Path("D:/Projects/DL-2025-11-074"),
            source_book_path=Path("D:/Projects/DL-2025-11-074/Source Book"),
            template_path=Path("D:/Template/DL-XXXX-YY-ZZZ project"),
            official_folder_path=Path("D:/Projects/DL-2025-11-074/DL-2025-11-074 Product Qualification test"),
            manifest_path=Path("D:/Projects/DL-2025-11-074/.connlab/manifest.json"),
            template_root_mode="template_root",
            status="ready",
            blockers=(),
            warnings=("Public Project locations is not configured; upload readiness will be checked later.",),
            planned_paths=(Path("D:/Projects/DL-2025-11-074"),),
            conflict_paths=(),
            conflict_options=(),
        )
    )
    app.dependency_overrides[get_official_project_workspace_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.get("/api/projects/P1/official-workspace/preview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == "P1"
    assert payload["status"] == "ready"
    assert payload["dl_number"] == "DL-2025-11-074"
    assert payload["warnings"][0].startswith("Public Project locations")
    assert payload["conflict_paths"] == []
    assert payload["conflict_options"] == []


def test_official_workspace_preview_api_returns_conflict_options() -> None:
    conflict_path = Path("D:/Projects/DL-2025-11-074/DL-2025-11-074 Product Qualification test")
    service = _FakeWorkspaceService(
        preview=OfficialWorkspacePreview(
            project_id="P1",
            dl_number="DL-2025-11-074",
            local_workspace_root=Path("D:/Projects"),
            local_workspace_path=Path("D:/Projects/DL-2025-11-074"),
            source_book_path=Path("D:/Projects/DL-2025-11-074/Source Book"),
            template_path=Path("D:/Template/DL-XXXX-YY-ZZZ project"),
            official_folder_path=conflict_path,
            manifest_path=Path("D:/Projects/DL-2025-11-074/.connlab/manifest.json"),
            template_root_mode="template_root",
            status="exists",
            blockers=(f"Official project folder already exists: {conflict_path}",),
            warnings=(),
            planned_paths=(Path("D:/Projects/DL-2025-11-074"), conflict_path),
            conflict_paths=(conflict_path,),
            conflict_options=(
                OfficialWorkspaceConflictOption(
                    key="backup_and_recreate",
                    label="Backup and Rebuild",
                    description="Move the existing folder to a timestamped backup first.",
                ),
            ),
        )
    )
    app.dependency_overrides[get_official_project_workspace_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.get("/api/projects/P1/official-workspace/preview")
    finally:
        app.dependency_overrides.clear()

    payload = response.json()
    assert response.status_code == 200
    assert payload["status"] == "exists"
    assert payload["conflict_paths"] == [str(conflict_path)]
    assert payload["conflict_options"][0]["key"] == "backup_and_recreate"


def test_official_workspace_create_api_returns_created_paths() -> None:
    record = OfficialWorkspaceRecord(
        workspace_id="W1",
        project_id="P1",
        dl_number="DL-2025-11-074",
        local_workspace_path=Path("D:/Projects/DL-2025-11-074"),
        source_book_path=Path("D:/Projects/DL-2025-11-074/Source Book"),
        official_folder_path=Path("D:/Projects/DL-2025-11-074/DL-2025-11-074 Product Qualification test"),
        manifest_path=Path("D:/Projects/DL-2025-11-074/.connlab/manifest.json"),
        template_source_path=Path("D:/Template/DL-XXXX-YY-ZZZ project"),
        created_at="2026-06-12T00:00:00+00:00",
    )
    service = _FakeWorkspaceService(
        create=OfficialWorkspaceCreateResult(
            record=record,
            created_paths=(record.local_workspace_path, record.official_folder_path),
            warnings=(),
        )
    )
    app.dependency_overrides[get_official_project_workspace_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.post(
            "/api/projects/P1/official-workspace/create",
            json={"conflict_strategy": "backup_and_recreate"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    payload = response.json()
    assert payload["workspace_id"] == "W1"
    assert payload["official_project_folder_path"].endswith("Qualification test")
    assert len(payload["created_paths"]) == 2
    assert service.created_with_strategy == "backup_and_recreate"


def test_official_workspace_create_blocked_returns_409() -> None:
    service = _FakeWorkspaceService(error=OfficialWorkspaceCreateError("Official project folder already exists"))
    app.dependency_overrides[get_official_project_workspace_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.post("/api/projects/P1/official-workspace/create")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_official_workspace_missing_project_returns_404() -> None:
    service = _FakeWorkspaceService(error=OfficialWorkspaceNotFoundError("Project not found: P404"))
    app.dependency_overrides[get_official_project_workspace_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.get("/api/projects/P404/official-workspace/preview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert "Project not found" in response.json()["detail"]


class _FakeWorkspaceService:
    def __init__(
        self,
        *,
        preview: OfficialWorkspacePreview | None = None,
        create: OfficialWorkspaceCreateResult | None = None,
        error: Exception | None = None,
    ) -> None:
        self._preview = preview
        self._create = create
        self._error = error

    def preview(self, project_id: str) -> OfficialWorkspacePreview:
        if self._error:
            raise self._error
        assert self._preview is not None
        return self._preview

    def create(
        self,
        project_id: str,
        conflict_strategy: str | None = None,
    ) -> OfficialWorkspaceCreateResult:
        if self._error:
            raise self._error
        assert self._create is not None
        self.created_with_strategy = conflict_strategy
        return self._create
