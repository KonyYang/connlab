# TASK_052_PROJECT_NO_OPTIONAL_DL_CENTRIC_IDENTITY

## Status

done

## Goal

Downgrade application `project_no` / `Project #` from a required business identifier to optional metadata, and make the project workflow explicitly rely on internal project IDs before LTR registration and `DL_NUMBER` after LTR registration.

## Scope

- Make `Project.project_no` optional in domain, application commands, API DTOs, frontend API types, and storage models.
- Remove `project_no` from intake confirmation required fields.
- Preserve parsed application `project_number` as optional application-form metadata when present.
- Keep project continuity based on `project_id`, `intake_package_id`, `intake_case_id`, and later `DL_NUMBER` / `ltr_number`.
- Keep `{PROJECT_NO}` folder placeholder backward-compatible but document it as optional and no longer recommended for default templates.
- Update user-facing frontend labels so project number is optional metadata, not the primary project identity.
- Update tests and docs to reflect DL-centric project management.

## Out Of Scope

- Do not implement a new full migration framework.
- Do not remove existing `project_no` columns or response fields in a breaking API cleanup.
- Do not implement Matrix, Report, AI review, LAN deployment, permissions, or Outlook inbox auto-scan.
- Do not write or mutate any external LTR workbook.
- Do not change LTR number allocation rules.

## Inputs

- Existing Project, intake confirmation, folder template, lookup, and frontend project registry code.
- User clarification that real project management and communication use `DL_NUMBER`, while application `Project #` is not critical.

## Outputs

- Updated backend model/API/storage behavior where `project_no` may be `null`.
- Intake confirmation can create a project without `project_no`.
- Folder previews do not require `{PROJECT_NO}` and docs recommend `{DL_NUMBER}` based names.
- Frontend project creation no longer requires Project No.
- Tests for optional project number, duplicate missing project numbers, and folder placeholder compatibility.
- Updated task board.

## Acceptance Criteria

- Creating a project without `project_no` succeeds.
- Confirming an intake case without `project_no` succeeds when product name and requester exist.
- Multiple projects with missing `project_no` are allowed.
- Lookup and summaries tolerate missing `project_no`.
- Folder placeholder replacement handles missing project number as an empty optional value.
- Frontend build passes.
- Backend tests pass.

## Validation

- Run relevant backend tests.
- Run full backend test suite if feasible.
- Run frontend build because user-facing labels and required fields change.
- Run `git diff --check`.
