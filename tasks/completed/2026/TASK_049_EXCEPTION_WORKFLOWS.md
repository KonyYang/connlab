# TASK_049_EXCEPTION_WORKFLOWS

## Status

done

## Goal

Make real exception cases explicit and traceable.

## Scope

- Define explicit behavior for no-form, multi-form, missing-info, correction, and renumbering cases.
- Add operator-facing reason records or lifecycle/event evidence where needed.
- Preserve original and corrected evidence.
- Keep exception handling attached to the current project/intake lifecycle.

## Out Of Scope

- Matrix, Report, AI review, LAN deployment, permissions, or Outlook inbox auto-scan.
- Email sending or Outlook inbox automation.
- Destructive folder rename or workbook mutation unless explicitly scoped by the task.
- Frontend changes unless explicitly required.

## Inputs

- Real sample baseline.
- Current intake package/case/draft records.
- Project lifecycle guards.
- Evidence placement policy.
- LTR renumber preview behavior.

## Outputs

- Exception workflow records or explicit service/API behavior.
- Business-readable blocked/follow-up reasons.
- Tests for no-form, multi-form, missing-info, correction, and renumbering paths.
- Task board update after completion.

## Acceptance Criteria

- No application form in email creates a package needing follow-up, not a project.
- One email with multiple application forms creates separate cases/projects.
- Missing application form info blocks downstream steps until confirmed.
- Corrected application forms preserve original and communication evidence.
- LTR changes require reason and preview.

## Validation

- Run focused exception workflow tests.
- Run related intake, lifecycle, LTR, and evidence tests.
