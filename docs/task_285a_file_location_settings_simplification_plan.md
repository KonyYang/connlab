# TASK_285A File Location Settings Simplification Plan

> Status: proposed for review
> Created: 2026-06-03
> Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

## 1. Goal

Simplify the Settings page so ordinary lab users can update moved public-drive files and folders without seeing developer/backend configuration concepts.

The page should become a file-location surface:

```text
File Locations
  Public registration and record files
    LTR registration workbook
    Standard record Excel
    Equipment calibration Excel
  Default locations
    Project default save location
    Template folder
```

## 2. Current Reality

Current frontend Settings uses:

- `Configuration`
- `External resources`
- `Active`
- `Local machine paths`
- `local TOML or environment settings`

The backend currently stores external resource paths through the `ExternalResource` registry in SQLite. That storage can remain an implementation detail. The operator-facing UI should not describe it as database-backed registry/configuration.

Current registry-backed frontend rows are six backend resource types:

- `ltr_workbook`
- `project_folder_template`
- `project_output_root`
- `application_form_template`
- `standard_record_excel`
- `equipment_calibration_excel`

TASK_285A must not render all six. It must render an explicit five-entry operator allowlist.

## 3. Design

### Frontend

Update Settings UI copy and row configuration:

- Rename the page heading to `File Locations`.
- Replace developer-oriented helper copy with operator copy, for example:
  - `If a public-drive file or template folder moved, paste the new address here and check it before project work.`
- Replace `External resources` with `Public registration and record files`.
- Remove `Active` from ordinary user view.
- Remove the `Local machine paths` section from ordinary user view.
- Keep path inputs and validation state.
- Rename action buttons:
  - `Save` remains `Save`.
  - `Validate` becomes `Check path`.
- Remove the fake `...` browse button unless a real picker is implemented and tested.
- Update selector-level status labels and failure reasons so they use operator-readable copy.
- Update `tests/unit/test_frontend_shell_files.py` Settings assertions, including any historical TASK_149 assertions that still expect old Settings copy.

### Backend / API

Use existing external-resource APIs and resource types for V1. Do not add new external resource enum values in TASK_285A.

Fixed V1 mapping:

| Operator-facing entry | Existing backend resource type | Validation kind |
| --- | --- | --- |
| LTR registration workbook | `ltr_workbook` | Excel file |
| Standard record Excel | `standard_record_excel` | Excel file |
| Equipment calibration Excel | `equipment_calibration_excel` | Excel file |
| Project default save location | `project_output_root` | Folder |
| Template folder | `project_folder_template` | Folder |

`application_form_template` must be hidden from the ordinary-user Settings view in TASK_285A. It may remain in backend/API compatibility paths for existing behavior.

The frontend config should implement an explicit allowlist for the five visible rows rather than rendering every registered backend resource.

### Browse Button

V1 should not show a fake browse action. If a real file/folder picker is not already available in the app shell, remove the current placeholder browse button and keep paste path as the reliable supported workflow.

If a reliable picker is retained or wired in this task, file entries must use a real file picker, folder entries must use a real folder picker, and frontend tests must cover the browse action. Otherwise, no browse button should be shown.

## 4. Expected File-Level Changes

Likely frontend files:

- `frontend/src/pages/SettingsPage.tsx`
- `frontend/src/features/settings/SettingsExternalResourcesPanel.tsx`
- `frontend/src/features/settings/settingsResourceConfig.ts`
- `frontend/src/features/settings/settingsSelectors.ts`
- `frontend/src/settings.css`
- `tests/unit/test_frontend_shell_files.py`

Backend files are not expected to require new resource types. Touch backend only if an existing test reveals operator-copy or validation behavior cannot be achieved through the frontend allowlist and existing resource types.

- `backend/application/external_resource_service.py`
- `frontend/src/api/client.ts`
- relevant tests for external resource validation

## 5. Risks

1. Reusing `project_folder_template` as operator-facing `Template folder` is a transitional naming layer; later template discovery may need a more structured model.
2. Existing tests may assert old Settings copy.
3. A browse button without real picker behavior would be worse for users than paste-only V1.
4. Hiding `Active` must not break backend active-resource semantics if existing services expect active paths.

## 6. Validation

Targeted frontend/static validation:

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "settings or external_resource"
cd frontend
npm run build
```

If backend resource types change:

```powershell
py -m pytest tests/unit/test_external_resource_service.py tests/integration/test_external_resource_api.py -q
```

Backend resource type changes are not expected for the approved V1 mapping. If implementation changes backend validation copy or behavior, run the backend command above even without enum changes.

## 7. Acceptance Summary

- Ordinary users see file locations, not backend configuration.
- Only five path entries are visible.
- The five entries map to the fixed existing backend resource types listed in this plan.
- `application_form_template` is not visible in ordinary Settings.
- No SQLite/database/TOML/environment/lock/backup wording appears in Settings.
- Paste path, `Save`, and `Check path` are supported for each entry.
- No fake browse button remains.
- The old external-resource storage can remain hidden implementation detail.

## 8. Approval Gate

Implementation starts only after explicit user approval, for example:

```text
批准执行 TASK_285A
```
