# CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_BOOTSTRAP Developer Evidence

Status: ready_for_reviewer_implementation_re_gate

Branch: `lane/connlab-controlled-lane-orchestration-v2-bootstrap`

Bounded-fix base: `738af3e51663f8ab3d63c4a6840810cb5b08f5e0`

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
  are unchanged; every touched Python file is now below the project hard limit.

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
| `tests/unit/test_connlab_controlled_lane_registry.py` | 421 |
| `tests/unit/test_connlab_controlled_lane_state_machine.py` | 367 |
| `tests/integration/test_connlab_controlled_lane_dry_run.py` | 500 |
| `tests/integration/test_connlab_controlled_lane_bootstrapped_pilot.py` | 229 |

Reviewer should review this evidence's containing lane checkpoint commit. No fetch, push, runtime
bootstrap, pilot activation, QA, Integrator action, or merge was performed.
