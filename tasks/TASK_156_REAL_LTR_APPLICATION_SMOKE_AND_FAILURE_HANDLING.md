# TASK_156 Real LTR Application Smoke And Failure Handling

> Status: complete
> Created: 2026-05-10
> Phase: Phase 10F - Real public-drive LTR workbook operational closure

---

## 1. Purpose

Run and harden the actual operator workflow for applying an LTR number against the configured workbook path.

This task focuses on the business action itself: operator confirmation, workbook write, backup, lock contention, and business-readable failure handling.

---

## 2. Scope

In scope:

- smoke the real LTR application flow
- verify backup and lock behavior under expected operator conditions
- improve failure messages when workbook path, password, structure, or lock state blocks completion

Out of scope:

- no server authority
- no unrelated workbook features

---

## 3. Acceptance Criteria

- The real operator flow for `Apply LTR Number` is manually validated.
- Common failure modes return actionable operator guidance.
- Workbook write remains authority-first and local SQLite remains secondary.

---

## 4. Completion Notes (2026-05-10)

- Added authority-layer actionable failure guidance for lock timeout, read-only open, write-disabled, and backup failures.
- API conflict semantics improved for direct workbook write commit route:
  - lock-timeout now returns HTTP `409`
  - other business/write failures remain HTTP `400`
- Verified current real configured workbook compatibility baseline:
  - path: `D:\LabShare\LTR\LTR.xls`
  - workbook open/read: `ok`
  - write prerequisites: enabled and configured
  - blockers: none
- Validation tests:
  - `py -m pytest tests/unit/test_ltr_excel_authority_adapter.py tests/integration/test_ltr_workbook_write_commit_api.py tests/integration/test_new_project_completion_api.py -q` passed (`13 passed`)
