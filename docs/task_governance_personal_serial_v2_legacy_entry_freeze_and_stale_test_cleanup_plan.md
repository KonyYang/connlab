# Personal Serial V2 Legacy Entry Freeze And Stale Test Cleanup — Plan

TASK_ID: `TASK_GOVERNANCE_PERSONAL_SERIAL_V2_LEGACY_ENTRY_FREEZE_AND_STALE_TEST_CLEANUP`

STATUS: `READY_FOR_USER_APPROVAL`

## 1. Confirmed Baseline

- The task was activated through `scripts/run_task.ps1 -Action Submit` under Personal Serial V2.
- Activation parent: `f2e3c3c13ec4c29f156cec5d245291290a237bff`.
- Primary and index were clean before activation; the board was `idle`, `active=null`, `queue=[]`.
- `AGENTS.md` section 22 is normative but appears after retained sections 13–21, which still contain
  conflicting Classic, Quick Fixer, FIFO and Controlled Lane wording.
- `.agents/skills/connlab-controlled-lane/SKILL.md` still reads like an executable daily skill.
- `scripts/connlab_controlled_lane.ps1` currently forwards directly into the frozen legacy Python CLI.
- `tests/integration/test_connlab_execution_gate_recovery.py` still models public FIFO/ActivateNext.
- `tests/integration/test_connlab_serial_complex_recovery.py` fixes `last_closed.task_id` to the old
  cutover task instead of accepting the most recent legal close record.

## 2. Discovery Gate

Confirmed by User: goal, non-goals, Personal Serial V2 entry, retained-history preservation, one normal
complex role chain, maximum one bounded fix, and no push/cleanup.

Confirmed by repository: the exact stale wording and assertions above, the V2 marker-delimited board,
the existing stable `BLOCKED_LEGACY_MODE_FROZEN` result code, and public `run_task.ps1` actions limited
to Submit/Approve/Close.

Planner inference: no clarification is required. The adapter can fail before touching legacy request,
registry or Python runtime state by parsing the repository board in PowerShell. No new schema, helper
or dependency is needed.

## 3. Exact Implementation Allowlist

1. `AGENTS.md`
2. `.agents/skills/connlab-controlled-lane/SKILL.md`
3. `scripts/connlab_controlled_lane.ps1`
4. `docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md`
5. `docs/project_management/TASK_EXECUTION_SKILL.md`
6. `tests/unit/test_connlab_lane_worktree_script.py`
7. `tests/integration/test_connlab_execution_gate_recovery.py`
8. `tests/integration/test_connlab_serial_complex_recovery.py`
9. `docs/task_board.md`

Task/Plan and fixed role evidence paths are V2 governance artifacts outside implementation scope.
Any other implementation path requires stopping for a new User approval.

## 4. File-Level Implementation

- `AGENTS.md`: add a short banner near the beginning. It states that section 22 and the current
  `connlab-lane-orchestrator` skill are the only daily routing authority and that conflicting sections
  13–21 are historical only.
- Controlled Lane skill: replace executable-looking opening guidance with a hard-freeze notice; retain
  the remainder as historical audit material.
- Controlled Lane PowerShell adapter: after resolving repository root, read and parse the single board
  control block. If it is `connlab.personal-serial-control` version 2 with
  `mode=personal_serial`, output a stable JSON object containing
  `code=BLOCKED_LEGACY_MODE_FROZEN`, `allowed=false`, `changed=false`, `zero_write=true`, the requested
  command and a fixed reason; exit 2 before request/registry consumption, directory creation, Python
  module loading or Git/worktree calls. Non-v2 historical behavior remains unchanged.
- V2 protocols: remove FIFO/role-dispatch contradictions from the active execution instructions and
  state that daily User entry is only Submit/Approve/Close. Do not rewrite unrelated historical docs.
