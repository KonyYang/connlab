# TASK_069_STEP_STYLE_NEW_PROJECT_INTAKE_UI

## Status

done

## Goal

Redesign the New Project intake page as the first step of a four-step project creation workflow, following the provided `Intake.png` reference while preserving the current backend scope.

## Scope

- Add a horizontal four-step New Project stepper: Intake, Precheck, LTR, Folder.
- Make the Intake page assume one imported email package at a time.
- Left column:
  - import source actions
  - email/source information for the current package
  - attachment list
- Right column:
  - attachment details for the selected attachment
  - large document preview placeholder
- Only Word document attachments are selectable as the application form.
- Allow one selected Word document at a time.
- Keep direct application-form upload as an entry affordance without implementing new backend behavior if no existing endpoint fits.
- Keep current `.msg` package import API and package review navigation behavior.
- Add/update static frontend guard tests.
- Update `docs/task_board.md` after validation.

## Out Of Scope

- No Precheck page redesign in this task.
- No LTR page redesign in this task.
- No Folder page redesign in this task.
- No direct Word import backend implementation.
- No Outlook inbox auto-scan.
- No email sending.
- No external LTR workbook write hardening.
- No Matrix, Report, AI review, LAN deployment, permissions, or future-scope behavior.

## Design Notes

- The page should fit 14-inch laptop layouts.
- The user should understand that the selected Word document is the application form for the next step.
- Non-Word attachments can be inspected but not selected as the application form.
- Continue action remains bounded by current route behavior: proceed into the package review path for the imported package.

## Validation

- Frontend build.
- Static frontend guard tests.

## Completion Notes

- Reworked New Project Intake as step 1 of a four-step flow.
- The page now handles one imported email package at a time, shows email metadata, lists attachments, and lets the operator select exactly one Word attachment as the application form.
- The right-side Attachment details workspace shows selected attachment metadata and a document-preview placeholder.
- Direct application-form upload remains a visible affordance only; no backend route was added in this task.

## Validation Result

- `npm run build` from `frontend/`: passed
- `py -m pytest tests\unit\test_frontend_shell_files.py -q`: `19 passed`
- `py -m pytest -q`: `245 passed`
- `git diff --check`: passed with line-ending warnings only
