# TASK_031A_INTAKE_INBOX_FRONTEND_UX

## Status

done

## Goal

Add the intake inbox frontend entry point for Phase 6A package intake.

## Scope

- Use `$impeccable` for UX decisions before UI edits.
- Add or adapt the frontend navigation entry for Intake.
- Show intake packages as a review queue.
- Provide a clear import entry for `.msg` / direct document intake when backend endpoints are available.
- Keep the existing Project workbench flow intact.

## Out Of Scope

- Package detail review UI.
- Case draft review UI.
- Word parsing.
- Project confirmation.
- Outlook inbox auto-scan.

## Required Implementation

- Read `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json` if present.
- Follow the current light workbench visual direction.
- Add frontend tests or build/static validation appropriate to the touched code.
- Do not add backend endpoints unless the task is explicitly revised.

## Validation

- Run frontend build/static validation when UI files are touched.
- Run relevant backend tests only if backend code is touched.
