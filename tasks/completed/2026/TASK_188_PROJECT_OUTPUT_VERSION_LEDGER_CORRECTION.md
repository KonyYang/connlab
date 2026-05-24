# TASK_188 Project Output Version Ledger Correction

> Status: proposed
> Created: 2026-05-14
> Phase: Phase 11 - Project planning data foundation before downstream document automation
> Plan: `docs/task_188_project_output_version_ledger_correction_plan.md`

---

## 0. Execution Gate

- Current phase: `Phase 11`.
- Current local board reality at creation time: `TASK_188_PROJECT_WORKBENCH_VERSION_AND_STALE_STATUS` is marked complete as a frontend-derived status implementation.
- Why this correction task is required:
  - Later user-confirmed business workflow shows frontend-only status is insufficient.
  - ConnLab must persist downstream output lineage to support reload-safe stale detection, approval-package review, future report generation, and historical reuse.
  - This correction must happen before Matrix editing/freezing work becomes the mainline, otherwise Matrix changes will not have a durable way to mark downstream outputs stale.

Implementation gate:

- This task file and the plan document are proposal/control documents.
- Do not implement code until the user explicitly approves this correction task.

---

## 1. Purpose

Replace or supplement the current frontend-only downstream freshness model with a minimal persistent Project output version ledger.

The ledger must record which Matrix/TestPlan draft version produced or justified each downstream output:

- Section 2 write-back;
- test record form;
- fee evaluation;
- approval package.

It must allow Workbench to show `current`, `stale`, `missing`, `manual`, and `failed` after the app is reopened.

---

## 2. Business Rationale

The lab workflow confirmed on 2026-05-14:

- One Project usually has one current Matrix/TestPlan.
- Matrix may be revised by the project owner.
- All downstream files and reports should follow the latest confirmed Matrix.
- Old files should not be deleted, but must be marked stale when no longer aligned with the current Matrix.
- Future similar-project reuse depends on structured historical Matrix, output, result, image, fee, and report metadata.

Frontend-only warnings cannot provide that traceability.

---

## 3. In Scope

- Add a minimal persisted output record model/repository/service/API.
- Track output records by `project_id`, `draft_id`, `draft_version`, `output_kind`, `output_path`, `status`, `source`, timestamps, and note.
- Expose a Project-scoped read model for Workbench.
- Let Workbench display persisted output freshness.
- Preserve current frontend status display behavior where useful, but backend persisted state is authoritative.
- Add tests for create/list/status transitions and Workbench API smoke.

---

## 4. Out Of Scope

- No Matrix editing.
- No Matrix freeze UI.
- No test record import.
- No image/evidence step attachment workflow.
- No fee price mapping overhaul.
- No report generation.
- No AI review.
- No LAN/multi-user permission model.
- No direct Office operations in API or UI.

---

## 5. Required Decisions To Follow

Follow:

- `docs/matrix_test_plan_data_management_decisions.md`
- `docs/task_188_project_workbench_version_and_stale_status_plan.md`

Key authority rule:

```text
Original spec / Word Matrix / Excel Matrix = source evidence
ConnLab confirmed ProjectTestPlanDraft = project plan authority
Generated Word / Excel / PDF files = output artifacts
Imported test results/images = project execution evidence
```

---

## 6. Minimal Data Contract

Suggested domain object:

```text
ProjectOutputRecord
```

Suggested fields:

```text
output_record_id
project_id
draft_id
draft_version
output_kind
output_path
status
source
created_at
updated_at
note
```

Initial output kinds:

```text
section2_write_back
test_record_form
fee_evaluation
approval_package
```

Initial statuses:

```text
missing
current
stale
manual
failed
```

---

## 7. Expected Implementation Shape

Backend:

- domain enum/model additions;
- SQLAlchemy model;
- repository;
- application service;
- typed API route;
- dependency wiring.

Frontend:

- API client DTOs/functions;
- Workbench model loads persisted output status;
- Workbench status panel uses backend status as the durable source;
- current route page remains thin.

Tests:

- unit service tests;
- integration API tests;
- frontend static boundary tests.

---

## 8. Validation Plan

Backend:

```powershell
py -m pytest tests\unit\test_project_output_record_service.py tests\integration\test_project_output_record_api.py -q
```

Frontend:

```powershell
cd frontend
npm run build
```

Static guard:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix or approval"
```

Task-board guard:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

---

## 9. Acceptance Criteria

- Workbench can show output freshness after reload.
- Stale detection is based on active Matrix draft/version.
- Manual outputs are not falsely presented as system-generated current files.
- Old outputs remain available as traceability evidence.
- No future-scope Matrix editing, record import, image workflow, fee overhaul, or report generation is implemented in this correction.

---

## 10. Stop Condition

Stop after this correction task is completed and reviewed.

Do not proceed to `TASK_189_MATRIX_EDIT_AND_FREEZE_FOUNDATION` until this ledger correction is either implemented or explicitly deferred by the user.
