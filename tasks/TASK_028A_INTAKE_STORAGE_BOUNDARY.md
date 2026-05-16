# TASK 028A 鈥?Intake Storage Boundary

## Goal

Create a controlled intake file storage boundary for `data/intake/{package_id}` before adding intake persistence tables.

This task prevents later `.msg`, attachment, direct `.docx`, and confirm flows from scattering path construction and file copy logic across services.

## Current Phase

`Phase 6A - Outlook Email Package Intake, Application Form Selection And Human Confirmation`

## Why This Task Is Allowed Now

`TASK_027C_REAL_MSG_SAMPLE_COMPATIBILITY` documented current `.msg` compatibility behavior. The next safe step is centralizing intake file storage before persistence, candidate scoring, API, or UI.

## Required Read Order

1. `AGENTS.md`
2. `docs/task_board.md`
3. `docs/archive/historical_plans/ConnLab_Phase6_Implementation_Plan.md`
4. this task file
5. `TASK_EXECUTION_SKILL.md`
6. `TASK_REVIEW_CHECKLIST.md`
7. `TESTING_SKILL.md`

## Scope

Implement only a storage boundary for:

- safe file name cleanup
- package root resolution
- `source/`, `attachments/`, and `snapshots/` directory resolution
- source file copy
- attachment file copy
- sha256 calculation
- non-overwriting destination names

## Requirements

- Keep storage logic under infrastructure.
- Do not create intake database tables.
- Do not create Project, ApplicationForm, SampleInfo, or FileAsset.
- Do not add API endpoints.
- Do not add UI.

## Out Of Scope

- Persistence repositories.
- Candidate scoring.
- Form selection.
- Draft creation.
- Direct `.docx` import flow.
- Matrix, Report, AI review, email sending, Outlook inbox automation.

## Acceptance Criteria

- Intake storage helper creates deterministic package directories.
- Copied files never overwrite existing files.
- sha256 is calculated consistently.
- Unit tests cover source, attachment, snapshot paths, safe filenames, and duplicate names.
- `docs/task_board.md` is updated after completion and the task stops.
