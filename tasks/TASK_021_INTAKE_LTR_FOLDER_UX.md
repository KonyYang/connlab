# TASK 021 — Intake, LTR, And Folder UX Refinement

## Goal

Improve the three MVP action panels: upload application form, register LTR, preview/generate folder.

## Scope

Frontend only unless a tiny API DTO display fix is necessary.

## Requirements

Use `$impeccable` before designing or editing UI. Follow `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json`.

Application Form:

- Use a clear upload panel.
- Show uploaded form metadata.
- Show next action after upload.

LTR:

- Show latest LTR clearly.
- Show not registered / registered status.
- Keep simple registration input.

Folder:

- Show folder preview as a tree-like preview.
- Display conflict status clearly.
- Disable generate button when conflict exists.
- Avoid overwhelming users with raw paths first.

## Out of Scope

- No file picker integration with Windows shell.
- No template management page.
- No automatic LTR application.
- No real email/Word intake implementation.

## Tests

- Add or update frontend static pytest checks.
- Run `npm run build`.

## Acceptance Criteria

- Existing API calls still work.
- User sees clear action state for each MVP step.
- Frontend build passes.
