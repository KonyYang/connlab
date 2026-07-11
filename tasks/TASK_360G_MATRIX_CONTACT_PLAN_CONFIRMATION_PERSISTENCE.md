# TASK_360G Matrix Contact Plan Confirmation Persistence

## Status

Complete / Integrator accepted.

## Current Phase / Active Task / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Active board task: `TASK_360G_MATRIX_CONTACT_PLAN_CONFIRMATION_PERSISTENCE` is complete / accepted; predecessor `TASK_360C_MATRIX_CONTACT_PLAN_REVISION_DRAFT_ENABLEMENT` is complete/accepted in `5c1b10ab1aa85d478903d7e53947c23a6c7c9056`.
- Completed task: `TASK_360G_MATRIX_CONTACT_PLAN_CONFIRMATION_PERSISTENCE`.
- Role: Integrator packaging/readiness.
- Why allowed: Developer implementation and focused-validation fix pass completed; Reviewer B1 re-gate passed; QA gate passed; Integrator package isolation is the next legal gate.

## User Goal

When an operator saves LLCR/CR contact families in an editable revision draft and confirms that revision, the active confirmed Matrix must retain each plan's family counts and derived `readings_per_sample`. Re-entering the draft must show the saved common profile when it is uniform, and TASK_360B must then preview and generate its managed macro-free workbook from the new confirmed authority.

## Confirmed By User

- On project `72fbbfa290294da9a507344b68ff900f`, the operator opened an editable revision draft, entered LLCR HP `4`, LP `5`, Signal `24`, and entered CR specified-current `33`.
- `Save contact plan`, blank-only apply, and `Save quantities` completed. Two CR targets displayed `Applied`.
- After confirming and re-entering, coverage still displayed `2 targets / Applied`, but common LLCR/CR family inputs were empty and both readings displays were `Review`.
- Specialized record preview returned `No included LLCR/CR targets`; Generate remained disabled and no workbook was created.

## Repository Evidence And Root-Cause Assessment

### H1, Confirmed: no-change comparison excludes structured quantities

`MatrixEditorSessionService.confirm_session()` computes `_build_signature_from_session_payload()` and compares it with `_build_signature_from_confirmed()` before it loads the saved revision draft. Both signatures contain groups, rows, cells, and schedule only, not Step quantities or `contact_plan`. A contact-plan-only edit therefore returns `publish_status = no_change` and leaves the previous active authority in place.

### H2, Confirmed: session-confirm snapshot omits Step quantities

If the revision publish path is reached, `_build_confirmed_snapshot_from_session_draft()` currently returns groups, rows, and cells without `step_quantities`. In contrast, the existing direct authority and revision-flow builders already call `build_confirmed_step_quantities()`. The session path must use the same builder to copy structured `contact_plan` family data and derived readings.

### H3, Confirmed: common profile UI is not hydrated from saved targets

`MatrixEditorWorkspace` initializes `contactPlanProfiles` from `DEFAULT_CONTACT_PLAN_PROFILES` and only changes it through local edit handlers. The draft Step-quantity load restores target plans, explaining `Applied`, but never derives the common profile state, explaining blank family fields and `Review`.

### Not the root cause

Draft and confirmed repositories already serialize `contact_plan_json`, and the direct draft-confirm API regression proves a plan can persist into a confirmed snapshot. The defect is the Matrix Editor session-confirm path and UI hydration, not a schema or repository absence.

## Corrective Contract

1. A revision with matrix payload equal to active authority but structurally different Step quantities/contact plans must publish a new confirmed revision.
2. `no_change` remains valid only when both the Matrix payload and canonical structured Step quantity/contact-plan projection equal active confirmed authority.
3. Canonical comparison ignores generated ids, timestamps, and storage ordering, but includes Group/row position, Step sequence/suffix, scalar quantity values, contact plan coverage/override fields, derived readings, and ordered family fields (id, label, count, prefix, inclusion, custom flag).
4. Session-confirm snapshot construction uses existing `build_confirmed_step_quantities()` so confirmed authority stores the same structured contact plan as the saved draft.
5. Common profile hydration occurs only from uniform, included, non-override saved plans for each contact kind. Divergent target-specific plans are never collapsed into one common profile; the UI retains their target status and shows concise review feedback.
6. Fee, specialized workbook preview/generate, and generic Test Record continue to read only active confirmed authority. Draft values remain invisible to those consumers until successful reconfirmation.

