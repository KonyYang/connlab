# Projects Registry UI Optimization Plan

> Date: 2026-06-07
> Target route: `/projects`
> Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
> Current active task: None
> Status: Plan for user review. No implementation is approved yet.

## 1. Task Goal

Optimize the Projects registry interface so a lab operator can scan existing projects faster, find the right LTR/project row with less visual noise, and open a project without losing the business fields operators expect from the application-form setup flow.

This is a registry-display task. It must add a narrow read-only API/display DTO to expose already captured application-form/LTR setup fields in a stable way. It must not change Project lifecycle rules, LTR authority behavior, Matrix scope, project creation flow, persistence authority, or output generation.

## 2. Current UI Findings

Observed at `http://localhost:5173/projects`:

- Five metric cards consume a large part of the first viewport even when the operator's main job is registry lookup.
- The toolbar mixes active controls with unavailable controls (`Filter`, `Columns`, inactive grid view), making the page feel busier than its current functional surface.
- The primary action `New Project` is visually heavy inside the same row as search/filter utilities, competing with the registry lookup task.
- Table rows are readable but visual priority is spread evenly across every column; LTR Number, status, and open action should be easier to scan.
- The current `Project Name` column is not needed by the operator on this page.
- The current `Product` column is also not needed because `Sample Description` is the operator-facing replacement.
- The operator expects `Sample Description` and `Test Item` from the application-form/project setup flow to appear in the registry.
- `Recent Activity` is not needed in the registry table.
- A `Notes` column is needed for operator-facing notes.
- The page already has no horizontal viewport overflow at 1280x720, so this task should preserve existing layout stability.

## 3. Inputs

- Existing project registry summary rows from a backend read-only DTO.
- Existing captured business setup fields, where available through the backend DTO:
  - `sample_description`
  - `test_item`
  - operator-facing note text
- Existing frontend route callbacks:
  - `onNewProject`
  - `onOpenProject`
- Existing CSS tokens and product UI rules from `PRODUCT.md` and `DESIGN.md`.

## 4. Outputs

- A cleaner `/projects` registry surface using the same data and existing route callbacks.
- A backend-provided read-only registry row shape:
  - `project_id`
  - `ltr_number`
  - `sample_description`
  - `test_item`
  - `requestor`
  - `business_unit`
  - `status`
  - `progress`
  - `notes`
- Registry rows with these visible columns:
  - `LTR Number`
  - `Sample Description`
  - `Test Item`
  - `Requestor`
  - `Business Unit`
  - `Status`
  - `Progress`
  - `Notes`
  - `Action`
- No new persisted frontend state.
- No new project lifecycle behavior.

## 5. Proposed Design

### 5.1 Header Metrics

Compress the five metric cards into a slimmer summary strip:

- Keep all current metrics and calculations.
- Reduce card height and icon dominance.
- Emphasize `Total projects`, `In progress`, and `Pending review`; keep `Completed` and `Draft` present but quieter.
- Preserve semantic color paired with labels.

### 5.2 Registry Toolbar

Restructure the toolbar into two visual groups:

- Lookup group: title, short description, search input, show-cancelled toggle.
- Actions group: refresh and `New Project`.

De-emphasize currently unavailable controls:

- Hide `Filter`, `Columns`, and disabled grid view from the main toolbar for this phase, or move them behind non-primary inactive affordance only if tests require their presence.
- Keep no future-scope feature exposed as active.

### 5.3 Table Scan Quality

Polish the table and adjust the column set:

- Make LTR Number the strongest row anchor.
- Remove `Project Name`.
- Remove `Product`; `Sample Description` replaces it as the sample-facing description.
- Add `Sample Description` immediately before `Test Item`.
- Add `Test Item` from the same application-form/project setup source used during New Project completion when available.
- Remove `Recent Activity`.
- Add `Notes`.
- Tighten row height slightly while preserving wrapped product names.
- Make status badges calmer and consistent with product tokens.
- Keep progress visible but secondary to status.
- Keep `Open` as the only row action.

Fallback display rules:

- Missing `sample_description`: show `Not recorded`.
- Missing `test_item`: show `Not recorded`.
- Missing `notes`: show `None`.
- Do not synthesize test items from Matrix rows in this task.
- Do not parse free-form LTR audit JSON in the frontend.
- Do not rename or reuse `project.product_name` as `Sample Description`.

### 5.4 Field Source Rules

`Sample Description`, `Test Item`, and `Notes` must come from the backend read-only registry summary DTO. The frontend must not parse LTR notes JSON, intake draft JSON, parser warnings, or system audit payloads.

Authoritative display rules:

- `Sample Description`
  - Preferred source: the project-creation/LTR setup `sample_description` captured during New Project completion or LTR workbook write preparation, when available through backend application services.
  - Historical fallback: if no normalized or safely extractable `sample_description` exists, return `null` from the backend DTO and display `Not recorded`.
  - Forbidden fallback: do not use `project.product_name` as a renamed substitute.
