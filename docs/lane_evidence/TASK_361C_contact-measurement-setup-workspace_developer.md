# TASK_361C Contact Measurement Setup Workspace Developer Evidence

Date: 2026-07-12

Role: Developer

Status: ready_for_review - implementation complete pending Reviewer implementation gate.

## Current Phase / Why Allowed

Phase 11 controlled Matrix foundation. TASK_361A and TASK_361B are accepted;
TASK_361B local commit is `8cafc79e`. Reviewer plan/readiness gates and user
implementation approval are recorded in source-of-truth reconciliation. This
implementation uses only the authorized TASK_361C read bridge, UI/client, and route
surface; TASK_361B storage/lifecycle/commands remain unchanged.

## Planning Decisions

- Replace the existing long, mixed `MatrixContactMeasurementPlanCard` with a compact
  Matrix summary adjacent to Project Schedule and a dedicated project route:
  `/projects/{project_id}/contact-measurement-setup`.
- The summary shows only authority status/revision, Matrix revision, included/total
  targets, LLCR and CR specified-current uniform-or-multiple readings, one concise
  needs-review/compatibility/blocker message, and the setup entry point. It does not
  expose editable families, raw ids, or fingerprints.
- The setup page follows the Basic Information route-page -> feature-workspace ->
  model boundary. It owns one selected target at a time, readable Group/Step/impact/
  candidate/Matrix-binding context, local dirty protection, and inline stale/error
  recovery. It uses no modal-first interaction or bottom overlay.
- A narrow additive read-only backend workspace bridge is required because the
  accepted TASK_361B workspace DTO has opaque target keys and lacks operator-readable
  target, Matrix binding, and impact/candidate context. The bridge adds no schema,
  repository write, command, lifecycle, bootstrap, classifier, or projection
  semantic change.
- All writes reuse existing TASK_361B single-target commands. Each successful command
  reloads the workspace and replaces the fingerprint. A stale `409` preserves local
  editor input until an explicit Reload/discard choice. No bulk-write endpoint is
  planned.
- `Confirm measurement plan` stays in the setup workspace and is independent from
  Matrix `Confirm Matrix`.
- TASK_360B remains a compact Matrix-only compatibility row using its current
  confirmed-Matrix source. It has no controls in the setup workspace and no invented
  artifact history. TASK_361D/E remain separate.

## Future May Touch

Exact candidate paths are recorded in
`docs/task_361c_contact_measurement_setup_workspace_plan.md`: the new read-only
workspace service, additive GET route/dependency composition and focused backend
tests; the typed frontend client, app route, Matrix page/workspace replacement,
dedicated feature/page/styles/tests; and TASK_361C governance/evidence files only.

## Locked Boundaries

Schema/models/migrations/repositories, all TASK_361B write/lifecycle/classifier/
bootstrap semantics, Matrix confirmation/persistence, TASK_360B backend generation,
TASK_361D/E, generic Test Record, Matrix parser/import, Fee, Basic Information,
LTR/public-drive, StepInstance/Report, real files, settings/release, `.agents/**`,
and `docs/project_management/**` remain locked.

## Validation Plan

- Backend unit/API coverage: read-only workspace enrichment, typed status/context,
  no-write behavior, and unchanged TASK_361B formal effective projection.
- Frontend coverage: route/Back flow, compact summary states, accessibility focus,
  one-target dirty lock, command-reload fingerprint handling, stale `409`, impact
  review/rebind, plan confirmation separation, and TASK_360B compatibility row.
- Gate commands: focused `py -m pytest`, focused `npm test`, `py_compile`,
  `npm run build`, diff/trailing/forbidden-scope/no-real-mutation scans, plus a
  controlled desktop and narrow-width browser smoke.

## Implementation Summary

### Read-only backend bridge

- Added `ContactMeasurementPlanWorkspaceReadService`, a no-write projection that
  enriches existing TASK_361B authority rows with readable Group/Step/family/impact/
  Matrix-binding context, concise diagnostics, and compact counts/readings facts.
- Added only the typed workspace GET DTO/dependency composition. Existing lifecycle,
  target PATCH, rebind, confirmation, feature-flag, repository, classifier, and
  effective-projection behavior were not changed.

### Compact Matrix summary and compatibility row

- Replaced the long editable `MatrixContactMeasurementPlanCard` runtime surface with
  the compact `ContactMeasurementPlanSummaryCard` beside Project Schedule. It shows
  state, target coverage, LLCR/CR readings, plan/Matrix revisions, and a concise
  review warning.
