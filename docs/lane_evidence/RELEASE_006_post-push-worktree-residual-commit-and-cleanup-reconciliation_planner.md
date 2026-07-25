# RELEASE_006 Planner Discovery Evidence

Date: 2026-07-25
Role: Planner
Status: scope_corrected_pending_reviewer_package_regate
Task: `RELEASE_006_POST_PUSH_WORKTREE_RESIDUAL_COMMIT_AND_CLEANUP_RECONCILIATION`
Lane: `post-push-worktree-residual-commit-and-cleanup-reconciliation`

## Result

Definition of Ready is satisfied for a planned-only non-atomic reconciliation
umbrella and Reviewer plan gate.

Only Child A's exact docs-only package is authorized; product/test, restore,
deletion, Child B/C execution, and push remain unauthorized.

## Independent Repository Facts

- `git rev-parse HEAD`:
  `580fbb5ecc5a7fb8ffbdd151fb5198bd1db51db5`.
- `git rev-parse origin/master`:
  `580fbb5ecc5a7fb8ffbdd151fb5198bd1db51db5`.
- `git rev-list --left-right --count origin/master...HEAD`: `0 0`.
- Index: empty.
- Pre-RELEASE_006 status: `52` entries, `37` tracked plus `15` untracked.
- RELEASE_005 Reviewer evidence exists and reports `reviewer_plan_pass`.
- RELEASE_005 QA evidence does not exist; prior QA was validation-only.
- RELEASE_005's four governance files account for the increase from its
  pre-Discovery `48` snapshot to current `52`.

## Confirmed Residual Model

- Class A candidate governance: `40` original paths plus `4` RELEASE_005 paths.
- Class B tests:
  - Fee preview frontend test `114/0`;
  - Confirmed Matrix Fee draft service test `38/13`;
  - spec section extractor test `51/0`.
- Class C:
  - one blank-line deletion `0/1`;
  - three untracked TASK_364A governance files.
- Class D:
  - mixed `docs/task_board.md`, never a whole-file package.

## Child A Boundary

Child A audits the exact `44` governance candidates and reconstructs only these
board hunk owners:

- top Status/Current Active/Proposed Next fields;
- RELEASE_005 and RELEASE_006 execution-model bullets;
- RELEASE_005 and RELEASE_006 lane rows.

It must split retained evidence from stale/duplicate candidates before any
package authorization. Reviewer package gate and explicit User authorization
precede an Integrator local docs-only commit.

## Child B Boundary

Child B is read-only. It compares each exact test hunk against accepted bounded
coverage:

- Child 3 hydration/currentness for Fee preview;
- Child 1 Base Fee precedence and single/multi-Group equivalence for Fee draft;
- accepted Damp Heat and TASK_365C parser coverage for the old extractor test.

Unique coverage becomes a separate tests-only child lane. Duplicate/stale
coverage becomes a precise discard candidate. Neither outcome is executable
without later Reviewer and User gates.

## Child C Boundary

- The profile-consumer change is a behavior-neutral one-blank-line restore
  candidate.
- No accepted commit contains the three TASK_364A files. Accepted HEAD
  references them only as unaccepted residuals.
- TASK_364A requires an archive/package/delete decision.
- Restore/delete is prohibited until Reviewer confirms the exact list and User
  approves. Permanent deletion requires exact text `discard`.

## Final Gate

The final gate requires:

- empty `git status --short`;
- empty index;
- all retained content in controlled local commits;
- all removed/restored content backed by explicit decisions;
- ref, diff-check, focused-test, no-real-data, and generated-output checks.

Any remote push remains a separate action requiring a fresh-ref check and
explicit User approval.

## Scope Verification

This Planner pass may modify only:

```text
tasks/RELEASE_006_POST_PUSH_WORKTREE_RESIDUAL_COMMIT_AND_CLEANUP_RECONCILIATION.md
docs/release_006_post_push_worktree_residual_commit_and_cleanup_reconciliation_plan.md
docs/lane_evidence/RELEASE_006_post-push-worktree-residual-commit-and-cleanup-reconciliation_planner.md
docs/task_board.md  # exact RELEASE_006 planned-only hunks only
```

It does not modify any pre-existing product/test/residual path. It does not
stage, commit, push, restore, delete, clean, stash, reset, or run Git object
maintenance.

## Next Legal Role

Reviewer Child A exact package-scope re-gate only.

Reviewer should verify:

- exact `52 = 37 + 15` baseline;
- exhaustive `44 + 3 + 4 + 1 mixed board` ownership model without
  double-counting;
- Child A retained-vs-discard separation;
- Child B hunk-level and tests-only stop points;
- Child C exact approval language;
- final clean and separate push gates;
- prohibition of a catch-all commit or destructive cleanup.
