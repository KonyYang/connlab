# RELEASE_006B1 Fee Preview Manual-Required Blocker Test Reviewer Evidence

Date: 2026-07-25
Role: Reviewer
Status: `reviewer_diff_gate_pass`
Task: `RELEASE_006B1_FEE_PREVIEW_MANUAL_REQUIRED_BLOCKER_TEST`
Lane: `fee-preview-manual-required-blocker-test`
Parent: `RELEASE_006_POST_PUSH_WORKTREE_RESIDUAL_COMMIT_AND_CLEANUP_RECONCILIATION`

## Conclusion

The planned-only RELEASE_006B1 lane passes the Reviewer plan gate.

This pass authorizes no test implementation, product change, discard,
cleanup, staging, commit, or push. The next legal role is User approval for
Developer tests-only planning-first. It is not Developer implementation.

## Findings

No blocking finding was identified.

The lane is correctly limited to the unique `16/0` manual-required Unit Price
blocker coverage confirmed by the Child B ownership audit. B2, B3,
duplicate/support hunks, Child C, and all external residuals remain excluded.

## Independent Repository Review

- `HEAD` is `267eb50a4247082344e3d7a64a7e58353540d4be`.
- `origin/master` is `580fbb5ecc5a7fb8ffbdd151fb5198bd1db51db5`.
- The index is empty.
- The future bounded test path does not exist.
- The dirty legacy test remains exactly `114/0`, 1389 UTF-8 physical lines,
  and read-only for this lane.
- The accepted public model exports
  `buildFeeEvaluationPreviewRows()`,
  `applyFeeEvaluationPreviewEdits()`, and
  `buildFeeEvaluationUpdateBlockers()`.
- Clean HEAD contains the existing manual-required Unit Price behavior node
  but does not assert the exact row label, `["Unit Price"]` ownership, and
  `Complete Unit Price.` copy together.
- The dirty unique hunk adds only that exact blocker assertion to the existing
  behavior node; the separate `98/0` LLCR hydration node remains excluded.

## Contract Review

The task and plan freeze one exact characterization:

- manual-required Unit Price remains blank;
- Testing Fee remains `Pending`;
- the row label is
  `Group 1, Step 1, DIELECTRIC WITHSTANDING VOLTAGE`;
- blocker fields are exactly `["Unit Price"]`;
- row copy is exactly `Complete Unit Price.`.

The proposed test can exercise the accepted public functions with a local
minimal fixture. It does not require a production change, shared fixture,
backend setup, UI rendering, API change, or new dependency.

The characterization RED/GREEN interpretation is valid: RED is the absence
of bounded accepted coverage, while GREEN is the new test passing against
unchanged accepted production. Manufacturing a product failure is forbidden.

## Scope And Package Review

Future test May Touch is exactly:

```text
frontend/src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts
```

The `<=250` UTF-8 physical-line limit is sufficient. The old 1389-line mixed
test remains read-only and cannot be staged whole-file. Validation must use a
clean-HEAD isolate or exact reconstruction so the dirty `114/0` residual is
not consumed accidentally.

The package and rollback contracts correctly preserve:

- zero product diff;
- zero legacy-test diff;
- no B2/B3 or duplicate/support ownership;
- no old-hunk discard before replacement acceptance and separate User
  authorization;
- no real-data or generated-artifact mutation;
- no implicit cleanup, commit, or push authority.

## Validation

Independent focused execution:

```text
npm test -- --run src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts
  -t "keeps a manually required unit price pending instead of defaulting it to zero"
```

Result:

```text
1 passed, 28 skipped
```

Governance/task facts reviewed:

- task: 199 physical lines;
- plan: 311 physical lines;
- Planner evidence: 226 physical lines;
- future bounded test path: absent;
- task, plan, evidence, and board agree on planned-only status, exact scope,
  locks, validation, and stop point.

## Next Legal Role

