# TASK_089_NEW_PROJECT_WORKFLOW_SHELL_AND_BUTTON_UNIFICATION

Status: Done

## Goal

Unify the New Project workflow shell across Intake and Precheck so the operator sees one consistent four-step flow:

1. Intake
2. Precheck
3. LTR Number
4. Project Folder

## Scope

- Add a shared frontend workflow header/stepper component for New Project steps.
- Use the shared component in `IntakeInboxPage` and `IntakeCaseReviewPage`.
- Remove the disabled Back button from the Intake footer.
- Align footer primary/secondary button vocabulary between Intake and Precheck.
- Preserve existing business behavior, API calls, validation, and session persistence.

## Out of Scope

- Do not extract the full Intake or Precheck page into feature layouts.
- Do not change precheck rules, lookup loading, parser behavior, or API contracts.
- Do not implement LTR Number or Project Folder screens.
- Do not introduce a router, state library, or new dependency.

## Acceptance Criteria

- Intake shows `New Project Step 1 of 4: Intake`.
- Precheck shows `New Project Step 2 of 4: Precheck`.
- Both pages show the same four-step stepper labels and visual vocabulary.
- Precheck marks Intake as completed while Precheck is current.
- Intake footer has no disabled Back action.
- Existing Continue/Save/Confirm enablement behavior remains unchanged.
- Frontend shell static tests and production build pass.

## Validation

- `py -m pytest tests\unit\test_frontend_shell_files.py -q`, result `33 passed`.
- `npm run build` from `frontend/`, result passed.
- `py -m pytest -q`, result `286 passed`.
