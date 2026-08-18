# TASK_GOVERNANCE_PERSONAL_SERIAL_V2_LEGACY_ENTRY_FREEZE_AND_STALE_TEST_CLEANUP

Status: complete (archived 2026-08-18; implementation evidence in docs/lane_evidence/TASK_GOVERNANCE_PERSONAL_SERIAL_V2_LEGACY_ENTRY_FREEZE_AND_STALE_TEST_CLEANUP_*)

## Goal

Remove the confirmed ambiguity between the active Personal Serial Workflow V2 and retained legacy
daily-entry material. Preserve historical files, but make legacy Controlled Lane execution fail closed
whenever the authoritative board is Personal Serial V2, and replace two stale test assumptions about
public `ActivateNext` and a fixed `last_closed` task.

## Exact Implementation May Touch

1. `AGENTS.md`
2. `.agents/skills/connlab-controlled-lane/SKILL.md`
3. `scripts/connlab_controlled_lane.ps1`
4. `docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md`
5. `docs/project_management/TASK_EXECUTION_SKILL.md`
6. `tests/unit/test_connlab_lane_worktree_script.py`
7. `tests/integration/test_connlab_execution_gate_recovery.py`
8. `tests/integration/test_connlab_serial_complex_recovery.py`
9. `docs/task_board.md`

Task/Plan/role evidence paths are governance evidence managed by the V2 role chain, not additional
implementation scope.

## Required Behavior

- Add an early, prominent `AGENTS.md` notice that section 22 is the only current daily workflow and
  supersedes conflicting sections 13–21; those sections remain historical reference.
- Mark the Controlled Lane skill as hard-frozen under Personal Serial V2.
- Make `scripts/connlab_controlled_lane.ps1` inspect the authoritative board before consuming legacy
  request/registry inputs or loading legacy Python. With a Personal Serial V2 board, return stable
  `BLOCKED_LEGACY_MODE_FROZEN`, `changed=false`, `zero_write=true` and perform no board, registry,
  journal, Git, branch or worktree mutation.
- Replace the public `ActivateNext`/FIFO test assumption with busy-submit-zero-write and close-then-
  resubmit behavior through `scripts/run_task.ps1`.
- Make the cutover/history test accept the most recent legal `last_closed` record instead of requiring
  one fixed governance-switch task.
- Keep the public daily entry surface exactly `Submit`, `Approve`, and `Close`.

## Must Not Touch

- Product, backend, frontend, API, database, persistence and business-rule code.
- Board schema, role chain, model routing, trust roots, manifests, CAS or proof frameworks.
- Controlled Lane registry/runtime modules, retained resources, archives, pilot or lifecycle cleanup.
- Any path not listed in Exact Implementation May Touch.
- Push or destructive Git/worktree operations.

## Validation

- `py -m pytest tests/unit/test_task_scoped_role_thread_lifecycle_governance.py tests/unit/test_connlab_lane_worktree_script.py -q`
- `py -m pytest tests/integration/test_connlab_execution_gate_recovery.py tests/integration/test_connlab_serial_complex_recovery.py -q`
- `py -m pytest tests/unit/test_connlab_personal_serial_workflow.py -q`
- `git diff --check`
- Exact-path diff and zero-write snapshots for board, registry root, Git HEAD/status, branches and
  worktrees around the frozen Controlled Lane adapter call.

## Execution Gate

No implementation is authorized until the User approves the exact committed Plan ref and canonical
approved-request SHA-256. After approval, run one Developer -> Reviewer -> QA -> Integrator chain.
At most one bounded same-scope fix is allowed; a second failure remains a typed blocker for the User.

