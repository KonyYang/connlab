# TASK_137_LTR_SPECIFIED_NUMBER_RULES_AND_YEAR_MONTH_GUARDS

## Status

done

## Phase / Active Task Justification

- Current Phase: `Phase 10B - LTR workbook write hardening`
- Current Active Task on board: `None - TASK_136 complete, pending user decision for next task`
- Why this is allowed now: `docs/task_board.md` explicitly marks LTR specified-number rule clarification as the next controlled direction to implement when opened.

## Step 1 Plan (For Review Only)

This document is the executable implementation plan for review.
No coding changes are allowed before explicit user approval.

## Purpose

Harden `Use specified LTR number` classification and commit guards so workbook write behavior matches operator intent, including cross-year duplicate prevention and year/month boundary handling.

## Confirmed Business Baseline

1. Base number format is `DL-YYYY-MM-NNN`.
2. Manual input types:
   - Base number (e.g. `DL-2026-05-001`)
   - Full number with suffix (e.g. `DL-2026-05-001A1`)
   - Alphanumeric suffix token only (e.g. `A1`, `SAMPLE2`)
3. Input containing non-alphanumeric token characters (for suffix-token mode) must be rejected.
4. Rule correction accepted by user: creation of `base + suffix` is allowed even when base did not pre-exist (through auto-allocation path).

## Scope

1. Extend specified-number parsing/classification in commit flow.
2. Apply validation and lookup branches by input category:
   - Base number: must match format, must exist in workbook for replacement path, else reject.
   - Full base+suffix: if full exists -> replacement path; if full missing and base exists -> ask/allow associated creation path; if base missing -> reject this branch.
   - Suffix token only: allocate next base number then append suffix.
3. Add year-sheet/month sequence guards:
   - On Jan 1 or when target year sheet missing, enforce existing controlled year-sheet bootstrap mechanism (no silent create).
   - Monthly non-associated base sequence starts at `001` for each month.
4. Add duplicate guard across relevant sheets:
   - Exact full-number duplicate check across current and prior-year sheets when associated creation references prior-year base.
5. Keep lock/backup/short transaction guarantees unchanged.

## Out Of Scope

1. No new frontend workflow redesign.
2. No Matrix/Report/AI review/Outlook auto-scan/email sending.
3. No change to unrelated precheck/project creation rules.

## Proposed File-Level Changes

1. `backend/application/ltr_workbook_write_commit_service.py`
   - Add/adjust specified-number classification branches and decision outcomes.
   - Wire year/month guard checks into existing commit orchestration.
2. `backend/application/ltr_number_rules.py` (or existing number-rule module)
   - Centralize parse/validate helpers for:
     - base format `DL-YYYY-MM-NNN`
     - full base+suffix format
     - suffix-token-only format `[A-Za-z0-9]+`
3. `backend/infrastructure/office/excel_com_ltr_workbook_gateway.py` and/or workbook snapshot gateway
   - Ensure cross-sheet visible-number scan API can query:
     - current year sheet
     - prior year sheet
     - exact-full-number existence
4. API DTOs if needed:
   - keep backward compatibility; only add fields when required for operator confirmation messaging.
5. Tests:
   - `tests/unit/test_ltr_number_rules.py`
   - `tests/unit/test_ltr_workbook_write_commit_service.py`
   - `tests/integration/test_ltr_workbook_write_commit_api.py`

## Detailed Execution Design

1. Input classification priority:
   1) try base format `DL-YYYY-MM-NNN`
   2) try full base+suffix (`DL-YYYY-MM-NNN` + alnum suffix)
   3) try suffix-token-only `[A-Za-z0-9]+`
   4) otherwise reject with actionable message
2. Base input branch:
   - if base invalid -> reject
   - if base exists in workbook -> replacement candidate returned
   - if base missing -> reject (no creation from explicit base branch)
3. Full input branch:
   - if full exists -> replacement candidate returned
   - else if base exists -> associated creation candidate returned
   - else reject
4. Suffix-token-only branch:
   - allocate next monthly base (`DL-YYYY-MM-NNN`) from workbook-visible numbers
   - append suffix, then duplicate-check exact full number
5. Year-sheet guard:
   - if target year sheet absent -> require existing bootstrap-ack path to create before write
6. Cross-year duplicate guard:
   - for associated creation referencing prior-year base, check exact full number in both prior and current year sheets before write

## Risks And Mitigations

1. Risk: ambiguous classification between full/base/suffix.
   - Mitigation: strict parser order and explicit error messages.
2. Risk: duplicate scan misses hidden/legacy rows.
   - Mitigation: reuse existing workbook-visible scan abstraction; add tests with representative fixtures.
3. Risk: behavior drift in existing commit API.
   - Mitigation: preserve response contracts; add backward-compatible fields only.

## Validation Plan

Required:

```powershell
py -m pytest tests\unit\test_ltr_number_rules.py tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py -q
py -m pytest tests\unit tests\integration -q
```

Manual spot checks:

1. Base input existing/missing.
2. Full input existing/base-existing/base-missing.
3. Suffix token valid/invalid characters.
4. Cross-year associated creation duplicate prevention.
5. Missing target year sheet with bootstrap disabled/enabled+ack.

## Validation Result

- `py -m pytest tests\unit\test_ltr_number_rules.py tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py -q` passed (`33 passed`).
- `py -m pytest tests\unit tests\integration -q` passed (`401 passed`).

## Approval Gate

After user explicitly replies with approval, Step 2 implementation will start.
