# TASK_270_RECORD_STEP_WORKSPACE_PANEL

## Status

Complete.

## Naming Alias

Former label used in prior discussion: `TASK_270_PROJECT_WORKBENCH_RECORD_STEP_WORKSPACE_PROTOTYPE`.

## Current Execution Context

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current product direction: `Matrix-driven Laboratory Execution Phase`
- Current active task for planning: `TASK_270_RECORD_STEP_WORKSPACE_PANEL`
- Allowed reason: `TASK_269_PROJECT_WORKBENCH_MATRIX_PROJECTION_PROTOTYPE` is complete, `docs/task_board.md` had no active implementation task, and this task is the next guideline-aligned frontend slice from `docs/post_phase11_matrix_driven_laboratory_execution_workflow_guideline.md`.

## Source Guideline

Reference: `docs/post_phase11_matrix_driven_laboratory_execution_workflow_guideline.md`

Guideline intent:

```text
Turn clicked matrix token into record-oriented step detail.
```

The guideline requires a right-side panel that shows:

- Group
- Step token
- Test item
- Section
- Method
- Condition
- Requirement / remarks
- Sample quantity
- Record generation status placeholder
- Evidence / data placeholder
- Review placeholder

The panel must stay read-only with respect to Matrix authority.

## Objective

Convert the current TASK_269 inline matrix-token detail into a named, record-oriented Step Workspace panel inside Project Workbench.

The panel should help the operator understand what information will be needed to prepare or fill a Test Record, while clearly showing that this task does not persist execution records or mutate Matrix authority.

## Baseline

TASK_269 added:

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
- `frontend/src/features/project-workbench/projectWorkbenchMatrixProjectionSelectors.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`

Current behavior:

- Project Workbench fetches active Confirmed Matrix Test Record preview.
- The projection table renders group columns and clickable token cells.
- Clicking a token opens an inline right-side `Matrix token detail` panel.
- The detail panel already shows the main authority fields, but it is not yet framed as a record workspace and does not show evidence/data/review placeholders.

## Scope

In scope:

- Frontend-only Project Workbench UI refinement.
- Create a named `RecordStepWorkspacePanel` feature component.
- Replace the inline token detail panel in `ProjectWorkbenchMatrixProjectionPanel`.
- Keep existing TASK_269 projection fetching, row grouping, token identity, and status tones.
- Show record-oriented authority fields from the selected `MatrixProjectionTokenCell`.
- Add read-only placeholders for record draft, evidence/data, and review.
- Add tests and static guards for the new panel wiring.
- Update task and board status after implementation.

Out of scope:

- Backend/API changes.
- Database/schema changes.
- StepInstance persistence.
- LLCR runtime persistence.
- Evidence upload.
- Structured measurement forms.
- Test Record Word generation.
- Report engine.
- AI recommendation or AI review.
- Equipment assignment.
- Permission or multi-user review workflow.
- Matrix authority mutation from Project Workbench.

## Expected File Changes

Create:

- `frontend/src/features/project-workbench/RecordStepWorkspacePanel.tsx`
- `frontend/src/features/project-workbench/RecordStepWorkspacePanel.test.tsx`

Modify:

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- `docs/task_board.md`
- `tasks/TASK_270_RECORD_STEP_WORKSPACE_PANEL.md`

No backend files should change.

## UI / UX Requirements

- The right-side panel title must be `Record Step Workspace`.
- When no token is selected, the panel must show a calm empty state asking the operator to select a matrix token.
- When a token is selected, the panel must show the selected record context:
  - Group
  - Step token
  - Status
  - Sample quantity
  - Test item
  - Section
  - Method
  - Condition
  - Requirement
- The panel must include record-oriented placeholders:
  - `Record draft`
  - `Evidence / data`
  - `Review`
- Placeholder copy must make clear these are not active persistence features in this task.
- The panel must not expose enabled edit, upload, generate, approve, or save actions.
- Copy must stay operational and concise, with no technical backend terminology in user-facing text.

## Data Contract

TASK_270 consumes the existing frontend view model:

```ts
type MatrixProjectionTokenCell = {
  tokenReference: string;
  groupKey: string;
  groupLabel: string;
  rawToken: string;
  sequence: number;
  statusTone: MatrixProjectionStatusTone;
  sampleQuantityExpression: string;
  testItem: string;
  section: string;
  method: string;
  condition: string;
  requirement: string;
};
```

No new API response type is introduced.

## Acceptance Criteria

- Clicking a Matrix projection token opens `Record Step Workspace`.
- The selected panel shows group, step token, item, section, method, condition, requirement, and sample quantity.
- Record draft, evidence/data, and review are visible as inactive placeholders.
- The panel remains read-only and does not mutate Confirmed Matrix authority.
- Existing TASK_269 projection behavior remains intact.
- No backend, API, database, StepInstance, report, AI, fee, equipment, or permission code is introduced.
- Relevant frontend tests and Python static guard tests pass.

## Validation Plan

Required commands after implementation:

```powershell
cd frontend
npm test -- --run RecordStepWorkspacePanel
npm test -- --run ProjectWorkbenchMatrixProjectionPanel
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task270 or task269 or project_workbench"
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
git diff --name-only -- backend
git diff --check
```

Expected backend check:

```text
git diff --name-only -- backend
```

returns no output.

## Risks

- The current right-side panel already shows useful detail; implementation should avoid adding extra fake workflow actions that imply persistence.
- The panel name and copy must not suggest that Test Record generation or evidence upload is already available.
- CSS changes must stay near existing `.runtime-console-matrix-projection-*` rules and avoid disrupting the matrix table layout.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task.

Reason:

- The task is a focused frontend refactor and UI clarity slice.
- It requires reading existing React/TypeScript component boundaries, adding a small component, and preserving established API contracts.
- It does not require deep backend architecture changes, schema migration, Office automation, or broad cross-module refactoring.

Recommended mode:

- `GPT-5.3-codex` with medium reasoning is sufficient.
- High reasoning is optional only if implementation uncovers unexpected coupling in the Workbench projection component.

## Implementation Summary

- Added `RecordStepWorkspacePanel` as a dedicated read-only right-side workspace for selected projection tokens.
- Replaced inline token detail panel in `ProjectWorkbenchMatrixProjectionPanel` with `RecordStepWorkspacePanel`.
- Preserved TASK_269 projection fetch, grouping, token selection, and status tone behavior.
- Added workspace styles and static guard coverage for TASK_270.
- No backend/API/database files were changed.

## Validation Results

```powershell
cd frontend
npm test -- --run RecordStepWorkspacePanel
```

Result: `3 passed`

```powershell
cd frontend
npm test -- --run ProjectWorkbenchMatrixProjectionPanel
```

Result: `5 passed`

```powershell
cd frontend
npm run build
```

Result: passed

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task270 or task269 or project_workbench"
```

Result: `3 passed, 108 deselected`

```powershell
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
```

Result: `1 passed`

```powershell
git diff --name-only -- backend
```

Result: no output

```powershell
git diff --check
```

Result: no whitespace errors; existing CRLF warnings only.
