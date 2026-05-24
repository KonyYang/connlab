# TASK_190 Project Workbench Matrix Authority Workspace

> Status: proposed  
> Created: 2026-05-14  
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 0. Execution Gate

- Current phase: `Phase 11`.
- Current prerequisite: `TASK_189_MATRIX_AUTHORITY_READ_MODEL_AND_GROUP_IDENTITY_CORRECTION` complete.
- Why this task is allowed next:
  - TASK_189 establishes Matrix authority/candidate semantics.
  - The current Workbench UI still displays many unrelated downstream tools as large first-screen panels.
  - The agreed product direction is Matrix-first: the confirmed Matrix authority should become the primary Project work surface.

Implementation gate:

- This task file only defines scope.
- Do not implement code until a separate plan document is created and explicitly approved by the user.

---

## 1. Purpose

Refactor Project Workbench information architecture so Matrix authority becomes the primary workspace.

The goal is not to add new Matrix business capability. The goal is to reshape the existing Workbench around:

- confirmed Matrix authority;
- editable candidate draft when present;
- Matrix overview;
- selected group/step detail;
- compact downstream output status.

---

## 2. Required References

Follow:

- `docs/project_workbench_matrix_authority_workspace_target.md`
- `docs/matrix_test_plan_data_management_decisions.md`
- `docs/task_189_matrix_authority_read_model_and_group_identity_correction_plan.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`

Frontend/UI work must follow the ConnLab `$impeccable` product UI rules.

---

## 3. In Scope

Frontend:

- Reshape Project Workbench layout so Matrix occupies the primary work area.
- Show Matrix authority and candidate state clearly.
- Keep or introduce a Matrix overview surface that can display test items, technical columns, group columns, and step tokens.
- Move complex group/step details into a focused inspector/detail panel.
- Convert Section 2, test record, fee evaluation, approval package, and evidence placement into compact downstream status/entry points.
- Preserve existing feature-level model boundaries; do not grow route-page state.

Tests:

- Update frontend static tests to enforce Matrix-first Workbench wiring.
- Keep route page thin and feature logic inside `frontend/src/features/project-workbench`.
- Run frontend build.

Documentation:

- Create a task plan document before implementation.
- Update `docs/task_board.md` after completion.

---

## 4. Out Of Scope

- No backend schema changes.
- No new Matrix import source.
- No new record form generation behavior.
- No filled record form import.
- No step image/evidence management.
- No fee price mapping overhaul.
- No report generation.
- No AI review.
- No historical project reuse.
- No new output ledger semantics.

---

## 5. UX Direction

The Workbench first screen should prioritize:

1. Project header and authority status.
2. Matrix authority bar.
3. Matrix overview as the main work surface.
4. Group/step inspector for editing and validation context.
5. Compact downstream output strip.

Current large panels for project folder, approval package, evidence placement, and read-only lookup should be demoted, collapsed, or moved behind stage entry points where possible.

Target mental model:

```text
Project -> Matrix authority -> group/step planning -> downstream outputs
```

Avoid:

- a toolbox page full of unrelated buttons;
- giant editable spreadsheet behavior;
- new future-scope actions;
- route-page state growth;
- UI copy that exposes backend terms unnecessarily.

---

## 6. Acceptance Criteria

- Matrix is visually and structurally the primary Workbench work surface.
- Authority and candidate draft states are distinguishable.
- Downstream outputs remain visible but no longer dominate the first screen.
- Existing project folder, approval package, evidence, lookup, and output status flows remain reachable.
- Workbench route remains thin and feature-level boundaries are preserved.
- No new backend business scope is added.
- Frontend build and targeted static tests pass.

---

## 7. Validation Plan

Expected after implementation:

```powershell
cd frontend
npm run build
```

```powershell
python -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix or task190"
```

Task-board guard:

```powershell
python -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

---

## 8. Recommended Coding Model

Recommended implementation model: `gpt-5.3-codex` with `high` reasoning.

Reason:

- This is primarily a frontend architecture and UX information-architecture task.
- The risk is not backend complexity, but preserving existing behavior while changing page structure and visual priority.
- The task requires careful boundary control so Project Workbench does not become a larger route-level component.

---

## 9. Stop Condition

Stop after TASK_190 is planned, implemented, tested, and the task board is updated.

Do not proceed to test record import, image management, fee mapping, report generation, or historical reuse in this task.
