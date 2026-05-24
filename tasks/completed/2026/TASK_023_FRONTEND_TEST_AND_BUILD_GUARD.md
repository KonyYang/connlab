# TASK 023 — Frontend Build And Smoke Guard

## Goal

Add minimal frontend validation so future UI changes do not silently break MVP flow.

## Scope

- Use `$impeccable` before changing frontend smoke checklist wording or UI validation expectations.
- Follow `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json`.
- Add or update a smoke checklist.
- Add a script or documented command that runs frontend build.
- Update README with frontend validation command.
- Optional component tests only if a test framework already exists or is explicitly approved.

## Recommended File

```text
docs/archive/validation_summaries/frontend_smoke_checklist.md
```

## Smoke Checklist Must Cover

- project list loads
- project can be created
- project detail opens
- application form upload UI appears
- precheck panel appears
- LTR panel appears
- folder preview/generate panel appears
- Matrix/Report are not exposed as active features

## Out of Scope

- No end-to-end browser automation yet.
- No Playwright/Cypress unless explicitly approved.

## Tests

- Run `npm run build`.
- Run relevant pytest checks.

## Acceptance Criteria

- Frontend build passes.
- `docs/archive/validation_summaries/frontend_smoke_checklist.md` exists.
- README points to frontend validation.
