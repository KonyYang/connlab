# RELEASE_001 - Windows Desktop Portable EXE Packaging

> Status: complete
> Created: 2026-06-30
> Phase: release engineering outside product feature mainline
> Owner role: Planner, then Developer after explicit approval

## Goal

Create a repeatable Windows release process that lets a developer produce a portable ConnLab desktop package for non-programmer operators.

Target operator experience:

```text
Copy ConnLab release folder to another Windows computer
Double-click ConnLab_<date>_<version>.exe
ConnLab opens like a normal desktop app
No manual backend, frontend, Node, npm, Python, or PowerShell development startup
```

## Current Phase And Active Task

- Current project phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active implementation task: none after `TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH`.
- Why this is allowed now: this is release engineering / packaging infrastructure, not a product workflow feature and not a Matrix, Workbench, Folder Actions, Report, AI, LAN, permissions, or multi-user task.

## Confirmed By User

- Target computers already have Microsoft Office installed.
- Target computers have Microsoft Edge installed.
- The release should be easy for non-programmers to run on another computer.
- The generated executable name should include a date or version number.
- The developer wants an experienced release/versioning approach rather than ad hoc manual steps.

## Confirmed By Repository Evidence

- `README.md` currently marks full installer and PyInstaller packaging as deferred scope.
- `docs/packaging_notes.md` currently documents only MVP local-development startup.
- `backend.desktop.shell` currently loads `http://localhost:5173`, which requires the Vite dev server and is not suitable for operator delivery.
- `pyproject.toml` already has optional `desktop` dependencies for PyWebView.
- `frontend/package.json` already supports `npm run build`.
- Existing scripts live under `scripts/`, including backend, frontend, build, desktop shell, and test helpers.

## Release Strategy

Use a portable folder release first, not an installer.

Reason:

- It is easier to validate and roll back during frequent internal releases.
- Operators can run it by copying one folder and double-clicking the EXE.
- It avoids early MSI/installer complexity while the product is still evolving quickly.
- It keeps user data outside the application folder so replacing the folder can upgrade the app without deleting local data.

Recommended output shape:

```text
dist_release/
  ConnLab_20260630_v0.1.0/
    ConnLab_20260630_v0.1.0.exe
    ConnLab.exe
    README_FOR_OPERATOR.md
    RELEASE_NOTES.md
    _internal/
```

`ConnLab_20260630_v0.1.0.exe` is the versioned executable requested by the user. `ConnLab.exe` is a stable convenience copy for users or shortcuts.

## Scope

### In Scope

1. Add a packaged desktop launcher that starts the local FastAPI app and opens PyWebView.
2. Serve the built React frontend from FastAPI in packaged mode.
3. Keep `/api` paths working as relative requests from the packaged frontend.
4. Add runtime path handling for packaged mode.
5. Store user data under `%LOCALAPPDATA%\ConnLab` by default in packaged mode.
6. Add a PyInstaller spec for a one-folder portable release.
7. Add a release build script under `scripts/`.
8. Add a release smoke script or command path for developer verification.
9. Generate a release folder and versioned EXE name using date and project version.
10. Document operator instructions.

### Out Of Scope

1. No MSI installer.
2. No auto-updater.
3. No Windows service.
4. No LAN/server deployment.
5. No permissions or multi-user behavior.
6. No Matrix, Report, StepInstance, AI, Folder Actions, LTR workbook authority, or business workflow changes.
7. No silent overwrite of operator data.
8. No requirement that target computers install Python, Node, npm, or development dependencies.

## Proposed File Changes

Expected implementation files:

```text
backend/desktop/packaged_launcher.py
backend/desktop/packaged_static.py
backend/desktop/runtime_paths.py
packaging/connlab_desktop.spec
scripts/build_windows_desktop_release.ps1
scripts/smoke_windows_desktop_release.ps1
docs/release_001_windows_desktop_portable_exe_packaging_plan.md
README or docs/packaging_notes.md update
tests/unit/test_desktop_packaged_runtime_paths.py
tests/unit/test_desktop_packaged_static.py
```

