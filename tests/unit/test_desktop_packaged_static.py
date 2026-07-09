from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.desktop.packaged_static import mount_packaged_frontend


def test_packaged_frontend_serves_assets_and_spa_fallback(tmp_path: Path) -> None:
    """Packaged FastAPI app serves built frontend files and React routes."""
    frontend = tmp_path / "frontend_dist"
    assets = frontend / "assets"
    assets.mkdir(parents=True)
    (frontend / "index.html").write_text("<main>ConnLab shell</main>", encoding="utf-8")
    (assets / "app.js").write_text("console.log('connlab');", encoding="utf-8")

    app = FastAPI()
    mount_packaged_frontend(app, frontend)
    client = TestClient(app)

    index_response = client.get("/")
    asset_response = client.get("/assets/app.js")
    route_response = client.get("/projects/abc/workbench")

    assert index_response.status_code == 200
    assert "ConnLab shell" in index_response.text
    assert asset_response.status_code == 200
    assert "connlab" in asset_response.text
    assert route_response.status_code == 200
    assert "ConnLab shell" in route_response.text


def test_packaged_frontend_requires_index_html(tmp_path: Path) -> None:
    """A release without built index.html fails early with a clear error."""
    app = FastAPI()

    try:
        mount_packaged_frontend(app, tmp_path / "missing-dist")
    except FileNotFoundError as exc:
        assert "index.html" in str(exc)
    else:
        raise AssertionError("missing packaged frontend did not fail")


def test_packaged_frontend_does_not_swallow_unknown_api_routes(tmp_path: Path) -> None:
    """Unknown API routes must remain API 404s instead of returning index.html."""
    frontend = tmp_path / "frontend_dist"
    frontend.mkdir(parents=True)
    (frontend / "index.html").write_text("<main>ConnLab shell</main>", encoding="utf-8")

    app = FastAPI()
    mount_packaged_frontend(app, frontend)
    response = TestClient(app).get("/api/does-not-exist")

    assert response.status_code == 404
    assert "ConnLab shell" not in response.text
