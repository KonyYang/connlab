# ConnLab Task Board

> Status: TASK_149-TASK_156 complete + TASK_159 hotfix complete + TASK_160 complete + TASK_161 complete + TASK_162 complete + TASK_163 complete + TASK_164 complete + TASK_165 complete + TASK_166 complete + TASK_167 complete + TASK_168 complete + TASK_169 complete + TASK_170 complete + TASK_171 complete + TASK_172 complete + TASK_173 complete + TASK_174 complete + TASK_175 complete + TASK_176 complete + TASK_177 complete + TASK_178 complete + TASK_179 complete + TASK_180 complete + TASK_181 complete + TASK_182 complete + TASK_183 complete + TASK_184 complete + TASK_185 complete + TASK_186 complete + TASK_187 complete + TASK_188 frontend status complete + TASK_188 ledger correction complete + TASK_189 corrected + TASK_189 authority read-model correction complete + TASK_190 corrected and accepted + TASK_191 complete + TASK_192 complete + TASK_193 complete
> Last Updated: 2026-05-15
> Current Source Of Truth: `docs/task_board.md`
> Current Active Task: none; TASK_193 governance sync complete, pending next controlled implementation task
> Current Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

- `TASK_193_PHASE_FREEZE_ARCHITECTURE_INVENTORY_SCOPE_REDEFINITION` is complete. Added stage freeze and architecture inventory documents, synchronized README stage wording with actual implemented scope, and registered governance alignment for the current Project Workbench / Matrix / Approval Package phase without business-code refactor.
- Deliverables: `docs/stage_freeze_2026-05-15_project_workbench_matrix_approval_package.md`, `docs/architecture_inventory_2026-05-15.md`, `tasks/TASK_193_PHASE_FREEZE_ARCHITECTURE_INVENTORY_SCOPE_REDEFINITION.md`, `docs/task_193_phase_freeze_architecture_inventory_scope_redefinition_plan.md`.
- Validation: document consistency check passed (README/task_board/tasks/code evidence aligned for stage definition); no backend/frontend behavior changes were made in this task.
- Next recommended action: define and approve next controlled implementation task within the frozen stage baseline (Project Workbench / Matrix / Approval Package), with explicit in-scope/out-of-scope boundaries.

> **TASK_178 COMPLETE**: New Project Intake Logic Fixes
> - Fixed P0 auto-select duplicate handling without using `create_separate` as an implicit page-load action.
> - Fixed duplicate confirmation re-click behavior with backend selected-asset shortcut and frontend active-case guard.
> - Stopped remaining Phase 2/3 items after review because they lack confirmed defects and would expand duplicate lifecycle scope.
> - Plan: `tasks/TASK_178_NEW_PROJECT_INTAKE_LOGIC_FIXES.md`

- `TASK_174_PROJECT_TEST_PLAN_MATRIX_BASELINE` is complete. Added read-only `.docx` product specification Matrix preview through `POST /api/test-plan/matrix-preview-from-path`, deterministic group/sequence extraction, source traceability, and explicit deferred capability responses for `.doc` and `.pdf`. The implementation preserves the boundary between New Project `IntakeCase`/`ApplicationDraft` data and Project Management `ProjectTestPlan` preview data; it does not persist ProjectTestPlan records or write Section 2/test record/fee/report files.
- Validation: `py -m pytest tests\unit\test_product_spec_matrix_parser.py tests\integration\test_project_test_plan_preview_api.py -q` passed (7 passed); targeted task-board sync run passed (24 passed). Real EnergyKlip 500A `.docx` sample selected table 21 and extracted `Group 1` through `Group 8`. Full `py -m pytest tests\unit tests\integration -q` reported 489 passed and 6 historical failures unrelated to TASK_174 in frontend static assertions and LTR workbook snapshot gateway expectations.
- `TASK_175_PROJECT_TEST_PLAN_REVIEW_AND_DRAFT_PERSISTENCE` is complete. Added Project-stage test-plan draft snapshot persistence, domain status/model, SQLite repository, application service, and Project-scoped create/list/read/update APIs. Creating a new draft for the same `project_id + source_document_path` supersedes prior active drafts while preserving history. The task does not mutate New Project `ApplicationDraft`/`IntakeCase` data and does not write Office files, Section 2, test records, fee evaluations, or reports.
- Validation: `py -m pytest tests\unit\test_project_test_plan_draft_service.py tests\integration\test_project_test_plan_draft_api.py -q` passed (7 passed); `py -m pytest tests\unit\test_product_spec_matrix_parser.py tests\integration\test_project_test_plan_preview_api.py -q` passed (7 passed).
- `TASK_176_PROJECT_FOLDER_EVIDENCE_CLASSIFICATION_FOR_APPROVAL_PACKAGE` is complete. Approval-package evidence placement now plans product specification files directly under `Submitted Material`; `.msg` evidence remains under `E-mail`; application/request forms, fee evaluation files, and test-record template-like supporting documents remain under `Submitted Material`; photos remain under `Photos`; LTR evidence/corrections keep their specialized subfolders. Preview-before-copy, no-overwrite, duplicate-target detection, and API response shape are unchanged.
- Validation: `py -m pytest tests\unit\test_evidence_placement_service.py tests\integration\test_evidence_placement_api.py -q` passed (6 passed); `py -m pytest tests\integration\test_folder_generation_api.py tests\integration\test_project_lifecycle_gating_api.py -q` passed (4 passed).
- `TASK_177_SECTION2_COMPLETION_PREVIEW` is complete. Added a read-only Section 2 preview service and API from Project-stage `ProjectTestPlanDraft` data. It computes received date, estimated completion date, lab/personnel/sample-condition preview fields, test demand summary, duration summary, and warnings for missing explicit test duration. It rejects missing/cross-project/superseded drafts and invalid duration buffers. It does not write Word files, mutate New Project drafts, mutate application forms, or generate test record/fee/report files.
- Validation: `py -m pytest tests\unit\test_section2_completion_preview_service.py tests\integration\test_section2_completion_preview_api.py -q` passed (6 passed); `py -m pytest tests\unit\test_project_test_plan_draft_service.py tests\integration\test_project_test_plan_draft_api.py -q` passed (7 passed); task-board guard run passed (17 passed).
- `TASK_178_NEW_PROJECT_INTAKE_LOGIC_FIXES` is complete. It fixed two verified New Project P0 issues from the expert review: auto-select no longer uses `create_separate` to silently create separate drafts during page load, and duplicate re-click handling now uses a backend existing selected-asset shortcut plus a frontend active-case guard. Remaining suggested Phase 2/3 items are stopped because they are either structure cleanup without a confirmed defect or broader lifecycle changes that need a separate task if real evidence appears.
- Validation: `py -m pytest tests\unit\test_new_project_auto_select_duplicate_handling.py tests\unit\test_select_already_selected_asset_shortcut.py tests\unit\test_new_project_application_draft_service.py tests\unit\test_intake_form_selection_service.py -q` passed; `npm run build` from `frontend` passed.
- `TASK_179_SECTION2_WRITE_BACK_TO_APPLICATION_FORM` is complete. Added controlled `.docx` Section 2 write-back through the Office infrastructure boundary with backup-before-write, deterministic Section 2 label matching, changed/unchanged field results, and typed API endpoint. It writes only lab, assigned personnel, received date, estimated completion date, and sample condition. It does not support `.doc`/PDF, does not add UI, and does not generate test record/fee/report files.
- Validation: `py -m pytest tests\unit\test_section2_write_back_service.py tests\unit\test_word_document_section2_write_gateway.py tests\integration\test_section2_write_back_api.py -q` passed (8 passed); TASK_177 preview regression passed (6 passed); Office boundary tests passed (7 passed); task-board guard run passed (17 passed).
- `TASK_180_TEST_RECORD_AND_FEE_INPUT_DATASET_PREVIEW` is complete. Added read-only backend dataset preview from Project-stage `ProjectTestPlanDraft` data for later test record template generation and fee evaluation form generation. The preview exposes test-record groups/steps/source traceability and fee line candidates with missing-price warnings. It rejects missing/cross-project/superseded drafts, does not write Office files, does not calculate prices, and does not generate templates.
- Validation: `py -m pytest tests\unit\test_test_record_fee_dataset_preview_service.py tests\integration\test_test_record_fee_dataset_preview_api.py -q` passed (7 passed); `py -m pytest tests\unit\test_project_test_plan_draft_service.py tests\integration\test_project_test_plan_draft_api.py -q` passed (7 passed); task-board guard run passed (17 passed).
- Plan: `docs/task_180_test_record_fee_dataset_preview_plan.md`.
- `TASK_181_TEST_RECORD_TEMPLATE_AND_FEE_FORM_GENERATION` is complete. Added backend document generation from TASK_180 dataset preview for test record `.docx` and fee-evaluation workbook outputs with strict infrastructure-boundary Office writes. Test-record generation is implemented via `python-docx`; fee generation is isolated behind Excel COM and returns `skipped_unavailable` when COM is unavailable. Includes overwrite protection, template/path validation, and typed API response.
- Validation: `py -m pytest tests\unit\test_test_record_fee_document_generation_service.py tests\unit\test_test_record_document_gateway.py tests\unit\test_fee_evaluation_workbook_gateway.py tests\integration\test_test_record_fee_document_generation_api.py -q` passed (9 passed); `py -m pytest tests\unit\test_project_test_plan_draft_service.py tests\integration\test_project_test_plan_draft_api.py tests\unit\test_test_record_fee_dataset_preview_service.py tests\integration\test_test_record_fee_dataset_preview_api.py -q` passed (14 passed); task-board guard run passed (17 passed).
- Plan: `docs/task_181_test_record_template_fee_form_generation_plan.md`.
- `TASK_182_APPROVAL_PACKAGE_GENERATION_AND_PROJECT_FOLDER_PLACEMENT` is complete. Added a backend preview-and-execute approval-package workflow that places completed application form, generated test record, generated fee evaluation file, and selected evidence/source files into Project folder approval-package destinations. It enforces conflict blocking when overwrite is false and keeps `.msg` evidence under `E-mail` while package documents are placed under `Submitted Material`.
- Validation: `py -m pytest tests\unit\test_approval_package_service.py tests\integration\test_approval_package_api.py -q` passed (5 passed); `py -m pytest tests\unit\test_evidence_placement_service.py tests\integration\test_evidence_placement_api.py tests\unit\test_test_record_fee_document_generation_service.py tests\integration\test_test_record_fee_document_generation_api.py -q` passed (11 passed); task-board guard run passed (17 passed).
- Plan: `docs/task_182_approval_package_generation_and_project_folder_placement_plan.md`.
- `TASK_183_PROJECT_WORKBENCH_APPROVAL_PACKAGE_UI_WIRING` is complete. Project Workbench now includes a dedicated approval-package panel that wires TASK_182 backend preview/execute APIs through `frontend/src/api/client.ts` and a focused `ApprovalPackagePanel` component. Operators can input required paths, optional fee/evidence paths, preview blockers and warnings, and execute only when preview exists and is blocker-free.
- Validation: `npm run build` (frontend) passed; `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or approval or folder"` passed (`5 passed, 53 deselected`); task-board guard run passed (`17 passed`).
- Plan: `docs/task_183_project_workbench_approval_package_ui_wiring_plan.md`.
- `TASK_184_PROJECT_WORKBENCH_MATRIX_FIRST_REDESIGN_BASELINE` is complete. It defines the Matrix-first Workbench redesign baseline from real operator flow: source archive, Matrix review, duration and Section 2, test record, fee evaluation, approval package, and reference lookup. It confirms the boundary that `Project` remains the system center, `ProjectTestPlan` is the structured intermediate object, and Matrix is the primary operator work view rather than an overloaded all-purpose table.
- Validation: `py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q` passed (`17 passed`).
- Plan: `docs/task_184_project_workbench_matrix_first_redesign_baseline_plan.md`.
- `TASK_185_PROJECT_WORKBENCH_STATE_MODEL_AND_LAYOUT_REFACTOR` is created as the next controlled implementation task. It scopes the first implementation step from TASK_184: thin the route page, extract a feature-level workbench model hook, and introduce stage-oriented layout composition while preserving existing folder/evidence/approval package behavior and API contracts.
- `TASK_185_PROJECT_WORKBENCH_STATE_MODEL_AND_LAYOUT_REFACTOR` is complete. Project Workbench route-level logic is now thinned through a feature model and layout composition: state and API orchestration moved to `useProjectWorkbenchModel`, evidence rendering moved to `ProjectWorkbenchEvidencePanel`, and page composition moved to `ProjectWorkbenchLayout`, while preserving existing folder/evidence/approval package behavior and API contracts.
- Validation: `npm run build` passed (frontend); `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or approval or folder"` passed (`5 passed, 53 deselected`); task-board guard run passed (`17 passed`).
- Plan: `docs/task_185_project_workbench_state_model_and_layout_refactor_plan.md`.
- `TASK_186_PROJECT_WORKBENCH_MATRIX_REVIEW_SURFACE` is complete. Project Workbench now renders a Matrix-first review surface from existing ProjectTestPlanDraft APIs. The UI shows active draft availability, source document/status/version context, group/step summaries, duration hint visibility, and draft warning/empty/error states while preserving existing folder, lookup, approval-package, and evidence workflows.
- Validation: `npm run build` passed (frontend); `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix"` passed (`4 passed, 55 deselected`); task-board guard run passed (`17 passed`).
- Plan: `docs/task_186_project_workbench_matrix_review_surface_plan.md`.
- `TASK_187_PROJECT_WORKBENCH_DOCUMENT_PIPELINE_AUTOFILL` is complete. Project Workbench now auto-fills approval package inputs from known project context: latest project folder record, source-archive evidence plan, and approval-package preview/execute outputs. Auto-filled fields stay editable, and manual edits switch that field to manual mode so subsequent auto-refresh does not overwrite operator corrections.
- Validation: `npm run build` passed (frontend); `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or approval or matrix"` passed (`5 passed, 55 deselected`); task-board guard run passed (`17 passed`).
- Plan: `docs/task_187_project_workbench_document_pipeline_autofill_plan.md`.
- `TASK_188_PROJECT_WORKBENCH_VERSION_AND_STALE_STATUS` frontend status slice is complete, but later business review found it incomplete for reload-safe lab traceability. Project Workbench now derives and displays version/freshness status for downstream outputs (`Section 2`, `test record`, `fee evaluation`, `approval package`) using feature-level selectors. This remains useful UI, but the next controlled correction must add a minimal persistent output version ledger before Matrix editing/freeze becomes the mainline.
- Validation: `npm run build` passed (frontend); `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or approval or matrix"` passed (`6 passed, 55 deselected`); task-board guard run passed (`17 passed`).
- Plan: `docs/task_188_project_workbench_version_and_stale_status_plan.md`.
- Product/data-management baseline: `docs/matrix_test_plan_data_management_decisions.md`.
- Proposed correction task: `tasks/TASK_188_PROJECT_OUTPUT_VERSION_LEDGER_CORRECTION.md`.
- Correction plan: `docs/task_188_project_output_version_ledger_correction_plan.md`.
- `TASK_188_PROJECT_OUTPUT_VERSION_LEDGER_CORRECTION` is complete. Added persisted project output ledger (`project_output_records`) with domain enums/model, repository, application service, and API routes (`POST/GET /api/projects/{project_id}/output-records`, `GET /api/projects/{project_id}/output-records/status`). Integrated output-record registration into Section 2 write-back, test-record/fee generation, and approval-package execute flow. Workbench version status now consumes backend persisted status summary (reload-safe) with existing local derivation kept as fallback.
- Validation: `python -m pytest tests/unit/test_project_output_record_service.py tests/integration/test_project_output_records_api.py tests/integration/test_section2_write_back_api.py tests/integration/test_test_record_fee_document_generation_api.py tests/integration/test_approval_package_api.py -q` passed (9 passed); `python -m pytest tests/unit/test_frontend_shell_files.py -k task188 -q` passed (1 passed).
- `TASK_189_MATRIX_EDIT_AND_FREEZE_FOUNDATION` implementation is present but acceptance mismatch is confirmed during review. Current behavior supersedes previous reviewed authority immediately when editing a reviewed draft, which conflicts with approved semantics requiring supersede only after candidate confirm succeeds. Validation severity is also mismatched (method/requirement currently treated as blockers).
- Validation note: existing TASK_189 tests pass but currently assert the incorrect authority behavior; acceptance is therefore not granted.
- Correction task proposed: `tasks/TASK_189_MATRIX_EDIT_FREEZE_AUTHORITY_SEMANTICS_CORRECTION.md`.
- `TASK_189_MATRIX_EDIT_FREEZE_AUTHORITY_SEMANTICS_CORRECTION` is complete. Matrix reviewed-edit now creates a candidate draft without superseding the current reviewed authority; supersede of previous reviewed draft happens only after candidate confirm succeeds. Confirm validation severity is corrected: method/condition/requirement/duration/source-trace/step-description gaps are warnings, while identity/token/sequence/test-item issues remain blockers.
- Validation: `python -m pytest tests\unit\test_project_test_plan_matrix_edit_service.py tests\integration\test_project_test_plan_matrix_edit_api.py tests\unit\test_matrix_step_sequence_validation.py -q` passed (12 passed); task-board guard run `python -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q` passed (17 passed).
- `TASK_189_MATRIX_AUTHORITY_READ_MODEL_AND_GROUP_IDENTITY_CORRECTION` is complete. Output ledger now treats only the latest reviewed draft as authority (`active_draft_id/version`), and draft candidates do not participate in stale comparison before confirm. Workbench model now distinguishes `matrixAuthorityDraft` and `matrixCandidateDraft` while editing prefers candidate when present. Matrix confirm now blocks missing explicit stable group identity.
- Validation: `python -m pytest tests\unit\test_project_output_record_service.py tests\unit\test_project_test_plan_matrix_edit_service.py tests\integration\test_project_test_plan_matrix_edit_api.py tests\integration\test_project_output_records_api.py -q` passed (16 passed); `npm run build` from `frontend` passed; `python -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix or task188"` passed (7 passed).
- Workbench Matrix authority target layout recorded in `docs/project_workbench_matrix_authority_workspace_target.md`.
- `TASK_190_PROJECT_WORKBENCH_MATRIX_AUTHORITY_WORKSPACE` is now accepted after controlled correction `TASK_190_MATRIX_OVERVIEW_CROSS_TABLE_AND_SUPPORTING_COMPACTNESS_CORRECTION`. Matrix overview now uses cross-table structure (technical columns + dynamic group columns + row×group token aggregation), supporting workflows default to collapsed entry points, and Matrix review surface is split into dedicated feature components (`AuthorityBar`, `Overview`, `Inspector`).
- Validation: `npm run build` from `frontend` passed; `python -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix or task190"` passed (8 passed); task-board guard run passed (`17 passed`).
- Plans: `docs/task_190_project_workbench_matrix_authority_workspace_plan.md`, `docs/task_190_matrix_overview_cross_table_and_supporting_compactness_correction_plan.md`.
- `TASK_191_MATRIX_DRAFT_STARTER_IMPORT_AND_MANUAL_EMPTY_STATE` is complete. Project Workbench Matrix empty state now supports two starter paths: import by `.docx` source path using Matrix preview + draft create APIs, or create a manual starter draft with explicit stable `Group 1` identity metadata. The starter workflow is rendered directly in Matrix empty state and preserves existing authority/candidate semantics after draft creation.
- Validation: `npm run build` (frontend) passed; `python -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix or task191"` passed (9 passed); `python -m pytest tests\integration\test_project_test_plan_preview_api.py tests\integration\test_project_test_plan_draft_api.py -q` passed (5 passed); task-board guard run passed (17 passed).
- Plan: `docs/task_191_matrix_draft_starter_import_and_manual_empty_state_plan.md`.
- `TASK_192_MATRIX_SOURCE_CANDIDATES_AND_BROWSE_FALLBACK_CORRECTION` is complete. Added Project-scoped Matrix source candidate read model from project `file_assets`, candidate listing API, and candidate-preview API so Workbench starter can preview by selected source asset instead of path-first only. Matrix starter now prioritizes project source candidates, keeps external Browse/path fallback, and keeps manual Matrix as final fallback. Draft creation from preview now persists `source_asset_id` when preview came from a project candidate.
- Validation: `python -m pytest tests\unit\test_matrix_source_candidate_service.py tests\integration\test_project_test_plan_source_candidates_api.py -q` passed (5 passed); `python -m pytest tests\integration\test_project_test_plan_preview_api.py tests\integration\test_project_test_plan_draft_api.py -q` passed (5 passed); `python -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix or task191 or task192"` passed (10 passed); `npm run build` from `frontend` passed.
- Plan: `docs/task_192_matrix_source_candidates_and_browse_fallback_correction_plan.md`.
- Next recommended action: wait for explicit approval of the next controlled task before starting implementation.

