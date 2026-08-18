# TASK_312 Project Package Orchestrator Preview Executable Plan

Status: Complete.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: `TASK_312_PROJECT_PACKAGE_ORCHESTRATOR_PREVIEW`, complete.

Allowed reason: `docs/task_board.md` stated TASK_311 was complete and TASK_312 had prepared task file / executable plan; the user explicitly approved implementation. TASK_312 is now implemented and validated. TASK_313 still requires a separate task file, executable plan, and explicit approval.

## Frontend And Architecture Preconditions

Before implementation:

- Read `AGENTS.md`.
- Read `docs/task_board.md`.
- Read `tasks/TASK_312_PROJECT_PACKAGE_ORCHESTRATOR_PREVIEW.md`.
- Read `docs/project_management/TASK_EXECUTION_SKILL.md`.
- Load `$impeccable` product context.
- Read `docs/02_ARCHITECTURE_RULES.md`.
- Read `docs/frontend_architecture_rules.md`.

TASK_312 touches Workbench UI, so `$impeccable` and frontend architecture rules are mandatory.

## Summary

TASK_312 adds a read-only package preview to Project Workbench. It composes existing project readiness signals into a single operator-facing checklist before TASK_313 is allowed to generate or place any formal package files.

V1 must not generate, copy, publish, overwrite, or register output records.

## Scope

In scope:

- New backend application service that builds a read-only project package preview.
- New thin FastAPI route:
  - `GET /api/projects/{project_id}/project-package/preview`
- Frontend API DTOs and client function.
- Workbench model state for package preview loading/refresh.
- New `ProjectPackagePreviewPanel` under the Project Workbench feature boundary.
- Static tests proving TASK_312 does not expose package execution/generation actions.

Out of scope:

- No backend route calling backend HTTP.
- No `ApprovalPackageService.execute`.
- No old `/approval-package/execute` button or wrapper.
- No Test Record, Fee Form, or Customer Feedback file generation.
- No evidence copying.
- No public-drive publishing.
- No `ProjectOutputRecord`.
- No StepInstance, TestResult, report, AI review, permissions, LAN, or multi-user scope.

## Backend Design

### New Files

- `backend/application/project_package_preview_service.py`
- `backend/api/routes_project_package_preview.py`
- `tests/unit/test_project_package_preview_service.py`
- `tests/integration/test_project_package_preview_api.py`

### Modified Files

- `backend/api/dependencies.py`
- `backend/api/main.py`

### Service Responsibility

`ProjectPackagePreviewService` builds a pure read-only preview from current structured state.

It should coordinate existing stores/services rather than duplicate their business logic:

- Project repository: verify project exists.
- Folder service or folder repository: read latest project folder record and validate path is a directory.
- Confirmed Matrix authority repository/service: read active Confirmed Matrix identity and revision.
- Confirmed Fee service: read latest Confirmed Fee status and confirm it is `current`.
- Section 2 sync service: use preview to determine whether Application Form Section 2 is synchronized.
- Customer Feedback template discovery: reuse or extract the TASK_311 pure template discovery rule, `*E-4243*.xlsx`, without invoking the workbook gateway.

The service must not:

- call Excel/Word gateways,
- create output directories,
- copy files,
- generate files,
- register outputs,
- mutate database rows.

### Preview Response Model

Recommended response model:

```python
ProjectPackagePreviewResponse(
    status="ready" | "blocked",
    project_folder=ProjectPackageFolderPreview(...),
    authority_context=ProjectPackageAuthorityContext(...),
    required_items=[ProjectPackagePreviewItem(...), ...],
    optional_items=[ProjectPackagePreviewItem(...), ...],
    blockers=[...],
    warnings=[...],
)
```

Item fields should stay business-readable:

- `key`
- `label`
- `status`: `ready`, `blocked`, `warning`, `deferred`
- `target_folder`
- `target_path`
- `message`

### Readiness Decisions

Project:

- Missing project => API `404`.

Project folder:

- Missing latest folder record => blocker.
- Folder record path missing or not a directory => blocker.

Confirmed Matrix:

- Missing active Confirmed Matrix => blocker.
- Present active authority => include id and revision in `authority_context`.

Confirmed Fee:

- Missing or stale latest Confirmed Fee => blocker.
- Current latest Confirmed Fee => include confirmed fee version id and bound pricing draft id.

Section 2:

- `blocked` => blocker.
- `ready` => blocker because required sync has not been performed.
- `partial` => warning unless existing preview data exposes an invalid required target, in which case blocker.
- `up_to_date` or synced-equivalent status => ready.

Customer Feedback:

- Missing Template folder setting => blocker.
- No `*E-4243*.xlsx` under Template folder => blocker.
- Multiple `*E-4243*.xlsx` under Template folder => blocker.
- Exactly one candidate => ready.
- Do not generate or copy the workbook.

