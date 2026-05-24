# Markdown Management Rules

Last Updated: 2026-05-24
Owner: ConnLab task execution governance

## Purpose

Keep `docs/` and `tasks/` navigable while preserving completed-task traceability.

This document defines which Markdown files are current source of truth, which are task artifacts, and how completed task artifacts may be archived after final alignment.

## Source-Of-Truth Priority

Use this order when documents disagree:

1. `AGENTS.md`
2. `docs/task_board.md`
3. Current active or planned task file in `tasks/`
4. Current task plan in `docs/`
5. Current architecture/product guideline documents
6. Archive indexes and historical task files
7. Legacy notes, old phase plans, and external AI records

## Protected Files

Never auto-archive these files:

- `AGENTS.md`
- `README.md`
- `PRODUCT.md`
- `DESIGN.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/project_management/TASK_REVIEW_CHECKLIST.md`
- `docs/task_board.md`
- `docs/README.md`
- `docs/markdown_management_rules.md`
- `docs/task_archive_index.md`
- `docs/plan_archive_index.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- Current phase guidelines and workflow plans referenced by the active task board

## Directory Roles

`tasks/`
: Active, planned, recently completed, or not-yet-archived task files.

`tasks/completed/YYYY/`
: Archived completed task files. These files remain historical evidence and must not be edited for new scope.

`docs/`
: Current documentation, task plans awaiting archive, architecture guidelines, phase guidance, and current knowledge documents.

`docs/completed_plans/YYYY/`
: Archived completed task plan files.

`docs/archive/`
: Legacy phase plans, old blueprints, external AI logs, validation summaries, nonstandard task artifacts, and historical context not tied to the task archive helper.

## Archive Eligibility

A task artifact may be archived only when all conditions are true:

- `docs/task_board.md` says the task is complete.
- `docs/task_board.md` current active task is `none`, or the current active task is a different task.
- The task file is under `tasks/TASK_XXX*.md`.
- The plan file is under `docs/task_XXX*_plan.md`.
- The task is not being edited for review, follow-up correction, or immediate implementation.

## Archive Workflow

Use dry-run first:

```powershell
py scripts\archive_completed_markdown.py --task TASK_267 --dry-run
py scripts\archive_completed_markdown.py --all-completed --dry-run
```

Apply only after reviewing the dry-run output:

```powershell
py scripts\archive_completed_markdown.py --task TASK_267 --apply
py scripts\archive_completed_markdown.py --all-completed --apply
```

Apply mode moves eligible files and updates:

- `docs/task_archive_index.md`
- `docs/plan_archive_index.md`

## Rules For Future Task Completion

After a task is completed and the final Markdown files are aligned:

1. Update the task file status.
2. Update `docs/task_board.md`.
3. Run the relevant validation commands.
4. Run the archive helper in dry-run mode.
5. Archive with `--apply` only when the user asks for cleanup or the current task explicitly includes archive cleanup.

## Non-Goals

This rule does not require bulk migration of existing task history. Historical bulk cleanup should be a dedicated task because `docs/task_board.md` contains many historical path references.
