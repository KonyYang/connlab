# TASK_314A Matrix Editor Draft Persistence Plan

Status: Planned. Task scope accepted for review; awaiting explicit user approval before implementation.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_314A_MATRIX_EDITOR_DRAFT_PERSISTENCE` is the narrowed execution slice split from the larger TASK_314 umbrella.

This plan is documentation-only. It prepares a reviewable Matrix-only implementation path and does not authorize coding by itself. Implementation must wait for explicit user approval after this plan is reviewed.

## Why This Task Is Allowed Now

The original TASK_314 combined two separable subsystems:

- Matrix Editor draft persistence and Confirm Matrix saved-draft gating.
- Fee Evaluation pricing draft autosave and Confirm Fee UI gating.

The completed task series shows that TASK_315 depends on Matrix draft lifecycle, not Fee autosave:

- TASK_308 established Confirmed Fee authority from saved pricing drafts.
- TASK_309 wired Confirm Fee with current pricing draft guards.
- TASK_310 through TASK_312 connected Confirmed Matrix/Fee to downstream outputs.
- TASK_318 through TASK_321 established Project Folder readiness and Required forms generation around current authority states.

Therefore TASK_314A narrows the immediate prerequisite to Matrix Editor draft persistence only. Fee autosave remains deferred to TASK_314B.

## Step 1: Task Understanding

Goal:

- Preserve unfinished Matrix Editor edits as a background non-authority draft.
- Restore that draft on Matrix Editor re-entry while the active Confirmed Matrix context is unchanged.
- Make `Cancel` discard the current Matrix editor draft.
- Make `Confirm Matrix` publish only a successfully autosaved draft verified by draft id and payload signature.

Inputs:

- Project id.
- Active Confirmed Matrix id/revision.
- Matrix Editor editable payload: groups, rows, cells, selected groups, sample quantities, schedule fields, and source lineage fields already used by the existing session/confirm flow.
- Last saved Matrix draft id/signature from autosave response.

Outputs:

- Current non-authority Matrix editor draft bound to the active Confirmed Matrix context.
- Saved payload signature for frontend/backend confirm gating.
- Confirmed Matrix authority revision only after explicit `Confirm Matrix`.
- Discard response for current draft removal.

Involved modules:

- `backend/application/matrix_editor_session_service.py`
- `backend/application/project_matrix_draft_persistence_service.py`
- `backend/infrastructure/storage/repositories/project_matrix_draft.py`
- `backend/api/routes_matrix_editor_session.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `tests/unit/test_matrix_editor_session_service.py`
- `tests/integration/test_matrix_editor_session_api.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx` or the existing Matrix Editor Vitest file
- `tests/unit/test_frontend_shell_files.py`

Not allowed:

- No Fee Evaluation autosave or Confirm Fee behavior change.
- No Matrix-to-Fee rebase.
- No ProjectOutputRecord change.
- No Confirmed Matrix schema rewrite.
- No Office gateway change.
- No package execute, public-drive publish, StepInstance, report, AI, permissions, LAN/server sync, multi-user, or draft-history UI.

## Step 2: Backend Design

### Session Seed Restore

Extend the Matrix Editor session seed application result with:

```text
editor_draft_id: str | None
draft_status: Literal["missing", "current", "stale"]
loaded_source: Literal["authority", "draft"]
stale_draft_present: bool
draft_updated_at: datetime | None
saved_payload_signature: str | None
```

Behavior:

- Resolve project and active Confirmed Matrix through the existing Matrix Editor session service boundary.
- If no active Confirmed Matrix exists, return the existing first-authority editor session behavior with draft metadata set to missing/null.
- If active Confirmed Matrix exists, query Matrix drafts bound to that active Confirmed Matrix id/revision.
- Choose the current draft deterministically by latest `updated_at`, then stable id as tie-breaker.
- Load the chosen draft aggregate into the same editor payload shape used by the session response.
- Use `loaded_source = "draft"` only when the editor payload is loaded from a current draft.
- Use `loaded_source = "authority"` when the editor payload is loaded from the active Confirmed Matrix baseline.
- Use `stale_draft_present = true` to warn that older-context drafts exist.
- Do not set the editor into a blocking stale state when stale drafts were not applied and the actual loaded source is the authority baseline.
- Return stale metadata only as an operational warning; do not apply stale drafts to the editor.

