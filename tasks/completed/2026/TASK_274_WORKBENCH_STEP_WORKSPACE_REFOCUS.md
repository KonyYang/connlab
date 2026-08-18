# TASK_274_WORKBENCH_STEP_WORKSPACE_REFOCUS

## Status

Complete. Implemented and validated on 2026-05-26.

## Current Execution Context

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current product direction: `Matrix-driven Laboratory Execution Phase`
- Current task status: `TASK_274_WORKBENCH_STEP_WORKSPACE_REFOCUS` complete
- Allowed reason: `TASK_273_MATRIX_EDITOR_WORKBENCH_SMOKE_UI_FIXES` is complete, `docs/task_board.md` sets `TASK_274_WORKBENCH_STEP_WORKSPACE_REFOCUS` as the current active planned task (awaiting approval), and user smoke testing clarified that Project Workbench should keep the existing right-side Step Workspace as the future execution workspace while simplifying the Matrix projection surface.

## Source Inputs

Primary source:

- User smoke-test feedback on the Workbench page after TASK_273.

Relevant project rules:

- `$impeccable` product register.
- `PRODUCT.md`
- `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/project_management/TASK_REVIEW_CHECKLIST.md`

## Objective

Refocus Project Workbench around the existing right-side Step Workspace as the main step execution workspace direction, while simplifying the left Matrix projection to a single read-only Matrix table surface.

This task is a frontend UI refocus slice. It must not add StepInstance persistence, test data persistence, image/evidence upload, report automation, permissions, or new backend behavior.

## User Problems

1. The new read-only `Record Step Workspace` duplicates the existing right-side Step Workspace and only displays information.
2. The existing right-side Step Workspace better matches the business direction because it is the natural place for step confirmation, test data entry, image/evidence entry, Record flow, and lifecycle management.
3. The left `Matrix execution projection` repeats its own title and explanatory container, creating two nested layers of similar information.
4. `Authority Change History` is not needed on the main Workbench page and distracts operators.
5. `Generate Test Record Draft` is redundant on the Matrix projection because the right-side `Record` action is the natural entry for record generation.

## Scope

In scope:

- Remove the new read-only `Record Step Workspace` from `ProjectWorkbenchMatrixProjectionPanel`.
- Keep the existing right-side `Step Workspace` in `ProjectWorkbenchLayout`.
- Keep the right-side `Step Workspace` as a mock or disabled future-oriented surface only where current project rules allow it.
- Simplify the left Matrix projection to one clear title and one Matrix table region.
- Hide `Authority Change History` from the main Workbench projection panel.
- Hide or remove `Generate Test Record Draft` from the main Matrix projection panel.
- Keep backend/API/services/tests for authority history and Word draft generation intact.
- Keep frontend client functions and focused component tests unless static guards require dead UI cleanup.
- Add static guards that prevent the removed main Workbench UI elements from returning accidentally.
- Update relevant frontend tests.
- Update task and board status after implementation.

Out of scope:

- Deleting backend authority history APIs or services.
- Deleting backend Test Record Word generation APIs or services.
- Implementing the right-side `Record` button.
- Implementing real test data entry.
- Implementing image or evidence upload.
- Implementing StepInstance, execution persistence, lifecycle persistence, or report binding.
- Adding new backend APIs.
- Changing ConfirmedMatrix authority rules.
- Redesigning the whole Workbench shell.
- Making future disabled actions active.

## Expected File Changes

