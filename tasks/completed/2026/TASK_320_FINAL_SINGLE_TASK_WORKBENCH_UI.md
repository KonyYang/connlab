# TASK_320_FINAL_SINGLE_TASK_WORKBENCH_UI

Status: Complete.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: TASK_320 is complete after explicit user approval. Do not enter a later task without separate user approval.

Executable plan:

- `docs/task_320_final_single_task_workbench_ui_plan.md`

## Goal

Finish the Project Workbench `Project Folder` UI contraction defined by TASK_317A after TASK_317-TASK_319 landed their capabilities, so operators see one process-based Project Folder preparation flow rather than a wide status grid and several disconnected panels.

## User Story

As a lab operator, I want the Workbench to tell me which Project Folder task needs attention and show the details for that task in one focused area, so I can create or repair the local project folder, collect request material, confirm fee, review required files, update Section 2, check Submitted Material, and upload to the public drive without understanding package/workspace/internal readiness concepts.

## Why This Task Exists

TASK_317A defined the target Project Folder information architecture. TASK_317, TASK_318, and TASK_319 added request material collection, official folder check/repair, and public-drive upload preview/update. The implementation is safer now, but the UI still has these remaining problems:

- The Project Folder tab still starts with a wide checklist grid that reads like many status cards rather than a single task flow.
- Request material and public-drive upload are separate panels instead of details for the relevant selected task.
- `packageStatus`, `packageBlockers`, and `actionTarget: "package"` still influence the user-facing flow even though `Package` should no longer be an operator concept.
- The stage/next-action area can feel large compared with the actual work, especially after the page already has Project Folder tabs and task rows.
- The page still does not clearly show the user's process order from local folder to public-drive upload as one vertical preparation list.

TASK_320 is the final UI-only contraction pass for this series.

## User-Facing Naming Contract

Use these names in user-facing UI:

- `Project Folder`
- `Local project folder`
- `Local DL folder`
- `Official project folder`
- `Source Book`
- `Request material`
- `Confirmed Fee authority`
- `Required forms`
- `Application Form Section 2`
- `Submitted Material`
- `Public drive upload`
- `Execution`

Avoid these user-facing names in the Project Folder flow:

- `Package`
- `Project package`
- `Workspace`
- `Orchestrator`
- `.connlab`
- `manifest`
- `SQLite`
- API route names

Internal code and API names may retain `package` where renaming would be unsafe or outside scope, but TASK_320 must hide those names from operator-facing Workbench copy.

## Target UI Contract

For a project with a DL number and active Confirmed Matrix, the Workbench should present:

```text
Header:
  DL number + Sample Description + Test Item

Compact next action:
  One task title
  One reason
  One primary action

Tabs:
  Project Folder | Execution

Project Folder:
  Left or top task list:
    Local project folder
    Request material
    Confirmed Fee authority
    Required forms
    Application Form Section 2
    Submitted Material
    Public drive upload

  Current task detail:
    Details and preview for the selected task only
    Default selection is the system current task
    User can click any task row to inspect that task detail
    Row-level/detail-level action when the task has an approved action
```

The Project Folder surface must read as one preparation sequence. It must not read as a dashboard of unrelated cards.

## Selection And Action Contract

The task list must support both system guidance and user inspection:

- `currentTaskKey` is the system-recommended next task derived from blockers/readiness.
- `selectedTaskKey` is the user-visible detail selection.
- On initial render, `selectedTaskKey` defaults to `currentTaskKey`.
- Clicking a task row changes `selectedTaskKey` and updates the detail panel without changing the underlying lifecycle state.
- The selected row and the current row may be the same, but they are not the same concept.
- The current row may have a subtle "Current task" marker; non-current rows must remain inspectable.
- Keyboard users must be able to focus and select task rows.

Actions must be row/task scoped:

- A row or detail panel may show an enabled action only when the task has an approved existing action.
- The action contract must pass a task-scoped action target to the existing Workbench action handler.
- The top next action remains the primary recommendation, but it must not be the only way to act on a selected task.
- If a selected task has no approved action, show a non-actionable state explanation instead of a disabled fake workflow button.

