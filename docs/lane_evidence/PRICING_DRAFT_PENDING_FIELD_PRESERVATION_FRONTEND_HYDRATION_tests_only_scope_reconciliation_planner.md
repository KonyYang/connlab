# PRICING_DRAFT_PENDING_FIELD_PRESERVATION_FRONTEND_HYDRATION Tests-Only Scope Reconciliation

Date: 2026-07-24
Role: Planner
Status: `qa_blocked_pending_reviewer_tests_only_scope_gate`
Task: `PRICING_DRAFT_PENDING_FIELD_PRESERVATION_FRONTEND_HYDRATION`
Lane: `pricing-draft-pending-field-preservation-frontend-hydration`

## Gate Facts

- Developer product implementation is complete.
- Reviewer B2 implementation re-gate passed.
- QA's bounded Child 3 suites passed: frontend contract `37/37`, wrapper selector `6`,
  API compatibility `3/3`, and V2/currentness/CAS `37/37`.
- QA's read-only run of
  `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`
  produced `16 failed / 28 total`.
- Planner reran that exact module read-only with verbose reporting and reproduced the same
  sixteen node IDs. No product/test file was modified.

The product candidate is locked. This reconciliation proposes only an exact-node tests-only
scope for Reviewer approval. It is not tests-only implementation authorization.

## Classification A - Stale Assertions Or Fixtures Directly Conflict With B2/CAS

Only these six nodes may replace the described stale expectation/fixture:

1. Line 247:
   `FeeEvaluationReviewExportPage > sends current edited preview values to the Fee Form download`
   - Root cause: clicks Fee Form immediately after edits, before autosave plus fresh GET proves
     `current_v2`.
   - Migration: preserve all export payload assertions, but explicitly drive the per-node edit,
     successful save, and fresh `current_v2` GET sequence; assert no export before that GET and
     click only after the button is enabled.
2. Line 388:
   `FeeEvaluationReviewExportPage > seeds a missing pricing draft from defaults and confirms without an extra save`
   - Root cause: expects load-time missing-state seed write and confirmation. Accepted Child 3
     makes a missing load zero-write and non-current.
   - Migration: change this exact node to assert missing load does not save or confirm and leaves
     Update Fee disabled. Do not restore load-time seed behavior.
3. Line 491:
   `FeeEvaluationReviewExportPage > saves a reviewed rebase candidate before updating Fee`
   - Root cause: expects raw preview defaults instead of the server candidate and does not return
     fresh `current_v2` from the post-save GET.
   - Migration: assert server candidate values render while non-current; use a per-node ordered
     GET sequence `rebase_required -> current_v2`; assert save occurs before GET-based promotion
     and confirmation occurs only after fresh current proof.
4. Line 578:
   `FeeEvaluationReviewExportPage > blocks Update Fee at the incomplete Report preparation row without duplicate alerts`
   - Root cause: core Report preparation assertions remain valid, but the node also expects an
     obsolete missing-state automatic seed save.
   - Migration: provide explicit per-node current-V2 context for the Report-row scenario, remove
     only the seed-save expectation, and preserve all blocker/copy/no-confirm assertions.
5. Line 968:
   `FeeEvaluationReviewExportPage > restores the entry baseline before leaving when autosave already saved edits`
   - Root cause: old fixture does not model immutable entry CAS, latest session-owned CAS, reload
     before restore, exact-CAS restore, and final read verification.
   - Migration: use per-node ordered current-V2 GET/save responses for entry, autosave, reload,
     restore, and verification; preserve baseline payload assertions and add exact CAS assertions.
6. Line 1018:
   `FeeEvaluationReviewExportPage > stays on Fee Evaluation when baseline restore fails`
   - Root cause: its single rejected save models autosave failure rather than a restore failure
     under the accepted session-owned-CAS sequence.
   - Migration: make autosave succeed, reload prove the session-owned current V2, then reject only
     the restore save; preserve no-navigation, error, and no-blind-overwrite assertions.

## Classification B - Business Assertion Valid, Per-Node Fresh-Current Fixture Missing

