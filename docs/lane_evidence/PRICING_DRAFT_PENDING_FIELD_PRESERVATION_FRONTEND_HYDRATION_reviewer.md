# PRICING_DRAFT_PENDING_FIELD_PRESERVATION_FRONTEND_HYDRATION Reviewer Evidence

Date: 2026-07-24
Role: Reviewer
Status: `reviewer_blocked_docs_only_fix`
Task: `PRICING_DRAFT_PENDING_FIELD_PRESERVATION_FRONTEND_HYDRATION`
Lane: `pricing-draft-pending-field-preservation-frontend-hydration`

## Findings

### B1 - Locked hydration test has no frozen compatibility path

The plan requires extracting saved-draft hydration from
`frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts` into the
new `feeEvaluationPricingDraftHydration.ts`, while also declaring the existing
`feeEvaluationPreviewModel.test.ts` read-only. That locked `1389`-line test
directly imports and executes
`hydrateFeeEvaluationPreviewEditsFromSavedDraft` at six existing nodes.

The effective plan does not specify how the existing public symbol remains
available after the extraction. As written, implementation must either remove
the symbol and fail the locked regression, or edit the oversized locked test.
Neither outcome is within the declared package.

**Required docs-only correction:** freeze one narrow compatibility contract:

1. the new helper owns the hydration implementation;
2. `feeEvaluationPreviewModel.ts` retains an explicit compatibility re-export
   or one-line delegation for `hydrateFeeEvaluationPreviewEditsFromSavedDraft`
   (and its public result type if moved);
3. the helper may consume model types only through type-only imports, or shared
   types must move to a one-way module, so the compatibility layer cannot form
   a runtime import cycle;
4. the wrapper/re-export is included in the `<=930` model budget and the old
   test stays read-only, with its six hydration nodes rerun as regression
   evidence.

No product or test code is authorized by this finding.

## Readiness Facts Verified

- Board status is planned-only/dependency released/pending Reviewer plan gate;
  product implementation remains unauthorized.
- Child 1 commit `c5d91c36c5e1d54885fc0a3b406c92ff9aa0cb6b` and Child 2 commit
  `dff635a6489f2664f7e496c424ceff8400237283` are HEAD ancestors; current HEAD
  equals Child 2. Both remain read-only baselines.
- The API mapper's current residual correctly keeps Pending Unit Price, Units,
  and Testing Fee blank while Base Fee stays backend-owned.
- The Fee page currently discards the server `rebase_required` payload and
  instead renders raw preview defaults, so the planned narrow hydration/status
  repair is justified. It must remain non-current until explicit server save
  and reload/revalidation.
- The planned locks correctly exclude frontend API client, CSS, backend V2
  policy/attestation/currentness/CAS modules, Base Fee precedence, duration
  authority, formulas, seeds, schema/database, exports, Child 1/2, and real
  data. Child 3 has not been authorized to implement them.

## Next Legal Role

Planner docs-only fix for B1, followed by Reviewer Child 3 plan/dependency-
release re-gate. Do not route Developer planning-first, product implementation,
QA, or Integrator. The parent umbrella remains non-atomic.

## B1 Plan And Dependency-Release Re-Gate

Date: 2026-07-24

### Result

`reviewer_pass` for the Child 3 plan/dependency-release gate. Developer
planning-first and product implementation remain unauthorized pending the
separate User approval.

### B1 Closure Verified

The task, plan, Planner evidence, dependency reconciliation, and board now
freeze one executable compatibility path:

- `feeEvaluationPricingDraftHydration.ts` owns the moved implementation and is
  bounded to `<=300` lines.
- `feeEvaluationPreviewModel.ts` runtime-imports that helper but retains
  `hydrateFeeEvaluationPreviewEditsFromSavedDraft`, its existing signature,
  and `FeeEvaluationSavedDraftHydrationResult` as a narrow public
  wrapper/delegation.
- Helper references to model-owned types are explicitly type-only; a helper
  runtime import of the model and any helper-model runtime cycle are forbidden.
- No shared type module is authorized. If type-only imports prove insufficient,
  implementation must stop for a new scope gate.
