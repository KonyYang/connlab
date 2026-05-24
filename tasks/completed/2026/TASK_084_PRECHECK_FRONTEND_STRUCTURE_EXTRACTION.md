# TASK_084_PRECHECK_FRONTEND_STRUCTURE_EXTRACTION

## Status

Done.

## Phase

Phase 10A - Intake Entry Completion.

## Goal

Reduce the maintainability risk in the Precheck route page by extracting field configuration, sample table configuration, issue selectors, and named business components into a `features/precheck` boundary.

## Inputs

- `docs/frontend_architecture_rules.md`
- Current `frontend/src/pages/IntakeCaseReviewPage.tsx`
- Current Precheck review behavior after TASK_079 through TASK_083.

## Scope

Allowed:

- Extract Precheck field configuration from the route page.
- Extract sample column configuration and sample row helpers.
- Extract issue summary and sample table into named feature components.
- Extract page-level Precheck/Intake style rules that belong to reusable feature surfaces into maintainable tokens or component-scoped rules.
- Preserve the recent readability corrections for operational data: neutral ink text for extracted values and table cells, normal data weight, and practical dropdown/form widths.
- Keep API calls centralized in `frontend/src/api/client.ts`.
- Preserve current behavior and visual design.

Not allowed:

- New business behavior.
- Parser changes.
- Lookup storage changes.
- Sample row behavior changes.
- LTR workbook write hardening.
- Matrix, Report, AI review, LAN, permissions, or Outlook automation.

## Acceptance Criteria

- Route page is thinner and composes named Precheck feature components.
- Field/table configuration is not embedded directly in the page.
- Existing Precheck behavior remains stable.
- Page-level CSS is not allowed to keep growing as ad hoc color, font-weight, or width overrides when those rules belong to feature components or shared design tokens.
- Intake/Precheck extracted values and table data remain readable without overusing blue or bold styling.
- `npm run build` and relevant frontend tests pass.

## Completion Notes

- `IntakeCaseReviewPage.tsx` now composes named Precheck feature components and keeps route-level loading, saving, confirmation, and navigation state.
- Precheck field configuration, sample column configuration, sample row helpers, issue selectors, and source/status formatting moved into `frontend/src/features/precheck`.
- Precheck and Intake page readability adjustments are now backed by scoped data/text tokens instead of scattered hard-coded data color and weight overrides.
- Existing API boundaries remain unchanged; API calls still go through `frontend/src/api/client.ts`.

## Validation

- `py -m pytest tests\unit\test_frontend_shell_files.py -q`
- Result: `28 passed`
- `npm run build`
- Result: passed
- `py -m pytest -q`
- Result: `276 passed`
- `git diff --check`
- Result: passed with CRLF working-copy warnings only
