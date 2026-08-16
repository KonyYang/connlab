# TASK_GOVERNANCE_PERSONAL_SERIAL_V2_WRITER_RECOVERY_CORRECTION

Status: `planned` / `ready_for_user_approval`

## Goal

Correct Personal Serial V2 writer recovery so every native-action attempt is allocated independently
from that role's durable invocation/timing history, blocked scope reapproval binds the exact committed
Plan's validation manifest together with its paths, and complete board candidates are validated before
atomic replacement with zero-write failure behavior.

## Confirmed root causes

- `build_native_action` allocates from global `current_attempt`, so roles borrow one another's count.
- bounded-fix reentry also requires global `current_attempt + 1`.
- timing validation detects duplicate timing identities but not per-role gaps or invocation/timing drift.
- `write_board` performs `os.replace` before parsing the complete candidate board.
- blocked v2 reapproval skips committed-Plan and validation-manifest verification.
- scope amendment updates paths but leaves the previous `validation_manifest` in authority.
- `connlab_serial_phase2.py` and `connlab_personal_task.py` currently exceed the 500-line hard limit.

## Required behavior

1. Planner, Developer, Reviewer, QA, and Integrator attempts are independent role-local sequences.
2. Developer attempt 1 followed by a legal blocked/resume path produces canonical Developer attempt 2.
3. Reviewer/QA fix-loop Developer attempts derive only from Developer history.
4. First and repeated Planner/Reviewer/QA/Integrator attempts never borrow another role's count.
5. Invocation and timing identities are unique, continuous per role, and mutually consistent.
6. A legal `dispatch_pending` state may have exactly its own timing start unmatched by an invocation.
7. Any duplicate, gap, mismatch, stale pending identity, or illegal extra identity blocks before write.
8. Complete rendered bytes and complete temporary bytes are parsed and validated before `os.replace`.
9. No fallible validation occurs after replacement.
10. Every `BLOCKED_*` or `changed=false` result preserves original board bytes, HEAD, index/worktree
    status/content, and reports `changed=false`.
11. Every blocked v2 reapproval validates the exact committed Plan, its one embedded approved request,
    execution routes, and its one validation manifest before mutation.
12. Scope reapproval atomically synchronizes `scope_contract`, `approved_code_paths`, `plan_ref`,
    `approval_ref`, and `validation_manifest`.
13. Missing, wrong-task, stale-ref, duplicate, malformed, or semantically mismatched Plan/manifest facts
    fail closed with zero writes.
14. Existing schemas, role order, callback/evidence contracts, route table, and blocker policy remain
    unchanged.

## Exact implementation/test scope

1. `scripts/connlab_serial_phase2.py`
2. `scripts/connlab_serial_native_action.py`
3. `scripts/connlab_serial_board.py`
4. `scripts/connlab_personal_task.py`
5. `tests/unit/test_connlab_serial_phase2_runtime.py`
6. `tests/integration/test_connlab_serial_phase2_writer.py`

## Fixed governance paths

- `tasks/TASK_GOVERNANCE_PERSONAL_SERIAL_V2_WRITER_RECOVERY_CORRECTION.md`
- `docs/task_governance_personal_serial_v2_writer_recovery_correction_plan.md`
- fixed Planner/Developer/Reviewer/QA/Integrator evidence paths for this task
- `docs/task_board.md`

Total approved scope is exactly 14 unique paths.

## Single extraction seam

Mechanically extract native-action construction and role-attempt history validation from the oversized
`connlab_serial_phase2.py` into the sole new module `connlab_serial_native_action.py`.
`connlab_serial_phase2.py` re-exports the public builder and uses the same validator for bounded
Developer reentry. No second module or governance framework is authorized.

All six controlled Python implementation/test paths must be at most 500 lines. Bring the already
oversized `connlab_personal_task.py` under the limit only through behavior-neutral compaction while
editing its blocked-approval branch; do not create another abstraction seam.

## Required regressions

- Developer blocked/resume `1 -> 2`.
- Reviewer/QA bounded fixes increment Developer from Developer history only.
- first and repeated attempts for every role remain role-local.
- duplicate, gapped, mismatched, stale, and illegal pending histories block before board write.
- complete rendered and temporary-board validation occurs before replacement.
- malformed candidate, temporary write/fsync/read/validation failure, replacement failure, invalid
  Plan, and invalid manifest preserve byte-for-byte board and Git snapshots.
- same-scope blocked Plan correction and scope expansion both bind the exact committed manifest.
- missing, wrong-task, stale, duplicate, or malformed manifest/Plan binding fails closed.
- existing recovery and approval-preflight compatibility suites remain green.

## Non-goals

Do not modify `scripts/connlab_serial_complex.py`, schemas, role order, callback/evidence contracts,
product/backend/frontend/API/database/business logic, public-drive behavior, or external state.
Do not add a bypass, allowlist, new governance framework, push, cleanup, archive, retire, reset,
restore, stash, rebase, cherry-pick, force-ref, branch movement, worktree movement, or deletion.

## Acceptance

- The committed validation manifest passes on the final exact clean subject.
- The exact six implementation/test paths are the complete task-host diff.
- Every controlled Python path is at most 500 lines.
- Board raw bytes and Git facts remain unchanged for every blocked/no-change scenario.
- Developer, Reviewer, QA, and Integrator use `gpt-5.6-sol / medium / risk:authority`.
- The task stops at `implemented_pending_human_review`.
