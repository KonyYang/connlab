# TASK_361H QA Gate Checkpoint

Date: 2026-07-13
Role: QA / Smoke Owner
Task: `TASK_361H_CONTACT_MEASUREMENT_FREEFORM_CATEGORIES`
Lane: `contact-measurement-freeform-categories`
Result: `qa_blocked`

## Blocking Source-Of-Truth Mismatch

QA did not run the requested disposable SQLite suites, browser fixture, build, or
static validation because the declared lane state is contradictory:

- The current board (`docs/task_board.md`) names TASK_361H as the active task but
  marks it `implementation_authorized / pending Developer implementation`, with
  Developer as owner and Developer implementation as the next required action.
- The task file also says implementation is pending Developer implementation.
- The current Reviewer callback and reviewer evidence report an implementation pass
  and direct QA to start the browser/regression gate.

The lane orchestration protocol requires the board/evidence/task state to agree before
the next role may run. QA cannot safely treat a product diff as an accepted Developer
handoff while the board and task still say that no implementation has occurred.

## Work Performed

- Read `AGENTS.md`, `docs/task_board.md`, lane orchestration controls, TASK_361H
  task/plan/evidence, current status/diff, and relevant contact-measurement source
  and tests.
- Loaded ConnLab product UI context because the requested gate includes browser,
  accessibility, and narrow-viewport smoke.
- Performed no product/test/database/file/browser mutation and no test execution.

## Required Resolution

Planner or Orchestrator must reconcile the TASK_361H board/task status with the
Developer and Reviewer evidence, including whether the visible working-tree changes
are the authorized Developer implementation candidate. After that reconciliation,
route QA again for the requested disposable-data and browser smoke.

## Decision

`QA gate: blocked`

Recommended next role: Planner / source-of-truth reconciliation.

---

# QA Re-run Gate

Date: 2026-07-13
Role: QA / Smoke Owner
Task: `TASK_361H_CONTACT_MEASUREMENT_FREEFORM_CATEGORIES`
Lane: `contact-measurement-freeform-categories`
Result: `qa_blocked`

## Source-Of-Truth Re-check

The Planner reconciliation is now reflected in the board, task, and evidence:
TASK_361H is the active task with Developer and Reviewer gates complete and this
QA re-run authorized. The earlier governance-only checkpoint above is therefore
superseded for product validation by this section.

## Environment And Safety Boundary

- OS: Windows; repository: `D:\PythonProject\connlab`.
- Disposable API/UI fixture only:
  `D:\PythonProject\connlab\tmp\task_361h_qa_browser\20260713T055741Z\authority.sqlite3`.
- The temporary backend ran at `127.0.0.1:8011`; a temporary Vite proxy ran at
  `127.0.0.1:5176`. No request used `data/connlab.sqlite3`, real project files,
  LTR/public-drive paths, or workbook/document generation.
- The fixture contained a test-only project `P1` and a confirmed Matrix snapshot
  with two eligible LLCR targets. The browser used
  `/projects/P1/contact-measurement-setup`.

## Automated Validation

Passed:

```text
py -m pytest -p no:cacheprovider --basetemp=tmp\task_361h_qa_pytest \
  tests\unit\test_contact_measurement_plan_family_validation.py \
  tests\integration\test_contact_measurement_plan_freeform_categories.py \
  tests\unit\test_contact_measurement_plan_workspace_read_service.py \
  tests\integration\test_contact_measurement_plan_workspace_api.py \
  tests\unit\test_contact_measurement_plan_confirmed_consumer_adapter.py \
  tests\unit\test_effective_contact_measurement_llcr_cr_record_projection.py \
  tests\unit\test_confirmed_matrix_llcr_cr_record_projection.py \
  tests\integration\test_llcr_cr_specialized_record_workbook_api.py \
  tests\integration\test_contact_measurement_plan_draft_workbook_api.py -q
26 passed in 3.44s

cd frontend
npm test -- ContactMeasurementPlanSummaryCard ContactMeasurementSetupWorkspace \
  contactMeasurementPlanSelectors useContactMeasurementPlanModel \
  DraftMeasurementPlanWorkbookPanel useDraftMeasurementPlanWorkbookModel \
  matrixContactMeasurementPlanSelectors --run
7 files / 24 tests passed

npm run build
passed; existing Vite chunk-size warning only
```

