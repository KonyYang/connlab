# TASK_314_MATRIX_AND_FEE_BACKGROUND_DRAFT_PERSISTENCE

Status: Planned. Awaiting user review and explicit approval before implementation.

Executable plan: `docs/task_314_matrix_and_fee_background_draft_persistence_plan.md`

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

TASK_314 is a follow-up task after TASK_313. It must not be implemented before TASK_313 is explicitly handled or the task board is explicitly reprioritized.

TASK_315 will handle Matrix Draft -> Fee Draft incremental rebase. TASK_314 only establishes the shared background draft lifecycle and must not implement Matrix-to-Fee structural synchronization.

## Model Fit Assessment

GPT-5.3-codex is suitable for TASK_314 because the task is a bounded draft-lifecycle and frontend workflow refactor across existing Matrix Editor and Fee Evaluation surfaces. It requires tracing current FastAPI routes, application services, SQLite repositories, React state, API client DTOs, and Vitest/pytest coverage. The primary risk is preserving the distinction between non-authority drafts and authority versions; this can be controlled with focused service/API tests and UI state tests.

## Goal

Unify Matrix Editor and Fee Evaluation draft behavior:

- User edits are saved in the background as non-authority drafts.
- `Confirm Matrix` and `Confirm Fee` publish the latest saved draft into authority versions.
- `Cancel` / `Cancel edits` explicitly discards the current draft and returns the page to the current authority-derived baseline.

The user should not need to manually click `Save changes` during the normal Fee Evaluation flow.

## Current Code Reality

- Matrix Editor currently loads from `GET /api/projects/{project_id}/matrix-editor/session`, edits mostly in frontend memory, and writes/publishes through `POST /api/projects/{project_id}/matrix-editor/session/confirm`.
- Matrix Editor already has Project Matrix draft persistence services and routes, but the session flow does not autosave page edits or restore a current draft as the normal entry path.
- Fee Evaluation already has Pricing Draft persistence bound to active Confirmed Matrix id/revision and fee rule version.
- Fee Evaluation currently exposes a manual `Save changes` button, and `Confirm Fee` saves current visible values before confirming.
- Confirmed Matrix and Confirmed Fee are the authority records. Drafts are working copies only.

## V1 Contract

### Matrix Editor

Add background Matrix draft behavior to the Matrix Editor session flow:

- Session seed returns current draft metadata:
  - `editor_draft_id`
  - `draft_status`
  - `draft_updated_at`
- If a current draft exists for the active Confirmed Matrix, Matrix Editor opens that draft.
- If no current draft exists, Matrix Editor opens the active Confirmed Matrix-derived state.
- Editing marks the page dirty and triggers debounce autosave after 800 ms.
- Autosave writes a draft bound to the current active Confirmed Matrix id/revision.
- `Confirm Matrix` is disabled while autosave is pending or failed.
- `Confirm Matrix` first requires the current UI payload to have autosaved successfully, then publishes that saved draft into a new Confirmed Matrix revision through one explicit confirm path.
- `Cancel` discards the current draft and returns to Workbench.

Suggested API additions:

- `PUT /api/projects/{project_id}/matrix-editor/session/draft`
- `DELETE /api/projects/{project_id}/matrix-editor/session/draft`

### Fee Evaluation

Refactor Fee Evaluation so pricing draft persistence is background behavior:

- Remove the primary-flow `Save changes` button.
- Editing any pricing/cost field triggers debounce autosave after 800 ms.
- Save state shows concise operational text: `Saving...`, `Saved`, `Save failed`, or `Draft stale`.
- `Confirm Fee` requires the latest autosave to be current and successful.
- `Cancel edits` discards the current pricing draft for the current Matrix/rule context and reloads default Fee Evaluation values.
- Stale pricing drafts remain blocked and are not automatically applied.

Suggested API addition:

- `DELETE /api/projects/{project_id}/confirmed-matrix/fee-evaluation/pricing-draft`

## In Scope

- Backend Matrix Editor session draft save/discard service behavior.
- Backend Fee Evaluation pricing draft discard behavior.
- Thin API routes and typed frontend API client DTOs.
- Matrix Editor autosave state, confirm blocking, cancel discard, and draft restore behavior.
- Fee Evaluation autosave state, removal of manual Save button, confirm blocking, and cancel edits behavior.
- Focused pytest and Vitest coverage.
- Static frontend shell guard updates.
- Task board update only after implementation approval and completion.

## Out Of Scope

- No TASK_313 package execution work.
- No package execute, public-drive publishing, or ProjectOutputRecord changes.
- No Confirmed Matrix or Confirmed Fee authority schema changes.
- No draft history, audit trail, multi-user merge, permissions, LAN/server sync, or conflict-resolution UI beyond current stale guards.
- No StepInstance, execution persistence, evidence/image handling, AI review, report engine, or new pricing-rule logic.
- No Office gateway changes unless a failing test proves a direct dependency.
- No conversion of drafts into authority; drafts remain non-authority working copies.
- No Matrix Draft -> Fee Draft incremental rebase, no soft add/delete of Fee groups or steps, and no preservation/migration of Fee edits across Matrix structural changes. Those belong to TASK_315.

## Acceptance Criteria

- Matrix Editor reload/re-entry restores unsent edits from a current background Matrix draft.
- Matrix Editor `Cancel` discards the current draft and reopens from the active Confirmed Matrix baseline.
- Matrix Editor `Confirm Matrix` cannot proceed while autosave is pending or failed.
- Matrix Editor V1 autosave is enabled only when an active Confirmed Matrix already exists; first-authority/no-active-Matrix editing keeps the existing short-session behavior.
- Fee Evaluation no longer exposes `Save changes` as a primary workflow button.
- Fee Evaluation edits are autosaved and restored after re-entry while the Matrix/rule context is current.
- Fee Evaluation `Cancel edits` discards the current pricing draft and returns to default current Matrix-derived values.
- `Confirm Fee` confirms only a current, successfully saved pricing draft.
- Stale Matrix/rule contexts remain protected: stale drafts are not applied or confirmed.
- Existing TASK_308-TASK_312 authority, preview, and package-readiness behavior remains intact.
- Matrix structural edits do not update Fee Evaluation in TASK_314. Fee rebase behavior starts only in TASK_315.

## Required Validation

```powershell
py -m pytest tests/unit/test_matrix_editor_session_service.py tests/integration/test_matrix_editor_session_api.py -q
```

```powershell
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q
```

```powershell
cd frontend
npm test -- --run MatrixEditorWorkspace FeeEvaluationReviewExportPage --watch=false
```

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "matrix_editor or fee"
```

## Stop Point

Stop after TASK_314 implementation, validation, and task board update. Do not proceed to package execution, StepInstance, reporting, AI, permissions, or multi-user scope.
