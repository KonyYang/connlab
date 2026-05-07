# TASK_129_SECRET_AND_LOCAL_SETTINGS_POLICY

## Status

done

## Purpose

Harden the local settings and secret policy for the external LTR workbook before later workbook structure probes and write gateways.

## Scope

- Keep the real LTR workbook password out of source code, tests, screenshots, and committed config.
- Continue loading short-term workbook settings from operator-managed `connlab.local.toml` or environment variables.
- Keep `connlab.local.toml` ignored by Git and keep the committed example config placeholder-only.
- Validate local settings for lock timeout and sheet bootstrap row so later lock/write tasks do not receive invalid values.
- Provide a safe settings summary that never exposes `modify_password`.
- Document the local settings policy and future Windows Credential Manager direction.

## Out Of Scope

- Do not implement Windows Credential Manager integration.
- Do not implement lock files, workbook write transactions, or backups.
- Do not probe external Excel workbook structure.
- Do not write public-drive Excel files.
- Do not add frontend UI.
- Do not implement Matrix, Report, AI review, Outlook auto-scan, email sending, LAN, or permissions.

## Validation

Required:

```powershell
py -m pytest tests\unit\test_config.py -q
py -m pytest tests\unit tests\integration -q
```

Completed:

- `py -m pytest tests\unit\test_config.py -q`, result `6 passed`.
- `py -m pytest tests\unit tests\integration -q`, result `362 passed`.

## Stop Rule

Stop after implementation and update `docs/task_board.md`.
