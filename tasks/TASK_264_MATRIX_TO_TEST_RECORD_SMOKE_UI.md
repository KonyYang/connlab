# TASK_264_MATRIX_TO_TEST_RECORD_SMOKE_UI

## Status

Complete on 2026-05-23. Frontend smoke panel for ConfirmedMatrix -> Test Record preview is implemented and validated.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

none. `TASK_264_MATRIX_TO_TEST_RECORD_SMOKE_UI` is complete; awaiting next approved task.

## Why This Task Is Allowed Now

- `TASK_261_MATRIX_IMPORT_GROUP_SELECTION_COMMIT` is complete.
- `TASK_262_MATRIX_IMPORT_GROUP_SELECTION_VIEW` is complete.
- `TASK_262A_MATRIX_IMPORT_SELECTION_MODE_AND_ACTION_CLARITY` is complete.
- `TASK_262B_MATRIX_IMPORT_PREVIEW_DETECTION_FEEDBACK_HARDENING` is complete.
- `TASK_263_CONFIRMED_MATRIX_TEST_RECORD_PREVIEW_BACKEND` is complete.
- `docs/task_board.md` records `TASK_264_MATRIX_TO_TEST_RECORD_SMOKE_UI` as complete.
- Current execution is now blocked until the next task is explicitly approved.
- `docs/matrix_authority_to_test_record_smoke_flow_plan.md` identifies this task as the next controlled frontend slice after the backend ConfirmedMatrix Test Record preview API.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- The task is a bounded frontend consumer slice.
- It consumes the already implemented TASK_263 read-only API and does not require backend schema, persistence, or domain changes.
- The main risk is UI boundary control: the Test Record Preview must live in the downstream Project Workbench / consumer surface, not inside the Matrix editing grid.
- Higher reasoning is optional if the existing Workbench composition is fragmented, but the implementation should remain deterministic and narrow.

## Required UI Context

This is a frontend/UI task. Implementation must load `$impeccable` context before editing UI code and follow:

- `PRODUCT.md`
- `DESIGN.md`
- `$impeccable` product-register guidance
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`

Design posture:

- ConnLab is a restrained product UI for offline lab engineers.
- The smoke panel must prove workflow correctness, not become a polished Test Record product.
- UI copy must be operational and concise: state, blocker, next action.
- Do not expose future features as active actions.

## Objective

Add a minimal operator-facing smoke UI that proves selected Matrix groups drive a downstream Test Record preview from ConfirmedMatrix authority.

Primary flow:

```text
Import Matrix
-> select groups
-> save/edit ProjectMatrixDraft
-> confirm Matrix authority
-> open Project Workbench downstream preview panel
-> fetch TASK_263 Test Record preview
-> display selected groups, sample quantity, and step rows
```

This task validates the workflow bridge from Matrix authority to Test Record preview. It is not a formal Test Record implementation.

## Scope

Allowed:

- Add typed frontend API client symbols for `GET /api/projects/{project_id}/confirmed-matrix/test-record-preview`.
- Add a minimal Project Workbench or Project Workbench-equivalent downstream consumer panel for Test Record preview smoke validation.
- Render preview status:
  - loading
  - ready
  - empty active ConfirmedMatrix
  - no active ConfirmedMatrix / not ready
  - generic fetch error
- Render group-level preview data:
  - group label/key
  - sample quantity expression
  - step count
  - compact step rows with sequence, raw token, test item, section, method, condition, requirement
- Make it visually clear that the panel consumes ConfirmedMatrix authority and is read-only.
- Add or update focused frontend tests.
- Add or update `tests/unit/test_frontend_shell_files.py` static guard coverage.
- Update `docs/task_board.md` only after implementation completion.

Forbidden:

- No backend changes.
- No API route changes.
- No database/schema changes.
- No Matrix import, parser, SourceMatrix, ProjectMatrixDraft, or ConfirmedMatrix authority changes.
- No formal TestRecord aggregate.
- No StepInstance, execution state, execution result persistence, evidence/image records, structured LLCR sheet, reviewer workflow, runtime execution dashboard, report generation, fee generation, duration estimation, equipment matching, AI review, LAN, permissions, or deployment work.
- No `.docx`, PDF, Excel, or export generation.
- No editing controls in the Test Record preview.
- No pass/fail inputs, measurement fields, evidence upload, image attachment, or judgement controls.
- No embedding Test Record Preview inside the Matrix editing grid.
- No broad Project Workbench redesign or Matrix Editor layout polish.
- No new fee/report/equipment buttons or interactions are introduced by the Test Record preview smoke panel.

## Placement Rules

Preferred placement:

- Project Workbench downstream consumer area, or a Project Workbench-equivalent panel already used for derived outputs.

Do not place:

- Inside the Matrix Editor grid.
- Inside Matrix import selection mode.
- Inside right-side Matrix group/step editing cards.

Reason:

- Matrix Workspace owns authority definition.
- Project Workbench owns downstream derived preview consumption.
- Test Record Preview is derived output, not Matrix authority editing.

## Expected API Client Contract

Add or extend frontend types in `frontend/src/api/client.ts`.

Expected TypeScript shape:

```ts
export type ConfirmedMatrixTestRecordPreviewStatus = "ready" | "empty";

