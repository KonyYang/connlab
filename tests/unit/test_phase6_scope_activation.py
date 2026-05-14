from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_phase6_plan_defines_real_intake_scope() -> None:
    """The Phase 6 plan captures the real Outlook package intake workflow."""
    source = (ROOT / "docs" / "ConnLab_Phase6_Implementation_Plan.md").read_text(
        encoding="utf-8"
    )

    for term in [
        "Outlook Email Package Intake",
        "Application Form Selection",
        "Human Confirmation",
        "一份申请单创建一个项目",
        "IntakePackage -> IntakeAsset -> Application Form Selection -> IntakeCase -> Review Draft -> Confirm Project",
        "OfficeFacade",
        "Phase 6 不做",
        "TASK_027A",
        "TASK_027B",
        "TASK_031A",
        "TASK_031B",
        "IntakeStorage",
    ]:
        assert term in source

    compatibility = (ROOT / "docs" / "msg_compatibility.md").read_text(
        encoding="utf-8"
    )
    assert "blocked_missing_fixtures" in compatibility
    assert "real samples found: 3" in compatibility
    assert "all available samples classified as `supported`" in compatibility


def test_task025_activates_only_office_boundary_next() -> None:
    """TASK_025 is a board activation task and must not implement later scope."""
    task = (
        ROOT
        / "tasks"
        / "TASK_025_PHASE6_SCOPE_REVISION_AND_BOARD_ACTIVATION.md"
    ).read_text(encoding="utf-8")

    for term in [
        "Open Phase 6A",
        "Activate only `TASK_026_OFFICE_INTEGRATION_BOUNDARY`",
        "Do not implement OfficeFacade code in this task",
        "No `.msg` parsing",
        "No backend implementation",
    ]:
        assert term in task


def test_task026_exists_as_the_next_controlled_task() -> None:
    """TASK_026 defines the next implementation boundary without jumping ahead."""
    task = (ROOT / "tasks" / "TASK_026_OFFICE_INTEGRATION_BOUNDARY.md").read_text(
        encoding="utf-8"
    )

    for term in [
        "Office Integration Boundary",
        "backend/infrastructure/office/",
        "OfficeFacade",
        "must not create `Project`",
        "No intake database tables",
        "No frontend pages",
    ]:
        assert term in task


