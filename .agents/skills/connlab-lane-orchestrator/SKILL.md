---
name: connlab-lane-orchestrator
description: Orchestrate ConnLab task lanes across role-specific Codex threads. Use when the user asks to 执行/启动/实施 TASK, 自动推进, 自动接力, 编排, orchestrate, hand off, route Planner/Developer/Reviewer/QA/Integrator work, advance a TASK lane, or reduce manual role-to-role prompting in ConnLab.
---

# ConnLab Lane Orchestrator

## Purpose

Use this skill to route ConnLab work through the permanent classic roles recorded in
`ROLE_THREAD_REGISTRY.md`. The permanent Orchestrator reads repository evidence, decides the next
valid role, and routes Planner/Developer/Reviewer/QA/Integrator or the bounded Quick Fixer fast
path. Do not create a V1-Lite task-scoped role bundle for ordinary work.

Canonical persistent titles:

```text
ConnLab｜全自动编排 Orchestrator
ConnLab｜总计划者 Planner
ConnLab｜开发执行者 Developer
ConnLab｜质量评审员 Reviewer
ConnLab｜验证测试员 QA
ConnLab｜集成负责人 Integrator
ConnLab｜快速修补员 Quick Fixer
```

Exact native thread IDs remain authoritative. Titles are display-only and must not be used to
discover or infer identity.

## Default Execute-Task Trigger

Treat an explicit user command such as `执行 TASK_XXX`, `启动 TASK_XXX`, or `实施 TASK_XXX` as a request to:

1. scan authoritative task/lane/worktree/thread state
2. prepare or resume the isolated lane environment
3. continue the approved role chain through local Integrator acceptance

The user does not need to repeat "create a worktree/branch" or "continue to Integrator".

This trigger does not invent missing approval. If the task is not planned/approved for the requested implementation, route the smallest required Planner/User gate first and then resume automatically after authorization.

## Required Context

