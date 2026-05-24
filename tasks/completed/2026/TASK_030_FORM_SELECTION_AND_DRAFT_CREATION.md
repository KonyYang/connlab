# TASK_030_FORM_SELECTION_AND_DRAFT_CREATION

## Status

done

## Goal

Use a human-selected application form asset to create an intake case and editable intake draft.

## Scope

- Accept one selected `IntakeAsset` from an existing `IntakePackage`.
- Require the selected asset to be a candidate or Word document asset.
- Create or update `IntakeCase` without creating a final `Project`.
- Create an `IntakeDraft` placeholder for later form parsing and human correction.
- Preserve human confirmation as the gate before formal project creation.

## Out Of Scope

- Full Word body/header/table parsing.
- Project creation.
- Frontend selection UI.
- Precheck bridge.
- Outlook inbox auto-scan.

## Required Implementation

- Add a backend application service for form selection and draft creation.
- Keep repository writes explicit and testable.
- Do not parse Word content in this task.
- Add unit/integration tests for selection, invalid asset rejection, and draft creation.

## Validation

- Run targeted pytest coverage for form selection and draft creation.
- Run full backend pytest suite before closing.