Target safety:

- Expected package targets must resolve under the latest project folder.
- If a target cannot be resolved under that folder, add a blocker.
- V1 can list target folders for generated outputs even when exact future filenames are not final. Do not invent a misleading exact file path.

### Relationship To Existing ApprovalPackageService

The old `ApprovalPackageService` accepts caller-supplied source/output paths and is still useful historical infrastructure for explicit-path preview/execute. TASK_312 is different:

- It reads project structured state.
- It creates a readiness checklist.
- It does not execute or register package outputs.
- It does not require operators to manually provide Test Record/Fee/Feedback paths.

Do not wire TASK_312 UI to the old execute path.

## API Design

Endpoint:

```text
GET /api/projects/{project_id}/project-package/preview
```

Behavior:

- `404` only when the project does not exist.
- Readiness problems return `200` with `status="blocked"`.
- Response is typed with Pydantic models.
- Route is thin and calls `ProjectPackagePreviewService`.

## Frontend Design

### New Files

- `frontend/src/features/project-workbench/ProjectPackagePreviewPanel.tsx`
- `frontend/src/features/project-workbench/ProjectPackagePreviewPanel.test.tsx`

### Modified Files

- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`

### UI Placement

Render `ProjectPackagePreviewPanel`:

- below `ProjectSection2SyncPanel`,
- above Matrix workspace,
- full-width in the main Workbench flow,
- not in the right step column.

This keeps package readiness near setup surfaces while preserving the Matrix as the main execution work area.

### UI Contract

The panel shows:

- readiness status,
- target project folder,
- required items,
- optional/deferred items,
- blockers,
- warnings,
- `Refresh preview` action.

The panel must not show:

- `Execute`,
- `Publish`,
- `Generate package`,
- `Generate Test Record`,
- `Fee Form`,
- `Generate Customer Feedback`,
- evidence copy/move actions.

### State Flow

`useProjectWorkbenchModel` owns:

- package preview response,
- loading/error state,
- `refreshProjectPackagePreview`.

`useProjectRuntimeConsoleModel` exposes the relevant fields to `ProjectWorkbenchLayout`.

`ProjectWorkbenchLayout` composes the panel and passes typed state/actions. Display components must not call `fetch()`.

## Static Boundary Tests

Add tests to ensure TASK_312 does not accidentally pull later scope into Workbench:

- `ProjectWorkbenchLayout` imports/renders `ProjectPackagePreviewPanel`.
- It does not import or render old approval-package execute controls.
- It does not import Customer Feedback generation buttons.
- It does not import Fee Form or Test Record generation actions as package actions.
- It does not include public-drive publish copy.

## Test Plan

Backend unit tests:

- no project folder => `blocked`
- folder path does not exist => `blocked`
- no active Confirmed Matrix => `blocked`
- Confirmed Fee missing/stale => `blocked`
- Section 2 still ready => `blocked`
- Customer Feedback template missing => `blocked`
- multiple Customer Feedback templates => `blocked`
- all readiness satisfied => `ready`
- preview does not create files or register `ProjectOutputRecord`

API tests:

- project missing => `404`
- blockers => `200` and `status="blocked"`
- ready => `200` and `status="ready"`
- route response is typed and includes folder/authority/items/blockers/warnings

Frontend tests:

- Workbench renders package preview panel.
- Refresh calls `fetchProjectPackagePreview(projectId)`.
- Blockers/warnings render as business-readable text.
- No execute/publish/generate action appears.
- Narrow layout keeps button text readable and avoids an action-heavy card.

Regression:

- Existing TASK_306-TASK_311 tests should not regress.

## Implementation Steps After Approval

1. Add backend service tests first.
2. Implement `ProjectPackagePreviewService`.
3. Add API route integration tests.
4. Wire API dependency and route registration.
5. Add frontend client DTO and fetch function.
6. Add `ProjectPackagePreviewPanel` tests.
7. Wire Workbench model/runtime/layout.
8. Add static shell boundary tests.
9. Run validation commands.
10. Update `docs/task_board.md` and this plan to complete status.

## Validation Commands

```powershell
py -m pytest tests/unit/test_project_package_preview_service.py tests/integration/test_project_package_preview_api.py -q
cd frontend; npm test -- --run ProjectPackagePreview ProjectWorkbench --watch=false
cd frontend; npm run build
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "project_workbench or package"
git diff --check
```

## Risks

- Existing `ApprovalPackageService` may tempt reuse of explicit-path behavior. TASK_312 must stay structured-state based.
- Customer Feedback template discovery must not accidentally call Excel gateway.
- Package preview can become visually noisy. Keep it compact and status-first.
- Target path preview must not imply public-drive publishing. V1 target is latest project folder only.

## Stop Point

After TASK_312 implementation, stop. TASK_313 package execution requires a separate task file, executable plan, explicit approval, and its own validation.
