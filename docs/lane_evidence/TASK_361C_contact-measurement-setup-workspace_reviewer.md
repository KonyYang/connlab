# TASK_361C Contact Measurement Setup Workspace Reviewer Evidence

Status: reviewer_pass
Task: `TASK_361C_CONTACT_MEASUREMENT_SETUP_WORKSPACE`
Lane: `contact-measurement-setup-workspace`
Date: 2026-07-12
Role: Reviewer

## Gate

Reviewer plan gate only. No product code, schema, API, client, test, or authority
implementation was changed or authorized by this review.

Current phase: Phase 11, Project Workbench / Matrix / Approval Package controlled
foundation.
Current active task: `TASK_361C_CONTACT_MEASUREMENT_SETUP_WORKSPACE`, planned-only.
Why allowed: TASK_361A and TASK_361B are accepted, including TASK_361B local commit
`8cafc79e`; the board records TASK_361C as the current planned lane pending this gate.

## Review Findings

### Independent confirmation and authority boundary

The plan correctly keeps Matrix `Confirm Matrix` separate from `Confirm measurement
plan`. The latter remains available only in the dedicated workspace and uses the
accepted TASK_361B lifecycle command and current fingerprint. TASK_361C does not
change Matrix persistence, matrix confirmation, lifecycle transitions, classifier
categories, bootstrap, or write-command semantics.

### Narrow read-model bridge

The existing TASK_361B workspace response contains only opaque target keys, kind,
inclusion, readings, and family data. It cannot support an operator-readable target
or impact review without either exposing opaque identifiers or recreating authority
logic in the frontend. The proposed `ContactMeasurementPlanWorkspaceReadService` is
therefore a justified narrow exception: it is additive and read-only, resolves Group,
Step, Matrix-binding, candidate, and impact context server-side, and preserves the
existing command request/error shapes and formal effective projection.

### Stale-safe single-target interaction

The V1 interaction model is adequately bounded. Only one selected target may be
locally dirty; each accepted per-target command uses its current fingerprint and
reloads the workspace before another mutation. Stale `409` recovery keeps the page
open and does not silently discard input. The plan explicitly excludes bulk writes.

### TASK_360B compatibility and downstream isolation

The accepted TASK_360B controls remain a separate compact compatibility row using
their unchanged confirmed-Matrix source and API. They are not presented as draft-plan
output and do not enter the dedicated setup page. Persistent artifact history and
draft workbook behavior stay in TASK_361D; Fee and formal specialized-workbook
consumer migration stay in TASK_361E.

### UX and accessibility

The planned route follows the existing project page -> feature workspace -> model
pattern. It replaces the current long mixed editor with a compact read-only Matrix
summary and a dedicated, dense operator workspace. The plan preserves keyboard
reachability, inline error/stale recovery, responsive stacking, reserved action-area
space, non-modal-first behavior, and no nested-card or raw-token presentation.

## Scope and validation

The exact future May Touch list is sufficient: a new backend read service, additive
GET DTO/dependency composition and focused tests; typed client helpers, route/page,
feature model/selectors/components/styles/tests; and narrow retirement of the legacy
Matrix editor surface. Schema, migrations, repositories, TASK_361B lifecycle and
command semantics, Matrix confirmation, TASK_360B backend generation, TASK_361D/E,
generic Test Record, parser/import, Fee, Basic Information, LTR/public-drive,
StepInstance, Report, real files, release/settings, `.agents/**`, and
`docs/project_management/**` remain locked.

The proposed validation is proportionate: read-only service/API regression including
unchanged formal projection; route/summary/one-target/stale/impact/rebind/confirmation
frontend tests; TASK_360B source regression; focused build/compile/static scans; and
controlled desktop/narrow browser smoke without real workbook or folder mutation.

## Validation Performed

- Re-read AGENTS, task board, lane orchestration/role controls, TASK_361A/B accepted
  context, TASK_361C task/plan/Planner evidence, current Matrix card, existing route
  pattern, and current workspace projection/DTO code.
- Confirmed the board names TASK_361C as the current planned-only task and TASK_361B
  as accepted in local commit `8cafc79e`.
