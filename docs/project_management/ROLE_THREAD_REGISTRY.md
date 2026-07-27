# ConnLab Role Thread Registry

Last Updated: 2026-06-27
Status: active local registry
Scope: role-specific Codex threads used by ConnLab orchestration

| Role | 中文线程名称 | Thread ID | Primary use |
|---|---|---|---|
| Orchestrator | ConnLab｜全自动编排 Orchestrator | `019eb3b8-8624-74b2-a4a7-a6856399deac` | 自动扫描、合法路由、接收角色 completion callback |
| Planner | ConnLab｜总计划者 Planner | `019eff12-a71a-7861-b3d2-908b204bdf73` | 任务拆分、lane 审批准备、board 规划 |
| Developer | ConnLab｜开发执行者 Developer | `019eff12-f314-79f3-ae0b-73795dc9b2c1` | 执行一个 approved lane，写 developer evidence |
| Reviewer | ConnLab｜质量评审员 Reviewer | `019eff13-27d3-75a2-b654-d8ac28937614` | 独立评审 diff/evidence，输出 blocking/non-blocking |
| QA | ConnLab｜验证测试员 QA | `019eff13-7311-7ba1-9594-c0f7dc6a3d75` | 执行 smoke/integration/manual 验证，写 QA evidence |
| Integrator | ConnLab｜集成负责人 Integrator | `019eff13-bcb5-74c3-bb20-3c704038f4b3` | 检查 merge gate、合并、更新全局 board |

## Notes

- These thread IDs are local Codex thread identifiers, not repository data.
- If a thread is archived, renamed, or replaced, update this registry before orchestrating.
- The orchestrator should prefer these threads when `send_message_to_thread` is available.
- Role threads should send completion callbacks to `ConnLab｜全自动编排 Orchestrator` when full-auto orchestration is active.

## Controlled V2 Controller

- Canonical title: `ConnLab｜研发任务编排与集成主控 v2`.
- Runtime status: not created; production bootstrap remains separately gated.
- Thread ID: unassigned. Do not infer or persist a placeholder ID.
- On authorized bootstrap, the native receipt and exact read-back must establish the binding before
  registry acknowledgement.
- All v1 role rows above and the retained TASK_367A topology remain authoritative and unchanged
  until a separately reviewed migration/retirement task.

