# TASK_349B Specified LTR Workbook Authority Modal Polish

> Status: complete/accepted - Integrator packaging/readiness accepted
> Created: 2026-07-04
> Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
> Lane: specified-ltr-workbook-authority-modal-polish

---

## 1. Goal

Convert the accepted TASK_349A specified-LTR workbook authority preview from an embedded Intake page panel into a true confirmation modal/dialog.

The modal must preserve TASK_349A authority semantics: the public-drive LTR workbook remains the first authority for full specified DL numbers, found workbook rows must be reviewed before completion continues, and not-found previews block local creation. This task is UI polish only.

## 2. Why This Follows TASK_349A

TASK_349A is complete/accepted and implements the workbook-first preview gate. User in-app feedback on `/intake` reported that the current embedded `specified-ltr-preview-panel` is a large inline panel that pushes into the Intake page and visually mixes with the bottom Apply area. The user confirmed the confirmation layer is better as a pop-up window.

This is not a continuation of TASK_349A implementation because TASK_349A is closed/accepted. It needs a formal lightweight follow-up lane with its own plan, review gate, validation, and package boundary.

## 3. Current Repository Facts

- `frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx` renders the preview content with `role="dialog"` or `role="alertdialog"`, but the element is still an inline `<section className="specified-ltr-preview-panel">`.
- `frontend/src/pages/IntakeInboxPage.tsx` mounts `SpecifiedLtrWorkbookAuthorityPreviewPanel` after the main Intake layout when `specifiedLtrWorkbookPreview` exists.
- `frontend/src/intake-inbox.css` styles `.specified-ltr-preview-panel` as an inline bordered panel with margin and padding.
- Existing tests in `frontend/src/pages/IntakeInboxPage.test.tsx` cover found preview, not-found message, preview confirmation, and local duplicate handoff.
- TASK_349A board/evidence says backend/API/workbook authority semantics are accepted and must not be changed by this polish lane.

## 4. Scope

May plan and later implement:

- Show the specified-LTR workbook authority preview as a modal/dialog overlay instead of an inline page panel.
- Mask or otherwise disable the Intake page background while the modal is open so the user cannot operate Import, sidebar navigation, Apply LTR, Create Temporary, or editable Intake controls underneath it.
- Preserve the existing preview content and action sequence: DL number, workbook path, sheet/row, required business fields table, found confirmation, not-found close, Cancel/Close, and `Use this LTR number`.
- Preserve TASK_347A busy/interaction lock and TASK_348A/TASK_348B local duplicate second-layer behavior.
- Add focused frontend tests for modal behavior, background lock, found/not-found paths, and no inline panel regression.

## 5. Non-Goals

- No backend/API/client contract changes.
- No workbook read/write/preview acknowledgement semantic changes.
- No local duplicate conflict semantics changes.
- No Workbench LTR update preview semantic changes.
- No Matrix, Fee Evaluation, Folder Actions, Project Workbench, Projects registry/list, Basic Information, Settings/LTR, release/packaging, or desktop scope.
- No real workbook, public-drive, or folder mutation.

## 6. May Touch

Future Developer implementation may touch only:

- `frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/intake-inbox.css`
- `frontend/src/pages/IntakeInboxPage.test.tsx`
- Optional focused component test for the preview panel if Developer adds one under `frontend/src/features/new-project/`
- `tasks/TASK_349B_SPECIFIED_LTR_WORKBOOK_AUTHORITY_MODAL_POLISH.md`
- `docs/task_349b_specified_ltr_workbook_authority_modal_polish_plan.md`
- `docs/lane_evidence/TASK_349B_specified-ltr-workbook-authority-modal-polish_*.md`
- `docs/task_board.md` through normal lane flow

## 7. Must Not Touch / Locked Paths

- `backend/**`
- `frontend/src/api/client.ts`
- Database schema or migrations
- Public LTR workbook read/write authority implementation
- Workbench LTR update preview semantics
- `frontend/src/features/project-workbench/**`
- `frontend/src/features/matrix-editor/**`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/**`
- Fee Evaluation, Folder Actions/public-folder workflow
- Real workbook/public-drive/folder data
- Basic Information, Settings/LTR, release/packaging, desktop residuals
- `.agents/**`
- `docs/project_management/**`
- StepInstance, Report, AI, permissions, LAN/server, multi-user scope

## 8. UX Acceptance

- The preview appears as a true modal/dialog overlay, not as a long inline page panel.
- Background Intake content is visibly subdued and interaction-locked while the modal is open.
- The modal is compact, dense, and operational; it does not introduce long explanatory copy, decorative hero styling, glass effects, gradient text, or status/readiness panel language.
- Found blank, partial, or full workbook rows still show the existing confirmation table and `Use this LTR number`.
- Not-found still shows `LTR workbook 中不存在该编号` and only allows closing back to Intake.
- Cancel/Close dismisses only the preview and returns to the prior Intake state without local creation or workbook write.
- Confirm continues the existing TASK_349A completion path and local duplicate second-layer protection.
- Keyboard/focus behavior is modal-appropriate: labelled dialog, `aria-modal` or equivalent, focus moves into the modal, focus returns after close, and Escape/backdrop behavior cannot bypass confirmation.

## 9. Validation Gate

Reviewer plan gate should verify:

- The task is frontend UI polish only and does not reopen TASK_349A backend/API semantics.
- May Touch and Locked Paths exclude backend/API client and external residuals.
- Modal acceptance criteria cover background lock, found/not-found behavior, confirm/cancel semantics, and accessibility/focus expectations.
- Validation is focused and testable.

Future implementation validation should include:

- Focused frontend tests for modal rendering, background interaction lock, found confirm, not-found close, cancel/close return, and no inline `.specified-ltr-preview-panel` page-flow regression.
- `npm test -- IntakeInboxPage --run` or an equivalent focused frontend test command.
- `npm run build`.
- Static/status checks proving no backend/API client/workbook authority/product-unrelated files changed.
- Optional browser smoke at `http://localhost:5173/intake` using safe mocked or non-mutating data.

## 10. Merge Gate

TASK_349B is implementation-authorized after:

- Reviewer plan gate passes.
- User explicitly approves Developer planning-first.
- Developer planning-first completes.
- Reviewer implementation-readiness passes.
- User explicitly approves reconciliation and Developer implementation.
- Planner source-of-truth reconciliation records the authorization.

Merge/acceptance requires Developer evidence, Reviewer implementation gate, QA gate as required by the board, and Integrator packaging/readiness. Remote push remains out of scope unless separately authorized.

## 11. Next Role

Recommended next role: Developer implementation pass.

---

## 12. Source-Of-Truth Reconciliation

Date: 2026-07-04

Planner reconciliation records:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed in `docs/lane_evidence/TASK_349B_specified-ltr-workbook-authority-modal-polish_developer.md`.
- Reviewer implementation-readiness passed by callback.
- User approved TASK_349B reconciliation and Developer implementation.

TASK_349B is complete/accepted by Integrator after Reviewer implementation gate pass, QA gate pass, and controlled packaging/readiness validation.
