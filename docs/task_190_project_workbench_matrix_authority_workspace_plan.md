# TASK_190 Plan: Project Workbench Matrix Authority Workspace

> Task: `TASK_190_PROJECT_WORKBENCH_MATRIX_AUTHORITY_WORKSPACE`  
> Status: plan proposed (implementation not started)  
> Date: 2026-05-14

---

## 1. Execution Context

- Current phase: `Phase 11 - Project planning data foundation before downstream document automation`.
- Current active task on board: `TASK_190_PROJECT_WORKBENCH_MATRIX_AUTHORITY_WORKSPACE` proposed for user approval.
- Why this task is allowed now:
  - `TASK_189_MATRIX_AUTHORITY_READ_MODEL_AND_GROUP_IDENTITY_CORRECTION` is complete.
  - Workbench now has authority/candidate Matrix semantics, but the page still visually behaves like a stack of unrelated tools.
  - The agreed product direction is Matrix authority first, downstream tools second.

This plan is the required plan-file stage. No implementation code should be changed until the user explicitly approves this plan.

---

## 2. Problem Statement

The current Project Workbench first screen still gives large, equal visual weight to:

- workbench boundary explanation;
- project folder creation;
- Matrix review/edit;
- downstream output status;
- read-only lookup;
- approval package;
- evidence placement.

That made sense while features were being wired incrementally, but it now conflicts with the business model:

```text
Project -> confirmed Matrix authority -> group/step planning -> downstream outputs
```

The user needs the Matrix to become the dominant project planning surface, while folder, approval, evidence, and lookup remain reachable as supporting workflows.

---

## 3. Scope

### In Scope

Frontend-only information architecture refactor:

- Make Matrix authority the primary Workbench work surface.
- Add or reshape a Matrix authority header/status band.
- Keep authority and candidate draft states visible and business-readable.
- Keep the Matrix overview visible as the central surface.
- Use a right-side or adjacent group/step inspector/detail area for selected Matrix context.
- Convert downstream outputs into compact status/entry points.
- Demote project folder, approval package, evidence placement, and lookup into supporting sections.
- Preserve existing API calls, model hook ownership, and backend behavior.
- Update frontend static tests and run build.

### Out Of Scope

- No backend schema/API changes.
- No new Matrix import channels.
- No new Matrix parser behavior.
- No new test record generation behavior.
- No filled record import.
- No image/evidence step attachment feature.
- No fee mapping overhaul.
- No report generation.
- No AI or historical reuse.
- No new output ledger semantics.

---

## 4. Design Direction

Physical scene:

> A lab engineer is reviewing a confirmed connector qualification project on a daytime Windows workstation and needs to verify the Matrix authority before generating or refreshing downstream files.

Register: product.

UI strategy:

- restrained product interface;
- dense but readable operational layout;
- Matrix owns the main visual weight;
- state and blockers own color;
- no hero, no decorative cards, no toolbox grid.

Target first-screen hierarchy:

```text
Project summary / back navigation
Matrix authority band
Matrix workspace
  Matrix overview
  Group/step inspector
Downstream output strip
Supporting workflow panels
  Folder
  Approval package
  Evidence
  Lookup
```

---

## 5. Proposed UI Structure

### 5.1 Project Header

Keep `ProjectSummaryPanel`, but avoid letting it dominate the page.

Purpose:

- identify current project;
- expose back navigation;
- show essential project metadata.

No new project lifecycle behavior in this task.

### 5.2 Matrix Authority Band

Add a compact authority/candidate band near the top of the Workbench.

It should show:

- confirmed authority version, or no confirmed Matrix yet;
- candidate draft version if present;
- validation blocker/warning counts;
- downstream freshness summary;
- primary next action text, such as confirm candidate, resolve blockers, or review Matrix.

This can live inside `ProjectWorkbenchMatrixReviewPanel` or a new feature component, depending on implementation clarity.

### 5.3 Matrix Workspace

Create a Matrix-first workspace area.

Recommended composition:

```text
ProjectWorkbenchMatrixWorkspace
  Matrix authority band
  Matrix overview region
  Group/step inspector region
```

The overview should preserve the lab-friendly Matrix mental model:

- test item rows;
- technical context columns where available: section, method, condition, requirement;
- group columns;
- step tokens in cells;
- sample size row or compact group metadata.

The inspector should show selected group/step context and editing controls already supported by TASK_189. If a full cell-based selection model is too much for this task, the first implementation may keep existing group-detail editing but place it next to the overview in the new workspace.

### 5.4 Downstream Status Strip

Move `ProjectWorkbenchDocumentStatusPanel` directly under or beside the Matrix workspace as a compact dependency strip.

Purpose:

- show Section 2, test record, fee evaluation, and approval package status against Matrix authority;
- avoid large permanent document panels on first screen;
- keep stale/current/missing labels visible.

