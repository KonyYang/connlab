# TASK_149 Settings External Resources UI And Local Paths Plan

> Current phase: Phase 10E - External resource settings and LTR workbook authority
> Active task for planning: TASK_149_SETTINGS_EXTERNAL_RESOURCES_UI_AND_LOCAL_PATHS
> Status: awaiting user review before implementation
> Date: 2026-05-09

## 1. Task Goal

Create an operator-facing Settings page for configuring ConnLab external resource paths. The page must let a non-programmer list, edit, save, and validate known shared/public resource paths from the browser, using the existing external resource registry API where possible.

This task is allowed now because `docs/task_board.md` marks Phase 10E as current, has no active implementation task, and recommends TASK_149 as the next implementation task while requiring user approval before code changes.

## 2. Inputs

- Existing backend API:
  - `GET /api/external-resources`
  - `PUT /api/external-resources/{resource_type}`
  - `POST /api/external-resources/{resource_type}/validate`
- Existing resource types:
  - `ltr_workbook`
  - `application_form_template`
  - `project_folder_template`
  - `standard_record_excel`
  - `equipment_calibration_excel`
- Operator-entered path strings and active-state choices in the Settings UI.
- Existing local LTR workbook settings from `connlab.local.toml` / environment, for backup and lock directory display only if surfaced.

## 3. Outputs

- A reachable `/settings` route from the sidebar.
- A Settings page with grouped external resource rows.
- Typed frontend client methods for listing, saving, and validating external resources.
- A backend-supported `project_output_root` external resource if implemented in this task.
- Business-readable resource labels, categories, validation state, timestamps, and failure reasons.
- Tests covering the backend resource addition and static frontend wiring.

## 4. Scope Boundaries

In scope:

- Enable Settings navigation.
- Add a Settings route and page.
- Add typed frontend API methods and DTOs in `frontend/src/api/client.ts`.
- Render grouped rows for shared/public resources and local-machine paths.
- Support manual path paste and save.
- Support validate action per registry-backed resource.
- Add `project_output_root` as a directory-style external resource unless code reality blocks it.
- Document local machine LTR backup and lock directories as read-only/deferred if they do not fit the registry.

Out of scope:

- No native OS file picker.
- No PyWebView integration.
- No changes to workbook write, folder generation, or resource authority behavior.
- No centralized server settings service.
- No Matrix, Report, AI review, email sending, permissions, LAN deployment, or future-scope UI.

## 5. Current Code Reality

Backend:

- `ExternalResourceType` currently lacks `project_output_root`.
- `ExternalResourceService` already validates folder template directories and Excel/Word resources.
- `routes_external_resources.py` already exposes typed list, upsert, and validate routes.
- `ExternalResourceRepository` stores arbitrary resource rows by enum value, so adding a type is mostly enum plus validation behavior.

Frontend:

- `Sidebar.tsx` contains `Settings` but marks it disabled.
- `App.tsx` has no `settings` route.
- `api/client.ts` centralizes all fetch calls and currently has no external resource methods.
- Existing UI architecture permits a new page plus feature folder, with API calls kept in `api/client.ts`.

UX/design:

- `$impeccable` product context applies. Settings should be dense, calm, operational, and not a developer console.
- Use the existing app shell, restrained state colors, familiar inputs/buttons, and visible disabled or failure reasons.

## 6. Data Structure Design

Backend enum addition:

```python
class ExternalResourceType(StrEnum):
    PROJECT_OUTPUT_ROOT = "project_output_root"
```

Validation rule:

- `project_folder_template`: existing non-empty directory validation remains unchanged.
- `project_output_root`: directory resource. It should validate as an existing readable directory. It should not require the directory to be non-empty.

Frontend DTOs:

```ts
export type ExternalResourceType =
  | "ltr_workbook"
  | "application_form_template"
  | "project_folder_template"
  | "project_output_root"
  | "standard_record_excel"
  | "equipment_calibration_excel";

export type ExternalResource = {
  resource_id: string;
  resource_type: ExternalResourceType;
  path: string;
  active: boolean;
  validation_status: "not_validated" | "valid" | "invalid";
  last_validated_at: string | null;
  validation_failure_reason: string | null;
};
```

Frontend view model:

```ts
type ResourceConfigRow = {
  resourceType: ExternalResourceType;
  label: string;
  category: "Shared resource" | "Local machine path";
  expectedKind: "Excel file" | "Word file" | "Folder";
  editable: boolean;
  registryBacked: boolean;
};
```

Local machine paths:

- `LTR workbook backup directory`
- `LTR workbook lock directory`

These are currently `Settings.ltr_workbook` values, not external resource registry records. TASK_149 should not force them into the registry unless the backend already has a clean API for them. Proposed implementation: render a small read-only/deferred section explaining they remain configured by local TOML/env for now. This satisfies the task's split-documentation requirement without mis-modeling local-only settings.

## 7. File-Level Implementation Plan

Backend:

- `backend/domain/enums.py`
  - Add `PROJECT_OUTPUT_ROOT`.
- `backend/application/external_resource_service.py`
  - Add directory validation branch for `PROJECT_OUTPUT_ROOT`.
  - Keep `PROJECT_FOLDER_TEMPLATE` non-empty requirement unchanged.
- `tests/unit/test_external_resource_service.py`
  - Add coverage that `project_output_root` accepts an existing empty directory.
- `tests/integration/test_external_resource_api.py`
  - Add coverage for register/list/validate `project_output_root`.

