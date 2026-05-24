# TASK 020 — Precheck Issue Experience

## Goal

Make precheck results understandable for non-programmer lab engineers.

## Scope

Add components:

```text
frontend/src/components/precheck/PrecheckSummary.tsx
frontend/src/components/precheck/PrecheckIssueCard.tsx
frontend/src/components/precheck/IssueSeverityBadge.tsx
```

Update precheck display in:

```text
frontend/src/pages/ProjectWorkbenchPage.tsx
```

## Requirements

- Use `$impeccable` before designing or editing UI.
- Follow `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json`.

Convert technical issue display into business-readable cards:

- issue title
- severity
- field/category
- what is wrong
- expected value if available
- suggested action

If backend issue only has `message`, derive a simple display from current fields without changing backend schema.

## Out of Scope

- No AI explanation.
- No new precheck rules.
- No backend rule changes.

## Tests

- Add or update frontend static pytest checks.
- Run `npm run build`.

## Acceptance Criteria

- Precheck issues are no longer shown as raw list items only.
- Errors and warnings are visually distinct.
- User can understand what to fix next.
- Frontend build passes.
