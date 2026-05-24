# TASK_183 Project Workbench Approval Package UI Wiring

> Status: complete
> Created: 2026-05-12
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 0. Execution Gate

- Current phase at creation time: `Phase 11`.
- Current active task in board at creation time: `none; TASK_182 complete`.
- Why this task is allowed now: `TASK_182_APPROVAL_PACKAGE_GENERATION_AND_PROJECT_FOLDER_PLACEMENT` is complete, but operators still need a Project Workbench surface to trigger the backend preview/execute approval package workflow.
- Implementation gate: this task file and plan define the implementation scope; do not write implementation code until the user explicitly approves this task, for example `批准执行 TASK_183`.

---

## 1. Model Fit

`gpt-5.3-codex` is suitable for implementation.

Reason:

- The task is bounded frontend/API wiring against existing backend endpoints.
- The architecture rules are clear: API calls stay in `frontend/src/api/client.ts`, workflow state belongs in feature components/hooks, and route pages should not accumulate more business logic.
- The main work is TypeScript DTOs, focused React workflow UI, API integration, and static/build tests.
- No deep algorithmic reasoning, Office template reverse engineering, or broad backend redesign is required.

---

## 2. Purpose

Wire the approval package backend workflow into Project Workbench so an operator can preview and execute approval package placement from the project lifecycle surface.

The UI should make current state, blockers, target paths, and next action clear before copying files.

---

## 3. Business Context

TASK_179, TASK_181, and TASK_182 provide backend capabilities for:

- completed Section 2 application form;
- generated test record template;
- generated fee evaluation form;
- approval package preview and folder placement.

The current frontend already exposes folder and evidence placement flows. The next step is a focused approval-package panel in Project Workbench that can call the TASK_182 preview/execute APIs.

---

## 4. Scope

In scope:

- Add typed frontend API DTOs and client functions for:
  - approval package preview;
  - approval package execute.
- Add a Project Workbench approval package panel.
- Reuse existing workbench visual language and product UI rules.
- Let the operator provide or paste required file paths for:
  - completed application form;
  - generated test record file;
  - optional fee evaluation file;
  - optional evidence paths.
- Show preview items, statuses, warnings, blockers, and final execute result.
- Disable execute when preview has blockers.
- Add frontend static/build tests.

Out of scope:

- No backend changes unless a small DTO mismatch is discovered.
- No new Office document generation.
- No report generation.
- No customer feedback form generation.
- No automatic file picker or desktop-shell integration.
- No Matrix editing UI.
- No AI review.

---

## 5. Inputs

User-provided UI inputs:

```text
project_folder_path
completed_application_form_path
test_record_output_path
fee_evaluation_output_path: optional
evidence_source_paths: optional multiline list
overwrite: bool
```

Backend data source:

- `POST /api/projects/{project_id}/approval-package/preview`
- `POST /api/projects/{project_id}/approval-package/execute`

---

## 6. Outputs

UI output:

```text
approval package preview status
planned items table/list
warnings[]
blockers[]
execute result
```

---

## 7. UX Rules

- Keep the Project Workbench as a work surface, not a new landing page.
- Put state before action:
  - whether preview exists;
  - whether blockers exist;
  - whether execute is allowed.
- Keep copy operational and business-readable.
- Do not expose raw API route names or backend enum internals in user-facing text.
- Keep the panel compact enough for a 14-inch laptop workflow.
- Do not create nested cards or decorative panels.

---

## 8. Expected Files

Frontend:

- `frontend/src/api/client.ts`
- `frontend/src/components/workflow/ApprovalPackagePanel.tsx`
- `frontend/src/pages/ProjectWorkbenchPage.tsx`
- relevant CSS file(s), preserving existing workbench styles

Tests:

- `tests/unit/test_frontend_shell_files.py`

Docs:

- `docs/task_183_project_workbench_approval_package_ui_wiring_plan.md`
- `docs/task_board.md`

---

## 9. Validation Plan

Frontend validation:

```powershell
npm run build
```

Static guard:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or approval or folder"
```

Task board guards:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

---

## 10. Acceptance Criteria

- Project Workbench can preview approval package placement.
- Project Workbench can execute approval package placement only after preview is available and blocker-free.
- UI shows planned item status, target path, warnings, and blockers.
- API client remains the only frontend fetch boundary.
- Route page does not grow large ad hoc JSX beyond the approved panel wiring.
- No backend Office or document generation logic is added.
- Frontend build passes.
- Task board is updated after implementation and validation.

---

## 11. Stop Condition

After implementation and validation:

- update task board;
- record validation;
- stop;
- do not start report generation, customer feedback form UI, or test status dashboard without explicit approval.

---

## 12. Completion Notes

Completed on 2026-05-12.

Implemented:

- Added approval package API DTOs and client methods in `frontend/src/api/client.ts`:
  - `ApprovalPackageRequest`
  - `ApprovalPackageItem`
  - `ApprovalPackageResponse`
  - `previewApprovalPackage(...)`
  - `executeApprovalPackage(...)`
- Added `frontend/src/components/workflow/ApprovalPackagePanel.tsx` with:
  - operator input fields for required/optional paths
  - optional multiline evidence path input
  - overwrite toggle
  - preview and execute actions
  - blocker/warning visibility and item status list
  - execute disabled unless preview exists and has no blockers
- Wired the panel into `frontend/src/pages/ProjectWorkbenchPage.tsx` with local workflow state and API orchestration.
- Added minimal style support in `frontend/src/workbench.css` for multiline evidence input.

Validation:

- `npm run build` (frontend) passed.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or approval or folder"` passed (`5 passed, 53 deselected`).
- `py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q` passed (`17 passed`).
