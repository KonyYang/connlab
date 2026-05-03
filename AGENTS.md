# AGENTS.md — ConnLab AI Coding Rules

## 1. Product Mission

ConnLab is an offline Windows-first workbench for an electronic connector laboratory. It supports project intake, application-form precheck, LTR tracking, and project folder creation first, with future expansion to Matrix planning, test records, test result ingestion, image assets, report generation, report audit, knowledge base, and AI review.

ConnLab is a new project. Do not copy old TestFlowManager architecture. Old code and documents are reference material only.

## 2. Current MVP Scope

Only implement the MVP unless a task explicitly says otherwise:

1. Application form intake and precheck.
2. LTR number registration / tracking.
3. Project folder creation from a template.

Do not implement Matrix, Test Record, Report Generation, AI review, multi-user collaboration, permissions, or LAN deployment during the MVP unless a future task explicitly requests it.

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

- Project is the system center.
- Application form is the project starting point.
- Precheck is the first quality gate.
- LTR and project folder creation are downstream of a confirmed project.
- Word and Excel are input/output formats, not the primary system data model.
- All extracted or confirmed data must be stored as structured records.
- Every future feature must attach to a Project lifecycle stage.

## 6. MVP Domain Objects

Implement these before any advanced objects:

- Project
- ApplicationForm
- SampleInfo
- PrecheckResult
- PrecheckIssue
- LtrRecord
- ProjectFolderRecord
- FileAsset

Future reserved objects, not MVP implementation unless requested:

- MatrixPlan
- TestDefinition
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
- Treat Matrix as the system center.
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
4. Implement only the current active task allowed by `docs/task_board.md`.
5. Add/update tests.
6. Run relevant tests if possible.
7. Update `docs/task_board.md` after task completion before closing the turn.
8. Summarize changed files and any known limitations.

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
2. 使用 TASK_EXECUTION_SKILL.md
3. 输出设计方案后再写代码
4. 执行 TASK_REVIEW_CHECKLIST.md
5. 提供运行验证方法
6. 停止，不进入下一个任务

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
