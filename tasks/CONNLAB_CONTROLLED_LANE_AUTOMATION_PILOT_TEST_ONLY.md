# CONNLAB_CONTROLLED_LANE_AUTOMATION_PILOT_TEST_ONLY

Status: administrative_planning_first_complete / pending User / Orchestrator exact governance checkpoint authorization

Lane: `connlab-controlled-lane-automation-pilot-test-only`

## Current Phase And Authority

Current phase: controlled v2 tests-only pilot administrative planning.

Why this task is allowed now:

- the authoritative Controller scan reports registry generation `21` and
  `bootstrap_ready`;
- the pilot lane is absent, so direct dispatch correctly returned `CTL_NO_ACTION` and performed
  no write;
- the User approved only Planner preflight/planning-first;
- production pilot registration, task/worktree creation, role dispatch, implementation, runtime
  mutation, stage, commit, fetch, and push are not authorized in this pass.

The primary worktree and index were clean at planning entry. These four governance edits are an
uncommitted checkpoint candidate, so `register-lane` remains illegal until an exact local
governance checkpoint is separately authorized and the primary/index are clean again.

## Objective

Exercise the complete controlled lane lifecycle with a no-product tests-only change while proving
that the v2 controller remains deterministic, crash-recoverable, single-action, and fail-closed.

## Sole Tests-Only Implementation Candidate

Future implementation May Touch exactly:

`tests/integration/test_connlab_controlled_lane_bootstrapped_pilot.py`

Contract:

- final file is `<=250` UTF-8 physical lines including blanks;
- current accepted baseline is `229` lines;
- the test uses only the public controlled-lane CLI/contracts;
- test fixtures use fake/in-memory native adapters, temporary Git repositories, and temporary
  registry roots;
- no product module, business fixture, real registry, real DB, public drive, attachment, workbook,
  or generated artifact is read or written by the test;
- no second implementation/test path may be added without Planner/User scope expansion.

## Governance May Touch

Governance is limited to these exact paths:

1. `tasks/CONNLAB_CONTROLLED_LANE_AUTOMATION_PILOT_TEST_ONLY.md`
2. `docs/connlab_controlled_lane_automation_pilot_test_only_plan.md`
3. `docs/task_board.md`
4. `docs/lane_evidence/CONNLAB_CONTROLLED_LANE_AUTOMATION_PILOT_TEST_ONLY_planner.md`
5. `docs/lane_evidence/CONNLAB_CONTROLLED_LANE_AUTOMATION_PILOT_TEST_ONLY_developer.md`
6. `docs/lane_evidence/CONNLAB_CONTROLLED_LANE_AUTOMATION_PILOT_TEST_ONLY_reviewer.md`
7. `docs/lane_evidence/CONNLAB_CONTROLLED_LANE_AUTOMATION_PILOT_TEST_ONLY_qa.md`
8. `docs/lane_evidence/CONNLAB_CONTROLLED_LANE_AUTOMATION_PILOT_TEST_ONLY_integrator.md`
9. `docs/lane_evidence/CONNLAB_CONTROLLED_LANE_AUTOMATION_PILOT_TEST_ONLY_reconciliation_planner.md`

The future repository package is therefore at most these nine governance paths plus the sole test
path. Whole-directory or whole-repository staging is forbidden.

## Runtime May Touch

Only after every role/User gate, runtime pilot operations may touch:

- the production registry entry for this exact pilot lane;
- this lane's exact shared-owner, dispatch, callback, completion-authority, and recovery records;
- one native-created Developer task/worktree and its adopted branch/base/HEAD/path/project binding;
- short-lived Planner/Reviewer/QA/Integrator role bindings for this lane;
- one exact local tests-only integration and its residual ledger.

No other lane, owner, binding, task, worktree, branch, registry record, or automation may change.

## Must Not Touch

- all `backend/**`, `frontend/**`, API, schema, database, Matrix, Fee, Office, LTR, and product
  code;