def test_task_board_preserves_phase6a_completion_and_forbids_future_scope() -> None:
    """The task board preserves Phase 6A completion while later phases advance."""
    board = (ROOT / "docs" / "task_board.md").read_text(encoding="utf-8")

    assert (
        "Current Active Task: None - pending user approval for next phase" in board
        or "Current Active Task: TASK_125_FULL_TEST_SUITE_HISTORICAL_EXPECTATION_SYNC" in board
        or "Current Active Task: TASK_126_NEW_PROJECT_SETUP_CONFIRMATION_REQUIRED_FIELDS_REWORK" in board
        or "Current Active Task: None - TASK_127 complete, pending user approval for TASK_128" in board
        or "Current Active Task: None - TASK_128 complete, pending user approval for TASK_129" in board
        or "Current Active Task: None - TASK_129 complete, pending user approval for TASK_130" in board
        or "Current Active Task: None - TASK_130 complete, pending user approval for TASK_131" in board
        or "Current Active Task: TASK_131_LTR_WORKBOOK_LOCK_BACKUP_AND_SHORT_TRANSACTION_GATEWAY" in board
        or "Current Active Task: None - TASK_131 complete, pending user approval for TASK_132" in board
        or "Current Active Task: TASK_132_LTR_WORKBOOK_WRITE_PREVIEW" in board
        or "Current Active Task: None - TASK_132 complete, pending user approval for TASK_133" in board
        or "Current Active Task: TASK_133_LTR_WORKBOOK_WRITE_COMMIT" in board
        or "Current Active Task: None - TASK_133 complete, pending user decision for next task" in board
        or "Current Active Task: TASK_134_NEW_PROJECT_LTR_WORKBOOK_COMMIT_UI_INTEGRATION" in board
        or "Current Active Task: None - TASK_134 complete, pending user decision for next task" in board
        or "Current Active Task: TASK_135_LTR_WORKBOOK_YEAR_SHEET_BOOTSTRAP" in board
        or "Current Active Task: None - TASK_135 complete, pending user decision for next task" in board
        or "Current Active Task: TASK_136_REVISION_H_NON_BLOCKING_IN_NEW_PROJECT_PRECHECK" in board
        or "Current Active Task: None - TASK_136 complete, pending user decision for next task" in board
        or "Current Active Task: TASK_137_LTR_SPECIFIED_NUMBER_RULES_AND_YEAR_MONTH_GUARDS" in board
        or "Current Active Task: None - TASK_137 complete, pending user decision for next task" in board
        or "Current Active Task: TASK_138_LTR_SUFFIX_TOKEN_STRICT_INPUT_AND_BOARD_CLEANUP" in board
        or "Current Active Task: None - TASK_138 complete, pending user decision for next task" in board
        or "Current Active Task: TASK_099_LTR_REGISTERED_FREEZE_AND_EXCEPTION_PATH" in board
        or "Current Active Task: None - TASK_099 complete, pending user decision for next task" in board
        or "Current Active Task: TASK_100_PROJECT_WORKBENCH_BOUNDARY_AFTER_FOLDER_CREATION" in board
        or "Current Active Task: None - TASK_100 complete, pending user decision for next task" in board
        or "Current Active Task: `TASK_174_PROJECT_TEST_PLAN_MATRIX_BASELINE`" in board
        or "Current Active Task: none; TASK_174 complete" in board
        or "Current Active Task: `TASK_175_PROJECT_TEST_PLAN_REVIEW_AND_DRAFT_PERSISTENCE`" in board
        or "Current Active Task: none; TASK_175 complete" in board
        or "Current Active Task: `TASK_176_PROJECT_FOLDER_EVIDENCE_CLASSIFICATION_FOR_APPROVAL_PACKAGE`" in board
        or "Current Active Task: none; TASK_176 complete" in board
        or "Current Active Task: `TASK_177_SECTION2_COMPLETION_PREVIEW`" in board
        or "Current Active Task: none; TASK_177 complete" in board
        or "Current Active Task: none; TASK_178 complete" in board
        or "Current Active Task: `TASK_179_SECTION2_WRITE_BACK_TO_APPLICATION_FORM`" in board
        or "Current Active Task: none; TASK_179 complete" in board
        or "Current Active Task: `TASK_180_TEST_RECORD_AND_FEE_INPUT_DATASET_PREVIEW`" in board
        or "Current Active Task: none; TASK_180 complete" in board
        or "Current Active Task: `TASK_181_TEST_RECORD_TEMPLATE_AND_FEE_FORM_GENERATION`" in board
        or "Current Active Task: none; TASK_181 complete" in board
        or "Current Active Task: `TASK_182_APPROVAL_PACKAGE_GENERATION_AND_PROJECT_FOLDER_PLACEMENT`" in board
            or "Current Active Task: none; TASK_182 complete" in board
            or "Current Active Task: `TASK_183_PROJECT_WORKBENCH_APPROVAL_PACKAGE_UI_WIRING`" in board
            or "Current Active Task: `TASK_184_PROJECT_WORKBENCH_MATRIX_FIRST_REDESIGN_BASELINE`" in board
            or "Current Active Task: `TASK_185_PROJECT_WORKBENCH_STATE_MODEL_AND_LAYOUT_REFACTOR`" in board
            or "Current Active Task: `TASK_186_PROJECT_WORKBENCH_MATRIX_REVIEW_SURFACE`" in board
            or "Current Active Task: none; TASK_186 complete, pending user approval for TASK_187" in board
            or "Current Active Task: none; TASK_187 complete, pending user approval for TASK_188" in board
            or "Current Active Task: none; TASK_188 complete, pending user approval for TASK_189" in board
            or "Current Active Task: none; TASK_188 ledger correction complete, pending user approval for `TASK_189_MATRIX_EDIT_AND_FREEZE_FOUNDATION`" in board
            or "Current Active Task: none; TASK_189 complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_189 acceptance mismatch confirmed, pending user approval for `TASK_189_MATRIX_EDIT_FREEZE_AUTHORITY_SEMANTICS_CORRECTION`" in board
            or "Current Active Task: none; TASK_189 authority semantics correction complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_189 authority read-model/group-identity correction complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_190 complete, pending user approval for next controlled task" in board
            or "Current Active Task: TASK_190_MATRIX_OVERVIEW_CROSS_TABLE_AND_SUPPORTING_COMPACTNESS_CORRECTION plan proposed; awaiting user approval before implementation" in board
            or "Current Active Task: none; TASK_190 correction complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_191 complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_192 complete, pending user approval for next controlled task" in board
    )
    assert (
        "Current Phase: `Phase 10A follow-up redirection - New Project single-page redesign`"
        in board
        or "Current Phase: `Phase 10B - LTR workbook write hardening`" in board
        or "Current Phase: `Phase 11 - Project planning data foundation before downstream document automation`"
        in board
    )
    assert "| T6A-1 | `TASK_025_PHASE6_SCOPE_REVISION_AND_BOARD_ACTIVATION` | done |" in board
    assert "| T6A-2 | `TASK_026_OFFICE_INTEGRATION_BOUNDARY` | done |" in board
    assert (
        "| T6A-3 | `TASK_027A_OUTLOOK_MSG_SOURCE_IMPORT_AND_MINIMAL_METADATA` | done |"
        in board
    )
    assert "| T6A-4 | `TASK_027B_OUTLOOK_MSG_ATTACHMENT_EXTRACTION` | done |" in board
    assert "| T6A-5 | `TASK_027C_REAL_MSG_SAMPLE_COMPATIBILITY` | done |" in board
    assert "| T6A-6 | `TASK_028A_INTAKE_STORAGE_BOUNDARY` | done |" in board
    assert "| T6A-7 | `TASK_028B_INTAKE_PACKAGE_ASSET_CASE_STORAGE` | done |" in board
    assert "| T6A-8 | `TASK_029_APPLICATION_FORM_CANDIDATE_DETECTION` | done |" in board
    assert "| T6A-9 | `TASK_030_FORM_SELECTION_AND_DRAFT_CREATION` | done |" in board
    assert "| T6A-10 | `TASK_031A_INTAKE_INBOX_FRONTEND_UX` | done |" in board
    assert "| T6A-11 | `TASK_031B_INTAKE_PACKAGE_DETAIL_FRONTEND_UX` | done |" in board
    assert "| T6A-12 | `TASK_031C_INTAKE_CASE_REVIEW_FRONTEND_UX` | done |" in board
    assert "| T6A-13 | `TASK_032_CONFIRM_INTAKE_CASE_TO_PROJECT` | done |" in board
    assert "| T6A-14 | `TASK_033_DIRECT_WORD_APPLICATION_FORM_IMPORT` | done |" in board
    assert "| T6A-15 | `TASK_034_ATTACHMENT_AWARE_PRECHECK_BRIDGE` | done |" in board
    assert "| T6A-16 | `TASK_035_PHASE6_VALIDATION_AND_DOCS_SYNC` | done |" in board
    assert "TASK_027A_OUTLOOK_MSG_SOURCE_IMPORT_AND_MINIMAL_METADATA" in board
    assert "TASK_028A_INTAKE_STORAGE_BOUNDARY" in board
    assert "TASK_031A_INTAKE_INBOX_FRONTEND_UX" in board

    assert (
        ROOT / "tasks" / "TASK_027A_OUTLOOK_MSG_SOURCE_IMPORT_AND_MINIMAL_METADATA.md"
    ).is_file()
    assert (ROOT / "tasks" / "TASK_027B_OUTLOOK_MSG_ATTACHMENT_EXTRACTION.md").is_file()
    assert (ROOT / "tasks" / "TASK_027C_REAL_MSG_SAMPLE_COMPATIBILITY.md").is_file()
    assert (ROOT / "tasks" / "TASK_028A_INTAKE_STORAGE_BOUNDARY.md").is_file()
    assert (ROOT / "tasks" / "TASK_028B_INTAKE_PACKAGE_ASSET_CASE_STORAGE.md").is_file()
    assert (ROOT / "tasks" / "TASK_029_APPLICATION_FORM_CANDIDATE_DETECTION.md").is_file()
    assert (ROOT / "tasks" / "TASK_030_FORM_SELECTION_AND_DRAFT_CREATION.md").is_file()
    assert (ROOT / "tasks" / "TASK_031A_INTAKE_INBOX_FRONTEND_UX.md").is_file()
    assert (ROOT / "tasks" / "TASK_031B_INTAKE_PACKAGE_DETAIL_FRONTEND_UX.md").is_file()
    assert (ROOT / "tasks" / "TASK_031C_INTAKE_CASE_REVIEW_FRONTEND_UX.md").is_file()
    assert (ROOT / "tasks" / "TASK_032_CONFIRM_INTAKE_CASE_TO_PROJECT.md").is_file()
    assert (ROOT / "tasks" / "TASK_033_DIRECT_WORD_APPLICATION_FORM_IMPORT.md").is_file()
    assert (ROOT / "tasks" / "TASK_034_ATTACHMENT_AWARE_PRECHECK_BRIDGE.md").is_file()
    assert (ROOT / "tasks" / "TASK_035_PHASE6_VALIDATION_AND_DOCS_SYNC.md").is_file()
    assert (ROOT / "docs" / "phase6a_validation.md").is_file()

    for forbidden in [
        "Outlook inbox auto-scan",
        "email sending",
        "Matrix",
        "Report",
        "AI review",
    ]:
        assert forbidden in board
