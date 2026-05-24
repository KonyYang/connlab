# TASK_187 Plan - Project Workbench Document Pipeline Autofill

## 1. Execution Gate (Anti-Skip Protocol)

- Current phase: `Phase 11 - Project planning data foundation before downstream document automation`.
- Current active task ID: `TASK_187_PROJECT_WORKBENCH_DOCUMENT_PIPELINE_AUTOFILL` (approved by user on 2026-05-13).
- Why this task is allowed now:
  - `TASK_184` defined this as the next step after Matrix-first baseline.
  - `TASK_185` completed Workbench model/layout extraction.
  - `TASK_186` completed Matrix review surface and explicitly stopped before TASK_187.

## 2. Required Read Order Check

Completed in this turn:

1. `AGENTS.md`
2. `docs/task_board.md`
3. Task-chain sources containing TASK_187 constraints:
   - `tasks/TASK_184_PROJECT_WORKBENCH_MATRIX_FIRST_REDESIGN_BASELINE.md`
   - `tasks/TASK_185_PROJECT_WORKBENCH_STATE_MODEL_AND_LAYOUT_REFACTOR.md`
   - `tasks/TASK_186_PROJECT_WORKBENCH_MATRIX_REVIEW_SURFACE.md`
4. UI architecture constraints:
   - `docs/02_ARCHITECTURE_RULES.md`
   - `docs/frontend_architecture_rules.md`
5. Execution/checklist protocol:
   - `docs/project_management/TASK_EXECUTION_SKILL.md`
   - `docs/project_management/TASK_REVIEW_CHECKLIST.md`

Note:
- A dedicated `tasks/TASK_187_*.md` file is not present in repository yet.
- This plan is based on the declared TASK_187 scope in `TASK_184` and task board progression.

## 3. Task Understanding (Step 1)

1. Task goal:
   - Autofill downstream Workbench document pipeline inputs from known upstream outputs so operators do not manually paste paths in normal flow.

2. Input data:
   - Project/workbench context (`project_id`, project status, latest LTR).
   - Folder state from latest `ProjectFolderRecord`.
   - Matrix/TestPlan draft context (already loaded by TASK_186 model).
   - Existing generated/selected paths in Workbench state (Section 2 / test record / fee / approval package inputs).
   - Existing API payload contracts for approval package preview/execute and related stages.

3. Output data:
   - A deterministic frontend autofill state for downstream path fields.
   - UI-visible source markers (auto-filled vs manual override) where needed.
   - Existing backend APIs called with pre-filled values; no API contract break.

4. Modules involved:
   - Frontend only (React/TypeScript):
     - `frontend/src/features/project-workbench/*`
     - `frontend/src/components/workflow/ApprovalPackagePanel.tsx` (if prop model adjusted)
     - `frontend/src/api/client.ts` (only if DTO additions are required)
     - `frontend/src/workbench.css` (only if minimal state styles are needed)
   - Tests:
     - `tests/unit/test_frontend_shell_files.py`

5. Must not do:
   - No new backend endpoint.
   - No Office write behavior changes.
   - No persistence schema migration.
   - No scope jump to stale/version lifecycle (reserved for TASK_188).
   - No Matrix parser/data model changes.

## 4. Implementation Design (Step 2)

### 4.1 Data Structure Design

Add/extend a Workbench-level document path model in feature state:

- `DocumentPipelineState`
  - `applicationFormPath`: string | null
  - `testRecordPath`: string | null
  - `feeEvaluationPath`: string | null
  - `evidencePaths`: string[]
  - `sources`: metadata per field (`auto` | `manual`)
  - `autofillWarnings`: string[]

Add derived selectors:

- `deriveApprovalPackageInputsFromContext(modelState) -> approval input object`
- `deriveSection2InputsFromContext(modelState) -> section2 input object` (if applicable in current UI scope)
- `deriveRecordFeeInputsFromContext(modelState) -> generation input object` (only where UI already exposes these actions)

### 4.2 File-Level Change Plan

Planned files (expected):

1. `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
   - Add document pipeline autofill derivation and manual-override reconciliation.
   - Ensure existing manual input remains authoritative once operator edits a field.

2. `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
   - Wire new auto-filled values into stage panels in existing order.

3. `frontend/src/components/workflow/ApprovalPackagePanel.tsx` or feature wrapper
   - Accept and display auto-filled defaults without forcing manual input.
   - Keep correction mode via editable fields.

4. `frontend/src/features/project-workbench/ProjectWorkbenchEvidencePanel.tsx` (if needed)
   - Expose selected evidence as pipeline input source when already available.

5. `frontend/src/workbench.css` (optional, minimal)
   - Only small visual state cues for auto/manual source if required.

6. `tests/unit/test_frontend_shell_files.py`
   - Update static assertions for TASK_187 ownership boundaries and no direct route-page logic regression.

### 4.3 API / Function Signatures

No backend API changes planned.

Frontend signatures likely added/changed:

- `useProjectWorkbenchModel(...)` return shape extends with:
  - `documentPipeline`
  - `setManualDocumentPath(field, value)`
  - `resetDocumentPathToAuto(field)` (optional)

Approval package action functions should keep existing call signatures, with payload sourced from derived pipeline state.

### 4.4 Dependency Rules

- Keep dependency direction:
  - `pages -> features -> components/common`
  - API calls only through `frontend/src/api/client.ts`
- No direct file operations in frontend.
- No route-page business logic expansion; keep orchestration in feature model/selectors.

## 5. Risks And Mitigations

1. Risk: Auto-fill overwrites operator manual corrections.
   - Mitigation: field-level source flag (`manual` wins until explicit reset).

2. Risk: Missing upstream outputs causes false confidence.
   - Mitigation: explicit warning text and null-safe payload blocking where required.

3. Risk: Hidden coupling with approval-package required fields.
   - Mitigation: preserve existing backend preview/execute validation as final guard; frontend only pre-populates.

4. Risk: Scope creep into stale/version status.
   - Mitigation: no lifecycle freshness model persistence in TASK_187; only input autofill.

## 6. Validation Plan

1. Build:

```powershell
cd frontend
npm run build
```

2. Static boundary checks:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or approval or matrix"
```

3. Task-board guard run:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

4. Manual smoke (frontend):
   - Open a project with folder + matrix draft context.
   - Confirm approval-package paths are prefilled from known outputs.
   - Manually edit one path and confirm subsequent reload/update does not overwrite manual value.
   - Run preview and confirm backend blockers/warnings still authoritative.

## 7. Acceptance Criteria

- Workbench pre-fills document pipeline path inputs from existing project context in normal flow.
- Manual path entry remains available as correction mode.
- Existing API contracts and backend behavior remain unchanged.
- Route page remains thin; feature model owns derivation logic.
- Frontend build and targeted tests pass.

## 8. Explicit Out-of-Scope

- No new backend endpoints or schema changes.
- No automatic stale/version tagging UI model persistence (TASK_188).
- No report-generation, AI review, or non-MVP feature work.

## 9. Stop Condition

After this plan review:

- wait for your explicit approval of this plan;
- only then move to code implementation and tests for TASK_187.
