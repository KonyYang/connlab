# TASK_315D_FEE_UI_PROJECT_FOLDER_REGRESSION

Status: Complete.

Executable plan: `docs/task_315d_fee_ui_project_folder_regression_plan.md`

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Parent umbrella: `TASK_315_MATRIX_DRAFT_TO_FEE_DRAFT_INCREMENTAL_REBASE`.

Prerequisites:

- `TASK_315A_MATRIX_TO_FEE_REBASE_CORE` is complete.
- `TASK_315B_PENDING_REBASE_PERSISTENCE_AND_MATRIX_AUTOSAVE_CANCEL_LIFECYCLE` is complete, including review follow-up.
- `TASK_315C_MATRIX_CONFIRM_PROMOTION` is complete, including review follow-up for saved Matrix draft payload signature validation.

TASK_315D is the final planned executable slice of TASK_315. It verifies and finishes the user-facing Fee Evaluation and Project Folder behavior after Matrix Confirm promotion creates a new-context Fee pricing draft. It must not add new backend authority semantics unless a regression proves the existing API contract is insufficient.

## Why This Task Is Allowed To Plan Now

TASK_315C now promotes pending/fallback Matrix-to-Fee rebase output into a current Fee pricing draft after Matrix Confirm. The remaining product gap is making sure the Fee Evaluation UI loads and explains that promoted current draft correctly, and that Project Folder Required forms readiness remains governed by current Confirmed Matrix plus current Confirmed Fee authority, not by an unconfirmed promoted pricing draft.

Implementation was completed after separate explicit user approval.

## Goal

After a Matrix edit is confirmed and TASK_315C promotion creates a current Fee pricing draft:

- Fee Evaluation opens on the promoted current pricing draft without treating it as missing or stale;
- Fee Evaluation makes it clear that pricing was carried forward from the Matrix rebase and still requires operator review plus Confirm Fee;
- Confirm Fee stays disabled until the currently visible pricing draft is saved/current and matches local signature gates;
- Project Folder Required forms remain blocked until the new-context Confirmed Fee authority is confirmed;
- after Confirm Fee succeeds for the promoted draft, Project Folder Required forms can become ready/current according to existing TASK_321 rules.

## Inputs

- Existing Fee Evaluation pricing draft API:
  - `GET /api/projects/{project_id}/confirmed-matrix/fee-evaluation/pricing-draft`
  - `PUT /api/projects/{project_id}/confirmed-matrix/fee-evaluation/pricing-draft`
  - `DELETE /api/projects/{project_id}/confirmed-matrix/fee-evaluation/pricing-draft`
- Existing Confirmed Fee API:
  - `GET /api/projects/{project_id}/confirmed-fee/latest`
  - `POST /api/projects/{project_id}/confirmed-fee/versions`
- TASK_315C promoted/fallback current pricing draft for the active Confirmed Matrix context.
- Existing Project Folder selectors and Required forms preview/generation behavior from TASK_314C and TASK_321.

## Outputs

- Minimal Fee Evaluation UI/state handling improvements, if existing UI does not already satisfy the flow.
- Frontend and/or backend regression tests proving the Matrix Confirm -> promoted pricing draft -> Confirm Fee -> Project Folder Required forms chain.
- Updated task board notes after validation.

## In Scope

- Fee Evaluation UI load/gating behavior for a `status="current"` pricing draft produced by TASK_315C promotion/fallback.
- Operator-facing Fee Evaluation status/copy that distinguishes:
  - current saved pricing draft needs review/Confirm Fee;
  - Confirmed Fee missing/stale;
  - unconfirmed saved/local pricing changes.
- Confirm Fee frontend regression coverage for promoted current draft ids/signatures.
- Project Folder selector/regression coverage proving Required forms stay blocked while Confirmed Fee is missing/stale after Matrix Confirm promotion.
- Project Folder selector/regression coverage proving Required forms may become ready/current only after Confirm Fee authority matches the active Confirmed Matrix/Fee rule context.
- Static frontend shell guards if needed to keep API client wiring and user-facing copy stable.

## Out Of Scope

- No new Matrix rebase algorithm changes.
- No pending rebase storage changes.
- No Matrix autosave/Cancel lifecycle changes.
- No Matrix Confirm promotion backend changes unless a regression proves the current TASK_315C contract is unusable.
- No Confirmed Fee authority schema change.
- No automatic Confirm Fee.
- No inactive removed-row editing UI.
- No Fee calculation or pricing rule changes.
- No Required forms generation behavior change beyond regression-proven linkage fixes.
- No ProjectOutputRecord schema/semantics/API changes.
- No StepInstance, report generation, execution evidence/image, AI, permissions, LAN/server, or multi-user scope.

If implementation needs any out-of-scope behavior, stop and split a follow-up task instead of expanding TASK_315D.

