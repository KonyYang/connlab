# Frontend Smoke Checklist

Use this checklist after starting the backend and frontend dev servers. It is a manual guard for the Phase 5 workbench UI. It does not replace backend pytest or `npm run build`.

## Startup

1. From the repository root, run `.\scripts\run_backend.ps1`.
2. In a second PowerShell window, run `.\scripts\run_frontend.ps1`.
3. Open the Vite URL shown by the frontend script.

## Project Registry

1. Confirm the left navigation and top context bar are visible.
2. Confirm the project registry page loads without a workflow error.
3. Confirm the project table or empty state is visible.
4. Create a project with project number, product name, requestor, and optional business unit.
5. Confirm the created project appears in the registry and can be opened.

## Project Workbench

1. Confirm the project detail page opens.
2. Confirm the project summary panel shows project number, requestor, business unit, and status.
3. Confirm the workflow stepper shows only these MVP steps:
   - Application Form
   - Precheck
   - LTR
   - Project Folder
4. Confirm only the active step content is expanded in the main action panel.

## MVP Action Panels

1. Application Form: confirm the upload UI appears and accepts `.docx`.
2. Application Form: after upload, confirm extracted metadata appears.
3. Precheck: confirm the precheck panel appears and can run after upload.
4. Precheck: confirm issues appear as business-readable cards with severity, field/category, problem, expected value, and suggested action.
5. LTR: confirm the LTR panel appears and shows not registered or latest LTR status.
6. Folder: confirm the folder preview/generate panel appears.
7. Folder: confirm preview displays a tree-like summary.
8. Folder: confirm generate is disabled when preview conflicts exist.

## Scope Guard

1. Confirm Matrix is not exposed as an active feature.
2. Confirm Report generation is not exposed as an active feature.
3. Confirm AI review is not exposed as an active feature.
4. Confirm permissions, LAN deployment, and installer controls are not exposed as active features.

## Required Commands Before Merge

Run from repository root:

```powershell
.\scripts\run_tests.ps1
.\scripts\run_frontend_build.ps1
```

Equivalent frontend-only command:

```powershell
Set-Location frontend
npm run build
```
