# TASK_150 Project Folder Uses Configured Resources Plan

> Current phase: Phase 10E - External resource settings and LTR workbook authority
> Active task for planning: TASK_150_PROJECT_FOLDER_USES_CONFIGURED_RESOURCES
> Status: awaiting user review before implementation
> Date: 2026-05-10

## 1. Task Goal

Connect Project Workbench folder creation to Settings-managed external resources so an operator no longer types `template_path` and `target_root` during normal folder creation.

This task is allowed now because `docs/task_board.md` marks TASK_149 complete and recommends TASK_150 as the next implementation task, while requiring user approval before code changes.

## 2. Inputs

- Existing Settings-managed external resources:
  - `project_folder_template`
  - `project_output_root`
- Existing external resource API:
  - `GET /api/external-resources`
  - `POST /api/external-resources/{resource_type}/validate`
- Existing folder APIs:
  - `POST /api/projects/{project_id}/folder/preview`
  - `POST /api/projects/{project_id}/folder/generate`
  - `GET /api/projects/{project_id}/folder/latest`
- Existing project context:
  - project id
  - project status
  - latest LTR number

## 3. Outputs

- Workbench folder creation displays configured folder template and output root from Settings.
- Folder preview/generation uses the configured paths rather than user-typed raw paths.
- Missing, inactive, or invalid configured resources block preview/generation with business-readable copy.
- Existing preview-before-write and conflict-blocking behavior remains unchanged.

## 4. Scope Boundaries

In scope:

- Load external resources in Project Workbench or folder feature.
- Resolve `project_folder_template` and `project_output_root` into a `FolderRequest`.
- Show resource path, active state, validation status, and failure reason near the folder action.
- Disable `Preview folder` until both required resources are active and valid.
- Keep paths visible for traceability.
- Preserve existing folder preview/generate endpoints and request DTOs unless implementation proves unsafe.

Out of scope:

- No native folder picker.
- No overwrite/conflict resolution strategy.
- No evidence placement behavior changes.
- No LTR workbook behavior changes.
- No Matrix, Report, AI review, email sending, permissions, LAN deployment, or future-scope UI.

## 5. Current Code Reality

Backend:

- `routes_folder.py` accepts explicit `template_path` and `target_root`.
- `FolderService` already enforces lifecycle guards, preview-before-write, and conflict blocking.
- `routes_external_resources.py` can list Settings resources.
- TASK_149 added `project_output_root`.

Frontend:

- `ProjectFolderCreationPanel.tsx` currently owns local `folderInput` state for `template_path`, `target_root`, and `dl_number`.
- The normal UI exposes raw path input fields.
- `api/client.ts` already has `listExternalResources`, `previewFolder`, and `generateFolder`.
- `ProjectWorkbenchPage.tsx` already composes `ProjectFolderCreationPanel`.

UX/design:

- `$impeccable` product context applies. The Workbench should show current state, blocker, and next action without requiring technical path entry.
- Paths remain visible, but they become read-only traceability fields, not normal operator inputs.

## 6. Data Structure Design

Frontend resource selector view model:

```ts
type FolderResourceState = {
  template: ExternalResource | null;
  outputRoot: ExternalResource | null;
  ready: boolean;
  blockingReason: string | null;
};
```

Readiness rules:

- Missing `project_folder_template` blocks.
- Missing `project_output_root` blocks.
- `active === false` blocks.
- `validation_status !== "valid"` blocks.
- `validation_failure_reason` should be shown when available.

Folder request construction:

```ts
const request: FolderRequest = {
  template_path: template.path,
  target_root: outputRoot.path,
  dl_number: latestLtrNumber ?? undefined
};
```

## 7. Implementation Plan

Preferred implementation: frontend-resolved Settings resources using existing APIs.

Rationale:

- TASK_150 explicitly allows keeping existing `POST /folder/preview` and `POST /folder/generate` contracts stable.
- Existing folder service already validates filesystem paths and conflict behavior.
- This is the smallest safe step and avoids adding duplicate configured preview/generate endpoints prematurely.

Backend changes:

- No backend API changes planned.
- Keep integration tests for existing folder and external resource APIs.
- If implementation exposes a backend gap, stop and update the plan before widening API scope.

Frontend changes:

- `frontend/src/features/project-workbench/projectFolderResourceSelectors.ts`
  - New selector helpers to find `project_folder_template` and `project_output_root`.
  - Build business-readable blocking reasons.
