# ConnLab Browser Release Notes

This portable release is intended for Windows local-browser use.

## Requirements

- Microsoft Office is installed.
- Microsoft Edge or another modern browser is available.
- The whole release folder is copied together.

## Startup

Run `Start_ConnLab.bat`.

The application starts its local backend automatically and opens `http://127.0.0.1:8765/` in a browser. No Python, Node, npm, Vite, or manual backend/frontend startup is required on the operator computer.

This release changes only the startup shell. LTR registration, Settings, Project Workbench, and workbook behavior are the same application workflows as the normal ConnLab build.

## LTR Workbook Settings

Saving `LTR registration workbook` in Settings now also updates the local workbook write configuration used by LTR number application. Existing local operator settings are preserved.
