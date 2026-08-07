# AGENTS.md — ConnLab AI Coding Rules

## 1. Product Mission

ConnLab is an offline Windows-first workbench for an electronic connector laboratory. It started with project intake, application-form precheck, LTR tracking, and project folder creation, and now has a controlled Project Workbench / Matrix / Approval Package foundation.

The next product direction is the Matrix-driven Laboratory Execution Phase:

```text
Matrix is the execution authority map, Project remains the lifecycle container.
```

Project owns lifecycle identity and traceability. Matrix owns the authoritative test execution map. Step-level records will own execution data, evidence, images, lifecycle state, and report bindings when future tasks explicitly implement them. Test Record, Report, Fee Evaluation, and Approval Package are derived outputs.

ConnLab is a new project. Do not copy old TestFlowManager architecture. Old code and documents are reference material only.

## 2. Current Stage And Scope

The original MVP baseline is implemented and extended:

1. Application form intake and precheck.
2. LTR number registration / tracking.
3. Project folder creation from a template.

Current frozen baseline:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

Next direction:

```text
Matrix-driven Laboratory Execution Phase
```

Do not implement StepInstance, test execution persistence, image asset management, report generation, AI review, multi-user collaboration, permissions, or LAN deployment unless a current approved task explicitly requests it. Matrix and Step work must remain task-controlled and must not turn into an Excel-like string editor.

## 3. Mandatory Technical Stack

- Backend: Python 3.11+.
- API: FastAPI.
- Data storage: SQLite.
- ORM: SQLAlchemy 2.x is preferred.
- Validation schemas: Pydantic v2.
- Frontend: React + TypeScript. Keep UI minimal during early backend tasks.
- Desktop shell: PyWebView later, not in the first repository scaffold unless requested.
- Office handling: Windows + Microsoft Office only. Use python-docx/openpyxl for offline parsing where possible, pywin32 only behind gateway/facade classes.

## 4. Architecture Layers

Use this backend structure:

```text
backend/
  domain/              # pure domain dataclasses/enums/value objects
  application/         # use case services and orchestration
  infrastructure/      # SQLite, files, Office gateways, config, logging
  modules/             # intake, precheck, ltr, folder implementations
  api/                 # FastAPI routes, request/response DTOs
  shared/              # common errors, result types, utilities
```

Layering rules:

- `domain` must not import `api`, `infrastructure`, `modules`, or Office libraries.
- `application` may import `domain` and abstract ports; avoid direct Office/SQLite code.
- `infrastructure` implements persistence, file, Office, and template adapters.
- `api` calls application services only.
- UI/frontend never directly manipulates Office files or project folders.

### 4.1 Project-Wide Frontend/UI Design Rule

`$impeccable` is a ConnLab project-wide rule for frontend and UI work. It is not limited to Phase 5 or Phase 6.

Use `$impeccable` before any task that designs, changes, critiques, audits, polishes, refactors, or documents:

- frontend pages, routes, components, forms, navigation, panels, tables, dashboards, empty states, error states, loading states, or disabled states
- UX copy, operator guidance, business-readable status text, action labels, confirmation flows, or frontend smoke expectations
- layout, spacing, typography, color, visual hierarchy, responsive behavior, icons, interaction states, or motion

Requirements:

- Load `$impeccable` context before UI design or edits and follow `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json`.
- Read `docs/02_ARCHITECTURE_RULES.md` and `docs/frontend_architecture_rules.md` before any frontend/UI implementation, refactor, UX-copy, layout, component, route, state, API-client, or styling task.
- Treat ConnLab as `$impeccable` `register: product`.
- Backend-only, parser-only, storage-only, Office gateway-only, database-only, and non-UI test tasks are exempt unless they change UI behavior or user-facing copy.
- If `$impeccable` guidance conflicts with the active task scope, obey `AGENTS.md` and `docs/task_board.md` scope control first, then report the conflict.

Frontend architecture control:

