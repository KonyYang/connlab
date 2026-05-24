# TASK 018 — Project Dashboard Redesign

## Goal

Redesign the project list page into a usable dashboard for lab engineers.

## Scope

Update:

```text
frontend/src/pages/ProjectListPage.tsx
```

Add components as needed:

```text
frontend/src/components/project/ProjectStatusBadge.tsx
frontend/src/components/common/EmptyState.tsx
frontend/src/components/common/ErrorMessage.tsx
frontend/src/components/common/LoadingState.tsx
```

## Requirements

- Use `$impeccable` before designing or editing UI.
- Follow `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json`.
- Show project number, product name, requestor, business unit, and status.
- Prefer table or dense dashboard rows for project lists.
- Add client-side search if backend search is not available.
- Keep create project form, but redesign it as a compact New Project panel.
- Show clear empty/loading/error states.

## Out of Scope

- No advanced filtering API.
- No pagination.
- No multi-user features.

## Tests

- Add or update frontend static pytest checks.
- Run `npm run build`.

## Acceptance Criteria

- User can still create a project.
- User can still open a project.
- Page reads as a dashboard, not a landing page.
- Frontend build passes.
