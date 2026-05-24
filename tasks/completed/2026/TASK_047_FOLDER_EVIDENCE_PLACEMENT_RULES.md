# TASK_047_FOLDER_EVIDENCE_PLACEMENT_RULES

## Status

active

## Goal

Define and implement project-folder evidence placement for email, selected application forms, attachments, specifications, LTR evidence, and corrections.

## Scope

- Define deterministic evidence placement rules for existing project assets and intake evidence.
- Preserve original `.msg`, selected application form, supporting attachments, specifications, LTR preview/commit evidence, and correction evidence.
- Preview placement before execution.
- Copy evidence without deleting or overwriting existing files.
- Add tests with temporary directories.

## Out Of Scope

- Matrix, Report, AI review, LAN deployment, permissions, or Outlook inbox auto-scan.
- External workbook mutation.
- LTR renumber execution.
- Project folder destructive rename.
- Frontend changes unless explicitly required.

## Inputs

- Current folder generation records.
- Project `FileAsset` records.
- Phase 6A intake evidence records where available.
- LTR preview/local commit audit notes.

## Outputs

- Evidence placement rule module and/or application service.
- Preview and execution behavior only where safe and explicitly scoped.
- Tests for no-overwrite evidence copy behavior.
- Task board update after completion.

## Acceptance Criteria

- Original email evidence is preserved when available.
- Selected application form and supporting attachments are placed separately.
- Specifications can be placed under a predictable specifications area.
- LTR evidence can be placed under a predictable LTR area.
- Existing files are not overwritten.
- Corrected evidence appends instead of deleting old evidence.

## Validation

- Run focused evidence placement tests.
- Run related folder/LTR tests if shared paths are touched.
