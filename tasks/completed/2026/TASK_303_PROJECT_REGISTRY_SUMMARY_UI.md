# TASK_303_PROJECT_REGISTRY_SUMMARY_UI

> Status: complete (archived 2026-08-18; implementation integrated and covered by tests)
> Approved: 2026-06-07
> Plan: `docs/project_management/plans/PROJECTS_REGISTRY_UI_OPTIMIZATION_PLAN_2026-06-07.md`

## Goal

Update `/projects` Project registry so its table shows operator-facing registry fields:

- `LTR Number`
- `Sample Description`
- `Test Item`
- `Requestor`
- `Business Unit`
- `Status`
- `Progress`
- `Notes`
- `Action`

Remove:

- `Project Name`
- `Product`
- `Recent Activity`

## Data Authority

`Sample Description`, `Test Item`, and `Notes` must come from a backend read-only registry summary DTO. The frontend must not rename `project.product_name`, parse LTR audit JSON, parse intake draft JSON, or synthesize values from Matrix rows.

Historical rows without normalized registry fields must show:

- `Sample Description`: `Not recorded`
- `Test Item`: `Not recorded`
- `Notes`: `None`

## Scope

Allowed:

- Add a backend application service for read-only registry summary rows.
- Add a typed API endpoint for registry rows.
- Update the `/projects` frontend table columns and search scope.
- Update focused tests.

Forbidden:

- Persist new fields.
- Change project lifecycle behavior.
- Change LTR authority behavior.
- Derive `Test Item` from Matrix rows.
- Use `project.product_name` as `Sample Description` fallback.
- Display raw audit JSON or parser/system diagnostics as `Notes`.

## Validation

- Backend unit/API tests for registry summary rows.
- Frontend shell test for new/removed columns and no frontend JSON parsing.
- `npm run build`.
- Browser smoke on `http://localhost:5173/projects`.
