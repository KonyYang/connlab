# AGENTS.md — ConnLab AI Coding Rules

> **Current daily workflow authority:** section 13, Personal Serial Workflow V2, and the active
> `connlab-lane-orchestrator` skill are the only daily routing authority. Historical workflow
> documents outside this file remain audit evidence and do not authorize daily execution.

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

## 13. Personal Serial Workflow V2 (Current Normative Rule)

Effective 2026-08-07, Personal Serial Workflow V2 is the only daily task workflow. The serial complex workflow is active. Older lane,
persistent-role, Quick Fix, parallel-lane, Controlled Lane V2, and deterministic handoff documents are
historical evidence only unless a new approved task explicitly reactivates them.

### Authority and entry

- The version-2 `connlab.personal-serial-control` block in `docs/task_board.md` is the sole machine
  authority; `scripts/connlab_personal_task.py` is its sole writer.
- Read `AGENTS.md`, `docs/task_board.md`, the active Task/Plan, and relevant evidence before acting.
- User-facing task actions are only Submit, Approve, and Close through `scripts/run_task.ps1`.
- Board, Git, committed Task/Plan, and evidence override conversation memory.
- WIP is exactly one from activation through explicit User Close. A new request while occupied is
  zero-write and must be resubmitted after close.

### Proportionate routing

A simple task requires a clear root cause and expected result, 1–3 total changed repository paths
including tests and board, and no API/database/schema/migration/persistence/authority/public-drive/
business-semantic/destructive/external mutation. It runs directly on primary after its activation
commit, receives bounded validation, and stops at human review.

Every other task is planned/complex:

```text
Submit -> fresh read-only Planner -> User approval
-> one task host -> Developer -> Reviewer -> QA -> Integrator
-> verified local integration -> human review -> User 关闭
```

A normal complex task has three User interactions: submit the requirement, approve the exact committed
plan, and inspect the completed result and say `关闭`. Routine role handoffs, approved bounded fixes,
and non-conflicting local integration require no extra approval. Reviewer/QA blockers return to
Developer only inside approved scope.

Supporting skills are selected by role and risk according to
`.agents/skills/connlab-lane-orchestrator/SKILL.md`; they never create a new route or expand scope.

### Execution and safety

- Commit each authority transition before the next write-capable action.
- Modify only approved `may_touch` paths and validate against the frozen plan.
- Keep the task host clean at the exact reviewed subject; primary owns execution evidence and integration.
- Return early only for scope/behavior/authority change, destructive action, conflict, unprovable
  identity/evidence, dirty divergence, or an unresolved repeated failure.
- Never silently restore, discard, stash, clean, push, rebase, force-remove, delete, archive, or retire.
- Stop at `implemented_pending_human_review`; only explicit User `关闭` releases WIP.
- Do not automatically start another task after close.

### Normative operational references

- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md`
- `docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`
- `docs/project_management/TASK_REVIEW_CHECKLIST.md`

Frozen legacy skills remain available only for explicit audit and have implicit invocation disabled:

- `.agents/skills/connlab-planner/` is an explicit-only read-only planning reference.
- `.agents/skills/connlab-controlled-lane/` is frozen Controlled Lane audit material.
