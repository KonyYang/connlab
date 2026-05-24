# TASK_195 Project Workbench Runtime Console Information Architecture Plan

> Status: draft for review  
> Created: 2026-05-16  
> Phase: Phase 11 controlled foundation baseline, preparing Matrix-driven Laboratory Execution Phase  
> Task ID: TASK_195_PROJECT_WORKBENCH_RUNTIME_CONSOLE_INFORMATION_ARCHITECTURE

## 0. Execution Gate

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active task before this plan: `none`.
- Current board state: TASK_194 complete, next recommended action is to define and approve `TASK_195_PROJECT_WORKBENCH_RUNTIME_CONSOLE_INFORMATION_ARCHITECTURE`.
- Why this task is allowed now:
  - `docs/task_board.md` explicitly recommends TASK_195 as the next controlled task.
  - The user explicitly requested entering TASK_195.
  - This plan is the required pre-implementation plan document.

Important constraint:

- `tasks/TASK_195_PROJECT_WORKBENCH_RUNTIME_CONSOLE_INFORMATION_ARCHITECTURE.md` does not exist yet.
- This plan proposes creating it during TASK_195 execution after user approval.

## 1. Purpose

TASK_195 will define ConnLab's Project Workbench runtime information architecture.

The task is not a UI implementation task. It must answer:

```text
When a laboratory project is running, what does the operator need to see, enter, process, track, and resolve?
```

The task must preserve the approved principle:

```text
Matrix is the execution authority map, Project remains the lifecycle container.
```

The task must also clarify that Matrix-driven does not mean Matrix-first UI. In TASK_195, Matrix is defined as:

```text
Execution authority map
Runtime projection surface
```

The core design target is the runtime execution model, not a React table redesign.

## 2. Task Understanding

### 2.1 Goal

Define the information architecture for a Workbench Runtime Console:

- runtime execution model;
- step lifecycle;
- runtime status hierarchy;
- step-centric navigation;
- runtime issue visibility;
- report synchronization visibility;
- execution-state projection;
- Project lifecycle versus Matrix execution relationship;
- runtime navigation flow.

### 2.2 Inputs

Primary inputs:

- `AGENTS.md`
- `docs/task_board.md`
- `docs/matrix_execution_phase_principles.md`
- `docs/project_workbench_matrix_authority_workspace_target.md`
- `docs/matrix_test_plan_data_management_decisions.md`
- `docs/frontend_architecture_rules.md`
- user TASK_195 execution prompt

Reference inputs:

- TASK_194 plan and task artifacts;
- existing Workbench/Matrix task history TASK_174 through TASK_194;
- user-provided Workbench Runtime Console reference image;
- user-provided Matrix Editor reference image;
- `TestFlowManager.zip` as lessons-only reference, not source code.

### 2.3 Outputs

TASK_195 should output documentation only:

1. A formal task file:
   - `tasks/TASK_195_PROJECT_WORKBENCH_RUNTIME_CONSOLE_INFORMATION_ARCHITECTURE.md`
2. A Runtime IA document:
   - `docs/project_workbench_runtime_console_information_architecture.md`
3. A task-board update after completion:
   - `docs/task_board.md`
4. Optional static governance test updates only if existing guard tests need to recognize TASK_195 board state.

### 2.4 Modules Involved

Documentation/governance only:

- `docs/`
- `tasks/`
- possibly `tests/unit/*scope*` static governance tests, if needed.

No backend, frontend, database, API, or Office runtime modules are in scope.

### 2.5 Explicit Non-Goals

TASK_195 must not implement:

- React components;
- CSS or styling;
- table virtualization;
- drawer behavior or animation;
- frontend state or API behavior;
- backend runtime services;
- database schema;
- `StepInstance`;
- Matrix Editor;
- report generation;
- image assets;
- test data persistence.

## 3. Information Architecture Deliverable Shape

The main document, `docs/project_workbench_runtime_console_information_architecture.md`, should contain these sections.

## 4. Workbench Runtime Information Hierarchy

Define the hierarchy from highest-level attention to deepest work surface:

1. Project runtime header
   - Project identity;
   - LTR;
   - lifecycle readiness;
   - current Matrix authority;
   - last runtime update.
2. Runtime attention summary
   - active steps;
   - failed steps;
   - blocked steps;
   - missing data;
   - missing evidence/images;
   - report unsynced sections;
   - setup items blocking derived outputs, not necessarily blocking testing.
3. Matrix runtime projection
   - group and step map;
   - status projection;
   - issue markers;
   - selected step entry.
4. Step workspace
   - selected step state;
   - data/evidence/report sync context;
   - actions appropriate to execution, not definition editing.
