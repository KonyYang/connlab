"""FastAPI application for the ConnLab backend."""

from fastapi import FastAPI

from backend.api.routes_project import router as project_router


app = FastAPI(title="ConnLab API")
app.include_router(project_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
