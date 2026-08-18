# TASK_304 New Project Lab Performing Tests Confirmation

Status: Complete.

Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Allowed reason: The task board has no active implementation task, and the user explicitly assigned this requested New Project setup correction to TASK_304. This task is limited to a planned, reviewable correction for the existing New Project Project setup confirmation flow and downstream Section 2 lab write-back compatibility.

## Goal

Add a required `Lab Performing the Tests` confirmation value to the New Project setup confirmation flow, with controlled options:

```text
Dongguan
Valley Green
```

The default value is `Dongguan`.

This value must be stored as structured New Project setup data and promoted into the confirmed `ApplicationForm.lab` value during New Project completion, so later application-form Section 2 preview/write-back and LTR readiness paths can consume the same persistent project source.

## Current Findings

- The frontend `Project setup confirmation` card currently captures `Test Item`, `Sample Description`, `Test Type in sheet`, and `Project Leader`.
- New Project setup values are already persisted in `IntakeCase.project_setup`.
- The backend currently filters persisted setup values through an allowlist, so a new setup field requires backend persistence changes.
- The New Project completion API currently has no `lab_performing_tests` request field.
- The real template label in `D:\Source\Template\E-3718_H Laboratory Test Request-Even.docx` is `Lab Performing the Tests:`.
- Current Section 2 Word gateway matching does not recognize that real label for the `lab` field.
- Existing Section 2 preview/write-back request models accept `lab` from request body; they do not read `project_setup` directly.
- Existing LTR readiness `lab_performing_tests` reads `application_form.lab`, so `ApplicationForm.lab` is the minimal persistent consumption source for this task.

## Scope

### In Scope

- Add `lab_performing_tests` to New Project setup confirmation state.
- Render a required select in the existing `Project setup confirmation` card.
- Default the select to `Dongguan`.
- Persist the value in `IntakeCase.project_setup`.
- Include the value in the New Project completion request and backend command.
- Validate the value as required and limited to `Dongguan` or `Valley Green`.
- Reject unsupported values during Project setup draft autosave/update, so invalid setup values do not persist until final completion.
- Promote the validated value into the confirmed project's latest `ApplicationForm.lab` during New Project completion, only when the project is fresh or already confirmed but not yet registered.
- Record the value in New Project completion operator note/audit context.
- Update Section 2 Word gateway label aliases so `Lab Performing the Tests:` maps to the existing Section 2 `lab` field.
- Add or update focused tests.
- Update `docs/task_board.md` after implementation.

### Out Of Scope

- New Section 2 UI workflow.
- Automatic Section 2 write-back during New Project completion.
- Changing LTR workbook Location/Mfg. Site mapping.
- Adding database columns for this field.
- New settings UI for lab options.
- Reading Section 2 from Word as authority.
- Making Section 2 APIs read `project_setup` directly.
- Matrix, StepInstance, report generation, fee evaluation changes, AI review, permissions, or deployment work.

## Required Behavior

1. When `/intake` loads a new or imported package, `Lab Performing the Tests*` defaults to `Dongguan`.
2. The field offers exactly `Dongguan` and `Valley Green`.
3. The field is required for `Apply LTR Number`.
4. The field is saved with other `project_setup` values during draft autosave.
5. Draft autosave/update rejects unsupported values instead of persisting them.
6. Reloading or switching back to a saved draft restores the saved value.
7. Completing New Project sends the selected value to the backend.
8. Backend completion validation rejects missing or unsupported values.
9. New Project completion writes the validated value to the latest `ApplicationForm.lab` before LTR commit when the project is not yet registered.
10. Already registered/idempotent completion does not mutate `ApplicationForm.lab`.
11. LTR readiness can resolve `lab_performing_tests` from the promoted `ApplicationForm.lab`.
12. The completion operator note includes `lab_performing_tests`.
13. Section 2 write-back gateway can locate the real template label `Lab Performing the Tests:` for the existing `lab` field.

## Acceptance Criteria

- The Project setup confirmation card shows `Lab Performing the Tests*`.
- The default value is `Dongguan`.
- `Valley Green` can be selected and retained through draft save/load.
- Missing or invalid completion input fails with a business-readable validation error.
- Invalid autosave/update input fails before it is persisted into `project_setup`.
- After successful New Project completion, the confirmed project's `ApplicationForm.lab` equals the selected lab.
- Already-registered/idempotent completion does not overwrite `ApplicationForm.lab`.
- LTR readiness reports `lab_performing_tests` from the promoted `ApplicationForm.lab`.
- Existing setup fields continue to work.
- Existing LTR workbook write behavior is unchanged except for carrying the new audit context.
- The Word Section 2 gateway recognizes `Lab Performing the Tests:` as the `lab` write target.

## Validation Plan

Implementation validation should run:

```powershell
cd frontend
npm test -- --run NewProjectSetupConfirmationPanel IntakeInboxPage useNewProjectCompletion --watch=false
npm run build
cd ..
py -m pytest tests/unit/test_intake_case_review_service.py tests/integration/test_new_project_completion_api.py tests/unit/test_ltr_readiness_service.py tests/unit/test_word_document_section2_write_gateway.py -q
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "new_project or section2 or task304"
git diff --check
```

Manual/browser smoke:

```text
Open http://localhost:5173/intake.
Confirm Project setup confirmation shows Lab Performing the Tests*.
Confirm Dongguan is selected by default.
Select Valley Green and verify the selection remains visible while editing the draft.
```

## Stop Rule

TASK_304 is complete. Stop here; do not enter the next task.

## Completion Notes

- Added required New Project setup confirmation field `Lab Performing the Tests*`.
- Field options are `Dongguan` and `Valley Green`, with `Dongguan` as the default.
- Persisted `project_setup.lab_performing_tests` with draft setup values and rejected unsupported draft values.
- Carried `lab_performing_tests` through New Project completion API/service.
- Promoted the validated lab into latest `ApplicationForm.lab` before LTR commit for fresh/already-confirmed-not-registered paths.
- Preserved already-registered/idempotent completion behavior without mutating `ApplicationForm.lab`.
- Added Word Section 2 label alias support for `Lab Performing the Tests:`.
- Added tests for setup persistence/validation, completion promotion/idempotency, LTR readiness consumption, Word label matching, and frontend wiring.
