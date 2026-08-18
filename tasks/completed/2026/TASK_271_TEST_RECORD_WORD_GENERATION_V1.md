# TASK_271_TEST_RECORD_WORD_GENERATION_V1

## Status

Complete.

## Current Execution Context

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current product direction: `Matrix-driven Laboratory Execution Phase`
- Current task status: `TASK_271_TEST_RECORD_WORD_GENERATION_V1`
- Allowed reason: `TASK_270_RECORD_STEP_WORKSPACE_PANEL` is complete, `docs/task_board.md` has no active implementation task, and this task is the next guideline-aligned slice from `docs/post_phase11_matrix_driven_laboratory_execution_workflow_guideline.md`.

## Source Guideline

Reference: `docs/post_phase11_matrix_driven_laboratory_execution_workflow_guideline.md`

Guideline intent:

```text
Generate a real Word Test Record draft from active ConfirmedMatrix.
```

This task improves Matrix to Test Record continuity by converting the validated active ConfirmedMatrix preview chain into a downloadable `.docx` Test Record draft, so the operator can move from authority confirmation to a real Word working document.

## Objective

Add v1 Test Record Word draft generation from the active ConfirmedMatrix only.

The output is a downloadable `.docx` draft that contains selected groups and confirmed Matrix step data. This task must remain a narrow derived-output slice, not a formal TestRecord aggregate, report engine, execution persistence system, equipment workflow, or generic template engine.

## Baseline

Current completed baseline:

- TASK_263 provides a read-only backend ConfirmedMatrix to Test Record preview service and API.
- TASK_269 renders a Project Workbench Matrix projection from that preview.
- TASK_270 turns clicked matrix tokens into a read-only Record Step Workspace panel.
- Existing legacy `test_record_fee_document_generation_service.py` generates approval-package files from ProjectMatrixDraft data, not from active ConfirmedMatrix authority.
- Existing `TestRecordDocumentGateway` proves `.docx` generation through the infrastructure Office boundary, but its current dataset shape is legacy draft/fee oriented.

## Scope

In scope:

- Backend generation from active ConfirmedMatrix only.
- Use existing confirmed Matrix preview mapping as the source data.
- Generate a deterministic Word `.docx` draft through an infrastructure Office gateway using a controlled default Test Record layout.
- Include selected groups only.
- Fill first-pass group and step fields:
  - Group number / label
  - Sample quantity and sample number placeholder
  - Step token / sequence
  - Test item
  - Test method
  - Test condition
  - Remarks / requirement
  - Product description if available from Project
  - Applicable specification if available from active matrix source metadata or leave blank
- Leave manual execution fields blank:
  - Start Date/Time
  - Complete Date/Time
  - Equipment ID No.
  - Tested By
  - handwritten remarks
  - execution data
- Add a download endpoint and minimal Project Workbench UI action labelled `Generate Test Record Draft`.
- Add unit, integration, frontend, and static guard tests.
- Update task and board status after implementation.

Out of scope:

- Formal `TestRecord` aggregate.
- StepInstance persistence.
- LLCR runtime persistence.
- Evidence upload.
- Structured measurement forms.
- Report engine.
- Fee engine.
- AI recommendation or AI review.
- Equipment assignment.
- Permission or multi-user review workflow.
- Generation history or regeneration ledger.
- Saving under the project folder as a managed artifact.
- Historical Test Record template selection.
- Generic template engine or placeholder DSL.
- Matrix authority mutation from Project Workbench.

## Expected File Changes

Create:

- `backend/application/confirmed_matrix_test_record_document_generation_service.py`
- `backend/api/routes_confirmed_matrix_test_record_generation.py`
- `frontend/src/features/project-workbench/TestRecordDraftGenerationButton.tsx`
- `frontend/src/features/project-workbench/TestRecordDraftGenerationButton.test.tsx`
- `tests/unit/test_confirmed_matrix_test_record_document_generation_service.py`
- `tests/integration/test_confirmed_matrix_test_record_generation_api.py`

Modify:

