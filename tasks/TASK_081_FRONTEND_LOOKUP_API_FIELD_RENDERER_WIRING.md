# TASK_081_FRONTEND_LOOKUP_API_FIELD_RENDERER_WIRING

## Status

Done.

## Phase

Phase 10A - Intake Entry Completion.

## Goal

Wire the Intake/Precheck frontend to the backend lookup option API and remove hardcoded select values from the review page.

## Inputs

- `GET /api/lookups/intake-precheck`
- `docs/frontend_architecture_rules.md`
- `docs/02_ARCHITECTURE_RULES.md`
- User-confirmed Word dropdown behavior for `Post-Testing Sample Disposition`.

## Scope

Allowed:

- Add a frontend API client function for Intake/Precheck lookup options.
- Load lookup options in the Precheck review flow.
- Replace hardcoded select arrays in `IntakeCaseReviewPage.tsx` with backend-provided options.
- Treat `post_testing_disposition` as the same kind of select field as Business Unit, Mfg. Site, Results Format, Test Type, Sample Status, and Project Type.
- Remove or thin the current independent hardcoded `DispositionPanel`.
- Preserve parsed values that are not present in the current lookup list by showing them as temporary selectable values.

Not allowed:

- Changing backend lookup storage model.
- Parser calibration work.
- Sample row edit/copy/delete implementation.
- Broad Precheck redesign outside the select-field wiring.
- LTR workbook write hardening or future-scope features.

## Required Lookup Values

`post_testing_disposition` must support backend-managed Word dropdown values such as:

- `Choose an item.`
- `Send Back to Requestor`
- `Scrap`
- `Keep in the Lab`

Placeholder values must not be treated as valid confirmed values during future precheck/confirmation rules unless that behavior is explicitly approved.

## Acceptance Criteria

- No Intake/Precheck select option list remains hardcoded in page JSX.
- `Post-Testing Sample Disposition` uses the shared lookup/select implementation.
- Existing parsed values remain visible even when not in the backend lookup list.
- Frontend build or targeted frontend tests pass.

## Completion Notes

- Added a typed frontend API client for `GET /api/lookups/intake-precheck`.
- Replaced hardcoded Precheck select option arrays with backend lookup groups.
- Moved `Post-Testing Sample Disposition` into the same shared `ReviewField` select renderer.
- Removed the independent hardcoded disposition select from the lower panel.
- Added backend required-default backfill for Word disposition values so existing local databases receive the new values without overwriting existing options.

## Validation

- `py -m pytest tests\unit\test_frontend_shell_files.py tests\integration\test_lookup_options_api.py tests\unit\test_lookup_options_service.py -q`
- Result: `29 passed`
- `npm run build`
- Result: passed
