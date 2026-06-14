# TASK_314C Matrix Fee Project Folder Regression Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a focused regression gate proving TASK_314A Matrix draft persistence and TASK_314B Fee draft persistence still work with TASK_318/TASK_320/TASK_321 Project Folder readiness and Required forms generation.

**Architecture:** Treat TASK_314C as a test-first linkage hardening task. Prefer adding focused backend/frontend regression tests and static guards over changing production code; only apply small production fixes when a regression test exposes a real cross-task bug. Keep Matrix, Fee, and Project Folder authority boundaries intact.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy, Pydantic v2, pytest, React, TypeScript, Vitest.

---

## Current Phase And Permission Gate

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

Current task status:

```text
TASK_314C_MATRIX_FEE_PROJECT_FOLDER_REGRESSION is complete.
```

Implementation was started only after the user explicitly approved TASK_314C. TASK_314C is a regression gate; completion does not authorize TASK_315 or any execution/reporting scope.

## Anti-Skip Statement

- Current active completed baseline: TASK_314A, TASK_314B, and TASK_314C are complete.
- TASK_314C implementation was allowed because the user explicitly approved execution.
- Not allowed now: enter TASK_315, implement rebase, or change Project Folder behavior beyond the completed TASK_314C regression fix.

## Task Understanding

### Goal

Verify the completed background-draft work does not break the downstream Project Folder preparation flow:

- Confirmed Matrix authority remains the Matrix source for downstream flows.
- Confirmed Fee authority remains the Fee source for Required forms.
- Project Folder task selectors still present one ordered task flow.
- Required forms still gate on current Confirmed Matrix and current Confirmed Fee.

### Inputs

- Active Confirmed Matrix authority.
- Matrix Editor draft save/restore/discard behavior.
- Fee Evaluation pricing draft save/restore/discard behavior.
- Latest Confirmed Fee authority.
- Official project folder check status.
- Required forms preview/generation status.
- Workbench Project Folder row model.

### Outputs

- Regression tests and validation commands.
- Small fixes only if tests expose an existing linkage bug.
- Updated task board with pass counts after approved implementation.

### Modules

Backend:

- `backend/application/matrix_editor_session_service.py`
- `backend/application/fee_evaluation_pricing_draft_persistence_service.py`
- `backend/application/confirmed_fee_version_service.py`
- `backend/application/official_project_folder_check_service.py`
- `backend/application/project_folder_required_forms_service.py`
- related API route modules and repositories already covered by existing tests

Frontend:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`

### Explicit Non-Goals

- Do not implement Matrix Draft -> Fee Draft incremental rebase.
- Do not change Fee formulas or Matrix semantics.
- Do not generate new Required forms behavior.
- Do not change ProjectOutputRecord schema, generation semantics, or API contracts. If a regression points there, stop and split a follow-up task.
- Do not add StepInstance, execution persistence, report generation, AI, permissions, LAN, or multi-user scope.

## File-Level Plan

Likely test files to modify:

- `tests/unit/test_project_folder_required_forms_service.py`
- `tests/unit/test_official_project_folder_check_service.py`
- `tests/unit/test_frontend_shell_files.py`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`

Likely production files only if a regression is found:

