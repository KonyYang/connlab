# TASK_184 Plan - Project Workbench Matrix-First Redesign Baseline

## 1. Current Phase And Gate

- Current phase: `Phase 11 - Project planning data foundation before downstream document automation`.
- Current active task before creation: `TASK_183_PROJECT_WORKBENCH_APPROVAL_PACKAGE_UI_WIRING` complete.
- This task is planning-only. It must not write Project Workbench implementation code.
- `$impeccable` product context applies because this is frontend/workflow UX planning.

## 2. Model Fit

`gpt-5.3-codex` is suitable for this task.

Reason:

- The task is documentation, architecture baseline, and task decomposition.
- It depends on reading existing frontend/backend boundaries and user workflow input.
- It does not require complex Office parsing, standards retrieval, report generation, or broad backend redesign.

## 3. Business Direction

Project Workbench should become Matrix-first because the first real operator question after New Project completion is:

```text
What tests are required, what steps are in each group, what information is missing, and can approval materials be prepared?
```

The first visible surface should therefore show:

- Matrix test groups and steps;
- approval-package readiness;
- available source and generated files;
- current project blocker or stage;
- stale/downstream status when a test plan changes.

## 4. Important Constraint

Matrix must not become the system center.

The previous failed pattern was to place all project data into one Matrix table and then generate test records, data sheets, reports, plans, and other outputs from that overloaded table. That makes maintenance and extension harder as features grow.

The correct boundary is:

```text
Project remains the system center.
ProjectTestPlan is the structured intermediate object.
Matrix is the primary operator view of ProjectTestPlan.
Generated documents and approval packages are downstream outputs.
```

## 5. Current Code Gap

Current Workbench entry:

- `frontend/src/pages/ProjectWorkbenchPage.tsx`

Current issues:

- It loads Project, LTR, Settings resources, evidence state, approval package state, and page messages in one route page.
- Evidence placement is still inline JSX in the page.
- Approval package UI exists, but it asks operators for manual paths that should eventually come from previous-stage outputs.
- Project lookup mixes current project summary and historical lookup in the same panel.
- Matrix/TestPlan is not visible as the first work surface, even though backend capability already exists from TASK_174/TASK_175.

Current useful pieces:

- `ProjectFolderCreationPanel` already belongs under `features/project-workbench`.
- `ApprovalPackagePanel` can be moved under `features/project-workbench`.
- `ProjectLookupPanel` can later become a reference lookup stage.
- Evidence placement can be extracted into a `SourceArchiveStage`.

## 6. Target Workbench Shape

Recommended structure:

```text
frontend/src/features/project-workbench/
  useProjectWorkbenchModel.ts
  projectWorkbenchStages.ts
  projectWorkbenchSelectors.ts
  ProjectWorkbenchLayout.tsx
  ProjectWorkbenchHeader.tsx
  ProjectWorkbenchStageRail.tsx
  ProjectWorkbenchFileRail.tsx
  SourceArchiveStage.tsx
  MatrixReviewStage.tsx
  Section2Stage.tsx
  TestRecordStage.tsx
  FeeEvaluationStage.tsx
  ApprovalPackageStage.tsx
  ReferenceLookupStage.tsx
```

Route page target:

```tsx
const model = useProjectWorkbenchModel(projectId);
return <ProjectWorkbenchLayout model={model} onBack={onBack} />;
```

The page should own route identity and fatal loading/error only. Workflow state and derived blockers should move into the feature model and selectors.

## 7. Stage Model

### Source Archive

Purpose:

- Ensure project folder exists.
- Place source email, attachments, specifications, photos, and customer documents into the project folder.

Inputs:

- Project and latest LTR.
- Settings resources.
- Intake package assets and evidence placement plan.

Outputs:

- Project folder record.
- Archived source files.
- Missing source warnings.

### Matrix Review

Purpose:

- Show test groups and test steps as the primary work surface.
- Let operator confirm or revise test requirement understanding.

Inputs:

- Product specification Matrix preview.
- ProjectTestPlanDraft.
- Source document traceability.

