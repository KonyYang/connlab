# TASK_314C_MATRIX_FEE_PROJECT_FOLDER_REGRESSION

Status: Complete. Implemented after separate explicit user approval.

Executable plan: `docs/task_314c_matrix_fee_project_folder_regression_plan.md`

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

TASK_314C is the linkage regression slice split out from `TASK_314_MATRIX_AND_FEE_BACKGROUND_DRAFT_PERSISTENCE`.

TASK_314C is not a prerequisite for `TASK_315_MATRIX_DRAFT_TO_FEE_DRAFT_INCREMENTAL_REBASE` unless the user explicitly decides to run this regression gate before TASK_315. TASK_315's functional prerequisite remains completed TASK_314A Matrix Editor draft persistence. TASK_314B Fee Evaluation background draft persistence is also complete. TASK_314C is now complete and does not automatically authorize TASK_315.

Completion summary: added backend Required forms regressions for missing Confirmed Matrix, missing Confirmed Fee, and stale Confirmed Fee; added frontend Project Folder selector regressions so Required forms cannot show ready/current when Matrix or Confirmed Fee authority is not current; added a static shell guard for Fee autosave/discard wiring and Project Folder wording/gating; fixed the narrow selector linkage bug in `projectFolderTaskSelectors.ts`.

## Goal

Verify that the completed TASK_314A Matrix Editor draft persistence and TASK_314B Fee Evaluation background draft persistence do not break the Project Folder preparation chain built by TASK_318, TASK_320, and TASK_321.

This task is a regression hardening task, not a feature task.

## Current Code Reality

- Matrix Editor draft persistence is implemented in:
  - `backend/application/matrix_editor_session_service.py`
  - Matrix Editor session API routes
  - `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- Fee Evaluation pricing draft persistence is implemented in:
  - `backend/application/fee_evaluation_pricing_draft_persistence_service.py`
  - `backend/application/confirmed_fee_version_service.py`
  - `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py`
  - `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
- Project Folder readiness and generation behavior is implemented by:
  - TASK_318 Official project folder check
  - TASK_320 single-task Workbench UI
  - TASK_321 Required forms generation

## V1 Scope

TASK_314C should add or update regression coverage only where a real cross-task gap exists.

It must verify:

1. Matrix draft autosave/confirm/discard still leaves active Confirmed Matrix authority coherent for downstream Fee and Project Folder flows.
2. Fee pricing draft autosave/confirm/discard still leaves Confirmed Fee authority coherent for Required forms.
3. Confirmed Matrix and Confirmed Fee readiness are reflected correctly in the TASK_320 Project Folder task list.
4. TASK_318 Official project folder check still reads generated output status correctly after Confirmed Matrix/Fee changes.
5. TASK_321 Required forms preview/generation still gates correctly on current Confirmed Matrix and current Confirmed Fee authority.

## Out Of Scope

- No Matrix Draft -> Fee Draft incremental rebase. That belongs to TASK_315.
- No Fee calculation model changes.
- No Matrix Editor behavior changes except test-only fixture adjustments needed for regression coverage.
- No ProjectOutputRecord schema, generation semantics, or API contract changes inside TASK_314C. If a regression points to that kind of fix, stop and split a follow-up task instead of repairing it here.
- No new Required forms generation behavior.
- No public-drive upload changes.
- No Application Form Section 2 write-back changes.
- No StepInstance, execution persistence, evidence/photos, report generation, AI review, permissions, LAN, or multi-user work.
- No broad UI redesign or copy polish.

## Required Regression Areas

### Backend/API

- Matrix Editor session save/restore/confirm/discard:
  - `tests/unit/test_matrix_editor_session_service.py`
  - `tests/integration/test_matrix_editor_session_api.py`
- Confirmed Matrix authority:
  - `tests/integration/test_confirmed_matrix_authority_api.py`
  - `tests/integration/test_matrix_revision_flow_api.py`
- Fee pricing draft persistence and Confirmed Fee:
  - `tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py`
  - `tests/integration/test_fee_evaluation_pricing_draft_api.py`
  - `tests/unit/test_confirmed_fee_version_service.py`
  - `tests/integration/test_confirmed_fee_version_api.py`
- Project Folder readiness:
  - `tests/unit/test_official_project_folder_check_service.py`
  - `tests/unit/test_project_folder_required_forms_service.py`
  - `tests/integration/test_project_folder_required_forms_api.py`

### Frontend

- Matrix Editor autosave/cancel/confirm gating:
  - `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- Fee Evaluation autosave/discard/confirm gating:
  - `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`
- Project Folder task order and Required forms detail:
  - `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
  - `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
  - `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- Static shell guards:
  - `tests/unit/test_frontend_shell_files.py`

## Expected Deliverables

Implementation, when later approved, should deliver one or more of:

- focused backend regression tests,
- focused frontend regression tests,
- static shell guards for the cross-task contract,
- small bug fixes only if those tests reveal a real regression in the TASK_314A/TASK_314B/TASK_318/TASK_320/TASK_321 linkage,
- updated `docs/task_board.md` validation summary.

If the first run finds no functional gaps, TASK_314C may complete as a test-only / validation-only task.

Production-code stop rule: TASK_314C may only apply narrow fixes inside the files named by the approved plan. If a fix needs to touch broader ProjectOutputRecord behavior, schema, generation semantics, API contracts, storage migrations, or unrelated Matrix/Fee/Project Folder production paths, stop and create a separate follow-up task for review.

## Acceptance Criteria

- Matrix Editor and Fee Evaluation draft tests pass together.
- Confirmed Matrix and Confirmed Fee authority tests pass together.
- Project Folder check and Required forms tests pass together.
- Workbench Project Folder task selectors still keep the process order:
  - Local project folder
  - Request material
  - Confirmed Fee authority
  - Required forms
  - Application Form Section 2
  - Submitted Material
  - Public drive upload
- Required forms remains blocked when Confirmed Fee is missing/stale.
- Required forms remains blocked when current Confirmed Matrix authority is missing/stale.
- Required forms becomes ready/current only when current Confirmed Matrix and current Confirmed Fee authority are present.
- No old `Package` / `Execute package` normal-flow copy reappears in Project Folder UI.
- Validation commands and pass counts are recorded in `docs/task_board.md`.

## Stop Point

TASK_314C implementation is complete. Stop here after validation and task board update.

Do not proceed to TASK_315, package execution, StepInstance, reporting, AI, permissions, or multi-user scope without separate explicit approval.