- The compatibility wrapper/import/type remains inside the model's final
  `<=930` budget. The old `1389`-line test remains read-only and keeps its six
  existing imports/calls at lines `797`, `910`, `956`, `997`, `1033`, and
  `1073`; the new bounded test covers the helper directly.

### Remaining Gate Conclusions

- Child 1/2 accepted commits are verified HEAD ancestors and remain read-only.
- The server continues to own Base Fee precedence, duration authority, field
  metadata, V2 attestation/currentness/rebase/CAS, and all Fee calculations.
  Child 3 only consumes typed payload state.
- The reviewed-rebase requirement is correctly scoped to rendering the server
  merged candidate as non-current until explicit save plus server
  reload/revalidation returns `current_v2`.
- Pending Unit Price, Units, and Testing Fee remain blank through the narrow
  route mapper; legacy/blocked/stale records remain non-hydrating and
  non-writing.
- Exact May Touch, bounded replacement tests, line budgets, API-client/CSS/
  schema/database/seeds/export locks, and controlled 514px/desktop smoke are
  sufficient for the next planning-first pass. Child 3 does not reopen the
  parent umbrella.

## Next Legal Role

User approval for Developer docs-only planning-first, followed by Planner
source-of-truth reconciliation. Do not route Developer product implementation,
QA, or Integrator directly.

## Implementation-Readiness Gate

Date: 2026-07-24

### Result

`reviewer_pass` for implementation readiness. Product implementation remains
unauthorized until separate User approval and Planner final reconciliation.

### Implementation Contract Verified

- The new helper has explicit `current_v2_compatibility` and
  `server_rebase_candidate` modes. The model retains the two-argument public
  compatibility wrapper and may add only a narrow delegation for the server
  candidate; runtime direction remains model to helper, with type-only helper
  references back to model-owned types.
- Value semantics are executable: `null` is non-hydrating, empty strings are
  Pending rather than browser defaults, literal `"0"` remains numeric, and
  manual-required Unit Price/Units stay blank. Testing Fee stays derived;
  Base Fee is consumed from the accepted Child 1 metadata/value and is not
  recomputed in the frontend.
- The page state machine now specifies zero-write loading/missing/reload,
  current-V2 hydration by stable identity, server-owned rebase-candidate
  hydration while non-current, fail-closed legacy/blocked/stale states, and
  explicit save plus fresh GET `current_v2` before Update Fee/consumers.
- Cancel now freezes entry payload/context/CAS separately from the latest
  session-owned CAS. A post-save restore first reloads, requires both context
  and latest-CAS equality, restores with exact CAS, and rereads/validates the
  entry signature. Concurrent replacement remains typed no-write.
- Mandatory mechanical extraction has a realistic `<=925` target within the
  model's `<=930` budget; helper and bounded test budgets, read-only legacy
  tests, narrow route/page ownership, API-client/CSS/schema/database/V2 locks,
  and desktop/514px browser validation are sufficient.

Child 1 and Child 2 commits are verified HEAD ancestors and remain read-only.
Child 3 still cannot implement any Base Fee precedence, duration authority,
Fee formula, V2 policy/attestation/currentness/CAS, API client, schema, or
external residual behavior. The parent umbrella remains non-atomic.

## Next Legal Role

User product implementation approval, followed by Planner final source-of-
truth reconciliation. Do not start Developer implementation, QA, or
Integrator directly.

## Implementation Gate

Date: 2026-07-24

### Result

`reviewer_blocked`.

### Blocking Finding

**B2 - Fee Form can invoke a production export before reviewed rebase has
become `current_v2`.** `FeeEvaluationReviewExportPage.tsx` sets the Fee Form
disabled reason from `feeFileDownloadBlocker(draftState)` only. A loaded
`rebase_required` candidate therefore remains clickable, and
`handleGenerateFeeFile` directly calls the production export client without
the required explicit pricing-draft save followed by fresh `GET current_v2`.

This violates the frozen reviewed-rebase contract: a server candidate remains
non-current until its explicit save and reload/revalidation; only after that
may *any* production consumer proceed. Server-side rejection is not a UI
license to invoke that consumer from a non-current candidate.

