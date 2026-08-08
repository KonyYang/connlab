# Orchestrator Latency And Model Routing — Short Implementation Plan

Task: `TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING`

Status: `READY_FOR_USER_APPROVAL`

Planning base: `6227acb7cfccaab276194d2a7cbda96bc1f09a89`

## 1. Discovery Gate

### Confirmed by the User

- Permanent Orchestrator and direct simple work remain `gpt-5.6-sol / medium`; simple work does not
  add an agent hop or attempt implicit model switching.
- Default complex roles use `gpt-5.6-terra`: Developer/Reviewer/Integrator at medium and QA at low or
  medium based on the approved validation risk.
- A relevant role upgrades to `gpt-5.6-sol` only for the frozen high-risk categories: API contract;
  database/schema/migration/persistence; authority/public-drive/business semantics; cross-frontend/
  backend or multi-layer work; unexplained repeated test failure; integration conflict; or
  security-sensitive change. Sol defaults to medium; high is limited to migration, authority, or a
  hard-to-diagnose failure. Luna is not used.
- Submit, Approve, and Close use `scripts/run_task.ps1`. The task does not rewrite that script or add
  routing runtime/configuration/schema machinery.
- Simple tasks use one preflight, activation commit, implementation, one bounded validation, completion,
  and human review; no Task/Plan, role agent, branch, worktree, or intermediate `继续` is added.
- Browser smoke is conditional on visible UI change and uses documented load state or deterministic
  selectors. Targeted tests and an independent build may run in parallel.
- Recovery reuses the durable active task/host reconstructed from board, Git, and evidence, and stops
  fail-closed when identity cannot be proved.

### Confirmed by the Repository

- The board was idle and `master` clean at `38372b9351a5ab84007bcde4728a07fefa2dae43`.
- `scripts/run_task.ps1` exposes only Submit, Approve, Close and Preview, and transports one JSON
  argument through `CONNLAB_PERSONAL_TASK_ARGV_JSON`; this task need not modify it.
- The current Orchestrator skill and serial role-chain protocol define automatic role order and
  recovery safety, but contain no explicit model/reasoning routing table.
- `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py` is a bounded 42-line static
  governance contract test and is the appropriate implementation-test owner.
- The two requested integration suites already exercise the real PowerShell entry, occupied/idle
  submission, complex recovery, role callbacks, integration proof, and retained closeout.
- Planned intake was activated through `scripts/run_task.ps1` and committed at `6227acb7...`; no agent,
  branch, worktree, host, runtime file, or product file was created or modified.
- A preliminary planned payload containing the obsolete `kind` field was rejected with
  `BLOCKED_CLASSIFICATION_INVALID` and zero writes. Reading the current classifier and passing the
  tested `connlab.serial-task-request` contract then activated once. This is concrete evidence for
  documenting one canonical entry contract rather than retrying schemas.

### Planner Inference And Bounded Assumptions

- This is a planned governance task because it changes long-lived orchestration behavior, has four
  implementation paths, and requires independent Reviewer/QA/Integrator gates.
- Model routing remains an explicit dispatch-time decision in the Orchestrator contract; it is not
  persisted in the board schema or delegated to a new routing service.
- QA uses Terra low for bounded/static validation and Terra medium when the approved test matrix or
  failure diagnosis requires it. Any high-risk category routes the affected role according to the
  frozen Sol rule.
- The next three simple-task durations are observational evidence toward about ten minutes, not an
  acceptance blocker and not a repository automation feature.

No unresolved discovery question changes scope, behavior, ownership, or validation.

## 2. Exact Scope

### Planning Files (this committed planning package)

1. `docs/task_board.md` — writer-generated planned activation only.
2. `tasks/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING.md` — frozen task boundary.
3. `docs/task_governance_orchestrator_latency_and_model_routing_plan.md` — this short Plan and
   approved-request contract.

### Implementation May Touch / Locked Paths (exactly four)

1. `.agents/skills/connlab-lane-orchestrator/SKILL.md`
2. `docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md`
3. `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py`
4. `docs/task_board.md`

These four paths are exclusive to the single approved task host from approval through integration.
Any additional path is scope expansion and must stop for a new Plan/User decision.

### Must Not Touch

- `scripts/run_task.ps1`, `scripts/connlab_personal_task.py`, `scripts/connlab_serial_board.py`, or any
  board JSON schema/runtime writer;
- product/backend/frontend code, database/API/schema/migration/persistence/authority/public-drive/
  business semantics;