5. Runtime attention priority
   - what must be handled first;
   - what can wait;
   - what blocks testing;
   - what only affects derived outputs;
   - what belongs to setup completeness.
6. Setup Manager/status entries
   - source materials;
   - folder;
   - approval package;
   - fee evaluation;
   - generated records;
   - supporting evidence placement.

The hierarchy should state that the primary runtime question is not "what does the table look like?" but "what needs attention in the running project?"

## 5. Runtime Attention Priority Model

Define a dedicated information architecture model for runtime attention priority.

Purpose:

```text
Workbench should express what deserves attention first when many runtime states, missing items, failures, warnings, and setup gaps coexist.
```

This is not notification implementation, backend priority engine design, enum implementation, React badge implementation, or alert system implementation.

This is an IA-level ordering model so the future Runtime Console behaves like:

```text
Runtime command console
```

not:

```text
status stacking page
```

### 5.1 Runtime Attention Concept

Runtime attention is the operator-facing answer to:

```text
What is the most important issue to handle now?
```

It should summarize the highest-impact runtime concern without forcing the operator to read the entire Matrix. Attention is derived from runtime meaning, not visual loudness. A minor setup gap should not compete with a failed active step unless that setup gap blocks the next required runtime action.

### 5.2 Priority Hierarchy

Recommended IA hierarchy:

```text
P0 - blocks execution
P1 - risks execution integrity
P2 - risks report/output integrity
P3 - runtime warning
P4 - setup completeness
```

P0 - blocks execution:

- no current Matrix authority when testing needs to start;
- active step cannot proceed because required method, condition, requirement, or group identity is missing;
- required sample/group identity is unresolved;
- blocking test data conflict prevents pass/fail decision;
- required retest decision is pending after failure.

P1 - risks execution integrity:

- step is in progress with missing required data;
- failed step has no disposition, retest decision, or responsible owner;
- evidence exists but is not linked to the active step;
- result text conflicts with normalized status;
- sequence or group mapping issue threatens execution-state meaning.

P2 - risks report/output integrity:

- report section is stale after step data/evidence change;
- generated test record is stale after Matrix authority change;
- fee evaluation is stale or missing price assumptions;
- approval package is stale against current Matrix/output records;
- derived output exists but traces to an older Matrix version.

P3 - runtime warning:

- optional evidence is missing;
- low-confidence source trace exists but does not block execution;
- duration/cost estimate is incomplete;
- step has comments that need review;
- setup action is recommended soon but does not block the current runtime action.

P4 - setup completeness:

- project folder needs cleanup or confirmation;
- source material placement is incomplete;
- approval package has not been prepared;
- fee file has not been generated;
- external resource validation is stale but no current runtime action depends on it.

### 5.3 Attention Surfacing Order

Define surfacing order:

1. Show the highest active priority at project level.
2. Group related issues by runtime object: project, Matrix authority, group, step, derived output, setup surface.
3. Prefer execution-blocking issues over setup completeness.
4. Prefer selected/active group issues over inactive group warnings when priorities are equal.
5. Prefer issues with direct next action over passive informational warnings.

The model should support a future console that can say:

```text
Step 2 in Group 3 failed and needs disposition before execution can continue.
```

instead of only showing a list of disconnected statuses.

### 5.4 Runtime Issue Escalation Direction

Define escalation routes:

- P0/P1 execution issues route to Step Workspace or Matrix change request when definition is the root cause.
- P2 output-integrity issues route to derived output status surfaces, such as report sync, test record, fee, or approval package.
- P3 warnings stay visible in runtime context but should not interrupt the primary action.
- P4 setup completeness issues route to Setup Manager/status entries.

Escalation should answer:

```text
Where should the operator go next to resolve this?
```

### 5.5 Blocking Categories

Issues that block testing:

- missing current Matrix authority;
- unresolved step identity, group identity, or required sequence meaning;
- missing required method/condition/requirement for a step that is ready to execute;
- failed step requiring disposition before dependent steps continue;
- conflicting result/status data that prevents execution decision.

Issues that do not block testing but affect derived outputs:

- stale report draft;
- stale generated test record;
- stale approval package;
- stale fee evaluation;
- missing report section;
- output generated from old Matrix version.

Issues that belong to setup completeness:

- folder not created when testing can still proceed;
- source material not placed in final folder;
- approval package not assembled;
- fee form not generated;
- external resource validation not current when not needed for the current step.

Issues that belong to execution integrity:

- missing step data;
- missing required evidence/image for a step decision;
- failed step without disposition;
- result/status conflict;
- evidence not linked to the step it supports;
- runtime state inconsistent with Matrix authority.