- Retired the unreferenced legacy card and its test after confirming it had no runtime
  caller. TASK_360B specialized-record controls remain in a compact Matrix-only
  compatibility row with their existing confirmed-Matrix hook/API and current-session
  artifact behavior.

### Dedicated setup workspace

- Added `/projects/{project_id}/contact-measurement-setup`, a thin page following the
  Basic Information page-to-feature-workspace pattern. Back returns to Matrix Editor.
- Added typed client helpers and a one-target model. Each command calls an existing
  TASK_361B command then reloads the read model and fingerprint. `409` stale recovery
  remains inline and preserves the page/local target state. No bulk write exists.
- The workspace keeps plan confirmation independent from Matrix confirmation, exposes
  readable target and impact/candidate context, uses normal/sticky reserved action
  flow, and adds visible heading/status focus behavior. It contains no workbook
  controls.

## Changed Files

- `backend/application/contact_measurement_plan_workspace_read_service.py`
- `backend/api/dependencies.py`
- `backend/api/routes_contact_measurement_plan.py`
- `tests/unit/test_contact_measurement_plan_workspace_read_service.py`
- `tests/integration/test_contact_measurement_plan_workspace_api.py`
- `frontend/src/api/client.ts`, `frontend/src/App.tsx`, and
  `frontend/src/pages/ProjectMatrixEditorPage.tsx`
