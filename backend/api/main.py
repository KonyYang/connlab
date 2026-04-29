"""FastAPI application for the ConnLab backend."""

from fastapi import FastAPI

from backend.api.routes_evidence import router as evidence_router
from backend.api.routes_folder import router as folder_router
from backend.api.routes_intake import router as intake_router
from backend.api.routes_lookup import router as lookup_router
from backend.api.routes_ltr import router as ltr_router
from backend.api.routes_project import router as project_router


app = FastAPI(title="ConnLab API")
app.include_router(evidence_router)
app.include_router(folder_router)
app.include_router(intake_router)
app.include_router(lookup_router)
app.include_router(ltr_router)
app.include_router(project_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
