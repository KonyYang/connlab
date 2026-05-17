# TASK_215_DEFAULT_COLLAPSED_ICON_SIDEBAR

## Status

Approved and executed on 2026-05-16.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Why This Task Is Allowed Now

TASK_214 completed the Project Workbench visual clone density pass. The user then explicitly requested a narrower default application sidebar so the Workbench can reserve more horizontal space for runtime content. This is a bounded UI shell adjustment and does not change backend, runtime projection, API, database, Matrix authority, Step identity, or Workbench business behavior.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task because it is a small React/CSS shell change with clear acceptance criteria, focused validation through the frontend build, and no need for broad architectural inference.

## Objective

Make the application sidebar default to a collapsed icon-only state while preserving discoverability through hover tooltips and an explicit expand/collapse control.

## Scope

Allowed:

- Default the app shell sidebar to collapsed when no stored user preference exists.
- Preserve existing local storage preference after a user manually expands or collapses the sidebar.
- Render icon-only navigation in the collapsed sidebar.
- Add native hover tooltip labels to collapsed navigation icons and the sidebar toggle.
- Tighten collapsed sidebar dimensions to increase Workbench horizontal room.
- Update `docs/task_board.md` and static board-state guards.

Forbidden:

- Backend, API, DB, ORM, runtime projection, or Matrix authority changes.
- Workbench Runtime Console behavior changes.
- Route changes.
- New frontend dependencies.
- Business logic changes.
- Matrix Editor or StepInstance implementation.

## Implementation Notes

- `AppShell` uses a lazy local-storage initializer so the first render is collapsed by default, except when the operator has explicitly stored an expanded preference.
- `Sidebar` exposes native `title` labels on navigation buttons, matching the user request for tooltip information when hovering over icon-only navigation.
- Collapsed sidebar styling hides the brand mark and text, keeps a compact top toggle, and uses 40px icon buttons inside a 64px rail.

## Acceptance Criteria

- First-time app load shows the left sidebar collapsed by default.
- If the operator expands the sidebar, the expanded preference persists.
- Collapsed sidebar displays only icons, not text labels.
- Hovering a collapsed navigation icon shows its label through the browser tooltip.
- Hovering the collapsed sidebar toggle shows an expand/open tooltip.
- Workbench content gains additional horizontal space compared with the previous 78px collapsed rail.
- `npm run build` passes from `frontend/`.

## Validation

To run:

```powershell
cd frontend
npm run build
```

Governance board guard validation:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```
