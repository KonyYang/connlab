# TASK 017 — App Shell With Left Navigation

## Goal

Replace the current landing-page style shell with a modern app shell using left navigation and a main work area.

## Scope

Modify frontend only.

Create components:

```text
frontend/src/components/layout/AppShell.tsx
frontend/src/components/layout/Sidebar.tsx
frontend/src/components/layout/TopBar.tsx
```

Update:

```text
frontend/src/App.tsx
frontend/src/styles.css
```

## Requirements

- Use `$impeccable` before designing or editing UI.
- Follow `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json`.
- Left sidebar includes Dashboard, Projects, Intake, Precheck, LTR, Folders, Settings.
- Disabled future placeholders must be clearly unavailable.
- Main area renders current routes.
- Remove oversized hero layout.
- Preserve existing routes `/projects` and `/projects/:id`.

## Out of Scope

- No Matrix page.
- No Report page.
- No authentication.
- No backend changes.

## Tests

- Add or update frontend static pytest checks for layout files.
- Run `npm run build`.

## Acceptance Criteria

- App opens with left navigation.
- Existing project list and detail routes still work.
- Frontend build passes.
