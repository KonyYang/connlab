# TASK_193 Phase Freeze, Architecture Inventory, Scope Redefinition Plan

> Status: proposed for review  
> Created: 2026-05-15  
> Task: `TASK_193_PHASE_FREEZE_ARCHITECTURE_INVENTORY_SCOPE_REDEFINITION`  
> Phase: `Phase 11 - Project planning data foundation before downstream document automation`

---

## 1. Execution Protocol

- Current phase: `Phase 11`.
- Current active task: `none` (task board states TASK_192 complete and waiting next controlled task).
- Why this task is allowed now:
  - User explicitly requested a governance/documentation action (stage freeze + architecture inventory + scope redefinition).
  - This is a bounded documentation and alignment task, not a cross-scope feature build.
  - It can be executed as the next controlled task after TASK_192 without changing business behavior.

This file is the required executable plan. No implementation edits should start before explicit user approval.

---

## 2. Goal And Boundaries

### Goal

Perform one controlled project-level governance pass:

1. Stage freeze (current baseline snapshot).
2. Architecture inventory (docs/tasks/code consistency check).
3. Scope redefinition (explicitly move from early MVP wording to current Project Workbench / Matrix / Approval Package stage).

### Hard boundaries

- No large-scale business-code refactor.
- No behavior change to existing APIs/frontend workflows.
- No schema migration purely for cleanup.
- No new future-scope module implementation.
- Focus on documentation and task governance consistency.

---

## 3. Current Observed Mismatch (Inventory Input)

Based on current repository state:

- `README.md` still describes ConnLab as an MVP and marks Matrix/report flows out of scope.
- `docs/task_board.md` records completion through `TASK_192` and substantial Matrix / draft authority / approval package capabilities.
- `backend/api` and `frontend/src/features/project-workbench` already contain Matrix editing/review/freeze-related and approval-package pipeline routes/components.
- `tasks/` history includes many post-MVP tasks (`TASK_174+` etc.) that materially exceed initial MVP boundaries.

Conclusion: formal docs baseline is not synchronized with implemented system stage.

---

## 4. Proposed Implementation Design (Docs-Only)

### 4.1 Stage Freeze Artifact

Create a single freeze document, e.g.:

- `docs/stage_freeze_2026-05-15_project_workbench_matrix_approval_package.md`

Content structure:

- freeze date and commit-context note;
- accepted capability snapshot (implemented);
- excluded/deferred capability snapshot (not yet implemented);
- authority statement: current stage is no longer early MVP.

### 4.2 Architecture Inventory Artifact

Create a traceability matrix document, e.g.:

- `docs/architecture_inventory_2026-05-15.md`

Sections:

- `README claimed scope` vs `task_board actual scope` vs `code evidence` comparison table;
- backend layer structure check against AGENTS architecture rules;
- route/module/page ownership map for:
  - New Project Intake;
  - Project Workbench Matrix;
  - Approval Package pipeline;
  - Output version ledger;
- mismatch list with severity (`critical governance mismatch` / `minor wording drift`).

### 4.3 Scope Redefinition Update

Update core governance docs (text-level only):

1. `README.md`
   - replace MVP-only positioning with staged positioning;
   - set current mainline to `Project Workbench / Matrix / Approval Package`.
2. `docs/task_board.md`
   - update header fields:
     - `Current Phase`
     - `Current Active Task`
     - top-level status sentence
   - append completion note for TASK_193 with summary + validation.
3. `AGENTS.md` (minimal, controlled wording update only if approved)
   - preserve all architectural and anti-pattern rules;
   - revise scope section to distinguish:
     - historical MVP baseline;
     - current active stage.

If AGENTS scope rewrite is considered too broad for one task, keep AGENTS unchanged and record controlled exception in TASK_193 note.

### 4.4 New Task File Registration

Add:

- `tasks/TASK_193_PHASE_FREEZE_ARCHITECTURE_INVENTORY_SCOPE_REDEFINITION.md`

Purpose: make this governance action auditable as a normal controlled task.

---

## 5. File-Level Change List (Planned)

- Add `docs/stage_freeze_2026-05-15_project_workbench_matrix_approval_package.md`
- Add `docs/architecture_inventory_2026-05-15.md`
- Add `tasks/TASK_193_PHASE_FREEZE_ARCHITECTURE_INVENTORY_SCOPE_REDEFINITION.md`
- Update `README.md`
- Update `docs/task_board.md`
- Optional minimal update `AGENTS.md` (only if explicitly approved inside this task)

No changes planned under `backend/`, `frontend/src/`, `tests/` for this task.

---

## 6. Risks And Controls

Risk: documentation redefinition accidentally implies unimplemented capabilities.  
Control: every statement must be backed by existing task-board entries and route/component evidence.

Risk: AGENTS MVP wording conflicts with current board and causes future execution ambiguity.  
Control: either (a) minimal controlled wording update or (b) explicit exception note in task board and TASK_193 output.

Risk: hidden scope creep into architecture refactor.  
Control: strictly prohibit business-code edits and schema/behavior changes in this task.

---

## 7. Validation Plan

Governance/document checks:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

Sanity checks:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix or approval or task193"
```

Build (no functional change expected, optional confidence check):

```powershell
Set-Location frontend
npm run build
Set-Location ..
```

If any command is not runnable in current environment, document the reason and provide manual verification steps.

---

## 8. Acceptance Criteria

- A dated freeze document exists and clearly states current stage baseline.
- A traceable inventory document exists with `README vs task_board vs code` consistency table.
- README no longer labels Matrix / Approval Package as out-of-scope for current stage.
- Task board is updated to register TASK_193 completion and next recommended task.
- No backend/frontend business behavior is modified.
- Any AGENTS/task-board wording conflict is explicitly resolved or explicitly recorded with rationale.

---

## 9. Approval Needed

Please approve this TASK_193 plan.

After approval, I will execute documentation updates only (no large-scale code refactor, no cross-task feature work), then return a concise diff summary and validation results.
