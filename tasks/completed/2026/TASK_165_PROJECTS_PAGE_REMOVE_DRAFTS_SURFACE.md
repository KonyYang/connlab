# TASK_165 Projects Page Remove Drafts Surface

> Status: complete
> Created: 2026-05-10
> Phase: Phase 10F - Real public-drive LTR workbook operational closure

---

## 1. Purpose

Keep `Projects` focused on Project registry behavior only and remove Drafts/In-Progress management from this page.

Draft records remain stored in backend and are not deleted by this task.

---

## 2. Scope

In scope:

- Remove `Drafts / In Progress` section from `ProjectListPage`.
- Remove Projects-page draft continue/discard UI logic and related App wiring.
- Keep all backend draft APIs and data unchanged.
- Update frontend static tests to reflect the new scope boundary.

Out of scope:

- No backend schema or API deletion.
- No New Project draft-list UX redesign.
- No draft data cleanup.

---

## 3. Completion Notes

- `ProjectListPage` no longer imports or renders draft-list/discard behavior.
- `App.tsx` no longer passes `onContinueDraft` or performs detail-load handoff from Projects page.
- Draft persistence/query APIs remain available for future New Project-side management.

Validation:

- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "project_dashboard or projects_page_removes_drafts_surface_after_task163 or task100_workbench"` passed (`3 passed, 55 deselected`).
- `npm run build` from `frontend` passed.
