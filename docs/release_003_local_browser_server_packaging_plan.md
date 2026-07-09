# RELEASE_003 Local Browser Server Packaging Plan

Date: 2026-07-01

## Objective

Deliver ConnLab as a portable local browser release for operator machines without
administrator rights. The browser release should feel like the development
server mode while keeping application workflows unchanged.

## Design

1. Package a console server executable named `ConnLab_Server.exe`.
2. Start FastAPI with the bundled React frontend mounted as static files.
3. Bind to `127.0.0.1:8765` so operators have one predictable local URL.
4. Use `Start_ConnLab.bat` to start the server and open the browser.
5. Reuse existing packaged runtime path handling:
   `%LOCALAPPDATA%\ConnLab` remains the mutable user-data root.
6. Keep release code isolated under `backend/desktop`, `packaging`, and
   `scripts`.

## File-Level Scope

May touch:

- `backend/desktop/packaged_server.py`
- `packaging/connlab_browser_server.spec`
- `packaging/Start_ConnLab.bat`
- `packaging/README_FOR_BROWSER_OPERATOR.md`
- `packaging/RELEASE_NOTES_BROWSER.md`
- `scripts/build_windows_browser_release.ps1`
- `scripts/smoke_windows_browser_release.ps1`
- `tests/unit/test_desktop_release_scripts.py`
- release documentation and task records

Must not touch:

- LTR registration and workbook write services
- Settings page structure
- `frontend/src/api/client.ts` business API helpers
- Project Workbench business flow
- database schema or migrations

## Risks

- Port `8765` may already be occupied. The first implementation uses a fixed
  port for operator predictability; support should close the old server window
  before retrying.
- Antivirus or corporate endpoint tools may scan the PyInstaller executable on
  first launch and make startup slow.
- Browser release still depends on the same application runtime behavior as the
  normal packaged build; it does not solve path or workbook permission issues.

## Acceptance

- Browser release static tests pass.
- Build script produces a `ConnLab_Web_...` folder.
- Smoke script confirms the release folder shape.
- Starting `ConnLab_Server.exe` returns the frontend at
  `http://127.0.0.1:8765/`.
- No LTR/Settings/Workbench business code is changed for this release.
