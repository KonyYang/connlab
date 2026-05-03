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
4. Create a project with product name, requestor, and optional business unit. Project number is optional metadata.
5. Confirm the created project appears in the registry and can be opened.

## Project Workbench

1. Confirm the project detail page opens.
2. Confirm the project summary panel shows product name, optional project reference, requestor, business unit, and status.
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

## Phase 9 Operator Workflow Wiring

1. Project lookup: confirm the Read-only lookup panel can search by LTR, part, product, or requestor.
2. Project lookup: confirm sample summary and testing condition/method summary are read-only.
3. LTR: confirm readiness blockers, review-required fields, and placeholders appear before preview.
4. LTR: confirm preview copy states no workbook write has occurred.
5. LTR: confirm local commit requires operator confirmation and is blocked by lifecycle guard reasons.
6. Intake package detail: confirm no-form and multi-form outcomes are visible.
7. Intake case review: confirm missing-information blockers are visible before project creation.
8. Folder evidence: confirm evidence preview lists email, selected application form, attachments, specifications, LTR evidence, and correction evidence categories.
9. Folder evidence: confirm conflicts block execution and No-overwrite behavior is visible.
10. Lifecycle guards: confirm blocked LTR, folder, and evidence actions show inline reasons instead of relying on hidden modal guidance.

## Phase 10A Intake Entry Completion

1. Intake: confirm the `.msg` import control is visible and does not imply Outlook inbox auto-scan.
2. Intake: import an exported `.msg` file and confirm the latest import summary shows source email and candidate forms.
3. Package detail: confirm source context, stored assets, candidate assets, no-form outcome, multi-form outcome, and created case summaries use real package data.
4. Manual intake: create a no-email manual intake and confirm it creates a package/case review path before project creation.
5. Manual intake: leave product name or requester blank and confirm missing required fields are visible.
6. Case review: confirm email-import and manual-intake cases use the same review page.
7. Case review: confirm source context, reviewed fields, operator notes, and confirmation blockers are visible.
8. Case review: confirm the project creation button is disabled until required fields are present and the operator confirmation checkbox is checked.
9. Case review: confirm one reviewed case creates one Project only after explicit operator confirmation.
10. Scope guard: confirm copied-workbook LTR write hardening, external workbook mutation, Outlook inbox auto-scan, email sending, Matrix, Report, AI review, permissions, and LAN deployment are not exposed as active UI.

## Phase 10A Stabilization: Intake Attachment Preview

1. Intake: import one exported `.msg` package that contains at least one Word Laboratory Testing Request and at least one non-Word attachment.
2. Intake: click each attachment and confirm `Attachment details` updates for that selected attachment.
3. Intake: click the Word `.docx` application form and confirm the preview shows structured Laboratory Testing Request fields, sample rows, and requested testing information.
4. Intake: click a non-Word attachment and confirm the preview shows a clear unsupported or metadata-only state instead of the previous fake document preview.
5. Intake: confirm the Word radio selection still controls which application form proceeds to Precheck.
6. Intake to Precheck: select the Word file, continue to Precheck, and confirm Precheck uses the same selected Word data.

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
