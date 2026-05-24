# TASK_098_PRECHECK_CONFIRMED_APPLICATION_EDITING

## Status

done

## Current Phase

Phase 10A follow-up. This is the third proposed task in the Project creation draft flow series.

## Active Task Rule

Do not implement this task until `docs/task_board.md` explicitly marks `TASK_098_PRECHECK_CONFIRMED_APPLICATION_EDITING` as current or ready after the draft lifecycle work is complete.

## User Decision Baseline

The user approved removing `Back to Intake`.

Reason:

- Intake is source selection.
- Precheck is where the operator edits and confirms the application-form data.
- The final submitted/confirmed application data is not the raw Word form extracted from email. It is the corrected structured data from Precheck.
- Switching application forms after entering Precheck is not supported in the normal workflow.

## Goal

Make Precheck the authoritative editing surface for confirmed application data before Project creation, and remove the confusing `Back to Intake` path.

## Scope

Frontend:

- Remove `Back to Intake` from the New Project Precheck page.
- Add or refine `Save draft and exit` and `Exit without saving` actions according to `TASK_096`.
- Keep Precheck fields editable for application data corrections.
- Ensure source application-form metadata remains visible enough for traceability without implying the raw source is the final submitted data.

Backend/API:

- Ensure Project confirmation uses corrected Precheck draft/manual override data.
- Ensure saved draft continuation returns the corrected Precheck data.
- Preserve source package/asset traceability without allowing form switching from Precheck.

Documentation:

- Update the Intake/Precheck field contract to state:
  - Intake selects source.
  - Precheck edits confirmed application data.
  - Form switching after Precheck entry is not a normal workflow.

## Out Of Scope

- Do not add a form replacement workflow.
- Do not support multi-form case switching.
- Do not redesign the whole Precheck page.
- Do not implement LTR revise/exception.

## Acceptance Criteria

- Precheck no longer shows `Back to Intake`.
- Precheck provides save/discard exit paths.
- Corrected Precheck data is used for Project creation.
- Continuing a saved Precheck draft restores corrected data.
- Raw source file remains traceable but is not presented as the final confirmed application record.
- No route or UI path allows silent switching to another application form after entering Precheck.

## Validation

Add or update tests:

- Frontend static test: `Back to Intake` is absent from Precheck.
- Unit/integration test: Project confirmation uses edited Precheck fields.
- Integration test: saved Precheck draft continues with manual corrections.
- Frontend build passes.

Recommended validation:

```powershell
py -m pytest tests\unit\test_intake_case_review_service.py tests\integration -q
py -m pytest tests\unit\test_frontend_shell_files.py -q
npm run build
```

## Stop Rule

After completing this task, update `docs/task_board.md`, record validation, and stop. Do not start `TASK_099` automatically.

## Completion Notes

Completed on 2026-05-05.

- Removed the New Project Precheck `Back to Intake` action and the associated route/session snapshot callback.
- Kept `Save draft and exit` and `Exit without saving` as the supported Precheck exit paths.
- Updated the Precheck source panel from source/template-switching language to source traceability language.
- The UI now states that confirmed application data is edited in Precheck and Project creation uses corrected Precheck values.
- Updated `docs/intake_precheck_field_contract.md` to record:
  - Intake selects source only.
  - Precheck edits confirmed application data.
  - Normal workflow does not support switching to another application form after Precheck entry.
  - Raw source files remain traceability context, not the final confirmed application record.
- Strengthened integration coverage to assert confirmed Project, ApplicationForm, and SampleInfo records use corrected Precheck data.

Validation:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py tests\integration\test_manual_intake_api.py tests\unit\test_intake_case_review_service.py -q
```

Result: `66 passed`.

```powershell
npm run build
```

Result: passed.

```powershell
py -m pytest tests\integration -q
```

Result: `53 passed`, `1 failed`.

Observed failure outside this task's change scope:

- `tests/integration/test_intake_package_repositories.py::test_form_selection_service_creates_case_and_draft_with_repositories` seeds a fake `.docx` path and fails the current Word header gate.

Known limitations:

- No form replacement workflow was added.
- LTR registered freeze and revise/exception behavior remains `TASK_099`.