- `docs/02_ARCHITECTURE_RULES.md` defines the project-wide dependency and UI architecture reference.
- `docs/frontend_architecture_rules.md` defines page, feature, component, API, state, selector, config, styling, copy/mock, and review boundaries for React frontend work.
- Future frontend changes must follow those documents unless an active task explicitly updates the rules.
- Do not grow route pages by adding ad hoc fields, `useState`, workflow decisions, or large JSX blocks when the change belongs in feature config, selectors, feature hooks, or named business components.

## 5. Core Domain Principles

- Project is the lifecycle container and traceability center.
- Matrix is the execution authority map for what must be tested.
- Step is the future execution data and lifecycle unit.
- Application form is the project starting point.
- Precheck is the first quality gate.
- LTR and project folder creation are downstream of a confirmed project.
- Word and Excel are input/output formats, not the primary system data model.
- All extracted or confirmed data must be stored as structured records.
- Every future feature must attach to a Project lifecycle stage.
- Test Record, Report, Fee Evaluation, and Approval Package are derived outputs, not primary data sources.

### 5.1 Legacy Authority Compatibility Mode

ConnLab currently uses a legacy-authority compatibility mode:

```text
Public-drive LTR Excel files and existing Word/Excel templates remain the current business authority or delivery templates.
Local SQLite is only a personal workstation cache, automation aid, synchronization backup, and future migration backup.
After ConnLab upgrades to a server deployment, authority may migrate to the server database, and Word/Excel files should become derived outputs for user reading, review, approval, and delivery.
```

Current-stage rules:

- Do not silently replace public-drive authoritative Excel workflows with local SQLite-only workflows.
- LTR registration, project-number lookup, and required legacy workbook writeback must continue to support the current public-drive `.xlsx` authority path when the active task touches those workflows.
- User-editable external reference and template file paths should be exposed as plain file-path settings, not as database concepts.
- SQLite may store local snapshots, recent paths, operation records, parsed data, and migration-ready backups, but this must remain an implementation detail for operators.
- Programmers may maintain structured configuration, rule libraries, and backups through controlled config files or approved maintenance tasks.
- When future server deployment is explicitly approved, plan the authority cutover as a separate migration task rather than an incidental refactor.

## 6. Domain Objects

Historical MVP objects:

- Project
- ApplicationForm
- SampleInfo
- PrecheckResult
- PrecheckIssue
- LtrRecord
- ProjectFolderRecord
- FileAsset

Current controlled Matrix foundation:

- ProjectTestPlanDraft
- ProjectOutputRecord

Future execution objects, not implemented unless a task explicitly requests them:

- TestDefinition
- TestGroup
- StepInstance
- TestRecord
- TestResult
- TestAsset
- LabReport
- AuditReport
- KnowledgeDocument
- AIReviewResult

## 7. Forbidden Anti-Patterns

Do not:

- Put business logic inside UI click handlers or API route bodies.
- Let UI or API routes directly call Word/Excel COM.
- Create a generic “tools” page full of buttons.
- Treat Matrix as replacing Project as the lifecycle container.
- Treat Matrix cells as the long-term string-only authority.
- Treat Word/Excel files as the only source of truth.
- Create god services or god files.
- Implement future scope just because it appears in the blueprint.
- Mix parsing, validation, persistence, and UI in one class.
- Use broad `except Exception: pass` or hide errors.
- Add unrequested dependencies.

## 8. Size and Maintainability Constraints

- Python file target: under 300 lines; hard limit 500 lines.
- Service class target: under 250 lines; hard limit 400 lines.
- API route modules should remain thin.
- Each task should be small and reviewable.
- Add or update tests with each functional task.

## 9. Precheck Rules Scope for MVP

Application form precheck should support rules for:

- Form number and revision, e.g. Form No. E-3718 / Rev H.
- Requestor fields: requester, phone, date, email, business unit, manufacturing site, project number.
- Sample fields: product name, part number/revision, lot/traceability, material, plating, housing material, quantity.
- Requested testing description: empty, too vague, “see attachment” without registered attachment.
- Subcontract permission: Yes/No extracted as structured value.
- Lab section: lab, assigned personnel, received date, estimated completion date, sample condition.

Precheck is not AI. Use deterministic rules first.

## 10. Folder Generation Rules

