# TASK_314A_MATRIX_EDITOR_DRAFT_PERSISTENCE

Status: Planned. Task scope accepted for review; awaiting explicit user approval before implementation.

Executable plan: `docs/task_314a_matrix_editor_draft_persistence_plan.md`

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

TASK_314A is the narrowed Matrix-only execution slice split out from `TASK_314_MATRIX_AND_FEE_BACKGROUND_DRAFT_PERSISTENCE`.

TASK_314A is the real prerequisite for `TASK_315_MATRIX_DRAFT_TO_FEE_DRAFT_INCREMENTAL_REBASE`, because TASK_315 depends on Matrix Editor background draft persistence, Matrix draft discard, and Confirm Matrix saved-draft gating. Fee Evaluation autosave is useful for workflow consistency, but it is not required before TASK_315.

Any existing unverified worktree changes that attempted the full TASK_314 scope must be reviewed against this narrowed TASK_314A contract before they are continued or accepted. Do not treat partial full-TASK_314 implementation as completed TASK_314A until the validation below passes.

## Goal

Implement a Matrix Editor draft lifecycle:

- User edits to an existing active Confirmed Matrix are autosaved in the background as a non-authority Matrix draft.
- Matrix Editor re-entry restores the current autosaved draft for the active Confirmed Matrix context.
- `Cancel` discards the current Matrix editor draft and returns the operator to the active Confirmed Matrix baseline.
- `Confirm Matrix` publishes only the latest successfully autosaved Matrix draft, guarded by backend-checkable draft id and payload signature.

The task must preserve the authority distinction:

```text
autosaved Matrix draft = non-authority working copy
Confirmed Matrix = authority version, created only by explicit Confirm Matrix
```

## Current Code Reality

- Matrix Editor loads through `GET /api/projects/{project_id}/matrix-editor/session`.
- Matrix Editor currently confirms through `POST /api/projects/{project_id}/matrix-editor/session/confirm`.
- Matrix draft persistence infrastructure already exists, but the editor session flow is not yet a complete background draft lifecycle.
- Fee Evaluation has separate pricing draft persistence and Confirm Fee behavior; TASK_314A must not change it.
- Project Folder readiness from TASK_318/TASK_320/TASK_321 depends on active Confirmed Matrix/Confirmed Fee authority and must not be regressed.

## V1 Contract

### Session Seed Restore

- Session seed returns draft metadata:
  - `editor_draft_id`
  - `draft_status`
  - `loaded_source`
  - `stale_draft_present`
  - `draft_updated_at`
  - `saved_payload_signature`
- If a current non-authority Matrix draft exists for the active Confirmed Matrix id/revision, Matrix Editor opens that draft.
- If no current draft exists, Matrix Editor opens the active Confirmed Matrix-derived baseline.
- If no active Confirmed Matrix exists, TASK_314A keeps the existing first-authority short-session behavior and does not enable autosave.
- Stale drafts from older active authority contexts must not be applied to the editor.
- Stale draft presence is a warning/metadata condition, not the loaded editor state. If the editor loads the active Confirmed Matrix baseline, `loaded_source` must be `authority` and Confirm must not be blocked merely because stale older drafts exist.
- If inconsistent storage contains multiple non-authority drafts for the same active context, the seed path must choose the latest deterministically and treat the others as stale/non-current.

### Draft Autosave

- Editing Matrix groups/rows/cells, selected groups, sample quantities, and schedule fields marks the page dirty.
- After 800 ms debounce, the frontend saves the current editor payload to the backend.
- Autosave updates one current draft per project plus active Confirmed Matrix context; it must not create a new current draft on every edit.
- Autosave response includes:
  - `editor_draft_id`
  - `draft_status`
  - `draft_updated_at`
  - `saved_payload_signature`
  - active Confirmed Matrix id/revision
- The frontend must skip autosave during initial seed load and when the current payload signature already matches the last saved signature.

### Confirm Matrix Gate

- `Confirm Matrix` is disabled while autosave is dirty, pending, failed, or the loaded editor draft itself is stale.
- `Confirm Matrix` sends:
  - `expected_editor_draft_id`
  - `expected_saved_payload_signature`
- Backend confirm reloads the saved draft by `expected_editor_draft_id`, validates it belongs to the current active Confirmed Matrix id/revision, and validates the saved payload signature.
- Backend confirm must reject stale or mismatched draft tokens.
- Backend confirm must not silently save a newer UI payload during confirm.
- Confirm publishes the saved draft through the existing Confirmed Matrix authority path.
- If an existing active Confirmed Matrix opens from authority baseline and the user makes no changes, the frontend must not force creation of a draft. V1 should disable `Confirm Matrix` as no-op/no-change, or keep the existing no-change compatibility path only if tests prove it already exists and does not create authority noise.
- If the user makes any change, `Confirm Matrix` remains unavailable until that changed payload has autosaved successfully and has matching draft id/signature tokens.

### Cancel / Discard