- `TASK_166_LTR_PROJECT_TYPE_WORKBOOK_MAPPING` is complete (controlled backend hotfix). LTR workbook E-column `Project Type` now uses backend-controlled mapping and blocks unmapped values before workbook write/commit: `New Product Development->NPD`, `Product Extension->PEX`, `Innovation->ADM`, `Lab Activities (Lab Use Only)->ADM`, `Operational Support->OPS`, `Cost Reduction->CR`. Commit path now converts preview mapping failures into `LtrWorkbookWriteCommitError` for a stable application boundary.
- Validation: `py -m pytest tests\unit\test_ltr_workbook_write_preview_service.py -q` passed (6 passed); `py -m pytest tests\unit\test_ltr_workbook_write_commit_service.py -q` passed (13 passed); `py -m pytest tests\integration\test_ltr_workbook_write_preview_api.py -q` passed (1 passed).
- `TASK_167_LTR_J_COLUMN_DROPDOWN_AUTO_EXPAND` is complete (controlled backend workflow hardening, corrected scope). During workbook-authority commit, backend now ensures J-column dropdown source contains the selected application-form `Mfg. Site` (`manufacturing_site`): it reads legacy validation source range (for example `=$AB$1:$AB$36`), checks normalized duplicates, appends missing site value at AB tail, and expands source range by one row before row write. `Location` is no longer used for J-column mapping in this flow. Commit audit notes include dropdown append/range details. `Test Type in sheet` logic remains unchanged and required.
- Validation: `py -m pytest tests\unit\test_excel_com_ltr_workbook_gateway.py -q` passed (11 passed); `py -m pytest tests\unit\test_ltr_workbook_write_commit_service.py -q` passed (14 passed); `py -m pytest tests\integration\test_ltr_workbook_write_commit_api.py tests\integration\test_new_project_completion_api.py -q` passed (9 passed); `py -m pytest tests\unit\test_ltr_excel_authority_adapter.py tests\unit\test_ltr_workbook_transaction_gateway.py -q` passed (9 passed).
- `TASK_168_NEW_PROJECT_REMOVE_LOCATION_USE_MFG_SITE` is complete (frontend scope cleanup). New Project setup confirmation no longer shows `Location*`; completion payload no longer sends `location`; setup required checks no longer include `location`; `Test Type in sheet*` remains unchanged and required. Backend completion endpoint remains compatible with optional `location` input for transition safety.
- Validation: `npm run build` passed from `frontend`; `py -m pytest tests\integration\test_new_project_completion_api.py -q` passed (6 passed); targeted frontend shell run `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "new_project or intake or setup"` reported 2 historical static assertion failures unrelated to TASK_168 (`test_task087_intake_information_density_cleanup`, `test_task091_intake_precheck_typography_uses_shared_ui_vocabulary`) and 20 passed/36 deselected.
- `TASK_169_LTR_WORKBOOK_VIEW_STATE_NORMALIZATION` is complete (backend workbook hardening). LTR workbook write session now provides `prepare_sheet_for_operation` and clears active sheet filters before write flow so shared-workbook residual view state (saved filter mode) does not block full-range operations. Commit path now calls sheet preparation before dropdown ensure and row write. This preparation seam is reusable for future read-only workbook query flows.
- Validation: `py -m pytest tests\unit\test_excel_com_ltr_workbook_gateway.py -q` passed (13 passed); `py -m pytest tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py -q` passed (17 passed).
- `TASK_170_LTR_COMMIT_UNHIDE_ROWS_COLUMNS` is complete (backend operational consistency). Workbook sheet preparation now not only clears active filters but also unhides rows and columns in used-range scope before LTR write operations. Commit flow still does not restore prior view state after completion, so the saved workbook remains in an operator-friendly full-view state for the next user.
- Validation: `py -m pytest tests\unit\test_excel_com_ltr_workbook_gateway.py -q` passed (13 passed); `py -m pytest tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py -q` passed (17 passed).
- `TASK_171_NEW_PROJECT_UNIQUE_DRAFT_REINITIALIZE_REBUILD` is complete (duplicate-flow simplification hardening). Same-identity `Reinitialize` now performs clean draft rebuild semantics in place: existing draft for the target case is deleted (`delete_by_case`) and a fresh draft record is created, preventing residual manual override/history payload leakage while preserving a single active draft identity path. `Load existing` behavior remains unchanged and does not create new case/draft records.
- Validation: `py -m pytest tests\unit\test_intake_form_selection_service.py -q` passed (20 passed); `py -m pytest tests\integration\test_msg_package_intake_api.py -q` passed (16 passed); `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "duplicate or new_project"` passed (8 passed, 50 deselected).
- `TASK_172_NEW_PROJECT_DUPLICATE_DRAFT_HISTORY_CLEANUP` is complete (backend cleanup control). Added duplicate draft history cleanup service and API to keep one latest unconfirmed draft package per identical MSG email identity, and to delete redundant package graph + intake folder (`draft -> case -> asset -> package -> Data/intake/<package_id>`). Confirmed or incomplete chains are skipped with reasons in dry-run/execute response.
- Validation: `py -m pytest tests/unit/test_duplicate_draft_history_cleanup_service.py tests/integration/test_cleanup_api.py -q` passed (5 passed).
- `TASK_173_UNIFIED_DUPLICATE_PROMPT_WITH_DRAFT_CHANGE_GUARD` is complete (duplicate UX consistency hardening). Single-form and multi-form duplicate handling now share the same prompt contract for unconfirmed draft duplicates. Frontend adds guarded same-session decision reuse only when case/asset target is unchanged and no draft edit occurred since prior resolution.
- Validation: `py -m pytest tests/unit/test_intake_form_selection_service.py -q` passed (21 passed); `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "duplicate or new_project"` passed (8 passed, 50 deselected); `npm run build` from `frontend` passed.

---

## 1. Purpose

This board is stricter than a normal TODO list.

It is the shared execution control document for both humans and AI tools. It defines:

- required read order
- current mainline
- allowed active task
- phase status
- acceptance gates
- what must be updated after each completed task

If conversational memory conflicts with this board, this board wins.

---

## 2. Required Read Order For AI

Every new execution turn must read and obey documents in this order:

1. `AGENTS.md`
2. `docs/task_board.md`
3. current active task file in `tasks/`
4. only then expand any additional referenced docs if the task requires them

Control meaning:

- `AGENTS.md` defines stable rules, MVP boundaries, forbidden scope, and architecture constraints.
- `docs/task_board.md` defines what task is allowed right now.
- `tasks/TASK_XXX_*.md` defines the implementation target and acceptance criteria for that task.

Minimum operator prompt:

```text
Read AGENTS.md first, then docs/task_board.md, then only the current active task file.
Implement only the active task allowed by docs/task_board.md.
Do not skip ahead.
Before coding, state the current phase and active task ID.
After finishing, update docs/task_board.md with status, validation, and next step.
```

---

## 3. Execution Rules

1. Only one active implementation task is allowed at a time unless the board explicitly opens parallel work.
2. A task may move to `done` only after code, tests, and board update are all completed.
3. If a requested task is ahead of the current active task, AI must stop and report the mismatch.
4. If a task uncovers missing prerequisite work, the board must be updated before moving on.
5. Future-scope work is forbidden even if related files already exist in the repository.
6. Project-wide UI rule: any frontend UI, UX copy, layout, visual design, component, navigation, interaction, frontend smoke expectation, UI critique, UI audit, or UI polish work must use `$impeccable` before design or edits. Backend-only, parser-only, storage-only, Office gateway-only, database-only, and non-UI test work is exempt unless it changes UI behavior or user-facing copy.

---

## 4. Current Mainline

Current judgment as of 2026-04-26:

- Repository scaffold is complete.
- Configuration and logging foundation is complete.
- SQLite persistence foundation is complete.
- MVP domain model foundation is complete.
- MVP database models and repositories are complete.
- Project service and thin API foundation are complete.
- Application form parser foundation is complete.
- Deterministic precheck engine is complete.
- Intake/precheck API is complete.
- LTR registration/tracking module is complete.
- Folder generation preview is complete.
- Safe folder generation execution is complete.
- The project is entering shell integration and packaging.
- Minimal frontend shell is complete.
- MVP workflow integration is complete.
- Packaging notes and local run scripts are complete.
- The MVP task sequence is complete.
- Workbench UX modernization is approved as the next controlled phase.
- The UX baseline and decision record is complete.
- The product app shell and left navigation are complete.
- The project dashboard/table-oriented project registry is complete.
- The project detail page now uses a sequential workflow stepper.
- The precheck issue experience now uses business-readable summary and issue cards.
- The intake, LTR, and folder action panels now provide clearer operator guidance.
- Frontend workflow state and API usage are cleaned up.
- Frontend build and smoke validation guard is documented.
- Phase 5 documentation and board sync are complete.
- Phase 6A has been explicitly approved by the user.
- Phase 6A scope is revised around Outlook `.msg` package intake, application form selection, human confirmation, and direct `.docx` import.
- `TASK_025_PHASE6_SCOPE_REVISION_AND_BOARD_ACTIVATION` is complete.
- `TASK_026_OFFICE_INTEGRATION_BOUNDARY` is complete.
- `TASK_027A_OUTLOOK_MSG_SOURCE_IMPORT_AND_MINIMAL_METADATA` is complete.
- `TASK_027B_OUTLOOK_MSG_ATTACHMENT_EXTRACTION` is complete.
- `TASK_027C_REAL_MSG_SAMPLE_COMPATIBILITY` is complete.
- `TASK_028A_INTAKE_STORAGE_BOUNDARY` is complete.
- Phase 6A validation is complete.
- Phase 6A plan was completed as split `.msg` import, intake storage, intake UI, confirmation, direct Word intake, and attachment-aware precheck tasks.
- Phase 7 has been explicitly approved by the user.
- `TASK_036_PHASE7_SCOPE_AND_BOARD_ACTIVATION` is complete.
- `TASK_037_REAL_SAMPLE_BASELINE` is complete.
- `TASK_038_REAL_DOCX_PARSER_CALIBRATION` is complete.
- `TASK_039_LTR_FIELD_CATALOG_AND_READINESS_SOURCE_MAP` is complete.
- `TASK_040_LTR_NUMBER_RULES` is complete.
- `TASK_041_LTR_WORKBOOK_SNAPSHOT_GATEWAY` is complete.
- `TASK_042_LTR_READINESS_SERVICE_AND_API` is complete.
- `TASK_043_LTR_REGISTRATION_PREVIEW` is complete.
- `TASK_044_LTR_LOCAL_COMMIT_AND_AUDIT_RECORD` is complete.
- `TASK_045_LTR_EXCEL_WRITE_GATEWAY_AND_SYNC` is complete.
- `TASK_046_LTR_RENUMBER_AND_PROJECT_FOLDER_RENAME_PLAN` is complete.
- `TASK_047_FOLDER_EVIDENCE_PLACEMENT_RULES` is complete.
- `TASK_048_PROJECT_LIFECYCLE_GATING` is complete.
- `TASK_049_EXCEPTION_WORKFLOWS` is complete.
- `TASK_050_LOOKUP_SURFACES_FOR_SAMPLE_AND_TEST_CONDITIONS` is complete.
- Phase 7 is complete for real sample baseline, parser calibration, LTR readiness/preview, folder evidence placement, lifecycle guards, exception workflows, lookup surfaces, validation, and documentation sync.
- Phase 8 has been explicitly approved by the user for DL-centric project identity hardening.
- `TASK_052_PROJECT_NO_OPTIONAL_DL_CENTRIC_IDENTITY` is complete.
- Application `Project #` is optional metadata; internal IDs preserve pre-LTR continuity, and DL/LTR number is the business identity after registration.
- Phase 9 has been explicitly approved by the user after manual smoke testing.
- `TASK_053_PHASE9_SCOPE_AND_BOARD_ACTIVATION` is complete.
- Phase 9 is activated for frontend operator workflow wiring of existing Phase 7/8 backend capabilities.
- `TASK_054_LTR_READINESS_PREVIEW_COMMIT_FRONTEND_WIRING` is complete.
- LTR readiness, no-write preview, and local-only commit are wired into the frontend workflow with explicit operator confirmation and workbook-write caveats.
- `TASK_055_INTAKE_EXCEPTION_WORKFLOW_FRONTEND_WIRING` is complete.
- Intake package exception review, no-form outcome guidance, multi-form separate case creation, and missing-info confirmation blockers are wired into the frontend.
- `TASK_056_FOLDER_EVIDENCE_PLACEMENT_FRONTEND_WIRING` is complete.
- Evidence placement preview, no-overwrite execution, category display, warnings, and conflicts are wired into the frontend project folder workflow.
- `TASK_057_PROJECT_LOOKUP_SAMPLE_TESTING_SUMMARY_FRONTEND_PANEL` is complete.
- Read-only project lookup, sample summary, and testing condition/method summary are wired into the frontend project workbench.
- `TASK_058_LIFECYCLE_GUARDS_DISABLED_REASON_UI` is complete.
- Lifecycle guard disabled-state reasons are visible inline for LTR, folder, and evidence actions.
- `TASK_059_PHASE9_BROWSER_SMOKE_AND_DOCS_SYNC` is complete.
- Phase 9 validation summary, manual browser smoke checklist, board sync, and next recommendation are complete.
- Phase 10A has been explicitly approved by the user as an intake-entry correction before copied-workbook LTR write hardening.
- `TASK_060_PHASE10A_SCOPE_AND_BOARD_ACTIVATION` is complete.
- Phase 10A is activated for manual `.msg` package import and no-email manual intake entry completion.
- `TASK_061_MSG_PACKAGE_IMPORT_API_AND_FRONTEND_ENTRY` is complete.
- Manual `.msg` package import is wired through the Intake UI, API client, FastAPI route, application service, OfficeFacade, intake storage, and repositories.
- `TASK_062_INTAKE_PACKAGE_DETAIL_REAL_DATA_WIRING` is complete.
- Intake package detail now loads real package metadata, source preservation state, stored assets, candidate application forms, and case summaries from backend data.
- `TASK_063_DIRECT_MANUAL_INTAKE_ENTRY` is complete.
- No-email manual intake now creates structured package, asset, case, and draft records before project creation, with missing required fields returned to the UI.
- Copied-workbook LTR write hardening is deferred until after intake entry completion.
- `TASK_076_FRONTEND_ARCHITECTURE_RULES_AND_UI_BOUNDARY` is complete.
- `docs/frontend_architecture_rules.md` now defines page, feature, component, API, state, selector, config, styling, and review boundaries for future UI work.
- `TASK_077_INTAKE_PRECHECK_BUSINESS_GAP_AUDIT` is complete.
- `docs/intake_precheck_business_gap_audit.md` now records current Intake/Precheck UI, backend contract, parser, persistence, mock-content, and workflow gaps before any broad UI completion work.
- `TASK_078_INTAKE_PRECHECK_FIELD_CONTRACT_AND_SECTION1_RULES` is complete.
- `docs/intake_precheck_field_contract.md` now defines SECTION 1 project-creation fields, warning/blocker/auto-clear states, sample edit rules, lookup groups, direct `.docx` policy, draft-level precheck scope, and source `.msg` display policy.
- `TASK_079_LOOKUP_OPTIONS_BACKEND_AND_API` is complete.
- Backend-managed Intake/Precheck lookup options now have SQLite persistence, a repository/service boundary, first-run default seed values, and a read-only API endpoint.
- `TASK_080_DOCX_PARSER_FIELD_CALIBRATION_FOR_SECTION1` is complete.
- E-3718 Rev H parser calibration now prevents neighboring labels from being accepted as values and reads SECTION 1 content-control values such as Phone, Date, Business Unit, Mfg. Site, and downstream dropdown fields from the real local sample.
- `TASK_081_FRONTEND_LOOKUP_API_FIELD_RENDERER_WIRING` is complete.
- Precheck select fields now load backend-managed lookup options through `GET /api/lookups/intake-precheck`; `Post-Testing Sample Disposition` uses the same shared field renderer as other lookup fields.
- `TASK_082_PRECHECK_SAMPLE_ROW_EDIT_COPY_DELETE_UI` is complete.
- Precheck sample rows are now editable before Project confirmation, with compact edit/copy/delete icon actions and draft persistence through the review update API.
- `TASK_083_PREPROJECT_SECTION1_PRECHECK_AND_CONFIRMATION_GUIDANCE` is complete.
- Precheck review now runs deterministic SECTION 1 pre-project checks, blocks Project confirmation on error-level issues, shows warnings, clears prefilled Lab Test Request Number in the draft view, and excludes SECTION 2 lab fields from pre-project blockers.
- `TASK_084_PRECHECK_FRONTEND_STRUCTURE_EXTRACTION` is complete.
- Precheck route page now composes named feature components from `frontend/src/features/precheck`; field config, sample config, issue summary, source check, lower panels, messages, state panel, and pure selectors are outside the route page while behavior is preserved.
- `TASK_085_INTAKE_SESSION_PERSISTENCE` is complete.
- Intake session now persists through browser refresh with `sessionStorage`, falls back safely when storage is unavailable or invalid, and clears after successful Project confirmation.
- `TASK_086_DIRECT_WORD_APPLICATION_FORM_UPLOAD_WIRING` is complete.
- New Project Intake `Upload application form` now imports direct Word files through the backend and creates the same package/asset/candidate flow as email-based intake.
- `TASK_087_INTAKE_INFORMATION_DENSITY_AND_ATTACHMENT_LIST_CLEANUP` is complete.
- New Project Intake now shows a concise source summary with sender email, subject, and date; attachment rows prioritize file names and application-form selection without separate type/size columns.
- `TASK_088_ATTACHMENT_DETAILS_PREVIEW_COMPLETION` is complete.
- Intake Attachment details now renders inline image previews, keeps application-form Word previews focused on business fields and sample/requested-testing content, and shows metadata-only details for Excel, PDF, MSG, non-application Word, and other files.
- TASK_088 sample preview correction is complete: Attachment details `Test Sample Information` now matches the application-form / Precheck sample columns, including combined `Part Number / Revision`, contact material/plating/lubricant, housing material, and quantity, without changing persisted sample storage schema.
- `TASK_090_INTAKE_WORKFLOW_STRUCTURE_EXTRACTION` is complete.
- Intake source panel, attachment list, attachment preview panel, and pure display selectors now live under `frontend/src/features/intake`; the shared New Project workflow stepper no longer shows the redundant heading row, keeps labels on one line in narrow windows, and prevents connector lines from crossing text.
- `TASK_091_INTAKE_PRECHECK_MANUAL_SMOKE_AND_UI_POLISH_BACKLOG` is complete.
- `TASK_093_EMAIL_PACKAGE_MISSING_FORM_UPLOAD_CONTINUATION` is complete: an imported email package without a detected application form can continue by uploading a Word application form into the same package while preserving the source email and original attachments.
- `TASK_094_INTAKE_APPLICATION_FORM_HEADER_GATE` is complete: Intake to Precheck is gated by `.docx` plus Laboratory Testing Request header table cell `(1,2)` validation through the OfficeFacade boundary, with backend selection enforcement and frontend disabled reasons.
- TASK_094 manual smoke hotfix is complete: every attachment selection now refreshes the footer guidance and `Continue to Precheck` state from the current selected file.
- TASK_094 supplemental upload hotfix is complete: uploading a `.docx` into an email package now returns a business-readable 400 validation message when the header gate fails instead of surfacing `Internal Server Error`.
- Intake and Precheck now share a small UI typography/action vocabulary for panel titles, preview titles, section titles, primary actions, secondary actions, and compact actions. Static frontend shell tests guard the shared vocabulary on key Intake/Precheck components.
- `TASK_095_SINGLE_ACTIVE_PRECHECK_CASE_PER_INTAKE_SESSION` is complete: repeated Intake to Precheck navigation now keeps one active unconfirmed review case, preserves edits only for the same selected form, clears manual overrides when rebinding to a different form, and removes the Precheck `Review cases` card.
- Project creation continuation decisions are captured as proposed task series:
  - `TASK_096_PROJECT_CREATION_DRAFT_LIFECYCLE`: complete; explicit `Save draft and exit` versus `Exit without saving`, including deletion of ConnLab-owned unsaved database rows and stored files.
  - `TASK_097_DRAFTS_IN_PROGRESS_SURFACE`: complete; separate Drafts / In Progress area with `Continue` / `Discard`, distinct from confirmed Projects using `Open`.
  - `TASK_098_PRECHECK_CONFIRMED_APPLICATION_EDITING`: complete; removed Precheck `Back to Intake` and treats Precheck as the confirmed application-data editing surface.
  - `TASK_099_LTR_REGISTERED_FREEZE_AND_EXCEPTION_PATH`: freeze normal Precheck base-field editing after LTR registration and use revise/exception for later changes.
  - `TASK_100_PROJECT_WORKBENCH_BOUNDARY_AFTER_FOLDER_CREATION`: keep Project Workbench focused on confirmed projects, folder state, and file/source material management.
- No Matrix, Report, AI review, LAN deployment, permissions, Outlook inbox auto-scan, email sending, external LTR workbook mutation, or future-scope work is allowed in Phase 9 or Phase 10A.

Current stop point:

- `TASK_001_REPOSITORY_SCAFFOLD` is complete.
- `TASK_002_CONFIG_LOGGING` is complete.
- `TASK_003_SQLITE_DATABASE` is complete.
- `TASK_004_DOMAIN_MODELS_MVP` is complete.
- `TASK_005_DATABASE_MODELS_AND_REPOSITORIES` is complete.
- `TASK_006_PROJECT_SERVICE_AND_API` is complete.
- `TASK_007_APPLICATION_FORM_PARSER` is complete.
- `TASK_008_PRECHECK_ENGINE` is complete.
- `TASK_009_INTAKE_PRECHECK_API` is complete.
- `TASK_010_LTR_MODULE` is complete.
- `TASK_011_FOLDER_PREVIEW` is complete.
- `TASK_012_FOLDER_GENERATION` is complete.
- `TASK_013_MINIMAL_FRONTEND_SHELL` is complete.
- `TASK_014_MVP_WORKFLOW_INTEGRATION` is complete.
- `TASK_015_PACKAGING_NOTES` is complete.
- `TASK_016_UX_BASELINE_AND_DECISION_RECORD` is complete.
- `TASK_017_APP_SHELL_LEFT_NAV` is complete.
- `TASK_018_PROJECT_DASHBOARD` is complete.
- `TASK_019_PROJECT_WORKBENCH_STEPPER` is complete.
- `TASK_020_PRECHECK_ISSUE_EXPERIENCE` is complete.
- `TASK_021_INTAKE_LTR_FOLDER_UX` is complete.
- `TASK_022_FRONTEND_STATE_AND_API_CLEANUP` is complete.
- `TASK_023_FRONTEND_TEST_AND_BUILD_GUARD` is complete.
- `TASK_024_PHASE5_DOCS_AND_BOARD_SYNC` is complete.
- `TASK_025_PHASE6_SCOPE_REVISION_AND_BOARD_ACTIVATION` is complete.
- `TASK_026_OFFICE_INTEGRATION_BOUNDARY` is complete.
- `TASK_027A_OUTLOOK_MSG_SOURCE_IMPORT_AND_MINIMAL_METADATA` is complete.
- `TASK_027B_OUTLOOK_MSG_ATTACHMENT_EXTRACTION` is complete.
- `TASK_027C_REAL_MSG_SAMPLE_COMPATIBILITY` is complete.
- `TASK_028A_INTAKE_STORAGE_BOUNDARY` is complete.
- `TASK_028B_INTAKE_PACKAGE_ASSET_CASE_STORAGE` is complete.
- `TASK_029_APPLICATION_FORM_CANDIDATE_DETECTION` is complete.
- `TASK_030_FORM_SELECTION_AND_DRAFT_CREATION` is complete.
- `TASK_031A_INTAKE_INBOX_FRONTEND_UX` is complete.
- `TASK_031B_INTAKE_PACKAGE_DETAIL_FRONTEND_UX` is complete.
- `TASK_031C_INTAKE_CASE_REVIEW_FRONTEND_UX` is complete.
- `TASK_032_CONFIRM_INTAKE_CASE_TO_PROJECT` is complete.
- `TASK_033_DIRECT_WORD_APPLICATION_FORM_IMPORT` is complete.
- `TASK_034_ATTACHMENT_AWARE_PRECHECK_BRIDGE` is complete.
- `TASK_035_PHASE6_VALIDATION_AND_DOCS_SYNC` is complete.
- `TASK_036_PHASE7_SCOPE_AND_BOARD_ACTIVATION` is complete.
- `TASK_037_REAL_SAMPLE_BASELINE` is complete.
- `TASK_038_REAL_DOCX_PARSER_CALIBRATION` is complete.
- `TASK_039_LTR_FIELD_CATALOG_AND_READINESS_SOURCE_MAP` is complete.
- `TASK_040_LTR_NUMBER_RULES` is complete.
- `TASK_041_LTR_WORKBOOK_SNAPSHOT_GATEWAY` is complete.
- `TASK_042_LTR_READINESS_SERVICE_AND_API` is complete.
- `TASK_043_LTR_REGISTRATION_PREVIEW` is complete.
- `TASK_044_LTR_LOCAL_COMMIT_AND_AUDIT_RECORD` is complete.
- `TASK_045_LTR_EXCEL_WRITE_GATEWAY_AND_SYNC` is complete.
- `TASK_046_LTR_RENUMBER_AND_PROJECT_FOLDER_RENAME_PLAN` is complete.
- `TASK_047_FOLDER_EVIDENCE_PLACEMENT_RULES` is complete.
- `TASK_048_PROJECT_LIFECYCLE_GATING` is complete.
- `TASK_049_EXCEPTION_WORKFLOWS` is complete.
- `TASK_050_LOOKUP_SURFACES_FOR_SAMPLE_AND_TEST_CONDITIONS` is complete.
- `TASK_051_PHASE7_VALIDATION_AND_DOCS_SYNC` is complete.
- `TASK_052_PROJECT_NO_OPTIONAL_DL_CENTRIC_IDENTITY` is complete.
- `TASK_053_PHASE9_SCOPE_AND_BOARD_ACTIVATION` is complete.
- `TASK_054_LTR_READINESS_PREVIEW_COMMIT_FRONTEND_WIRING` is complete.
- `TASK_055_INTAKE_EXCEPTION_WORKFLOW_FRONTEND_WIRING` is complete.
- `TASK_056_FOLDER_EVIDENCE_PLACEMENT_FRONTEND_WIRING` is complete.
- `TASK_057_PROJECT_LOOKUP_SAMPLE_TESTING_SUMMARY_FRONTEND_PANEL` is complete.
- `TASK_058_LIFECYCLE_GUARDS_DISABLED_REASON_UI` is complete.
- `TASK_059_PHASE9_BROWSER_SMOKE_AND_DOCS_SYNC` is complete.
- `TASK_060_PHASE10A_SCOPE_AND_BOARD_ACTIVATION` is complete.
- `TASK_061_MSG_PACKAGE_IMPORT_API_AND_FRONTEND_ENTRY` is complete.
- `TASK_062_INTAKE_PACKAGE_DETAIL_REAL_DATA_WIRING` is complete.
- `TASK_063_DIRECT_MANUAL_INTAKE_ENTRY` is complete.
- `TASK_064_UNIFIED_INTAKE_CASE_REVIEW_AND_CONFIRMATION_UI` is complete.
- `TASK_065_INTAKE_ENTRY_BROWSER_SMOKE_AND_DOCS_SYNC` is complete.
- `TASK_066_PHASE10A_SMOKE_BLOCKER_FIXES` is complete.
- `TASK_067_PROJECTS_REGISTRY_AND_LTR_NUMBER_TERMINOLOGY_REALIGNMENT` is complete.
- `TASK_068_REFERENCE_STYLE_PROJECTS_UI_POLISH` is complete.
- `TASK_069_STEP_STYLE_NEW_PROJECT_INTAKE_UI` is complete.
- `TASK_070_STEP_STYLE_PRECHECK_UI` is complete.
- `TASK_071_INTAKE_PRECHECK_SESSION_STATE` is complete.
- `TASK_072_PRECHECK_ENTRY_CASE_CREATION_AND_STYLE_FIX` is complete.
- `TASK_073_SELECTED_FORM_PRECHECK_BINDING_HOTFIX` is complete.
- `TASK_074_PRECHECK_DYNAMIC_WORD_DATA_DISPLAY_HOTFIX` is complete.
- `TASK_075_INTAKE_ATTACHMENT_PREVIEW_AND_DOCX_PRIORITY` is complete.
- `TASK_076_FRONTEND_ARCHITECTURE_RULES_AND_UI_BOUNDARY` is complete.
- `TASK_077_INTAKE_PRECHECK_BUSINESS_GAP_AUDIT` is complete.
- `TASK_078_INTAKE_PRECHECK_FIELD_CONTRACT_AND_SECTION1_RULES` is complete.
- `TASK_079_LOOKUP_OPTIONS_BACKEND_AND_API` is complete.
- `TASK_080_DOCX_PARSER_FIELD_CALIBRATION_FOR_SECTION1` is complete.
- `TASK_081_FRONTEND_LOOKUP_API_FIELD_RENDERER_WIRING` is complete.
- `TASK_082_PRECHECK_SAMPLE_ROW_EDIT_COPY_DELETE_UI` is complete.
- `TASK_083_PREPROJECT_SECTION1_PRECHECK_AND_CONFIRMATION_GUIDANCE` is complete.
- `TASK_084_PRECHECK_FRONTEND_STRUCTURE_EXTRACTION` is complete.
- `TASK_085_INTAKE_SESSION_PERSISTENCE` is complete.
- `TASK_086_DIRECT_WORD_APPLICATION_FORM_UPLOAD_WIRING` is complete.
- `TASK_087_INTAKE_INFORMATION_DENSITY_AND_ATTACHMENT_LIST_CLEANUP` is complete.
- `TASK_088_ATTACHMENT_DETAILS_PREVIEW_COMPLETION` is complete.
- `TASK_091_INTAKE_PRECHECK_MANUAL_SMOKE_AND_UI_POLISH_BACKLOG` is complete.
- `TASK_093_EMAIL_PACKAGE_MISSING_FORM_UPLOAD_CONTINUATION` is complete.
- `TASK_094_INTAKE_APPLICATION_FORM_HEADER_GATE` is complete.
- TASK_094 manual smoke hotfix is complete.
- TASK_094 supplemental upload 500 hotfix is complete.
- `TASK_095_SINGLE_ACTIVE_PRECHECK_CASE_PER_INTAKE_SESSION` is complete.
- No implementation task is active. Await explicit user approval for the next task.

---

## 5. Phase Status

### Phase 0 - Repository Initialization

Goal:

- establish repository structure
- make FastAPI app importable
- add a passing smoke test

Status table:

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T0-1 | `TASK_001_REPOSITORY_SCAFFOLD` | done | Scaffold, package init files, `/health`, smoke test completed on 2026-04-25 |

Acceptance gate:

- backend package exists
- minimal FastAPI app imports
- `/health` returns `{"status": "ok"}`
- smoke test passes

### Phase 1 - Backend MVP Foundation

Goal:

- establish configuration, logging, storage foundation, domain skeleton, and application-facing API flow for MVP

Status table:

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T1-1 | `TASK_002_CONFIG_LOGGING` | done | `Settings.load()` and `configure_logging()` landed with tests on 2026-04-25 |
| T1-2 | `TASK_003_SQLITE_DATABASE` | done | SQLite engine, session factory, Base, `init_db()`, and tests completed on 2026-04-26 |
| T1-3 | `TASK_004_DOMAIN_MODELS_MVP` | done | Pure dataclass domain models and enums completed on 2026-04-26 |
| T1-4 | `TASK_005_DATABASE_MODELS_AND_REPOSITORIES` | done | SQLAlchemy models and repositories completed with temp SQLite tests on 2026-04-26 |
| T1-5 | `TASK_006_PROJECT_SERVICE_AND_API` | done | Project service and `/api/projects` create/list/detail routes completed on 2026-04-26 |

Acceptance gate:

- settings and logger are explicit
- database location comes from settings
- MVP domain objects exist as structured records
- project service and thin API route layer are established

### Phase 2 - Intake And Precheck Flow

Goal:

- parse application form
- run deterministic precheck
- expose intake/precheck API path

Status table:

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T2-1 | `TASK_007_APPLICATION_FORM_PARSER` | done | DOCX parser with synthetic fixture tests completed on 2026-04-26 |
| T2-2 | `TASK_008_PRECHECK_ENGINE` | done | Deterministic precheck rules completed with rule tests on 2026-04-26 |
| T2-3 | `TASK_009_INTAKE_PRECHECK_API` | done | Upload, parse, precheck, latest, and issue resolve API completed on 2026-04-26 |

Acceptance gate:

- application form fields are parsed into structured records
- precheck is deterministic
- route layer stays thin

### Phase 3 - LTR And Folder Flow

Goal:

- support LTR registration/tracking
- support folder preview and safe generation

Status table:

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T3-1 | `TASK_010_LTR_MODULE` | done | LTR registration, project lookup, search, and duplicate protection completed on 2026-04-26 |
| T3-2 | `TASK_011_FOLDER_PREVIEW` | done | Template scan, placeholder replacement, and conflict preview completed on 2026-04-26 |
| T3-3 | `TASK_012_FOLDER_GENERATION` | done | Safe folder generation, original application form copy, persistence, and overwrite protection completed on 2026-04-26 |

Acceptance gate:

- LTR is structured and persisted
- folder generation is previewable
- no unsafe overwrite behavior

### Phase 4 - Shell Integration And Packaging

Goal:

- add minimal frontend shell
- connect MVP workflow
- document packaging notes

Status table:

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T4-1 | `TASK_013_MINIMAL_FRONTEND_SHELL` | done | Minimal React + TypeScript shell with project list/detail and MVP task cards completed on 2026-04-26 |
| T4-2 | `TASK_014_MVP_WORKFLOW_INTEGRATION` | done | Frontend workflow actions, backend full-flow test, and manual smoke checklist completed on 2026-04-26 |
| T4-3 | `TASK_015_PACKAGING_NOTES` | done | Windows local run scripts, README setup/run guide, and packaging notes completed on 2026-04-26 |

Acceptance gate:

- frontend remains minimal
- integration only covers MVP flow
- packaging notes reflect real repository state

### Phase 5 - Workbench UX Modernization

Goal:

- convert the MVP prototype frontend into a modern workflow-oriented ConnLab workbench
- establish left navigation, project dashboard, project workbench, workflow stepper, business-readable issue display, and frontend validation guard

Mandatory project-wide UI rule as applied in Phase 5:

- Use `$impeccable` for every UX/UI design, frontend interface change, visual polish, layout change, UX copy change, component extraction, audit, or critique.
- Before editing UI, load `$impeccable` context and follow `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json`.
- Treat ConnLab as `register: product`.
- If the `$impeccable` context files are missing or stale, refresh them before UI work.
- Backend-only bug fixes are exempt from this rule.

Status table:

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T5-1 | `TASK_016_UX_BASELINE_AND_DECISION_RECORD` | done | UX decision record, status vocabulary, target layout, and component structure completed on 2026-04-26 |
| T5-2 | `TASK_017_APP_SHELL_LEFT_NAV` | done | Product app shell, left navigation, top context bar, and hero removal completed on 2026-04-26 |
| T5-3 | `TASK_018_PROJECT_DASHBOARD` | done | Searchable project registry, compact new project panel, status badges, and explicit empty/loading/error states completed on 2026-04-26 |
| T5-4 | `TASK_019_PROJECT_WORKBENCH_STEPPER` | done | Project summary, sequential workflow stepper, single active action panel, and blocked/ready/done/warning states completed on 2026-04-26 |
| T5-5 | `TASK_020_PRECHECK_ISSUE_EXPERIENCE` | done | Business-readable precheck summary, severity badges, issue cards, and mark-reviewed action completed on 2026-04-26 |
| T5-6 | `TASK_021_INTAKE_LTR_FOLDER_UX` | done | Upload metadata panel, latest LTR panel, tree-like folder preview, conflict display, and safer generate affordance completed on 2026-04-26 |
| T5-7 | `TASK_022_FRONTEND_STATE_AND_API_CLEANUP` | done | Workflow state derivation extracted, workbench page reduced, and raw fetch usage guarded to API client on 2026-04-26 |
| T5-8 | `TASK_023_FRONTEND_TEST_AND_BUILD_GUARD` | done | Frontend smoke checklist, root build script, README validation command, and static documentation checks completed on 2026-04-26 |
| T5-9 | `TASK_024_PHASE5_DOCS_AND_BOARD_SYNC` | done | Phase 5 decision record, board state, validation summary, and next-phase recommendation synced on 2026-04-26 |

Acceptance gate:

- left navigation workbench shell exists
- project dashboard is usable by non-programmer lab engineers
- project detail page uses sequential workflow stepper
- precheck issues are business-readable
- application/LTR/folder actions are easier to operate
- existing MVP backend workflow still works
- backend tests pass
- frontend build passes
- manual smoke checklist passes

---

### Phase 6A - Outlook Email Package Intake, Application Form Selection And Human Confirmation

Goal:

- introduce the real intake boundary for request materials that usually arrive as an Outlook `.msg` package
- support direct Word `.docx` application form import through the same intake path
- enforce that one selected application form creates one project
- keep parser output as a draft until human review and confirmation
- establish OfficeFacade as the only Office integration boundary

Mandatory Phase 6A rules:

- Do not model one email as one project.
- Use `IntakePackage -> IntakeAsset -> IntakeCase -> IntakeDraft -> Confirm Project` as the planned flow.
- Parser output is draft data only.
- Office-related file reading/extraction must enter through `backend/infrastructure/office/`.
- Phase 6A does not implement Outlook inbox auto-scan, email sending, Matrix, Report, AI review, Excel result ingestion, permissions, LAN deployment, or folder template UX.
- `.msg` handling is split into source import, attachment extraction, and real-sample compatibility instead of one oversized task.
- Intake UI is split into inbox, package detail, and case review instead of one oversized task.
- Intake file storage gets its own boundary before persistence and attachment handling.
- UI changes in Phase 6A follow the project-wide `$impeccable` rule and the `PRODUCT.md` / `DESIGN.md` / `DESIGN.json` context.

Status table:

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T6A-1 | `TASK_025_PHASE6_SCOPE_REVISION_AND_BOARD_ACTIVATION` | done | Phase 6A scope opened, `TASK_026` activated, and static scope checks added on 2026-04-27 |
| T6A-2 | `TASK_026_OFFICE_INTEGRATION_BOUNDARY` | done | OfficeFacade, Word gateway snapshot, Office lifecycle boundary, and gateway placeholders completed on 2026-04-27 |
| T6A-3 | `TASK_027A_OUTLOOK_MSG_SOURCE_IMPORT_AND_MINIMAL_METADATA` | done | `.msg` source copy, minimal metadata read, source preservation on metadata failure completed on 2026-04-27 |
| T6A-4 | `TASK_027B_OUTLOOK_MSG_ATTACHMENT_EXTRACTION` | done | Fixture-supported attachment extraction, metadata, sha256, and non-destructive failures completed on 2026-04-27 |
| T6A-5 | `TASK_027C_REAL_MSG_SAMPLE_COMPATIBILITY` | done | Compatibility probe added; real sample validation documented as blocked until `.msg` fixtures are provided |
| T6A-6 | `TASK_028A_INTAKE_STORAGE_BOUNDARY` | done | IntakeStorage added for safe names, package/source/attachments/snapshots paths, non-overwrite copy, and sha256 |
| T6A-7 | `TASK_028B_INTAKE_PACKAGE_ASSET_CASE_STORAGE` | done | Added IntakePackage, IntakeAsset, IntakeCase, and IntakeDraft domain/storage persistence with tests on 2026-04-27 |
| T6A-8 | `TASK_029_APPLICATION_FORM_CANDIDATE_DETECTION` | done | Added deterministic application-form candidate scoring and asset role persistence with tests on 2026-04-27 |
| T6A-9 | `TASK_030_FORM_SELECTION_AND_DRAFT_CREATION` | done | Added human form selection service with IntakeCase/IntakeDraft creation and repository coverage on 2026-04-27 |
| T6A-10 | `TASK_031A_INTAKE_INBOX_FRONTEND_UX` | done | Added Intake sidebar route, inbox entry page, import boundary note, and preview queue UI on 2026-04-27 |
| T6A-11 | `TASK_031B_INTAKE_PACKAGE_DETAIL_FRONTEND_UX` | done | Added package detail route, source metadata panel, asset list, and form selection action placement on 2026-04-27 |
| T6A-12 | `TASK_031C_INTAKE_CASE_REVIEW_FRONTEND_UX` | done | Added case review route, selected form context, draft field review rows, manual override placement, and confirmation gate on 2026-04-27 |
| T6A-13 | `TASK_032_CONFIRM_INTAKE_CASE_TO_PROJECT` | done | Added intake confirmation service that creates Project, ApplicationForm, SampleInfo, FileAsset, and confirmed case linkage on 2026-04-27 |
| T6A-14 | `TASK_033_DIRECT_WORD_APPLICATION_FORM_IMPORT` | done | Added direct Word intake service that preserves `.doc/.docx`, creates direct intake package and asset, and reuses candidate detection on 2026-04-27 |
| T6A-15 | `TASK_034_ATTACHMENT_AWARE_PRECHECK_BRIDGE` | done | Registered supporting project attachments are passed into deterministic precheck context on 2026-04-27 |
| T6A-16 | `TASK_035_PHASE6_VALIDATION_AND_DOCS_SYNC` | done | Phase 6A validation summary, manual smoke checklist, backend tests, and frontend build synced on 2026-04-27 |

Acceptance gate:

- `.msg` intake can form a package with source email and assets
- direct `.docx` intake uses the same draft/review/confirm path
- users choose one application form candidate before project creation
- parser output remains editable draft data until confirmation
- confirmed cases create Project, ApplicationForm, SampleInfo, and FileAsset records
- supporting attachments are connected to precheck where relevant
- backend tests pass
- frontend build passes when UI tasks are touched
- manual smoke checklist covers the Phase 6A intake flow

---

### Phase 7 - Real LTR, Folder Evidence, And Lifecycle Governance

Goal:

- prove ConnLab can handle the real laboratory intake-to-registration path using real `.msg`, `.docx`, and LTR workbook samples
- calibrate real application form parsing before downstream automation
- introduce LTR readiness, number preview, local registration, optional workbook integration, evidence placement, lifecycle guards, exception handling, and lookup surfaces in controlled steps

Mandatory Phase 7 rules:

- Start with real sample baseline and parser calibration; do not start with Excel write.
- Keep original `.msg` and `.docx` samples out of Git unless explicitly sanitized.
- Treat `D:\Source\Office Auto\TestDocument\LTR_number.xls` as a local validation backup, not a hard-coded production source.
- Do not write to the real LTR workbook unless a later active task explicitly allows workbook write and settings enable it.
- The LTR workbook password must be configurable; the expected default may be `DGLAB`, but code and tests must not hard-code that value.
- Office/Excel/Word/Outlook access must stay behind `backend/infrastructure/office/`.
- Do not replace current `ProjectStatus` broadly before lifecycle guard requirements are proven.
- Do not implement Matrix, Report, AI review, LAN deployment, permissions, or Outlook inbox auto-scan in Phase 7.
- Any Phase 7 frontend UI, UX copy, layout, workflow display, disabled-state reason, lookup panel, smoke checklist UX expectation, critique, audit, or polish work must use `$impeccable` before design or edits.

Status table:

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T7-1 | `TASK_036_PHASE7_SCOPE_AND_BOARD_ACTIVATION` | done | Phase 7 approved, board section added, and `TASK_037` activated on 2026-04-27 |
| T7-2 | `TASK_037_REAL_SAMPLE_BASELINE` | done | Real `.msg` and `.docx` baseline documented without committing originals on 2026-04-27 |
| T7-3 | `TASK_038_REAL_DOCX_PARSER_CALIBRATION` | done | Real-style parser coverage for footer form/revision, request fields, sample rows, requested testing, and lab section completed on 2026-04-28 |
| T7-4 | `TASK_039_LTR_FIELD_CATALOG_AND_READINESS_SOURCE_MAP` | done | 19-field readiness catalog, source map, severity, fallback, and placeholder policy completed on 2026-04-28 |
| T7-5 | `TASK_040_LTR_NUMBER_RULES` | done | Pure LTR parsing, validation, formatting, suffix/W-prefix support, and monthly sequence rules completed on 2026-04-28 |
| T7-6 | `TASK_041_LTR_WORKBOOK_SNAPSHOT_GATEWAY` | done | Read-only `.xlsx` workbook snapshot gateway, explicit `.xls` unsupported adapter handling, and metadata/LTR number scan completed on 2026-04-28 |
| T7-7 | `TASK_042_LTR_READINESS_SERVICE_AND_API` | done | Readiness service/API, blockers, review-required fields, placeholder policy, and thin route completed on 2026-04-28 |
| T7-8 | `TASK_043_LTR_REGISTRATION_PREVIEW` | done | No-write registration preview, deterministic proposed DL number, readiness mapping, local/workbook conflict reporting, and API smoke completed on 2026-04-28 |
| T7-9 | `TASK_044_LTR_LOCAL_COMMIT_AND_AUDIT_RECORD` | done | Approved preview local commit, duplicate-safe registration, project status update, and notes-based audit snapshot completed on 2026-04-28 |
| T7-10 | `TASK_045_LTR_EXCEL_WRITE_GATEWAY_AND_SYNC` | done | Config-gated OfficeFacade + Excel COM write boundary, real `.xls` layout probe, password config policy, and fake COM gateway tests completed on 2026-04-28 |
| T7-11 | `TASK_046_LTR_RENUMBER_AND_PROJECT_FOLDER_RENAME_PLAN` | done | Non-destructive renumber preview, local duplicate detection, folder/file asset path impacts, and conflict reporting completed on 2026-04-28 |
| T7-12 | `TASK_047_FOLDER_EVIDENCE_PLACEMENT_RULES` | done | Evidence placement preview/execution, real folder shape rules, no-overwrite copy, and API smoke completed on 2026-04-28 |
| T7-13 | `TASK_048_PROJECT_LIFECYCLE_GATING` | done | Project lifecycle guard service, guarded LTR/folder/evidence operations, and business-readable API blocks completed on 2026-04-28 |
| T7-14 | `TASK_049_EXCEPTION_WORKFLOWS` | done | Explicit no-form and multi-form package review, per-form case/draft creation, missing-info confirmation blocks, correction evidence preservation, and renumber reason coverage completed on 2026-04-29 |
| T7-15 | `TASK_050_LOOKUP_SURFACES_FOR_SAMPLE_AND_TEST_CONDITIONS` | done | Read-only project lookup, sample summary, testing summary API, and structured-record search completed on 2026-04-29 |
| T7-16 | `TASK_051_PHASE7_VALIDATION_AND_DOCS_SYNC` | done | Phase 7 validation summary, manual smoke checklist, board sync, workbook limitations, and next recommendation completed on 2026-04-29 |

Acceptance gate:

- all real `.msg` and `.docx` samples have documented expected behavior
- parser handles real `.docx` forms well enough to create reviewable drafts
- LTR field catalog maps all 19 readiness fields to source/fallback/severity/policy
- LTR readiness check blocks incomplete registration correctly
- LTR number rules are deterministic and tested
- workbook snapshot is available before write
- LTR registration preview is available before commit
- local commit is traceable and duplicate-safe
- external workbook write, if enabled, is behind infrastructure gateway and safely releases Excel
- project folder evidence placement preserves original email, selected application form, attachments, specifications, LTR evidence, and correction evidence
- lifecycle guards prevent invalid next actions
- sample info and testing condition/method lookup is available
- no Matrix, Report, AI review, LAN deployment, permissions, Outlook inbox auto-scan, or future-scope feature slipped into Phase 7

