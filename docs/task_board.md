# ConnLab Task Board

> Status: TASK_149 complete + TASK_150-153 archived as historical reference (not implemented) + TASK_154-TASK_156 complete + TASK_157 archived as historical reference (not implemented) + TASK_199 abandoned (superseded by implementation-first approach) + TASK_250 abandoned (Anti-Goal) + TASK_252CI completed (Change Source Matrix button) + TASK_159 hotfix complete + TASK_160 complete + TASK_161 complete + TASK_162 complete + TASK_163 complete + TASK_164 complete + TASK_165 complete + TASK_166 complete + TASK_167 complete + TASK_168 complete + TASK_169 complete + TASK_170 complete + TASK_171 complete + TASK_172 complete + TASK_173 complete + TASK_174 complete + TASK_175 complete + TASK_176 complete + TASK_177 complete + TASK_178 complete + TASK_179 complete + TASK_180 complete + TASK_181 complete + TASK_182 complete + TASK_183 complete + TASK_184 complete + TASK_185 complete + TASK_186 complete + TASK_187 complete + TASK_188 frontend status complete + TASK_188 ledger correction complete + TASK_189 corrected + TASK_189 authority read-model correction complete + TASK_190 corrected and accepted + TASK_191 complete + TASK_192 complete + TASK_193 complete + TASK_194 complete + TASK_195 complete + TASK_196 complete + TASK_197 complete + TASK_198 complete + TASK_200 complete + TASK_201 complete + TASK_202 complete + TASK_203 Slice A/B/C/D complete + TASK_204 complete + TASK_205 complete + TASK_206 complete + TASK_207 complete + TASK_208 complete + TASK_209 complete + TASK_210 complete + TASK_211 complete + TASK_212 complete + TASK_213 complete + TASK_214 complete + TASK_215 complete + TASK_216 complete + TASK_217 complete + TASK_218 complete + TASK_219 complete + TASK_219A complete + TASK_219B complete + TASK_219C complete + TASK_219D complete + TASK_219E complete + TASK_219F complete + TASK_220 complete + TASK_221 complete + TASK_222 complete + TASK_223 complete + TASK_224 complete + TASK_225 complete + TASK_226 complete + TASK_227 complete + TASK_228 complete + TASK_229A complete + TASK_229B complete + TASK_230 complete + TASK_231 complete + TASK_243 complete + TASK_244 complete + TASK_245 complete + TASK_246 complete + TASK_247 complete + TASK_248 complete + TASK_249 complete + TASK_253 complete + TASK_254 complete + TASK_255 complete + TASK_256 complete + TASK_257 complete + TASK_258 complete + TASK_259 complete + TASK_260 complete + TASK_261 complete + TASK_262 complete + TASK_262A complete + TASK_262B complete + TASK_263 complete + TASK_264 complete + TASK_265 complete + TASK_266 complete + TASK_267 complete + DOCS_001 complete + Markdown file organization complete + Core docs (AGENTS.md, DESIGN.md, PRODUCT.md) moved back to root directory + TASK_268 complete
> Last Updated: 2026-05-24
> Current Source Of Truth: `docs/task_board.md`
> Current Active Task: none (`TASK_268_GROUP_SELECTION_COMPLETENESS_GUARD` complete; awaiting next approved task).
> Current Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

- Runtime governance policy update (post TASK_202): governance-only expansion is frozen by default. New tasks must produce at least one consumable runtime artifact (backend runtime artifact, projection consumer artifact, runtime adapter, immutable read-model output, frontend read-only prototype, aggregation consumer, or runtime projection consumption validation), unless implementation is genuinely blocked by a documented architectural contradiction.
- Runtime direction update: prioritize consumer-first slices (read-only projection consumers, immutable runtime summaries, frontend-consumable adapters, fake/static refresh prototypes). Avoid runtime engine/orchestration/persistence complexity and ontology recursion before consumer validation.
- Projection minimality enforcement: new projection DTOs are not allowed unless insufficiency of existing DTOs is explicitly proven in task plan acceptance criteria.
- UI boundary reaffirmed: current Project Workbench remains temporary shell; future UI work should use Runtime Console baseline replacement. Matrix definition editing remains in Matrix Editor (Definition Studio), not in Workbench.
- Governance principles unchanged: `Projection != Domain Identity`; `Runtime Projection is not source of truth`; `Projection composition must remain independently evolvable`.
- Task planning rule update: every new task file must include a `Model Fit Assessment` section that explicitly states whether `GPT-5.3-codex` is suitable for execution and why.
- `TASK_268_GROUP_SELECTION_COMPLETENESS_GUARD` is complete. Group Selection mode now shows selected group count, selected step count when derivable, sample quantity visibility in headers and summary, inline confirmation summary, and explicit zero-selection blocker while keeping TASK_261 commit API unchanged.
- Deliverables: `frontend/src/features/matrix-editor/matrixImportSelectionSelectors.ts`, `frontend/src/features/matrix-editor/MatrixImportSelectionMode.tsx`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`, `frontend/src/workbench.css`, `tests/unit/test_frontend_shell_files.py`, `tasks/TASK_268_GROUP_SELECTION_COMPLETENESS_GUARD.md`, and `docs/task_268_group_selection_completeness_guard_plan.md`.
- Validation: `py -m pytest tests\\unit\\test_frontend_shell_files.py -q -k "task268 or task267 or matrix_editor"` passed (`36 passed, 73 deselected`); `cd frontend; npm test -- --run MatrixEditorWorkspace` passed (`13 passed`); `cd frontend; npm run build` passed; `py -m pytest tests\\integration\\test_matrix_to_test_record_smoke_flow_api.py -q` passed (`1 passed`).
- Scope boundary held: frontend-only completeness guard; no backend/API/database/Test Record generation/Project Workbench projection/StepInstance scope was introduced.
- `TASK_262_MATRIX_IMPORT_GROUP_SELECTION_VIEW` is complete. Matrix import flow now gates through a Group Selection View after preview parsing, then calls `POST /api/projects/{project_id}/matrix-import/commit` using preview payload + selected group keys, and loads returned selected-only `ProjectMatrixDraft` (`created`/`reused` treated as success). Deliverables: `frontend/src/api/client.ts`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `frontend/src/features/matrix-editor/MatrixImportGroupSelectionView.tsx`, `frontend/src/features/matrix-editor/matrixImportSelectionSelectors.ts`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`, `frontend/src/workbench.css`, `tests/unit/test_frontend_shell_files.py`, and `tasks/completed/2026/TASK_262_MATRIX_IMPORT_GROUP_SELECTION_VIEW.md`. Validation: `py -m pytest tests\\unit\\test_frontend_shell_files.py -q -k "task262 or matrix_editor"` passed (`35 passed`); `cd frontend; npm test -- --run MatrixEditorWorkspace` passed (`3 passed`); `cd frontend; npm run build` passed.
- `TASK_262A_MATRIX_IMPORT_SELECTION_MODE_AND_ACTION_CLARITY` is complete. Matrix import flow now enters inline selection mode (Test Item + group columns with header checkboxes), hides `Section/Method/Condition/Requirement` and draft/revision actions while selecting, and commits selected groups through TASK_261 API before returning to normal edit mode. Append Matrix is visible as a disabled future placeholder with lineage-required messaging.
- Deliverables: `frontend/src/features/matrix-editor/MatrixImportSelectionMode.tsx`, `frontend/src/features/matrix-editor/matrixImportSelectionSelectors.ts`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`, `frontend/src/workbench.css`, `tests/unit/test_frontend_shell_files.py`, and `tasks/completed/2026/TASK_262A_MATRIX_IMPORT_SELECTION_MODE_AND_ACTION_CLARITY.md`.
- Validation: `py -m pytest tests\\unit\\test_frontend_shell_files.py -q -k "task262a or matrix_editor"` passed (`34 passed`); `cd frontend; npm test -- --run MatrixEditorWorkspace` passed (`3 passed`); `cd frontend; npm run build` passed.
- `TASK_262B_MATRIX_IMPORT_PREVIEW_DETECTION_FEEDBACK_HARDENING` is complete. Matrix import preview detection now rejects revision/history tables before Matrix scoring, including tables whose description text mentions `TEST GROUP` or `SAMPLE QTY`, while preserving real Matrix support for numeric/alphanumeric group headers. Reparse miss/error states keep the converted PDF preview available and jump it to the operator-entered page so the user can continue reviewing nearby pages.
- Deliverables: `tasks/completed/2026/TASK_262B_MATRIX_IMPORT_PREVIEW_DETECTION_FEEDBACK_HARDENING.md`, `docs/completed_plans/2026/task_262b_matrix_import_preview_detection_feedback_hardening_plan.md`, `backend/modules/test_plan/product_spec_matrix_parser.py`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`, and `tests/unit/test_product_spec_matrix_parser.py`.
- Validation: `py -m pytest tests\\unit\\test_product_spec_matrix_parser.py -q` passed (`13 passed`); `py -m pytest tests\\integration\\test_project_test_plan_preview_api.py -q` passed (`6 passed`); `py -m pytest tests\\unit\\test_frontend_shell_files.py -q -k "task262 or matrix_editor"` passed (`35 passed`); `cd frontend; npm test -- --run MatrixEditorWorkspace` passed (`5 passed`); `cd frontend; npm run build` passed.
- `TASK_263_CONFIRMED_MATRIX_TEST_RECORD_PREVIEW_BACKEND` is complete. Added a backend-only read-only Test Record preview endpoint derived strictly from active ConfirmedMatrix authority, including deterministic group/row/token ordering, `ready|empty` preview status, and typed `404`/`422` behavior.
- Deliverables: `backend/application/confirmed_matrix_test_record_preview_service.py`, `backend/api/routes_confirmed_matrix_test_record_preview.py`, wiring updates in `backend/api/dependencies.py` and `backend/api/main.py`, plus tests `tests/unit/test_confirmed_matrix_test_record_preview_service.py` and `tests/integration/test_confirmed_matrix_test_record_preview_api.py`.
- Validation: `py -m pytest tests\\unit\\test_confirmed_matrix_test_record_preview_service.py -q` passed (`5 passed`); `py -m pytest tests\\integration\\test_confirmed_matrix_test_record_preview_api.py -q` passed (`3 passed`); `py -m pytest tests\\unit\\test_confirmed_matrix_runtime_projection_service.py tests\\integration\\test_confirmed_matrix_runtime_projection_api.py -q` passed (`6 passed`); `py -m pytest tests\\unit\\test_matrix_import_commit_service.py tests\\unit\\test_project_matrix_draft_persistence_service.py -q` passed (`13 passed`); `py -m pytest tests\\integration\\test_matrix_import_group_selection_commit_api.py tests\\integration\\test_project_test_plan_preview_api.py -q` passed (`8 passed`).
- `TASK_264_MATRIX_TO_TEST_RECORD_SMOKE_UI` is complete. Added a frontend-only read-only smoke panel in Project Workbench that consumes TASK_263 API and displays confirmed Test Record preview groups, sample quantity expression, step count, and compact step rows with explicit loading/ready/empty/not-ready/error states.
- Deliverables: `docs/completed_plans/2026/task_264_matrix_to_test_record_smoke_ui_plan.md`, `tasks/completed/2026/TASK_264_MATRIX_TO_TEST_RECORD_SMOKE_UI.md`, `frontend/src/api/client.ts`, `frontend/src/features/project-workbench/TestRecordPreviewSmokePanel.tsx`, `frontend/src/features/project-workbench/TestRecordPreviewSmokePanel.test.tsx`, `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `py -m pytest tests\\unit\\test_frontend_shell_files.py -q -k "task264 or test_record_preview or project_workbench"` passed (`2 passed`); `cd frontend; npm test -- --run TestRecordPreviewSmokePanel` passed (`3 passed`); `cd frontend; npm run build` passed; `py -m pytest tests\\integration\\test_confirmed_matrix_test_record_preview_api.py -q` passed (`3 passed`).
- `TASK_265_END_TO_END_SMOKE_VALIDATION_AND_BOARD_SYNC` is complete. Added one validation-only end-to-end smoke test for Matrix import commit -> SourceMatrix lineage -> selected-only ProjectMatrixDraft -> ConfirmedMatrix -> Test Record preview, and synchronized board/task status after passing validation.
- Deliverables: `tests/integration/test_matrix_to_test_record_smoke_flow_api.py`, `tasks/completed/2026/TASK_265_END_TO_END_SMOKE_VALIDATION_AND_BOARD_SYNC.md`, `docs/completed_plans/2026/task_265_end_to_end_smoke_validation_and_board_sync_plan.md`, and `docs/task_board.md`.
- Validation: `py -m pytest tests\\integration\\test_matrix_to_test_record_smoke_flow_api.py -q` passed (`1 passed`); `py -m pytest tests\\integration\\test_confirmed_matrix_test_record_preview_api.py -q` passed (`3 passed`); `py -m pytest tests\\integration\\test_matrix_import_group_selection_commit_api.py tests\\unit\\test_confirmed_matrix_test_record_preview_service.py -q` passed (`7 passed`); `cd frontend; npm test -- --run TestRecordPreviewSmokePanel` passed (`3 passed`); `cd frontend; npm run build` passed.
- Scope boundary held: no fee/report/equipment/StepInstance/execution persistence scope was introduced.
- `TASK_266_MATRIX_WORKSPACE_NAVIGATION_AND_STATE_CLARITY` is complete. Matrix Workspace now shows explicit Draft / Active Authority / Revision Draft state, separates Draft Actions from Authority Actions, and adds consequence copy for key operations while preserving TASK_261-TASK_265 smoke-flow behavior.
- Deliverables: `frontend/src/api/client.ts`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx`, `frontend/src/features/matrix-editor/MatrixWorkspaceStateBanner.tsx`, `frontend/src/features/matrix-editor/matrixWorkspaceClarityModel.ts`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`, `frontend/src/workbench.css`, `tests/unit/test_frontend_shell_files.py`, `tasks/completed/2026/TASK_266_MATRIX_WORKSPACE_NAVIGATION_AND_STATE_CLARITY.md`, and `docs/completed_plans/2026/task_266_matrix_workspace_navigation_and_state_clarity_plan.md`.
- Validation: `py -m pytest tests\\unit\\test_frontend_shell_files.py -q -k "task266 or matrix_editor"` passed (`35 passed, 72 deselected`); `cd frontend; npm test -- --run MatrixEditorWorkspace` passed (`9 passed`); `cd frontend; npm run build` passed; `py -m pytest tests\\integration\\test_matrix_to_test_record_smoke_flow_api.py -q` passed (`1 passed`).
- Scope boundary held: no backend authority refactor, API/schema change, permission system, LLCR runtime persistence, report engine, AI recommendation, Test Record Word generation, StepInstance, or multi-matrix merge implementation was introduced.
- `TASK_267_PERSISTENT_MATRIX_IMPORT_SESSION_UX` is complete. Matrix Workspace now keeps a frontend-only live import session so operators can go back to matrix candidate preview, return to selection mode from draft actions, or cancel import session explicitly without backend session changes.
- Deliverables: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `frontend/src/features/matrix-editor/MatrixImportSelectionMode.tsx`, `frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`, `frontend/src/features/matrix-editor/matrixImportSessionModel.ts`, `frontend/src/workbench.css`, `tests/unit/test_frontend_shell_files.py`, `tasks/completed/2026/TASK_267_PERSISTENT_MATRIX_IMPORT_SESSION_UX.md`, and `docs/completed_plans/2026/task_267_persistent_matrix_import_session_ux_plan.md`.
- Validation: `py -m pytest tests\\unit\\test_frontend_shell_files.py -q -k "task267 or task266 or matrix_editor"` passed (`36 passed, 72 deselected`); `cd frontend; npm test -- --run MatrixEditorWorkspace` passed (`12 passed`); `cd frontend; npm run build` passed; `py -m pytest tests\\integration\\test_matrix_to_test_record_smoke_flow_api.py -q` passed (`1 passed`).
- Scope boundary held: frontend in-memory import-session UX only; no backend import-session API, no schema/API change, no reload recovery, no multi-matrix merge, no StepInstance/LLCR/report/AI/permission/Test Record generation scope introduced.

- `DOCS_001_MARKDOWN_INFORMATION_ARCHITECTURE_AND_AUTO_ARCHIVE_RULES` is complete. Added Markdown information architecture rules, task/plan archive indexes, a `tasks/` navigation guide, and a dry-run-first archive helper for completed task and plan files.
- Deliverables: `tasks/DOCS_001_MARKDOWN_INFORMATION_ARCHITECTURE_AND_AUTO_ARCHIVE_RULES.md`, `docs/docs_001_markdown_information_architecture_and_auto_archive_rules_plan.md`, `docs/markdown_management_rules.md`, `docs/task_archive_index.md`, `docs/plan_archive_index.md`, `tasks/README.md`, `scripts/archive_completed_markdown.py`, `tests/unit/test_markdown_archive_tool.py`, plus updates to `docs/README.md` and `docs/task_plan_index.md`.
- Validation: `py -m pytest tests\\unit\\test_markdown_archive_tool.py -q` passed; `py scripts\\archive_completed_markdown.py --all-completed --dry-run` now reports `Tasks: 0` and `Moves: 0`; `git diff --check` passed with existing CRLF warnings only. After user approval for actual Markdown management, all root-level task files and plan files verifiably marked complete were archived and recorded in `docs/task_archive_index.md` and `docs/plan_archive_index.md`.
- Scope boundary held: no backend/frontend/API/database/Matrix/Test Record behavior was changed; `TASK_268` was later created and completed as the Group Selection Completeness Guard task.

- `TASK_252CH_MATRIX_EDITOR_NOTE_LINK_RESTORE_AND_SCOPE_LOCK` is complete. Recovery restored marker-aware `.docx` Matrix preview payload fields (`raw_token`, `suffix_note`, `source_note`, `source_note_origin`, `source_item_section_note`, group sample expression/note) and reconnected preview parsing to paragraph note extraction. Matrix Editor group-cell token validation now accepts marker-bearing tokens (e.g., `3(a)`, `6#`, `10*`) while keeping sequence continuity guards. Step preview now includes separated `Step Notes`, `Item/Section Notes`, and `Samples`/`Samples Notes` cards with inline editable samples input.
- Deliverables: `tasks/completed/2026/TASK_252CH_MATRIX_EDITOR_NOTE_LINK_RESTORE_AND_SCOPE_LOCK.md`, `docs/completed_plans/2026/task_252ch_matrix_editor_note_link_restore_and_scope_lock_plan.md`, `backend/modules/test_plan/product_spec_matrix_parser.py`, `backend/application/project_test_plan_matrix_preview_service.py`, `backend/api/routes_project_test_plan.py`, `frontend/src/api/client.ts`, `frontend/src/features/project-workbench/projectWorkbenchMatrixHelpers.ts`, and `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`.
- Validation: `py -m pytest tests\\unit\\test_product_spec_matrix_parser.py tests\\integration\\test_project_test_plan_preview_api.py -q` passed (`7 passed`); `cd frontend; npm run build` passed; `py -m pytest tests\\unit\\test_frontend_shell_files.py -q -k "matrix_editor or task252"` passed (`25 passed`, `69 deselected`).