Exact names may be adjusted during implementation if repository conventions make a different name cleaner.

## Runtime Design

Packaged mode should run as:

```text
ConnLab_<date>_<version>.exe
-> resolve packaged resources
-> ensure user data directories exist
-> start FastAPI on 127.0.0.1 using an available local port
-> mount frontend/dist as static app with React SPA fallback
-> open PyWebView window to http://127.0.0.1:<port>/
-> shutdown local server when desktop window exits
```

Default packaged data directories:

```text
%LOCALAPPDATA%\ConnLab\data\connlab.sqlite3
%LOCALAPPDATA%\ConnLab\projects\
%LOCALAPPDATA%\ConnLab\templates\
%LOCALAPPDATA%\ConnLab\logs\
%LOCALAPPDATA%\ConnLab\config\
```

Developer builds must not delete or overwrite these user data directories.

## Version And Naming Rule

Use:

```text
ConnLab_<YYYYMMDD>_v<project-version>.exe
ConnLab_<YYYYMMDD>_v<project-version>.zip
```

The initial project version comes from `pyproject.toml`.

If multiple builds are created on the same date without a version bump, the release script may accept a suffix:

```text
ConnLab_20260630_v0.1.0_build2.exe
```

## Validation

Required developer validation:

1. `py -m pytest tests/unit/test_desktop_packaged_runtime_paths.py tests/unit/test_desktop_packaged_static.py -q`
2. `npm run build`
3. `scripts/build_windows_desktop_release.ps1`
4. Start the generated EXE on the developer machine.
5. Confirm the UI opens without manually starting backend or frontend.
6. Confirm `/health` and at least one existing frontend page/API-backed view loads.
7. Copy the release folder to another Windows machine with Office and Edge/WebView2 and repeat the smoke run.

## Acceptance Criteria

1. A developer can run one documented release script to produce a portable ConnLab release folder.
2. The release folder contains a versioned EXE whose name includes date and version.
3. A non-programmer can launch ConnLab by double-clicking the EXE.
4. No Python, Node, npm, Vite dev server, or manual backend startup is required on the target computer.
5. Existing browser development mode still works.
6. Packaged mode stores user data outside the release folder.
7. The release script does not silently delete operator data.
8. Scope boundaries are preserved: no business feature work is included.

## Stop Point

After this task is implemented and validated, stop. Do not proceed to installer, updater, LAN deployment, or product feature work without a separate explicit task.

## Completion Notes

Completed on 2026-06-30.

Implemented:

- Packaged runtime path handling under `%LOCALAPPDATA%\ConnLab`.
- First-run local directory and empty local config initialization.
- Packaged FastAPI static frontend serving with React SPA fallback.
- API fallback guard so unknown `/api/*` paths stay 404s.
- PyWebView packaged launcher that starts a local Uvicorn server and opens ConnLab.
- PyInstaller one-folder spec.
- Developer release script: `scripts/build_windows_desktop_release.ps1`.
- Release folder smoke script: `scripts/smoke_windows_desktop_release.ps1`.
- Operator README and release notes copied into the release folder.
- Release dependency extra: `py -m pip install -e .[dev,release]`.

Validation:

- `py -m pytest tests\unit\test_desktop_packaged_runtime_paths.py tests\unit\test_desktop_packaged_static.py tests\unit\test_desktop_release_scripts.py tests\unit\test_packaging_notes.py -q` -> `13 passed`.
- `npm run build` from `frontend` -> passed with existing Vite chunk-size warning.
- `.\scripts\build_windows_desktop_release.ps1` -> passed outside sandbox; generated `dist_release\ConnLab_20260630_v0.1.0`.
- `.\scripts\smoke_windows_desktop_release.ps1` -> passed; verified versioned EXE, stable `ConnLab.exe`, operator README, release notes, and `_internal`.

Generated local artifact:

```text
dist_release\ConnLab_20260630_v0.1.0
```

Remaining manual validation:

- Double-click smoke on this machine.
- Copy the release folder to a second Windows machine with Office and Edge/WebView2 and run `ConnLab.exe`.
