# TASK_145 Phase 10C Validation and Board Sync Plan

## Purpose

Close Phase 10C after the user-completed manual smoke test and make the next
execution boundary explicit in `docs/task_board.md`.

## Current State

- Current phase: `Phase 10C - New Project intake flow friction cleanup`
- Last completed task: `TASK_144_PROJECT_SETUP_DRAFT_SCOPED_AUTOSAVE`
- Current active task before this plan: none
- User reported manual smoke testing is complete
- No `TASK_145` or next phase task existed before this planning step

## Implementation Scope

1. Update `docs/task_board.md`.
   - Mark `TASK_145` as the active validation closeout task while it is running.
   - Record Phase 10C completion notes for `TASK_140` through `TASK_144`.
   - Record the user-completed manual smoke test as manual validation evidence.
   - Record automated validation commands and results.
   - Set the next recommended action after Phase 10C.

2. Update `tasks/TASK_145_PHASE10C_VALIDATION_AND_BOARD_SYNC.md`.
   - Move status from `plan_review` to `done` only after validation and board sync.
   - Record validation results and any limitations.

3. Run targeted validation.
   - Backend/import/intake focused tests.
   - Frontend shell static checks for the New Project intake surface.
   - Frontend production build.
   - `git diff --check`.

## Proposed Test Commands

Primary targeted backend/frontend validation:

```powershell
py -m pytest tests\unit\test_outlook_msg_source_import.py tests\integration\test_msg_package_intake_api.py tests\integration\test_manual_intake_api.py tests\unit\test_intake_case_review_service.py tests\unit\test_frontend_shell_files.py -q -k "msg or intake or task102 or task103 or task142 or task143 or task144 or project_setup"
```

If the `-k` selector includes unrelated historical checks, narrow to:

```powershell
py -m pytest tests\unit\test_outlook_msg_source_import.py tests\integration\test_msg_package_intake_api.py tests\integration\test_manual_intake_api.py tests\unit\test_intake_case_review_service.py -q
py -m pytest tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell tests\unit\test_frontend_shell_files.py::test_task103_application_form_import_is_explicit_and_confirmed tests\unit\test_frontend_shell_files.py::test_task142_draft_duplicate_resolution_is_business_readable tests\unit\test_frontend_shell_files.py::test_task143_email_import_waits_for_application_form_selection -q
```

Frontend build:

```powershell
cd frontend
npm run build
```

Diff hygiene:

```powershell
git diff --check
```

## Risks

- The broad pytest selector may include stale historical frontend shell tests.
  Mitigation: narrow to the explicit Phase 10C-relevant tests and record why.
- Manual smoke details are user-reported, not independently replayed in browser
  during this task. Mitigation: document this explicitly as user-completed
  manual validation.
- Updating the board may imply a next phase. Mitigation: mark only a
  recommendation; do not activate a next phase without user approval.

## Acceptance Criteria

- `TASK_145` task file exists and records validation scope.
- `docs/task_board.md` reflects Phase 10C validation closeout.
- Automated validation results are recorded.
- Manual smoke completion is recorded as user-completed evidence.
- Current active task returns to none after completion.
- No product behavior is changed by this task.

## Stop Rule

After this plan is approved and executed, stop at Phase 10C closeout. Do not
start the next phase or next product task in the same turn.