- Folder creation must be previewable before execution.
- Template source and target path must be validated.
- Support placeholder replacement in folder names and file names:
  - `{DL_NUMBER}`
  - `{PROJECT_NO}`
  - `{PRODUCT_NAME}`
  - `{REQUESTOR}`
  - `{DATE}`
  - `{BUSINESS_UNIT}`
- Never overwrite an existing project folder unless the task explicitly implements a safe conflict strategy.

## 11. API Rules

- Routes must return typed Pydantic responses.
- Route bodies should call application services.
- Do not leak SQLAlchemy models directly as API responses.
- Return actionable error messages.

## 12. Testing Rules

Use pytest for backend tests. Each functional task should include tests for happy path and key error/warning cases.

Minimum test categories during MVP:

- Domain model tests.
- Repository tests with temporary SQLite database.
- Precheck rule tests.
- Folder preview/generation tests using temporary directories.
- API smoke tests.

## 13. How to Work on Tasks

For each task:

1. Read this AGENTS.md.
2. Read `docs/task_board.md`.
3. Read the specific task file in `tasks/`.
4. Create a concrete implementation plan document first (scope, design, file-level changes, risks, validation).
5. Submit the plan document for user review and wait for explicit approval.
6. After user approval, implement only the current active task allowed by `docs/task_board.md`.
7. Add/update tests.
8. Run relevant tests if possible.
9. Update `docs/task_board.md` after task completion before closing the turn.
10. Summarize changed files and any known limitations.

If a task conflicts with AGENTS.md, follow AGENTS.md and report the conflict.

## 14. Task Board Is The Current Source Of Truth

`docs/task_board.md` is the project execution board and the current source of truth for task progression.

Mandatory rules:

1. Read order for every new task:
   - `AGENTS.md`
   - `docs/task_board.md`
   - current `tasks/TASK_XXX_*.md`
   - any task-specific docs referenced by that task
2. Do not start a task that is not marked as current or explicitly ready in `docs/task_board.md`.
3. Do not skip forward to later tasks just because they look implementable.
4. When a task is completed, update `docs/task_board.md` in the same turn:
   - task status
   - last updated date
   - completion notes
   - next recommended task
   - validation summary
5. If implementation reality differs from the board, update the board instead of relying on conversational memory.

Execution priority:

- Stable rules and scope boundaries: `AGENTS.md`
- Current stage, active task, and completion state: `docs/task_board.md`
- Concrete implementation details: current `tasks/TASK_XXX_*.md`

## 15. Anti-Skip Protocol

To prevent AI from jumping stages, every execution turn must state:

- current phase
- current active task ID
- why this task is allowed now

If the requested task is ahead of the active task on the board, stop and report the mismatch instead of implementing it silently.

## 🔴 强制执行协议（Task Execution Protocol）

每个任务必须执行：

1. 阅读 TASK 文件
2. 使用 `docs/project_management/TASK_EXECUTION_SKILL.md`
3. 先产出“可执行方案文件”（必须可审阅，包含范围、改动点、风险、验证）
4. 将方案文件提交给用户审阅，未获得“同意/批准”前禁止写实现代码
5. 用户批准后再进入第二步：实施编码与测试
6. 执行 `docs/project_management/TASK_REVIEW_CHECKLIST.md`
7. 提供运行验证方法
8. 停止，不进入下一个任务

---

## 🚫 严格禁止

* 不允许实现未指定功能
* 不允许跨 Task 开发
* 不允许自动推进多个 Task
* 不允许重构未授权代码

---

## 🧠 开发模式

AI 角色：

* 执行者（不是架构师）
* 必须服从 Task
* 必须服从 AGENTS.md
---

## 16. ConnLab Lane Orchestration

当用户要求“自动推进”“自动接力”“编排 lane”“把 Planner/Developer/Reviewer/QA/Integrator 串起来”时，默认使用项目 skill：

- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`

自动编排只能转发和接力已批准 lane，不得绕过以下规则：

- proposed/planned 不能执行
- Developer 只能修改 lane 允许范围
- Reviewer/QA blocking finding 必须回到 Developer 修复
- Integrator 只能在 merge gate 满足后合并
- evidence 文件和 `docs/task_board.md` 优先于聊天记忆
- 任何可写 implementation dispatch、Quick Fix preemption、reconciliation 或 resume 前必须
  重新运行只读 `scripts/connlab_execution_gate.ps1`；`BLOCKED_*` 必须停止，
  `QUEUE_REQUIRED` 只能进入排队治理

如果当前环境没有线程发送工具，则输出可复制到目标中文角色对话框的完整命令。

## 17. ConnLab Planner Discovery

当用户要求“规划”“拆任务”“创建/激活 lane”“下一阶段怎么做”“把需求整理成任务”时，默认使用项目 Planner skill：

- `.agents/skills/connlab-planner/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`

Planner 不得把简短或模糊的用户请求直接转换成 approved task/lane。进入任务或 lane 规划前，必须先执行 Discovery Gate，至少区分：

- 用户已明确确认的目标
- 仓库文件已证明的事实
- Planner 自己的推断
- 仍未确认且会影响范围、依赖、验收或文件边界的信息

如果缺失信息会影响 `May Touch`、`Must Not Touch`、`Locked Paths`、验证口径、API/data ownership、UX 行为或串并行顺序，Planner 必须先提出最多 3 个阻塞澄清问题，或将 lane 保持为 `proposed/planned`，不得标记为 `approved`。

Planner 只有在 `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md` 的 Definition of Ready 满足后，才能在用户明确批准下创建或激活 approved lane。

## 18. Parallel Lane Worktree And Closeout

实现默认 `WIP=1`，并由 `docs/task_board.md` 内唯一 marker-delimited JSON execution block
记录 execution token。受控并行是显式 User-approved exception，不是路径无重叠时的默认行为。
所有实现仍必须使用真实 Git 隔离，不能把不同聊天线程当作隔离。完整规范见
`docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`。

强制规则：

1. 一个产品 lane 必须对应一个 `lane/*` branch 和一个独立 sibling worktree。
2. primary `master` worktree 仅用于 Planner/Integrator 的治理与集成，不得作为多个 lane 的共享草稿区。
3. Developer implementation 开始前，Orchestrator 必须自动创建并记录 worktree path、branch、base commit；用户不负责执行 Git worktree 命令。
4. 同一个 shared file、oversized mixed test 或 authority path 同时只能有一个 active owner；发生重叠时必须串行化。
5. 新测试默认写入 bounded 独立模块，不继续堆入超大 mixed test。
6. Developer 必须以 clean local lane checkpoint commit 交给 Reviewer；Reviewer 只评审 base..lane HEAD。
7. QA 必须基于 reviewed commit 的 clean worktree、临时 worktree 或 exact archive，不能使用 primary worktree 的 ambient dirty files。
8. Integrator 每次接受 package 后必须立即记录 residual ledger：`retain`、`duplicate`、`stale`、`format-only` 或 `conflict`。
9. `retain` 必须立即分配正式 owner/lane；`duplicate`、`stale`、`format-only` 进入一次 exact discard 清单；`conflict` 返回 Planner/User。
10. task、plan、evidence 必须跟随所属 planning/implementation package 提交，不得长期积压未跟踪治理文件。
11. lane complete 必须同时满足 worktree/index clean、治理文档已提交、remote 状态已说明，并且 primary worktree clean 或所有 residual 都有 owner 与 expiry。
12. 多 lane 系列应由一个用户授权 Goal 持续收口；Goal 范围内的普通角色接力、bounded fix、tests-only migration、evidence reconciliation、local commit 和 clean worktree lifecycle 不重复请求人工批准。
13. execution token 从首次实现写入前一直保留到 Integrator acceptance/cancelled closeout 或完整
    `paused_preempted` transition；Reviewer、QA、Integrator 不释放 token。
14. 普通第二任务进入 durable FIFO queue，不创建 implementation worktree，不 dispatch Developer。
15. 并行例外必须记录独立范围/锁/authority/test owner 证明、结束条件和 User 明确批准，最多两个 owner。

自动化入口：

- `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md`
- `docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`
- `scripts/connlab_execution_gate.ps1`
- `scripts/connlab_lane_worktree.ps1`
- `scripts/task_complete_commit.ps1`

默认任务启动语义：

- 当用户明确说“执行 TASK_XXX”“启动 TASK_XXX”或“实施 TASK_XXX”时，默认进入受控全自动编排；用户不需要重复说明 worktree/branch 或“持续到 Integrator”。
- Orchestrator 必须先重新读取 board/task/plan/evidence、角色线程状态和 `git worktree list`，不得仅凭聊天记忆判断是否已有任务在执行。
- 若同一 TASK 已有 worktree，必须复用并续跑，禁止创建重复 branch/worktree。
- 若其他 task 持有 execution token，普通任务必须排队；仅有 exact proof、board record 和 User 明确批准的 parallel exception 才可启动第二 owner，路径无重叠本身不授权并行。
- product/tests-only implementation 即使当前没有其他任务，也默认使用独立 lane worktree；primary worktree 继续只承担 planning/integration。
- 在用户已批准的 task/Goal 范围内，自动持续到本地 Integrator acceptance，并自动完成普通 Reviewer/QA/fix/reconciliation/local-commit/worktree-retire 接力。
- 只有缺少正式批准、范围/行为变化、shared ownership 冲突、无法解释的测试失败、destructive discard 或未授权 merge/push 才暂停找用户。

绝对禁止：

- `git add -A`
- force-remove dirty worktree
- 未授权 discard/reset/restore/delete
- 未授权 remote push
- 把 unnamed residual 留给未来人工猜测

## 19. Classic Persistent Roles And Quick Fixer

ConnLab 日常工作恢复为长期经典角色模式：

```text
用户 -> Orchestrator
复杂或范围不清 -> Planner -> User approval -> Developer -> Reviewer -> QA -> Integrator
明确的小修复 -> Quick Fixer -> targeted smoke -> Reviewer/Integrator as risk requires
```

唯一主控、永久角色及其原生 thread ID 记录在
`docs/project_management/ROLE_THREAD_REGISTRY.md`。日常任务复用这些长期角色，不再为每个
TASK 自动创建和归档一整套临时 Controller/Planner/Developer/Reviewer/QA/Integrator。

强制规则：

1. `ConnLab｜全自动编排 Orchestrator` 是唯一日常路由主控；其他入口不得并行发起角色动作。
2. `docs/task_board.md`、task、plan、evidence 和 Git 高于聊天记忆与任何路由清单。
3. 复杂功能、范围不清、跨层、数据/authority/API/schema/迁移或高风险任务继续执行完整
   Planner、User approval、Developer、Reviewer、QA、Integrator gate。
4. Reviewer/QA blocking finding 必须回到 Developer；Integrator 只能在 merge gate 满足后集成。
5. 实现任务仍使用独立 `lane/*` branch 和 sibling worktree；长期角色线程不是 Git 隔离。
6. 不自动 push，不 destructive cleanup，不丢弃未知修改，不强制删除 dirty worktree。

### 19.1 Quick Fixer Fast Path

同时满足以下条件时，Orchestrator 必须使用永久 Quick Fixer compact capsule fast path，
不得创建独立 Planner 对话、full plan、重复 User approval 或默认 QA：

- 问题可稳定复现，根因和期望行为清楚；
- 不新增产品需求，不改变业务 authority 或持久化语义；
- 不涉及数据库/schema/migration、公共盘权威写入、API breaking change 或破坏性操作；
- 修改范围小且边界明确，通常为 1-3 个实现文件及其 bounded tests；
- 有可执行的 targeted test 或手工 smoke；
- 与活动 lane 的 `Locked Paths`、shared files 和 authority ownership 不冲突。

compact capsule 必须包含 Goal、Why Safe、May Touch、Must Not Touch、Locked Paths、Targeted
Validation、Risk Gate、Branch/worktree/base 和 Evidence path。风险路由固定为：QF-1
`Quick Fixer -> Integrator`；QF-2 `Quick Fixer -> Reviewer -> Integrator`；QF-3
`Quick Fixer -> Reviewer -> QA -> Integrator`；QF-4 禁止 fast path，进入完整 Planner/User flow。

Quick Fixer 流程：

```text
Orchestrator 只读核验
-> Quick Fixer 在隔离 worktree 中修复
-> targeted test / smoke
-> 根据风险进入 Reviewer 或 Integrator
-> 记录 task/board/evidence 与 residual
```

出现需求歧义、范围扩大、共享所有权冲突、无法解释的测试失败、第二次同类修复失败或需要
destructive action 时，或触及 API contract/schema/migration/authority/persistence/公共盘业务语义
时，Quick Fixer 必须停止并升级到 Planner/完整任务流程。

冒烟测试后发现的纯文案、样式、明确 wiring、release guard 或单点兼容修复，默认先评估
Quick Fixer；不得仅因仓库存在完整角色流程就自动创建六个新对话。

## 20. Frozen Legacy Automation Modes

V1-Lite task-scoped bundle 和 Controlled Lane V2 均保留为历史审计材料，但不再是日常产品
任务入口。已有 V1-Lite 活动 worktree/修改必须以 checkpoint 方式保留，由 Orchestrator 决定
迁移到经典角色、完成或关闭；不得静默丢弃。

Controlled Lane V2 的 helper、registry、heartbeat、pilot、corrective 和测试继续冻结：

- `docs/project_management/CONTROLLED_LANE_ORCHESTRATION_V2.md`
- `.agents/skills/connlab-controlled-lane/SKILL.md`
- `scripts/connlab_controlled_lane.ps1`

V2 registry 保持只读，heartbeat 保持 `PAUSED`，pilot/corrective 不继续。不得通过普通
`执行 TASK_XXX` 命令启动 V2 scan、CAS journal、bootstrap、pilot、migration 或 corrective。
任何重新启用 V2 的行为都需要新的正式 task、Planner Discovery、User 明确批准以及独立
Reviewer/QA/Integrator gate。

## 21. Deterministic Active Context And Handoff

Classic permanent-role execution additionally follows
`docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md`.
The primary board JSON is the sole machine authority. Routine Developer/Reviewer/QA handoffs use
the fail-closed transition and handoff helpers, perform at most one transition and one dispatch per
Orchestrator turn, and do not launch Planner. Every Integrator closeout plans board maintenance;
only the authorized `gate_running/Integrator` owner may apply it before token release.

## 22. Personal Serial Workflow V2 Override (Current Normative Rule)

Effective 2026-08-07, the personal serial complex workflow is active. This section supersedes
sections 13–21 wherever their older daily-routing, persistent-role, Quick Fix, parallel-lane,
Controlled Lane V2 or handoff rules conflict with this section. Historical artifacts remain
retained but do not authorize execution.

Daily authority is the version-2 `connlab.personal-serial-control` JSON block in
`docs/task_board.md`; `scripts/connlab_personal_task.py` is its sole writer. WIP is exactly one from
activation through User close. A submission received while occupied returns a zero-write wait result
immediately after board parsing and before Git/worktree inspection, lock acquisition, request parsing
or classification; the User submits it again after close, and only then is it classified.

A simple task requires a clear root cause/expected result, 1–3 total changed repository paths
including tests and board, and no API/database/schema/migration/persistence/authority/public-drive/
business-semantic/destructive/external mutation. It runs directly on primary after an activation
commit, uses targeted validation, and stops at `implemented_pending_human_review`.

Every other task uses exactly three normal User interactions: submit the requirement, approve the
Planner plan, and inspect the completed result and say `关闭`. Planner is read-only. Approval binds
the exact committed plan, paths and validation contract. After approval, one task host executes
Developer -> Reviewer -> QA -> Integrator automatically and then returns the integrated result for
human review. Routine role handoffs, approved bounded fixes and a non-conflicting local integration
do not require additional User approval.

Only scope/behavior/authority change, a destructive action or an unresolved blocker returns early
to the User. Failures retain active/WIP with typed blocker and exact Git/evidence facts. Never
silently restore, discard, stash, clean, push, rebase, force-remove, delete, archive or retire.
User close records verified retained resources before releasing active. Version-2 queue compatibility
fields remain empty and have no daily operation entry.

Normative operational references:

- `docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`
- `docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/project_management/TASK_REVIEW_CHECKLIST.md`
