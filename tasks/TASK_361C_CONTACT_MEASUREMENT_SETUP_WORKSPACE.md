# TASK_361C Contact Measurement Setup Workspace

## Status

Complete / Integrator accepted on 2026-07-12 after Developer implementation,
Reviewer implementation re-gate, QA gate, and controlled Integrator
packaging/readiness. The responsive browser narrow-width limitation is recorded
as a non-blocking tooling residual in QA evidence.

## Lane

`contact-measurement-setup-workspace`

## Current Phase / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Upstream: TASK_361A contract and TASK_361B backend authority are complete/accepted;
  TASK_361B local commit is `8cafc79e` and remote was not pushed.
- Role: Integrator packaging/readiness.
- Why allowed: Reviewer implementation re-gate passed, QA gate passed, and the
  package is limited to the reviewed setup workspace route/read-model/client/UI
  scope plus precise board closeout.

## Goal

Replace the long editable Matrix Contact Measurement Plan card with a compact
read-only summary and one `Contact measurement setup` action. Add a dedicated
project route/workspace that consumes typed independent-authority APIs for target
families, counts, prefixes, inclusion/exclusion, overrides, impact review, draft
save, and plan confirmation.

Matrix confirmation and Measurement Plan confirmation remain separate actions.

## Planned Backend Read-Model Bridge

Repository evidence shows the accepted TASK_361B command API is sufficient, but the
current workspace DTO lacks operator-readable Group/Step context, Matrix binding,
impact/candidate rows, and post-command fingerprint context. TASK_361C therefore
proposes one additive read-only workspace bridge. It may enrich DTO/read projection
only; it must not change schema, repository writes, lifecycle transitions,
classifier categories, bootstrap, or authority semantics.

## Authorized May Touch For Developer Implementation

Backend read-model bridge only:

- `backend/application/contact_measurement_plan_workspace_read_service.py`
- `backend/application/contact_measurement_plan_projection_service.py` only if the
  existing summary delegates to the new read service without changing formal
  effective-projection semantics
- `backend/api/routes_contact_measurement_plan.py` only for additive typed summary/
  workspace response fields and dependency use
- `backend/api/dependencies.py` only to compose the read service
- `tests/unit/test_contact_measurement_plan_workspace_read_service.py`
- `tests/unit/test_contact_measurement_plan_projection_service.py` only for summary
  regression
- `tests/integration/test_contact_measurement_plan_workspace_api.py`

Frontend integration and UI:

