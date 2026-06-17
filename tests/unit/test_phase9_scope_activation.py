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
        or "Current Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`"
        in board
    )
    assert (
        "Current Active Task: None - pending user approval for next phase" in board
        or "Current Active Task: `TASK_317_SOURCE_BOOK_AND_REQUEST_MATERIAL_COLLECTION` complete" in board
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
            or "Current Active Task: TASK_204_RUNTIME_PROJECTION_READ_ONLY_CONSUMER_MINIMAL_SLICE task file pending user review; awaiting approval before implementation" in board
            or "Current Active Task: none; TASK_204 runtime projection read-only consumer minimal slice complete, pending user approval for next controlled task" in board
            or "Current Active Task: TASK_205_RUNTIME_PROJECTION_SNAPSHOT_ADAPTER_MINIMAL_SLICE task file pending user review; awaiting approval before implementation" in board
            or "Current Active Task: none; TASK_205 runtime projection snapshot adapter minimal slice complete, pending user approval for next controlled task" in board
            or "Current Active Task: TASK_206_RUNTIME_PROJECTION_READ_ONLY_API_ADAPTER_MINIMAL_SLICE task file pending user review; awaiting approval before implementation" in board
            or "Current Active Task: none; TASK_206 runtime projection read-only api adapter minimal slice complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_207 api contract snapshot sync complete, pending user approval for next controlled task" in board
            or "Current Active Task: TASK_208_RUNTIME_PROJECTION_READ_ONLY_API_TYPED_CONTRACT_MINIMAL_SLICE task file pending user review; awaiting approval before implementation" in board
            or "Current Active Task: none; TASK_208 runtime projection read-only api typed contract minimal slice complete, pending user approval for next controlled task" in board
            or "Current Active Task: TASK_209_RUNTIME_PROJECTION_READ_ONLY_FRONTEND_CONSUMER_PROTOTYPE_MINIMAL_SLICE task file pending user review; awaiting approval before implementation" in board
            or "Current Active Task: none; TASK_209 runtime projection read-only frontend consumer prototype minimal slice complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_210 runtime projection prototype isolation hardening complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_211 Project Workbench Runtime Console baseline replacement complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_212 Project Workbench Runtime Console mockup completeness pass complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_213 Project Workbench topbar and filter control density fix complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_214 Project Workbench mockup visual clone density pass complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_215 default collapsed icon sidebar complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_216 matrix authority to runtime console sync contract and navigation slice complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_217 matrix editor placeholder clone and workbench matrix button navigation complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_218 matrix editor visual alignment density pass complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_219 matrix editor pixel alignment pass complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_219A runtime console repositioning complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_219B workbench model boundary split complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_219C derived output status console alignment complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_219D lightweight material drop surface slice complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_219E runtime console regression guards complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_219F Workbench legacy support removal complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_219F Workbench runtime console responsibility refinement complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_220 Project Workbench target UI alignment complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_221 Matrix Editor target UI alignment and workflow convergence complete, pending user approval for next controlled task" in board
            or "Current Active Task: none; TASK_222 Matrix Editor target UI pixel tuning pass complete, pending user approval for next controlled task" in board
            or "Current Active Task: `TASK_315F_FEE_CURRENT_VERSION_CANCEL_UPDATE_SEMANTICS` is complete" in board
        or "Current Active Task: none (`DOCS_001_MARKDOWN_INFORMATION_ARCHITECTURE_AND_AUTO_ARCHIVE_RULES` complete; awaiting next approved task)." in board
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
        task = ROOT / "tasks" / "completed" / "2026" / filename
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
        / "completed"
        / "2026"
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
    summary = (ROOT / "docs" / "archive" / "validation_summaries" / "phase9_validation_summary.md").read_text(
        encoding="utf-8"
    )
    checklist = (ROOT / "docs" / "archive" / "validation_summaries" / "frontend_smoke_checklist.md").read_text(
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
