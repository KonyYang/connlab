# TASK_184 Project Workbench Matrix-First Redesign Baseline

> Status: complete
> Created: 2026-05-12
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 0. Execution Gate

- Current phase at creation time: `Phase 11`.
- Current active task in board at creation time: `TASK_183_PROJECT_WORKBENCH_APPROVAL_PACKAGE_UI_WIRING` complete.
- Why this task is allowed now: TASK_174 through TASK_183 added backend and minimal frontend capabilities around Matrix preview, ProjectTestPlanDraft, Section 2, test record, fee evaluation, approval package, and folder placement. The current Project Workbench UI now exposes isolated operations but does not match the real operator workflow.
- Implementation gate: this task is a baseline and redesign-plan task. Do not write Project Workbench implementation code until the user explicitly approves an implementation follow-up task.

---

## 1. Model Fit

`gpt-5.3-codex` is suitable for this planning and refactor-baseline task.

Reason:

- The task requires codebase reading, frontend boundary analysis, business workflow mapping, and task decomposition.
- It does not require complex Office reverse engineering, specification parsing upgrades, or knowledge-base retrieval.
- The expected output is project documentation and a controlled follow-up task sequence.

---

## 2. Purpose

Define the next Project Workbench direction as a Matrix-first project management work surface while avoiding the failed pattern of making Matrix a giant all-purpose table.

The goal is to make Project Workbench reflect the real lab flow after New Project completion:

```text
Create project folder -> archive email/specification/source files -> review Matrix -> calculate duration -> write Section 2 -> generate test record -> generate fee evaluation -> prepare approval package
```

---

## 3. Business Findings From User Input

- First screen priority:
  - visible test groups and steps from the Matrix;
  - approval package readiness;
  - available source/generated files;
  - current blocker or current stage.
- Paths that must be automatically carried forward:
  - source email and attachments;
  - project folder path;
  - completed application form;
  - generated test record;
  - generated fee evaluation file.
- Both evidence workflows are required:
  - ordinary source archive: all source material is copied into the project folder for traceability;
  - approval package: supervisor-review package files are placed and retained on the public drive.
- The Workbench must support change and rollback:
  - if test groups or steps change, Matrix/TestPlan data should be versioned;
  - downstream Section 2, test record, fee evaluation, and approval package outputs should be marked stale/outdated and regenerated from the newer plan.
- Long-term context:
  - standards lookup, historical project retrieval, report wording reuse, and knowledge search are real business needs, but not the immediate implementation scope of this task.

---

## 4. Current Code Reality

Current main frontend entry:

- `frontend/src/pages/ProjectWorkbenchPage.tsx`

Current related pieces:

- `frontend/src/features/project-workbench/ProjectFolderCreationPanel.tsx`
- `frontend/src/components/workflow/ApprovalPackagePanel.tsx`
- `frontend/src/components/project/ProjectLookupPanel.tsx`
- evidence placement JSX still lives inside `ProjectWorkbenchPage.tsx`

Observed problems:

- The page owns too much state and workflow orchestration.
- The UI is arranged by backend capability panels instead of the operator's project workflow.
- Matrix/TestPlan is not yet the first visible work surface.
- Approval package inputs still depend on manual path entry rather than previous-stage outputs.
- Ordinary evidence archive and approval package placement are both present but not clearly separated by business purpose.
- Project lookup mixes current-project summaries with historical search, making it unclear whether it is a main workflow stage or reference tool.

---

## 5. Target Workbench Concept

Project Workbench should become:

```text
Project-centered, Matrix-first, stage-driven project management surface.
```

System center remains `Project`, not Matrix.

Matrix is the operator's first work view because it answers what testing is required. Internally, the durable structured object should remain `ProjectTestPlan` / `ProjectTestPlanDraft`.

Target relationship:

```text
Project
  -> Source Materials
  -> ProjectTestPlan
       -> Matrix View
       -> Duration / Section 2 Data
       -> Test Record Dataset
       -> Fee Dataset
       -> Approval Package Inputs
  -> Generated Documents
  -> Evidence Archive
  -> Version History
```

---

## 6. Target Information Architecture

Recommended Project Workbench layout:

```text
ProjectWorkbenchPage
  -> useProjectWorkbenchModel(projectId)
  -> ProjectWorkbenchLayout
       -> ProjectWorkbenchHeader
       -> ProjectWorkbenchStageRail
       -> ProjectWorkbenchPrimaryStage
       -> ProjectWorkbenchFileRail
```

Recommended stages:

1. `Source Archive`
   - Create or read project folder.
   - Place source email, attachments, specifications, photos, and customer material.
   - Show archived source files and missing required material.

2. `Matrix Review`
   - Show Matrix groups and steps as the first meaningful work surface.
   - Confirm test groups, steps, source clauses, methods, references, conditions, judgement criteria, and duration assumptions.
   - Create or supersede a `ProjectTestPlanDraft` when the Matrix changes.

3. `Duration & Section 2`
   - Show duration calculation and buffers.
   - Preview Section 2 values.
   - Write Section 2 back to the application form after confirmation.