- Confirmed the Planner package is governance-only: task, plan, Planner evidence, and
  board changes. Current MCR/parser tests and TASK_360Q/R/S files are external
  residuals and excluded.
- Targeted documentation diff/status inspection found no TASK_361C product code.
  Existing line-ending warnings are limited to working-copy LF/CRLF normalization.

## Decision

`reviewer_pass`

Recommended next role/action: explicit User approval, then Developer planning-first.
Do not authorize Developer implementation directly. A later implementation still
requires source-of-truth reconciliation and its own Reviewer implementation-readiness
gate.

Blocking summary: none for the planned-only plan gate.

---

# TASK_361C Reviewer Implementation-Readiness Gate

Status: reviewer_pass
Task: `TASK_361C_CONTACT_MEASUREMENT_SETUP_WORKSPACE`
Lane: `contact-measurement-setup-workspace`
Date: 2026-07-12
Role: Reviewer

## Gate

Reviewer implementation-readiness gate only. The Developer planning-first pass is
documentation-only. No product code, schema, API, client, test, or authority
implementation was changed or authorized by this review.

## Readiness Assessment

### Concrete implementation boundary

The future package is sufficiently exact. Backend work is limited to the new
read-only workspace service, additive GET DTO composition, dependency wiring, and
focused unit/API regressions. Frontend work is limited to typed client helpers, one
project route/page, the named contact-plan feature boundary, compact Matrix summary,
narrow legacy-editor retirement, scoped styles, and focused tests. No implicit
backend, route, client, storage, or stylesheet expansion is authorized.

### Command, stale, and confirmation safety

The workspace consumes existing TASK_361B typed commands without changing their
request/error contracts. It permits one dirty target, sends the current fingerprint,
reloads after every successful command, and retains local input through a stale
`409` until the operator explicitly reloads or discards. Matrix confirmation remains
separate from independent Measurement Plan confirmation.

### Read-only DTO and compatibility contract

The additive DTO bridge is explicitly read-only and provides operator-readable
target, Matrix-binding, impact, and candidate context that current workspace DTOs do
not expose. It preserves the existing formal effective projection. TASK_360B remains
a Matrix-only, confirmed-Matrix compatibility row using its current hook/API; it is
outside the setup workspace and may not acquire draft-plan or persistent-artifact
semantics.

### UX, accessibility, and validation

The plan defines compact summary states, project-route parsing, Back behavior,
initial heading focus, save/reload focus restoration, action-triggered live status,
visible focus, labelled native controls, narrow source order, and non-obscuring
sticky actions. The focused backend/frontend/build/static/browser-smoke coverage is
proportionate and preserves the no-real-workbook/folder-mutation boundary.

## Source-Of-Truth Reconciliation Required

The board still says TASK_361C is pending the Reviewer plan gate even though the
Reviewer plan gate passed and the user-approved Developer planning-first pass is now
complete. This is a governance mismatch, not a design blocker. Planner or Integrator
must reconcile the board/task/lane state before any explicit Developer implementation
authorization. This readiness pass does not authorize implementation.

## Validation Performed

- Re-read AGENTS, board, TASK_361C task/updated plan/Planner/Developer evidence, the
  existing Reviewer plan-gate evidence, and TASK_361B API/projection boundary.
- Confirmed the Developer pass touched only the TASK_361C plan and Developer evidence;
  visible MCR/parser test changes and TASK_360Q/R/S residuals are external and
  excluded.
- Re-checked the exact May Touch/locked paths, route/workspace UX, single-target
  fingerprint recovery, independent confirmation, TASK_360B compatibility, and
  validation plan.
- Documentation diff-check is clean apart from the existing board LF/CRLF working-copy
  warning; UTF-8 trailing-whitespace scan found no matches.

## Decision

`reviewer_pass`

Recommended next role/action: User approval plus Planner/Integrator source-of-truth
reconciliation. Only after both, route Developer implementation. Do not route
Developer implementation from this gate alone.

Blocking summary: source-of-truth reconciliation is required before implementation
authorization; no implementation-design blocker was found.