- `backend/application/project_folder_required_forms_service.py`
- `backend/application/official_project_folder_check_service.py`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`

Do not create new backend APIs for TASK_314C unless a regression proves an existing route contract cannot express the current authority state.

Hard stop rule:

- TASK_314C fixes may touch only the narrow linkage files listed above.
- If a fix requires changing ProjectOutputRecord schema, ProjectOutputRecord generation semantics, API contracts, storage migrations, or production files outside this list, stop TASK_314C implementation and create a separate follow-up task for review.
- Do not treat a failing broad regression as permission to refactor Matrix, Fee, Project Folder, or output-record architecture inside TASK_314C.

## Regression Contract

TASK_314C should lock these contracts:

1. Current Confirmed Matrix, not unsaved Matrix Editor payload, drives downstream readiness.
2. Current Confirmed Fee, not unsaved Fee pricing draft, drives Required forms readiness.
3. Existing current Confirmed Fee becomes stale when Matrix/Fee context changes.
4. Missing current Fee pricing draft may seed for Confirm Fee, but that seed is not itself Confirmed Fee authority.
5. Required forms remains blocked until Confirmed Fee authority is current.
6. Project Folder task order remains stable and operator-facing.
7. Project Folder UI does not regress to broad Package wording or old package-preview actions.

## Implementation Tasks

### Task 0: Baseline Existing Regression State

**Files:**

- No code changes.
- Record results in implementation notes before adding new tests.

- [ ] **Step 1: Run existing Matrix baseline**

Run:

```powershell
py -m pytest tests/unit/test_matrix_editor_session_service.py tests/integration/test_matrix_editor_session_api.py tests/integration/test_confirmed_matrix_authority_api.py tests/integration/test_matrix_revision_flow_api.py -q
```

Expected: pass. If it fails before TASK_314C adds tests, record the failure as baseline state and stop to assess whether it belongs to TASK_314C or a separate repair.

- [ ] **Step 2: Run existing Fee baseline**

Run:

```powershell
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py tests/unit/test_confirmed_fee_version_service.py tests/integration/test_confirmed_fee_version_api.py -q
```

Expected: pass. If it fails before TASK_314C adds tests, record the failure as baseline state and stop to assess whether it belongs to TASK_314C or a separate repair.

- [ ] **Step 3: Run existing Project Folder baseline**

Run:

```powershell
py -m pytest tests/unit/test_official_project_folder_check_service.py tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
```

Expected: pass. If it fails before TASK_314C adds tests, record the failure as baseline state and stop to assess whether it belongs to TASK_314C or a separate repair.

- [ ] **Step 4: Run existing frontend baseline**

Run:

```powershell
cd frontend
npm test -- --run MatrixEditorWorkspace FeeEvaluationReviewExportPage projectFolderTaskSelectors ProjectFolderTaskList ProjectWorkbenchLayout --watch=false
```

Expected: pass. Existing non-failing React `act(...)` warnings in Fee tests may be recorded, but do not treat them as TASK_314C failures unless they become failing tests.

### Task 1: Backend Matrix/Fee Authority Regression Tests

**Files:**

- Modify: `tests/unit/test_project_folder_required_forms_service.py`
- Modify if needed: `tests/integration/test_project_folder_required_forms_api.py`

- [ ] **Step 1: Add a failing test for Required forms blocked by missing Confirmed Fee**

Add or strengthen a test that creates a valid active Confirmed Matrix context but no current Confirmed Fee authority, then asserts Required forms preview is blocked with an actionable Confirmed Fee blocker.

Expected assertion shape:

```python
assert preview.status == "blocked"
assert any("Confirmed Fee" in blocker for blocker in preview.blockers)
```

- [ ] **Step 2: Add or confirm Required forms blocked by missing/stale Confirmed Matrix**

If existing tests do not already cover this explicitly, add the smallest backend assertion that Required forms preview remains blocked when current Confirmed Matrix authority is missing or stale.

Expected assertion shape:

```python
assert preview.status == "blocked"
assert any("Confirmed Matrix" in blocker or "Matrix" in blocker for blocker in preview.blockers)
```

This test must not introduce Matrix Draft -> Fee Draft rebase behavior. It only proves Required forms does not proceed without current Matrix authority.

- [ ] **Step 3: Run the focused backend test**

Run:

```powershell
py -m pytest tests/unit/test_project_folder_required_forms_service.py -q
```

Expected during RED if missing: the new test fails because Required forms is not blocked clearly enough.

- [ ] **Step 4: Fix only if RED exposes a real gap**

If the test fails, update only the existing Required forms readiness logic in:

```text
backend/application/project_folder_required_forms_service.py
```

The fix must use existing Confirmed Fee read model data and must not create new authority state.

- [ ] **Step 5: Re-run focused backend tests**

Run:

```powershell
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
```

Expected: all pass.

### Task 2: Backend Current/Stale Authority Regression Tests

**Files:**

- Modify: `tests/unit/test_confirmed_fee_version_service.py`
- Modify: `tests/unit/test_project_folder_required_forms_service.py`

- [ ] **Step 1: Confirm stale Confirmed Fee remains stale after Matrix/Fee context changes**

Add or confirm a test that latest Confirmed Fee with old context reports stale when current Fee context changes.

Expected assertion shape:

```python
assert result.status == "stale"
```

- [ ] **Step 2: Confirm Required forms does not treat stale Confirmed Fee as ready**

Add or confirm Required forms preview blocks when Confirmed Fee exists but is stale.

Expected assertion shape:

```python
assert preview.status == "blocked"
assert any("Confirmed Fee" in blocker for blocker in preview.blockers)
```

- [ ] **Step 3: Run authority tests**

Run:

```powershell
py -m pytest tests/unit/test_confirmed_fee_version_service.py tests/integration/test_confirmed_fee_version_api.py tests/unit/test_project_folder_required_forms_service.py -q
```

Expected: pass after any required narrow fix.

### Task 3: Frontend Project Folder Task Order And Required Forms Gating

**Files:**

- Modify: `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
- Modify if needed: `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`

