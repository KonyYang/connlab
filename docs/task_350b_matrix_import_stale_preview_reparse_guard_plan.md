# TASK_350B Matrix Import Stale Preview Reparse Guard Plan

Status: complete - Integrator accepted
Task: `TASK_350B_MATRIX_IMPORT_STALE_PREVIEW_REPARSE_GUARD`
Lane: `matrix-import-stale-preview-reparse-guard`
Created: 2026-07-04

## 1. Discovery Gate

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current active task/lane: `TASK_350B_MATRIX_IMPORT_STALE_PREVIEW_REPARSE_GUARD` / `matrix-import-stale-preview-reparse-guard`, Planner requirement update / formal planned lane correction only.

Current role: ConnLab Planner.

Why allowed: Orchestrator routed a new Planner Discovery / lane creation request after TASK_350A was accepted, and explicitly prohibited product-code changes or Developer routing.

## 2. User Goal

In the Matrix Editor Import Matrix modal, changing Page, Table on page, or Table Title / Content Keyword after a successful parse must not allow `Replace` to commit the old preview. The UI should still let the operator click `Replace`: if the preview is stale, `Replace` first auto-runs Reparse with the current locator fields. If that auto-Reparse finds a usable Matrix preview, the UI updates the preview snapshot and continues the original Replace/commit. If auto-Reparse fails or finds no usable Matrix, the modal shows the result/error and does not commit.

## 3. Evidence Read

- `AGENTS.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/impeccable/SKILL.md`
- `$impeccable` product context from `PRODUCT.md` / `DESIGN.md`
- `docs/task_board.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/frontend_architecture_rules.md`
- `docs/02_ARCHITECTURE_RULES.md`
- TASK_350A board/evidence context
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- Current `git status --short`

## 4. Confirmed By User

- The observed issue is in the Matrix Editor Import Matrix modal.
- The stale-risk fields are Page, Table on page, and Table Title / Content Keyword.
- The desired model is `lastParsedLocator: { page, tableOnPage, keyword }`.
- File auto-parse success and Reparse success should update the snapshot.
- Any locator mismatch should make the preview stale.
- Updated requirement after initial Reviewer plan pass: `Replace` must not be disabled merely because the preview is stale.
- `Replace` clicked while stale must auto-Reparse using the current Page / Table on page / Keyword before any commit.
- Auto-Reparse success with usable Matrix groups should update `importPreview`, update `lastParsedLocator`, then continue the original Replace/commit.
- Auto-Reparse not found, failure, invalid input, or page/table mismatch should keep the dialog open, show an in-dialog error/result, and not commit.
- Manual Reparse remains an explicit preview refresh entry.
- Non-stale Replace should not reparse; it commits the current non-stale preview.
- Scope should be frontend MatrixEditorWorkspace and focused tests only.

## 5. Confirmed By Repository Evidence

- `docs/task_board.md` records TASK_350A as complete/accepted and notes MatrixEditorWorkspace was packaged only for accepted `.docx` to `.doc,.docx` input behavior.
- `MatrixEditorWorkspace.tsx` currently has `locatorPage`, `locatorTableOnPage`, `locatorKeyword`, `importPreview`, `importingPreview`, and `committingImport` state.
- Initial file preview success sets `importPreview`, `importPreviewPdfToken`, and locator fields, then opens the dialog.
- `reparseImportPreview` validates positive integer Page / Table on page values and sends the current locator values to `previewProjectTestPlanMatrixFromUpload`.
- `Replace` is currently disabled by `isLifecycleReadonly || importingPreview || !importPreview || importPreview.groups.length === 0`.
- Locator inputs are currently disabled only by `isLifecycleReadonly`.
- The focused test file already covers Import Matrix, Replace, Append disabled, and `.doc,.docx` accept behavior.
- Current `git status --short` shows external release/settings residuals but no modified MatrixEditorWorkspace file at this planning point.

## 6. Planner Inferences