`py -m py_compile` passed for the touched contact-plan backend modules/routes and
focused tests. Candidate `git diff --check` reported only the known LF/CRLF
normalization warnings; no diff error was reported. Candidate trailing-whitespace
scan had no matches. Changed-hunk locked/no-real-path scan had no matches for real
DB/folders, Fee, Test Record, Report, StepInstance, LTR/public-drive, Projects
registry, Matrix editor, `.agents`, or `docs/project_management`. External working
tree residuals, including `docs/task_board.md` and TASK_361F operational evidence,
remain excluded.

## Controlled Browser Smoke

Observed passing behavior:

- Opening an editable plan rendered the setup workspace, two Matrix targets, a
  default blank freeform family, optional High Power/Low Power/Signal templates,
  add/remove/reorder controls, include controls, shared blank-eligible apply, and
  the draft-workbook panel without generating an artifact.
- The Signal template saved successfully through `Save target`; reload retained it
  and enabled the other target. This exercised target-local editing and safe
  temporary PATCH/reload behavior.
- At a `514 x 900` viewport, document and body widths did not exceed the viewport;
  labels and controls remained exposed. The browser console contained no warning or
  error entries. No workbook preview, generation, download, Cancel/Delete, or real
  data operation was invoked.
- Screenshot artifact: `docs/lane_evidence/artifacts/TASK_361H_qa/narrow-514px-signal-template.png`.

## Blocking Finding B1: Default Blank Freeform Category Cannot Be Saved

Severity: blocking implementation defect.

Reproduction against the disposable fixture:

1. Open `http://127.0.0.1:5176/projects/P1/contact-measurement-setup`.
2. Select the first eligible target and choose `Open measurement plan`.
3. The required default blank category appears with a visible Label, Count per
   sample, and Prefix (optional) input.
4. Enter `P1` as Label, a positive count, and `PX` as Prefix, then choose
   `Save target`.
5. Actual: the UI blocks the save with `Contact family label and prefix are
   required.` No PATCH is issued.
6. Expected: a user must be able to turn the required blank default category into
   a valid freeform category using the fields presented by the UI, then save it.

The fault is independently supported by source inspection. The editable UI changes
`label` and `record_prefix`, but exposes no `record_label` input
(`ContactMeasurementSetupWorkspace.tsx:163-165`). Client validation also requires
`record_label` to be nonblank (`contactMeasurementPlanSelectors.ts:136-137`). A
new blank category starts with an empty legacy record label, so the operator cannot
make it valid through the approved UI. This also blocks the required blank-only
shared-apply path when the source profile is the default category.

The Signal-template success shows the API and general save/reload path work; it
does not resolve the default-freeform path. The existing focused suite is missing
this exact browser/component regression.

## Decision

`QA gate: blocked`

Recommended next role: Developer fix pass.

Required minimal fix: preserve distinct legacy `record_label` for existing legacy
families while ensuring a new blank freeform category obtains a valid record label
from the user-entered label (or a clearly exposed editable equivalent) before
client validation/save. Add a focused regression for blank-default label/prefix
entry followed by Save and shared blank-only apply.

---

# QA Re-smoke After B1R4

Date: 2026-07-13
Role: QA / Smoke Owner
Task: `TASK_361H_CONTACT_MEASUREMENT_FREEFORM_CATEGORIES`
Lane: `contact-measurement-freeform-categories`
Result: `qa_blocked`

## Environment And Safety Boundary

- New disposable fixture only:
  `tmp/task_361h_rerun_browser/20260713T192200Z/authority.sqlite3`.
- Temporary backend/API: `127.0.0.1:8012`; temporary Vite proxy:
  `127.0.0.1:5177`. Both were stopped after validation.
- Fixture projects: `P1` (template rows) and `P2` (two empty LLCR targets).
  No request used `data/connlab.sqlite3`, real workbook/document generation,
  LTR/public-drive operations, or any real project directory. A path-existence-only
  safety check did not enumerate or read the real folder contents.
- No Cancel/Delete, confirmation, preview, generation, or download operation ran.

## Regression Validation

Passed:

```text
py -m pytest -p no:cacheprovider --basetemp=tmp\task_361h_rerun_pytest \
  tests\unit\test_contact_measurement_plan_family_validation.py \
  tests\integration\test_contact_measurement_plan_freeform_categories.py \
  tests\unit\test_contact_measurement_plan_workspace_read_service.py \
  tests\integration\test_contact_measurement_plan_workspace_api.py \
  tests\unit\test_contact_measurement_plan_confirmed_consumer_adapter.py \
  tests\unit\test_effective_contact_measurement_llcr_cr_record_projection.py \
  tests\unit\test_confirmed_matrix_llcr_cr_record_projection.py \
  tests\integration\test_llcr_cr_specialized_record_workbook_api.py \
  tests\integration\test_contact_measurement_plan_draft_workbook_api.py -q
26 passed in 3.51s

cd frontend
npm test -- ContactMeasurementPlanSummaryCard ContactMeasurementSetupWorkspace \
  contactMeasurementPlanSelectors useContactMeasurementPlanModel \
  useContactMeasurementPlanModel.projectSwitch DraftMeasurementPlanWorkbookPanel \
  useDraftMeasurementPlanWorkbookModel matrixContactMeasurementPlanSelectors --run
8 files / 35 tests passed

npm run build
passed; existing Vite chunk-size warning only
```

