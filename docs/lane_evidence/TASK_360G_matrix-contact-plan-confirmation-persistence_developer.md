# TASK_360G Matrix Contact Plan Confirmation Persistence Developer Evidence

Status: ready_for_review
Task: `TASK_360G_MATRIX_CONTACT_PLAN_CONFIRMATION_PERSISTENCE`
Lane: `matrix-contact-plan-confirmation-persistence`
Date: 2026-07-11
Role: Developer

## Gate

Developer implementation pass complete. The reconciliation records implementation authorization after the completed planning and Reviewer readiness gates.

Current phase: Phase 11, Project Workbench / Matrix / Approval Package controlled foundation.
Current active task: `TASK_360G_MATRIX_CONTACT_PLAN_CONFIRMATION_PERSISTENCE`.
Why allowed: TASK_360G is implementation authorized on the board and reconciliation evidence. The pass is limited to promotion equivalence, existing confirmed quantity mapping reuse, and persisted-profile hydration.

## Confirmed Implementation Facts

- `MatrixEditorSessionService.confirm_session()` compares only its Matrix/session payload signature before it loads an expected saved revision draft. The current signatures omit Step quantities and structured contact plans.
- `_build_confirmed_snapshot_from_session_draft()` maps groups, rows, and cells but currently returns no Step quantities.
- Existing `build_confirmed_step_quantities()` already maps draft quantities to confirmed ids and preserves `contact_plan`; draft and confirmed repositories already persist the structured contact-plan JSON.
- Matrix Editor loads draft Step quantities after `savedEditorDraftId` becomes available, but initializes common contact profiles from defaults and does not hydrate from persisted target plans.
- TASK_360B, Fee, and generic Test Record consume active confirmed authority, so their observed no-target state after the reproduced flow is downstream-correct rather than a consumer defect.

## Implementation Summary

1. Added `matrix_step_quantity_authority_comparison.py`, a pure canonical comparison layer for draft versus confirmed Step quantity/contact-plan authority. It ignores generated ids, timestamps, storage order, and suffix whitespace while retaining selected Group/Row/Step identity, scalar quantity/review fields, coverage/override state, derived readings, and ordered contact families.
2. `MatrixEditorSessionService.confirm_session()` now loads an expected saved revision draft before returning Matrix-equal `no_change`. A contact-plan-only authority delta publishes a revision; a fully equivalent draft retains the prior `no_change` result and stale signature protection.
3. The session confirmed-snapshot builder now reuses `build_confirmed_step_quantities()` so structured contact plans persist in the active confirmed snapshot instead of disappearing at confirmation.
4. Added uniform-only profile hydration in the Matrix Editor. Persisted included non-override plans hydrate the common profile when all matching targets agree. Divergent targets retain target authority and show the short review message `Contact plans differ by target. Review target coverage.`

## Changed Files

