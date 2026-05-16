# TASK_194 Matrix Execution Phase Product Realignment Plan

> Status: draft for review  
> Created: 2026-05-16  
> Phase: Phase 11 controlled foundation baseline, preparing Matrix-driven Laboratory Execution Phase  
> Task ID: TASK_194_MATRIX_EXECUTION_PHASE_PRODUCT_REALIGNMENT

## 0. Execution Gate

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active task before this plan: `none`.
- Why TASK_194 is allowed now:
  - `docs/task_board.md` says TASK_193 is complete and the next action is to define and approve the next controlled implementation task.
  - The user explicitly confirmed entering the TASK_194 plan-preparation stage.
  - This plan is documentation and governance preparation only.

No business code, database model, API contract, frontend component, or runtime behavior change is included in this plan step.

## 1. Purpose

TASK_194 will align ConnLab's product direction, governance documents, and task roadmap with the next formal product direction:

```text
Matrix-driven Laboratory Execution Phase
```

The key principle to record across project governance is:

```text
Matrix is the execution authority map, Project remains the lifecycle container.
```

Interpretation:

- `Project` owns the project lifecycle, intake history, LTR linkage, folder state, and overall traceability.
- `Matrix` owns the authoritative test execution map for what must be tested.
- `Step` owns execution-level data, status, evidence, lifecycle, and later report bindings.
- `Test Record`, `Report`, `Fee Evaluation`, and `Approval Package` are derived outputs, not primary data.

## 2. Confirmed Direction

The next stage should move ConnLab away from a setup-heavy approval dashboard and toward a Matrix-driven laboratory execution system.

Confirmed route:

1. Plan Workbench Runtime Console information architecture first.
2. Establish minimal step-centric backend/domain foundation next.
3. Refactor Matrix Editor into a Definition Studio after runtime boundaries are clear.

Confirmed UI/product boundary:

- Project Workbench becomes the `Live Project Runtime Console`.
- Matrix Editor becomes the `Test Plan Definition Studio`.
- Workbench does not directly edit Matrix definition by default. It can request Matrix changes and route to Matrix Editor.
- Folder, Approval Package, Evidence Placement, Source Materials, and Fee Evaluation become setup/status entry points or folded workspaces rather than the main Workbench visual weight.

Confirmed lifecycle direction:

- Testing may begin before approval-package/setup work is fully complete.
- Future readiness levels may allow `Test Ready` before `Authority Ready` or `Approval Package Ready`.
- Setup must not block real laboratory testing when the Matrix/test execution path is ready.

## 3. Inputs

TASK_194 uses the following source material:

