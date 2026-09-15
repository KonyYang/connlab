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

## Fee Form XLSX generation

Fee Form download and project-folder publication now use the unique `.xlsx`
template whose name contains `FDQF-E-176` in the configured Project Folder
Template directory. Legacy `.xls` templates are not selected. Fee Form generation
is performed locally without starting Microsoft Excel, while retaining the
approved template's formulas, logo, layout, comments, and print settings.

## LTR Workbook Settings

Saving `LTR registration workbook` in Settings now also updates the local workbook write configuration used by LTR number application. Existing local operator settings are preserved.

## Support Diagnostics

The packaged server keeps rotating runtime logs under `%LOCALAPPDATA%\ConnLab\logs`. Use **Settings > Support diagnostics > Export diagnostic package** to download a privacy-bounded ZIP for support. The export does not include project files, the database, or settings files.
