# TASK_348A Local LTR Duplicate Override Confirmation

> Status: complete/accepted by Integrator
> Created: 2026-07-02
> Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
> Lane: local-ltr-duplicate-override-confirmation

---

## 1. Purpose

Define and review a controlled contract for local SQLite LTR duplicate handling during New Project LTR application.

The target problem is the high-risk case where the public LTR authority and operator intent allow the current project to use a DL/LTR number, but local SQLite already contains a registered `ltr_records.ltr_number` for an older project. ConnLab must not silently overwrite, delete, rebind, or bypass the old local record. It must show the conflict, provide a safe default path, require explicit confirmation for any local association replacement, and retain audit history.

This task is complete/accepted after Reviewer re-gate, QA gate, and Integrator packaging/readiness. Planner reconciled the exact user-requested adjacent New Project setup/defaulting behavior into the package scope, and Integrator accepted only that narrow adjacent scope with the TASK_348A duplicate override package.

---

## 2. Current Evidence

- `docs/task_board.md` reports no active lane after `TASK_347A_NEW_PROJECT_APPLY_LTR_BUSY_LOCK_UX` complete/accepted.
- `backend/infrastructure/storage/models.py` defines `LtrRecordModel.ltr_number` as globally unique.
- `backend/api/routes_new_project_completion.py` maps local `IntegrityError` during New Project completion to a generic `409` string: `LTR number already exists in local records. Refresh and retry with the next available number.`
- `backend/application/ltr_workbook_write_commit_service.py` rejects exact workbook duplicates for append paths, but can replace an existing workbook row for supported specified numbers before local registration.
- `frontend/src/api/client.ts` preserves structured API `detail` objects through `ApiRequestError.detail`, so a typed conflict contract can be surfaced without replacing the fetch boundary.
- `frontend/src/features/new-project/useNewProjectCompletion.ts` currently catches completion failures as plain error text.
- `tests/integration/test_new_project_completion_api.py` has existing coverage for duplicate specified LTR and local-record duplicate failure, but the accepted behavior is still generic error handling.

---

## 3. Planned Scope

In scope after later approval:

- Backend discovery and contract for local LTR duplicate conflict detection before unsafe local registration side effects.
- Typed API conflict response for local duplicate LTR cases.
- Safe local association override protocol with explicit second action, confirmation token or equivalent intent, and audit record.
- Data model and migration strategy for retaining old local LTR history while preserving one current local owner per LTR number.
- New Project Apply LTR UI conflict confirmation flow.
- Focused backend, API, frontend, and integration tests using temp databases and mocked workbook authority.

Out of scope:

- No silent public workbook override.
- No real public-drive LTR Excel mutation in tests.
- No broad LTR authority rewrite.
- No Matrix, Workbench Folder Actions, Project Registry, StepInstance, Report, AI, permissions, LAN/server, or multi-user scope.
- No cleanup of unrelated Settings/LTR/release/packaging residuals.

---

## 4. Business Contract Draft

Default safe path:

1. If a local duplicate LTR is found, the backend returns a structured `LOCAL_LTR_DUPLICATE` conflict instead of a plain string.
2. The conflict includes display-safe existing record/project summary and a backend-generated confirmation token or equivalent signed/short-lived intent.
3. The frontend shows a compact confirmation surface with three choices:
   - Open or view the existing project.
   - Cancel and return to the current application.
   - Continue using this DL/LTR number for the current project, after a second explicit confirmation.
4. Confirmed continue must retain old local history and audit old/new project association.
5. Public workbook duplicate behavior remains authority-controlled. Local override cannot silently bypass a workbook duplicate or workbook-row ownership blocker.

---

## 5. Stop Point

Current stop point: complete/accepted by Integrator.

Recommended next role: Orchestrator/User for next routing decision.

Remote push was intentionally not performed.

---

## 6. Implementation Authorization Reconciliation

Source-of-truth reconciliation recorded:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed in `docs/lane_evidence/TASK_348A_local-ltr-duplicate-override-confirmation_developer.md`.
- Reviewer implementation-readiness gate passed.
- User explicitly approved TASK_348A reconciliation and Developer implementation.
- Planner reconciliation evidence is recorded in `docs/lane_evidence/TASK_348A_local-ltr-duplicate-override-confirmation_reconciliation_planner.md`.

This authorization does not broaden scope beyond the TASK_348A plan. Real public-drive LTR workbook files, real public-drive data, real local/public folders, Matrix Editor, Workbench Folder Actions, Project Registry behavior outside the approved open-existing route action, StepInstance, Report, AI, permissions, LAN/server, multi-user, release/packaging residuals, Settings/LTR helper residuals, `.agents/**`, and `docs/project_management/**` remain locked.

---

## 7. B1 Adjacent New Project Setup Scope Reconciliation

Reviewer B1 correctly identified three adjacent New Project setup/defaulting files outside the original local LTR duplicate override contract:

- `backend/application/intake_case_review_service.py`
- `frontend/src/features/new-project/NewProjectSetupConfirmationPanel.tsx`
- `tests/unit/test_intake_case_review_service.py`

Planner decision: include only these exact adjacent changes in the TASK_348A package instead of splitting a new lane.

Rationale:

- Thread `019f2347-8027-7980-9f27-46c19284f7d9` was accessible and confirms a user-requested New Project setup UI/defaulting adjustment.
- Developer evidence records that the adjacent changes are not technically required for the duplicate override, but are user-requested and already validated.
- The diff is narrow: parsed-intake defaults for New Project setup sample/test fields, `Sample Description*` before `Test Item*`, and focused unit tests.
- Accepting the exact adjacent behavior avoids orphaning a user-requested New Project setup fix while keeping broad setup refactors locked.

Allowed adjacent behavior:

- Default New Project setup `sample_description` from the first parsed sample table data cell only when no saved setup override exists.
- Default New Project setup `test_item` from the first `Description of Requested Testing` row's `Tests to be Performed` cell only when no saved setup override exists.
- Default `test_type_in_sheet` from the application failure-analysis signal or matching words in `test_item`, falling back to `Partial Qualification`.
- Preserve saved/manual `project_setup` values over parsed defaults.
- Display `Sample Description*` before `Test Item*` in the setup confirmation panel.

Still forbidden:

- No broad New Project setup refactor.
- No additional intake parsing behavior beyond the exact defaults above.
- No public-drive/LTR workbook mutation beyond the TASK_348A approved duplicate workflow.
- No Matrix Editor, Folder Actions, Project Workbench unrelated behavior, StepInstance, Report, AI, permissions, LAN/server, or multi-user scope.
