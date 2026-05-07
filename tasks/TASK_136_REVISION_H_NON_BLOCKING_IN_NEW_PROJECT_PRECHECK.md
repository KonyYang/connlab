# TASK_136_REVISION_H_NON_BLOCKING_IN_NEW_PROJECT_PRECHECK

## Status

done

## Purpose

Make `Revision must be H` a warning-only precheck issue during New Project creation, not a blocker.

## Scope

- Keep SECTION 1 deterministic precheck.
- Change only the Revision expected-value rule from `error` to `warning`.
- Keep `Form No. must be E-3718` as blocker (`error`).
- Add/update unit tests for precheck rule levels.

## Out Of Scope

- Do not remove or weaken other required-field blockers.
- Do not change LTR/folder/workbook write logic.
- Do not add UI flow changes in this task.

## Validation

Required:

```powershell
py -m pytest tests\unit\test_intake_section1_precheck.py tests\integration\test_manual_intake_api.py -q
py -m pytest tests\unit tests\integration -q
```

Completed:

- `py -m pytest tests\unit\test_intake_section1_precheck.py tests\integration\test_manual_intake_api.py -q` passed (`12 passed`).
- `py -m pytest tests\unit tests\integration -q` passed (`394 passed`).

## Stop Rule

Stop after implementation, review checklist, validation, and `docs/task_board.md` update.
