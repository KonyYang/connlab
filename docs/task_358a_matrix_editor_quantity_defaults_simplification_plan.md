# TASK_358A Matrix Editor Quantity Defaults Simplification Plan

Status: complete/accepted by Integrator
Task: `TASK_358A_MATRIX_EDITOR_QUANTITY_DEFAULTS_SIMPLIFICATION`
Lane: `matrix-editor-quantity-defaults-simplification`
Date: 2026-07-09
Role: Planner

## 1. Current Phase / Active Task / Why Allowed

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: `TASK_357E_TEST_RECORD_REPORT_REUSE_MATRIX_STEP_QUANTITIES` is complete/accepted. User/Orchestrator requested a corrective simplification after the accepted TASK_357A-E quantity authority series.

Current role: Planner.

Why allowed: The user explicitly changed the product direction for quantity default entry. Planner Discovery and Developer planning-first are complete; Reviewer plan gate and implementation-readiness passed; the user approved source-of-truth reconciliation and Developer implementation.

## 2. User Goal Restatement

The user wants Basic Information to stop being the place where project-level quantity defaults are entered. Quantity default entry should move into Matrix Editor, near the Step setup workflow or bottom Matrix controls. Matrix Editor remains the place where each Step confirms or overrides quantity values. Fee Evaluation, Test Record, and Report remain passive consumers of confirmed Matrix Step quantities.

Corrected product chain:

```text
Matrix Editor default values entry
  -> Matrix Editor per-Step confirmation / override
  -> Fee / Test Record / Report passive consumption
```

## 3. Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `$impeccable` product context from `PRODUCT.md` / `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- TASK_357B Basic Information quantity defaults QA evidence
- TASK_357C Matrix Step quantity setup QA evidence
- TASK_357D Fee passive consumption accepted board/evidence
- TASK_357E Test Record reuse accepted board/evidence
- `frontend/src/features/project-basic-information/basicInformationFieldConfig.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx`
- `backend/application/project_basic_information_service.py`
- `backend/application/matrix_step_quantity_service.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixStepQuantityPanel.tsx`
- `frontend/src/features/matrix-editor/matrixStepQuantitySelectors.ts`
- `frontend/src/api/client.ts`
- focused Basic Information / Matrix Step quantity tests by targeted search
- current `git status --short`

## 4. Confirmed By User

- Basic Information should no longer keep the `Quantity defaults` entry.
- Basic Information should no longer be the quantity default input surface.
- Matrix Editor should provide the default value entry near the bottom or Step setup area.
- Matrix Editor per-Step setup remains the final confirmation/override location.
- Fee/Test Record/Report continue to passively consume confirmed Matrix Step quantities.
- Do not delete or break existing persisted data unless proven safe and approved.
- Do not change LTR/public-drive, Matrix parser, StepInstance, full Report generation, release/settings, `.agents/**`, or `docs/project_management/**`.

## 5. Confirmed By Repository Evidence

- TASK_357B added `Quantity defaults` to Basic Information with three fields: `test_points_per_sample`, `readings_per_point`, `contact_points_per_sample`.
- Basic Information service currently validates those quantity defaults as optional non-negative decimals on confirm.
- TASK_357C Matrix Step quantity setup already exists and loads defaults from Basic Information through `MatrixStepQuantityService`.
- Matrix Editor already renders `MatrixStepQuantityPanel` and saves per-Step quantities through `fetchMatrixStepQuantities` / `saveMatrixStepQuantities`.
- TASK_357D and TASK_357E consume confirmed Matrix Step quantities downstream and do not use Basic Information or Fee edits as final authority.
- Current worktree contains external release/settings/template residuals that must remain excluded.

## 6. Inferred By Planner

- This should be a corrective lane, not a broad rework of the quantity authority chain.
- The safest product correction is UI/source-policy migration, not schema deletion.
- Existing Basic Information values-map keys can remain readable for historical compatibility while disappearing from the Basic Information UI.
- Matrix Editor default values should be a convenience to populate Step rows, not a new persisted authority separate from Matrix Step quantity records.
- If backend default-source policy changes are needed, they should be scoped to `MatrixStepQuantityService` and not Basic Information schema.

