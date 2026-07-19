# TASK_364B QA Evidence

Date: 2026-07-19
Role: QA / Smoke Owner
Status: `qa_pass / user_acceptance_pending`

## Environment And Safety

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- QA used pytest `tmp\\task_364b_qa_backend`, a local Vite harness, and an isolated
  Chrome `--headless=new` profile with CDP bound only to `127.0.0.1`.
- The browser harness imported the actual `ProjectPointProfileEditor` source but used
  only local React state. It made no API request and its Confirm callback returns
  `false`; no project authority, real database, workbook, LTR, folder, or output file
  was opened or written.
- The temporary Vite/CDP processes were stopped after verification. QA did not edit
  product code/tests, stage, commit, push, or package any candidate.

## Focused Regression

```powershell
py -m pytest -p no:cacheprovider --basetemp=tmp\task_364b_qa_backend tests\unit\test_contact_point_profile_expression.py tests\unit\test_contact_point_profile_fingerprint.py tests\unit\test_contact_point_profile_legacy_suggestion.py tests\unit\test_contact_point_profile_lifecycle.py tests\unit\test_contact_point_profile_schema.py tests\unit\test_contact_point_profile_confirmed_consumer_adapter.py tests\integration\test_contact_point_profile_api.py -q
cd frontend
npm test -- src/features/contact-measurement-plan MatrixEditorWorkspace.test.tsx
npm run build
```

Actual results:

- Disposable backend/API authority suite: `46 passed in 17.82s`.
- Frontend Point Profile, Contact Measurement, and Matrix regression: `12 files / 91 passed`.
- `py_compile` passed for the reviewed Point Profile API/application/storage modules.
- Frontend build passed; only the existing Vite chunk-size advisory appeared.

The disposable lifecycle/API tests cover direct no-target save/confirm, existing
confirmed revision reload, dynamic category CR selection, all-selected `follow_llcr`,
custom coverage, zero-selection rejection, stable identity, stale/no-partial-write,
and typed disabled/no-write paths. The frontend model test confirms local edit stays
local until its one direct Confirm command, and serializes all-selected coverage as
the existing follow contract.

## Controlled Browser Smoke

Artifact: [514px native checkbox smoke](D:\PythonProject\connlab\docs\lane_evidence\artifacts\TASK_364B_qa\controlled_514_native_checkbox.png)

At an actual Chromium emulated `514x831` viewport, using the actual editor component:

- LLCR heading remained present; there were exactly three labelled native CR
  checkboxes, one per category row. No separate CR coverage section or LLCR checkbox
  column appeared.
- The default rows were selected. Pointer click on `Include LP in CR` changed checked
  state once and logged exactly one model action (`1:false`).
- Tab order reached the LP native checkbox. Space changed it once and logged exactly
  one action, with `scrollY` unchanged. Enter produced the Chromium native-checkbox
  no-op (checked state/action log unchanged), which is the expected native semantic
  and confirms no accidental custom or double activation.
- In the busy harness, the checkbox was disabled and a center pointer action produced
  no model action.
- `scrollWidth <= clientWidth` for both document and table; the row inputs, CR column,
  delete controls, Add row control, Cancel, and Confirm action bar were visible and
  non-overlapping. Screenshot inspection found no truncated labels.
- Fresh page console collected no warning or error. Chrome process-level GCM messages
  were not page-console events and were outside the product harness.

## Static And Scope Checks

- Scoped `git diff --check` passed; existing LF/CRLF normalization notices only.
- UTF-8 trailing-whitespace scan of R1 frontend candidates was clean.
- Physical lines remain bounded: selector `82`, hook `101`, editor `24`, editor test
  `119`, stylesheet `426`; no staged file was present.
- No real project/public-drive/workbook path reference appeared in the R1 frontend
  production paths.
- The current dirty worktree includes pre-existing TASK_364B authority/API and external
  TASK_363C/TASK_363D/TASK_365A/B/C, Fee, parser, frontend API-client, and release
  residuals. Per the Reviewer R1 boundary, QA neither attributed nor packaged those
  hunks. R1 remains limited to Point Profile selector/model/editor/CSS and focused
  tests; Matrix sample totals, Measurement Plan target authority, Fee, workbook,
  parser, LTR, and downstream consumers remain excluded.

