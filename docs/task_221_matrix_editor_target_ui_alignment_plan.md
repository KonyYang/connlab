# TASK_221 Plan - Matrix Editor Target UI Alignment And Workflow Convergence

## 1. Task Understanding

Goal:

Align the current Matrix Editor placeholder page to `Matrix Edit Page.png` so it reads as a Definition Studio workflow instead of a runtime/status dashboard.

Input data:

- Existing `ProjectMatrixEditorPage` runtime-boundary model data.
- Existing placeholder matrix constants.
- Static placeholder library/template/reference data introduced only in the frontend.

Output data:

- A frontend-only Matrix Editor layout aligned to the target page.
- Static tests that guard the target structure.
- Updated task and board records after implementation.

Modules involved:

- Matrix Editor page component.
- Shared Workbench stylesheet.
- Frontend static shell tests.
- Task board and task file after completion.

Not allowed:

- Backend, API, domain, database, or persistence changes.
- Real inline editing, drag/drop, template import, authority publish behavior, or step persistence.
- Runtime dashboard expansion inside Matrix Editor.

## 2. Target UI Interpretation

The target page has four primary zones:

1. Header and operation toolbar:
   Project identity, matrix metrics, save/publish actions, dense authoring commands, display/filter/search controls.
2. Main authoring workspace:
   Left `Test Item Library`, center `Matrix Grid`, right `Group / Step Workspace`.
3. Supporting bottom workspace:
   Bottom left `Templates`, bottom right `Reference Library`.
4. Secondary runtime/projection context:
   Small metadata only, never a dominant status-card stack.

The visual priority order must be:

```text
Matrix Grid > right Group / Step Workspace > left Test Library > bottom Templates / Reference Library > runtime metadata
```

## 3. Current vs Target Delta

| Area | Current State | Target State | Implementation Direction |
| --- | --- | --- | --- |
| Header | Generic title, summary cards below title | Back link, strong project identity, matrix metrics, save/publish actions | Collapse identity and metrics into target-like header band |
| Operation toolbar | Sparse generic controls | Dense authoring toolbar with add/import/export/search/filter controls | Add static/disabled target-equivalent controls |
| Left Test Library | Missing | Searchable auxiliary test item library | Add left panel with static library sections |
| Matrix Grid | Present but not dominant enough | Center of Definition Studio | Increase central weight and table density |
| Right panel | Runtime/status card stack | Contextual group/step workspace | Replace card stack with group/step table, tabs, notes, apply action |
| Runtime projection | Too visible in primary workflow | Secondary metadata only | Keep projection ref in header or small note |
| Bottom Templates | Missing | Supporting template cards | Add static template panel |
| Bottom Reference Library | Missing | Supporting tabular reference library | Add static reference panel |

## 4. File-Level Change Plan

### 4.1 `frontend/src/pages/ProjectMatrixEditorPage.tsx`

Planned changes:

- Restructure the page into target-aligned sections:
  - `matrix-editor-target-header`
  - `matrix-editor-actionbar`
  - `matrix-editor-studio`
  - `matrix-editor-test-library`
  - `matrix-editor-grid-surface`
  - `matrix-editor-step-workspace`
  - `matrix-editor-supporting`
  - `matrix-editor-templates`
  - `matrix-editor-reference-library`
- Expand static placeholder rows to closer target density.
- Replace right-side runtime/status cards with contextual group/step workspace.
- Add static Test Library, Templates, and Reference Library content.
- Keep `onBackToWorkbench` as the only active navigation behavior.
- Keep save/publish/import/action buttons disabled or placeholder-safe unless existing behavior already supports them.

No changes:

- No new fetch calls.
- No API client changes.
- No backend-driven edit behavior.

### 4.2 `frontend/src/workbench.css`

Planned changes:

- Add Matrix Editor target layout styles:
  - header band
  - dense action bar
  - three-column studio grid
  - compact test library
  - dominant matrix grid
  - contextual step workspace
  - bottom templates/reference grid