- `TASK_252CJ_MATRIX_EDITOR_NOTE_MARKER_VARIANT_EXTRACTION_HARDENING` is complete. Matrix note extraction now supports additional deterministic marker-prefix variants (`a)`, `A)`, `（a）`, `a.`, `Note (a):`) while preserving existing `(a)`, `*`, `#` support and exact step/sample marker linkage. Note body text is preserved for document-number/path-like content (for example Windows path strings ending with `.doc`).
- Deliverables: `tasks/completed/2026/TASK_252CJ_MATRIX_EDITOR_NOTE_MARKER_VARIANT_EXTRACTION_HARDENING.md`, `docs/completed_plans/2026/task_252cj_matrix_editor_note_marker_variant_extraction_hardening_plan.md`, `backend/modules/test_plan/product_spec_matrix_parser.py`, `tests/unit/test_product_spec_matrix_parser.py`, and `tests/integration/test_project_test_plan_preview_api.py`.
- Validation: `py -m pytest tests\\unit\\test_product_spec_matrix_parser.py tests\\integration\\test_project_test_plan_preview_api.py -q` passed (`10 passed`). Frontend note-scope safety command `py -m pytest tests\\unit\\test_frontend_shell_files.py -q -k "matrix_editor and notes"` returned `94 deselected` with exit code `1` (no matched tests under current filter), no runtime assertion failure reported.

- `TASK_252CK_MATRIX_EDITOR_STEP_NOTES_PAYLOAD_WIRING_AND_CONCISE_ITEM_SECTION` is complete. Matrix Editor Step preview notes now consume import preview payload note fields (`source_note`, `source_item_section_note`, `sample_note`) with marker-aware fallback to local tokens when payload is unavailable. `Item/Section Notes` lines are now concise and default to `Step N | Section:...` format with redundant `Test Item` fragment removed.
- Deliverables: `tasks/completed/2026/TASK_252CK_MATRIX_EDITOR_STEP_NOTES_PAYLOAD_WIRING_AND_CONCISE_ITEM_SECTION.md`, `docs/completed_plans/2026/task_252ck_matrix_editor_step_notes_payload_wiring_and_concise_item_section_plan.md`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `py -m pytest tests\\unit\\test_frontend_shell_files.py -q -k "task252ck or matrix_editor"` passed (`26 passed`, `69 deselected`); `cd frontend; npm run build` passed.

- `TASK_252CL_MATRIX_EDITOR_STEP_NOTES_PREFIX_COVERAGE_AND_CARD_VISUAL_RESTORE` is complete. Step Notes now render token-prefixed lines (for example `3(a) ...`) while removing duplicated leading marker from note body; note rows are deduped for repeated step rows. Parser marker extraction now recognizes digit-prefixed parenthesis markers such as `(5e)` so sample expressions like `5+(5e)` can map to `(e)` notes. Matrix Editor note areas now restore independent card visuals with separated warm/cool/neutral backgrounds for Step Notes, Item/Section Notes, and Samples.
- Deliverables: `tasks/completed/2026/TASK_252CL_MATRIX_EDITOR_STEP_NOTES_PREFIX_COVERAGE_AND_CARD_VISUAL_RESTORE.md`, `docs/completed_plans/2026/task_252cl_matrix_editor_step_notes_prefix_coverage_and_card_visual_restore_plan.md`, `backend/modules/test_plan/product_spec_matrix_parser.py`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `frontend/src/workbench.css`, `tests/unit/test_product_spec_matrix_parser.py`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `py -m pytest tests\\unit\\test_product_spec_matrix_parser.py tests\\integration\\test_project_test_plan_preview_api.py -q` passed (`11 passed`); `py -m pytest tests\\unit\\test_frontend_shell_files.py -q -k "task252cl or matrix_editor"` passed (`27 passed`, `69 deselected`); `cd frontend; npm run build` passed.

- `TASK_252CM_MATRIX_EDITOR_NOTE_BLOCK_SCOPED_EXTRACTION_AND_MAPPING_FIX` is complete. Marker-note extraction now prefers the last contiguous marker-note block (matrix-adjacent footer note region) instead of unconstrained paragraph-wide capture, preventing early unrelated marker-like lines from overriding true `(a)..(e)` matrix notes. A sparse-document fallback keeps single-line marker-note extraction behavior unchanged when no contiguous block is found. The parser also recovers A2-style Word list notes when `python-docx` drops `(a)..(d)` labels and only leaves the final explicit `(e)` marker, backfilling labels from the matrix table caption context.
- Deliverables: `tasks/completed/2026/TASK_252CM_MATRIX_EDITOR_NOTE_BLOCK_SCOPED_EXTRACTION_AND_MAPPING_FIX.md`, `docs/completed_plans/2026/task_252cm_matrix_editor_note_block_scoped_extraction_and_mapping_fix_plan.md`, `backend/modules/test_plan/product_spec_matrix_parser.py`, `tests/unit/test_product_spec_matrix_parser.py`, and `tests/integration/test_project_test_plan_preview_api.py`.
- Validation: `py -m pytest tests\\unit\\test_product_spec_matrix_parser.py tests\\integration\\test_project_test_plan_preview_api.py -q` passed (`14 passed`); `py -m pytest tests\\unit\\test_frontend_shell_files.py -q -k "task252cl or matrix_editor"` passed (`27 passed`, `69 deselected`); `cd frontend; npm run build` passed.

- `TASK_252CN_MATRIX_EDITOR_SECTION_SYMBOL_NOTE_EXTRACTION_RESTORE` is complete. Parser note extraction now merges standalone line-start symbol notes (`*`, `#`) into the selected marker-note map without reopening global letter-marker matching, restoring section-note text for rows such as `6.5*` and `6.6*` in `GS-12-1507 RA Coplanar Rev7 (3).docx`. Matrix Editor also reuses imported symbol item/section note bodies for locally edited section-marker rows and no longer duplicates the marker in fallback text (`Section:6.5**`).
- Deliverables: `tasks/completed/2026/TASK_252CN_MATRIX_EDITOR_SECTION_SYMBOL_NOTE_EXTRACTION_RESTORE.md`, `docs/completed_plans/2026/task_252cn_matrix_editor_section_symbol_note_extraction_restore_plan.md`, `backend/modules/test_plan/product_spec_matrix_parser.py`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `tests/unit/test_product_spec_matrix_parser.py`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `py -m pytest tests\\unit\\test_product_spec_matrix_parser.py tests\\integration\\test_project_test_plan_preview_api.py -q` passed (`15 passed`); `py -m pytest tests\\unit\\test_frontend_shell_files.py -q -k "task252cn or matrix_editor"` passed (`28 passed`, `69 deselected`); `cd frontend; npm run build` passed.

- `TASK_252CO_MATRIX_EDITOR_SAMPLES_INLINE_AND_NOTES_LABEL_MINIFY` is complete. In Matrix Editor Step preview, `Samples` label and samples input now remain on one inline row, and sample note heading text is simplified from `Samples Notes` to `Notes` while keeping note content unchanged.
- Deliverables: `tasks/completed/2026/TASK_252CO_MATRIX_EDITOR_SAMPLES_INLINE_AND_NOTES_LABEL_MINIFY.md`, `docs/completed_plans/2026/task_252co_matrix_editor_samples_inline_and_notes_label_minify_plan.md`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `py -m pytest tests\\unit\\test_frontend_shell_files.py -q -k "task252co or matrix_editor"` passed (`29 passed`, `69 deselected`); `cd frontend; npm run build` passed.

- `TASK_252CP_MATRIX_EDITOR_SAMPLES_ROW_VERTICAL_ALIGN_AND_TOKEN_WRAP` is complete. Matrix Editor main-grid sample row now vertically centers the `Samples Quantity (PCS)` label cell and uses an auto-grow textarea for per-group sample expressions so narrow cells can wrap tokens like `5+(5e)` instead of clipping.
- Deliverables: `tasks/completed/2026/TASK_252CP_MATRIX_EDITOR_SAMPLES_ROW_VERTICAL_ALIGN_AND_TOKEN_WRAP.md`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `py -m pytest tests\\unit\\test_frontend_shell_files.py -q -k "task252cp or matrix_editor"` passed (`30 passed`, `69 deselected`); `cd frontend; npm run build` passed.

- `TASK_252CQ_MATRIX_EDITOR_IDENTICAL_SAMPLE_ROWS_MERGE_NOTE` is complete. Matrix Editor import mapping now detects identical multi-row sample quantities (for example `Header / Rec. / Rec+ Cable`) and displays one merged sample value per group while adding a right-side Samples `Notes` line that names the merged source rows. Existing marker sample notes remain visible, and manual sample edits clear stale merge-source notes.
- Deliverables: `tasks/completed/2026/TASK_252CQ_MATRIX_EDITOR_IDENTICAL_SAMPLE_ROWS_MERGE_NOTE.md`, `docs/completed_plans/2026/task_252cq_matrix_editor_identical_sample_rows_merge_note_plan.md`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `py -m pytest tests\\unit\\test_frontend_shell_files.py -q -k "task252cq or matrix_editor"` passed (`31 passed`, `69 deselected`); `cd frontend; npm run build` passed.

- `TASK_252CR_MATRIX_IMPORT_PREVIEW_LAYOUT_AND_CONTROL_STYLE_REFINEMENT` is complete. Import dialog header now keeps `Import Matrix` and source filename on one line, locator controls place `Page` and `Table on page` in a two-column row, and `Reparse` button style is unified with commit action button dimensions/typography and primary palette. PDF preview URL now opens with `#page=<n>&zoom=page-width&pagemode=thumbs` so preview defaults to matrix page and fit-width mode (viewer support dependent).
- Deliverables: `tasks/completed/2026/TASK_252CR_MATRIX_IMPORT_PREVIEW_LAYOUT_AND_CONTROL_STYLE_REFINEMENT.md`, `docs/completed_plans/2026/task_252cr_matrix_import_preview_layout_and_control_style_refinement_plan.md`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `py -m pytest tests\\unit\\test_frontend_shell_files.py -q -k "matrix_editor or task252"` passed (`32 passed`, `69 deselected`); `cd frontend; npm run build` passed.

- `TASK_252CS_MATRIX_EDITOR_STEP_PREVIEW_HEADER_AND_SAMPLES_CARD_VISUAL_REFINEMENT` is complete. Step workspace header now renders as `Group <n>: <n> steps` in unified typography and removes redundant `Step preview` and `Selected group` labels. Samples card now uses a distinct visual tint from other note cards (`#eef9f4` with `#bfe1d1` border) per operator request.
- Deliverables: `tasks/completed/2026/TASK_252CS_MATRIX_EDITOR_STEP_PREVIEW_HEADER_AND_SAMPLES_CARD_VISUAL_REFINEMENT.md`, `docs/completed_plans/2026/task_252cs_matrix_editor_step_preview_header_and_samples_card_visual_refinement_plan.md`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `py -m pytest tests\\unit\\test_frontend_shell_files.py -q -k "matrix_editor or task252"` passed (`33 passed`, `69 deselected`); `cd frontend; npm run build` passed.

- `TASK_253_MATRIX_PERSISTENCE_DOMAIN_MODEL_DESIGN` is complete. Matrix persistence domain design now defines Source Matrix, Project Matrix Draft, Confirmed Matrix authority, Matrix Version, Group Selection Projection, Source Metadata, and Matrix Revision Flow boundaries before implementation.
- Deliverables: `tasks/completed/2026/TASK_253_MATRIX_PERSISTENCE_DOMAIN_MODEL_DESIGN.md` and `docs/archive/task_artifacts/2026/task_253_matrix_persistence_domain_model_design.md`.
- Validation: design-only review completed. No database schema, API route, repository, backend implementation, or frontend implementation was introduced.

