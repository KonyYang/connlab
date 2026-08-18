# TASK_313A Project Workbench Lifecycle Mode Redesign Plan

Status: Complete.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: none; `TASK_313A_PROJECT_WORKBENCH_LIFECYCLE_MODE_REDESIGN` complete.

Allowed reason: The user approved reprioritizing the Workbench lifecycle-mode redesign before continuing TASK_313. `docs/task_board.md` defers TASK_313 until package execution is explicitly reprioritized after the lifecycle-mode Workbench is in place.

## Step 1: Task Understanding

### Goal

Convert Project Workbench from a single stacked page into a lifecycle-mode driven project management console.

The page must show the current project stage and next action first, then display only the work surfaces that belong to that stage.

### Inputs

Existing frontend state from `useProjectWorkbenchModel` and `ProjectRuntimeConsoleModel`, including:

- `project`
- `latestLtr`
- `matrixAuthorityDraft`
- `matrixCandidateDraft`
- `matrixDraft`
- `folderReady`
- `folderResources`
- `section2SyncPreview`
- `packagePreview`
- `packagePreviewError`
- `versionStatus`
- `runtimeProjectionSnapshot`

Existing route callbacks:

- `onBack`
- `onOpenMatrixEditor`
- `onOpenFeeEvaluation`

### Outputs

Frontend-only UI/read-model outputs:

- lifecycle mode,
- stage label,
- next action model,
- mode tabs or segmented control labels,
- mode-specific rendered Workbench sections.

No backend output is introduced.

### Modules

Primary modules:

- `frontend/src/features/project-workbench`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`

### Not Allowed

- No backend/API/domain/storage changes.
- No package execution endpoint or execute action.
- No StepInstance, TestResult, evidence/image persistence, report, AI, permissions, or multi-user scope.
- No TASK_314 autosave/draft lifecycle.
- No TASK_315 Matrix/Fee rebase.
- No old approval-package execute flow.

## Step 2: Design

### Lifecycle Data Structure

Add `projectWorkbenchLifecycleSelectors.ts`.

Suggested types:

```ts
export type WorkbenchLifecycleMode =
  | "temporary_planning"
  | "registered_setup"
  | "package_preparation"
  | "execution_console";

export type WorkbenchLifecycleTab = {
  mode: WorkbenchLifecycleMode;
  label: string;
  disabled?: boolean;
  reason?: string;
};

export type WorkbenchNextAction = {
  title: string;
  reason: string;
  tone: "ready" | "blocked" | "warning" | "neutral";
  actionLabel?: string;
  actionTarget?: "matrix" | "fee" | "package" | "settings" | null;
};

export type WorkbenchLifecycleViewModel = {
  mode: WorkbenchLifecycleMode;
  stageLabel: string;
  stageSummary: string;
  nextAction: WorkbenchNextAction;
  tabs: WorkbenchLifecycleTab[];
};
```

Selector input should stay narrow and serializable:

```ts
export type WorkbenchLifecycleInput = {
  hasLtr: boolean;
  hasActiveMatrix: boolean;
  hasCandidateMatrix: boolean;
  folderReady: boolean;
  packageStatus: "ready" | "blocked" | null;
  packageBlockers: string[];
  section2Status: string | null;
  hasPackagePreviewError: boolean;
};
```

### Mode Derivation

Initial V1 rules:

1. If no LTR/DL exists: `temporary_planning`.
2. If LTR exists and no active Matrix authority exists: `registered_setup`.
3. If active Matrix authority exists and package preview has blockers or warnings: default `package_preparation`.
4. If active Matrix authority exists and package preview is clear: allow `package_preparation` and `execution_console`; V1 may default to `package_preparation` until execution persistence exists.

The user can switch between Package and Execution when both are available. Temporary and registered setup modes should keep unavailable modes disabled with a visible reason.

### Component Structure

Refactor `ProjectWorkbenchLayout.tsx` into clearer sections without changing route ownership:

```text
ProjectWorkbenchLayout
  WorkbenchStageBanner
  WorkbenchModeTabs
  TemporaryPlanningMode
  RegisteredSetupMode
  PackagePreparationMode
  ExecutionConsoleMode
