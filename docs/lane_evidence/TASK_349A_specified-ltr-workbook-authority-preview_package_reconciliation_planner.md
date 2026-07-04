# TASK_349A Package/Scope Reconciliation Planner Evidence

> Task: `TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW`
> Lane: `specified-ltr-workbook-authority-preview`
> Role: Planner
> Status: package_scope_reconciled
> Created: 2026-07-04

---

## 1. Objective

Resolve QA B1 package/evidence scope mismatch without changing product code.

QA B1 summary:

- TASK_349A functional validation passed.
- QA blocked package readiness because actual product diff includes adjacent intake/precheck/parser/duplicate-summary/New Project files outside the clearly recorded TASK_349A Developer evidence package.
- Developer triage says the adjacent diffs are not required for TASK_349A and cannot be safely reverted inside TASK_349A because they may be pre-existing or separately user-requested.

This Planner pass only updates source-of-truth docs/evidence and does not route QA/Integrator.

---

## 2. Sources Re-Read

- `AGENTS.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `docs/task_board.md`
- `tasks/TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW.md`
- `docs/task_349a_specified_ltr_workbook_authority_preview_plan.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_planner.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_developer.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_qa.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_reconciliation_planner.md`
- targeted `git status --short`
- targeted `git diff --stat` for QA B1 files

---

## 3. B1 Adjacent Diffs Observed

Targeted status/stat confirmed dirty adjacent files including:

- `backend/application/intake_form_selection_service.py`
- `backend/modules/intake/application_form_parser.py`
- `tests/unit/test_application_form_parser.py`
- `tests/unit/test_intake_form_selection_service.py`
- `frontend/src/features/precheck/PrecheckFieldGrid.tsx`
- `frontend/src/features/precheck/precheckReviewSelectors.ts`
- `frontend/src/intake-case-review.css`
- `backend/application/ltr_duplicate_resolution_service.py`
- `frontend/src/features/new-project/LocalLtrDuplicateConflictPanel.tsx`
- `frontend/src/features/new-project/LocalLtrDuplicateConflictPanel.test.tsx`
- `frontend/src/features/new-project/NewProjectApplicationEditor.tsx`
- `frontend/src/features/new-project/NewProjectCompletionDock.tsx`
- `frontend/src/features/new-project/NewProjectCompletionDock.test.tsx`
- `frontend/src/features/new-project/newProjectRequiredState.ts`
- `frontend/src/features/new-project/newProjectRequiredState.test.ts`

Targeted `git diff --stat` showed those adjacent tracked files include `456 insertions` and `106 deletions` across 14 tracked files, plus an untracked New Project required-state test.

---

## 4. Planner Decision

Decision: exclude the B1 adjacent diffs as external residuals.

Rationale:

- TASK_349A's approved product purpose is specified-LTR workbook authority preview before New Project Apply LTR completion.
- Developer triage explicitly records that the adjacent files are not required for workbook-first preview, read-only workbook access, preview acknowledgement verification, not-found blocking, or preview-confirm-to-completion handoff.
- There is no clear TASK_349A user/Reviewer authorization to silently fold intake parser/selection, precheck UI, duplicate summary, or adjacent New Project setup/local-duplicate residuals into this lane.
- Planner must not revert unknown or separately user-requested product work.

Therefore:

- Do not expand TASK_349A May Touch/package scope to include the B1 adjacent residuals.
- Do not package those residuals with TASK_349A.
- If those adjacent changes are desired, create or route a separate approved lane/owner, or perform a separate explicit scope reconciliation outside TASK_349A.

---

## 5. TASK_349A Package Boundary

TASK_349A package may include only:

- `backend/application/specified_ltr_workbook_authority_preview_service.py`
- `backend/application/new_project_completion_service.py`
- `backend/api/routes_new_project_completion.py`
- `backend/api/dependencies.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/new-project/useNewProjectCompletion.ts`
- `frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/intake-inbox.css`
- `tests/unit/test_specified_ltr_workbook_authority_preview_service.py`
- `tests/integration/test_new_project_completion_api.py`
- `frontend/src/pages/IntakeInboxPage.test.tsx`
- TASK_349A task/plan/evidence/board docs

TASK_349A package must not include:

- `backend/application/intake_form_selection_service.py`
- `backend/modules/intake/application_form_parser.py`
- `tests/unit/test_application_form_parser.py`
- `tests/unit/test_intake_form_selection_service.py`
- `frontend/src/features/precheck/PrecheckFieldGrid.tsx`
- `frontend/src/features/precheck/precheckReviewSelectors.ts`
- `frontend/src/intake-case-review.css`
- `backend/application/ltr_duplicate_resolution_service.py`
- adjacent New Project local-duplicate/setup files omitted from Developer evidence section 2
- Basic Information residuals
- Settings/LTR helper residuals
- release/packaging/desktop residuals
- `.agents/**`
- `docs/project_management/**`
- `temp_agents_stash.md`

---

## 6. Updated Source Of Truth

Updated files:

- `docs/task_board.md`
- `tasks/TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW.md`
- `docs/task_349a_specified_ltr_workbook_authority_preview_plan.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_package_reconciliation_planner.md`

No product code was modified by this Planner pass.

---

## 7. Next Role Recommendation

Recommended next role:

- Reviewer/QA re-gate only if they can verify package isolation against the file list above.

If package isolation cannot be verified because adjacent residuals remain mixed in the candidate package:

- route to User/Planner for a separate lane/owner decision, or
- route to the appropriate role to isolate/stage/package only TASK_349A-approved files without reverting unknown user work.

Do not route Integrator acceptance until package isolation is confirmed.

---

## 8. Validation

Executed after reconciliation writes:

- `git diff --check -- docs/task_board.md tasks/TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW.md docs/task_349a_specified_ltr_workbook_authority_preview_plan.md docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_package_reconciliation_planner.md`: passed with existing LF/CRLF warning on `docs/task_board.md` only.
- `rg -n "[ \t]$" docs/task_board.md tasks/TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW.md docs/task_349a_specified_ltr_workbook_authority_preview_plan.md docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_package_reconciliation_planner.md`: no matches.
- Targeted `git status --short -- docs/task_board.md tasks/TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW.md docs/task_349a_specified_ltr_workbook_authority_preview_plan.md docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_package_reconciliation_planner.md frontend backend tests` shows this Planner pass changed TASK_349A docs/board/evidence only. The worktree still contains both TASK_349A product files and the QA B1 adjacent residuals; those residuals are explicitly excluded by this reconciliation and must not be packaged with TASK_349A.
- No backend, frontend, tests, API client, schema, workbook, public-drive, real-folder, `.agents/**`, or `docs/project_management/**` files were modified by this Planner pass.

Planner package reconciliation gate: package_scope_reconciled.
