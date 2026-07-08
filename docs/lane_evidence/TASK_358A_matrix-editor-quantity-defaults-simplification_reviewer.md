# TASK_358A Matrix Editor Quantity Defaults Simplification Reviewer Evidence

Status: reviewer_pass
Task: `TASK_358A_MATRIX_EDITOR_QUANTITY_DEFAULTS_SIMPLIFICATION`
Lane: `matrix-editor-quantity-defaults-simplification`
Date: 2026-07-09
Role: Reviewer

## Gate

Reviewer plan gate only. No product implementation, QA, packaging, commit, Developer routing, or product-code edits were performed.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/impeccable` product context via `node .agents/skills/impeccable/scripts/load-context.mjs`
- `PRODUCT.md`
- `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_358A_MATRIX_EDITOR_QUANTITY_DEFAULTS_SIMPLIFICATION.md`
- `docs/task_358a_matrix_editor_quantity_defaults_simplification_plan.md`
- `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_planner.md`
- TASK_357A-E evidence/context as needed, including Matrix quantity authority, Basic Information defaults, Matrix Step quantity setup, Fee passive consumption, and Test Record reuse context.
- Current Basic Information quantity defaults code/tests:
  - `frontend/src/features/project-basic-information/basicInformationFieldConfig.ts`
  - `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx`
  - `backend/application/project_basic_information_service.py`
- Current Matrix Step quantity setup code:
  - `frontend/src/features/matrix-editor/MatrixStepQuantityPanel.tsx`
  - `frontend/src/features/matrix-editor/matrixStepQuantitySelectors.ts`
  - `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
  - `backend/application/matrix_step_quantity_service.py`

## Findings

No blocking findings.

The board allows `TASK_358A_MATRIX_EDITOR_QUANTITY_DEFAULTS_SIMPLIFICATION` as the current planned lane for Reviewer plan gate. The task, plan, and Planner evidence all keep implementation unauthorized and restrict this pass to corrective planning.

The plan correctly reflects the latest user-confirmed product direction:

- Basic Information should no longer expose a `Quantity defaults` project-level entry.
- Existing Basic Information quantity data remains compatibility data; the plan does not authorize schema deletion, destructive migration, or persisted-value removal.
- Matrix Editor becomes the operator-facing place for quantity defaults near the bottom controls or Step setup surface.
- Matrix Step rows remain final per-step authority after operator review/save/confirmation.
- Fee Evaluation, Test Record, and Report-derived outputs remain passive consumers of confirmed Matrix Step quantities.

Repository facts support the corrective lane:

- Basic Information currently exposes a `Quantity defaults` group with `test_points_per_sample`, `readings_per_point`, and `contact_points_per_sample`.
- Basic Information backend validation currently recognizes these quantity default values.
- Matrix Step quantity service currently falls back to latest confirmed/draft Basic Information values when no persisted Step quantity exists.
- Matrix Editor already has a Step quantity setup panel and save flow that can host the corrected default-entry affordance without making Basic Information the UI authority.

The data-compatibility policy is safe for a planning gate. The plan explicitly avoids deleting existing values or schema and treats old BI values as compatibility/historical fallback only. Developer planning-first should later decide the exact compatibility read behavior, but must not revive Basic Information as the visible default-entry surface or silently overwrite Matrix Step quantities.

May Touch / Must Not Touch / Locked Paths are adequate for this corrective lane:

- May Touch is focused on Basic Information quantity UI removal/tests, Matrix Editor Step quantity default-entry UI/selectors/service/API/tests, API client only if the existing DTO/helper path requires it, and TASK_358A evidence/docs.
- Must Not Touch correctly locks schema/data deletion, destructive migration, Fee/Test Record/Report semantic changes, StepInstance/execution persistence, Matrix parser/import, LTR/public-drive authority, real folders/workbooks, release/settings cleanup, `.agents/**`, and `docs/project_management/**`.

The planned validation gate is reviewable:

- Basic Information no longer renders the quantity-default entry.
- Existing persisted BI quantity values do not break reads/confirm/history.
- Matrix Editor exposes a compact default-entry affordance.
- Applying defaults fills intended blank Step quantity rows and does not silently overwrite reviewed Step values.
- Per-Step edit/save/final authority behavior remains intact.
- Fee/Test Record/Report regressions confirm passive consumption semantics are unchanged.
- Build, focused tests, static/scope scans, and browser smoke are listed.

## Validation

- `git diff --check -- docs/task_board.md tasks/TASK_358A_MATRIX_EDITOR_QUANTITY_DEFAULTS_SIMPLIFICATION.md docs/task_358a_matrix_editor_quantity_defaults_simplification_plan.md docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_planner.md` passed with only the existing `docs/task_board.md` LF/CRLF warning.
- Trailing whitespace scan on TASK_358A docs/board/planner evidence returned no matches.
- `git status --short` shows TASK_358A docs/board/evidence plus unrelated external residuals. No TASK_358A product implementation files are authorized or treated as package scope.

## Decision

`reviewer_pass`.

Recommended next role/action: User approval / Developer planning-first. Do not route Developer implementation from TASK_358A.

Blocking summary: none.

---

## Implementation-Readiness Gate

Date: 2026-07-09
Status: reviewer_readiness_pass

Reviewed Developer planning-first evidence:

- `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_developer.md`
- updated `docs/task_358a_matrix_editor_quantity_defaults_simplification_plan.md`

No blocking findings.

Developer planning-first is docs-only. Targeted status over the TASK_358A plan/evidence plus future product May Touch and locked governance paths shows only:

- `docs/task_358a_matrix_editor_quantity_defaults_simplification_plan.md`
- `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_developer.md`
- this Reviewer evidence file

No Basic Information, Matrix Editor, API client, backend Matrix Step quantity, `.agents/**`, or `docs/project_management/**` product/governance files were changed by the Developer planning-first pass. Existing external residuals remain visible in the worktree and are excluded from TASK_358A.

The implementation strategy is concrete enough for future implementation after User approval and source-of-truth reconciliation:

- Basic Information removal is scoped to removing the config-driven `Quantity defaults` UI group and updating focused Basic Information tests/copy.
- Backend/data compatibility is preserved: no schema deletion, no destructive migration, and existing Basic Information values-map records with quantity keys remain readable/harmless.
- Matrix Editor gets a compact inline default strip inside `MatrixStepQuantityPanel`, not a modal, new navigation surface, or extra card stack.
- V1 Matrix Editor defaults are transient UI state, not a new persisted default authority or competing source of truth.
- `Apply to blank Step quantities` is blank-only by default and must not silently overwrite non-blank Step values, saved overrides, carry-forward values, or review values.
- Persistence remains the existing Matrix Step quantity save flow; confirmed Matrix Step quantities remain the final downstream authority.
- `total_readings` remains derived/read-only.
- Fee/Test Record/Report behavior remains unchanged except for regression verification.
- `frontend/src/api/client.ts` is avoided unless a later implementation proves a typed API contract change is unavoidable.

The UX plan matches ConnLab `$impeccable` product constraints: dense, restrained, operational, standard inputs, one quiet action, no long copy, no modal-first design, no nested card, no side-stripe accent, no gradient text, and no glassmorphism.

Locked scope remains intact for readiness:

- no schema/data deletion or destructive migration;
- no Fee default-fill behavior change;
- no Test Record/Report consumer behavior change;
- no StepInstance/execution persistence;
- no Matrix parser/import changes;
- no LTR/public-drive/real workbook/folder behavior;
- no release/settings/template residual cleanup;
- no `.agents/**` or `docs/project_management/**`.

Validation plan is adequate:

- focused Basic Information and Matrix Editor frontend tests;
- focused Matrix Step quantity backend/API tests only if backend source policy changes;
- TASK_357D/TASK_357E regressions if backend/default-source behavior changes;
- `npm run build`;
- diff/trailing whitespace checks;
- Python line-count scan if backend is touched;
- forbidden-scope scans for locked paths and real folder/workbook mutations;
- browser smoke for Matrix Editor when tooling/data is available.

