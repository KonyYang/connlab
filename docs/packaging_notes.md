# ConnLab Packaging Notes

Status: MVP local-development runbook only.

## Current Supported Mode

ConnLab currently runs as two local development processes:

- FastAPI backend on `http://127.0.0.1:8000`.
- Vite React frontend with `/api` proxied to the backend.

This is intentional for MVP validation. There is no installer, Windows service, PyInstaller bundle, or PyWebView shell yet.

## Local Startup Scripts

- `scripts\init_db.ps1`: initializes the SQLite schema using the configured database path.
- `scripts\run_backend.ps1`: starts the FastAPI backend with `uvicorn`.
- `scripts\run_frontend.ps1`: installs frontend dependencies if missing, then starts Vite.
- `scripts\run_mvp_dev.ps1`: opens backend and frontend scripts in separate PowerShell windows.

## Runtime Assumptions

- Windows is the primary target.
- Python 3.11+ is required.
- Node.js/npm are required for frontend development.
- SQLite is local file storage.
- Microsoft Office is assumed for realistic lab document handling, but current MVP code must avoid direct UI/API Office automation.

## Data Locations

Default paths from repository root:

- `data\connlab.sqlite3`
- `projects\`
- `templates\`
- `logs\`

Environment overrides:

- `CONNLAB_DATA_DIR`
- `CONNLAB_PROJECTS_DIR`
- `CONNLAB_TEMPLATES_DIR`
- `CONNLAB_DATABASE_PATH`
- `CONNLAB_LOG_LEVEL`

## Local Secret And Workbook Settings Policy

External LTR workbook settings are operator-managed local settings. The committed
`connlab.local.example.toml` contains placeholders only. The real
`connlab.local.toml` file is ignored by Git and must stay local to the workstation.

Current short-term supported inputs:

- `connlab.local.toml` under `[ltr_workbook]`
- `CONNLAB_LTR_WORKBOOK_*` environment variable overrides

Rules:

- Do not hard-code the workbook modify password in source, tests, docs screenshots, or committed config.
- Do not log `modify_password`; use the redacted `safe_summary()` diagnostic shape.
- Keep `lock_timeout_seconds` and `sheet_bootstrap_clear_start_row` positive integers.
- Keep write mode disabled unless a later approved task enables a guarded write path.
- Future Windows Credential Manager integration must be a separate task and should replace, not duplicate, plaintext local password handling.

## Future Packaging Placeholder

PyWebView or PyInstaller packaging can be considered after MVP validation, but should be implemented as a separate task. Before that task, define:

- frontend build output location
- backend process ownership
- database migration strategy
- Office automation boundary
- user data directory strategy
- upgrade and rollback path