These ten nodes retain their stated Matrix/lifecycle/export/negative business assertion. Only
their local pricing-draft fixtures and directly dependent currentness assertions may change:

1. Line 432:
   `confirms Fee Evaluation with the latest autosaved draft id without saving again`
   - Add ordered missing/edit-save/fresh-GET-current-V2 facts; preserve latest id and one-save
     assertions.
2. Line 633:
   `loads a promoted current pricing draft and allows Update Fee when authority is missing`
   - Replace compatibility `current` with an explicit attested `current_v2` fixture; preserve
     payload hydration and confirmation assertions.
3. Line 718:
   `normalizes pending numeric values from promoted pricing draft before confirming`
   - Provide explicit current-V2 context; preserve Pending normalization and summary assertions.
4. Line 774:
   `allows Update Fee refresh when confirmed fee is stale and promoted draft is current`
   - Provide explicit current-V2 pricing context; preserve stale-confirmed-fee refresh behavior.
5. Line 878:
   `does not confirm when autosave succeeds without a pricing draft id`
   - Make the save response V2-shaped while retaining a null draft id; preserve the negative
     no-confirm/no-current assertion.
6. Line 1094:
   `stays on Fee Evaluation when the Matrix or fee context changed before restore`
   - Use explicit per-node current-V2 entry/latest responses before the changed context; preserve
     typed conflict, no restore write, and no navigation.
7. Line 1134:
   `keeps the Fee file action enabled when the project folder path is missing`
   - Supply explicit current-V2 pricing state; preserve the independent missing-folder assertion.
8. Line 1147:
   `downloads the generated Fee file through the direct download endpoint`
   - Supply explicit current-V2 pricing state; preserve direct-download and anchor assertions.
9. Line 1180:
   `shows timeout cleanup guidance from structured API detail`
   - Supply explicit current-V2 pricing state; preserve structured error and cleanup guidance.
10. Line 1201:
    `shows the template-missing download error instead of a Matrix blocker`
    - Supply explicit current-V2 pricing state; preserve template-error and no-Matrix-blocker
      assertions.

## Classification C - Product Regression Or External Residual

- No product regression was identified from these sixteen failures.
- No unrelated external product residual was identified in this module run.
- All twelve passing legacy nodes remain read-only and must not be modified.
- Browser automation availability is a non-product QA tooling residual. It does not relax the
  controlled disposable desktop/514px browser gate and does not authorize the normal app or
  operator configuration.

## Exact Proposed Tests-Only May Touch

`frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx` may become a
tests-only path only after Reviewer approval, and only at the sixteen exact nodes above.

The following are forbidden:

- whole-file authorization or staging;
- edits to the twelve passing nodes;
- global `arrangeSuccessfulContext()` changes that force every test to `current_v2`;
- weakening the production fresh-GET gate, CAS rules, or export no-call behavior;
- changing Matrix/lifecycle/export payload semantics;
- increasing the file beyond its current `1718` UTF-8 physical lines including blanks.

Prefer line-neutral replacement. If a required new assertion cannot fit line-neutrally, add it to
the already-approved bounded
`FeeEvaluationReviewExportPage.pricingDraftHydration.test.tsx` and keep the legacy file at or
below `1718`.

## Required Validation

1. Run each sixteen-node selector and the complete legacy module: `28/28`.
2. Rerun bounded Child 3 frontend contract: `37/37`.
3. Rerun six read-only model wrapper nodes.
4. Rerun API compatibility `3/3` and V2/currentness/CAS `37/37`.
5. Run frontend build, diff/trailing/line/scope/staging/no-real-data checks.
6. Use a controlled disposable browser harness or the previously audited harness; do not launch
   the normal app against operator configuration.

## Locked Scope

All product files are locked. Child 1/2, TASK_361L/TASK_363D V2 authority, frontend API client,
CSS, schema/database, seeds, formulas, export services, the non-atomic umbrella, real data/files,
generated artifacts, and external residuals remain locked.

## Next Legal Role

Reviewer tests-only scope gate. Do not route Developer, QA, or Integrator until Reviewer confirms
the exact sixteen-node boundary.