- `TASK_254_SOURCE_MATRIX_IMPORT_PERSISTENCE_MODEL` is complete. Source Matrix import persistence now stores immutable import metadata + snapshot body (rows/groups/sparse non-empty cells) at draft import commit boundary while keeping matrix preview API behavior unchanged and preserving existing `ProjectTestPlanDraft` semantics.
- Deliverables: `tasks/completed/2026/TASK_254_SOURCE_MATRIX_IMPORT_PERSISTENCE_MODEL.md`, `docs/completed_plans/2026/task_254_source_matrix_import_persistence_model_plan.md`, `backend/application/source_matrix_import_persistence_service.py`, `backend/infrastructure/storage/models_matrix_source.py`, `backend/infrastructure/storage/repositories/source_matrix_import.py`, and dependency wiring in draft persistence path.
- Validation: `py -m pytest tests\unit\test_source_matrix_persistence_service.py tests\unit\test_source_matrix_import_repository_atomicity.py -q` passed (`3 passed`); `py -m pytest tests\integration\test_project_test_plan_source_matrix_import_persistence_api.py tests\integration\test_project_test_plan_preview_api.py -q` passed (`7 passed`); `py -m pytest tests\unit\test_project_test_plan_draft_service.py tests\integration\test_project_test_plan_draft_api.py -q` passed (`7 passed`); `cd frontend; npm run build` passed.
- `TASK_255_PROJECT_MATRIX_DRAFT_PERSISTENCE_MODEL` is complete. Structured Project Matrix draft persistence now supports creating one editable working-copy draft from immutable Source Matrix lineage with draft root/group/row/cell storage, draft-local selected-group state defaults, group-level sample quantity initialization, sparse non-empty draft cell persistence, duplicate `project_id + source_import_id` conflict guarding, and API-to-application-only routing.
- Deliverables: `tasks/completed/2026/TASK_255_PROJECT_MATRIX_DRAFT_PERSISTENCE_MODEL.md`, `docs/completed_plans/2026/task_255_project_matrix_draft_persistence_model_plan.md`, `backend/domain/project_matrix_draft_models.py`, `backend/infrastructure/storage/models_project_matrix_draft.py`, `backend/infrastructure/storage/repositories/project_matrix_draft.py`, `backend/application/project_matrix_draft_persistence_service.py`, `backend/api/routes_project_matrix_drafts.py`, and related dependency/router wiring.
- Validation: `py -m pytest tests\unit\test_project_matrix_draft_persistence_service.py tests\unit\test_project_matrix_draft_repository.py -q` passed (`9 passed`); `py -m pytest tests\integration\test_project_matrix_draft_from_source_matrix_api.py tests\unit\test_source_matrix_persistence_service.py -q` passed (`3 passed`); `py -m pytest tests\integration\test_project_test_plan_draft_api.py tests\integration\test_project_test_plan_preview_api.py tests\integration\test_api_default_dependencies.py -q` passed (`8 passed`); `cd frontend; npm run build` passed.
- Residual risk record: under concurrent duplicate-create requests, DB unique constraints can still raise `IntegrityError` after service-level precheck. Current single-machine offline scope accepts this behavior. When multi-user/LAN scope is activated, add DB-level conflict mapping to application-level conflict semantics.
- `TASK_256_MATRIX_EDITOR_SAVE_TO_DRAFT_WIRING` is complete. Matrix Editor now loads persisted Project Matrix Draft target data when available and wires `Save` to typed Project Matrix Draft update API with draft-only semantics.
- Deliverables: `tasks/completed/2026/TASK_256_MATRIX_EDITOR_SAVE_TO_DRAFT_WIRING.md`, `docs/completed_plans/2026/task_256_matrix_editor_save_to_draft_wiring_plan.md`, `backend/application/project_matrix_draft_persistence_service.py`, `backend/infrastructure/storage/repositories/project_matrix_draft.py`, `backend/api/routes_project_matrix_drafts.py`, `frontend/src/api/client.ts`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `frontend/src/workbench.css`, `tests/unit/test_project_matrix_draft_persistence_service.py`, `tests/unit/test_project_matrix_draft_repository.py`, `tests/integration/test_project_matrix_draft_save_api.py`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `py -m pytest tests\unit\test_project_matrix_draft_persistence_service.py tests\unit\test_project_matrix_draft_repository.py -q` passed (`13 passed`); `py -m pytest tests\integration\test_project_matrix_draft_save_api.py tests\integration\test_project_matrix_draft_from_source_matrix_api.py -q` passed (`2 passed`); `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor or task256"` passed (`33 passed`, `70 deselected`); `py -m pytest tests\integration\test_api_default_dependencies.py -q` passed (`1 passed`); `cd frontend; npm run build` passed.
- Residual risk record: update operation is last-write-wins in this task scope; optimistic version/timestamp conflict control remains out of scope for TASK_256.
- `TASK_257_CONFIRMED_MATRIX_AUTHORITY_MODEL` is complete. Backend now supports confirming one saved Project Matrix Draft into immutable active Confirmed Matrix authority with controlled boundaries.
- Deliverables: `backend/domain/confirmed_matrix_authority_models.py`, `backend/application/confirmed_matrix_authority_service.py`, `backend/infrastructure/storage/models_confirmed_matrix_authority.py`, `backend/infrastructure/storage/repositories/confirmed_matrix_authority.py`, `backend/api/routes_project_matrix_drafts.py`, dependency wiring updates, and new tests `tests/unit/test_confirmed_matrix_authority_service.py`, `tests/unit/test_confirmed_matrix_authority_repository.py`, `tests/integration/test_confirmed_matrix_authority_api.py`.
- Validation: `py -m pytest tests/unit/test_confirmed_matrix_authority_service.py tests/unit/test_confirmed_matrix_authority_repository.py -q` passed (`11 passed`); `py -m pytest tests/integration/test_confirmed_matrix_authority_api.py tests/integration/test_project_matrix_draft_save_api.py -q` passed (`4 passed`); `py -m pytest tests/integration/test_api_default_dependencies.py -q` passed (`1 passed`).
- `TASK_258_MATRIX_REVISION_FLOW` is complete. Backend now supports creating revision drafts from active confirmed authority and confirming those drafts into new active confirmed revisions with atomic supersession of the previous active version.
- Deliverables: `backend/application/matrix_revision_flow_service.py`, `backend/api/routes_matrix_revisions.py`, updates to `backend/api/routes_project_matrix_drafts.py`, `backend/infrastructure/storage/models_project_matrix_draft.py`, `backend/infrastructure/storage/models_confirmed_matrix_authority.py`, `backend/infrastructure/storage/repositories/project_matrix_draft.py`, `backend/infrastructure/storage/repositories/confirmed_matrix_authority.py`, migration updates in `backend/infrastructure/storage/database.py`, and related domain/dependency/router wiring.
- Validation: `py -m pytest tests/unit/test_matrix_revision_flow_service.py tests/unit/test_confirmed_matrix_authority_repository.py tests/unit/test_project_matrix_draft_repository.py -q` passed (`19 passed`); `py -m pytest tests/integration/test_matrix_revision_flow_api.py tests/integration/test_confirmed_matrix_authority_api.py -q` passed (`5 passed`); `py -m pytest tests/integration/test_api_default_dependencies.py -q` passed (`1 passed`).
- `TASK_259_MATRIX_EDITOR_REVISION_ACTIONS_WIRING` is complete. Matrix Editor now wires frontend revision actions for creating revision drafts from active confirmed authority and confirming revision drafts through TASK_258 APIs while preserving existing draft Save behavior.
- Deliverables: `tasks/completed/2026/TASK_259_MATRIX_EDITOR_REVISION_ACTIONS_WIRING.md`, `docs/completed_plans/2026/task_259_matrix_editor_revision_actions_wiring_plan.md`, `frontend/src/api/client.ts`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`, `frontend/vite.config.ts`, `frontend/package.json`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor or task259 or task256"` passed (`34 passed`, `70 deselected`); `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task259"` passed (`1 passed`, `103 deselected`); `cd frontend; npm test -- --run MatrixEditorWorkspace` passed (`2 passed`); `cd frontend; npm run build` passed.
- `TASK_260_CONFIRMED_MATRIX_RUNTIME_PROJECTION_CONSUMER` is complete. Backend now exposes a confirmed-authority runtime projection consumer endpoint that maps active Confirmed Matrix sparse cells into existing runtime projection snapshots without changing the existing read-only snapshot API contract.
- Deliverables: `tasks/completed/2026/TASK_260_CONFIRMED_MATRIX_RUNTIME_PROJECTION_CONSUMER.md`, `docs/completed_plans/2026/task_260_confirmed_matrix_runtime_projection_consumer_plan.md`, `backend/application/confirmed_matrix_runtime_projection_service.py`, `backend/api/routes_confirmed_matrix_runtime_projection.py`, `backend/api/runtime_projection_response_mapper.py`, updates in `backend/api/routes_runtime_projection_read_only.py`, `backend/api/dependencies.py`, `backend/api/main.py`, plus tests `tests/unit/test_confirmed_matrix_runtime_projection_service.py` and `tests/integration/test_confirmed_matrix_runtime_projection_api.py`.
- Validation: `py -m pytest tests/unit/test_confirmed_matrix_runtime_projection_service.py tests/unit/test_runtime_projection_read_only_api_mapping.py tests/unit/test_runtime_projection_read_only_api_contract.py -q` passed (`8 passed`); `py -m pytest tests/integration/test_confirmed_matrix_runtime_projection_api.py tests/integration/test_runtime_projection_read_only_api.py -q` passed (`4 passed`); `py -m pytest tests/integration/test_api_default_dependencies.py -q` passed (`1 passed`).
- `TASK_261_MATRIX_IMPORT_GROUP_SELECTION_COMMIT` is complete. Matrix import commit API now persists full Source Matrix lineage while creating a selected-only ProjectMatrixDraft, with deterministic idempotent reuse (`commit_status=created|reused`) based on persisted `task261_commit_fingerprint`.
- Deliverables: `tasks/completed/2026/TASK_261_MATRIX_IMPORT_GROUP_SELECTION_COMMIT.md`, `docs/completed_plans/2026/task_261_matrix_import_group_selection_commit_plan.md`, `backend/application/matrix_import_commit_service.py`, `backend/api/routes_matrix_import_commit.py`, updates in `backend/application/source_matrix_import_persistence_service.py`, `backend/infrastructure/storage/models_matrix_source.py`, `backend/infrastructure/storage/repositories/source_matrix_import.py`, `backend/infrastructure/storage/database.py`, `backend/api/dependencies.py`, `backend/api/main.py`, plus tests `tests/unit/test_matrix_import_commit_service.py` and `tests/integration/test_matrix_import_group_selection_commit_api.py`.
- Validation: `py -m pytest tests/unit/test_matrix_import_commit_service.py -q` passed (`3 passed`); `py -m pytest tests/integration/test_matrix_import_group_selection_commit_api.py tests/integration/test_project_test_plan_preview_api.py -q` passed (`7 passed`); `py -m pytest tests/unit/test_source_matrix_persistence_service.py tests/unit/test_project_matrix_draft_persistence_service.py -q` passed (`12 passed`).
- Numbering alignment note: earlier persistence design documentation used `TASK_259_SELECTED_GROUPS_PROJECTION_CONSUMER` as a suggested follow-up label; this was later renumbered and respecified as `TASK_260_CONFIRMED_MATRIX_RUNTIME_PROJECTION_CONSUMER` to avoid collision with completed `TASK_259` and to align with the confirmed-authority consumer direction.

- `TASK_252C_MATRIX_IMPORT_DOCUMENT_PAGE_PREVIEW_AND_CONFIRMATION` flow is restored in current Matrix Editor: file-picker import now opens a large confirmation modal with left PDF preview (`.docx` converted via Word COM) and right-side locator fields (`Page`, `Table on page`, `Keyword in table`) that trigger debounce reparse. Footer actions support `Cancel`, `Replace`, and `Append`.
- Added endpoints: `POST /api/test-plan/matrix-preview-from-upload` now accepts optional locator form fields; `GET /api/test-plan/matrix-preview-pdf/{token}` serves generated preview PDF under controlled temp directory.

- `TASK_248_REVERT_MATRIX_EDITOR_GROUP_NAME_WRAP` is complete. Matrix Editor group name input now restores single-line clipping with `white-space: nowrap`, `overflow: hidden`, and `text-overflow: ellipsis`, while preserving TASK_246 fixed 44px group column width. No backend/API/domain/persistence behavior was changed.
- Deliverables: `tasks/completed/2026/TASK_248_REVERT_MATRIX_EDITOR_GROUP_NAME_WRAP.md`, `docs/completed_plans/2026/task_248_revert_matrix_editor_group_name_wrap_plan.md`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task248 or matrix_editor"` (`25 passed`, `69 deselected`).
- Next recommended action: open a controlled Matrix Editor import task only after task file and plan review.

- `TASK_249_MATRIX_EDITOR_SEED_AND_HEADER_SIMPLIFICATION` is complete. Matrix Editor edit area now removes the top grid toolbar (`Matrix Version / Group / Filter / Section`) and removes the selection hint strip (`Selection: none` and structural-fixed reminder copy). Initial group display name is now `1` instead of `G1`. No backend/API/domain/persistence behavior was changed.
- Deliverables: `docs/completed_plans/2026/task_249_matrix_editor_seed_and_header_simplification_plan.md`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task249 or task244 or task243 or task224 or matrix_editor"` (`25 passed`, `69 deselected`).
- Next recommended action: wait for user approval before opening the next controlled Matrix Editor task.

- `TASK_219F_PROJECT_WORKBENCH_LEGACY_SUPPORT_REMOVAL_AND_RUNTIME_CONSOLE_RESPONSIBILITY_REFINEMENT` is complete. The Workbench Runtime Console now removes the remaining lower historical-process surfaces: always-visible Derived outputs board, Runtime Support / Project setup status board, Other materials intake panel, material placement counters, routine Approval Package/Fee Evaluation readiness entries, and Setup Manager entry. The implementation preserves Matrix authority/projection sync, runtime execution map, selected Step context, runtime attention, and Matrix Editor navigation. Backend APIs, output records, reusable legacy components, and support hooks were not deleted.
- Deliverables: `tasks/completed/2026/TASK_219F_PROJECT_WORKBENCH_LEGACY_SUPPORT_REMOVAL.md`, `docs/completed_plans/2026/task_219f_runtime_console_responsibility_refinement_plan.md`, `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`, `frontend/src/pages/ProjectWorkbenchPage.tsx`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. TASK_219F-related static checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task219 or task188 or task190 or task187 or project_lookup or task100 or task150"` (`9 passed`, `59 deselected`). Full `tests\unit\test_frontend_shell_files.py -q` reports `64 passed`, `4 failed`; remaining failures are existing Intake/Precheck static assertion drift outside TASK_219F scope.
- Next recommended action: wait for user approval before opening the next controlled runtime-console or Step Workspace task.

- `TASK_220_PROJECT_WORKBENCH_TARGET_UI_ALIGNMENT` is complete. Workbench runtime console layout and wording were aligned to the approved target UI structure without backend/API/domain changes. The update keeps Runtime Console boundaries and preserves TASK_219F legacy-support removals.
- Deliverables: `tasks/completed/2026/TASK_220_PROJECT_WORKBENCH_TARGET_UI_ALIGNMENT.md`, `docs/completed_plans/2026/task_220_project_workbench_target_ui_alignment_plan.md`, `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task220 or task219 or task188 or task190"` (`6 passed`, `63 deselected`).
- Next recommended action: wait for user approval before opening the next controlled runtime-console refinement task.

