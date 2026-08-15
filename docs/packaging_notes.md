# ConnLab Packaging Notes

Status: MVP local-development runbook plus RELEASE_001 portable desktop release path and RELEASE_003 local browser release path.

## Current Supported Mode

ConnLab currently runs as two local development processes:

- FastAPI backend on `http://127.0.0.1:8000`.
- Vite React frontend with `/api` proxied to the backend.

This is intentional for MVP validation. The regular development workflow still uses
separate backend and frontend processes. RELEASE_001 adds a portable desktop release
path, and RELEASE_003 adds a local browser release path. There is still no MSI
installer, Windows service, auto-updater, LAN deployment, permissions system, or
multi-user deployment.
In short: no installer is provided yet; these are portable folder releases.

## Local Startup Scripts

- `scripts\init_db.ps1`: initializes the SQLite schema using the configured database path.
- `scripts\run_backend.ps1`: starts the FastAPI backend with `uvicorn`.
- `scripts\run_frontend.ps1`: installs frontend dependencies if missing, then starts Vite.
- `scripts\run_mvp_dev.ps1`: opens backend and frontend scripts in separate PowerShell windows.

## Portable Desktop Release

RELEASE_001 produces a copyable Windows desktop release folder for non-programmer
operators.

Developer setup for release builds:

```powershell
py -m pip install -e .[dev,release]
Set-Location frontend
npm install
Set-Location ..
```

Build a release from the repository root:

```powershell
.\scripts\build_windows_desktop_release.ps1
```

Expected output:

```text
dist_release\
  ConnLab_YYYYMMDDHHMM_v0.1.0\
    ConnLab_YYYYMMDDHHMM_v0.1.0.exe
    ConnLab.exe
    README_FOR_OPERATOR.md
    RELEASE_NOTES.md
    config\
      connlab.admin.example.toml
    _internal\
```

Copy the whole `ConnLab_YYYYMMDDHHMM_v...` folder to the operator computer and run
`ConnLab.exe`. The target computer does not need Python, Node, npm, Vite, or
manual backend/frontend startup. Microsoft Office and Edge/WebView2 are expected.

Smoke-check the latest release folder:

```powershell
.\scripts\smoke_windows_desktop_release.ps1
```

Optionally launch it for manual smoke:

```powershell
.\scripts\smoke_windows_desktop_release.ps1 -Launch
```

## Portable Browser Release

RELEASE_003 produces a copyable Windows local-browser release folder for
non-programmer operators. It starts ConnLab on `http://127.0.0.1:8765/` and opens
the browser, without changing LTR registration, Settings, Project Workbench, or
workbook behavior.

Build a browser release from the repository root:

```powershell
.\scripts\build_windows_browser_release.ps1
```

Expected output:

```text
dist_release\
  ConnLab_Web_YYYYMMDDHHMM_v0.1.0\
    Start_ConnLab.bat
    ConnLab_Server.exe
    README_FOR_OPERATOR.md
    RELEASE_NOTES.md
    config\
      connlab.admin.example.toml
    _internal\
```

Copy the whole `ConnLab_Web_YYYYMMDDHHMM_v...` folder to the operator computer and
run `Start_ConnLab.bat`. The target computer does not need Python, Node, npm,
Vite, or manual backend/frontend startup. Microsoft Office and a browser such as
Microsoft Edge are expected.

Smoke-check the latest browser release folder:

```powershell
.\scripts\smoke_windows_browser_release.ps1
```

## Runtime Assumptions

- Windows is the primary target.
- Python 3.11+ is required.
- Node.js/npm are required for frontend development.
- SQLite is local file storage.
- Microsoft Office is assumed for realistic lab document handling, but current MVP code must avoid direct UI/API Office automation.

## Data Locations

Default development paths from repository root:

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

Packaged desktop mode uses `%LOCALAPPDATA%\ConnLab` for mutable operator data:

- `%LOCALAPPDATA%\ConnLab\data\connlab.sqlite3`
- `%LOCALAPPDATA%\ConnLab\projects\`
- `%LOCALAPPDATA%\ConnLab\templates\`
- `%LOCALAPPDATA%\ConnLab\logs\`
- `%LOCALAPPDATA%\ConnLab\config\connlab.local.toml`

The release folder is application code. Do not store operator data in the release
folder. New release folders must not overwrite an operator's existing local
database, logs, project files, or configured paths. The release-local
`config\connlab.admin.example.toml` is a secret-free administrator template only.

## Administrator Secret And Workbook Settings Policy

Non-secret external LTR workbook paths and operating options remain operator-managed
in `connlab.local.toml`. The LTR workbook modify password is administrator-managed
and is not available through ConnLab Settings or its public API.

The packaged runtime reads the mutable administrator file at:

```text
%PROGRAMDATA%\ConnLab\config\connlab.admin.toml
```

The application never creates or writes this file or directory. An administrator
must copy `config\connlab.admin.example.toml` outside the release folder, rename it
to `connlab.admin.toml`, enter the deployment value, and apply the organization's
file-permission policy. Release replacement therefore cannot overwrite the value.

Repository/development execution defaults to `<base_dir>\connlab.admin.toml`.
`CONNLAB_ADMIN_CONFIG_PATH` may select another administrator-managed path and is the
reuse seam for a future network deployment. `CONNLAB_LTR_WORKBOOK_PASSWORD`, when
present, remains the highest-priority override, including an explicitly blank value.

One-time upgrade action: if an existing workstation previously stored
`modify_password` under `[ltr_workbook]` in `connlab.local.toml`, an administrator
must copy that value manually into the administrator file. The old local key is
inert; ConnLab does not migrate, delete, display, log, or rewrite it.

Current supported inputs are:

- non-secret LTR settings in `connlab.local.toml` under `[ltr_workbook]`
- administrator password in `connlab.admin.toml` under `[ltr_workbook]`
- `CONNLAB_LTR_WORKBOOK_*` environment variable overrides

Rules:

- Do not hard-code the workbook modify password in source, tests, docs screenshots, or committed config.
- Do not log `modify_password`; use the redacted `safe_summary()` diagnostic shape.
- Keep `lock_timeout_seconds` and `sheet_bootstrap_clear_start_row` positive integers.
- Keep write mode disabled unless a later approved task enables a guarded write path.
- Future Windows Credential Manager integration must be a separate task and should replace, not duplicate, plaintext administrator password handling.

## Future Packaging Placeholder

RELEASE_001 covers the first PyWebView + PyInstaller portable folder path.
Before moving beyond that into a full installer or managed deployment, define:

- frontend build output location
- backend process ownership
- database migration strategy
- Office automation boundary
- user data directory strategy
- upgrade and rollback path
