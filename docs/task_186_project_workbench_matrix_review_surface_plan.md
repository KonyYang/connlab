# TASK_186 Plan - Project Workbench Matrix Review Surface

## 1. Current Phase And Gate

- Current phase: `Phase 11 - Project planning data foundation before downstream document automation`.
- Current active task before creation: `TASK_185` complete.
- This plan is proposal-only. Implementation must wait for explicit approval: `批准执行 TASK_186`.
- Why allowed now: TASK_184 defined the Matrix-first Workbench direction and TASK_185 created the route/model/layout boundary needed for the next UI slice.

## 2. Goal

Make Project Workbench show the active ProjectTestPlanDraft as the first meaningful work surface.

The operator should immediately see what testing is required without leaving the Workbench:

- Matrix group sequence;
- test steps and source traceability;
- duration assumptions when available;
- missing-data warnings;
- whether a Project has no active test-plan draft yet.

This is display and review only. It does not edit Matrix data, write Office files, or generate downstream documents.

## 3. Task Understanding

Input data:

- current `project_id` from the Workbench route;
- existing ProjectTestPlanDraft list/detail backend responses;
- draft snapshot content created from previous Matrix preview/persistence tasks.

Output data:

- typed frontend state representing active draft loading/success/empty/error;
- Workbench Matrix review panel rendered from existing draft data;
- no database mutation and no file output.

Involved modules:

- frontend API client;
- `features/project-workbench` model hook and layout;
- Workbench styles;
- frontend static guard tests.

Not allowed:

- no new backend endpoint;
- no parser/persistence changes;
- no Office write behavior;
- no Section 2/test record/fee/approval-package autofill;
- no report generation or AI review.

## 4. Current Context

TASK_185 left the Workbench in a healthier shape:

- route page is thin;
- `useProjectWorkbenchModel` owns Workbench state/API orchestration;
- `ProjectWorkbenchLayout` composes status, folder, lookup, approval package, and evidence panels.

The remaining gap from TASK_184 is that Matrix/TestPlan is still not the first visible work surface. Current layout starts with boundary/status and operational panels, while the real operator question is: "What testing is required for this project?"

## 5. Data Shape Design

Add frontend DTOs in `frontend/src/api/client.ts` based on the existing backend response contracts.

Planned frontend types:

```ts
export type ProjectTestPlanDraftSummary = {
  draft_id: string;
  project_id: string;
  status: string;
  source_document_path: string;
  created_at?: string | null;
  superseded_at?: string | null;
};

export type ProjectTestPlanDraftDetail = ProjectTestPlanDraftSummary & {
  snapshot: ProjectTestPlanSnapshot;
};

export type ProjectTestPlanSnapshot = {
  groups: ProjectTestPlanGroup[];
  warnings: string[];
};

export type ProjectTestPlanGroup = {
  group_label: string;
  sequence: number;
  steps: ProjectTestPlanStep[];
};

export type ProjectTestPlanStep = {
  sequence: number;
  test_item: string;
  method?: string | null;
  condition?: string | null;
  reference?: string | null;
  judgement?: string | null;
  duration_days?: number | null;
  source_trace?: string | null;
};
```

The exact field names must be verified against backend Pydantic responses before implementation. If the backend uses different keys, the frontend types should match existing API truth rather than introducing adapters with guessed names.

## 6. API And Function Signatures

Add API client functions only if not already present:

```ts
export function listProjectTestPlanDrafts(projectId: string): Promise<ProjectTestPlanDraftSummary[]>;

export function getProjectTestPlanDraft(
  projectId: string,
  draftId: string
): Promise<ProjectTestPlanDraftDetail>;
```

Expected backend paths must be verified from `backend/api` before implementation. The implementation should use existing endpoints from TASK_175 and must not add new backend routes.

Extend model state:

```ts
type MatrixReviewState = {
  activeDraft: ProjectTestPlanDraftDetail | null;
  loading: boolean;
  error: string | null;
};
```

Expose from `ProjectWorkbenchModel`:

```ts
matrixReview: MatrixReviewState;
onReloadMatrixReview: () => Promise<void>;
```

## 7. UI Composition

Add:

`frontend/src/features/project-workbench/ProjectWorkbenchMatrixReviewPanel.tsx`

Responsibilities:

- show empty state when no active draft exists;
- show source document and draft status;
- render group rows with compact step details;
- show warnings as business-readable notes;
- keep display dense but scannable for a 14-inch workstation screen.

Placement:

- inside `ProjectWorkbenchLayout`;
- after summary/status;
- before folder/evidence/approval package downstream actions.

Design stance:

- product register, restrained palette;
- no spreadsheet clone;
- no nested cards;
- semantic badges paired with text;
- no decorative gradients, glass, or thick side stripes.

## 8. File-Level Changes

Planned changes after approval:

- `frontend/src/api/client.ts`
  - add existing test-plan draft DTOs/functions.
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
  - load active draft after project load or in the same Workbench load flow.
  - expose reload callback and clear business-readable error.
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - compose Matrix review panel before downstream document stages.
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixReviewPanel.tsx`
  - new display component.
- `frontend/src/workbench.css`
  - add scoped Workbench Matrix styles.
- `tests/unit/test_frontend_shell_files.py`
  - assert Matrix panel stays in feature boundary and route page remains thin.

## 9. Risk Control

- Risk: guessed frontend DTO field names drift from backend response.
  - Control: inspect backend route schemas before implementation and type to actual API output.
- Risk: Matrix panel becomes a broad editable spreadsheet.
  - Control: display-only scope; no editing callbacks or persistence actions.
- Risk: downstream panels change accidentally.
  - Control: keep folder/evidence/approval package props and behavior unchanged.
- Risk: no active draft in local test data.
  - Control: empty state is a first-class acceptance path.

## 10. Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix"
```

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

Manual smoke after implementation:

- Workbench opens for a Project with no draft and shows a non-blocking empty state.
- Workbench opens for a Project with an active draft and shows Matrix groups/steps.
- Existing folder/evidence/approval package actions remain visible and usable.

## 11. Review Checklist

- Scope is current TASK only.
- No backend route or persistence change.
- No Office direct access.
- No frontend filesystem operations.
- No Matrix editing or document generation.
- Route page remains a composition shell.
- UI copy is operational and business-readable.

## 12. Stop Point

Stop after this plan until the user explicitly approves implementation with `批准执行 TASK_186`.
