# TASK_183 Plan - Project Workbench Approval Package UI Wiring

## 1. Current Phase And Gate

- Current phase: `Phase 11 - Project planning data foundation before downstream document automation`.
- Current active task before creation: `none; TASK_182 complete`.
- This plan is proposal-only. Implementation must wait for explicit user approval: `批准执行 TASK_183`.
- `$impeccable` product context has been loaded because this is frontend/UI work.

## 2. Model Fit

`gpt-5.3-codex` is suitable for implementation.

Reason:

- The task is a bounded TypeScript/React integration task.
- Existing backend endpoints already exist.
- Expected work is DTO wiring, API client functions, a focused workbench panel, button/disabled state logic, and build/static tests.
- The task does not require a large architecture redesign, real Office template reverse engineering, or ambiguous business-rule discovery.

## 3. Goal

Expose TASK_182 approval-package preview and execute actions in Project Workbench.

The operator should be able to paste the required generated/source file paths, preview the placement plan, see blockers, and execute only when the plan is safe.

## 4. Design Direction

Use a compact workbench panel within the existing Project Workbench flow.

The physical scene is a lab coordinator on a daytime Windows workstation checking package readiness before supervisor review. The UI should stay restrained, dense, and explicit. It should not use a hero layout, decorative cards, or future-feature messaging.

## 5. Data Flow

1. User enters approval-package file paths in the Workbench panel.
2. Frontend calls `previewApprovalPackage(projectId, request)`.
3. UI renders item statuses, target paths, warnings, and blockers.
4. Execute button stays disabled until a preview exists and has no blockers.
5. Frontend calls `executeApprovalPackage(projectId, request)`.
6. UI shows copied/already-in-place results and any returned warnings.

## 6. API Client Changes

Add frontend DTOs:

```ts
export type ApprovalPackageRequest = {
  project_folder_path: string;
  completed_application_form_path: string;
  test_record_output_path: string;
  fee_evaluation_output_path?: string | null;
  evidence_source_paths: string[];
  overwrite: boolean;
};
```

Add response DTOs:

```ts
export type ApprovalPackageItem = {
  source_path: string;
  target_relative_path: string;
  target_path: string;
  classification: string;
  status: string;
  warnings: string[];
};

export type ApprovalPackageResult = {
  project_id: string;
  project_folder_path: string;
  mode: string;
  items: ApprovalPackageItem[];
  warnings: string[];
  blockers: string[];
};
```

Add API functions:

```ts
previewApprovalPackage(projectId: string, request: ApprovalPackageRequest)
executeApprovalPackage(projectId: string, request: ApprovalPackageRequest)
```

## 7. Component Plan

Add:

- `frontend/src/components/workflow/ApprovalPackagePanel.tsx`

Responsibilities:

- render path fields;
- parse multiline evidence path input into `evidence_source_paths`;
- call preview and execute callbacks supplied by Project Workbench page;
- render preview/result item list;
- render blockers/warnings;
- keep execute disabled when blockers exist.

Modify:

- `frontend/src/pages/ProjectWorkbenchPage.tsx`
- `frontend/src/api/client.ts`
- relevant CSS file used by workbench/workflow panels

## 8. State Boundary

Page-level state remains limited to route workflow coordination:

- approval package form fields;
- latest preview/result;
- loading/error message flags.

The visual rendering and disabled-state explanation should live in the panel or small selectors if needed. Do not add direct `fetch()` calls outside `frontend/src/api/client.ts`.

## 9. UX Copy

Use operational labels:

- `Preview approval package`
- `Place approval package`
- `Blockers`
- `Warnings`
- `Target`
- `Already in place`
- `Planned`
- `Copied`

Avoid backend route names, raw stack errors, or future workflow promises.

## 10. Validation

Frontend build:

```powershell
cd frontend
npm run build
```

Static frontend guard:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or approval or folder"
```

Task-board guard:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

## 11. Risks

- Project Workbench may already be a large page. Keep new UI in a named component to avoid increasing page complexity.
- Operators may not know all generated file paths yet. This task uses path paste only; native picker or auto-population should be a later desktop-shell task.
- Approval package backend may report blockers from real filesystem state. UI must render blockers as authoritative and not try to override them.

## 12. Review Checklist Result For Plan Stage

- Architecture boundary: API client remains fetch boundary; UI does not touch files directly.
- Scope: approval package UI only.
- Frontend guidance: `$impeccable` product register loaded; panel should remain workbench-style and restrained.
- Model fit: `gpt-5.3-codex` suitable for implementation.
- Stop condition: wait for explicit implementation approval.