export type ConfirmedMatrixTestRecordPreviewStep = {
  sequence: number;
  raw_token: string;
  test_item: string;
  section: string;
  method: string;
  condition: string;
  requirement: string;
};

export type ConfirmedMatrixTestRecordPreviewGroup = {
  group_key: string;
  group_label: string;
  sample_quantity_expression: string;
  step_count: number;
  steps: ConfirmedMatrixTestRecordPreviewStep[];
};

export type ConfirmedMatrixTestRecordPreview = {
  project_id: string;
  confirmed_matrix_id: string;
  preview_status: ConfirmedMatrixTestRecordPreviewStatus;
  groups: ConfirmedMatrixTestRecordPreviewGroup[];
};
```

Expected function:

```ts
export async function fetchConfirmedMatrixTestRecordPreview(
  projectId: string,
): Promise<ConfirmedMatrixTestRecordPreview>;
```

The function must call:

```text
GET /api/projects/{project_id}/confirmed-matrix/test-record-preview
```

## UI Requirements

The smoke panel must show:

- A compact title such as `Test Record Preview`.
- Confirmed authority context when available:
  - confirmed matrix id or concise authority label
  - preview status
- Empty/not-ready state:
  - business-readable copy when no active ConfirmedMatrix exists
  - no raw backend stack or technical route text
- Ready state:
  - group list in confirmed order
  - sample quantity per group
  - step count per group
  - compact step rows
- Read-only affordance:
  - no inputs
  - no edit/save/confirm controls

Visual rules:

- Use existing ConnLab restrained product UI vocabulary.
- Prefer dense rows/tables over decorative cards.
- Do not create a landing-style hero.
- Do not create a modal as the primary surface.
- Do not use decorative gradients, glassmorphism, or side-stripe cards.
- Keep copy short and operational.

## Candidate Impact Files

Exact files must be confirmed during executable planning.

Likely files:

- `frontend/src/api/client.ts`
- new `frontend/src/features/project-workbench/TestRecordPreviewSmokePanel.tsx`
- `frontend/src/features/project-workbench/*` composition files as needed
- `frontend/src/workbench.css`
- `frontend/src/features/project-workbench/*.test.tsx` or existing relevant frontend test file
- `tests/unit/test_frontend_shell_files.py`

Avoid modifying:

- backend files
- Matrix import parser
- Matrix authority services
- generated document gateways
- fee/report/equipment services

## Acceptance Criteria

- UI consumes TASK_263 API through `frontend/src/api/client.ts`.
- UI does not send Matrix rows, draft payload, selected group keys, SourceMatrix data, or frontend temporary Matrix state to build preview.
- UI displays ready preview groups from ConfirmedMatrix Test Record preview response.
- UI displays group label/key, sample quantity, step count, and compact step rows.
- UI visibly proves selected group propagation using mocked or fixture response data.
- Static/frontend tests verify unselected group labels from mocked data are not rendered.
- Component behavior tests verify mocked selected-only response rendering (`G1` rendered, `G2` absent), `404 -> not_ready`, and `preview_status="empty"` state messaging.
- UI displays clear state when no active ConfirmedMatrix exists.
- UI displays clear state for `preview_status="empty"`.
- The new Test Record Preview smoke panel adds no fee/report/equipment actions and introduces no coupling to fee/report/equipment workflows.
- UI has no execution controls or result-entry inputs.
- UI is not embedded inside Matrix editing grid.
- Existing Matrix Editor import/selection/edit/save/confirm behavior remains unchanged.
- Existing Project Workbench routing remains stable.
- `cd frontend; npm run build` passes.

## Validation

Minimum expected validation after implementation:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task264 or test_record_preview or project_workbench"
```

```powershell
cd frontend; npm test -- --run TestRecordPreviewSmokePanel
```

Expected component behavior test result for TASK_264 closure:

```text
3 passed
```

Required build validation:

```powershell
cd frontend; npm run build
```

Recommended backend contract safety check:

```powershell
py -m pytest tests\integration\test_confirmed_matrix_test_record_preview_api.py -q
```

## Required Executable Plan Before Implementation

Before implementation, create a reviewable plan document, for example:

```text
docs/task_264_matrix_to_test_record_smoke_ui_plan.md
```

The plan must include:

- actual Project Workbench component/composition structure found in code
- exact placement decision
- exact API client symbols
- exact loading/error/empty UI state model
- test strategy and mocked response data
- risks and fallback choices
- validation commands

No implementation code may be written before that plan is reviewed and explicitly approved.

## Residual Risk Record

- Project Workbench has historical mock/runtime console surfaces. The implementation plan must identify the current real composition point before adding UI.
- If no clean Project Workbench panel boundary exists, prefer creating a named feature component and composing it narrowly rather than expanding a large page JSX block.
- Users may expect preview before confirmation. This task must keep the rule explicit: Test Record preview consumes active ConfirmedMatrix only.
- This task is smoke validation, not final Test Record UX.