## May Touch

- `backend/application/matrix_editor_session_service.py`
- A focused pure Step-quantity/contact-plan comparison helper under `backend/application/` only if needed to keep session service bounded
- `backend/application/matrix_step_quantity_authority_builder.py` only if the canonical comparison belongs beside its existing draft-to-confirmed mapping
- `tests/unit/test_matrix_editor_session_service.py`
- `tests/integration/test_matrix_editor_session_api.py`
- `frontend/src/features/matrix-editor/matrixContactMeasurementPlanSelectors.ts`
- `frontend/src/features/matrix-editor/matrixContactMeasurementPlanSelectors.test.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- Focused existing TASK_360A/B and Fee regression tests only as assertions, plus normal TASK_360G docs/evidence/board

## Must Not Touch / Locked Paths

- No storage schema, model, repository, migration, API route, API-client contract, or Matrix revision endpoint changes.
- No Fee rule/default-fill behavior, Fee-side authoring, TASK_360B projection/gateway/artifact semantics, or generic Test Record behavior.
- No Matrix parser/import, Basic Information, LTR/public-drive, StepInstance/execution, Report, real workbook/folder, release/settings, `.agents/**`, `docs/project_management/**`, or external residual cleanup.

## Validation Gate

- Backend unit: contact-plan-only revision draft change publishes revision `n+1`; confirmed snapshot includes LLCR/CR families and derived readings; structurally identical draft yields no-change; ids/timestamps do not cause false change.
- API integration: save draft contact plan through session flow, confirm, then read active confirmed snapshot and assert family counts/`readings_per_sample` survived.
- Frontend: uniform loaded plans hydrate HP/LP/Signal and CR profile counts; divergent/override plans do not silently become a common profile; saved target status remains intact.
- Regression: Fee reads confirmed readings only after reconfirm; TASK_360B preview becomes ready and Generate writes exactly one macro-free `.xlsx` under the managed artifact lifecycle; no workbook on blocked/no-change path; generic Test Record remains unchanged.
- Authorized real smoke: open revision draft, save LLCR `4/5/24` and CR `33`, apply/save, reconfirm, verify the active confirmed preview has included targets, then generate/download the managed workbook. Never use LTR/public-drive paths.
- Run focused `pytest`, focused `npm test`, `npm run build`, `py_compile`, `git diff --check`, trailing whitespace, forbidden-scope, and no-real-mutation scans.

## Merge Gate

Completed authorization chain: Reviewer plan re-gate passed; user approved Developer planning-first; Developer planning-first completed as docs-only; Reviewer implementation-readiness passed; user approved source-of-truth reconciliation and Developer implementation; Developer implementation and focused-validation fix pass completed; Reviewer B1 re-gate passed; QA gate passed; Integrator package isolation accepted.

## Definition of Ready

Satisfied. The defect is reproduced, source paths are known, no schema/API decision is open, and the confirmed-only authority boundary is explicit. Reviewer, QA, and Integrator gates are complete.

## Integrator Closeout

- Integrator gate: accepted.
- Package includes canonical Step quantity/contact-plan comparison, saved-draft-aware Matrix Editor session confirmation, confirmed snapshot Step-quantity persistence reuse, uniform-only common profile hydration, focused backend/frontend tests, TASK_360G task/plan/evidence, and TASK_360G board closeout.
- Package excludes external Fee residuals, parser hotfix residuals, CSS/shell-test residuals, `docs/superpowers/`, future TASK_360D-L files, schema/model/repository/migration/API-client changes, TASK_360B implementation changes, generic Test Record, Matrix parser/import, LTR/public-drive, StepInstance, Report, real workbook/folder paths, `.agents/**`, and `docs/project_management/**`.
- Remote push intentionally not performed.

## Blocking Questions

None.