- [ ] **Step 1: Add or strengthen selector tests for task order**

Assert exact visible Project Folder order:

```typescript
expect(tasks.map((task) => task.title)).toEqual([
  "Local project folder",
  "Request material",
  "Confirmed Fee authority",
  "Required forms",
  "Application Form Section 2",
  "Submitted Material",
  "Public drive upload",
]);
```

- [ ] **Step 2: Add or strengthen Required forms gating test**

Assert Required forms is not ready when Confirmed Fee authority is missing or stale, even if Required forms preview data exists.

Expected assertion shape:

```typescript
expect(taskByTitle(tasks, "Required forms").status).not.toBe("ready");
expect(taskByTitle(tasks, "Required forms").actionTarget).toBeNull();
```

- [ ] **Step 3: Run selector tests**

Run:

```powershell
cd frontend
npm test -- --run projectFolderTaskSelectors --watch=false
```

Expected: pass after any required narrow fix.

### Task 4: Frontend Matrix/Fee Draft Gating Smoke Regression

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- Modify: `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`

- [ ] **Step 1: Confirm Matrix Editor tests still cover autosave/cancel/confirm gating**

Do not duplicate large Matrix Editor flows. Add only a missing assertion if current tests do not prove:

- confirm is blocked while draft is dirty/saving/error,
- cancel discard failure stays on the editor,
- confirm uses saved draft id/signature.

- [ ] **Step 2: Confirm Fee Evaluation tests still cover autosave/discard/confirm gating**

Do not duplicate large Fee flows. Add only a missing assertion if current tests do not prove:

- missing pricing draft gets seed save,
- Confirm Fee does not implicitly save,
- Back discard bounded-waits/aborts in-flight autosave,
- discard failure stays on the page.

- [ ] **Step 3: Run focused frontend tests**

Run:

```powershell
cd frontend
npm test -- MatrixEditorWorkspace FeeEvaluationReviewExportPage
```

Expected: pass. Existing non-failing React `act(...)` warnings in Fee tests may remain unless this task explicitly fixes them.

### Task 5: Static Shell Guards For Cross-Task Scope

**Files:**

- Modify: `tests/unit/test_frontend_shell_files.py`

- [ ] **Step 1: Add or strengthen static guards**

Add a TASK_314C static guard only if existing guards do not cover these strings and contracts:

- Project Folder UI must use `Project Folder`, not normal-flow `Package` / `Execute package`.
- Fee Evaluation normal flow must not expose `Save changes`.
- Matrix Editor / Fee Evaluation must keep autosave and discard routes wired.

Expected assertion shape:

```python
assert "Save changes" not in fee_page_source
assert "discardFeeEvaluationPricingDraft" in fee_page_source
assert "Project Folder" in project_workbench_source
assert "Execute package" not in project_workbench_source
```

- [ ] **Step 2: Run static guards**

