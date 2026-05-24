# TASK_160 New Project LTR Atomic Completion Gate

> Status: complete
> Created: 2026-05-10
> Phase: Phase 10F - Real public-drive LTR workbook operational closure

---

## 1. Purpose

Fix the New Project LTR application flow so a project enters Project Registry only after LTR application succeeds.

The current frontend sequence can create a confirmed project before the external workbook LTR write succeeds. If the workbook write fails, a no-LTR project remains in Project Registry. This task closes that source of dirty project records.

---

## 2. Scope

In scope:

- Remove frontend direct `confirmIntakeCase` and direct `commitLtrWorkbookWrite` calls from New Project completion.
- Make New Project completion use the single backend orchestration API only:
  - `POST /api/intake-cases/{case_id}/complete-new-project`
- Ensure workbook-authority commit metadata returned by the backend is displayed/preserved by the frontend result snapshot.
- Add regression coverage proving workbook commit failure does not persist a visible confirmed project/LTR registration result.

Out of scope:

- Historical dirty project cleanup.
- Project soft delete.
- LTR recycle candidate pool.
- Workbook row delete/void behavior.
- Project Registry cleanup filters beyond what is needed for this gate.

---

## 3. Acceptance Criteria

- Clicking `Apply LTR Number` calls only `complete-new-project` from New Project completion UI.
- If workbook commit fails, the New Project UI shows the failure and does not navigate to Project Registry.
- If workbook commit fails, local LTR is not registered.
- If workbook commit succeeds, Project Registry receives and displays the committed LTR result.
- Frontend build and targeted backend/frontend tests pass.

---

## 4. Completion Notes (2026-05-10)

- New Project frontend completion now calls only `completeNewProject(activeCase.case_id, ...)`.
- Removed frontend direct `confirmIntakeCase` and direct `commitLtrWorkbookWrite` sequencing from the New Project completion hook.
- Result snapshot now uses backend `complete-new-project` response metadata.
- Failure regression now asserts workbook commit failure leaves no confirmed project link and no created Project record.

## 5. Validation

- `py -m pytest tests/integration/test_new_project_completion_api.py -q` passed (`5 passed`)
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "new_project or project"` passed (`10 passed, 48 deselected`)
- `npm run build` from `frontend` passed
