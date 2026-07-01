# TASK_347A New Project Apply LTR Busy Lock UX - QA Evidence

Status: qa_pass
Date: 2026-07-02
Role: QA / Smoke Owner
Task: `TASK_347A_NEW_PROJECT_APPLY_LTR_BUSY_LOCK_UX`
Lane: `new-project-apply-ltr-busy-lock-ux`

## Gate Result

QA gate: pass.

Recommended next role: Integrator packaging/readiness.

Blocking findings: none.

Residual risk:

- QA did not click the live `Apply LTR Number` button because the real `/complete-new-project` path can write to the authoritative LTR workbook. No safe delayed/mocked browser harness was available in this QA thread. Focused mocked frontend tests and static/source checks covered the busy-lock behavior; browser smoke was limited to read-only `/intake` observation.

No product source, product tests, `docs/task_board.md`, backend files, frontend API client, real LTR workbook, real project folder, release/packaging residual, `.agents/**`, or `docs/project_management/**` files were modified by QA. QA created this evidence file and artifacts under `docs/lane_evidence/artifacts/TASK_347A_qa/`.

## Sources Re-read

- `AGENTS.md`
- `docs/task_board.md`
- `tasks/TASK_347A_NEW_PROJECT_APPLY_LTR_BUSY_LOCK_UX.md`
- `docs/task_347a_new_project_apply_ltr_busy_lock_ux_plan.md`
- `docs/lane_evidence/TASK_347A_new-project-apply-ltr-busy-lock-ux_planner.md`
- `docs/lane_evidence/TASK_347A_new-project-apply-ltr-busy-lock-ux_developer.md`
- `docs/lane_evidence/TASK_347A_new-project-apply-ltr-busy-lock-ux_reconciliation_planner.md`
- Actual TASK_347A frontend diff/status and focused code/tests/CSS.

Board timing note:

- `docs/task_board.md` still says TASK_347A is implementation authorized and pending Developer implementation.
- Current Orchestrator/User delegation says Reviewer implementation gate passed and QA is required. QA recorded this source-of-truth timing mismatch and did not update the board.

Current phase:

- `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

## Command Validation

Focused frontend tests:

```powershell
cd frontend
npm test -- IntakeSourcePanel AttachmentList Sidebar NewProjectCompletionDock --run
```

Result:

```text
Test Files 4 passed (4)
Tests 4 passed (4)
```

Frontend build:

```powershell
cd frontend
npm run build
```

Result: passed. Vite emitted the existing chunk-size warning only.

Static/package checks:

```powershell
git diff --check -- frontend/src/App.tsx frontend/src/components/layout/AppShell.tsx frontend/src/components/layout/Sidebar.tsx frontend/src/features/intake/AttachmentList.tsx frontend/src/features/intake/IntakeSourcePanel.tsx frontend/src/features/new-project/NewProjectCompletionDock.tsx frontend/src/intake-inbox.css frontend/src/pages/IntakeInboxPage.tsx frontend/src/styles.css docs/lane_evidence/TASK_347A_new-project-apply-ltr-busy-lock-ux_developer.md
Select-String -Path frontend/src/App.tsx,frontend/src/components/layout/AppShell.tsx,frontend/src/components/layout/Sidebar.tsx,frontend/src/components/layout/Sidebar.test.tsx,frontend/src/features/intake/AttachmentList.tsx,frontend/src/features/intake/AttachmentList.test.tsx,frontend/src/features/intake/IntakeSourcePanel.tsx,frontend/src/features/intake/IntakeSourcePanel.test.tsx,frontend/src/features/new-project/NewProjectCompletionDock.tsx,frontend/src/features/new-project/NewProjectCompletionDock.test.tsx,frontend/src/intake-inbox.css,frontend/src/pages/IntakeInboxPage.tsx,frontend/src/styles.css,docs/lane_evidence/TASK_347A_new-project-apply-ltr-busy-lock-ux_developer.md,docs/lane_evidence/artifacts/TASK_347A_qa/*.json -Pattern '[ \t]+$' -Encoding UTF8
Select-String -Path frontend/src/App.tsx,frontend/src/components/layout/AppShell.tsx,frontend/src/components/layout/Sidebar.tsx,frontend/src/features/intake/AttachmentList.tsx,frontend/src/features/intake/IntakeSourcePanel.tsx,frontend/src/features/new-project/NewProjectCompletionDock.tsx,frontend/src/intake-inbox.css,frontend/src/pages/IntakeInboxPage.tsx,frontend/src/styles.css -Pattern 'Workbook opened|Writing row|Saving workbook|Step 1|Step 2|percent|progress|public-folder-workflow|sync|submit|pull|ProjectListPage|MatrixEditor|D:\\Test Project|D:\\PublicProject|completeNewProject\(' -Encoding UTF8
```

Results:

- `git diff --check`: passed with LF/CRLF warnings only.
- Trailing whitespace scan: no matches.
- Fake-progress / future-scope scan: no blocking matches. `App.tsx` already imports/routes `ProjectListPage` and `ProjectMatrixEditorPage`; this is baseline routing and not a TASK_347A scope breach. No fake workbook phase copy, percent/progress UI, real folder path, Sync/Submit/Pull, or direct `completeNewProject(` call was introduced in the TASK_347A package files.

Forbidden-scope status:

- Current worktree still contains external dirty residuals in backend, `frontend/src/api/client.ts`, Settings/LTR, release/packaging, Workbench Folder Actions, `docs/task_board.md`, `pyproject.toml`, and `temp_agents_stash.md`.
- TASK_347A package status is limited to approved New Project/shell busy-lock files plus focused tests/evidence. `frontend/src/styles.css` contains sidebar disabled-state support and is accepted as TASK_347A-scoped per Reviewer note.

## Browser Smoke

Local app:

- Frontend dev server was started for QA on `127.0.0.1:5173`.
- A backend server was already occupying `127.0.0.1:8000`; the QA backend start attempt exited with port-in-use and did not create a new backend process.
- QA stopped the temporary frontend listener after the smoke. Final listener checks for `5173` and `8000` returned no remaining output.

Artifacts:

- `docs/lane_evidence/artifacts/TASK_347A_qa/browser_intake_readonly_smoke_20260702.png`
- `docs/lane_evidence/artifacts/TASK_347A_qa/browser_intake_readonly_smoke_20260702.json`
- `docs/lane_evidence/artifacts/TASK_347A_qa/frontend_vite_qa_20260702_074438.out.log`
- `docs/lane_evidence/artifacts/TASK_347A_qa/frontend_vite_qa_20260702_074438.err.log`
- `docs/lane_evidence/artifacts/TASK_347A_qa/backend_uvicorn_qa_20260702_074438.err.log`

Read-only browser observations at `http://localhost:5173/intake`:

- Page loaded with no browser console warnings/errors.
- New Project / intake page shell rendered.
- Sidebar, Import, hidden file inputs, setup fields, and temporary project control were inspectable at rest.
- No busy copy or fake progress was visible at rest, as expected.
- Current live state did not expose `Apply LTR Number` because there was no safely prepared active completion-ready case in the browser state.

Safety blocker for live busy trigger:

- QA did not trigger `Apply LTR Number`: the real path calls `/api/intake-cases/{case_id}/complete-new-project`, which may mutate the authoritative LTR workbook. This lane explicitly forbids real workbook mutation.
- No safe mocked/delayed completion harness was available through the running browser.
- Backend log scan found no `complete-new-project` POST and no LTR write attempt from QA.

## Coverage Mapping

- Apply LTR double-submit guard: covered by focused `NewProjectCompletionDock` test and source inspection of `completionDisabled`.
- Compact busy copy with accessibility semantics: covered by focused test/source inspection; `NewProjectCompletionDock` renders `role="status"` and `aria-live="polite"` with concise copy.
- Import button / hidden file input / drag-drop guard: covered by focused `IntakeSourcePanel` test and source inspection.
- Attachment select/open/import/duplicate guard: covered by focused `AttachmentList` test and source inspection.
- Sidebar navigation/collapse lock: covered by focused `Sidebar` test and source inspection.
- Setup/editor/temporary action guards: covered by source inspection and Developer evidence; live browser state was not safe to drive into busy state.
- Success/failure recovery: covered by Developer evidence and existing single-source `completionLoading` flow; not live-smoked because live completion would risk real authority mutation.
- No fake progress: covered by source scan and read-only browser smoke.

## QA Decision

QA gate: pass.

Recommended next role: Integrator packaging/readiness.

Integrator notes:

- Package `frontend/src/styles.css` only as the small TASK_347A sidebar disabled-state support noted by Reviewer.
- Exclude external Settings/LTR, release/packaging, backend, API client, Workbench Folder Actions, Matrix, board residuals, and `temp_agents_stash.md`.
- If a full live busy-state browser test is required later, route a separate safe mocked/delayed harness or disposable LTR-authority fixture lane. Do not test it against real LTR workbook authority data.