User decision only: approve Developer tests-only planning-first for
`RELEASE_006B1_FEE_PREVIEW_MANUAL_REQUIRED_BLOCKER_TEST`.

Do not route Developer implementation, QA, Integrator, discard, cleanup,
staging, commit, or push from this plan-pass checkpoint.

## Developer-Plan Implementation-Readiness Gate

Latest gate status:

```text
reviewer_implementation_readiness_blocked
```

The earlier plan gate remains passed. The Developer planning-first refinement
has one blocking fixture contradiction and is not yet implementation-ready.

### B1 - Empty manual rows create earlier fallback blockers

The refined fixture freezes:

```text
one Group containing the DWV line
no group manual rows
no top-level manual rows
```

That shape does not produce only the DWV preview row. The accepted
`buildFeeEvaluationPreviewRows()` implementation creates:

- a pending Sample preparation fallback whenever
  `group.manual_line_items` is absent or empty;
- a pending Report preparation fallback whenever
  `draft.manual_line_items` is absent or empty.

Both fallback rows contain incomplete fields. After
`applyFeeEvaluationPreviewEdits(rows, {})`,
`buildFeeEvaluationUpdateBlockers()` walks those rows in display order, so the
first blocker is not guaranteed to be the planned DWV Unit Price blocker.
The statement that the fixture "cannot pull in sample-preparation [or]
report" is therefore false against the current public implementation.

This is a planning/fixture defect, not a product defect. Production and tests
remain locked.

Required bounded docs-only correction:

1. Freeze complete local Sample preparation and Report preparation manual
   line fixtures so neither fallback is generated, matching the accepted
   legacy node's valid context; or freeze another equally explicit public-API
   fixture strategy that proves the full-row first-blocker contract without
   filtering away real fallback behavior.
2. Keep the exact DWV values, blocker tuple, one future bounded test path,
   `<=250` line budget, clean-HEAD isolation, and zero-product-diff contract.
3. Update the detailed fixture shape and expected row order in the plan and
   Developer evidence.
4. Do not add a product change, import legacy-test helpers, weaken the
   first-blocker assertion, or authorize implementation.

### Verified Facts

- Public `FeeEvaluationDraft` and `FeeEvaluationLineItem` types otherwise
  support the proposed local typed fixture.
- The three public preview functions and their signatures are correctly
  identified.
- The dirty legacy test remains 1389 lines with SHA-256
  `D2BF49BBDDCCC3971D81594B98208B5BC979344CAA74C64996F2AB1D64BACD95`
  and `114/0`; it was not modified by this review.
- The future bounded test path remains absent.
- The index remains empty.

## Current Next Legal Role

Developer docs-only planning fix for B1, followed by Reviewer
implementation-readiness re-gate.

Do not route tests-only implementation, QA, Integrator, discard, cleanup,
staging, commit, or push.

## B1 Implementation-Readiness Re-Gate

Latest gate status:

```text
reviewer_implementation_readiness_pass
```

The B1 fixture blocker is closed. No new blocking finding was identified.

### B1 Closure

The corrected future fixture now supplies:

- one completed Group Sample preparation manual row;
- one completed top-level Report preparation manual row;
- one target Group 1 / Step 1 DWV business row.

The support rows populate complete Man-hour, Unit Price, Unit Type, Units,
Base Fee, Discount, and Testing Fee values. Their presence prevents
`buildFeeEvaluationPreviewRows()` from synthesizing either accepted Pending
fallback row, and their complete values produce no update blocker.

The plan now freezes the complete preview order:

```text
sample-preparation:g1
manual-unit-price:1:0
manual-report-preparation
```

It also requires the unfiltered, complete blocker array to have exactly one
entry: the target DWV row with `fields=["Unit Price"]` and
`rowMessage="Complete Unit Price."`. This directly closes the prior finding;
the test may not filter out support or fallback rows.

### Independent Re-Gate Checks

