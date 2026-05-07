# TASK_142_EMAIL_PACKAGE_DUPLICATE_RESOLUTION_UI

## Status

plan_review

## Phase / Active Task Justification

- Current Phase: `Phase 10C - New Project intake flow friction cleanup`
- Current Active Task on board: `None - awaiting next approved task`
- Why this task is allowed to plan now: `TASK_141` is expected to provide backend duplicate classification and explicit resolution actions. The New Project UI then needs a calm, inline resolution surface that lets operators open an existing draft, replace it, or create a separate draft without modal-first interruption.

## Step 1 Plan Only

This document is the executable implementation plan for review.
No implementation code may be written until the user approves this plan.

## Purpose

Wire duplicate `.msg` import resolution into the New Project page.

The UI should distinguish exact duplicate imports from same-name different-content imports. It should make differences visible enough for a lab coordinator to choose correctly, while keeping the flow concise and workbench-like.

## Prerequisite

`TASK_141_EMAIL_PACKAGE_DUPLICATE_DETECTION_BACKEND` must be complete before this task starts.

This task depends on backend/API responses that expose:

- duplicate classification
- incoming package summary
- existing draft summary
- source file differences
- attachment manifest differences
- allowed resolution actions

## Task Understanding

Confirmed UX rules:

- Re-importing an identical message should primarily offer opening the existing draft.
- Replacing an existing draft is allowed only when backend says the existing package is unconfirmed.
- Same-name but different-content imports should show the concrete differences before asking whether to replace or create a separate draft.
- Prefer inline/progressive UI over modal-first flow.
- Do not show raw backend ids or technical route names.

## Scope

Frontend:

1. Update the New Project import flow to handle backend duplicate classification.
2. For `exact_existing_draft`, show an inline resolution panel with:
   - existing source name
   - existing draft status
   - source size summary
   - attachment count
   - primary action: open existing draft
   - secondary action: replace existing draft
3. For `same_name_different_content`, show an inline difference summary with:
   - source size/hash changed indicator
   - attachment count difference
   - attachment names added/removed/changed when provided
   - actions: create separate draft, replace existing draft
4. On selected action, call backend resolution APIs from `frontend/src/api/client.ts`.
5. Navigate or update session state according to backend response.
6. Keep copy operational and business-readable.

Backend:

1. No new duplicate detection rules in this task.
2. Only adjust API DTOs if the implemented backend response needs frontend type alignment.

Documentation:

1. Update `docs/task_board.md` after implementation.
2. Mark this task `done` after validation.

## Out Of Scope

- No duplicate detection backend design; belongs to `TASK_141`.
- No Outlook inbox auto-scan.
- No email sending.
- No merge package workflow.
- No duplicate UI for direct Word import unless backend already supports it and the implementation is trivial.
- No Matrix, Report, AI review, permissions, or LAN deployment.

## UI Behavior

Exact duplicate:

```text
This email is already in Drafts / In Progress.

Actions:
- Open existing draft
- Replace existing draft
```

Same name, different content:

```text
A draft with this email filename already exists, but the file contents differ.

Show:
- existing size vs incoming size
- existing attachment count vs incoming attachment count
- added / removed / changed attachment names

Actions:
- Create separate draft
- Replace existing draft
```

Keep the resolution surface within the New Project import area. Do not use a modal unless implementation discovery shows the current page structure cannot support a stable inline panel.

## Proposed File-Level Changes

Likely frontend files:

1. `frontend/src/api/client.ts`
   - Add duplicate classification response DTOs and resolution request function if not already added in `TASK_141`.
2. `frontend/src/pages/IntakeInboxPage.tsx`
   - Handle duplicate import responses.
   - Store pending duplicate resolution state.
   - Render inline resolution panel.
   - Apply chosen resolution to current New Project session.
3. `frontend/src/intake-inbox.css`
   - Add restrained workbench styling for duplicate resolution panel and difference rows.
4. `tests/unit/test_frontend_shell_files.py`
   - Static checks for duplicate resolution copy/actions and no modal-first pattern.

Possible feature extraction if the page is already too large:

1. `frontend/src/features/intake/EmailDuplicateResolutionPanel.tsx`
2. `frontend/src/features/intake/intakeDuplicateSelectors.ts`

Use extraction only if it keeps the page from growing further.

## Acceptance Criteria

- Exact duplicate `.msg` import shows an inline existing-draft resolution panel.
- Same-name different-content `.msg` import shows concrete source/attachment differences.
- Operator can open existing draft.
- Operator can replace existing draft when backend allows it.
- Operator can create a separate draft for same-name different-content imports.
- UI does not expose raw IDs, API route names, stack traces, or future-scope features.
- UI uses backend duplicate classification as authoritative and does not reimplement comparison logic in React.

## Validation Plan

Required:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
npm run build
```

Recommended:

```powershell
py -m pytest tests\integration\test_msg_package_intake_api.py -q
```

Manual smoke after implementation:

```text
1. Import a new .msg package.
2. Re-import the exact same .msg and open the existing draft.
3. Re-import the exact same .msg and replace the existing draft.
4. Import a same-name .msg with changed attachment content and create a separate draft.
5. Import a same-name .msg with changed attachment content and replace the old unconfirmed draft.
```

Final:

```powershell
git diff --check
```

## Risks And Mitigations

Risk: duplicate resolution UI becomes another confirmation-heavy interruption.

- Mitigation: use inline action panel with concrete differences and direct actions.

Risk: frontend duplicates backend comparison logic.

- Mitigation: UI only renders backend classification and differences.

Risk: page file grows further.

- Mitigation: extract a named feature component if the JSX block is non-trivial.

## Approval Gate

After user explicitly approves this task, Step 2 implementation may start.
