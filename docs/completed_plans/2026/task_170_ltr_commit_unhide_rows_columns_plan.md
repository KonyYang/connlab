# TASK_170 LTR Commit Unhide Rows/Columns After Apply Plan

> Status: proposed
> Created: 2026-05-11
> Phase: Phase 10F - Real public-drive LTR workbook operational closure

---

## 1. Scope

In scope:

- During LTR apply transaction, explicitly clear worksheet hidden state for rows and columns on target annual sheet.
- Keep existing filter normalization.
- Do not restore any previous view state after commit.
- Add tests for unhide behavior.

Out of scope:

- No UI changes.
- No read-only browser mode changes.
- No audit-note schema extension.

---

## 2. Behavior

After successful LTR apply write:

1. target sheet rows become unhidden in used range scope
2. target sheet columns become unhidden in used range scope
3. filter remains cleared
4. no restoration of prior hidden/filter state

---

## 3. File Changes

- `backend/infrastructure/office/excel_com_ltr_workbook_gateway.py`
  - extend `prepare_sheet_for_operation` with unhide rows/columns actions
  - add COM-safe helper methods for unhide operations

- `tests/unit/test_excel_com_ltr_workbook_gateway.py`
  - add assertions for row/column unhide calls and resulting state

- `tests/unit/test_ltr_workbook_write_commit_service.py`
  - keep/no-regression flow assertion

- `docs/task_board.md`
  - completion note + validation summary

---

## 4. Risks and Controls

Risk:
- workbook with unusual protected sheet settings may block unhide.

Control:
- raise clear write error in protected/blocked cases, so operator can intervene.

Risk:
- unhide full-sheet might be heavy.

Control:
- unhide only used-range related row/column scope first.

---

## 5. Validation

- `py -m pytest tests\unit\test_excel_com_ltr_workbook_gateway.py -q`
- `py -m pytest tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py -q`

