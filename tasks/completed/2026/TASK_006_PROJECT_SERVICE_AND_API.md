# TASK 006 — Project Service and API

## Goal

Implement project creation/list/detail through application service and API routes.

## Scope

- Application service for Project.
- FastAPI routes for project CRUD subset.

## Requirements

- `backend/application/project_service.py`.
- `backend/api/routes_project.py`.
- Register routes in FastAPI app.
- Typed Pydantic request/response models.
- Thin route bodies.

## Endpoints

- `POST /api/projects`
- `GET /api/projects`
- `GET /api/projects/{project_id}`

## Tests

- API smoke tests with temp DB dependency override.
- Service unit tests if practical.

## Out of Scope

- No application form upload.
- No folder generation.

## Acceptance Criteria

- Can create and retrieve a project through API.
- Project status defaults to DRAFT or PRECHECK_REQUIRED based on request design.
