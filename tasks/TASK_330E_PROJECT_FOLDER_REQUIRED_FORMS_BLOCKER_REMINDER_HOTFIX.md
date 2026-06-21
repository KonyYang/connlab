# TASK_330E_PROJECT_FOLDER_REQUIRED_FORMS_BLOCKER_REMINDER_HOTFIX

## Status

Complete, including review follow-up.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Allowed

TASK_330D_PROJECT_FOLDER_UPDATE_PERFORMANCE_AND_COLLECT_DTO_HOTFIX is complete and stopped at the approved boundary. A real browser/API smoke on project `72fbbfa290294da9a507344b68ff900f` confirmed that Required forms generation was correctly blocked because Project Basic Information was unconfirmed and missing required fields:

- Project Leader
- Lab Performing the Tests

The backend rule is correct, but the `Update project folder` operator flow can feel like generation silently failed when the Required forms preview is blocked. This task is a narrow UI/flow hotfix to surface the existing backend blocker clearly.

## Goal

When `Update project folder` or Required forms generation cannot proceed because Required forms preview is blocked, disable the one-click project-folder action when the blocker is already known and show an operator-readable reminder that explains the blocker and points to Basic Information when that is the missing prerequisite.

## In Scope

- Frontend Project Workbench only.
- Preserve the backend Required forms blocker rule.
- Preserve Matrix/Fee/Basic Information authority semantics.
- Derive the reminder from existing Required forms preview blockers and status.
- Disable the `Update project folder` one-click action when the current known Project Folder blocker means the flow cannot complete.
- Keep the reminder visible in the Folder Action panel and Required forms detail area.
- Stop automatic Required forms generation when preview is blocked and record a clear Required forms error/reminder instead of silently returning.
- Add/update frontend tests around the blocked Basic Information reminder path.

## Out Of Scope

- No backend Required forms generation behavior changes.
- No Basic Information schema, API, field mapping, or confirmation rule changes.
- No Office generation, Excel COM, Word write-back, or template mapping changes.
- No new generated output type.
- No Matrix, Fee, StepInstance, report, AI, permissions, LAN/server, or multi-user scope.
- No broad Project Workbench redesign.

## Acceptance Criteria

- A blocked Required forms preview with `Confirm Basic Information before generating Project Folder outputs.` appears as a clear blocker in the Project Folder/Folder Action UI.
- The displayed reminder tells the operator to confirm Basic Information before generating Required forms.
- The `Update project folder` one-click action is disabled when Required forms are already known to be blocked by Basic Information.
- The disabled action exposes the blocker reason through visible nearby text and button title/disabled reason behavior consistent with existing Workbench buttons.
- The automatic `Update project folder` chain does not continue into Required forms generation when preview is blocked.
- The manual Required forms action does not show a generic missing-context error when preview is blocked; it shows the preview blocker.
- Existing ready/current/conflict Required forms behavior remains unchanged.
- Frontend tests cover the blocked Basic Information reminder path.

## Validation

Completed validation:

```powershell
cd frontend
npm test -- --run projectFolderTaskSelectors ProjectFolderTaskList ProjectWorkbenchLayout useProjectWorkbenchModel --watch=false
# 44 passed
```

```powershell
cd frontend
npm run build
# passed
```

Review follow-up covered:

- The top `Update project folder` action now scans the Required forms task for known Basic Information blockers even when an earlier Project Folder task is the current attention item.
- The automatic one-click chain stops after a blocked Required forms preview and downgrades the overall message instead of continuing into Section 2, application-form write-back, package preview, and public-drive preview.
- Added hook-level regression coverage proving blocked Required forms does not call the downstream Section 2, application-form write-back, package preview, or public-drive preview steps.

Manual smoke:

1. Open a project whose Required forms preview is blocked by unconfirmed Basic Information.
2. Verify the Folder Action area shows the Basic Information blocker.
3. Verify `Update project folder` is disabled with the Basic Information blocker reason.
5. Confirm Basic Information, refresh/update again, and verify Required forms can generate or become current.

## Stop Point

Stop after TASK_330E. Do not proceed to backend generation changes, Office optimization, LTR workbook writeback, report generation, StepInstance, AI, permissions, LAN/server, or multi-user scope without a separate approved task.
