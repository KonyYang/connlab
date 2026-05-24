# TASK_070_STEP_STYLE_PRECHECK_UI

## Status

done

## Goal

Redesign the New Project Precheck step UI to follow the provided reference image: a dense, polished operator workspace for source document checks, extracted key information editing, sample table review, requested testing, and confirmation toward LTR Number.

## Scope

- Update the frontend Precheck/case-review surface only.
- Use the same four-step New Project workflow vocabulary as Intake: Intake, Precheck, LTR Number, Project Folder.
- Show source document and template check summary at the top.
- Show a blocking Lab Test Request Number warning before confirmation.
- Present extracted key project/request fields as editable controls.
- Present sample information as a compact table.
- Present disposition, confidentiality, subcontracting, requested testing, additional information, and report-copy recipients.
- Keep existing API calls and backend behavior.
- Add/update static frontend guard tests.
- Update `docs/task_board.md` after validation.

## Out Of Scope

- No LTR Number allocation implementation changes.
- No Project Folder page redesign in this task.
- No real template-library update or Word document write-back.
- No new backend parser behavior.
- No Matrix, Report, AI review, LAN deployment, permissions, Outlook inbox auto-scan, email sending, or external LTR workbook mutation.

## Design Notes

- The UI should fit common 14-inch laptop screens with dense but readable controls.
- Controls that are not backed by existing backend behavior may be displayed as disabled or static operator affordances.
- The visual style should match the reference: clean blue labels, compact form controls, semantic red blocker row, and clear primary action.

## Validation

- Frontend build.
- Static frontend guard tests.

## Completion Notes

- Reworked the existing case-review page as the New Project Precheck step.
- Added source document and template check summary, a Lab Test Request Number blocker row, key information edit controls, sample table, requested testing panel, additional information, recipients, and a sticky confirmation footer.
- Existing API calls remain unchanged: load review, save field corrections, and confirm case into project.
- Template update and source-document clearing are visible disabled affordances only; no Word write-back or template-library update was added.

## Validation Result

- `npm run build` from `frontend/`: passed
- `py -m pytest tests\unit\test_frontend_shell_files.py -q`: `20 passed`
- `py -m pytest -q`: `246 passed`
- `git diff --check`: passed with line-ending warnings only
