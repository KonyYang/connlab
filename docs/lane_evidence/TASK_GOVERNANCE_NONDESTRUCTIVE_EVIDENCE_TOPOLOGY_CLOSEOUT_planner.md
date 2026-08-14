# TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT Planner Evidence

TASK_ID: TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT
ROLE: Planner
STATUS: ready_for_user_approval
MODEL: gpt-5.6-sol
REASONING_EFFORT: medium
MODEL_ROUTE_REASON: risk:authority
ATTEMPT: 1
ACTION_ID: d9ebd4935e7cc614dd855844078e624ac28e14e6f5b0f340f53235be8cf69f77
PROMPT_SHA256: 0c902de0f0536a5b65b427051f3262b618fe8c4c62bcbae9d181b3a48e8b571e
NEXT: User
BLOCKER: none

## Bounded Scope Amendment

- STATUS: bounded_scope_amendment_pending_user_approval
- The current durable task remains `DEVELOPER_BLOCKED`; its host, task branch and five-path dirty
  implementation patch remain unchanged.
- The strict verifier produced `13 passed, 4 failed` in the mandatory recovery suite because that
  suite binds an unavailable sentinel Plan. A production exception would be an authority bypass.
- The unit contract bundle produced `59 passed, 1 failed` because its fixture passes the linked task
  worktree as the primary repository and now correctly receives `BLOCKED_PRIMARY_UNVERIFIED` before
  its intended task-mismatch assertion.
- The minimum amendment adds exactly
  `tests/integration/test_connlab_serial_complex_recovery.py` and
  `tests/unit/test_connlab_serial_complex_orchestrator_contract.py` for fixture-only corrections.
- The recovery fixture will bind a real committed Plan; the unit fixture will resolve the real
  primary. No verifier relaxation, production bypass, runtime/schema/authority behavior or third
  path is authorized.
- Exact implementation/test scope becomes seven paths; governance scope remains the existing eight
  paths, for fifteen ordered paths total.
- Canonical amended approved-request SHA-256:
  `9910790e5d12df746f4c1fc3680eccbe249b6fec7762e76cd7deb340a106ee51`.
- NEXT: User
- BLOCKER: none

## Machine Authority

- Canonical Submit returned `ALLOW_ACTIVATE` from idle board SHA-256
  `5dcbc0dfff355181eaf6efc96871bc8d034ab942d7317a119c20a2df4acb79d6`.
- Activation was committed board-only at `0c7d04fb`.
- Planner begin-role and invocation were separately persisted through the production writer at
  `01eeedc1` and `ad8199d2`.
- Planning base and activation parent: `dd88e7fab9494985502236a32a46e81c3c79e0fe`.
- Primary remained clean throughout read-only discovery.

## Discovery Result

- The current integration contract correctly requires the task branch/worktree HEAD to equal the
  exact QA-reviewed subject.
- The real temporary-repository happy path already demonstrates primary-owned evidence commits, but
  production orchestration does not enforce that ownership and callback-time topology.
- The unique selected model is primary sequential evidence-only commits interleaved with existing
  board-only commits. It adds no ref, worktree, registry, command, schema or lifecycle.
- Review clarification removes both line-budget risks: `connlab_personal_task.py` remains a thin
  <=500-line seam; one bounded verifier module owns repository checks; one new <=500-line integration
  test owns the E2E while the existing 1059-line recovery suite stays unchanged.
- Board evidence is `E_P` followed by the dynamic callback evidence sequence, including bounded
  fix-loop callbacks. No fixed role count, evidence count or route-length allowlist is authorized.
- Durable invocation proves ACTION_ID/ROLE/ATTEMPT only. Model/effort/reason bind the committed Plan's
  frozen `gpt-5.6-sol / medium / risk:authority` route and require independent Reviewer/QA dispatch
  audit; the Plan does not claim those fields can be reconstructed from board invocation.
- Exact implementation scope is five paths; the Task, Plan, five fixed role evidence paths and board
  are the only governance paths, thirteen total.
- `scripts/connlab_serial_complex.py` remains read-only because the state machine and callback schema
  do not change.

## Design Influence

The `codebase-design` module/interface/seam discipline keeps `connlab_personal_task.py` thin and
extracts one cohesive repository-verification module while leaving the pure state machine unchanged.
This avoids a second evidence subsystem, protects Python line budgets and makes the operational
contract deep: one ownership rule, one verifier and a small writer-facing interface.

## Authorization Boundary

No host, branch/worktree, Developer, runtime/protocol/test edit, integration, push or cleanup is
authorized until the User approves the exact committed Plan ref and approved-request SHA-256.