## 6. Runtime vs Setup Boundary

Define two categories:

Runtime:

- step status;
- step lifecycle;
- test data state;
- evidence/image readiness;
- failure state;
- retest or blocked state;
- report sync state;
- current execution risks.

Setup:

- project folder existence;
- source material placement;
- application form Section 2 write-back;
- test-record form generation;
- fee-evaluation file generation;
- approval package preview/execute;
- external resource configuration.

Key rule:

```text
Setup supports execution. Setup must not occupy the runtime center unless it blocks the next runtime action.
```

## 7. Matrix Overview Responsibility

Define Matrix Overview as a projection surface, not an editor:

- shows current Matrix authority version;
- shows groups and step tokens;
- projects runtime status onto step tokens;
- supports selection/navigation into Step Workspace;
- exposes issue markers for missing data/evidence/failure/report sync;
- preserves technical context needed for execution:
  - test item;
  - section;
  - method;
  - condition;
  - requirement.

Out of responsibility:

- direct condition/requirement editing;
- step mapping changes;
- sequence changes;
- template import;
- Excel-like bulk editing;
- direct record/report/file writes.

## 8. Step Workspace Responsibility

Define Step Workspace as the execution workspace for one selected step.

It should eventually contain:

- step identity:
  - project;
  - Matrix version;
  - group;
  - sequence;
  - token variant;
  - test item.
- execution state:
  - not started;
  - in progress;
  - pass;
  - failed;
  - blocked;
  - waiting evidence;
  - report unsynced.
- required technical context:
  - method;
  - condition;
  - requirement;
  - step description.
- execution artifacts:
  - measurements/data;
  - images;
  - attachments/evidence;
  - comments;
  - actual completion time;
  - actual cost.
- derived-output relationships:
  - test record status;
  - report section sync;
  - fee impact.

TASK_195 only defines responsibilities and future relationships. It does not create data entry UI or backend persistence.

## 9. Runtime Status Model

Define a conceptual status hierarchy without implementing enums or schema.

Suggested hierarchy:

1. Identity readiness
   - no Matrix authority;
   - Matrix candidate pending;
   - Matrix authority current;
   - Matrix authority stale or superseded.
2. Execution status
   - not started;
   - ready;
   - in progress;
   - paused;
   - blocked;
   - pass;
   - fail;
   - retest required;
   - waived or not applicable.
3. Evidence/data status
   - data missing;
   - data present;
   - evidence missing;
   - evidence present;
   - image missing;
   - image present.
4. Derived output sync status
   - missing;
   - current;
   - stale;
   - failed;
   - manual;
   - not applicable.
5. Project readiness projection
   - Draft;
   - Test Ready;
   - Authority Ready;
   - Report Ready;
   - Closed.

The document should explicitly distinguish project readiness from step execution status.

## 10. Step Token Interaction Model

Define step token interaction as navigation into runtime state:

- token displays sequence and variant;
- token carries status projection;
- token is selectable;
- selection opens or focuses Step Workspace;
- token may show compact markers for:
  - fail;
  - in progress;
  - missing data;
  - missing evidence;
  - report unsynced;
  - blocked.

Token interaction must not imply direct definition editing. Definition changes route to Matrix Editor or a Matrix change request flow.

## 11. Runtime Issue Surfacing Model

Define issue levels and surfacing rules.

Issue groups:

- runtime attention priorities;
- execution blockers;
- failed steps;
- missing data;
- missing evidence/images;
- report sync gaps;
- setup blockers;
- source traceability warnings;
- Matrix authority warnings.

Surfacing hierarchy:

1. Highest-priority runtime attention summary.
2. Global runtime attention list ordered by priority.
3. Group-level issue projection.
4. Step token marker.
5. Step Workspace issue list.
6. Setup Manager status entry if the issue belongs to setup rather than execution.

The document should state that not every setup issue blocks testing.

## 12. Report Sync Visibility Model

Define report sync as visibility, not report generation.

Report sync states should show:

- not started;
- section missing;
- data newer than report;
- evidence newer than report;
- synced/current;
- manual update required;
- sync failed.

Visibility relationships:

- Step updates can make report sections stale.
- Matrix authority changes can make report, record, fee, and approval outputs stale.
- Report is a derived output and must not become the primary data source.

TASK_195 does not implement report draft sync.

## 13. Project Lifecycle vs Matrix Execution Relationship

Define relationship:

- Project lifecycle describes the whole project state.
- Matrix execution describes the test execution state inside the project.
- Step lifecycle describes the granular execution state.

Example relationship:

```text
Project: active
Matrix authority: v3 current
Group 3: in progress
Step 2: failed, evidence present, report unsynced
Approval package: stale, does not block retest
```

The document should clarify that `Test Ready` can precede `Authority Ready` or `Approval Package Ready`.

## 14. Runtime Navigation Flow

Define navigation flow as information hierarchy:

1. Open Project Workbench.
2. Read runtime attention summary.
3. Review Matrix runtime projection.
4. Select group or step token needing attention.
5. Work in Step Workspace.
6. Resolve data/evidence/status/report sync issue or route to setup/definition surface.
7. Return to Matrix runtime projection and continue.

Branching rules:

- Definition issue: request Matrix change / open Matrix Editor.
- Setup issue: open Setup Manager/status entry.
- Execution issue: stay in Step Workspace.
- Output issue: open derived-output status surface.

## 15. File-Level Change Plan

### 15.1 `tasks/TASK_195_PROJECT_WORKBENCH_RUNTIME_CONSOLE_INFORMATION_ARCHITECTURE.md`

Create the formal task file with:

- execution gate;
- purpose;
- in-scope/out-of-scope;
- acceptance criteria;
- validation method;
- stop condition.

### 15.2 `docs/project_workbench_runtime_console_information_architecture.md`

Create the main Runtime IA document with the sections above.

### 15.3 `docs/task_board.md`

After TASK_195 completion:

- record TASK_195 completion;
- update last updated date;
- record validation summary;
- set next recommended task.

Recommended next task:

```text
TASK_196_STEP_CENTRIC_DOMAIN_FOUNDATION
```

### 15.4 Static Governance Tests

Only if needed, update existing static guard tests so they recognize TASK_195 completion in the board.

Do not add runtime/frontend tests because this is a documentation-only task.

## 16. Acceptance Criteria

TASK_195 is complete when:

- `tasks/TASK_195_PROJECT_WORKBENCH_RUNTIME_CONSOLE_INFORMATION_ARCHITECTURE.md` exists.
- `docs/project_workbench_runtime_console_information_architecture.md` exists.
- The Runtime IA document covers:
  - Workbench Runtime Information Hierarchy;
  - Runtime Attention Priority Model;
  - Runtime vs Setup boundary;
  - Matrix Overview responsibility;
  - Step Workspace responsibility;
  - Runtime status model;
  - Step token interaction model;
  - Runtime issue surfacing model;
  - Report sync visibility model;
  - Project lifecycle vs Matrix execution relationship;
  - Runtime navigation flow.
- The document explicitly says Matrix-driven does not mean Matrix-first UI.
- The document explicitly blocks Excel-like Matrix editing.
- The document explicitly defines how Workbench expresses the highest-priority runtime attention item without becoming a status stacking page.
- `docs/task_board.md` records completion and next recommended task.
- No React, CSS, backend, API, DB, or Office runtime files are changed.

## 17. Validation Plan

Document validation:

1. Confirm required files exist.
2. Search the TASK_195 documents for forbidden implementation language, including:
   - React component implementation;
   - CSS/styling;
   - table virtualization;
   - drawer animation;
   - DB schema;
   - StepInstance implementation.
3. Confirm the Runtime Attention Priority Model remains IA-only and does not define DB schema, status enums, APIs, notification behavior, or React badge implementation.
4. Confirm no runtime source files changed.
5. Run governance guard tests if board state changes require it:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

No `npm run build` is required because no frontend implementation should change.

## 18. Risks And Controls

Risk: TASK_195 may drift into a page layout or visual redesign task.  
Control: keep output at information architecture and responsibility-boundary level only.

Risk: "Matrix-driven" may be interpreted as "Matrix-first UI".  
Control: state that Matrix is the execution authority map and runtime projection surface, not the whole runtime model.

Risk: Matrix may regress into an Excel-like editor.  
Control: define Matrix Overview as a projection and navigation surface; definition editing belongs to Matrix Editor.

Risk: setup work may still dominate Workbench thinking.  
Control: separate Runtime from Setup and define Setup Manager/status entries as supporting surfaces.

Risk: runtime attention may drift into a notification system or priority engine design.  
Control: define priority as IA-level surfacing order only; do not define database schema, enums, API, alerts, or badges in TASK_195.

Risk: future StepInstance work may be designed too broadly.  
Control: TASK_195 defines relationships only; TASK_196 must still separately plan the minimal domain foundation.

## 19. Stop Condition

After this plan is reviewed, do not proceed to TASK_195 execution until the user explicitly approves.

After TASK_195 execution is later completed, stop again. Do not automatically enter TASK_196.