- The local `completeLine()` shape satisfies the accepted
  `FeeEvaluationLineItem` contract.
- `unit_label="sample"` and `unit_label="report"` map to valid complete
  preview unit types.
- Both support rows retain numeric complete values after
  `applyFeeEvaluationPreviewEdits(rows, {})`.
- The target row retains blank manual-required Unit Price, `per reading`,
  Units `1`, Base Fee `0`, and Pending Testing Fee.
- The clean-HEAD coverage RED and unchanged-product GREEN interpretation
  remains valid.
- The future May Touch remains one absent bounded test module with a
  `<=250` physical-line limit.
- The 1389-line mixed legacy test remains read-only at SHA-256
  `D2BF49BBDDCCC3971D81594B98208B5BC979344CAA74C64996F2AB1D64BACD95`
  and `114/0`.
- Product code, B2/B3, duplicate/support hunks, Child C, discard, cleanup,
  staging, commit, push, and external residuals remain locked.
- The index remains empty.

Independent focused read-only regression:

```text
npm test -- --run src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts
  -t "keeps a manually required unit price pending instead of defaulting it to zero"
```

Result:

```text
1 passed, 28 skipped
```

## Re-Gate Next Legal Role

User decision only: explicit tests-only implementation approval followed by
Planner final source-of-truth reconciliation.

Do not route Developer implementation before that authorization and
reconciliation. Do not route QA, Integrator, discard, cleanup, staging,
commit, or push.

## Tests-Only Implementation Diff Gate

Latest gate status:

```text
reviewer_diff_gate_pass
```

No blocking finding was identified in the authorized tests-only candidate.

### Actual Diff Review

The only new implementation path is:

```text
frontend/src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts
```

It is 181 UTF-8 physical lines, below the `<=250` limit, with no trailing
whitespace.

The test:

- imports only accepted public DTOs and preview-model functions;
- defines local fixtures rather than importing from the oversized legacy
  test;
- supplies complete Sample preparation and Report preparation support rows;
- verifies the complete preview order without filtering rows;
- proves the target DWV preview keeps blank Unit Price and Pending Testing
  Fee;
- requires the complete blocker array to have exactly one entry;
- verifies the exact Group/Step/test-item label, Unit Price-only ownership,
  and `Complete Unit Price.` copy.

No product, API client, package, dependency, backend, schema, database, or
other test path is part of the RELEASE_006B1 implementation candidate.

### Scope And Isolation

- The old mixed test remains 1389 lines, SHA-256
  `D2BF49BBDDCCC3971D81594B98208B5BC979344CAA74C64996F2AB1D64BACD95`,
  and `114/0`.
- Clean HEAD contains 28 legacy preview-model nodes. The current dirty file
  contains one additional excluded LLCR duplicate node, explaining the
  one-test difference between clean-isolate and current-worktree counts.
- `feeEvaluationPreviewModel.ts`, `client.ts`, `package.json`, and the package
  lock have no diff.
- The index is empty.
- B2/B3, duplicate/support hunks, Child C, discard, cleanup, commit, push,
  real data, generated artifacts, and external residuals remain excluded.

### Independent Validation

Focused current-worktree run:

```text
3 files passed
34 tests passed
```

This equals the declared clean-HEAD isolate result of 33 plus the one known
excluded dirty LLCR legacy node.

Full current-worktree frontend run:

```text
54 files passed
385 tests passed
```

This equals the declared clean-HEAD isolate result of 384 plus the same known
excluded node.

Frontend build:

```text
tsc -b && vite build passed
```

The existing Vite chunk-size warning and existing test stderr/React act
warnings remain non-blocking and are unrelated to this tests-only file.

Diff, UTF-8, trailing, line-count, product-lock, package-lock, scope, and
staging checks passed.

## Diff-Gate Next Legal Role

QA isolated regression/build gate only.

Do not route Integrator, discard, cleanup, staging, commit, or push before QA
evidence and later authorization gates.
