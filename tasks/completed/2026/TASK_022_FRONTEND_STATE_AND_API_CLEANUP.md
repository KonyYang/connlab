# TASK 022 — Frontend State And API Cleanup

## Goal

Clean frontend state and API usage after the UI refactor so code remains maintainable.

## Scope

- Keep `frontend/src/api/client.ts` as the only API client entry.
- Avoid duplicating fetch logic in pages.
- Extract repeated status mapping helpers.
- Extract workflow state derivation helper.

Suggested file:

```text
frontend/src/components/workflow/workflowState.ts
```

## Requirements

- Use `$impeccable` before changing UI state language, component structure, or UX copy.
- Follow `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json`.
- Keep pages readable.
- Avoid giant component files.
- Keep API calls centralized.
- Preserve existing backend contracts.

## Out of Scope

- No Redux or global state library.
- No React Query unless explicitly approved.
- No new backend features.

## Tests

- Add or update frontend static pytest checks.
- Run `npm run build`.

## Acceptance Criteria

- `ProjectWorkbenchPage.tsx` is smaller and easier to read.
- API calls stay centralized.
- Frontend build passes.
