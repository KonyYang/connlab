# TASK_090_MANUAL_OVERRIDES_SELECTION_HOTFIX

Status: Done

## Goal

Fix Intake form reselection so saved Precheck manual edits are preserved only when the operator continues with the same selected application form asset.

## Scope

- Keep manual overrides when the selected asset already has its own existing case/draft.
- Clear manual overrides when an existing reusable case is rebound to a different selected asset.
- Do not change frontend flow, API request/response contracts, or add confirmation UI.

## Validation

- `py -m pytest tests\unit\test_intake_form_selection_service.py tests\integration\test_msg_package_intake_api.py tests\unit\test_frontend_shell_files.py -q`, result `50 passed`.
- `npm run build` from `frontend/`, result passed.
- `py -m pytest -q`, result `292 passed`.
- `git diff --check`, result passed with CRLF working-copy warnings only.