`py_compile` passed for the touched backend modules/routes. Candidate
`git diff --check` exited `0`; informational LF/CRLF messages remain. UTF-8
trailing-whitespace and changed-hunk locked/no-real-path scans had no matches.
Touched Python modules remain under the project hard limit. The frontend model and
its focused test currently count 512 and 511 lines respectively; this is recorded
as a non-blocking maintainability observation because the hard limit is stated for
Python and no task-specific frontend cap is defined.

Focused coverage also passed for persisted empty `record_label` no-write behavior,
semantic renew/stale reapply, duplicate label/prefix typed 422, high-water/no-reuse,
and A -> B -> A old-reload resolve/reject isolation. TASK_360B/TASK_361D temporary
consumer/API suites included above remained green; no artifact was generated.

## B1 Re-smoke: Passed

After manually selecting an empty target in the P2 fixture:

1. The default starter row appeared with visible Label, positive Count (`1`), and
   resolved Prefix (`C1`).
2. Entering Label `P1` and choosing `Save target` succeeded; the prior hidden
   `record_label` validation blocker did not recur.
3. `Apply to blank eligible targets` succeeded with the visible success status.
   Selecting the second target showed the applied `P1 / C1` row.
4. An explicit Add row (`P2`) saved/reloaded. Signal template insertion, accessible
  move-up reorder, and save/reload also succeeded.
5. A subsequent `P2` -> `P3` visible-label rename saved. A read-only temp API check
   returned renewed `ff-llcr-6|P3|P2|C3`, proving the distinct initialized
   `record_label` was preserved through semantic identity renewal.

At `514 x 900`, body/document widths did not exceed the viewport and the browser
console had no warning/error entries. Visible inputs and actions retained accessible
labels. Screenshot artifact:
`docs/lane_evidence/artifacts/TASK_361H_qa/rerun-narrow-514px.png`.

## New Blocking Finding B2: Starter Row Missing Immediately After Open Draft

Severity: blocking user-flow regression.

Reproduction against the fresh disposable P2 fixture:

1. Open `/projects/P2/contact-measurement-setup`; both eligible targets begin with
   no category families.
2. Choose `Open measurement plan` and wait for the reloaded draft state.
3. Actual: the page presents `Selected contact target: Group 1` with no category
   rows. The required default blank starter row is absent, even though Group 1 is
   displayed as the selected target.
4. Click the already displayed Group 1 target once.
5. Actual: the expected blank starter row appears immediately, with Count `1` and
   Prefix `C1`; B1 save/apply then works.
6. Expected: opening an editable plan with the current empty target must render the
   required starter row without an unexplained second selection action.

Likely cause by source inspection: `reload()` only restores an editable target when
the old `localTarget.stable_target_key` matches a target in the new draft
(`useContactMeasurementPlanModel.ts:67-75`). The newly opened draft can have no
matching local target, so it returns the old/null state instead of hydrating
`next.targets[0]` through `editableContactMeasurementTarget`. `selectTarget()` does
hydrate correctly, explaining the redundant-click workaround.

## Decision

`QA gate: blocked`

Recommended next role: Developer fix pass.

Required minimal fix: in the open-draft reload path, select and hydrate a safe
fallback current target when the prior local stable key is absent, then mark its
starter provenance. Add a focused regression that opens a draft from an empty
confirmed target and asserts the starter row is visible before any target reselect.

---

# Final QA Re-smoke After B2R

Date: 2026-07-13
Role: QA / Smoke Owner
Task: `TASK_361H_CONTACT_MEASUREMENT_FREEFORM_CATEGORIES`
Lane: `contact-measurement-freeform-categories`
Result: `qa_pass`

## Environment And Safety Boundary

- Browser and API smoke used only the disposable fixture root
  `tmp/task_361h_final_browser/20260713T195200Z`, including its
  `authority.sqlite3`, temporary project/template roots, Uvicorn on `8013`, and
  Vite proxy on `5178`.