- `AGENTS.md`
- `README.md`
- `PRODUCT.md`
- `ConnLab_Master_Blueprint.md`
- `docs/task_board.md`
- `docs/stage_freeze_2026-05-15_project_workbench_matrix_approval_package.md`
- `docs/architecture_inventory_2026-05-15.md`
- `docs/matrix_test_plan_data_management_decisions.md`
- `docs/project_workbench_matrix_authority_workspace_target.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `connlab_matrix_workbench_rearchitecture_guideline.md` supplied by the user
- UI direction references supplied by the user:
  - Matrix Editor / Definition Studio reference
  - Project Workbench / Runtime Console reference
- `TestFlowManager.zip` as lessons-only reference material

## 4. In Scope

TASK_194 should make governance and planning changes only:

1. Create a formal task file:
   - `tasks/TASK_194_MATRIX_EXECUTION_PHASE_PRODUCT_REALIGNMENT.md`
2. Add a Matrix execution phase architecture/principles document, proposed:
   - `docs/matrix_execution_phase_principles.md`
3. Update product/governance wording in:
   - `AGENTS.md`
   - `README.md`
   - `PRODUCT.md`
   - `ConnLab_Master_Blueprint.md`
   - `docs/task_board.md`
4. Update or add roadmap guidance for the next controlled sequence:
   - Workbench Runtime Console information architecture
   - Step-centric foundation
   - Matrix Editor Definition Studio
5. Record legacy TestFlowManager lessons at the principle level:
   - keep high-density Matrix overview and lab workflow insights
   - reject legacy architecture, Excel-first data authority, UI-driven business logic, and string-only Matrix cells
6. Preserve existing Phase 11 frozen baseline while declaring the next product direction.

## 5. Out Of Scope

TASK_194 must not:

- modify backend business logic;
- add or change database tables;
- add `StepInstance` implementation;
- add runtime status persistence;
- change FastAPI route behavior;
- refactor React components;
- implement Workbench Runtime Console UI;
- implement Matrix Editor UI;
- implement test data persistence, image assets, report sync, AI review, permissions, or LAN deployment;
- migrate or copy code from `TestFlowManager.zip`;
- change Office gateway behavior;
- change existing Matrix draft confirmation semantics.

## 6. File-Level Change Plan

### 6.1 `tasks/TASK_194_MATRIX_EXECUTION_PHASE_PRODUCT_REALIGNMENT.md`

Create the task artifact with:

- execution gate;
- purpose;
- in-scope and out-of-scope boundaries;
- acceptance criteria;
- validation steps;
- explicit stop condition after governance alignment.

### 6.2 `docs/matrix_execution_phase_principles.md`

Create the next-stage principle document with these sections:

- phase definition;
- Project / Matrix / Step / Output authority model;
- Definition Layer vs Execution Layer;
- Workbench Runtime Console principles;
- Matrix Editor Definition Studio principles;
- Interactive Step Token and StepInstance direction;
- setup/status-entry demotion rule;
- real laboratory workflow rule: setup cannot block testing;
- TestFlowManager lessons to keep and reject;
- prohibited anti-patterns for the next phase.

### 6.3 `AGENTS.md`

Update stable project rules so they no longer describe the project as MVP-only.

Expected changes:

- preserve historical MVP scope as completed baseline;
- add current baseline: Phase 11 controlled foundation;
- add next product direction: Matrix-driven Laboratory Execution Phase;
- replace the old Matrix prohibition with a more precise boundary:
  - Project remains lifecycle container;
  - Matrix is execution authority map;
  - Matrix must not become an Excel-like string editor;
  - all Matrix/Step features must remain task-controlled.
- keep all existing layering, Office gateway, API, frontend, task-board, and approval-gate rules.

### 6.4 `README.md`

Update stage wording only:

- keep current working stage visible;
- add next product direction;
- clarify deferred areas still not active unless task-approved.

### 6.5 `PRODUCT.md`

Update product purpose and strategic principles:

- ConnLab is moving from project preparation into Matrix-driven execution;
- Workbench should communicate execution state, not just setup state;
- Matrix owns test execution authority, while Project remains the container;
- reports and fees are derived outputs.

### 6.6 `ConnLab_Master_Blueprint.md`

Because this file contains older packed guidance, update only the high-level source-of-truth sections or add a dated addendum.

Preferred approach:

- avoid rewriting the whole large document;
- add a 2026-05-16 addendum that points to `docs/matrix_execution_phase_principles.md`;
- clarify that older MVP-only and "Matrix is not central" wording is historical unless superseded by the task board and the new principles document.

### 6.7 `docs/task_board.md`

Update after TASK_194 completion only, not during plan drafting:

- set status to include TASK_194 complete;
- set last updated date;
- record validation summary;
- set next recommended task.

Proposed next recommended task:

```text
TASK_195_PROJECT_WORKBENCH_RUNTIME_CONSOLE_INFORMATION_ARCHITECTURE
```

## 7. Proposed Next Task Sequence

The following sequence should be documented, not implemented in TASK_194:

1. `TASK_195_PROJECT_WORKBENCH_RUNTIME_CONSOLE_INFORMATION_ARCHITECTURE`
   - planning/design task;
   - no UI implementation;
   - defines Workbench Runtime Console structure, status hierarchy, setup-manager demotion, and step workspace placement.
2. `TASK_196_STEP_CENTRIC_DOMAIN_FOUNDATION`
   - minimal backend/domain design and persistence plan for `StepInstance`, lifecycle, status, and Matrix cell parsing alignment.
3. `TASK_197_INTERACTIVE_STEP_TOKEN_READ_MODEL`
   - backend read model/API for Matrix overview tokens with status metadata, without full execution data entry.
4. `TASK_198_WORKBENCH_RUNTIME_CONSOLE_UI_BASELINE`
   - UI implementation of Matrix as persistent main view and setup areas as status entries, using existing data where possible.
5. `TASK_199_MATRIX_EDITOR_DEFINITION_STUDIO_INFORMATION_ARCHITECTURE`
   - Definition Layer plan for Matrix Editor before any editor UI refactor.

## 8. Acceptance Criteria

TASK_194 is complete when:

- `tasks/TASK_194_MATRIX_EXECUTION_PHASE_PRODUCT_REALIGNMENT.md` exists and matches the approved plan.
- `docs/matrix_execution_phase_principles.md` exists and records the new authority model.
- `AGENTS.md`, `README.md`, `PRODUCT.md`, and `ConnLab_Master_Blueprint.md` no longer conflict with the confirmed Matrix-driven direction.
- `docs/task_board.md` records TASK_194 completion, validation, and next recommended task.
- No backend behavior, frontend behavior, API contract, database schema, or Office gateway behavior is changed.

## 9. Validation Plan

Because TASK_194 is governance/documentation only, validation is document-level:

1. Confirm all referenced files exist.
2. Search for direct contradictions in updated docs, especially:
   - MVP-only current-stage wording;
   - absolute "do not implement Matrix" wording outside historical context;
   - "Matrix as system center" wording that conflicts with Project as lifecycle container.
3. Confirm no code/runtime files changed outside approved documentation/task files.
4. Run task-board guard tests if practical:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

No `npm run build` is required unless frontend files are modified, which this task should not do.

## 10. Risks And Controls

Risk: new guidance may make Matrix sound like it replaces Project as the system center.  
Control: use the approved wording: `Matrix is the execution authority map, Project remains the lifecycle container.`

Risk: documentation updates could accidentally authorize too much feature work.  
Control: every future task remains controlled by `docs/task_board.md`, task files, and explicit approval.

Risk: old MVP documents and packed blueprint may retain contradictory historical text.  
Control: update active governance wording and add an explicit supersession note rather than rewriting all history.

Risk: UI reference images may be interpreted as immediate implementation targets.  
Control: record them as directional references only; TASK_194 does not implement UI.

Risk: TestFlowManager code may tempt direct migration.  
Control: state clearly that it is lessons-only reference material and must not be copied into ConnLab.

## 11. Stop Condition

After this plan is reviewed, do not proceed to TASK_194 execution until the user explicitly approves.

After TASK_194 execution is later completed, stop again. Do not automatically enter TASK_195.