- `frontend/src/features/project-workbench/ProjectFolderCreationPanel.tsx`
  - Accept external resources as props or load them via a feature-level hook.
  - Remove raw `Template path` and `Target root` input fields from the normal path.
  - Show read-only configured rows for template and output root.
  - Keep `LTR number` display read-only from latest registered LTR.
  - Build `FolderRequest` from configured resource paths.
  - Keep `Preview folder` and `Create folder` behavior.
- `frontend/src/pages/ProjectWorkbenchPage.tsx`
  - Load `listExternalResources()` with project and LTR data, or pass resources from a hook.
  - Keep page orchestration thin.
- `frontend/src/workbench.css`
  - Add compact configured-resource row styles.
- `tests/unit/test_frontend_shell_files.py`
  - Static checks that Workbench folder creation uses external resource methods, no longer exposes normal raw path inputs, and shows missing/invalid resource copy.

Optional backend read model, only if needed:

- `GET /api/external-resources` is already enough for this task.
- Do not add `preview-configured` / `generate-configured` unless frontend resolution proves too error-prone during implementation.

## 8. API And Function Signatures

No new backend endpoint planned.

Existing frontend API calls:

```ts
listExternalResources(): Promise<ExternalResource[]>
previewFolder(projectId: string, input: FolderRequest): Promise<FolderPlan>
generateFolder(projectId: string, input: FolderRequest): Promise<FolderGeneration>
```

Potential selector signatures:

```ts
export function buildFolderResourceState(
  resources: ExternalResource[]
): FolderResourceState;

export function configuredFolderRequest(
  state: FolderResourceState,
  latestLtrNumber: string | null
): FolderRequest | null;
```

## 9. Dependency Direction

- Frontend calls only typed API functions in `frontend/src/api/client.ts`.
- Workbench display components do not call `fetch()` directly.
- UI never touches filesystem directly.
- Existing API routes remain thin and call application services.
- `FolderService` remains the authoritative folder preview/generation path.

## 10. UX Plan

Physical scene: a lab coordinator has already configured shared folder resources in Settings and is now creating a project folder after LTR registration. They should verify the selected template/root and preview the result, not type paths again.

Workbench folder panel should show:

- LTR number context.
- Configured template resource:
  - label: `Project folder template`
  - path
  - validation badge
- Configured output resource:
  - label: `Project output root`
  - path
  - validation badge
- Blocking copy when resource setup is incomplete:
  - `Configure and validate Project folder template in Settings.`
  - `Configure and validate Project output root in Settings.`
- `Preview folder` disabled until:
  - project has registered LTR
  - project status allows folder creation
  - both resources are active and valid
- `Create folder` remains available only after a clear preview.

No raw path fields in the normal business path. If debug overrides are retained at all, they must be hidden from the normal operator path and explicitly labeled as diagnostic. Default plan: remove normal raw path entry.

## 11. Risks

- Frontend-resolved resource paths still send paths to existing folder APIs. This is acceptable for TASK_150 because the source is Settings, not operator typing, but a future backend configured endpoint may be safer.
- If a resource is saved but not validated, operators may expect it to work. The UI must block and direct them to validate in Settings.
- Existing tests may still expect raw path strings in Workbench. Update static tests to the new business path without broad historical rewrites.
- Worktree contains prior TASK_149 follow-up changes; implementation must not revert them.

## 12. Validation Plan

Automated:

```powershell
py -m pytest tests\integration\test_folder_generation_api.py tests\integration\test_external_resource_api.py -q
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or folder or settings"
cd frontend
npm run build
git diff --check
```

Manual smoke:

1. Open Settings.
2. Configure and validate local `project_folder_template`.
3. Configure and validate local `project_output_root`.
4. Create/apply LTR for a New Project or open an existing `ltr_registered` project.
5. Open Project Workbench.
6. Confirm folder panel shows configured paths and validation states.
7. Preview folder without typing paths.
8. Create folder only after preview is clear.

## 13. Acceptance Criteria Mapping

- Normal Workbench folder creation uses Settings-managed resources: selector + `ProjectFolderCreationPanel` request construction.
- Missing/invalid resources block actions: selector readiness + disabled action + inline copy.
- Raw path entry is no longer normal path: remove visible editable template/root inputs.
- Conflict blocking still works: unchanged folder preview/generate APIs and `FolderService`.

## 14. Self-Check Before Implementation

- AGENTS.md compliance: task is limited to TASK_150.
- No future scope: no LTR workbook authority change, no evidence placement behavior change, no native picker.
- Layering: frontend uses API client; API/application boundaries stay intact.
- Hard-coded paths: none planned.
- TODOs: avoid TODO comments and keep any future configured endpoint note in documentation/final risk only.