Outputs:

- Active/superseded ProjectTestPlanDraft.
- Duration and missing-detail warnings.

### Duration And Section 2

Purpose:

- Calculate estimated completion date and Section 2 preview.
- Write Section 2 back to the original request form after confirmation.

Inputs:

- Active ProjectTestPlanDraft.
- Duration buffer settings and operator adjustments.
- Application form path.

Outputs:

- Section 2 preview.
- Section 2 write-back result and completed application form path.

### Test Record

Purpose:

- Generate or refresh test record template from active ProjectTestPlanDraft.

Inputs:

- Active ProjectTestPlanDraft.
- Test record template.
- Generated output target.

Outputs:

- Test record file path.
- Current/stale/missing status.

### Fee Evaluation

Purpose:

- Generate or refresh fee evaluation file.

Inputs:

- Active ProjectTestPlanDraft.
- Fee template.
- Pricing or fee-line assumptions where available.

Outputs:

- Fee evaluation file path.
- Missing-price warnings.
- Current/stale/missing status.

### Approval Package

Purpose:

- Assemble supervisor-review package.

Inputs:

- Completed application form path.
- Test record file path.
- Fee evaluation file path.
- Required source evidence.
- Project folder path.

Outputs:

- Approval package placement preview/result.
- Blockers and permanent public-drive placement status.

### Reference Lookup

Purpose:

- Support similar project and historical document lookup.

Inputs:

- Search query, Project data, future knowledge/reference APIs.

Outputs:

- Similar projects, historical references, future standards/report hints.

This is not the main workflow stage for TASK_184 implementation planning.

## 8. Auto-Carry Rules

Normal operator path should not require manually typing known file paths.

Auto-carry targets:

- `project_folder_path` from latest project folder record;
- source email and attachments from intake/file asset records;
- specification/source documents from evidence classification;
- completed application form from Section 2 write-back result;
- test record file from test record generation result;
- fee file from fee generation result;
- approval-package evidence list from source archive and generated document outputs.

Manual path inputs should remain available only as correction or transition behavior until generated document metadata is persisted end to end.

## 9. Version And Stale Rules

ProjectTestPlanDraft versioning should drive downstream freshness.

Freshness states:

- `current`: output generated from the active confirmed draft;
- `stale`: output generated from a superseded or changed draft;
- `missing`: output has not been created;
- `manual`: output path was provided manually and is not traceable to a generation result;
- `failed`: output generation or placement failed.

When Matrix groups/steps change, mark these outputs stale:

- Section 2 write-back;
- test record file;
- fee evaluation file;
- approval package preview/result.

## 10. Implementation Split

Recommended next tasks:

1. `TASK_185_PROJECT_WORKBENCH_STATE_MODEL_AND_LAYOUT_REFACTOR`
   - Extract feature model/hook and stage layout.
   - Move evidence and approval package UI into project-workbench feature boundary.
   - Preserve current behavior.

2. `TASK_186_PROJECT_WORKBENCH_MATRIX_REVIEW_SURFACE`
   - Add Matrix-first read/review UI from ProjectTestPlanDraft.
   - Show groups, steps, source traceability, duration assumptions, and warnings.

3. `TASK_187_PROJECT_WORKBENCH_DOCUMENT_PIPELINE_AUTOFILL`
   - Connect Section 2, record/fee generation, and approval package inputs.
   - Reduce manual path entry.

4. `TASK_188_PROJECT_WORKBENCH_VERSION_AND_STALE_STATUS`
   - Add or expose generated-document metadata and stale-state display.

Deferred:

- standards lookup;
- public-drive reference document search;
- similar historical report retrieval;
- test execution status table;
- report generation and incremental report update.

## 11. Validation

Planning-only validation:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

Frontend build is not required unless implementation files change.

## 12. Acceptance

TASK_184 is complete when:

- task file exists;
- this plan exists;
- task board registers TASK_184 as the next controlled task;
- guard tests accept the updated board state;
- no Project Workbench implementation code is changed.
