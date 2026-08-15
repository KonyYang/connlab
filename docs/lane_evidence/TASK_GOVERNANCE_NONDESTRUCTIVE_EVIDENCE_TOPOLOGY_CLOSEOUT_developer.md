# TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT Developer Evidence

TASK_ID: TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT
ROLE: Developer
STATUS: ready
SUBJECT: 59e0cc7b7fa4b53b1a5a21719647aa47f9491fcb
MODEL: gpt-5.6-sol
REASONING_EFFORT: medium
MODEL_ROUTE_REASON: risk:authority
ACTION_ID: cef992a7eb2245504ec2a389b4bae7ff305f8fe06731880049210889543edb43
ATTEMPT: 4
NEXT: Reviewer
BLOCKER: none

## Scope

- Modified only `scripts/connlab_serial_evidence_topology.py` and `tests/integration/test_connlab_nondestructive_evidence_topology.py`.
- No board/evidence write on task branch; no push or destructive Git operation.

## Implementation

- Planner accepted evidence now requires the fixed Task-derived Planner evidence path and exact raw SHA-256.
- An otherwise-unmapped Planner revision bundle is accepted only as an exact single-parent Task/derived-Plan/fixed-Planner-evidence three-path commit whose board bytes equal its parent, immediately followed by a single-parent board-only commit whose active task and exact `plan_ref` bind that same commit, derived Plan path, and recomputed raw Plan SHA-256.
- No commit/SHA allowlist or hardcoded production identity was added.
- Execution-role evidence verifier code and its ordering/path/digest/parent/board/subject/identity/model/ancestry checks were unchanged.

## TDD / Validation

- RED: `test_integration_accepts_immediately_bound_planner_revision_bundle` initially failed with `BLOCKED_INTEGRATION_PROOF` unknown/code-mixed commit (1 failed).
- GREEN was compressed into the existing disposable-repo fixture to preserve Plan line budget. The fixture is non-SHA-specific and exercises the legal revision bundle in every integration history.
- Planner drift matrix covers unbound, wrong digest, extra path, board modification, and later-descendant binding, all fail closed; existing multiparent, reorder, unknown commit, execution-path/digest/identity/subject/worktree and zero-write regressions remain active.
- `py -m pytest tests/integration/test_connlab_nondestructive_evidence_topology.py -q` — 21 passed in 49.84s.
- `py -m pytest tests/integration/test_connlab_serial_complex_recovery.py -q` — 17 passed in 73.72s.
- `py -m py_compile scripts/connlab_serial_evidence_topology.py` — passed.
- `git diff --check` and cached diff check — passed.
- Line counts: verifier 326; integration test 495, both <=500 hard limit.
- Post-commit worktree/index clean; changed paths confirmed exactly the two authorized files.

## Safety

No schema, Plan, scope, board, integration, push, cleanup, branch repair or destructive Git operation was performed. The task branch remains at the exact fixed subject.
