# TASK_146 New Project Apply-LTR Only and Completion Handoff

## Status

done

## Current Phase

Phase 10D - New Project completion handoff and Project workspace boundary

## Why This Task Is Allowed

`TASK_145_PHASE10C_VALIDATION_AND_BOARD_SYNC` is complete and the board has no
active task. The user explicitly rejected prioritizing Drafts / In Progress
because it is low frequency for the real workflow, and approved shifting the
mainline back to LTR number application and project management.

The current New Project action says `Apply LTR Number and Create Folder`, but
folder creation belongs in Project management / Workbench. More importantly,
after LTR application succeeds, New Project must not retain an actionable
completed case that can be submitted again and create duplicate projects.

## Goal

Make New Project completion apply/register the LTR number and hand off to the
Project workspace without creating the project folder from New Project.

## Scope

- Rename the New Project completion action to `Apply LTR Number`.
- Change New Project completion semantics so it:
  - confirms the intake case
  - commits/registers the LTR number
  - creates or returns the formal Project
  - does not preview or generate the project folder
  - clears the current New Project session after success
  - navigates to the created/existing Project workspace
- Add backend idempotency/protection so repeat completion for the same intake
  case cannot create a second Project.
- Update API DTOs/types and frontend completion hook to reflect LTR-only
  completion.
- Leave folder creation in Project Workbench / Project management paths.
- Update tests for duplicate-submit, retry, button label, and handoff behavior.

## Out Of Scope

- Do not implement Drafts / In Progress expansion.
- Do not redesign Project Workbench folder creation beyond preserving the
  existing folder APIs.
- Do not implement Outlook inbox auto-scan or email sending.
- Do not implement Matrix, Report, AI review, LAN deployment, permissions, or
  future-scope workflows.

## Acceptance Criteria

- New Project button reads `Apply LTR Number`.
- Successful completion does not create a folder record.
- Successful completion leaves Project status at the registered-LTR stage, not
  `folder_created`.
- Project folder generation remains available through existing Project
  management / Workbench folder APIs.
- Repeating completion for the same intake case does not create a duplicate
  Project.
- Frontend clears the intake session and navigates to the Project workspace on
  completion.
- Stale or repeated frontend actions cannot keep the completed case actionable
  in New Project.

## Proposed Validation

```powershell
py -m pytest tests\integration\test_new_project_completion_api.py tests\integration\test_ltr_workbook_write_commit_api.py tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell tests\unit\test_frontend_shell_files.py::test_task146_new_project_applies_ltr_before_project_handoff -q
```

```powershell
cd frontend
npm run build
```

```powershell
git diff --check
```

## Stop Rule

Stop after this task is implemented, validated, and the task board is updated.
Do not start Project Workbench folder UX changes in the same task.

## Implementation Summary

- New Project completion now applies/registers the LTR number and returns the
  Project handoff payload without previewing or generating the project folder.
- `complete-new-project` response no longer includes folder result fields.
- Repeating completion for the same intake case returns the existing confirmed
  Project/LTR and does not create a duplicate Project.
- The frontend completion button now reads `Apply LTR Number`, with loading
  text `Applying LTR number...`.
- The frontend API type was narrowed to the LTR-only completion response.
- Project Workbench copy now treats missing folders as a project-folder workflow
  concern rather than a New Project completion concern.

## Validation Results

```powershell
py -m pytest tests\integration\test_new_project_completion_api.py -q
```

Result: `4 passed`.

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell tests\unit\test_frontend_shell_files.py::test_task146_new_project_applies_ltr_before_project_handoff -q
```

Result: `2 passed`.

```powershell
py -m pytest tests\integration\test_new_project_completion_api.py tests\integration\test_ltr_workbook_write_commit_api.py tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell tests\unit\test_frontend_shell_files.py::test_task146_new_project_applies_ltr_before_project_handoff -q
```

Result: `8 passed`.

```powershell
cd frontend
npm run build
```

Result: passed.

```powershell
git diff --check
```

Result: passed with LF/CRLF working-copy warnings only.
