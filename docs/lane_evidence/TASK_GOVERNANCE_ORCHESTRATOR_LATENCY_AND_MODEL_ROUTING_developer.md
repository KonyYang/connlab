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
- `py -m pytest tests/integration/test_connlab_execution_gate_recovery.py tests/integration/test_connlab_serial_complex_recovery.py -q` — 9 failed, 8 passed. The failures split exactly:
  - `test_run_task_activate_next_starts_only_the_fifo_head_and_accepts_json` is a stale V1 test. It
    supplies unsupported `-ActivateNext` to the current `scripts/run_task.ps1`, receives empty stdout,
    then fails JSON decoding.
  - The other eight failures are in `test_connlab_serial_complex_recovery.py`. Its `init_v2_repo`
    fixture copies the current active `docs/task_board.md`; each temporary repository therefore correctly
    returns `BLOCKED_ACTIVE_TASK_RUNNING` before its flow can create a separate active task.

## Scope proof

`git diff --name-only 3d0884e12cc39e7b416da75ab01aaffd36c6418c..HEAD` contains neither integration test,
`scripts/run_task.ps1`, any runtime helper, nor `docs/task_board.md`. The committed diff is limited to
the three approved implementation paths and this Developer evidence path.
