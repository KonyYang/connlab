# ConnLab Controlled Lane V2 Bootstrap Implementation Plan

Status: implementation/governance complete at `62ded429`; runtime bootstrap blocked by planned-only `CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_THREAD_TITLE_CORRECTIVE`

Task: `CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_BOOTSTRAP`

## 1. Delivery Boundary

This lane implements and tests the bootstrap surface. It does not execute production bootstrap.
All tests use disposable registry roots, temporary Git repositories, and fake native identities.

## 2. Architecture

### `bootstrap.py`

Owns:

- canonical controller and heartbeat constants;
- genesis and planned-lane payload validation;
- administrative mutation projections;
- bootstrap-only action/transition selection;
- native controller/heartbeat/dry-run target and read-back validation;
- atomic adoption facts applied by the existing registry transaction.

It calls no native API, subprocess, network, automation, worktree, or product service.

### Existing modules

- `contracts.py`: two-command administrative catalog; no new error codes.
- `registry.py`: delegates administrative mutations and bootstrap acknowledgement inside the
  existing token lock, CAS, idempotency ledger, and atomic write.
- `cli.py`: exposes the commands and retains one canonical JSON response.
- `state_machine.py`: delegates bootstrap states/actions while preserving the normal lane table.
- controlled-lane skill: documents native adapter, heartbeat, and separate runtime gates.

## 3. TDD Order

1. Baseline original bounded suite.
2. RED for missing bootstrap module and administrative catalog.
3. GREEN for genesis, exact replay, planned registration, digest validation, and owner conflict.
4. RED for controller post-create ID adoption.
5. GREEN for prepare/start/result/read-back/ack/advance.
6. Run the original bounded suite to detect regression.
7. Add disposable public-CLI pilot characterization.
8. Run combined focused and full bounded verification.

## 4. Registry Genesis

Genesis accepts only:

- expected generation `0`;
- state `bootstrap_controller_pending`;
- exact repository and Git-common-dir fingerprint supplied by the store;
- authority-file map and canonical digest;
- read-only legacy inventory and canonical digest;
- `migration.status=not_required` with the same source digest;
- canonical controller and paused heartbeat values.

The existing `RegistryStore` creates the root only after validation, obtains a token lock, writes a
same-directory fsynced temporary file, writes recovery intent, atomically replaces, rereads, and
verifies the digest. Generation becomes `1`.

## 5. Planned Lane Registration

Registration requires an existing v2 registry, expected-generation CAS, exact planned state,
base/root/scope/owner/authority digests, and no conflict with active shared owners. It writes
`implementation_authorized=false`. Review and User gates remain normal journal events.

## 6. Bootstrap Native Lifecycle

Controller creation uses one prepared target containing canonical title, project, repository,
prompt, route, operation, and scope identity. It contains no invented thread ID.

After invocation:

1. record the native receipt;
2. read back exactly one matching task;
3. validate title and project binding;
4. acknowledge and atomically store the real thread ID;
5. advance to heartbeat pending.

Heartbeat creation and zero-write dry-run use the same journal pattern. Bootstrap-ready produces
`CTL_NO_ACTION`.

## 7. Heartbeat Policy

- callback before scan;
- recurrence `FREQ=MINUTELY;INTERVAL=5`;
- creation state `PAUSED`;
- activation only while active/pending/recovery work exists;
- idle pause as its own final action;
- no approval, scope expansion, archive, push, or cleanup authority.

This lane records the contract and validation helpers only; it does not create an automation.

## 8. Legacy Inventory And Rollback

Legacy role and TASK_367A identities are read-only and remain authoritative. No v1 schema
conversion runs. Unexpected migration/recovery facts fail closed.

Runtime rollback, if later authorized:

1. pause heartbeat;
2. pause controller without archive;
3. retain registry, journal, evidence, and worktrees;
4. return authority to v1;
5. perform no deletion/reset/restore/clean.

## 9. Tests-Only Pilot Asset

`tests/integration/test_connlab_controlled_lane_bootstrapped_pilot.py` is a bounded public-CLI
characterization. It:

- initializes a temporary Git repository;
- proves administrative dry-run is zero-write;
- bootstraps a temporary registry;
- registers a planned tests-only lane;
- verifies the next action is the exact Reviewer binding;
- performs no product import or native side effect.

The real pilot role chain remains unexecuted and separately gated.

## 10. Verification

```powershell
py -m pytest tests/unit/test_connlab_controlled_lane_*.py `
  tests/integration/test_connlab_controlled_lane_dry_run.py `
  tests/integration/test_connlab_controlled_lane_bootstrapped_pilot.py -q
```

Also run:

- Python compilation for controlled-lane modules/tests;
- PowerShell parser for controlled-lane scripts;
- 39-code parity;
- line, UTF-8, trailing, diff, whitelist, forbidden-scope, and no-real-registry scans;
- primary and retained TASK_367A worktree preservation checks.

## 11. Stop Conditions

Stop without runtime action on dirty primary/index, partial registry, recovery marker, stale CAS,
ambiguous native read-back, owner conflict, scope expansion, product path diff, unexpected test
failure, or any need for network/migration/destructive cleanup.

## 12. Reviewer And QA Acceptance

Reviewer implementation re-gate passed for clean checkpoint
`08f99cdec1d9f7ca0de802109089b70105a17ad3`. Isolated QA then passed the exact reviewed
`3614a6d12e56e02420b47d8dbe0fc6251c52bb37..08f99cdec1d9f7ca0de802109089b70105a17ad3`
candidate: 32 paths, `1975/48`, bounded `166 passed`, TOCTOU direct/adjacent `18 passed`,
py_compile, three PowerShell parsers, 39-code/six-command parity, line caps, UTF-8, trailing, and
`git show --check`.

The QA evidence and this reconciliation are docs-only overlays on paths already present in the
reviewed 32-path set; they do not expand implementation May Touch. At QA handoff, Integrator was
required to audit the exact 32-path base-to-final-tree package at `2136/48`, while retaining
`1975/48` as the reviewed implementation-only checkpoint fact. That audit later passed as recorded
below. Production bootstrap, pilot execution, and every real task/worktree/registry/automation
side effect remain unauthorized.

## 13. Local Integration Acceptance

Reviewer, QA, and Integrator accepted the lane. Implementation checkpoint
`08f99cdec1d9f7ca0de802109089b70105a17ad3` and governance commit
`91c6b42564c1ef030761bd9c757889159e438974` form the final exact 32-path, `2136/48`
base-to-master package; excluded residual is zero. Local master and lane HEAD both resolve to
`91c6b42564c1ef030761bd9c757889159e438974`; at Integrator acceptance both worktrees and indexes
were clean. This reconciliation changes only task-owned governance documents, keeps the index
empty, and leaves the lane worktree clean.

The local `origin/master` tracking ref remains unfetched at
`3614a6d12e56e02420b47d8dbe0fc6251c52bb37`; local comparison is behind `0`, ahead `5`, and does
not assert current remote state. Production registry/controller/heartbeat, real bootstrap, pilot,
native task/worktree/automation effects, fetch, and push remain unexecuted and unauthorized.

## 14. Runtime Title Corrective Dependency

Runtime activation remains blocked by
`CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_THREAD_TITLE_CORRECTIVE`. The native create operation
cannot set the canonical controller title, so title mutation/read-back must become its own
journaled state/action before heartbeat creation. The failed runtime attempt stopped before
registry genesis; after corrective acceptance and a separate User runtime gate, bootstrap restarts
from proven registry absence.
