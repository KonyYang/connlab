"""
Pack Project Workbench and Matrix Edit related code files into a zip archive.
"""
from pathlib import Path
import zipfile


REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_ZIP = REPO_ROOT / "ProjectWorkbench_MatrixEdit_Code.zip"

# Files to include
FILES_TO_PACK = [
    # Frontend - Pages
    "frontend/src/pages/ProjectWorkbenchPage.tsx",
    # Frontend - Features (project-workbench)
    "frontend/src/features/project-workbench/ProjectFolderCreationPanel.tsx",
    "frontend/src/features/project-workbench/ProjectWorkbenchDocumentStatusPanel.tsx",
    "frontend/src/features/project-workbench/ProjectWorkbenchEvidencePanel.tsx",
    "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
    "frontend/src/features/project-workbench/ProjectWorkbenchMatrixAuthorityBar.tsx",
    "frontend/src/features/project-workbench/ProjectWorkbenchMatrixInspector.tsx",
    "frontend/src/features/project-workbench/ProjectWorkbenchMatrixOverview.tsx",
    "frontend/src/features/project-workbench/ProjectWorkbenchMatrixReviewPanel.tsx",
    "frontend/src/features/project-workbench/ProjectWorkbenchMatrixStarter.tsx",
    "frontend/src/features/project-workbench/projectFolderResourceSelectors.ts",
    "frontend/src/features/project-workbench/projectWorkbenchMatrixHelpers.ts",
    "frontend/src/features/project-workbench/projectWorkbenchVersionSelectors.ts",
    "frontend/src/features/project-workbench/useProjectWorkbenchModel.ts",
    # Frontend - Components (workflow)
    "frontend/src/components/workflow/ApprovalPackagePanel.tsx",
    # Frontend - Styles
    "frontend/src/styles.css",
    "frontend/src/workbench.css",
    # Frontend - Layout
    "frontend/src/components/layout/AppShell.tsx",
    "frontend/src/components/layout/Sidebar.tsx",
    "frontend/src/components/layout/TopBar.tsx",
    # Frontend - API client
    "frontend/src/api/client.ts",
    # Backend - API routes
    "backend/api/routes_project_test_plan_matrix_edit.py",
    "backend/api/routes_project_test_plan.py",
    "backend/api/routes_project_test_plan_drafts.py",
    "backend/api/routes_project_test_plan_source_candidates.py",
    "backend/api/routes_project_output_records.py",
    "backend/api/routes_section2_completion_preview.py",
    "backend/api/routes_section2_write_back.py",
    "backend/api/routes_test_record_fee_dataset_preview.py",
    "backend/api/routes_test_record_fee_document_generation.py",
    "backend/api/routes_approval_package.py",
    "backend/api/routes_folder.py",
    "backend/api/routes_lookup.py",
    "backend/api/routes_lookup_options.py",
    "backend/api/dependencies.py",
    "backend/api/main.py",
    # Backend - Application services
    "backend/application/project_test_plan_matrix_edit_service.py",
    "backend/application/project_test_plan_draft_service.py",
    "backend/application/project_test_plan_matrix_preview_service.py",
    "backend/application/project_test_plan_source_candidate_service.py",
    "backend/application/project_output_record_service.py",
    "backend/application/section2_completion_preview_service.py",
    "backend/application/section2_write_back_service.py",
    "backend/application/test_record_fee_dataset_preview_service.py",
    "backend/application/test_record_fee_document_generation_service.py",
    "backend/application/approval_package_service.py",
    "backend/application/folder_service.py",
    "backend/application/lookup_service.py",
    "backend/application/lookup_options_service.py",
    # Backend - Domain
    "backend/domain/enums.py",
    "backend/domain/models.py",
    # Backend - Infrastructure (storage)
    "backend/infrastructure/storage/__init__.py",
    "backend/infrastructure/storage/repositories.py",
    # Backend - Tests (integration)
    "tests/integration/test_project_test_plan_matrix_edit_api.py",
    "tests/integration/test_project_test_plan_draft_api.py",
    "tests/integration/test_project_test_plan_preview_api.py",
    "tests/integration/test_project_test_plan_source_candidates_api.py",
    "tests/integration/test_project_output_records_api.py",
    "tests/integration/test_section2_completion_preview_api.py",
    "tests/integration/test_section2_write_back_api.py",
    "tests/integration/test_test_record_fee_dataset_preview_api.py",
    "tests/integration/test_test_record_fee_document_generation_api.py",
    "tests/integration/test_approval_package_api.py",
    "tests/integration/test_folder_generation_api.py",
    # Backend - Tests (unit)
    "tests/unit/test_project_test_plan_matrix_edit_service.py",
    "tests/unit/test_project_test_plan_draft_service.py",
    "tests/unit/test_project_output_record_service.py",
    "tests/unit/test_section2_completion_preview_service.py",
    "tests/unit/test_section2_write_back_service.py",
    "tests/unit/test_test_record_fee_dataset_preview_service.py",
    "tests/unit/test_test_record_fee_document_generation_service.py",
    "tests/unit/test_approval_package_service.py",
    "tests/unit/test_evidence_placement_service.py",
    "tests/unit/test_folder_service.py",
    # Documentation
    "docs/task_184_project_workbench_matrix_first_redesign_baseline_plan.md",
    "docs/task_185_project_workbench_state_model_and_layout_refactor_plan.md",
    "docs/task_186_project_workbench_matrix_review_surface_plan.md",
    "docs/task_187_project_workbench_document_pipeline_autofill_plan.md",
    "docs/task_188_project_workbench_version_and_stale_status_plan.md",
    "docs/task_188_project_output_version_ledger_correction_plan.md",
    "docs/task_189_matrix_edit_freeze_authority_semantics_correction_plan.md",
    "docs/task_189_matrix_authority_read_model_and_group_identity_correction_plan.md",
    "docs/task_190_project_workbench_matrix_authority_workspace_plan.md",
    "docs/task_190_matrix_overview_cross_table_and_supporting_compactness_correction_plan.md",
    "docs/task_191_matrix_draft_starter_import_and_manual_empty_state_plan.md",
    "docs/task_192_matrix_source_candidates_and_browse_fallback_correction_plan.md",
    "docs/project_workbench_matrix_authority_workspace_target.md",
    "docs/matrix_test_plan_data_management_decisions.md",
]


def pack_files() -> None:
    """Pack all specified files into a zip archive."""
    packed_count = 0
    missing_count = 0

    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in FILES_TO_PACK:
            full_path = REPO_ROOT / file_path
            if full_path.exists():
                zipf.write(full_path, file_path)
                packed_count += 1
                print(f"[OK] {file_path}")
            else:
                missing_count += 1
                print(f"[MISSING] {file_path}")

    print(f"\n{'=' * 60}")
    print("Packing complete!")
    print(f"Total files: {packed_count} packed, {missing_count} missing")
    print(f"Output: {OUTPUT_ZIP}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    pack_files()
