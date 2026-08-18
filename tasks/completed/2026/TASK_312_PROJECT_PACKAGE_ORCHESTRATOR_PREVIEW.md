# TASK_312_PROJECT_PACKAGE_ORCHESTRATOR_PREVIEW

Status: Complete.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

TASK_312 implementation is complete. TASK_313 package execution requires its own task file, executable plan, and explicit approval before implementation.

## Model Fit Assessment

GPT-5.3-codex is suitable for TASK_312 because the task is a bounded backend/API plus Workbench read-only UI integration. It mainly composes existing project folder, Confirmed Matrix, Confirmed Fee, Section 2 sync, and Customer Feedback readiness signals into a preview. It does not require new pricing judgment, AI reasoning, public-drive publishing logic, or Office generation behavior.

## Goal

Add a Project Workbench package preview that shows whether the current project is ready for formal package generation before any file operation happens.

The preview answers:

- Is there a valid project folder target?
- Is the active Confirmed Matrix authority available?
- Is the latest Confirmed Fee authority current?
- Is Application Form Section 2 synchronized from the active Confirmed Matrix?
- Is the Customer Feedback template discoverable from the configured Template folder?
- Which expected package outputs will TASK_313 generate later?
- What blockers and warnings must the operator resolve first?

## Current Code Reality

- `ApprovalPackageService` already exists, but it requires explicit caller-provided file paths and its execute path registers `ProjectOutputRecord`.
- TASK_312 is not a rename or UI wrapper around the old approval-package execute flow.
- TASK_312 must derive readiness from current structured project state and existing application services/repositories.
- Customer Feedback Form generation exists through TASK_311, but TASK_312 must only check template readiness. It must not generate or copy the workbook.
- Project Workbench already contains folder creation, Section 2 sync, Matrix workspace, and Fee status surfaces. TASK_312 adds one compact read-only preview surface.

## V1 Contract

`GET /api/projects/{project_id}/project-package/preview`

Project-not-found is a `404`.

Readiness problems are returned as `200` with `status="blocked"` plus business-readable blockers. The preview endpoint must not mutate data.

Response shape must include:

- `status`: `ready` or `blocked`
- `project_folder`
- `authority_context`
- `required_items`
- `optional_items`
- `blockers`
- `warnings`

## Readiness Rules

Required readiness checks:

- Project exists.
- Latest project folder record exists and its path is an existing directory.
- Active Confirmed Matrix authority exists.
- Latest Confirmed Fee status is `current`.
- Section 2 sync preview is not blocked and not still requiring required date sync.
- Exactly one Customer Feedback `.xlsx` template whose filename contains `E-4243` is discoverable from the configured Template folder.
- Expected package targets resolve under the latest project folder.

V1 Section 2 interpretation:

- `blocked` => blocker.
- `ready` => blocker because required sync has not been applied yet.
- `partial` => warning unless the implementation detects an invalid required field, in which case it is a blocker.
- `up_to_date` / `synced` => ready for package preview.

## In Scope

- Backend read-only application service for project package preview.
- Thin API route for package preview.
- Dependency and API main wiring.
- Typed frontend API client function and DTOs.
- Workbench read-only package preview panel.
- Workbench model/runtime selector state for loading and refreshing package preview.
- Tests for readiness blockers, ready status, no mutation, and UI boundary.
- Documentation and task-board completion update after implementation.

## Out Of Scope

- No package execute action.
- No public-drive publish/copy operation.
- No Test Record generation.
- No Fee Form generation.
- No Customer Feedback workbook generation.
- No evidence copying.
- No `ProjectOutputRecord` registration.
- No old `/approval-package/execute` invocation.
- No StepInstance, TestResult, report generation, image upload, AI review, permission, LAN, or multi-user scope.
- No Matrix/Fee default filling or pricing rule update.
- No generic tools page.

## Frontend Preconditions

Before implementation, load `$impeccable` context and read:

- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`

Workbench UI must remain operational and dense. The package preview panel must show state, blockers, target folder, and expected outputs without crowding the Matrix workspace or exposing future execute actions.

## Acceptance Criteria

- Workbench shows a read-only package preview panel below Section 2 sync and above the Matrix workspace.
- The panel has a `Refresh preview` action only.
- The panel does not show `Execute`, `Publish`, `Generate package`, Test Record generation, Fee Form generation, or Customer Feedback generation actions.
- The backend preview returns `blocked` with actionable blockers when required readiness is missing.
- The backend preview returns `ready` only when all required readiness checks pass.
- The preview does not create, copy, modify, or delete files.
- The preview does not register `ProjectOutputRecord`.
- Expected package targets are described under the latest project folder only.
- Customer Feedback template readiness is checked without invoking Excel COM or workbook generation.
- Existing TASK_306-TASK_311 behavior remains unchanged.

## Validation Plan

- `py -m pytest tests/unit/test_project_package_preview_service.py tests/integration/test_project_package_preview_api.py -q`
- `cd frontend; npm test -- --run ProjectPackagePreview ProjectWorkbench --watch=false`
- `cd frontend; npm run build`
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "project_workbench or package"`
- `git diff --check`

Browser smoke after implementation approval:

- Open an existing Project Workbench.
- Confirm the package preview appears below Section 2 sync.
- Confirm missing readiness appears as blockers.
- Confirm there is no execute/publish/generate package button.

## Stop Point

Stop after implementing TASK_312, running relevant validation, and updating the task board. TASK_313 package execution requires its own task file, executable plan, and explicit approval.
