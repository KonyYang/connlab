from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_phase10a_board_closes_after_task065_completion() -> None:
    """TASK_065 closes Phase 10A without activating later work."""
    board = (ROOT / "docs" / "task_board.md").read_text(encoding="utf-8")

    assert "Phase 10A" in board
    assert (
        "Current Phase: `Phase 10A follow-up redirection - New Project single-page redesign`"
        in board
        or "Current Phase: `Phase 10B - LTR workbook write hardening`" in board
        or "Current Phase: `Phase 11 - Project planning data foundation before downstream document automation`"
        in board
        or "Current Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`"
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
            or "Current Active Task: none; TASK_194 product realignment complete, pending next controlled implementation task" in board
            or "Current Active Task: none; TASK_195 runtime information architecture complete, pending next controlled implementation task" in board
            or "Current Active Task: none; TASK_196 step-centric domain foundation complete, pending next controlled implementation task" in board
            or "Current Active Task: none; TASK_197 interactive step token read model complete, pending next controlled implementation task" in board
            or "Current Active Task: none; TASK_198 runtime projection service boundary complete, pending next controlled implementation task" in board
            or "Current Active Task: none; TASK_200 first runtime implementation slice planning complete, pending next controlled implementation task" in board
            or "Current Active Task: none; TASK_201 projection dto and token reference builder minimal slice complete, pending next controlled implementation task" in board
            or "Current Active Task: none; TASK_202 runtime projection composition helper minimal slice complete, pending next controlled implementation task" in board
    )
    assert "### Phase 10A - Intake Entry Completion" in board
    assert "| T10A-1 | `TASK_060_PHASE10A_SCOPE_AND_BOARD_ACTIVATION` | done |" in board
    assert "| T10A-2 | `TASK_061_MSG_PACKAGE_IMPORT_API_AND_FRONTEND_ENTRY` | done |" in board
    assert "| T10A-3 | `TASK_062_INTAKE_PACKAGE_DETAIL_REAL_DATA_WIRING` | done |" in board
    assert "| T10A-4 | `TASK_063_DIRECT_MANUAL_INTAKE_ENTRY` | done |" in board
    assert "| T10A-5 | `TASK_064_UNIFIED_INTAKE_CASE_REVIEW_AND_CONFIRMATION_UI` | done |" in board
    assert "| T10A-6 | `TASK_065_INTAKE_ENTRY_BROWSER_SMOKE_AND_DOCS_SYNC` | done |" in board
    assert "Phase 10A validation summary" in board
    assert (
        "copied-workbook LTR write hardening is deferred until explicit user approval"
        in board
    )


def test_phase10a_plan_documents_email_first_and_manual_exception() -> None:
    """The Phase 10A plan preserves the corrected intake-entry priority."""
    plan = (ROOT / "docs" / "phase10a_intake_entry_completion_plan.md").read_text(
        encoding="utf-8"
    )

    for term in [
        "Manual `.msg` package import",
        "Direct manual intake",
        "No Outlook inbox auto-scan",
        "No email sending",
        "No copied-workbook LTR write hardening in Phase 10A",
        "Operators can start from a `.msg` file without creating a project first",
        "Operators can start from manual intake when no email exists",
    ]:
        assert term in plan


def test_phase10a_task_files_exist_and_preserve_scope() -> None:
    """Phase 10A tasks exist and keep future scope blocked."""
    expected_tasks = [
        "TASK_060_PHASE10A_SCOPE_AND_BOARD_ACTIVATION.md",
        "TASK_061_MSG_PACKAGE_IMPORT_API_AND_FRONTEND_ENTRY.md",
        "TASK_062_INTAKE_PACKAGE_DETAIL_REAL_DATA_WIRING.md",
        "TASK_063_DIRECT_MANUAL_INTAKE_ENTRY.md",
        "TASK_064_UNIFIED_INTAKE_CASE_REVIEW_AND_CONFIRMATION_UI.md",
        "TASK_065_INTAKE_ENTRY_BROWSER_SMOKE_AND_DOCS_SYNC.md",
    ]

    for filename in expected_tasks:
        task = ROOT / "tasks" / filename
        assert task.is_file()
        source = task.read_text(encoding="utf-8")
        for forbidden in [
            "Outlook inbox auto-scan",
            "email sending",
            "Matrix",
            "Report",
            "AI review",
            "external LTR workbook mutation",
        ]:
            assert forbidden in source

    done_task = (
        ROOT / "tasks" / "TASK_061_MSG_PACKAGE_IMPORT_API_AND_FRONTEND_ENTRY.md"
    ).read_text(encoding="utf-8")
    completed_task = (
        ROOT / "tasks" / "TASK_062_INTAKE_PACKAGE_DETAIL_REAL_DATA_WIRING.md"
    ).read_text(encoding="utf-8")
    manual_task = (
        ROOT / "tasks" / "TASK_063_DIRECT_MANUAL_INTAKE_ENTRY.md"
    ).read_text(encoding="utf-8")
    review_task = (
        ROOT / "tasks" / "TASK_064_UNIFIED_INTAKE_CASE_REVIEW_AND_CONFIRMATION_UI.md"
    ).read_text(encoding="utf-8")
    closeout_task = (
        ROOT / "tasks" / "TASK_065_INTAKE_ENTRY_BROWSER_SMOKE_AND_DOCS_SYNC.md"
    ).read_text(encoding="utf-8")
    assert "## Status\n\ndone" in done_task
    assert "manual `.msg` email package import entry point" in done_task
    assert "## Status\n\ndone" in completed_task
    assert "real backend package, asset, and candidate state" in completed_task
    assert "## Status\n\ndone" in manual_task
    assert "no-email exception path" in manual_task
    assert "## Status\n\ndone" in review_task
    assert "## Status\n\ndone" in closeout_task


def test_phase10a_validation_summary_closes_scope_without_future_work() -> None:
    """TASK_065 records validation and manual smoke guidance for Phase 10A."""
    summary = (ROOT / "docs" / "phase10a_validation_summary.md").read_text(
        encoding="utf-8"
    )
    checklist = (ROOT / "docs" / "frontend_smoke_checklist.md").read_text(
        encoding="utf-8"
    )

    for term in [
        "Status: Phase 10A complete",
        "Manual Browser Smoke Checklist",
        "manual `.msg` package import",
        "direct manual intake",
        "unified email-import and manual-intake case review",
        "explicit operator confirmation",
        "Do not activate the candidate automatically",
    ]:
        assert term in summary

    for term in [
        "Phase 10A Intake Entry Completion",
        ".msg` import control",
        "no-email manual intake",
        "same review page",
        "operator confirmation checkbox",
        "copied-workbook LTR write hardening",
    ]:
        assert term in checklist
