"""FastAPI application for the ConnLab backend."""

from fastapi import FastAPI

from backend.api.routes_cleanup import router as cleanup_router
from backend.api.routes_approval_package import router as approval_package_router
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
from backend.api.routes_project_test_plan import router as project_test_plan_router
from backend.api.routes_matrix_import_commit import router as matrix_import_commit_router
from backend.api.routes_project_test_plan_drafts import (
    router as project_test_plan_drafts_router,
)
from backend.api.routes_project_matrix_drafts import (
    router as project_matrix_drafts_router,
)
from backend.api.routes_matrix_revisions import (
    router as matrix_revisions_router,
)
from backend.api.routes_project_test_plan_matrix_edit import (
    router as project_test_plan_matrix_edit_router,
)
from backend.api.routes_project_test_plan_source_candidates import (
    router as project_test_plan_source_candidates_router,
)
from backend.api.routes_runtime_projection_read_only import (
    router as runtime_projection_read_only_router,
)
from backend.api.routes_confirmed_matrix_runtime_projection import (
    router as confirmed_matrix_runtime_projection_router,
)
from backend.api.routes_confirmed_matrix_test_record_preview import (
    router as confirmed_matrix_test_record_preview_router,
)
from backend.api.routes_confirmed_matrix_fee_draft import (
    router as confirmed_matrix_fee_draft_router,
)
from backend.api.routes_confirmed_matrix_fee_evaluation_export import (
    router as confirmed_matrix_fee_evaluation_export_router,
)
from backend.api.routes_confirmed_matrix_fee_evaluation_pricing_draft import (
    router as confirmed_matrix_fee_evaluation_pricing_draft_router,
)
from backend.api.routes_confirmed_fee_version import (
    router as confirmed_fee_version_router,
)
from backend.api.routes_confirmed_matrix_test_record_generation import (
    router as confirmed_matrix_test_record_generation_router,
)
from backend.api.routes_confirmed_matrix_authority_history import (
    router as confirmed_matrix_authority_history_router,
)
from backend.api.routes_confirmed_matrix_active_snapshot import (
    router as confirmed_matrix_active_snapshot_router,
)
from backend.api.routes_matrix_editor_session import (
    router as matrix_editor_session_router,
)
from backend.api.routes_matrix_editor_test_record_generation import (
    router as matrix_editor_test_record_generation_router,
)
from backend.api.routes_project_output_records import (
    router as project_output_records_router,
)
from backend.api.routes_section2_completion_preview import (
    router as section2_completion_preview_router,
)
from backend.api.routes_section2_write_back import (
    router as section2_write_back_router,
)
from backend.api.routes_project_section2_sync import (
    router as project_section2_sync_router,
)
from backend.api.routes_customer_feedback_form_generation import (
    router as customer_feedback_form_generation_router,
)
from backend.api.routes_project_package_preview import (
    router as project_package_preview_router,
)
from backend.api.routes_official_project_workspace import (
    router as official_project_workspace_router,
)
from backend.api.routes_project_request_material import (
    router as project_request_material_router,
)
from backend.api.routes_official_project_folder_check import (
    router as official_project_folder_check_router,
)
from backend.api.routes_public_drive_upload import (
    router as public_drive_upload_router,
)
from backend.api.routes_test_record_fee_dataset_preview import (
    router as test_record_fee_dataset_preview_router,
)
from backend.api.routes_test_record_fee_document_generation import (
    router as test_record_fee_document_generation_router,
)


app = FastAPI(title="ConnLab API")
app.include_router(cleanup_router)
app.include_router(approval_package_router)
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
app.include_router(project_test_plan_router)
app.include_router(matrix_import_commit_router)
app.include_router(project_test_plan_drafts_router)
app.include_router(project_matrix_drafts_router)
app.include_router(matrix_revisions_router)
app.include_router(project_test_plan_matrix_edit_router)
app.include_router(project_test_plan_source_candidates_router)
app.include_router(runtime_projection_read_only_router)
app.include_router(confirmed_matrix_runtime_projection_router)
app.include_router(confirmed_matrix_test_record_preview_router)
app.include_router(confirmed_matrix_fee_draft_router)
app.include_router(confirmed_matrix_fee_evaluation_export_router)
app.include_router(confirmed_matrix_fee_evaluation_pricing_draft_router)
app.include_router(confirmed_fee_version_router)
app.include_router(confirmed_matrix_test_record_generation_router)
app.include_router(confirmed_matrix_authority_history_router)
app.include_router(confirmed_matrix_active_snapshot_router)
app.include_router(matrix_editor_session_router)
app.include_router(matrix_editor_test_record_generation_router)
app.include_router(project_output_records_router)
app.include_router(section2_completion_preview_router)
app.include_router(section2_write_back_router)
app.include_router(project_section2_sync_router)
app.include_router(customer_feedback_form_generation_router)
app.include_router(project_package_preview_router)
app.include_router(official_project_workspace_router)
app.include_router(project_request_material_router)
app.include_router(official_project_folder_check_router)
app.include_router(public_drive_upload_router)
app.include_router(test_record_fee_dataset_preview_router)
app.include_router(test_record_fee_document_generation_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
