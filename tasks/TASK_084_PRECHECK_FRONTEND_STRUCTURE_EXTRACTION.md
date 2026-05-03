# TASK_084_PRECHECK_FRONTEND_STRUCTURE_EXTRACTION

## Status

Proposed. Await explicit user approval before implementation.

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
- `npm run build` and relevant frontend tests pass.
