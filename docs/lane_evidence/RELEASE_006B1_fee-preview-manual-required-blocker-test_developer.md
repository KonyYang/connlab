# RELEASE_006B1 Developer Evidence

Date: 2026-07-25
Role: Developer tests-only implementation
Status: `ready_for_reviewer_diff_gate`
Task: `RELEASE_006B1_FEE_PREVIEW_MANUAL_REQUIRED_BLOCKER_TEST`
Lane: `fee-preview-manual-required-blocker-test`
Parent: `RELEASE_006_POST_PUSH_WORKTREE_RESIDUAL_COMMIT_AND_CLEANUP_RECONCILIATION`

## Gate

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

The earlier docs-only planning pass was allowed because Reviewer evidence
recorded `reviewer_plan_pass` and the User explicitly approved Developer
tests-only planning-first.

Reviewer subsequently blocked implementation-readiness on B1: an empty
Group/top-level manual-row fixture triggers accepted Pending Sample
preparation and Report preparation fallback rows. This bounded follow-up
changed only the plan/evidence fixture contract.

Reviewer then passed the implementation-readiness re-gate, the User
explicitly approved tests-only implementation, and Planner reconciled the
source of truth. The current implementation pass may create only:

```text
frontend/src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts
```

Product implementation remains unauthorized.

## Required Reads

Read completely and applied:

- `AGENTS.md`
- `docs/task_board.md`
- the RELEASE_006B1 task and plan
- RELEASE_006B1 Planner and Reviewer evidence
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/TASK_REVIEW_CHECKLIST.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- accepted public preview model/type definitions and the relevant clean-HEAD
  and dirty legacy-test node

## Repository Audit

Read-only commands and results:

```text
git rev-parse HEAD
  267eb50a4247082344e3d7a64a7e58353540d4be

git branch --show-current
  master

git rev-parse origin/master
  580fbb5ecc5a7fb8ffbdd151fb5198bd1db51db5

git rev-list --left-right --count origin/master...HEAD
  0  1

git diff --cached --quiet
  exit 0; index empty
```

Legacy and future path facts:

```text
frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts
  exists
  1389 UTF-8 physical lines including blanks
  dirty numstat 114/0
  SHA-256 d2bf49bbddccc3971d81594b98208b5bc979344caa74c64996f2ab1d64bacd95

frontend/src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts
  absent
```

The working tree contains many unrelated dirty/untracked residuals. None was
cleaned, restored, staged, or absorbed.

## Technical Review

The future test requires only existing public contracts:

- `FeeEvaluationDraft`
- `FeeEvaluationLineItem`
- `buildFeeEvaluationPreviewRows()`
- `applyFeeEvaluationPreviewEdits()`
- `buildFeeEvaluationUpdateBlockers()`

The accepted production model is read-only and currently 925 physical lines.
The accepted hydration regression is read-only and currently 198 lines.
`frontend/package.json` exposes `test: vitest run` and
`build: tsc -b && vite build`; no package or dependency change is needed.

The clean-HEAD legacy node already verifies that manual-required Unit Price
stays blank and Testing Fee stays Pending. The dirty unique `16/0` hunk adds
the exact blocker tuple:

```text
rowLabel  Group 1, Step 1, DIELECTRIC WITHSTANDING VOLTAGE
fields    Unit Price only
copy      Complete Unit Price.
```

Therefore RED is a coverage absence, not a production failure. A future
Developer must not alter production to create or satisfy RED.

Reviewer B1 was independently confirmed from the accepted model:

- absent/empty `group.manual_line_items` creates a Pending Sample preparation
  row before Matrix rows;
- absent/empty `draft.manual_line_items` creates a Pending Report preparation
  row after Matrix rows;
- `buildFeeEvaluationUpdateBlockers()` scans the real row list without
  ignoring those fallbacks.

## Executable Plan

The plan now freezes:

1. one local complete `FeeEvaluationLineItem` factory;
2. one target Step 1 DWV business row;
3. one explicit completed Group Sample preparation row;
4. one explicit completed top-level Report preparation row;
5. one `FeeEvaluationDraft` with one Group and those three rows;
6. exact row order: Sample preparation, DWV, Report preparation;
7. exact input metadata and five DWV preview assertions;
8. full blocker-array length one plus exact DWV Unit Price blocker;
9. one future test node and no shared fixtures;
10. accepted-HEAD isolate/exact reconstruction before testing;
11. GREEN against unchanged production;
12. focused Vitest, read-only legacy/hydration regressions, and frontend build;
13. exact new-test whitelist, `<=250` physical lines, old-test hash/line
   preservation, and zero product diff.

Detailed fixture fields, public signatures, commands, risks, rollback, and
acceptance criteria are recorded in
`docs/release_006b1_fee_preview_manual_required_blocker_test_plan.md`.

## Scope

Current docs-only May Touch used:

- `docs/task_board.md` (RELEASE_006B1 status hunks only)
- `tasks/RELEASE_006B1_FEE_PREVIEW_MANUAL_REQUIRED_BLOCKER_TEST.md`
- `docs/release_006b1_fee_preview_manual_required_blocker_test_plan.md`
- this Developer evidence

Future test May Touch remains exactly:

```text
frontend/src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts
```

with `<=250` UTF-8 physical lines including blanks.

Locked and unchanged:

- `feeEvaluationPreviewModel.test.ts`
- all product/frontend/backend/API/schema/database/package code
- B2/B3, duplicate/support hunks, Child C, and external residuals
- real data/files and generated artifacts
- discard, restore, cleanup, stage, commit, push, and remote refs

The future bounded test path was not created.

## Planning Self-Review

