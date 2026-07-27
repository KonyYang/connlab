# CONNLAB_CONTROLLED_LANE_AUTOMATION_PILOT_TEST_ONLY

Status: planned-only / runtime pilot not authorized

Lane: `connlab-controlled-lane-automation-pilot-test-only`

## Objective

Exercise a future bootstrapped controller through the complete controlled role flow using one new
non-product test file.

## Sole Candidate

- `tests/integration/test_connlab_controlled_lane_bootstrapped_pilot.py`
- maximum 250 physical lines
- public CLI, temporary Git repository, temporary registry, and fake native adapter only

## Runtime Flow

Planner -> Reviewer plan gate -> User planning approval -> Developer planning-first -> Planner
reconciliation -> Reviewer readiness -> User tests-only implementation approval -> native-created
Developer task/worktree -> Developer checkpoint -> Reviewer -> QA -> Integrator -> local master
integration -> evidence closeout -> non-force retirement -> one-task-per-scan archive -> idle
heartbeat pause.

## Locks

No bootstrap helper correction, product code/test, real business data, public drive, remote push,
migration, v1 retirement, or TASK_367A cleanup. A helper defect stops the pilot and opens a
separate corrective task.

## Gate

The real pilot requires bootstrap acceptance, production `bootstrap_ready`, and a separate User
approval. The current integration test is characterization only.