## Project Folder Task Rows

TASK_320 should consolidate the current setup materials into a row model with stable row keys.

Required rows:

1. `Local project folder`
   - Status sources: official workspace preview/record and official folder check.
   - Shows concise status: Created / Not created / Needs repair / Conflict.
   - Details may include Local DL folder and Official project folder paths.
   - Actions may route to create/review local project folder or repair folder structure.

2. `Request material`
   - Status source: TASK_317 request material preview.
   - Shows concise status: Ready to collect / Collected / Needs review / Conflict / Partial.
   - Details show files checked, already collected, needs review, blockers/warnings.
   - Action: `Collect request material` only when copyable material remains.

3. `Confirmed Fee authority`
   - Status source: the current Confirmed Fee authority read model already loaded by Workbench, such as `versionStatus.downstream` or the existing Confirmed Fee API-derived state.
   - Shows business authority state only: Missing / Confirmed / Stale.
   - Action: `Open Fee Evaluation` when missing or stale.
   - Must not imply Fee form file generation.

4. `Required forms`
   - Status source: `ProjectOutputStatusSummary` or the existing generated-output summary read model. Do not infer generated form readiness from old package preview wording.
   - Shows file-output state only: Missing files / Ready / Stale / Deferred.
   - May mention Customer Feedback, Fee form, and Test Record as output items.
   - Must distinguish `Confirmed Fee authority is confirmed` from `Fee form file exists/generated`.
   - No broad generation action may silently confirm Fee, update Section 2, upload to public drive, repair folder conflicts, or collect request material.
   - If generation is not implemented or not currently approved, show a read-only deferred state.

5. `Application Form Section 2`
   - Status source: Section 2 sync preview.
   - Shows Not updated / Preview ready / Written / Stale / Blocked.
   - Treat as controlled preview/write-back, not a normal generated file.
   - Action must remain within the existing Section 2 approved behavior.

6. `Submitted Material`
   - Status source: official folder check required files and request material collection.
   - Shows Ready / Missing files / Needs review / Conflict.
   - Action routes to refresh/check, not to broad package preview.

7. `Public drive upload`
   - Status source: TASK_319 public-drive upload preview.
   - Shows Not configured / Ready to upload / Already current / Warning / Conflict / Blocked.
   - Details show target path, add/update/current/conflict counts, warnings/blockers, and item list.
   - Action: `Upload to public drive` only after Project Folder readiness is loaded and ready.

## Next Action Rules

Show one primary top action. The selector should use this priority:

1. Missing DL number: plan Matrix / register formal project entry as current existing behavior allows.
2. Missing active Matrix authority: `Open Matrix`.
3. Missing local project folder: `Create local project folder`.
4. Folder structure conflict or missing repairable folders: `Repair folder structure` or review conflict.
5. Request material ready or partial with copyable items: `Collect request material`.
6. Request material review-only: `Review request material`.
7. Missing or stale Confirmed Fee authority: `Open Fee Evaluation`.
8. Required generated files missing or stale: show read-only/deferred unless the current code has an approved generation action.
9. Application Form Section 2 missing/stale: existing Section 2 action if approved and available.
10. Submitted Material incomplete: `Check Submitted Material` / refresh folder check.
11. Public drive preview blocked/conflict/warning/ready/current: current TASK_319 action rules.
12. Everything ready/current: `Open official project folder` only if an existing safe open action is available; otherwise show read-only `Project Folder is ready`.

If a task action is not implemented by previous approved tasks, TASK_320 must not create a fake enabled button for it.

## Required Implementation Shape

TASK_320 should be frontend-only unless review finds an unavoidable typed DTO gap.

Expected frontend shape:

```text
frontend/src/features/project-workbench/
  projectFolderTaskSelectors.ts          # new row/task model selectors
  ProjectFolderTaskList.tsx              # new compact task list + selected row
  ProjectFolderTaskDetailPanel.tsx       # new current-task details
  ProjectWorkbenchLifecycleSections.tsx  # compose new Project Folder surface
  ProjectWorkbenchLayout.tsx             # pass existing previews/results only
  projectWorkbenchLifecycleSelectors.ts  # remove package-facing action terminology
  ProjectWorkbenchLayout.test.tsx
  projectWorkbenchLifecycleSelectors.test.ts
frontend/src/workbench.css
tests/unit/test_frontend_shell_files.py
```

