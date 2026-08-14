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
- Exact implementation scope is four paths; the Task, Plan, five fixed role evidence paths and board
  are the only governance paths, twelve total.
- `scripts/connlab_serial_complex.py` remains read-only because the state machine and callback schema
  do not change.

## Design Influence

The `codebase-design` module/interface/seam discipline keeps Git and evidence verification in the
existing repository-aware writer seam (`connlab_personal_task.py`) while leaving the pure state
machine unchanged. This avoids a second evidence subsystem and makes the operational contract deep:
one evidence ownership rule with strict validation and a small role-facing interface.

## Authorization Boundary

No host, branch/worktree, Developer, runtime/protocol/test edit, integration, push or cleanup is
authorized until the User approves the exact committed Plan ref and approved-request SHA-256.