```

V1 can keep these components in `ProjectWorkbenchLayout.tsx` if file size remains reasonable. If it becomes too large, split into:

- `ProjectWorkbenchLifecycleBanner.tsx`
- `ProjectWorkbenchLifecycleModes.tsx`

### Mode Content

#### Temporary Planning

Show:

- project identity,
- Matrix planning entry,
- Fee Evaluation entry,
- message that formal package tools become available after DL registration.

Hide:

- project folder creation,
- Section 2 sync,
- package preview,
- Submitted Material,
- Step Workspace as primary content.

#### Registered Setup

Show:

- Matrix authority setup message,
- Matrix Editor action,
- concise explanation that Test Record, Fee, Section 2, and package require active Matrix authority.

Hide:

- package execution,
- Step Workspace as primary content,
- future evidence/image/test data controls.

#### Package Preparation

Show:

- readiness checklist style summary,
- `ProjectFolderCreationPanel`,
- `ProjectSection2SyncPanel`,
- `ProjectPackagePreviewPanel`,
- compact `FeeEvaluationStatusSummary`.

Keep:

- Matrix Editor link as secondary action.

Do not show:

- `Execute package` in TASK_313A.

#### Execution Console

Show:

- `ProjectWorkbenchMatrixProjectionPanel`,
- right-side Step Workspace,
- compact Fee context if still useful.

Hide or clearly disable:

- future data/image/evidence controls that are not implemented.

### Copy Cleanup

Replace development wording:

- `Pending result judgement placeholder (read-only in this task).`
- `Execution evidence, charts, and attachments stay read-only placeholders in this task.`
- `Future output package`
- any visible `TASK_313`

Use operator wording:

- `Result judgement is not available yet.`
- `Execution data and evidence will be managed after step records are implemented.`
- `Package execution is pending approval.`

### Styling

Use existing `workbench.css` with restrained additions:

- stage banner,
- mode tabs,
- lifecycle checklist rows,
- mode content grid.

Avoid nested cards. Avoid making every mode a large framed card.

## File-Level Plan

### Add

- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`

### Modify

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
- `frontend/src/features/project-workbench/ProjectPackagePreviewPanel.tsx`
- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts` only if a narrow lifecycle input helper is needed
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`

### Documentation Already Prepared

- `tasks/TASK_313A_PROJECT_WORKBENCH_LIFECYCLE_MODE_REDESIGN.md`
- `docs/task_313a_project_workbench_lifecycle_mode_redesign_plan.md`
- `docs/task_board.md`
- `docs/task_plan_index.md`
- `docs/task_306_313_project_package_execution_series_plan.md`

## API And Dependency Design

No new API.

Frontend dependency remains:

```text
ProjectWorkbenchPage -> useProjectWorkbenchModel -> ProjectWorkbenchLayout
ProjectWorkbenchLayout -> lifecycle selectors + feature components
feature components -> typed API DTOs only through existing hooks/model
```

No component may call `fetch()` directly.

## Testing Plan

### Selector Tests

Cover:

- no LTR -> temporary planning,
- LTR without active Matrix -> registered setup,
- active Matrix with package blockers -> package preparation,
- active Matrix with ready package -> package and execution tabs available,
- next-action messages for missing Matrix, package blockers, and ready package state.

### Component Tests

Cover:

- formal package surfaces hidden in temporary planning,
- Step Workspace not primary in registered setup,
- package mode shows folder/Section 2/package preview,
- execution mode shows Matrix and Step Workspace,
- no `TASK_313`, `placeholder`, or `read-only in this task` text appears.

### Static Guards

Extend `tests/unit/test_frontend_shell_files.py` to check:

- no backend files changed for TASK_313A,
- Workbench lifecycle selector exists,
- old development copy is absent,
- no package execute API/client is introduced by TASK_313A.

### Commands

```powershell
cd frontend
npm test -- --run projectWorkbenchLifecycleSelectors ProjectWorkbench --watch=false
npm test -- --run ProjectWorkbenchMatrixProjectionPanel ProjectPackagePreview --watch=false
npm run build
```

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "project_workbench or task313a"
git diff --name-only -- backend
git diff --check
```

### Browser Smoke

Use the existing local route:

```text
http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f
```

Check:

- stage and next action appear first,
- package and execution are separated,
- package blockers are not mixed into the execution Matrix surface,
- Step Workspace is only primary in execution mode,
- no package execute button exists in TASK_313A.

## Risks And Controls

- Risk: hiding always-visible Matrix table may feel like a regression. Control: keep `Execution` mode one click away whenever active Matrix exists.
- Risk: package preview may become less discoverable. Control: default to Package mode when package blockers exist.
- Risk: current tests assume all surfaces render together. Control: update tests to match lifecycle mode behavior rather than preserving the broken layout.
- Risk: selector may overstate business truth. Control: selector is display-only and uses existing API state; backend remains authoritative.

## Stop Point

Stop after TASK_313A implementation, validation, and task board update. Do not implement package execute, background Matrix/Fee drafts, Matrix/Fee rebase, StepInstance, evidence/image management, report generation, AI, permissions, or multi-user behavior.

Implementation must not begin until the user explicitly approves this plan.