Repository requirement:

- Add or reuse a method that loads the full Project Matrix Draft aggregate by `project_matrix_draft_id`.
- Add or reuse a method that lists current non-authority drafts by project id plus active Confirmed Matrix context.
- Do not implement draft history UI or broad cleanup of old stale drafts.

### Draft Autosave

Add an application service method on the Matrix Editor session boundary:

```text
save_editor_draft(project_id, payload) -> MatrixEditorDraftSaveResult
```

Behavior:

- Require project existence.
- Resolve active Confirmed Matrix.
- If no active Confirmed Matrix exists, reject autosave with an actionable not-ready error or return a not-supported result that the API maps consistently.
- Normalize the same Matrix Editor payload used by confirm.
- Compute `saved_payload_signature` from the normalized payload.
- Save or update one current Matrix draft for the project plus active Confirmed Matrix context.
- Return draft id, active Confirmed Matrix id/revision, updated timestamp, status, and signature.

Signature rule:

- The signature must be stable for semantically identical normalized payloads.
- It must cover all editor fields that affect Confirmed Matrix authority output.
- It must not include volatile timestamps.

### Confirm Matrix Gate

Extend the confirm application request with:

```text
expected_editor_draft_id: str | None
expected_saved_payload_signature: str | None
```

Behavior:

- For existing-active-Matrix edit sessions, require both fields.
- Reload the saved draft by `expected_editor_draft_id`.
- Verify project id, active Confirmed Matrix id, and active Confirmed Matrix revision.
- Recompute or read the saved payload signature and compare it to `expected_saved_payload_signature`.
- Publish from the saved draft snapshot.
- Do not use a newer request payload as an implicit final save source.
- Keep first-authority/no-active-Matrix confirm behavior compatible with the existing short-session path.
- For existing-active-Matrix sessions loaded from authority baseline with no user edits and no current draft token, do not require creating a draft only to confirm no change.
- V1 should disable `Confirm Matrix` as a no-op/no-change in that state. If existing no-change compatibility is reused instead, tests must prove it does not create an unnecessary authority revision and does not bypass the draft-token requirement for changed payloads.
- For any changed payload, confirm requires a successful autosave of that exact payload and matching expected draft id/signature.

### Draft Discard

Add an application service method:

```text
discard_editor_draft(project_id) -> MatrixEditorDraftDiscardResult
```

Behavior:

- Resolve active Confirmed Matrix.
- Find the current draft for project plus active Confirmed Matrix context.
- If none exists, return `discarded=false` without error.
- Accept expected discard tokens when the frontend has them:
  - `expected_editor_draft_id`
  - `expected_saved_payload_signature`
- If expected tokens are provided and do not match the current draft, reject discard with a conflict instead of deleting a different newer draft.
- Before deleting, verify the draft is not referenced by Confirmed Matrix authority/version/history/source lineage.
- Delete only the current non-authority draft aggregate and its children.
- Do not delete stale drafts from older authority contexts in TASK_314A.
- Return discarded status and active Confirmed Matrix identity.

## Step 3: API / DTO Design

Extend `GET /api/projects/{project_id}/matrix-editor/session` response with:

```text
editor_draft_id
draft_status
loaded_source
stale_draft_present
draft_updated_at
saved_payload_signature
```

Add:

```text
PUT /api/projects/{project_id}/matrix-editor/session/draft
DELETE /api/projects/{project_id}/matrix-editor/session/draft
```

`PUT` request:

- Same Matrix Editor business payload as confirm, excluding `confirmed_by`.
- Frontend may keep compatibility fields already used by existing DTOs, but backend must normalize them before persistence/signature generation.

