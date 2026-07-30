# TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD User Approval

Date: 2026-07-30
Role: User approval gate
Status: `implementation_approved`
Task: `TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD`
Lane: `browser-release-frontend-freshness-instance-guard`
Planning base: `02517ba968f1a16d5ddda6ba038411ef4133226d`

## Approved Input

The User explicitly replied:

```text
批准 TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD 按已评审计划实施
```

The approved contract is the exact corrected plan in
`docs/task_browser_release_frontend_freshness_and_instance_guard_plan.md`, with
`docs/lane_evidence/TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD_reviewer.md`
recording `reviewer_plan_pass`.

## Authority Granted

- Persist the approved planning/governance package in a local exact-path commit.
- Create one isolated `lane/*` branch and sibling worktree after the primary cleanliness and
  shared-owner gates pass.
- Lazily create the task-specific Developer and implement only the approved May Touch scope.
- Continue normal local Reviewer, QA, bounded-fix, evidence, commit, integration, and clean
  worktree lifecycle gates within the approved task.
- During automated smoke only, close the exact disposable process created by that smoke after both
  recorded PID and release identity prove ownership.

## Authority Not Granted

- No remote push, fetch, destructive discard, historical release cleanup, or existing
  `dist_release/**` mutation.
- No production termination, reuse, replacement, takeover, or alternate-port behavior for any
  pre-existing occupant.
- No Controlled Lane V2 action and no product/frontend/Matrix/Fee/LTR/Office/schema/database scope
  expansion.
- No cleanup or packaging of unrelated ambient primary-worktree changes.

## Next Gate

Controller records approval, commits the exact planning package, then creates the isolated lane
only if primary cleanliness and shared ownership are satisfied. Developer remains unauthorized
until concrete base, branch, and worktree values are recorded.
