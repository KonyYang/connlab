# TASK_348B Local LTR Duplicate Cancel State Recovery

> Status: complete/accepted by Integrator
> Created: 2026-07-03
> Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
> Lane: local-ltr-duplicate-cancel-state-recovery

---

## 1. Purpose

Plan a lightweight post-acceptance follow-up for `TASK_348A_LOCAL_LTR_DUPLICATE_OVERRIDE_CONFIRMATION`.

After TASK_348A acceptance, user smoke found that selecting `Cancel` in the `LOCAL LTR CONFLICT` panel can return the New Project / Intake page to a locked or incomplete state where the operator can effectively only use `Import`. The intended behavior is narrower: Cancel should cancel only the current local duplicate resolution flow, close the conflict panel, preserve the current imported application/session/form state, and restore the same editable/apply readiness that existed before the conflict appeared.

This task is complete/accepted after Reviewer implementation gate, QA gate, and Integrator packaging/readiness. The accepted package is frontend-only and restores imported New Project state after local duplicate conflict Cancel without changing backend duplicate, token, audit, current-owner, or workbook authority semantics.

---

## 2. Repository Facts

Confirmed from current code:

- `frontend/src/features/new-project/LocalLtrDuplicateConflictPanel.tsx` wires the `Cancel` button to `onCancel` only.
- `frontend/src/features/new-project/useNewProjectCompletion.ts` exposes `clearLocalDuplicateConflict`, which currently only clears `localDuplicateConflict`.
- `useNewProjectCompletion` does not perform backend writes when clearing a duplicate conflict.
- `frontend/src/pages/IntakeInboxPage.tsx` renders `LocalLtrDuplicateConflictPanel` with `onCancel={clearLocalDuplicateConflict}`.
- The New Project editor and completion dock are controlled by parent state such as `packageImport`, `activeCase`, `completionLoading`, `editorLoading`, `activeCase.confirmed_project_id`, `requiredState`, and `setupMissingKeys`.
- Current focused tests cover duplicate confirmation busy-lock behavior and `LocalLtrDuplicateConflictPanel` callback wiring, but do not cover Cancel preserving active intake/session/form readiness.

Planner inference:

- The defect should be treated as a frontend state recovery gap unless Developer discovery proves a typed API contract issue.
- A focused regression should reproduce the post-conflict cancel path at the hook/page boundary, not just at the panel button callback.

---

## 3. Target Behavior

When the operator clicks `Cancel` in the local LTR duplicate conflict panel:

1. The `LOCAL LTR CONFLICT` panel closes.
2. Current imported source, selected asset, selected intake case, parsed form state, setup values, and editable form state are preserved.
3. The page returns to the same editable/apply eligibility state it had before the duplicate conflict appeared.
4. `Apply LTR Number` and `Create Temporary Project` availability continue to be determined by the existing readiness rules, not by a stale duplicate-cancel state.
5. Cancel does not call the duplicate confirmation API, does not send `duplicate_resolution`, does not retire/supersede old local records, and does not write backend state.
6. Cancel does not clear the current application or force the operator to start over with `Import`.

---

## 4. Planned Scope

Future implementation may touch only the New Project frontend state/recovery path needed for Cancel behavior:

- Reproduce the user-reported Cancel state using focused hook/page/component tests.
- Fix the smallest frontend state boundary that causes the post-cancel lock or loss of readiness.
- Preserve TASK_348A duplicate conflict semantics, busy-lock semantics, explicit second confirmation, and open-existing behavior.
- Add focused frontend regression coverage.

---

## 5. Out Of Scope

This task must not:

- Change TASK_348A backend duplicate token, audit, migration, current-owner, or local override semantics.
- Change public-drive LTR Excel authority behavior.
- Add a cancel API or backend write unless Developer discovery proves the current typed API contract is wrong and Planner creates a separate approved lane.
- Modify Matrix Editor, Folder Actions/public folder workflow, Project Workbench unrelated behavior, Projects registry/list, Basic Information, Settings/LTR helpers, release/packaging work, or future scopes.
- Touch real LTR workbook files, real public-drive data, or real local/public folders.

