# TASK_349B QA Evidence - Specified LTR Workbook Authority Modal Polish

Date: 2026-07-04

Role: QA / Smoke Owner

Task: `TASK_349B_SPECIFIED_LTR_WORKBOOK_AUTHORITY_MODAL_POLISH`

Lane: `specified-ltr-workbook-authority-modal-polish`

Result: `qa_pass`

---

## 1. Gate And Role Boundary

- Current phase from `docs/task_board.md`: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Orchestrator delegation states Reviewer implementation gate passed and QA gate is required.
- QA performed validation and evidence only.
- QA did not modify product source, tests, `docs/task_board.md`, backend/API/client/workbook authority code, Workbench/Matrix/Fee/Folder Actions/Projects code, release/packaging residuals, real workbook data, or public-drive/folder data.
- QA did not stage, commit, push, or package.

## 2. Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `tasks/TASK_349B_SPECIFIED_LTR_WORKBOOK_AUTHORITY_MODAL_POLISH.md`
- `docs/task_349b_specified_ltr_workbook_authority_modal_polish_plan.md`
- `docs/lane_evidence/TASK_349B_specified-ltr-workbook-authority-modal-polish_planner.md`
- `docs/lane_evidence/TASK_349B_specified-ltr-workbook-authority-modal-polish_developer.md`
- `docs/lane_evidence/TASK_349B_specified-ltr-workbook-authority-modal-polish_reconciliation_planner.md`
- TASK_349A accepted QA/package-isolation context in `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_qa.md`
- Actual status/diff for TASK_349B candidate files and visible external residuals

## 3. Candidate Package / Scope Check

TASK_349B product candidate observed in diff:

- `frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx`
- `frontend/src/intake-inbox.css`
- `frontend/src/pages/IntakeInboxPage.test.tsx`

Developer evidence also records `docs/lane_evidence/TASK_349B_specified-ltr-workbook-authority-modal-polish_developer.md`.

Observed implementation behavior from static diff:

- Specified-LTR preview now renders inside `.specified-ltr-preview-modal`.
- Found preview uses `role="dialog"` with `aria-modal="true"`.
- Not-found/blocked preview uses `role="alertdialog"` with `aria-modal="true"`.
- Modal focus enters the primary confirm button for found previews and Close for not-found/blocked previews.
- Tab/Shift+Tab focus containment and Escape safe close are implemented.
- TASK_349A preview ack, confirm, cancel/close, and local duplicate handoff are preserved at component/test level.

External residuals still visible and excluded from TASK_349B:

- Backend intake/parser/duplicate residuals.
- `frontend/src/api/client.ts`.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`.
- release/packaging/desktop residuals and `temp_agents_stash.md`.
- Existing same-file non-TASK_349B `frontend/src/intake-inbox.css` local duplicate modal hunks.

Package note:

- `frontend/src/intake-inbox.css` contains TASK_349B `.specified-ltr-preview-*` hunks and external local duplicate modal hunks in the same file. Integrator must use hunk-level staging/package selection for this file and must not stage the unrelated local duplicate residual hunks as TASK_349B.

## 4. Focused Frontend Tests

Command:

```powershell
cd frontend
npm test -- IntakeInboxPage --run
```

Observed result:

- Passed.
- `1` test file passed.
- `6` tests passed.

Command:

```powershell
cd frontend
npm test -- NewProjectCompletionDock IntakeInboxPage --run
```

Observed result:

- Passed.
- `2` test files passed.
- `8` tests passed.

Coverage confirmed by tests/source inspection:

- Found preview modal/dialog with `aria-modal`.
- Not-found preview close-only alertdialog with no confirm action.
- Background Apply action remains disabled while preview is open.
- Focus entry into modal action.
- Escape closes without completing.
- Confirm handoff and local duplicate behavior remain covered.

## 5. Build

Command:

```powershell
cd frontend
npm run build
```

Observed result:

- Passed.
- Existing Vite chunk-size warning only.

## 6. Static Checks

Candidate diff check:

```powershell
git diff --check -- frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx frontend/src/pages/IntakeInboxPage.test.tsx frontend/src/intake-inbox.css docs/lane_evidence/TASK_349B_specified-ltr-workbook-authority-modal-polish_developer.md docs/task_349b_specified_ltr_workbook_authority_modal_polish_plan.md tasks/TASK_349B_SPECIFIED_LTR_WORKBOOK_AUTHORITY_MODAL_POLISH.md docs/lane_evidence/TASK_349B_specified-ltr-workbook-authority-modal-polish_planner.md docs/lane_evidence/TASK_349B_specified-ltr-workbook-authority-modal-polish_reconciliation_planner.md
```

Observed result:

- Passed with LF/CRLF warnings only for frontend files.

Trailing whitespace scan on candidate files:

```powershell
Select-String -Path <TASK_349B candidate files/docs> -Pattern '[ \t]+$' -Encoding UTF8
```

Observed result:

- No matches.

Anti-pattern scan on TASK_349B production files:

```powershell
Select-String -Path frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx,frontend/src/intake-inbox.css -Pattern 'border-left:\s*[2-9]px|background-clip:\s*text|backdrop-filter|glass|linear-gradient|hero|box-shadow:.*rgba' -Encoding UTF8
```

Observed result:

- No side-stripe border, gradient text, glass/backdrop-filter, or hero copy found in TASK_349B component.
- CSS scan reported ordinary `box-shadow` styles and an existing `linear-gradient` elsewhere in `intake-inbox.css`; TASK_349B modal addition uses plain backdrop/surface, 1px border, and operational shadow only.

No-real-workbook/folder mutation scan on TASK_349B files:

```powershell
Select-String -Path frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx,frontend/src/pages/IntakeInboxPage.test.tsx,frontend/src/intake-inbox.css -Pattern 'D:\\Test Project|D:\\PublicProject|D:/Test Project|D:/PublicProject|Workbooks\.Open|SaveAs|win32com|Dispatch\(|open_write_session|write_registration_row|append_registration_row|\.save\(|copyfile|shutil\.copy|os\.remove|rmtree' -Encoding UTF8
```

Observed result:

- Production component/CSS had no matches.
- `D:/PublicProject/LTR.xlsx` appeared only in test fixture strings in `IntakeInboxPage.test.tsx`; no real workbook operation is performed by the test.

Forbidden-scope status:

```powershell
git status --short -- backend frontend/src/api/client.ts frontend/src/features/project-workbench frontend/src/features/matrix-editor frontend/src/pages/ProjectListPage.tsx frontend/src/features/projects-registry frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx frontend/src/pages/IntakeInboxPage.tsx frontend/src/intake-inbox.css frontend/src/pages/IntakeInboxPage.test.tsx .agents docs/project_management dist_release packaging temp_agents_stash.md
```

Observed result:

- TASK_349B candidate product files were visible under the approved frontend UI polish scope.
- Locked/external residuals were also visible in backend, `frontend/src/api/client.ts`, Matrix, release/packaging, and `temp_agents_stash.md`; these are not TASK_349B scope and must remain excluded.
- No TASK_349B evidence indicates backend/API/client/workbook authority/local duplicate semantic changes.

## 7. Browser Smoke

Live browser modal smoke was not executed.

Reason:

- The specified-LTR preview modal appears only after the Intake Apply LTR preview path.
- No safe mocked/disposable browser harness was available in this QA thread.
- Triggering the live Apply LTR path could touch real public workbook authority data.

Disposition:

- Non-blocking residual for TASK_349B because focused frontend tests validate the modal/dialog semantics, focus entry, Escape close, background lock, not-found close-only behavior, confirm path, and local duplicate preservation without real workbook mutation.
- Future browser smoke should use a mocked/disposable authority-preview harness.

## 8. QA Decision

QA gate: pass.

Blocking findings: none.

Residual risks:

- Live browser modal smoke remains unexecuted due safe-data/tooling constraints.
- `frontend/src/intake-inbox.css` contains external same-file residual hunks; Integrator must hunk-stage only TASK_349B `.specified-ltr-preview-*` modal changes and exclude unrelated local duplicate modal residuals.
- External backend/API client/Matrix/release/packaging residuals remain dirty and must not be packaged with TASK_349B.

Recommended next role:

- Integrator packaging/readiness.

Integrator instruction:

- Stage/package only TASK_349B candidate hunks/files recorded above.
- Exclude backend/API client/workbook authority/local duplicate semantic residuals, Workbench/Matrix/Fee/Folder Actions/Projects residuals, release/packaging residuals, `.agents/**`, `docs/project_management/**`, and `temp_agents_stash.md`.