- `Cancel` means discard the current non-authority Matrix editor draft for the active Confirmed Matrix context.
- Before calling discard, the frontend must clear any debounce timer and enter a cancelling state that prevents new autosave scheduling.
- If an autosave request is in flight, Cancel must either wait for it to settle and then discard the latest saved draft token, or abort it before it reaches the backend. Late autosave responses after cancelling must be ignored by the UI and must not re-enable Confirm.
- Discard must carry backend-checkable expected draft identity, at minimum `expected_editor_draft_id` and `expected_saved_payload_signature` when a draft token is known. Backend discard must reject mismatched expected tokens rather than deleting an unrelated newer draft.
- Discard must never delete Confirmed Matrix authority records.
- Discard must never delete a draft aggregate referenced by any Confirmed Matrix version/history/source lineage.
- After discard completes, no pending autosave from the cancelled editor session may recreate the draft. Re-entry must open the active Confirmed Matrix-derived baseline.

## Suggested API / DTO Changes

New Matrix Editor draft endpoints:

```text
PUT /api/projects/{project_id}/matrix-editor/session/draft
DELETE /api/projects/{project_id}/matrix-editor/session/draft
```

Matrix session seed response additions:

```text
editor_draft_id: string | null
draft_status: "missing" | "current" | "stale"
loaded_source: "authority" | "draft"
stale_draft_present: boolean
draft_updated_at: string | null
saved_payload_signature: string | null
```

Matrix confirm request additions:

```text
expected_editor_draft_id: string | null
expected_saved_payload_signature: string | null
```

Matrix discard request additions:

```text
expected_editor_draft_id: string | null
expected_saved_payload_signature: string | null
```

## In Scope

- Backend Matrix Editor session draft save behavior.
- Backend Matrix Editor session draft restore behavior.
- Backend Matrix Editor draft discard behavior.
- Backend Confirm Matrix draft id/signature validation.
- Thin API routes and typed frontend API client DTOs for Matrix draft lifecycle only.
- Matrix Editor autosave state, status text, confirm blocking, cancel discard, and draft restore behavior.
- Focused pytest and Vitest coverage for Matrix Editor only.
- Static frontend shell guard updates if needed for Matrix Editor copy/contracts.
- Task board update after implementation approval, validation, and completion.

## Out Of Scope

- No Fee Evaluation autosave, pricing draft discard endpoint, Save button removal, or Confirm Fee UI changes. Those belong to TASK_314B.
- No Matrix Draft -> Fee Draft incremental rebase, no Fee row add/remove preservation, and no Fee migration across Matrix structural edits. Those belong to TASK_315.
- No TASK_313 package execution work.
- No ProjectOutputRecord changes.
- No Confirmed Matrix authority schema rewrite.
- No Confirmed Fee authority schema or behavior changes.
- No StepInstance, execution persistence, evidence/image handling, report engine, AI review, permissions, LAN/server sync, multi-user merge, or draft-history UI.
- No Office gateway changes unless a failing Matrix-specific test proves a direct dependency.
- No automatic conversion of drafts into authority. Authority changes only through explicit `Confirm Matrix`.

## Acceptance Criteria

- Matrix Editor re-entry restores current background Matrix draft edits for the active Confirmed Matrix context.
- Matrix Editor opens the active Confirmed Matrix-derived baseline when no current draft exists.
- Matrix Editor V1 autosave is enabled only when an active Confirmed Matrix already exists.
- Matrix Editor autosave updates one current draft for the active authority context instead of creating a new current draft per edit.
- Matrix Editor autosave returns a saved payload signature.
- Matrix Editor `Confirm Matrix` cannot proceed while autosave is dirty, pending, failed, or the loaded editor draft itself is stale.
- Matrix Editor `Confirm Matrix` is disabled or no-op-compatible when the page loaded from authority baseline and no edits have been made.
- Matrix Editor stale old-draft metadata does not block Confirm when the editor is actually loaded from authority baseline and no stale draft was applied.
- Matrix Editor `Confirm Matrix` rejects mismatched `expected_editor_draft_id`.
- Matrix Editor `Confirm Matrix` rejects mismatched `expected_saved_payload_signature`.
- Matrix Editor `Confirm Matrix` does not silently save a newer unsaved UI payload.
- Matrix Editor `Cancel` discards the current non-authority draft and returns to Workbench.
- Matrix Editor `Cancel` clears pending debounce work and prevents in-flight or late autosave responses from recreating the discarded draft.
- Matrix Editor `Cancel` sends expected draft id/signature when known and backend discard rejects mismatched tokens.
- Matrix Editor `Cancel` never deletes Confirmed Matrix authority or authority-referenced draft lineage.
- Existing TASK_308-TASK_312 Confirmed Matrix/Fee authority behavior remains intact.
- Existing TASK_318 Official project folder check, TASK_320 single-task Workbench UI, and TASK_321 Required forms readiness remain intact.

## Required Validation

```powershell
py -m pytest tests/unit/test_matrix_editor_session_service.py tests/integration/test_matrix_editor_session_api.py -q
```

```powershell
cd frontend
npm test -- --run MatrixEditorWorkspace --watch=false
```

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "matrix_editor"
```

Recommended regression guard:

```powershell
py -m pytest tests/unit/test_official_project_folder_check_service.py tests/unit/test_project_folder_required_forms_service.py -q
```

## Stop Point

Stop after TASK_314A implementation, validation, and task board update.

Do not proceed to TASK_314B, TASK_314C, TASK_315, package execution, StepInstance, reporting, AI, permissions, or multi-user scope without separate explicit approval.