### Required Bounded Developer Fix

1. In `FeeEvaluationReviewExportPage.tsx`, make Fee Form unavailable whenever
   the pricing draft is not an attested `current_v2` state, including
   `rebase_required`, `missing`, compatibility `current`, stale, blocked, and
   loading/error states. Preserve the existing backend export guard; do not
   alter export services, client contracts, V2 authority, or Fee formulas.
2. Add the narrow regression in the already-authorized bounded
   `FeeEvaluationReviewExportPage.pricingDraftHydration.test.tsx`: a reviewed
   rebase candidate must not call `generateConfirmedMatrixFeeFileDownload`
   before explicit save plus fresh `GET current_v2`; the existing Update Fee
   path remains the only promotion boundary.
3. Re-run the Child 3 API compatibility, helper/page/model focused suites and
   frontend build. Keep the model wrapper, type-only helper boundary,
   Pending/null/zero semantics, CAS Cancel protection, Child 1/2 locks, and
   external-residual isolation unchanged.

### Independent Verification

- `tests/integration/test_fee_evaluation_pricing_draft_compatibility_api.py`:
  `3 passed`.
- Fee hydration/model focused Vitest suites: `37 passed`.
- `npm run build`: passed, with only the existing Vite chunk-size warning.
- The candidate's Pending mapper preserves `""` distinctly from literal
  `"0"`; the dual helper keeps server rebase values exact; the model-to-helper
  dependency is one-way with type-only helper imports. These findings remain
  valid, but do not close B2.

## Next Legal Role

Developer bounded fix pass for B2. Do not route QA or Integrator. Child 3's
parent umbrella remains non-atomic; Child 1/2 and external residuals stay
locked.

## B2 Implementation Re-Gate

Date: 2026-07-24

### Result

`reviewer_pass`. B2 is closed; the candidate may proceed only to the Child 3
QA gate.

### B2 Closure Verified

- Fee Form preserves its prior Matrix/lifecycle blocker and now additionally
  requires both pricing status `current` and saved-page state. Thus missing,
  compatibility current, stale/blocked/error/loading, dirty/saving, and
  `rebase_required` remain unable to invoke the export client.
- A successful save response intentionally remains non-current. In
  `ensureCurrentPricingDraftSavedForUpdate()`, the page obtains a fresh GET,
  verifies `current_v2`, identity, canonical payload, and CAS facts, then and
  only then sets the status to `current`.
- The bounded regression proves Fee Form is disabled for a reviewed candidate
  and after its save response, cannot call the export client in either state,
  and becomes enabled only after fresh `current_v2` reload. Existing Matrix
  gates and the Update Fee CAS flow remain intact.
- Physical line counts including blanks are within the frozen budgets: page
  `1425`, page orchestration test `422`, model `925`, helper `288`.

### Independent Verification

- Bounded page orchestration suite: `4 passed`.
- Helper plus model suites: `33 passed`; combined Child 3 frontend focused
  suite: `37 passed`.
- Pricing-draft compatibility API: `3 passed`.
- `npm run build`: passed; only the existing Vite chunk-size warning remains.
- `git diff --check`: no diff errors beyond the workspace's existing LF/CRLF
  notices. No Child 1/2, V2 authority, API-client, schema/database, formula,
  or external-residual hunk was added by B2.

## Next Legal Role

QA gate for `PRICING_DRAFT_PENDING_FIELD_PRESERVATION_FRONTEND_HYDRATION`.
Do not route Integrator directly. Child 3's parent umbrella remains
non-atomic.

## QA Legacy Tests-Only Scope Gate

Date: 2026-07-24

### Result

`reviewer_pass_tests_only_scope`.

The read-only legacy module reproduces exactly `16 failed / 28 total`; the
failure mode is the new fresh-current gate, not a newly observed product
regression. The bounded Child 3 product candidate remains locked.

### Authorized Tests-Only Boundary

Developer may modify only these exact existing nodes in
`frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`:

1. `sends current edited preview values to the Fee Form download`
2. `seeds a missing pricing draft from defaults and confirms without an extra save`
3. `confirms Fee Evaluation with the latest autosaved draft id without saving again`
4. `saves a reviewed rebase candidate before updating Fee`
5. `blocks Update Fee at the incomplete Report preparation row without duplicate alerts`
6. `loads a promoted current pricing draft and allows Update Fee when authority is missing`
7. `normalizes pending numeric values from promoted pricing draft before confirming`
8. `allows Update Fee refresh when confirmed fee is stale and promoted draft is current`
9. `does not confirm when autosave succeeds without a pricing draft id`
10. `restores the entry baseline before leaving when autosave already saved edits`
11. `stays on Fee Evaluation when baseline restore fails`
12. `stays on Fee Evaluation when the Matrix or fee context changed before restore`
13. `keeps the Fee file action enabled when the project folder path is missing`
14. `downloads the generated Fee file through the direct download endpoint`
15. `shows timeout cleanup guidance from structured API detail`
16. `shows the template-missing download error instead of a Matrix blocker`

The six direct B2/CAS migrations must assert the fresh-current/no-call
boundaries described in the Planner reconciliation. The other ten may update
only their local pricing-draft fixtures and directly dependent currentness
assertions so their original business assertions run under an attested
`current_v2` context.

No whole-file authorization is granted: the twelve passing nodes and global
`arrangeSuccessfulContext()` are read-only. Keep the legacy file at or below
`1718` UTF-8 physical lines, preferring line-neutral substitution. If a
necessary additional assertion cannot fit, add it only to the existing bounded
`FeeEvaluationReviewExportPage.pricingDraftHydration.test.tsx` within its
`<=450` budget.

### Locks And Required Validation

- Do not modify product code, APIs, export services, V2 authority, Child 1/2,
  formulas, schema/database, CSS, API client, seeds, or external residuals.
- Do not weaken fresh GET `current_v2`, CAS, no-write, or Fee Form no-call
  guarantees.
- Rerun the sixteen nodes and full legacy module (`28/28`), Child 3 frontend
  focused suite, six read-only wrapper nodes, API compatibility, V2/CAS
  regressions, build, line/diff/trailing/scope/staging checks.

## Next Legal Role

Developer tests-only fix pass. Do not route QA or Integrator until this exact
scope is implemented and Reviewer re-gates it.

## QA Legacy Tests-Only Implementation Re-Gate

Date: 2026-07-24

### Result

`reviewer_pass`.

### Scope And Contract Review

- Actual changed-hunk mapping resolves to exactly the sixteen previously
  authorized `FeeEvaluationReviewExportPage` test nodes; the twelve original
  passing nodes and the shared `arrangeSuccessfulContext()` fixture have no
  diff.
- The migrated export-positive cases establish an attested `current_v2`
  snapshot with saved page state. The edited/export path also proves that a
  save response alone cannot call the Fee Form endpoint; only the remounted
  fresh-current context enables it.
- Missing, incomplete, rebase, failed-restore, and changed-context paths keep
  the relevant consumer disabled and assert no save, confirm, or download call
  where the B2 currentness/CAS contract requires it.
- The existing bounded hydration suite continues to cover the fresh-GET gate:
  rebase candidate and save-before-reload stay non-current, while the verified
  `current_v2` reload is the sole transition that enables Fee Form.
- The legacy test file is `1706` UTF-8 physical lines, within the `<=1718`
  budget. This pass adds no product, API, V2 authority, Child 1/2, CSS, client,
  schema, formula, or external-residual hunk.

### Independent Verification

- Legacy Fee page module: `28 passed`.
- Page hydration, preview-model, and helper suites: `65 passed` combined.
- `npm run build`: passed; only the existing Vite chunk-size warning remains.
- `git diff --check`: clean apart from pre-existing LF/CRLF notices; staging
  remains empty.
- The legacy module still prints existing React `act(...)` warnings from
  unchanged tests. They are not introduced by this tests-only migration and
  remain a QA observation rather than a Child 3 product blocker.

## Next Legal Role

QA re-gate for `PRICING_DRAFT_PENDING_FIELD_PRESERVATION_FRONTEND_HYDRATION`.
Do not route Integrator directly. Child 3's parent umbrella remains
non-atomic; Child 1/2 and all external residuals remain locked.
