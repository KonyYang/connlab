# TASK_285A_FILE_LOCATION_SETTINGS_SIMPLIFICATION

## Status

Status: complete (archived 2026-08-18; implementation integrated and covered by tests)

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Objective

Simplify the Settings page into an operator-facing file-location page for legacy-authority compatibility mode.

The page should let non-programmer users update moved public-drive file and folder paths by copying/pasting paths, or by selecting files/folders when a browser/picker capability is available. It must not expose SQLite, database, TOML, environment variables, lock directories, backup directories, registry concepts, or developer-oriented configuration language.

## Business Context

ConnLab is in a transition stage from manual public-drive Office workflows to controlled software automation. Public-drive Excel files and template folders remain important operational inputs. Ordinary users know where moved public-drive files are and should be able to update visible file locations without asking an administrator to edit backend configuration.

This task supports the `AGENTS.md` legacy-authority compatibility mode:

```text
Public-drive LTR Excel files and existing Word/Excel templates remain the current business authority or delivery templates.
Local SQLite is only a personal workstation cache, automation aid, synchronization backup, and future migration backup.
```

## Scope

### In Scope

1. Rename the Settings user-facing concept from developer-style configuration to file locations.
2. Display only ordinary-user path entries:
   - LTR registration workbook.
   - Standard record Excel.
   - Equipment calibration Excel.
   - Project default save location.
   - Template folder.
3. Allow each visible entry to accept a copied/pasted path.
4. Keep a path-check action with operator-readable wording such as `Save and check`.
5. Show check results in business-readable language:
   - ready to use;
   - file not found;
   - folder not found;
   - expected Excel file;
   - expected folder.
6. Remove or hide ordinary-user exposure of:
   - `Configuration`;
   - `External resources`;
   - `Active`;
   - `Local machine paths`;
   - TOML/environment wording;
   - lock/backup directory rows;
   - SQLite/database wording.
7. Keep the existing backend external-resource storage concept as an implementation detail if it is the narrowest low-risk path.
8. Implement the visible rows through a frontend allowlist of exactly five operator-facing entries, not by rendering all backend registered resource types.
9. Add or update frontend tests/static checks for the new Settings copy and removed developer-facing copy.

### Out Of Scope

1. No fee rule seed library implementation.
2. No fee draft generation.
3. No template search or template selection engine.
4. No advanced administrator Settings UI.
5. No database authority change.
6. No server deployment or permissions.
7. No LTR workbook writeback behavior change.
8. No new SQLite schema unless strictly required for the two new operator-facing path types.

## User-Facing Entries

### Public Registration And Record Files

- LTR registration workbook: Excel file.
- Standard record Excel: Excel file.
- Equipment calibration Excel: Excel file.

### Default Locations

- Project default save location: folder.
- Template folder: folder.

The Template folder is a low-complexity transitional model. Users can put fee templates, Test Record templates, application form templates, and other Office templates in one visible folder. Later tasks may add structured template discovery or version management.

## Backend Resource Mapping

TASK_285A must use the following V1 mapping and must not leave this as an implementation-time choice:

| Operator-facing entry | Existing backend resource type |
| --- | --- |
| LTR registration workbook | `ltr_workbook` |
| Standard record Excel | `standard_record_excel` |
| Equipment calibration Excel | `equipment_calibration_excel` |
| Project default save location | `project_output_root` |
| Template folder | `project_folder_template` |

Current `application_form_template` must not appear in the ordinary-user Settings view in TASK_285A. It can remain in backend/API compatibility paths and may be handled by future structured template discovery.

Do not add new external resource enum values in TASK_285A unless the approved implementation plan is explicitly revised. The V1 intent is operator-facing rename and allowlist filtering over the existing resource model.

## Interaction Rules

- The primary operator action is paste path, then use separate `Save` and `Check path` buttons.
- `Save` stores the path.
- `Check path` validates the currently saved path.
- TASK_285A must not deliver both a single-button and two-button interpretation; V1 keeps the current two-action structure with operator-readable labels.
- If this task does not implement a real file/folder picker, remove the existing fake browse button instead of keeping a placeholder hint button.
- If browse support is retained in TASK_285A, it must call a real picker capability and include frontend test coverage. Otherwise, paste path is the supported V1 workflow.
- Validation must not mutate the referenced public-drive files.

## Acceptance Criteria

1. The Settings page reads as `File Locations` or equivalent operator-facing wording.
2. The page shows exactly the five ordinary-user path entries listed in scope.
3. The page does not show `Configuration`, `External resources`, `Active`, `Local machine paths`, `TOML`, `environment`, `SQLite`, or `database`.
4. Each entry has a path input for paste/update.
5. Each entry has separate `Save` and `Check path` actions.
6. Check status is readable without technical backend vocabulary.
7. LTR workbook, Standard record Excel, and Equipment calibration Excel validate as Excel-file entries.
8. Project default save location and Template folder validate as folder entries.
9. The existing fake browse placeholder button is removed unless it is replaced with a real file/folder picker and tested.
10. Existing backend storage remains an implementation detail and is not explained to operators.
11. Tests or static checks cover the visible entry labels and absence of developer-facing Settings copy.
12. Tests or static checks verify that `application_form_template` is not in the ordinary-user Settings allowlist.
13. Scope boundary is held: no fee rules, no template discovery, no advanced admin UI, no authority cutover.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task because it is a bounded frontend UX simplification with small backend/resource-type alignment risk and clear operator-facing copy requirements.

## Required Execution Mode

Use `superpowers:executing-plans` for implementation. Use `$impeccable` for UI/copy work. Also read `docs/project_management/TASK_EXECUTION_SKILL.md` before coding and run `docs/project_management/TASK_REVIEW_CHECKLIST.md` before completion.

## Stop Rule

Do not implement until this task file and its executable plan are reviewed and explicitly approved by the user.
