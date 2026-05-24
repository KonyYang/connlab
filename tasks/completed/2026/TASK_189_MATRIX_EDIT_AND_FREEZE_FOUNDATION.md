# TASK_189 Matrix Edit And Freeze Foundation

> Status: proposed
> Created: 2026-05-14
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 0. Execution Gate

- Current phase: `Phase 11`.
- Current board prerequisite: `TASK_188_PROJECT_OUTPUT_VERSION_LEDGER_CORRECTION` complete.
- Why this task is allowed next:
  - Project Workbench already has Matrix review display.
  - Downstream output freshness now has a persistent ledger foundation.
  - The next business requirement is to let the project owner correct and confirm the Matrix/TestPlan authority before generating or refreshing downstream documents.

Implementation gate:

- This task file only defines scope.
- Do not implement code until a separate plan document is created and explicitly approved by the user.

---

## 1. Purpose

Add the first controlled Matrix editing and freeze/confirm foundation for Project Workbench.

The goal is not to build a giant spreadsheet editor. The goal is to let the project owner edit structured Matrix group/step data, validate it, and freeze/confirm the current Matrix draft as the Project test-plan authority.

---

## 2. Business Context

Real lab Matrix sources may be:

- product specification tables in Word;
- existing Excel Matrix files;
- manually created project Matrix data.

The original file is evidence. The confirmed ConnLab Matrix/TestPlan draft is the project plan authority.

Downstream files such as Section 2, test record forms, fee evaluation, approval package, and future reports should follow the latest confirmed Matrix.

---

## 3. In Scope

Backend:

- Provide a controlled way to edit ProjectTestPlanDraft payload at group/step level.
- Validate Matrix step token parsing and step sequence continuity before freeze/confirm.
- Support freeze/confirm of a Matrix draft as the current project authority.
- When a draft is confirmed or revised, rely on the output ledger to mark downstream outputs stale where appropriate.

Frontend:

- Add a Workbench Matrix editing entry point.
- Provide group/step editing UI using a detail panel, not a giant editable Matrix table.
- Show validation blockers before freeze/confirm.
- Keep Matrix overview readable and use group/step detail for complex edits.

Tests:

- Unit tests for step token parsing and continuity validation.
- Unit tests for Matrix draft edit/freeze application service.
- Integration tests for Matrix edit/freeze API.
- Frontend static tests to keep Workbench route thin and editing logic inside feature boundaries.

---

## 4. Out Of Scope

- No Word/Excel Matrix import expansion beyond existing parsed draft payloads.
- No test record form generation.
- No filled record form import.
- No step image/evidence management.
- No fee price mapping overhaul.
- No report generation.
- No AI review.
- No historical project reuse UI.
- No multi-user approval/permission workflow.

---

## 5. Required Decisions To Follow

Follow:

- `docs/matrix_test_plan_data_management_decisions.md`
- `docs/task_188_project_workbench_version_and_stale_status_plan.md`
- `docs/task_188_project_output_version_ledger_correction_plan.md`

Key rules:

```text
Original spec / Word Matrix / Excel Matrix = source evidence
ConnLab confirmed ProjectTestPlanDraft = project plan authority
Generated Word / Excel / PDF files = output artifacts
Imported test results/images = project execution evidence
```

Matrix must remain Matrix-first but not spreadsheet-heavy. Complex operations belong to group/step detail panels.

---

## 6. Matrix Step Rules

Step token parsing:

- comma, whitespace, and newline are separators;
- each token creates one step;
- leading digits become `step_sequence`;
- trailing non-digits are retained as `suffix_note`;
- sorting and validation use `step_sequence`.

Examples:

```text
3(a) -> step_sequence 3, suffix_note "(a)"
4(b) -> step_sequence 4, suffix_note "(b)"
```

Freeze blockers:

- group does not start at step 1;
- duplicate step number inside one group;
- missing step number gap inside one group;
- required step fields missing for confirmed authority state.

Repeated test items:

- same test item may appear multiple times inside a group;
- each occurrence is a separate step;
- stable identity is group + step sequence, not test item name.

---

## 7. Suggested Data Shape

The existing `ProjectTestPlanDraft.payload_json` may be used as the persistence carrier for this task if that keeps scope smaller.

The editable payload should normalize toward:

```text
groups[]
  group_number
  sample_size
  steps[]
    sequence
    raw_token
    suffix_note
    test_item
    section
    method
    condition
    requirement
    step_description
    duration_value
    duration_unit
    source_trace
    note
```

Do not introduce separate group/step tables in TASK_189 unless the plan proves the existing draft payload cannot safely support the task.

---

## 8. Expected API Shape

Candidate endpoints for the plan stage to validate:

```text
PUT  /api/projects/{project_id}/test-plan/drafts/{draft_id}/matrix
POST /api/projects/{project_id}/test-plan/drafts/{draft_id}/matrix/validate
POST /api/projects/{project_id}/test-plan/drafts/{draft_id}/matrix/confirm
```

The exact route design must be finalized in the TASK_189 plan document after reading current backend routes.

---

## 9. UX Direction

Workbench should show:

- Matrix overview as the first work surface.
- Edit action for the active draft.
- Group selector/detail panel.
- Step rows inside the selected group.
- Freeze/confirm action only after validation passes.
- Validation blockers in business-readable language.

Avoid:

- editable giant spreadsheet UI;
- per-cell complex action buttons;
- future-scope report/AI/history actions;
- route page state growth.

---

## 10. Validation Plan

Expected after implementation:

```powershell
py -m pytest tests\unit\test_matrix_step_sequence_validation.py tests\unit\test_project_test_plan_matrix_edit_service.py -q
```

```powershell
py -m pytest tests\integration\test_project_test_plan_matrix_edit_api.py -q
```

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix"
```

Task-board guard:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

---

## 11. Acceptance Criteria

- Project owner can edit Matrix group/step data for an active draft.
- Step token parsing preserves suffix notes and validates numeric sequence.
- Freeze/confirm is blocked by missing, duplicated, or non-continuous step numbers.
- Confirmed Matrix draft is treated as the Project test-plan authority.
- Downstream output ledger remains the mechanism for current/stale state.
- Workbench stays Matrix-first without becoming a giant spreadsheet.
- No downstream document generation, record import, image management, fee overhaul, report generation, or AI scope is added.

---

## 12. Recommended Coding Model

Recommended implementation model: `gpt-5.3-codex` with `high` reasoning.

Reason:

- This task crosses backend validation, application service design, typed API, and frontend Workbench UX.
- The highest risk is not code volume, but preserving boundaries while introducing editable Matrix authority semantics.
- `medium` is acceptable for the plan document or small follow-up fixes, but `high` is the safer default for the first implementation pass.

---

## 13. Stop Condition

Stop after TASK_189 is implemented, tested, and the task board is updated.

Do not proceed to record form generation, record import, image management, fee mapping, report generation, or historical reuse in this task.