- browser plugin or browser implementation;
- retained, frozen, cancelled, legacy lane/V1/V2 audit resources;
- lifecycle cleanup, push, release, publication, restart, reset, restore, stash, rebase, or clean.

## 3. File-Level Implementation

1. Update the Orchestrator skill with the fixed model-routing table, high-risk escalation table,
   explicit `model` and `reasoning_effort` dispatch/callback summary requirement, canonical
   `run_task.ps1` Submit/Approve/Close entry, shortest simple path, deterministic recovery, and
   UI-smoke/load-state rule.
2. Mirror the same normative contract in the serial role-chain protocol. Preserve WIP=1, the single
   complex host, independent Reviewer/QA/Integrator, fail-closed recovery, and all no-destructive/no-push
   rules.
3. Extend the bounded unit test with executable static assertions for exact default/escalation models,
   no Luna, no direct Python request-JSON entry, simple-path interaction count, recovery reuse, browser
   smoke condition, and final route reporting.
4. Use only the personal serial writer for implementation-phase board transitions; do not hand-edit
   the machine JSON or change its schema.

## 4. Validation And Gates

Run on the exact clean implementation HEAD:

```powershell
py -m pytest tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q
py -m pytest tests/integration/test_connlab_execution_gate_recovery.py tests/integration/test_connlab_serial_complex_recovery.py -q
git diff --check
```

Also inspect the exact changed-path list and verify every Must Not Touch path is unchanged. The
automatic chain remains Developer -> Reviewer -> mandatory QA -> Integrator; the final completion
summary lists each role's actual model and reasoning effort. No browser smoke is required because this
governance task has no user-visible UI change.

Runtime acceptance additionally checks that the written contract enforces: no simple-task schema
retry; submit-and-close only when uninterrupted; no duplicate activation on recovery; explicit complex
role model/effort; no Luna. Three later simple-task durations are observed toward approximately ten
minutes without making timing a hard failure.

## 5. Risks And Rollback

- **Documentation/runtime mismatch:** bounded static tests bind the skill and protocol to the same
  route table and canonical entry. Integration suites protect the unchanged runtime behavior.
- **Underpowered routing:** frozen high-risk categories force role-specific Sol escalation; ambiguous
  or repeated unexplained failure stops or escalates rather than silently continuing.
- **Over-routing/cost regression:** Terra remains the complex default; simple work stays on the
  permanent Sol Orchestrator without another hop.
- **Recovery duplication:** board/Git/evidence identity is read before action; uncertainty fails closed.
- **Rollback:** before integration, retain the clean task host and return to Developer. After a local
  accepted integration and before any later task changes these paths, use an ordinary reviewed
  `git revert <integration-commit>` as a separate authorized governance action. Never reset, restore,
  stash, clean, rewrite history, or delete retained resources.

## 6. Exact Approved-Request Contract

Canonicalization: the SHA-256 is over the exact single-line UTF-8 JSON bytes below, with no BOM and no
trailing newline.

```json
{"schema":"connlab.personal-task-approved-request","version":1,"task_id":"TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING","summary":"Reduce Personal Serial Workflow V2 retry latency and execution cost through explicit role model routing and deterministic daily orchestration guidance.","kind":"planned","may_touch":[".agents/skills/connlab-lane-orchestrator/SKILL.md","docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md","tests/unit/test_task_scoped_role_thread_lifecycle_governance.py","docs/task_board.md"],"expected_file_count":4,"classification_reason":"Governance-only four-path change with mandatory independent Reviewer, QA, and Integrator gates; no runtime, schema, product, authority, or persistence changes.","targeted_validation":["py -m pytest tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q","py -m pytest tests/integration/test_connlab_execution_gate_recovery.py tests/integration/test_connlab_serial_complex_recovery.py -q","git diff --check"],"forbidden_categories":{"api_contract":false,"database":false,"schema_or_migration":false,"persistence":false,"authority":false,"public_drive_workflow":false,"business_rule_semantics":false,"destructive_action":false,"external_mutation":false,"push_or_release":false}}
```

SHA-256:
`b3caa75c1cf2678fec1b2d06ced4bb9e551b49e75767aba3564d6f7537b7b19c`

Explicit approval must identify this committed Plan ref and authorize this exact approved-request
contract. Approval authorizes implementation only; it does not authorize push, cleanup, Task B, or
any scope expansion.

`STATUS: READY_FOR_USER_APPROVAL`