- Reduce dashboard-card feel in Matrix Editor right panel.
- Keep styles scoped to `matrix-editor-*` selectors.
- Preserve existing Workbench Runtime Console styles.

### 4.3 `tests/unit/test_frontend_shell_files.py`

Planned changes:

- Add `TASK_221` static assertions:
  - target sections exist
  - Matrix Grid remains central
  - Test Library, Templates, Reference Library exist
  - right panel uses Group / Step Workspace wording
  - dashboard-like runtime card stack labels are absent from Matrix Editor primary component
- Keep tests static and bounded to frontend shell structure.

### 4.4 `tasks/TASK_221_*.md`

After implementation:

- Mark status complete.
- Add validation summary.

### 4.5 `docs/task_board.md`

After implementation:

- Add `TASK_221 complete` to board status line.
- Set current active task to none, pending user approval for next controlled task.
- Add deliverables and validation summary.

## 5. Static Placeholder Data Strategy

Use local constants inside `ProjectMatrixEditorPage.tsx`:

- `TEST_LIBRARY_SECTIONS`
- `MATRIX_EDITOR_ROWS`
- `STEP_WORKSPACE_ROWS`
- `TEMPLATE_CARDS`
- `REFERENCE_LIBRARY_ROWS`
- `ACTION_BAR_ITEMS`

Reason:

- The task is visual/workflow alignment only.
- Backend data models for library/reference/template behavior are not approved.
- Static data lets the page match target structure without creating false persistence semantics.

## 6. Component Reuse Strategy

- Keep implementation in `ProjectMatrixEditorPage.tsx` unless JSX becomes too large to read.
- Prefer small local render helper functions over new files.
- Do not introduce a new feature folder or design system.
- Reuse existing CSS variables and button/table vocabulary from `workbench.css`.

## 7. API And Function Signatures

No API signature changes.

No backend function signature changes.

Potential local helper signatures:

```tsx
function MatrixEditorActionBar(): ReactElement
function MatrixEditorTestLibrary(): ReactElement
function MatrixEditorStepWorkspace(): ReactElement
function MatrixEditorTemplates(): ReactElement
function MatrixEditorReferenceLibrary(): ReactElement
```

These helpers remain local to the page file unless implementation size requires extraction.

## 8. Dependencies

Existing dependencies only:

- React
- existing project frontend types/hooks
- existing CSS variables

No new package dependency.

## 9. Risk And Controls

Risk: The page becomes a newly invented design.

Control: Follow target section order and target page role names.

Risk: Static placeholder controls imply implemented business behavior.

Control: Disabled buttons and placeholder-safe labels where behavior is not implemented.

Risk: Runtime/status cards continue to dominate.

Control: Remove `Authority Status`, `Step Identity Preview`, and `Runtime Mapping Notes` from the right primary card stack and replace with contextual workspace.

Risk: Large JSX becomes hard to maintain.

Control: Use local helper render functions with typed constants.

## 10. Validation Plan

Required build:

```powershell
cd frontend
npm run build
```

Required targeted frontend shell tests:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task221 or task220 or task219"
```

Recommended governance tests after board update:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

## 11. Manual Smoke Checklist

1. Open Project Workbench.
2. Navigate to Matrix Editor.
3. Confirm header follows target identity and metrics structure.
4. Confirm top toolbar is dense and authoring-oriented.
5. Confirm left Test Library is visible.
6. Confirm central Matrix Grid has dominant width and height.
7. Confirm right Group / Step Workspace is contextual and not a runtime dashboard.
8. Confirm bottom Templates and Reference Library are visible.
9. Confirm Workbench back navigation works.
10. Confirm disabled placeholder controls do not imply completed editing behavior.

## 12. Done Criteria

Implementation is complete only when:

- Target page structure is present.
- Matrix Grid is visually dominant.
- Left, right, and bottom supporting surfaces match target roles.
- Runtime/projection context is secondary.
- No backend/API/domain changes exist.
- Build and targeted tests pass.
- Board and task file are updated.

## 13. Stop Point

This is the required implementation plan for `TASK_221`.

Per task protocol, implementation code changes must wait for explicit user approval.
