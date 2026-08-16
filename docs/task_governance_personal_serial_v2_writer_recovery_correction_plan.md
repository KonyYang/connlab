# TASK_GOVERNANCE_PERSONAL_SERIAL_V2_WRITER_RECOVERY_CORRECTION Plan

Status: `ready_for_user_approval`

## 1. Confirmed repository facts

The active board is `running / planning / Planner / attempt 1` for this task. The primary worktree is
clean. `scripts/connlab_serial_native_action.py` does not exist. Current line counts are 565 for
`connlab_serial_phase2.py`, 532 for `connlab_personal_task.py`, and 489 for
`connlab_serial_board.py`.

The active implementation allocates native attempts from global `current_attempt`; bounded-fix
reentry repeats that rule. Durable `role_invocations` and `timing_facts.roles` already contain the
role-local facts but are not reconciled for continuous identity.

`write_board` renders and fsyncs a temporary file, then calls `os.replace`, and only afterward parses
the complete board. Blocked v2 reapproval validates neither the exact committed Plan nor its
validation manifest and therefore can synchronize paths while retaining stale validation authority.

## 2. One implementation design

Create only `scripts/connlab_serial_native_action.py`. Mechanically move native-action hashing and
construction there with a shared validator that returns the next attempt for one role.

For each Planner/Developer/Reviewer/QA/Integrator role:

- timing attempts must be exactly `1..N`, unique;
- invocation attempts must be exactly `1..M`, unique;
- every invocation identity must exist in timing;
- normally `M == N`;
- during exact `dispatch_pending`, timing may contain only that one pending identity beyond invocation;
- pending/current role/attempt must agree;
- all other duplicate, gap, mismatch, stale, or extra identities fail closed.

The builder selects `N + 1` for its own role. `current_attempt` remains a compatibility snapshot only.
Host creation remains attempt 1 and existing host-duplication gates remain unchanged.

`apply_bounded_fix_reentry` calls the same validator for Developer, verifies the supplied canonical
action against the derived attempt, then atomically records the pending Developer timing identity.

## 3. Board durability transaction

For every changed writer command:

1. acquire the ignored writer lock;
2. reread raw board bytes and verify expected SHA-256;
3. parse current authority;
4. validate all command, repository, Plan, manifest, and transition preconditions;
5. mutate only the in-memory candidate;
6. render the full candidate board;
7. parse and validate those rendered bytes before temporary-file creation;
8. write, flush, and fsync a same-directory temporary file;
9. reread the temporary file, require exact byte equality, and parse/validate it;
10. call `os.replace` only after all validation succeeds;
11. perform no fallible validation after replacement;
12. return the replacement digest and `changed=true`.

Any failure before replacement removes only the temporary file and returns `BLOCKED_*`,
`changed=false`, and the original board digest. Replacement failure likewise leaves the original
board. Tests snapshot and compare raw board bytes, HEAD, cached diff, worktree diff/status, and file
content for all blocked/no-change cases.

## 4. Blocked reapproval transaction

Before any v2 blocked reapproval mutation:

1. parse the supplied approved request;
2. resolve and verify the exact committed Plan path, commit, and raw SHA-256;
3. require exactly one embedded approved-request object equal to the supplied object;
4. resolve all four execution routes and require no route drift;
5. require exactly one valid `connlab.validation-manifest/v1` for this task;
6. fail closed on missing, wrong-task, stale, duplicate, malformed, or mismatched facts;
7. verify clean committed primary and exact recorded host when required;
8. for scope expansion, require a strict path superset and unchanged risk facts;
9. atomically update scope, approved paths, Plan/approval refs, and exact manifest;
10. archive the blocker and resume development only after the complete candidate validates.

Same-scope blocked Plan-reference correction also stores the newly validated exact manifest while
leaving the blocker until its existing explicit recovery path. No route, schema, callback, evidence,
or role-chain behavior changes.

## 5. Exact approved scope

Implementation/test paths:

1. `scripts/connlab_serial_phase2.py`
2. `scripts/connlab_serial_native_action.py`
3. `scripts/connlab_serial_board.py`
4. `scripts/connlab_personal_task.py`
5. `tests/unit/test_connlab_serial_phase2_runtime.py`
6. `tests/integration/test_connlab_serial_phase2_writer.py`

Fixed governance paths:

7. `tasks/TASK_GOVERNANCE_PERSONAL_SERIAL_V2_WRITER_RECOVERY_CORRECTION.md`
8. `docs/task_governance_personal_serial_v2_writer_recovery_correction_plan.md`
9. `docs/lane_evidence/TASK_GOVERNANCE_PERSONAL_SERIAL_V2_WRITER_RECOVERY_CORRECTION_planner.md`
10. `docs/lane_evidence/TASK_GOVERNANCE_PERSONAL_SERIAL_V2_WRITER_RECOVERY_CORRECTION_developer.md`
11. `docs/lane_evidence/TASK_GOVERNANCE_PERSONAL_SERIAL_V2_WRITER_RECOVERY_CORRECTION_reviewer.md`
12. `docs/lane_evidence/TASK_GOVERNANCE_PERSONAL_SERIAL_V2_WRITER_RECOVERY_CORRECTION_qa.md`
13. `docs/lane_evidence/TASK_GOVERNANCE_PERSONAL_SERIAL_V2_WRITER_RECOVERY_CORRECTION_integrator.md`
14. `docs/task_board.md`

Any outside dependency stops for User decision.

## 6. TDD and verification order

1. Add role-local attempt regressions and prove the current allocator fails.
2. Add invalid-history cases for duplicate, gap, invocation/timing mismatch, and illegal pending state.
3. Add writer snapshots proving raw board and Git preservation on candidate validation and write failure.
4. Add exact blocked-reapproval Plan/manifest success and negative cases.
5. Implement the sole extraction and minimal writer corrections.
6. Self-review the exact six-path task-host diff.
7. Run the complete Developer manifest last on the final clean subject.
8. Reviewer runs focused recovery/atomicity regressions and diff validation.
9. QA independently runs the complete assigned matrix once.
10. Integrator verifies exact scope, line budgets, subject, evidence topology, clean Git, and local
    integration facts without rerunning the matrix.

## 7. Validation manifest

```json
{"schema":"connlab.validation-manifest","version":1,"task_id":"TASK_GOVERNANCE_PERSONAL_SERIAL_V2_WRITER_RECOVERY_CORRECTION","checks":[{"id":"serial-writer-recovery-focused","kind":"targeted","run_for":["Developer","Reviewer","QA"],"cwd":".","argv":["py","-m","pytest","tests/unit/test_connlab_serial_phase2_runtime.py","tests/integration/test_connlab_serial_phase2_writer.py","-q"],"timeout_seconds":900,"permission":"pytest_temp","required":true},{"id":"serial-recovery-compatibility","kind":"full","run_for":["Developer","QA"],"cwd":".","argv":["py","-m","pytest","tests/integration/test_connlab_serial_complex_recovery.py","tests/integration/test_connlab_serial_approval_preflight.py","tests/unit/test_connlab_personal_serial_workflow.py","tests/unit/test_connlab_serial_complex_state.py","tests/unit/test_connlab_serial_complex_orchestrator_contract.py","tests/unit/test_task_scoped_role_thread_lifecycle_governance.py","-q"],"timeout_seconds":1200,"permission":"pytest_temp","required":true},{"id":"serial-governance-compile","kind":"static","run_for":["Developer","QA"],"cwd":".","argv":["py","-m","py_compile","scripts/connlab_personal_task.py","scripts/connlab_serial_phase2.py","scripts/connlab_serial_native_action.py","scripts/connlab_serial_board.py"],"timeout_seconds":120,"permission":"workspace","required":true},{"id":"serial-python-line-budget","kind":"static","run_for":["Developer","QA"],"cwd":".","argv":["py","-c","from pathlib import Path; paths=['scripts/connlab_serial_phase2.py','scripts/connlab_serial_native_action.py','scripts/connlab_serial_board.py','scripts/connlab_personal_task.py','tests/unit/test_connlab_serial_phase2_runtime.py','tests/integration/test_connlab_serial_phase2_writer.py']; counts={p:len(Path(p).read_text(encoding='utf-8').splitlines()) for p in paths}; print(counts); raise SystemExit(0 if all(n <= 500 for n in counts.values()) else 1)"],"timeout_seconds":120,"permission":"workspace","required":true},{"id":"serial-diff-check","kind":"static","run_for":["Developer","Reviewer","QA"],"cwd":".","argv":["git","diff","--check"],"timeout_seconds":120,"permission":"workspace","required":true},{"id":"exact-implementation-scope","kind":"static","run_for":["Developer","QA"],"cwd":".","argv":["py","-c","import subprocess; expected=['scripts/connlab_serial_phase2.py','scripts/connlab_serial_native_action.py','scripts/connlab_serial_board.py','scripts/connlab_personal_task.py','tests/unit/test_connlab_serial_phase2_runtime.py','tests/integration/test_connlab_serial_phase2_writer.py']; base=subprocess.check_output(['git','merge-base','master','HEAD'],text=True,encoding='utf-8').strip(); actual=subprocess.check_output(['git','diff','--name-only',base+'..HEAD'],text=True,encoding='utf-8').splitlines(); print({'base':base,'expected':expected,'actual':actual}); raise SystemExit(0 if len(actual)==len(expected) and set(actual)==set(expected) else 1)"],"timeout_seconds":120,"permission":"workspace","required":true}]}
```

