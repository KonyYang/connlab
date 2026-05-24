# TASK_146 New Project Apply-LTR Only and Completion Handoff Plan

## Purpose

Move New Project completion back to the business boundary the user expects:
apply/register the LTR number, create/bind the Project, clear the intake
session, and hand off to Project workspace. Folder generation should be a
Project management action, not part of the New Project submit button.

## Current Behavior

The current completion path is still one combined operation:

- Frontend button text: `Apply LTR Number and Create Folder`
- Frontend hook: `useNewProjectCompletion`
- Frontend API: `completeNewProject`
- Backend route: `POST /api/intake-cases/{case_id}/complete-new-project`
- Backend service: `NewProjectCompletionService.complete`

The backend service currently:

1. confirms the intake case into a Project
2. commits/registers LTR
3. previews the project folder
4. generates the project folder
5. returns folder result fields

That means a UI label-only change would be misleading and risky.

## Design

### Backend

Revise `NewProjectCompletionService.complete` to be LTR-only:

- If the case is already linked to a confirmed project, return that project/LTR
  state instead of creating another project.
- If not linked, confirm the intake case into a Project.
- Commit/register the LTR number using the existing workbook-backed path.
- Do not call `FolderService.preview_folder`.
- Do not call `FolderService.generate_folder`.
- Return an LTR-only completion result:
  - `project_id`
  - `project_status`
  - `ltr_number`
  - workbook/action metadata already returned by the workbook commit path if
    needed by frontend

The safest idempotency policy is:

- `confirmed_project_id` already set:
  - inspect existing LTRs for that project
  - return existing project/LTR if present
  - do not create a project
  - do not write workbook again
- no confirmed project:
  - perform normal confirm + workbook commit

This avoids duplicate Projects from double-click, retry, stale browser state,
or a second call against the same case.

### API

Update `routes_new_project_completion.py`:

- Route name can remain `/complete-new-project` for compatibility.
- Response DTO should remove folder fields:
  - remove `folder_id`
  - remove `project_folder_path`
  - remove `preview_item_count`
  - remove `generated_paths`
- Error handling remains actionable.

### Frontend

Update:

- `CompleteNewProject` type in `frontend/src/api/client.ts`
- `NewProjectCompletionDock`
  - button: `Apply LTR Number`
  - loading text: `Applying LTR number...`
- `useNewProjectCompletion`
  - remove folder-specific completion text
  - on success, call current `onCompleted(projectId)`
- `IntakeInboxPage`
  - existing `onCompleted` already clears session and routes by project id;
    verify it cannot leave the completed case actionable.

### Tests

Update integration tests:

- Existing New Project completion tests should expect LTR-only completion.
- Assert no folder record is created by New Project completion.
- Assert project status is LTR-registered state, not `folder_created`.
- Add repeat-call test:
  - first completion creates one Project
  - second completion against same case returns same `project_id`
  - project count does not increase
  - workbook commit is not repeated if an LTR already exists

Update frontend static tests:

- Replace `Apply LTR Number and Create Folder` expectations with
  `Apply LTR Number`.
- Ensure folder creation copy remains in Project Workbench tests, not New
  Project completion tests.

## Risks

- Existing `complete-new-project` callers may expect folder fields.
  Mitigation: update the frontend API type and integration tests together.
- Folder-related Project status may currently be used as the signal for
  Workbench readiness.
  Mitigation: keep existing Project Workbench folder APIs and allow Workbench
  to show folder not recorded after New Project completion.
- Reusing prior workbook commit state needs care.
  Mitigation: if the case already has a confirmed project and LTR, return
  existing state without writing again.

## Validation

Run:

```powershell
py -m pytest tests\integration\test_new_project_completion_api.py tests\integration\test_ltr_workbook_write_commit_api.py tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell tests\unit\test_frontend_shell_files.py::test_task146_new_project_applies_ltr_before_project_handoff -q
```

Run:

```powershell
cd frontend
npm run build
```

Run:

```powershell
git diff --check
```

## Acceptance

- New Project applies LTR only.
- Folder is not created by New Project.
- Same intake case cannot create duplicate Projects through repeat completion.
- Successful frontend completion clears the New Project session and navigates
  to Project workspace.
- Task board is updated and no later task is started.
