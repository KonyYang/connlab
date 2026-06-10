# TASK_310_PROJECT_SECTION2_SYNC_FROM_CONFIRMED_MATRIX

Status: Complete.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

TASK_310 implementation is complete. TASK_311 requires a separate task file, executable plan, and explicit approval before implementation.

## Model Fit Assessment

GPT-5.3-codex is suitable for this task. The work is a bounded application/API/frontend integration task that connects existing Confirmed Matrix authority date fields with existing structured Application Form Section 2 fields. It requires careful scope control and stale/source semantics, but it does not require new Matrix rules, Office template design, public-drive package publishing, StepInstance execution persistence, AI review, permissions, or multi-user behavior.

## Goal

Add an explicit operator-controlled sync operation that copies schedule dates from the active Confirmed Matrix authority version into the structured Application Form Section 2 fields for the same project.

This task supports the project package preparation chain by making the Section 2 date source explicit before later Customer Feedback and package tasks.

## Current Code Reality

- Confirmed Matrix authority versions already store schedule fields:
  - `sample_received_date`
  - `estimated_completion_date`
- Structured `ApplicationForm` records already store Section 2 fields:
  - `received_date`
  - `estimated_completion_date`
- `ApplicationFormRepository.update(...)` can persist those structured fields.
- Existing Section 2 preview/write-back services already generate and write Word Section 2 values, but that Word write-back is a separate controlled operation.
- Project Workbench already shows project preparation and derived-output status, and it is the right operator surface for an explicit Section 2 sync action.

## V1 User Contract

When an operator runs Section 2 sync:

1. ConnLab reads the active Confirmed Matrix authority for the project.
2. ConnLab reads the current selected or latest Application Form record for the same project.
3. ConnLab copies:
   - `confirmed_matrix.version.sample_received_date` to `application_form.received_date`
   - `confirmed_matrix.version.estimated_completion_date` to `application_form.estimated_completion_date`
4. ConnLab never clears an Application Form field with an empty Confirmed Matrix value.
5. ConnLab reports changed, unchanged, and skipped fields in business-readable form.
6. ConnLab does not write the Word application form file in TASK_310.
7. ConnLab does not register a `ProjectOutputRecord` in TASK_310.

This operation is explicit. It must not happen automatically when Matrix is confirmed, Fee is confirmed, a folder is generated, or a package preview is opened.

## In Scope

- Add a backend application service for Confirmed Matrix to structured Section 2 sync.
- Add a thin API route for previewing sync state and executing sync.
- Reuse existing `ConfirmedMatrixAuthorityRepository` and `ApplicationFormRepository`.
- Add a compact Workbench UI entry showing sync status, source Matrix revision, current Section 2 dates, and a `Sync Section 2` action.
- Add frontend API client types/functions.
- Add focused backend, API, frontend, and static shell tests.
- Update `docs/task_board.md` after implementation.

## Out Of Scope

- No Word `.docx` Section 2 write-back in TASK_310.
- No public-drive write or package publish.
- No Customer Feedback Form generation.
- No package orchestrator.
- No Test Record generation changes.
- No Fee Evaluation or Fee Form changes.
- No Confirm Matrix behavior changes.
- No Confirm Fee behavior changes.
- No ProjectOutputRecord registration.
- No Office COM or Word gateway changes.
- No StepInstance, execution persistence, evidence placement, report generation, AI review, permissions, multi-user, or server authority migration.

## Frontend/UI Preconditions

Before implementation, because this task adds a Workbench UI action and user-facing copy, the agent must:

1. Read `AGENTS.md`.
2. Read `docs/task_board.md`.
3. Read this task file.
4. Load `$impeccable`.
5. Read `docs/02_ARCHITECTURE_RULES.md`.
6. Read `docs/frontend_architecture_rules.md`.
7. Read `docs/project_management/TASK_EXECUTION_SKILL.md`.
8. Read `docs/task_310_project_section2_sync_from_confirmed_matrix_plan.md`.
9. Wait for explicit user approval before writing implementation code.

## Source And Target Contract

Source:

- The active Confirmed Matrix authority version only.
- Unconfirmed Matrix Editor state and historical Matrix drafts are not valid sources.

Target:

- The structured Application Form record for the same project.
- V1 may update exactly one Application Form target only when the target is unambiguous. If the project has zero Application Forms, return a readiness blocker. If the project has multiple Application Forms and no existing selected-form business rule can prove which one is current, return a readiness blocker instead of guessing from repository order, `form_id`, filename, or upload time.

Date handling:

- Confirmed Matrix values must be valid ISO-like dates before sync.
- Missing source values are skipped and reported.
- Invalid source values block sync with actionable error copy.
- Target values may be overwritten only by non-empty valid source values.

## UX Requirements

- The Workbench entry must be compact and project-level, near existing preparation/status surfaces.
- It must show current state before action:
  - no active Confirmed Matrix
  - no Application Form target
  - up to date
  - changes available
  - partially available because one source date is missing
- It must explain that this updates structured Section 2 dates only and does not write the Word form.
- It must not expose Customer Feedback, package execute, public-drive publish, Test Record generation, or Fee Form actions.

## Acceptance Criteria

- Backend preview returns source Confirmed Matrix id/revision and the two source date values.
- Backend preview returns current Application Form id and current Section 2 date values.
- Backend preview classifies each field as `will_change`, `unchanged`, `skipped_missing_source`, or `blocked_invalid_source`.
- Backend sync updates only non-empty valid source fields.
- Backend sync returns changed, unchanged, and skipped field summaries.
- Backend sync rejects projects without active Confirmed Matrix authority.
- Backend sync rejects projects without an Application Form target.
- Backend sync rejects ambiguous multiple-Application-Form targets unless an existing selected-form rule is available and covered by tests.
- Backend sync requires `expected_confirmed_matrix_id` and `expected_confirmed_revision` from the preview response; mismatch returns a conflict before mutation.
- Backend sync rejects invalid Confirmed Matrix date values before mutating Application Form data.
- Workbench shows the compact Section 2 sync entry and calls preview/sync through `frontend/src/api/client.ts`.
- Workbench refreshes sync status after successful sync.
- No Word file is mutated.
- No `ProjectOutputRecord` is registered.
- No package, Customer Feedback, Test Record, Fee Form, evidence, or public-drive action is introduced.

## Required Validation

The executable plan must define exact commands. Expected coverage includes:

- Unit tests for sync preview, no-op, update, missing source, invalid source, missing authority, and missing Application Form.
- API integration tests for preview and sync endpoints.
- Frontend tests for Workbench Section 2 sync status and action.
- Static shell tests proving no package/Test Record/Fee Form/Customer Feedback/evidence action is introduced by TASK_310.
- `cd frontend; npm test -- --run ProjectWorkbench --watch=false`.
- `cd frontend; npm run build`.
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "project_workbench or section2"`.
- `git diff --check`.

## Stop Point

After TASK_310 implementation and validation, stop. Do not proceed to TASK_311 without a separate task file / executable plan review and explicit approval.