- `TASK_221_MATRIX_EDITOR_TARGET_UI_ALIGNMENT_AND_WORKFLOW_CONVERGENCE` is complete. Matrix Editor placeholder UI was converged to Definition Studio workflow structure aligned to the approved target page. The implementation restores Matrix Grid visual dominance, introduces left Test Library and bottom supporting libraries, and replaces dashboard-like right status-card stack with contextual Group/Step workspace, without backend/API/domain changes.
- Deliverables: `tasks/completed/2026/TASK_221_MATRIX_EDITOR_TARGET_UI_ALIGNMENT_AND_WORKFLOW_CONVERGENCE.md`, `docs/completed_plans/2026/task_221_matrix_editor_target_ui_alignment_plan.md`, `frontend/src/pages/ProjectMatrixEditorPage.tsx`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task221 or task220 or task219"` (`5 passed`, `65 deselected`).
- Next recommended action: wait for user approval before opening the next controlled Matrix Editor refinement task.

- `TASK_222_MATRIX_EDITOR_TARGET_UI_PIXEL_TUNING_PASS` is complete. Matrix Editor received a pixel-level density and spacing refinement pass to reduce visual drift from the target image while preserving `TASK_221` structure and Definition Studio workflow. No backend/API/domain behavior was changed.
- Deliverables: `tasks/completed/2026/TASK_222_MATRIX_EDITOR_TARGET_UI_PIXEL_TUNING_PASS.md`, `docs/completed_plans/2026/task_222_matrix_editor_target_ui_pixel_tuning_plan.md`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task222 or task221 or task220 or task219"` (`6 passed`, `65 deselected`).
- Next recommended action: wait for user approval before opening the next controlled Matrix Editor refinement task.

- `TASK_223_MATRIX_EDITOR_GRID_LOCAL_FIX` is complete. Matrix Editor table area received a bounded local fix: removed left `#` sequence column, removed duplicate second header row, tightened `Test Item`/`Condition`/`Requirement` widths with wrapping, and added basic inline editing for all data-row text/group cells. No backend/API/domain/workbench behavior was changed.
- Deliverables: `tasks/completed/2026/TASK_223_MATRIX_EDITOR_GRID_LOCAL_FIX.md`, `docs/completed_plans/2026/task_223_matrix_editor_grid_local_fix_plan.md`, `frontend/src/pages/ProjectMatrixEditorPage.tsx`, and `frontend/src/workbench.css`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task223 or task222 or task221"` (`2 passed`, `69 deselected`).
- Next recommended action: wait for user approval before opening the next controlled Matrix Editor refinement task.

- `TASK_224_MATRIX_EDITOR_STRUCTURAL_EDIT_INTERACTION_RULES` is complete. Matrix Editor now includes frontend-only guarded structural editing interactions: row action rail, group header action menu, minimum-structure guard enforcement, protected-structure status messaging, and lightweight local structural undo, while keeping header/fixed-definition region structurally protected. No backend/API/domain/workbench changes were made.
- Deliverables: `tasks/completed/2026/TASK_224_MATRIX_EDITOR_STRUCTURAL_EDIT_INTERACTION_RULES.md`, `docs/completed_plans/2026/task_224_matrix_editor_structural_edit_interaction_rules_plan.md`, `frontend/src/pages/ProjectMatrixEditorPage.tsx`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task224 or task223 or task222 or task221"` (`3 passed`, `69 deselected`).
- Next recommended action: wait for user approval before opening the next controlled Matrix Editor refinement task.

- `TASK_225_MATRIX_EDITOR_CONTEXT_MENU_INTERACTION_DENSITY_FIX` is complete. Matrix Editor structural actions were moved from persistent row/group header controls into right-click context menus to reclaim grid width while preserving guarded row/group operations, minimum-structure protection, inline editing, and structural undo. No backend/API/domain/workbench changes were made.
- Deliverables: `tasks/completed/2026/TASK_225_MATRIX_EDITOR_CONTEXT_MENU_INTERACTION_DENSITY_FIX.md`, `docs/completed_plans/2026/task_225_matrix_editor_context_menu_interaction_density_fix_plan.md`, `frontend/src/pages/ProjectMatrixEditorPage.tsx`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task225 or task224 or task223"` (`2 passed`, `71 deselected`).
- Next recommended action: wait for user review before opening the next controlled Matrix Editor refinement task.

- `TASK_226_MATRIX_EDITOR_ROW_SELECTOR_AND_SELECTION_HIGHLIGHT` is complete. Matrix Editor now has a compact row-number selector column, row click selection with full-row highlight, group header click selection with full-column highlight, and right-click context menus on the selected row/group target surfaces. No backend/API/domain/workbench changes were made.
- Deliverables: `tasks/completed/2026/TASK_226_MATRIX_EDITOR_ROW_SELECTOR_AND_SELECTION_HIGHLIGHT.md`, `docs/completed_plans/2026/task_226_matrix_editor_row_selector_and_selection_highlight_plan.md`, `frontend/src/pages/ProjectMatrixEditorPage.tsx`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task226 or task225 or task224 or task223"` (`3 passed`, `71 deselected`).
- Next recommended action: wait for user review before opening the next controlled Matrix Editor refinement task.

- `TASK_227_MATRIX_EDITOR_EDITABLE_GROUP_HEADER_AND_COLUMN_INDEX` is complete. Matrix Editor group columns now use stable internal IDs with editable header names, plus an A/B/C... index selector row for column selection and right-click structural operations. Newly added group columns start with empty display names for manual business naming. No backend/API/domain/workbench changes were made.
- Deliverables: `tasks/completed/2026/TASK_227_MATRIX_EDITOR_EDITABLE_GROUP_HEADER_AND_COLUMN_INDEX.md`, `docs/completed_plans/2026/task_227_matrix_editor_editable_group_header_and_column_index_plan.md`, `frontend/src/pages/ProjectMatrixEditorPage.tsx`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task227 or task226 or task225"` (`3 passed`, `72 deselected`).
- Next recommended action: wait for user review before opening the next controlled Matrix Editor refinement task.

- `TASK_228_MATRIX_EDITOR_COLUMN_HEADER_DIRECT_CONTEXT_MENU` is complete. Matrix Editor removed the A/B/C index row and now uses group headers directly as the column operation surface: click to select/highlight the column and right-click to open the column context menu, while keeping editable group names. No backend/API/domain/workbench changes were made.
- Deliverables: `tasks/completed/2026/TASK_228_MATRIX_EDITOR_COLUMN_HEADER_DIRECT_CONTEXT_MENU.md`, `docs/completed_plans/2026/task_228_matrix_editor_column_header_direct_context_menu_plan.md`, `frontend/src/pages/ProjectMatrixEditorPage.tsx`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task228 or task227 or task226"` (`3 passed`, `73 deselected`).
- Next recommended action: wait for user review before opening the next controlled Matrix Editor refinement task.

- `TASK_229A_RUNTIME_PROJECTION_API_APPLICATION_SERVICE_ALIGNMENT` is complete. Runtime projection read-only API route now depends on an application-layer service and no longer directly calls projection builder functions from route code. Endpoint path and response contract are unchanged.
- Deliverables: `tasks/completed/2026/TASK_229A_RUNTIME_PROJECTION_API_APPLICATION_SERVICE_ALIGNMENT.md`, `docs/completed_plans/2026/task_229a_runtime_projection_api_application_service_alignment_plan.md`, `backend/application/runtime_projection_read_only_service.py`, and `backend/api/routes_runtime_projection_read_only.py`.
- Validation: `py -m pytest tests\integration\test_runtime_projection_read_only_api.py tests\unit\test_runtime_projection_read_only_api_mapping.py tests\unit\test_runtime_projection_read_only_api_contract.py -q` passed (`6 passed`); `py -m pytest tests\unit\test_runtime_projection_snapshot_adapter.py tests\unit\test_runtime_projection_consumer_views.py tests\unit\test_runtime_projection_token_builder.py tests\unit\test_runtime_projection_composition.py -q` passed (`45 passed`).
- Next recommended action: if approved, open TASK_229B for Matrix Editor page-to-feature decomposition.

- `TASK_229B_MATRIX_EDITOR_PAGE_TO_FEATURE_DECOMPOSITION` is complete. Matrix Editor route page is now a thin wrapper and the full editor implementation has been moved into `features/matrix-editor/MatrixEditorWorkspace.tsx`, reducing route-page controller weight while preserving current interactions and validations.
- Deliverables: `tasks/completed/2026/TASK_229B_MATRIX_EDITOR_PAGE_TO_FEATURE_DECOMPOSITION.md`, `docs/completed_plans/2026/task_229b_matrix_editor_page_to_feature_decomposition_plan.md`, `frontend/src/pages/ProjectMatrixEditorPage.tsx`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor or task229 or task228 or task227"` (`8 passed`, `69 deselected`).
- Next recommended action: open controlled follow-up task to split `MatrixEditorWorkspace` further into config/hook/presentational components (`useMatrixEditorDraftModel`, `MatrixEditorGrid`, `MatrixEditorContextMenu`, `MatrixEditorStepWorkspace`) if deeper decomposition is required.

- `TASK_230_MATRIX_EDITOR_STEP_TOKEN_VALIDATION_GUARDS` is complete. Matrix group step cells now default to blank, enforce digits/comma format, and apply per-group sequence guards (start at 1, continuous, no duplicates) with inline invalid highlights and status-strip error messaging aligned with existing group-name validation patterns.
- Deliverables: `tasks/completed/2026/TASK_230_MATRIX_EDITOR_STEP_TOKEN_VALIDATION_GUARDS.md`, `docs/completed_plans/2026/task_230_matrix_editor_step_token_validation_guards_plan.md`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task230 or matrix_editor or task229"` (`9 passed`, `69 deselected`).
- Next recommended action: collect user feedback on token validation wording and strictness before opening deeper Matrix Editor decomposition or API-bound draft save tasks.

- `TASK_231_MATRIX_EDITOR_STEP_PREVIEW_EDITABLE_REQUIREMENT_DESCRIPTION` is complete. The Matrix Editor right-side Step preview now derives rows from the selected group, sorts by step number, shows Matrix Test Item as read-only, and provides local editable Requirement / Step Description fields defaulting from the Matrix Requirement. No backend/API/domain/persistence/report generation changes were made.
- Deliverables: `tasks/completed/2026/TASK_231_MATRIX_EDITOR_STEP_PREVIEW_EDITABLE_REQUIREMENT_DESCRIPTION.md`, `docs/completed_plans/2026/task_231_matrix_editor_step_preview_editable_requirement_description_plan.md`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task231 or task230 or matrix_editor"` (`10 passed`, `69 deselected`).
- Next recommended action: wait for user review before opening the next controlled Matrix Editor task.

- `TASK_232_MATRIX_EDITOR_STEP_PREVIEW_DESCRIPTION_FROM_TEST_ITEM` is complete. Matrix Editor Step preview now removes the preview `Test Item` column, keeps `Requirement` editable with default from Matrix `Requirement`, and sets `Step Description` editable default from Matrix `Test Item`, while preserving local override behavior and selected-group step sorting. No backend/API/domain/persistence changes were made.
- Deliverables: `tasks/completed/2026/TASK_232_MATRIX_EDITOR_STEP_PREVIEW_DESCRIPTION_FROM_TEST_ITEM.md`, `docs/completed_plans/2026/task_232_matrix_editor_step_preview_description_from_test_item_plan.md`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task232 or task231 or matrix_editor"` (`11 passed`, `69 deselected`).
- Next recommended action: wait for user review before opening the next controlled Matrix Editor task.

- `TASK_233_MATRIX_EDITOR_STEP_DESCRIPTION_SPECIAL_RULES` is complete. Matrix Editor Step preview now includes alias-ready special-family staged defaults for `LLCR`, `IR`, `DWV`, and `mating/un-mating`: single occurrence -> family label, multiple -> first `Initial`, last `Final`, middle `After <previous numeric step Test Item>`, with fallback to family label when the previous-step item is empty. User-edited description overrides still take precedence.
- Deliverables: `tasks/completed/2026/TASK_233_MATRIX_EDITOR_STEP_DESCRIPTION_SPECIAL_RULES.md`, `docs/completed_plans/2026/task_233_matrix_editor_step_description_special_rules_plan.md`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task233 or task232 or task231 or matrix_editor"` (`12 passed`, `69 deselected`).
- Next recommended action: wait for user review before opening the next controlled Matrix Editor task.

- `TASK_234_MATRIX_EDITOR_REQUIREMENT_SPLIT_RULES` is complete. Matrix Editor Step preview now applies deterministic Requirement split defaults for repeated special-family steps when Matrix requirement matches `Initial ...; After ...` pattern: first step uses `Initial` part and remaining steps use stripped follow part, while keeping conservative fallback to original requirement when split confidence is low. Manual Requirement overrides still take precedence.
- Deliverables: `tasks/completed/2026/TASK_234_MATRIX_EDITOR_REQUIREMENT_SPLIT_RULES.md`, `docs/completed_plans/2026/task_234_matrix_editor_requirement_split_rules_plan.md`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task234 or task233 or task232 or matrix_editor"` (`13 passed`, `69 deselected`).
- Next recommended action: wait for user review before opening the next controlled Matrix Editor task.

- `TASK_235_MATRIX_EDITOR_REQUIREMENT_SPLIT_COLON_VARIANT_SUPPORT` is complete. Requirement split parsing now supports colon-heavy multi-clause variants by locating `Initial` and `After` markers and keeping full initial/after blocks. For repeated special-family steps, first step receives the full initial block and remaining steps receive full after-block content without the `After test:` prefix, with conservative fallback when parsing is uncertain.
- Deliverables: `tasks/completed/2026/TASK_235_MATRIX_EDITOR_REQUIREMENT_SPLIT_COLON_VARIANT_SUPPORT.md`, `docs/completed_plans/2026/task_235_matrix_editor_requirement_split_colon_variant_support_plan.md`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task235 or task234 or task233 or matrix_editor"` (`14 passed`, `69 deselected`).
- Next recommended action: wait for user review before opening the next controlled Matrix Editor task.

- `TASK_236_MATRIX_EDITOR_COLUMN_WIDTH_REALIGNMENT_FOR_CONDITION` is complete. Matrix main table width proportions were rebalanced to narrow `Test Item`/`Section`/`Method` and widen `Condition`, including both duplicated main-table width rule blocks to keep behavior consistent across style branches.
- Deliverables: `tasks/completed/2026/TASK_236_MATRIX_EDITOR_COLUMN_WIDTH_REALIGNMENT_FOR_CONDITION.md`, `docs/completed_plans/2026/task_236_matrix_editor_column_width_realignment_for_condition_plan.md`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task236 or task235 or matrix_editor"` (`15 passed`, `69 deselected`).
- Next recommended action: wait for user review before opening the next controlled Matrix Editor task.

- `TASK_237_MATRIX_EDITOR_FIXED_COLUMNS_BG_AND_GROUP_HEADER_DENSITY` is complete. Matrix main table now applies a subtle fixed-zone background treatment to the left 6 columns, and group-header capsule density is tuned with lower input height and larger outer header padding to improve column selection clickability while preserving existing interactions.
- Deliverables: `tasks/completed/2026/TASK_237_MATRIX_EDITOR_FIXED_COLUMNS_BG_AND_GROUP_HEADER_DENSITY.md`, `docs/completed_plans/2026/task_237_matrix_editor_fixed_columns_bg_and_group_header_density_plan.md`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task237 or task236 or matrix_editor"` (`16 passed`, `69 deselected`).
- Next recommended action: wait for user review before opening the next controlled Matrix Editor task.