---

# TASK_361C Reviewer Implementation Gate

Status: reviewer_blocked
Task: `TASK_361C_CONTACT_MEASUREMENT_SETUP_WORKSPACE`
Lane: `contact-measurement-setup-workspace`
Date: 2026-07-12
Role: Reviewer

## Gate

Reviewer implementation gate only. No product code was changed by this review.

Current phase: Phase 11, Project Workbench / Matrix / Approval Package controlled
foundation.
Current active task: `TASK_361C_CONTACT_MEASUREMENT_SETUP_WORKSPACE`, implementation
authorized and pending this Reviewer gate.

## Findings

### B1 - Selected-target family editor omits required authority fields and custom-family actions

`ContactMeasurementSetupWorkspace` only exposes each family count and prefix. It
does not expose the planned family label and record-label inputs, family inclusion,
or local custom-family add/remove actions. This is a material regression from the
accepted scope: TASK_361C moves the legacy family-editing surface into the dedicated
workspace, rather than removing those authorized per-target capabilities. A user
cannot therefore author or correct the complete `families` payload that the existing
TASK_361B target PATCH accepts.

Smallest fix: complete the selected-target family editor and its model helpers so it
can edit the supported family fields, toggle family inclusion, and add/remove custom
families locally. Preserve the one-target dirty lock and send the existing PATCH
payload only. Add focused UI/model regressions for custom add/remove, label/record
label/prefix/count/inclusion editing, and no silent overwrite.

### B2 - Stale `409` has no explicit reload recovery action

The model turns a stale response into the text `Reload before continuing.`, but the
workspace exposes no Reload control or explicit discard/re-application decision.
This fails the plan's required stale contract: local input must remain intact until
the operator explicitly reloads or discards it. The current UI leaves the operator
at an error message with no in-product recovery path.

Smallest fix: model stale state explicitly and render one inline Reload action. If
the selected target is dirty, make the operator explicitly discard or re-apply local
values after reload; never silently merge. Add a regression proving stale `409`,
visible Reload, preserved local input before the choice, and correct post-choice
fingerprint behavior.

## Passed Review Areas

- The new backend workspace read service uses repository and confirmed-Matrix reads
  only. It introduces no schema, repository write, lifecycle, classifier, bootstrap,
  Matrix-confirmation, or command-semantic change.
- API route/dependency wiring is additive for the typed workspace GET boundary. The
  frontend client uses the existing typed TASK_361B commands rather than raw fetch or
  a new write endpoint.
- The Matrix summary replaces the legacy long card and keeps TASK_360B workbook
  controls as a Matrix-only confirmed-snapshot compatibility row. The dedicated
  workspace contains no workbook actions, and independent plan confirmation remains
  separate from Matrix `Confirm Matrix`.
- The package does not modify schema/storage, Fee, generic Test Record, parser/import,
  LTR/public-drive, StepInstance/Report, TASK_361D/E, or other locked product scope.

## Validation Performed

- Re-read board, TASK_361C task/plan/Planner/Developer/Reviewer/reconciliation
  evidence, actual package status/diff, workspace read service, typed route/client,
  summary/workspace/model, Matrix integration, CSS, and focused tests.
- `py -m pytest tests/unit/test_contact_measurement_plan_workspace_read_service.py
  tests/unit/test_contact_measurement_plan_projection_service.py
  tests/integration/test_contact_measurement_plan_authority_bootstrap.py
  tests/integration/test_contact_measurement_plan_workspace_api.py -q` passed:
  `12 passed`.
- `npm test -- MatrixEditorWorkspace contactMeasurementPlanSelectors
  ContactMeasurementPlanSummaryCard useContactMeasurementPlanModel --run` passed:
  `5 files / 58 tests`.
- `py -m py_compile` for the new service, route, and dependency module passed.
  `npm run build` passed with the existing Vite chunk-size warning only.
- `git diff --check` and UTF-8 trailing-whitespace scans are clean apart from the
  known LF/CRLF working-copy warnings. The new service is 221 lines; no new hard-limit
  module was added. External MCR/parser and TASK_360Q/R/S residuals remain excluded.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer fix pass for B1 and B2 only. Do not route QA
