# TASK_138_LTR_SUFFIX_TOKEN_STRICT_INPUT_AND_BOARD_CLEANUP

## Status

done

## Phase / Active Task Justification

- Current Phase: `Phase 10B - LTR workbook write hardening`
- Current Active Task on board: `None - TASK_137 complete, pending user decision for next task`
- Why this is allowed now: post-task review of `TASK_137` found a behavior mismatch in suffix-token validation and a stale task-board note. This is a narrow correction before opening further feature work.

## Step 1 Plan (For Review Only)

This document is the executable implementation plan for review.
No coding changes are allowed before explicit user approval.

## Review Finding Being Fixed

`Use specified LTR number` suffix-token mode is supposed to accept only strings composed of letters and digits. Current implementation normalizes whitespace before token validation, so input such as `A 9` is accepted as `A9`. That conflicts with the confirmed rule that any non-letter/non-digit character must be rejected.

`docs/task_board.md` also still contains a stale `TASK_133 LTR number rule clarification to implement when opened` section even though the rule set was implemented in `TASK_137`.

## Scope

1. Make suffix-token-only validation strict on the raw trimmed input:
   - Accept: `A9`, `sample2`, `123`
   - Reject: `A 9`, `A-9`, `A_9`, blank input
2. Keep full DL number parsing behavior unchanged:
   - `DL-YYYY-MM-NNN`
   - `DL-YYYY-MM-NNN` plus alphanumeric suffix
3. Update tests so whitespace inside suffix-token input is rejected.
4. Clean up `docs/task_board.md` stale `TASK_133` clarification section, replacing it with a completed `TASK_137` note or removing the now-implemented pending wording.

## Out Of Scope

1. No frontend/UI changes.
2. No changes to workbook transaction, backup, lock, COM gateway, or write mapping.
3. No changes to base/full specified-number classification beyond strict suffix-token validation.
4. No new LTR numbering features.

## Proposed File-Level Changes

1. `backend/modules/ltr/ltr_number_rules.py`
   - Adjust `is_alphanumeric_ltr_suffix_token()` to evaluate the raw `.strip()` value instead of `_normalize()`.
2. `tests/unit/test_ltr_number_rules.py`
   - Change `A 9` expectation from accepted to rejected.
   - Add representative rejections for underscore and internal whitespace if not already covered.
3. `docs/task_board.md`
   - Remove or rewrite the stale `TASK_133 LTR number rule clarification to implement when opened` block so future task selection is not confused by completed work.
4. `tasks/TASK_138_LTR_SUFFIX_TOKEN_STRICT_INPUT_AND_BOARD_CLEANUP.md`
   - Mark `done` after implementation and validation.

## Validation Plan

Required:

```powershell
py -m pytest tests\unit\test_ltr_number_rules.py tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py -q
py -m pytest tests\unit tests\integration -q
git diff --check
```

## Validation Result

- `py -m pytest tests\unit\test_ltr_number_rules.py tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py -q` passed (`35 passed`).
- `py -m pytest tests\unit tests\integration -q` passed (`403 passed`).
- `git diff --check` passed with LF/CRLF working-copy warnings only.

## Approval Gate

After user explicitly replies with approval, Step 2 implementation will start.
