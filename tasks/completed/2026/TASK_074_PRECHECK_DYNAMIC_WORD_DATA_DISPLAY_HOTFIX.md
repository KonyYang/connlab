# TASK_074_PRECHECK_DYNAMIC_WORD_DATA_DISPLAY_HOTFIX

## Status

done

## Goal

Fix the Precheck UI so data parsed from the selected Word application form is actually visible in the workspace, including sample rows and non-standard select values.

## Scope

- Expose parsed sample rows from the intake draft through the case-review API.
- Render parsed sample rows in the Precheck sample table instead of hard-coded reference rows.
- Render parsed additional information and requested testing text where available.
- Preserve parsed select values even when they are not in the fixed UI option list.
- Add/update focused frontend and API tests.
- Update `docs/task_board.md` after validation.

## Out Of Scope

- No parser calibration beyond display binding.
- No LTR workbook write hardening.
- No Outlook inbox auto-scan or email sending.
- No Matrix, Report, AI review, LAN deployment, permissions, or future-scope modules.

## Completion Notes

- Case review API now returns parsed `sample_rows` from the selected Word draft.
- Precheck sample table now renders parsed sample rows instead of reference mock rows.
- Precheck additional information and disposition panels now use parsed fields where available.
- Select controls preserve parsed values that are not present in the fixed option list.
- The selected Word parser path was verified against the latest runtime package in `data/connlab.sqlite3`.

## Validation Result

- `py -m pytest tests\integration\test_msg_package_intake_api.py tests\unit\test_frontend_shell_files.py -q`: `26 passed`
- `npm run build` from `frontend/`: passed
- `py -m pytest -q`: `250 passed`
- `git diff --check`: passed with line-ending warnings only
