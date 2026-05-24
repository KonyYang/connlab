# TASK_125_FULL_TEST_SUITE_HISTORICAL_EXPECTATION_SYNC

## Status

done

## Purpose

Synchronize stale unit/integration expectations with the current ConnLab behavior so the required full suite can pass after TASK_104.

## Scope

- Update direct Word intake tests to reflect the current `.docx`-only entry rule.
- Update candidate detection repository expectations for the current document score.
- Keep form-selection repository tests focused on persistence by injecting a passing eligibility validator instead of relying on fake Word bytes.
- Update historical task-board tests so they preserve completed phase evidence without requiring the old Phase 10A active-phase header.

## Out Of Scope

- Do not change product workflow behavior unless a failing test exposes a real bug.
- Do not implement copied workbook write, Outlook auto-scan, email sending, Matrix, Report, AI review, LAN, or permissions.

## Validation

Required:

```powershell
py -m pytest tests\unit tests\integration -q
```

## Stop Rule

Stop after the suite passes and update `docs/task_board.md`.