Source-of-truth caveat: `docs/task_board.md` and the task file still show TASK_358A as planned / ready for Reviewer plan gate only. That does not block this readiness review, but it does block direct product implementation authorization. Before any Developer implementation pass, User approval plus Planner/Integrator source-of-truth reconciliation is required.

Readiness decision: `reviewer_readiness_pass`.

Recommended next role/action: User approval + Planner/Integrator source-of-truth reconciliation before Developer implementation.

Blocking summary: none.

---

## Implementation Gate

Date: 2026-07-09
Status: reviewer_implementation_pass

Reviewed Developer implementation evidence:

- `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_developer.md`
- `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_reconciliation_planner.md`
- actual frontend/CSS/test diffs for TASK_358A candidate files

No blocking findings.

The implementation stays within the approved TASK_358A UI simplification scope:

- Removed the Basic Information `Quantity defaults` group from `basicInformationFieldConfig.ts`.
- Removed Basic Information frontend quantity-default validation/status blocking from `ProjectBasicInformationWorkspace.tsx`.
- Updated Basic Information tests so hidden historical quantity values no longer render or block Confirm.
- Added a compact inline `Defaults for this group` strip inside `MatrixStepQuantityPanel`.
- Added transient Matrix Editor defaults and `Apply to blank Step quantities`.
- Added selector logic that fills only blank values in the selected group, preserves non-blank Step quantity values, recalculates `total_readings`, marks changed rows as `matrix_step_override`, and leaves persistence to the existing `Save quantities` flow.
- Updated Matrix Editor tests to prove blank-only application, preservation of existing values, and existing save payload use.

Backend/data compatibility is preserved for this scope. No backend files, schema/migrations, or Basic Information storage code were changed by TASK_358A. Existing Basic Information quantity values can remain in stored records, but the Basic Information UI no longer exposes them as an authoring surface.

UX checks pass for the implementation gate:

- The default-entry UI is inline with Step quantity setup, not modal-first.
- It uses standard inputs and one quiet action.
- It does not add a separate navigation/card surface or long explanatory copy.
- The CSS uses a thin separator and restrained product styling, with no side-stripe accent, gradient text, glassmorphism, or nested-card workaround.
- Matrix Step setup remains the working surface, and Matrix Step rows remain final authority after save/confirmation.

Locked scope remains intact for the TASK_358A candidate package:

- no backend/schema/data deletion or destructive migration;
- no Fee/Test Record/Report behavior changes;
- no Matrix parser/import changes;
- no LTR/public-drive/real workbook/folder behavior;
- no StepInstance/execution persistence;
- no `.agents/**` or `docs/project_management/**` changes.

Current worktree still contains external residuals, including `backend/api/dependencies.py`, Fee rule seed/test residuals, Settings/LTR/template services/tests, desktop/release/packaging files, New Project test residuals, and `temp_agents_stash.md`. These remain excluded from TASK_358A and must not be packaged with this lane unless separately owned.

## Implementation Validation

- `npm test -- ProjectBasicInformationWorkspace MatrixEditorWorkspace --run` from `frontend/` passed: 2 files / 60 tests.
- `npm run build` from `frontend/` passed with the existing Vite chunk-size warning only.
- `git diff --check -- frontend/src/features/project-basic-information/basicInformationFieldConfig.ts frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx frontend/src/features/matrix-editor/matrixStepQuantitySelectors.ts frontend/src/features/matrix-editor/MatrixStepQuantityPanel.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx frontend/src/workbench.css docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_developer.md` passed with LF/CRLF warnings only.
- Trailing whitespace scan on TASK_358A touched frontend/evidence files returned no matches.
- Targeted forbidden-scope/status scans showed TASK_358A candidate frontend files plus excluded external residuals; no TASK_358A backend/API-client/schema/Fee/Test Record/Report/Matrix parser/LTR/public-drive/governance changes were identified.

Implementation decision: `reviewer_implementation_pass`.

Recommended next role/action: QA gate for focused browser/UI smoke of Basic Information and Matrix Editor Step quantity defaults.

Blocking summary: none.
