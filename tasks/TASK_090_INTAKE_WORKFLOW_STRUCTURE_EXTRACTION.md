# TASK_090_INTAKE_WORKFLOW_STRUCTURE_EXTRACTION

Status: Done

## Goal

Extract Intake workflow display logic from `IntakeInboxPage.tsx` into the `features/intake` boundary while preserving current behavior.

## Scope

- Move attachment classification, role text, mail date formatting, preview status text, and byte formatting into `features/intake/intakeSelectors.ts`.
- Move Intake source import panel JSX into `features/intake/IntakeSourcePanel.tsx`.
- Move attachment list JSX into `features/intake/AttachmentList.tsx`.
- Move attachment detail and preview JSX into `features/intake/AttachmentPreviewPanel.tsx`.
- Keep API calls, route navigation, session ownership, and import/continue orchestration in `IntakeInboxPage.tsx`.

## Out of Scope

- Do not change backend APIs, parsers, or storage.
- Do not change `.msg` attachment extraction behavior.
- Do not change Precheck, LTR, Project Folder, or route behavior.
- Do not introduce a new state management library, router, or dependency.
- Do not redesign the Intake layout.

## Acceptance Criteria

- `IntakeInboxPage.tsx` becomes a route-level coordinator instead of owning large preview/list/source JSX blocks.
- Feature components live under `frontend/src/features/intake`.
- Display selectors are pure functions and import only frontend API DTO types.
- Existing Intake behavior remains stable: Outlook import, direct Word import, attachment selection, selected Word form state, preview loading, and Continue to Precheck.
- Static frontend shell tests and production build pass.

## Validation

- `py -m pytest tests\unit\test_frontend_shell_files.py -q`, result `35 passed`.
- `npm run build` from `frontend/`, result passed.
- `py -m pytest -q`, result `290 passed`.
- `git diff --check`, result passed with CRLF working-copy warnings only.
- `IntakeInboxPage.tsx` is reduced from 664 lines to 234 lines.

## Notes

- **UX Polish (post-structure extraction)**: Intake attachment list now hides role subtitles (Supporting Attachment / Application Form Candidate) and displays long filenames as up to two medium-weight lines (font-weight: 500, -webkit-line-clamp: 2). This cleanup reduces visual density while preserving file type chips (MSG/W/PDF) and attachment selection behavior.
- **New Project Stepper Polish (post-structure extraction)**: The shared New Project workflow stepper now removes the redundant `New Project Step ...` heading row, exposes the current step through the stepper `aria-label`, keeps step labels on one line in narrow windows through horizontal overflow, and layers connector lines behind labels so they do not cross operator-readable text.
- **Attachment Details Cleanup (post-structure extraction)**: The Attachment details header no longer shows the redundant file type subtitle (Word Document / PDF Document) below the filename, reducing visual noise while keeping the file type chip visible on the left.
- **Email Information Polish (post-structure extraction)**: The Email information panel now displays From/Subject/Date values in the primary ink color (black) instead of muted gray, improving readability and matching the visual hierarchy of the Attachment details header.
- **Left Column Attachment Stretch (post-structure extraction)**: The Intake left column now keeps `Import source` and `Email information` at natural height while allowing the `Attachments` panel to consume remaining vertical space and scroll when needed. The layout uses `grid-template-rows: auto auto minmax(0, 1fr)` on `.intake-left-stack` and `grid-template-rows: auto minmax(0, 1fr)` on `.intake-attachments-panel`, with `overflow: auto` on `.attachment-list`.

## Additional Validation

- `py -m pytest tests\unit\test_frontend_shell_files.py::test_task070_precheck_step_matches_reference_workspace tests\unit\test_frontend_shell_files.py::test_task089_new_project_workflow_shell_is_shared -q`, result `2 passed`.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q`, result `35 passed`.
- `npm run build` from `frontend/`, result passed.