- `TASK_238_MATRIX_EDITOR_STEP_PREVIEW_DUPLICATE_STEP_NUMBER_FIX` is complete. Step preview derivation now dedupes repeated step-number entries by keeping the first sorted row for each `stepNo`, resolving the smoke-tested duplicate-step display issue while preserving existing sorting and staged rule flow.
- Deliverables: `tasks/completed/2026/TASK_238_MATRIX_EDITOR_STEP_PREVIEW_DUPLICATE_STEP_NUMBER_FIX.md`, `docs/completed_plans/2026/task_238_matrix_editor_step_preview_duplicate_step_number_fix_plan.md`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task238 or task237 or matrix_editor"` (`17 passed`, `69 deselected`).
- Next recommended action: wait for user review before opening the next controlled Matrix Editor task.

- `TASK_239_MATRIX_EDITOR_CELL_EDIT_AUTO_SELECT_GROUP` is complete. Editing any group step cell now auto-selects its group column, so the group highlight updates immediately during inline edit.
- Deliverables: `tasks/completed/2026/TASK_239_MATRIX_EDITOR_CELL_EDIT_AUTO_SELECT_GROUP.md`, `docs/completed_plans/2026/task_239_matrix_editor_cell_edit_auto_select_group_plan.md`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task239 or matrix_editor"` (`18 passed`, `69 deselected`).
- Next recommended action: wait for user review before opening the next controlled Matrix Editor task.

- `TASK_240_MATRIX_EDITOR_NEW_ROW_EMPTY_FIELD_GUARDS` is complete. Matrix row rendering now adds empty-state red-border cues on first 5 base fields (`Test Item`, `Section`, `Method`, `Condition`, `Requirement`) and row-level step-empty cue styling when all group step cells in that row are blank.
- Deliverables: `tasks/completed/2026/TASK_240_MATRIX_EDITOR_NEW_ROW_EMPTY_FIELD_GUARDS.md`, `docs/completed_plans/2026/task_240_matrix_editor_new_row_empty_field_guards_plan.md`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task240 or task239 or matrix_editor"` (`19 passed`, `69 deselected`).
- Next recommended action: wait for user review before opening the next controlled Matrix Editor task.

- `TASK_241_MATRIX_EDITOR_ROW_NO_WARNING_FOR_MISSING_STEPS` is complete. Empty-step reminder is now shown on row `No.` selector only (warning highlight + hover text `缺少步骤编号`), and the prior row-wide group-cell empty warning styling has been removed to avoid misleading users that every blank step cell must be filled.
- Deliverables: `tasks/completed/2026/TASK_241_MATRIX_EDITOR_ROW_NO_WARNING_FOR_MISSING_STEPS.md`, `docs/completed_plans/2026/task_241_matrix_editor_row_no_warning_for_missing_steps_plan.md`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task241 or task240 or matrix_editor"` (`19 passed`, `69 deselected`).
- Next recommended action: wait for user review before opening the next controlled Matrix Editor task.

- `TASK_242_MATRIX_EDITOR_MISSING_STEP_TOOLTIP_EN_COPY` is complete. Row-number warning tooltip copy is now English: `Missing step number`.
- Deliverables: `tasks/completed/2026/TASK_242_MATRIX_EDITOR_MISSING_STEP_TOOLTIP_EN_COPY.md`, `docs/completed_plans/2026/task_242_matrix_editor_missing_step_tooltip_en_copy_plan.md`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task242 or matrix_editor"` (`19 passed`, `69 deselected`).
- Next recommended action: wait for user review before opening the next controlled Matrix Editor task.

- `TASK_243_MATRIX_EDITOR_MINIMAL_INITIAL_GRID` is complete. Matrix Editor now initializes with one blank test item row and one group column (`G1`), with the group step cell blank so existing required-field and missing-step validation cues guide the user from the minimal valid structure.
- Deliverables: `tasks/completed/2026/TASK_243_MATRIX_EDITOR_MINIMAL_INITIAL_GRID.md`, `docs/completed_plans/2026/task_243_matrix_editor_minimal_initial_grid_plan.md`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task243 or matrix_editor"` (`20 passed`, `69 deselected`).
- Next recommended action: wait for explicit user approval before opening the next controlled Matrix Editor task.

- `TASK_244_MATRIX_EDITOR_DEFAULT_TWO_ROW_SEED_AND_SECTION_OPTIONAL` is complete. Matrix Editor now initializes with two rows: a first Visual Examination starter row (`EIA-364-18B`, `10x min magnification`, `No detrimental condition`, `G1=1`) and a second blank row. Blank `Section` cells no longer show required-field red highlighting; other required base fields keep the existing cue.
- Deliverables: `tasks/completed/2026/TASK_244_MATRIX_EDITOR_DEFAULT_TWO_ROW_SEED_AND_SECTION_OPTIONAL.md`, `docs/completed_plans/2026/task_244_matrix_editor_default_two_row_seed_and_section_optional_plan.md`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task244 or matrix_editor"` (`21 passed`, `69 deselected`).
- Next recommended action: wait for explicit user approval before opening the next controlled Matrix Editor task.

- `TASK_245_MATRIX_EDITOR_FIXED_COLUMN_WIDTHS` is complete. Matrix Editor table now uses content-width table sizing plus fixed `width`/`min-width` pairs for the row selector, first 5 definition columns, and group columns, so extra groups expand the table and use horizontal scrolling instead of compressing the column baseline.
- Deliverables: `tasks/completed/2026/TASK_245_MATRIX_EDITOR_FIXED_COLUMN_WIDTHS.md`, `docs/completed_plans/2026/task_245_matrix_editor_fixed_column_widths_plan.md`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task245 or matrix_editor"` (`22 passed`, `69 deselected`).
- Next recommended action: wait for explicit user approval before opening the next controlled Matrix Editor task.

- `TASK_246_MATRIX_EDITOR_COMPACT_FIXED_WIDTH_TABLE` is complete. Matrix Editor no longer applies the 1180px table-level minimum; the table remains content-width and each row selector, definition, and group column now has matching fixed width/min-width/max-width so the default one-group grid stays compact while many groups still overflow horizontally.
- Deliverables: `tasks/completed/2026/TASK_246_MATRIX_EDITOR_COMPACT_FIXED_WIDTH_TABLE.md`, `docs/completed_plans/2026/task_246_matrix_editor_compact_fixed_width_table_plan.md`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task246 or matrix_editor"` (`23 passed`, `69 deselected`).
- Next recommended action: wait for explicit user approval before opening the next controlled Matrix Editor task.

- `TASK_247_MATRIX_EDITOR_GROUP_NAME_WRAP_WITHIN_FIXED_WIDTH` is complete. Matrix Editor group name input now wraps text inside the existing fixed-width group column (`white-space: normal`, `overflow-wrap: anywhere`, `word-break: break-word`) and no longer applies nowrap/ellipsis clipping to group names such as `11,12`.
- Deliverables: `tasks/completed/2026/TASK_247_MATRIX_EDITOR_GROUP_NAME_WRAP_WITHIN_FIXED_WIDTH.md`, `docs/completed_plans/2026/task_247_matrix_editor_group_name_wrap_within_fixed_width_plan.md`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task247 or matrix_editor"` (`24 passed`, `69 deselected`).
- Next recommended action: wait for explicit user approval before opening the next controlled Matrix Editor task.

- `TASK_248_REVERT_MATRIX_EDITOR_GROUP_NAME_WRAP` is complete. Group name wrapping from TASK_247 was reverted to single-line nowrap/hidden/ellipsis display while preserving TASK_246 fixed 44px group column width.
- Deliverables: `tasks/completed/2026/TASK_248_REVERT_MATRIX_EDITOR_GROUP_NAME_WRAP.md`, `docs/completed_plans/2026/task_248_revert_matrix_editor_group_name_wrap_plan.md`, `frontend/src/workbench.css`, and `tests/unit/test_frontend_shell_files.py`.
- Validation: `cd frontend; npm run build` passed. Targeted checks passed with `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task248 or matrix_editor"` (`25 passed`, `69 deselected`).

- `TASK_203_DOCUMENTATION_INFORMATION_ARCHITECTURE_CLEANUP` Slice A is complete. Added a documentation map and archive semantics, updated root README read order, converted stale MVP-only domain/API/future docs into current snapshots, and recorded that later archive/move/slimming slices require separate approval. No backend, frontend, API, database, runtime, UI, task-file relocation, task-plan relocation, or deletion was performed.
- Deliverables: `tasks/completed/2026/TASK_203_DOCUMENTATION_INFORMATION_ARCHITECTURE_CLEANUP.md`, `docs/completed_plans/2026/task_203_documentation_information_architecture_cleanup_plan.md`, `docs/README.md`, `docs/archive/README.md`, `README.md`, `docs/03_DOMAIN_MODEL.md`, `docs/04_API_CONTRACTS.md`, `docs/07_FUTURE_EXTENSION_MAP.md`.
- Validation: static governance guard tests passed. `py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q` passed (`17 passed`). Documentation reference check found only historical/plan references for old MVP wording.
- Next recommended action: if further documentation cleanup is desired, explicitly approve TASK_203 Slice B for low-risk archive moves; otherwise return to the next controlled runtime consumer-first implementation task.

- `TASK_203_DOCUMENTATION_INFORMATION_ARCHITECTURE_CLEANUP` Slice B is complete. Low-risk historical materials were moved into archive groups: external AI/modification notes to `docs/archive/external_ai/`, old phase-wide plans to `docs/archive/historical_plans/`, and the packed legacy blueprint to `docs/archive/legacy_blueprints/`. References and static governance tests were updated to use archive paths. No `tasks/` files were moved, no `docs/task_XXX_*_plan.md` files were moved, and no task-board slimming was performed.
- Deliverables: `docs/archive/external_ai/`, `docs/archive/historical_plans/`, `docs/archive/legacy_blueprints/`, plus reference updates in docs, task history, and static tests.
- Validation: path-reference search found no remaining active references to old moved paths. Static governance guard tests and archive-path tests passed.
- Next recommended action: if further documentation cleanup is desired, explicitly approve Slice C task-plan archive decision or Slice D task-board slimming.

- `TASK_203_DOCUMENTATION_INFORMATION_ARCHITECTURE_CLEANUP` Slice C is complete. Task-plan archive strategy is now explicit: keep `docs/task_XXX_*_plan.md` files in place and index them instead of bulk moving paths. Added `docs/task_plan_index.md` to define usage and future revisit triggers. This preserves `task_board` historical reference stability and avoids high-risk mass path rewrites.
- Deliverables: `docs/task_plan_index.md`, plus Slice C status updates in `tasks/completed/2026/TASK_203_DOCUMENTATION_INFORMATION_ARCHITECTURE_CLEANUP.md`, `docs/completed_plans/2026/task_203_documentation_information_architecture_cleanup_plan.md`, and `docs/README.md`.
- Validation: static governance guard tests and archive-path tests passed; no old moved-path references remain.
- Next recommended action: if further documentation cleanup is desired, explicitly approve Slice D task-board slimming.

- `TASK_203_DOCUMENTATION_INFORMATION_ARCHITECTURE_CLEANUP` Slice D is complete. `docs/task_board.md` was slimmed by archiving long historical completion-note chains to `docs/archive/task_board_history_2026-05-16.md` while preserving current phase/status, source-of-truth headers, and active governance state in the main board.
- Deliverables: `docs/archive/task_board_history_2026-05-16.md`, plus board pointer text to archived history.
- Validation: static governance guard tests passed after slimming; board-state compatibility was preserved.
- Next recommended action: TASK_203 is complete. Open a new controlled task for any additional documentation restructuring.

- `TASK_204_RUNTIME_PROJECTION_READ_ONLY_CONSUMER_MINIMAL_SLICE` is complete in single-file task mode. Task file: `tasks/completed/2026/TASK_204_RUNTIME_PROJECTION_READ_ONLY_CONSUMER_MINIMAL_SLICE.md`. Implemented backend-only, in-memory, deterministic read-only runtime consumer outputs for both Matrix Overview and Step Workspace, based on existing TASK_201/TASK_202 projection foundations without API, UI, DB, StepInstance, runtime engine, or parser duplication.
- Deliverables: `backend/modules/runtime_projection/consumer_views.py`, `tests/unit/test_runtime_projection_consumer_views.py`, updates to `backend/modules/runtime_projection/__init__.py`, and execution record updates in `tasks/completed/2026/TASK_204_RUNTIME_PROJECTION_READ_ONLY_CONSUMER_MINIMAL_SLICE.md`.
- Validation: `py -m pytest tests\unit\test_runtime_projection_consumer_views.py -q` passed (`12 passed`); `py -m pytest tests\unit\test_runtime_projection_token_builder.py tests\unit\test_runtime_projection_composition.py -q` passed (`23 passed`).
- `TASK_205_RUNTIME_PROJECTION_SNAPSHOT_ADAPTER_MINIMAL_SLICE` is complete in single-file task mode. Task file: `tasks/completed/2026/TASK_205_RUNTIME_PROJECTION_SNAPSHOT_ADAPTER_MINIMAL_SLICE.md`. Implemented a backend-only, in-memory, deterministic snapshot adapter that composes existing projection builder, composition summary, Matrix Overview consumer view, and Step Workspace consumer view into one directly consumable runtime snapshot without API, UI, DB, StepInstance, runtime engine, or parser duplication.
- Deliverables: `backend/modules/runtime_projection/snapshot_adapter.py`, `tests/unit/test_runtime_projection_snapshot_adapter.py`, updates to `backend/modules/runtime_projection/__init__.py`, and execution record updates in `tasks/completed/2026/TASK_205_RUNTIME_PROJECTION_SNAPSHOT_ADAPTER_MINIMAL_SLICE.md`.
- Model fit result: `GPT-5.3-codex` suitable and confirmed for this slice.
- Validation: `py -m pytest tests\unit\test_runtime_projection_snapshot_adapter.py -q` passed (`10 passed`); `py -m pytest tests\unit\test_runtime_projection_consumer_views.py tests\unit\test_runtime_projection_token_builder.py tests\unit\test_runtime_projection_composition.py -q` passed (`35 passed`).
- Next action: review and explicitly approve TASK_206 before implementation.

- `TASK_206_RUNTIME_PROJECTION_READ_ONLY_API_ADAPTER_MINIMAL_SLICE` is complete in single-file task mode. Task file: `tasks/completed/2026/TASK_206_RUNTIME_PROJECTION_READ_ONLY_API_ADAPTER_MINIMAL_SLICE.md`. Implemented a minimal read-only runtime projection snapshot API adapter using existing snapshot composition outputs, without introducing runtime engine, persistence, UI changes, or parser duplication.
- Deliverables: `backend/api/routes_runtime_projection_read_only.py`, route wiring in `backend/api/main.py`, `tests/integration/test_runtime_projection_read_only_api.py`, and `tests/unit/test_runtime_projection_read_only_api_mapping.py`.
- Model fit result: `GPT-5.3-codex` suitable and confirmed for this slice.
- Validation: `py -m pytest tests\integration\test_runtime_projection_read_only_api.py tests\unit\test_runtime_projection_read_only_api_mapping.py -q` passed (`4 passed`); `py -m pytest tests\unit\test_runtime_projection_snapshot_adapter.py tests\unit\test_runtime_projection_consumer_views.py tests\unit\test_runtime_projection_token_builder.py tests\unit\test_runtime_projection_composition.py -q` passed (`45 passed`).
- `TASK_207_API_CONTRACT_SNAPSHOT_SYNC_AFTER_RUNTIME_PROJECTION_READ_ONLY_ADAPTER` is complete in single-file task mode. Task file: `tasks/completed/2026/TASK_207_API_CONTRACT_SNAPSHOT_SYNC_AFTER_RUNTIME_PROJECTION_READ_ONLY_ADAPTER.md`. Synced `docs/04_API_CONTRACTS.md` to include the runtime projection read-only API route added in TASK_206 and removed stale wording that no runtime projection API is exposed.
- Deliverables: `docs/04_API_CONTRACTS.md`, `tasks/completed/2026/TASK_207_API_CONTRACT_SNAPSHOT_SYNC_AFTER_RUNTIME_PROJECTION_READ_ONLY_ADAPTER.md`, and board-state text sync in static governance tests.
- Model fit result: `GPT-5.3-codex` suitable and confirmed for this slice.
- Next action: review and explicitly approve TASK_208 before implementation.

