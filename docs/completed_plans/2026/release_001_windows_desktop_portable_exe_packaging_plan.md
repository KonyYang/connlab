# RELEASE_001 Windows Desktop Portable EXE Packaging Plan

> Status: implemented
> Created: 2026-06-30
> Related task: `tasks/RELEASE_001_WINDOWS_DESKTOP_PORTABLE_EXE_PACKAGING.md`

## 1. Discovery Gate

Current phase:

- `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

Current active task/lane:

- None after `TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH`.

Current role:

- Planner.

Why allowed:

- The user is asking for release packaging so non-programmers can run ConnLab on another computer. This is release engineering and should be kept outside product feature mainline tasks.

User goal restatement:

- The user wants a repeatable developer workflow to publish ConnLab as a Windows desktop app.
- The target operator should not need to understand Python, Node, frontend/backend servers, PowerShell, or development startup.
- The target computer already has Microsoft Office and Edge installed.
- Release artifacts should be clearly named with date or version so frequent delivery remains understandable.

Evidence read:

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/project_management/TASK_REVIEW_CHECKLIST.md`
- `README.md`
- `docs/packaging_notes.md`
- `docs/task_285a_desktop_path_picker_bridge_followup_plan.md`
- `backend/desktop/shell.py`
- `scripts/run_desktop_shell.ps1`
- `scripts/run_frontend_build.ps1`
- `pyproject.toml`
- `frontend/package.json`
- `frontend/vite.config.ts`

Confirmed by user:

- Target machines have Microsoft Office.
- Target machines have Edge.
- The operator should be able to copy/open ConnLab like an ordinary application.
- The EXE name should include date or version.
- The user wants experienced release management choices handled by Codex.

Confirmed by repository evidence:

- Current runtime is development-oriented: backend and frontend are separate processes.
- Current desktop shell loads Vite at `http://localhost:5173`.
- Current packaging docs explicitly say there is no installer or PyInstaller bundle yet.
- The project already has PyWebView as an optional desktop dependency.
- The frontend can be built with `npm run build`.

Planner assumptions:

- A portable folder is preferable to an installer for the first release line.
- One-folder PyInstaller packaging is preferable to one-file packaging because it starts faster and is easier to inspect/debug.
- Packaged user data should live under `%LOCALAPPDATA%\ConnLab`, not inside the copied release folder.
- The release should keep a stable `ConnLab.exe` convenience copy alongside a versioned executable.

Not yet confirmed:

- Whether WebView2 Runtime is guaranteed on every target machine. Edge is installed, but some Windows environments can still lack the WebView2 runtime required by PyWebView's Edge Chromium backend.
- Whether the user wants release ZIP generation in the first implementation, or only a release folder.

Decision:

- Continue with the explicit assumption that first implementation produces a portable release folder and optionally a ZIP only if local tooling supports it safely.
- Treat WebView2 absence as an operator-facing error message / prerequisite note, not as an installer responsibility in RELEASE_001.

## 2. Implementation Scope

Implement the first portable release path only:

```text
Developer script builds a release folder.
Operator copies the folder.
Operator double-clicks the versioned ConnLab EXE.
ConnLab opens a desktop window and starts its local API internally.
```

No installer, updater, LAN deployment, user permissions, or business feature changes.

## 3. Runtime Architecture

Development mode remains unchanged:

```text
scripts/run_backend.ps1
scripts/run_frontend.ps1
scripts/run_desktop_shell.ps1
```

Packaged mode adds a separate entry point:

```text
ConnLab_<date>_v<version>.exe
  -> backend.desktop.packaged_launcher
  -> starts FastAPI internally
  -> serves frontend/dist from packaged resources
  -> opens PyWebView window
```

The packaged frontend should use relative `/api` calls exactly as the current frontend already does. FastAPI serves both:

```text
/api/*
/health
/*
```

The `/*` static route must support React SPA fallback to `index.html`.

## 4. File-Level Plan

### Backend Desktop Runtime

Add:

```text
backend/desktop/runtime_paths.py
```

Responsibilities:

- Detect packaged vs development runtime.
- Resolve bundled frontend static directory.
- Resolve user data directory under `%LOCALAPPDATA%\ConnLab`.
- Provide environment defaults for database, projects, templates, and logs.

Add:

```text
backend/desktop/packaged_static.py
```

Responsibilities:

- Mount built frontend static files into FastAPI.
- Return `index.html` for SPA routes.
- Keep `/api` routes owned by existing API modules.

Add:

```text
backend/desktop/packaged_launcher.py
```

Responsibilities:

- Start the FastAPI app on `127.0.0.1` using an available port.
- Open PyWebView to the local packaged URL.
- Inject existing desktop bridge functions where needed.
- Stop the server when the window closes.
- Show clear startup errors if static frontend files or desktop runtime are missing.

### Packaging

Add:

```text
packaging/connlab_desktop.spec
```

Responsibilities:

- Use PyInstaller one-folder mode.
- Include backend package.
- Include built frontend `frontend/dist`.
- Include needed template/default documentation files only when safe.
- Name output using release script parameters.

### Scripts

Add:

```text
scripts/build_windows_desktop_release.ps1
```

Responsibilities:

- Read project version from `pyproject.toml`.
- Compute release date from local date.
- Build frontend.
- Run focused Python tests.
- Run PyInstaller.
- Create release folder under `dist_release\ConnLab_<date>_v<version>`.
- Produce both:
  - `ConnLab_<date>_v<version>.exe`
  - `ConnLab.exe`
- Copy operator README and release notes.
- Print final release path.

Add:

```text
scripts/smoke_windows_desktop_release.ps1
```

Responsibilities:

- Check release folder shape.
- Check versioned EXE exists.
- Optionally launch the EXE for manual smoke.
- Avoid deleting user data.

## 5. Versioning And Naming

Use project version from `pyproject.toml`:

```text
version = "0.1.0"
```

Default artifact names:

```text
ConnLab_20260630_v0.1.0/
ConnLab_20260630_v0.1.0.exe
ConnLab.exe
```

The versioned EXE is for traceability. The stable `ConnLab.exe` is for convenience. This is the lowest-friction pattern for non-programmers while still making releases auditable.

## 6. User Data Policy

Packaged mode must default to:

```text
%LOCALAPPDATA%\ConnLab\data
%LOCALAPPDATA%\ConnLab\projects
%LOCALAPPDATA%\ConnLab\templates
%LOCALAPPDATA%\ConnLab\logs
%LOCALAPPDATA%\ConnLab\config
```

Rationale:

- Operators can replace the release folder without deleting work data.
- Multiple release folders do not create multiple accidental databases.
- The release folder remains mostly application code, not mutable business data.

No script may recursively delete `%LOCALAPPDATA%\ConnLab`.

## 7. Validation Plan

Before implementation completion:

```powershell
py -m pytest tests\unit\test_desktop_packaged_runtime_paths.py tests\unit\test_desktop_packaged_static.py -q
npm run build
.\scripts\build_windows_desktop_release.ps1
.\scripts\smoke_windows_desktop_release.ps1
```

Manual smoke:

1. Double-click the versioned EXE in the release folder.
2. Confirm the ConnLab window opens.
3. Confirm no separate backend/frontend PowerShell windows are required.
4. Confirm a known page loads.
5. Confirm at least one API-backed view can fetch data or show a controlled empty state.
6. Copy the release folder to a second Windows machine with Office and Edge and repeat.

## 8. Risks And Controls

Risk: WebView2 missing even though Edge is installed.

- Control: document prerequisite and show a clear startup error.

Risk: packaged static frontend path is wrong.

- Control: add unit tests for static path resolution and release folder smoke checks.

Risk: release overwrites operator data.

- Control: store data in `%LOCALAPPDATA%\ConnLab`; release scripts only touch build output directories.

Risk: one-file PyInstaller startup is slow or opaque.

- Control: use one-folder mode first.

Risk: packaging accidentally changes product behavior.

- Control: no product workflow changes in RELEASE_001; existing development mode must remain unchanged.

## 9. Acceptance Criteria

1. Developer can produce a release folder using one script.
2. Release folder contains a versioned EXE and stable `ConnLab.exe`.
3. Operator can start ConnLab by double-clicking the EXE.
4. No manual backend/frontend startup is required.
5. Target machine does not need Python, Node, npm, or Vite.
6. Data is stored outside the release folder.
7. Existing development scripts still work.
8. Scope boundaries hold: no business feature implementation.

## 10. Approval Gate

The user approved implementation on 2026-06-30.

Suggested approval phrase:

```text
批准 RELEASE_001，按这个方案实现。
```

## 11. Implementation Result

RELEASE_001 was implemented on 2026-06-30.

Implemented files:

```text
backend/desktop/runtime_paths.py
backend/desktop/packaged_static.py
backend/desktop/packaged_launcher.py
packaging/connlab_desktop.spec
packaging/README_FOR_OPERATOR.md
packaging/RELEASE_NOTES.md
scripts/build_windows_desktop_release.ps1
scripts/smoke_windows_desktop_release.ps1
tests/unit/test_desktop_packaged_runtime_paths.py
tests/unit/test_desktop_packaged_static.py
tests/unit/test_desktop_release_scripts.py
```

Updated:

```text
pyproject.toml
docs/packaging_notes.md
docs/task_board.md
```

Validated:

```powershell
py -m pytest tests\unit\test_desktop_packaged_runtime_paths.py tests\unit\test_desktop_packaged_static.py tests\unit\test_desktop_release_scripts.py tests\unit\test_packaging_notes.py -q
npm run build
.\scripts\build_windows_desktop_release.ps1
.\scripts\smoke_windows_desktop_release.ps1
```

Release artifact generated:

```text
dist_release\ConnLab_20260630_v0.1.0
```

Manual second-machine smoke remains required before this release is treated as operator-proven.
