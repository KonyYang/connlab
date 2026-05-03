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