- `TASK_208_RUNTIME_PROJECTION_READ_ONLY_API_TYPED_CONTRACT_MINIMAL_SLICE` is pending user review in single-file task mode. Task file: `tasks/completed/2026/TASK_208_RUNTIME_PROJECTION_READ_ONLY_API_TYPED_CONTRACT_MINIMAL_SLICE.md`. The task should harden runtime projection read-only API response contracts from broad dictionary payloads to explicit typed nested response models, while keeping route path, read-only semantics, and runtime projection boundaries unchanged.
- Model fit: `GPT-5.3-codex` is suitable because this is a bounded backend API contract typing refactor with focused tests and no runtime engine/persistence/UI scope.
- `TASK_208_RUNTIME_PROJECTION_READ_ONLY_API_TYPED_CONTRACT_MINIMAL_SLICE` is complete in single-file task mode. Task file: `tasks/completed/2026/TASK_208_RUNTIME_PROJECTION_READ_ONLY_API_TYPED_CONTRACT_MINIMAL_SLICE.md`. Hardened runtime projection read-only API response contracts from broad dictionary payloads to explicit typed nested response models, while preserving route path and read-only semantics.
- Deliverables: typed runtime projection API response models in `backend/api/routes_runtime_projection_read_only.py` and contract coverage in `tests/unit/test_runtime_projection_read_only_api_contract.py`.
- Model fit result: `GPT-5.3-codex` suitable and confirmed for this slice.
- Validation: `py -m pytest tests\integration\test_runtime_projection_read_only_api.py tests\unit\test_runtime_projection_read_only_api_mapping.py tests\unit\test_runtime_projection_read_only_api_contract.py -q` passed (`6 passed`); `py -m pytest tests\unit\test_runtime_projection_snapshot_adapter.py tests\unit\test_runtime_projection_consumer_views.py tests\unit\test_runtime_projection_token_builder.py tests\unit\test_runtime_projection_composition.py -q` passed (`45 passed`).
- Next action: review and explicitly approve TASK_209 before implementation.

- `TASK_209_RUNTIME_PROJECTION_READ_ONLY_FRONTEND_CONSUMER_PROTOTYPE_MINIMAL_SLICE` is pending user review in single-file task mode. Task file: `tasks/completed/2026/TASK_209_RUNTIME_PROJECTION_READ_ONLY_FRONTEND_CONSUMER_PROTOTYPE_MINIMAL_SLICE.md`. The task should implement a minimal read-only frontend consumer prototype that uses the typed runtime projection API contract, validates projection consumption behavior, and avoids Workbench replacement or runtime write behavior.
- Model fit: `GPT-5.3-codex` is suitable because this is a bounded frontend read-only consumer integration slice with strict runtime boundary constraints.
- `TASK_209_RUNTIME_PROJECTION_READ_ONLY_FRONTEND_CONSUMER_PROTOTYPE_MINIMAL_SLICE` is complete in single-file task mode. Task file: `tasks/completed/2026/TASK_209_RUNTIME_PROJECTION_READ_ONLY_FRONTEND_CONSUMER_PROTOTYPE_MINIMAL_SLICE.md`. Implemented a minimal isolated read-only frontend runtime projection consumer prototype with typed API consumption and deterministic projection rendering, without Workbench replacement or runtime write behavior.
- Deliverables: runtime projection typed client additions in `frontend/src/api/client.ts`, prototype feature under `frontend/src/features/runtime-projection-read-only/`, route/page wiring in `frontend/src/App.tsx` and `frontend/src/pages/RuntimeProjectionPrototypePage.tsx`, plus style file `frontend/src/runtime-projection-prototype.css`.
- Model fit result: `GPT-5.3-codex` suitable and confirmed for this slice.
- Validation: `npm run build` passed; `tests/unit/test_frontend_shell_files.py -q` currently reports existing historical failures outside TASK_209 scope (legacy static expectation drift).
- Next action: wait for user approval of the next controlled task; do not auto-advance.

- `TASK_210_RUNTIME_PROJECTION_PROTOTYPE_ISOLATION_HARDENING` is complete in single-file task mode. Task file: `tasks/completed/2026/TASK_210_RUNTIME_PROJECTION_PROTOTYPE_ISOLATION_HARDENING.md`. Added clear isolation markers to prevent user confusion between development prototype and production features: sidebar navigation label changed to "Runtime Prototype (Dev)", page-level warning banner added with dev badge and explanatory text, and route-level comment documenting prototype nature. No functional behavior changes were made.
- Deliverables: `frontend/src/components/layout/Sidebar.tsx` (navigation label), `frontend/src/features/runtime-projection-read-only/RuntimeProjectionPrototypeView.tsx` (warning banner), `frontend/src/runtime-projection-prototype.css` (banner styles), `frontend/src/App.tsx` (route comment).
- Model fit result: `GPT-5.3-codex` suitable and confirmed for this bounded UI isolation fix.
- Validation: `npm run build` passed; no new test failures introduced; prototype page remains fully functional with clear dev labeling.
- Next action: wait for user approval of the next controlled task; do not auto-advance.

- `TASK_211_PROJECT_WORKBENCH_RUNTIME_CONSOLE_BASELINE_REPLACEMENT` is complete in single-file task mode. Task file: `tasks/completed/2026/TASK_211_PROJECT_WORKBENCH_RUNTIME_CONSOLE_BASELINE_REPLACEMENT.md`. Replaced the Project Workbench primary IA with a Runtime Console baseline skeleton that consumes the existing read-only runtime projection snapshot API from Matrix draft data, renders runtime summary, Matrix projection tokens, Step Workspace, runtime attention, and report/output sync visibility, while downgrading folder, approval package, evidence placement, and lookup to secondary folded surfaces.
- Deliverables: runtime projection consumption wiring in `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`, Runtime Console layout in `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`, projection-driven Matrix Overview in `frontend/src/features/project-workbench/ProjectWorkbenchMatrixOverview.tsx`, related styles in `frontend/src/workbench.css`, and static test alignment in `tests/unit/test_frontend_shell_files.py`.
- Model fit result: `GPT-5.3-codex` suitable and confirmed for this bounded frontend IA replacement slice.
- Validation: `npm run build` passed; `py -m pytest tests\unit\test_frontend_shell_files.py -q` reports 9 known historical failures outside TASK_211 scope, with TASK_211 Workbench assertions aligned to the Runtime Console direction.
- Next action: wait for user approval of the next controlled task; do not auto-advance.

- `TASK_212_PROJECT_WORKBENCH_RUNTIME_CONSOLE_MOCKUP_COMPLETENESS_PASS` is complete in single-file task mode. Task file: `tasks/completed/2026/TASK_212_PROJECT_WORKBENCH_RUNTIME_CONSOLE_MOCKUP_COMPLETENESS_PASS.md`. Expanded the Project Workbench first screen to closely match the approved Runtime Console mockup with dense placeholder Matrix table, filter toolbar, full Step Workspace, runtime attention, recent activity, fee estimate, lifecycle/readiness strip, and compact Setup Manager entry. Placeholder/mock surfaces are intentionally used where real runtime data is not implemented yet.
- Deliverables: enhanced Runtime Console layout in `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`, high-density placeholder/real projection Matrix rendering in `frontend/src/features/project-workbench/ProjectWorkbenchMatrixOverview.tsx`, and related styles in `frontend/src/workbench.css`.
- Model fit result: `GPT-5.3-codex` suitable and confirmed for this bounded frontend mockup completeness pass.
- Validation: `npm run build` passed; board/governance tests passed (`17 passed`); `py -m pytest tests\unit\test_frontend_shell_files.py -q` reports 9 known historical failures outside TASK_212 scope.
- Next action: wait for user approval of the next controlled task; do not auto-advance.

- `TASK_213_PROJECT_WORKBENCH_TOPBAR_AND_FILTER_CONTROL_DENSITY_FIX` is complete in single-file task mode. Task file: `tasks/completed/2026/TASK_213_PROJECT_WORKBENCH_TOPBAR_AND_FILTER_CONTROL_DENSITY_FIX.md`. Corrected the Runtime Console top area to better match the approved mockup, moving project identity, metadata, progress, runtime metrics, last update, and refresh affordance into a compact single top row. Also locked filter checkbox/radio controls to normal 14px sizing and reduced readiness status dot size.
- Deliverables: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`, `frontend/src/workbench.css`.
- Model fit result: `GPT-5.3-codex` suitable and confirmed for this bounded frontend density correction.
- Validation: `npm run build` passed.
- Next action: wait for user approval of the next controlled task; do not auto-advance.

- `TASK_214_PROJECT_WORKBENCH_MOCKUP_VISUAL_CLONE_DENSITY_PASS` is complete in single-file task mode. Task file: `tasks/completed/2026/TASK_214_PROJECT_WORKBENCH_MOCKUP_VISUAL_CLONE_DENSITY_PASS.md`. Tightened Workbench visual density and proportions to better clone the approved mockup: reduced page/topbar spacing, Matrix table width/row/cell/token sizes, Step Workspace width and inner density, and bottom surface spacing so more target content is visible at once.
- Deliverables: `frontend/src/workbench.css`.
- Model fit result: `GPT-5.3-codex` suitable and confirmed for this bounded visual density pass.
- Validation: `npm run build` passed.
- Next action: wait for user approval of the next controlled task; do not auto-advance.

- `TASK_215_DEFAULT_COLLAPSED_ICON_SIDEBAR` is complete in single-file task mode. Task file: `tasks/completed/2026/TASK_215_DEFAULT_COLLAPSED_ICON_SIDEBAR.md`. Changed the application shell sidebar to default collapsed icon-only mode, preserved explicit local expanded/collapsed preference, added native hover tooltip labels for navigation icons, and tightened the collapsed rail to reserve more workspace width.
- Deliverables: `frontend/src/components/layout/AppShell.tsx`, `frontend/src/components/layout/Sidebar.tsx`, `frontend/src/styles.css`.
- Model fit result: `GPT-5.3-codex` suitable and confirmed for this bounded React/CSS shell adjustment.
- Validation: `npm run build` passed; static governance guard tests passed.
- Next action: wait for user approval of the next controlled task; do not auto-advance.

- `TASK_216_MATRIX_AUTHORITY_TO_RUNTIME_CONSOLE_SYNC_CONTRACT_AND_NAVIGATION_SLICE` is complete in single-file task mode. Task file: `tasks/completed/2026/TASK_216_MATRIX_AUTHORITY_TO_RUNTIME_CONSOLE_SYNC_CONTRACT_AND_NAVIGATION_SLICE.md`. Added a dedicated project-scoped Matrix Editor route/page, wired Workbench-to-Matrix navigation, surfaced runtime authority sync contract fields (authority version, candidate version, projection reference, alignment state), and added selected-token clearing protection when refreshed projection no longer contains the previous token.
- Deliverables: `frontend/src/pages/ProjectMatrixEditorPage.tsx`, `frontend/src/App.tsx`, `frontend/src/pages/ProjectWorkbenchPage.tsx`, `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`, `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`, `frontend/src/workbench.css`.
- Model fit result: `GPT-5.3-codex` suitable and confirmed for this bounded frontend/runtime-consumer integration slice.
- Validation: `npm run build` passed; static governance guard tests passed.
- Next action: wait for user approval of the next controlled task; do not auto-advance.

- `TASK_217_MATRIX_EDITOR_PLACEHOLDER_CLONE_AND_WORKBENCH_MATRIX_BUTTON_NAV` is complete in single-file task mode. Task file: `tasks/completed/2026/TASK_217_MATRIX_EDITOR_PLACEHOLDER_CLONE_AND_WORKBENCH_MATRIX_BUTTON_NAV.md`. Replaced Matrix Editor page with a static placeholder clone-oriented layout (toolbar + matrix table + side panel) and wired the Workbench Step Workspace right-side `Matrix` button to open the Matrix Editor route.
- Deliverables: `frontend/src/pages/ProjectMatrixEditorPage.tsx`, `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`, `frontend/src/workbench.css`, `frontend/src/App.tsx`.
- Model fit result: `GPT-5.3-codex` suitable and confirmed for this bounded frontend placeholder/navigation slice.
- Validation: `npm run build` passed; static governance guard tests passed.
- Next action: wait for user approval of the next controlled task; do not auto-advance.

- `TASK_218_MATRIX_EDITOR_VISUAL_ALIGNMENT_DENSITY_PASS` is complete in single-file task mode. Task file: `tasks/completed/2026/TASK_218_MATRIX_EDITOR_VISUAL_ALIGNMENT_DENSITY_PASS.md`. Applied a visual-density alignment pass to Matrix Editor placeholder UI: denser top header hierarchy, summary strip, segmented section tabs, tighter matrix grid typography/spacing, and more structured right-side panel cards, while keeping placeholder-only behavior.
- Deliverables: `frontend/src/pages/ProjectMatrixEditorPage.tsx`, `frontend/src/workbench.css`.
- Model fit result: `GPT-5.3-codex` suitable and confirmed for this bounded frontend visual-alignment slice.
- Validation: `npm run build` passed; static governance guard tests passed.
- Next action: wait for user approval of the next controlled task; do not auto-advance.

- `TASK_219_MATRIX_EDITOR_PIXEL_ALIGNMENT_PASS` is complete in single-file task mode. Task file: `tasks/completed/2026/TASK_219_MATRIX_EDITOR_PIXEL_ALIGNMENT_PASS.md`. Added grouped matrix header bands and tighter subheaders, promoted primary action hierarchy, and reorganized right-side panel card flow to better match the target sketch while preserving placeholder-only behavior.
- Deliverables: `frontend/src/pages/ProjectMatrixEditorPage.tsx`, `frontend/src/workbench.css`.
- Model fit result: `GPT-5.3-codex` suitable and confirmed for this bounded frontend alignment refinement.
- Validation: `npm run build` passed; static governance guard tests passed.
- Next action: wait for user approval of the next controlled task; do not auto-advance.

- `TASK_219A_PROJECT_WORKBENCH_RUNTIME_CONSOLE_REPOSITIONING` is complete in single-file task mode. Task file: `tasks/completed/2026/TASK_219A_PROJECT_WORKBENCH_RUNTIME_CONSOLE_REPOSITIONING.md`. Repositioned Workbench lower-half information architecture into runtime-first support surfaces: added compact runtime support status cards, demoted folder/approval/evidence/lookup heavy workflows into a single collapsed advanced-support section with nested details, and kept runtime/output sections as primary.
- Deliverables: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`, `frontend/src/workbench.css`, `docs/completed_plans/2026/task_219a_project_workbench_runtime_console_repositioning_plan.md`.
- Model fit result: `GPT-5.3-codex` suitable and confirmed for this bounded frontend IA repositioning slice.
- Validation: `npm run build` passed; board-state governance tests passed (`17 passed`); `py -m pytest tests\unit\test_frontend_shell_files.py -q` reports historical static expectation drift failures outside TASK_219A scope.
- Next action: wait for user approval of the next controlled task; do not auto-advance.

