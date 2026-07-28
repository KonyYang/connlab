# CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_BOOTSTRAP Developer Evidence

Status: local implementation integrated and accepted at `91c6b425` / exact 9-path docs-only closeout candidate `102/32` / pending Reviewer docs-only closeout re-gate; real bootstrap pending User authorization

Branch: `lane/connlab-controlled-lane-orchestration-v2-bootstrap`

Bounded-fix base: `b92ee61517fd200cd37945095ca932c05d437881`

## Register-Lane Token-Lock Revalidation

- The first administrative preflight now returns a canonical observation digest containing the
  resolved repository root, actual Git/common-dir/HEAD/clean/index facts, and verified authority
  file digests.
- `RegistryStore` carries that frozen observation into `_execute_locked()`. After acquiring the
  token-owned registry lock and before `load()`, mutation, or write, it repeats the same real
  repository and authority observation and compares the result with the frozen digest.
- A changed authority file fails with `CTL_EVIDENCE_STALE`; a clean new commit that leaves
  authority unchanged fails with `CTL_HEAD_MISMATCH`. Other observation drift fails with the
  existing `CTL_TOPOLOGY_STALE`.
- Both deterministic races use disposable Git repositories. The controlled test hook mutates only
  after the real token lock is acquired. Each failure leaves generation `0`, creates no lane, and
  releases the token lock.

Direct RED:

```text
py -m pytest tests/unit/test_connlab_controlled_lane_registry.py::
  test_register_lane_revalidates_repository_inside_token_lock -q
2 failed in 1.73s
```

Direct/adjacent GREEN:

```text
py -m pytest tests/unit/test_connlab_controlled_lane_registry.py::
  test_register_lane_revalidates_repository_inside_token_lock \
  tests/unit/test_connlab_controlled_lane_bootstrap.py \
  tests/integration/test_connlab_controlled_lane_dry_run.py::
  test_register_lane_preflight_rejects_unverified_repository_authority -q
18 passed in 15.20s
```

Final bounded result: `166 passed in 39.62s`.

## Register-Lane Preflight Fix

- `register-lane` now enters the same fail-closed administrative preflight as registry genesis
  before lock acquisition or any registry mutation.
- The preflight resolves the caller's actual repository, derives the Git-common-dir fingerprint,
  and compares it with the canonical primary root, request fingerprint, and store fingerprint.
- A clean worktree and index are required. The submitted base commit must equal the observed clean
  repository HEAD, so both nonexistent and stale bases fail with `CTL_HEAD_MISMATCH`.
- Authority paths are read from the observed repository and SHA-256 verified before CAS mutation;
  missing or forged authority fails with `CTL_EVIDENCE_STALE`.
- Wrong root, missing/forged authority, and nonexistent/stale base all leave generation unchanged
  and do not create a lane record. Existing 39-code, admin CAS, replay, and planned-only semantics
  are unchanged.

Direct RED:

```text
py -m pytest tests/integration/test_connlab_controlled_lane_dry_run.py::
  test_register_lane_preflight_rejects_unverified_repository_authority -q
5 failed in 2.37s
```

Direct GREEN and adjacent bootstrap coverage:

```text
py -m pytest tests/integration/test_connlab_controlled_lane_dry_run.py::
  test_register_lane_preflight_rejects_unverified_repository_authority \
  tests/unit/test_connlab_controlled_lane_bootstrap.py -q
16 passed in 11.10s
```

Final bounded command:

```powershell
$unit = @(Get-ChildItem tests\unit -Filter 'test_connlab_controlled_lane_*.py' |
  ForEach-Object { $_.FullName })
py -m pytest @unit `
  tests\integration\test_connlab_controlled_lane_dry_run.py `
  tests\integration\test_connlab_controlled_lane_bootstrapped_pilot.py -q
```

Result: `164 passed in 37.35s`.

## Bounded Fix

- Bootstrap acknowledgement now binds the exact prepared `task_id`, `lane_id`, `route_id`,
  `scope_fingerprint`, and operation lookup before bootstrap-specific read-back adoption.
- Authoritative prepare derives controller, heartbeat, and zero-write dry-run target facts from
  registry state. Controller project/repository/prompt facts, the adopted controller thread,
  heartbeat name/RRULE/`PAUSED` state, and dry-run zero-action scope cannot be caller-substituted.
- `bootstrap-registry` preflights a real disposable Git repository before creating the registry
  root. It derives the Git-common-dir fingerprint, resolves the canonical repository root, verifies
  clean worktree/index state, hashes authority and legacy source files, and checks recovery/lock
  state before generation `1`.
- Invalid repository fingerprint, wrong root, missing authority, and forged authority digest are
  zero-write and leave no registry directory or file.
- The bootstrap lifecycle tests were mechanically moved from the oversized dry-run integration
  module to the bounded registry unit module. Assertions and disposable `RegistryStore` behavior
  are unchanged; every candidate Python file satisfies the `<=500` hard limit. The dry-run
  integration module is exactly `500` blank-inclusive physical lines, not below `500`.

