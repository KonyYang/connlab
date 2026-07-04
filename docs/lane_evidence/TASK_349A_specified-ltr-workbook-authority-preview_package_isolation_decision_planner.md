# TASK_349A Package-Isolation Decision Planner Evidence

> Task: `TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW`
> Lane: `specified-ltr-workbook-authority-preview`
> Role: Planner
> Status: package_isolation_required
> Created: 2026-07-04

---

## 1. Objective

Record the Planner decision after Integrator blocked TASK_349A packaging because candidate TASK_349A files contain mixed hunks/dependencies and cannot be staged safely as-is.

This Planner pass does not modify product code, does not stage, does not commit, and does not route Integrator.

---

## 2. Sources Re-Read

- `AGENTS.md`
- `docs/task_board.md`
- `tasks/TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW.md`
- `docs/task_349a_specified_ltr_workbook_authority_preview_plan.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_developer.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_qa.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_reconciliation_planner.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_package_reconciliation_planner.md`
- targeted `git status --short`
- targeted diffs for `backend/api/dependencies.py`, `frontend/src/pages/IntakeInboxPage.tsx`, `backend/application/ltr_duplicate_resolution_service.py`, and adjacent New Project files

---

## 3. Integrator Blocker Confirmed

Mixed backend candidate:

- `backend/api/dependencies.py` includes legitimate TASK_349A preview dependency injection.
- The same file also includes duplicate-resolution constructor arguments (`temporary_context_store`, `folder_store`) that depend on excluded `backend/application/ltr_duplicate_resolution_service.py` residuals.
- Staging only `dependencies.py` as-is would pull an excluded residual dependency into TASK_349A.

Mixed frontend candidate:

- `frontend/src/pages/IntakeInboxPage.tsx` includes legitimate TASK_349A preview wiring.
- The same file also depends on excluded adjacent New Project residuals:
  - moved `completionError` from `NewProjectApplicationEditor` to `NewProjectCompletionDock`
  - `buildNewProjectRequiredState(projectFields, ...)`
  - related imports/plumbing that require excluded New Project files
- Staging only TASK_349A candidate files as-is would create a non-self-contained package.

Therefore Integrator's blocker is valid: the previous package/scope reconciliation excluded residuals, but the current candidate hunks still depend on them.

---

## 4. Option Decision

Chosen route: Option A.

```text
Route Developer/package-isolation owner to split mixed hunks so TASK_349A becomes self-contained without adjacent residuals.
```

Why Option A:

- It preserves the approved TASK_349A business scope.
- It avoids silently absorbing adjacent residuals.
- It avoids reverting unknown or separately user-requested work in Planner.
- It gives Developer the right role boundary to edit product files narrowly and prove the package is self-contained.

Option B is not selected now:

- A separate adjacent lane may be needed later, but TASK_349A should first attempt package isolation because Developer triage said the adjacent diffs are not required for TASK_349A.

Option C is not selected:

- There is no strong TASK_349A-specific user/business authorization to expand this lane to duplicate-resolution summary, precheck/parser/selection, or adjacent New Project setup residual behavior.
- Any scope expansion would require Reviewer re-gate before packaging.

---

## 5. Developer Package-Isolation Rules

Developer package-isolation fix pass may:

- edit only TASK_349A candidate files and TASK_349A Developer evidence
- remove TASK_349A candidate-file dependencies on excluded residuals
- keep specified-LTR workbook authority preview behavior intact
- rerun focused TASK_349A validation after isolation
- update Developer evidence with exact files/hunks retained for the isolated package

Developer package-isolation fix pass must not:

- stage, commit, push, or package
- silently include adjacent residual files in TASK_349A
- broaden TASK_349A to duplicate-resolution summary, intake parser/selection, precheck UI, Basic Information, Settings/LTR helpers, release/packaging, or adjacent New Project setup work
- revert unknown user-requested adjacent work wholesale
- touch real workbook/public-drive data, real folders, schema/migrations, Workbench LTR update preview semantics, Matrix, Fee Evaluation, Folder Actions, Projects registry/list, `.agents/**`, or `docs/project_management/**`

If Developer cannot isolate TASK_349A without deleting or breaking adjacent user-requested behavior, Developer must stop and route back to Planner/User for a separate lane/owner decision.

---

## 6. Updated Source Of Truth

Updated files:

- `docs/task_board.md`
- `tasks/TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW.md`
- `docs/task_349a_specified_ltr_workbook_authority_preview_plan.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_package_isolation_decision_planner.md`

No product code was modified by this Planner pass.

---

## 7. Next Role Recommendation

Recommended next role:

```text
Developer package-isolation fix pass
```

After Developer updates evidence:

- Reviewer/QA re-gate should verify the isolated TASK_349A package is self-contained and contains no excluded residual dependencies.
- Integrator must not run packaging/readiness until Reviewer/QA re-gate passes.

---

## 8. Validation

Executed after decision writes:

- `git diff --check -- docs/task_board.md tasks/TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW.md docs/task_349a_specified_ltr_workbook_authority_preview_plan.md docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_package_isolation_decision_planner.md`: passed with existing LF/CRLF warning on `docs/task_board.md` only.
- `rg -n "[ \t]$" docs/task_board.md tasks/TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW.md docs/task_349a_specified_ltr_workbook_authority_preview_plan.md docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_package_isolation_decision_planner.md`: no matches.
- Targeted `git status --short -- docs/task_board.md tasks/TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW.md docs/task_349a_specified_ltr_workbook_authority_preview_plan.md docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_package_isolation_decision_planner.md frontend backend tests` shows this Planner pass changed TASK_349A docs/board/evidence only. The worktree still contains mixed TASK_349A product files and adjacent residuals; Developer package-isolation fix pass is required before re-gate/packaging.
- No backend, frontend, tests, API client, schema, workbook, public-drive, real-folder, `.agents/**`, or `docs/project_management/**` files were modified by this Planner pass.

Planner decision gate: package_isolation_required.
