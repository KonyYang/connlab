# TASK_306 Project Folder Panel Workbench Entry - Executable Plan

## Summary

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: `TASK_306_PROJECT_FOLDER_PANEL_WORKBENCH_ENTRY`, complete.

TASK_306 implementation was explicitly approved and completed against this plan.

TASK_306 wires the existing Project folder creation surface into Project Workbench. It is a frontend-only entry task and does not create a project package orchestrator.

This task inherits the transition-authority boundary from `docs/task_306_313_project_package_execution_series_plan.md`: the public-drive project folder remains the current official business package authority. TASK_306 only makes the existing folder preview/generate workflow visible from Workbench; it does not publish a package, classify official deliverables, or promote local working material into the public-drive package.

Mandatory frontend preconditions before implementation:

- Load `$impeccable` project context.
- Read `docs/02_ARCHITECTURE_RULES.md`.
- Read `docs/frontend_architecture_rules.md`.
- Treat this as a ConnLab product UI change.

## Task Understanding

Goal:

- Make Project folder preview/generation accessible from Project Workbench.

Inputs:

- `ProjectFolderCreationPanel`
- Workbench model fields for folder resources, latest LTR, folder readiness, project status, and folder-created refresh callback
- Existing folder preview/generate API behavior

Outputs:

- Workbench includes a project-level folder creation panel.
- Existing blocker/preview/generation behavior remains unchanged.

Modules involved:

- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- existing `ProjectFolderCreationPanel`
- project-workbench tests/static shell tests

Not allowed:

- No backend code.
- No API client change unless existing types are not exposed through the runtime model.
- No package orchestrator.
- No evidence placement.
- No Test Record, Fee Form, or Customer Feedback generation.
- No broad Workbench redesign.

## Design

Expose the existing model data through `ProjectRuntimeConsoleModel`:

- `folderResources`
- `onFolderCreated`

Render `ProjectFolderCreationPanel` in `ProjectWorkbenchLayout` after the readiness strip and before the Matrix workspace. Pass:

- `configuredTemplate={runtimeModel.folderResources.template}`
- `configuredOutputRoot={runtimeModel.folderResources.outputRoot}`
- `folderReady={runtimeModel.folderReady}`
- `latestLtrNumber={runtimeModel.latestLtr}`
- `projectId={project.project_id}`
- `projectStatus={project.status}`
- `onFolderCreated={runtimeModel.onFolderCreated}`

Keep the panel full-width. This preserves the current Workbench principle that setup/output materials are project-level surfaces, while the right column remains focused on selected step context.

## Tests

Add or update focused frontend tests:

- `ProjectWorkbenchLayout` renders Project folder creation when given folder resources.
- The panel receives project status, latest LTR, folder readiness, and configured resources.
- Missing folder resources show existing blocker text through the reused panel.
- Workbench does not render new package, Test Record, Fee Form, Customer Feedback, or evidence placement actions as part of this task.
- Static shell or component tests assert the TASK_306 `ProjectWorkbenchLayout` wiring imports/renders `ProjectFolderCreationPanel` and does not add rendered `ApprovalPackagePanel`, `ProjectWorkbenchEvidencePanel`, `TestRecordDraftGenerationButton`, or Fee Form action surfaces. Existing historical model-layer imports/fields in `useProjectWorkbenchModel` are not part of this TASK_306 assertion.

Run:

- `cd frontend; npm test -- --run ProjectWorkbench --watch=false`
- `cd frontend; npm run build`
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "project_workbench or folder"`
- `git diff --check`

## Risks And Guards

- The existing panel is 269 lines and may be visually large. TASK_306 should wire it without redesigning it; any later UX simplification should be a separate task.
- Folder generation can create real filesystem output. Browser smoke should verify visibility and preview. Actual generate should only be performed when the operator explicitly wants to test a safe target.
- Existing folder conflict/no-overwrite behavior must remain backend-authoritative.

## Completion Criteria

- TASK_306 task file remains the source of implementation scope.
- Workbench exposes the folder panel.
- Tests/build/checks pass.
- `docs/task_board.md` is updated to TASK_306 complete with validation results and the next task awaiting explicit approval.
