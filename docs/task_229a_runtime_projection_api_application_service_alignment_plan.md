# TASK_229A Runtime Projection API Application Service Alignment Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_229A_RUNTIME_PROJECTION_API_APPLICATION_SERVICE_ALIGNMENT`
- Allowed now: user-approved architecture risk closure after TASK_228.

## Goal

Align API layering so runtime projection read-only route uses application service orchestration.

## Problem

- Current route imports projection module logic directly.
- This bypasses application-layer boundary rules.

## Minimal Design

1. Add a dedicated application service:
- e.g. `backend/application/runtime_projection_read_only_service.py`
- service method calls existing snapshot adapter/builder from module layer
- service returns current snapshot structure unchanged

2. Update route:
- instantiate/use service
- remove direct module-level call from route body

3. Keep contract stable:
- same endpoint path
- same response model and payload structure

## File-Level Changes

1. `backend/application/runtime_projection_read_only_service.py` (new)
2. `backend/api/routes_runtime_projection_read_only.py` (route now calls service)
3. tests:
- adapt/add focused unit test for route->service dependency if needed
- keep existing integration/contract tests passing

## Risks

- accidental contract drift while moving invocation point
- import cycle risk if service placement is incorrect

## Validation

```powershell
py -m pytest tests\integration\test_runtime_projection_read_only_api.py tests\unit\test_runtime_projection_read_only_api_mapping.py tests\unit\test_runtime_projection_read_only_api_contract.py -q
```

```powershell
py -m pytest tests\unit\test_runtime_projection_snapshot_adapter.py tests\unit\test_runtime_projection_consumer_views.py tests\unit\test_runtime_projection_token_builder.py tests\unit\test_runtime_projection_composition.py -q
```

## Out Of Scope

- new runtime projection semantics
- database/persistence changes
- frontend changes