---

## 6. May Touch Draft

Future Developer implementation may touch:

- `frontend/src/features/new-project/useNewProjectCompletion.ts`
- `frontend/src/features/new-project/useNewProjectCompletion.test.tsx`
- `frontend/src/features/new-project/LocalLtrDuplicateConflictPanel.tsx`
- `frontend/src/features/new-project/LocalLtrDuplicateConflictPanel.test.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/pages/IntakeInboxPage.test.tsx` if an existing page-level test harness is available or a focused test is added.
- `frontend/src/features/new-project/NewProjectCompletionDock.tsx` and focused tests only if readiness/disabled propagation must be adjusted.
- `frontend/src/intake-inbox.css` only if a small user-visible recovery/error hint is required.
- TASK_348B task, plan, evidence, and board docs through the normal lane flow.

---

## 7. Must Not Touch / Locked Paths

Locked unless a separate approved lane exists:

- `backend/**`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/**`
- `frontend/src/features/matrix-editor/**`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/**`
- Basic Information residual files
- Settings/LTR helper residual files
- release/packaging files and residuals
- real public-drive LTR workbook/data
- real `D:\Test Project/**`
- real `D:\PublicProject/**`
- real public-drive folders
- `.agents/**`
- `docs/project_management/**`
- `temp_agents_stash.md`
- StepInstance, Report, AI, permissions, LAN/server, multi-user

---

## 8. Validation Gate

Reviewer plan gate should confirm:

- The lane is a post-acceptance TASK_348A frontend recovery follow-up and not a backend duplicate override redesign.
- May Touch is sufficient for New Project state recovery.
- Backend/product authority locks remain intact.
- Test expectations are specific enough to catch the user-reported defect.

Future implementation validation should include:

- Focused frontend test for duplicate conflict Cancel hiding the panel while preserving active intake/session/form state.
- Focused frontend test that `Apply LTR Number` / `Create Temporary Project` availability after Cancel matches the pre-conflict readiness rules.
- Test proving Cancel makes no second `completeNewProject` call and sends no `duplicate_resolution`.
- Focused regression for no stale busy/disabled lock after Cancel.
- `npm test -- --run useNewProjectCompletion LocalLtrDuplicateConflictPanel IntakeInboxPage NewProjectCompletionDock` or the closest focused equivalent.
- `npm run build`.
- Browser smoke on New Project / Intake with a safe mocked or fixture local duplicate conflict; no real workbook or public-drive mutation.

---

## 9. Merge Gate

Do not merge or package until:

1. Reviewer plan gate passes.
2. User explicitly approves Developer planning-first and later implementation according to protocol.
3. Developer evidence records implementation details and focused validation.
4. Reviewer implementation gate passes.
5. QA gate runs the agreed frontend/browser smoke or records a justified blocker.
6. Integrator confirms package scope excludes backend duplicate semantics, real workbook/folder mutation, Basic Information, Settings/LTR, release/packaging residuals, `.agents/**`, and `docs/project_management/**`.

---

## 10. Next Role

Recommended next role: Orchestrator/User for next routing decision.

Integrator gate: accepted.

---

## 11. Implementation Authorization Reconciliation

Source-of-truth reconciliation recorded:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed in `docs/lane_evidence/TASK_348B_local-ltr-duplicate-cancel-state-recovery_developer.md`.
- Reviewer implementation-readiness gate passed.
- User explicitly approved TASK_348B reconciliation and Developer implementation.
- Planner reconciliation evidence is recorded in `docs/lane_evidence/TASK_348B_local-ltr-duplicate-cancel-state-recovery_reconciliation_planner.md`.

This authorization does not broaden scope beyond the TASK_348B frontend local duplicate Cancel state recovery plan. Backend duplicate/token/audit/current-owner semantics, public workbook authority, real workbook/folder data, Matrix Editor, Folder Actions/public folder workflow, Project Workbench unrelated behavior, Basic Information residuals, Settings/LTR helper residuals, release/packaging residuals, `.agents/**`, `docs/project_management/**`, StepInstance, Report, AI, permissions, LAN/server, and multi-user scope remain locked.
