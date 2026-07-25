# RELEASE_006B1 Final Authorization Reconciliation

Date: 2026-07-25
Role: Planner
Status: `tests-only implementation authorized / pending Developer implementation`
Task: `RELEASE_006B1_FEE_PREVIEW_MANUAL_REQUIRED_BLOCKER_TEST`
Lane: `fee-preview-manual-required-blocker-test`
Parent: `RELEASE_006_POST_PUSH_WORKTREE_RESIDUAL_COMMIT_AND_CLEANUP_RECONCILIATION`

## 1. Gate Record

Completed gates:

- Child B ownership audit Reviewer pass;
- RELEASE_006B1 plan gate pass;
- User approval for Developer tests-only planning-first;
- Developer docs-only planning-first and B1 fixture correction complete;
- Reviewer implementation-readiness re-gate pass;
- User explicit tests-only implementation approval.

The current effective state is:

```text
tests-only implementation authorized / pending Developer implementation
```

Earlier planned-only, pending Reviewer, and implementation-unauthorized
statements are historical checkpoints superseded by this reconciliation.

## 2. Exact Authorized May Touch

Developer may create only:

```text
frontend/src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts
```

Maximum:

```text
<=250 UTF-8 physical lines including blanks
```

No other test or product path is authorized.

## 3. Frozen Fixture

The bounded test must use:

- one Group;
- one Step 1 `DIELECTRIC WITHSTANDING VOLTAGE` target row;
- one explicit completed Group Sample preparation manual row;
- one explicit completed top-level Report preparation manual row.

The support rows must provide complete Man-hour, Unit Price, Unit Type, Units,
Base Fee, Discount, and Testing Fee values. They exist only to prevent the
accepted public model from generating Pending fallback rows.

Expected preview order:

```text
sample-preparation:g1
manual-unit-price:1:0
manual-report-preparation
```

The test must inspect the complete unfiltered blocker array. It must contain
exactly one blocker, owned by the target DWV row.

## 4. Exact Assertions

Target preview:

```text
unitPrice   ""
unitType    "per reading"
units       "1"
baseFee     "0"
testingFee  "Pending"
```

Only blocker:

```text
rowLabel    "Group 1, Step 1, DIELECTRIC WITHSTANDING VOLTAGE"
fields      ["Unit Price"]
rowMessage  "Complete Unit Price."
```

No support row or synthetic fallback may be filtered away to obtain this
result.

## 5. TDD And Validation

Coverage RED:

- clean accepted HEAD lacks the bounded test module;
- accepted coverage does not assert the complete exact blocker tuple.

Unchanged-product GREEN:

- add only the bounded test;
- pass it against clean accepted production;
- require zero product diff and zero old-test diff.

Required focused/full validation:

```powershell
Set-Location frontend
npm test -- --run `
  src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts `
  src/features/fee-evaluation/feeEvaluationPricingDraftHydration.test.ts `
  src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts
npm run build
```

The legacy test in validation must come from clean accepted HEAD, not the
dirty working-tree residual.

## 6. Locked Paths And Facts

Read-only legacy test:

```text
frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts
1389 UTF-8 physical lines including blanks
dirty numstat 114/0
SHA-256 D2BF49BBDDCCC3971D81594B98208B5BC979344CAA74C64996F2AB1D64BACD95
```

Locked:

- all frontend and backend production code;
- API client, schema, database, dependencies, CSS, and package files;
- B2/B3 unique hunks;
- all duplicate/support hunks;
- Child C and every external residual;
- real data/files and generated artifacts;
- discard, restore, cleanup, staging, commit, and push.

The old `16/0` hunk remains untouched. It may become a later cleanup candidate
only after the bounded replacement is accepted and a separate Reviewer/User
cleanup gate authorizes the exact action.

## 7. Package Isolation

The Developer candidate must show:

- exactly one new test module;
- no edit to the old 1389-line test;
- no product diff;
- no B2/B3 or duplicate/support hunk;
- no Child C or external residual;
- physical line count within the frozen maximum;
- UTF-8, trailing-whitespace, diff-check, whitelist, forbidden-path, and
  no-real-data/generated-output checks.

This authorization does not permit staging or committing the candidate.

## 8. Next Legal Role

```text
Developer tests-only implementation pass
```

Do not route QA or Integrator until Developer and Reviewer gates complete.
Do not discard, clean, stage, commit, or push.