Likely modify:

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx` if present or if added by implementation
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- `docs/task_board.md`
- `docs/task_plan_index.md`
- `tasks/TASK_274_WORKBENCH_STEP_WORKSPACE_REFOCUS.md`

Likely preserve:

- `frontend/src/features/project-workbench/AuthorityChangeHistoryPanel.tsx`
- `frontend/src/features/project-workbench/AuthorityChangeHistoryPanel.test.tsx`
- `frontend/src/features/project-workbench/TestRecordDraftGenerationButton.tsx`
- `frontend/src/features/project-workbench/TestRecordDraftGenerationButton.test.tsx`
- backend authority history files
- backend Test Record Word generation files

No backend files should be modified.

## UI / UX Requirements

- ConnLab register: `product`.
- Physical scene: a lab engineer or coordinator works from a confirmed Matrix and needs the Workbench to prioritize step execution context over audit or generation controls.
- Matrix projection should answer: what must be tested, by group and step.
- Right-side Step Workspace should answer: what step is selected, what data/evidence/lifecycle will be managed here later.
- Do not show audit history as main operator content.
- Do not show Word draft generation as a top-level Matrix action.
- Avoid nested cards and repeated headings.
- Keep copy operational and concise.

## Behavioral Requirements

### Matrix Projection

- The Workbench Matrix area should render one primary `Matrix execution projection` title.
- The projection panel should not render another duplicate `Matrix execution projection` heading inside a framed nested card.
- The projection table remains read-only and token cells remain selectable if already supported.
- Selecting Matrix tokens may continue to update the existing right-side Step Workspace where current wiring supports it.

### Step Workspace

- The existing right-side `Step Workspace` remains visible.
- It remains the future execution workspace direction.
- Existing unavailable actions must remain disabled or otherwise clearly non-operational unless already implemented before this task.
- This task must not make `Image`, `Record`, `Edit step`, `Import data`, `Generate record`, or `Save` perform new behavior.

### Authority History

- `Authority Change History` should not be displayed in the main Workbench projection area.
- Existing history backend/API and component-level behavior may remain for future secondary placement.

### Test Record Draft Generation

- `Generate Test Record Draft` should not be displayed as a main Matrix projection action.
- Existing backend/API and component-level behavior may remain for future right-side `Record` flow.

## Acceptance Criteria

- Workbench keeps the existing right-side `Step Workspace`.
- Workbench no longer displays the new read-only `Record Step Workspace`.
- Workbench left Matrix area has a single clear `Matrix execution projection` title and no duplicate nested projection heading.
- Workbench main Matrix area does not display `Authority Change History`.
- Workbench main Matrix area does not display `Generate Test Record Draft`.
- Matrix projection table remains visible and read-only.
- Existing Step Workspace future action buttons remain non-operational unless previously implemented.
- No backend/API/domain/storage changes are introduced.
- No StepInstance, execution persistence, evidence upload, report, fee, AI, equipment, permission, or approval scope is introduced.
- Relevant frontend tests, static guards, and build pass.

## Validation Plan

Required commands after implementation:

```powershell
cd frontend
npm test -- --run ProjectWorkbenchMatrixProjectionPanel
npm test -- --run AuthorityChangeHistoryPanel
npm test -- --run TestRecordDraftGenerationButton
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task274 or task273 or project_workbench"
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
git diff --check
```

Manual browser smoke validation:

```text
Open Workbench -> confirm old right-side Step Workspace remains visible
Open Workbench -> confirm read-only Record Step Workspace is gone
Open Workbench -> confirm Authority Change History is not visible in main projection
Open Workbench -> confirm Generate Test Record Draft is not visible in main projection
Open Workbench -> confirm Matrix projection table remains visible and selectable
```

## Risks

- Hiding `Generate Test Record Draft` may leave TASK_271 backend capability without a visible UI entry until a future Record flow task places it correctly.
- Hiding `Authority Change History` may require future secondary placement for audit users.
- Removing the read-only `Record Step Workspace` can break tests that were written around TASK_270. Tests should be updated to reflect the new product direction instead of preserving obsolete UI.
- Existing right-side Step Workspace still contains future execution affordances. This task should clarify their non-operational status but not implement them.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task because it is a scoped frontend refocus with clear UI acceptance criteria, existing React components, existing tests, and no backend or schema changes. The task requires careful codebase reading and conservative removal/hiding of UI elements rather than broad architectural redesign.
