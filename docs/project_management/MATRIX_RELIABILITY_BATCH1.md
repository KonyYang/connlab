# Matrix experience and reliability — batch 1

Task: `TASK_MATRIX_EXPERIENCE_RELIABILITY_BATCH1`. Baseline: `d407f3ffbe8d7fdb4b5a3772b2c4ef19ce68c04c`.
Status: implementation checkpoint, NOT complete or ready for close.

## Implemented

- Matrix Editor uses a dedicated identity/lifecycle loader instead of mounting the entire Workbench
  model. It waits for lifecycle information, reports load failures, supports retry, and ignores late
  responses from another project. Workbench itself retains its existing behavior.
- Registry receives active confirmed-Matrix presence from one batch query, without loading Matrix
  aggregates per row. Display is `Matrix Confirmed`, not an assertion that execution is ready.
  Stopped/closed lifecycle labels remain higher priority. Legacy Project status is unchanged.
- Imported drafts can save before first confirmation. Missing or changed import lineage is rejected;
  saving does not create confirmed authority. First confirmation reuses the imported draft rather
  than importing it again and rerunning unrelated source-file/standard resolution.
- Failed confirmation recovery keeps the editor and its content visible, with an error, instead of
  silently navigating back to Workbench.

## Evidence at this checkpoint (2026-09-05)

- RED: the old context loader issued 16 requests against a controlled HTTP fixture that supplied only
  identity, LTR, and lifecycle responses. GREEN: the new loader issues exactly 3. This is the context
  loader only, not total page requests or an end-user latency percentage. Real deployments need separate
  timing measurements; missing optional responses in the fixture limit the old request count.
- RED: a failed stale-confirm retry navigated away without showing its error. The new regression passes.
- RED: pre-confirmation autosave did not run; the API rejected it with HTTP 422. GREEN: isolated
  import/edit/save/reopen/confirm/export retains method, condition, requirement and source lineage.
  A mismatched source save returns 409 and leaves the saved signature unchanged.
- Latest affected frontend run: 10 files, 74 tests passed, Vitest duration 6.56 s. Production build
  passed (including TypeScript); Vite build phase 1.08 s. Not a full frontend-suite claim.
- Latest affected backend run: 57 tests passed in 10.26 s across editor session API/service, registry
  API/service, and live XLSX export API. One dependency deprecation warning about Starlette/httpx.
  The new round-trip test reads the actual XLSX bytes with openpyxl and checks retained field values.
- Browser: isolated server/data, edit method before confirmation, verify API persisted draft, reload
  and read identical method, confirm, inspect identical Workbench method, inspect registry status,
  reopen editor and download Matrix Draft successfully. Browser feedback does not substitute for
  the XLSX-byte assertions above.
- No real business data used or changed. Temporary frontend/backend listeners on 5187/8017 were
  stopped after validation. No release build was installed, no real-data migration, no push.

## Initial-slice Standards review

Same-agent focused pass, not an independent Reviewer. No blocking standards defect identified in
the implemented slice. Reused API/adapter/draft boundaries; no database schema, dependency or framework
introduced. Further simplification of the first-confirm method's duplicated confirmation/error handling
can be considered during final review; do not expand into a publication-module rewrite.

## Confirmed step-text requirement and work in progress

Initial browser repro: `Step Description` / `Requirement` were page-local overrides; changing only
Step 1 description left Confirm disabled and reload discarded it. The implementation below fixes
that storage/output gap; final independent review and QA still need to validate the complete batch.

User decision is resolved: step Description / Requirement are durable, group-local and step-local draft
values. Saving must leave existing formal authority unchanged. Successful Confirm publishes a new
immutable version; failure keeps the draft and prior authority and reports the error. No propagation
to another group, step, or shared source row. Null inherits the derived default; an empty string is an
explicit blank. Identity includes group, row, sequence and suffix.

Implementation uses additive draft/confirmed child records and the existing transaction/creation
mechanism, not unrelated JSON storage. Independent planning, backend development and focused review
contexts are used for this persistence risk; final independent QA/integration are still pending.
No real business database is opened for migration or testing.

Frontend RED/GREEN: step-only changes previously never saved; they now save, reopen and survive a
confirmation error. Targeted checks cover two groups, repeated LLCR steps, suffixes and explicit blanks.
Live Test Record requests now include the step-local edits without rewriting the shared test item.
Independent review also identified late autosave A overwriting newly loaded draft B identity; the
deferred-response regression failed before isolation and now passes along with existing Cancel checks.
These are Developer feedback checks, not the final QA claim.

Matrix XLSX remains the existing shared-row grid. Per-step text must not overwrite that row for all
groups or silently introduce a new worksheet/template format. Step-specific formal outputs use the
confirmed step projection; live draft outputs must be distinguished from confirmed authority.

Additional Developer checks: manually entered Matrix autosaves and keeps new source lineage; Confirm
waits for the current save, and browser refresh/close requests warn while edits are unsaved. This is
not a claim that every application-level navigation has a global route guard. Excluded groups keep
their draft text and invalidate the saved-draft signature without changing formal authority.

Developer evidence on the completed implementation: frontend 73 affected tests passed (9.08 s),
with a separate TypeScript check passed. Backend persistence/revision 79 passed (47.76 s); after the
last saved-signature change, 42 affected tests passed (25.08 s), with storage bytes unchanged.
Output tests 132 passed (43.36 s), including real isolated DOCX/XLSX checks, formal-authority matching
negatives and canonical test-item preservation. Those counts overlap and must not be summed as a
distinct-test total. Final QA is still pending.

Next: review exact combined diff; run a risk-proportionate final QA matrix once on the clean
reviewed state, including browser/real export coverage. Then integrate and finish to ready_for_close.
This checkpoint is not final QA. No broad architecture redesign or unrelated UI cleanup is authorized.

Recovery: inspect board/Git and this checkpoint. Do not repeat task activation or recreate completed
work. Temporary browser harnesses are outside the repository in the current Codex work directory.
