# TASK_029_APPLICATION_FORM_CANDIDATE_DETECTION

## Status

done

## Goal

Detect and score likely application form candidates from stored intake assets without auto-confirming the final application form.

## Scope

- Read `IntakeAsset` records for one intake package.
- Score candidates using deterministic metadata rules first.
- Prefer `.docx` / `.doc` files with application-form-like names.
- Preserve human confirmation as the required decision gate.
- Persist candidate role and score back to intake asset storage.

## Out Of Scope

- Outlook inbox auto-scan.
- AI classification.
- Project creation from a candidate.
- Full DOCX field parsing.
- Frontend candidate selection UI.

## Required Implementation

- Add a backend application or module service for candidate detection.
- Keep rules deterministic and testable.
- Add unit tests for scoring and edge cases.
- Add integration coverage for repository update behavior if persistence is touched.

## Validation

- Run targeted pytest coverage for candidate scoring.
- Run full backend pytest suite before closing.
