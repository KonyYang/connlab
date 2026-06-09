# TASK_306_PROJECT_FOLDER_PANEL_WORKBENCH_ENTRY

Status: Complete.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

TASK_306 implementation was explicitly approved and completed.

## Model Fit Assessment

GPT-5.3-codex is suitable for this task. The change is a small, bounded frontend wiring task that reuses an existing typed component, existing API client functions, existing project-workbench model data, and existing CSS conventions. It does not require new business-rule invention, backend schema design, Office automation, or rule maintenance.

## Mandatory Frontend Preconditions

Before implementation, the agent must:

- Load `$impeccable` project context for this Workbench UI change.
- Read `docs/02_ARCHITECTURE_RULES.md`.
- Read `docs/frontend_architecture_rules.md`.
- Keep ConnLab as an `$impeccable` `product` UI surface.

## Goal

Expose the existing `ProjectFolderCreationPanel` in Project Workbench so an operator can preview and generate the project folder from the Workbench preparation area.

This task follows the transition-authority principle in `docs/task_306_313_project_package_execution_series_plan.md`: the public-drive project folder remains the current official business package authority. TASK_306 only exposes the existing folder preview/generate entry in Workbench; it is not a package publish action and must not automatically promote local working material into the official package.

## Inputs

- Existing `ProjectFolderCreationPanel`.
- Existing Project Workbench runtime model.
- Existing configured folder resources:
  - project folder template
  - project output root
- Current project status.
- Latest LTR number.
- Existing folder preview/generation API calls used by the panel.

## Outputs

- Workbench displays the existing project folder creation surface.
- Folder blockers, preview, conflict, and generation behavior remain owned by the existing panel and backend FolderService.
- On successful folder generation, Workbench refreshes folder readiness through the existing `onFolderCreated` callback.

## Scope

In scope:

- Expose `folderResources` and `onFolderCreated` through the Workbench runtime model if needed.
- Render `ProjectFolderCreationPanel` in `ProjectWorkbenchLayout`.
- Keep the panel full-width in the setup/preparation area, below readiness and above Matrix workspace.
- Add/update frontend tests and static shell checks for the wiring.

Out of scope:

- No backend FolderService changes.
- No folder API changes.
- No new route.
- No Test Record generation.
- No Fee Form generation.
- No Customer Feedback Form generation.
- No evidence placement.
- No package orchestrator.
- No Confirm Fee.
- No StepInstance, TestResult, report, AI, permission, or multi-user scope.

## UX Placement Decision

Use a full-width Workbench preparation panel. Do not place folder creation in the right step column because folder setup is a project-level preparation action, not a selected Matrix step action.

## Acceptance Criteria

- Project Workbench renders a Project folder creation panel.
- The panel receives configured folder template, configured output root, latest LTR number, folder readiness, project status, project id, and `onFolderCreated`.
- If LTR or configured resources are missing/invalid, the existing blocker copy is shown.
- If conditions are met, the existing preview/generate flow remains available.
- Successful generation calls `onFolderCreated` and updates Workbench folder readiness through existing model behavior.
- No package-generation, Test Record, Fee Form, Customer Feedback, or evidence placement action appears as part of TASK_306.
- Static or component tests assert the TASK_306 `ProjectWorkbenchLayout` wiring imports/renders `ProjectFolderCreationPanel` without adding rendered `ApprovalPackagePanel`, `ProjectWorkbenchEvidencePanel`, `TestRecordDraftGenerationButton`, or Fee Form action surfaces. Historical fields/imports already present in `useProjectWorkbenchModel` are not part of this TASK_306 assertion.

## Required Validation

- `cd frontend; npm test -- --run ProjectWorkbench --watch=false`
- `cd frontend; npm run build`
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "project_workbench or folder"`
- `git diff --check`

## Stop Point

After TASK_306 implementation and validation, stop. Do not proceed to TASK_307 without a new task file/plan approval cycle.
