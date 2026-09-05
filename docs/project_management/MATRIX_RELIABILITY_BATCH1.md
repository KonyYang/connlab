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

## Standards review

Same-agent focused pass, not an independent Reviewer. No blocking standards defect identified in
the implemented slice. Reused API/adapter/draft boundaries; no database schema, dependency or framework
introduced. Further simplification of the first-confirm method's duplicated confirmation/error handling
can be considered during final review; do not expand into a publication-module rewrite.

## Spec review and remaining work

The full goal remains incomplete. `Step Description` / `Requirement` in the Group Step Workspace
are page-local overrides. Browser repro: changing only Step 1 description leaves Confirm disabled;
reloading restores `Visual Examination`, discarding the temporary change. They are absent from draft,
confirmed and export payloads. Do not declare all Matrix edits durable based on the row-field tests.

Awaiting User decision: are these **formal per-group/per-step Matrix values**, or **export-only text
adjustments**? This changes authority, persistence and downstream outputs. Do not silently apply a
step edit to the whole source row/all groups, disable the inputs to claim a fix, or pack the fields into
unrelated storage. If schema work is required, use the existing high-risk workflow and isolated migration
tests; real-data migration still needs explicit authority.

After that decision: complete the chosen step-edit round trip; assess navigation before the autosave
delay expires; review exact combined diff; run a risk-proportionate final QA matrix once on the clean
reviewed state, including browser/real export coverage. Then integrate and finish to ready_for_close.
This checkpoint is not final QA. No broad architecture redesign or unrelated UI cleanup is authorized.

Recovery: inspect board/Git and this checkpoint. Do not repeat task activation or recreate completed
work. Temporary browser harnesses are outside the repository in the current Codex work directory.