- `backend/application/matrix_editor_session_service.py`
- `backend/application/matrix_step_quantity_authority_comparison.py`
- `tests/unit/test_matrix_editor_session_service.py`
- `tests/unit/test_matrix_step_quantity_authority_comparison.py`
- `frontend/src/features/matrix-editor/matrixContactMeasurementPlanSelectors.ts`
- `frontend/src/features/matrix-editor/matrixContactMeasurementPlanSelectors.test.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- This Developer evidence file

## Validation

- `py -m pytest tests/unit/test_matrix_step_quantity_authority_comparison.py tests/unit/test_matrix_editor_session_service.py tests/unit/test_confirmed_matrix_authority_service.py tests/unit/test_confirmed_matrix_authority_repository.py tests/integration/test_matrix_editor_session_api.py tests/integration/test_matrix_step_quantity_api.py -q` -> 52 passed.
- `py -m pytest tests/unit/test_confirmed_matrix_llcr_cr_record_projection.py tests/unit/test_confirmed_matrix_llcr_cr_record_generation_service.py tests/integration/test_llcr_cr_specialized_record_workbook_api.py tests/unit/test_confirmed_matrix_fee_step_quantities.py -q` -> 9 passed. These confirm the existing downstream consumers remain confirmed-snapshot only.
- `py -m pytest tests/unit/test_matrix_step_quantity_authority_comparison.py tests/unit/test_matrix_editor_session_service.py -q` -> 19 passed after final cleanup.
- `py -m py_compile backend/application/matrix_editor_session_service.py backend/application/matrix_step_quantity_authority_comparison.py` -> passed.
- `npm test -- MatrixEditorWorkspace matrixContactMeasurementPlanSelectors MatrixContactMeasurementPlanCard --run` -> 3 files, 54 tests passed.
- `npm run build` -> passed. Existing Vite bundle-size warning remains.
- `git diff --check` for the candidate files -> passed with existing LF/CRLF working-copy warnings only.
- Trailing-whitespace scan of the candidate files and this evidence -> no matches.
- Focused line counts: new canonical helper is 150 lines; the pre-existing session service remains 1,895 lines. The new logic is isolated in the helper rather than extending the service with a second canonicalization implementation.
- Browser smoke was intentionally deferred: confirming a Matrix mutates project authority. The API/integration tests use temporary SQLite and fixture paths; Reviewer/QA can exercise the explicit live project flow separately.

## Scope And Residuals

- No schema, repository, route, API-client, Fee, TASK_360B workbook, generic Test Record, parser/import, Basic Information, LTR/public-drive, or real workbook/folder mutation changes were made.
- Existing Fee rule/seed/test, parser, CSS, board, release, and other untracked TASK residuals remain external and excluded.

## Reviewer B1 Fix Pass

Reviewer B1 found that the uniform hydration selector filtered `is_override` plans before it decided whether a contact kind was common. A normal included plan could therefore hydrate the shared profile while an included target override was silently omitted.

- `hydrateUniformContactPlanProfiles()` now collects all included plans for a kind first. Any included override prevents common-profile hydration and returns the existing concise review message.
- Added selector regression coverage for both normal-plus-override and override-only persisted plans.
- Added a Workspace regression proving persisted target overrides leave the common profile at its default value and surface the review message instead of overwriting the input with a normal target's count.
- This pass changed only `matrixContactMeasurementPlanSelectors.ts`, its selector test, `MatrixEditorWorkspace.test.tsx`, and this evidence. The existing API-client type import is read-only usage, not an API-client change.

Fix-pass validation:

- Red: `npm test -- MatrixEditorWorkspace matrixContactMeasurementPlanSelectors --run` failed as expected before the selector fix. The normal-plus-override selector case returned an LLCR common profile, and the Workspace input was incorrectly hydrated to `4`.
- Green: `npm test -- MatrixEditorWorkspace matrixContactMeasurementPlanSelectors MatrixContactMeasurementPlanCard --run` -> 3 files, 56 tests passed.
- `py -m pytest tests/unit/test_matrix_step_quantity_authority_comparison.py tests/unit/test_matrix_editor_session_service.py tests/unit/test_confirmed_matrix_authority_service.py tests/unit/test_confirmed_matrix_authority_repository.py tests/integration/test_matrix_editor_session_api.py tests/integration/test_matrix_step_quantity_api.py -q` -> 52 passed.
- `npm run build` -> passed with the existing Vite bundle-size warning only.
- Focused `git diff --check` passed with existing LF/CRLF warnings only; trailing-whitespace scan returned no matches.

## Integrator Focused-Validation Fix Pass

Integrator reproduced two frontend failures during the required full-suite rerun: the uniform hydration assertion read the common input before the async Step-quantity request completed, and the selected-group quantity test read its label after only waiting for the synchronously rendered panel title. The product state was not missing; both tests were racing the completed fetch state.

- The selected-group test now waits for the fetch invocation and then uses the async label query before editing the quantity.
- The uniform hydration assertion now waits for the persisted value `4` rather than reading the initially rendered empty input.
- The override Workspace regression waits for the review message, which proves the async persisted plan load completed, before asserting that the common input remains empty.
- No product implementation, backend, API client, storage, or downstream consumer behavior changed in this pass.

Fix-pass validation:

- Stable single-test rerun for `hydrates the common contact profile from uniform persisted draft targets` -> passed.
- Required `npm test -- MatrixEditorWorkspace matrixContactMeasurementPlanSelectors MatrixContactMeasurementPlanCard --run` -> 3 files, 56 tests passed.
- `npm run build` -> passed with the existing Vite bundle-size warning only.
- Final candidate `git diff --check` passed with existing LF/CRLF working-copy warnings only; trailing-whitespace scan of the touched tests, selector, and evidence returned no matches.
- The full frontend run and build took longer than normal while the local process environment was under contention, but both completed successfully. No product performance conclusion is drawn from that host condition.

## Planned Strategy Retained For Review Context

1. Add a bounded pure backend comparison helper, not more signature logic to the 1,845-line session service. Canonical projections compare authority identity by group/row position, step sequence, normalized suffix, scalar quantity/review fields, structured plan coverage/override/readings, and ordered family values. They ignore generated ids, timestamps, and storage ordering.
2. For an active Matrix with Matrix-equal payload and an expected saved revision draft, load that draft before returning `no_change`. Publish through the existing revision path when canonical quantities differ; retain `no_change` only for complete equivalence or a no-draft authority view.
3. Reuse existing `build_confirmed_step_quantities()` from the session-confirm snapshot builder. Do not duplicate mapping or alter repository/API/schema contracts.
4. Add a pure frontend uniform-profile hydration selector. Hydrate only uniform included, non-override persisted plans on successful quantity loads; retain defaults for absent plans and retain target-level authority plus concise review feedback for divergent plans.
5. Preserve Confirm Matrix as the promotion boundary. Fee, TASK_360B, and generic Test Record remain unchanged confirmed-snapshot consumers.

## Exact Future May Touch

- `backend/application/matrix_editor_session_service.py`
- `backend/application/matrix_step_quantity_authority_comparison.py`
- `tests/unit/test_matrix_step_quantity_authority_comparison.py`
- `tests/unit/test_matrix_editor_session_service.py`
- `tests/integration/test_matrix_editor_session_api.py`
- `frontend/src/features/matrix-editor/matrixContactMeasurementPlanSelectors.ts`
- `frontend/src/features/matrix-editor/matrixContactMeasurementPlanSelectors.test.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- TASK_360G lane docs/evidence/board through normal gate flow

