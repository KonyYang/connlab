# TASK 010 — LTR Module

## Goal

Implement LTR registration and history lookup.

## Scope

- Application service.
- Repository usage.
- API routes.

## Endpoints

- `POST /api/projects/{project_id}/ltr`
- `GET /api/projects/{project_id}/ltr`
- `GET /api/ltr-records?query=...`

## Requirements

- LTR number is required.
- A project may have one active registered LTR in MVP.
- Save requested_by, requested_date, notes.
- Update Project status to LTR_REGISTERED when appropriate.

## Tests

- Register LTR for project.
- Retrieve LTR.
- Prevent duplicate active LTR unless update behavior is explicitly designed.

## Out of Scope

- No automatic Outlook extraction.
- No LTR application form auto-fill.

## Acceptance Criteria

- LTR can be registered and queried.
