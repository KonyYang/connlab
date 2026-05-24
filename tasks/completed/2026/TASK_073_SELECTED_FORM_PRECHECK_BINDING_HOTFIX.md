# TASK_073_SELECTED_FORM_PRECHECK_BINDING_HOTFIX

## Status

done

## Goal

Fix the Intake to Precheck bridge so the Word application form selected by the operator is the exact source used to create and open the Precheck review case.

## Scope

- Add an API endpoint that selects one intake asset as the application form for a package.
- Parse the selected `.docx` application form into the intake draft with the existing deterministic parser.
- Return the created or refreshed case id to the frontend.
- Make `Continue to Precheck` call the explicit selection endpoint instead of package-level exception review.
- Preserve app-session Intake state and pass the selected case id into the Precheck page.
- Make Precheck prefer the selected case id when several cases exist.
- Add/update focused backend and frontend guard tests.
- Update `docs/task_board.md` after validation.

## Out Of Scope

- No LTR workbook write hardening.
- No Outlook inbox auto-scan or email sending.
- No Matrix, Report, AI review, LAN deployment, permissions, or future-scope modules.
- No broad Precheck UI redesign beyond the selected-case binding and data population required by this bug.

## Validation

- Backend API/integration tests for selected form binding.
- Frontend static guard tests.
- Frontend build.
- Full pytest suite if feasible.

## Completion Notes

- Added an explicit selected-form API for `package_id + asset_id`.
- The selected `.docx` is parsed into intake draft fields before Precheck opens.
- Intake stores the returned `case_id` in app session state.
- Precheck now prefers that selected `case_id` when multiple review cases exist.
- Existing package-level exception review remains available for package detail workflows.

## Validation Result

- `py -m pytest tests\unit\test_intake_form_selection_service.py tests\integration\test_msg_package_intake_api.py -q`: `12 passed`
- `py -m pytest tests\unit\test_frontend_shell_files.py -q`: `22 passed`
- `npm run build` from `frontend/`: passed
- `py -m pytest -q`: `250 passed`
- `git diff --check`: passed with line-ending warnings only
