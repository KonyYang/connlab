# TASK 027C — Real `.msg` Sample Compatibility

## Goal

Validate Outlook `.msg` source import and attachment extraction against real user-provided `.msg` samples, then document compatibility gaps.

This task hardens behavior around real Outlook files only after `TASK_027A` and `TASK_027B` established the controlled source and attachment boundaries.

## Current Phase

`Phase 6A - Outlook Email Package Intake, Application Form Selection And Human Confirmation`

## Why This Task Is Allowed Now

`TASK_027B_OUTLOOK_MSG_ATTACHMENT_EXTRACTION` added fixture-supported attachment extraction. The next controlled step is validating real `.msg` samples without adding Project creation, persistence tables, or UI.

## Required Read Order

1. `AGENTS.md`
2. `docs/task_board.md`
3. `docs/ConnLab_Phase6_Implementation_Plan.md`
4. this task file
5. `TASK_EXECUTION_SKILL.md`
6. `TASK_REVIEW_CHECKLIST.md`
7. `TESTING_SKILL.md`

## Scope

Implement only:

- compatibility probes for real `.msg` fixtures if available
- clear failure classification for unsupported `.msg` variants
- documentation of sample compatibility behavior
- tests that do not require Outlook to be open

## Requirements

- Preserve source `.msg` files even when parsing fails.
- Do not automate Outlook.
- Do not create Project, ApplicationForm, SampleInfo, FileAsset, IntakePackage tables, or UI.
- Do not silently treat failed attachment extraction as success.

## Out Of Scope

- Candidate scoring.
- Intake persistence tables.
- API endpoints.
- Frontend UI.
- Direct `.docx` import.
- Matrix, Report, AI review, email sending, Outlook inbox automation.

## Acceptance Criteria

- Real `.msg` behavior is documented as supported, unsupported, or blocked by missing fixtures.
- Unsupported variants fail clearly and non-destructively.
- Existing fixture-based `.msg` import still passes.
- `docs/task_board.md` is updated after completion and the task stops.
