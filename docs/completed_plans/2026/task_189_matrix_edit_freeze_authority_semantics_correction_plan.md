# TASK_189 Correction Plan: Matrix Edit/Freeze Authority Semantics

> Task: `TASK_189_MATRIX_EDIT_FREEZE_AUTHORITY_SEMANTICS_CORRECTION`  
> Status: plan proposed (implementation not started)  
> Date: 2026-05-14

---

## 1) Execution Context

- Current phase: `Phase 11 - Project planning data foundation before downstream document automation`
- Current active task on board: `none; TASK_189 acceptance mismatch confirmed, pending user approval for TASK_189_MATRIX_EDIT_FREEZE_AUTHORITY_SEMANTICS_CORRECTION`
- Why this task is allowed now: user-approved acceptance review found a confirmed semantic mismatch in TASK_189 behavior and requested controlled correction before any next feature task.

---

## 2) Problem Statement

Acceptance review confirmed three mismatches against approved TASK_189 semantics:

1. Editing a `reviewed` draft currently supersedes the old reviewed authority immediately.
2. Existing unit tests encode this incorrect behavior, so passing tests are not acceptance evidence.
3. Confirm validation severity is stricter than approved (method/requirement treated as blockers instead of warnings).

Target: align runtime behavior + tests + board wording with approved semantics.

---

## 3) Scope

### In Scope

- Correct authority lifecycle in Matrix edit/confirm service.
- Correct blocker/warning classification for confirm validation.
- Update unit/integration tests to enforce corrected semantics.
- Keep API route shape unchanged.
- Keep persistence model unchanged (no schema migration in this correction).

### Out of Scope

- No new endpoints.
- No UI architecture expansion.
- No output-ledger redesign.
- No new matrix import sources.
- No TASK_190+ functionality.

---

## 4) Design Decisions

### A. Authority lifecycle correction

When editing a `reviewed` draft:

- Create a new candidate draft for edits.
- Do **not** supersede current reviewed authority at edit time.
- Keep old reviewed draft as authority until candidate confirm succeeds.

On confirm candidate success:

- Candidate transitions to `reviewed`.
- Previous reviewed authority transitions to `superseded`.

Implementation approach:

- Avoid direct use of draft service `create_draft()` path that auto-supersedes active same-source drafts.
- In matrix edit service, create candidate draft through repository-level create path with explicit version assignment, or equivalent service-safe path that preserves old reviewed status.
- In confirm flow, supersede old reviewed explicitly after candidate review success.

### B. Validation severity correction

For confirm:

- Blockers: group identity issues, invalid token/no numeric token, sequence start/duplicate/gap, missing `test_item`.
- Warnings: missing `method`, `condition`, `requirement` (`judgement_criteria`), duration-related, source trace, step description.

---

## 5) File-Level Change Plan

Primary backend:

- `backend/application/project_test_plan_matrix_edit_service.py`
  - Refactor reviewed-edit candidate creation path to preserve old reviewed authority.
  - Adjust confirm flow to supersede previous reviewed only after successful candidate confirm.
  - Reclassify validation outputs (blocker/warning).

Potential backend helper wiring (only if strictly needed for clean layering):

- `backend/application/project_test_plan_draft_service.py`
  - Add a narrowly-scoped helper command/path if needed to create a candidate draft without auto-supersede.
  - Keep existing behaviors for other tasks unchanged.

Tests:

- `tests/unit/test_project_test_plan_matrix_edit_service.py`
  - Replace “edit reviewed => superseded” assertion.
  - Add assertion: old reviewed remains reviewed before candidate confirm.
  - Add assertion: old reviewed supersedes only after confirm success.
  - Add blocker/warning severity assertions.

- `tests/integration/test_project_test_plan_matrix_edit_api.py`
  - Ensure API-level behavior matches corrected authority lifecycle.
  - Ensure confirm rejects only true blockers; warning-only cases can confirm.

- `tests/unit/test_matrix_step_sequence_validation.py`
  - Keep parser continuity coverage and extend only if needed for corrected invalid-token handling expectations.

Board guard tests (string allowlist sync only if board status wording changes):

- `tests/unit/test_phase10a_scope_activation.py`
- `tests/unit/test_phase5_ux_decision.py`
- `tests/unit/test_phase6_scope_activation.py`
- `tests/unit/test_phase7_validation_summary.py`
- `tests/unit/test_phase9_scope_activation.py`

Task board sync:

- `docs/task_board.md`
  - Update correction status/validation summary after implementation and tests pass.

---

## 6) Risks and Mitigations

1. **Risk:** breaking existing TASK_175 draft semantics for unrelated paths.  
   **Mitigation:** keep changes isolated to matrix edit service flow; do not modify default draft lifecycle behavior globally unless strictly required.

2. **Risk:** candidate version collisions with manual version assignment.  
   **Mitigation:** derive next version from same-source draft max version within transaction/session, matching current sequence logic.

3. **Risk:** warning-only confirm might allow poor data quality.  
   **Mitigation:** keep warnings visible and returned consistently; confirm gate still blocks structural/data-integrity failures.

4. **Risk:** board guard tests fail due to status string drift.  
   **Mitigation:** update allowlist assertions in same turn as board wording update.

---

## 7) Validation Plan

Run in this order:

```powershell
python -m pytest tests\unit\test_project_test_plan_matrix_edit_service.py -q
```

```powershell
python -m pytest tests\integration\test_project_test_plan_matrix_edit_api.py -q
```

```powershell
python -m pytest tests\unit\test_matrix_step_sequence_validation.py -q
```

```powershell
python -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

Optional confidence check (if requested):

```powershell
npm run build
```

---

## 8) Completion Criteria

This correction is complete only when all are true:

- Reviewed-edit no longer supersedes old reviewed authority immediately.
- Confirm candidate supersedes old reviewed authority only on successful confirm.
- Validation severity matches approved blocker/warning split.
- Unit + integration tests explicitly enforce corrected semantics and pass.
- `docs/task_board.md` updated with correction completion notes and validation summary.

