# TASK 009 — Intake and Precheck API

## Goal

Expose application form parsing and precheck through API.

## Scope

- Upload/register application form file.
- Parse and persist ApplicationForm/SampleInfo/FileAsset.
- Run precheck and persist PrecheckResult/Issues.

## Endpoints

- `POST /api/projects/{project_id}/application-form`
- `POST /api/application-forms/{application_form_id}/precheck/run`
- `GET /api/projects/{project_id}/prechecks/latest`
- `PATCH /api/precheck-issues/{issue_id}/resolve`

## Requirements

- Use application services.
- Save uploaded original file under a controlled project/data asset location.
- Do not parse in API route body.
- Return typed responses.

## Tests

- Upload synthetic docx and receive extracted fields.
- Run precheck and receive issues.
- Resolve an issue.

## Out of Scope

- No frontend UI.
- No folder generation.

## Acceptance Criteria

- A project can have a parsed application form and precheck result via API.