- `backend/infrastructure/office/test_record_document_gateway.py`
- `backend/infrastructure/office/models.py`
- `backend/infrastructure/office/__init__.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- `docs/task_board.md`
- `docs/task_plan_index.md`
- `tasks/TASK_271_TEST_RECORD_WORD_GENERATION_V1.md`

No database migrations are expected.

## API Contract

Add a new endpoint:

```text
POST /api/projects/{project_id}/confirmed-matrix/test-record-draft/generate
```

Behavior:

- Source is active ConfirmedMatrix for `project_id`.
- Response is a downloadable `.docx` file.
- `404` when no active ConfirmedMatrix exists.
- `422` when active ConfirmedMatrix exists but has no previewable steps.
- No request body is required for v1.

## UI / UX Requirements

- ConnLab register: `product`.
- Physical scene: a lab coordinator on a daytime Windows workstation has confirmed matrix authority and needs a Word draft for paper/package review.
- The Project Workbench action must be labelled `Generate Test Record Draft`.
- The action must be disabled or unavailable when there is no ready active ConfirmedMatrix preview.
- The UI must show concise loading/error feedback.
- The UI must not expose Report, Fee, AI, equipment, permission, or execution-data actions.
- The UI must not ask the user for arbitrary local file paths.
- API calls must stay in `frontend/src/api/client.ts`.

## Data Contract

The generation service must consume the existing confirmed preview source:

```py
ConfirmedMatrixTestRecordPreview
ConfirmedMatrixTestRecordPreviewGroup
ConfirmedMatrixTestRecordPreviewStep
```

The Word gateway must receive an application-owned document model, not ORM rows or API DTOs directly.

## Acceptance Criteria

- Clicking `Generate Test Record Draft` in Project Workbench downloads a `.docx` file.
- The backend generates only from active ConfirmedMatrix authority.
- Generated document contains selected groups only.
- Generated document includes group label, sample quantity, step token / sequence, test item, method, condition, and requirement / remarks.
- Manual execution fields are present but blank.
- No backend/API/database changes introduce StepInstance, execution persistence, report engine, AI, fee, equipment, permission, or generation history scope.
- Existing TASK_263 to TASK_270 behavior remains intact.
- Relevant unit, integration, frontend, and static guard tests pass.

## Validation Plan

Required commands after implementation:

```powershell
py -m pytest tests\unit\test_confirmed_matrix_test_record_document_generation_service.py -q
py -m pytest tests\unit\test_test_record_document_gateway.py -q
py -m pytest tests\integration\test_confirmed_matrix_test_record_generation_api.py -q
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
```

```powershell
cd frontend
npm test -- --run TestRecordDraftGenerationButton
npm test -- --run ProjectWorkbenchMatrixProjectionPanel
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task271 or task270 or task269 or project_workbench"
git diff --check
```

## Risks

- Existing legacy approval-package document generation is draft-based. TASK_271 must not reuse it in a way that makes generation depend on ProjectMatrixDraft or fee data.
- A real lab Word template may be more complex than v1. This task should produce a deterministic v1 Word draft from the controlled default layout and leave historical-template selection for later.
- Downloading a generated file without history is acceptable for v1, but later tasks may need output registration and regeneration freshness tracking.
- Existing Project Workbench has older mock step controls. UI work must be narrowly attached to the confirmed Matrix projection path to avoid reviving inactive mock workflow actions.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task.

Reason:

- The task is a bounded backend/API/frontend integration slice with existing precedent in confirmed Matrix preview and Word gateway code.
- It requires careful layer control and tests, but does not require broad schema migration, COM automation, report engine design, or multi-user workflow modeling.
- Medium reasoning is sufficient if the implementation follows the existing ConfirmedMatrix preview service and infrastructure Office gateway boundary.

Recommended mode:

- `GPT-5.3-codex` with medium reasoning.
- Use `superpowers:executing-plans` for implementation after user approval.

## Implementation Summary

- Added backend service and route to generate a downloadable `.docx` from active ConfirmedMatrix authority only.
- Extended `TestRecordDocumentGateway` with ConfirmedMatrix-specific writer method while preserving legacy `generate(...)`.
- Added Project Workbench `Generate Test Record Draft` action with ready/disabled/error states through `frontend/src/api/client.ts`.
- Added service, gateway, API integration, frontend component, projection wiring, and static guard tests.

## Validation Results

- `py -m pytest tests\unit\test_confirmed_matrix_test_record_document_generation_service.py -q` -> `3 passed`
- `py -m pytest tests\unit\test_test_record_document_gateway.py -q` -> `3 passed`
- `py -m pytest tests\integration\test_confirmed_matrix_test_record_generation_api.py -q` -> `2 passed`
- `py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q` -> `1 passed`
- `cd frontend; npm test -- --run TestRecordDraftGenerationButton` -> `3 passed`
- `cd frontend; npm test -- --run ProjectWorkbenchMatrixProjectionPanel` -> `5 passed`
- `cd frontend; npm run build` -> `passed`
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task271 or task270 or task269 or project_workbench"` -> `4 passed`
- `git diff --check` -> passed (CRLF working-copy warnings only)