## Acceptance Criteria

- Fee Evaluation loading a TASK_315C promoted current pricing draft sets pricing draft status to `current`, hydrates the promoted values, stores the returned saved draft id/signature, and does not trigger the missing-draft seed path.
- Confirm Fee is enabled only when:
  - Fee draft is loaded;
  - Confirmed Fee status is available, even when that status is `missing` or `stale`;
  - latest saved pricing draft id exists;
  - saved local pricing signature equals the visible current pricing signature;
  - no pricing draft autosave/discard is pending;
  - `confirmed_by` is non-empty.
- `missing` or `stale` Confirmed Fee status must not by itself disable Confirm Fee. Those states should guide the operator to review and create/refresh Fee authority.
- Confirm Fee is disabled only for loading/error Confirmed Fee status, draft missing/stale, dirty/autosave pending, missing saved draft id, saved/current signature mismatch, discard in progress, or empty `confirmed_by`.
- If Confirmed Fee is missing after Matrix Confirm promotion, Fee Evaluation shows business-readable guidance that Fee must be reviewed and confirmed for the active Matrix before controlled Fee forms/Required forms are ready.
- If Confirmed Fee is stale after Matrix Confirm promotion, Fee Evaluation shows business-readable stale guidance and requires Confirm Fee again.
- Project Folder `Confirmed Fee authority` task is blocked when Confirmed Fee is missing or stale, even if a promoted pricing draft exists.
- Project Folder `Required forms` task is blocked when Confirmed Fee is missing or stale, even if Required forms preview data looks ready/current.
- Project Workbench mapping from `ConfirmedFeeLatestResponse.status` to Project Folder `confirmedFeeAuthorityStatus` is covered: `missing -> missing`, `stale -> stale`, `current -> confirmed`.
- After Confirm Fee succeeds for the promoted current pricing draft, Project Folder selector behavior can show `Confirmed Fee authority` ready and allow Required forms readiness according to existing preview status.
- No Project Folder task can treat a promoted pricing draft as Confirmed Fee authority.
- UI copy remains operator-facing and does not expose backend terms such as `fee_rebase`, payload signature, route names, stack traces, or task IDs.
- Scope remains frontend/UI and regression focused unless a narrow linkage bug is proven.

## Required Validation

Baseline before implementation:

```powershell
py -m pytest tests/unit/test_matrix_fee_rebase_promotion_service.py tests/unit/test_matrix_editor_session_service.py tests/integration/test_matrix_editor_session_api.py -q
```

Frontend Fee Evaluation:

```powershell
cd frontend
npm test -- --run FeeEvaluationReviewExportPage --watch=false
```

Project Folder regression:

```powershell
cd frontend
npm test -- --run projectFolderTaskSelectors ProjectFolderTaskList FeeEvaluationStatusSummary --watch=false
```

Static/frontend guards:

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or project_workbench or task315"
```

Build:

```powershell
cd frontend
npm run build
```

If backend linkage is touched:

```powershell
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py tests/unit/test_confirmed_fee_version_service.py tests/integration/test_confirmed_fee_version_api.py -q
```

## Stop Point

TASK_315D stops after Fee UI and Project Folder regression validation. Do not proceed to inactive removed-row editing, StepInstance, report, evidence/image, AI, permissions, LAN/server, multi-user scope, or TASK_316+ work from this task.

## Completion Notes

Completed TASK_315D as a regression-focused Fee UI and Project Folder gate. Existing Fee Evaluation production behavior already loaded TASK_315C promoted current pricing drafts and allowed Confirm Fee when Confirmed Fee authority was missing or stale, as long as pricing draft saved-id/signature gates passed. Added regression coverage for promoted current pricing draft hydration, Confirm Fee missing/stale guidance, stale authority refresh, Project Folder selector gating, Project Workbench Confirmed Fee status mapping, and static frontend boundary/copy guards. No backend production code, Fee calculation rule, ProjectOutputRecord, Required forms generation semantics, Matrix rebase algorithm, pending storage, or Matrix Confirm promotion behavior was changed.

Validation:

```powershell
py -m pytest tests/unit/test_matrix_fee_rebase_promotion_service.py tests/unit/test_matrix_editor_session_service.py tests/integration/test_matrix_editor_session_api.py -q
# 31 passed

cd frontend
npm test -- --run FeeEvaluationReviewExportPage --watch=false
# 20 passed, with existing non-failing React act(...) warnings in older async tests

cd frontend
npm test -- --run ProjectWorkbenchLayout projectFolderTaskSelectors ProjectFolderTaskList FeeEvaluationStatusSummary --watch=false
# 37 passed

py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task315 or fee or project_workbench"
# 12 passed, 134 deselected

cd frontend
npm run build
# passed
```
