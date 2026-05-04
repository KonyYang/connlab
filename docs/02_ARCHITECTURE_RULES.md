# Architecture Rules

## Layering

```text
Frontend -> API -> Application Services -> Domain + Ports -> Infrastructure
```

## Dependency Direction

Allowed:

- api -> application
- application -> domain
- application -> ports/interfaces
- infrastructure -> domain/application ports

Forbidden:

- domain -> infrastructure
- domain -> api
- frontend -> Office/SQLite directly
- api route -> Office directly

## Frontend/UI Design Rule

`$impeccable` is required for all ConnLab frontend/UI work across the whole project, not just a single phase.

Use it before designing, changing, critiquing, auditing, polishing, refactoring, or documenting frontend UI, UX copy, layout, visual hierarchy, interaction states, responsive behavior, or frontend smoke expectations.

Backend-only, parser-only, storage-only, Office gateway-only, database-only, and non-UI test work is exempt unless it changes UI behavior or user-facing copy.

Frontend architecture boundaries are defined in `docs/frontend_architecture_rules.md`. Future UI work must follow those page, feature, component, API, state, selector, config, and styling rules unless the active task explicitly updates them.

## Office Gateway Principle

All Word/Excel/Outlook access must be hidden behind infrastructure gateway classes:

```text
WordDocumentGateway
ExcelWorkbookGateway
OutlookMailGateway
```

MVP application form parsing can use python-docx first. If pywin32 is later needed, it must stay inside gateways.

Intake application-form header gating is also an Office gateway responsibility:

- Frontend and API routes must not read Word files directly.
- Application services call a validator that uses `OfficeFacade`.
- `OfficeFacade` delegates Word header table cell reads to `WordDocumentGateway`.
- Word COM, when used, stays inside `backend/infrastructure/office`.
- The stable gate for Intake to Precheck is `.docx` plus header table cell `(1,2)` containing `Laboratory Testing Request`.

## Feature Admission Checklist

Before adding any feature, answer:

1. Which Project stage does it belong to?
2. What is its input?
3. What is its output?
4. Which domain object does it change?
5. Does it affect report data?
6. What validation is required?
7. Is it MVP scope?

If unclear, do not implement.
