# TASK_350B QA Evidence - Matrix Import Stale Preview Reparse Guard

Date: 2026-07-05

Role: QA / Smoke Owner

Task: `TASK_350B_MATRIX_IMPORT_STALE_PREVIEW_REPARSE_GUARD`

Lane: `matrix-import-stale-preview-reparse-guard`

Result: `qa_pass`

---

## 1. Gate And Role Boundary

- Current phase from `docs/task_board.md`: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Orchestrator delegation states Reviewer implementation gate passed and QA gate is required.
- Local `docs/task_board.md` still records TASK_350B as implementation authorized / pending Developer implementation; QA records this as a board timing mismatch against the newer Orchestrator delegation and did not update the board.
- QA performed validation and evidence only.
- QA did not modify product source, tests, backend/API/client/parser code, `docs/task_board.md`, release/settings/desktop residuals, or real user data.
- QA did not stage, commit, push, package, or run destructive cleanup.

## 2. Sources Read

- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/task_board.md`
- `tasks/TASK_350B_MATRIX_IMPORT_STALE_PREVIEW_REPARSE_GUARD.md`
- `docs/task_350b_matrix_import_stale_preview_reparse_guard_plan.md`
- `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_planner.md`
- `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_developer.md`
- `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_reconciliation_planner.md`
- Actual diff/status for TASK_350B candidate files and external residuals.

## 3. Candidate Package / Scope Check

TASK_350B candidate product files observed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

Developer evidence observed:

- `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_developer.md`

External residuals still visible and excluded:

- `frontend/src/features/new-project/LocalLtrDuplicateConflictPanel.test.tsx`
- `frontend/src/features/new-project/LocalLtrDuplicateConflictPanel.tsx`
- `frontend/src/features/new-project/NewProjectCompletionDock.tsx`
- Settings/LTR backend residuals under `backend/api/routes_settings.py` and `backend/application/ltr_workbook_*`
- desktop/release/packaging residuals, `dist_release/`, and `temp_agents_stash.md`

Observed TASK_350B behavior from source diff:

- Adds `ImportLocatorSnapshot` and `lastParsedLocator`.
- Records locator snapshot after initial import preview success.
- Records current locator snapshot after manual Reparse success.
- Computes stale state by comparing current Page / Table on page / Keyword against `lastParsedLocator`.
- Non-stale Replace calls commit directly.
- Stale Replace validates current locator, runs the existing preview/Reparse path with current locator inputs, updates `importPreview` and `lastParsedLocator` only on usable success, then commits refreshed preview.
- Stale Replace validation failure, preview failure, page/table mismatch, blockers, or no groups leaves the dialog open and does not commit.
- `importActionBusy = importingPreview || committingImport` disables file input, locator inputs, Reparse, Cancel, Replace, and preserves Append disabled behavior during busy state.

## 4. Focused Frontend Tests

Command:

```powershell
cd frontend
npm test -- MatrixEditorWorkspace --run
```

Observed result:

- Passed.
- `1` test file passed.
- `35` tests passed.

Coverage confirmed by test names/source:

- Stale Replace auto-Reparses with current locator before committing.
- Stale Replace failure keeps the dialog open and does not commit.
- Invalid stale locator does not reparse or commit and shows validation copy.
- Manual Reparse refreshes locator snapshot before direct Replace.
- Busy stale Replace disables locator inputs and import actions.
- Existing `.doc,.docx` accept and MatrixEditorWorkspace regression coverage remain green.

## 5. Build

Command:

```powershell
cd frontend
npm run build
```

Observed result:

- Passed.
- Existing Vite chunk-size warning only.

## 6. Static Checks

Candidate diff check:

```powershell
git diff --check -- frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_developer.md docs/task_350b_matrix_import_stale_preview_reparse_guard_plan.md tasks/TASK_350B_MATRIX_IMPORT_STALE_PREVIEW_REPARSE_GUARD.md docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_planner.md docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_reconciliation_planner.md
```

Observed result:

- Passed with LF/CRLF warnings only.

Trailing whitespace scan:

```powershell
Select-String -Path <TASK_350B candidate files/docs> -Pattern '[ \t]+$' -Encoding UTF8
```

Observed result:

- No matches.

Locked-path/status scan:

```powershell
git status --short -- backend frontend/src/api/client.ts backend/modules/test_plan/product_spec_matrix_parser.py backend/application/project_test_plan_matrix_preview_service.py backend/api/routes_project_test_plan.py frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx frontend/src/features/new-project frontend/src/features/project-workbench frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx .agents docs/project_management dist_release packaging temp_agents_stash.md
```

Observed result:

- TASK_350B candidate files appeared under MatrixEditorWorkspace only.
- No TASK_350B backend, API client, parser, backend preview route/service, TASK_350A conversion, Project Workbench, Projects registry/list, `.agents/**`, or `docs/project_management/**` implementation changes appeared.
- New Project, Settings/LTR, desktop/release/packaging, and temp-stash residuals remain visible and excluded.

Targeted source/test scan:

```powershell
Select-String -Path frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx,frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx -Pattern 'lastParsedLocator|ImportLocatorSnapshot|currentImportLocatorSnapshot|importLocatorSnapshotsMatch|manual Reparse|No matching matrix found|Page must be a positive integer|Table on page must be a positive integer|importActionBusy|commitMatrixImport|previewProjectTestPlanMatrixFromUpload' -Encoding UTF8
```

Observed result:

- Positive TASK_350B hooks and coverage appeared in source/tests.
- No blocking forbidden-scope match was identified in TASK_350B candidate diff.

## 7. Browser Smoke

Browser smoke was not executed.

Environment/tooling observations:

- `http://localhost:5173` responded with status `200`.
- Direct in-app browser control was not exposed in the available tools for this QA thread; tool search exposed node REPL and unrelated plugin tools, not the browser controller.
- A real Matrix import modal smoke also requires a safe project route and disposable Matrix import fixture. QA did not upload real user documents or create unrelated fixture data in this gate.

Disposition:

- Non-blocking residual for TASK_350B because focused component tests and source checks cover stale detection, stale Replace auto-Reparse success/failure, invalid locator, manual Reparse, non-stale direct commit, and busy disabled behavior.
- Future manual smoke can use a disposable Matrix import fixture and a known local project route to edit Page/Table/Keyword and verify Replace auto-Reparses before commit.

## 8. QA Decision

QA gate: pass.

Blocking findings: none.

Residual risks:

- Browser smoke remains unexecuted due missing direct browser control and no prepared safe Matrix import fixture in this QA thread.
- External New Project, Settings/LTR, desktop/release/packaging, and temp-stash residuals remain dirty and must not be packaged with TASK_350B.

Recommended next role:

- Integrator packaging/readiness.

Integrator instruction:

- Stage/package only TASK_350B candidate MatrixEditorWorkspace files/hunks and TASK_350B evidence/docs intended by the lane.
- Exclude backend/API client/parser/preview route/service/TASK_350A conversion files and all external Settings/LTR, New Project, desktop/release/packaging, and temp-stash residuals.
