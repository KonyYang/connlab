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

## Office Gateway Principle

All Word/Excel/Outlook access must be hidden behind infrastructure gateway classes:

```text
WordDocumentGateway
ExcelWorkbookGateway
OutlookMailGateway
```

MVP application form parsing can use python-docx first. If pywin32 is later needed, it must stay inside gateways.

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
