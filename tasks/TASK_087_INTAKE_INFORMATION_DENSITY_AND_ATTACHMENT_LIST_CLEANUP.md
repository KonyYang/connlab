# TASK_087 Intake Information Density And Attachment List Cleanup

## Status

Done

## Phase

Phase 10A - Intake Entry Completion

## Goal

Make the New Project Intake page more suitable for real business use by reducing redundant copy, tightening the email summary, and simplifying the attachment list without changing the intake workflow.

## Inputs

- Imported Outlook `.msg` package metadata.
- Direct Word application-form import metadata.
- Stored intake package assets.
- Existing Intake session state.

## Outputs

- Intake email summary shows only sender email, subject, and message/import date.
- Attachment list prioritizes file name and application-form selection.
- Redundant separate attachment type and size columns are removed from the list.
- Application-form selection guidance is placed near the Continue action.
- Import API response exposes package `received_at` so the UI can show the actual message date when available.

## Allowed Scope

- Update `IntakePackageImportResponse` and frontend DTOs with optional `received_at`.
- Update `IntakeInboxPage.tsx` copy, formatting helpers, and attachment row markup.
- Update `intake-inbox.css` for the simplified layout.
- Add or update focused tests for this behavior.
- Update `docs/task_board.md` when complete.

## Out Of Scope

- Attachment preview expansion for images, Excel, non-application Word, or nested `.msg` files.
- Full New Project workflow shell unification across Intake and Precheck.
- Precheck page layout or business behavior.
- Intake route structural extraction into feature components.
- Outlook inbox auto-scan, email sending, copied workbook writes, Matrix, Report, AI review, LAN deployment, or permissions.

## Acceptance Criteria

- `Upload application form` continues using the backend direct Word import endpoint.
- Email information no longer shows a verbose sender name/source-file block.
- Attachments list no longer renders separate visible type and file-size columns.
- File names remain the primary attachment list text.
- The Continue area tells the operator which Word application form is selected or what is missing.
- No direct `fetch()` is added outside `frontend/src/api/client.ts`.
- Targeted backend/frontend static tests pass.
- `npm run build` passes.
- Full pytest suite passes if feasible.

## Hotfix Notes

- Real Outlook `.msg` sender extraction now prefers SMTP addresses over Exchange X.500 paths when both are available.
- Outlook RFC-style date headers are parsed and surfaced through the existing `received_at` import response field.
- The Intake date display formats parseable timestamps for operators.
- Word application-form selection no longer uses radio controls; clicking a Word attachment row selects it and the active row highlight is the visible selection state.