---

### Phase 8 - DL-Centric Project Identity Hardening

Goal:

- downgrade application `Project #` / `project_no` from required project identity to optional metadata
- keep pre-LTR continuity on internal `project_id`, `intake_package_id`, and `intake_case_id`
- make post-registration operations and folder naming DL/LTR-centric

Mandatory Phase 8 rules:

- Do not use application `Project #` as a required business key.
- Do not remove compatibility response fields or folder placeholders in a breaking cleanup.
- Keep `{PROJECT_NO}` as an optional legacy placeholder only.
- Do not change LTR number allocation rules or write to the external LTR workbook.
- Do not implement Matrix, Report, AI review, LAN deployment, permissions, or Outlook inbox auto-scan.

Status table:

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T8-1 | `TASK_052_PROJECT_NO_OPTIONAL_DL_CENTRIC_IDENTITY` | done | `project_no` is optional metadata across backend/API/frontend, intake confirmation no longer requires it, legacy SQLite constraint is relaxed, folder docs recommend DL-centric names, and tests/build passed on 2026-04-29 |

Acceptance gate:

- projects can be created without application `Project #`
- intake confirmation works without application `Project #`
- multiple projects with missing `project_no` are allowed
- lookup, summaries, and folder preview tolerate missing `project_no`
- frontend no longer presents Project No. as required identity
- no future-scope feature slipped into Phase 8

---

### Phase 9 - Operator Workflow UI Wiring

Goal:

- wire existing Phase 7/8 backend capabilities into the frontend operator workflow
- make readiness, preview, commit, exception, evidence, lookup, and lifecycle blocked states visible to lab operators
- preserve preview-before-write and DL-centric workflow identity in the UI

Mandatory Phase 9 rules:

- Use `$impeccable` for every frontend UI, UX copy, workflow display, disabled-state reason, lookup panel, browser smoke expectation, critique, audit, or polish task.
- Do not add new backend product behavior unless a Phase 9 task explicitly requires a thin API/client adjustment for existing backend behavior.
- UI must call backend APIs through `frontend/src/api/client.ts`.
- UI must not directly manipulate Office files, project folders, or external LTR workbooks.
- Do not write to the external LTR workbook in Phase 9.
- Do not implement Matrix, Report, AI review, LAN deployment, permissions, Outlook inbox auto-scan, or email sending in Phase 9.

Status table:

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T9-1 | `TASK_053_PHASE9_SCOPE_AND_BOARD_ACTIVATION` | done | Phase 9 scope opened, task sequence added, and `TASK_054` activated on 2026-04-29 |
| T9-2 | `TASK_054_LTR_READINESS_PREVIEW_COMMIT_FRONTEND_WIRING` | done | LTR readiness, no-write preview, explicit local commit confirmation, latest local LTR state, and workbook-write caveats wired into frontend on 2026-04-29 |
| T9-3 | `TASK_055_INTAKE_EXCEPTION_WORKFLOW_FRONTEND_WIRING` | done | Intake exception review API, no-form guidance, multi-form case creation, and missing-info blockers wired into frontend on 2026-04-29 |
| T9-4 | `TASK_056_FOLDER_EVIDENCE_PLACEMENT_FRONTEND_WIRING` | done | Evidence placement preview/execution, no-overwrite state, warnings, and conflicts wired into frontend on 2026-04-29 |
| T9-5 | `TASK_057_PROJECT_LOOKUP_SAMPLE_TESTING_SUMMARY_FRONTEND_PANEL` | done | Read-only lookup, sample summary, and testing condition/method summary wired into frontend on 2026-04-29 |
| T9-6 | `TASK_058_LIFECYCLE_GUARDS_DISABLED_REASON_UI` | done | Lifecycle guard disabled-state reasons for LTR, folder, and evidence actions surfaced inline on 2026-04-29 |
| T9-7 | `TASK_059_PHASE9_BROWSER_SMOKE_AND_DOCS_SYNC` | done | Phase 9 validation summary, browser smoke checklist, board sync, and next recommendation completed on 2026-04-29 |

Acceptance gate:

- LTR readiness, preview, and local commit are usable from frontend without external workbook write
- intake exception workflows are visible and actionable
- evidence placement is previewed before execution
- lookup and summary surfaces are read-only and business-readable
- lifecycle guard blocks are visible as actionable disabled-state reasons
- frontend build passes
- relevant backend tests pass
- no Matrix, Report, AI review, LAN deployment, permissions, Outlook inbox auto-scan, email sending, or external workbook mutation slipped into Phase 9

---

### Phase 10A - Intake Entry Completion

Goal:

- make the project entry point match real lab operations
- support manual `.msg` package import as the primary intake entry
- support no-email direct manual intake as the exception path
- route both entry paths into shared review and confirmation before project creation

Mandatory Phase 10A rules:

- Use `$impeccable` for every frontend UI, UX copy, workflow display, browser smoke expectation, critique, audit, or polish task.
- Do not add Outlook inbox auto-scan or email sending.
- Do not implement Matrix, Report, AI review, LAN deployment, permissions, or external LTR workbook mutation.
- Do not implement copied-workbook LTR write hardening in Phase 10A.
- UI must call backend APIs through `frontend/src/api/client.ts`.
- UI must not directly manipulate Office files, project folders, or external LTR workbooks.

Status table:

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T10A-1 | `TASK_060_PHASE10A_SCOPE_AND_BOARD_ACTIVATION` | done | Phase 10A intake-entry priority documented and `TASK_061` activated on 2026-04-29 |
| T10A-2 | `TASK_061_MSG_PACKAGE_IMPORT_API_AND_FRONTEND_ENTRY` | done | Manual `.msg` package import API, frontend entry, import result summary, and review navigation wired on 2026-04-29 |
| T10A-3 | `TASK_062_INTAKE_PACKAGE_DETAIL_REAL_DATA_WIRING` | done | Real package detail API and frontend source/assets/candidates/cases display wired on 2026-04-29 |
| T10A-4 | `TASK_063_DIRECT_MANUAL_INTAKE_ENTRY` | done | No-email manual intake API, structured draft storage, missing-field response, and frontend entry wired on 2026-04-29 |
| T10A-5 | `TASK_064_UNIFIED_INTAKE_CASE_REVIEW_AND_CONFIRMATION_UI` | done | Unified email/manual case review API, frontend review page, explicit confirmation gate, and confirmation blocker tests on 2026-04-30 |
| T10A-6 | `TASK_065_INTAKE_ENTRY_BROWSER_SMOKE_AND_DOCS_SYNC` | done | Phase 10A validation summary, manual browser smoke checklist, board sync, and next recommendation completed on 2026-04-30 |
| T10A-7 | `TASK_066_PHASE10A_SMOKE_BLOCKER_FIXES` | done | Case review field corrections, intake draft override persistence, and folder/evidence not-ready preview handling completed on 2026-05-01 |
| T10A-8 | `TASK_067_PROJECTS_REGISTRY_AND_LTR_NUMBER_TERMINOLOGY_REALIGNMENT` | done | Projects registry layout, New Project entry, and LTR Number terminology aligned on 2026-05-01 |
| T10A-9 | `TASK_068_REFERENCE_STYLE_PROJECTS_UI_POLISH` | done | Product shell and Projects registry polished closer to the reference layout with 14-inch laptop constraints on 2026-05-01 |
| T10A-10 | `TASK_069_STEP_STYLE_NEW_PROJECT_INTAKE_UI` | done | Step-style New Project Intake page completed with one-email attachment list, Word-only application-form radio selection, and attachment detail workspace on 2026-05-01 |
| T10A-11 | `TASK_070_STEP_STYLE_PRECHECK_UI` | done | Step-style New Project Precheck workspace completed with source/template checks, blocker row, editable key information, sample table, requested testing, and confirmation controls on 2026-05-01 |
| T10A-12 | `TASK_071_INTAKE_PRECHECK_SESSION_STATE` | done | Intake imported package and selected Word application-form state now persists across route changes, with direct Intake to Precheck and Precheck back to Intake navigation on 2026-05-01 |
| T10A-13 | `TASK_072_PRECHECK_ENTRY_CASE_CREATION_AND_STYLE_FIX` | done | Continue to Precheck now prepares review cases through the existing API and Precheck CSS is loaded on 2026-05-01 |
| T10A-14 | `TASK_073_SELECTED_FORM_PRECHECK_BINDING_HOTFIX` | done | Intake-selected Word application form now creates/opens the matching Precheck case and populates draft fields from the selected `.docx` on 2026-05-01 |
| T10A-15 | `TASK_074_PRECHECK_DYNAMIC_WORD_DATA_DISPLAY_HOTFIX` | done | Precheck now displays parsed sample rows and parsed non-standard field values from the selected Word draft instead of reference mock data on 2026-05-01 |
| T10A-16 | `TASK_075_INTAKE_ATTACHMENT_PREVIEW_AND_DOCX_PRIORITY` | done | Intake attachment preview completed on 2026-05-01 |
| T10A-17 | `TASK_076_FRONTEND_ARCHITECTURE_RULES_AND_UI_BOUNDARY` | done | Frontend architecture rules documented on 2026-05-01 |
| T10A-18 | `TASK_077_INTAKE_PRECHECK_BUSINESS_GAP_AUDIT` | done | Intake/Precheck business gap audit documented on 2026-05-01 |
| T10A-19 | `TASK_078_INTAKE_PRECHECK_FIELD_CONTRACT_AND_SECTION1_RULES` | done | Intake/Precheck field contract documented on 2026-05-01 |
| T10A-20 | `TASK_079_LOOKUP_OPTIONS_BACKEND_AND_API` | done | Backend-managed lookup options completed on 2026-05-01 |
| T10A-21 | `TASK_080_DOCX_PARSER_FIELD_CALIBRATION_FOR_SECTION1` | done | Parser calibration for Section 1 fields completed on 2026-05-01 |
| T10A-22 | `TASK_081_FRONTEND_LOOKUP_API_FIELD_RENDERER_WIRING` | done | Frontend lookup API field renderer wiring completed on 2026-05-01 |
| T10A-23 | `TASK_082_PRECHECK_SAMPLE_ROW_EDIT_COPY_DELETE_UI` | done | Sample row edit/copy/delete UI completed on 2026-05-01 |
| T10A-24 | `TASK_083_PREPROJECT_SECTION1_PRECHECK_AND_CONFIRMATION_GUIDANCE` | done | Pre-project Section 1 precheck completed on 2026-05-01 |
| T10A-25 | `TASK_084_PRECHECK_FRONTEND_STRUCTURE_EXTRACTION` | done | Precheck feature component extraction completed on 2026-05-01 |
| T10A-26 | `TASK_085_INTAKE_SESSION_PERSISTENCE` | done | Intake session persistence completed on 2026-05-01 |
| T10A-27 | `TASK_086_DIRECT_WORD_APPLICATION_FORM_UPLOAD_WIRING` | done | Direct Word upload API and frontend wiring completed on 2026-05-01 |
| T10A-28 | `TASK_087_INTAKE_INFORMATION_DENSITY_AND_ATTACHMENT_LIST_CLEANUP` | done | Intake information density and attachment list cleanup completed on 2026-05-01 |
| T10A-29 | `TASK_088_ATTACHMENT_DETAILS_PREVIEW_COMPLETION` | done | Attachment details preview completed on 2026-05-04 |
| T10A-30 | `TASK_089_NEW_PROJECT_WORKFLOW_SHELL_AND_BUTTON_UNIFICATION` | done | New Project workflow shell and button unification completed on 2026-05-04 |
| T10A-31 | `TASK_090_INTAKE_WORKFLOW_STRUCTURE_EXTRACTION` | done | Intake workflow structure extraction completed on 2026-05-04 |
| T10A-32 | `TASK_091_INTAKE_PRECHECK_MANUAL_SMOKE_AND_UI_POLISH_BACKLOG` | done | Intake/Precheck manual smoke and UI polish backlog completed on 2026-05-04 |
| T10A-33 | `TASK_092_INTAKE_ATTACHMENT_DOWNLOAD_ACTION` | done | Intake attachment Download button, /download API, and frontend wiring completed on 2026-05-04 |
| T10A-34 | `TASK_093_EMAIL_PACKAGE_MISSING_FORM_UPLOAD_CONTINUATION` | done | Email package missing-form upload continuation completed on 2026-05-04 |
| T10A-35 | `TASK_094_INTAKE_APPLICATION_FORM_HEADER_GATE` | done | Intake Continue to Precheck is gated by `.docx` and Laboratory Testing Request header table cell `(1,2)` validation through OfficeFacade on 2026-05-04; manual smoke hotfix keeps footer/button state synced to every selected attachment |
| T10A-36 | `TASK_095_SINGLE_ACTIVE_PRECHECK_CASE_PER_INTAKE_SESSION` | done | Single active Precheck case behavior completed on 2026-05-04; A-to-B form selection reuses the unconfirmed case, clears old manual overrides, and the Precheck case switcher was removed |

Acceptance gate:

- operators can start from a `.msg` file without creating a project first
- operators can start from manual intake when no email exists
- both paths preserve source context and create structured records through the same review gate
- one selected application form creates one project only after confirmation
- missing required information is visible before confirmation
- copied-workbook LTR write hardening remains deferred until Phase 10A is complete
- no future-scope feature slips into Phase 10A

---

## 6. Completion Update Protocol

After finishing any task, AI must update this board in the same turn.

Minimum required updates:

1. change task status
2. update `Last Updated`
3. record validation result
4. record current stop point
5. activate the next allowed task or explain why the next task is blocked

Recommended completion note format:

```text
Completed:
- TASK_XXX_NAME

Validation:
- tests run
- key result

Next:
- next active task
- prerequisites or known limits
```

---

## 7. Current Validation Snapshot

Latest completed task:

- `TASK_094_INTAKE_APPLICATION_FORM_HEADER_GATE`

Validation result:

- `py -m pytest tests\unit\test_application_form_eligibility_service.py tests\unit\test_intake_form_selection_service.py -q`
- result: `18 passed`
- `py -m pytest tests\unit\test_intake_form_selection_service.py -q`
- result: `12 passed`
- `py -m pytest tests\integration\test_msg_package_intake_api.py -q`
- result: `9 passed`
- `py -m pytest tests\unit\test_frontend_shell_files.py -q`
- result: `43 passed`
- `npm run build` from `frontend/`
- result: passed
- TASK_094 manual smoke hotfix:
- `py -m pytest tests\unit\test_frontend_shell_files.py -q`
- result: `43 passed`
- `npm run build` from `frontend/`
- result: passed
- TASK_094 supplemental upload 500 hotfix:
- `py -m pytest tests\integration\test_msg_package_intake_api.py::test_email_package_supplemental_application_form_rejects_bad_header tests\integration\test_msg_package_intake_api.py::test_email_package_without_form_accepts_supplemental_application_form tests\integration\test_msg_package_intake_api.py::test_email_package_supplemental_application_form_rejects_non_word -q`
- result: `3 passed`
- `py -m pytest tests\unit\test_frontend_shell_files.py::test_task093_email_package_missing_form_upload_continuation tests\unit\test_frontend_shell_files.py::test_task094_intake_continue_uses_application_form_header_gate -q`
- result: `2 passed`
- `npm run build` from `frontend/`
- result: passed
- `npm run build` from `frontend/`
- result: passed
- `py -m pytest tests\unit\test_frontend_shell_files.py -q`
- result: `21 passed`
- `py -m pytest -q`
- result: `247 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `py -m pytest tests\integration\test_msg_package_intake_api.py tests\unit\test_frontend_shell_files.py -q`
- result: `26 passed`
- `npm run build` from `frontend/`
- result: passed
- `py -m pytest -q`
- result: `250 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `py -m pytest tests\unit\test_intake_form_selection_service.py tests\integration\test_msg_package_intake_api.py -q`
- result: `12 passed`
- `py -m pytest tests\unit\test_frontend_shell_files.py -q`
- result: `22 passed`
- `npm run build` from `frontend/`
- result: passed
- `py -m pytest -q`
- result: `250 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `npm run build` from `frontend/`
- result: passed
- `py -m pytest tests\unit\test_frontend_shell_files.py -q`
- result: `21 passed`
- `py -m pytest -q`
- result: `247 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `npm run build` from `frontend/`
- result: passed
- `py -m pytest tests\unit\test_frontend_shell_files.py -q`
- result: `20 passed`
- `py -m pytest -q`
- result: `246 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `npm run build` from `frontend/`
- result: passed
- `py -m pytest tests\unit\test_frontend_shell_files.py -q`
- result: `19 passed`
- `py -m pytest -q`
- result: `245 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- static documentation review for `TASK_060_PHASE10A_SCOPE_AND_BOARD_ACTIVATION`
- result: `docs/phase10a_intake_entry_completion_plan.md` added, Phase 10A board section added, and `TASK_061_MSG_PACKAGE_IMPORT_API_AND_FRONTEND_ENTRY` activated
- targeted documentation regression tests for Phase 10A:
- result: `16 passed`
- `py -m pytest -q`
- result: `222 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `py -m pytest tests\unit\test_msg_package_intake_service.py tests\integration\test_msg_package_intake_api.py tests\unit\test_frontend_shell_files.py -q`
- result: `21 passed`
- `npm run build` from `frontend/`
- result: passed
- `py -m pytest tests\unit\test_intake_case_review_service.py tests\integration\test_manual_intake_api.py tests\unit\test_frontend_shell_files.py -q`
- result: `24 passed`
- `npm run build` from `frontend/`
- result: passed
- `py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase9_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_frontend_shell_files.py -q`
- result: `34 passed`
- `py -m pytest -q`
- result: `241 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- static documentation review for `TASK_065_INTAKE_ENTRY_BROWSER_SMOKE_AND_DOCS_SYNC`
- result: `docs/phase10a_validation_summary.md` added, `docs/frontend_smoke_checklist.md` updated, Phase 10A marked complete
- `py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase9_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py -q`
- result: `17 passed`
- `py -m pytest tests\unit\test_frontend_shell_files.py tests\unit\test_msg_package_intake_service.py tests\integration\test_msg_package_intake_api.py tests\unit\test_intake_package_query_service.py tests\unit\test_manual_intake_service.py tests\integration\test_manual_intake_api.py tests\unit\test_intake_case_review_service.py -q`
- result: `34 passed`
- `npm run build` from `frontend/`
- result: passed
- `py -m pytest -q`
- result: `242 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `py -m pytest tests\unit\test_msg_package_intake_service.py tests\integration\test_msg_package_intake_api.py tests\unit\test_frontend_shell_files.py tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase9_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py -q`
- result: `37 passed`
- `npm run build` from `frontend/`
- result: passed
- `py -m pytest -q`
- result: `228 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `py -m pytest tests\unit\test_intake_package_query_service.py tests\integration\test_msg_package_intake_api.py tests\unit\test_frontend_shell_files.py -q`
- result: `22 passed`
- `py -m pytest tests\unit\test_manual_intake_service.py tests\integration\test_manual_intake_api.py tests\unit\test_frontend_shell_files.py -q`
- result: `22 passed`
- `py -m pytest tests\unit\test_manual_intake_service.py tests\integration\test_manual_intake_api.py tests\unit\test_frontend_shell_files.py tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase9_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py -q`
- result: `38 passed`
- `npm run build` from `frontend/`
- result: passed
- `py -m pytest -q`
- result: `237 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `npm run build` from `frontend/`
- result: passed
- `py -m pytest tests\unit\test_intake_package_query_service.py tests\integration\test_msg_package_intake_api.py tests\unit\test_frontend_shell_files.py tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase9_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py -q`
- result: `38 passed`
- `npm run build` from `frontend/`
- result: passed
- `py -m pytest -q`
- result: `232 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `npm run build` from `frontend/`
- result: passed
- `py -m pytest -q`
- result: `219 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- static documentation review for `TASK_059_PHASE9_BROWSER_SMOKE_AND_DOCS_SYNC`
- result: `docs/phase9_validation_summary.md` added, `docs/frontend_smoke_checklist.md` updated, Phase 9 marked complete
- `py -m pytest tests\unit\test_project_service.py tests\integration\test_project_api.py tests\integration\test_repositories.py tests\unit\test_intake_confirmation_service.py tests\unit\test_folder_template_service.py tests\unit\test_precheck_engine.py -q`
- result: `26 passed`
- `npm run build` from `frontend/`
- result: passed
- `py -m pytest -q`
- result: `210 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `py -m pytest -q`
- result: `203 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- Phase 7 validation summary:
- result: `docs/phase7_validation_summary.md` added with manual smoke checklist, known limitations, workbook write policy, and next recommendation
- Frontend build:
- result: not rerun for `TASK_051`; no frontend or UX-copy files changed
- `py -m pytest tests\unit\test_lookup_service.py tests\integration\test_lookup_api.py -q`
- result: `6 passed`
- `py -m pytest tests\integration\test_ltr_api.py tests\integration\test_intake_precheck_api.py tests\integration\test_project_lifecycle_gating_api.py tests\unit\test_ltr_readiness_service.py -q`
- result: `12 passed`
- `py -m pytest -q`
- result: `201 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `py -m pytest tests\unit\test_exception_workflow_service.py tests\integration\test_exception_workflow_api.py -q`
- result: `5 passed`
- `py -m pytest tests\unit\test_intake_form_selection_service.py tests\unit\test_intake_confirmation_service.py tests\unit\test_evidence_placement_service.py tests\unit\test_ltr_renumber_preview_service.py -q`
- result: `21 passed`
- `py -m pytest tests\integration\test_intake_package_repositories.py tests\integration\test_exception_workflow_api.py tests\integration\test_evidence_placement_api.py tests\integration\test_ltr_renumber_preview_api.py tests\integration\test_project_lifecycle_gating_api.py -q`
- result: `14 passed`
- `py -m pytest -q`
- result: `195 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `py -m pytest tests\unit\test_project_lifecycle_service.py tests\integration\test_project_lifecycle_gating_api.py -q`
- result: `9 passed`
- `py -m pytest tests\integration\test_ltr_api.py tests\integration\test_ltr_registration_preview_api.py tests\integration\test_ltr_local_commit_api.py tests\integration\test_folder_generation_api.py tests\integration\test_evidence_placement_api.py tests\integration\test_mvp_workflow_api.py -q`
- result: `7 passed`
- `py -m pytest -q`
- result: `187 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `py -m pytest tests\unit\test_evidence_placement_service.py tests\integration\test_evidence_placement_api.py -q`
- result: `4 passed`
- `py -m pytest tests\unit\test_evidence_placement_service.py tests\integration\test_evidence_placement_api.py tests\integration\test_folder_generation_api.py tests\unit\test_ltr_renumber_preview_service.py -q`
- result: `10 passed`
- `py -m pytest -q`
- result: `178 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `py -m pytest tests\unit\test_intake_storage.py tests\unit\test_msg_compatibility.py tests\unit\test_outlook_msg_attachment_extraction.py -p no:cacheprovider`
- result: `15 passed`
- `py -m pytest tests\unit\test_intake_storage.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase5_ux_decision.py -p no:cacheprovider`
- result: `14 passed`
- `py -m pytest tests\unit\test_msg_compatibility.py tests\unit\test_outlook_msg_attachment_extraction.py tests\unit\test_phase6_scope_activation.py -p no:cacheprovider`
- result: `11 passed`
- `py -m pytest tests\unit\test_msg_compatibility.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase5_ux_decision.py -p no:cacheprovider`
- result: `10 passed`
- `py -m pytest tests\unit\test_msg_compatibility.py tests\unit\test_phase6_scope_activation.py -p no:cacheprovider`
- result: `8 passed`
- `py -m pytest tests\unit\test_msg_compatibility.py tests\unit\test_outlook_msg_attachment_extraction.py tests\unit\test_outlook_msg_source_import.py tests\unit\test_office_integration_boundary.py -p no:cacheprovider`
- result: `17 passed`
- `py -m pytest tests\unit\test_outlook_msg_attachment_extraction.py tests\unit\test_outlook_msg_source_import.py tests\unit\test_office_integration_boundary.py -p no:cacheprovider`
- result: `14 passed`
- `py -m pytest tests\unit\test_outlook_msg_attachment_extraction.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase5_ux_decision.py -p no:cacheprovider`
- result: `11 passed`
- `py -m pytest tests\unit\test_outlook_msg_source_import.py tests\unit\test_office_integration_boundary.py -p no:cacheprovider`
- result: `10 passed`
- `py -m pytest tests\unit\test_outlook_msg_source_import.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase5_ux_decision.py -p no:cacheprovider`
- result: `11 passed`
- `py -m pytest tests\unit\test_office_integration_boundary.py tests\unit\test_phase6_scope_activation.py -p no:cacheprovider`
- result: `10 passed`
- `py -m pytest tests\unit\test_office_integration_boundary.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase5_ux_decision.py -p no:cacheprovider`
- result: `13 passed`
- `py -m pytest tests\unit\test_phase6_scope_activation.py tests\unit\test_phase5_ux_decision.py -p no:cacheprovider`
- result: `7 passed`
- `py -m pytest tests\unit\test_intake_package_domain_models.py tests\integration\test_intake_package_repositories.py -q`
- result: `4 passed`
- `py -m pytest tests\unit\test_application_form_candidate_detector.py tests\integration\test_intake_package_repositories.py -q`
- result: `7 passed`
- `py -m pytest tests\unit\test_intake_form_selection_service.py tests\integration\test_intake_package_repositories.py -q`
- result: `11 passed`
- `npm run build`
- result: `passed`
- `py -m pytest tests\unit\test_intake_confirmation_service.py tests\integration\test_intake_package_repositories.py -q`
- result: `10 passed`
- `py -m pytest tests\unit\test_direct_word_intake_service.py tests\integration\test_intake_package_repositories.py -q`
- result: `10 passed`
- `py -m pytest tests\unit\test_precheck_engine.py tests\integration\test_intake_precheck_api.py -q`
- result: `7 passed`
- safe real `.docx` parser coverage probe for `TASK_038_REAL_DOCX_PARSER_CALIBRATION`
- result: 2 real `.docx` files readable; parser now extracts footer form/revision, requested testing, and 3-4 sample rows without committing originals
- `py -m pytest -q`
- result: `114 passed`
- `py -m pytest tests\unit\test_ltr_field_catalog.py -q`
- result: `6 passed`
- `py -m pytest tests\integration\test_ltr_api.py tests\unit\test_ltr_field_catalog.py -q`
- result: `7 passed`
- `py -m pytest -q`
- result: `120 passed`
- `py -m pytest tests\unit\test_ltr_number_rules.py -q`
- result: `12 passed`
- `py -m pytest tests\integration\test_ltr_api.py tests\unit\test_ltr_field_catalog.py tests\unit\test_ltr_number_rules.py -q`
- result: `19 passed`
- `py -m pytest -q`
- result: `132 passed`
- `py -m pytest tests\unit\test_ltr_workbook_snapshot_gateway.py -q`
- result: `6 passed`
- `py -m pytest tests\unit\test_office_integration_boundary.py tests\unit\test_ltr_workbook_snapshot_gateway.py -q`
- result: `12 passed`
- safe real `.xls` workbook probe for `TASK_041_LTR_WORKBOOK_SNAPSHOT_GATEWAY`
- result: `LTR_number.xls` detected as legacy `.xls` and rejected with explicit unsupported adapter error; no write attempted
- `py -m pytest -q`
- result: `138 passed`
- `py -m pytest tests\unit\test_ltr_readiness_service.py -q`
- result: `5 passed`
- `py -m pytest tests\integration\test_ltr_readiness_api.py -q`
- result: `1 passed`
- `py -m pytest tests\unit\test_ltr_field_catalog.py tests\unit\test_ltr_number_rules.py tests\unit\test_ltr_workbook_snapshot_gateway.py tests\integration\test_ltr_api.py tests\integration\test_ltr_readiness_api.py -q`
- result: `26 passed`
- `py -m pytest -q`
- result: `144 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `py -m pytest tests\unit\test_ltr_registration_preview_service.py -q`
- result: `6 passed`
- `py -m pytest tests\integration\test_ltr_registration_preview_api.py -q`
- result: `1 passed`
- `py -m pytest tests\unit\test_ltr_registration_preview_service.py tests\unit\test_ltr_readiness_service.py tests\unit\test_ltr_number_rules.py tests\unit\test_ltr_workbook_snapshot_gateway.py tests\integration\test_ltr_registration_preview_api.py tests\integration\test_ltr_readiness_api.py tests\integration\test_ltr_api.py -q`
- result: `32 passed`
- `py -m pytest tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py -q`
- result: `7 passed`
- `py -m pytest -q`
- result: `151 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `py -m pytest tests\unit\test_ltr_local_commit_service.py -q`
- result: `4 passed`
- `py -m pytest tests\integration\test_ltr_local_commit_api.py -q`
- result: `2 passed`
- `py -m pytest tests\unit\test_ltr_local_commit_service.py tests\unit\test_ltr_registration_preview_service.py tests\unit\test_ltr_readiness_service.py tests\unit\test_ltr_number_rules.py tests\integration\test_ltr_local_commit_api.py tests\integration\test_ltr_registration_preview_api.py tests\integration\test_ltr_readiness_api.py tests\integration\test_ltr_api.py -q`
- result: `33 passed`
- `py -m pytest -q`
- result: `158 passed`
- safe real `.xls` layout probe for `TASK_045_LTR_EXCEL_WRITE_GATEWAY_AND_SYNC`
- result: `LTR_number_解密版.xls` opened read-only through Excel COM; annual sheets `2020`-`2026` confirmed; A:Q registration columns and DL column D confirmed; no save/write attempted
- `py -m pytest tests\unit\test_config.py tests\unit\test_office_integration_boundary.py tests\unit\test_excel_com_ltr_workbook_gateway.py -q`
- result: `15 passed`
- `py -m pytest tests\unit\test_ltr_number_rules.py tests\unit\test_ltr_registration_preview_service.py tests\unit\test_ltr_local_commit_service.py tests\integration\test_ltr_registration_preview_api.py tests\integration\test_ltr_local_commit_api.py -q`
- result: `28 passed`
- `py -m pytest tests\unit\test_ltr_workbook_snapshot_gateway.py tests\unit\test_ltr_number_rules.py tests\unit\test_excel_com_ltr_workbook_gateway.py -q`
- result: `25 passed`
- `py -m pytest -q`
- result: `168 passed`
- `py -m pytest tests\unit\test_ltr_renumber_preview_service.py -q`
- result: `5 passed`
- `py -m pytest tests\integration\test_ltr_renumber_preview_api.py -q`
- result: `1 passed`
- `py -m pytest tests\unit\test_ltr_renumber_preview_service.py tests\integration\test_ltr_renumber_preview_api.py tests\integration\test_ltr_api.py tests\integration\test_folder_generation_api.py tests\unit\test_ltr_number_rules.py -q`
- result: `22 passed`
- `py -m pytest -q`
- result: `174 passed`
- `py -m pytest -q`
- result: `112 passed`
- `npm run build`
- result: `passed`
- `npm run build`
- result: `passed`
- `npm run build`
- result: `passed`
- `py -m pytest -q`
- result: `95 passed`
- manual browser smoke checklist
- result: not required for docs-only scope activation
- static documentation review for `TASK_036_PHASE7_SCOPE_AND_BOARD_ACTIVATION`
- result: Phase 7 board section added and `TASK_037_REAL_SAMPLE_BASELINE` activated
- safe real sample probe for `TASK_037_REAL_SAMPLE_BASELINE`
- result: 4 `.msg` samples supported by current gateway; attachments extracted into temporary workspace only
- safe real `.docx` parser coverage probe for `TASK_037_REAL_SAMPLE_BASELINE`
- result: 2 real `.docx` files readable; current parser extracts 6-7 top-level fields, 0 lab fields, and 0 sample rows
- `py -m pytest tests\unit\test_application_form_parser.py -q`
- result: `4 passed`
- `py -m pytest tests\unit\test_precheck_engine.py tests\integration\test_intake_precheck_api.py -q`
- result: `7 passed`

Known limits:

- no full installer or PyInstaller bundle implemented
- PyWebView remains a future packaging placeholder
- browser-based manual frontend smoke has not been executed by Codex
- `$impeccable` context is present in `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json`
- no report generation, AI review, Matrix, or future-scope features
- OfficeFacade boundary and Word snapshot gateway are implemented
- `.msg` source import and minimal metadata are implemented
- `.msg` fixture-supported attachment extraction is implemented
- real `.msg` sample compatibility baseline now covers 4 local samples; all were readable by the current gateway
- intake storage boundary is implemented
- intake persistence, candidate detection, review UI, and confirm flow are planned but not implemented
- Phase 7 is complete; later phases were activated only after explicit user approval
- real `.msg` / `.docx` originals must not be committed
- external LTR workbook write remains disabled and out of scope until a later explicit task
- parser now has generated real-style regression coverage and real-sample probe coverage for footer form/revision, request fields, sample rows, requested testing, and lab section; original real `.docx` files remain local and uncommitted
- LTR readiness field catalog is defined as pure Python only; readiness evaluation, API, preview, commit, and workbook integration remain out of scope
- LTR number rules are defined as pure Python only; workbook snapshot, readiness service, preview, commit, and workbook write remain out of scope
- LTR workbook snapshot gateway is read-only; `.xlsx` package snapshots are supported, legacy `.xls` is explicitly unsupported until a later adapter task, and workbook write remains out of scope
- LTR readiness service/API is implemented; it evaluates confirmed project/form/sample/evidence data plus an optional proposed LTR number, but it does not preview, commit, or write workbook data
- LTR registration preview is implemented as no-write/no-commit; API supports `local_only` preview and service supports optional read-only workbook snapshot injection for conflict and fingerprint context
- `DL` is generated during preview and should be `pending_preview` before a candidate number exists; it is not expected to be present in the mailed application attachment
- LTR local commit is implemented; it recomputes preview-equivalent data, requires operator confirmation, stores audit JSON in `LtrRecord.notes`, updates project status through `LtrService`, and does not call workbook write
- LTR Excel COM write boundary is implemented behind `OfficeFacade`; write remains disabled by default and password/path are configuration-driven
- Normal LTR preview no longer calculates or reserves a candidate number; final normal DL allocation happens inside the Excel COM write session after reading workbook data
- LTR renumber preview is implemented as non-destructive planning only; it reports affected folder/file asset paths and blocks future execution when target paths or local LTR numbers conflict
- LTR workbook password handling is a future adapter/write requirement: default may be configured as `DGLAB`, but password must not be hard-coded and missing/invalid password must not create local registered state
- `$impeccable` is now a project-wide rule for all frontend/UI and UX-copy work, not only Phase 5 or Phase 6A
- application `Project #` / `project_no` is now optional metadata; current workflow continuity relies on internal IDs before LTR registration and DL/LTR number after registration
- existing SQLite databases with legacy `projects.project_no NOT NULL UNIQUE` are relaxed by a narrow `init_db()` migration; no general migration framework has been added
- Phase 9 is complete; external LTR workbook write remains out of scope
- TASK_054 frontend wiring does not write the shared LTR workbook; normal DL allocation remains finalized only during an enabled Excel write session
- TASK_055 frontend wiring calls existing intake exception review APIs only; it does not add Outlook inbox auto-scan or email sending
- TASK_056 frontend wiring calls existing evidence placement APIs only; file copy remains backend-controlled and no-overwrite
- TASK_057 frontend wiring is read-only lookup and summary display only; it does not add Matrix, Report, or AI review behavior
- TASK_058 frontend disabled-state text mirrors existing lifecycle guard outcomes; backend remains authoritative
- TASK_059 closes Phase 9
- TASK_060 opens Phase 10A for intake entry completion
- TASK_061 adds manual `.msg` package import through API/frontend entry without Outlook inbox auto-scan or email sending
- TASK_062 replaces static package detail data with real backend package detail state
- TASK_063 adds the no-email manual intake exception path without creating a project
- TASK_064 unifies email/manual review and keeps project creation behind explicit operator confirmation
- TASK_065 closes Phase 10A
- copied-workbook LTR write hardening is deferred until explicit user approval for the next phase

---

## 8. Next Recommended Action

Current recommendation:

- request user approval before opening the next controlled implementation task or phase

Why this is next:

- `TASK_003` established the SQLite engine, session factory, Base, and `init_db()`
- `TASK_004` established pure MVP domain models and enums
- `TASK_005` established SQLAlchemy models and repositories
- `TASK_006` established project service and thin project API
- `TASK_007` established structured DOCX parser output
- `TASK_008` established deterministic precheck rules
- `TASK_009` exposed parser + precheck flow through API
- `TASK_010` established LTR registration/tracking
- `TASK_011` established safe folder preview
- `TASK_012` established safe folder generation with persistence and overwrite protection
- `TASK_013` established the minimal React + TypeScript shell
- `TASK_014` connected the MVP workflow through backend and frontend
- `TASK_015` documented local Windows run scripts and packaging status
- the defined MVP task sequence is complete
- `docs/ConnLab_Phase5_Workbench_UX_Plan.md` defines the approved UX modernization direction
- `TASK_016` established the approved UX decision record
- `TASK_017` established the product app shell and left navigation
- `TASK_018` established the searchable project registry/dashboard
- `TASK_019` established the sequential project workbench stepper
- `TASK_020` established business-readable precheck issue review
- `TASK_021` established clearer intake, LTR, and folder operation panels
- `TASK_022` cleaned up frontend workflow state derivation and centralized API usage checks
- `TASK_023` established frontend build and manual smoke validation guards
- `TASK_024` completed Phase 5 documentation and board sync
- Phase 5 implementation is complete
- the user explicitly approved executing the Phase 6 implementation plan
- `TASK_025` opened Phase 6A and activated the Office integration boundary task
- `TASK_026` established OfficeFacade, Word document snapshots, and gateway boundaries
- `TASK_027A` established controlled `.msg` source preservation and minimal metadata parsing
- `TASK_027B` established fixture-supported attachment extraction and metadata
- `TASK_027C` documented real `.msg` compatibility status and missing fixture blocker
- `TASK_028A` established controlled intake file storage
- `TASK_036` activated Phase 7 without implementing product behavior
- `TASK_037` documented real `.msg` and `.docx` baseline behavior without committing original samples
- `TASK_038` improved deterministic parser coverage for generated real-style `.docx` layouts
- `TASK_039` defined the authoritative 19-field LTR readiness catalog and placeholder policy
- `TASK_040` defined pure deterministic LTR number parsing, validation, formatting, suffix/W-prefix handling, and monthly sequence rules
- `TASK_041` added the read-only workbook snapshot gateway and explicit legacy `.xls` unsupported handling
- `TASK_042` added the readiness service/API so incomplete LTR registration data blocks preview or registration
- `TASK_043` added no-write registration preview with deterministic proposed number, readiness field mapping, conflict reporting, and snapshot context
- `TASK_044` added local-only commit with operator confirmation and traceable audit notes
- `TASK_045` added the config-gated OfficeFacade + Excel COM workbook write boundary and patched normal preview so final normal numbering is allocated only inside write access
- `TASK_046` added non-destructive renumber/folder rename impact preview and conflict reporting
- `TASK_047` added deterministic evidence placement preview/execution for email, forms, specs, LTR evidence, corrections, and no-overwrite copy behavior
- `TASK_048` added lifecycle operation guards around existing project statuses for LTR, folder, and evidence operations
- `TASK_049` added explicit no-form, multi-form, missing-info, correction evidence, and renumber reason workflow behavior
- `TASK_050` added read-only project lookup, sample summary, and testing condition/method summary from structured records
- `TASK_051` closed Phase 7 with validation summary, manual smoke checklist, known limitations, workbook write policy, and next recommendation
- `TASK_052` downgraded application Project # to optional metadata and preserved DL-centric project identity
- `TASK_053` opened Phase 9 and activated the first controlled frontend operator workflow wiring task
- `TASK_054` wired LTR readiness, no-write preview, and local commit confirmation into the frontend workflow without external workbook mutation
- `TASK_055` wired intake no-form, multi-form, and missing-info exception workflows into the frontend without Outlook auto-scan or email sending
- `TASK_056` wired folder evidence placement preview and no-overwrite execution into the frontend without direct file manipulation
- `TASK_057` wired read-only project lookup, sample summary, and testing condition/method summary into the frontend without adding future workflow scope
- `TASK_058` surfaced lifecycle guard disabled-state reasons for LTR, folder, and evidence actions without adding a new lifecycle model
- `TASK_059` closed Phase 9 with validation summary, manual browser smoke checklist, docs sync, and next recommendation
- the user explicitly approved adjusting the plan so intake entry is corrected before copied-workbook LTR write hardening
- `TASK_060` opened Phase 10A for manual `.msg` package import and no-email manual intake
- `TASK_061` added manual `.msg` package import through API/frontend entry and stores source email plus extracted attachments
- `TASK_062` added real package detail API/frontend wiring for source metadata, stored assets, candidate forms, no-form and multi-form outcomes, and created case summaries
- `TASK_063` added no-email manual intake entry with structured package/case/draft storage and missing required field visibility
- `TASK_066` fixed Phase 10A manual smoke blockers: case review field correction, persisted draft overrides, and folder/evidence not-ready preview handling
- The user approved `TASK_067` to align the Projects registry layout, New Project entry, and LTR Number terminology before Phase 10B.
- `docs/ltr_number_terminology.md` defines the current terminology rule: `LTR` is Laboratory Testing Request, while `LTR Number` is the registered project business identifier.
- `TASK_067` is complete: Projects uses the approved registry layout direction, the existing intake route is presented as New Project, and operator-facing LTR identity text uses LTR Number.
- The user approved `TASK_068` to polish the shell and Projects registry closer to the reference image, including sidebar icons, top-right utilities, registry toolbar controls, visual refinement, and 14-inch laptop fit.
- `TASK_068` is complete: sidebar icons, top utility controls, registry toolbar controls, and 14-inch laptop spacing were added without implementing unavailable backend behavior.
- The user approved `TASK_069` to redesign only the Intake step of New Project as a reference-style step workflow around one email package and Word application-form selection.
- `TASK_069` is complete: New Project Intake now uses a four-step visual workflow, one email package metadata panel, attachment list, Word-only application-form selection, and attachment details workspace.
- The user approved `TASK_070` to redesign the Precheck step based on the provided reference image.
- `TASK_070` is complete: Precheck now uses a source/template check header, Lab Test Request Number blocker row, key information edit surface, sample table, requested testing section, recipient chips, and confirmation footer.
- The user reported that Intake imported email data was cleared after switching pages and confirmed the desired business behavior is to keep it while the app remains open.
- `TASK_071` is complete: Intake import state now lives at App session scope, Continue goes directly to Precheck, and Precheck Back returns directly to Intake.
- The user reported that Continue to Precheck reached an unstyled Precheck page with no review case.
- `TASK_072` is complete: Continue to Precheck now prepares review cases with the existing exception-review API before routing, and Precheck CSS is imported.
- The user reported that Precheck did not use the application form selected in Intake and could show stale or incomplete data when multiple Word forms exist.
- `TASK_073` is complete: Continue to Precheck now calls an explicit selected-form API, parses the selected `.docx` into draft fields, stores the returned case id in app session state, and Precheck opens that matching case first.
- The user reported that selected Word data still did not visibly populate Precheck after the case binding fix.
- Runtime inspection showed the selected Word draft did contain parsed fields and samples, but the Precheck UI was still rendering reference mock sample rows and fixed select options hid parsed values that were not in the option list.
- `TASK_074` is complete: case review now returns `sample_rows`, Precheck renders parsed sample rows and parsed additional/disposition fields, and select controls preserve parsed values outside the fixed option list.
- real operation usually starts from an exported `.msg` application package, while no-email manual intake is an exception path
- Phase 10A intake entry completion hotfix is closed
- The user approved stabilizing Intake attachment preview before moving to the next phase.
- `TASK_075_INTAKE_ATTACHMENT_PREVIEW_AND_DOCX_PRIORITY` is complete: New Project Intake now loads a safe selected-attachment preview, prioritizing structured `.docx` Laboratory Testing Request preview from the standard table-driven E-3718_H application form.
- The user approved documenting frontend architecture rules before any further UI or Phase 10B work.
- `TASK_076_FRONTEND_ARCHITECTURE_RULES_AND_UI_BOUNDARY` is complete: frontend page, feature, component, API, state, selector, config, styling, copy/mock, and review boundaries are documented in `docs/frontend_architecture_rules.md` and linked from `docs/02_ARCHITECTURE_RULES.md`.
- `AGENTS.md` now requires reading `docs/02_ARCHITECTURE_RULES.md` and `docs/frontend_architecture_rules.md` before frontend/UI implementation, refactor, UX-copy, layout, component, route, state, API-client, or styling tasks.
- Validation for `TASK_076`: `py -m pytest tests\unit\test_frontend_architecture_rules.py -q`, result `2 passed`.
- The user approved auditing the real-business Intake and Precheck pages before any broad UI completion work.
- `TASK_077_INTAKE_PRECHECK_BUSINESS_GAP_AUDIT` is complete: current Intake/Precheck route-page structure, UI mock/reference content, frontend/backend contract mismatches, parser-to-confirmation data loss, direct Word/manual path ambiguity, Lab Test Request Number blocker gap, and deterministic precheck placement gap are documented in `docs/intake_precheck_business_gap_audit.md`.
- Validation for `TASK_077`: `py -m pytest tests\unit\test_intake_precheck_business_gap_audit.py -q`, result `2 passed`.
- The user approved `TASK_078` after confirming SECTION 1 project-creation rules, `Project #` warning policy, Lab Test Request Number auto-clear warning policy, direct `.docx` intake, backend-soft-coded lookup options, send-copy recipient confirmation, sample row editing boundaries, pre-project draft precheck, workflow state concern, and source `.msg` display rules.
- `TASK_078_INTAKE_PRECHECK_FIELD_CONTRACT_AND_SECTION1_RULES` is complete: `docs/intake_precheck_field_contract.md` defines field states, SECTION 1 required/warning rules, SECTION 2 exclusion, sample row edit/copy/delete rules, lookup groups, direct `.docx` intake policy, draft-level precheck policy, and source `.msg` display policy.
- Validation for `TASK_078`: `py -m pytest tests\unit\test_intake_precheck_field_contract.py -q`, result `2 passed`.
- The user approved `TASK_079_LOOKUP_OPTIONS_BACKEND_AND_API` as the next step after confirming that lookup values should be backend/database managed instead of hardcoded in frontend JSX.
- `TASK_079_LOOKUP_OPTIONS_BACKEND_AND_API` is complete: Intake/Precheck lookup groups are stored in `lookup_options`, seeded on first-run empty databases, exposed through `GET /api/lookups/intake-precheck`, and covered by unit/integration tests.
- Validation for `TASK_079`: `py -m pytest tests\unit\test_lookup_options_service.py tests\integration\test_lookup_options_api.py -q`, result `4 passed`.
- User-reported screenshot issues are recorded for `TASK_080_DOCX_PARSER_FIELD_CALIBRATION_FOR_SECTION1`: Business Unit/Mfg. Site label bleed, application Date mapping, and Phone # import.
- The user approved executing `TASK_080` and requested remembering the Disposition lookup unification as `TASK_081`.
- `TASK_080_DOCX_PARSER_FIELD_CALIBRATION_FOR_SECTION1` is complete: parser now rejects neighboring field labels as values and maps E-3718 Rev H ordered content-control values for Date, Business Unit, Mfg. Site, and related dropdown fields.
- Real local sample probe result for `local/office files samples/E-3718_H Laboratory Test Request-Even.docx`: Phone `0513-80167327`, Date `10/11/2024`, Business Unit `Power Solutions`, Mfg. Site `Nantong`, Results Format `Formal Report (Customer)`, Test Type `Customer Specific Testing`, Sample Status `Production`, Project Type `New Product Development`, and Post-Testing Sample Disposition `Keep in the Lab`.
- Validation for `TASK_080`: `py -m pytest tests\unit\test_application_form_parser.py tests\integration\test_intake_precheck_api.py -q`, result `9 passed`.
- TASK_080 hotfix: Precheck date inputs now normalize Word-style `MM/DD/YYYY` strings to browser-compatible `YYYY-MM-DD` display values, so parsed Date and Requested Testing Completion Date are visible in the UI.
- Validation for TASK_080 date hotfix: `py -m pytest tests\unit\test_frontend_shell_files.py tests\unit\test_application_form_parser.py -q`, result `31 passed`; `npm run build`, result passed.
- `TASK_081_FRONTEND_LOOKUP_API_FIELD_RENDERER_WIRING` is proposed: frontend should consume `GET /api/lookups/intake-precheck`, remove hardcoded select arrays, and treat `post_testing_disposition` as the same backend-managed select implementation as the other Intake/Precheck lookup fields.
- The user approved executing the next recommended task, `TASK_081_FRONTEND_LOOKUP_API_FIELD_RENDERER_WIRING`.
- `TASK_081_FRONTEND_LOOKUP_API_FIELD_RENDERER_WIRING` is complete: frontend API client now exposes `getIntakePrecheckLookupOptions`, Precheck select field options are injected from backend lookup groups, `post_testing_disposition` moved into the shared field renderer, and the independent hardcoded Disposition select was removed.
- Backend lookup defaults now include Word `Post-Testing Sample Disposition` values: `Choose an item.`, `Send Back to Requestor`, `Scrap`, and `Keep in the Lab`; existing local databases receive missing required disposition defaults without overwriting other lookup options.
- Validation for `TASK_081`: `py -m pytest tests\unit\test_frontend_shell_files.py tests\integration\test_lookup_options_api.py tests\unit\test_lookup_options_service.py -q`, result `29 passed`; `npm run build`, result passed.
- `TASK_082_PRECHECK_SAMPLE_ROW_EDIT_COPY_DELETE_UI` is proposed for the next controlled task: make sample rows editable, add compact edit/copy/delete actions, preserve at least one row, and persist sample row corrections before project confirmation.
- The user approved executing `TASK_082_PRECHECK_SAMPLE_ROW_EDIT_COPY_DELETE_UI` and requested compact edit/copy/delete icons matching the provided reference image.
- `TASK_082_PRECHECK_SAMPLE_ROW_EDIT_COPY_DELETE_UI` is complete: sample rows now render as editable inputs, Add Sample creates a blank row, Copy duplicates the selected row, Delete is disabled for the last remaining row, and compact edit/copy/delete icon buttons replace text-heavy row actions.
- The review-fields API now accepts `sample_rows`; backend review service persists sample row corrections as draft manual overrides so project confirmation uses corrected sample rows.
- Validation for `TASK_082`: `py -m pytest tests\unit\test_intake_case_review_service.py tests\integration\test_manual_intake_api.py tests\unit\test_frontend_shell_files.py -q`, result `34 passed`; `npm run build`, result passed.
- TASK_082 hotfix: sample table columns now preserve the application-form shape by using one `Part Number / Revision` column and one `Traceability Manufacturing Lot Info` column instead of splitting revision and manufacturing lot into separate UI columns.
- Validation for TASK_082 hotfix: `py -m pytest tests\unit\test_frontend_shell_files.py tests\unit\test_intake_case_review_service.py tests\integration\test_manual_intake_api.py -q`, result `34 passed`; `npm run build`, result passed.
- `TASK_083_PREPROJECT_SECTION1_PRECHECK_AND_CONFIRMATION_GUIDANCE` is proposed for the next controlled task: run deterministic SECTION 1 precheck before Project creation and show clear blockers/warnings.
- The user approved executing `TASK_083_PREPROJECT_SECTION1_PRECHECK_AND_CONFIRMATION_GUIDANCE`.
- `TASK_083_PREPROJECT_SECTION1_PRECHECK_AND_CONFIRMATION_GUIDANCE` is complete: deterministic SECTION 1 draft precheck now evaluates required requestor/project fields, sample rows, requested testing, disposition, confidentiality/subcontract, and report copy recipients before Project creation.
- Backend confirmation is authoritative: error-level SECTION 1 issues reject Project creation; `Project #` and nonblank Lab Test Request Number are warnings; SECTION 2 lab fields are excluded from pre-project blockers.
- Precheck UI now shows a top issue summary, field-level error/warning highlights, and no longer displays fixed recipient chips as real data. `send_copies_recipients` is a real editable field.
- Validation for `TASK_083`: `py -m pytest tests\unit\test_intake_case_review_service.py tests\integration\test_manual_intake_api.py tests\unit\test_frontend_shell_files.py -q`, result `37 passed`; `py -m pytest -q`, result `275 passed`; `npm run build`, result passed; `git diff --check`, result passed with CRLF working-copy warnings only.
- Sidebar correction for `TASK_083`: removed `Precheck` and `LTR Number` from global navigation because they are workflow steps, then updated shell static expectations. Validation: `py -m pytest tests\unit\test_frontend_shell_files.py -q`, result `27 passed`; `npm run build`, result passed.
- `TASK_084_PRECHECK_FRONTEND_STRUCTURE_EXTRACTION` is proposed for the next controlled task: extract Precheck field config, sample config, issue summary, named components, and maintainable feature style/token rules into a `features/precheck` boundary while preserving behavior and the recent Intake/Precheck readability fixes.
- The user approved `TASK_084_PRECHECK_FRONTEND_STRUCTURE_EXTRACTION`.
- `TASK_084_PRECHECK_FRONTEND_STRUCTURE_EXTRACTION` is complete: Precheck field configuration, sample table configuration, issue summary, source check, lower panels, messages, state panel, and pure selectors now live under `frontend/src/features/precheck`; `IntakeCaseReviewPage.tsx` remains the route-level workflow coordinator.
- TASK_084 style cleanup preserved the recent Intake/Precheck readability fixes through scoped data/text tokens instead of scattered hard-coded color and font-weight overrides.
- Validation for `TASK_084`: `py -m pytest tests\unit\test_frontend_shell_files.py -q`, result `28 passed`; `npm run build`, result passed; `py -m pytest -q`, result `276 passed`; `git diff --check`, result passed with CRLF working-copy warnings only.
- The user approved `TASK_085_INTAKE_SESSION_PERSISTENCE` after reviewing the deep evaluation and session persistence plan.
- `TASK_085_INTAKE_SESSION_PERSISTENCE` is complete: App-level Intake session now loads from `sessionStorage`, saves changes back to `sessionStorage`, removes empty persisted sessions, and clears after successful Project confirmation.
- Validation for `TASK_085`: `py -m pytest tests\unit\test_frontend_shell_files.py -q`, result `29 passed`; `npm run build`, result passed; `py -m pytest -q`, result `277 passed`; `git diff --check`, result passed with CRLF working-copy warnings only.
- The user approved the Intake improvement task plan and started with `TASK_086_DIRECT_WORD_APPLICATION_FORM_UPLOAD_WIRING`.
- `TASK_086_DIRECT_WORD_APPLICATION_FORM_UPLOAD_WIRING` is complete: direct Word upload is exposed as `POST /api/intake-packages/import-docx`, the frontend API client calls it, and the Intake page updates session state with the returned package and selected Word asset.
- Validation for `TASK_086`: `py -m pytest tests\integration\test_manual_intake_api.py tests\unit\test_frontend_shell_files.py -q`, result `32 passed`; `npm run build`, result passed; `py -m pytest -q`, result `278 passed`; `git diff --check`, result passed with CRLF working-copy warnings only.
- The user approved executing the next recommended task, `TASK_087_INTAKE_INFORMATION_DENSITY_AND_ATTACHMENT_LIST_CLEANUP`.
- `TASK_087_INTAKE_INFORMATION_DENSITY_AND_ATTACHMENT_LIST_CLEANUP` is complete: Intake source summary is reduced to sender email, subject, and date; import responses expose optional `received_at`; attachment rows now prioritize file names with compact role text instead of separate type and size columns; application-form selection guidance appears near the Continue action.
- Validation for `TASK_087`: `py -m pytest tests\integration\test_manual_intake_api.py tests\unit\test_frontend_shell_files.py -q`, result `33 passed`; `npm run build`, result passed; `py -m pytest -q`, result `279 passed`; `git diff --check`, result passed with CRLF working-copy warnings only.
- TASK_087 hotfix: real Outlook `.msg` import now avoids showing Exchange X.500 sender paths when a SMTP sender address is available, parses RFC-style Outlook Date headers, formats Intake dates in the UI, and uses row click/highlight instead of a radio button for selecting the Word application form.
- Validation for TASK_087 hotfix: `py -m pytest tests\unit\test_outlook_msg_source_import.py tests\unit\test_frontend_shell_files.py tests\integration\test_msg_package_intake_api.py -q`, result `41 passed`; `npm run build`, result passed; `py -m pytest -q`, result `281 passed`; `git diff --check`, result passed with CRLF working-copy warnings only.
- TASK_085 hotfix: Precheck `Back to Intake` now syncs the active case id and selected Word form asset id back into the App-level Intake session before routing, so returning to Intake preserves the selected application form and Continue eligibility.
- Validation for TASK_085 hotfix: `py -m pytest tests\unit\test_frontend_shell_files.py -q`, result `31 passed`; `npm run build`, result passed; `py -m pytest -q`, result `282 passed`; `git diff --check`, result passed with CRLF working-copy warnings only.
- The user approved executing the next recommended task, `TASK_088_ATTACHMENT_DETAILS_PREVIEW_COMPLETION`.
- `TASK_088_ATTACHMENT_DETAILS_PREVIEW_COMPLETION` is complete: Intake selected-attachment preview now supports inline image previews, metadata-only previews for Excel/PDF/MSG/non-application Word/other files, and application-form Word previews focused on business fields, sample rows, and requested-testing details without generic document structure.
- Validation for `TASK_088`: `py -m pytest tests\unit\test_intake_asset_preview_service.py tests\integration\test_msg_package_intake_api.py tests\unit\test_frontend_shell_files.py -q`, result `42 passed`; `npm run build`, result passed; `py -m pytest -q`, result `285 passed`; `git diff --check`, result passed with CRLF working-copy warnings only.
- TASK_088 sample preview correction: Attachment details sample preview now uses the same sample columns as the application form / Precheck, adds parser support for `Contact Lubricant`, and combines part number/revision with suffix-only de-duplication.
- Validation for TASK_088 sample preview correction: `py -m pytest tests\unit\test_intake_asset_preview_service.py tests\unit\test_application_form_parser.py tests\unit\test_intake_form_selection_service.py -q`, result `22 passed`; `py -m pytest tests\unit\test_intake_asset_preview_service.py tests\unit\test_application_form_parser.py tests\unit\test_intake_form_selection_service.py tests\unit\test_frontend_shell_files.py -q`, result `57 passed`; `py -m pytest tests\integration\test_msg_package_intake_api.py tests\integration\test_manual_intake_api.py -q`, result `8 passed`.
- The user approved executing `TASK_089_NEW_PROJECT_WORKFLOW_SHELL_AND_BUTTON_UNIFICATION`.
- `TASK_089_NEW_PROJECT_WORKFLOW_SHELL_AND_BUTTON_UNIFICATION` is complete: Intake and Precheck now share one New Project workflow header/stepper component, the four stage labels are consistent, Intake no longer shows a disabled Back action, and footer primary/secondary action styling is aligned without changing business behavior.
- Validation for `TASK_089`: `py -m pytest tests\unit\test_frontend_shell_files.py -q`, result `33 passed`; `npm run build`, result passed; `py -m pytest -q`, result `286 passed`.
- TASK_087 hotfix: real Outlook `.msg` attachment extraction now filters inline body images, preserves embedded Outlook item attachments as `.msg` records, hides the imported source email from the Intake Attachments list while keeping it stored for traceability, and labels `.msg` rows as `MSG` instead of `FILE`.
- Validation for TASK_087 hotfix: `py -m pytest tests\unit\test_outlook_msg_source_import.py tests\unit\test_frontend_shell_files.py -q`, result `42 passed`; `py -m pytest tests\unit\test_msg_package_intake_service.py tests\integration\test_msg_package_intake_api.py -q`, result `8 passed`; `npm run build`, result passed; real sample probe extracted 6 visible attachments from `D:\test_samples\Coolopower HDF 3 40mm Busbar to Busbar &Busbar to PCB Connector Qualification Testing_NPD.msg`; `py -m pytest -q`, result `289 passed`; `git diff --check`, result passed with CRLF working-copy warnings only.
- The user approved executing `TASK_090_INTAKE_WORKFLOW_STRUCTURE_EXTRACTION`.
- `TASK_090_INTAKE_WORKFLOW_STRUCTURE_EXTRACTION` is complete: Intake source panel, attachment list, attachment preview panel, and pure display selectors now live under `frontend/src/features/intake`; `IntakeInboxPage.tsx` remains the route-level API/session coordinator and was reduced from 664 lines to 234 lines without changing behavior.
- Validation for `TASK_090`: `py -m pytest tests\unit\test_frontend_shell_files.py -q`, result `35 passed`; `npm run build`, result passed; `py -m pytest -q`, result `290 passed`; `git diff --check`, result passed with CRLF working-copy warnings only.
- TASK_090 hotfix: Intake form selection now preserves `manual_overrides_json` only when the existing case already belongs to the same selected application form asset; reusable cases rebound to a different asset clear manual overrides to avoid mixing old edits with a new form.
- Validation for TASK_090 hotfix: `py -m pytest tests\unit\test_intake_form_selection_service.py tests\integration\test_msg_package_intake_api.py tests\unit\test_frontend_shell_files.py -q`, result `50 passed`; `npm run build`, result passed; `py -m pytest -q`, result `292 passed`; `git diff --check`, result passed with CRLF working-copy warnings only.
- TASK_090 UX polish: Intake attachment list now hides role subtitles and displays long filenames as up to two medium-weight lines.
- Validation for TASK_090 UX polish: `py -m pytest tests\unit\test_frontend_shell_files.py::test_task087_intake_information_density_cleanup -q`, result `1 passed`; `npm run build`, result passed.
- TASK_090 New Project stepper polish: the shared Intake/Precheck workflow stepper no longer renders the redundant `New Project Step ...` title row; step connector lines are layered behind labels; narrow Windows side-by-side layouts keep all four step labels on one line with horizontal overflow instead of wrapping.
- Validation for TASK_090 New Project stepper polish: `py -m pytest tests\unit\test_frontend_shell_files.py::test_task070_precheck_step_matches_reference_workspace tests\unit\test_frontend_shell_files.py::test_task089_new_project_workflow_shell_is_shared -q`, result `2 passed`; `py -m pytest tests\unit\test_frontend_shell_files.py -q`, result `35 passed`; `npm run build`, result passed.
- TASK_090 Attachment details cleanup: the Attachment details header no longer shows the redundant file type subtitle (Word Document / PDF Document) below the filename, reducing visual noise while keeping the file type chip visible.
- TASK_090 Email information polish: the Email information panel now displays From/Subject/Date values in the primary ink color (black) instead of muted gray, matching the visual hierarchy of the Attachment details header.
- `TASK_095_SINGLE_ACTIVE_PRECHECK_CASE_PER_INTAKE_SESSION` is complete: `IntakeFormSelectionService` now reuses unconfirmed package cases when switching selected application forms, clears manual overrides only when rebinding to a different form, leaves confirmed cases intact, and the New Project Precheck page no longer renders the `Review cases` switcher.
- Validation for `TASK_095`: `py -m pytest tests\unit\test_intake_form_selection_service.py -q`, result `13 passed`; `py -m pytest tests\integration\test_msg_package_intake_api.py -q`, result `10 passed`; `py -m pytest tests\unit\test_frontend_shell_files.py -q`, result `44 passed`; `npm run build`, result passed.
- `TASK_096_PROJECT_CREATION_DRAFT_LIFECYCLE` is complete: New Project creation packages can now be explicitly saved as `draft_saved` or discarded through the unsaved-session path, which removes ConnLab-owned intake database rows and the package storage directory without touching Outlook originals or arbitrary source paths.
- Validation for `TASK_096`: `py -m pytest tests\unit\test_project_creation_draft_lifecycle_service.py tests\integration\test_manual_intake_api.py tests\unit\test_frontend_shell_files.py -q`, result `54 passed`; `npm run build`, result passed.
- Wider check for `TASK_096`: `py -m pytest tests\unit tests\integration -q`, result `319 passed`, `7 failed`; failures are existing/directly unrelated to TASK_096 expectations around direct `.doc` intake, historical board-title assertions, and fake `.docx` header-gate setup.
- `TASK_097_DRAFTS_IN_PROGRESS_SURFACE` is complete: saved `draft_saved` creation packages are listed in a separate Drafts / In Progress panel, use `Continue` / `Discard`, and continue back into New Project Intake or Precheck rather than Project Workbench.
- Validation for `TASK_097`: `py -m pytest tests\integration\test_manual_intake_api.py tests\unit\test_project_creation_draft_lifecycle_service.py tests\unit\test_frontend_shell_files.py -q`, result `57 passed`; `npm run build`, result passed.
- Wider integration check for `TASK_097`: `py -m pytest tests\integration -q`, result `53 passed`, `1 failed`; the remaining failure is the existing fake `.docx` Word header-gate setup in `test_intake_package_repositories.py`.
- `TASK_098_PRECHECK_CONFIRMED_APPLICATION_EDITING` is complete: Precheck no longer offers `Back to Intake`, keeps save/discard exit paths, shows source files as traceability context, and confirms Projects from corrected Precheck draft data.
- Validation for `TASK_098`: `py -m pytest tests\unit\test_frontend_shell_files.py tests\integration\test_manual_intake_api.py tests\unit\test_intake_case_review_service.py -q`, result `66 passed`; `npm run build`, result passed.
- Wider integration check for `TASK_098`: `py -m pytest tests\integration -q`, result `53 passed`, `1 failed`; the remaining failure is the existing fake `.docx` Word header-gate setup in `test_intake_package_repositories.py`.
- User redirected the New Project workflow strategy on 2026-05-05: the current four-step frontend is too heavy and should be redesigned as a single New Project page combining request source, attachments, editable application information, LTR number choice, and project folder creation completion.
- `TASK_101_NEW_PROJECT_SINGLE_PAGE_FLOW_REDESIGN` is complete: `docs/new_project_single_page_flow_redesign.md` defines the single-page New Project UX/data-flow design, request email and attachment behavior, editable application information editor, field-level required guidance, no-silent-replace import rule, LTR/folder completion model, draft/cancel behavior, backend orchestration boundary, and implementation split.
- `TASK_102_NEW_PROJECT_SINGLE_PAGE_INTAKE_APPLICATION_EDITOR` is complete: `/intake` now uses one New Project page with request source, email information, attachments, attachment preview, editable SECTION 1 application information, automatic draft persistence through the review-field boundary, direct required-field red states, and a disabled `Apply LTR Number and Create Folder` completion affordance. A narrow `application-draft` API prepares the blank durable editor draft without importing a Word form.
- `TASK_103_APPLICATION_FORM_IMPORT_TO_EDITOR_NO_SILENT_REPLACE` is complete: Word attachment rows now expose explicit `Import`, attachment selection remains preview-only, double-click opens the stored file through the API download URL, import uses the existing backend `select-form` eligibility/header-gate/parser path, and replacement requires inline confirmation before manual editor data is cleared.
- Implementation sequence after `TASK_101`: `TASK_102_NEW_PROJECT_SINGLE_PAGE_INTAKE_APPLICATION_EDITOR`, `TASK_103_APPLICATION_FORM_IMPORT_TO_EDITOR_NO_SILENT_REPLACE`, `TASK_104_NEW_PROJECT_LTR_AND_FOLDER_ONE_ACTION_ORCHESTRATION`.
- `TASK_099_LTR_REGISTERED_FREEZE_AND_EXCEPTION_PATH` and `TASK_100_PROJECT_WORKBENCH_BOUNDARY_AFTER_FOLDER_CREATION` are paused until the single-page New Project redesign is resolved.
- Validation for `TASK_101`: `py -m pytest tests\unit\test_task101_single_page_flow_redesign.py tests\unit\test_frontend_shell_files.py -q`, result passed.
- Validation for `TASK_102`: `py -m pytest tests\unit\test_new_project_application_draft_service.py tests\unit\test_frontend_shell_files.py tests\integration\test_manual_intake_api.py -q`, result `60 passed`; `npm run build`, result passed.
- Validation for `TASK_103`: `py -m pytest tests\unit\test_intake_form_selection_service.py tests\unit\test_frontend_shell_files.py tests\integration\test_msg_package_intake_api.py -q`, result `73 passed`; `npm run build`, result passed.
- Recommended next controlled task: `TASK_104_NEW_PROJECT_LTR_AND_FOLDER_ONE_ACTION_ORCHESTRATION`, pending explicit user approval to activate.
- User approved an out-of-sequence, UI-only hotfix path (option 2) and authorized creating a dedicated task for the New Project editor textarea scrollbar behavior.
- `TASK_105_NEW_PROJECT_EDITOR_TEXTAREA_SCROLLBAR_HOTFIX` is complete: `Description of Requested Testing` and `Additional Information` textarea editors now use auto-grow behavior with no vertical drag/inner scroll, aligned with `Test Sample Information`.
- Validation for `TASK_105`: `npm run build`, result passed.
- User requested a follow-up visual consistency hotfix for New Project editor typography and Additional Information textarea border style.
- `TASK_106_NEW_PROJECT_EDITOR_TYPOGRAPHY_AND_ADDITIONAL_INFO_STYLE_HOTFIX` is complete: three editable table textareas now use typography aligned with select fields; `Additional Information` textarea now uses matching border color and corner radius.
- Validation for `TASK_106`: `npm run build`, result passed.
- User requested a messaging placement hotfix: remove redundant bottom guidance, move imported-form message beside `Application information`, and keep full filename readable in narrow layouts.
- `TASK_107_NEW_PROJECT_IMPORT_MESSAGE_PLACEMENT_AND_FOOTER_GUIDANCE_HOTFIX` is complete: redundant bottom guidance was removed during active package editing, import message now appears beside `Application information`, and narrow-layout wrapping keeps full filenames readable.
- Validation for `TASK_107`: `npm run build`, result passed.
- `TASK_108_NEW_PROJECT_IMPORTED_FORM_MESSAGE_COPY_STYLE_HOTFIX` is complete: removed `Imported application form:` prefix and restyled the imported filename message to normal black non-bold text.
- Validation for `TASK_108`: `npm run build`, result passed.
- `TASK_109_SIDEBAR_COLLAPSE_TOGGLE_FOR_SMALL_SCREEN_WORKSPACE` is complete: added sidebar collapse/expand control, icon-only collapsed navigation, and local persistence of collapse preference for better small-screen workspace width.
- Validation for `TASK_109`: `npm run build`, result passed; `py -m pytest tests\unit\test_frontend_shell_files.py -q`, result `50 passed`.
- `TASK_110_NEW_PROJECT_IMPORTED_FILENAME_VISIBILITY_AND_SAMPLE_TABLE_WIDTH_HOTFIX` is complete: imported application filename now remains visible beside `Application information` using selected form fallback, and sample table now uses wide editable columns with horizontal scrolling plus sticky `Actions` column for small-screen usability.
- Validation for `TASK_110`: `npm run build`, result passed; `py -m pytest tests\unit\test_frontend_shell_files.py -q`, result `50 passed`.
- User rejected TASK_110 sample-table width/scroll presentation and requested full revert for item #2 while keeping filename visibility fix.
- `TASK_111_REVERT_SAMPLE_TABLE_WIDTH_SCROLL_HOTFIX` is complete: reverted sample table wide columns, sticky `Actions`, and related scroll styling to previous behavior; imported filename visibility fix remains.
- Validation for `TASK_111`: `npm run build`, result passed.
- `TASK_112_COLLAPSED_SIDEBAR_EDITOR_AREA_EXPANSION` is complete: when sidebar is collapsed, New Project editor workspace width is expanded (main work area max width and left/right split adjusted), so the sample table columns widen proportionally with the card.
- Validation for `TASK_112`: `npm run build`, result passed.
- User requested selective (not proportional) widening in collapsed-sidebar mode.
- `TASK_113_COLLAPSED_SIDEBAR_SELECTIVE_SAMPLE_COLUMN_WIDENING` is complete: only `Contact Base Material` and `Contact Plating` columns widen in collapsed-sidebar mode; other sample columns remain unchanged.
- Validation for `TASK_113`: `npm run build`, result passed.
- User requested immediate rollback of the selective widening change.
- `TASK_114_REVERT_SELECTIVE_SAMPLE_COLUMN_WIDENING` is complete: removed collapsed-sidebar selective column widening override and restored prior column-width behavior.
- Validation for `TASK_114`: `npm run build`, result passed.
- User reported a severe readability risk: sample table content appears incomplete/clipped compared to Word source.
- `TASK_115_SAMPLE_TABLE_TEXT_VISIBILITY_AND_AUTOGROW_FIX` is complete: sample table typography is compacted for dense fields, table cells top-align content, and sample-row autogrow adds a clipping safety buffer so wrapped second lines remain fully visible.
- Validation for `TASK_115`: `npm run build`, result passed.
- User reported inline blue focus capsule still obscures content and requested a Word-like cell display.
- `TASK_116_SAMPLE_TABLE_INLINE_EDIT_VISUAL_DECONFLICT` is complete: sample-table inline editors now remove inner input chrome (border/radius/focus outline), keeping direct editing while making content read like plain table text.
- Validation for `TASK_116`: `npm run build`, result passed.
- User approved adding a subtle editing cue without intrusive input chrome.
- `TASK_117_SAMPLE_TABLE_FOCUS_ROW_SOFT_HIGHLIGHT` is complete: sample table now applies a soft row background highlight on `:focus-within` to indicate current edit row without covering text.
- Validation for `TASK_117`: `npm run build`, result passed.
- User requested a capsule-style editor retry with strict no-clipping behavior.
- `TASK_118_SAMPLE_TABLE_CAPSULE_RESTORE_WITH_NO_CLIP_AUTOGROW` is complete: restored capsule-like sample cell editor chrome, kept focus visuals without box-model jumps, and increased auto-grow safety buffer to prevent wrapped-line clipping.
- Validation for `TASK_118`: `npm run build`, result passed.
- User requested multiline auto-expand behavior for `Send copies of test results/reports to`.
- `TASK_119_SEND_COPIES_FIELD_AUTOGROW_TEXTAREA` is complete: `send_copies_recipients` now renders as an auto-grow textarea (Enter creates new lines and height expands automatically) while keeping other fields unchanged.
- Validation for `TASK_119`: `npm run build`, result passed.
- User requested visual alignment for the last `Actions` column between the two lower tables.
- `TASK_120_ALIGN_ACTIONS_COLUMN_WIDTH_BETWEEN_TABLES` is complete: unified `Actions` column width to 116px and centered content in both sample and requested-testing tables for consistent alignment.
- Validation for `TASK_120`: `npm run build`, result passed.
- User clarified intent: lower table actions column should be narrowed and action icon colors should stay consistently blue.
- `TASK_121_NARROW_REQUESTED_TESTING_ACTIONS_COLUMN_AND_BLUE_ICON_UNIFY` is complete: narrowed lower requested-testing `Actions` column to 92px and adjusted disabled action icon styling to a blue tone.
- Validation for `TASK_121`: `npm run build`, result passed.
- User requested rollback of the above two actions-column adjustments.
- `TASK_122_REVERT_TASK120_TASK121_ACTIONS_COLUMN_CHANGES` is complete: restored requested-testing `Actions` width to 112px, restored sample table `Actions` width to 10%, removed cross-table fixed-width alignment rule, and restored disabled action icon opacity behavior.
- Validation for `TASK_122`: `npm run build`, result passed.
- User requested removing sample-table blue capsule editors due to visibility issues.
- `TASK_123_REMOVE_SAMPLE_TABLE_CAPSULE_FOR_FULL_VISIBILITY` is complete: removed capsule-like inner borders/radius/focus chrome for sample table editors and returned to plain inline text appearance for maximum content visibility.
- Validation for `TASK_123`: `npm run build`, result passed.
- User requested `Test Sample Information` last-column action icons in blue.
- `TASK_124_SAMPLE_TABLE_ACTIONS_ICON_BLUE` is complete: sample table action icons now use blue tones for normal and disabled states.
- Validation for `TASK_124`: `npm run build`, result passed.
- copied-workbook LTR write hardening depends on explicit approval for a new phase

