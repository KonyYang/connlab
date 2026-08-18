# TASK_349B Specified LTR Workbook Authority Modal Polish Plan

> Status: complete/accepted - Integrator packaging/readiness accepted
> Date: 2026-07-04
> Task: `TASK_349B_SPECIFIED_LTR_WORKBOOK_AUTHORITY_MODAL_POLISH`
> Lane: `specified-ltr-workbook-authority-modal-polish`

---

## 1. Discovery Gate

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task/lane: TASK_349A is complete/accepted. This Planner pass creates the next planned follow-up lane only.

Current role: Planner.

Why allowed: The user and Orchestrator requested a Planner lightweight follow-up lane after TASK_349A acceptance. The request is a new post-acceptance UI polish finding, so it must not be implemented by directly modifying the closed TASK_349A package.

## 2. User Goal

The specified-LTR workbook authority preview in Intake should be a true confirmation modal/dialog instead of an embedded large panel in the page body. The modal should make the confirmation moment clear, prevent background Intake actions while open, and keep all accepted TASK_349A business rules intact.

## 3. Confirmed By User

- The current `specified-ltr-preview-panel` is inline and visually crowds/mixes with the Intake page.
- The user confirmed a pop-up/modal format is more appropriate for the confirmation.
- The change should not alter TASK_349A workbook authority semantics.

## 4. Confirmed By Repository Evidence

- `docs/task_board.md` records TASK_349A as complete/accepted after Developer package-isolation fix, Reviewer re-gate, QA re-gate, and Integrator packaging/readiness validation.
- `frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx` renders the TASK_349A preview contents as an inline `<section className="specified-ltr-preview-panel">`.
- `frontend/src/pages/IntakeInboxPage.tsx` mounts that panel below the main Intake layout when `specifiedLtrWorkbookPreview` exists.
- `frontend/src/intake-inbox.css` styles `.specified-ltr-preview-panel` as an inline bordered panel.
- `frontend/src/pages/IntakeInboxPage.test.tsx` already contains TASK_349A coverage for found preview, not-found message, preview confirmation, and local duplicate handoff.
- TASK_349A evidence locks backend/API/workbook authority semantics and external residuals.

## 5. Planner Assumptions

- Existing preview content and handlers can be reused; the primary change is presentation, focus/background locking, and tests.
- `frontend/src/api/client.ts` does not need to change because TASK_349B does not alter DTOs or server contracts.
- The modal should use explicit buttons for confirmation and dismissal; backdrop click should not confirm or bypass the preview.

## 6. Not Yet Confirmed

None blocking for a planned lane. Developer may discover a small focus-management helper need, but it must remain inside the allowed frontend UI files or return to Planner/Reviewer if it requires broader scope.

## 7. Formal Lane Decision

Create one lightweight formal follow-up lane:

```text
TASK_349B_SPECIFIED_LTR_WORKBOOK_AUTHORITY_MODAL_POLISH
lane: specified-ltr-workbook-authority-modal-polish
status: planned
```

This should not be a quick fix because TASK_349A is accepted and the change affects a user-visible authority confirmation layer. A separate lane preserves package isolation and reviewability.

## 8. UX Contract

Found preview:

- Show a modal/dialog titled `Confirm LTR workbook row`.
- Keep the `LTR workbook authority` context label or equivalent compact label.
- Show DL number, workbook path, sheet/row, and the required business fields table in the accepted TASK_349A order.
- Primary action remains `Use this LTR number`.
- Secondary action remains `Cancel`.
- Confirm continues the existing TASK_349A Apply LTR flow.

Not found:

- Show the message `LTR workbook 中不存在该编号`.
- Do not show `Use this LTR number`.
- Only allow closing back to Intake.
- Do not create or confirm a local Project.

Modal behavior:

- Background Intake page is visibly subdued and interaction-locked while the modal is open.
- Import, sidebar navigation, Apply LTR, Create Temporary, and editable form controls must not be operable behind the modal.
- Focus moves into the modal when it opens and returns to the triggering or safe Intake control when it closes.
- The dialog must be labelled and use `aria-modal` or an equivalent accessible modal pattern.
- Escape/backdrop behavior may close only if it is equivalent to explicit Cancel/Close and cannot bypass confirmation.

Visual style:

- Dense, restrained, operational ConnLab UI.
- No long explanation, decorative modal, gradient text, glass effect, hero treatment, or status/readiness panel styling.

## 9. May Touch

- `frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/intake-inbox.css`
- `frontend/src/pages/IntakeInboxPage.test.tsx`
- Optional focused component test under `frontend/src/features/new-project/` if needed
- `tasks/TASK_349B_SPECIFIED_LTR_WORKBOOK_AUTHORITY_MODAL_POLISH.md`
- `docs/task_349b_specified_ltr_workbook_authority_modal_polish_plan.md`
- `docs/lane_evidence/TASK_349B_specified-ltr-workbook-authority-modal-polish_*.md`
- `docs/task_board.md` through normal lane flow

