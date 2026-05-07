# TASK_102_NEW_PROJECT_SINGLE_PAGE_INTAKE_APPLICATION_EDITOR

## Status

done

## Purpose

Implement the first runtime slice of the single-page New Project redesign after `TASK_101` is complete.

Reference design: `docs/new_project_single_page_flow_redesign.md`.

## Scope

- Replace the separate Intake/Precheck frontend route experience with one New Project page shell.
- Show request email source, email information, and attachments on the left.
- Show editable SECTION 1 application information on the main/right area.
- Default the editor blank after request email import.
- Persist field edits to the existing durable draft boundary.
- Render required fields with direct red field state when blank.
- Clear required state immediately when a field is filled.
- Show one disabled primary completion action with concise remaining-count copy.
- Keep request email and attachments visible as traceability context.
- Keep automatic draft behavior. Do not add multiple save buttons.
- Provide `Cancel and remove draft` only if the existing draft lifecycle API can be reused safely in this slice.
- Do not implement LTR/folder execution in this task.

## Completion Notes

- `/intake` now renders one New Project page with request source, email information, attachments, attachment preview, and editable SECTION 1 application information.
- A narrow backend endpoint prepares a blank durable application draft without importing or parsing a Word form.
- Field edits auto-save through the existing review-field draft boundary.
- Required state is shown directly on fields, sample cells, requested testing, and Yes/No required controls.
- The completion action is visible but disabled as `Apply LTR Number and Create Folder`; LTR/folder execution remains deferred to `TASK_104`.
- Application-form import remains deferred to `TASK_103`; attachment selection only changes preview/traceability context.

## Key Rules

- Attachment double-click opens/views the file only if the current download/open API supports it; otherwise keep it as a clearly planned disabled affordance.
- Application-form import may be shown as disabled or deferred in this task, but must not silently populate the editor.
- No warning/blocker panel for normal required-field state.
- Backend remains authoritative for required validation.
- No final Word application-form generation.
- Do not implement `TASK_103` import behavior or `TASK_104` completion orchestration.

## Architecture Notes

- Page composes `features/new-project` components and selectors.
- Raw `fetch()` remains only in `frontend/src/api/client.ts`.
- Frontend must not inspect Word files, Outlook files, SQLite, or folders.
- Reuse existing Intake and Precheck field configs where practical instead of duplicating field lists in the route page.

## Validation

Required:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
npm run build
```

Completed validation:

```powershell
py -m pytest tests\unit\test_new_project_application_draft_service.py tests\unit\test_frontend_shell_files.py tests\integration\test_manual_intake_api.py -q
npm run build
```

Result: `60 passed`; frontend build passed.

## Stop Rule

Stop after this frontend/API slice and update `docs/task_board.md`.