- Scope: one tests-only characterization; no additional behavior.
- Layering: test consumes public feature/model contracts only.
- Data: local typed fixture; no API, database, file, or Office access.
- Dependencies: no new runtime or package dependency.
- Size: future test capped at 250 lines.
- TDD: coverage RED, unchanged-product GREEN.
- B1: completed manual rows prevent fallback blockers without filtering the
  public model output.
- Rollback: omit or later revert only the bounded test.
- Package isolation: clean HEAD plus one new test; old mixed test read-only.
- Placeholders/TODOs: none in the executable plan.

## Docs-Only Validation

Validation performed without npm, test execution, dependency generation, or
build artifacts:

- all required governance files read as UTF-8;
- HEAD/branch/origin/index facts checked;
- dirty worktree enumerated read-only;
- old/future test path, line, hash, and numstat facts checked;
- existing model functions and client types inspected;
- implementation path not created;
- no stage, commit, push, real-data, or generated-output action performed.

Final docs-only checks:

```text
UTF-8 physical lines
  board      2398
  task       199
  plan       679
  evidence   246 before this B1 validation update

trailing whitespace
  0 matches across board/task/plan/evidence

tracked board git diff --check
  passed

task/plan/evidence no-index diff --check
  expected exit 1 for add-file diffs; no whitespace error

placeholder scan
  clean

legacy test
  1389 lines
  SHA-256 unchanged
  dirty numstat remains 114/0

future bounded path
  absent

package/output status
  frontend package files, frontend/dist, data, and dist_release clean

index
  empty
```

The only current-role edits are RELEASE_006B1 board/task/plan/evidence
governance. The legacy test status shown by Git is pre-existing and remained
read-only.

## B1 Docs-Only Fix Validation

The corrected fixture contract was checked without running Vitest, npm, a
frontend build, or any implementation command:

- stale wording that omitted local manual rows is absent from the task, plan,
  Developer evidence, and RELEASE_006B1 board entries;
- the future fixture explicitly supplies one completed Group Sample
  preparation row and one completed top-level Report preparation row;
- the expected preview order is Sample preparation, target DWV, then Report
  preparation;
- the assertion inspects the complete blocker array and requires exactly one
  blocker, the target DWV `Unit Price`; it does not filter support rows;
- the single-Group/single-DWV business focus and the future `<=250`-line test
  budget remain unchanged;
- the future bounded test path remains absent;
- the locked mixed legacy test remains 1389 physical lines, SHA-256
  `d2bf49bbddccc3971d81594b98208b5bc979344caa74c64996f2ab1d64bacd95`,
  and dirty numstat `114/0`;
- tracked board `git diff --check` passed; each untracked task/plan/evidence
  no-index check returned the expected add-file exit `1` with no whitespace
  error;
- frontend package files, `frontend/dist`, `data`, and `dist_release` have no
  scoped status;
- the Git index is empty.

## Tests-Only Implementation

Created only:

```text
frontend/src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts
```

The bounded module:

- defines its own complete local `FeeEvaluationLineItem` factory;
- supplies one completed Group Sample preparation row;
- supplies one completed top-level Report preparation row;
- supplies one Group 1 / Step 1 DWV row with manual-required Unit Price;
- verifies exact sample, DWV, report preview order;
- verifies the target preview values remain blank/per-reading/1/0/Pending;
- passes the complete, unfiltered row array to
  `buildFeeEvaluationUpdateBlockers()`;
- requires exactly one blocker with the frozen row label,
  `fields=["Unit Price"]`, and `rowMessage="Complete Unit Price."`.

No production, legacy-test, package, dependency, API, schema, database, CSS,
B2/B3, duplicate/support, Child C, or external-residual path was edited.

## Implementation Validation

Coverage RED:

```text
clean HEAD bounded path: absent
clean HEAD exact "Complete Unit Price." coverage in feature tests: absent
```

Direct GREEN in the working tree:

```text
npm test -- --run \
  src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts

1 file passed, 1 test passed
```

Clean-HEAD isolated focused regression, with only the new bounded module
copied into the isolate:

```text
feeEvaluationPreviewManualRequiredBlockers.test.ts  1 passed
feeEvaluationPricingDraftHydration.test.ts          4 passed
feeEvaluationPreviewModel.test.ts                  28 passed
total                                                33 passed
```

Clean-HEAD isolated full frontend regression:

```text
54 test files passed
384 tests passed
```

Clean-HEAD isolated frontend build:

```text
npm run build
passed
```

The build emitted only the existing Vite chunk-size warning. The full suite
also emitted existing intentional error-path logs and React `act(...)`
warnings; all tests passed. The temporary isolate and its build output were
removed outside the repository after validation, and the workspace
`frontend/node_modules` remained intact.

Package and scope checks:

```text
new test physical lines  181 (limit <=250)
new test trailing         0
new test SHA-256          907803d09e900bc277f7495406897a6b15b87fa3f6dd0cc5f6c23c9aaaf7af92
new test no-index check   expected add-file exit 1, no whitespace error

legacy test physical lines  1389
legacy test SHA-256          d2bf49bbddccc3971d81594b98208b5bc979344caa74c64996f2ab1d64bacd95
legacy test dirty numstat    114/0

HEAD                    267eb50a4247082344e3d7a64a7e58353540d4be
worktree status         54 = 37 tracked + 17 untracked
status delta            one authorized new untracked test
product/package status  no TASK_006B1 changes
staged index            empty
real data/files         not accessed
stage/commit/push       not performed
```

## Result

Status:

```text
ready_for_reviewer_diff_gate
```

Remaining blocker: none for Reviewer diff gate.

Next legal role: Reviewer diff gate. Do not route QA, Integrator, cleanup,
discard, restore, stage, commit, or push.