- all business tests other than the sole tests-only candidate;
- real DBs, public drives, attachments, source workbooks, templates, and generated artifacts;
- bootstrap helper/runtime implementation, controlled-lane skill, `AGENTS.md`, and v1 tasks;
- TASK_367A task, branch, worktree, evidence, or retained topology;
- remote push, fetch, migration, archive outside this lane, destructive cleanup, reset, restore,
  clean, or forced retirement.

If the pilot exposes a helper defect, stop without changing the helper and create a separate
corrective proposal.

## Required Gate Chain

The exact role sequence is:

1. Planner administrative planning-first.
2. User authorizes the exact local governance checkpoint.
3. Integrator creates only that local docs checkpoint; primary/index return clean.
4. A later authoritative scan performs one `register-lane` administrative action, creating only
   a `planned` lane.
5. Reviewer plan gate; a blocker returns to the same Planner.
6. User approves Developer planning-first.
7. Developer completes docs-only planning-first.
8. Planner reconciles source of truth.
9. Reviewer implementation-readiness gate.
10. User approves tests-only implementation.
11. Planner reconciles implementation authority.
12. Option A creates one Developer task plus native worktree in one native external action and
    atomically adopts the exact identities.
13. Developer implements the sole test and creates one clean lane checkpoint.
14. Reviewer reviews immutable base-to-lane HEAD; bounded fixes reuse the same Developer task and
    worktree.
15. QA validates the reviewed clean HEAD or exact isolated archive.
16. Integrator packages and locally integrates only the accepted tests-only package with excluded
    residual `0`.
17. Governance closeout, non-force retirement, one-task-per-scan archive, and final heartbeat
    pause proceed only through their separately authorized states.

No role may be skipped. QA is mandatory.

## CAS, Replay, And Recovery

Every dispatch uses the existing six-command journal:

`prepare-dispatch -> mark-invocation-started -> one external action -> record-action-result -> ack-dispatch -> advance-state`

Requirements:

- every mutation uses expected-generation CAS and stable route/operation/idempotency identity;
- each scan/callback performs at most one external action;
- canonical replay returns the existing result without generation drift;
- possible-start uncertainty, missing or ambiguous read-back, stale authority, wrong target,
  owner conflict, and changed payload fail closed with no resend;
- Reviewer/QA bounded fixes reuse the same Developer task/worktree;
- role completion callback is separate from dispatch acknowledgement;
- recovery adopts only one exact durable identity and never guesses from list order or title.

## Validation

Planning and implementation gates must include:

- exact focused test for the sole candidate;
- all bounded `test_connlab_controlled_lane_*.py` unit/integration modules;
- `py_compile` for the candidate and touched controlled-lane Python modules used by the test;
- PowerShell parser checks for existing orchestration wrappers without modification;
- 39 CTL code and six mutation-command parity;
- UTF-8, trailing whitespace, `git diff --check`, line count, exact whitelist, forbidden path,
  clean-index, and product-diff-zero checks;
- immutable checkpoint/archive QA and residual ledger `0`.

## Success, Failure, Stop, And Heartbeat

Success requires accepted local integration, exact evidence, residual `0`, clean lane worktree and
index, drained owner/callback/recovery records, non-force retirement, and authorized short-lived
task archival.

Failure remains recorded and recoverable. No failed or ambiguous action is retried unless durable
pre-invocation proof permits same-ID replay. Scope expansion, helper defect, product diff,
unattributed blocker, nonzero residual, dirty retirement, or destructive operation stops at
Planner/User.

Heartbeat is active only while an authorized pilot action is pending or active. Callback handling
precedes heartbeat scanning. Activation and final `PAUSED` state are separate external actions;
idle completion must end with heartbeat `PAUSED`.

## Current Stop Gate

This pass modifies governance only. It must stop with:

- exact four-path docs-only checkpoint candidate, `415 additions / 69 deletions`;
- index empty;
- no `register-lane`, task/worktree, registry, automation, runtime, stage, commit, fetch, or push;
- next role `User / Orchestrator exact governance checkpoint authorization`.

Suggested local commit message after separate authorization:

`docs(orchestration): plan controlled lane tests-only pilot`
