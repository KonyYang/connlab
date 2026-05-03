# TASK_060_PHASE10A_SCOPE_AND_BOARD_ACTIVATION

## Status

done

## Goal

Open Phase 10A for intake entry completion and activate only the first implementation task.

## Scope

- Document that project intake normally starts from a manually imported `.msg` email package.
- Document the no-email exception path where an operator directly enters application request information.
- Add Phase 10A task sequence to `docs/task_board.md`.
- Defer copied-workbook LTR write hardening until after intake entry completion.

## Out Of Scope

- No implementation code.
- No `.msg` import UI.
- No direct manual intake form UI.
- No Outlook inbox auto-scan.
- No email sending.
- No Matrix, Report, AI review, LAN deployment, permissions, or external LTR workbook mutation.

## Validation

- Static documentation checks.
- Task board points to `TASK_061_MSG_PACKAGE_IMPORT_API_AND_FRONTEND_ENTRY` as the only active task.
