# TASK_313 Project Package Orchestrator Execute Executable Plan

Status: Planned; awaiting explicit approval.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: `TASK_313_PROJECT_PACKAGE_ORCHESTRATOR_EXECUTE`, planned.

Allowed reason: `docs/task_board.md` states TASK_312 is complete and TASK_313 requires a task file, executable plan, and explicit approval before implementation. This plan prepares the implementation contract only; coding starts after explicit approval.

## Frontend And Architecture Preconditions

Before implementation:

- Read `AGENTS.md`.
- Read `docs/task_board.md`.
- Read `tasks/TASK_313_PROJECT_PACKAGE_ORCHESTRATOR_EXECUTE.md`.
- Read `docs/project_management/TASK_EXECUTION_SKILL.md`.
- Load `$impeccable` product context.
- Read `docs/02_ARCHITECTURE_RULES.md`.
- Read `docs/frontend_architecture_rules.md`.

TASK_313 touches Workbench UI, so `$impeccable` and frontend architecture rules are mandatory.

## Summary

TASK_313 adds explicit project package execution from the Workbench package preview. V1 generates and places only the three approved package files:

- Confirmed Matrix Test Record
- Confirmed Fee Form
- Customer Feedback Form

The operator must first see a ready package preview. Execute revalidates the preview context, stages generated files, blocks target conflicts, then copies the three files into the latest project folder's `Submitted Material` directory.

## Scope

In scope:

- New backend package execution application service.
- New thin FastAPI route:
  - `POST /api/projects/{project_id}/project-package/execute`
- Typed frontend API client function and DTOs.
- Workbench package preview panel execute state/action.
- Tests for context mismatch, blockers, conflicts, staging, final placement, and UI boundary.

Out of scope:

- No old `/approval-package/execute` route or service wrapping.
- No evidence placement.
- No Application Form Word write-back.
- No public-drive publishing outside the latest project folder.
- No package-level or artifact-level `ProjectOutputRecord` registration in package mode.
- No StepInstance, TestResult, report execution, image upload, AI review, permissions, LAN, or multi-user scope.

## Backend Design

### New Files

- `backend/application/project_package_execute_service.py`
- `backend/api/routes_project_package_execute.py`
- `tests/unit/test_project_package_execute_service.py`
- `tests/integration/test_project_package_execute_api.py`

### Modified Files

- `backend/api/dependencies.py`
- `backend/api/main.py`
- `backend/application/project_package_preview_service.py`
- `backend/api/routes_project_package_preview.py`

Modify existing generation services only if needed to support staging or disabling package-unrelated side effects:

- Confirmed Matrix Test Record generation may need an explicit staging-output mode.
- Fee Form export may need a no-registration/package-staging mode so TASK_313 does not create any `ProjectOutputRecord`.
- Customer Feedback generation should keep its TASK_311 output-dir safety; package execute copies its generated file after service completion.

Package mode ledger rule:

- Reused Test Record generation must not register a `ProjectOutputRecord`.
- Reused Fee Form export must not register a `ProjectOutputRecord`.
- Reused Customer Feedback generation must not register a `ProjectOutputRecord`.
- TASK_313 itself must not register a package-level `ProjectOutputRecord`.
- If an existing service currently registers output records by default, implementation must add an explicit package/no-ledger mode and tests proving no record is created.

### Execute Service Responsibility

`ProjectPackageExecuteService` coordinates execution. It must:

- Load project and latest project folder.
- Re-run package preview/readiness.
- Compare current preview context with request context.
- Resolve the latest project folder's `Submitted Material` directory.
- Generate all three package files into controlled staging locations.
- Resolve final target paths under `Submitted Material`.
- Block if any final target exists.
- Copy staged files into final targets with no-overwrite behavior.
- Return final generated item metadata.

It must not:

- call backend HTTP routes,
- write outside the latest project folder final target,
- overwrite existing final package files,
- register package-level or artifact-level `ProjectOutputRecord`,
- copy evidence,
- write Application Form Word files,
- invoke public-drive discovery or publish logic.

### Request Model

`ProjectPackageExecuteRequest`:

```python
class ProjectPackageExecuteRequest(BaseModel):
    expected_project_folder_path: str
    expected_confirmed_matrix_id: str
    expected_confirmed_revision: int
    expected_confirmed_fee_id: str
    expected_confirmed_fee_revision: int
    expected_confirmed_fee_pricing_draft_edit_id: str
    expected_customer_feedback_template_path: str
```

The preview API must expose enough context for the frontend to send this request. If TASK_312 currently lacks `confirmed_fee_pricing_draft_edit_id` or Customer Feedback template path, extend the preview response with an execution context object rather than parsing display text.

### Response Model

`ProjectPackageExecuteResponse`:

```python
class ProjectPackageExecuteResponse(BaseModel):
    project_id: str
    project_folder_path: str
    submitted_material_path: str
    status: Literal["executed"]
    generated_items: list[ProjectPackageExecutedItemResponse]
    warnings: list[str]

class ProjectPackageExecutedItemResponse(BaseModel):
    key: Literal["test_record", "fee_form", "customer_feedback_form"]
    label: str
    file_name: str
    final_path: str
```

Failures:

- Project missing: `404`.
- Readiness/context mismatch/target conflict: `409`.
- Template or source validation failures: `409` unless an existing service has a more specific typed error.
- Unexpected gateway or filesystem errors should not be swallowed; return a server error with context.

### Context Matching

Before generating files, compare request fields to current state:

- latest folder path equals `expected_project_folder_path`
- active Confirmed Matrix id/revision equals expected
- latest Confirmed Fee is `current` and id/revision/pricing draft id equals expected
- discovered Customer Feedback template path equals expected

