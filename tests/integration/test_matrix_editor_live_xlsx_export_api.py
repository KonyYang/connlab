from fastapi import FastAPI
from fastapi.testclient import TestClient
from pathlib import Path
from types import SimpleNamespace

from backend.api.dependencies_matrix_editor_live_xlsx_export import (
    get_matrix_editor_live_xlsx_export_service,
    get_matrix_editor_live_xlsx_publication_service,
)
from backend.api.routes_matrix_editor_live_xlsx_export import router
from backend.application.matrix_editor_live_xlsx_export_service import (
    MatrixEditorLiveXlsxExportService,
)
from backend.application.matrix_editor_live_xlsx_publication_service import (
    ExecuteMatrixEditorLiveXlsxPublicationCommand,
    PreviewMatrixEditorLiveXlsxPublicationCommand,
)
from backend.shared.config import Settings
from backend.infrastructure.office.matrix_editor_live_xlsx_workbook_gateway import (
    MatrixEditorLiveXlsxWorkbookGateway,
)


def payload():
    return {
        "source": "matrix_editor_current_ui_state",
        "project_reference": "DL-测试",
        "groups": [{
            "group_id": "g1", "group_key": "G1", "group_label": "Group 1",
            "sample_size": "5", "time_display": "0 d", "sample_note": "Reserve",
        }],
        "rows": [{
            "row_id": "r1", "test_item": "Item", "section": "", "test_method": "",
            "condition": "", "requirement": "",
            "day_expression": "2.5x",
            "cells": [{"group_id": "g1", "step_text": "1"}],
        }],
        "schedule": {"post_test_buffer_days": "2"},
    }


def client(service=None, publication_service=None, settings=None):
    app = FastAPI()
    app.include_router(router)
    if service is not None:
        app.dependency_overrides[get_matrix_editor_live_xlsx_export_service] = lambda: service
    if publication_service is not None:
        app.dependency_overrides[get_matrix_editor_live_xlsx_publication_service] = (
            lambda: publication_service
        )
    if settings is not None:
        from backend.api.routes_matrix_editor_live_xlsx_export import get_settings

        app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app)


def test_live_xlsx_api_returns_bytes_and_utf8_content_disposition():
    service = MatrixEditorLiveXlsxExportService(MatrixEditorLiveXlsxWorkbookGateway())
    response = client(service).post("/api/projects/p1/matrix-editor/live-xlsx-export", json=payload())
    assert response.status_code == 200
    assert response.content.startswith(b"PK")
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert "filename*=UTF-8''DL-%E6%B5%8B%E8%AF%95" in response.headers["content-disposition"]


def test_live_xlsx_api_returns_typed_422_for_zero_rows():
    invalid = payload()
    invalid["rows"] = []
    response = client(
        MatrixEditorLiveXlsxExportService(MatrixEditorLiveXlsxWorkbookGateway())
    ).post("/api/projects/p1/matrix-editor/live-xlsx-export", json=invalid)
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "matrix_editor_live_xlsx_export_blocked"
    assert response.content.startswith(b'{"detail"')


def test_publication_routes_preserve_preview_and_conflict_choice(tmp_path: Path):
    publication = _PublicationService()
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "data" / "connlab.sqlite3",
    )
    api = client(publication_service=publication, settings=settings)

    preview_response = api.post(
        "/api/projects/p1/matrix-editor/live-xlsx-export/publication/preview",
        json=payload(),
    )
    publish_response = api.post(
        "/api/projects/p1/matrix-editor/live-xlsx-export/publication/publish",
        json={
            **payload(),
            "preview_token": "preview-token",
            "conflict_action": "archive",
        },
    )

    assert preview_response.status_code == 200
    assert preview_response.json() == {
        "mode": "official",
        "status": "conflict",
        "existing_file": True,
        "existing_modified_at": "2026-08-29T10:00:00+08:00",
        "blockers": [],
        "preview_token": "preview-token",
    }
    assert isinstance(publication.preview_commands[0], PreviewMatrixEditorLiveXlsxPublicationCommand)
    assert publication.preview_commands[0].request.groups[0].sample_note == "Reserve"
    assert publication.preview_commands[0].request.rows[0].day_expression == "2.5x"
    assert publication.preview_commands[0].request.schedule.post_test_buffer_days == "2"
    assert publish_response.status_code == 200
    assert publish_response.json() == {
        "file_name": "DL-测试 Matrix.xlsx",
        "archive_path": str(Path("D:/Projects/DL-测试/History/Matrix/old.xlsx")),
    }
    assert isinstance(publication.execute_commands[0], ExecuteMatrixEditorLiveXlsxPublicationCommand)
    assert publication.execute_commands[0].conflict_action == "archive"
    assert publication.execute_commands[0].staging_dir == (
        settings.data_dir / "generated_matrix_publications"
    )


class _PublicationService:
    def __init__(self) -> None:
        self.preview_commands = []
        self.execute_commands = []

    def preview(self, command):
        self.preview_commands.append(command)
        return SimpleNamespace(
            mode="official",
            status="conflict",
            existing_file=True,
            existing_modified_at="2026-08-29T10:00:00+08:00",
            blockers=(),
            preview_token="preview-token",
        )

    def execute(self, command):
        self.execute_commands.append(command)
        return SimpleNamespace(
            file_name="DL-测试 Matrix.xlsx",
            archive_path=Path("D:/Projects/DL-测试/History/Matrix/old.xlsx"),
        )
