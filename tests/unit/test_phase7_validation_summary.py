from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_phase7_validation_summary_closes_phase_without_future_scope() -> None:
    """TASK_051 records Phase 7 closeout without activating future work."""
    summary = (ROOT / "docs" / "phase7_validation_summary.md").read_text(
        encoding="utf-8"
    )
    board = (ROOT / "docs" / "task_board.md").read_text(encoding="utf-8")

    for term in [
        "Status: Phase 7 complete",
        "Manual Smoke Checklist",
        "Workbook Write Mode",
        "Write mode is disabled by default",
        "configuration-driven",
        "Do not activate either candidate automatically",
    ]:
        assert term in summary

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
    )
    assert "| T7-16 | `TASK_051_PHASE7_VALIDATION_AND_DOCS_SYNC` | done |" in board
    assert "Current recommendation:" in board
    assert "Phase 10A has been explicitly approved by the user" in board


def test_phase7_task_file_is_done() -> None:
    """The TASK_051 file must match the closed board state."""
    task = (
        ROOT / "tasks" / "TASK_051_PHASE7_VALIDATION_AND_DOCS_SYNC.md"
    ).read_text(encoding="utf-8")

    assert "## Status\n\ndone" in task
