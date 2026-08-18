# TASK_315F Follow-up: Project Folder Business Flow Plan

## Scope

Implement the approved Project Folder button flow for Phase 11:

- preview two-layer folder conflicts before creation
- allow explicit backup-and-recreate or overwrite-rebuild strategies
- keep cancel frontend-only
- preserve staged, recoverable template copy semantics
- route `.msg` request attachments to `E-mail`
- keep Matrix, Fee, report, StepInstance, permissions, LAN, and multi-user scope unchanged

## Design

- Extend the official workspace preview/create API with conflict metadata and a create request body.
- Keep destructive choices explicit: the frontend shows the three-choice conflict dialog only when backend preview reports an existing target.
- Implement overwrite through a safe staged replacement: move old target aside, place staged copy, then delete the old target.
- Implement backup through a timestamped sibling backup folder.
- Reuse current official workspace naming, manifest, and repository records.
- Update request-material target planning so confirmed `.msg` attachments copy to `E-mail` instead of `Submitted Material`.

## Files

- `backend/application/official_project_workspace_service.py`
- `backend/api/routes_official_project_workspace.py`
- `backend/application/project_request_material_collection_service.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- related backend/frontend tests

## Validation

- pytest coverage for preview conflicts, backup create, overwrite create, temp cleanup, and `.msg` routing.
- API test coverage for conflict options and create strategy payload.
- React test coverage for conflict dialog and strategy callbacks.
- Existing focused Project Workbench, official workspace, and request material tests must remain green.
