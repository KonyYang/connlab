# TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING — Developer Evidence

MODEL: gpt-5.6-terra
REASONING_EFFORT: medium
MODEL_ROUTE_REASON: default_complex

## Scope

Implemented only the approved governance documentation and bounded unit-contract test paths. The board
is authority-only and was not edited in this lane. No runtime, schema, product, API, persistence,
authority, public-drive, browser, remote, or lifecycle-cleanup change was made.

## Delivered contract

- Frozen V2 Submit, Approve, and Close payload guidance, including the ten-key versus nine-key
  forbidden-category boundary and no schema retry.
- Explicit Terra default, deterministic QA low/medium rule, frozen Sol escalation conditions, and
  forbidden-Luna rule.
- Required role evidence audit fields and final `ACTUAL_MODEL_ROUTING` reconciliation contract.
- Direct simple path, durable recovery reuse/fail-closed behavior, and conditional deterministic UI
  smoke rule.
- Executable classifier/approved-validator and PowerShell action-mapping regression tests.

## Validation

- `py -m pytest tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q` — passed: 7 tests.
- `git diff --check` — passed.
- `py -m pytest tests/integration/test_connlab_execution_gate_recovery.py tests/integration/test_connlab_serial_complex_recovery.py -q` — baseline fixture failure: 9 failed, 8 passed. The
  fixture copies the current V2 board, which is already `running` for this active task; its temporary
  repositories therefore correctly return `BLOCKED_ACTIVE_TASK_RUNNING` before the test flow can create
  its own active task. No runtime or implementation path was changed to influence this result.