Do not change output ledger rules.

### 5.5 Supporting Workflow Panels

Demote these areas so they remain reachable without dominating the first screen:

- `ProjectFolderCreationPanel`
- `ApprovalPackagePanel`
- `ProjectWorkbenchEvidencePanel`
- `ProjectLookupPanel`

Acceptable implementation options:

- compact accordion-style supporting section;
- grouped secondary workflow area below Matrix;
- reduced panel density with smaller headings and less vertical space.

This task should not remove access to existing flows.

---

## 6. File-Level Change Plan

### Frontend Components

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - Reorder composition so Matrix workspace appears before folder/lookup/approval/evidence.
  - Replace the current stacked equal-priority layout with Matrix-first sections.
  - Keep this file a composition layer only.

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixReviewPanel.tsx`
  - Refactor if needed into smaller named subcomponents.
  - Preserve existing save/validate/confirm props and behavior.
  - Improve authority/candidate display and make Matrix overview more central.

- Potential new file:
  - `frontend/src/features/project-workbench/ProjectWorkbenchMatrixWorkspace.tsx`

  Use this if it keeps `ProjectWorkbenchMatrixReviewPanel.tsx` from growing further. The preferred direction is a named workspace component with smaller internal sections.

- Potential new file:
  - `frontend/src/features/project-workbench/ProjectWorkbenchSupportingWorkflows.tsx`

  Use this if demoting folder/approval/evidence/lookup into a supporting area would otherwise bloat `ProjectWorkbenchLayout.tsx`.

- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
  - No new backend orchestration expected.
  - Only expose derived display fields if needed for authority/candidate/status copy.
  - Avoid adding new persistent business truth in frontend state.

- `frontend/src/workbench.css`
  - Add Matrix-first workspace layout classes.
  - Keep colors restrained and state-driven.
  - Avoid nested cards, decorative panels, side-stripe accents, and text overflow.

### Tests

- `tests/unit/test_frontend_shell_files.py`
  - Add TASK_190 assertions that:
    - Matrix workspace component or Matrix-first layout exists;
    - authority/candidate wording is present;
    - downstream status remains wired;
    - route/page boundary stays thin;
    - no new future-scope labels such as report generation, AI review, historical reuse active actions are introduced.

### Documentation

- `docs/task_board.md`
  - After implementation only: mark TASK_190 complete with validation summary and next recommended task.

---

## 7. Implementation Sequence

1. Inspect current `ProjectWorkbenchMatrixReviewPanel.tsx` and identify extractable subcomponents.
2. Introduce the Matrix workspace composition component if needed.
3. Reorder `ProjectWorkbenchLayout.tsx` so Matrix is the primary Workbench region.
4. Demote supporting workflows without removing access.
5. Update CSS for the Matrix workspace, authority band, inspector, and downstream strip.
6. Update frontend static tests.
7. Run validation commands.
8. Update task board only after implementation and tests pass.

---

## 8. Risks And Mitigations

1. **Risk:** existing workflows become harder to find.  
   **Mitigation:** keep all current flows reachable as named supporting sections with clear status labels.

2. **Risk:** Matrix panel grows larger and harder to maintain.  
   **Mitigation:** prefer named feature components for authority band, overview, inspector, and supporting workflows.

3. **Risk:** layout change accidentally changes business behavior.  
   **Mitigation:** preserve model hook functions and API calls; this task changes visual priority and composition only.

4. **Risk:** first version of Matrix overview cannot fully reproduce the source Matrix table.  
   **Mitigation:** keep existing group/detail editing behavior if needed, but structure the page so a richer overview can be added in the next controlled task.

5. **Risk:** 14-inch laptop usability worsens.  
   **Mitigation:** use stable responsive constraints, horizontal overflow only for the Matrix overview, and compact supporting sections.

---

## 9. Validation Plan

Run after implementation:

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

Manual smoke expectation:

- Open a Project Workbench.
- Confirm Matrix area is the first primary work surface after project header.
- Confirm authority/candidate state is visible.
- Confirm downstream output status is visible but compact.
- Confirm folder, approval package, evidence placement, and lookup remain reachable.
- Confirm no new backend feature or future-scope action appears.

---

## 10. Acceptance Criteria

- Matrix authority workspace is visually and structurally primary.
- Authority and candidate states are shown in business-readable copy.
- Matrix overview/group-detail area occupies the main Workbench region.
- Downstream outputs are visible as compact status/entry points.
- Folder, approval package, evidence, and lookup are demoted but reachable.
- Route/page state does not grow; feature components own the Workbench UI.
- Existing API contracts and backend behavior are preserved.
- `npm run build` and targeted frontend/static tests pass.

---

## 11. Stop Condition

Stop after the user reviews and approves this plan.

Do not implement TASK_190 until explicit approval is given.