`PUT` response:

```text
editor_draft_id
draft_status
draft_updated_at
saved_payload_signature
active_confirmed_matrix_id
active_confirmed_matrix_revision
```

`DELETE` response:

```text
discarded
active_confirmed_matrix_id
active_confirmed_matrix_revision
```

`DELETE` request/query/body must carry expected tokens when known:

```text
expected_editor_draft_id
expected_saved_payload_signature
```

If both expected tokens are missing because no draft has ever been saved, discard may return `discarded=false`. If expected tokens are present and stale, the backend must return a conflict and must not delete a newer draft.

Confirm request additions:

```text
expected_editor_draft_id
expected_saved_payload_signature
```

## Step 4: Frontend Design

### Autosave State

Add Matrix Editor local save state:

```text
idle | dirty | saving | saved | failed | stale
```

Operator-facing text:

```text
Editing
Saving...
Saved
Save failed
Draft stale
```

Behavior:

- Skip autosave during initial session load.
- Build one normalized payload for autosave and confirm.
- Compute or receive a payload signature to compare current UI state with last saved state.
- Debounce autosave by 800 ms after editable changes.
- Track a per-editor-session autosave generation so responses from older/cancelled generations are ignored.
- Keep edits in memory when autosave fails.
- Retry through the same autosave path after later edits or explicit retry if the existing UI pattern supports it.

### Confirm Matrix

Disable `Confirm Matrix` when:

- Initial session is loading.
- Payload is dirty and not yet saved.
- Autosave is pending.
- Autosave failed.
- The loaded editor draft itself is stale.
- Current UI signature does not match last successful saved signature.

Do not disable `Confirm Matrix` merely because `stale_draft_present=true` when `loaded_source="authority"` and stale old drafts were not applied to the editor.

If the editor loaded from authority baseline and no edits have been made, V1 should show `Confirm Matrix` disabled as no-change/no-op rather than force a draft save. If existing no-change compatibility is retained, add tests proving it does not publish an extra authority revision.

When enabled, send:

```text
expected_editor_draft_id
expected_saved_payload_signature
```

Do not call autosave as a hidden side effect of Confirm Matrix.

### Cancel

Behavior:

- If no current draft/current changes exist, return to Workbench.
- If there is a current draft or dirty editor state, ask for discard confirmation using existing confirmation patterns.
- On confirmed Cancel, immediately clear the debounce timer and enter a `cancelling` state that prevents any new autosave scheduling.
- If an autosave request is in flight, either wait for it to settle and then discard the latest saved token, or abort it before it reaches the backend. If the abort cannot prove the backend did not receive the request, wait for settlement or refresh the latest draft token before discard.
- Ignore late autosave responses after `cancelling` starts. They must not update `lastSavedSignature`, re-enable Confirm, or navigate the page.
- Call `DELETE /matrix-editor/session/draft` with `expected_editor_draft_id` and `expected_saved_payload_signature` when a draft token is known.
- Return to Workbench after discard succeeds or no current draft exists.
- Keep the operator on the editor and show an actionable error if discard fails because the draft is authority-referenced.
- Keep the operator on the editor and show an actionable error if discard fails because expected tokens no longer match the current draft.
- Add a regression test for edit-then-immediate-Cancel and pending-autosave-then-Cancel so a late autosave cannot recreate the discarded draft.

## Step 5: Testing Plan

Backend tests:

- Session seed returns active authority-derived baseline when no current Matrix draft exists.
- Session seed returns and applies the current saved draft when one exists.
- Session seed ignores stale drafts from older active authority contexts.
- Session seed reports `loaded_source="authority"` plus `stale_draft_present=true` without applying or blocking on old stale drafts.
- Autosave binds the draft to active Confirmed Matrix id/revision.
- Autosave updates one current draft instead of creating a new current draft per edit.
- Autosave is not enabled for first-authority/no-active-Matrix editing.
- Discard deletes the current non-authority draft and next seed returns the authority baseline.
- Discard refuses authority-referenced draft deletion.
- Discard with stale/mismatched expected draft id or signature returns conflict and does not delete a newer draft.
- Edit followed immediately by Cancel cannot leave a recreated draft after debounce/in-flight autosave settles.
- Confirm Matrix accepts a matching saved draft id/signature.
- Confirm Matrix rejects mismatched draft id.
- Confirm Matrix rejects mismatched saved payload signature.
- Confirm Matrix does not publish a newer unsaved request payload.
- Confirm Matrix no-change behavior is explicit: authority-baseline with no edits either keeps Confirm disabled or uses a tested no-change path that does not create an authority revision.

Frontend tests:

- Matrix Editor autosaves after an edit and shows saved state.
- Matrix Editor blocks Confirm Matrix while autosave is pending.
- Matrix Editor blocks Confirm Matrix after autosave failure.
- Matrix Editor sends expected draft id/signature after successful autosave.
- Matrix Editor does not call draft save as a hidden Confirm Matrix side effect.
- Matrix Editor loaded from authority baseline with stale old-draft warning does not enter blocking stale UI.
- Matrix Editor disables Confirm Matrix as no-change/no-op when no draft exists and no edits were made, unless the tested existing no-change path is intentionally retained.
- Matrix Editor cancel calls discard endpoint and navigates back.
- Matrix Editor cancel clears pending debounce and ignores late autosave responses.
- Matrix Editor cancel sends expected draft id/signature when known.
- Matrix Editor re-entry renders restored draft values from session seed.

Validation commands:

```powershell
py -m pytest tests/unit/test_matrix_editor_session_service.py tests/integration/test_matrix_editor_session_api.py -q
cd frontend
npm test -- --run MatrixEditorWorkspace --watch=false
npm run build
cd ..
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "matrix_editor"
```

Regression guard:

```powershell
py -m pytest tests/unit/test_official_project_folder_check_service.py tests/unit/test_project_folder_required_forms_service.py -q
```

## Risks

- Autosave can create excessive writes if debounce and signature gating are incomplete.
- Cancel and autosave can race: a pending debounce or in-flight PUT can recreate a draft after DELETE unless cancelling clears timers, blocks new autosave scheduling, waits/aborts in-flight saves, ignores late responses, and discards with expected tokens.
- Confirm Matrix can accidentally reintroduce hidden save-on-confirm behavior if the implementation keeps using request payload as authority source.
- `draft_status="stale"` can be misread as a UI-blocking state even when stale old drafts were not loaded. Use `loaded_source` and `stale_draft_present` to separate loaded payload source from stale warning metadata.
- Active authority baseline with no current draft can create ambiguous Confirm behavior. TASK_314A must explicitly choose disabled no-change or a tested no-change compatibility path.
- Draft discard can be destructive if it does not verify non-authority status and authority references.
- Existing Matrix Editor session code is large; implementation must stay localized to draft lifecycle.
- Current worktree may already contain partial full-TASK_314 implementation changes. Those changes must be reviewed against TASK_314A and reduced if they include Fee Evaluation autosave scope.

## Review Checklist Before Implementation

- Confirm TASK_314A is the only implementation scope.
- Confirm TASK_314B Fee autosave is deferred.
- Confirm 800 ms debounce is acceptable.
- Confirm route-leave behavior: dirty/pending Matrix edits should either block navigation or require explicit Cancel discard.
- Confirm first-authority/no-active-Matrix editing remains compatible with the existing short-session behavior.
- Confirm Confirm Matrix must use saved draft id/signature and must not perform implicit final save.

## Stop Point

After this plan is reviewed, stop unless explicit implementation approval is given.

After implementation starts, stop after TASK_314A validation and task board update. Do not proceed to TASK_314B, TASK_314C, TASK_315, package execution, StepInstance, reporting, AI, permissions, or multi-user scope.