Any mismatch returns `409` with a message telling the operator to refresh package preview.

### Placement Policy

Final V1 target directory:

```text
<latest project folder>/Submitted Material
```

If `Submitted Material` does not exist or is not a directory, return `409` blocker. Do not create it in TASK_313.

All final paths must be resolved and verified to stay under the latest project folder.

### Staging Policy

Generate first, copy second.

Recommended staging:

- Test Record: controlled package staging directory under app data.
- Fee Form: controlled package staging directory under app data.
- Customer Feedback: use TASK_311 controlled generated output, then treat that file as staging source.

After all staging files exist:

- compute final target paths with `ProjectPackageFinalNamePlanner`
- reject if any final target exists
- copy each file with no-overwrite semantics
- best-effort remove only files created by this execution if a later final copy fails

### Final File Naming

Add a pure filename planner for package final names.

Prefix rule:

- use the first non-empty value from project LTR number, project number, then project id
- sanitize with the same safe filename rules used by existing Office generation paths

V1 final names:

```text
{prefix}_Test_Record.docx
{prefix}_Fee_Form.xls
{prefix}_Customer_Feedback_Form.xlsx
```

Staging file names are implementation details. Do not use staging names as final package names. If any final name already exists under `Submitted Material`, return `409` before final copy and do not add numeric suffixes.

### Fee Form Source

Use latest current Confirmed Fee authority snapshot.

Implementation must not read current Fee Evaluation page state or unconfirmed saved pricing draft values. If existing Fee Form export requires edited values, add a small application helper to convert the Confirmed Fee `pricing_snapshot_json` into the edited-values payload used by TASK_300 export.

### Customer Feedback Source

Reuse TASK_311 discovery and generation rules:

- configured Template folder
- exactly one `.xlsx` filename containing `E-4243`
- no workbook filling beyond TASK_311 behavior

Do not expose an arbitrary output directory in the package execute API.

## API Design

Endpoint:

```text
POST /api/projects/{project_id}/project-package/execute
```

Route behavior:

- Thin route that calls `ProjectPackageExecuteService`.
- `404` only for project-not-found.
- `409` for business blockers and stale preview context.
- Typed Pydantic request/response.
- No route-level Office, filesystem copy, or repository orchestration logic.

## Frontend Design

### Modified Files

- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/ProjectPackagePreviewPanel.tsx`
- `frontend/src/features/project-workbench/ProjectPackagePreviewPanel.test.tsx`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`

### UI Contract

`ProjectPackagePreviewPanel` gains:

- `Execute package` action when preview `status === "ready"` and execution context is complete.
- inline executing/success/error state.
- final generated path list after success.
- business-readable blocker/conflict messages after failure.

It must not show:

- public-drive publish action,
- evidence placement action,
- Application Form write-back action,
- individual Test Record/Fee Form/Customer Feedback generation buttons,
- generic tools controls.

### State Flow

`useProjectWorkbenchModel` owns:

- package preview state from TASK_312,
- execute loading/error/result state,
- `executeProjectPackage` action.

On successful execute:

- refresh package preview or mark it executed with returned paths.
- keep Matrix and step workspace state unchanged.

On `409`:

- show the server message.
- keep preview visible.
- tell the operator to refresh preview if the message indicates stale context.

## Static Boundary Tests

Add shell/static checks that Workbench package execution:

- imports the package execute API client only in Workbench feature/model boundaries,
- does not import old approval-package execute route/client,
- does not add public-drive publish copy,
- does not expose evidence/Application Form write-back controls,
- does not call Customer Feedback generation as a visible standalone Workbench action.

## Test Plan

Backend unit tests:

- ready context stages and copies exactly three files to `Submitted Material`.
- stale Confirmed Matrix context returns conflict before generation.
- stale Confirmed Fee context returns conflict before generation.
- Customer Feedback template path mismatch returns conflict.
- missing `Submitted Material` returns blocker.
- existing final target file blocks before final copy.
- generated final paths outside project folder are rejected.
- Fee Form uses Confirmed Fee snapshot values, not an arbitrary current-page payload.
- no package-level or artifact-level `ProjectOutputRecord` is registered.
- final names follow `{prefix}_Test_Record.docx`, `{prefix}_Fee_Form.xls`, and `{prefix}_Customer_Feedback_Form.xlsx`.

API tests:

- `POST /api/projects/{project_id}/project-package/execute` returns generated metadata on success.
- project-not-found returns `404`.
- readiness conflict returns `409`.
- response paths are under latest project folder.

Frontend tests:

- ready preview renders `Execute package`.
- blocked preview does not enable execute.
- successful execute displays final paths.
- stale/conflict response displays actionable copy.
- no publish/evidence/Application Form actions appear.

Regression:

- `py -m pytest tests/unit/test_project_package_execute_service.py tests/integration/test_project_package_execute_api.py -q`
- `cd frontend; npm test -- --run ProjectPackagePreview ProjectWorkbench --watch=false`
- `cd frontend; npm run build`
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "project_workbench or package"`
- `git diff --check`

## Risks And Controls

- Office gateway failure can occur after staging starts. Control: staging is outside the final project folder; final folder copy starts only after all staged outputs exist.
- Final file copy is not truly transactional on Windows. Control: no-overwrite preflight and best-effort cleanup of files created by the current run only.
- Preview can become stale. Control: execute request carries expected context and service revalidates before generation.
- Existing Fee export may register output records by default. Control: add a scoped no-registration mode for package execution if required.

## Stop Point

Stop after implementing TASK_313, running validation, and updating `docs/task_board.md`. Do not start evidence placement, public-drive publish, Application Form Word write-back, or TASK_314+ work without separate task file, plan, and approval.
