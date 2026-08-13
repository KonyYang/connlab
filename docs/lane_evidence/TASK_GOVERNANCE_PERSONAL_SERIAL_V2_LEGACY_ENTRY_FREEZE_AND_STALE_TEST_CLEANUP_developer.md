# TASK_GOVERNANCE_PERSONAL_SERIAL_V2_LEGACY_ENTRY_FREEZE_AND_STALE_TEST_CLEANUP — Developer Evidence

TASK_ID: `TASK_GOVERNANCE_PERSONAL_SERIAL_V2_LEGACY_ENTRY_FREEZE_AND_STALE_TEST_CLEANUP`

ROLE: Developer

STATUS: `completed_after_bounded_fix`

MODEL: `gpt-5.6-terra`

REASONING_EFFORT: `medium`

MODEL_ROUTE_REASON: `default_complex`

SUBJECT: `6070bbd241431891579e99fc0c7d432281507c4d`

attempt: `2`

action: `ca10514cf0b9141a2e1053e6c2a6e7e6745202258d4b9c2884a61f98582aad26`

prompt: `c1ced08ae4a80925fb0e72db20c8cfea1de51b85aff3d01cc8a48eeca383883d`

## Delivered

- The legacy Controlled Lane adapter now reads the authoritative board first and fails closed under
  Personal Serial V2 before consuming a request, registry input, Python module, or Git/worktree path.
- Authority and protocol text now clearly designate Personal Serial V2 and public `Submit`,
  `Approve`, and `Close` as the only daily entry workflow.
- Regression tests prove adapter zero-write behavior, remove stale public FIFO/`ActivateNext`
  assumptions, and make cutover history accept a legal most-recent close record.

## TDD and validation

- Attempt 1 Red: `py -m pytest tests/unit/test_connlab_lane_worktree_script.py -q` failed as
  expected with `CTL_INVALID_REQUEST`, proving the adapter consumed the unreadable request before
  its V2 guard.
- Attempt 2 Red: the marker-boundary test failed because prose outside the authoritative block
  caused `BLOCKED_LEGACY_MODE_FROZEN`; the new runnable V2 busy-submit fixture also failed before
  its repository was initialized.
- Attempt 2 Green: the adapter now parses the single marker-delimited JSON control block, and the
  executable V2 regression proves busy Submit is zero-write before a legal Close permits the same
  request to be submitted again.
- `py -m pytest tests/unit/test_task_scoped_role_thread_lifecycle_governance.py tests/unit/test_connlab_lane_worktree_script.py -q` — `15 passed`.
- `py -m pytest tests/integration/test_connlab_execution_gate_recovery.py tests/integration/test_connlab_serial_complex_recovery.py -q` — `17 passed`.
- `py -m pytest tests/unit/test_connlab_personal_serial_workflow.py -q` — `13 passed`.
- `git diff --check` passed.
- Adapter regression snapshots confirmed unchanged board bytes, absent registry root, unchanged Git
  HEAD/status/branches/worktrees for the frozen call.

No push, cleanup, archive, retire, reset, restore, stash, rebase, or destructive operation occurred.
