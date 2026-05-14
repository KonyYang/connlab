# TASK_191 Matrix Draft Starter Import And Manual Empty State Plan

> Status: proposed for review  
> Created: 2026-05-14  
> Task: `TASK_191_MATRIX_DRAFT_STARTER_IMPORT_AND_MANUAL_EMPTY_STATE`  
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 1. Execution Protocol

- Current phase: `Phase 11`.
- Current active task: `TASK_191_MATRIX_DRAFT_STARTER_IMPORT_AND_MANUAL_EMPTY_STATE`.
- Why this task is allowed now:
  - TASK_190 correction is complete and accepted.
  - `docs/task_board.md` has no active implementation task.
  - The current Workbench Matrix area is correctly prioritized but cannot be started when no draft exists.

This document is the required plan artifact. Implementation must wait for explicit user approval.

---

## 2. Problem Summary

The Workbench now treats Matrix as the primary project planning workspace, but a new or migrated project with no `ProjectTestPlanDraft` still shows an empty message:

```text
No active Project test-plan draft is available yet.
```

That is technically accurate but operationally incomplete. The real lab workflow after LTR registration is:

1. Find the product specification or Matrix in the requester email attachments.
2. Import the Matrix when a suitable Word specification is available.
3. Create the Matrix manually when no suitable specification exists.
4. Review/edit/freeze the Matrix before downstream documents.

TASK_191 should add that starter path without changing downstream scope.

---

## 3. Existing Capabilities To Reuse

Backend already provides:

- `POST /api/test-plan/matrix-preview-from-path`
  - `.docx` Matrix preview from local source path;
  - returns groups, steps, warnings, blockers, source metadata.
- `POST /api/projects/{project_id}/test-plan/drafts`
  - persists a Project-scoped `ProjectTestPlanDraft`.
- `GET /api/projects/{project_id}/test-plan/drafts`
  - lists drafts used by Workbench model loading.
- Matrix edit/validate/confirm APIs from TASK_189.

Frontend already provides:

- Matrix authority/candidate read model in `useProjectWorkbenchModel`.
- Matrix overview cross-table in `ProjectWorkbenchMatrixOverview`.
- Matrix inspector/editor in `ProjectWorkbenchMatrixInspector`.
- Matrix review container in `ProjectWorkbenchMatrixReviewPanel`.

Therefore the implementation should reuse existing backend contracts first.

---

## 4. Proposed Scope

### 4.1 API Client

Update `frontend/src/api/client.ts` with typed functions and DTOs:

- `previewProjectTestPlanMatrixFromPath(input)`
- `createProjectTestPlanDraft(projectId, input)`

Add response/request types that mirror current API responses:

- Matrix preview response:
  - `project_id`
  - `source_document_path`
  - `source_document_name`
  - `source_format`
  - `capability_status`
  - `selected_table_index`
  - `groups`
  - `warnings`
  - `blockers`
- Draft create request:
  - `source_document_path`
  - `source_document_name`
  - `source_format`
  - `payload`
  - `status`
  - optional source IDs

Do not call `fetch()` outside the API client.

### 4.2 Workbench Model

Extend `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts` to own starter workflow state:

- source path input;
- preview loading/error state;
- latest preview response;
- create-draft loading/error state;
- actions:
  - `previewMatrixSourcePath`;
  - `createMatrixDraftFromPreview`;
  - `createManualMatrixDraft`.

After draft creation:

- reload Matrix drafts using the existing draft-loading path;
- select the created draft as the active candidate;
- reset starter transient state where appropriate.

Keep the route page thin.

### 4.3 Matrix Starter UI

Add a focused component under `frontend/src/features/project-workbench`, for example:

```text
ProjectWorkbenchMatrixStarter.tsx
```

Place it inside `ProjectWorkbenchMatrixReviewPanel` only when:

- not loading;
- no error;
- no active authority draft;
- no candidate draft / active editable draft.

UI contents:

- Import from product specification:
  - local path input;
  - preview button;
  - preview summary: source name, capability status, selected table, group count, step count;
  - warnings/blockers list;
  - create draft button disabled when blockers exist or preview missing.
- Create manual Matrix:
  - short operational copy;
  - button to create a blank editable draft.

### 4.4 Manual Draft Payload

Manual starter should persist a real draft with explicit manual origin metadata.

Preferred payload:

```json
{
  "groups": [
    {
      "group_key": "group_1",
      "group_label": "Group 1",
      "sample_size": null,
      "steps": []
    }
  ],
  "warnings": [
    "Manual Matrix draft was created without source document extraction."
  ],
  "blockers": []
}
```

Preferred source metadata:

```text
source_document_path: manual://project-matrix
source_document_name: Manual Matrix
source_format: manual
```

If existing backend validation rejects this source metadata, the implementation should add the smallest application/API support needed for manual-origin drafts. Do not introduce a schema migration unless unavoidable.

### 4.5 Import Draft Payload Mapping

The preview response should be converted into the same payload shape already consumed by Matrix overview and inspector.

Mapping direction:

- preview `groups` -> draft `payload.groups`;
- preview `group_key`, `group_label`, `source_table_index` preserved;
- preview `steps` -> draft steps;
- preserve:
  - `sequence`;
  - `test_item`;
  - `source_section`;
  - `condition_summary`;
  - `method_summary`;
  - `reference_standard`;
  - `judgement_criteria`;
  - `estimated_duration_hint`;
  - `source_table_index`;
  - `source_row_index`;
  - warnings.

Do not normalize away suffix notes or step identity that existing parser/edit service expects.

---

## 5. Out Of Scope

- PDF import and parsing.
- `.doc` import and parsing.
- Native Windows file picker.
- Outlook/email attachment browser.
- Automatic selection from source archive unless already available without new scope.
- Test record form generation changes.
- Filled record form import.
- Images/evidence per step.
- Fee evaluation mapping.
- Report generation.
- Historical Matrix reuse.
- Auto-loading a fake sample Matrix into real project data.

---

## 6. File-Level Change Plan

Expected implementation files:

- `frontend/src/api/client.ts`
  - add Matrix preview and draft creation DTOs/functions.
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
  - add starter workflow state/actions and draft reload after creation.
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixReviewPanel.tsx`
  - render starter component when no draft exists.
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixStarter.tsx`
  - new focused UI component.
- `frontend/src/features/project-workbench/projectWorkbenchMatrixHelpers.ts`
  - add preview-to-draft and manual-draft helper functions if they stay presentation/application-side.
- `frontend/src/workbench.css`
  - add compact starter styles consistent with current Workbench design.
- `tests/unit/test_frontend_shell_files.py`
  - add static boundary assertions for TASK_191 wiring.
- `docs/task_board.md`
  - update status after implementation only.

Possible backend files only if required:

- `backend/api/routes_project_test_plan_drafts.py`
- `backend/application/project_test_plan_draft_service.py`
- focused tests for manual-origin draft support.

Backend changes are not the preferred path for this task.

---

## 7. UX Acceptance Details

The Matrix empty state should answer:

- Where can I import Matrix from?
- What happened after preview?
- Why can I not create a draft from this file?
- How do I start manually when there is no source Matrix?

The design should remain product UI:

- restrained table/form layout;
- no hero section;
- no decorative card grid;
- no nested cards;
- no future-feature showcase;
- no raw backend enum-only copy as the main guidance.

---

## 8. Risk Controls

Risk: the starter becomes a general file manager.

Control: accept a path input only. Native browse/source archive integration remains a later task.

Risk: manual draft source metadata looks like a real file.

Control: use explicit manual origin labels and source metadata.

Risk: import creates a draft from a blocked preview.

Control: disable create action when preview blockers exist.

Risk: route/page state grows again.

Control: starter state belongs in `useProjectWorkbenchModel`; UI belongs in feature components.

Risk: fake sample data contaminates real project records.

Control: no default demo Matrix is silently persisted. Manual draft is empty except for `Group 1` identity.

---

## 9. Validation

After implementation, run:

```powershell
cd frontend
npm run build
```

```powershell
python -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix or task191"
```

```powershell
python -m pytest tests\integration\test_project_test_plan_preview_api.py tests\integration\test_project_test_plan_draft_api.py -q
```

```powershell
python -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

Manual smoke:

- Open a project with no Matrix draft.
- Verify the starter appears inside Matrix review.
- Preview a valid `.docx` source path.
- Create draft from preview.
- Verify Matrix cross-table appears after reload.
- Create manual Matrix on another draftless project.
- Verify `Group 1` is available for editing in the inspector.

---

## 10. Approval Needed

Please approve this plan before implementation.

Implementation must stop at TASK_191. It must not continue into record form generation, record import, images, fee mapping, reports, or historical reuse.
