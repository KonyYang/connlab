# TASK_164 New Project Draft-Scope Duplicate Only

> Status: complete
> Created: 2026-05-10
> Phase: Phase 10F - Real public-drive LTR workbook operational closure

---

## 1. Purpose

Reduce New Project duplicate-flow complexity by enforcing duplicate checks only inside the draft/package boundary.

Confirmed/created Project duplicate checks are removed from New Project intake selection flow.

---

## 2. Scope

In scope:

- Keep duplicate checks for draft identity (`exact_existing_application_draft`, `exact_existing_no_form_draft`).
- Remove selected-form conflict path against already confirmed Projects.
- Remove frontend confirmed-project duplicate reminder card and related action wiring.
- Update API/frontend typing and tests to the new boundary.

Out of scope:

- No change to LTR number duplicate guards in LTR registration/write paths.
- No Project deletion logic changes.
- No workbook behavior changes.

---

## 3. Completion Notes

- Backend `IntakeFormSelectionService` no longer raises confirmed-project duplicate conflicts.
- Intake select-form API no longer maps confirmed-project duplicate errors.
- Frontend duplicate model removed `existing_confirmed_project_ltr` and `open_project` action branch.
- New Project attachment panel now renders only draft-scope duplicate resolution.

Validation:

- `py -m pytest tests\unit\test_intake_form_selection_service.py tests\integration\test_msg_package_intake_api.py -q` passed (`36 passed`).
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "duplicate_scope or task147 or duplicate"` passed (`2 passed, 56 deselected`).
- `npm run build` from `frontend` passed.