- Tests: update the existing adapter test to prove raw board, registry-root absence, HEAD/status,
  branches and worktree list are unchanged. Rewrite the stale public FIFO/ActivateNext test to prove a
  busy Submit is zero-write and that the same request can be submitted after legal close. Change the
  cutover assertion to preserve an already valid recent `last_closed` record rather than one fixed ID.

## 5. Validation

1. `py -m pytest tests/unit/test_task_scoped_role_thread_lifecycle_governance.py tests/unit/test_connlab_lane_worktree_script.py -q`
2. `py -m pytest tests/integration/test_connlab_execution_gate_recovery.py tests/integration/test_connlab_serial_complex_recovery.py -q`
3. `py -m pytest tests/unit/test_connlab_personal_serial_workflow.py -q`
4. `git diff --check`
5. Exact implementation-path diff; board/registry/Git/worktree zero-write snapshot assertions.

No browser smoke is required because the task has no user-visible product UI change.

## 6. Risks And Rollback

- Risk: a freeze check placed too late could allow registry or Git side effects. Mitigation: test that
  the v2 decision occurs before legacy inputs and compare all relevant snapshots.
- Risk: over-editing historical docs could erase audit context. Mitigation: one early authority banner
  plus minimal active-protocol corrections; do not delete retained files.
- Risk: fixtures could accidentally test v1 instead of v2. Mitigation: assert exact board schema,
  version and mode in each freeze test.
- Rollback after local integration requires separate User authorization and a verified two-parent
  merge, using `git revert -m 1 <merge-commit>`. No reset/restore/rebase is authorized.

## 7. Execution Contract

- Developer, Reviewer, QA and Integrator use `gpt-5.6-terra / medium / default_complex` because this
  bounded governance cleanup changes no API/schema/persistence/authority/business semantics and has no
  unexplained failure.
- Each dispatch and role evidence records model, reasoning effort and route reason.
- Execute one normal role chain. One same-scope bounded fix is permitted; a second gate failure stops
  with a typed blocker.
- Do not use Classic, Quick Fixer, FIFO, Controlled Lane V2, push, cleanup, archive or retire paths.

## 8. Canonical Approved Request

```json
{"schema":"connlab.personal-task-approved-request","version":1,"task_id":"TASK_GOVERNANCE_PERSONAL_SERIAL_V2_LEGACY_ENTRY_FREEZE_AND_STALE_TEST_CLEANUP","summary":"Freeze legacy Controlled Lane entry under Personal Serial V2, remove stale ActivateNext/last_closed assumptions, and clarify the sole Submit/Approve/Close daily workflow without creating a new governance framework.","kind":"planned","may_touch":["AGENTS.md",".agents/skills/connlab-controlled-lane/SKILL.md","scripts/connlab_controlled_lane.ps1","docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md","docs/project_management/TASK_EXECUTION_SKILL.md","tests/unit/test_connlab_lane_worktree_script.py","tests/integration/test_connlab_execution_gate_recovery.py","tests/integration/test_connlab_serial_complex_recovery.py","docs/task_board.md"],"expected_file_count":9,"classification_reason":"Complex governance cleanup with independent review; exact nine-path scope freezes retained legacy entry behavior and corrects only confirmed stale workflow assumptions.","targeted_validation":["py -m pytest tests/unit/test_task_scoped_role_thread_lifecycle_governance.py tests/unit/test_connlab_lane_worktree_script.py -q","py -m pytest tests/integration/test_connlab_execution_gate_recovery.py tests/integration/test_connlab_serial_complex_recovery.py -q","py -m pytest tests/unit/test_connlab_personal_serial_workflow.py -q","git diff --check"],"forbidden_categories":{"api_contract":false,"database":false,"schema_or_migration":false,"persistence":false,"authority":false,"public_drive_workflow":false,"business_rule_semantics":false,"destructive_action":false,"external_mutation":false}}
```

The SHA-256 of the exact single-line UTF-8 JSON above is recorded in Planner evidence and returned with
the committed Plan ref. User approval must bind both values before implementation.

