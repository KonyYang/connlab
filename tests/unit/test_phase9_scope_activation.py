from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_phase9_board_closes_after_task059_completion() -> None:
    """TASK_059 closes Phase 9 while later approved phases may advance."""
    board = (ROOT / "docs" / "task_board.md").read_text(encoding="utf-8")

    assert (
        "Current Phase: `Phase 10A follow-up redirection - New Project single-page redesign`"
        in board
        or "Current Phase: `Phase 10B - LTR workbook write hardening`" in board
        or "Current Phase: `Phase 11 - Project planning data foundation before downstream document automation`"
        in board
    )
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
    )
    assert "Phase 10A" in board
    assert "| T9-1 | `TASK_053_PHASE9_SCOPE_AND_BOARD_ACTIVATION` | done |" in board
    assert (
        "| T9-2 | `TASK_054_LTR_READINESS_PREVIEW_COMMIT_FRONTEND_WIRING` | done |"
        in board
    )
    assert "| T9-3 | `TASK_055_INTAKE_EXCEPTION_WORKFLOW_FRONTEND_WIRING` | done |" in board
    assert "| T9-4 | `TASK_056_FOLDER_EVIDENCE_PLACEMENT_FRONTEND_WIRING` | done |" in board
    assert "| T9-5 | `TASK_057_PROJECT_LOOKUP_SAMPLE_TESTING_SUMMARY_FRONTEND_PANEL` | done |" in board
    assert "| T9-6 | `TASK_058_LIFECYCLE_GUARDS_DISABLED_REASON_UI` | done |" in board
    assert "| T9-7 | `TASK_059_PHASE9_BROWSER_SMOKE_AND_DOCS_SYNC` | done |" in board
    assert "Phase 9 validation summary" in board


def test_phase9_task_files_exist_and_preserve_scope() -> None:
    """Phase 9 tasks exist and keep future scope blocked."""
    expected_tasks = [
        "TASK_053_PHASE9_SCOPE_AND_BOARD_ACTIVATION.md",
        "TASK_054_LTR_READINESS_PREVIEW_COMMIT_FRONTEND_WIRING.md",
        "TASK_055_INTAKE_EXCEPTION_WORKFLOW_FRONTEND_WIRING.md",
        "TASK_056_FOLDER_EVIDENCE_PLACEMENT_FRONTEND_WIRING.md",
        "TASK_057_PROJECT_LOOKUP_SAMPLE_TESTING_SUMMARY_FRONTEND_PANEL.md",
        "TASK_058_LIFECYCLE_GUARDS_DISABLED_REASON_UI.md",
        "TASK_059_PHASE9_BROWSER_SMOKE_AND_DOCS_SYNC.md",
    ]

    for filename in expected_tasks:
        task = ROOT / "tasks" / filename
        assert task.is_file()
        source = task.read_text(encoding="utf-8")
        assert "Matrix" in source
        assert "Report" in source
        assert "AI review" in source


def test_task054_defines_ltr_ui_wiring_without_workbook_write() -> None:
    """The first Phase 9 implementation task is LTR UI wiring only."""
    task = (
        ROOT
        / "tasks"
        / "TASK_054_LTR_READINESS_PREVIEW_COMMIT_FRONTEND_WIRING.md"
    ).read_text(encoding="utf-8")

    for term in [
        "Show LTR readiness fields",
        "Add no-write LTR preview action",
        "Add local commit action",
        "No external workbook write",
        "$impeccable",
    ]:
        assert term in task


def test_phase9_validation_summary_closes_phase_without_future_scope() -> None:
    """TASK_059 records Phase 9 closeout without future scope."""
    summary = (ROOT / "docs" / "phase9_validation_summary.md").read_text(
        encoding="utf-8"
    )
    checklist = (ROOT / "docs" / "frontend_smoke_checklist.md").read_text(
        encoding="utf-8"
    )

    for term in [
        "Status: Phase 9 complete",
        "Manual Browser Smoke Checklist",
        "LTR readiness",
        "Evidence placement",
        "lifecycle guard",
        "Do not activate either candidate automatically",
    ]:
        assert term in summary

    for term in [
        "Phase 9 Operator Workflow Wiring",
        "Read-only lookup",
        "No-overwrite",
        "Lifecycle guards",
    ]:
        assert term in checklist
