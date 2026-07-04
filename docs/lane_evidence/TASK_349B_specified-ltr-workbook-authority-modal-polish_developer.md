# TASK_349B Developer Evidence - Specified LTR Workbook Authority Modal Polish

Status: implementation complete - pending Reviewer implementation gate

Task: `TASK_349B_SPECIFIED_LTR_WORKBOOK_AUTHORITY_MODAL_POLISH`
Lane: `specified-ltr-workbook-authority-modal-polish`
Role: Developer
Date: 2026-07-04

---

## 1. Gate And Scope

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Allowed reason:

- Orchestrator delegated TASK_349B Developer planning-first.
- Delegation states Reviewer plan gate passed and user approved Developer planning-first.
- This pass is docs-only and does not implement product code.

Source-of-truth timing mismatch:

- Local `docs/task_board.md`, task file, plan header, and Planner evidence still record TASK_349B as planned/ready for Reviewer plan gate.
- Developer proceeded with planning-first refinement because the delegation explicitly authorized this docs-only pass.
- Before implementation, Planner/Orchestrator should reconcile source-of-truth to record Reviewer plan gate pass, Developer planning-first completion, Reviewer implementation-readiness if required, and user implementation approval.

---

## 2. Sources Read

Governance and design:

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `.agents/skills/impeccable/SKILL.md`
- `$impeccable` product context
- `.agents/skills/impeccable/reference/product.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`

TASK_349B:

- `tasks/TASK_349B_SPECIFIED_LTR_WORKBOOK_AUTHORITY_MODAL_POLISH.md`
- `docs/task_349b_specified_ltr_workbook_authority_modal_polish_plan.md`
- `docs/lane_evidence/TASK_349B_specified-ltr-workbook-authority-modal-polish_planner.md`

TASK_349A context:

- `docs/task_board.md` TASK_349A/TASK_349B rows
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_developer.md`
- current TASK_349A preview component, mount point, CSS, and tests

Code inspected read-only:

- `frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/intake-inbox.css`
- `frontend/src/pages/IntakeInboxPage.test.tsx`

---

## 3. Current Code Findings

- The preview component already contains the accepted TASK_349A content and action semantics.
- It currently renders an inline `<section className="specified-ltr-preview-panel">`.
- It uses `role="dialog"` for found previews and `role="alertdialog"` for not-found/blocked previews, but does not set `aria-modal`.
- There is no modal overlay, focus entry, focus trap, Escape handling, or focus return logic.
- `IntakeInboxPage.tsx` mounts the panel after the main Intake layout when `specifiedLtrWorkbookPreview` exists.
- CSS styles the panel as a page-flow bordered panel with margin/padding.
- Existing tests cover found preview, not-found, confirm, close, and local duplicate handoff. They do not yet assert modal overlay, `aria-modal`, focus behavior, or no-inline-panel regression.

---

## 4. Future Implementation Strategy

Implementation should be frontend-only.

Use the existing `SpecifiedLtrWorkbookAuthorityPreviewPanel` as the modal content owner, and upgrade it from inline section to modal dialog surface:

- Add an outer fixed overlay/backdrop.
- Add a dialog surface with `aria-modal="true"` and the existing labelled title.
- Keep existing found/not-found content, buttons, labels, and preview row table.
- Add minimal focus management inside the component or via a small local hook in the same file.
- Keep `IntakeInboxPage` as the mount owner and state owner. Do not add API calls or business rules there.
- Keep existing page-level `specifiedLtrPreviewActive` lock so background controls stay disabled.

Focus behavior:

- Capture the previously focused element when the modal opens.
- Move focus to `Use this LTR number` for found previews, or `Close` for not-found/blocked.
- Trap Tab/Shift+Tab within modal controls.
- Escape performs safe Cancel/Close only.
- Restore focus to the previous element if still connected, otherwise to a safe Intake control if available.

Backdrop behavior:

- Preferred: backdrop click is inert to avoid accidental dismissal during an authority confirmation.
- If implementation chooses backdrop close, it must be exactly equivalent to Cancel/Close and must be covered by tests.

---

## 5. Exact Future Implementation File List

Future implementation May Touch:

- `frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/intake-inbox.css`
- `frontend/src/pages/IntakeInboxPage.test.tsx`
- Optional: `frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.test.tsx`
- `docs/lane_evidence/TASK_349B_specified-ltr-workbook-authority-modal-polish_developer.md`
- TASK_349B plan/evidence docs through normal lane flow

Must not touch:

- `backend/**`
- `frontend/src/api/client.ts`
- public workbook authority/read/write services
- preview acknowledgement contract
- local duplicate behavior
- Workbench LTR update preview behavior
- Workbench, Matrix, Projects registry, Fee, Folder Actions, Basic Information, Settings/LTR, release/packaging, `.agents/**`, `docs/project_management/**`

---

## 6. Validation Plan

Focused frontend tests:

- Modal renders with `role="dialog"` or `role="alertdialog"` and `aria-modal="true"`.
- Found preview displays row values and `Use this LTR number`.
- Not-found preview displays `LTR workbook 中不存在该编号`, does not render confirm, and close returns to Intake.
- Confirm still calls completion with the existing preview ack.
- Cancel/Close does not call completion.
- Escape triggers safe close only.
- Focus moves into the modal and returns after close where practical.
- Background Apply/import/editor actions remain locked while modal is open.
- Local duplicate handoff remains intact after preview confirm.

Commands:

- `npm test -- IntakeInboxPage --run`
- Optional: `npm test -- SpecifiedLtrWorkbookAuthorityPreviewPanel --run`
- `npm run build`
- `git diff --check` on TASK_349B package files
- trailing whitespace scan
- static anti-pattern scan for side-stripe borders over 1px, gradient text, glass/backdrop blur, and long/modal marketing copy
- forbidden-scope status proving no backend/API client/workbook authority/Workbench/Matrix/Projects/release/governance changes

Browser smoke:

- If safe browser/test data is available, smoke `/intake` and verify modal overlay, background lock, focus/keyboard, found confirm, and not-found close-only behavior.
- If not available, record a QA residual and do not use real public workbook mutation to force a live path.

---

## 7. External Residuals

Current worktree has unrelated backend/frontend/tests/release residuals visible in `git status`, including Settings/LTR, release/packaging, intake/precheck/parser/New Project adjacent files, and TASK_349A/TASK_349B docs.

This planning-first pass intentionally modified only TASK_349B plan/evidence docs.

---

## 8. Validation Results

Planning-doc validation:

- Required TASK_349B task/plan/planner evidence files exist.
- Developer evidence created at `docs/lane_evidence/TASK_349B_specified-ltr-workbook-authority-modal-polish_developer.md`.
- Product code was not modified in this planning-first pass.
- `git diff --check -- docs/task_349b_specified_ltr_workbook_authority_modal_polish_plan.md docs/lane_evidence/TASK_349B_specified-ltr-workbook-authority-modal-polish_developer.md` passed.
- Trailing whitespace scan on the TASK_349B plan/evidence returned no matches.
- Targeted status still shows pre-existing backend/frontend/tests/release residuals, including `frontend/src/intake-inbox.css`; those residuals are excluded from this docs-only planning-first pass and were not cleaned or packaged.

---

## 9. Implementation Pass

Date: 2026-07-04

Authorization:

- Orchestrator delegated TASK_349B Developer implementation after Planner source-of-truth reconciliation.
- `docs/lane_evidence/TASK_349B_specified-ltr-workbook-authority-modal-polish_reconciliation_planner.md` records implementation authorization and pending Developer implementation.

Changed files for TASK_349B:

- `frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx`
- `frontend/src/pages/IntakeInboxPage.test.tsx`
- `frontend/src/intake-inbox.css`
- `docs/lane_evidence/TASK_349B_specified-ltr-workbook-authority-modal-polish_developer.md`

Implementation summary:

- Converted the specified-LTR workbook authority preview from inline page-flow panel to a fixed modal layer with an inert backdrop.
- Preserved TASK_349A found/not-found business behavior, preview ack confirmation, local duplicate handoff, and close/cancel behavior.
- Added modal semantics: found previews use `role="dialog"`, not-found/blocked previews use `role="alertdialog"`, both with `aria-modal="true"` and the existing labelled title.
- Added focus entry to `Use this LTR number` for found previews and `Close` for not-found/blocked previews.
- Added local Tab/Shift+Tab focus containment and Escape safe close when not confirming.
- Kept the visual treatment compact and operational: plain surface, 1px border, no side stripe, no gradient text, no glass/backdrop blur, no nested card treatment.

Focused regression coverage:

- Found preview renders as modal dialog with `aria-modal="true"`.
- Modal wrapper exists and background Apply action remains disabled while the preview is open.
- Focus enters the primary confirm action for found previews.
- Not-found preview renders as close-only alertdialog with no confirm action.
- Escape closes the found modal without calling completion.
- Existing confirm path and local duplicate handoff remain covered.

External residual classification:

- `frontend/src/intake-inbox.css` already contains unrelated Local LTR duplicate modal residual hunks in the working tree. TASK_349B only added the `specified-ltr-preview-*` modal/backdrop/surface styles in that file.
- Targeted forbidden-scope status still shows pre-existing backend/API client/Matrix/release residuals. They were not edited, cleaned, or packaged by this implementation pass.

Validation results:

- Initial TDD red: `npm test -- IntakeInboxPage --run` failed on missing `aria-modal`, as expected.
- `npm test -- IntakeInboxPage --run` passed: 1 file / 6 tests.
- `npm test -- NewProjectCompletionDock IntakeInboxPage --run` passed: 2 files / 8 tests.
- `npm run build` passed. Existing Vite chunk-size warning remains.
- `git diff --check -- frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx frontend/src/pages/IntakeInboxPage.test.tsx frontend/src/intake-inbox.css docs/lane_evidence/TASK_349B_specified-ltr-workbook-authority-modal-polish_developer.md` passed with existing LF/CRLF warnings only.
- Trailing whitespace scan on TASK_349B package files returned no matches.
- Static anti-pattern scan found no side-stripe border over 1px, no `background-clip: text`, no `backdrop-filter`, and no glass copy. It reported `preview_ack` only as a non-displayed existing contract field in component logic.
- Browser smoke was not run in this Developer thread because there is no safe mocked `/intake` authority-preview harness available, and forcing a real Apply LTR path risks public workbook authority side effects. QA should live-smoke the modal with safe fixture data.

Recommended next role:

- Reviewer implementation gate.

Blocking summary:

- None for TASK_349B implementation. QA browser smoke remains the normal next-gate residual.

---

## 10. Integrator Packaging Closeout

Date: 2026-07-04

Integrator result:

- `Integrator gate: accepted`.
- Package was limited to approved TASK_349B frontend modal polish files/tests/docs/evidence/board updates.
- `frontend/src/intake-inbox.css` was hunk-staged so only TASK_349B `.specified-ltr-preview-*` modal/backdrop/surface changes entered the package; same-file local duplicate modal residual hunks were excluded.
- No backend, API client, workbook authority contract, Matrix, Workbench, Fee, Folder Actions, Projects, release/packaging, Settings/LTR, Basic Information, real workbook/public-drive data, `.agents/**`, `docs/project_management/**`, or `temp_agents_stash.md` files were staged.

Validation summary:

- Focused frontend tests: `npm test -- IntakeInboxPage --run` passed, 1 file / 6 tests.
- Focused preservation tests: `npm test -- NewProjectCompletionDock IntakeInboxPage --run` passed, 2 files / 8 tests.
- Frontend build passed with the existing Vite chunk-size warning only.
- Staged `git diff --cached --check`, staged whitelist/forbidden-path checks, trailing whitespace scan, anti-pattern scan, and no-real-workbook/folder mutation scan passed.

Remote push was intentionally not performed.
