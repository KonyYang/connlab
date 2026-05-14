# TASK_190 Matrix Overview Cross Table And Supporting Compactness Correction

> Status: proposed  
> Created: 2026-05-14  
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 0. Execution Gate

- Current phase: `Phase 11`.
- Current prerequisite: `TASK_190_PROJECT_WORKBENCH_MATRIX_AUTHORITY_WORKSPACE` implemented and reviewed as partially accepted.
- Why this correction task is allowed:
  - Acceptance review confirmed TASK_190 direction is correct but not fully aligned with target.
  - This is a bounded correction for TASK_190 scope, not a new feature task.

Implementation gate:

- Do not implement code until a dedicated correction plan is reviewed and explicitly approved by the user.

---

## 1. Purpose

Close remaining TASK_190 acceptance gaps:

1. Matrix overview must be a cross-table surface (technical columns + group columns + step-token cells), not a flattened step list.
2. Supporting workflows must be compact by default (collapsed/entry-first), not expanded large panels on first screen.
3. Matrix review surface should be split into maintainable feature components.

---

## 2. In Scope

Frontend:

- Rework Matrix overview into cross-table view:
  - left technical columns (`test item`, `method`, `condition`, `requirement`, optional context);
  - right dynamic group columns (`Group 1`, `Group 2`, ...);
  - cell content as step tokens.
- Keep group/step edit path reachable through inspector/editor flow.
- Make supporting workflows compact by default:
  - approval package, folder, evidence, lookup should be entry-first and collapsed by default where practical.
- Split oversized Matrix panel into smaller feature components.

Tests:

- Update frontend static tests for:
  - cross-table overview wiring;
  - supporting-workflow compactness defaults;
  - matrix component split boundaries.
- Run frontend build and targeted static checks.

Documentation:

- Provide correction plan before implementation.
- Update `docs/task_board.md` after correction is implemented and validated.

---

## 3. Out Of Scope

- No backend schema/API change.
- No new Matrix import source.
- No test-result import flow.
- No step image management.
- No fee mapping redesign.
- No report generation.
- No AI review.
- No historical project reuse.

---

## 4. Acceptance Criteria

- Matrix overview is rendered as cross-table (left technical columns + group columns + token cells).
- Supporting workflows no longer dominate first viewport and default to compact/collapsed entry points.
- Matrix workspace remains primary visual and structural surface.
- Matrix feature code is split into smaller components (authority bar, overview, inspector/editor at minimum).
- Existing downstream actions remain reachable.
- Frontend build and targeted static tests pass.

---

## 5. Validation Baseline

```powershell
cd frontend
npm run build
```

```powershell
python -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix or task190"
```

```powershell
python -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

---

## 6. Stop Condition

Stop after this correction task is planned, approved, implemented, validated, and board-synced.

Do not advance to TASK_191 or later tasks in the same turn.