Run:

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task314 or matrix_editor or fee or project_workbench or task320 or task321"
```

Expected: pass, except do not expand scope to unrelated historical failures.

### Task 6: Validation Matrix

Run the final TASK_314C validation set:

```powershell
py -m pytest tests/unit/test_matrix_editor_session_service.py tests/integration/test_matrix_editor_session_api.py tests/integration/test_confirmed_matrix_authority_api.py tests/integration/test_matrix_revision_flow_api.py -q
```

```powershell
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py tests/unit/test_confirmed_fee_version_service.py tests/integration/test_confirmed_fee_version_api.py -q
```

```powershell
py -m pytest tests/unit/test_official_project_folder_check_service.py tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
```

```powershell
cd frontend
npm test -- --run MatrixEditorWorkspace FeeEvaluationReviewExportPage projectFolderTaskSelectors ProjectFolderTaskList ProjectWorkbenchLayout --watch=false
```

```powershell
cd frontend
npm run build
```

Expected: all commands pass. Record pass counts in `docs/task_board.md`.

### Task 7: Task Board Update

**Files:**

- Modify: `docs/task_board.md`
- Modify: `tasks/TASK_314C_MATRIX_FEE_PROJECT_FOLDER_REGRESSION.md`

- [ ] **Step 1: Update TASK_314C status only after approved implementation**

Set:

```text
Status: Complete. Implemented after separate explicit user approval.
```

- [ ] **Step 2: Add validation summary to task board**

Add a concise bullet under the current TASK_314 section:

```text
TASK_314C_MATRIX_FEE_PROJECT_FOLDER_REGRESSION is complete. Added/confirmed linkage regression coverage for Matrix draft authority, Fee draft authority, Project Folder task order, and Required forms gating. Validation: <commands and pass counts>. Scope boundaries held: no TASK_315 rebase, no new Required forms behavior, no execution/reporting/AI/multi-user scope.
```

## Risk Register

| Risk | Mitigation |
| --- | --- |
| Regression task grows into feature work | Add tests first; only fix failing contracts directly tied to TASK_314A/B/318/320/321 linkage. |
| Broad production fix is needed | Stop and split a follow-up task if the fix touches files outside the approved narrow list or changes ProjectOutputRecord schema/semantics/API contracts. |
| Over-broad test suite creates noisy failures | Use focused command sets and record unrelated pre-existing failures separately. |
| Frontend async tests keep non-failing `act(...)` warnings | Do not treat warnings as failure unless the task explicitly scopes test hygiene cleanup. |
| Required forms gating duplicates backend and frontend logic differently | Keep backend as authority; frontend selector tests assert display/gating only. |
| TASK_314C accidentally becomes TASK_315 | Explicitly forbid Matrix Draft -> Fee Draft rebase and any rebase semantics in tests and implementation. |

## Acceptance Mapping

- Confirmed Matrix authority coherence: Tasks 1, 2, 4, 6.
- Confirmed Fee authority coherence: Tasks 1, 2, 4, 6.
- TASK_318 Official project folder check regression: Task 6.
- TASK_320 single-task Workbench UI regression: Tasks 3, 5, 6.
- TASK_321 Required forms generation regression: Tasks 1, 2, 3, 6.
- No new product scope: risk register and stop point.

## Self-Review

Spec coverage:

- The expected TASK_314C scope from umbrella task is covered: Confirmed Matrix/Fee authority behavior, TASK_318, TASK_320, TASK_321.
- TASK_315 rebase is explicitly out of scope.
- StepInstance/report/AI/multi-user scope is explicitly out of scope.

Placeholder scan:

- No unresolved TODO/TBD placeholders remain.
- Each validation step has an exact command.

Type consistency:

- Existing task names, route concepts, and test filenames match current repository names.
- The plan avoids inventing new DTOs or APIs.

## Stop Point

TASK_314C implementation is complete after validation and task board update.

Do not proceed to TASK_315, package execution, StepInstance, reporting, AI, permissions, or multi-user scope without separate explicit approval.
