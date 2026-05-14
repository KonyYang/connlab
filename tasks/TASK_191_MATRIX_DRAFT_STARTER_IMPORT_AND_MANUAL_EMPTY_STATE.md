# TASK_191 Matrix Draft Starter Import And Manual Empty State

> Status: proposed  
> Created: 2026-05-14  
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 0. Execution Gate

- Current phase: `Phase 11`.
- Current prerequisite: `TASK_190_MATRIX_OVERVIEW_CROSS_TABLE_AND_SUPPORTING_COMPACTNESS_CORRECTION` complete and accepted.
- Why this task is allowed next:
  - TASK_190 made Matrix the primary Workbench surface.
  - The current empty Matrix state has no operator entry point to import a Matrix or create a manual Matrix draft.
  - Real workflow requires the project owner to start Matrix planning from a source product specification, an existing Matrix file, or manual entry when no suitable source exists.

Implementation gate:

- This task file only defines scope.
- Do not implement code until a separate plan document is created and explicitly approved by the user.

---

## 1. Purpose

Add a controlled Matrix draft starter flow in Project Workbench so the Matrix workspace can appear and be used even when the project has no existing `ProjectTestPlanDraft`.

The task should support two first actions:

1. Import Matrix from a local `.docx` product specification path by reusing the existing Matrix preview API and draft persistence API.
2. Create a manual blank Matrix draft with explicit stable group identity so the engineer can begin editing from ConnLab.

This task exists to make the Matrix authority workspace operational. It is not a new parser expansion, record-import workflow, report generator, or file browser task.

---

## 2. Required References

Follow:

- `docs/matrix_test_plan_data_management_decisions.md`
- `docs/project_workbench_matrix_authority_workspace_target.md`
- `docs/task_190_matrix_overview_cross_table_and_supporting_compactness_correction_plan.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`

Frontend/UI work must follow the ConnLab `$impeccable` product UI rules.

---

## 3. In Scope

Frontend/API client:

- Add typed API client support for:
  - `POST /api/test-plan/matrix-preview-from-path`;
  - `POST /api/projects/{project_id}/test-plan/drafts`.
- Add an empty-state starter area inside the Matrix workspace, not as a separate toolbox panel.
- Provide two clear entry actions:
  - `Import from product specification`;
  - `Create manual Matrix`.
- For `.docx` import:
  - accept a local source document path as a controlled path input;
  - call the existing preview API;
  - show preview status, warnings, blockers, group count, and step count;
  - create a draft only after preview succeeds and the operator confirms;
  - reload the Workbench Matrix draft after creation.
- For manual creation:
  - create a draft with source metadata that clearly indicates manual origin;
  - include at least one explicit group identity such as `group_1` / `Group 1`;
  - let existing Matrix inspector/editor become the path for adding or editing steps.
- Keep user-facing copy operational and business-readable.
- Keep route pages thin; place workflow state and helpers under `frontend/src/features/project-workbench`.

Tests:

- Add or update frontend static tests for Matrix starter wiring and API client coverage.
- Reuse existing backend tests for preview and draft persistence where practical.

Documentation:

- Create a task plan document before implementation.
- Update `docs/task_board.md` after completion.

---

## 4. Out Of Scope

- No PDF parsing.
- No `.doc` parsing.
- No native Windows file picker.
- No automatic email attachment browser unless an existing source-material picker already exists and can be reused without expanding scope.
- No Office file write behavior.
- No report generation.
- No filled Word record form import.
- No test image/evidence management.
- No fee price mapping.
- No historical project reuse.
- No automatic sample/demo Matrix silently inserted as real project data.
- No backend schema migration unless the implementation proves existing draft metadata cannot represent manual origin cleanly.

---

## 5. UX Direction

The empty Matrix state should feel like the beginning of project planning, not an error.

Target shape:

```text
Matrix review
  Authority bar
  Empty starter:
    Import from product specification
      source path input
      preview button
      preview summary
      create draft button
    Create manual Matrix
      creates editable draft with Group 1
  After creation:
    Matrix cross-table appears
    Inspector becomes available for group/step edits
```

Rules:

- Keep Matrix as the main work area.
- Make source/manual origin explicit.
- Keep preview before persistence for file import.
- Do not show fake sample data as if it is project evidence.
- Do not place complex controls inside every Matrix cell.

---

## 6. Acceptance Criteria

- A project with no Matrix draft shows actionable Matrix starter controls in the Matrix workspace.
- Import from `.docx` source path can preview the Matrix and create a persisted Project test-plan draft through existing backend APIs.
- Manual starter creates a persisted draft with explicit stable group identity and opens the normal Matrix overview/inspector path.
- After draft creation, the Workbench reloads and the Matrix cross-table is visible.
- Preview blockers prevent draft creation from source import.
- User-facing copy distinguishes imported source evidence from manual Matrix origin.
- Existing authority/candidate semantics remain intact.
- No downstream output, report, PDF, image, or fee scope is added.
- Frontend build and targeted tests pass.

---

## 7. Validation Plan

Expected after implementation:

```powershell
cd frontend
npm run build
```

```powershell
python -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix or task191"
```

Backend regression scope:

```powershell
python -m pytest tests\integration\test_project_test_plan_preview_api.py tests\integration\test_project_test_plan_draft_api.py -q
```

Task-board guard:

```powershell
python -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

Manual smoke path:

1. Open an existing Project Workbench with no Matrix draft.
2. Confirm the Matrix starter actions are visible.
3. Paste a valid `.docx` product specification path and preview it.
4. Create a draft from the preview.
5. Confirm the Matrix overview appears.
6. Repeat on another project with manual Matrix creation and confirm `Group 1` is editable.

---

## 8. Recommended Coding Model

Recommended implementation model: `gpt-5.3-codex` with `high` reasoning.

Reason:

- The task crosses frontend API typing, Workbench model orchestration, Matrix empty-state UX, and existing backend contract reuse.
- The main risk is scope control: it must not accidentally become a file-browser, parser-expansion, or downstream document-generation task.
- `medium` is acceptable only if the implementation is limited to frontend API wiring and empty-state UI with no backend service changes.

---

## 9. Stop Condition

Stop after TASK_191 is planned, approved, implemented, tested, and the task board is updated.

Do not proceed to group record form generation, filled record import, image management, fee mapping, report generation, or historical reuse in this task.
