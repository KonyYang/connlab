# TASK_GOVERNANCE_PERSONAL_SERIAL_V2_LEGACY_ENTRY_FREEZE_AND_STALE_TEST_CLEANUP — Reviewer Evidence

TASK_ID: `TASK_GOVERNANCE_PERSONAL_SERIAL_V2_LEGACY_ENTRY_FREEZE_AND_STALE_TEST_CLEANUP`

ROLE: Reviewer

STATUS: `reviewer_blocked`

MODEL: `gpt-5.6-terra`

REASONING_EFFORT: `medium`

MODEL_ROUTE_REASON: `default_complex`

SUBJECT: `6a20ae7373e2404307741e4d559b6a08e4819945`

PARENT: `828d22b16f17d35206b37d2687d24b724e8b83b4`

PLAN_REF: `ca3858a8a8eafe59a3322a17a98c6e5d8684b5a7#67db77e0`

ATTEMPT: `1`

ACTION_ID: `7797c6402c5d2886af5a72343e2655c735816c7ae02e0ad5c14e4d44dcb00c73`

PROMPT_SHA256: `50a94f54e4731bcc6c34a8932e6bb80a011dd0fdd467516c5adde57a3df52584`

## Blocking findings

### F1 — Adapter does not inspect the authoritative control block

`scripts/connlab_controlled_lane.ps1` identifies Personal Serial V2 with three independent regular
expression searches across the complete Markdown board. The approved plan requires parsing the single
marker-delimited authoritative control block. A legacy/non-V2 control block with the three matching
JSON fragments elsewhere in prose, retained history, or another fenced block would be falsely frozen.
This fails the exact authority-boundary requirement and needs a bounded control-block parser before
the legacy-input guard.

### F2 — Required stale-entry behavioral regression was removed, not replaced

The approved plan requires a test proving a busy Submit is zero-write and that the same request can
be submitted after a legal Close. `tests/integration/test_connlab_execution_gate_recovery.py` instead
removes both behavioral FIFO/`ActivateNext` tests and adds only a static assertion that
`scripts/run_task.ps1` contains the three allowed action names. The static check cannot establish
busy-submit zero-write or close-then-resubmit behavior, so the specified regression contract remains
uncovered.

## Verification performed

- Reviewed exact implementation diff `828d22b16f17d35206b37d2687d24b724e8b83b4..6a20ae7373e2404307741e4d559b6a08e4819945`; the eight implementation paths are within the allowlist.
- Confirmed Developer evidence hash target and required route fields.
- `py -m pytest tests/unit/test_task_scoped_role_thread_lifecycle_governance.py tests/unit/test_connlab_lane_worktree_script.py -q` — `14 passed`.
- `py -m pytest tests/integration/test_connlab_execution_gate_recovery.py tests/integration/test_connlab_serial_complex_recovery.py -q` — `16 passed`.
- `py -m pytest tests/unit/test_connlab_personal_serial_workflow.py -q` — `13 passed`.
- `git diff --check 828d22b16f17d35206b37d2687d24b724e8b83b4 6a20ae7373e2404307741e4d559b6a08e4819945` — passed.

The test suites passing does not resolve F1 or F2 because the required control-block and behavioral
cases are absent. Return to Developer for one bounded same-scope fix.

---

## Attempt 2

STATUS: `reviewer_blocked`

MODEL: `gpt-5.6-terra`

REASONING_EFFORT: `medium`

MODEL_ROUTE_REASON: `default_complex`

SUBJECT: `6070bbd241431891579e99fc0c7d432281507c4d`

PARENT: `e92f087cf4b2b2e50a38a0c39b256e4c77c1e8db`

ATTEMPT: `2`

ACTION_ID: `c6a87eea908e97756dcda9fe6e4661a3bfc351d9eb7368b0e0b06abacc9c514b`

PROMPT_SHA256: `504162740cbcc8e5998bb7613ebb354b317abf15d106e15b1a6a86521d2527d5`

### F3 — Missing control block now fails before retained legacy behavior

F1 and F2 are corrected: the adapter binds its V2 decision to the marker-delimited control block,
and an executable V2 busy-Submit/Close/re-Submit test is restored. However,
`scripts/connlab_controlled_lane.ps1` enables `Set-StrictMode -Version Latest` and only assigns
`$control` inside `if ($controlBlock.Success)`. The following unconditional condition evaluates
`$control` even when an older retained board has no marker block:

```powershell
if ($null -ne $control -and ...)
```

Under StrictMode that is an uninitialized-variable error, rather than the required unchanged
non-V2 historical adapter path. Initialize `$control = $null` before the marker match (and add the
no-marker legacy regression) before re-review. This is the only permitted bounded fix; any further
blocking result must stop for the User.

### Attempt 2 verification

- Reviewed exact bounded-fix diff `62c3915e4cf0c6766e08e21fb00e86fad19107c5..6070bbd241431891579e99fc0c7d432281507c4d`; changed implementation paths remain within the approved allowlist.
- `py -m pytest tests/unit/test_task_scoped_role_thread_lifecycle_governance.py tests/unit/test_connlab_lane_worktree_script.py -q` — `15 passed`.
- `py -m pytest tests/integration/test_connlab_execution_gate_recovery.py tests/integration/test_connlab_serial_complex_recovery.py -q` — `17 passed`.
- `py -m pytest tests/unit/test_connlab_personal_serial_workflow.py -q` — `13 passed`.
- `git diff --check 828d22b16f17d35206b37d2687d24b724e8b83b4 6070bbd241431891579e99fc0c7d432281507c4d` — passed.

The suites do not cover a board without the marker block, so their passing result does not resolve
F3. Stop the task: the one bounded same-scope fix was already consumed.