- `Test Item`
  - Preferred source: the single project-creation/LTR setup `test_item` captured during New Project completion or LTR workbook write preparation, when available through backend application services.
  - Multi-value rule: registry does not derive or merge multiple requested-testing rows, Matrix rows, or confirmed Matrix test items. If the single setup `test_item` is absent, return `null`.
  - Display fallback: show `Not recorded`.
- `Notes`
  - Meaning: operator-facing note only, from New Project/LTR operator note data when available.
  - Forbidden sources: raw LTR audit JSON, backend diagnostic notes, parser warnings, review system notes, stack traces, and Matrix extraction notes.
  - Display fallback: show `None`.

### 5.5 Search Rules

The registry search must cover the fields the operator can see:

- `LTR Number`
- `Sample Description`
- `Test Item`
- `Requestor`
- `Business Unit`
- `Status`
- `Notes`

Search must not depend on removed display columns (`Project Name`, `Product`, `Recent Activity`) except where existing project identifiers are still required internally for routing.

### 5.6 Responsive Behavior

Preserve current 1280x720 stability and improve narrow behavior:

- No page-level horizontal overflow.
- Registry toolbar may wrap into stacked groups under existing breakpoints.
- Table remains horizontally scrollable inside its existing wrapper when needed.

## 6. File-Level Change Plan

Expected implementation files:

- Backend:
  - `backend/application/project_registry_summary_service.py`
    - Build read-only registry rows from existing project/LTR/application setup data.
    - Define source precedence for `sample_description`, `test_item`, and `notes`.
    - Return `null` instead of guessing when historical projects lack normalized values.
    - Keep source parsing and fallback rules out of the React page.
  - `backend/api/routes_project.py`
    - Add a narrow typed registry response, for example `GET /api/projects/registry`.
    - Keep existing `ProjectResponse` backward-compatible.
  - `backend/api/dependencies.py`
    - Wire the read-only service if a new service is introduced.
  - Backend tests for source precedence, missing-field fallback, and no Matrix/test-item derivation.
- `frontend/src/pages/ProjectListPage.tsx`
  - Use the registry summary DTO.
  - Recompose the metric, toolbar, and table columns.
  - Update search to cover `LTR Number`, `Sample Description`, `Test Item`, `Requestor`, `Business Unit`, `Status`, and `Notes`.
  - Keep pagination and route callbacks unchanged.
- `frontend/src/project-dashboard.css`
  - Adjust `/projects` layout, metric strip, toolbar grouping, table density, and responsive rules.
- `tests/unit/test_frontend_shell_files.py`
  - Add or update a narrow shell assertion for the new table headers and removed columns.

Backend files should change only to expose existing authoritative display data. No database migration is planned.

## 7. Out Of Scope

- Advanced filtering beyond the existing search box.
- Column customization.
- Grid view implementation.
- Project list sorting.
- Persisting new project fields.
- Reinterpreting historical workbook data as the authority source.
- Project creation workflow changes.
- Matrix, report, fee, or approval package behavior.
- Editing or persisting project data from the registry page.
- Pulling `Test Item` from confirmed Matrix rows.
- Frontend parsing of audit JSON or intake draft JSON.

## 8. Risks

- Existing shell tests may assert current disabled toolbar controls or copy. If so, update tests to reflect the approved UI simplification.
- The current `/api/projects` DTO does not expose `sample_description`, `test_item`, or operator notes. A small read-only summary endpoint is required.
- Historical projects may not have these values captured in a normalized place; they must display an explicit fallback instead of guessing.
- If old operator note data exists only inside audit JSON, this task should not expose it until the backend can safely distinguish operator-facing notes from system audit metadata.
- Over-compressing metric cards could reduce status clarity. Keep labels and counts visible.
- Table density changes must not clip long product names or Chinese text.

## 9. Validation Plan

Run:

```powershell
cd frontend
npm run build
```

Run relevant frontend shell tests:

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "project"
```

If a backend summary DTO is added, run targeted backend/API tests:

```powershell
py -m pytest tests/unit/test_project_registry_summary_service.py tests/integration/test_project_registry_summary_api.py -q
```

Manual browser smoke:

1. Open `http://localhost:5173/projects`.
2. Confirm metrics, search, show-cancelled toggle, refresh, `New Project`, pagination, and `Open` remain visible and usable.
3. Confirm no horizontal page overflow at 1280x720.
4. Search by an LTR number, Sample Description, Test Item, Requestor, Business Unit, Status, and Notes value where sample data exists.
5. Toggle `Show cancelled` and confirm hidden-cancelled messaging updates.
6. Confirm table headers include `Sample Description`, `Test Item`, and `Notes`.
7. Confirm table headers do not include `Project Name`, `Product`, or `Recent Activity`.
8. Confirm historical rows without normalized setup fields show `Not recorded` / `None` instead of copied `Product` values or raw JSON.

## 10. Approval Gate

Implementation must wait for explicit user approval.

Suggested approval phrase:

```text
同意按这个方案优化 /projects
```
