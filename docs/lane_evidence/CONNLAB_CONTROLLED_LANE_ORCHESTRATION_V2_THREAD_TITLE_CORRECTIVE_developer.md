# CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_THREAD_TITLE_CORRECTIVE Developer Evidence

Status: `ready_for_reviewer_implementation_gate`

Date: 2026-07-28

Base:

- branch: `lane/connlab-controlled-lane-orchestration-v2-thread-title-corrective`
- base HEAD: `d5c2117eac6694fc685c0995a4ea5fa96feb98bc`
- implementation used only the authorized corrective worktree and exact May Touch paths.

## Implemented Contract

- Controller creation now adopts only the exact native thread/project read-back and leaves the role
  binding `title_pending`; it does not require or attest an automatically generated title.
- `bootstrap_controller_title_pending` selects either `set_controller_title` or the journaled
  read-only `adopt_exact_controller_title` action from durable title proof.
- Title targets deterministically bind registry, task, lane, role, thread, host/cwd/project,
  route, operation, action version, and the canonical title
  `ConnLab｜研发任务编排与集成主控 v2`.
- Mutation follows the existing six-command journal:
  prepare, invocation-start, one fake native action, result, exact read-back, ack, and advance.
- Exact-title adoption performs zero title mutation. Wrong/zero/multiple/unreadable read-back fails
  closed. Controller becomes active only after exact title acknowledgement.
- Canonical replay returns `CTL_ALREADY_APPLIED` without generation drift or controller recreation;
  invocation-started receipt loss recovers from exact read-back without resend.
- Heartbeat creation remains the next independent action. Runtime bootstrap remains inactive.

## TDD Evidence

RED:

```text
py -m pytest tests/unit/test_connlab_controlled_lane_controller_title.py \
  tests/integration/test_connlab_controlled_lane_controller_title_recovery.py -q
```

Result: collection failed for both modules because
`scripts.connlab_controlled_lane.controller_title` did not exist.

The migrated existing create-ack node also failed with
`CTL_DISPATCH_ACK_MISMATCH`, proving the old implementation still required title verification at
controller creation.

GREEN:

```text
py -m pytest tests/unit/test_connlab_controlled_lane_controller_title.py \
  tests/integration/test_connlab_controlled_lane_controller_title_recovery.py -q
```

Result: `23 passed in 1.42s`.

Focused bootstrap/state/registry compatibility:

```text
py -m pytest tests/unit/test_connlab_controlled_lane_bootstrap.py \
  tests/unit/test_connlab_controlled_lane_state_machine.py \
  tests/unit/test_connlab_controlled_lane_registry.py \
  tests/unit/test_connlab_controlled_lane_controller_title.py \
  tests/integration/test_connlab_controlled_lane_controller_title_recovery.py -q
```

Result before the final three additional binding parameters: `81 passed in 24.14s`.

Final complete bounded controlled-lane regression:

```text
py -m pytest tests/unit tests/integration -q -k connlab_controlled_lane
```

Result: `189 passed, 2373 deselected in 44.96s`.

## Static Validation

- `py_compile`: passed for all changed runtime and new test modules.
- PowerShell parser errors: `0/0/0` for `connlab_controlled_lane.ps1`,
  `connlab_lane_worktree.ps1`, and `task_complete_commit.ps1`.
- stable catalog: `39` `CTL_*` codes.
- mutation commands: `6` unchanged.
- fake/in-memory adapters and disposable registry roots only; no real task, title, heartbeat,
  registry, worktree, branch, automation, migration, archive, fetch, push, or bootstrap action.
- retained original bootstrap and TASK_367A topology was not modified.

Blank-inclusive UTF-8 physical line budgets:

- `bootstrap.py`: `270/270`
- `controller_title.py`: `220/220`
- `state_machine.py`: `278/280`
- existing registry test: `485/485`
- new controller-title unit test: `187/240`
- new controller-title recovery integration test: `296/300`
- skill: `98/150`
- controlled-v2 protocol: `161/190`
- role registry: `34/60`

Final checkpoint validation additionally requires and records UTF-8 strict decode, trailing
whitespace, `git diff --check`, exact whitelist, forbidden-path, staging-empty, clean worktree,
and exact `base..HEAD` diff facts after the local lane commit.