- This should be a formal lightweight frontend follow-up lane, not a quick fix, because it protects Matrix import commit correctness.
- No backend/API/client/parser changes are needed.
- The implementation can be localized to MatrixEditorWorkspace state and tests.
- A concise in-dialog stale/error message may be useful, but the hard acceptance criterion is that stale Replace performs auto-Reparse before commit and never commits an old preview. Any copy should stay operational and short.

## 7. Not Yet Confirmed

None blocking for a planned lane. Browser smoke availability can be handled as QA/manual residual.

## 8. Definition Of Ready

DoR is satisfied for a planned lane and Reviewer plan gate:

- User scenario is clear.
- Current behavior has been checked in code.
- Scope is narrow and testable.
- May Touch / Must Not Touch / Locked Paths are concrete.
- Acceptance criteria are explicit.
- No unresolved backend/API/data model question affects the lane.

This is not an implementation approval.

## 9. Implementation Design Recommendation

Add a local locator snapshot type:

```ts
type ImportLocatorSnapshot = {
  page: string;
  tableOnPage: string;
  keyword: string;
};
```

Normalize comparison by trimming all three fields. Use the same string values the UI owns, not parsed integers, so stale detection tracks what the operator sees.

State and derived values:

- `const [lastParsedLocator, setLastParsedLocator] = useState<ImportLocatorSnapshot | null>(null);`
- `const currentLocator = { page: locatorPage.trim(), tableOnPage: locatorTableOnPage.trim(), keyword: locatorKeyword.trim() };`
- `const isPreviewStale = Boolean(importPreview && lastParsedLocator && (currentLocator.page !== lastParsedLocator.page || currentLocator.tableOnPage !== lastParsedLocator.tableOnPage || currentLocator.keyword !== lastParsedLocator.keyword));`

Snapshot updates:

- On new file selection before preview: reset `lastParsedLocator` to `null`.
- On initial preview success after locator fields are set from preview metadata: set `lastParsedLocator` to the same displayed values.
- On Reparse success after validation and mismatch checks: set `lastParsedLocator` to the current trimmed locator values.
- On manual or auto-Reparse failure / validation failure: keep the dialog open, keep or mark the current preview as stale, show the existing in-dialog error/lookup state, and do not commit.

Disable and busy behavior:

- Replace disabled if `isLifecycleReadonly || importingPreview || committingImport || !importPreview || importPreview.groups.length === 0`.
- Do not include `isPreviewStale` in the disabled predicate by itself; stale Replace is the auto-Reparse entry.
- Locator inputs disabled if `isLifecycleReadonly || importingPreview || committingImport`.
- Reparse disabled if `isLifecycleReadonly || importingPreview || committingImport || !importFile`.
- Append remains disabled and should also respect busy state.

Commit behavior:

- `applyImportedMatrixDirectly` should branch on `isPreviewStale`.
- If not stale, it should call `commitMatrixImport` with the current `importPreview` and must not call preview/reparse again.
- If stale, it should run the same validation and preview request used by Reparse with the current locator fields.
- If stale auto-Reparse succeeds and returns usable Matrix groups, update `importPreview`, update `lastParsedLocator`, then call `commitMatrixImport` with the refreshed preview.
- If stale auto-Reparse fails, returns no usable Matrix groups, or hits invalid Page/Table / page-table mismatch, show the existing in-dialog error or lookup message and do not call `commitMatrixImport`.
- During manual Reparse, auto-Reparse, and commit, disable inputs and relevant action buttons to prevent concurrent requests or double-submit.

## 10. May Touch

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `tasks/TASK_350B_MATRIX_IMPORT_STALE_PREVIEW_REPARSE_GUARD.md`
- `docs/task_350b_matrix_import_stale_preview_reparse_guard_plan.md`
- `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_*.md`
- `docs/task_board.md` through normal lane flow.

## 11. Must Not Touch