No production registry, controller, heartbeat, task, worktree, automation, migration, archive,
network, or product-data side effect was executed.

## TDD Evidence

Reviewer fresh pre-fix baseline:

```text
149 passed in 23.08s
```

Local RED:

- disposable pilot genesis negatives: `3 failed, 1 passed`; forged fingerprint, wrong root, and
  missing authority all incorrectly wrote generation `1`;
- prepared-request acknowledgement matrix: `4 failed`; task/route/scope were accepted and a wrong
  lane leaked `KeyError`;
- Reviewer canonical-target probes established that controller/heartbeat/dry-run target changes
  were accepted before the fix.

Focused GREEN:

```text
py -m pytest tests/unit/test_connlab_controlled_lane_bootstrap.py \
  tests/unit/test_connlab_controlled_lane_state_machine.py::test_bootstrap_prepare_rejects_targets_changed_from_canonical_registry_state \
  tests/unit/test_connlab_controlled_lane_registry.py::test_bootstrap_controller_ack_adopts_exact_readback \
  tests/unit/test_connlab_controlled_lane_registry.py::test_bootstrap_ack_rejects_changed_prepared_request_identity \
  tests/integration/test_connlab_controlled_lane_bootstrapped_pilot.py -q
```

Result: `26 passed`.

Final bounded command:

```powershell
$unit = @(Get-ChildItem tests\unit -Filter 'test_connlab_controlled_lane_*.py' |
  ForEach-Object { $_.FullName })
py -m pytest @unit `
  tests\integration\test_connlab_controlled_lane_dry_run.py `
  tests\integration\test_connlab_controlled_lane_bootstrapped_pilot.py -q
```

Result: `160 passed in 28.42s`.

The old `154` evidence count was stale. Reviewer independently established the real pre-fix
baseline as `149`; this pass adds eleven direct cases and removes one redundant selector-only case
that is subsumed by the three-stage canonical-target matrix, yielding the final `160`.

## Static Validation

- `py_compile`: passed for all changed runtime and test modules.
- PowerShell parser: zero errors for `connlab_controlled_lane.ps1`,
  `connlab_lane_worktree.ps1`, and `task_complete_commit.ps1`.
- Stable catalogs: `39` `CTL_*` codes and `6` mutation commands.
- `git diff --check`: passed; only expected Git LF/CRLF notices were emitted.
- strict UTF-8 invalid files: `0`; trailing-whitespace hits: `0`.
- candidate whitelist: `9` exact paths including this evidence; forbidden product paths: `0`.
- staged index before checkpoint assembly: empty.
- production Git-common-dir registry path:
  `D:\PythonProject\connlab\.git\connlab-controlled-lane`: absent.
- retained TASK_367A worktree remains at
  `C:\Users\White\.codex\worktrees\705b\connlab`, branch
  `lane/task-367a-matrix-editor-live-xlsx-export`, HEAD
  `53840b42ea73358c31fe40c5225646363d485829`.

Blank-inclusive UTF-8 physical lines:

| Path | Lines |
|---|---:|
| `scripts/connlab_controlled_lane/bootstrap.py` | 300 |
| `scripts/connlab_controlled_lane/contracts.py` | 300 |
| `scripts/connlab_controlled_lane/registry.py` | 350 |
| `scripts/connlab_controlled_lane/state_machine.py` | 280 |
| `tests/unit/test_connlab_controlled_lane_bootstrap.py` | 300 |
| `tests/unit/test_connlab_controlled_lane_registry.py` | 485 |
| `tests/unit/test_connlab_controlled_lane_state_machine.py` | 367 |
| `tests/integration/test_connlab_controlled_lane_dry_run.py` | 500 |
| `tests/integration/test_connlab_controlled_lane_bootstrapped_pilot.py` | 229 |

At Developer handoff, Reviewer was asked to review this evidence's containing lane checkpoint
commit. Developer performed no fetch, push, runtime bootstrap, pilot activation, QA, Integrator
action, or merge; the subsequent gate status below supersedes that routing checkpoint.

## Post-Implementation Gates

Reviewer implementation re-gate passed for checkpoint
`08f99cdec1d9f7ca0de802109089b70105a17ad3`. Isolated QA subsequently passed the exact reviewed
32-path `1975/48` candidate with bounded `166 passed` and TOCTOU direct/adjacent `18 passed`.
This status update is governance-only; Developer implementation remains unchanged. At that
handoff, Integrator was required to audit the exact 32-path, `2136/48` base-to-final-tree package
while preserving `1975/48` as the reviewed implementation-only fact. That audit later passed.
Production bootstrap, pilot activation, and all real registry/task/worktree/automation side
effects remain unauthorized.

## Local Integration

Reviewer, QA, and Integrator accepted the unchanged implementation. Checkpoint
`08f99cdec1d9f7ca0de802109089b70105a17ad3` was governance-completed and locally integrated at
`91c6b42564c1ef030761bd9c757889159e438974` as the exact 32-path, `2136/48` package with zero
excluded residual. No real bootstrap, pilot, registry, controller, heartbeat, task, worktree,
automation, fetch, or push action occurred.