## Locked Scope

- No storage schema/model/repository/migration, API route/client, or Matrix revision endpoint change.
- No Fee rule/default-fill, TASK_360B workbook projection/gateway/artifact implementation, generic Test Record, parser/import, Basic Information, LTR/public-drive, StepInstance/execution, Report, or real workbook/folder mutation.
- No release/settings cleanup, external residual cleanup, `.agents/**`, `docs/project_management/**`, commit, or push.

## Focused Validation Plan

- Backend canonical comparison and session service/API tests cover contact-plan-only publish, true no-change, confirmed family persistence, generated-id/timestamp/order normalization, and existing revision conflict behavior.
- Frontend selector/workspace tests cover uniform hydration, absent defaults, divergent/override review handling, and no automatic overwrite of local edits.
- Existing TASK_360B and Fee tests run as confirmed-only downstream regressions without implementation changes.
- Run focused `pytest`, `py_compile`, focused `npm test`, `npm run build`, session-service line count, diff/trailing/forbidden-scope/package-isolation/no-real-mutation scans, then an authorized controlled real-flow smoke at QA.

## Planning-Pass Validation

- Required TASK_360G plan and Developer evidence exist.
- `git diff --check -- docs/task_360g_matrix_contact_plan_confirmation_persistence_plan.md docs/lane_evidence/TASK_360G_matrix-contact-plan-confirmation-persistence_developer.md` passed with no output.
- A trailing-whitespace scan of both touched documents returned no matches.
- Targeted `git status --short` confirms this pass changed only the TASK_360G plan and this Developer evidence file. Existing Fee, parser, CSS, shell-test, UI hotfix, board, and release residuals remain external and excluded.

## Stop Point

Recommended next role: Reviewer implementation gate.

Blocking summary: none known. Implementation is complete pending Reviewer re-gate.