Allowed alternative:

- If implementing separate `ProjectFolderTaskDetailPanel.tsx` is too large for the current code shape, `ProjectFolderTaskList.tsx` may own both row and detail rendering, but the file must stay focused and should not become another multi-purpose Workbench page.

## Scope

Allowed:

- Frontend information architecture and copy cleanup.
- Project Folder task row selector/model.
- Project Folder row/detail rendering.
- User-selectable task details with default selection from current task.
- Row/detail scoped action routing to existing approved handlers.
- Compact next-action visual treatment.
- Consolidation of request-material and public-drive preview panels under their task details.
- CSS adjustments to remove horizontal overflow and improve density.
- Tests and static guards.
- Task board and plan index updates after completion.

Not allowed:

- Backend API changes unless a typed frontend contract cannot represent existing data.
- Database schema changes.
- File-system write behavior changes.
- Public-drive upload semantics changes.
- Request material copy behavior changes.
- Folder repair behavior changes.
- Section 2 Word write-back behavior changes.
- Test Record/Fee form/Customer Feedback generation implementation.
- StepInstance/TestResult/evidence/photo/report/AI/permissions/LAN/multi-user work.
- Renaming internal backend routes or database concepts from `package` to `project folder`.

## Acceptance Criteria

- Workbench active Matrix projects show only `Project Folder | Execution` tabs.
- The Project Folder tab shows a process task list, not a wide wall of status cards.
- The task list defaults to the system current task, and users can click `Request material`, `Application Form Section 2`, or `Public drive upload` to inspect those task details.
- Row/detail actions call existing approved action handlers through a task-scoped action target.
- Request material details appear under the `Request material` task detail, not as a disconnected panel.
- Public-drive upload preview appears under the `Public drive upload` task detail, not as a disconnected panel.
- The top next action is visually compact and shows one action only.
- User-facing Project Folder flow contains no `Package`, `Project package`, `Workspace`, `.connlab`, `manifest`, `SQLite`, or API route terms.
- `Confirmed Fee authority` and generated `Fee form` remain separate concepts.
- Tests cover the case where Confirmed Fee authority is confirmed while the generated Fee form is missing/deferred.
- `Application Form Section 2` remains a controlled preview/write-back task, not a generic required form.
- No enabled action appears for unimplemented generated-file work.
- No page-level horizontal scrollbar appears at 1280px or 740px wide Workbench smoke viewports.
- Existing public-drive upload preview safety behavior remains unchanged.
- Existing TASK_317 request material, TASK_318 folder check/repair, and TASK_319 public-drive upload tests still pass.

## Validation

Required commands after implementation:

```powershell
cd frontend; npm test -- --run ProjectWorkbenchLayout projectWorkbenchLifecycleSelectors --watch=false
cd frontend; npm run build
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "project_workbench or task320 or public_drive or request_material or official_folder"
git diff --check
```

Recommended adjacent regression:

```powershell
py -m pytest tests\unit\test_project_request_material_collection_service.py tests\unit\test_official_project_folder_check_service.py tests\unit\test_public_drive_upload_service.py -q
```

Browser smoke:

- Open `http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f`.
- Confirm Project Folder tab has no page-level horizontal scroll.
- Confirm one next action is visible.
- Confirm task rows are readable and ordered.
- Confirm selecting/opening request material and public-drive upload details does not obscure or duplicate information.
- Confirm Execution tab still shows Matrix execution map and Step workspace.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for TASK_320 because this is a bounded frontend/UI information architecture cleanup with existing typed data sources and strong regression tests. The main risks are scope creep into backend/file operations and over-polishing the UI beyond the approved Workbench contraction. The task therefore forbids backend/file behavior changes and requires tests plus browser smoke before closure.

## Approval Gate

This task file is for review only. Implementation must not start until the user explicitly approves TASK_320 implementation.
