# Merge Readiness Pytest Failure Fix Plan

## Scope

Fix the 23 pytest failures found during merge readiness evaluation for
`codex/task-321-required-forms` before merging to `master`.

This is a validation repair task only. It must not add product functionality or
advance to any later ConnLab task.

## Current Phase And Allowed Task

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active branch task state: TASK_321 and TASK_315F are complete.
- Allowed now because the user explicitly approved fixing the merge-blocking
  pytest failures before merging.

## Failure Groups

1. Historical static frontend shell guards are asserting old component names,
   class names, or copy after Project Folder / Workbench refactors.
2. Official Workspace service unit fixtures still assume local workspace
   preview/create can proceed without a registered DL number.
3. Historical phase-board tests assert exact old task-board active-state text
   after the board was compacted and updated to the Phase 11 completed state.

## Planned Changes

- Update stale tests or fixtures so they assert the current approved Phase 11
  behavior instead of old implementation details.
- Only change production code if a failure proves a real behavior regression.
- Preserve TASK_321 boundaries: no package execute UI, no StepInstance/report/AI,
  no permissions/LAN/multi-user scope, no new workflow actions.

## Validation

Run:

```powershell
py -m pytest --last-failed -q --tb=short
py -m pytest -q
cd frontend
npm test -- --run --watch=false
npm run build
```

Then re-check merge readiness and merge only if validation is green.
