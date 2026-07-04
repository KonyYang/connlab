# TASK_349B Specified LTR Workbook Authority Modal Polish - Planner Evidence

Date: 2026-07-04

Role: Planner

Task: `TASK_349B_SPECIFIED_LTR_WORKBOOK_AUTHORITY_MODAL_POLISH`

Lane: `specified-ltr-workbook-authority-modal-polish`

Status: ready_for_reviewer_plan_gate

---

## Scope

Create a planned lightweight frontend UI polish lane after accepted TASK_349A. The lane converts the specified-LTR workbook authority preview from an inline Intake page panel into a true modal/dialog. No product code was changed in this Planner pass.

## Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/impeccable/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW.md`
- `docs/task_349a_specified_ltr_workbook_authority_preview_plan.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_developer.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_qa.md`
- `frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/intake-inbox.css`
- `frontend/src/pages/IntakeInboxPage.test.tsx`
- Current `git status --short`

## Discovery Findings

Confirmed by user:

- The current preview is better as a pop-up window/modal.
- The current inline panel crowds the Intake page and visually mixes with the bottom Apply area.

Confirmed by repository evidence:

- TASK_349A is complete/accepted in `docs/task_board.md`.
- `SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx` contains the accepted preview content and actions.
- The component currently returns an inline `<section className="specified-ltr-preview-panel">`.
- `IntakeInboxPage.tsx` mounts the panel after the main Intake layout.
- `intake-inbox.css` styles the preview as an inline panel.
- Existing TASK_349A tests cover found/not-found/confirm/local-duplicate handoff paths and can be extended.

Planner inference:

- This should be one lightweight frontend-only follow-up lane.
- The current API/client DTOs should remain unchanged.
- Modal/focus/background-lock behavior is testable at the Intake page level.

Not yet confirmed:

- No blocking unknowns. Developer must stop and route back if implementation requires backend/API client changes or broader navigation shell changes.

## Lane Created

- Task file: `tasks/TASK_349B_SPECIFIED_LTR_WORKBOOK_AUTHORITY_MODAL_POLISH.md`
- Plan file: `docs/task_349b_specified_ltr_workbook_authority_modal_polish_plan.md`
- Evidence file: `docs/lane_evidence/TASK_349B_specified-ltr-workbook-authority-modal-polish_planner.md`
- Board update: `docs/task_board.md`

## May Touch

- `frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/intake-inbox.css`
- `frontend/src/pages/IntakeInboxPage.test.tsx`
- Optional focused component test under `frontend/src/features/new-project/`
- TASK_349B task/plan/evidence/board docs

## Must Not Touch / Locked Paths

- `backend/**`
- `frontend/src/api/client.ts`
- Database schema/migrations
- Public LTR workbook read/write services and authority semantics
- Workbench LTR update preview semantics
- Matrix/Fee/Folder Actions/Projects registry/list
- Basic Information, Settings/LTR, release/packaging, desktop residuals
- Real workbook/public-drive/folder data
- `.agents/**`
- `docs/project_management/**`
- StepInstance, Report, AI, permissions, LAN/server, multi-user scope

## Validation Gate

Reviewer plan gate should verify:

- TASK_349B is modal-only frontend UI polish and does not reopen TASK_349A backend/API/workbook authority semantics.
- The May Touch and Locked Paths are strict enough to avoid package contamination.
- UI acceptance covers found/not-found, background lock, confirm/cancel/close, focus/accessibility, and no inline-panel regression.
- Validation can be performed with focused frontend tests and build without real workbook/public-drive mutation.

## Merge Gate

No implementation is authorized by this Planner pass. Reviewer plan gate and explicit user approval are required before Developer planning-first or implementation routing.

## Validation Performed By Planner

`git diff --check` on TASK_349B docs/board:

```powershell
git diff --check -- docs/task_board.md tasks/TASK_349B_SPECIFIED_LTR_WORKBOOK_AUTHORITY_MODAL_POLISH.md docs/task_349b_specified_ltr_workbook_authority_modal_polish_plan.md docs/lane_evidence/TASK_349B_specified-ltr-workbook-authority-modal-polish_planner.md
```

Observed result: passed with existing LF/CRLF warning for `docs/task_board.md` only.

Trailing whitespace scan:

```powershell
Select-String -Path 'docs/task_board.md','tasks/TASK_349B_SPECIFIED_LTR_WORKBOOK_AUTHORITY_MODAL_POLISH.md','docs/task_349b_specified_ltr_workbook_authority_modal_polish_plan.md','docs/lane_evidence/TASK_349B_specified-ltr-workbook-authority-modal-polish_planner.md' -Pattern '[ \t]$' -Encoding UTF8
```

Observed result: no matches.

Targeted status:

```powershell
git status --short -- docs/task_board.md tasks/TASK_349B_SPECIFIED_LTR_WORKBOOK_AUTHORITY_MODAL_POLISH.md docs/task_349b_specified_ltr_workbook_authority_modal_polish_plan.md docs/lane_evidence/TASK_349B_specified-ltr-workbook-authority-modal-polish_planner.md backend frontend tests
```

Observed result:

- TASK_349B Planner pass changed only `docs/task_board.md` plus the new TASK_349B task/plan/evidence files.
- Existing external product residuals remain visible under backend/frontend/tests, including Basic Information, Settings/LTR, intake/precheck/parser/New Project adjacent files, `frontend/src/api/client.ts`, release/packaging/desktop files, and related tests.
- Those residuals are explicitly excluded from TASK_349B and were not packaged, cleaned, reverted, or modified by this Planner pass.

## Next Role

Reviewer plan gate.

## Completion Callback

Ready to send to Orchestrator.