## 10. Must Not Touch / Locked Paths

- `backend/**`
- `frontend/src/api/client.ts`
- Database schema/migration files
- Public LTR workbook read/write services and authority semantics
- Workbench LTR update preview semantics
- Matrix/Fee/Folder Actions/Projects registry/list
- Basic Information, Settings/LTR, release/packaging, desktop residuals
- Real workbook/public-drive/folder data
- `.agents/**`
- `docs/project_management/**`
- StepInstance, Report, AI, permissions, LAN/server, multi-user scope

## 11. Validation Plan

Future Developer/QA validation should include:

- Focused frontend tests verifying the preview renders as a modal/dialog rather than an inline panel.
- Background lock tests for Import, sidebar/app navigation hooks if available, Apply LTR, Create Temporary, and editable Intake controls while the modal is open.
- Found preview test: table content remains visible and `Use this LTR number` continues the existing completion path.
- Not-found test: `LTR workbook 中不存在该编号` appears and only Close returns to Intake.
- Cancel/Close test: preview closes without local Project creation, workbook write, or local duplicate override.
- Accessibility test assertions where practical: labelled dialog, modal semantics, focus entry/return.
- `npm test -- IntakeInboxPage --run` or equivalent focused command.
- `npm run build`.
- Forbidden-scope/status checks proving no backend/API client/workbook authority or unrelated residual files changed.

## 12. Reviewer Plan Gate

Reviewer should check:

- The lane is a UI presentation/focus/background-lock polish only.
- TASK_349A authority semantics and local duplicate ordering remain unchanged.
- `frontend/src/api/client.ts` and `backend/**` remain locked.
- Acceptance criteria are testable without touching real workbook/public-drive data.
- The plan does not silently package existing external residuals.

## 13. Merge Gate

Implementation is authorized after Reviewer plan gate pass, user approval for Developer planning-first, Developer planning-first completion, Reviewer implementation-readiness pass, explicit user approval for reconciliation and implementation, and Planner source-of-truth reconciliation.

TASK_349B frontend UI polish implementation is complete/accepted after Reviewer, QA, and Integrator gates.

## 14. Recommended Next Role

Developer implementation pass.

---

## 15. Developer Planning-First Refinement

Status: developer planning-first complete - pending implementation-readiness/source-of-truth reconciliation.

Delegation context:

- Orchestrator reported Reviewer plan gate passed.
- User approved TASK_349B Developer planning-first.
- Local `docs/task_board.md`, task file, plan header, and Planner evidence still record TASK_349B as planned/ready for Reviewer plan gate. This appears to be a source-of-truth timing mismatch and must be reconciled before implementation starts.

### 15.1 Current Implementation Shape

Current TASK_349A UI:

- `SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx` renders the accepted preview content as an inline `<section className="specified-ltr-preview-panel">`.
- The component already uses `role="dialog"` for found previews and `role="alertdialog"` for not-found/blocked previews, but it does not set `aria-modal`, move focus, trap focus, return focus, or render an overlay.
- `IntakeInboxPage.tsx` mounts the panel after the main Intake layout when `specifiedLtrWorkbookPreview` exists.
- `intake-inbox.css` styles `.specified-ltr-preview-panel` as an inline bordered page-flow panel.
- `IntakeInboxPage.test.tsx` already covers found preview, not-found, confirm, close, and local duplicate handoff; those tests should be extended to modal behavior rather than replaced.

### 15.2 Future Implementation File List

Future implementation May Touch should be limited to:

- `frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/intake-inbox.css`
- `frontend/src/pages/IntakeInboxPage.test.tsx`
- Optional new focused test: `frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.test.tsx`
- `docs/lane_evidence/TASK_349B_specified-ltr-workbook-authority-modal-polish_developer.md`
- TASK_349B plan/evidence docs through normal lane flow

Do not touch:

- `backend/**`
- `frontend/src/api/client.ts`
- TASK_349A backend/API/client contract
- local duplicate resolution behavior
- Workbench LTR update preview behavior
- Projects registry, Matrix, Fee, Folder Actions, Basic Information, Settings/LTR, release/packaging, `.agents/**`, or `docs/project_management/**`

### 15.3 Modal/Dialog UX Plan

Structure:

- Wrap the preview with a fixed modal layer, for example `.specified-ltr-preview-modal`.
- Add a backdrop element that visually masks Intake background with restrained tint, not blur/glassmorphism.
- Render the existing preview panel as the dialog surface inside the overlay.
- Keep the table and action copy from TASK_349A.
- Size the modal for operational reading:
  - desktop: max width around 760-860px, max height within viewport, internal scroll only for long row tables
  - small viewport: inset margins and full-width within safe bounds

