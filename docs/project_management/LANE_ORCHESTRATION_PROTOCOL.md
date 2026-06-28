# ConnLab Lane Orchestration Protocol

Last Updated: 2026-06-27
Status: active governance protocol
Scope: automate role-to-role handoffs for approved ConnLab task lanes

## 1. Goal

This protocol reduces manual prompting between role threads. It does not loosen ConnLab's gates. The orchestrator may route work, but Planner, Developer, Reviewer, QA, and Integrator responsibilities remain separate.

## 2. Automation Boundary

The orchestrator may:

- read `docs/task_board.md`, task files, plans, evidence, and diffs
- decide the next valid role from board/evidence state
- send a standard prompt to the matching role thread
- ask the role to update its evidence and stop at its gate
- report the current handoff chain and blockers

The orchestrator must not:

- implement product code while acting as orchestrator
- approve a proposed/planned lane by itself
- bypass Reviewer or QA findings
- merge code unless explicitly acting as Integrator in the Integrator thread
- treat chat history as more authoritative than board/evidence files

## 3. State Machine

| Current state | Required evidence | Next role |
|---|---|---|
| `proposed` | Planner draft only | Stop; ask Planner/user for approval |
| `planned` | task/plan exists, not approved | Stop; ask Planner/user for approval |
| `approved` | lane has task, branch/worktree, gates | Developer |
| `in_progress` | Developer still working | Stop or ask Developer for status |
| `in_progress` + `ready_for_review` | Developer evidence and validation result | Reviewer |
| `review` + blocking findings | Reviewer evidence | Developer fix pass |
| `review` + pass | Reviewer evidence | QA or Integrator, depending on merge gate |
| `qa` + fail | QA evidence | Developer fix pass or Planner, based on failure |
| `qa` + pass | QA evidence | Integrator |
| `integration` | review/QA gates passed | Integrator |
| `complete` | board and evidence updated | Stop |

## 4. Orchestrator Command Examples

Use these commands in the Orchestrator/Planner conversation:

```text
自动推进 TASK_337A。只按 board/evidence 判断下一角色，不扩大范围。
```

```text
继续编排 lane lifecycle-backend-api。如果 Developer 已 ready_for_review，就发给 Reviewer。
```

```text
检查 TASK_337B 的 Reviewer 结论。如果通过，生成 Integrator 合并命令并发送到集成负责人线程。
```

## 5. Role Thread Commands

The orchestrator sends role-specific prompts from `.agents/skills/connlab-lane-orchestrator/SKILL.md`. If thread tools are unavailable, it prints the exact prompt for manual paste.

## 6. Evidence Requirements

Every automated handoff must name one evidence file under `docs/lane_evidence/`. A role thread must update evidence before it returns control to the orchestrator.

Minimum evidence fields:

- task/lane/role
- status
- allowed scope checked
- changed files or inspected files
- commands run and results
- findings/failures
- next role recommendation
- stop point

## 7. Failure Handling

If state is unclear, stop and report the smallest blocking fact. Do not guess. Common blockers:

- branch differs from board
- evidence missing or stale
- uncommitted changes mix multiple lanes
- Reviewer blocking findings are unresolved
- QA failed but no Developer fix pass exists
- merge target is not declared
## 8. Full-Auto Mode

Full-auto mode is implemented by a Codex heartbeat attached to an Orchestrator/Planner conversation. The heartbeat periodically runs the lane orchestrator skill and performs at most one routing action per wake-up.

Default cadence: every 10 minutes while active.

Full-auto may continue without user input across normal gates:

```text
Developer ready_for_review -> Reviewer
Reviewer blocking finding -> Developer fix pass
Reviewer pass -> QA or Integrator readiness check
QA pass -> Integrator readiness check
```

Full-auto stops and reports when human judgment is required:

- task/lane is not approved or not found
- board/evidence/thread status conflicts
- same blocking finding returns after one fix pass
- QA failure is not clearly an implementation defect
- merge into `master`/main or remote push would be required and was not explicitly pre-authorized
- destructive git or filesystem action would be required