or Integrator until this implementation re-gate passes. QA browser smoke remains
appropriate after the functional fixes.

Blocking summary: B1 incomplete selected-target family editing; B2 missing explicit
stale Reload/discard recovery.

---

# TASK_361C Reviewer Implementation Re-Gate - B1/B2 Closure

Status: reviewer_pass
Task: `TASK_361C_CONTACT_MEASUREMENT_SETUP_WORKSPACE`
Lane: `contact-measurement-setup-workspace`
Date: 2026-07-12
Role: Reviewer

## Gate

Reviewer implementation re-gate only. No product code was changed by this review.

## B1 Closure - Complete selected-target family editing

The dedicated selected-target editor now exposes family inclusion, label, record
label, count per sample, and record prefix. It supports local custom-family add/remove
without any new backend command or bulk path. New custom IDs derive from the highest
current `custom-N` suffix, including reloaded/persisted families, so removal does not
allow a collision on the next add. Frontend validation blocks duplicate or blank IDs,
blank label/record-label/prefix values, and negative/non-integer counts before the
existing single-target PATCH is sent. Override and needs-review state remain visible.

## B2 Closure - Explicit stale recovery

On a stale `409`, the model preserves a cloned local target and renders explicit
`Reload latest`, `Discard local edits`, and `Re-apply saved edits` actions. Reload is
read-only. Discard restores the latest selected target. Re-apply first fetches the
latest workspace and fingerprint, validates the preserved payload, then calls the
existing target PATCH once. It does not write automatically on stale detection, and
retry failures stay inline and readable.

## Regression and Scope Review

- The workspace read bridge remains read-only; no schema, repository, lifecycle,
  classifier, bootstrap, command, Matrix-confirmation, or TASK_360B backend behavior
  changed in the fix.
- Summary and Matrix-only TASK_360B compatibility row still use confirmed-Matrix
  source. The dedicated setup workspace has no workbook controls, and independent
  plan confirmation remains separate from `Confirm Matrix`.
- Existing legacy Matrix contact-plan selector state remains inert after the long
  card removal: it has no remaining UI trigger and is not applied by normal Step
  quantity save. It is not a TASK_361C authority write path.
- Fee, generic Test Record, parser/import, LTR/public-drive, StepInstance/Report,
  TASK_361D/E, `.agents/**`, and `docs/project_management/**` remain excluded.

## Validation Performed

- Re-read actual B1/B2 code, focused selectors/hook/component tests, the workspace
  read bridge, typed client commands, Matrix summary/compatibility integration, and
  reconciliation/locked-scope evidence.
- `py -m pytest tests/unit/test_contact_measurement_plan_workspace_read_service.py
  tests/unit/test_contact_measurement_plan_projection_service.py
  tests/integration/test_contact_measurement_plan_authority_bootstrap.py
  tests/integration/test_contact_measurement_plan_workspace_api.py -q` passed:
  `12 passed`.
- `npm test -- ContactMeasurementSetupWorkspace useContactMeasurementPlanModel
  contactMeasurementPlanSelectors MatrixEditorWorkspace
  ContactMeasurementPlanSummaryCard --run` passed: `6 files / 60 tests`.
- `py -m py_compile` for the read service, route, and dependency module passed.
  `npm run build` passed with the existing Vite chunk-size warning only.
- Candidate line counts are below the hard limit. `git diff --check` and UTF-8
  trailing-whitespace scans are clean apart from known LF/CRLF working-copy warnings.
  Locked-path status is clean; external MCR/parser and TASK_360Q/R/S residuals remain
  excluded.

## Decision

`reviewer_pass`

Recommended next role/action: QA gate for controlled Matrix-authority fixture browser
smoke at desktop and narrow widths. QA must verify family editing/save, stale recovery,
independent plan versus Matrix confirmation, confirmed-Matrix-only TASK_360B controls,
focus behavior, and no real workbook/folder mutation.

Blocking summary: none for the Reviewer implementation re-gate. Browser smoke is the
remaining QA validation.
