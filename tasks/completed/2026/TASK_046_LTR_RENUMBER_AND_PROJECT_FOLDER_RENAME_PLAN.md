# TASK_046_LTR_RENUMBER_AND_PROJECT_FOLDER_RENAME_PLAN

## Status

done

## Goal

Support safe preview planning for LTR renumbering and the resulting project folder/file rename impacts.

## Scope

- Preview impacts when an LTR number changes after local registration or workbook sync.
- Identify affected local LTR record, project folder record, folder names, and evidence file names where current records allow it.
- Require explicit reason and operator confirmation before any future execution task.
- Block rename plans that would overwrite existing folders or files.
- Preserve old number, new number, reason, and evidence references in preview/audit data.
- Add tests with temporary directories and local records.

## Out Of Scope

- Executing destructive rename operations unless explicitly implemented by this task with safe guards.
- External workbook write or workbook row mutation.
- Folder evidence placement policy beyond rename impact preview.
- Frontend changes unless explicitly required.
- Matrix, Report, AI review, LAN deployment, permissions, or Outlook inbox auto-scan.

## Inputs

- Existing LTR records and project folder records.
- Current folder generation rules.
- Phase 7 workbook/local commit audit notes.

## Outputs

- LTR renumber/folder rename preview service or plan object.
- Tests for conflict detection and non-destructive preview behavior.
- Task board update after completion.

## Acceptance Criteria

- Preview requires old number, new number, and reason.
- Preview reports affected local records and folder paths.
- Existing target path conflicts block execution planning.
- No automatic destructive rename occurs.
- External workbook updates remain out of scope.

## Validation

- Run focused renumber/rename preview tests.
- Run related LTR/folder tests if shared paths are touched.
