# TASK_163 Project Registry Cancelled Visibility Filter

> Status: complete
> Created: 2026-05-10
> Phase: Phase 10F - Real public-drive LTR workbook operational closure

---

## 1. Purpose

Make the Project Registry reflect normal daily work after TASK_162 cleanup by hiding cancelled Projects by default while keeping an explicit way to inspect them.

TASK_162 correctly soft-cancelled historical no-LTR Project residues. Those records should remain auditable in SQLite, but they should not dominate the normal registry view or operational metrics.

---

## 2. Scope

In scope:

- Default Project Registry view excludes `cancelled` Projects.
- Add an operator-visible control to include cancelled Projects when needed.
- Metrics reflect the currently visible registry scope.
- Search and pagination work against the same visible scope.
- Empty-state copy distinguishes "no active projects" from no database records when cancelled records are hidden.
- Static frontend test coverage verifies the filter and operator control.

Out of scope:

- No backend deletion.
- No cleanup execution changes.
- No audit history page.
- No LTR recycle library.
- No invalid registered LTR cleanup.
- No redesign of the Project Registry table or metrics.

---

## 3. Acceptance Criteria

- Cancelled Projects are hidden by default in Project Registry.
- The operator can enable a "show cancelled" style control from the registry toolbar.
- When cancelled Projects are hidden, metric cards and pagination counts exclude them.
- When the control is enabled, cancelled Projects appear with their existing status badge and can still be opened for traceability.
- Existing Project Registry search continues to work.
- `npm run build` passes.
- Relevant frontend static tests pass.

---

## 4. Completion Notes

- Project Registry now hides `cancelled` Projects by default.
- Added toolbar control `Show cancelled` to include cancelled records when needed.
- Search, pagination, and metric cards now operate on the currently visible registry scope.
- Added a compact scope note when cancelled Projects are hidden.
- Added a dedicated empty state when current scope hides all records.

Validation:

- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "project_dashboard"` passed (`1 passed, 57 deselected`).
- `npm run build` from `frontend` passed.