## 7. Not Yet Confirmed

No blocker for planned lane creation.

Implementation-level decisions left for Developer planning-first:

1. Exact Matrix Editor placement: bottom action area versus inside/above `MatrixStepQuantityPanel`.
2. Apply/copy semantics: fill blank rows only by default, with explicit action for overwrite if needed.
3. Whether Matrix Editor defaults are temporary UI state or persisted as draft-level helper state. Default recommendation: avoid new schema unless Developer proves it is necessary and Reviewer/User re-gate it.

## 8. Planning Risk

- Deleting Basic Information stored keys or schema would risk historical data and older records.
- Leaving Basic Information UI visible would continue the product confusion the user explicitly corrected.
- Adding a second persisted default authority in Matrix Editor could create a competing source of truth.
- Overwriting per-Step values silently would violate the Matrix Step final authority contract.

## 9. What To Remove From Basic Information

- Remove the `Quantity defaults` group from the Basic Information UI configuration.
- Remove Basic Information UI expectations for `Test points / sample`, `Readings / point`, and `Contact points / sample`.
- Remove or adjust user-visible Basic Information validation copy for quantity defaults.
- Keep Basic Information focused on project identity, setup, LTR workbook fields, and confirmed Basic Information authority.

## 10. What To Preserve For Compatibility

- Preserve existing persisted Basic Information records that contain quantity keys.
- Avoid schema migration/deletion.
- Backend Basic Information may keep tolerant cleaning/validation behavior if incoming legacy payloads contain those keys.
- Do not break Project Basic Information API responses that include historical values, but do not surface those values as active BI fields.
- Matrix Step consumers should remain compatible with already-confirmed Matrix Step quantity records produced by TASK_357C.

## 11. Matrix Editor Default Entry Boundary

UI placement:

- Prefer a compact default strip in or immediately above the existing `MatrixStepQuantityPanel`, because the operator is already working on Step quantities there.
- Bottom panel placement is acceptable if it stays connected to Step setup and does not compete with Matrix confirmation/test-record actions.

Behavior:

- Operator can enter default `test_points_per_sample`, `readings_per_point`, and `contact_points_per_sample`.
- Action copy should be direct, for example `Apply to blank Step quantities`.
- Applying defaults should fill blank/manual-required rows by default.
- Existing saved/manual override values should not be overwritten silently.
- If overwrite-all behavior is needed, it should be an explicit secondary action or later lane.
- `total_readings` remains derived/read-only per Step.
- Save still uses the existing Matrix Step quantity save flow.

Data policy:

- Matrix Editor defaults are a convenience source for Step setup, not a separate downstream authority.
- Confirmed Matrix Step quantities remain the only downstream authority for Fee/Test Record/Report.
- Basic Information defaults should no longer be the primary source for new Matrix Step default rows after this lane.

## 12. Impact On TASK_357D/E Consumers

No consumer semantic change is planned.

- Fee Evaluation continues to consume confirmed Matrix Step quantities.
- Test Record / Report projection continues to consume confirmed Matrix Step quantities.
- Existing confirmed Step quantity records remain valid.
- Regression tests should prove downstream consumers are unaffected by removal of the Basic Information UI entry.

## 13. May Touch

Future implementation May Touch draft:

