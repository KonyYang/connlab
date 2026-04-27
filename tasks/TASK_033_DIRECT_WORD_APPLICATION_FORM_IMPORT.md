# TASK_033_DIRECT_WORD_APPLICATION_FORM_IMPORT

## Status

done

## Goal

Support direct Word application form import through the same intake review and confirm flow.

## Scope

- Accept a direct `.docx` or `.doc` application form source into intake storage.
- Create an `IntakePackage` with source type `DIRECT_APPLICATION_FORM`.
- Register the imported Word file as an `IntakeAsset`.
- Mark the asset as an application form candidate or selected form only when rules allow.
- Reuse the existing case/draft review flow instead of creating a project directly.

## Out Of Scope

- Full Word parsing implementation.
- Frontend upload wiring.
- Precheck bridge.
- Outlook inbox auto-scan.
- Email sending.

## Required Implementation

- Add a backend application service for direct Word intake import.
- Use existing intake storage and persistence boundaries.
- Validate extension and preserve original file material.
- Add unit/integration tests for happy path and invalid file rejection.

## Validation

- Run targeted pytest coverage for direct Word import.
- Run full backend pytest suite before closing.
