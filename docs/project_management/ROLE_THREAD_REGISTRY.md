# ConnLab Role Thread Registry

Last Updated: 2026-07-30
Status: V1-Lite stable-entry registry
Scope: the single persistent ConnLab task entry; product-task roles are temporary

| Role | Canonical title | Thread ID | Primary use |
|---|---|---|---|
| Stable Entry | ConnLab｜研发任务编排与集成主控 | `019faaf2-f172-7523-b70f-2c4952acd59f` | 接收 `执行 TASK_XXX`，创建任务专属角色包，报告 closeout |

## Active Bundle

- Current bundle: `docs/project_management/ACTIVE_TASK_THREAD_BUNDLE.md`.
- Permanent Planner/Developer/Reviewer/QA/Integrator thread IDs are no longer active authority.
- Every product TASK receives new temporary role threads and archives them after Integrator closeout.
- Native task IDs must come from exact create/read-back results; title search cannot establish identity.

## Frozen Legacy Inventory

The former Orchestrator, permanent roles, V2-Lite temporary roles, TASK_367A Developer task, and
Quick Fixer are preserved in:

`docs/archive/thread_bundles/CONNLAB_LEGACY_ROLE_THREADS_2026-07-30.md`

Controlled Lane V2 registry and heartbeat remain read-only/frozen. The stable entry does not run
V2 heartbeat or CAS routing for normal ConnLab tasks.

