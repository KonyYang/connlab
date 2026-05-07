# TASK_103_APPLICATION_FORM_IMPORT_TO_EDITOR_NO_SILENT_REPLACE

## Status

done

## Purpose

Implement explicit application-form import behavior inside the single-page New Project editor.

Reference design: `docs/new_project_single_page_flow_redesign.md`.

## Scope

- Use existing backend application-form eligibility, header-gate, and parser paths.
- Valid application-form attachments show `Import`.
- Clicking `Import` fills the application editor.
- If editor data is non-empty or dirty, show replacement confirmation.
- Record imported source filename for traceability.
- Keep attachment double-click/open behavior separate from import.
- Preserve manual editor data unless the operator confirms replacement.
- Backend import remains authoritative and returns structured draft data.
- Do not generate a final Word application form in this task.

## Completion Notes

- Word attachment rows now show an explicit `Import` action.
- Attachment row selection remains preview-only; double-click opens the stored file URL through the API download helper.
- Import uses the existing authoritative `select-form` backend path, including application-form eligibility and header-gate validation.
- If the editor already contains data or unsaved edits, import requires an inline replacement confirmation.
- Manual editor data is preserved unless the operator confirms replacement.
- Confirmed replacement sends `replace_existing=true` so backend clears existing manual overrides before parsed application-form data fills the editor.
- The editor displays the imported source filename from the active review case.

## Out Of Scope

- Do not implement LTR number selection.
- Do not implement folder preview or folder creation.
- Do not implement final Word application-form generation or template migration.
- Do not add direct frontend Word inspection.

## Validation

Required:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py tests\integration\test_msg_package_intake_api.py -q
npm run build
```

Completed validation:

```powershell
py -m pytest tests\unit\test_intake_form_selection_service.py tests\unit\test_frontend_shell_files.py tests\integration\test_msg_package_intake_api.py -q
npm run build
```

Result: `73 passed`; frontend build passed.

## Stop Rule

Stop after implementation and update `docs/task_board.md`.
