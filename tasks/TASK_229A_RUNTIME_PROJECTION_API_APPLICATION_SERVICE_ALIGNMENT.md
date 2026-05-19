# TASK_229A_RUNTIME_PROJECTION_API_APPLICATION_SERVICE_ALIGNMENT

## Status

Complete. Implemented and validated on 2026-05-18.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_229A_RUNTIME_PROJECTION_API_APPLICATION_SERVICE_ALIGNMENT`.

## Why This Task Is Allowed Now

Architecture review identified that runtime projection API route directly calls module-level projection builders, bypassing application service orchestration. This task is a bounded alignment fix.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Small backend layering correction.
- No domain expansion.
- No API contract or UI behavior change.

## Objective

1. Route layer stops directly calling `backend.modules.runtime_projection.*`.
2. Add an application service adapter for runtime projection read-only snapshot retrieval.
3. Keep response payload and API path unchanged.

## Scope

Allowed:

- `backend/application/`
- `backend/api/routes_runtime_projection_read_only.py`
- small wiring changes if needed
- related tests
- task file and board update

Forbidden:

- API schema/path changes
- runtime engine/persistence additions
- UI changes
- domain model changes

## Acceptance Criteria

- Route depends on application service, not module projection builder directly.
- Existing API tests pass without contract change.
- Relevant backend tests pass.

## Validation

```powershell
py -m pytest tests\integration\test_runtime_projection_read_only_api.py tests\unit\test_runtime_projection_read_only_api_mapping.py tests\unit\test_runtime_projection_read_only_api_contract.py -q
```

```powershell
py -m pytest tests\unit\test_runtime_projection_snapshot_adapter.py tests\unit\test_runtime_projection_consumer_views.py tests\unit\test_runtime_projection_token_builder.py tests\unit\test_runtime_projection_composition.py -q
```

Result:

- `py -m pytest tests\integration\test_runtime_projection_read_only_api.py tests\unit\test_runtime_projection_read_only_api_mapping.py tests\unit\test_runtime_projection_read_only_api_contract.py -q` passed (`6 passed`).
- `py -m pytest tests\unit\test_runtime_projection_snapshot_adapter.py tests\unit\test_runtime_projection_consumer_views.py tests\unit\test_runtime_projection_token_builder.py tests\unit\test_runtime_projection_composition.py -q` passed (`45 passed`).
