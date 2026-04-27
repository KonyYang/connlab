# TASK 027B — Outlook `.msg` Attachment Extraction

## Goal

Extract attachments from an imported Outlook `.msg` source and produce a basic asset list.

This task builds on `TASK_027A`, which only preserves the `.msg` source file and reads minimal metadata.

## Current Phase

`Phase 6A - Outlook Email Package Intake, Application Form Selection And Human Confirmation`

## Why This Task Is Allowed Now

`TASK_027A_OUTLOOK_MSG_SOURCE_IMPORT_AND_MINIMAL_METADATA` preserves `.msg` source files in controlled intake storage. The next controlled step is extracting attachments without creating projects, selecting forms, or writing intake persistence tables.

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

- attachment extraction from already imported `.msg` sources when a parser can provide attachments
- storing extracted attachments under `data/intake/{package_id}/attachments/`
- basic file classification for extracted attachments
- original name, stored path, extension, size, and sha256 metadata

## Requirements

- Do not require Outlook to be open.
- Do not automate Outlook inbox.
- Do not automatically select an application form.
- Do not create Project, ApplicationForm, SampleInfo, FileAsset, IntakePackage tables, or UI.
- Preserve source `.msg` files even if attachment extraction fails.

## Out Of Scope

- Real sample compatibility hardening beyond basic fixtures.
- Candidate scoring.
- Intake persistence tables.
- API endpoints.
- Frontend UI.
- Direct `.docx` import.
- Matrix, Report, AI review, email sending, Outlook inbox automation.

## Acceptance Criteria

- Attachments can be extracted into controlled intake storage for supported fixture inputs.
- Extracted attachments include basic metadata and sha256.
- Unsupported or malformed `.msg` inputs fail clearly and non-destructively.
- No Project or intake database rows are created.
- `docs/task_board.md` is updated after completion and the task stops.
