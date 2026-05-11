# TASK_167 LTR J-Column Dropdown Auto-Expand Plan

> Status: proposed
> Created: 2026-05-11
> Phase: Phase 10F - Real public-drive LTR workbook operational closure

---

## 1. Scope

In scope:

- Remove manual dependency on `Test Type in sheet` for LTR workbook commit path.
- Use backend project setup `location` as the authoritative J-column write value.
- Before writing J-column, ensure the workbook data-validation source list for J supports the value:
  - if present in source list, use directly
  - if missing, append to source list tail in column `AB` and expand source range by one row
- Keep all operations in one existing locked short transaction.
- Add unit/integration tests for:
  - existing value path (no expansion)
  - new value path (append + range expansion)
  - duplicate normalization (trim/case-insensitive)

Out of scope:

- No frontend UI redesign beyond API contract adjustments needed by backend change.
- No general Excel validation engine refactor.
- No migration to configurable multi-sheet dictionary model.

---

## 2. Business Rule (Confirmed)

- J column is driven by project `location`.
- If J validation source range does not contain `location`, backend auto-appends `location` to `AB` tail and expands validation range.
- Commit then writes J normally, without requiring manual operator pre-fill in workbook list.

---

## 3. Implementation Design

1. Workbook transaction/session capability extension

- Add a focused helper in workbook session/gateway layer:
  - resolve current J validation source range (baseline legacy `AB1:AB36`)
  - read source values
  - append missing value at tail
  - update validation source formula to expanded range

2. Commit service flow change

- In `LtrWorkbookWriteCommitService` transaction operation:
  - before row append/replace, call `ensure_location_dropdown_value(location)`
  - then continue existing preview mapping and row write logic

3. Command/DTO cleanup

- Remove `test_type_in_sheet` hard requirement from commit command path where it is only a manual workaround.
- Keep backward-compatible API handling for one transition task if needed (accept but ignore/deprecate field).

4. Normalization policy

- Compare using normalized text: `strip` + lowercase.
- Preserve original operator casing when appending new value.

5. Audit note extension

- Add audit metadata in commit notes:
  - `location_dropdown_appended`: true/false
  - `appended_value`: value or null
  - `source_range_before/after`

---

## 4. File-Level Change Plan

- `backend/infrastructure/office/*` related LTR workbook transaction/session files:
  - add data-validation source range read/update + AB append helper
- `backend/application/ltr_workbook_write_commit_service.py`:
  - call dropdown ensure step in transaction
  - adjust command dependency on `test_type_in_sheet`
- `backend/application/ltr_workbook_write_preview_service.py`:
  - align row_data mapping if `test_type_in_sheet` is no longer operator-entered
- `backend/api/routes_ltr_workbook.py` and/or related request DTO:
  - align request contract for removed/deprecated manual field
- tests:
  - `tests/unit/test_ltr_workbook_write_commit_service.py`
  - `tests/unit/test_ltr_workbook_transaction_gateway.py`
  - related integration API tests for commit path
- `docs/task_board.md`:
  - completion note and validation summary

---

## 5. Risks and Controls

Risk:
- Legacy workbook validation formulas may differ from expected `AB` range format.

Control:
- Parse and validate formula shape; fail with actionable error when unsupported.

Risk:
- Concurrent commits may append duplicate site values.

Control:
- Reuse existing workbook lock-based short transaction; re-check list inside lock before append.

Risk:
- API contract break for existing frontend payloads.

Control:
- One-task compatibility: accept old field during transition, backend ignores or maps internally.

---

## 6. Validation Plan

Focused tests:

- `py -m pytest tests\unit\test_ltr_workbook_transaction_gateway.py -q`
- `py -m pytest tests\unit\test_ltr_workbook_write_commit_service.py -q`
- `py -m pytest tests\integration\test_ltr_workbook_write_commit_api.py -q`
- `py -m pytest tests\integration\test_new_project_completion_api.py -q`

Optional confidence run:

- `py -m pytest tests\unit tests\integration -q`

