# TASK_278_MATRIX_EDITOR_TEMPORARY_SESSION_FLOW

## Status

Planned. Awaiting user review and explicit approval before implementation.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Allowed Reason

TASK_277 is complete and `docs/task_board.md` currently has no active implementation task. This task is a controlled follow-up created from Matrix Editor smoke feedback and user-approved product direction: Matrix Editor should behave as a temporary editing session, not as a visible draft/revision management screen.

## Objective

Refactor Matrix Editor into a temporary Matrix editing session:

```text
Workbench Active Matrix -> temporary editor session -> Confirm Matrix -> new Workbench Active Matrix
                                |
                                +-> Cancel -> discard session and return
```

Users must not need to understand `revision draft`, persisted draft lineage, stale draft state, backend draft IDs, or version routing. The visible workflow should be:

- enter Matrix Editor from Workbench
- edit the Matrix currently shown in Workbench
- use source-backed `Change selected Groups` when needed
- choose `Cancel` to discard this editing session
- choose `Confirm Matrix` to publish the current editor content back to Workbench

## User Feedback Source

This task is based on the post-TASK_277 Matrix Editor discussion:

- `Confirm As Active Matrix` is too technical and confusing.
- Users understand `Confirm`, `OK`, or `Confirm Matrix` better than authority/version wording.
- `Confirm` and `Cancel` should live together as page completion actions, preferably at the right side or bottom-right.
- `Back to Workbench` looks like a link and does not communicate discard/cancel semantics.
- Users normally enter Matrix Editor to modify the Matrix currently displayed in Workbench.
- Closing or exiting without confirming should not restore an old saved draft next time.
- Next entry should start from the current Workbench Active Matrix.
- However, the editor session must retain the full source Matrix snapshot behind the Active Matrix, because `Change selected Groups` needs all groups from the original Word-parsed Matrix, not only the groups currently published in Workbench.

## Product Decision

TASK_278 adopts this rule:

```text
No user-visible saved draft restore flow.
```

Matrix Editor may use internal backend draft or snapshot records as implementation details during publish, but:

- entering Matrix Editor must not default to an old persisted draft
- `Cancel` must discard the current editor session from the user's point of view
- closing the page or leaving mid-edit must not cause the next entry to resume those edits
- next entry must rebuild from the current Workbench Active Matrix plus its full source Matrix snapshot
- historical versions remain read-only future scope, not part of the default editing path

## Scope

### In Scope

1. Rename the visible publish action from `Confirm As Active Matrix` to `Confirm Matrix`.
2. Replace `Back to Workbench` with a visible secondary `Cancel` button.
3. Place `Cancel` and `Confirm Matrix` together as page completion actions, visually separated from import/group editing tools.
4. Treat Matrix Editor as a temporary in-memory editing session after initial load.
   - Do not auto-load old persisted project matrix drafts as the user's current editor state.
   - Do not use persisted draft updated time as the default "resume" source.
5. On Matrix Editor entry with an active Matrix:
   - load the current active ConfirmedMatrix authority
   - load the full SourceMatrix snapshot behind that authority
   - initialize the visible editor from the active authority content
   - initialize group-selection choices from the full SourceMatrix snapshot
   - mark currently active authority groups as selected by default
6. On Matrix Editor entry with no active Matrix:
   - initialize an empty local editor session or a clear import-first state
   - keep `Change selected Groups` disabled until a source snapshot exists
7. `Change selected Groups` must always use the current editor session's full source Matrix snapshot.
   - For active-authority sessions, source choices come from the original source snapshot behind the active Matrix.
   - For `Change Source Matrix` sessions, source choices come from the newly parsed Word Matrix preview.
   - If an active authority exists but its original source snapshot cannot be loaded, the editor may show and edit the currently active selected Matrix content, but `Change selected Groups` must be disabled and the UI must show business-readable guidance: `Original source Matrix is unavailable. Use Change Source Matrix to reselect groups.`
8. `Change Source Matrix` replaces the current editor session source.
   - It should not expose backend draft/revision concepts.
   - It should not make the next Matrix Editor entry resume this unconfirmed import automatically.
9. `Cancel` behavior:
   - if no local changes, return to Workbench
   - if local changes exist, ask for discard confirmation using business-readable copy
   - after discard, return to Workbench
   - do not publish
   - do not make this session the next default editor load
10. `Confirm Matrix` behavior:
    - validate that the session has at least one selected group and one step token
    - compare against the current active authority baseline when one exists
    - if unchanged, show `No Matrix changes to confirm.`
    - if changed, publish as the new active Matrix and return to Workbench
    - if the active Matrix changed since the session opened, show `Matrix was updated. Reload the latest Matrix to continue.` and do not show raw stale/revision wording
11. Fix the no-change publish contract as one protocol:
    - `POST /api/projects/{project_id}/matrix-editor/session/confirm` returns HTTP 200 with `publish_status: "no_change"` and message `No Matrix changes to confirm.`
    - frontend tests must not accept 409/422 for no-change
12. Introduce a minimal backend/API contract if needed to keep the frontend clean:
    - an editor seed/read endpoint for active authority plus full source snapshot
    - a confirm-session endpoint that converts session payload into a confirmed Matrix using internal draft/revision mechanics
    - no new database tables unless implementation review proves an unavoidable need
13. Preserve Matrix import preview, group selection, token parsing, note/sample display, and Workbench projection behavior unless explicitly changed by this task.
14. Preserve the existing right-side Group Step Workspace structure and behavior except for syncing it to the temporary editor session selection state.
15. Add regression tests and static guards to prevent reintroducing user-visible `revision draft`, `Create Revision Draft`, raw stale wording, or default persisted-draft resume behavior.

### Out Of Scope

Do not implement in TASK_278:

- historical version picker UI
- cross-project Matrix import UI
- saved draft restore/resume UI
- multi-user collaboration or locking
- permissions or approval workflow
- StepInstance or execution persistence
- image/evidence/test-data persistence
- Test Record generation placement
- report generation
- fee calculation
- AI or automated judgement
- broad Matrix grid redesign
- destructive cleanup of existing historical draft records

Existing persisted draft records may remain in storage for lineage or compatibility, but they must not define the default user-facing Matrix Editor entry state.

## Expected Files

Likely backend files:

- `backend/application/confirmed_matrix_authority_service.py`
- `backend/application/matrix_editor_session_service.py` or equivalent narrowly named service
- `backend/api/routes_matrix_editor_session.py` or equivalent route module
- `backend/api/dependencies.py`
- `backend/api/main.py`
- `backend/infrastructure/storage/repositories/source_matrix_import.py`
- `backend/infrastructure/storage/repositories/project_matrix_draft.py`

Likely frontend files:

- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx`
- `frontend/src/features/matrix-editor/matrixImportSessionModel.ts`
- `frontend/src/features/matrix-editor/matrixWorkspaceClarityModel.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/workbench.css`

Likely tests:

- `tests/unit/test_matrix_editor_session_service.py`
- `tests/integration/test_matrix_editor_session_api.py`
- `tests/unit/test_frontend_shell_files.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

Task tracking:

- `tasks/TASK_278_MATRIX_EDITOR_TEMPORARY_SESSION_FLOW.md`
- `docs/task_278_matrix_editor_temporary_session_flow_plan.md`
- `docs/task_board.md`
- `docs/task_plan_index.md`

## Acceptance Criteria

1. Matrix Editor no longer shows `Confirm As Active Matrix`; it shows `Confirm Matrix`.
2. Matrix Editor no longer shows `Back to Workbench`; it shows a visible `Cancel` button.
3. `Cancel` and `Confirm Matrix` are visually grouped as completion actions, separated from `Change Source Matrix`, `Change selected Groups`, import, and Undo tools.
4. Entering Matrix Editor with an active Matrix initializes from the current Workbench Active Matrix, not from the newest persisted Matrix draft.
5. Entering Matrix Editor after closing/canceling an unconfirmed session does not resume those edits.
6. The editor session keeps the full source Matrix snapshot associated with the active authority.
7. `Change selected Groups` shows all source groups from the session source snapshot, including groups not currently published in Workbench.
8. If active authority exists but its full source snapshot is unavailable, Matrix Editor still opens the currently active selected Matrix content, disables `Change selected Groups`, and shows `Original source Matrix is unavailable. Use Change Source Matrix to reselect groups.`
9. With no active Matrix and no source seed, `Change selected Groups` is disabled until a source Matrix exists.
10. `Change Source Matrix` replaces the current temporary session source and group-selection choices without making an unconfirmed import the next default editor load.
11. `Cancel` with local changes asks for discard confirmation and returns to Workbench without publishing.
12. `Cancel` without local changes returns to Workbench directly.
13. `Confirm Matrix` publishes changed session content and returns to Workbench.
14. Workbench Matrix projection refreshes from the newly active Matrix after successful confirm.
15. `Confirm Matrix` no-change behavior uses one fixed API contract: HTTP 200 with `publish_status: "no_change"` and message `No Matrix changes to confirm.`
16. `Confirm Matrix` does not create a new active Matrix when the session content is unchanged.
17. Raw user-visible backend phrases are not shown:
    - `revision draft`
    - `Create Revision Draft`
    - `Confirm Revision`
    - `Revision draft is stale relative to current active confirmed matrix.`
18. Stale active-authority conflicts are translated to business-readable copy:
    - `Matrix was updated. Reload the latest Matrix to continue.`
19. The existing right-side Group Step Workspace is preserved. TASK_278 may only update its selected group/step context to match the temporary editor session.
20. The task does not introduce StepInstance, report, fee, image, evidence, permission, AI, or multi-user scope.

## Validation Plan

Frontend:

```powershell
cd frontend
npm test -- --run MatrixEditorWorkspace
npm run build
```

Backend:

```powershell
py -m pytest tests\unit\test_matrix_editor_session_service.py -q
py -m pytest tests\integration\test_matrix_editor_session_api.py -q
```

Existing smoke and static guards:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task278 or task277 or matrix_editor"
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
py -m pytest tests\integration\test_confirmed_matrix_authority_api.py -q
git diff --check
```

Manual browser smoke:

```text
http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f
```

Check:

- enter Matrix Editor from Workbench
- verify visible actions are `Cancel` and `Confirm Matrix`
- verify no revision/draft wording leaks into the UI
- open `Change selected Groups` and verify all source groups are available
- cancel after editing and return to Workbench
- re-enter Matrix Editor and verify canceled edits are not resumed
- edit again, confirm, return to Workbench
- verify Workbench projection reflects the confirmed Matrix

## Model Fit Assessment

`GPT-5.3-codex` is suitable for execution.

Reason:

- The task requires careful cross-layer state-flow refactoring and test coverage, which matches the coding model's strengths.
- The work is bounded to Matrix Editor, Matrix authority/source snapshot read models, and publish routing.
- The risk is not algorithmic complexity but product semantics and persistence boundaries; this can be controlled through a written plan, targeted backend/API tests, frontend interaction tests, and manual browser smoke.

## Review Notes

Before implementation, reviewer should confirm:

- `Cancel` truly means discard this editor session, not save for later.
- Next entry always starts from current Workbench Active Matrix.
- Full source snapshot lineage is required for `Change selected Groups`.
- It is acceptable for backend to use internal draft records during confirm as long as they are not user-visible and not used as default resume state.
