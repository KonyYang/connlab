# TASK_037_REAL_SAMPLE_BASELINE

## Status

done

## Goal

Build a documented compatibility baseline for the four real Outlook `.msg` samples and two real `.docx` application forms without committing original sensitive files.

## Scope

- Inspect the real sample inventory under `C:\Users\White\Desktop\AI information`.
- Validate the existing Phase 6A intake path behavior against the samples where safe.
- Document expected classification and operator action for each `.msg` sample.
- Document parser coverage notes for each `.docx` form.
- Define sanitized or generated fixture strategy for regression tests.
- Create or update `docs/phase7_real_sample_baseline.md`.

## Out Of Scope

- Parser hardening implementation.
- LTR field catalog.
- LTR number generation.
- LTR workbook read/write.
- Folder evidence placement.
- Lifecycle guards.
- Matrix, Report, AI review, LAN deployment, permissions, or Outlook inbox auto-scan.
- Committing original `.msg` or `.docx` files.

## Inputs

- `docs/ConnLab_Phase7_Real_LTR_Folder_Lifecycle_Plan.md`
- `docs/phase6a_validation.md`
- Real files in `C:\Users\White\Desktop\AI information`
- Existing Phase 6A intake services

## Outputs

- `docs/phase7_real_sample_baseline.md`
- Fixture strategy for later tests
- Task board update after completion

## Acceptance Criteria

- Each `.msg` sample has expected classification:
  - no application form
  - one application form
  - multiple application forms
  - application form plus specification
- Each `.docx` form has parser field coverage notes.
- Real sample paths are documented but not hard-coded into code.
- Originals are not committed.
- No Phase 7 downstream implementation is started.

## Validation

- Static documentation review.
- Optional safe compatibility/probe commands may be run if they do not mutate real samples.
