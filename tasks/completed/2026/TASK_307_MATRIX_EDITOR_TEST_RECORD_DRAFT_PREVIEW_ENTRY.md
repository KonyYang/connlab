# TASK_307_MATRIX_EDITOR_TEST_RECORD_DRAFT_PREVIEW_ENTRY

Status: Complete.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

TASK_307 was approved for implementation and completed.

## Model Fit Assessment

GPT-5.3-codex is suitable for this task. The task is a bounded Matrix Editor / frontend-and-derived-output task with an existing Test Record generation foundation to reuse. It requires careful distinction between unconfirmed Matrix Editor preview drafts and Workbench/Project-package authority outputs, but it does not require StepInstance execution persistence, report generation, AI review, permissions, or package orchestration.

## Mandatory Frontend Preconditions

Before implementation, the agent must:

- Load `$impeccable` project context for this Matrix Editor UI change.
- Read `docs/02_ARCHITECTURE_RULES.md`.
- Read `docs/frontend_architecture_rules.md`.
- Keep ConnLab as an `$impeccable` `product` UI surface.

## Goal

Add a `Test record` action in the Matrix Editor page that lets an operator download and inspect a Test Record draft generated from the current Matrix Editor page state at click time.

This is intentionally different from the Workbench `Test record` action:

- Matrix Editor `Test record`: draft preview/download for the current editable Matrix state shown in the Matrix Editor at the moment the operator clicks the button. It is for user review before confirmation.
- Workbench `Test record`: authority output from active Confirmed Matrix. It is the version that can later be placed into the project folder and, in future package tasks, moved into the official public-drive package.

## Current Code Reality

- Workbench already has confirmed-Matrix Test Record generation behavior through the existing confirmed-Matrix endpoint/client.
- Matrix Editor currently does not provide an equivalent `Test record` download for the live editor state before confirmation.
- Existing Test Record generation services/gateways should be reused where possible, but the authority/source contract must be explicit.

## Inputs

- Current Matrix Editor page state at click time, captured as a bounded current UI state payload:
  - editable groups/rows/cells currently shown in Matrix Editor
  - current selected/imported Matrix content before Confirm Matrix
  - current dirty/unsaved visible edits included directly in the preview payload
- Existing Test Record template settings/gateway behavior.
- Existing Matrix Editor project id and draft lifecycle context.

V1 source contract:

- The `Test record` click must build and send the current Matrix Editor UI state payload, similar to the Fee Evaluation `Fee Form` export path.
- The backend generation input must be that bounded current UI state payload, not the active Confirmed Matrix authority and not a historical draft/revision selection.
- TASK_307 preview generation does not require saving the Matrix Editor draft first. Confirm Matrix remains the formal authority gate for official Workbench/package outputs.

## Outputs

- Matrix Editor exposes a clear `Test record` action near the Matrix draft controls.
- The action generates/downloads a `.docx` draft for review from the current Matrix Editor page state at click time.
- The draft is clearly labeled/copy-described as an unconfirmed preview when the Matrix draft is not active authority.
- The action must not register ProjectOutputRecord or mark an authority Test Record output as current.
- The downloaded file name and/or document body must include a clear unconfirmed preview marker, such as `Preview` / `Unconfirmed Matrix draft`, so the file remains distinguishable after it leaves the UI.

## Scope

In scope:

- Add Matrix Editor UI entry for `Test record` draft preview/download.
- Add or reuse backend/application generation path that accepts the bounded current Matrix Editor UI state payload as the source, if the existing confirmed-Matrix generation path cannot safely handle unconfirmed/current editor state.
- Keep generated file as a local/browser download candidate, not a persisted authority output.
- Add/update tests for Matrix Editor UI wiring, draft-source generation, and copy/guard behavior.

Out of scope:

- No Workbench authority Test Record behavior change unless needed to avoid duplicate/confusing labels.
- No package orchestrator.
- No project-folder placement.
- No public-drive publish/move.
- No ProjectOutputRecord registration for unconfirmed preview drafts.
- No Confirm Matrix side effect.
- No historical draft/revision selection.
- No exporting all historical Matrix draft versions or revision history.
- No StepInstance, execution persistence, image placement, report generation, AI review, permissions, or multi-user scope.
- No Fee Form or Customer Feedback Form changes.

## UX Placement Decision

The Matrix Editor `Test record` action belongs with Matrix draft actions because it previews the editor's current page state. It should not be placed in the Workbench project package/output area.

Copy must distinguish draft preview from authority output:

- Prefer action label: `Test record`
- Supporting copy or tooltip: `Download a draft from the current Matrix page state. Confirm Matrix before using it as the project authority version.`

## Acceptance Criteria

- Matrix Editor displays a `Test record` action.
- The action is available when the current Matrix Editor page state has previewable Matrix rows.
- The action sends the current Matrix Editor UI state payload and downloads a Test Record `.docx` draft based on that click-time payload, not the active Confirmed Matrix authority.
- A test covers editing the Matrix Editor, clicking `Test record` before confirmation or save, and verifying the generated request/source includes the latest visible value.
- If the current page state is missing/empty/invalid, the UI shows a clear blocker.
- The action does not require choosing or exporting historical Matrix draft versions/revisions.
- The backend input model is explicit, such as a Matrix Editor draft preview command carrying current groups/rows/cells/metadata needed by the Test Record writer, and it must not create a ConfirmedMatrixSnapshot, register ProjectOutputRecord, save the draft as a side effect, or pretend to be active authority.
- The downloaded filename or document content contains `Preview` / `Unconfirmed Matrix draft` wording to distinguish it from Workbench authority Test Record output.
- Generated unconfirmed draft is not registered as a current Project output.
- Workbench authority `Test record` behavior remains reserved for active Confirmed Matrix and future package placement.
- No public-drive placement, package execute, Fee Form, Customer Feedback, evidence placement, StepInstance, report, AI, permission, or multi-user scope appears as part of TASK_307.

## Required Validation

- `cd frontend; npm test -- --run MatrixEditorWorkspace TestRecord --watch=false`
- `cd frontend; npm run build`
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "matrix_editor or test_record"`
- Relevant backend unit/integration tests if a draft-source generation service/API is added.
- `git diff --check`

## Stop Point

After TASK_307 implementation and validation, stop. Do not proceed to TASK_308 without a new task file/plan approval cycle.
