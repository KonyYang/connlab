# TASK_314 Matrix And Fee Background Draft Persistence Plan

Status: Planned. Awaiting user review and explicit approval before implementation.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

The task board currently has no active implementation task and says `TASK_313` still requires its own task file, executable plan, and explicit approval. TASK_314 is a planned follow-up and must not be implemented before TASK_313 unless the task board is explicitly reprioritized.

TASK_315 will handle Matrix Draft -> Fee Draft incremental rebase. TASK_314 is intentionally limited to background draft persistence, Cancel discard semantics, and Confirm gating.

## Why This Task Is Allowed To Plan Now

The user identified a product consistency issue: Matrix Editor and Fee Evaluation should both preserve unfinished operator edits as background drafts, and `Cancel` should be the explicit way to abandon those edits. Planning this task is allowed because it does not implement code and prepares a reviewable future task.

## Step 1: Task Understanding

Goal:

- Make draft saving a background system responsibility for Matrix Editor and Fee Evaluation.
- Keep authority transitions explicit through `Confirm Matrix` and `Confirm Fee`.
- Make `Cancel` / `Cancel edits` mean “discard my unconfirmed draft.”

Inputs:

- Matrix Editor current UI state: groups, rows, cells, selected groups, sample quantities, schedule fields, source lineage, expected active confirmed authority.
- Fee Evaluation current edited pricing payload: row edits, manual rows, cost preview values, notes, lab manpower values, current Confirmed Matrix context, fee rule version.

Outputs:

- Non-authority Matrix Draft working copy.
- Non-authority Fee Pricing Draft working copy.
- Confirmed Matrix revision only after `Confirm Matrix`.
- Confirmed Fee version only after `Confirm Fee`.

Involved modules:

- `backend/application/matrix_editor_session_service.py`
- `backend/application/project_matrix_draft_persistence_service.py`
- `backend/infrastructure/storage/repositories/project_matrix_draft.py`
- `backend/api/routes_matrix_editor_session.py`
- `backend/application/fee_evaluation_pricing_draft_persistence_service.py`
- `backend/infrastructure/storage/repositories/fee_evaluation_pricing_draft_edit.py`
- `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`

Not allowed:

- No authority schema rewrite.
- No package execute or TASK_313 scope.
- No report, StepInstance, evidence/image, AI, permission, LAN/server, multi-user, or draft-history expansion.
- No Office file write behavior changes.
- No Matrix Draft -> Fee Draft incremental rebase, no soft add/delete of Fee groups or steps, and no migration of Fee edits across Matrix structural changes. Those belong to TASK_315.

## Step 2: Backend Design

### Matrix Editor Draft Save

Add a service method on the Matrix Editor session application boundary that accepts the same normalized Matrix Editor session payload shape used by confirm.

Behavior:

- Require project existence.
- Resolve current active Confirmed Matrix.
- V1 supports autosave only when an active Confirmed Matrix exists.
- If active authority exists, save/update a Project Matrix Draft bound to `base_confirmed_matrix_id = active.confirmed_matrix_id`.
- If no active authority exists, do not autosave. Keep the existing short-session first-authority behavior, where edits live in the current Matrix Editor session until `Confirm Matrix`.
- Reuse existing Project Matrix Draft persistence normalization rather than adding a parallel draft model.
- Return draft id, draft status, updated timestamp, and current active authority identity.

### Matrix Editor Draft Load

Extend session seed:

- If a draft exists for the current active Confirmed Matrix, return that draft as `editor_draft`.
- If no matching draft exists, return the active Confirmed Matrix-derived editor draft.
- Include `editor_draft_id`, `draft_status`, and `draft_updated_at`.
- Do not return stale drafts whose `base_confirmed_matrix_id` does not match the active Confirmed Matrix id.

### Matrix Editor Draft Discard

Add discard behavior:

- Physically delete the current non-authority draft aggregate for the active Confirmed Matrix context.
- Return a small response with `discarded: true/false`.
- Never delete Confirmed Matrix authority.
- Do not add a `discarded` status in V1; Cancel means the draft is abandoned and removed.

### Fee Pricing Draft Discard

Add a discard method to pricing draft persistence:

- Resolve current Matrix/rule context.
- Delete the pricing draft only when its project id, confirmed matrix id, confirmed revision, and fee rule version match the current context.
- Return `discarded: true/false`.
- Do not delete stale drafts for older contexts in V1.

## Step 3: Frontend Design

### Shared Interaction Model

Use concise status text:

- `Editing`
- `Saving...`
- `Saved`
- `Save failed`
- `Draft stale`

Confirm actions:

- Disabled while autosave is pending.
- Disabled after autosave failure until retry succeeds.
- Continue to rely on backend stale guards.

### Matrix Editor

Add an 800 ms debounce autosave after editable state changes.

Autosave should:

- Skip during initial seed load.
- Skip when current payload signature equals last saved signature.
- Save the same payload used by confirm.
- Update `saveBaselineSignature` only after successful save.
- Keep current page edits in memory on failure.

Cancel should:

- If no draft/current changes exist, return to Workbench.
- If there are draft/current changes, ask for discard confirmation.
- Call discard endpoint, then return to Workbench.

Confirm should:

- If autosave is pending, show a short message and wait/disable.
- If autosave failed, block with retry guidance.
- Confirm using the latest current UI payload only after that exact payload has autosaved successfully.

### Fee Evaluation

Remove `Save changes` from the normal action row.

Add autosave:

- Debounce edited pricing/cost state changes by 800 ms.
- Skip before the draft has loaded.
- Skip when loaded pricing draft is stale.
- Update `latestSavedPricingDraftId` after successful save.
- Mark draft dirty while edits are unsaved.

Add `Cancel edits`:

- Ask for discard confirmation when current page has saved or unsaved draft edits.
- Call pricing draft discard endpoint.
- Reload Fee Evaluation default draft and current pricing-draft status.

Confirm Fee:

- Use the latest saved draft id.
- If current edits are dirty, save first or block until autosave completes.
- Do not confirm when save failed or stale.

## Step 4: API / DTO Changes

Matrix session seed response additions:

- `editor_draft_id: string | null`
- `draft_status: "missing" | "current" | "stale"`
- `draft_updated_at: string | null`

New Matrix endpoints:

- `PUT /api/projects/{project_id}/matrix-editor/session/draft`
  - Request: Matrix Editor session payload, same business fields as confirm without `confirmed_by`.
  - Response: draft id, status, updated timestamp, active confirmed authority id/revision.

- `DELETE /api/projects/{project_id}/matrix-editor/session/draft`
  - Response: `discarded`, active confirmed authority id/revision.

New Fee endpoint:

- `DELETE /api/projects/{project_id}/confirmed-matrix/fee-evaluation/pricing-draft`
  - Response: current context plus `discarded`.

Do not change Confirmed Matrix or Confirmed Fee version response contracts except where tests prove existing API client typing needs nullable draft metadata.

## Step 5: Testing Plan

Backend:

- Matrix seed returns active authority-derived draft when no current draft exists.
- Matrix seed returns current saved draft after autosave.
- Matrix autosave binds draft to active Confirmed Matrix id/revision.
- Matrix autosave is not available when no active Confirmed Matrix exists; first-authority editing keeps existing short-session behavior.
- Matrix active authority change makes old draft non-current.
- Matrix discard physically deletes the current non-authority draft aggregate and removes it from the next seed.
- Matrix confirm publishes from autosaved draft/current payload and preserves no-change behavior.
- Fee save/load still restores current pricing draft.
- Fee discard removes only current-context pricing draft.
- Fee stale draft is not discarded by current-context discard unless it matches the current context.
- Confirm Fee still rejects missing/stale/changed draft ids.

Frontend:

- Matrix Editor autosaves after an edit and shows saved state.
- Matrix Editor re-entry restores current draft edits.
- Matrix Editor cancel calls discard and returns to Workbench.
- Matrix Editor confirm is blocked while saving or after save failure; after autosave succeeds, confirm uses the saved current UI payload through the single confirm path.
- Matrix structural edits do not update Fee Evaluation in TASK_314. Fee rebase behavior starts only in TASK_315.
- Fee Evaluation does not render `Save changes`.
- Fee Evaluation autosaves edited values and uses the returned draft id for Confirm Fee.
- Fee Evaluation `Cancel edits` calls discard and resets visible values.
- Fee Evaluation stale draft message remains visible and stale values are not applied.

Validation commands:

```powershell
py -m pytest tests/unit/test_matrix_editor_session_service.py tests/integration/test_matrix_editor_session_api.py -q
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q
cd frontend
npm test -- --run MatrixEditorWorkspace FeeEvaluationReviewExportPage --watch=false
npm run build
cd ..
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "matrix_editor or fee"
```

## Risks

- Autosave can produce excessive writes if not debounced and signature-gated.
- Matrix draft discard must physically delete only the current non-authority draft aggregate and must not delete active Confirmed Matrix authority.
- Fee discard must not remove historical/stale drafts unexpectedly.
- UI must not let users confirm while autosave is failed or pending.
- Existing Matrix Editor session flow is large; implementation should keep changes localized to draft lifecycle and avoid broad UI refactor.

## Review Checklist Before Implementation

- Confirm TASK_313 ordering or explicitly reprioritize TASK_314 on the task board.
- Confirm `Cancel` means discard draft, not simply leave page.
- Confirm 800 ms debounce is acceptable for both Matrix and Fee.
- Confirm no draft history/audit is required in V1.

## Stop Point

After user review, stop unless explicit implementation approval is given. Implementation must update `docs/task_board.md` only after approved execution and validation.
