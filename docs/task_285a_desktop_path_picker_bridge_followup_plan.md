# TASK_285A Desktop Path Picker Bridge Follow-up Plan

> Status: implemented
> Created: 2026-06-03
> Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
> Related task: TASK_285A_FILE_LOCATION_SETTINGS_SIMPLIFICATION

## 1. Goal

Add a thin Windows desktop shell integration point so the Settings page can use a fast native file/folder picker when ConnLab is opened from the desktop host.

This follow-up keeps the current web development architecture intact:

```text
Backend script starts FastAPI.
Frontend script starts Vite at localhost:5173.
Desktop shell optionally opens the same frontend URL in a desktop window.
```

The desktop shell does not replace React, FastAPI, or the existing API client. It only exposes selected local desktop capabilities to the already-running frontend.

## 2. Current Reality

The current Settings page already contains a frontend bridge contract:

```text
window.connlabDesktopPathPicker.pickExternalResourcePath(resourceType)
```

When that bridge is absent, the current browser page falls back to:

```text
React Settings button
-> frontend API client
-> POST /api/external-resources/{resource_type}/pick
-> backend LocalPathPickerService
-> tkinter filedialog
```

This fallback can open and select paths, but it is slower and visually rough because a browser action triggers a backend-side `tkinter` dialog.

## 3. Proposed User Experience

### Browser Mode

When the user opens `http://localhost:5173/settings` in a normal browser:

- The page remains a normal web page.
- No desktop bridge is available.
- The page should avoid showing slow backend picker buttons by default.
- Users can paste or type absolute paths and rely on blur/save validation.

### Desktop Shell Mode

When the user opens ConnLab through the desktop shell:

- The same React frontend is loaded.
- The shell injects `window.connlabDesktopPathPicker`.
- `Browse file` and `Browse folder` become available.
- Picker selection returns a real absolute Windows path to the Settings input.
- Existing save and validation flow remains unchanged.

## 4. Scope

### In Scope

1. Add a minimal desktop shell module that can load the existing frontend URL.
2. Add a desktop API object that exposes `pickExternalResourcePath(resourceType)`.
3. Implement native file and folder selection inside the desktop shell, not through the backend HTTP picker route.
4. Preserve existing frontend bridge contract in `frontend/src/desktop/pathPickerBridge.ts`.
5. Update Settings browse visibility so browse controls depend on the desktop bridge being present.
6. Keep the existing backend `/pick` route as compatibility or test support unless a later cleanup task removes it.
7. Add focused tests or static checks for:
   - frontend still detects `connlabDesktopPathPicker`;
   - browser mode does not require the backend picker for normal Settings use;
   - desktop shell API maps folder resources to folder selection and file resources to file selection.

### Out Of Scope

1. No one-click production packaging.
2. No automatic startup/shutdown management for backend and frontend scripts in this follow-up.
3. No installer, tray app, updater, permissions, or LAN deployment.
4. No change to Matrix, fee evaluation, Test Record, report, or approval package workflows.
5. No change to external-resource persistence semantics.
6. No replacement of FastAPI or Vite.
7. No browser extension or Chrome-specific integration.

## 5. Architecture

### Development Runtime

The expected development runtime after this task:

```text
Terminal 1: run backend server
Terminal 2: run frontend dev server
Terminal 3: run desktop shell script
```

The desktop shell loads:

```text
http://localhost:5173
```

The normal browser entry remains available for development and fallback testing.

### Future Packaged Runtime

A later packaging task may evolve the runtime into:

```text
User double-clicks ConnLab.exe
ConnLab starts or checks backend availability
ConnLab loads the built frontend
User does not manually manage localhost ports
```

That packaging behavior is not part of this follow-up.

## 6. Expected File-Level Changes

Likely new backend or desktop files:

- `backend/desktop/path_picker_api.py`
- `backend/desktop/shell.py`

Likely frontend files:

- `frontend/src/pages/SettingsPage.tsx`
- `frontend/src/desktop/pathPickerBridge.ts`
- `frontend/src/features/settings/SettingsExternalResourcesPanel.tsx`

Likely tests:

- `tests/unit/test_frontend_shell_files.py`
- `tests/unit/test_desktop_path_picker_api.py`

Optional documentation:

- `docs/task_board.md` only after implementation completion.
- A short run note if the shell command is not obvious from the code.

## 7. API Design

Frontend contract remains:

```ts
window.connlabDesktopPathPicker.pickExternalResourcePath(resourceType): Promise<string | null>
```

Desktop shell Python API shape:

```python
class DesktopPathPickerApi:
    def pickExternalResourcePath(self, resource_type: str) -> str | None:
        ...
```

Resource kind mapping should mirror `LocalPathPickerService`:

```text
project_folder_template -> folder picker
project_output_root -> folder picker
all other visible Settings resource types -> file picker
```

## 8. Risks

1. `pywebview` may not be installed in the current environment. If unavailable, the implementation should fail with a clear setup message and should not break the normal browser workflow.
2. PyWebView API exposure differs slightly by version. Tests should keep the API object small and avoid overfitting to UI internals.
3. Browser mode must not display a slow browse button when no desktop bridge exists.
4. Existing uncommitted TASK_285A files are present in the worktree. Implementation must work with them and avoid unrelated cleanup.
5. Native path selection is a Windows desktop capability. CI or headless tests should cover mapping and bridge wiring without opening a real picker dialog.

## 9. Validation Plan

Static and unit validation:

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "settings or desktop"
py -m pytest tests/unit/test_desktop_path_picker_api.py -q
```

Frontend build:

```powershell
cd frontend
npm run build
```

Manual smoke validation:

```powershell
# Terminal 1
<start backend command used by the project>

# Terminal 2
cd frontend
npm run dev

# Terminal 3
py -m backend.desktop.shell
```

Expected result:

- Normal browser mode at `http://localhost:5173/settings` remains usable.
- Desktop shell mode shows browse controls only when the bridge exists.
- Selecting a folder returns an absolute Windows folder path.
- Selected path is inserted into the row and follows the existing save/validate behavior.

## 10. Acceptance Criteria

1. Current `localhost:5173` browser architecture remains unchanged.
2. A desktop shell can load the existing frontend URL without replacing the backend or frontend dev servers.
3. The desktop shell exposes `window.connlabDesktopPathPicker.pickExternalResourcePath(...)`.
4. Settings browse controls are enabled only when the desktop bridge is available.
5. Folder resources use folder selection; file resources use file selection.
6. Picker cancellation returns `null` and does not modify the Settings path.
7. Normal browser mode does not depend on the slow backend `tkinter` picker for Settings path entry.
8. Tests cover bridge wiring and resource-kind mapping without opening real native dialogs.
9. Scope boundary is held: no packaging, no one-click startup, no fee/Matrix/report changes.

## 11. Approval Gate

Implementation starts only after explicit user approval of this plan, for example:

```text
批准执行 TASK_285A desktop path picker bridge follow-up
```