## 8. Model routing

Developer, Reviewer, QA, and Integrator are all
`gpt-5.6-sol / medium / risk:authority`.

## 9. Canonical approved request

```json
{"schema":"connlab.personal-task-approved-request","version":1,"task_id":"TASK_GOVERNANCE_PERSONAL_SERIAL_V2_WRITER_RECOVERY_CORRECTION","summary":"Correct Personal Serial V2 writer recovery so native-action attempts increment from each role's durable invocation and timing history, blocked scope reapproval synchronizes the exact committed validation manifest with paths, and fully rendered boards are validated before atomic replacement with zero-write failure behavior.","kind":"planned","may_touch":["scripts/connlab_serial_phase2.py","scripts/connlab_serial_native_action.py","scripts/connlab_serial_board.py","scripts/connlab_personal_task.py","tests/unit/test_connlab_serial_phase2_runtime.py","tests/integration/test_connlab_serial_phase2_writer.py","tasks/TASK_GOVERNANCE_PERSONAL_SERIAL_V2_WRITER_RECOVERY_CORRECTION.md","docs/task_governance_personal_serial_v2_writer_recovery_correction_plan.md","docs/lane_evidence/TASK_GOVERNANCE_PERSONAL_SERIAL_V2_WRITER_RECOVERY_CORRECTION_planner.md","docs/lane_evidence/TASK_GOVERNANCE_PERSONAL_SERIAL_V2_WRITER_RECOVERY_CORRECTION_developer.md","docs/lane_evidence/TASK_GOVERNANCE_PERSONAL_SERIAL_V2_WRITER_RECOVERY_CORRECTION_reviewer.md","docs/lane_evidence/TASK_GOVERNANCE_PERSONAL_SERIAL_V2_WRITER_RECOVERY_CORRECTION_qa.md","docs/lane_evidence/TASK_GOVERNANCE_PERSONAL_SERIAL_V2_WRITER_RECOVERY_CORRECTION_integrator.md","docs/task_board.md"],"expected_file_count":14,"classification_reason":"Planned/complex authority-runtime correction because it changes the sole Personal Serial V2 board writer, recovery attempt identity, committed Plan/manifest binding, and atomic authority persistence; independent Developer, Reviewer, QA, and Integrator gates are mandatory.","targeted_validation":["py -m pytest tests/unit/test_connlab_serial_phase2_runtime.py tests/integration/test_connlab_serial_phase2_writer.py -q","py -m pytest tests/integration/test_connlab_serial_complex_recovery.py tests/integration/test_connlab_serial_approval_preflight.py tests/unit/test_connlab_personal_serial_workflow.py tests/unit/test_connlab_serial_complex_state.py tests/unit/test_connlab_serial_complex_orchestrator_contract.py tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q","py -m py_compile scripts/connlab_personal_task.py scripts/connlab_serial_phase2.py scripts/connlab_serial_native_action.py scripts/connlab_serial_board.py","verify all six controlled Python implementation/test paths are at most 500 lines","git diff --check","verify the exact six-path task-host implementation diff","verify Developer blocked/resume 1 to 2, role-local attempts, duplicate/gapped/mismatched history rejection, exact blocked-reapproval manifest binding, and zero-write board/Git preservation for every blocked or changed=false outcome"],"forbidden_categories":{"api_contract":false,"database":false,"schema_or_migration":false,"persistence":false,"authority":true,"public_drive_workflow":false,"business_rule_semantics":false,"destructive_action":false,"external_mutation":false}}
```

## 10. Stop condition

After the planning bundle is committed and the Planner callback is consumed, stop at
`awaiting_user_approval`. Implementation starts only after explicit User approval of the exact
committed Plan. Final execution stops at `implemented_pending_human_review`.