- `frontend/src/api/client.ts` for TASK_361B typed DTOs/helpers only
- `frontend/src/App.tsx`
- `frontend/src/pages/ProjectMatrixEditorPage.tsx`
- `frontend/src/pages/ProjectContactMeasurementSetupPage.tsx`
- `frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.tsx`
- `frontend/src/features/contact-measurement-plan/ContactMeasurementSetupWorkspace.tsx`
- `frontend/src/features/contact-measurement-plan/useContactMeasurementPlanModel.ts`
- `frontend/src/features/contact-measurement-plan/contactMeasurementPlanSelectors.ts`
- focused tests alongside the new feature files
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/features/matrix-editor/MatrixContactMeasurementPlanCard.tsx` and its
  test only for replacement/removal of the legacy long editor
- `frontend/src/features/matrix-editor/matrixContactMeasurementPlanSelectors.ts` and
  its test only if all legacy runtime callers are removed
- `frontend/src/contact-measurement-plan.css`
- `frontend/src/workbench.css` only to remove/retire legacy contact-plan editor
  classes and preserve surrounding Matrix layout
- `tests/unit/test_frontend_shell_files.py` only for route/boundary assertions
- TASK_361C task/plan/evidence and `docs/task_board.md`

## Must Not Touch / Locked Paths

- No database schema/migration/model/repository changes.
- No TASK_361B lifecycle, bootstrap, identity, impact-classifier, partial-projection,
  feature-flag, or command semantics changes.
- No Matrix draft/confirmed persistence or `Confirm Matrix` semantics changes.
- No TASK_361D draft workbook preview/generate/download or artifact lineage.
- No TASK_361E Fee/specialized-workbook confirmed-consumer migration.
- No TASK_360B workbook route/service/gateway/artifact-store behavior change.
- No generic Test Record, Matrix parser/import, Fee rules/default fill, Basic
  Information, LTR/public-drive, Folder Actions, StepInstance, Report, release/
  settings, real workbook/folder mutation, or unrelated cleanup.
- `.agents/**`, `docs/project_management/**`, remote push, and destructive git
  operations remain locked.

## UX Acceptance Criteria

1. Matrix Editor no longer shows the long editable Contact Measurement Plan form.
2. A compact read-only summary near Project Schedule shows business-readable plan
   state, included/total targets, LLCR/CR readings per sample, plan and Matrix
   revisions, and one concise review/stale warning when applicable.
3. Uniform readings show one number; divergent target readings show `Multiple`
   rather than a misleading aggregate.
4. `Contact measurement setup` opens
   `/projects/{project_id}/contact-measurement-setup` as a dedicated page, not a
   modal, and Back returns to Matrix Editor.
5. The workspace shows readable Group, Step, test item, kind, readings, inclusion,
   override, and impact context. Opaque ids/fingerprints remain hidden UI state.
6. V1 edits one selected target at a time. Save uses its current revision token,
   reloads workspace after every command, and blocks selection/navigation while one
   local target edit is dirty. No stale multi-target batch writes.
7. `Review changes`, `Accept suggested changes`, explicit rebind/include/exclude,
   `Save draft`, and `Confirm measurement plan` follow TASK_361B typed commands and
   show inline success/error/stale recovery.
8. Matrix `Confirm Matrix` does not confirm a Measurement Plan. Plan confirmation is
   available only in the dedicated workspace.
9. TASK_360B specialized workbook actions remain a separate compact compatibility
   row near the summary, retain their accepted confirmed-Matrix source and API, and
   are not presented as draft-plan output. The setup workspace contains no workbook
   controls.
10. Only a current-session generated TASK_360B filename may be shown. Persistent
    latest draft/formal artifact metadata is unavailable in current APIs and is
    explicitly deferred to TASK_361D; the UI must not invent or persist it.
11. Layout is dense, restrained, keyboard reachable, non-nested, and responsive;
    action/footer regions reserve space and do not cover target rows or controls.

## Validation Gate

- Backend read tests prove additive operator context, impact/candidate mapping,
  Matrix binding/revision fields, no writes, no raw malformed fallback, and unchanged
  effective formal projection.
- API tests prove typed summary/workspace responses and all existing TASK_361B
  command/status/error contracts remain backward compatible.
- Frontend tests cover route parsing/navigation, compact summary states/readings/
  target counts/warnings, one-target dirty lock, open/save/reload, stale `409`
  recovery, impact review, compatible acceptance, rebind, confirm, and error states.
- Regression proves Matrix confirmation remains separate, the old long editor is
  absent, TASK_360B workbook controls retain existing behavior/source, and no
  TASK_361D/E API is called.
- `npm test` focused suites, focused `py -m pytest`, `npm run build`, Python compile,
  diff/trailing/forbidden-scope scans pass.
- Browser smoke on a controlled project covers Matrix summary -> setup -> open/save
  draft -> review/confirm -> return to Matrix at desktop and narrow widths, with no
  obscured controls and no real workbook/folder mutation.

## Merge Gate

Reviewer plan gate, user approval for Developer planning-first, docs-only Developer
planning-first, Reviewer implementation-readiness, explicit implementation
approval, Developer implementation, Reviewer implementation review, QA gate, and
Integrator package isolation are complete. External MCR/parser, TASK_360Q/R/S,
release/settings, schema/repository/lifecycle, TASK_361D/E, Fee/workbook
consumer, real-file, `.agents/**`, and `docs/project_management/**` residuals are
excluded.

## Definition Of Ready

Complete. TASK_361C is accepted as the setup workspace/client/UI lane only. This
does not authorize TASK_361D/E, schema/repository/lifecycle/command semantics,
Matrix confirmation changes, TASK_360B backend behavior, or downstream
Fee/workbook consumer migration.

## Blocking Questions

None for Developer implementation within the authorized scope.
