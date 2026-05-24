# TASK_144 Project Setup Draft-Scoped Autosave Plan

## Scope

Make `Project setup confirmation` belong to the selected application draft instead of
the page instance. This covers Test Item, Sample Description, Location, Test Type in
sheet, Project Leader, LTR mode, and specified LTR input.

## Implementation

1. Backend review model
   - Add `project_setup` to `IntakeCaseReviewItem`.
   - Load it from `manual_overrides_json.project_setup`.
   - Persist it through `update_case_fields(..., project_setup=...)`.

2. API contract
   - Add `project_setup` to `IntakeCaseReviewItemResponse`.
   - Add optional `project_setup` to `UpdateIntakeCaseReviewFieldsRequest`.

3. Frontend state flow
   - Add `project_setup` to `IntakeCaseReviewItem`.
   - Initialize `setupValues` from the active case when `case_id` changes.
   - Include setup values in the existing autosave payload.
   - Include setup changes in the dirty calculation.

4. Tests and docs
   - Add/extend static frontend shell assertions.
   - Add/extend backend review-fields persistence coverage.
   - Update task board after validation.

## Acceptance

- Switching application forms restores that form's setup confirmation values.
- Loading an existing draft restores its setup values.
- New drafts start from default setup values.
- Existing no-setup drafts remain compatible.
- Completion uses the currently loaded case-scoped setup values.
