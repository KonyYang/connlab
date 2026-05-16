# TASK 027A 鈥?Outlook `.msg` Source Import And Minimal Metadata

## Goal

Import an Outlook `.msg` source file into controlled intake storage and read the smallest reliable mail metadata set.

This task is intentionally smaller than full `.msg` package import. Attachment extraction belongs to `TASK_027B`.

## Current Phase

`Phase 6A - Outlook Email Package Intake, Application Form Selection And Human Confirmation`

## Why This Task Is Allowed Now

`TASK_026_OFFICE_INTEGRATION_BOUNDARY` established the OfficeFacade and gateway boundary. The next safe step is source-file intake and minimal `.msg` metadata, without creating projects or extracting attachments.

## Required Read Order

1. `AGENTS.md`
2. `docs/task_board.md`
3. `docs/archive/historical_plans/ConnLab_Phase6_Implementation_Plan.md`
4. this task file
5. `TASK_EXECUTION_SKILL.md`
6. `TASK_REVIEW_CHECKLIST.md`
7. `TESTING_SKILL.md`

## Scope

Implement only:

- copying a `.msg` file into a controlled `data/intake/{package_id}/source/` location
- minimal metadata extraction through the Office/Outlook gateway boundary
- explicit error handling that keeps the original copied source when metadata parsing fails
- focused tests with synthetic or fixture-safe inputs

## Requirements

- Do not require Outlook to be open.
- Do not automate Outlook inbox.
- Do not extract attachments in this task.
- Do not create Project, ApplicationForm, SampleInfo, FileAsset, IntakePackage tables, or UI.
- Keep parsing failure actionable and non-destructive.

## Out Of Scope

- Attachment extraction.
- Candidate scoring.
- Intake persistence tables.
- API endpoints.
- Frontend UI.
- Direct `.docx` import.
- Matrix, Report, AI review, email sending, Outlook inbox automation.

## Acceptance Criteria

- `.msg` source files can be copied into controlled intake storage.
- Minimal metadata extraction is attempted through `backend/infrastructure/office/`.
- Metadata extraction failures preserve the copied source file and return clear errors.
- Unit tests cover success/failure boundaries without depending on a live Outlook client.
- `docs/task_board.md` is updated after completion and the task stops.
