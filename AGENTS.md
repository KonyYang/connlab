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
- `docs/project_management/ROLE_THREAD_REGISTRY.md`

自动编排只能转发和接力已批准 lane，不得绕过以下规则：

- proposed/planned 不能执行
- Developer 只能修改 lane 允许范围
- Reviewer/QA blocking finding 必须回到 Developer 修复
- Integrator 只能在 merge gate 满足后合并
- evidence 文件和 `docs/task_board.md` 优先于聊天记忆

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

受控并行必须使用真实 Git 隔离，不能把不同聊天线程当作隔离。

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

自动化入口：

- `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md`
- `scripts/connlab_lane_worktree.ps1`
- `scripts/task_complete_commit.ps1`

默认任务启动语义：

- 当用户明确说“执行 TASK_XXX”“启动 TASK_XXX”或“实施 TASK_XXX”时，默认进入受控全自动编排；用户不需要重复说明 worktree/branch 或“持续到 Integrator”。
- Orchestrator 必须先重新读取 board/task/plan/evidence、角色线程状态和 `git worktree list`，不得仅凭聊天记忆判断是否已有任务在执行。
- 若同一 TASK 已有 worktree，必须复用并续跑，禁止创建重复 branch/worktree。
- 若其他 lane 正在执行，先比较 `Locked Paths`、shared files 和 authority ownership：无重叠才可并行；有重叠则自动排队/串行，不得靠不同 worktree 绕过所有权冲突。
- product/tests-only implementation 即使当前没有其他任务，也默认使用独立 lane worktree；primary worktree 继续只承担 planning/integration。
- 在用户已批准的 task/Goal 范围内，自动持续到本地 Integrator acceptance，并自动完成普通 Reviewer/QA/fix/reconciliation/local-commit/worktree-retire 接力。
- 只有缺少正式批准、范围/行为变化、shared ownership 冲突、无法解释的测试失败、destructive discard 或未授权 merge/push 才暂停找用户。

绝对禁止：

- `git add -A`
- force-remove dirty worktree
- 未授权 discard/reset/restore/delete
- 未授权 remote push
- 把 unnamed residual 留给未来人工猜测

## 19. V1-Lite Task-Scoped Role Lifecycle

ConnLab 日常产品任务默认使用 V1-Lite：

```text
一个产品 TASK
-> 一个临时 Controller
-> 临时 Planner / Developer / Reviewer / QA / Integrator
-> Integrator closeout
-> 归档该 TASK 的全部临时角色对话
```

固定入口为 `ConnLab｜研发任务编排与集成主控`，线程 ID 记录在
`docs/project_management/ROLE_THREAD_REGISTRY.md`。固定入口只接收新任务、读取
board/task/plan/evidence、创建任务专属角色包并报告 closeout；不得承载完整 diff、测试日志或
跨 TASK 的角色工作。

强制规则：

1. 每个产品 TASK 使用新的任务专属 Controller 和角色线程，下一 TASK 不复用。
2. 角色线程按 gate 延迟创建；同一 TASK 的 bounded fix 可复用该 TASK 的 Developer/Reviewer。
3. `docs/task_board.md`、task、plan、evidence 和 Git 高于 bundle manifest 与聊天记忆。
4. 当前 bundle 记录在 `docs/project_management/ACTIVE_TASK_THREAD_BUNDLE.md`。
5. callback 只传 TASK、ROLE、STATUS、EVIDENCE、COMMIT、NEXT、BLOCKER。
6. Integrator 只有在 evidence/commit/worktree/residual/remote 状态全部收口后才能归档。
7. 归档顺序为 Planner -> Developer -> Reviewer -> QA -> Integrator -> task-specific Controller。
8. 归档是可恢复操作；不得删除对话、丢弃 dirty worktree 或遗漏 retained owner。
9. 固定入口不得作为 Developer worktree，也不得替代 Planner/Reviewer/QA/Integrator gate。

## 20. Controlled Lane V2 Frozen Legacy

Controlled Lane V2 的 helper、registry、heartbeat、pilot、corrective 和测试保留为历史审计
材料，但不再是日常产品任务入口。

- `docs/project_management/CONTROLLED_LANE_ORCHESTRATION_V2.md`
- `.agents/skills/connlab-controlled-lane/SKILL.md`
- `scripts/connlab_controlled_lane.ps1`

V2 registry 保持只读，heartbeat 保持 `PAUSED`，pilot/corrective 不继续。不得通过普通
`执行 TASK_XXX` 命令启动 V2 scan、CAS journal、bootstrap、pilot、migration 或 corrective。
任何重新启用 V2 的行为都需要新的正式 task、Planner Discovery、User 明确批准以及独立
Reviewer/QA/Integrator gate。
