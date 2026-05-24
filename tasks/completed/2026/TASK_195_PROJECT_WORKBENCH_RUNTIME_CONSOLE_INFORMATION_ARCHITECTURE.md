# TASK_195 Project Workbench Runtime Console Information Architecture

> Status: done  
> Created: 2026-05-16  
> Phase: Phase 11 controlled foundation baseline, preparing Matrix-driven Laboratory Execution Phase

---

## 0. Execution Gate

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current prerequisite: `TASK_194_MATRIX_EXECUTION_PHASE_PRODUCT_REALIGNMENT` complete.
- Why this task is allowed:
  - `docs/task_board.md` recommends defining and approving TASK_195 after TASK_194.
  - The user approved the TASK_195 plan and requested creating TASK_195.
  - This task is documentation and information architecture only.

Implementation gate:

- no React component implementation;
- no CSS/styling implementation;
- no frontend behavior changes;
- no backend runtime changes;
- no DB schema changes;
- no StepInstance implementation;
- no Matrix Editor implementation.

---

## 1. Purpose

Define ConnLab's Project Workbench Runtime Console information architecture.

This task answers:

```text
When a laboratory project is running, what does the operator need to see, enter, process, track, and resolve?
```

It clarifies that Matrix-driven does not mean Matrix-first UI. Matrix is:

```text
Execution authority map
Runtime projection surface
```

---

## 2. In Scope

- Workbench runtime information hierarchy.
- Runtime attention priority model.
- Runtime versus setup boundary.
- Matrix Overview responsibility.
- Step Workspace responsibility.
- Runtime status model.
- Step token interaction model.
- Runtime issue surfacing model.
- Report sync visibility model.
- Project lifecycle versus Matrix execution relationship.
- Runtime navigation flow.

---

## 3. Out Of Scope

- React table redesign.
- Excel-like editor redesign.
- Data grid optimization.
- Visual polish.
- UI animation work.
- Component or CSS implementation.
- Backend runtime service implementation.
- DB schema or enum implementation.
- API design.
- Notification implementation.
- StepInstance implementation.
- Matrix Editor implementation.

---

## 4. Deliverables

- `docs/project_workbench_runtime_console_information_architecture.md`
- `docs/task_195_project_workbench_runtime_console_information_architecture_plan.md`
- `tasks/TASK_195_PROJECT_WORKBENCH_RUNTIME_CONSOLE_INFORMATION_ARCHITECTURE.md`
- task-board completion update

---

## 5. Acceptance Criteria

- Runtime IA document exists and covers all in-scope topics.
- Runtime Attention Priority Model is IA-only and does not define implementation mechanics.
- The document explicitly blocks Matrix regression into an Excel-like editor.
- The document distinguishes runtime execution, setup completeness, execution integrity, and derived-output integrity.
- No runtime backend/frontend/API/DB/Office files are changed.

---

## 6. Validation

Document validation:

1. Confirm required files exist.
2. Confirm forbidden implementation scope is not introduced.
3. Confirm no runtime source files changed.
4. Run static governance guard tests:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

---

## 7. Stop Condition

Stop after TASK_195 completion. Do not automatically enter TASK_196.
