# TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD Controller Evidence

Date: 2026-07-30
Role: Controller
Status: `worktree_ready_developer_pending`
Task: `TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD`
Lane: `browser-release-frontend-freshness-instance-guard`
Planning commit: `6e0fa345797bab1328c9df5366a2921db3529735`

## Gate Reached

- Reviewer plan re-gate passed.
- User explicitly approved the corrected implementation plan.
- The exact eight-file planning/governance package was committed locally at the planning commit.
- The index is empty after that commit.
- No implementation branch, worktree, Developer, product code, release artifact, push, cleanup, or
  Controlled Lane V2 action was created or performed.

## Blocking Fact

The mandatory primary-cleanliness gate failed after the planning commit. These modified,
unstaged paths remain in the primary worktree:

```text
.agents/skills/connlab-lane-orchestrator/SKILL.md
AGENTS.md
docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md
docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md
tests/unit/test_task_scoped_role_thread_lifecycle_governance.py
```

They pre-date implementation approval, are outside this task's May Touch, and have no owner or
expiry recorded in this task's board row or bundle. Their current diff is 62 additions and 10
deletions. They are preserved exactly as found and remain unstaged.

## Safety Decision

The Controller did not:

- stage or commit the five ambient paths with this task;
- restore, discard, stash, move, or clean them;
- treat a separate role thread as Git isolation;
- create a lane from a dirty primary worktree;
- guess an owner or classify the changes as duplicate/stale/format-only.

Residual class is `conflict` until an authoritative owner or exact authorized disposition is
recorded. This is a repository-hygiene blocker, not a product-plan blocker.

## Resume Contract

After the five paths are committed by their real owner or otherwise resolved through an exact
authorized non-destructive action, Controller must re-read board/task/plan/evidence, verify an
empty primary status and index, rescan shared ownership and existing worktrees, then create the
single isolated lane. Developer remains `null` until branch, worktree, and base are recorded.

## Authorized Governance Reconciliation Resolution

The User explicitly classified the five ambient paths as the prior V1-Lite task-scoped
`thread_label` / compact-title governance change and authorized an independent reconciliation.
The task-specific Controller owned that reconciliation without adding it to this product task's
implementation scope.

- Governance evidence:
  `docs/lane_evidence/V1_LITE_TASK_SCOPED_THREAD_LABEL_SHORT_TITLE_GOVERNANCE_RECONCILIATION_controller.md`
- Governance commit: `9a5e94b441440471ab3880ba4d8013d87883f647`
- Focused validation:
  `py -m pytest tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q`
  -> `3 passed in 0.05s`
- Safety: exact-path staging only; no product file, push, stash, deletion, cleanup, or V2 action
- Primary proof after commit: `git status --short` empty and cached index empty

The former `conflict_unowned_primary_paths` residual is therefore resolved by a separately owned
and committed governance package. No active worktree claims the approved browser release paths,
and no worktree or branch for this lane already exists. The next legal action is creation of the
single isolated implementation worktree; Developer remains `null` until its concrete base,
branch, and path are persisted.

## Implementation Worktree Checkpoint

The project worktree helper created the only implementation lane after a clean-primary dry-run:

- Base commit: `46081784f9feb6a7dcdf294f819cf8afe8a47a63`
- Branch: `lane/browser-release-frontend-freshness-instance-guard`
- Worktree:
  `D:\PythonProject\connlab-worktrees\browser-release-frontend-freshness-instance-guard`
- Helper result: `CTL_OK`
- Lane HEAD equals base commit and lane status is empty.
- Primary status remains empty after worktree creation.
- No other worktree claims the approved product paths; the four historical V2 worktrees remain
  frozen read-only and are not routed.

The concrete Git isolation gate is now satisfied. The next legal action is lazy creation of the
task-specific Developer, persistence/read-back of its exact native thread ID, then one bounded
implementation handoff.
