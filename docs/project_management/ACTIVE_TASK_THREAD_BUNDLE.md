# ConnLab Active Task Thread Bundle

Status: active routing manifest
Schema Version: 1

This file is a routing index, not approval authority. `AGENTS.md`, `docs/task_board.md`, the formal
task/plan/evidence, and Git remain authoritative.

```yaml
schema_version: 1
state: empty
active_task_id: null
```

When a product TASK is active, the stable entry records its task-scoped Controller, Planner,
Developer, Reviewer, QA, and Integrator IDs here. Integrator resets the manifest to the exact empty
state only after evidence, commits, worktree, residuals, remote state, and recoverable archival are
all closed.
