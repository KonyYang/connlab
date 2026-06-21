from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.dependencies import get_project_request_material_collection_service
from backend.api.main import app
from backend.application.project_request_material_collection_service import (
    ProjectRequestMaterialCollectionConflictError,
    RequestMaterialCollectResult,
    RequestMaterialPreview,
    RequestMaterialPreviewItem,
)


def test_request_material_preview_api_returns_business_state() -> None:
    service = _FakeRequestMaterialService(
        preview=_preview(status="partial", warnings=("Request email missing",))
    )
    app.dependency_overrides[get_project_request_material_collection_service] = lambda: service
    try:
        response = TestClient(app).get("/api/projects/P1/request-material/preview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "partial"
    assert payload["warnings"] == ["Request email missing"]
    assert payload["items"][0]["target_area"] == "submitted_material"


def test_request_material_collect_api_maps_conflict_to_409() -> None:
    service = _FakeRequestMaterialService(
        error=ProjectRequestMaterialCollectionConflictError("Target file conflict")
    )
    app.dependency_overrides[get_project_request_material_collection_service] = lambda: service
    try:
        response = TestClient(app).post("/api/projects/P1/request-material/collect")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json()["detail"] == "Target file conflict"


def test_request_material_collect_api_returns_workspace_context() -> None:
    service = _FakeRequestMaterialService()
    app.dependency_overrides[get_project_request_material_collection_service] = lambda: service
    try:
        response = TestClient(app).post("/api/projects/P1/request-material/collect")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["collection_id"] == "collection-1"
    assert payload["local_workspace_path"] == "workspace"
    assert payload["source_book_path"] == "workspace\\Source Book"
    assert payload["official_project_folder_path"] == "workspace\\Official"
    assert payload["copied_paths"] == ["target\\application.docx"]


class _FakeRequestMaterialService:
    def __init__(
        self,
        *,
        preview: RequestMaterialPreview | None = None,
        collect: RequestMaterialCollectResult | None = None,
        error: Exception | None = None,
    ) -> None:
        self._preview = preview or _preview()
        self._collect = collect or _collect()
        self._error = error

    def preview(self, project_id: str) -> RequestMaterialPreview:
        if self._error:
            raise self._error
        return self._preview

    def collect(self, project_id: str) -> RequestMaterialCollectResult:
        if self._error:
            raise self._error
        return self._collect


def _item(status: str = "planned") -> RequestMaterialPreviewItem:
    return RequestMaterialPreviewItem(
        source_asset_id="asset-1",
        source_asset_type="application_form",
        source_role="selected_application_form",
        source_name="application.docx",
        source_path=Path("source/application.docx"),
        dedupe_key="path:source/application.docx",
        target_area="submitted_material",
        target_path=Path("target/application.docx"),
        action="copy",
        status=status,
        message="Ready to copy.",
        review_required=False,
        size_bytes=10,
        sha256="a" * 64,
    )


def _preview(
    *,
    status: str = "ready",
    warnings: tuple[str, ...] = tuple(),
) -> RequestMaterialPreview:
    return RequestMaterialPreview(
        project_id="P1",
        local_workspace_path=Path("workspace"),
        source_book_path=Path("workspace/Source Book"),
        official_project_folder_path=Path("workspace/Official"),
        status=status,
        items=(_item(),),
        blockers=tuple(),
        warnings=warnings,
    )


def _collect() -> RequestMaterialCollectResult:
    return RequestMaterialCollectResult(
        project_id="P1",
        local_workspace_path=Path("workspace"),
        source_book_path=Path("workspace/Source Book"),
        official_project_folder_path=Path("workspace/Official"),
        collection_id="collection-1",
        status="collected",
        items=(_item("copied"),),
        copied_paths=(Path("target/application.docx"),),
        already_present_paths=tuple(),
        skipped_paths=tuple(),
        missing_source_paths=tuple(),
        conflict_paths=tuple(),
        blockers=tuple(),
        warnings=tuple(),
    )
