# TASK_360C Matrix Contact Plan Revision-Draft Enablement Developer Evidence

Status: ready_for_review
Task: `TASK_360C_MATRIX_CONTACT_PLAN_REVISION_DRAFT_ENABLEMENT`
Lane: `matrix-contact-plan-revision-draft-enablement`
Date: 2026-07-11
Role: Developer

## Gate

Developer implementation complete pending Reviewer implementation gate. The change stays within the authorized Matrix Editor bridge; no backend, API client, schema, or authority contract changed.

Current phase: Phase 11, Project Workbench / Matrix / Approval Package controlled foundation.
Current active task: `TASK_360C_MATRIX_CONTACT_PLAN_REVISION_DRAFT_ENABLEMENT`.
Why allowed: the board records TASK_360C as implementation authorized after Reviewer implementation-readiness and user-approved source-of-truth reconciliation.

## Repository Facts Confirmed

- `createMatrixRevisionDraft(projectId)` is already the typed frontend helper for `POST /api/projects/{project_id}/matrix-revisions`; no client contract change is necessary.
- The revision endpoint returns `201` for creation and `409` when the current confirmed Matrix already has a revision draft.
- `MatrixEditorWorkspace` already loads `fetchMatrixEditorSession(projectId)`, applies `editor_draft`, stores `savedEditorDraftId`, and fetches draft Step quantities through its existing id-based effect. Without an id, it intentionally clears `stepQuantityItems`.
- The existing revision service calls `carry_forward_step_quantities()`, which carries the confirmed `contact_plan` structured metadata into the revision draft.
- The current Contact Measurement Plan is draft-only for mutation. TASK_360B workbook preview/generation remains confirmed-snapshot-only, and Fee/generic Test Record remain downstream confirmed consumers.

## Implemented Behavior

1. `MatrixEditorWorkspace` renders a compact inline `Open editable Matrix draft` action only for an active confirmed Matrix with no current editor draft.
2. The action uses the existing typed `createMatrixRevisionDraft(projectId)` helper. It performs no local projection merge and creates no new client/API contract.
3. A `201` increments a local reload generation; the existing session-seed effect reloads `fetchMatrixEditorSession(projectId)`, applies the returned draft, and lets the existing `savedEditorDraftId` effect fetch Step quantities.
4. A `409` is handled as the same reload recovery. When the refresh exposes `editor_draft_id`, the UI reports `Editable Matrix draft opened.` and removes the duplicate-create command. It never exposes the raw duplicate error or invents an id.
5. The action is disabled while opening and for lifecycle-readonly projects. Draftless Contact Measurement Plan controls are disabled as well; they become available only after the reloaded draft id exists.
6. Confirmed `contact_plan` records continue to arrive through the existing `carry_forward_step_quantities()` service path. Blank-only apply/save and Confirm Matrix promotion behavior are unchanged.

## Changed Files

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/features/matrix-editor/MatrixContactMeasurementPlanCard.tsx`
- `frontend/src/workbench.css`
- `docs/lane_evidence/TASK_360C_matrix-contact-plan-revision-draft-enablement_developer.md`

## Scope Check

- No `backend/**`, `frontend/src/api/client.ts`, schema, revision service/route/domain, Fee/default-fill, TASK_360B workbook, generic Test Record, parser/import, LTR/public-drive, or real-file path changed in this pass.
- Existing Fee rule/seed/test diffs, `docs/task_board.md`, `tests/unit/test_frontend_shell_files.py`, and TASK_360D/docs residuals remain external and excluded.
- `frontend/src/workbench.css` has an existing unrelated `@media` breakpoint hunk (`1180px` to `1024px`) in the same file. TASK_360C owns only the compact revision-draft bridge styles; the breakpoint hunk must remain outside the candidate package.

## Validation

- TDD red: added action tests first; `npm test -- MatrixEditorWorkspace --run` failed because the button was absent, as expected before implementation.
- `npm test -- MatrixEditorWorkspace MatrixContactMeasurementPlanCard --run`: passed, 2 files / 46 tests.
- `py -m pytest tests/unit/test_matrix_revision_flow_service.py tests/integration/test_matrix_revision_flow_api.py tests/unit/test_matrix_step_quantity_service.py tests/integration/test_matrix_step_quantity_api.py -q`: passed, 20 tests.
- `npm run build`: passed. Existing Vite chunk-size warning remains.
- `git diff --check` on the candidate frontend files and this evidence passed with only existing LF/CRLF warnings.
- Trailing-whitespace scan on touched files returned no matches.
- Targeted forbidden-path scan found only external Fee backend diffs, not TASK_360C changes. Candidate package contains only the four files listed above, with the unrelated CSS breakpoint hunk excluded during review/package isolation.
- Browser smoke not run in Developer pass: the action deliberately writes a revision draft, so live-project invocation is deferred to QA's controlled fixture/smoke environment.

## Reviewer B1 Fix Pass

Reviewer B1 found that the draft editor lock was also disabling TASK_360B's confirmed-snapshot workbook actions. The Contact Plan card now accepts a narrow `workbookDisabled` prop that defaults to its existing editor `disabled` behavior for all other callers. `MatrixEditorWorkspace` passes `workbookDisabled={isLifecycleReadonly}` while retaining the draft/editor lock for profiles, targets, blank-only apply, and save.

This preserves the authority boundary:

- Draftless confirmed Matrix: Contact Plan mutation remains disabled; specialized workbook preview/generate/download retain their existing confirmed-snapshot lifecycle, busy, and fingerprint guards.
- Lifecycle readonly: both draft mutation and workbook actions remain disabled.
- No workbook action reads revision draft state or changes TASK_360B's API/model behavior.

Focused regression added: a draftless confirmed Workspace keeps `Save contact plan` disabled, enables `Preview specialized record`, and invokes the existing confirmed-snapshot preview helper for the project.

Fix-pass validation:

- TDD red: `npm test -- MatrixEditorWorkspace --run` failed with `Preview specialized record` disabled before the lock split.
- `npm test -- MatrixEditorWorkspace MatrixContactMeasurementPlanCard --run`: passed, 2 files / 47 tests.
- `py -m pytest tests/unit/test_matrix_revision_flow_service.py tests/integration/test_matrix_revision_flow_api.py tests/unit/test_matrix_step_quantity_service.py tests/integration/test_matrix_step_quantity_api.py -q`: passed, 20 tests.
- `npm run build`: passed with the existing Vite chunk-size warning.
- Candidate `git diff --check` passed with only existing LF/CRLF warnings; trailing-whitespace scan returned no matches; candidate forbidden-path scan returned no matches.

## Stop Point

Recommended next role: Reviewer implementation gate.

Blocking summary: Reviewer B1 fixed. QA should perform the state-writing browser smoke in a controlled fixture environment.
