# RELEASE_003 Local Browser Server Packaging

Status: implemented

Date: 2026-07-01

## Scope

Create a portable Windows browser-style release folder for ConnLab. Operators
double-click `Start_ConnLab.bat`, which starts a local server on
`http://127.0.0.1:8765/` and opens the browser.

## Allowed Changes

- Add packaged local web server launcher.
- Add PyInstaller browser server spec.
- Add browser release build and smoke scripts.
- Add browser operator README and release notes templates.
- Add release static tests.

## Explicit Non-Scope

- No LTR registration workflow changes.
- No LTR workbook write settings bridge.
- No Settings page structure changes.
- No `frontend/src/api/client.ts` business API changes.
- No Project Workbench business workflow changes.
- No installer, Windows service, LAN deployment, permissions, or multi-user scope.

## Runtime Data Rule

Mutable operator data remains under:

```text
%LOCALAPPDATA%\ConnLab
```

The browser release folder contains application code only and can be replaced
without deleting local database, logs, project files, or user settings.

## Expected Output

```text
dist_release\
  ConnLab_Web_YYYYMMDD_v0.1.0\
    Start_ConnLab.bat
    ConnLab_Server.exe
    README_FOR_OPERATOR.md
    RELEASE_NOTES.md
    _internal\
```

## Validation

- Focused release script/static tests.
- Browser release folder smoke script.
- Packaged `ConnLab_Server.exe` HTTP smoke when build output is available.