Before sending any role prompt, read:

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md` when routing to Planner or creating/activating a future lane
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- the task file declared by the lane
- the lane evidence file declared by the board

If any file is missing or contradicts the board, stop and report the mismatch.

## Core Safety Rules

- Orchestrate only lanes whose board status is `approved`, `in_progress`, `review`, `qa`, `integration`, or `blocked_waiting_fix`.
- Never start implementation from `proposed` or `planned`.
- Default implementation WIP is one. A second ordinary task queues even when paths/worktrees are
  disjoint; only an exact board-recorded, User-approved max-two parallel exception can bypass it.
- Run `scripts/connlab_execution_gate.ps1` immediately before Create, implementation dispatch,
  Quick Fix preemption, reconciliation, and resume. `BLOCKED_*` stops; `QUEUE_REQUIRED` performs
  queue governance only.
- Never ask Planner to approve a missing or ambiguous future lane without a Discovery Gate and Definition of Ready.
- Never expand lane scope, `May Touch`, `Must Not Touch`, or `Locked Paths`.
- Never route Developer implementation until the concrete `lane/*` branch and sibling worktree exist and are clean.
- Never allow two active lanes to own the same shared file or authority path.
- Never treat a separate role thread as Git isolation.
- Never add new coverage to an oversized mixed test when a bounded public-contract test module can carry it.
- Never merge a lane with unresolved blocking Reviewer/QA findings.
- Never use chat memory as the source of truth when evidence files or board state disagree.
- Use only the permanent role IDs recorded in `ROLE_THREAD_REGISTRY.md`.
- Never create a task-scoped Controller or role bundle for ordinary work.
- Use Quick Fixer only when every criterion in `AGENTS.md` section 19.1 is satisfied.
- When every 19.1 predicate is proven and no escalation trigger exists, must use the compact Quick
  Fix capsule and must not route an independent Planner, create a full plan, repeat User approval,
  or add default QA. Use QF-1/QF-2/QF-3 routing exactly; QF-4 returns Planner/User.
- Orchestrator must use the compact Quick Fix capsule whenever those predicates are proven.
- Create or rename native tasks only inside explicit User task/Goal authority.
- If the current thread has access to `send_message_to_thread`, use it for handoffs. If not, produce the exact prompt the user should paste into the target role thread.

## Orchestration Loop

1. Identify the lane from the user's request or from `docs/task_board.md`.
2. Re-read board JSON/task/capsule/plan/evidence, permanent-role status, and `git worktree list`; do not infer active execution from chat presence alone.
3. If the same task already has a worktree, verify its branch/base/owner and resume it. Never create a duplicate lane worktree.
4. Run `StartTask`. If it returns `QUEUE_REQUIRED`, record/report the durable queue and do not
   create a worktree or dispatch implementation. If a parallel exception exists, independently
   verify its exact approval/proof/end condition and max-two bound.
5. Verify lane readiness: formal task file, approved status, concrete branch/worktree plan, evidence path, validation gate, merge gate, and exclusive shared-path ownership.
6. If implementation owns the token but the worktree does not yet exist, require
   `ALLOW_WORKTREE_CREATE`, verify primary clean, and create it with
   `scripts/connlab_lane_worktree.ps1 -TaskId <TASK_ID>`. Record branch, path, and base commit.
7. Determine next role:
   - `approved` -> Developer
   - `in_progress` with developer evidence `ready_for_review` -> Reviewer
   - Reviewer evidence has blocking findings -> Developer fix pass
   - Reviewer evidence `pass` and QA required -> QA
   - Reviewer/QA gates passed -> Integrator
   - Integrator reports conflicts or failed validation -> Developer or Planner, based on evidence
8. Resolve the next permanent role by exact ID from `ROLE_THREAD_REGISTRY.md`; do not create or
   rename a replacement role silently.
9. Before a write-capable role prompt, require a fresh `ALLOW_DISPATCH`,
   `ALLOW_PREEMPT_CHECKPOINTED`, `ALLOW_RECONCILE`, or `ALLOW_RESUME` result as applicable. Send
   one standard prompt to the permanent role with the exact worktree and reviewed commit.
10. Ask the target role to update its evidence file and stop at its declared gate.
11. After the target thread completes, re-read board/evidence and inspect the lane worktree before sending the next prompt.
12. Continue normal approved gates automatically until local Integrator acceptance.
13. After Integrator acceptance, require an exact residual ledger and retire only a clean, integrated worktree.
14. Do not archive permanent roles at task closeout. Close task evidence/worktree/residual state
    and leave the classic role conversations available for the next task.

Run at most one full Developer->Reviewer->Developer-fix cycle without asking the user for confirmation. Continue beyond that only when the user explicitly requests automatic continuation.


## Goal And Callback Mode

Use Goal mode when the User explicitly requests persistent execution. Goal mode is callback-driven,
not heartbeat-driven. Each role writes durable evidence, sends one compact callback, and stops.
The permanent Orchestrator rereads board/evidence/Git/native status before routing the next gate.

Goal mode may automatically route permanent roles, create/retire clean worktrees, continue bounded
fixes, create local checkpoints, and integrate locally when authorized. It does not archive the
permanent role conversations.

Goal mode stops for missing approval, scope change, cross-lane ownership conflict, unexplained
test failure, destructive discard, or unapproved remote push. Controlled Lane V2 heartbeat remains
`PAUSED` and is never used for ordinary tasks.


## Worktree And Residual Contract

- Branch format: `lane/<lane-id>`.
- Default worktree location: sibling `<repo-name>-worktrees/<lane-id>`.
- Primary `master` worktree: planning and integration only.
- Developer handoff: clean local checkpoint commit and empty index.
- Reviewer input: recorded base commit to lane HEAD.
- QA input: reviewed clean commit or exact archive.
- Integrator closeout: accepted package, board update, residual ledger, clean lane worktree.
- Residual classes: `retain`, `duplicate`, `stale`, `format-only`, `conflict`.
- `retain` requires a named owner; `duplicate`/`stale`/`format-only` require one exact discard list; `conflict` returns to Planner/User.
- Never force-remove a worktree, run `git add -A`, or push remote as part of automatic lane closeout.

Each callback scan performs one legal handoff decision. Board execution state and role evidence are
the durable duplicate-suppression record.


## Event-Driven Completion Callback

Use compact completion callbacks. A permanent role that reaches its declared stop gate notifies
the permanent Orchestrator immediately, then stops.

Callback rules:

- Send callbacks to the permanent Orchestrator ID from `ROLE_THREAD_REGISTRY.md`.
- Send a callback only after evidence/checkpoint state changed; do not send duplicate callbacks for the same evidence status.
- The callback never authorizes the next gate by itself. Orchestrator must still re-read
  board/evidence/Git/native state.
- If `send_message_to_thread` is unavailable, print the exact callback for the User to paste into
  permanent Orchestrator.
- Do not callback while still actively editing, testing, reviewing, or integrating.

Callback message shape:

```text
TASK_ID: <TASK_ID>
ROLE: <ROLE>
STATUS: <ready_for_review | reviewer_pass | reviewer_blocked | qa_pass | qa_fail | integrator_accepted | integrator_blocked>
EVIDENCE: <EVIDENCE_PATH>
COMMIT: <FULL_SHA_OR_NULL>
NEXT: <Planner | Developer | Reviewer | QA | Integrator | User | Archive>
BLOCKER: <none 或最小阻塞事实>
```
## Lifecycle Series Mode

Use lifecycle series mode when the user asks to complete the ConnLab lifecycle/workbench series around `TASK_339` through `TASK_342`.

Series source of truth:

- `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`
- `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`
- `docs/task_board.md`

Expected sequence:

1. `TASK_339A_PROJECT_LIFECYCLE_FRONTEND_READONLY_MODEL`
2. `TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS`
3. `TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN` (planning output only; already may be complete)
4. `TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION`
5. `TASK_342_LIFECYCLE_INTEGRATION_QA_AND_BOARD_CLOSEOUT`

Full-auto may ask Planner to create/activate the next missing formal lane after the previous lane has Integrator acceptance. If a task file/plan/evidence does not exist yet, the next action is Planner Discovery Gate and lane preparation, not Developer implementation.

Never skip directly from an accepted lane to an implementation for a missing future task. Each missing future task still needs Discovery Gate, Definition of Ready, formal task file, evidence file, lane row, May Touch/Must Not Touch/Locked Paths, validation gate, and merge gate.

### Planner Discovery Prompt

```text
你是 ConnLab｜总计划者 Planner。
请对下一步需求执行 Planner Discovery Gate，不要直接创建 approved lane。
必须读取 AGENTS.md、docs/task_board.md、docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md、docs/project_management/PARALLEL_EXECUTION_MODEL.md，以及与该需求相关的 task/plan/evidence/code 文档。
输出：当前 phase/lane/role、用户目标复述、已确认事实、仓库证据、Planner 推断、未确认信息、最多 3 个阻塞澄清问题、是否满足 Definition of Ready、建议保持 proposed/planned/approved 的理由。
禁止写产品代码，禁止把推断当作用户批准，禁止跳过 Developer/Reviewer/QA/Integrator gate。
```

## Human Intervention Controls

Honor these commands immediately:

- `暂停全自动编排` / `pause auto orchestration`: pause the heartbeat automation or stop sending new role prompts.
- `恢复全自动编排` / `resume auto orchestration`: resume from board/evidence state, not chat memory.
- `停止当前角色任务`: send a stop/checkpoint request to the currently active role thread and wait for evidence.
- `改为人工确认`: stop after every gate and print the next prompt instead of sending it.
- `回退到 Planner`: stop routing and ask Planner to reconcile board/evidence/scope.
- `重新读取事实`: re-read board, task files, evidence, and recent target thread summaries before taking any next action.

If the user corrects direction, treat the newest user instruction as controlling, then update the next heartbeat prompt or pause the automation before further routing.
## Standard Role Prompts

### Developer Start

```text
你是 ConnLab｜开发执行者 Developer。
请执行 lane: <LANE_ID> / task: <TASK_ID>。
工作目录必须是 board 记录的 lane worktree: <WORKTREE_PATH>；分支必须是 <BRANCH>。
必须先读取 AGENTS.md、docs/task_board.md、任务文件、方案文件、并行模型和 evidence 文件。
只允许修改该 lane 的 May Touch 范围，禁止触碰 Must Not Touch / Locked Paths。
完成实现和验证后，使用 exact-path staging 创建本地 lane checkpoint commit，确认 worktree/index clean，更新 developer evidence（base commit、lane HEAD、changed paths、validation），状态写为 ready_for_review，并停止等待 Reviewer。
不要合并，不要替 Reviewer/Integrator 更新全局完成状态。
```

### Reviewer Gate

```text
你是 ConnLab｜质量评审员 Reviewer。
请评审 lane: <LANE_ID> / task: <TASK_ID>。
读取 AGENTS.md、docs/task_board.md、任务文件、developer evidence，并只评审 <BASE_COMMIT>..<LANE_HEAD> 的 committed diff。
按 docs/project_management/TASK_REVIEW_CHECKLIST.md 给出 blocking / non-blocking 结论，写入 reviewer evidence。
不要直接修代码，不要合并。若有 blocking findings，请给 Developer 可执行修复清单并停止。
```

### Developer Fix Pass

```text
你是 ConnLab｜开发执行者 Developer。
请只处理 Reviewer 对 lane: <LANE_ID> / task: <TASK_ID> 提出的 blocking findings。
禁止扩展需求或触碰 lane 范围外文件。
修复后运行相关验证，更新 developer evidence 的 fix-pass 记录，并停止等待 Reviewer 复审。
```

### QA Gate

```text
你是 ConnLab｜验证测试员 QA。
请对 lane: <LANE_ID> / task: <TASK_ID> 执行声明的 smoke / integration 验证。
必须使用 reviewed lane commit 的 clean worktree、临时 worktree 或 exact archive；不得读取 primary worktree ambient dirty files。
记录环境、命令、输入、输出、失败或通过结论到 QA evidence。
不要修改产品代码，不要合并。
```

### Integrator Merge Gate

```text
你是 ConnLab｜集成负责人 Integrator。
请检查 lane: <LANE_ID> / task: <TASK_ID> 是否满足 merge gate。
必须确认 Reviewer/QA blocking findings 已关闭、分支/工作区清晰、允许合并范围明确。
如可合并，执行受控合并和集成验证，更新 docs/task_board.md 与 integration evidence，并把每个 excluded path 分类为 retain/duplicate/stale/format-only/conflict。
确认 lane worktree clean 且 lane HEAD 已集成后，使用 worktree script 无 force 退役；否则保留并报告 blocker。
如不可合并，写明阻塞原因和下一角色。
```


### Completion Callback Footer

Append this footer to every role prompt when automatic orchestration is active:

```text
完成本角色 gate 后，先更新 evidence/checkpoint，再向
`ROLE_THREAD_REGISTRY.md` 记录的 permanent Orchestrator 发送 compact callback：
TASK_ID、ROLE、STATUS、EVIDENCE、COMMIT、NEXT、BLOCKER。发送后停止。
如果不能发送，在最终答复中输出同样的 callback 供用户粘贴；不要代替下一角色执行。
```
## Output Format

When orchestrating, report:

- lane and task
- current board status
- next role
- target thread title/id if available
- prompt sent or prompt to paste
- evidence file expected from the target role
- stop condition

