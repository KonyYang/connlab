# ConnLab Active Task Thread Bundle

Status: active routing manifest
Schema Version: 1

This file is a routing index, not approval authority. `AGENTS.md`, `docs/task_board.md`, the formal
task/plan/evidence, and Git remain authoritative.

```yaml
schema_version: 1
task_id: TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD
thread_label: 发布实例防串
lane_id: browser-release-frontend-freshness-instance-guard
state: worktree_ready_developer_pending
approval_state: user_approved
closeout_archive_authorized: false
entry_thread_id: 019faaf2-f172-7523-b70f-2c4952acd59f
controller_thread_id: 019fb32a-ff19-7170-b87f-f77f12bddff6
role_threads:
  planner: 019fb330-a311-7af3-8977-ad14fe48260b
  developer: null
  reviewer: 019fb343-5d7e-77f3-a861-c8e92c94013f
  qa: null
  integrator: null
base_commit: 46081784f9feb6a7dcdf294f819cf8afe8a47a63
branch: lane/browser-release-frontend-freshness-instance-guard
worktree: D:\PythonProject\connlab-worktrees\browser-release-frontend-freshness-instance-guard
reviewed_commit: null
accepted_commit: null
task_file: tasks/TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD.md
plan_file: docs/task_browser_release_frontend_freshness_and_instance_guard_plan.md
evidence_files:
  - docs/lane_evidence/TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD_planner.md
  - docs/lane_evidence/TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD_reviewer.md
  - docs/lane_evidence/TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD_reconciliation_planner.md
  - docs/lane_evidence/TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD_user_approval.md
  - docs/lane_evidence/TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD_controller.md
last_handoff:
  from_role: controller
  to_role: controller
  gate: worktree_created
  evidence_path: docs/lane_evidence/TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD_controller.md
residual_status: resolved_by_governance_reconciliation_9a5e94b4
archive_status: not_started
```

When a product TASK is active, the stable entry records its task-scoped Controller, Planner,
Developer, Reviewer, QA, and Integrator IDs here. Integrator resets the manifest to the exact empty
state only after evidence, commits, worktree, residuals, remote state, and recoverable archival are
all closed.