- `frontend/src/pages/ProjectContactMeasurementSetupPage.tsx`
- `frontend/src/features/contact-measurement-plan/**`
- `frontend/src/contact-measurement-plan.css`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` and focused test
- removed `MatrixContactMeasurementPlanCard.tsx` and its focused legacy test

## Implementation Validation

- `py -m pytest tests/unit/test_contact_measurement_plan_workspace_read_service.py
  tests/unit/test_contact_measurement_plan_projection_service.py
  tests/integration/test_contact_measurement_plan_authority_bootstrap.py
  tests/integration/test_contact_measurement_plan_workspace_api.py -q` -> 12 passed.
  A final repeat used an isolated workspace temporary directory after Windows denied
  access to the shared user pytest temp directory; it also returned 12 passed.
- `npm test -- MatrixEditorWorkspace contactMeasurementPlanSelectors
  ContactMeasurementPlanSummaryCard useContactMeasurementPlanModel --run` -> 5 files,
  58 tests passed.
- `py -m py_compile backend/application/contact_measurement_plan_workspace_read_service.py
  backend/api/routes_contact_measurement_plan.py backend/api/dependencies.py` -> passed.
- `npm run build` -> passed; existing Vite chunk-size warning only.
- `git diff --check` -> passed with existing LF/CRLF warnings only. UTF-8 trailing
  whitespace scan found no matches in TASK_361C package paths. New Python service is
  221 lines and route module is 431 lines, both below the 500-line hard limit.
- Static runtime scan finds no `MatrixContactMeasurementPlanCard` caller. The
  workspace bridge has no file/workbook/real-folder mutation path; TASK_360B calls
  stay behind its existing frontend hook. Full-file keyword hits in
  `backend/api/dependencies.py` are pre-existing shared dependency registrations, not
  new TASK_361C hunk behavior.

## Residuals

- Controlled browser smoke was not run in this Developer pass because no isolated
  local Matrix-authority fixture server/browser session was available without risking
  unrelated project data. Reviewer/QA should run the planned desktop and narrow-width
  smoke using a controlled temporary project.
- Existing MCR/parser tests, TASK_360Q/R/S task files, board changes, and other dirty
  worktree entries are external residuals and excluded. No schema/repository/lifecycle
  or TASK_360B backend, TASK_361D/E, Fee, parser, LTR/public-drive, or real-file
  change was made here.

## Planning-First Validation

- Re-read AGENTS, task board, TASK_361C task/plan/Planner/Reviewer evidence, the
  accepted TASK_361B API/projection boundary, Matrix Editor card, and Basic
  Information routing/workspace pattern.
- Loaded `$impeccable` product context and read PRODUCT, DESIGN, and frontend
  architecture rules. The plan uses a dense operational route, a non-nested summary,
  no modal-first flow, compact status copy, visible keyboard focus, and responsive
  source order.
- This pass changed documentation only. Existing MCR/parser tests, TASK_360Q/R/S
  task files, board changes, and other dirty worktree entries are external residuals
  and excluded.
- Required task/plan/Planner/Reviewer/Developer evidence files exist. `git diff
  --check` for the TASK_361C plan/evidence returned clean, and the UTF-8 trailing
  whitespace scan returned no matches. Targeted status shows only the TASK_361C
  plan/evidence documentation in this pass; existing backend test-plan and test-file
  modifications were present as excluded external residuals.

## Next Role

Reviewer implementation gate.

## Blocking Summary

None known for Reviewer implementation gate. Browser smoke remains the recorded QA
residual; no Reviewer/QA/Integrator routing was performed by Developer.

---

## Developer Fix Pass: Reviewer B1/B2

Status: ready_for_review - B1/B2 fixed; pending Reviewer implementation re-gate.

### B1: Full selected-target family editor

- Extended the dedicated workspace editor only. Each selected family now exposes its
  inclusion toggle, label, record label, count per sample, and record prefix.
- Added V1 custom-family add/remove using the existing single-target PATCH payload.
  No backend command, DTO, authority rule, or bulk-write path was added or changed.
- Custom ids use the greatest persisted/reloaded `custom-N` suffix plus one, so add
  A, add B, remove A, add C produces distinct ids. Save validation rejects empty
  label/record-label/prefix, negative or non-integer counts, and duplicate ids before
  a command can be sent.
- Override and needs-review state remain visible in the target editor. The existing
  editable-revision command and fingerprint-reload path remains the only authority
  write path.

### B2: Explicit stale recovery

- A stale `409` now retains a cloned local target and presents inline actions:
  `Reload latest`, `Discard local edits`, and `Re-apply saved edits`.
- Re-apply first fetches the latest workspace and fingerprint, then calls the existing
  single-target PATCH command. It performs no automatic write on stale detection and
  retains readable failure feedback when the latest target is no longer editable or a
  retry fails.
- Reload preserves the saved stale edit for an intentional subsequent re-apply;
  discard restores the latest selected target and clears the recovery state.

### Fix-Pass Changed Files

- `frontend/src/features/contact-measurement-plan/contactMeasurementPlanSelectors.ts`
- `frontend/src/features/contact-measurement-plan/contactMeasurementPlanSelectors.test.ts`
- `frontend/src/features/contact-measurement-plan/useContactMeasurementPlanModel.ts`
- `frontend/src/features/contact-measurement-plan/useContactMeasurementPlanModel.test.tsx`
- `frontend/src/features/contact-measurement-plan/ContactMeasurementSetupWorkspace.tsx`
- `frontend/src/features/contact-measurement-plan/ContactMeasurementSetupWorkspace.test.tsx`
- this Developer evidence file

### Fix-Pass Validation

- Red/green selector test first confirmed the absent custom-family helper, then passed
  after implementation: `npm test -- contactMeasurementPlanSelectors --run` -> 2
  files, 9 tests passed.
- Red/green hook test first confirmed stale recovery did not retain a target, then
  passed after implementation: `npm test -- useContactMeasurementPlanModel --run` ->
  1 file, 2 tests passed.
- `npm test -- ContactMeasurementSetupWorkspace useContactMeasurementPlanModel
  contactMeasurementPlanSelectors MatrixEditorWorkspace ContactMeasurementPlanSummaryCard
  --run` -> 6 files, 60 tests passed.
- `npm run build` -> passed; existing Vite chunk-size warning only.
- `py -m py_compile backend/application/contact_measurement_plan_workspace_read_service.py
  backend/api/routes_contact_measurement_plan.py backend/api/dependencies.py` -> passed.
- Isolated-temp backend regression command for the existing read bridge and authority
  projection: 12 tests passed.
- `git diff --check` -> passed with existing LF/CRLF warnings only. UTF-8 trailing
  whitespace scan found no matches in the TASK_361C candidate paths. Existing backend
  service is 221 lines and route module is 431 lines, below the 500-line hard limit.
- Targeted status/diff inspection confirms this fix pass did not modify backend
  authority/schema/repository/command files, Matrix confirmation, TASK_360B backend,
  TASK_361D/E, Fee, parser, LTR/public-drive, or external residuals.

### Residual and Next Role

The controlled browser smoke remains a QA residual because an isolated Matrix-authority
fixture browser session is not available in this pass. No real files, workbooks, or
folders were touched. Recommend **Reviewer implementation re-gate**; do not route QA
or Integrator from this Developer pass.