- `backend/**`
- `frontend/src/api/client.ts`
- Matrix parser rules.
- Backend preview service and routes.
- Confirmed Matrix authority, Fee Evaluation, Test Record generation, lifecycle semantics.
- TASK_350A `.doc` conversion backend flow.
- Folder Actions / public folder workflow.
- Intake / LTR workflow.
- Projects registry/list.
- Release/settings cleanup and unrelated residuals.
- `.agents/**`
- `docs/project_management/**`

## 12. Locked Paths

- `backend/**`
- `frontend/src/api/client.ts`
- `backend/modules/test_plan/product_spec_matrix_parser.py`
- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/api/routes_project_test_plan.py`
- `frontend/src/features/new-project/**`
- `frontend/src/features/project-workbench/**`
- `frontend/src/pages/ProjectListPage.tsx`
- `.agents/**`
- `docs/project_management/**`

## 13. Acceptance Criteria

- Initial auto-preview success records the locator snapshot displayed in the dialog.
- Reparse success records the current locator snapshot.
- Editing any locator field after preview success marks preview stale.
- Replace remains clickable when stale if the existing preview has Matrix groups and no readonly/busy blocker applies.
- Stale Replace calls the preview/Reparse path with the current locator fields before commit.
- Stale Replace auto-Reparse success with usable Matrix groups updates `importPreview`, updates `lastParsedLocator`, then commits the refreshed preview.
- Stale Replace auto-Reparse failure, invalid Page/Table, page-table mismatch, or no usable Matrix groups keeps the modal open, shows existing in-dialog error/lookup state, and does not call commit.
- Non-stale Replace does not call `previewProjectTestPlanMatrixFromUpload`; it commits only the existing non-stale `importPreview`.
- Replace is disabled while manual Reparse, auto-Reparse, or commit is running.
- Locator fields and Reparse are disabled while manual Reparse, auto-Reparse, or commit is running.
- Manual Reparse remains available as an explicit preview refresh path.
- Existing Reparse validation for positive Page / Table on page and page/table mismatch remains intact.

## 14. Validation Plan

Focused frontend tests:

- After import preview success, editing Page marks preview stale; clicking Replace auto-Reparses, then commits only after successful refreshed preview with groups.
- Editing Table on page marks preview stale; clicking Replace auto-Reparses, then commits only after successful refreshed preview with groups.
- Editing Table Title / Content Keyword marks preview stale; clicking Replace auto-Reparses, then commits only after successful refreshed preview with groups.
- Stale Replace auto-Reparse failure displays error/lookup message and does not call `commitMatrixImport`.
- Invalid Page / Table on page during stale Replace displays validation feedback and does not call preview commit.
- Existing positive manual Reparse path updates snapshot and preview.
- Manual Reparse failure displays error/lookup message and does not call `commitMatrixImport`.
- Reparse/committing state disables locator inputs, Reparse, Replace, and Append.
- Existing Replace direct commit test still passes when snapshot is current and proves no extra preview call happens.
- Existing `.doc,.docx` accept test remains green.

Suggested commands:

- `npm test -- MatrixEditorWorkspace --run`
- `npm run build`
- `git diff --check` on TASK_350B package files
- trailing whitespace scan on TASK_350B package files
- forbidden-scope status proving no backend/API/client/parser/Workbench/Projects/Intake-LTR/release/governance changes

Manual smoke:

- Browser smoke at the reported Matrix Editor route if local data/server are available: edit locator fields, click Replace, confirm the modal auto-Reparses before commit; verify success continues to Replace and failure/no-match stays in the modal without committing.

## 15. Source / Package Isolation Risks

- `MatrixEditorWorkspace.tsx` is a large file and has frequent lane history; Developer must isolate only stale-preview/reparse-guard hunks.
- Current status shows release/settings residuals outside this lane. They must remain excluded.
- If Developer finds MatrixEditorWorkspace dirty before implementation, stop and record package-isolation risk before editing.

## 16. Blockers

None for planned lane correction. Because the requirement changed after the first Reviewer plan gate, the next legal role is Reviewer plan re-gate before any Developer planning-first routing.

## 17. Developer Planning-First Addendum

Date: 2026-07-05

Developer planning-first authorization:

- Orchestrator delegated Developer planning-first after Reviewer plan re-gate pass and user approval.
- Local `docs/task_board.md`, TASK_350B task file, plan header before this addendum, and Planner evidence still record TASK_350B as planned / ready for Reviewer plan re-gate only.
- Product implementation must wait for Reviewer implementation-readiness, user implementation approval, and source-of-truth reconciliation.
- This pass updates only TASK_350B plan/evidence docs.

### Current Code Confirmation

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` is clean in the current TASK_350B planning context and retains the accepted TASK_350A `accept=".doc,.docx"` input behavior.
- Current import state includes `importPreview`, `importPreviewPdfToken`, `importingPreview`, `importError`, `importLookupMessage`, `importLookupTone`, `showImportDialog`, `committingImport`, `importFile`, `locatorPage`, `locatorTableOnPage`, and `locatorKeyword`.
- `onImportFileChange` sets locator fields from the initial preview response and opens the import dialog.
- `reparseImportPreview` already validates positive integer Page / Table on page values, sends current locator values to `previewProjectTestPlanMatrixFromUpload`, handles page/table mismatch, updates `importPreview`, and shows in-dialog lookup messages.
- `applyImportedMatrixDirectly` currently commits the existing `importPreview` directly and has no stale-locator guard.
- The Replace button is currently disabled by `isLifecycleReadonly || importingPreview || !importPreview || importPreview.groups.length === 0`; it does not include `committingImport` and does not distinguish stale preview state.
- Locator inputs are currently disabled only by `isLifecycleReadonly`.
- Focused tests already mock `previewProjectTestPlanMatrixFromUpload` and `commitMatrixImport`, cover the import selector accept value, Append disabled behavior, and direct Replace commit behavior.

### Exact Future Implementation File List

Future implementation May Touch:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_developer.md`

Docs/board via normal lane flow only after later gates:

- `docs/task_350b_matrix_import_stale_preview_reparse_guard_plan.md`
- `tasks/TASK_350B_MATRIX_IMPORT_STALE_PREVIEW_REPARSE_GUARD.md`
- `docs/task_board.md`

Locked:

- `backend/**`
- `frontend/src/api/client.ts`
- `backend/api/routes_project_test_plan.py`
- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/modules/test_plan/product_spec_matrix_parser.py`
- TASK_350A `.doc` conversion backend flow
- Confirmed Matrix, Fee Evaluation, Test Record, lifecycle, Workbench, Projects registry/list, Intake/LTR, Folder Actions, release/settings cleanup, `.agents/**`, and `docs/project_management/**`

### State Machine And Helper Plan

Add local UI-only helper state:

```ts
type ImportLocatorSnapshot = {
  page: string;
  tableOnPage: string;
  keyword: string;
};

const [lastParsedLocator, setLastParsedLocator] = useState<ImportLocatorSnapshot | null>(null);
```

Add helper functions inside `MatrixEditorWorkspace`:

- `buildCurrentImportLocatorSnapshot()`: returns trimmed `locatorPage`, `locatorTableOnPage`, and `locatorKeyword`.
- `buildPreviewLocatorSnapshot(preview)`: returns the displayed initial locator after a preview succeeds, using `selected_page_number`, `selected_page_table_index`, and empty keyword for the initial parse path.
- `isImportPreviewStale`: true when `importPreview` and `lastParsedLocator` exist and the current trimmed locator differs from the snapshot.
- `validateImportLocatorInputs()`: shared by manual Reparse and stale Replace. It should preserve existing positive-integer validation copy and set the current in-dialog error/lookup state.
- `requestImportPreviewForCurrentLocator()`: shared by manual Reparse and stale Replace. It should call `previewProjectTestPlanMatrixFromUpload(importFile, projectId, { pageNumber, pageTableIndex, tableTextQuery })`, update PDF token when returned, reject page/table mismatch with the current in-dialog error behavior, and return the preview or `null`.

State transitions:

- New file chosen:
  - set `lastParsedLocator(null)`;
  - clear previous import error/status;
  - run initial preview;
  - on success set locator display fields from preview and set `lastParsedLocator(buildPreviewLocatorSnapshot(preview))`.
- Manual Reparse:
  - validate current locator;
  - set `importingPreview(true)`;
  - clear current preview while requesting, preserving existing behavior;
  - on success with matching locator, set `importPreview(preview)` and `lastParsedLocator(buildCurrentImportLocatorSnapshot())`;
  - on invalid input, mismatch, no groups, or request failure, keep dialog open, show in-dialog status/error, do not commit.
- Non-stale Replace:
  - commit current `importPreview` directly;
  - do not call `previewProjectTestPlanMatrixFromUpload`.
- Stale Replace:
  - keep Replace clickable while stale when a usable preview exists and no readonly/busy blocker applies;
  - validate current locator;
  - run the same preview request as manual Reparse;
  - if success with usable Matrix groups, set `importPreview(refreshedPreview)`, set `lastParsedLocator(currentSnapshot)`, then call `commitMatrixImport` with the refreshed preview;
  - if invalid, failure, mismatch, or no usable groups, show in-dialog error/status and do not call `commitMatrixImport`.

Busy behavior:

- Introduce a derived busy guard such as `const importActionBusy = importingPreview || committingImport`.
- Disable locator inputs when `isLifecycleReadonly || importActionBusy`.
- Disable Reparse when `isLifecycleReadonly || importActionBusy || !importFile`.
- Disable Replace when `isLifecycleReadonly || importActionBusy || !importPreview || importPreview.groups.length === 0`.
- Keep Append disabled, and during busy state its disabled state remains true.

### UX And Copy Constraints

- Do not add long explanatory modal copy.
- Keep errors and lookup messages inside the existing import dialog.
- Use concise operational messages already present where possible:
  - `Page must be a positive integer.`
  - `Table on page must be a positive integer.`
  - `No matching matrix found at requested page/table. Reparse or edit manually.`
  - `No matching matrix found. Adjust page/table and reparse.`
- No backend tokens, parser terms, raw stack errors, decorative color, gradient text, glassmorphism, thick side stripes, or nested cards.

### Package Isolation Plan

- Start implementation from the current clean `MatrixEditorWorkspace.tsx` baseline.
- Keep TASK_350B product diff limited to `ImportLocatorSnapshot`, local helper functions, import modal busy/disabled predicates, and focused tests.
- Do not reintroduce any TASK_350A backend conversion changes or unrelated Matrix parser / commit-flow refactors.
- If `MatrixEditorWorkspace.tsx` becomes dirty with external residuals before implementation, stop and request package/scope reconciliation rather than silently mixing hunks.

### Focused Test Plan

Add or update tests in `MatrixEditorWorkspace.test.tsx`:

- `stale Replace auto-reparses with current locator and commits refreshed preview`
  - initial import preview returns `source_document_name: "spec.docx"` and group `g1`;
  - edit Page or Table on page;
  - click Replace;
  - assert `previewProjectTestPlanMatrixFromUpload` is called again with the edited locator;
  - assert `commitMatrixImport` receives the refreshed preview, not the old preview.
- `stale Replace auto-reparse failure does not commit and shows in-dialog error`
  - edit Keyword after preview;
  - second preview rejects;
  - assert `commitMatrixImport` is not called and dialog shows the error/lookup state.
- `stale Replace invalid Page or Table does not preview or commit`
  - edit Page to an invalid value;
  - click Replace;
  - assert no second preview call and no commit.
- `non-stale Replace commits current preview without reparse`
  - keep current direct Replace test and assert preview is called only once.
- `manual Reparse updates snapshot so later Replace commits directly`
  - edit locator, click Reparse, return refreshed preview, click Replace;
  - assert no additional preview call on Replace.
- `busy state disables locator inputs and import actions`
  - hold manual Reparse or stale Replace promise pending;
  - assert Page, Table on page, Keyword, Reparse, and Replace are disabled; Append remains disabled.
- Existing tests that must remain green:
  - `.doc,.docx` accept selector;
  - Append disabled;
  - direct Replace no group-selection mode;
  - existing MatrixEditorWorkspace flow tests.

### Validation Plan

Future implementation validation:

- `npm test -- MatrixEditorWorkspace --run`
- `npm run build`
- `git diff --check -- frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_developer.md`
- trailing whitespace scan on TASK_350B package files
- scope scan proving no backend/API client/parser/preview service/Workbench/Projects/Intake-LTR/release/governance changes
- candidate diff scan confirming no TASK_350A backend conversion hunk is included
- browser smoke if safe local data/server are available: import Matrix, edit locator, click Replace, verify auto-Reparse before commit; record tooling/data blocker if unavailable.

### Developer Planning-First Validation

This planning-first pass must validate:

- required TASK_350B task/plan/planner evidence files exist;
- Developer evidence exists;
- `git diff --check` on TASK_350B plan/developer evidence passes;
- trailing whitespace scan on TASK_350B plan/developer evidence returns no matches;
- targeted status shows no frontend/backend/tests/API-client product code changed by this planning-first pass.

## 18. Planner Source-Of-Truth Reconciliation

Date: 2026-07-05

Reconciliation facts:

- Reviewer plan re-gate passed after the user requirement update changed stale Replace from disabled-only behavior to auto-Reparse-before-commit behavior.
- User approved TASK_350B for Developer planning-first.
- Developer planning-first completed and recorded evidence in `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_developer.md`.
- Reviewer implementation-readiness passed.
- User approved TASK_350B source-of-truth reconciliation and Developer implementation.

Implementation authorization:

- TASK_350B is now implementation authorized / pending Developer implementation.
- This is not completion and does not bypass Reviewer implementation gate, QA gate, or Integrator packaging.
- The updated behavior contract remains: stale `Replace` auto-runs Reparse with current locator; success with usable Matrix groups updates preview/snapshot then commits; failure, invalid input, page-table mismatch, or no usable Matrix shows the in-dialog result/error and does not commit; manual Reparse remains; non-stale Replace commits directly without another preview call.

Authorized future implementation May Touch:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_developer.md`

Scope locks remain:

- No `backend/**`.
- No `frontend/src/api/client.ts`.
- No Matrix parser, backend preview service, or preview route changes.
- No TASK_350A `.doc` conversion backend flow changes.
- No Confirmed Matrix, Fee Evaluation, Test Record generation, lifecycle semantics, Folder Actions / public folder workflow, Intake / LTR workflow, Projects registry/list, release/settings cleanup, `.agents/**`, or `docs/project_management/**`.

Next legal role: Developer implementation pass.

## 19. Integrator Closeout

Date: 2026-07-05

Outcome:

- Integrator gate: accepted.
- Reviewer implementation gate: pass.
- QA gate: pass.
- Package readiness validated with focused MatrixEditorWorkspace tests (`35 passed`), frontend build, staged diff check, staged whitelist/forbidden-path checks, trailing whitespace scan, and static scope scans.
- The accepted package is frontend-only and limited to Matrix import stale-preview snapshot / auto-Reparse behavior, focused tests, TASK_350B docs/evidence, and `docs/task_board.md` closeout.
- No backend/API client/parser/preview route/service changes, no TASK_350A `.doc` conversion backend changes, no Confirmed Matrix/Fee/Test Record/lifecycle semantic changes, no Folder Actions/Intake LTR/Projects scope, no release/settings cleanup, no `.agents/**`, and no `docs/project_management/**` were packaged.
- Browser smoke remains a non-blocking QA residual because QA lacked direct browser control and a prepared disposable Matrix import fixture; focused tests and source/static checks cover stale detection, auto-Reparse success/failure, invalid locator, manual Reparse, non-stale direct commit, and busy disabled behavior.
- Remote push was intentionally not performed.
