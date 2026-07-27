# Controlled Lane Automation Tests-Only Pilot Plan

Status: planned-only / not executed

Task: `CONNLAB_CONTROLLED_LANE_AUTOMATION_PILOT_TEST_ONLY`

## Candidate

One file only:

`tests/integration/test_connlab_controlled_lane_bootstrapped_pilot.py`

The candidate is bounded to 250 lines and imports no product module.

## Acceptance Flow

1. Register a planned lane.
2. Reviewer plan gate; blocked returns to the same Planner.
3. User approves planning-first.
4. Developer planning-first and Planner reconciliation.
5. Reviewer implementation-readiness.
6. User approves tests-only implementation.
7. Option A creates one Developer task/worktree and atomically adopts native IDs.
8. Developer writes the sole test and commits a clean lane checkpoint.
9. Reviewer reviews immutable base..HEAD; fix returns to the same Developer/worktree.
10. QA validates clean HEAD/archive.
11. Integrator creates and integrates an exact local tests-only package.
12. Residual ledger must be zero.
13. Governance closeout commits.
14. Owners, callbacks, and recovery points drain.
15. Non-force worktree/branch retirement.
16. Archive one short-lived task per scan.
17. Replay final callback/heartbeat with `CTL_ALREADY_APPLIED` or `CTL_NO_ACTION`.
18. Pause idle heartbeat as the final action.

## Stop Conditions

Stop and return to User for dirty Git state, authority drift, partial registry, stale CAS,
ambiguous native read-back, owner/scope conflict, product diff, non-bounded blocker, nonzero
residual, failed clean retirement, or any need for push, migration, public data, or destructive
cleanup.

## Current Boundary

This plan does not authorize the real pilot. The repository test characterizes only the public CLI
against temporary Git and registry state with fake identities.
