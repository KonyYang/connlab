# CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_BOOTSTRAP

Status: implementation/governance complete at `62ded429`; runtime bootstrap blocked by planned-only `CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_THREAD_TITLE_CORRECTIVE`

Lane: `connlab-controlled-lane-orchestration-v2-bootstrap`

## Objective

Add the deterministic production bootstrap surface for the accepted controlled-lane v2 helper
without activating production runtime state. The candidate must support registry genesis,
planned-only lane registration, controller/heartbeat bootstrap states, exact native read-back
adoption, zero-write dry-run, and a disposable tests-only pilot characterization.

## Runtime Separation

This implementation task does not authorize:

- creating `<git-common-dir>/connlab-controlled-lane/registry-v2.json`;
- creating `ConnLab｜研发任务编排与集成主控 v2`;
- creating or activating `ConnLab v2 controlled-lane scan`;
- creating a real pilot task, branch, or worktree;
- migration, archive, cleanup, fetch, or push.

Those effects require separate runtime gates after implementation acceptance.

Runtime bootstrap is additionally blocked by
`CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_THREAD_TITLE_CORRECTIVE`: native `create_thread` cannot
set the canonical controller title, and the accepted state machine has no independent journaled
`set_thread_title` action. The failed runtime attempt stopped before registry genesis and left no
runtime state to adopt.

## May Touch

- this task, its plan, board hunk, and role evidence;
- `docs/project_management/CONTROLLED_LANE_ORCHESTRATION_V2.md`;
- `docs/project_management/ROLE_THREAD_REGISTRY.md`, status-only v2 binding section;
- `AGENTS.md`, controlled-v2 status/rules only;
- `.agents/skills/connlab-controlled-lane/SKILL.md`;
- `scripts/connlab_controlled_lane/bootstrap.py`, maximum 300 physical lines;
- bounded bootstrap hunks in `contracts.py`, `registry.py`, `cli.py`, and `state_machine.py`;
- `tests/unit/test_connlab_controlled_lane_bootstrap.py`, maximum 300 lines;
- bounded additions to existing controlled-lane contract/registry/state/integration tests;
- `tests/integration/test_connlab_controlled_lane_bootstrapped_pilot.py`, maximum 250 lines;
- planned-only pilot governance and pending role evidence.

## Must Not Touch

- `backend/**`, `frontend/**`, API, schema, database, Matrix, Fee, LTR, Office, or product tests;
- `.agents/skills/connlab-lane-orchestrator/**`;
- `scripts/_codex_runtime.ps1` or credential/config-copy behavior;
- v1 controller and existing role tasks;
- TASK_367A task, branch, worktree, or files;
- real DB, public drive, attachments, workbooks, generated output, or operator files;
- remote actions or destructive Git commands.

## Administrative Commands

`bootstrap-registry`:

- is legal only for an absent registry-v2 with no recovery marker;
- validates repository, authority, legacy inventory, migration, controller, and heartbeat identity;
- creates generation `1` using the existing lock/CAS/atomic-write implementation;
- returns `CTL_ALREADY_APPLIED` for exact replay without generation change;
- fails closed for mismatched existing state, stale generation, changed payload, lock, or recovery.

`register-lane`:

- creates only state `planned`;
- records base, scope, authority, and owner digests;
- cannot record implementation approval;
- rejects changed scope, owner conflict, stale authority, and changed replay;
- leaves owner acquisition to the normal reviewed lane flow.

No new `CTL_*` codes are allowed. The catalog remains 39.

## Bootstrap State

```text
bootstrap_controller_pending
-> bootstrap_heartbeat_pending
-> bootstrap_dry_run_pending
-> bootstrap_ready
```

Each native or Git effect uses the ordinary six-command journal and one external action. Controller
prepare does not invent a thread ID. Receipt and exact read-back provide the ID adopted during
acknowledgement. Role completion remains a later event.

The controller title, heartbeat name, recurrence, and initial state are fixed:

- `ConnLab｜研发任务编排与集成主控 v2`;
- `ConnLab v2 controlled-lane scan`;
- `FREQ=MINUTELY;INTERVAL=5`;
- `PAUSED`.

## Legacy Inventory

No v1 machine registry is expected. Bootstrap records:

- `migration.status = not_required`;
- source digest from the role registry;
- v1 role tasks and TASK_367A as `legacy_retained`.

Any unexpected v1 registry, partial v2 registry, recovery marker, stale lock, or unreadable
topology stops the operation.

## Verification

- original bounded controlled-lane suite remains green;
- bootstrap and disposable pilot tests pass;
- six mutation commands and two administrative commands retain direct dry-run/idempotency coverage;
- all 39 codes retain their exit classes;
- Python compilation and PowerShell parser checks pass;
- `bootstrap.py <= 300`, bootstrap unit test `<= 300`, pilot test `<= 250`;
- whitelist, UTF-8, trailing, and `git diff --check` pass;
- production registry is absent and no real native/runtime side effect occurred.

## Local Integration Acceptance

Reviewer implementation re-gate and isolated QA passed for reviewed checkpoint
`08f99cdec1d9f7ca0de802109089b70105a17ad3`. The reviewed implementation candidate is exactly
32 paths and `1975/48`; the QA reconciled base-to-final-tree package remains those 32 paths and is
exactly `2136/48`. Integrator accepted and integrated the governance-complete package as
`91c6b42564c1ef030761bd9c757889159e438974`; excluded residual is zero and local master equals the
lane HEAD. Production registry/controller/heartbeat, real bootstrap, and the real pilot remain
unstarted and require separate User authorization.
