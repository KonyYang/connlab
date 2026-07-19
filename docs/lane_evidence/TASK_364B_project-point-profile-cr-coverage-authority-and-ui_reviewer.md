# TASK_364B Reviewer Focused Implementation / Acceptance Gate

Date: 2026-07-19

Status: `reviewer_pass`

## Scope Reviewed

Reviewed the TASK_364B task, plan, Planner and Developer evidence, the R1 inline-table
candidate, and the existing Point Profile read/lifecycle contracts. This focused gate
reviews the R1 frontend hunk set only. The initial Point Profile authority/API/summary
implementation remains an inspected dependency; R1 adds no backend, API-client, DTO,
storage, or confirmed-summary behavior.

## Findings

No blocking findings.

- `ProjectPointProfileEditor` retains the LLCR heading and presents one native, labelled
  CR checkbox per category row. The former duplicate CR section and LLCR checkbox column
  are absent. The add-row command remains in the action header and the delete action
  retains an icon, title, and accessible label.
- The selector and model derive `follow_llcr` only when every visible row is selected.
  New rows start selected; any deselection derives `custom`; a zero-selection custom
  state remains invalid. Confirm serialization preserves the existing contract: follow
  sends row flags as false, while custom sends the visible row-owned selections.
- The inspected read projection supplies effective category ids for confirmed `follow`
  coverage, so hydration, the selected target, and the local row editor remain aligned.
  R1 does not alter Point Profile authority, target setup, Confirm/Cancel/Reload, Matrix
  group sample totals, Measurement Plan authority, Fee/workbook consumers, or generic
  outputs.

## Validation

- `npm test -- src/features/contact-measurement-plan MatrixEditorWorkspace.test.tsx`:
  `12` files, `91 passed`.
- `npm run build`: passed; the existing Vite chunk-size advisory remains non-blocking.
- Scoped `git diff --check`: passed with repository LF/CRLF notices only.
- Scoped UTF-8 trailing-whitespace scan: clean. R1 changed files are bounded (largest
  stylesheet: `426` physical lines); the index is empty.
- Disposable in-app browser smoke at effective `514x831`: document and table had no
  horizontal overflow; row input, CR checkbox, delete action, Add row, and footer actions
  did not overlap. The initial and newly added rows were CR-selected, pointer selection
  worked, and the fresh console had no warning or error.

The in-app automation layer did not dispatch the browser's default `Space` toggle for a
focused native checkbox. This is not treated as a product failure: the control is native,
has a visible focus treatment, and focused component tests cover the state transition.
QA must recheck physical keyboard activation in its controlled browser fixture.

## Package Isolation

The R1 hunk set is limited to the Point Profile selector/model/editor/CSS and their
focused tests. Backend/API/client/summary authority, Matrix group totals, Measurement
Plan authority, Fee/workbook/generic outputs, parser/LTR, real data/files, and
TASK_363C/TASK_363D/TASK_365A/B/C residuals remain excluded. The broader dirty worktree
contains initial authority work and unrelated residuals; none were absorbed into this
focused R1 conclusion.

## Next Legal Route

Route to **QA gate** for controlled browser re-smoke and user acceptance. Do not route
directly to Integrator.

## TASK_364C Dependency Release: Initial Calculation (Superseded)

Date: 2026-07-19

Status: `superseded by corrected reviewer calculation`

### Corrected Calculation

This initial blocker was caused by an arithmetic error while summing the per-file
numstat. Direct `git diff --numstat` calculation against accepted HEAD proves:

- the seven R1 paths total `343 additions / 23 deletions`;
- the exact client type hunk adds `11 / 0`; and
- the permitted SummaryCard fixture is one addition with no deletion.

The exact package target is therefore reproducible as `355 additions / 23 deletions`.
The full SummaryCard-test diff is `9 / 2`; its other `8 / 2` visual-test hunk remains
excluded. This correction restores the planned isolate review; it does not authorize
any extra hunk, optional-field weakening, or SummaryCard production change.

## Locked Scope Confirmed

No backend/API/schema authority hunk, `ContactMeasurementPlanSummaryCard.tsx`, Summary
visual-test hunk, optional-field weakening, TASK_363C/D, TASK_365A/B/C, or external
dirty residual was reviewed as eligible. TASK_364B remains Integrator blocked.

## Next Legal Route

Continue the current Reviewer package-boundary re-gate by constructing the exact
isolate. Do not route QA or Integrator until this gate finishes.

## TASK_364C Dependency Release: Client-Plus-Consumer Package Re-Gate

Date: 2026-07-19

Status: `reviewer_pass`

### Accepted Baseline And Exact Isolate

Reviewed against accepted TASK_364C baseline `b34f2c2cbcc3b27266b480d6ff76a604f06be452`.
A disposable LF worktree was created at that commit and received only the frozen hunk
set. Its source numstat is exactly `355 additions / 23 deletions`:

- seven R1 selector/model/editor/CSS paths: `343 / 23`;
- `frontend/src/api/client.ts`: exactly `11 / 0`; and
- `ContactMeasurementPlanSummaryCard.test.tsx`: exactly one `cr_coverage` fixture line
  (`1 / 0`).

The resulting isolate changes exactly nine paths. The `client.ts` hunk adds the required
CR coverage types, confirmed-revision field, direct category flag, and direct-confirm
mode; it does not weaken any field to optional. The one SummaryCard-test fixture line
is required to satisfy that now-required response contract.

### Scope Findings

No package-boundary blocker found.

- `ContactMeasurementPlanSummaryCard.tsx` is absent from the isolate. The remaining
  `8 / 2` SummaryCard visual-test hunk is also absent.
- No backend, API, schema, storage, TASK_364C governance, TASK_363C/D, TASK_365A/B/C,
  or other dirty-worktree path is present.
- The R1 implementation keeps its stated UI behavior: LLCR heading retained, native
  row-owned CR selection, new rows selected, all-selected `follow_llcr`, custom
  validation, and serialisation through the required direct-confirm fields.

### Reproduced Validation

- Exact-isolate `git diff --check`: passed (only repository LF/CRLF notices).
- Focused frontend suite in the exact isolate: `5` files / `61 passed`:
  selectors, model, editor, SummaryCard fixture consumer, and MatrixEditorWorkspace.
- Exact-isolate `npm run build` (`tsc -b && vite build`): passed. The existing Vite
  chunk-size advisory remains non-blocking.

### Next Legal Route

Route only to **QA package validation**. QA must preserve this nine-path hunk boundary,
perform its controlled frontend/browser validation, and continue to exclude SummaryCard
production/visual hunks, backend authority paths, and all external residuals. TASK_364B
must not route directly to Integrator.
