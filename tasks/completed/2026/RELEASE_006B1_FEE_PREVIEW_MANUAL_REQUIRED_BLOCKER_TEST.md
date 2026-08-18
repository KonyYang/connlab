# RELEASE_006B1 Fee Preview Manual-Required Blocker Test

Date: 2026-07-25
Status: `tests-only implementation authorized / pending Developer implementation`
Lane: `fee-preview-manual-required-blocker-test`
Parent: `RELEASE_006_POST_PUSH_WORKTREE_RESIDUAL_COMMIT_AND_CLEANUP_RECONCILIATION`
Source audit: `RELEASE_006B_TEST_RESIDUAL_OWNERSHIP_AUDIT`
Implementation authorization: tests-only, exact bounded module only
Discard authorization: none
Commit authorization: none
Push authorization: none

## 1. Goal

Move one unique, already-observed frontend blocker contract into a new bounded
test module without modifying product code or the oversized mixed legacy test.

The contract is the exact `16/0` assertion hunk currently present only in the
dirty working-tree copy of:

```text
frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts
```

For a Fee line whose Unit Price is explicitly `manual_required`, the preview
must remain incomplete and `buildFeeEvaluationUpdateBlockers()` must report
the owning row and field with exact operator-facing copy.

## 2. Why This Lane Is Allowed

- RELEASE_006 Child A is accepted in local docs commit
  `267eb50a4247082344e3d7a64a7e58353540d4be`.
- The Child B Planner audit classified the exact `16/0` hunk as unique.
- Reviewer passed that classification and named this bounded future lane:
  `RELEASE_006B1_FEE_PREVIEW_MANUAL_REQUIRED_BLOCKER_TEST`.
- Reviewer implementation-readiness re-gate passed after the completed-support
  fixture correction.
- The User explicitly authorized tests-only implementation.

No product implementation, legacy-test edit, discard, cleanup, commit, or push
is authorized by this checkpoint.

## 3. Frozen Behavior Contract

Given one Group 1, Step 1 matrix Fee line with:

- test item `DIELECTRIC WITHSTANDING VOLTAGE`;
- `unit_price = null`;
- Unit Price field metadata state `manual_required`;
- Units `1`;
- Base Fee `0`;
- Testing Fee `null`;
- review-required status;

the public preview-model entry points must continue to produce:

```text
unitPrice   ""
unitType    "per reading"
units       "1"
baseFee     "0"
testingFee  "Pending"
```

The first row blocker must be:

```text
rowLabel    "Group 1, Step 1, DIELECTRIC WITHSTANDING VOLTAGE"
fields      ["Unit Price"]
rowMessage  "Complete Unit Price."
```

The test must also prove that the blocker owns only Unit Price. It must not
convert an absent manual value to `0`, synthesize a price, or alter Units,
Base Fee, Testing Fee, review metadata, or another row.

Existing manual-required Units and Base Fee blocker behavior remains a
read-only regression and is not reimplemented in this lane.

The local fixture must contain exactly one Group and one target DWV business
row, plus:

- one explicit completed Group Sample preparation manual row;
- one explicit completed top-level Report preparation manual row.

Both support rows must contain complete numeric/editable fields so the public
preview model does not synthesize Pending fallback rows. The expected preview
order is Sample preparation, target DWV, then Report preparation. The test
must inspect the complete, unfiltered blocker array and prove it contains
exactly one entry: the target DWV Unit Price blocker.

## 4. Exact Future May Touch

Test-only:

```text
frontend/src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts
```

Governance:

```text
tasks/RELEASE_006B1_FEE_PREVIEW_MANUAL_REQUIRED_BLOCKER_TEST.md
docs/release_006b1_fee_preview_manual_required_blocker_test_plan.md
docs/lane_evidence/RELEASE_006B1_fee-preview-manual-required-blocker-test_planner.md
docs/task_board.md
future role evidence for this exact lane
```

The new test module must remain at or below `250` UTF-8 physical lines,
including blank lines.

## 5. Must Not Touch

- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts`;
- all frontend production code, including `feeEvaluationPreviewModel.ts`;
- page, component, CSS, API client, schema, and backend code;
- the B2 multi-Group Base Fee unique hunk;
- the B3 real Damp Heat extractor unique hunk;
- the LLCR hydration duplicate, backend fixture support hunk, Thermal Shock
  duplicate, and Voltage Surge duplicate;
- Child C and every other tracked or untracked residual;
- dependencies, generated artifacts, real databases, files, or remote refs.

The old 1389-line test is read-only. Whole-file staging is forbidden.

## 6. Authorized Test-Only Implementation Contract

The authorized Developer pass may:

1. create the single bounded test module;
2. define a local minimal `FeeEvaluationDraft` / line fixture;
3. import only the accepted public preview-model functions and public DTO
   types needed by the assertion;
4. assert the exact preview and blocker values above.

It may not:

- change production behavior to make the test pass;
- import helpers from the oversized legacy test;
- create a shared production fixture or dependency;
- edit, move, or delete the old dirty `16/0` hunk.

## 7. TDD And Validation

This is a characterization-coverage lane. Accepted production behavior is
already green; therefore no product failure may be manufactured.

Coverage RED checkpoint:

- on clean accepted HEAD, the new bounded test module does not exist;
- accepted tests do not assert the exact row label, field ownership, and
  `Complete Unit Price.` copy together;
- record that absence before adding the bounded module.

GREEN checkpoint:

- add only the bounded test module;
- run it against clean accepted HEAD plus that one test file;
- it must pass without any product change.

Focused regression:

```powershell
Set-Location frontend
npm test -- --run src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts src/features/fee-evaluation/feeEvaluationPricingDraftHydration.test.ts src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts
npm run build
```

The old preview-model test in this command must come from clean accepted HEAD,
not the dirty working-tree residual.

Package validation:

```powershell
git diff --check
git diff --cached --check
git diff --numstat
git status --short
```

Reviewer must verify a one-test-file package, the `<=250` line limit, no
production diff, no old-test diff, and no unrelated residual.

## 8. Disposition Of The Old Hunk

The old `16/0` assertion remains untouched throughout this lane.

Only after the bounded replacement is Reviewer/QA/Integrator accepted may the
old hunk become an exact discard or restore candidate. That later operation
still requires Reviewer confirmation and explicit User authorization using the
required cleanup wording. This lane does not authorize it.

## 9. Acceptance Criteria

- the new bounded module alone proves all exact blocker values;
- no product or legacy-test file changes;
- focused tests and frontend build pass in an isolated clean-HEAD package;
- physical line count is `<=250`;
- UTF-8, trailing-whitespace, diff, whitelist, forbidden-path, and staging
  checks pass;
- no real data or generated artifact is read or written;
- no discard, cleanup, commit, or push occurs without later gates.

## 10. Stop Point

Current next role:

```text
Developer tests-only implementation pass
```

Do not route QA, Integrator, cleanup, discard, commit, or push before the
Developer test-only candidate and subsequent gates.
