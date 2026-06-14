# TASK_313_PROJECT_PACKAGE_ORCHESTRATOR_EXECUTE

Status: Deferred historical reference. Do not implement as written. Superseded for execution planning by `TASK_321_PROJECT_FOLDER_REQUIRED_FORMS_GENERATION`.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

TASK_313 has a historical task definition, but its executable shape has been superseded by the Project Folder model completed in TASK_316-TASK_320. Do not implement the old package execution route, Package UI, or Submitted Material placement assumptions from this file.

Replacement task for review:

- `tasks/TASK_321_PROJECT_FOLDER_REQUIRED_FORMS_GENERATION.md`
- `docs/task_321_project_folder_required_forms_generation_plan.md`

## Model Fit Assessment

GPT-5.3-codex is suitable for TASK_313 because the task is a bounded orchestration task that composes already implemented application services and Workbench preview state. It requires careful dependency and side-effect control, but it does not require new pricing judgment, AI review, lab execution persistence, image management, permissions, or public-drive migration design.

## Goal

Add an explicit Project Workbench package execution action that places the approved V1 project package files into the current latest project folder after a successful readiness preview.

V1 package execution creates and places only:

- Confirmed Matrix Test Record
- Confirmed Fee Form
- Customer Feedback Form

## Business Context

ConnLab is in transition from manual public-drive project-folder management to structured package support. The project folder remains the business-visible package location. TASK_313 must act as an operator-controlled bridge from confirmed ConnLab data into that folder; it must not publish hidden outputs as a side effect of Confirm Matrix, Confirm Fee, Section 2 sync, or folder creation.

## Current Code Reality

- TASK_312 provides read-only package readiness via `GET /api/projects/{project_id}/project-package/preview`.
- Confirmed Matrix Test Record generation already exists for the active Confirmed Matrix authority.
- Fee Form export already exists and can write Matrix basic-fill workbooks, including edited pricing values.
- Confirmed Fee authority exists and snapshots the approved pricing draft and totals.
- Customer Feedback Form generation exists and safely copies the unique `*E-4243*.xlsx` template into a controlled generated output folder.
- The old `/approval-package/execute` flow requires caller-supplied file paths and is not the TASK_313 package orchestrator.

## V1 Contract

Add:

```text
POST /api/projects/{project_id}/project-package/execute
```

The request must carry the preview context the operator saw:

- `expected_project_folder_path`
- `expected_confirmed_matrix_id`
- `expected_confirmed_revision`
- `expected_confirmed_fee_id`
- `expected_confirmed_fee_revision`
- `expected_confirmed_fee_pricing_draft_edit_id`
- `expected_customer_feedback_template_path`

The backend must re-read current state and reject execution with `409` if the current preview context no longer matches the request.

Success returns generated package metadata:

- project id
- project folder path
- generated items with key, label, business final file name, final path, and source/staging path if useful for diagnostics
- warnings

## Execution Rules

- Re-run server-side readiness before generating or copying files.
- Use active Confirmed Matrix authority for Test Record.
- Use latest current Confirmed Fee authority snapshot for Fee Form; do not use current unconfirmed Fee Evaluation page edits.
- Use the unique Customer Feedback template found by TASK_311 discovery rules.
- Do not call backend HTTP routes from backend code.
- Do not call the old `/approval-package/execute` route.
- Do not overwrite project package files.
- If any final target file already exists, block execution before copying into the project folder.
- Final V1 placement target is the latest project folder's `Submitted Material` directory.
- If `Submitted Material` is missing or not a directory, return a readiness blocker.
- All final output paths must resolve under the latest project folder.
- Final file names must be produced by a package filename planner, not copied from staging technical filenames.
- Package mode must not create `ProjectOutputRecord` rows for the package itself or for any of the three generated artifacts.

## Staging And Partial Output Policy

TASK_313 must avoid writing Office gateway outputs directly into the formal project folder.

V1 must stage generated files first:

- Test Record and Fee Form should be generated into a controlled package staging directory.
- Customer Feedback may keep using its controlled generated output directory; the orchestrator treats that generated file as a staging source.
- After all staged files exist, the orchestrator resolves final targets under `Submitted Material`.
- If any target exists, no final copy is performed.
- Final copy uses no-overwrite behavior.
- If a final copy fails after earlier files were copied, the orchestrator performs best-effort cleanup only for files it created in the current run and returns a warning if cleanup is incomplete.

## Final File Naming

TASK_313 V1 must use deterministic, business-readable final names.

Package filename prefix:

- first non-empty available value from LTR number, project number, then project id
- sanitized with the same safe filename rules used by existing Office generation paths

Final names:

- `{prefix}_Test_Record.docx`
- `{prefix}_Fee_Form.xls`
- `{prefix}_Customer_Feedback_Form.xlsx`

If a final path already exists, execution blocks before final copy. Do not append suffixes and do not overwrite.

## In Scope

- Backend package execution application service.
- Thin API route for package execution.
- Dependency and API main wiring.
- Minimal extensions to existing generation services if needed to support controlled staging and no ProjectOutputRecord side effects.
- Frontend API client support for package execution.
- Workbench `ProjectPackagePreviewPanel` execute action, enabled only for ready preview state.
- Tests for context mismatch, readiness blockers, no-overwrite conflicts, staging/final placement, and UI boundary.
- Task board and documentation updates after implementation.

## Out Of Scope

- No evidence placement.
- No Application Form Word write-back.
- No public-drive publish beyond writing inside the latest configured project folder.
- No StepInstance, TestResult, image upload, report execution, AI review, permission, LAN, or multi-user scope.
- No Matrix/Fee automatic default filling.
- No generic tools page.
- No hidden package execution from Confirm Matrix, Confirm Fee, folder creation, Section 2 sync, or Customer Feedback generation.
- No package-level `ProjectOutputRecord` registration in V1.
- No artifact-level `ProjectOutputRecord` registration in package mode. Reused Test Record, Fee Form, and Customer Feedback generation paths must run in no-output-ledger mode for TASK_313.

## Frontend Preconditions

Before implementation, load `$impeccable` context and read:

- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`

The Workbench UI must stay dense and operational. The package panel may add one `Execute package` action only when the preview is ready. It must not add public-drive publish, evidence upload, Application Form write-back, or generic tool actions.

## Acceptance Criteria

- Workbench package preview shows `Execute package` only when preview status is `ready`.
- Clicking execute sends the current preview context.
- Backend rejects stale preview context with `409` and no generated final project-folder files.
- Backend rejects missing `Submitted Material` with a readiness blocker.
- Backend rejects existing final target files before copying anything to the project folder.
- Successful execution places exactly three files under the latest project folder's `Submitted Material` directory:
  - Confirmed Matrix Test Record
  - Confirmed Fee Form
  - Customer Feedback Form
- Fee Form content comes from the latest current Confirmed Fee authority snapshot, not unsaved or unconfirmed page edits.
- Customer Feedback generation does not relax TASK_311 public API output-dir safety.
- No package-level or artifact-level `ProjectOutputRecord` is registered.
- Existing TASK_306-TASK_312 behavior remains unchanged.

## Validation Plan

- `py -m pytest tests/unit/test_project_package_execute_service.py tests/integration/test_project_package_execute_api.py -q`
- `cd frontend; npm test -- --run ProjectPackagePreview ProjectWorkbench --watch=false`
- `cd frontend; npm run build`
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "project_workbench or package"`
- `git diff --check`

Browser smoke after implementation approval:

- Open an existing Project Workbench.
- Confirm package preview still appears above the Matrix workspace.
- Confirm `Execute package` is disabled or absent when preview is blocked.
- Confirm a ready preview can execute and display the three generated final paths.
- Confirm no evidence, public-drive publish, or Application Form write-back action appears.

## Stop Point

Stop after implementing TASK_313, running relevant validation, and updating the task board. Evidence placement, public-drive publish workflow, and Application Form Word write-back require later task files, plans, and explicit approval.
