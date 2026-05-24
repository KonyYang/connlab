# TASK_031B_INTAKE_PACKAGE_DETAIL_FRONTEND_UX

## Status

done

## Goal

Add the intake package detail frontend surface for reviewing one package and selecting the application form asset.

## Scope

- Use `$impeccable` for UX decisions before UI edits.
- Show package metadata, source preservation state, and attachment list.
- Show application form candidate state and selected asset state.
- Provide a clear selection action surface when backend endpoints are available.
- Keep the package detail separate from case draft review.

## Out Of Scope

- Case draft review UI.
- Word parsing.
- Project confirmation.
- Outlook inbox auto-scan.
- Email sending.

## Required Implementation

- Read `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json` if present.
- Follow the current light workbench visual direction.
- Add frontend build/static validation.
- Do not add backend endpoints unless the task is explicitly revised.

## Validation

- Run frontend build/static validation when UI files are touched.