- `frontend/src/features/project-basic-information/basicInformationFieldConfig.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx` only if validation/error surfaces need cleanup after removing the field group
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixStepQuantityPanel.tsx`
- `frontend/src/features/matrix-editor/matrixStepQuantitySelectors.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/api/client.ts` only if API DTOs need a minimal Matrix-default payload/helper
- `backend/application/matrix_step_quantity_service.py`
- `backend/api/routes_matrix_step_quantities.py`
- focused Matrix Step quantity backend/API tests
- focused Basic Information regression tests
- TASK_358A developer/reviewer/QA evidence and board updates through normal lane flow

## 14. Must Not Touch

- Do not delete schema/data or run destructive migrations.
- Do not remove compatibility reading for existing Basic Information quantity values unless Reviewer/User explicitly approve a migration.
- Do not change Fee default-fill semantics except regression verification.
- Do not change Test Record/Report consumer semantics except regression verification.
- Do not mutate confirmed Matrix Step quantities outside the existing Matrix Step quantity save/confirm path.
- Do not implement StepInstance/execution persistence.
- Do not change Matrix parser/import rules.
- Do not change LTR workbook/public-drive/real workbook/folder behavior.
- Do not clean release/settings/template residuals.
- Do not touch `.agents/**` or `docs/project_management/**`.

## 15. Locked Paths

- `backend/modules/fee_evaluation/**`
- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/application/confirmed_matrix_fee_step_quantities.py`
- Test Record / Report implementation paths except focused regression tests if needed
- Matrix parser/import implementation paths
- Basic Information storage schema/migrations
- Matrix Step quantity storage schema/migrations
- LTR/public-drive implementation paths
- real workbook files
- real public-drive folders
- real local project folders
- `D:\Test Project/**`
- `D:\PublicProject/**`
- `.agents/**`
- `docs/project_management/**`
- `dist_release/**`
- `packaging/**`
- release scripts/tests/docs
- `temp_agents_stash.md`

## 16. Validation Gate Draft

Backend tests:

- Matrix Step quantity defaults no longer require Basic Information quantity defaults for new rows, or the old source is treated only as compatibility fallback if still present.
- Matrix Step quantity save/load behavior remains unchanged for per-Step records.
- Existing confirmed Matrix Step quantity downstream consumers remain unaffected.
- Basic Information confirm no longer exposes UI-facing quantity default validation path, while legacy values do not break service behavior.

Frontend tests:

- Basic Information no longer renders `Quantity defaults`, `Test points / sample`, `Readings / point`, or `Contact points / sample`.
- Matrix Editor shows a compact default-entry affordance near Step quantity setup or bottom Step setup area.
- Applying defaults fills blank Step quantity rows.
- Applying defaults does not silently overwrite existing manual overrides.
- Per-Step edits and Save still work.
- `total_readings` remains derived/read-only.

Regression tests:

- TASK_357C Matrix Step setup focused tests.
- TASK_357D Fee passive consumption focused tests, or at least no touched Fee scope plus targeted backend regression if available.
- TASK_357E Test Record preview/document quantity metadata focused tests, or no touched Test Record scope plus targeted regression if available.

General validation:

- focused pytest for touched backend services/routes.
- focused frontend tests for Basic Information and Matrix Editor.
- `npm run build`.
- `git diff --check`.
- trailing whitespace scan.
- forbidden-scope scan for Fee, Test Record/Report implementation, StepInstance, Matrix parser/import, LTR/public-drive, real folders/workbooks, release/settings residuals, `.agents/**`, and `docs/project_management/**`.

## 17. Merge Gate Draft

- Reviewer plan gate pass before Developer planning-first.
- User approval required before Developer planning-first.
- Developer planning-first must refine UI placement, apply/copy behavior, backend compatibility strategy, tests, and package isolation.
- Reviewer implementation-readiness pass before implementation authorization.
- User approval and source-of-truth reconciliation before Developer implementation.
- QA required because this changes user-facing Basic Information and Matrix Editor UI behavior.
- Integrator packaging must isolate TASK_358A from existing release/settings/template residuals.

## 18. Definition Of Ready

Definition of Ready for planned lane creation is satisfied:

- corrected user goal is explicit;
- upstream TASK_357A-E state is verified from board/evidence;
- existing Basic Information quantity UI and Matrix Step quantity setup code were checked;
- May Touch / Must Not Touch / Locked Paths are concrete;
- validation and merge gates are testable;
- non-goals prevent schema deletion, downstream consumer changes, StepInstance, full Report generation, LTR/public-drive, and release/settings scope creep.

Lane was planned after Discovery Gate and has now passed Reviewer plan gate, Developer planning-first, Reviewer implementation-readiness, and user implementation approval.

## 19. Developer Planning-First Refinement

Status: Developer planning-first complete. Product implementation remains not authorized.

### Implementation Shape

Future implementation should keep the correction narrow:

1. Remove the Basic Information `Quantity defaults` field group from the config-driven Basic Information UI.
2. Remove Basic Information frontend validation/status affordances that exist only for those quantity default fields.
3. Preserve backend Basic Information values-map tolerance for historical records. Do not delete fields from stored records, do not add a migration, and do not make existing records fail solely because they still contain quantity keys.
4. Add a compact default-entry strip inside `MatrixStepQuantityPanel`, above the Step quantity table and below the panel header.
5. Keep defaults as transient Matrix Editor UI state for V1. Do not add a persisted default table, draft-level default record, or new schema.
6. Add one primary local action: `Apply to blank Step quantities`.
7. The apply action fills only blank Step quantity inputs in the currently displayed group. It must not silently overwrite any non-blank row value, saved Matrix Step override, carried-forward quantity, or existing review value.
8. After applying defaults, the operator still uses existing `Save quantities`. The existing Matrix Step quantity save API remains the persistence boundary and final Step authority.
9. Keep `total_readings` derived/read-only from `test_points_per_sample * readings_per_point`.
10. Preserve Fee/Test Record/Report behavior through regression checks only.

### UI Placement And Copy

Use the existing Step quantity surface rather than adding a modal, extra card stack, or separate navigation entry.

Recommended placement:

- inside `MatrixStepQuantityPanel`;
- immediately below the header with `Save quantities`;
- visually as a dense inline control strip with three small inputs and one action button;
- no nested card;
- no long explanation.

Suggested user-facing copy:

- Strip label: `Defaults for this group`
- Inputs:
  - `Test points / sample`
  - `Readings / point`
  - `Contact points / sample`
- Action: `Apply to blank Step quantities`
- Result message: `Defaults applied to blank Step quantities.`
- No-overwrite message: `No blank Step quantities to update.`

The UI should remain restrained and operational per `$impeccable`: standard inputs, one quiet action, semantic disabled state, no modal as first thought, no decorative side stripe, no gradient text, no glassmorphism, no large card clutter.

### Backend Compatibility Policy

Preferred V1 backend strategy:

- Keep `ProjectBasicInformationService` compatibility with legacy quantity keys in stored `values_json`.
- Do not expose those keys through Basic Information field config.
- Keep confirm/save tolerant enough that older records can still be read and round-tripped without destructive cleanup.
- Update `MatrixStepQuantityService` only if necessary to stop Basic Information from being the active primary default source for new Matrix Step rows.

Recommended Matrix Step service policy:

- Saved Matrix Step quantities remain first priority.
- Confirmed matrix carry-forward remains unchanged.
- For rows with no saved quantity, default to manual-required unless the implementation deliberately includes a clearly labeled legacy fallback for already-stored Basic Information quantity values.
- If a legacy fallback is retained, it must be documented as compatibility only and must not be presented as the main operator default-entry path.
- New Matrix default-entry values should enter persistence only after the operator applies them to rows and saves through the existing Matrix Step quantity API.

### Exact Future May Touch

Product implementation should be limited to:

- `frontend/src/features/project-basic-information/basicInformationFieldConfig.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx`
- `frontend/src/features/matrix-editor/MatrixStepQuantityPanel.tsx`
- `frontend/src/features/matrix-editor/matrixStepQuantitySelectors.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/workbench.css`
- `backend/application/matrix_step_quantity_service.py`, only if needed for active default-source policy
- `tests/unit/test_matrix_step_quantity_service.py`, only if backend source policy changes
- `tests/integration/test_matrix_step_quantity_api.py`, only if backend/API behavior changes
- TASK_358A Developer/Reviewer/QA evidence and board updates through normal lane flow

Avoid `frontend/src/api/client.ts` unless the implementation proves a typed DTO change is unavoidable. The preferred V1 does not require a new API contract.

### Implementation Tests

Frontend:

- Basic Information no longer renders `Quantity defaults`.
- Basic Information no longer renders `Test points / sample`, `Readings / point`, or `Contact points / sample`.
- Basic Information invalid quantity default validation/status copy is removed or no longer reachable.
- Matrix Editor renders `Defaults for this group` inside the Step quantity setup panel.
- Applying defaults fills blank Step quantity rows in the selected group.
- Applying defaults does not overwrite existing non-blank Step quantity values.
- Applying defaults updates derived `total_readings` in the UI.
- `Save quantities` persists the applied row values through the existing save helper.
- Readonly lifecycle state disables the default strip and apply action consistently with row inputs.

Backend, only if touched:

- New Matrix Step quantity rows no longer require Basic Information quantity defaults as the active default-entry source.
- Existing saved Matrix Step quantities still override any default.
- Legacy Basic Information quantity values remain harmless and readable.
- Matrix Step save/load behavior and duplicate identity protections from TASK_357C remain intact.

Regression:

- TASK_357D Fee passive consumption focused tests remain passing if backend/default-source behavior changes.
- TASK_357E Test Record preview/API quantity metadata focused tests remain passing if backend/default-source behavior changes.

### Validation For Implementation

- `npm test -- ProjectBasicInformationWorkspace MatrixEditorWorkspace --run`
- focused backend Matrix Step quantity tests if backend files are touched
- TASK_357D/357E backend regressions if backend source policy changes
- `npm run build`
- `git diff --check`
- trailing whitespace scan on touched files
- line-count scan on touched Python files
- forbidden-scope scan proving no Fee default-fill semantic change, no Test Record/Report consumer semantic change, no Matrix parser/import, no schema migration, no LTR/public-drive, no real folder/workbook mutation, no release/settings cleanup, no `.agents/**`, and no `docs/project_management/**`
- browser smoke for Matrix Editor if tooling is available: open a Matrix draft, enter group defaults, apply to blank Step quantities, verify non-blank row values are preserved, save, reload.

### Package Isolation Risks

- `docs/task_board.md` and release/settings/template residuals are already dirty and must remain outside this lane unless normal orchestration explicitly updates board/evidence.
- Existing TASK_357D residuals in Fee files must not be pulled into TASK_358A.
- Avoid broad edits to `MatrixEditorWorkspace.tsx`; keep new behavior in `MatrixStepQuantityPanel` and selectors where possible.
- Avoid expanding `matrix_step_quantity_service.py` near line-count limits. If backend changes are needed and the file approaches AGENTS limits, split helper logic instead of compressing whitespace.

## 20. Recommendation

Source-of-truth reconciliation is complete. Route to Developer implementation pass.

Blocking questions: none.

## 21. Source-Of-Truth Reconciliation

Date: 2026-07-09

Planner reconciliation records:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed.
- Reviewer implementation-readiness passed.
- User approved TASK_358A source-of-truth reconciliation and Developer implementation.

TASK_358A is complete/accepted by Integrator.

The authorized implementation scope remains:

- remove Basic Information `Quantity defaults` UI entry/card/tests;
- preserve backend/data compatibility and do not delete schema/data;
- provide compact Matrix Editor defaults inside `MatrixStepQuantityPanel` or near Step setup, not modal-first and not extra clutter;
- keep V1 default state transient in UI, with persisted authority remaining the per-Step Matrix Step quantity save flow;
- make `Apply to blank Step quantities` blank-only with no silent overwrite;
- keep Fee/Test Record/Report passive-consumer behavior unchanged except regression verification.

Locked scope remains:

- no schema/data deletion;
- no Fee/Test Record behavior changes except regression verification;
- no LTR/public-drive, Matrix parser, StepInstance, full Report, release/settings, `.agents/**`, or `docs/project_management/**` scope;
- no remote push.

## 22. Integrator Acceptance

Date: 2026-07-09

Status: complete/accepted by Integrator.

Accepted package:

- Basic Information quantity-default UI removal.
- Matrix Editor compact `Defaults for this group` strip.
- Blank-only `Apply to blank Step quantities` behavior.
- Focused Basic Information and Matrix Editor frontend tests.
- TASK_358A task, plan, Developer/Reviewer/QA/reconciliation evidence.
- `docs/task_board.md` closeout isolated from external residuals.

Validation summary:

- `npm test -- ProjectBasicInformationWorkspace MatrixEditorWorkspace --run`: 2 files / 60 tests passed.
- `npm run build` passed with existing Vite chunk-size warning only.
- staged diff, whitespace, whitelist, and forbidden-scope checks passed.

Remote push was intentionally not performed.
