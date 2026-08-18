# TASK_330A_PROJECT_BASIC_INFORMATION_AUTHORITY_DATA_API

## Status

Complete. Implemented and review follow-up validated on 2026-06-20.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Allowed

TASK_330 is an umbrella candidate for Project Basic Information authority. TASK_330A is the first safe implementation slice because it creates only the backend authority data/API boundary and does not change Workbench UI or formal file outputs.

## Goal

Create the backend authority model and API for Project Basic Information:

- assemble an unconfirmed draft for existing and new projects,
- preserve operator draft edits,
- confirm an authoritative version,
- expose review/changed-source state.

## Inputs

- Project id.
- Existing project/LTR identity.
- Parsed application form/intake fields.
- Operator draft edits.

Matrix authority date suggestions and current Fee authority total remain future
provider inputs for later tasks; TASK_330A does not read Matrix/Fee sources.

## Outputs

- Basic Information draft.
- Latest confirmed Basic Information snapshot.
- Status: `unconfirmed`, `confirmed`, or `needs_review`.
- Field-level source suggestions/review metadata.
- Business-readable blockers and missing required fields.

## Required Merge Rules

Draft assembly priority:

1. Existing unconfirmed operator draft values.
2. Latest confirmed Basic Information snapshot values.
3. Current source suggestions from application form / intake.
4. Current source suggestions from Project/LTR identity.

Later tasks may add Matrix authority dates and Fee authority total as additional
source providers. TASK_330A does not read those sources.

Source changes must never silently overwrite operator draft values or confirmed values. Differences become field-level suggestions and may set `needs_review`.

## Required Confirmation Fields

Confirm must require:

- DL/LTR number,
- project type,
- product description or description P/N,
- test item,
- requested by,
- project leader,
- lab performing the tests.

Other fields may remain blank.

## Backend API

Add typed Project-scoped routes:

```text
GET  /api/projects/{project_id}/basic-information
PUT  /api/projects/{project_id}/basic-information/draft
POST /api/projects/{project_id}/basic-information/confirm
```

Routes must be thin and call application services.

## In Scope

- Domain/application DTOs for Basic Information.
- Persistence model/repository for draft and confirmed versions.
- Source assembly service.
- Draft save service.
- Confirm service.
- Review status and field-level source suggestion metadata.
- FastAPI routes and Pydantic request/response models.
- Unit and API tests.

## Out Of Scope

- No Workbench top button or page.
- No frontend editor.
- No project folder blocker.
- No Fee form, Customer Feedback form, or Word output consumption.
- No LTR workbook writeback.
- No report generation.
- No Matrix/Fee authority semantic changes.

## Acceptance Criteria

- Existing projects with no confirmed snapshot return an assembled unconfirmed draft.
- Draft save preserves operator edits.
- Re-reading after source changes does not overwrite saved draft values.
- Confirm validates required fields and returns business-readable missing-field labels.
- Confirm writes a new version and keeps previous confirmed versions.
- Source differences after confirmation produce `needs_review`/field suggestions rather than changing confirmed data.
- API responses are typed and do not expose storage internals.

## Validation

```powershell
py -m pytest tests/unit/test_project_basic_information_service.py tests/unit/test_project_basic_information_repository.py tests/integration/test_project_basic_information_api.py -q
py -m pytest tests/unit/test_database.py -q
```

Results:

- `17 passed` for Project Basic Information service, repository, and API tests.
- `5 passed` for database/init_db tests.

Review follow-up fixed:

- required-field validation now treats `product_description` and `description_pn`
  as an either/or business rule;
- `needs_review` now compares the confirmed source signature with the current
  source signature, not confirmed operator values with source suggestions;
- confirmed version numbering is delegated to the repository and duplicate
  version writes are translated into a business error.

## Stop Point

Stop after TASK_330A is implemented and validated. Do not start TASK_330B without explicit user approval.