4. `Test Record`
   - Generate or refresh the test record template from the current confirmed draft.
   - Show whether the generated document is current or stale.

5. `Fee Evaluation`
   - Generate or refresh fee evaluation output.
   - Show missing price warnings without blocking unrelated Matrix review.

6. `Approval Package`
   - Assemble completed application form, test record, fee evaluation, and required source material.
   - Default inputs come from previous stage outputs.
   - Manual path entry is a correction/advanced mode, not the normal path.

7. `Reference Lookup`
   - Historical project and similar report lookup.
   - Future standards/document search belongs here or in a dedicated reference feature.
   - This is reference support, not the main project stage.

---

## 7. Boundaries

Matrix view must not become a giant spreadsheet that owns all later documents.

Allowed Matrix responsibilities:

- test group and sequence display;
- source clause traceability;
- test method/condition/reference/judgement visibility;
- duration assumptions;
- operator confirmation of test-plan content;
- current/stale status for downstream outputs.

Not allowed inside Matrix:

- editing report narrative as free-form report content;
- storing all test record measurements;
- storing fee workbook layout details;
- storing approval-package placement paths as table columns;
- becoming the only state source for project lifecycle.

---

## 8. Auto-Carry Data Rules

Normal Workbench operation should avoid manual path entry for known outputs.

Expected carry-forward sources:

- project folder path: latest `ProjectFolderRecord`;
- source email and attachments: intake package/file asset records and evidence archive plan;
- specification documents: source material/evidence classifications;
- completed application form: Section 2 write-back result;
- test record file: test record generation result;
- fee evaluation file: fee generation result;
- approval package evidence paths: source archive records plus generated document outputs.

Manual path fields should be treated as correction inputs until the system has complete persistence for generated documents.

---

## 9. Version And Stale-State Rules

When a test plan changes, create a new `ProjectTestPlanDraft` version instead of mutating downstream assumptions silently.

Downstream files should carry freshness state against the active draft:

- `current`: generated from the active confirmed draft;
- `stale`: generated from a superseded or changed draft;
- `missing`: not generated yet;
- `manual`: provided manually and not traceable to a generation result;
- `failed`: generation or placement failed and needs operator action.

Changing Matrix groups or steps should mark these outputs stale:

- Section 2 preview/write-back;
- test record document;
- fee evaluation file;
- approval package preview/result.

---

## 10. Proposed Follow-Up Tasks

Recommended follow-up sequence:

1. `TASK_185_PROJECT_WORKBENCH_STATE_MODEL_AND_LAYOUT_REFACTOR`
   - Extract `useProjectWorkbenchModel`.
   - Move approval package and evidence panels into `features/project-workbench`.
   - Introduce stage rail/layout.
   - Preserve existing behavior.

2. `TASK_186_PROJECT_WORKBENCH_MATRIX_REVIEW_SURFACE`
   - Add Matrix-first display surface from `ProjectTestPlanDraft`.
   - Show test groups, steps, duration, source traceability, and missing data warnings.
   - No Office write behavior.

3. `TASK_187_PROJECT_WORKBENCH_DOCUMENT_PIPELINE_AUTOFILL`
   - Carry generated file outputs into Section 2, record/fee, and approval package stages.
   - Reduce manual path entry to correction mode.

4. `TASK_188_PROJECT_WORKBENCH_VERSION_AND_STALE_STATUS`
   - Persist or expose enough generated-document metadata to show current/stale/missing/manual status.
   - Mark downstream outputs stale when the active test plan changes.

Deferred long-term tasks:

- standards lookup against public-drive standards;
- historical similar-project retrieval;
- historical report wording/reference search;
- test execution status table;
- report generation and incremental report update.

---

## 11. Deliverables For This Task

In scope:

- Create this task file.
- Create baseline plan document:
  - `docs/task_184_project_workbench_matrix_first_redesign_baseline_plan.md`
- Update `docs/task_board.md` to register TASK_184.
- Update guard tests only if required to keep board validation aligned.

Out of scope:

- No Project Workbench implementation changes.
- No new backend endpoints.
- No Office file generation changes.
- No Matrix parser changes.
- No report generation.
- No standards or historical report search.

---

## 12. Validation Plan

Documentation validation:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

No frontend build is required for this planning-only task unless implementation files are changed.

---

## 13. Acceptance Criteria

- TASK_184 exists and captures Matrix-first Workbench direction.
- Plan document explains real user workflow, current code gap, target architecture, data flow, version/stale rules, and follow-up task sequence.
- Current Workbench refactor direction preserves `Project` as system center and `ProjectTestPlan` as structured intermediate object.
- Matrix is defined as the primary work view, not the all-purpose data model.
- `docs/task_board.md` is updated without starting implementation work.

---

## 14. Completion Notes

Completed on 2026-05-12.

Delivered:

- Task definition file for Matrix-first Workbench baseline created and finalized.
- Baseline plan document created:
  - `docs/task_184_project_workbench_matrix_first_redesign_baseline_plan.md`
- Task board updated to register TASK_184 as completed baseline work.
- Guard tests updated for TASK_184 board state compatibility.

Validated:

- `py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q`