Frontend:

- `frontend/src/api/client.ts`
  - Add `ExternalResource` and related DTO types.
  - Add `listExternalResources`, `saveExternalResource`, `validateExternalResource`.
- `frontend/src/components/layout/Sidebar.tsx`
  - Enable `Settings`.
- `frontend/src/App.tsx`
  - Add route type and parser branch for `/settings`.
  - Render `SettingsPage`.
- `frontend/src/pages/SettingsPage.tsx`
  - New route-level page. Keep it thin: load data, pass state to feature components.
- `frontend/src/features/settings/settingsResourceConfig.ts`
  - Resource labels, grouping, expected-kind copy, and local-machine deferred rows.
- `frontend/src/features/settings/SettingsExternalResourcesPanel.tsx`
  - Operational list/table with path input, active checkbox, validation badge, last checked, failure reason, Save and Validate actions.
- `frontend/src/features/settings/settingsSelectors.ts`
  - Merge registry data with config rows and calculate status copy.
- `frontend/src/settings.css` or existing scoped stylesheet
  - Add Settings-specific layout and row styles, using ConnLab restrained product tokens.
- `tests/unit/test_frontend_shell_files.py`
  - Add static checks for Settings route, enabled nav item, external resource API methods, grouped copy, and no direct `fetch()` outside API client.

Documentation/board:

- `docs/task_board.md`
  - Update only after implementation and validation, not during plan-only approval.

## 8. API And Function Signatures

Backend API remains unchanged except accepting the new enum value:

```http
GET /api/external-resources
PUT /api/external-resources/project_output_root
POST /api/external-resources/project_output_root/validate
```

Frontend API:

```ts
export function listExternalResources(): Promise<ExternalResource[]>;

export function saveExternalResource(
  resourceType: ExternalResourceType,
  input: { path: string; active: boolean }
): Promise<ExternalResource>;

export function validateExternalResource(
  resourceType: ExternalResourceType
): Promise<ExternalResource>;
```

## 9. Dependency Direction

- Frontend Settings page calls only `frontend/src/api/client.ts`.
- API routes continue to call `ExternalResourceService`.
- `ExternalResourceService` keeps validation orchestration in application layer and delegates Office reads through `OfficeFacade`.
- Domain remains dataclasses/enums only and does not import infrastructure/API.
- No UI code touches Office files, SQLite, or project folders directly.

## 10. UX Plan

Physical scene: a lab coordinator on a Windows workstation is preparing ConnLab for daily public-drive based work, pasting known local or shared paths and checking whether each one is usable before creating projects.

Design direction:

- Use the existing left navigation and top bar.
- Page title: `Settings`.
- Primary section: `External resources`.
- Guidance copy: `Use local paths during development. Switch to public-drive paths before production use.`
- Group rows into `Shared resources` and `Local machine paths`.
- Each registry-backed row shows:
  - label
  - expected kind
  - path input
  - active checkbox
  - validation badge
  - last checked
  - failure reason
  - Save and Validate actions
- Local-machine rows show:
  - label
  - read-only/deferred status
  - copy explaining local TOML/env ownership

Validation copy mapping:

- `valid` -> `Valid`
- `not_validated` -> `Not checked`
- invalid file/folder failure from backend -> show backend reason, preceded by status `Missing` or `Invalid` when detectable from the string.

## 11. Risks

- `project_output_root` may later need to drive folder generation, but TASK_149 must not change folder generation behavior. This task only registers and validates it.
- Local backup and lock directories are not registry-backed today. Forcing them into external resources would mix local settings with shared resources; plan keeps them read-only/deferred unless a clean API already exists.
- Browser path paste can validate only from the backend process machine perspective. The UI copy must avoid implying the browser can inspect local files directly.
- Existing working tree is dirty. Implementation must avoid reverting or rewriting unrelated user changes.

## 12. Validation Plan

Automated:

```powershell
py -m pytest tests\integration\test_external_resource_api.py tests\unit\test_external_resource_service.py -q
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "settings or external"
cd frontend
npm run build
```

Optional broader check if time permits:

```powershell
py -m pytest tests\unit tests\integration -q
```

Manual smoke:

1. Open `/settings`.
2. Confirm Settings is reachable from the sidebar.
3. Paste local development paths for LTR workbook, project folder template, project output root, standard Excel, and equipment Excel.
4. Save each path.
5. Validate each path.
6. Confirm valid/invalid state and failure reasons are visible without reading logs.

## 13. Acceptance Criteria Mapping

- Settings page reachable from sidebar: `Sidebar.tsx` and `App.tsx`.
- External resources listed, edited, saved, and validated: `api/client.ts`, `SettingsPage.tsx`, settings feature components.
- `project_output_root` represented: enum, service validation, API integration tests, UI config row.
- Shared/public and local machine paths distinguished: settings resource config and grouped UI copy.
- No workbook write behavior changes: no edits to workbook write services/routes.
- Task board updated after implementation: deferred until user approves implementation and validation completes.

## 14. Self-Check Before Implementation

- AGENTS.md compliance: plan limits work to TASK_149.
- No future-scope features: no Matrix, Report, AI review, LAN, permissions, email sending.
- Layering: frontend uses API client; API uses application service; Office remains behind `OfficeFacade`.
- Hard-coded paths: none planned; operator paths are stored through registry.
- TODOs: implementation should avoid TODO comments and document deferred local-machine path handling in UI copy and final notes.