Semantics:

- Found preview remains `role="dialog"`.
- Not-found/blocked remains `role="alertdialog"`.
- Add `aria-modal="true"`.
- Keep `aria-labelledby="specified-ltr-preview-title"`.
- If message text is present, add `aria-describedby` pointing to a short message or metadata region.

Focus and keyboard:

- On open, move focus to the primary action for found previews, or to `Close` for not-found/blocked previews.
- Tab and Shift+Tab should remain within the modal while open.
- Escape may call Cancel/Close only; it must never confirm, bypass preview acknowledgement, or call completion.
- On close, return focus to a safe Intake control if available, preferably the Apply LTR Number button or the previously focused element if still connected.
- Backdrop click should either do nothing or perform the same safe Cancel/Close behavior. It must not confirm.

Background lock:

- The existing `specifiedLtrPreviewActive` page lock should remain active.
- Modal overlay should prevent pointer interaction with the Intake page behind it.
- Tests should assert import/apply/editor controls are unavailable or not actionable while the dialog is open.

Actions:

- Found:
  - Primary: `Use this LTR number`
  - Secondary: `Cancel`
  - Confirm continues the existing TASK_349A completion path with preview ack.
- Not found:
  - Message remains `LTR workbook 中不存在该编号`
  - Only close action is visible.
  - Close returns to Intake without local creation or workbook write.

### 15.4 Design Constraints

Register: product.

Apply `$impeccable` constraints:

- restrained, dense, operational confirmation layer
- no long explanatory copy
- no hero/modal marketing treatment
- no side-stripe accent border greater than 1px
- no gradient text
- no glassmorphism or decorative blur
- no nested cards inside the modal
- no raw backend/API/token/hash copy in user-facing UI
- buttons should remain consistent with existing ConnLab action styles

### 15.5 Business Semantics To Preserve

TASK_349B must not alter:

- preview API request/response shape
- `specified_ltr_workbook_preview_ack`
- found/not-found/blocked backend semantics
- local project creation timing
- local duplicate second-layer behavior
- preview confirm/cancel behavior beyond presentation and focus handling
- TASK_347A busy/interaction lock behavior
- TASK_348A/TASK_348B duplicate/cancel behavior
- Workbench LTR update preview

### 15.6 Focused Test Plan

Extend `frontend/src/pages/IntakeInboxPage.test.tsx` and optionally add a component test to cover:

- full specified DL Apply opens a modal dialog with `aria-modal="true"`
- modal is not an inline page-flow panel after the main Intake content
- found preview still renders workbook row values and `Use this LTR number`
- confirm calls existing completion with preview ack
- not-found renders `LTR workbook 中不存在该编号`, does not show confirm, and close returns to Intake
- Escape calls the safe Cancel/Close path only
- focus starts inside the modal and returns after close
- keyboard tab order remains inside the modal where practical with the test harness
- background Apply/import/editor actions are locked while modal is open
- local duplicate handoff after workbook confirmation still works

Implementation validation:

- `npm test -- IntakeInboxPage --run`
- optional `npm test -- SpecifiedLtrWorkbookAuthorityPreviewPanel --run` if a component test is added
- `npm run build`
- `git diff --check` on TASK_349B package files
- trailing whitespace scan on TASK_349B package files
- static scan for side-stripe borders over 1px, gradient text, backdrop-filter/glass copy, backend/API client changes, and real workbook/public-drive mutation strings
- targeted status check proving no backend/API client/Workbench/Matrix/Projects/release/governance files changed by implementation

Browser smoke:

- If tooling is available, smoke `http://localhost:5173/intake` with mocked/safe state or a QA-provided fixture.
- Verify the preview appears as modal overlay, background is masked/locked, not-found is close-only, and found confirm proceeds to the existing flow.
- If safe browser data is unavailable, document the exact QA residual rather than using a real workbook mutation path.

---

## 16. Source-Of-Truth Reconciliation

Date: 2026-07-04

Planner reconciliation records:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed.
- Reviewer implementation-readiness passed by callback.
- User approved TASK_349B reconciliation and Developer implementation.

TASK_349B is complete/accepted by Integrator after Reviewer implementation gate pass, QA gate pass, and controlled packaging/readiness validation.

Scope locks remain unchanged:

- Frontend UI polish only: inline specified-LTR workbook authority preview to modal/dialog.
- No backend/API/client contract/workbook authority changes.
- No preview acknowledgement contract change.
- No local duplicate behavior change.
- No Workbench, Matrix, Fee, Folder Actions, Projects, Basic Information, Settings/LTR, release/packaging, real workbook/public-drive data, `.agents/**`, or `docs/project_management/**` scope.