- `TASK_219B_PROJECT_WORKBENCH_MODEL_BOUNDARY_SPLIT` is complete in single-file task mode. Task file: `tasks/completed/2026/TASK_219B_PROJECT_WORKBENCH_MODEL_BOUNDARY_SPLIT.md`. Split Workbench consumer boundaries into runtime and support model surfaces, kept behavior stable, and reduced Matrix Editor coupling to support-action state by switching it to runtime-boundary model consumption.
- Deliverables: `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`, `frontend/src/features/project-workbench/useProjectWorkbenchSupportModel.ts`, `frontend/src/pages/ProjectWorkbenchPage.tsx`, `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`, `frontend/src/pages/ProjectMatrixEditorPage.tsx`, `docs/completed_plans/2026/task_219b_project_workbench_model_boundary_split_plan.md`.
- Model fit result: `GPT-5.3-codex` suitable and confirmed for this bounded frontend model split slice.
- Validation: `npm run build` passed; board-state governance tests passed (`17 passed`); `py -m pytest tests\unit\test_frontend_shell_files.py -q` reports historical static expectation drift failures outside TASK_219B scope.
- Next action: wait for user approval of the next controlled task; do not auto-advance.

- `TASK_219C_DERIVED_OUTPUT_STATUS_CONSOLE_ALIGNMENT` is complete in single-file task mode. Task file: `tasks/completed/2026/TASK_219C_DERIVED_OUTPUT_STATUS_CONSOLE_ALIGNMENT.md`. Aligned Project Workbench output panel language from downstream/manual-workflow framing to derived-output runtime-sync framing, while keeping output status DTO compatibility unchanged.
- Deliverables: `frontend/src/features/project-workbench/ProjectWorkbenchDocumentStatusPanel.tsx`, `frontend/src/features/project-workbench/projectWorkbenchVersionSelectors.ts`, `tests/unit/test_frontend_shell_files.py`.
- Model fit result: `GPT-5.3-codex` suitable and confirmed for this bounded frontend copy/selector alignment slice.
- Validation: `npm run build` passed; `py -m pytest tests\unit\test_frontend_shell_files.py -q` reports historical static expectation drift failures outside TASK_219C scope.
- Next action: wait for user approval of the next controlled task; do not auto-advance.

- `TASK_219D_LIGHTWEIGHT_MATERIAL_DROP_SURFACE_DESIGN_AND_SLICE` is complete in single-file task mode. Task file: `tasks/completed/2026/TASK_219D_LIGHTWEIGHT_MATERIAL_DROP_SURFACE_DESIGN_AND_SLICE.md`. Added a lightweight secondary "Other materials" surface with preview-first actions and explicit browser/desktop drop limitation messaging, without introducing new storage/runtime evidence domains.
- Deliverables: `frontend/src/features/project-workbench/ProjectWorkbenchMaterialDropPanel.tsx`, `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`, `frontend/src/workbench.css`, `tests/unit/test_frontend_shell_files.py`.
- Model fit result: `GPT-5.3-codex` suitable and confirmed for this bounded frontend support-surface slice.
- Validation: `npm run build` passed; board-state governance tests passed (`17 passed`); `py -m pytest tests\unit\test_frontend_shell_files.py -q` reports the same historical static expectation drift failures outside TASK_219D scope, with TASK_219D-specific static check passing.
- Next action: wait for user approval of the next controlled task; do not auto-advance.

- `TASK_219E_WORKBENCH_RUNTIME_CONSOLE_REGRESSION_GUARDS` is complete in single-file task mode. Task file: `tasks/completed/2026/TASK_219E_WORKBENCH_RUNTIME_CONSOLE_REGRESSION_GUARDS.md`. Added static regression guards to keep Workbench as Runtime Console consumption surface, keep Setup/Evidence sections secondary, keep Matrix editing out of Workbench, and keep `fetch()` access constrained to API client boundaries.
- Deliverables: `tests/unit/test_frontend_shell_files.py`, `tasks/completed/2026/TASK_219E_WORKBENCH_RUNTIME_CONSOLE_REGRESSION_GUARDS.md`.
- Model fit result: `GPT-5.3-codex` suitable and confirmed for this bounded static guard slice.
- Validation: `py -m pytest tests\unit\test_frontend_shell_files.py -q`; board-state governance tests executed because `docs/task_board.md` changed.
- Next action: wait for user approval of the next controlled task; do not auto-advance.

