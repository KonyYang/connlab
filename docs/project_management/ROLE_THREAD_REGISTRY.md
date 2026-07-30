# ConnLab Role Thread Registry

Last Updated: 2026-07-30
Status: classic persistent-role registry
Scope: one permanent Orchestrator plus permanent specialist roles and Quick Fixer

| Role | Canonical title | Thread ID | Primary use |
|---|---|---|---|
| Orchestrator | ConnLab｜全自动编排 Orchestrator | `019eb3b8-8624-74b2-a4a7-a6856399deac` | 唯一日常主控，接收新目标并路由经典角色 |
| Planner | ConnLab｜总计划者 Planner | `019eff12-a71a-7861-b3d2-908b204bdf73` | Discovery、task/plan、范围与 gate |
| Developer | ConnLab｜开发执行者 Developer | `019eff12-f314-79f3-ae0b-73795dc9b2c1` | 已批准 lane 的实现与 checkpoint |
| Reviewer | ConnLab｜质量评审员 Reviewer | `019eff13-27d3-75a2-b654-d8ac28937614` | committed diff 与 plan/implementation gate |
| QA | ConnLab｜验证测试员 QA | `019eff13-7311-7ba1-9594-c0f7dc6a3d75` | clean reviewed commit 的验证 |
| Integrator | ConnLab｜集成负责人 Integrator | `019eff13-bcb5-74c3-bb20-3c704038f4b3` | merge gate、集成、residual 和 closeout |
| Quick Fixer | ConnLab｜快速修补员 Quick Fixer | `019f0bc9-c88d-7262-a8ed-47e5472a3bdc` | 满足 AGENTS.md 19.1 的小修复快速通道 |

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

