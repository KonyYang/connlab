# TASK_048_PROJECT_LIFECYCLE_GATING

## Status

done

## Goal

Prevent operations that are invalid for the current project lifecycle stage.

## Scope

- Add lifecycle operation guards around current `ProjectStatus` values.
- Integrate guards into LTR preview/commit, folder generation, and evidence placement.
- Return business-readable blocking reasons.
- Keep existing `ProjectStatus` enum stable unless a later task explicitly changes it.
- Add tests for allowed and blocked operations.

## Out Of Scope

- Matrix, Report, AI review, LAN deployment, permissions, or Outlook inbox auto-scan.
- New role/permission model.
- Broad lifecycle enum replacement.
- Lifecycle event persistence unless required for the guard implementation.
- Frontend changes unless explicitly required.

## Inputs

- Current `Project` and `ProjectStatus` values.
- Existing intake, precheck, LTR, folder, and evidence services.
- Phase 7 lifecycle governance plan.

## Outputs

- `backend/application/project_lifecycle_service.py`.
- Guard integration through application services.
- Tests for invalid next actions and closed/cancelled project mutation blocks.
- Task board update after completion.

## Acceptance Criteria

- LTR preview/commit is blocked before confirmed project data.
- Folder generation is blocked before LTR registration prerequisites.
- Evidence placement execution is blocked before project folder creation.
- Closed/cancelled projects cannot be mutated by guarded operations.
- Blocked operations return business-readable reasons.
- Current `ProjectStatus` is not needlessly expanded or broken.

## Validation

- Run focused lifecycle guard tests.
- Run related LTR/folder/evidence integration tests.
- Run full backend tests if possible.
