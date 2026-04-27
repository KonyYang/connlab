# TASK 025 — Phase 6 Scope Revision And Board Activation

## Goal

Open Phase 6A as a controlled implementation phase based on the real intake workflow:

```text
Outlook .msg package / direct Word application form
  -> application form selection
  -> parser draft
  -> human confirmation
  -> Project + ApplicationForm + SampleInfo + FileAsset
```

## Current Phase

`Phase 6A - Outlook Email Package Intake, Application Form Selection And Human Confirmation`

## Why This Task Is Allowed Now

Phase 5 is complete and the user explicitly approved starting Phase 6 using:

```text
docs/ConnLab_Phase6_Implementation_Plan.md
```

The plan requires this activation task before any implementation work.

## Scope

Update execution control only:

```text
docs/task_board.md
tasks/TASK_025_PHASE6_SCOPE_REVISION_AND_BOARD_ACTIVATION.md
tasks/TASK_026_OFFICE_INTEGRATION_BOUNDARY.md
tests/unit/test_phase6_scope_activation.py
```

## Requirements

- Mark Phase 6A as opened.
- Record the Phase 6A name:
  `Outlook Email Package Intake, Application Form Selection And Human Confirmation`.
- Confirm that Phase 6 supports both `.msg` import and direct `.docx` application form import.
- Confirm that one selected application form creates one project.
- Confirm parser output is draft only until human confirmation.
- Confirm OfficeFacade is the required infrastructure boundary for Office-related reading/extraction.
- Activate only `TASK_026_OFFICE_INTEGRATION_BOUNDARY`.
- Do not implement OfficeFacade code in this task.

## Out Of Scope

- No backend implementation.
- No frontend implementation.
- No database tables.
- No `.msg` parsing.
- No direct Word import implementation.
- No Project/ApplicationForm/SampleInfo creation changes.
- No Matrix, Report, AI review, Outlook inbox auto-scan, email sending, or folder template UX.

## Acceptance Criteria

- `docs/task_board.md` current phase is Phase 6A.
- `docs/task_board.md` current active task is `TASK_026_OFFICE_INTEGRATION_BOUNDARY`.
- `TASK_026_OFFICE_INTEGRATION_BOUNDARY.md` exists and defines the next implementation boundary.
- Phase 6A plan remains the controlling reference.
- Static pytest coverage verifies scope activation and forbidden future scope.
