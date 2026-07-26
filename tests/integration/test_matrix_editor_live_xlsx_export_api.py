from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.dependencies_matrix_editor_live_xlsx_export import (
    get_matrix_editor_live_xlsx_export_service,
)
from backend.api.routes_matrix_editor_live_xlsx_export import router
from backend.application.matrix_editor_live_xlsx_export_service import (
    MatrixEditorLiveXlsxExportService,
)
from backend.infrastructure.office.matrix_editor_live_xlsx_workbook_gateway import (
    MatrixEditorLiveXlsxWorkbookGateway,
)


def payload():
    return {
        "source": "matrix_editor_current_ui_state",
        "project_reference": "DL-测试",
        "groups": [{
            "group_id": "g1", "group_key": "G1", "group_label": "Group 1",
            "sample_size": "5", "time_display": "0 d",
        }],
        "rows": [{
            "row_id": "r1", "test_item": "Item", "section": "", "test_method": "",
            "condition": "", "requirement": "",
            "cells": [{"group_id": "g1", "step_text": "1"}],
        }],
    }


def client(service=None):
    app = FastAPI()
    app.include_router(router)
    if service is not None:
        app.dependency_overrides[get_matrix_editor_live_xlsx_export_service] = lambda: service
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
