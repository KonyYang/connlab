# TASK_189 Matrix Authority Read Model And Group Identity Correction

> Status: proposed
> Created: 2026-05-14
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 0. Execution Gate

- Current phase: `Phase 11`.
- Current prerequisite: `TASK_189_MATRIX_EDIT_FREEZE_AUTHORITY_SEMANTICS_CORRECTION` implemented and reviewed as partially accepted.
- Why this task is allowed:
  - Acceptance review confirmed remaining semantic gaps in read model and identity validation.
  - This is a bounded correction task for TASK_189 behavior consistency, not a new feature task.

Implementation gate:

- Do not implement code until a dedicated correction plan is reviewed and explicitly approved by the user.

---

## 1. Purpose

Close the remaining TASK_189 semantic gaps:

1. Active authority read model must track latest `reviewed` draft, not latest non-superseded candidate.
2. Group identity must be a confirm blocker when missing.

---

## 2. In Scope

Backend:

- Correct active draft selection in output status summary to use reviewed authority only.
- Correct active draft selection logic used by Workbench draft loading context where needed.
- Enforce missing explicit stable group identity as blocker in Matrix confirm validation.

Frontend:

- Distinguish authority (`reviewed`) versus editable candidate (`draft`) in Workbench model read flow.

Tests:

- Add/adjust tests for reviewed v1 + candidate v2 coexistence:
  - before candidate confirm, active authority remains v1
  - after confirm, active authority becomes v2
- Add/adjust tests for missing group identity blocker.

---

## 3. Out Of Scope

- No endpoint shape redesign.
- No new Matrix editing UI surfaces.
- No output ledger schema migration.
- No TASK_190 scope.

---

## 4. Acceptance Criteria

- Output ledger status summary chooses latest reviewed draft as active authority.
- Workbench does not treat unconfirmed candidate as authority for stale checks.
- Missing explicit stable group identity is returned as blocker and prevents confirm.
- Tests explicitly lock these semantics.

---

## 5. Validation Baseline

```powershell
python -m pytest tests\unit\test_project_output_record_service.py tests\unit\test_project_test_plan_matrix_edit_service.py tests\integration\test_project_test_plan_matrix_edit_api.py -q
```

```powershell
python -m pytest tests\integration\test_project_output_records_api.py -q
```

```powershell
python -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix or task188"
```

```powershell
python -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

---

## 6. Stop Condition

Stop after this correction task is implemented, verified, and board-synced. Do not advance to next feature task in the same turn.