- Fixture project `P2` contained two empty, eligible LLCR targets. No request
  addressed `data/connlab.sqlite3`, a real project, LTR/public-drive resource, or
  workbook/document path.
- The smoke performed draft-local target saves and blank-only apply only. It did
  not run Cancel/Delete, plan confirmation, preview, generation, download, or any
  real workbook/document output.

## Regression Validation

Passed:

```text
py -m pytest -p no:cacheprovider --basetemp=tmp\task_361h_final_rerun_pytest \
  tests\unit\test_contact_measurement_plan_family_validation.py \
  tests\integration\test_contact_measurement_plan_freeform_categories.py \
  tests\unit\test_contact_measurement_plan_workspace_read_service.py \
  tests\integration\test_contact_measurement_plan_workspace_api.py \
  tests\unit\test_contact_measurement_plan_confirmed_consumer_adapter.py \
  tests\unit\test_effective_contact_measurement_llcr_cr_record_projection.py \
  tests\unit\test_confirmed_matrix_llcr_cr_record_projection.py \
  tests\integration\test_llcr_cr_specialized_record_workbook_api.py \
  tests\integration\test_contact_measurement_plan_draft_workbook_api.py -q
26 passed in 3.93s

cd frontend
npm test -- ContactMeasurementPlanSummaryCard ContactMeasurementSetupWorkspace \
  contactMeasurementPlanSelectors useContactMeasurementPlanModel \
  useContactMeasurementPlanModel.projectSwitch \
  useContactMeasurementPlanModel.targetHydration \
  DraftMeasurementPlanWorkbookPanel useDraftMeasurementPlanWorkbookModel \
  matrixContactMeasurementPlanSelectors --run
9 files / 37 tests passed

npm run build
passed; existing Vite chunk-size warning only
```

`py -m py_compile` passed for the five touched contact-measurement backend
modules/routes. Candidate `git diff --check` exited `0`; UTF-8 trailing-whitespace
and changed-hunk locked/no-real-path scans had no matches. The scan found no
TASK_361H changed-hunk reference to real folders/databases, StepInstance, Report,
AI, public drive, Projects list, Matrix import, `.agents`, or
`docs/project_management`. Existing board, TASK_361F operational, and other
worktree residuals remain excluded from this lane.

The focused tests cover the preferred-target eligibility fallback/all-ineligible
null result, A -> B and A -> B -> A reload isolation, freeform high-water/no-reuse,
duplicate typed-422/no-write, persisted-empty `record_label`, semantic renewal and
stale reapply. The included temporary TASK_360B/TASK_361D consumer/API regressions
remained green; no artifact generation request was made.

## B2R Controlled Browser Re-smoke

1. Opened `http://127.0.0.1:5178/projects/P2/contact-measurement-setup` and chose
   `Open measurement plan` once. On the first rendered draft state, Group 1 was
   selected and already showed the default blank starter with visible Label, Count
   per sample `1`, and resolved Prefix `C1`. No redundant target click was needed.
2. Filled the starter Label as `P1`; `Save target` returned
   `Contact measurement plan reloaded.` with no validation blocker. `Apply to blank
   eligible targets` returned `Profile applied to blank eligible targets.`; Group 2
   then displayed `P1 / C1`.
3. Added the optional Signal template. Its native labelled controls appeared with
   count `1` and prefix `SIG`; the included total changed to `2`. Its enabled
   `Move up` control moved Signal above P1. This confirms the compact add/template,
   include, derived-total and reorder surface without exercising remove/delete.
4. At `514 x 900`, `bodyScrollWidth` was `499` against viewport width `514`; at
   `1440 x 900`, it was `1425` against `1440`. No horizontal overflow or visible
   overlap was observed. Browser error/warning logs were empty. DOM inspection and
   source confirm native labelled inputs and native buttons for target selection,
   add/template/reorder, apply and save. The in-app automation binding exposes no
   direct focus primitive, so sequential Tab traversal was not separately driven;
   this is a non-blocking tooling limitation rather than a product error.

Artifacts:

- `docs/lane_evidence/artifacts/TASK_361H_qa/final-b2r-narrow-514px.png`
- `docs/lane_evidence/artifacts/TASK_361H_qa/final-b2r-desktop.png`

## Decision

`QA gate: pass`

Recommended next role: Integrator packaging/readiness. Integrator must stage only
the reconciled TASK_361H candidate files/evidence and keep the external board,
TASK_361F operational evidence, Settings/LTR/release/desktop and unrelated worktree
residuals out of the package.
