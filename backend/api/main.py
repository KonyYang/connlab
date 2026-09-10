"""FastAPI application for the ConnLab backend."""

import logging
import time
import uuid

from fastapi import FastAPI, Request
from backend.api.project_registry_access_guard import protect_project_mutations
from backend.api.routes_project_registry_management import router as project_registry_management_router
from backend.api.routes_project_folder_generation import router as project_folder_generation_router

from backend.api.routes_cleanup import router as cleanup_router
from backend.api.routes_approval_package import router as approval_package_router
from backend.api.routes_evidence import router as evidence_router
from backend.api.routes_external_excel_resources import (
    router as external_excel_read_router,
)
from backend.api.routes_external_resources import router as external_resources_router
from backend.api.routes_diagnostics import router as diagnostics_router
from backend.api.routes_folder import router as folder_router
from backend.api.routes_project_file_encryption import (
    router as project_file_encryption_router,
)
from backend.api.routes_intake import router as intake_router
from backend.api.routes_intake_review import router as intake_review_router
from backend.api.routes_lookup import router as lookup_router
from backend.api.routes_lookup_options import router as lookup_options_router
from backend.api.routes_ltr import router as ltr_router
from backend.api.routes_ltr_workbook import router as ltr_workbook_router
from backend.api.routes_ltr_workbook_basic_information_sync import (
    router as ltr_workbook_basic_information_sync_router,
)
from backend.api.routes_ltr_workbook_compatibility import (
    router as ltr_workbook_compatibility_router,
)
from backend.api.routes_new_project_completion import router as new_project_router
from backend.api.routes_project import router as project_router
from backend.api.routes_project_basic_information import (
    router as project_basic_information_router,
)
from backend.api.routes_project_schedule import router as project_schedule_router
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
from backend.api.routes_confirmed_matrix_llcr_cr_record_workbook import (
    router as confirmed_matrix_llcr_cr_record_workbook_router,
)
from backend.api.routes_confirmed_matrix_fee_draft import (
    router as confirmed_matrix_fee_draft_router,
)
from backend.api.routes_confirmed_matrix_fee_evaluation_export import (
    router as confirmed_matrix_fee_evaluation_export_router,
)
from backend.api.routes_fee_form_import import router as fee_form_import_router
from backend.api.routes_confirmed_matrix_fee_evaluation_pricing_draft import (
    router as confirmed_matrix_fee_evaluation_pricing_draft_router,
)
from backend.api.routes_confirmed_fee_version import (
    router as confirmed_fee_version_router,
)
from backend.api.routes_confirmed_matrix_test_record_generation import (
    router as confirmed_matrix_test_record_generation_router,
)
from backend.api.routes_test_report_draft import router as test_report_draft_router
from backend.api.routes_report_workspace import router as report_workspace_router
from backend.api.routes_confirmed_matrix_authority_history import (
    router as confirmed_matrix_authority_history_router,
)
from backend.api.routes_confirmed_matrix_active_snapshot import (
    router as confirmed_matrix_active_snapshot_router,
)
from backend.api.routes_matrix_editor_session import (
    router as matrix_editor_session_router,
)
from backend.api.routes_matrix_method_version_sync import (
    router as matrix_method_version_sync_router,
)
from backend.api.routes_matrix_editor_test_record_generation import (
    router as matrix_editor_test_record_generation_router,
)
from backend.api.routes_matrix_editor_test_status_generation import (
    router as matrix_editor_test_status_generation_router,
)
from backend.api.routes_matrix_editor_llcr_cr_record_generation import (
    router as matrix_editor_llcr_cr_record_generation_router,
)
from backend.api.routes_matrix_editor_live_xlsx_export import (
    router as matrix_editor_live_xlsx_export_router,
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
from backend.api.routes_public_folder_workflow import (
    router as public_folder_workflow_router,
)
from backend.api.routes_project_folder_required_forms import (
    router as project_folder_required_forms_router,
)
from backend.api.routes_project_application_form_write_back import (
    router as project_application_form_write_back_router,
)
from backend.api.routes_test_record_fee_dataset_preview import (
    router as test_record_fee_dataset_preview_router,
)
from backend.api.routes_test_record_fee_document_generation import (
    router as test_record_fee_document_generation_router,
)
from backend.api.routes_contact_measurement_plan import router as contact_measurement_plan_router
from backend.api.routes_contact_point_profile import router as contact_point_profile_router
from backend.api.routes_contact_measurement_plan_draft_workbook import (
    router as contact_measurement_plan_draft_workbook_router,
)


app = FastAPI(title="ConnLab API")
_request_logger = logging.getLogger("connlab.api.requests")


@app.middleware("http")
async def log_request_result(request: Request, call_next):
    """Log bounded request outcome data without query strings or request bodies."""
    request_id = uuid.uuid4().hex[:12]
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((time.perf_counter() - started) * 1000)
        _request_logger.exception(
            "request_failed request_id=%s method=%s path=%s duration_ms=%s",
            request_id,
            request.method,
            _request_route_pattern(request),
            duration_ms,
        )
        raise
    duration_ms = round((time.perf_counter() - started) * 1000)
    _request_logger.info(
        "request_complete request_id=%s method=%s path=%s status=%s duration_ms=%s",
        request_id,
        request.method,
        _request_route_pattern(request),
        response.status_code,
        duration_ms,
    )
    response.headers["X-Request-ID"] = request_id
    return response


def _request_route_pattern(request: Request) -> str:
    route = request.scope.get("route")
    return str(getattr(route, "path", request.url.path))


def _include_project_router(router):
    app.include_router(protect_project_mutations(router))


_include_project_router(project_registry_management_router)
_include_project_router(cleanup_router)
_include_project_router(approval_package_router)
_include_project_router(evidence_router)
_include_project_router(external_excel_read_router)
_include_project_router(external_resources_router)
_include_project_router(diagnostics_router)
_include_project_router(folder_router)
_include_project_router(project_file_encryption_router)
_include_project_router(intake_router)
_include_project_router(intake_review_router)
_include_project_router(lookup_router)
_include_project_router(lookup_options_router)
_include_project_router(ltr_router)
_include_project_router(ltr_workbook_router)
_include_project_router(ltr_workbook_basic_information_sync_router)
_include_project_router(ltr_workbook_compatibility_router)
_include_project_router(new_project_router)
_include_project_router(project_router)
_include_project_router(project_basic_information_router)
_include_project_router(project_schedule_router)
_include_project_router(project_test_plan_router)
_include_project_router(matrix_import_commit_router)
_include_project_router(project_test_plan_drafts_router)
_include_project_router(project_matrix_drafts_router)
_include_project_router(matrix_revisions_router)
_include_project_router(project_test_plan_matrix_edit_router)
_include_project_router(project_test_plan_source_candidates_router)
_include_project_router(runtime_projection_read_only_router)
_include_project_router(confirmed_matrix_runtime_projection_router)
_include_project_router(confirmed_matrix_test_record_preview_router)
_include_project_router(confirmed_matrix_llcr_cr_record_workbook_router)
_include_project_router(confirmed_matrix_fee_draft_router)
_include_project_router(confirmed_matrix_fee_evaluation_export_router)
_include_project_router(fee_form_import_router)
_include_project_router(confirmed_matrix_fee_evaluation_pricing_draft_router)
_include_project_router(confirmed_fee_version_router)
_include_project_router(confirmed_matrix_test_record_generation_router)
_include_project_router(test_report_draft_router)
_include_project_router(report_workspace_router)
_include_project_router(confirmed_matrix_authority_history_router)
_include_project_router(confirmed_matrix_active_snapshot_router)
_include_project_router(matrix_editor_session_router)
_include_project_router(matrix_method_version_sync_router)
_include_project_router(matrix_editor_test_record_generation_router)
_include_project_router(matrix_editor_test_status_generation_router)
_include_project_router(matrix_editor_llcr_cr_record_generation_router)
_include_project_router(matrix_editor_live_xlsx_export_router)
_include_project_router(project_output_records_router)
_include_project_router(section2_completion_preview_router)
_include_project_router(section2_write_back_router)
_include_project_router(project_section2_sync_router)
_include_project_router(customer_feedback_form_generation_router)
_include_project_router(project_package_preview_router)
_include_project_router(official_project_workspace_router)
_include_project_router(project_request_material_router)
_include_project_router(official_project_folder_check_router)
_include_project_router(public_drive_upload_router)
_include_project_router(public_folder_workflow_router)
_include_project_router(project_folder_required_forms_router)
_include_project_router(project_folder_generation_router)
_include_project_router(project_application_form_write_back_router)
_include_project_router(test_record_fee_dataset_preview_router)
_include_project_router(test_record_fee_document_generation_router)
_include_project_router(contact_measurement_plan_router)
_include_project_router(contact_point_profile_router)
_include_project_router(contact_measurement_plan_draft_workbook_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