- `TASK_219F_PROJECT_WORKBENCH_LEGACY_SUPPORT_REMOVAL` is complete in single-file task mode. Task file: `tasks/completed/2026/TASK_219F_PROJECT_WORKBENCH_LEGACY_SUPPORT_REMOVAL.md`. Removed visible legacy support surfaces from Workbench (`Project folder`, `Approval package` manual form, `Legacy evidence detail`, `Read-only lookup`) and kept Runtime Console + derived outputs + runtime support status with lightweight Other materials surface.
- Deliverables: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`, `tests/unit/test_frontend_shell_files.py`, `tasks/completed/2026/TASK_219F_PROJECT_WORKBENCH_LEGACY_SUPPORT_REMOVAL.md`.
- Model fit result: `GPT-5.3-codex` suitable and confirmed for this bounded frontend boundary-removal slice.
- Validation: `npm run build`; `py -m pytest tests\unit\test_frontend_shell_files.py -q`; board-state governance tests executed because `docs/task_board.md` changed.
- Next action: wait for user approval of the next controlled task; do not auto-advance.

- `TASK_202_RUNTIME_PROJECTION_COMPOSITION_HELPER_MINIMAL_SLICE` is complete. Implemented a minimal backend-only, in-memory, deterministic runtime composition helper that aggregates already-supplied projection dimensions into read-model summaries. The helper is not a runtime engine and does not evaluate real lifecycle, stale logic, execution state, or orchestration/report/evidence engines. It does not mutate projection fields, token identity, Matrix authority, or Project lifecycle.
- Deliverables: `tasks/completed/2026/TASK_202_RUNTIME_PROJECTION_COMPOSITION_HELPER_MINIMAL_SLICE.md`, `backend/modules/runtime_projection/composition.py`, `backend/modules/runtime_projection/models.py`, `backend/modules/runtime_projection/__init__.py`, `backend/modules/runtime_projection/fake_fixture_builder.py`, `tests/unit/test_runtime_projection_composition.py`.
- Validation: focused unit tests passed. `py -m pytest -q tests/unit/test_runtime_projection_composition.py tests/unit/test_runtime_projection_token_builder.py` passed.
- Next recommended action: define and approve the next controlled runtime projection task before any new implementation; do not auto-advance.

- `TASK_201_PROJECTION_DTO_AND_TOKEN_REFERENCE_BUILDER_MINIMAL_SLICE` is complete. Implemented a minimal backend-only, in-memory, deterministic, pure-function runtime projection slice with DTO-like structures and a token reference builder under `backend/modules/runtime_projection/`. The implementation reuses existing parser capabilities from `backend/modules/test_plan/matrix_step_sequence_validation.py` (`parse_step_tokens`, `ParsedStepToken`, `validate_group_step_sequences`) and does not create a duplicate parser file. Fake/static projection dimensions are optional and remain projection/read-model fields, not domain source of truth.
- Deliverables: `tasks/completed/2026/TASK_201_PROJECTION_DTO_AND_TOKEN_REFERENCE_BUILDER_MINIMAL_SLICE.md`, `backend/modules/runtime_projection/__init__.py`, `backend/modules/runtime_projection/models.py`, `backend/modules/runtime_projection/token_projection_builder.py`, `tests/unit/test_runtime_projection_token_builder.py`.
- Validation: focused unit tests and existing parser tests passed, plus static governance guard tests updated for TASK_201 board state. `python -m pytest -q tests/unit/test_runtime_projection_token_builder.py` passed; `python -m pytest -q tests/unit/test_matrix_step_sequence_validation.py` passed; `py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q` passed.
- Next recommended action: define and approve the next minimal runtime composition slice only if requested; do not auto-advance.

- `TASK_200_FIRST_RUNTIME_IMPLEMENTATION_SLICE_PLANNING` is complete. Converted the TASK_194-TASK_199 governance foundation into a first runtime implementation-slice plan without implementing runtime DTOs, parser changes, projection services, API routes, database schema, frontend components, StepInstance, report sync, or evidence/image behavior. The plan corrects TASK_201 direction to `TASK_201_PROJECTION_DTO_AND_TOKEN_REFERENCE_BUILDER_MINIMAL_SLICE`, requiring reuse of existing `backend/modules/test_plan/matrix_step_sequence_validation.py` (`parse_step_tokens`, `ParsedStepToken`, `validate_group_step_sequences`) and explicitly avoiding a duplicate default parser at `backend/modules/test_plan/matrix_step_token_parser.py`.
- Deliverables: `tasks/completed/2026/TASK_200_FIRST_RUNTIME_IMPLEMENTATION_SLICE_PLANNING.md`, `docs/first_runtime_implementation_slice_planning.md`, and `docs/completed_plans/2026/task_200_first_runtime_implementation_slice_planning_plan.md`.
- Validation: document-level consistency check completed; no backend/frontend/API/DB runtime source files were intentionally changed. Static governance guard tests were updated for the TASK_200 board state. `py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q` passed (`17 passed`).
- Next recommended action: define and approve `TASK_201_PROJECTION_DTO_AND_TOKEN_REFERENCE_BUILDER_MINIMAL_SLICE`; planning first, backend-only/in-memory/pure-function implementation only if separately approved.

- `TASK_198_RUNTIME_PROJECTION_SERVICE_AND_READ_MODEL_BOUNDARY` is complete. Defined the Runtime Projection Service and read-model boundary without implementing backend runtime, ORM/dataclasses, persistence, SQLite schema, API, React/CSS, runtime engine, cache engine, projection engine, report sync implementation, evidence/image implementation, notification system, or StepInstance. The task records that `Projection != Domain Identity`, Runtime Projection is not source of truth, and projection composition must remain independently evolvable. It also corrects the next-step direction from the earlier UI-baseline recommendation to a runtime-boundary governance task before UI implementation.
- Deliverables: `tasks/completed/2026/TASK_198_RUNTIME_PROJECTION_SERVICE_AND_READ_MODEL_BOUNDARY.md`, `docs/runtime_projection_service_and_read_model_boundary.md`, and `docs/completed_plans/2026/task_198_runtime_projection_service_and_read_model_boundary_plan.md`.
- Validation: document-level consistency check completed; no backend/frontend runtime source files were intentionally changed. Static governance guard tests were updated for the TASK_198 board state. `py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q` passed (`17 passed`).
- Next recommended action: define and approve `TASK_199_MATRIX_OVERVIEW_RUNTIME_PROJECTION_CONSUMPTION_MODEL`; planning first, no UI or runtime implementation unless separately approved.

- `TASK_197_INTERACTIVE_STEP_TOKEN_READ_MODEL` is complete. Defined the Interactive Step Token Read Model Projection Foundation without implementing backend runtime, ORM/dataclasses, persistence, SQLite schema, API, React/CSS, runtime engine, report sync engine, evidence/image storage, notification system, or StepInstance. The foundation records that `Projection != Domain Identity`, Runtime Projection is not source of truth, and projection layers must remain independently replaceable. UI token, badge, stale marker, report sync marker, runtime attention, selected state, evidence projection, and group runtime status are projection dimensions only and cannot redefine Step identity, Matrix authority, or Project lifecycle.
- Deliverables: `tasks/completed/2026/TASK_197_INTERACTIVE_STEP_TOKEN_READ_MODEL.md`, `docs/interactive_step_token_read_model_projection_foundation.md`, and `docs/completed_plans/2026/task_197_interactive_step_token_read_model_plan.md`.
- Validation: document-level consistency check completed; no backend/frontend runtime source files were intentionally changed. Static governance guard tests were updated for the TASK_197 board state. `py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q` passed (`17 passed`).
- Next recommended action: define and approve `TASK_198_WORKBENCH_RUNTIME_CONSOLE_UI_BASELINE`; planning first, no UI implementation unless separately approved.

- `TASK_196_STEP_CENTRIC_DOMAIN_FOUNDATION` is complete. Defined the minimal Step-centric domain foundation without implementing Python dataclasses, SQLAlchemy models, database migrations, repositories, services, APIs, frontend DTOs, read models, status engines, or UI changes. The foundation defines conceptual `StepInstance` identity, stable identity rules, Matrix token to StepInstance mapping, lifecycle concepts, Runtime Projection Boundary, data ownership boundaries, and derived output relationships.
- Deliverables: `tasks/completed/2026/TASK_196_STEP_CENTRIC_DOMAIN_FOUNDATION.md`, `docs/step_centric_domain_foundation.md`, and `docs/completed_plans/2026/task_196_step_centric_domain_foundation_plan.md`.
- Validation: document-level consistency check completed; no backend/frontend runtime source files were intentionally changed. Static governance guard tests were updated for the TASK_196 board state. `py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q` passed (`17 passed`).
- Next recommended action: define and approve `TASK_197_INTERACTIVE_STEP_TOKEN_READ_MODEL`; planning first, no read model/API/frontend implementation unless separately approved.

- `TASK_195_PROJECT_WORKBENCH_RUNTIME_CONSOLE_INFORMATION_ARCHITECTURE` is complete. Defined the Project Workbench Runtime Console information architecture without implementing UI, API, backend runtime, database schema, StepInstance, or Matrix Editor behavior. The Runtime IA clarifies that Matrix-driven does not mean Matrix-first UI; Matrix is the execution authority map and runtime projection surface inside the Project lifecycle container. It also defines the Runtime Attention Priority Model so Workbench can express the most important current issue instead of becoming a status stacking page.
- Deliverables: `tasks/completed/2026/TASK_195_PROJECT_WORKBENCH_RUNTIME_CONSOLE_INFORMATION_ARCHITECTURE.md`, `docs/project_workbench_runtime_console_information_architecture.md`, and `docs/completed_plans/2026/task_195_project_workbench_runtime_console_information_architecture_plan.md`.
- Validation: document-level consistency check completed; no backend/frontend runtime source files were intentionally changed. Static governance guard tests were updated for the TASK_195 board state. `py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q` passed (`17 passed`).
- Next recommended action: define and approve `TASK_196_STEP_CENTRIC_DOMAIN_FOUNDATION`; planning/design first, no schema or backend implementation unless separately approved.

- `TASK_194_MATRIX_EXECUTION_PHASE_PRODUCT_REALIGNMENT` is complete. Added the Matrix-driven Laboratory Execution Phase governance alignment while preserving Phase 11 as the controlled foundation baseline. The approved principle is now recorded: `Matrix is the execution authority map, Project remains the lifecycle container.` This task updated active product/governance wording and created the next-stage principles document without backend, frontend, API, database, or Office behavior changes.
- Deliverables: `tasks/completed/2026/TASK_194_MATRIX_EXECUTION_PHASE_PRODUCT_REALIGNMENT.md`, `docs/matrix_execution_phase_principles.md`, `docs/completed_plans/2026/task_194_matrix_execution_phase_product_realignment_plan.md`, plus stage wording updates in `AGENTS.md`, `README.md`, `PRODUCT.md`, `docs/archive/legacy_blueprints/ConnLab_Master_Blueprint.md`, and this task board.
- Validation: document-level consistency check completed; no backend/frontend runtime source files were intentionally changed. Static governance guard tests were updated for the TASK_194 board state. `py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q` passed (`17 passed`).
- Next recommended action: define and approve `TASK_195_PROJECT_WORKBENCH_RUNTIME_CONSOLE_INFORMATION_ARCHITECTURE`; planning/design only, no UI implementation unless separately approved.

- `TASK_193_PHASE_FREEZE_ARCHITECTURE_INVENTORY_SCOPE_REDEFINITION` is complete. Added stage freeze and architecture inventory documents, synchronized README stage wording with actual implemented scope, and registered governance alignment for the current Project Workbench / Matrix / Approval Package phase without business-code refactor.
- Deliverables: `docs/stage_freeze_2026-05-15_project_workbench_matrix_approval_package.md`, `docs/architecture_inventory_2026-05-15.md`, `tasks/completed/2026/TASK_193_PHASE_FREEZE_ARCHITECTURE_INVENTORY_SCOPE_REDEFINITION.md`, `docs/completed_plans/2026/task_193_phase_freeze_architecture_inventory_scope_redefinition_plan.md`.
- Validation: document consistency check passed (README/task_board/tasks/code evidence aligned for stage definition); no backend/frontend behavior changes were made in this task.
- Next recommended action: define and approve next controlled implementation task within the frozen stage baseline (Project Workbench / Matrix / Approval Package), with explicit in-scope/out-of-scope boundaries.

> **TASK_178 COMPLETE**: New Project Intake Logic Fixes
> - Fixed P0 auto-select duplicate handling without using `create_separate` as an implicit page-load action.
> - Fixed duplicate confirmation re-click behavior with backend selected-asset shortcut and frontend active-case guard.
> - Stopped remaining Phase 2/3 items after review because they lack confirmed defects and would expand duplicate lifecycle scope.
> - Plan: `tasks/completed/2026/TASK_178_NEW_PROJECT_INTAKE_LOGIC_FIXES.md`

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
- Plan: `docs/completed_plans/2026/task_180_test_record_fee_dataset_preview_plan.md`.
- `TASK_181_TEST_RECORD_TEMPLATE_AND_FEE_FORM_GENERATION` is complete. Added backend document generation from TASK_180 dataset preview for test record `.docx` and fee-evaluation workbook outputs with strict infrastructure-boundary Office writes. Test-record generation is implemented via `python-docx`; fee generation is isolated behind Excel COM and returns `skipped_unavailable` when COM is unavailable. Includes overwrite protection, template/path validation, and typed API response.
- Validation: `py -m pytest tests\unit\test_test_record_fee_document_generation_service.py tests\unit\test_test_record_document_gateway.py tests\unit\test_fee_evaluation_workbook_gateway.py tests\integration\test_test_record_fee_document_generation_api.py -q` passed (9 passed); `py -m pytest tests\unit\test_project_test_plan_draft_service.py tests\integration\test_project_test_plan_draft_api.py tests\unit\test_test_record_fee_dataset_preview_service.py tests\integration\test_test_record_fee_dataset_preview_api.py -q` passed (14 passed); task-board guard run passed (17 passed).
- Plan: `docs/completed_plans/2026/task_181_test_record_template_fee_form_generation_plan.md`.
- `TASK_182_APPROVAL_PACKAGE_GENERATION_AND_PROJECT_FOLDER_PLACEMENT` is complete. Added a backend preview-and-execute approval-package workflow that places completed application form, generated test record, generated fee evaluation file, and selected evidence/source files into Project folder approval-package destinations. It enforces conflict blocking when overwrite is false and keeps `.msg` evidence under `E-mail` while package documents are placed under `Submitted Material`.
- Validation: `py -m pytest tests\unit\test_approval_package_service.py tests\integration\test_approval_package_api.py -q` passed (5 passed); `py -m pytest tests\unit\test_evidence_placement_service.py tests\integration\test_evidence_placement_api.py tests\unit\test_test_record_fee_document_generation_service.py tests\integration\test_test_record_fee_document_generation_api.py -q` passed (11 passed); task-board guard run passed (17 passed).
- Plan: `docs/completed_plans/2026/task_182_approval_package_generation_and_project_folder_placement_plan.md`.
- `TASK_183_PROJECT_WORKBENCH_APPROVAL_PACKAGE_UI_WIRING` is complete. Project Workbench now includes a dedicated approval-package panel that wires TASK_182 backend preview/execute APIs through `frontend/src/api/client.ts` and a focused `ApprovalPackagePanel` component. Operators can input required paths, optional fee/evidence paths, preview blockers and warnings, and execute only when preview exists and is blocker-free.
- Validation: `npm run build` (frontend) passed; `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or approval or folder"` passed (`5 passed, 53 deselected`); task-board guard run passed (`17 passed`).
- Plan: `docs/completed_plans/2026/task_183_project_workbench_approval_package_ui_wiring_plan.md`.
- `TASK_184_PROJECT_WORKBENCH_MATRIX_FIRST_REDESIGN_BASELINE` is complete. It defines the Matrix-first Workbench redesign baseline from real operator flow: source archive, Matrix review, duration and Section 2, test record, fee evaluation, approval package, and reference lookup. It confirms the boundary that `Project` remains the system center, `ProjectTestPlan` is the structured intermediate object, and Matrix is the primary operator work view rather than an overloaded all-purpose table.
- Validation: `py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q` passed (`17 passed`).
- Plan: `docs/completed_plans/2026/task_184_project_workbench_matrix_first_redesign_baseline_plan.md`.
- `TASK_185_PROJECT_WORKBENCH_STATE_MODEL_AND_LAYOUT_REFACTOR` is created as the next controlled implementation task. It scopes the first implementation step from TASK_184: thin the route page, extract a feature-level workbench model hook, and introduce stage-oriented layout composition while preserving existing folder/evidence/approval package behavior and API contracts.
- `TASK_185_PROJECT_WORKBENCH_STATE_MODEL_AND_LAYOUT_REFACTOR` is complete. Project Workbench route-level logic is now thinned through a feature model and layout composition: state and API orchestration moved to `useProjectWorkbenchModel`, evidence rendering moved to `ProjectWorkbenchEvidencePanel`, and page composition moved to `ProjectWorkbenchLayout`, while preserving existing folder/evidence/approval package behavior and API contracts.
- Validation: `npm run build` passed (frontend); `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or approval or folder"` passed (`5 passed, 53 deselected`); task-board guard run passed (`17 passed`).
- Plan: `docs/completed_plans/2026/task_185_project_workbench_state_model_and_layout_refactor_plan.md`.
- `TASK_186_PROJECT_WORKBENCH_MATRIX_REVIEW_SURFACE` is complete. Project Workbench now renders a Matrix-first review surface from existing ProjectTestPlanDraft APIs. The UI shows active draft availability, source document/status/version context, group/step summaries, duration hint visibility, and draft warning/empty/error states while preserving existing folder, lookup, approval-package, and evidence workflows.
- Validation: `npm run build` passed (frontend); `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix"` passed (`4 passed, 55 deselected`); task-board guard run passed (`17 passed`).
- Plan: `docs/completed_plans/2026/task_186_project_workbench_matrix_review_surface_plan.md`.
- `TASK_187_PROJECT_WORKBENCH_DOCUMENT_PIPELINE_AUTOFILL` is complete. Project Workbench now auto-fills approval package inputs from known project context: latest project folder record, source-archive evidence plan, and approval-package preview/execute outputs. Auto-filled fields stay editable, and manual edits switch that field to manual mode so subsequent auto-refresh does not overwrite operator corrections.
- Validation: `npm run build` passed (frontend); `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or approval or matrix"` passed (`5 passed, 55 deselected`); task-board guard run passed (`17 passed`).
- Plan: `docs/completed_plans/2026/task_187_project_workbench_document_pipeline_autofill_plan.md`.
- `TASK_188_PROJECT_WORKBENCH_VERSION_AND_STALE_STATUS` frontend status slice is complete, but later business review found it incomplete for reload-safe lab traceability. Project Workbench now derives and displays version/freshness status for downstream outputs (`Section 2`, `test record`, `fee evaluation`, `approval package`) using feature-level selectors. This remains useful UI, but the next controlled correction must add a minimal persistent output version ledger before Matrix editing/freeze becomes the mainline.
- Validation: `npm run build` passed (frontend); `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or approval or matrix"` passed (`6 passed, 55 deselected`); task-board guard run passed (`17 passed`).
- Plan: `docs/completed_plans/2026/task_188_project_workbench_version_and_stale_status_plan.md`.
- Product/data-management baseline: `docs/matrix_test_plan_data_management_decisions.md`.
- Proposed correction task: `tasks/completed/2026/TASK_188_PROJECT_OUTPUT_VERSION_LEDGER_CORRECTION.md`.
- Correction plan: `docs/completed_plans/2026/task_188_project_output_version_ledger_correction_plan.md`.
- `TASK_188_PROJECT_OUTPUT_VERSION_LEDGER_CORRECTION` is complete. Added persisted project output ledger (`project_output_records`) with domain enums/model, repository, application service, and API routes (`POST/GET /api/projects/{project_id}/output-records`, `GET /api/projects/{project_id}/output-records/status`). Integrated output-record registration into Section 2 write-back, test-record/fee generation, and approval-package execute flow. Workbench version status now consumes backend persisted status summary (reload-safe) with existing local derivation kept as fallback.
- Validation: `python -m pytest tests/unit/test_project_output_record_service.py tests/integration/test_project_output_records_api.py tests/integration/test_section2_write_back_api.py tests/integration/test_test_record_fee_document_generation_api.py tests/integration/test_approval_package_api.py -q` passed (9 passed); `python -m pytest tests/unit/test_frontend_shell_files.py -k task188 -q` passed (1 passed).
- `TASK_189_MATRIX_EDIT_AND_FREEZE_FOUNDATION` implementation is present but acceptance mismatch is confirmed during review. Current behavior supersedes previous reviewed authority immediately when editing a reviewed draft, which conflicts with approved semantics requiring supersede only after candidate confirm succeeds. Validation severity is also mismatched (method/requirement currently treated as blockers).
- Validation note: existing TASK_189 tests pass but currently assert the incorrect authority behavior; acceptance is therefore not granted.
- Correction task proposed: `tasks/completed/2026/TASK_189_MATRIX_EDIT_FREEZE_AUTHORITY_SEMANTICS_CORRECTION.md`.
- `TASK_189_MATRIX_EDIT_FREEZE_AUTHORITY_SEMANTICS_CORRECTION` is complete. Matrix reviewed-edit now creates a candidate draft without superseding the current reviewed authority; supersede of previous reviewed draft happens only after candidate confirm succeeds. Confirm validation severity is corrected: method/condition/requirement/duration/source-trace/step-description gaps are warnings, while identity/token/sequence/test-item issues remain blockers.
- Validation: `python -m pytest tests\unit\test_project_test_plan_matrix_edit_service.py tests\integration\test_project_test_plan_matrix_edit_api.py tests\unit\test_matrix_step_sequence_validation.py -q` passed (12 passed); task-board guard run `python -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q` passed (17 passed).
- `TASK_189_MATRIX_AUTHORITY_READ_MODEL_AND_GROUP_IDENTITY_CORRECTION` is complete. Output ledger now treats only the latest reviewed draft as authority (`active_draft_id/version`), and draft candidates do not participate in stale comparison before confirm. Workbench model now distinguishes `matrixAuthorityDraft` and `matrixCandidateDraft` while editing prefers candidate when present. Matrix confirm now blocks missing explicit stable group identity.
- Validation: `python -m pytest tests\unit\test_project_output_record_service.py tests\unit\test_project_test_plan_matrix_edit_service.py tests\integration\test_project_test_plan_matrix_edit_api.py tests\integration\test_project_output_records_api.py -q` passed (16 passed); `npm run build` from `frontend` passed; `python -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix or task188"` passed (7 passed).
- Workbench Matrix authority target layout recorded in `docs/project_workbench_matrix_authority_workspace_target.md`.
- `TASK_190_PROJECT_WORKBENCH_MATRIX_AUTHORITY_WORKSPACE` is now accepted after controlled correction `TASK_190_MATRIX_OVERVIEW_CROSS_TABLE_AND_SUPPORTING_COMPACTNESS_CORRECTION`. Matrix overview now uses cross-table structure (technical columns + dynamic group columns + row×group token aggregation), supporting workflows default to collapsed entry points, and Matrix review surface is split into dedicated feature components (`AuthorityBar`, `Overview`, `Inspector`).
- Validation: `npm run build` from `frontend` passed; `python -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix or task190"` passed (8 passed); task-board guard run passed (`17 passed`).
- Plans: `docs/completed_plans/2026/task_190_project_workbench_matrix_authority_workspace_plan.md`, `docs/completed_plans/2026/task_190_matrix_overview_cross_table_and_supporting_compactness_correction_plan.md`.
- `TASK_191_MATRIX_DRAFT_STARTER_IMPORT_AND_MANUAL_EMPTY_STATE` is complete. Project Workbench Matrix empty state now supports two starter paths: import by `.docx` source path using Matrix preview + draft create APIs, or create a manual starter draft with explicit stable `Group 1` identity metadata. The starter workflow is rendered directly in Matrix empty state and preserves existing authority/candidate semantics after draft creation.
- Validation: `npm run build` (frontend) passed; `python -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix or task191"` passed (9 passed); `python -m pytest tests\integration\test_project_test_plan_preview_api.py tests\integration\test_project_test_plan_draft_api.py -q` passed (5 passed); task-board guard run passed (17 passed).
- Plan: `docs/completed_plans/2026/task_191_matrix_draft_starter_import_and_manual_empty_state_plan.md`.
- `TASK_192_MATRIX_SOURCE_CANDIDATES_AND_BROWSE_FALLBACK_CORRECTION` is complete. Added Project-scoped Matrix source candidate read model from project `file_assets`, candidate listing API, and candidate-preview API so Workbench starter can preview by selected source asset instead of path-first only. Matrix starter now prioritizes project source candidates, keeps external Browse/path fallback, and keeps manual Matrix as final fallback. Draft creation from preview now persists `source_asset_id` when preview came from a project candidate.
- Validation: `python -m pytest tests\unit\test_matrix_source_candidate_service.py tests\integration\test_project_test_plan_source_candidates_api.py -q` passed (5 passed); `python -m pytest tests\integration\test_project_test_plan_preview_api.py tests\integration\test_project_test_plan_draft_api.py -q` passed (5 passed); `python -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix or task191 or task192"` passed (10 passed); `npm run build` from `frontend` passed.
- Plan: `docs/completed_plans/2026/task_192_matrix_source_candidates_and_browse_fallback_correction_plan.md`.
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
- result: `docs/archive/historical_plans/phase10a_intake_entry_completion_plan.md` added, Phase 10A board section added, and `TASK_061_MSG_PACKAGE_IMPORT_API_AND_FRONTEND_ENTRY` activated
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
- result: `docs/archive/validation_summaries/phase10a_validation_summary.md` added, `docs/archive/validation_summaries/frontend_smoke_checklist.md` updated, Phase 10A marked complete
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
- result: `docs/archive/validation_summaries/phase9_validation_summary.md` added, `docs/archive/validation_summaries/frontend_smoke_checklist.md` updated, Phase 9 marked complete
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
- result: `docs/archive/validation_summaries/phase7_validation_summary.md` added with manual smoke checklist, known limitations, workbook write policy, and next recommendation
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
- `docs/archive/historical_plans/ConnLab_Phase5_Workbench_UX_Plan.md` defines the approved UX modernization direction
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
- `TASK_101_NEW_PROJECT_SINGLE_PAGE_FLOW_REDESIGN` is complete: `docs/archive/historical_plans/new_project_single_page_flow_redesign.md` defines the single-page New Project UX/data-flow design, request email and attachment behavior, editable application information editor, field-level required guidance, no-silent-replace import rule, LTR/folder completion model, draft/cancel behavior, backend orchestration boundary, and implementation split.
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

Historical completion notes were archived to reduce board size and keep active governance readable.

Archive file: `docs/archive/task_board_history_2026-05-16.md`

Legacy notes retained in archive include prior completed-note chains and old next-step recommendations.
