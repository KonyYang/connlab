# Matrix Execution Phase Principles

> Created: 2026-05-16  
> Scope: Product, architecture, and task-planning principles for the next ConnLab phase.  
> Status: Active guidance after TASK_194.

## 1. Phase Definition

ConnLab has completed and extended the original preparation-oriented MVP baseline:

```text
Project -> Application form -> Precheck -> LTR -> Project Folder
```

The current frozen baseline remains:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

The next product direction is:

```text
Matrix-driven Laboratory Execution Phase
```

This is a direction and governance statement. It does not authorize unscoped implementation. Every feature still requires an approved task in `docs/task_board.md`.

## 2. Authority Model

Approved principle:

```text
Matrix is the execution authority map, Project remains the lifecycle container.
```

Meaning:

- `Project` owns lifecycle identity, intake history, LTR linkage, folder state, source evidence, and overall traceability.
- `Matrix` owns the authoritative test execution map for what must be tested.
- `Step` owns execution data, status, lifecycle, evidence, measurements, images, comments, dates, cost, and later report bindings.
- `Test Record`, `Report`, `Fee Evaluation`, and `Approval Package` are derived outputs from structured project, Matrix, and Step data.

ConnLab must not become a generic tool collection, an Excel-like Matrix editor, or an approval-document-only system.

## 3. Definition Layer And Execution Layer

ConnLab separates two responsibilities.

Definition Layer:

- owns what should be tested;
- belongs primarily to Matrix Editor;
- manages test items, groups, step mapping, sequence, condition, requirement, method, section, templates, and source imports;
- may validate sequence gaps, duplicates, conflicts, and lifecycle reasonableness.

Execution Layer:

- owns what is happening now;
- belongs primarily to Project Workbench;
- manages step status, test data, images, evidence, remarks, pass/fail, actual completion time, actual cost, risk, and report sync status.

Workbench should not directly modify Matrix definition by default. It should request a Matrix change and route to Matrix Editor when definition changes are needed.

## 4. Project Workbench Direction

Project Workbench should become:

```text
Live Project Runtime Console
```

The first screen should answer:

- What is the current project progress?
- What Matrix version is the execution authority?
- Which groups and steps are active, blocked, failed, missing evidence, or not started?
- Which step needs attention now?
- Which outputs are current, stale, missing, or waiting for setup?

The Matrix overview should remain the main visual surface for execution awareness. Setup-related areas should not dominate the Workbench once Matrix authority exists.

## 5. Setup Manager Demotion

The following areas remain important but should be demoted to status entries, folded workspaces, or a Setup Manager surface:

- Project folder creation;
- source materials;
- evidence placement;
- approval package;
- fee evaluation;
- read-only lookup summaries.

These areas support the project. They should not compete with the Matrix runtime view as the main Workbench surface.

## 6. Matrix Editor Direction

Matrix Editor should become:

```text
Test Plan Definition Studio
```

It is responsible for:

- adding or removing test items;
- adding groups;
- editing step mapping and sequence;
- editing condition, requirement, method, and section;
- importing Matrix templates, historical projects, and specification-derived candidates;
- showing group step sequence preview;
- validating sequence and lifecycle reasonableness.

It is not responsible for:

- test data entry;
- image upload;
- report sync;
- runtime status maintenance;
- actual test execution;
- evidence management;
- actual completion time;
- test lifecycle advancement.

## 7. Interactive Step System

Matrix cells must not remain only strings such as:

```text
2,5,7
4(b)
3(a)
```

They should resolve into structured interactive step tokens, eventually backed by Step-centric records:

```text
Project -> TestGroup -> StepInstance
```

Each step token should be able to carry:

- sequence and variant;
- status;
- lifecycle state;
- data;
- images;
- evidence;
- comments;
- report binding;
- click behavior into a step workspace.

The next backend foundation should be minimal and task-controlled. Do not add full execution data entry until the step model and read model are approved.

## 8. Matrix Cell Parsing Direction

Step token parsing should treat separators as separators, not data:

- spaces;
- comma;
- slash;
- dash when used as a separator.

The meaningful token is the step number and optional variant, for example:

```json
[
  { "step": 2, "variant": null },
  { "step": 4, "variant": "b" }
]
```

Parsing, validation, and persistence must avoid string-only Matrix cells as the long-term authority.

## 9. Real Laboratory Workflow Rule

Real lab work may start before all setup and approval package work is complete.

Future readiness levels may allow:

```text
Draft -> Test Ready -> Authority Ready -> Report Ready -> Closed
```

`Test Ready` may occur before `Authority Ready` or `Approval Package Ready`.

Setup must not block real test execution when the Matrix/test execution path is sufficiently ready.

## 10. Derived Output Rule

Reports, test records, fee files, and approval packages are derived outputs.

They must not become the primary data source. When Matrix or Step data changes, downstream outputs should become stale or require regeneration/import, not silently become authoritative.

## 11. Lessons From TestFlowManager

Keep the lessons:

- high-density Matrix overview fits real lab work;
- group and step visibility matters;
- engineers need a fast project testing map;
- record, fee, and report outputs must be driven by structured test planning and execution data.

Reject the legacy architecture:

- do not migrate old code;
- do not let UI own business logic;
- do not couple directly to Word/Excel from UI or application logic;
- do not make Excel the source of truth;
- do not treat Matrix cells as plain strings;
- do not create a toolbox of disconnected buttons.

## 12. Next Controlled Sequence

Recommended next tasks:

1. `TASK_195_PROJECT_WORKBENCH_RUNTIME_CONSOLE_INFORMATION_ARCHITECTURE`
2. `TASK_196_STEP_CENTRIC_DOMAIN_FOUNDATION`
3. `TASK_197_INTERACTIVE_STEP_TOKEN_READ_MODEL`
4. `TASK_198_WORKBENCH_RUNTIME_CONSOLE_UI_BASELINE`
5. `TASK_199_MATRIX_EDITOR_DEFINITION_STUDIO_INFORMATION_ARCHITECTURE`

This sequence is guidance only. Each task requires its own plan, approval, implementation, validation, and board update.
