"""Static frontend mounting for the ConnLab packaged desktop runtime."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles


def mount_packaged_frontend(app: FastAPI, frontend_dist: Path) -> None:
    """Serve built React files and fall back to index.html for SPA routes."""
    dist = frontend_dist.resolve()
    index_path = dist / "index.html"
    if not index_path.is_file():
        raise FileNotFoundError(f"Packaged frontend index.html not found: {index_path}")

    assets_path = dist / "assets"
    if assets_path.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_path), name="packaged-assets")

    @app.get("/", include_in_schema=False)
    def packaged_frontend_index() -> FileResponse:
        """Return the packaged React application entry point."""
        return FileResponse(index_path)

    @app.get("/{full_path:path}", include_in_schema=False)
    def packaged_frontend_route(full_path: str) -> FileResponse:
        """Return static files when present, otherwise the React SPA entry."""
        if full_path == "api" or full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found.")
        candidate = (dist / full_path).resolve()
        if dist in candidate.parents and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(index_path)