## QA Decision

`QA gate: pass`

No implementation blocker remains. This user-facing UI candidate remains
`user_acceptance_pending`; recommended next role is **User acceptance**, not direct
Integrator packaging.

## 2026-07-19 Client-Plus-Consumer Package Re-Gate

Status: `qa_pass` for the reconciled nine-path package. This is a package-validation
result only; TASK_364B remains Integrator blocked pending Planner/Orchestrator
governance routing.

### Isolated Package Construction

QA used a new disposable detached-HEAD worktree at
`tmp/task_364b_ninepath_isolated4`, based on accepted TASK_364C commit
`b34f2c2cbcc3b27266b480d6ff76a604f06be452`.

The exact isolate contained only these nine paths:

1. `frontend/src/api/client.ts`
2. `frontend/src/contact-measurement-plan.css`
3. `frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.test.tsx`
4. `frontend/src/features/contact-measurement-plan/ProjectPointProfileEditor.test.tsx`
5. `frontend/src/features/contact-measurement-plan/ProjectPointProfileEditor.tsx`
6. `frontend/src/features/contact-measurement-plan/projectPointProfileSelectors.test.ts`
7. `frontend/src/features/contact-measurement-plan/projectPointProfileSelectors.ts`
8. `frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.test.tsx`
9. `frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.ts`

The client diff was exactly `11 / 0`. The SummaryCard test diff was exactly `1 / 0`
and contains only the required `cr_coverage` fixture addition. The other SummaryCard
test visual `8 / 2` hunk and `ContactMeasurementPlanSummaryCard.tsx` were absent.

The full isolated package diff was exactly `355 additions / 23 deletions`; no backend,
API, schema, TASK_364C governance, TASK_363C/D, TASK_365A/B/C, or external residual
path appeared. The worktree index remained empty.

### Regression And Build

In the isolated frontend worktree (with an independently installed temporary
`node_modules` directory):

```powershell
npm test -- --run src/features/contact-measurement-plan/projectPointProfileSelectors.test.ts \
  src/features/contact-measurement-plan/useProjectPointProfileModel.test.tsx \
  src/features/contact-measurement-plan/ProjectPointProfileEditor.test.tsx \
  src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.test.tsx \
  src/features/matrix-editor/MatrixEditorWorkspace.test.tsx --watch=false
# 5 files / 61 passed

npm run build
# tsc -b and Vite build passed; existing chunk-size advisory only
```

`git diff --check` exited 0 with no non-line-ending finding. Added-line trailing
whitespace and added-line real-data path scans had zero matches. Candidate staging was
empty. The largest checked R1 file was 498 physical lines, below the 500-line limit.

### Controlled Browser Smoke

Using the local `http://localhost:5173` UI without confirming or saving anything, QA
opened the read-only Test Points Setup route for project
`ce15026d119f408f80970ea7077f6e41` and set the browser viewport to `514x831`.

- The LLCR table rendered `Point category`, `Range`, and one native labelled CR
  checkbox (`Include P in CR`) with Add row, Cancel, and Confirm visible.
- The checkbox locator was unique, visible, enabled, and initially checked. One pointer
  click changed it once to unchecked. QA did not click Confirm or issue a write request.
- `document.scrollWidth` was 499 against `clientWidth` 514; the table width was
  `322 / 322`, so no horizontal overflow was observed.
- The fresh browser console had no warning or error.

Browser automation's Playwright `Space` and `Enter` dispatch did not change the native
checkbox state in this in-app browser binding. This matches the previously recorded
automation limitation rather than a product finding: the earlier controlled Chromium
smoke recorded actual Space activation once and native Enter no-op semantics. Focused
component coverage also remains green. The keyboard dispatch limitation is a
non-blocking QA residual, not a reason to include additional files or relax the package
boundary.

### Re-Gate Decision

`QA gate: pass` for the exact nine-path client-plus-consumer package.

Do not route directly to Integrator. Return to Planner/Orchestrator governance routing;
TASK_364B remains blocked from integration until its separate governance condition is
cleared.
