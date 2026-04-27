# TASK 028B — IntakePackage / IntakeAsset / IntakeCase Storage

## Goal

Add persistence for Phase 6 intake records after the controlled file storage boundary exists.

This task introduces intake database structures only. It must not add API endpoints, UI, candidate scoring, form confirmation, or project creation flow.

## Current Phase

`Phase 6A - Outlook Email Package Intake, Application Form Selection And Human Confirmation`

## Why This Task Is Allowed Now

`TASK_028A_INTAKE_STORAGE_BOUNDARY` centralized file storage for intake packages. The next controlled step is storing package, asset, case, and draft metadata in SQLite.

## Required Read Order

1. `AGENTS.md`
2. `docs/task_board.md`
3. `docs/ConnLab_Phase6_Implementation_Plan.md`
4. this task file
5. `TASK_EXECUTION_SKILL.md`
6. `TASK_REVIEW_CHECKLIST.md`
7. `TESTING_SKILL.md`

## Scope

Add persistence for:

- `IntakePackage`
- `IntakeAsset`
- `IntakeCase`
- `IntakeDraft`

## Requirements

- New tables must be created by existing `init_db()`.
- Repository tests must cover create/get/list/update.
- Do not break existing Project/FileAsset semantics.
- Do not create Project, ApplicationForm, SampleInfo, or FileAsset records in this task.
- Do not add API endpoints or frontend UI.

## Out Of Scope

- `.msg` import implementation changes.
- Candidate scoring.
- Form selection.
- Draft parser generation.
- Confirm-to-project flow.
- Direct `.docx` import flow.
- Matrix, Report, AI review, email sending, Outlook inbox automation.

## Acceptance Criteria

- Intake tables are included in SQLAlchemy metadata.
- Repository tests pass against temporary SQLite.
- Existing repository/API tests still pass.
- `docs/task_board.md` is updated after completion and the task stops.
