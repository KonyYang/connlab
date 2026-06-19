# TASK_323 Project Folder Conflict Dialog Style Hotfix Plan

> Status: Approved and implemented after user refined the scope.
> Date: 2026-06-19
> Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
> Active task candidate: TASK_323_PROJECT_FOLDER_CONFLICT_DIALOG_STYLE_HOTFIX

## 1. Why this task is allowed now

The current task board marks TASK_322 complete and does not authorize a later business feature. The user directly reported that the Project Workbench `Updated project folder` conflict dialog is visually inconsistent with the rest of ConnLab.

This is a narrow UI-only hotfix because it changes presentation of an existing approved Project Folder conflict choice dialog. It does not change backend folder conflict strategy, official workspace creation, request-material collection, Matrix/Fee authority, StepInstance, reports, AI, permissions, LAN, or multi-user scope.

## 2. Observed issue

User screenshot and source inspection show:

- `ProjectFolderConflictDialog` is rendered from `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`.
- The modal container uses `runtime-console-conflict-dialog`, but the action buttons only have a danger style for overwrite.
- Normal buttons fall back to browser default button chrome, making the dialog look disconnected from ConnLab's product UI.
- The path list is visually heavy and the action hierarchy is unclear.

## 3. Scope

In scope:

- Restyle the existing Project Folder conflict dialog to match ConnLab's restrained product UI.
- Keep the user's optimized dialog content unchanged.
- Keep the current three operator choices:
  - `Backup and Rebuild`
  - `Overwrite`
  - `Cancel`
- Keep the existing role/label contract: `role="dialog"` and accessible name `Project folder already exists`.
- Keep the existing callbacks and conflict strategy values unchanged.
- Add/update focused frontend tests or static guards for the styled dialog contract.

Out of scope:

- No backend changes.
- No new conflict strategy.
- No folder creation semantics change.
- No broad Project Workbench layout redesign.
- No replacement of this dialog with a native `window.confirm`.

## 4. Recommended UX direction

Make it feel like a ConnLab operational decision panel:

- Modal width around `520px`, surface color and border aligned with existing workbench cards.
- Path area:
  - quieter bordered block with label such as `Existing folder`
  - monospaced or compact path text with wrapping and no oversized bullet.
- Actions:
  - Keep the existing order and button titles.
  - `Backup and Rebuild` uses ConnLab's normal workbench action styling.
  - `Overwrite` uses muted danger styling, not a giant solid red button.
  - `Cancel` uses the same normal workbench button vocabulary.
- Button sizes should match Workbench action controls: compact height, 7-10px radius, no browser-default bevel.

## 5. File-level design

Expected implementation files:

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - Keep component, callbacks, and optimized content unchanged.
  - Preserve accessible dialog role/name.

- `frontend/src/workbench.css`
  - Add base styles for `.runtime-console-conflict-actions button`.
  - Add primary/recommended and danger variants.
  - Refine `.runtime-console-conflict-dialog`, path list, footer alignment, and responsive behavior.

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
  - Existing tests already assert dialog role and button behavior.
  - Add class/contract assertion only if needed, without overfitting visual CSS.

- `tests/unit/test_frontend_shell_files.py`
  - Add a narrow static guard for conflict-dialog button styling so normal buttons do not regress to browser defaults.

## 6. Validation plan

Automated:

```text
cd frontend; npm test -- --run ProjectWorkbenchLayout --watch=false
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task323 or project_folder"
cd frontend; npm run build
```

Manual browser smoke:

1. Open `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f`.
2. Click `Updated project folder`.
3. Confirm the conflict dialog uses ConnLab workbench styling rather than native browser buttons.
4. Confirm `Cancel` closes the dialog.
5. Confirm the two conflict actions still call the existing strategies.

## 7. Risks

- `frontend/src/workbench.css` and `ProjectWorkbenchLayout.tsx` are already dirty in the working tree from previous work, so implementation must preserve existing uncommitted changes.
- Styling-only tests can become brittle if they assert too many CSS details; keep guards focused on the missing base button style and accessible dialog contract.
- Because this dialog includes a destructive overwrite option, visual hierarchy must reduce ugliness without hiding risk.

## 8. Review checklist before coding

- Current phase stated: Phase 11 controlled foundation.
- Current active task ID stated: TASK_323_PROJECT_FOLDER_CONFLICT_DIALOG_STYLE_HOTFIX candidate.
- Allowed reason stated: user-requested Project Workbench UI-only hotfix.
- Implementation is blocked until user approval.
- No implementation code changed in this planning step.
