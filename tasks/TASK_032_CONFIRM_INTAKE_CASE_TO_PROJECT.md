# TASK_032_CONFIRM_INTAKE_CASE_TO_PROJECT

## Status

done

## Goal

Convert a human-reviewed intake case into formal MVP project records.

## Scope

- Confirm one `IntakeCase` after human review.
- Create `Project`, `ApplicationForm`, `SampleInfo`, and selected `FileAsset` records from reviewed draft data.
- Link the confirmed project back to `IntakeCase.confirmed_project_id`.
- Preserve the selected source asset and supporting attachments as traceable records.
- Keep confirmation explicit and non-automatic.

## Out Of Scope

- Word parsing implementation.
- Frontend confirmation wiring.
- Precheck bridge.
- Outlook inbox auto-scan.
- Email sending.

## Required Implementation

- Add a backend application service for confirmation.
- Validate package, case, selected asset, and draft existence.
- Parse draft JSON deterministically and reject missing required project fields.
- Add unit/integration tests for happy path and rejection cases.
- Do not create project records from unreviewed or already confirmed cases.

## Validation

- Run targeted pytest coverage for intake confirmation.
- Run full backend pytest suite before closing.
