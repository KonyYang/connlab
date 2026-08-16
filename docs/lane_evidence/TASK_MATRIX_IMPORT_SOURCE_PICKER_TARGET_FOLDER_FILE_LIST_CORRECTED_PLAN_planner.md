# TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN Planner Evidence

TASK_ID: TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN
ROLE: Planner
STATUS: ready_for_user_approval
SUBJECT: 72fad109c1971f3d7e73e7555c36fcae8be8be19
MODEL: gpt-5.6-sol
REASONING_EFFORT: medium
MODEL_ROUTE_REASON: risk:api_contract
ACTION_ID: 3e26244f4519e2823e1b716c8e7386defbb7a8ca73a4faf0cb28d03152a6f750
ATTEMPT: 1
NEXT: User
BLOCKER: none

## Bounded governance recovery scope amendment

AMENDMENT_STATUS: ready_for_user_approval
AMENDMENT_PLANNER_ID: /root/matrix_source_picker_governance_recovery_planner

### Recovery authority

- Primary was clean at `e4f5425863f1215187e9efe87fa09c4a3c2f15d0`.
- Board raw SHA-256 was `d3db3ae33b95badfd0ac633d32f30fb1df53352578c2961fc95006524e5a62cd`.
- Board was `running / blocked / NATIVE_ACTION_FAILED` with no current role or pending action.
- The registered task branch/worktree remained clean at exact subject
  `163e31d455eb4af12e606288fa36d387c81f1476`.
- The failed production action reused Developer attempt 1 after Developer attempt 1 had already
  completed blocked, and the recovered board is now valid and clean.

### Read-only planning decision

The User-authorized five paths are sufficient. Preserve the existing ordered 20 paths and append
exactly:

1. `scripts/connlab_serial_phase2.py`
2. `scripts/connlab_serial_native_action.py`
3. `scripts/connlab_serial_board.py`
4. `tests/unit/test_connlab_serial_phase2_runtime.py`
5. `tests/integration/test_connlab_serial_phase2_writer.py`

The four existing files are byte-identical between current primary and retained subject; the new
native-action module does not yet exist. The unique seam is per-role durable invocation/timing history
for attempt allocation plus complete pre-`os.replace` board validation. `NATIVE_ACTION_FAILED` remains
outside the bounded-fix allowlist. No role order, schema, callback/evidence contract, product behavior
or model route changes.

The amendment Planner made no repository, board, index, ref, branch, worktree or external-state write
and ran no implementation test.

## Machine authority

- Read-only primary HEAD was `72fad109c1971f3d7e73e7555c36fcae8be8be19`; primary was clean.
- Board raw SHA-256 was `17d6500df7ccae8efc6cbbacdf4537150f1765a1d696a7cd774128c7cfe4e073` in Planner callback-pending state.
- Retained branch/worktree were clean at exact subject `163e31d455eb4af12e606288fa36d387c81f1476`; its parent is `900c26a78009264ab0fc06f2c038e50d6d280869` and the diff is exactly 12 approved paths.
- Prior focused 12 backend and 54 frontend tests passed; the old task was cancelled only because frozen `npm` could not execute under Windows `shell=False`.

## Decision

Preserve the complete product/API/UI contract, 20-path scope, `gpt-5.6-sol / medium / risk:api_contract` execution routing and browser smoke. Correct only two manifest executable names to `npm.cmd`. After approval reuse the retained subject without destructive Git or ref movement and require fresh Developer/Reviewer/QA/Integrator evidence.

Planner made no repository, board, ref, branch, worktree, database, attachment, browser or external-file write and ran no implementation test.

STATUS: ready_for_user_approval

NEXT: User

BLOCKER: none
