"""FastAPI application for the ConnLab backend."""

from fastapi import FastAPI

from backend.api.routes_cleanup import router as cleanup_router
from backend.api.routes_evidence import router as evidence_router
from backend.api.routes_external_excel_resources import (
    router as external_excel_read_router,
)
from backend.api.routes_external_resources import router as external_resources_router
from backend.api.routes_folder import router as folder_router
from backend.api.routes_intake import router as intake_router
from backend.api.routes_intake_review import router as intake_review_router
from backend.api.routes_lookup import router as lookup_router
from backend.api.routes_lookup_options import router as lookup_options_router
from backend.api.routes_ltr import router as ltr_router
from backend.api.routes_ltr_workbook import router as ltr_workbook_router
from backend.api.routes_ltr_workbook_compatibility import (
    router as ltr_workbook_compatibility_router,
)
from backend.api.routes_new_project_completion import router as new_project_router
from backend.api.routes_project import router as project_router


app = FastAPI(title="ConnLab API")
app.include_router(cleanup_router)
app.include_router(evidence_router)
app.include_router(external_excel_read_router)
app.include_router(external_resources_router)
app.include_router(folder_router)
app.include_router(intake_router)
app.include_router(intake_review_router)
app.include_router(lookup_router)
app.include_router(lookup_options_router)
app.include_router(ltr_router)
app.include_router(ltr_workbook_router)
app.include_router(ltr_workbook_compatibility_router)
app.include_router(new_project_router)
app.include_router(project_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