Active implementation task:

- None. `TASK_146_NEW_PROJECT_APPLY_LTR_ONLY_AND_COMPLETION_HANDOFF` is complete; do not start another task until the user explicitly approves the next controlled task.

Reason:

- `TASK_133` was allowed because `TASK_131` added lock/backup/short transaction infrastructure and `TASK_132` added no-write workbook row preview mapping.
- The user requested the next task after `TASK_133`; this integration is the next controlled step because the external workbook commit API exists but is not connected to the New Project operator workflow.
- The user approved continuing after `TASK_134`; this task addressed the known gap where missing annual sheets failed commit without a controlled bootstrap path.
- The user explicitly confirmed the attached blocker message should not block project creation at this stage; this task narrows the rule to warning-only.
- The user approved opening `TASK_137`; this task aligns specified-number classification and workbook commit guards with the confirmed `DL-YYYY-MM-NNN` baseline and suffix-token handling.
- `TASK_139` is allowed for plan review because `TASK_099` froze normal base-field editing after LTR registration and `TASK_100` bounded Project Workbench to post-creation work. The next safe mainline gap is a traceable request record for frozen-field corrections, without applying changes to workbook, folder, or project identity.
- `TASK_140` is allowed because the user explicitly approved the Phase 10C sequence and requested implementation. The change stays in New Project UX scope only: remove in-page draft delete/replacement confirmation friction while preserving backend confirmed-case protection and existing Drafts/In Progress draft-discard path.
- `TASK_141` is allowed because `TASK_140` removed New Project in-page confirmation friction and the next controlled prerequisite is backend duplicate classification/resolution so UI can safely wire resolution actions in `TASK_142`.
- `TASK_142` is allowed for plan review because user review found the package-level duplicate model is wrong for multi-application-form emails; draft identity must be corrected before the duplicate UI is finalized.
- `TASK_143` is allowed for plan review because manual smoke testing of `TASK_142` found the duplicate card still appears too early after email import and the operator flow must wait for application-form selection before loading or resolving the right-side `Application information` editor.
- `TASK_144` is allowed because user review found `Project setup confirmation` was page-local state that could leak across application-form switches and could not restore with existing draft loads.
- `TASK_145` is allowed for plan review because `TASK_144` is complete, the user has completed manual smoke testing, and Phase 10C needs validation and board sync before any next phase is activated.
- `TASK_146` is allowed for plan review because Phase 10C is validated and closed, the user explicitly deprioritized Drafts / In Progress, and the next mainline business boundary is New Project applying LTR only before handing off to Project workspace.

Prior completed note:

- `TASK_146_NEW_PROJECT_APPLY_LTR_ONLY_AND_COMPLETION_HANDOFF` is complete. New Project now applies/registers the LTR number and hands off to the Project workspace without previewing or generating the project folder. The completion API no longer returns folder fields, repeat completion for the same intake case returns the existing confirmed Project/LTR instead of creating a duplicate Project, and the frontend action now reads `Apply LTR Number`.
- Validation: `py -m pytest tests\integration\test_new_project_completion_api.py -q` passed, 4 passed; `py -m pytest tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell tests\unit\test_frontend_shell_files.py::test_task146_new_project_applies_ltr_before_project_handoff -q` passed, 2 passed; `py -m pytest tests\integration\test_new_project_completion_api.py tests\integration\test_ltr_workbook_write_commit_api.py tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell tests\unit\test_frontend_shell_files.py::test_task146_new_project_applies_ltr_before_project_handoff -q` passed, 8 passed; `npm run build` passed from `frontend`; `git diff --check` passed with LF/CRLF working-copy warnings only.

- `TASK_145_PHASE10C_VALIDATION_AND_BOARD_SYNC` is complete. The user-completed manual smoke test is recorded as Phase 10C manual validation evidence, targeted intake/New Project automated checks passed, frontend build passed, and the board is synced back to no active task pending the next explicit approval.
- Validation: broad selector `py -m pytest tests\unit\test_outlook_msg_source_import.py tests\integration\test_msg_package_intake_api.py tests\integration\test_manual_intake_api.py tests\unit\test_intake_case_review_service.py tests\unit\test_frontend_shell_files.py -q -k "msg or intake or task102 or task103 or task142 or task143 or task144 or project_setup"` returned 68 passed, 34 deselected, and 3 historical frontend shell expectation failures from older TASK_069/TASK_087/TASK_091 checks pulled in by the broad selector. Narrowed validation passed: `py -m pytest tests\unit\test_outlook_msg_source_import.py tests\integration\test_msg_package_intake_api.py tests\integration\test_manual_intake_api.py tests\unit\test_intake_case_review_service.py -q` passed, 50 passed; `py -m pytest tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell tests\unit\test_frontend_shell_files.py::test_task103_application_form_import_is_explicit_and_confirmed tests\unit\test_frontend_shell_files.py::test_task142_draft_duplicate_resolution_is_business_readable tests\unit\test_frontend_shell_files.py::test_task143_email_import_waits_for_application_form_selection -q` passed, 4 passed; `npm run build` passed from `frontend`; `git diff --check` passed with LF/CRLF working-copy warnings only.

- `TASK_144_PROJECT_SETUP_DRAFT_SCOPED_AUTOSAVE` is complete. New Project setup confirmation values are now persisted per intake case draft under `project_setup`, returned by case review APIs, included in review-field autosave, restored when switching/loading application drafts, and used by completion from the currently loaded draft-scoped state.
- Follow-up email source provenance display: the Email source panel now shows only the original source filename returned by the intake package response; the ConnLab storage path is no longer exposed in the UI.
- Follow-up email source filename wrapping: long filenames now wrap in the Email source panel, so suffixes such as `副本` stay visible instead of being clipped.
- Follow-up email source Unicode preservation: uploaded `.msg` display names now keep the original Unicode filename rather than the sanitized storage filename.
- Validation: `py -m pytest tests\unit\test_intake_case_review_service.py::test_review_service_persists_project_setup_per_draft tests\integration\test_manual_intake_api.py::test_review_fields_persists_requested_testing_rows tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell -q` passed, 3 passed; `npm run build` passed from `frontend`.

Prior completed note:

- `TASK_143_EMAIL_PACKAGE_SELECTION_TIME_DRAFT_LOADING_HOTFIX` is complete. `.msg` import now preserves source and attachments without immediately selecting the first attachment or preparing a draft when selectable Word forms are present; duplicate handling runs after explicit application-form selection; new, opened, and replaced drafts all load into right-side `Application information`; the duplicate card now lives in the Attachments selection context and shows only the application-form filename plus `Load existing` and `Reinitialize`. Follow-up manual-smoke fix: duplicate resolution now reloads an existing selected review directly instead of calling blank draft preparation again, preventing the right-side editor from flashing and then clearing.
- Follow-up completion friction cleanup: removed the extra controlled-workbook acknowledgement checkbox from New Project setup; the workflow now treats this risk as accepted and sends the existing backend preview acknowledgement automatically.
- Follow-up completion dock cleanup: replaced the sticky autosave guidance with the final completion dock, moved LTR mode and specified-number input beside `Apply LTR Number and Create Folder`, and kept the left setup panel focused on workbook row metadata.
- Follow-up specified LTR input clarity: specified-number mode now keeps the input highlighted and completion blocked until the value matches `DL-YYYY-MM-NNN`, `DL-YYYY-MM-NNN` plus letter-led suffix, or a letter-led alphanumeric suffix token; a `?` help control explains accepted examples.
- Follow-up sample-table blocker clarity: required empty sample cells now highlight the whole cell with a non-obstructive tint instead of adding capsule borders or placeholder text that would obscure table content; each non-empty sample row independently checks Product Name and Quantity.
- Follow-up default application-form loading: `.msg` import now preselects the first `.docx` application form and immediately runs the selected-form import/duplicate path; emails with no application form still prepare the no-form draft path. Duplicate buttons now place `Load existing` on the right as the primary/recommended action.
- Follow-up import logic review: selected-form and no-form duplicate enforcement were rechecked against the backend services. A stale duplicate-card state was fixed so any successful prepared or selected draft load clears previous duplicate state before showing right-side `Application information`.
- Validation: `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "duplicate or msg_package or application_form_import"` passed, 3 passed and 52 deselected; `py -m pytest tests\unit\test_frontend_shell_files.py::test_task143_email_import_waits_for_application_form_selection -q` passed, 1 passed; `py -m pytest tests\unit\test_frontend_shell_files.py::test_task142_draft_duplicate_resolution_is_business_readable tests\unit\test_frontend_shell_files.py::test_task143_email_import_waits_for_application_form_selection -q` passed, 2 passed; `py -m pytest tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell tests\unit\test_frontend_shell_files.py::test_task103_new_project_page_chrome_is_minimal tests\unit\test_frontend_shell_files.py::test_task134_new_project_uses_ltr_workbook_commit_before_folder -q` passed, 3 passed; `py -m pytest tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell -q` passed, 1 passed; `py -m pytest tests\unit\test_frontend_shell_files.py::test_task143_email_import_waits_for_application_form_selection tests\unit\test_frontend_shell_files.py::test_task142_draft_duplicate_resolution_is_business_readable -q` passed, 2 passed; `py -m pytest tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell tests\unit\test_frontend_shell_files.py::test_task103_application_form_import_is_explicit_and_confirmed -q` passed, 2 passed; `py -m pytest tests\unit\test_frontend_shell_files.py::test_task143_email_import_waits_for_application_form_selection tests\unit\test_frontend_shell_files.py::test_task142_draft_duplicate_resolution_is_business_readable tests\unit\test_frontend_shell_files.py::test_task103_application_form_import_is_explicit_and_confirmed -q` passed, 3 passed; `npm run build` passed from `frontend`; `git diff --check` passed with LF/CRLF working-copy warnings only.

Prior completed note:

- `TASK_142_EMAIL_PACKAGE_DRAFT_IDENTITY_AND_DUPLICATE_RESOLUTION` is complete. `.msg` import no longer blocks on package-level duplicate identity before a draft exists; selected-form draft identity is checked by selected application form filename + email source filename + email source size; no-form email drafts are checked only against other no-form drafts; duplicate conflicts return structured business-safe details and the New Project UI renders inline actions to open, replace, or create a separate draft only when allowed.
- Validation: `py -m pytest tests\unit\test_intake_form_selection_service.py tests\unit\test_msg_package_intake_service.py tests\integration\test_msg_package_intake_api.py -q` passed, 36 passed; `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "duplicate or msg_package or application_form_import"` passed, 3 passed and 51 deselected; `npm run build` passed from `frontend`; `git diff --check` passed with LF/CRLF working-copy warnings only. Full `py -m pytest tests\unit tests\integration -q` currently reports 415 passed and 9 existing unrelated baseline failures in historical frontend shell checks, board phase checks, and the legacy LTR workbook snapshot expectation.

Prior completed note:

- `TASK_141_EMAIL_PACKAGE_DUPLICATE_DETECTION_BACKEND` is complete. Manual `.msg` import now supports backend duplicate classification and explicit resolution actions (`open_existing`, `replace_existing`, `create_separate`). Duplicate imports without explicit resolution return structured `409` conflict detail. Replacement stages the new package before removing old unconfirmed package records and does not delete old stored files inside the uncommitted request; confirmed/project-linked packages remain protected.
- Validation: `py -m pytest tests\unit\test_msg_package_intake_service.py tests\integration\test_msg_package_intake_api.py -q` passed, 21 passed; `py -m pytest tests\unit tests\integration -q` currently has existing unrelated baseline failures in frontend shell historical checks, board-phase historical checks, and legacy LTR workbook snapshot expectation; `git diff --check` passed with LF/CRLF working-copy warnings only.

Prior completed note:

- `TASK_140_NEW_PROJECT_DRAFT_FRICTION_CLEANUP` is complete. New Project no longer shows `Cancel and remove draft`, form switching now directly replaces/rebinds the active unconfirmed creation draft, and the inline replacement confirmation panel is removed. Draft discard remains available in `Drafts / In Progress`.
- Validation: `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task096 or task102 or task103_application_form_import_is_explicit_and_confirmed or task103_new_project_page_chrome_is_minimal"` passed, 4 passed; `npm run build` passed from `frontend`; `py -m pytest tests\unit\test_frontend_shell_files.py -q` has existing unrelated baseline failures in `test_task087_intake_information_density_cleanup`, `test_task082_precheck_sample_rows_are_editable_with_icon_actions`, and `test_task091_intake_precheck_typography_uses_shared_ui_vocabulary`; `git diff --check` passed.

Prior completed note:

- `TASK_100_PROJECT_WORKBENCH_BOUNDARY_AFTER_FOLDER_CREATION` is complete. Project Workbench is now bounded to post-creation project status and source material management: creation-stage controls (application form upload, precheck run, local LTR commit, initial folder generation) are removed from Workbench, while evidence placement preview/place remains. Projects continue to use `Open`; Drafts / In Progress continue to use `Continue`.
- Validation: `py -m pytest tests\unit\test_frontend_shell_files.py -q` passed, 53 passed; `npm run build` passed from `frontend`; `py -m pytest tests\unit tests\integration -q` passed, 409 passed.

Prior completed note:

- `TASK_099_LTR_REGISTERED_FREEZE_AND_EXCEPTION_PATH` is complete. Normal New Project/Precheck base-field editing is now frozen after the intake case is tied to a project with a registered LTR. The API exposes frozen state and returns a 409 revise/exception message when stale clients attempt to change frozen base fields; the New Project editor shows the same message, disables normal editing, and stops autosave in frozen state.
- Validation: `py -m pytest tests\unit\test_intake_case_review_service.py -q` passed, 14 passed; `py -m pytest tests\integration\test_manual_intake_api.py::test_review_fields_returns_conflict_after_registered_ltr -q` passed, 1 passed; `py -m pytest tests\unit\test_frontend_shell_files.py::test_task099_new_project_editor_exposes_ltr_registered_freeze_state -q` passed, 1 passed; `py -m pytest tests\integration\test_new_project_completion_api.py tests\integration\test_manual_intake_api.py tests\unit\test_frontend_shell_files.py -q` passed, 66 passed; `py -m pytest tests\unit tests\integration -q` passed, 408 passed; `npm run build` passed from `frontend`.

Prior completed note:

- `TASK_138_LTR_SUFFIX_TOKEN_STRICT_INPUT_AND_BOARD_CLEANUP` is complete. Suffix-token-only specified LTR input now validates the raw trimmed token, so internal spaces and other non-alphanumeric characters are rejected instead of normalized away. The stale pending TASK_133 rule-clarification block was replaced with implemented-rule notes for TASK_137/TASK_138.
- Validation: `py -m pytest tests\unit\test_ltr_number_rules.py tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py -q` passed, 35 passed; `py -m pytest tests\unit tests\integration -q` passed, 403 passed; `git diff --check` passed with LF/CRLF working-copy warnings only.

Prior completed note:

- `TASK_137_LTR_SPECIFIED_NUMBER_RULES_AND_YEAR_MONTH_GUARDS` is complete. `Use specified LTR number` now uses explicit category handling (base/full/suffix token), rejects invalid specified inputs with actionable errors, enforces base existence requirements for associated input, preserves replacement behavior for existing full numbers, and keeps year-sheet bootstrap plus duplicate guards on commit paths.
- Validation: `py -m pytest tests\unit\test_ltr_number_rules.py tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py -q` passed, 33 passed; `py -m pytest tests\unit tests\integration -q` passed, 401 passed.

Prior completed note:

- `TASK_136_REVISION_H_NON_BLOCKING_IN_NEW_PROJECT_PRECHECK` is complete. SECTION 1 `Revision must be H` is now warning-only during New Project creation precheck and no longer blocks completion, while `Form No. must be E-3718` remains an error-level blocker.
- Validation: `py -m pytest tests\unit\test_intake_section1_precheck.py tests\integration\test_manual_intake_api.py -q` passed, 12 passed; `py -m pytest tests\unit tests\integration -q` passed, 394 passed.

Prior completed note:

- `TASK_135_LTR_WORKBOOK_YEAR_SHEET_BOOTSTRAP` is complete. External LTR workbook commit now supports a controlled bootstrap path for missing annual sheets: when enabled by settings and explicitly acknowledged by the operator, the commit flow copies a configured template sheet, clears configured data rows, verifies the target year sheet exists, and then continues the same locked backup + short transaction write path.
- Validation: `py -m pytest tests\unit\test_ltr_workbook_write_commit_service.py tests\unit\test_ltr_workbook_transaction_gateway.py tests\unit\test_excel_com_ltr_workbook_gateway.py tests\integration\test_ltr_workbook_write_commit_api.py -q` passed, 23 passed; `py -m pytest tests\unit tests\integration -q` passed, 392 passed.

Prior completed note:

- `TASK_134_NEW_PROJECT_LTR_WORKBOOK_COMMIT_UI_INTEGRATION` is complete. New Project now requires an explicit controlled-workbook acknowledgement, confirms the intake case, commits the LTR workbook write through the TASK_133 API, records the workbook action/sheet/row/backup message, and then reuses New Project completion to generate the project folder with the committed LTR number. If folder generation fails after a workbook commit, retry skips duplicate case confirmation and duplicate workbook write.
- Validation: `py -m pytest tests\integration\test_new_project_completion_api.py tests\integration\test_ltr_workbook_write_commit_api.py tests\unit\test_frontend_shell_files.py -q` passed, 56 passed; `npm run build` passed; `py -m pytest tests\unit tests\integration -q` passed, 389 passed.

Prior completed note:

- `TASK_133_LTR_WORKBOOK_WRITE_COMMIT` is complete. The backend now has an operator-confirmed LTR workbook write commit service and API that require preview acknowledgement, use the lock/backup/short transaction gateway, re-scan workbook-visible numbers inside the write transaction, support the approved specified-number classifications, replace existing workbook rows or append new rows, and register local LTR records only after a successful workbook save.
- Validation: `py -m pytest tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py tests\unit\test_excel_com_ltr_workbook_gateway.py tests\unit\test_ltr_number_rules.py tests\unit\test_ltr_workbook_write_preview_service.py -q` passed, 34 passed; `py -m pytest tests\unit tests\integration -q` passed, 387 passed.

Prior completed note:

- `TASK_132_LTR_WORKBOOK_WRITE_PREVIEW` is complete. Confirmed project data and New Project setup confirmation values now map into a no-write LTR workbook A:Q row preview with workbook path, target sheet, target row when known, column values, and warnings.
- Validation: `py -m pytest tests\unit\test_ltr_workbook_write_preview_service.py tests\integration\test_ltr_workbook_write_preview_api.py tests\unit\test_ltr_workbook_transaction_gateway.py tests\unit\test_excel_com_ltr_workbook_gateway.py -q` passed, 14 passed; `py -m pytest tests\unit tests\integration -q` passed, 376 passed; `git diff --check` passed with CRLF working-copy warnings only.

Prior completed note:

- `TASK_131_LTR_WORKBOOK_LOCK_BACKUP_AND_SHORT_TRANSACTION_GATEWAY` is complete. LTR workbook write transactions now have an infrastructure-only gateway for exclusive lock acquisition, bounded wait/timeout, write-before backup, short COM write session execution, workbook close, and lock release.
- Validation: `py -m pytest tests\unit\test_ltr_workbook_transaction_gateway.py tests\unit\test_excel_com_ltr_workbook_gateway.py -q` passed, 9 passed; `py -m pytest tests\unit tests\integration -q` passed, 371 passed; `git diff --check` passed with CRLF working-copy warnings only.

Prior completed note:

- `TASK_130_EXTERNAL_EXCEL_STRUCTURE_PROBES` is complete. External Excel resources now have read-only `.xlsx` structure probes for expected sheets, headers, and date-like headers. The probes are connected to external resource validation for standard record and equipment calibration Excel files, while LTR workbook validation remains read-only through the existing snapshot gateway.
- Validation: `py -m pytest tests\unit\test_excel_structure_probe.py tests\unit\test_external_resource_service.py tests\unit\test_ltr_workbook_snapshot_gateway.py -q` passed, 17 passed; `py -m pytest tests\unit tests\integration -q` passed, 367 passed.

Prior completed note:

- `TASK_129_SECRET_AND_LOCAL_SETTINGS_POLICY` is complete. LTR workbook local settings now expose a redacted safe summary, reject invalid positive-integer policy values, preserve local/env password loading without hard-coding secrets, and document the local secret policy plus future Windows Credential Manager direction.
- Validation: `py -m pytest tests\unit\test_config.py -q` passed, 6 passed; `py -m pytest tests\unit tests\integration -q` passed, 362 passed.

Prior completed note:

- `TASK_128_EXTERNAL_RESOURCE_REGISTRY_AND_VALIDATION` is complete. External resources now have SQLite-backed registration, active state, validation status, last validation time, and failure reason. Backend APIs can list, upsert, and validate `ltr_workbook`, `application_form_template`, `project_folder_template`, `standard_record_excel`, and `equipment_calibration_excel` without writing public-drive Excel files.
- Validation: `py -m pytest tests\unit\test_external_resource_service.py tests\integration\test_external_resource_api.py -q` passed, 9 passed; `py -m pytest tests\unit tests\integration -q` passed, 359 passed.

Prior completed note:

- `TASK_127_LOOKUP_OPTIONS_SAFE_UPDATE_AND_IMPORT` is complete. New Project setup confirmation `Location` and `Test Type in sheet` now use the existing database-backed lookup option service with required default backfill for new and existing databases. A local TOML import API updates/ disables lookup options without deleting old records and backs up SQLite before import.
- Validation: `py -m pytest tests\unit\test_lookup_options_service.py tests\integration\test_lookup_options_api.py tests\integration\test_new_project_completion_api.py -q` passed, 9 passed; `py -m pytest tests\unit tests\integration -q` passed, 350 passed; `npm run build` passed from `frontend`.

Prior completed note:

- `TASK_126_NEW_PROJECT_SETUP_CONFIRMATION_REQUIRED_FIELDS_REWORK` is complete. LTR/setup confirmation controls now live in the left-side project setup card, obsolete blockers were loosened, and the main completion button remains in the Application information footer.
- Validation: `py -m pytest tests\unit tests\integration -q` passed, 347 passed; `npm run build` passed from `frontend`.

Prior completed note:

- `TASK_125_FULL_TEST_SUITE_HISTORICAL_EXPECTATION_SYNC` is complete. Historical test expectations now match current `.docx` intake, eligibility-gated form selection, candidate scoring, and task-board phase progression.
- Validation: `py -m pytest tests\unit tests\integration -q` passed, 347 passed.

Prior completed note:

- `TASK_104_NEW_PROJECT_LTR_AND_FOLDER_ONE_ACTION_ORCHESTRATION` is complete. New Project now has a one-action completion path for intake confirmation, LTR registration, folder preview, folder generation, and Workbench routing.
- Validation: `py -m pytest tests\integration\test_new_project_completion_api.py tests\integration\test_ltr_local_commit_api.py -q` passed; `npm run build` passed from `frontend`. Follow-up TASK_125 full-suite stabilization is complete; `py -m pytest tests\unit tests\integration -q` now passes with 347 tests.

Prior completed note:

- `TASK_139_LTR_FROZEN_FIELD_REVISION_REQUEST_RECORD` is complete. Added a structured frozen-field revision request record path after LTR registration freeze with typed create/list/detail APIs, strict frozen-field validation against `IntakeCaseReviewService` authoritative keys, and persisted backend current-value snapshots plus operator proposed values/reason without mutating intake draft data, project identity, workbook, or folder.
- Validation: `py -m pytest tests\unit\test_frozen_field_revision_request_service.py tests\integration\test_frozen_field_revision_request_api.py tests\unit\test_intake_case_review_service.py -q` passed, 19 passed; `git diff --check` passed with LF/CRLF working-copy warnings only.

Next recommended action:

- `TASK_149_SETTINGS_EXTERNAL_RESOURCES_UI_AND_LOCAL_PATHS` is complete. Settings is now reachable from the sidebar, lists registry-backed external resources, supports manual path paste, active-state save, per-resource validation, and business-readable validation state. `project_output_root` is represented as a directory-style external resource and validates existing readable directories without requiring them to be non-empty. Local LTR workbook backup and lock directories are shown as local-machine settings still owned by TOML/environment configuration.
- Validation: `py -m pytest tests\integration\test_external_resource_api.py tests\unit\test_external_resource_service.py -q` passed, 12 passed; `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "settings or external"` passed, 1 passed and 56 deselected; `npm run build` passed from `frontend`; `git diff --check` passed with LF/CRLF working-copy warnings only.
- TASK_149 manual usability follow-up is complete. Settings path rows now include a `...` browse entry beside the path input and show an inline desktop-shell guidance message when clicked. The current Web UI still uses manual path paste; no native file picker, upload flow, workbook write behavior, or folder generation behavior was added.
- Follow-up validation: `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "settings or external"` passed, 1 passed and 56 deselected; `npm run build` passed from `frontend`; `git diff --check` passed with LF/CRLF working-copy warnings only.
- `TASK_150_PROJECT_FOLDER_USES_CONFIGURED_RESOURCES` is complete. Project Workbench folder creation now resolves `project_folder_template` and `project_output_root` from Settings resources, shows configured resource state inline, blocks preview/generation when required resources are missing/inactive/invalid, and preserves existing preview-before-write plus conflict blocking behavior. Raw template/target path entry is no longer the normal business path.
- Validation: `py -m pytest tests\integration\test_folder_generation_api.py tests\integration\test_external_resource_api.py -q` passed, 5 passed; `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or folder or settings"` passed, 6 passed and 52 deselected; `npm run build` passed from `frontend`; `git diff --check` passed with LF/CRLF working-copy warnings only.

- Phase 10E task sequence is complete.
- The next business mainline is no longer additional standard/equipment Excel expansion.
- The next business mainline is real-world LTR application against the configured public-drive workbook path.

- `TASK_162_NO_LTR_PROJECT_CLEANUP_EXECUTION` is complete.

- Proposed Phase 10F task sequence:
  - `TASK_154_PHASE10F_SCOPE_AND_BOARD_ACTIVATION`
  - `TASK_155_REAL_PUBLIC_DRIVE_LTR_WORKBOOK_COMPATIBILITY_BASELINE`
  - `TASK_156_REAL_LTR_APPLICATION_SMOKE_AND_FAILURE_HANDLING`
  - `TASK_160_NEW_PROJECT_LTR_ATOMIC_COMPLETION_GATE`
  - `TASK_161_HISTORICAL_PROJECT_LTR_CLEANUP_DRY_RUN`
  - `TASK_162_NO_LTR_PROJECT_CLEANUP_EXECUTION`
  - `TASK_157_LTR_WORKBOOK_SQLITE_RECONCILIATION_AND_AUDIT_CHECK`
- Recommended next action: use the dry-run result to select explicit no-LTR Project IDs for cleanup execution, or open the next controlled task.
- Do not implement code or any later task before the next task is explicitly approved.

- `TASK_162_NO_LTR_PROJECT_CLEANUP_EXECUTION` is complete. Added `NoLtrProjectCleanupService`, `project_cleanup_audit_records`, repository wiring, and `POST /api/cleanup/project-ltr/no-ltr-projects/execute`. The endpoint requires explicit Project IDs and a cleanup reason, re-checks that each Project has no registered LTR before mutation, marks eligible Projects as `cancelled`, and writes one audit row per changed Project. It does not physically delete rows, touch files, mutate workbook data, recycle LTR numbers, or handle invalid registered LTR records.
- Validation: `py -m pytest tests\unit\test_no_ltr_project_cleanup_service.py tests\integration\test_cleanup_api.py -q` passed (6 passed).
- Live cleanup execution after user approval: selected 25 `project_without_registered_ltr` candidates from dry-run, cancelled all 25, rejected 0, and wrote 25 cleanup audit records. Post-check status distribution in `data\connlab.sqlite3`: `cancelled=25`, `folder_created=1`, `ltr_registered=2`.

- `TASK_163_PROJECT_REGISTRY_CANCELLED_VISIBILITY_FILTER` is proposed. This task updates the Project Registry UI to hide `cancelled` Projects by default after TASK_162 cleanup, adds an explicit `Show cancelled` operator control, and keeps search, metrics, pagination, and empty states aligned with the visible registry scope. Plan: `docs/task_163_project_registry_cancelled_visibility_filter_plan.md`.
- `TASK_163_PROJECT_REGISTRY_CANCELLED_VISIBILITY_FILTER` is complete. Project Registry now hides `cancelled` Projects by default, adds a `Show cancelled` toolbar control, aligns metrics/search/pagination with visible scope, and shows dedicated scope empty-state guidance plus a hidden-cancelled count note.
- Validation: `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "project_dashboard"` passed (`1 passed, 57 deselected`); `npm run build` from `frontend` passed.

- `TASK_164_NEW_PROJECT_DRAFT_SCOPE_DUPLICATE_ONLY` is complete. New Project duplicate checks are now limited to draft/package scope. Confirmed-project duplicate conflict branch (`existing_confirmed_project_ltr`) was removed from intake selected-form flow, API mapping, frontend duplicate DTO union, and attachment-panel reminder/action wiring. Draft duplicate resolution behavior remains unchanged.
- Validation: `py -m pytest tests\unit\test_intake_form_selection_service.py tests\integration\test_msg_package_intake_api.py -q` passed (`36 passed`); `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "duplicate_scope or task147 or duplicate"` passed (`2 passed, 56 deselected`); `npm run build` from `frontend` passed.

- `TASK_165_PROJECTS_PAGE_REMOVE_DRAFTS_SURFACE` is complete. Projects page now removes the `Drafts / In Progress` section and related continue/discard actions. Draft data and backend APIs are preserved; this task is UI-scope cleanup only.
- Validation: `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "project_dashboard or projects_page_removes_drafts_surface_after_task163 or task100_workbench"` passed (`3 passed, 55 deselected`); `npm run build` from `frontend` passed.

- Product decision update (2026-05-10): do not add a separate Draft list/management surface in Projects or New Project for now. Draft recovery remains selection-time/import-time only (`Load existing` / `Reinitialize`) within New Project. This is intentional scope control to keep duplicate and workflow boundaries simple.

- `TASK_161_HISTORICAL_PROJECT_LTR_CLEANUP_DRY_RUN` is complete. Added a read-only cleanup audit service and `GET /api/cleanup/project-ltr/dry-run`, classifying no-registered-LTR projects, invalid registered LTR numbers, multiple registered LTRs per project, and orphan LTR records. No database mutation or workbook operation is performed. Live local dry-run found `total_projects=28`, `total_ltr_records=5`, and `project_without_registered_ltr=25`.
- Validation: `py -m pytest tests/unit/test_project_ltr_cleanup_audit_service.py -q` passed (1 passed); `py -m pytest tests/integration/test_cleanup_api.py -q` passed (1 passed).

- `TASK_160_NEW_PROJECT_LTR_ATOMIC_COMPLETION_GATE` is complete. New Project frontend completion now calls only backend `complete-new-project`; it no longer directly confirms intake cases or directly calls workbook write commit before backend orchestration. The failure regression now asserts workbook commit failure leaves no confirmed project link and no Project record, preventing new no-LTR Project Registry entries from this path.
- Validation: `py -m pytest tests/integration/test_new_project_completion_api.py -q` passed (5 passed); `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "new_project or project"` passed (10 passed, 48 deselected); `npm run build` passed from `frontend`.

- `TASK_156_REAL_LTR_APPLICATION_SMOKE_AND_FAILURE_HANDLING` is complete. LTR authority commit failures now return clearer operator guidance for lock timeout/read-only/write-disabled/backup-failure classes, and direct workbook commit API now maps lock-timeout to `409 Conflict` with existing business failures kept as `400`. Real configured workbook compatibility baseline was manually verified at `D:\LabShare\LTR\LTR.xls` (`compatible=true`, no blockers).
- Validation: `py -m pytest tests/unit/test_ltr_excel_authority_adapter.py tests/integration/test_ltr_workbook_write_commit_api.py tests/integration/test_new_project_completion_api.py -q` passed (13 passed).
- `TASK_159_NEW_PROJECT_LTR_RESULT_VISIBILITY_AND_PROJECT_REGISTRY_PAGINATION` is complete (approved hotfix). New Project completion now writes a one-time result snapshot into session storage before redirect; Project Registry displays the latest apply result (LTR number + workbook sheet/row/backup when available) and supports dismiss. Project Registry `20 / page` is now real client-side pagination with Prev/Next page controls.
- Validation: `npm run build` passed from `frontend`.
- `TASK_155_REAL_PUBLIC_DRIVE_LTR_WORKBOOK_COMPATIBILITY_BASELINE` is complete. Added a read-only compatibility baseline service and API for configured `ltr_workbook` resources (`GET /api/external-resources/ltr-workbook/compatibility-baseline`) that checks resource registration/active state, file/open-read viability through the Office boundary, year-sheet presence, and write prerequisites (write enabled, password, lock/backup dirs), and reports blockers as actionable diagnostics.
- Validation: `py -m pytest tests\unit\test_ltr_workbook_compatibility_service.py tests\integration\test_ltr_workbook_compatibility_api.py -q` passed (5 passed); `py -m pytest tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py tests\integration\test_new_project_completion_api.py -q` passed (19 passed).
- Operational note update (2026-05-10): real configured workbook path is now active and compatibility baseline is manually verified; operator-smoke hardening moved from deferred state to completed under `TASK_156`.

- `TASK_154_PHASE10F_SCOPE_AND_BOARD_ACTIVATION` is complete. Phase 10F is now formally activated and the business mainline is explicitly focused on real public-drive LTR workbook operations (`LTR.XLS`/configured workbook path) instead of further standard/equipment Excel expansion.
- Validation: board/document sync only (no runtime code changes and no test scope required for this activation task).

- `TASK_153_LTR_AUTHORITY_SERVER_CUTOVER_SEAM` is complete. Added explicit LTR authority seam (`LtrAuthorityPort`), Excel authority adapter wiring, New Project authority-based orchestration dependency, static boundary tests preventing route-level workbook/COM leakage, and migration note document `docs/ltr_authority_cutover_seam.md`.
- Validation: `py -m pytest tests\integration\test_new_project_completion_api.py -q` passed (5 passed); `py -m pytest tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py -q` passed (14 passed); `py -m pytest tests\unit\test_ltr_authority_boundary.py tests\unit\test_frontend_shell_files.py -q -k "new_project or ltr or authority"` passed (10 passed, 50 deselected).

- `TASK_152_STANDARD_AND_EQUIPMENT_RESOURCE_READ_MODELS` is complete. Added read-only structured models and APIs for configured `standard_record_excel` and `equipment_calibration_excel` resources, with query filtering and sheet/header-based XLSX parsing through OfficeFacade/ExcelWorkbookGateway without write behavior.
- Validation: `py -m pytest tests\unit\test_excel_structure_probe.py tests\unit\test_external_resource_service.py -q` passed (12 passed); `py -m pytest tests\unit\test_external_excel_read_service.py -q` passed (3 passed); `py -m pytest tests\integration\test_external_resource_api.py tests\integration\test_external_excel_read_api.py -q` passed (6 passed).

- `TASK_151_NEW_PROJECT_LTR_WORKBOOK_AUTHORITY` is complete. New Project `complete-new-project` now commits through workbook-authority LTR write service, uses workbook-visible numbers for auto allocation, supports specified-number/suffix-token input pass-through, returns workbook write metadata (path/sheet/row/backup), and blocks local LTR registration when workbook write fails.
- Validation: `py -m pytest tests\unit\test_ltr_number_rules.py tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py -q` passed (39 passed); `py -m pytest tests\integration\test_new_project_completion_api.py -q` passed (5 passed); `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "new_project or ltr"` passed (8 passed, 50 deselected); `npm run build` passed from `frontend`.

Planning note:

- Phase 10E recognizes the current lab reality: public-drive Excel files remain authoritative for LTR numbering and other shared lab resources, while ConnLab stores structured local records and prepares for a future server/database authority.
- Development should use local simulated public-drive paths configured through Settings, not hard-coded paths and not the real public-drive workbook.
- Phase 10F shifts the mainline from architecture expansion back to operational closure on the real LTR workbook business path.
- Standard/equipment Excel read-model work is no longer the immediate priority; real LTR application behavior against the configured workbook path is.

Prior completed note:

- `TASK_148_PROJECT_WORKBENCH_FOLDER_CREATION_UX` is complete. Project Workbench now owns initial project folder creation after LTR registration: it previews folder generation, blocks conflicts, creates the folder through existing APIs, refreshes project state, shows the recorded folder path, and then enables evidence placement. A read-only `GET /api/projects/{project_id}/folder/latest` endpoint supports persisted folder-path display after reload. New Project remains LTR-only and does not create folders.
- Validation: `py -m pytest tests\integration\test_folder_generation_api.py tests\integration\test_project_lifecycle_gating_api.py -q` passed, 4 passed; `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or folder"` passed, 4 passed and 52 deselected; `py -m pytest tests\integration\test_new_project_completion_api.py -q` passed, 4 passed; `npm run build` passed from `frontend`; `git diff --check` passed with CRLF working-copy warnings only.
- Known validation note: full `tests\unit\test_frontend_shell_files.py` still has 4 historical static assertion failures in Intake/Precheck/Draft expectations, outside TASK_148 Workbench/folder scope.

Backlog note:

- `TASK_147` implemented confirmed Project/LTR duplicate reminders for imported email/application-form identity matches. `Import as new anyway` remains deferred unless explicitly approved in a future task.

Implemented LTR number rule clarification:

- `TASK_137` implemented specified-number classification for base DL numbers, full base-plus-suffix numbers, and suffix-token-only input.
- `TASK_138` tightens suffix-token-only input so any non-alphanumeric character, including internal spaces, is rejected instead of normalized away.

Do not start yet:

- Outlook inbox auto-scan
- email sending
- any Matrix, Report, AI review, LAN deployment, permissions, or future-scope feature
