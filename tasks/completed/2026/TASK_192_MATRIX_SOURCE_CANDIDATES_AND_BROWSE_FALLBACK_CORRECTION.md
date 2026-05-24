# TASK_192 Matrix Source Candidates And Browse Fallback Correction

> Status: done  
> Created: 2026-05-14  
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 0. Execution Gate

- Current phase: `Phase 11`.
- Current prerequisite: `TASK_191_MATRIX_DRAFT_STARTER_IMPORT_AND_MANUAL_EMPTY_STATE` complete.
- Why this task is allowed next:
  - TASK_191 added a Matrix starter foundation but its import path is still path-first.
  - Real lab workflow should search the current Project's imported email attachments before asking the operator to browse external folders.
  - Matrix drafts created from imported attachments must preserve `source_asset_id` for traceability.

Implementation gate:

- This task file only defines scope.
- Do not implement code until a separate plan document is created and explicitly approved by the user.

---

## 1. Purpose

Correct the Matrix starter source-selection workflow so Project-owned source material is used first.

Target priority:

```text
Project imported email attachments / file_assets
  -> select candidate .docx specification or Matrix source
  -> preview selected candidate
  -> create Matrix draft with source_asset_id
  -> Browse external source folder fallback
  -> manual Matrix fallback
```

This is a correction to TASK_191's starter flow. It must not expand into PDF parsing, report generation, record import, image management, fee mapping, or historical reuse.

---

## 2. Required References

Follow:

- `docs/archive/task_artifacts/2026/task_191_acceptance_review_and_followup_recommendations.md`
- `docs/task_191_matrix_draft_starter_import_and_manual_empty_state_plan.md`
- `docs/matrix_test_plan_data_management_decisions.md`
- `docs/project_workbench_matrix_authority_workspace_target.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`

Frontend/UI work must follow the ConnLab `$impeccable` product UI rules.

---

## 3. In Scope

Backend/read model:

- Add a Project-scoped Matrix source candidate read model.
- Candidate sources must be derived from project `file_assets` first.
- Candidate selection should include at minimum:
  - `.docx` project file assets;
  - likely product specification or Matrix file names;
  - existing specification-like assets when role/type information is available;
  - supporting attachments that are Word documents.
- Add a read API such as:

```text
GET /api/projects/{project_id}/test-plan/source-candidates
```

- Candidate response should include:
  - `source_asset_id`;
  - `original_name`;
  - `extension`;
  - `asset_type`;
  - `candidate_kind`;
  - `reason`;
  - whether the stored file currently exists.

Preview/create flow:

- Allow preview from a selected project source candidate without requiring manual path entry.
- Reuse the existing `.docx` Matrix preview service.
- When draft is created from a candidate, persist `source_asset_id`.
- Preserve the existing external path preview as fallback.

Frontend:

- Matrix starter must list Project source candidates before external path/manual actions.
- Candidate interaction:
  - select candidate;
  - preview selected candidate;
  - create draft from preview.
- External source fallback:
  - provide a `Browse` action in the UI;
  - preserve path input fallback where native browse is unavailable;
  - make the native-browse limitation clear without exposing technical stack details.
- Manual Matrix remains available but should be visually secondary when source candidates exist.

Tests:

- Add backend unit/API tests for source candidate read model.
- Add or update frontend static tests for candidate-first starter wiring and `source_asset_id` draft creation.
- Preserve existing TASK_191 tests.

Documentation:

- Create a task plan document before implementation.
- Update `docs/task_board.md` after completion.

---

## 4. Out Of Scope

- No PDF parsing.
- No `.doc` parsing.
- No report generation.
- No filled record form import.
- No step image/evidence management.
- No fee price mapping.
- No historical project reuse.
- No AI review.
- No hard-coded public-drive path.
- No direct frontend filesystem access.
- No native desktop-shell implementation unless an existing safe file-picker bridge already exists.

---

## 5. UX Direction

The Matrix starter should communicate this hierarchy:

1. Use project source files already received from the request.
2. Browse external specification folder only when the received materials are insufficient.
3. Create a manual Matrix only when no usable source exists.

Target empty-state shape:

```text
Matrix source
  Candidate source files from this project
    [candidate rows]
    Preview selected source
    Create draft from preview

  External source fallback
    Browse...
    path fallback input

  Manual fallback
    Create manual Matrix
```

Avoid:

- making manual path entry the primary path;
- showing fake sample data;
- hiding source traceability;
- exposing backend-only IDs as the main user label.

---

## 6. Acceptance Criteria

- A draftless Project Workbench lists Matrix source candidates from Project file assets before external/manual actions.
- Candidate list includes at least `.docx` attachments already registered against the Project.
- Candidate preview reuses existing Matrix preview logic.
- Drafts created from project candidates persist `source_asset_id`.
- Existing path-based preview still works as fallback.
- Browse action exists for external source fallback; if native file picker is unavailable, the UI keeps a clear path-input fallback.
- Manual Matrix remains available as final fallback.
- No PDF/report/record/image/fee/history scope is added.
- Relevant backend, frontend, and task-board tests pass.

---

## 7. Validation Plan

Expected after implementation:

```powershell
python -m pytest tests\unit\test_matrix_source_candidate_service.py tests\integration\test_project_test_plan_source_candidates_api.py -q
```

```powershell
python -m pytest tests\integration\test_project_test_plan_preview_api.py tests\integration\test_project_test_plan_draft_api.py -q
```

```powershell
python -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix or task191 or task192"
```

```powershell
cd frontend
npm run build
```

Task-board guard:

```powershell
python -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

Manual smoke path:

1. Open a Project created from an email package that has `.docx` attachments.
2. Confirm Matrix starter lists Project source candidates.
3. Preview a selected `.docx` candidate.
4. Create a draft and confirm `source_asset_id` is persisted in draft response.
5. Open a Project without suitable candidates and confirm external Browse/path fallback is available.
6. Confirm manual Matrix is still available.

---

## 8. Recommended Coding Model

Recommended implementation model: `gpt-5.3-codex` with `high` reasoning.

Reason:

- This task crosses backend read models, Project file assets, source traceability, API contracts, Workbench state, and UI priority.
- The main risk is not UI appearance; it is preserving evidence lineage from imported email attachments to Matrix authority.
- `medium` is acceptable only if the task is split into backend candidate API first and frontend wiring later.

---

## 9. Stop Condition

Stop after TASK_192 is planned, approved, implemented, tested, and the task board is updated.

Do not proceed to group/step detail deepening, record form generation, record import, images, fee mapping, reports, or historical reuse in this task.