The stop report must include current lane/task, evidence read, blocking reason, recommended next role, and the exact command the user can approve.

## 8.1 Event-Driven Completion Callback

Full-auto orchestration can run in event-driven mode in addition to the heartbeat. The heartbeat remains a safety net; normal handoff should be triggered by a role thread callback when that role reaches its stop gate.

Role completion contract:

- Developer sends a callback after evidence becomes `ready_for_review` or after a fix-pass checkpoint is written.
- Reviewer sends a callback after `pass` or blocking findings are written.
- QA sends a callback after `pass`, `fail`, or an unclear validation blocker is written.
- Integrator sends a callback after `accepted`, `blocked`, or a packaging checkpoint is written.
- Planner sends a callback after a formal lane is created/activated, or after Discovery Gate blocks.

Callback target:

- Prefer `ConnLab｜全自动编排 Orchestrator` in `ROLE_THREAD_REGISTRY.md`.
- If a delegated prompt contains `source_thread_id`, that source thread is also a valid callback target.
- If thread tools are unavailable, the role prints the callback message for manual paste.

Callback payload must include:

- source role
- completion status
- task ID and lane ID
- evidence/checkpoint path
- validation or review summary
- next-role recommendation
- blocker summary, or `none`

On receiving a callback, the Orchestrator must re-read board/evidence/thread state and perform at most one legal route action. A callback is a wake-up signal, not evidence authority.

Duplicate prevention:

- A role sends only one callback per changed evidence status.
- The Orchestrator ignores callbacks whose evidence status has already been routed.
- If callback state conflicts with board/evidence, pause and report the smallest conflict.
## 9. Lifecycle Series Automation

When the user authorizes full-auto completion of the lifecycle/workbench series, the heartbeat should advance the series defined by TASK_336 instead of watching only one task.

Series order:

| Step | Task | Automation behavior |
|---|---|---|
| 1 | `TASK_339A_PROJECT_LIFECYCLE_FRONTEND_READONLY_MODEL` | Continue active Developer lane, then Reviewer/QA/Integrator gates. |
| 2 | `TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS` | If missing after TASK_339A acceptance, ask Planner to create/activate the formal lane before any implementation. |
| 3 | `TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN` | Treat as planning output only. If already complete, use it as input for TASK_341. |
| 4 | `TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION` | Create/activate via Planner after TASK_339A and TASK_340 are accepted; then route Developer/Reviewer/QA/Integrator. |
| 5 | `TASK_342_LIFECYCLE_INTEGRATION_QA_AND_BOARD_CLOSEOUT` | Run final QA/board closeout after prior lanes are accepted. |

The orchestrator may auto-create the next Planner handoff prompt, but it must not invent missing task content silently. Planner owns formal lane creation.

## 10. Human Intervention

Human intervention is expected and safe. The operator can intervene from the Orchestrator conversation or from a role thread.

Preferred controls from the Orchestrator conversation:

```text
暂停全自动编排。不要再向任何角色线程发送命令，先报告当前 TASK/lane/thread 状态。
```

```text
恢复全自动编排。从 docs/task_board.md 和 evidence 重新判断，不使用旧聊天记忆。
```

```text
改为人工确认模式。以后每个 gate 只输出下一步命令，不自动发送。
```

```text
回退到 Planner。请让 Planner 重新核对 TASK_339-TASK_342 的顺序、范围和 board 状态。
```

Preferred control from an active role thread:

```text
停止当前任务，写 checkpoint evidence：已完成内容、未完成内容、当前阻塞、已改文件、已跑验证、下一步建议。不要继续改文件。
```

Dead-loop detection:

- same target role receives the same prompt twice without evidence change
- same blocking finding returns after one fix pass
- board status and evidence status disagree for two heartbeat runs
- a role thread remains active beyond a reasonable task slice without checkpoint evidence

On dead-loop detection, pause routing and report to the user.

