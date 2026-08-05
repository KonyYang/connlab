# ConnLab Role Thread Registry — Frozen Legacy

> Status: frozen legacy audit reference since 2026-08-06. The listed tasks are not daily execution endpoints and must not be dispatched by the personal serial workflow.

Last Updated: 2026-07-30
Status: classic persistent-role registry
Scope: one permanent Orchestrator plus permanent specialist roles and Quick Fixer

| Role | Canonical title | Thread ID | Primary use |
|---|---|---|---|
| Orchestrator | ConnLab｜全自动编排 Orchestrator | `019fb3d4-12a5-73b3-be8e-e59686fa39a9` | 唯一日常主控，接收新目标并路由经典角色 |
| Planner | ConnLab｜总计划者 Planner | `019fb3ce-5133-77e3-b256-faa2111ee265` | Discovery、task/plan、范围与 gate |
| Developer | ConnLab｜开发执行者 Developer | `019fb3ce-5c37-79e1-8f33-dd3a0deb09de` | 已批准 lane 的实现与 checkpoint |
| Reviewer | ConnLab｜质量评审员 Reviewer | `019fb3ce-6824-7670-9015-326da4ce178f` | committed diff 与 plan/implementation gate |
| QA | ConnLab｜验证测试员 QA | `019fb3ce-7479-7472-a739-9cad8c11af8a` | clean reviewed commit 的验证 |
| Integrator | ConnLab｜集成负责人 Integrator | `019fb3ce-8c1b-73a0-a23d-cfd15a8a4b14` | merge gate、集成、residual 和 closeout |
| Quick Fixer | ConnLab｜快速修补员 Quick Fixer | `019fb3ce-80fa-7cb3-9400-1a4aa61f7a77` | 满足 AGENTS.md 19.1 的小修复快速通道 |

## Former V1-Lite Entry

`019faaf2-f172-7523-b70f-2c4952acd59f` 已撤销主控权，保留为
`ConnLab｜V1-Lite入口（停用）` 历史入口，不得路由新动作。

## Transition Snapshot

- `docs/project_management/ACTIVE_TASK_THREAD_BUNDLE.md` 仅保留切换时正在进行的 V1-Lite
  任务快照，不再创建新 bundle。
- `TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD` 的独立 worktree 和修改必须保留，
  等 Orchestrator 选择迁移到永久 Developer/Quick Fixer 或按原 gate 收口。
- Native identity 始终使用 exact thread ID；不得按标题猜测。

## Frozen Legacy

Controlled Lane V2 registry/heartbeat 与 V1-Lite 自动建包逻辑均冻结。V2 heartbeat 保持
`PAUSED`。

