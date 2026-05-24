# TASK_209 Runtime Projection Read-Only Frontend Consumer Prototype Minimal Slice

Status: done
Date: 2026-05-16

## Execution Mode

Single-file task mode.

This file contains both:

- the reviewable task plan
- the later execution record

Do not create a separate `docs/task_209_*_plan.md` file for this task.

Approval rule:

- Before approval, only this task file may be reviewed and adjusted.
- After explicit user approval, implementation may proceed directly from this task file.
- After implementation, append the execution result to the `Execution Record` section and update `docs/task_board.md`.

## Current Phase / Active Task / Allowance

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

Current active task:

```text
TASK_209_RUNTIME_PROJECTION_READ_ONLY_FRONTEND_CONSUMER_PROTOTYPE_MINIMAL_SLICE pending user review
```

Why this task is allowed:

- TASK_205 created a deterministic runtime snapshot adapter.
- TASK_206 exposed read-only runtime projection API.
- TASK_208 hardened API typed response contracts.
- The next minimal consumable slice is a frontend read-only consumer prototype that verifies real consumption flow from typed runtime projection APIs.

## Model Fit Assessment

Recommended execution model:

```text
GPT-5.3-codex: suitable
```

Reason:

- The task is a bounded integration slice: API client + typed mapping + read-only rendering prototype.
- No runtime engine, persistence, or domain refactor is expected.
- Risk is mostly frontend state and contract wiring, which is manageable with focused tests/smoke checks.

Escalate to a stronger model only if frontend architecture constraints conflict with current runtime projection boundaries.

## Goal

Create a minimal frontend read-only consumer prototype for runtime projection snapshot output, using the typed API contract from TASK_208.

## Scope

TASK_209 should provide:

- a typed frontend API client call for `POST /api/runtime-projection/read-only-snapshot`
- minimal read-only UI prototype surface for:
  - matrix overview groups/tokens
  - optional selected step workspace projection
  - parser warnings visibility
- deterministic loading/empty/error states for prototype validation

This task is a prototype slice, not Workbench replacement.

## UI Boundary

Must follow:

- current Project Workbench is temporary shell and not a refinement target
- no Matrix Editor embedding into Workbench
- no setup-heavy panel expansion

TASK_209 prototype should be isolated and read-only:

- standalone route/page/feature module for validation
- no mutation controls
- no execution write actions

## File Scope

Allowed implementation files:

- `frontend/src/api/runtimeProjectionClient.ts`
- `frontend/src/features/runtimeProjectionReadOnly/*` (typed model, mapper, hook, prototype view)
- `frontend/src/routes/*` (minimal route wiring only if needed)
- `tests/unit/test_frontend_shell_files.py` (static scope checks if needed)
- `tasks/TASK_209_RUNTIME_PROJECTION_READ_ONLY_FRONTEND_CONSUMER_PROTOTYPE_MINIMAL_SLICE.md`
- `docs/task_board.md`

Avoid changing unless proven necessary:

- `backend/modules/runtime_projection/*`
- `backend/api/routes_runtime_projection_read_only.py`
- existing Workbench core pages outside prototype entry

## Forbidden Scope

TASK_209 must not implement:

- runtime engine/orchestration
- persistence/schema/ORM/API write changes
- StepInstance implementation
- report sync engine
- evidence/image storage
- notification system
- Matrix authority mutation
- Project lifecycle mutation
- full Workbench replacement
- Matrix Editor rebuild

## Validation Strategy

Focused validation should cover:

- typed API response consumption in frontend client
- deterministic render of group/token summary
- deterministic render for selected-token found vs not-found
- parser warnings visibility
- no write actions exposed

Run (expected direction; exact commands depend on existing frontend test harness):

```powershell
npm run build
py -m pytest tests\unit\test_frontend_shell_files.py -q
```

If board-state tests are updated:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

## Acceptance Criteria

TASK_209 is complete when:

- frontend can call typed runtime projection read-only API successfully
- prototype view renders matrix overview + optional step workspace projection
- parser warnings are visible in prototype
- no write/mutation behavior is introduced
- no backend runtime behavior changes are required
- `docs/task_board.md` is updated after completion

## Execution Record

Completed.

Implemented files:

- `frontend/src/api/client.ts`
- `frontend/src/features/runtime-projection-read-only/useRuntimeProjectionPrototype.ts`
- `frontend/src/features/runtime-projection-read-only/RuntimeProjectionPrototypeView.tsx`
- `frontend/src/pages/RuntimeProjectionPrototypePage.tsx`
- `frontend/src/runtime-projection-prototype.css`
- `frontend/src/App.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/layout/TopBar.tsx`

Board/document updates:

- `docs/task_board.md`

What was implemented:

- Added typed frontend client models and API call for:
  - `POST /api/runtime-projection/read-only-snapshot`
- Added isolated read-only runtime projection prototype feature:
  - deterministic snapshot fetch
  - matrix overview group/token rendering
  - parser warnings rendering
  - optional step workspace rendering via token selection
- Added route wiring:
  - `/runtime-projection`
  - sidebar navigation entry `Runtime Prototype`
  - top bar route title mapping
- Preserved scope:
  - no Workbench replacement
  - no backend runtime changes
  - no write/mutation actions

Validation results:

- `npm run build` (frontend)
  - passed
- `py -m pytest tests\unit\test_frontend_shell_files.py -q`
  - has existing historical failures outside TASK_209 scope (legacy expectation mismatches around Workbench/Intake static assertions)

Stop condition:

- TASK_209 completed and stopped.
- Did not auto-enter next task.
