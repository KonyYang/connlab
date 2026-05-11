# TASK_169 LTR Workbook View-State Normalization And Read-Only Reuse Plan

> Status: proposed
> Created: 2026-05-11
> Phase: Phase 10F - Real public-drive LTR workbook operational closure

---

## 0. Execution Context

- Current phase: `Phase 10F`
- Current active task: `none`
- Why this task is allowed: user requested a controlled implementation plan for the next approved hardening step; this document is planning-only and does not change runtime behavior.

---

## 1. Problem Statement

The target workbook (`LTR_updated.xlsx`) is shared by multiple operators. In daily usage, operators may:

- hide rows/columns
- apply AutoFilter conditions
- save and exit with non-default view state

Current LTR apply and future read-only query flows can be affected by these residual workbook view states. The system needs an explicit pre-operation normalization step to guarantee full-range, deterministic behavior.

---

## 2. Goal

Introduce a reusable workbook session preparation capability that:

1. normalizes relevant sheet view/filter state before write operations
2. is reusable for future read-only workbook open/query operations
3. keeps current lock/transaction safety model unchanged

---

## 3. Scope

In scope:

- add session-level `prepare_sheet_for_operation` capability in Excel COM gateway/session
- normalize filter/view state on target annual sheet before:
  - number lookup
  - dropdown source check/expansion
  - append/replace write
- wire preparation into LTR workbook commit flow
- provide equivalent preparation hook for read-only workbook usage path (no write)
- add unit/integration tests for normalized behavior
- update `docs/task_board.md` after completion

Out of scope:

- no workbook structure redesign
- no migration away from workbook authority
- no frontend changes
- no global "restore previous user view state" feature

---

## 4. Functional Design

### 4.1 Session Preparation Contract

Add a focused session method:

- `prepare_sheet_for_operation(sheet_name: str, mode: "write" | "read") -> PreparationResult`

`PreparationResult` should include diagnostics:

- filter_cleared: bool
- hidden_rows_detected: bool
- hidden_columns_detected: bool
- warnings: list[str]

### 4.2 Normalization Behavior

For the target sheet:

1. detect active filter mode
2. if filter is active, clear to full data view (`ShowAllData` when available)
3. ensure range reads/writes use full physical row scan logic (not visible-only)
4. do not depend on user-hidden states for row finding or dedupe logic

Note:
- Do not force destructive unhide of all rows/columns in this task unless required by COM behavior.
- First guarantee algorithmic full-range scanning independent of UI-visible state.

### 4.3 Commit Flow Wiring

Within existing locked short transaction:

1. resolve target sheet/number decision
2. call `prepare_sheet_for_operation(target_sheet, "write")`
3. continue dropdown ensure + preview + write

### 4.4 Read-Only Reuse Path

For future read-only workbook operations:

- call same preparation method in `"read"` mode before query extraction.
- mode can disable write-only checks while preserving view normalization.

---

## 5. File-Level Change Plan

Primary:

- `backend/infrastructure/office/excel_com_ltr_workbook_gateway.py`
  - add preparation method + COM-safe filter normalization helpers
  - keep existing write session APIs backward compatible

- `backend/application/ltr_workbook_write_commit_service.py`
  - call preparation before dropdown/value write actions
  - include preparation diagnostics in audit notes (optional but recommended)

Secondary:

- `backend/infrastructure/office/__init__.py`
  - export new preparation result type if needed

Tests:

- `tests/unit/test_excel_com_ltr_workbook_gateway.py`
  - filter-active normalization
  - no-filter no-op
  - COM failure to clear filter -> actionable error/warning handling

- `tests/unit/test_ltr_workbook_write_commit_service.py`
  - ensure commit calls preparation before write path

- `tests/integration/test_ltr_workbook_write_commit_api.py`
  - verify no regression in commit contract

Docs:

- `docs/task_board.md` completion update

---

## 6. Risks and Controls

Risk:
- Different workbook variants expose AutoFilter/ShowAllData inconsistently.

Control:
- implement tolerant COM calls with guarded fallback and clear operator error when normalization cannot be guaranteed.

Risk:
- Over-aggressive unhide operations may disrupt operator preferred workbook view.

Control:
- initial version prioritizes algorithmic full-range behavior and filter clearing only; avoid broad cosmetic state rewrites.

Risk:
- Added preparation step could mask unrelated workbook issues.

Control:
- return and log preparation diagnostics to audit notes for traceability.

---

## 7. Validation Plan

Focused backend tests:

- `py -m pytest tests\unit\test_excel_com_ltr_workbook_gateway.py -q`
- `py -m pytest tests\unit\test_ltr_workbook_write_commit_service.py -q`
- `py -m pytest tests\integration\test_ltr_workbook_write_commit_api.py -q`

Operational smoke:

- open workbook manually, apply filter/hide states, save
- run LTR apply from ConnLab
- verify row allocation and dropdown source behavior remain correct

---

## 8. Acceptance Criteria

1. LTR apply remains correct when workbook had pre-existing filters/hide view state.
2. Commit path performs explicit sheet preparation before write actions.
3. Preparation helper is reusable for future read-only workbook open/query path.
4. Tests cover preparation and no-regression behavior.
5. Task board updated with validation evidence.

