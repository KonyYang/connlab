# TASK_076_FRONTEND_ARCHITECTURE_RULES_AND_UI_BOUNDARY

## Status

done

## Goal

Document frontend UI architecture rules so future ConnLab UI changes have the same kind of boundary control that backend and task execution already have.

## Why This Task Is Allowed Now

- Current board state has no active implementation task after `TASK_075`.
- The user explicitly approved creating UI architecture rules before moving to the next phase.
- This task is documentation-only and does not activate Phase 10B.
- The work supports existing MVP Intake, Precheck, LTR Number, and Folder UI maintainability.

## Scope

- Add a frontend architecture rules document.
- Define page, feature, component, API, state, selector, config, and styling boundaries.
- Document safe rules for adding fields, state, workflow decisions, and mock/reference content.
- Link the new rules from the general architecture rules document.
- Update the task board to record completion and the next stop point.

## Out Of Scope

- No frontend code refactor.
- No new route, component, hook, API, or CSS implementation.
- No copied-workbook LTR write hardening.
- No Outlook inbox auto-scan or email sending.
- No Matrix, Report, AI review, LAN deployment, permissions, or future-scope feature.

## Design Notes

- Treat `features/*` as the future business boundary for Intake, Precheck, LTR Number, and Folder UI.
- Keep `pages/*Page.tsx` as route-level composition instead of long-term business logic containers.
- Keep `api/*` as the only frontend fetch boundary.
- Prefer field/table config, selectors, and feature hooks over growing page JSX and ad hoc `useState`.
- Preserve `$impeccable` product UI guidance as a mandatory rule for UI work.

## Validation

- Static documentation review confirms the new document covers page, feature, state, API, component, styling, and review boundaries.
- `docs/02_ARCHITECTURE_RULES.md` links to the new frontend architecture rules.
- `docs/task_board.md` records this task as complete and keeps the next implementation task blocked pending user approval.

## Completion Notes

- Added `docs/frontend_architecture_rules.md`.
- Linked frontend rules from `docs/02_ARCHITECTURE_RULES.md`.
- Linked `docs/02_ARCHITECTURE_RULES.md` and `docs/frontend_architecture_rules.md` from `AGENTS.md` as mandatory frontend/UI read-before-work rules.
- Updated `docs/task_board.md` with `TASK_076` completion and current stop point.
- No frontend runtime code was changed.

## Validation Result

- Static documentation review completed.
- `py -m pytest tests\unit\test_frontend_architecture_rules.py -q`: `2 passed`

## Stop Condition

Stop after documentation and board sync. Do not proceed into frontend refactor or Phase 10B without explicit user approval.
