# Orchestrator Latency And Model Routing — Short Implementation Plan

Task: `TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING`

Status: `REVISION_3_READY_FOR_USER_APPROVAL`

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
- The first exact Approve attempt against Revision 2 was rejected with
  `BLOCKED_APPROVED_SCOPE_INVALID` and zero writes because the Submit classifier accepts the extra
  `push_or_release` forbidden-category fact while the approved-scope validator forbids that key.
  Revision 3 binds the two distinct frozen key sets and adds a cross-copy negative; runtime/schema
  files remain unchanged.

### Planner Inference And Bounded Assumptions

- This is a planned governance task because it changes long-lived orchestration behavior, has four
  implementation paths, and requires independent Reviewer/QA/Integrator gates.
- Model routing remains an explicit dispatch-time decision in the Orchestrator contract; it is not
  persisted in the board schema or delegated to a new routing service.
- QA uses Terra low only for a documentation/copy-only task that changes no operational skill,
  protocol, runtime or product behavior, has all frozen risk flags false, has no blocker/fix loop, and
  has a fully enumerated bounded validation set. Every other non-high-risk task uses Terra medium.
  This governance task changes operational orchestration guidance and therefore deterministically
  routes QA to `gpt-5.6-terra / medium`. Any frozen high-risk category routes the affected role to Sol.
- The next three simple-task durations are observational evidence toward about ten minutes, not an
  acceptance blocker and not a repository automation feature.

No unresolved discovery question changes scope, behavior, ownership, or validation.

## 2. Exact Scope

### Planning Files (this committed planning package)

1. `docs/task_board.md` — writer-generated planned activation only.
2. `tasks/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING.md` — frozen task boundary.
3. `docs/task_governance_orchestrator_latency_and_model_routing_plan.md` — this short Plan and
   approved-request contract.
4. `docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_planner.md` — immutable
   current-conversation Planner evidence used only for the genuine Planner-ready transition.

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
3. Extend the bounded unit test with executable contract assertions for the exact Submit/Approve/Close
   entry shapes, rejection of `kind` in Submit, required `kind=planned` in Approve, required scalar
   `DecisionRef` in Close, exact default/escalation models, no Luna, no direct Python request-JSON
   entry, simple-path interaction count, recovery reuse, browser-smoke condition, evidence audit fields,
   and final route reporting.
4. Use only the personal serial writer for implementation-phase board transitions; do not hand-edit
   the machine JSON or change its schema.

## 4. Planner-Ready Transition Before Approval

The current board is correctly `running/planning`; `Approve` is illegal until the existing state
machine consumes a genuine `Planner/ready/User` event. No new command or runtime/schema change is
needed, and no callback is fabricated.

The legal transition is:

1. Planning remains in this permanent Orchestrator conversation, as required by the active Planner
   skill. No Planner agent, thread, branch, lane, host or worktree is created.
2. Commit the revised Task and Plan. Then create and commit the Planner evidence path listed above,
   binding the exact Task ID, revised committed Plan ref/hash, current primary HEAD, current board
   digest, confirmed facts, Reviewer findings addressed, and `STATUS: ready`.
3. Use the existing `begin-role` state-writer command with the frozen `planner_dispatch` action name,
   a prompt digest bound to this exact revision, `role=Planner`, and the current permanent Orchestrator
   thread as the execution identity. This records the real inline Planner action; it does not dispatch
   or create an agent. Commit that sole board transition.
4. Use `record-invocation` with the same action ID, `thread_id` equal to the current conversation,
   `agent_id=null`, and status `completed`; commit that sole board transition.
5. Submit a `connlab.serial-callback` whose exact tuple is `Planner / ready / User`, whose
   `subject_commit` is the committed Planner-evidence HEAD, whose evidence ref is the exact committed
   evidence blob/SHA-256, and whose blocker is null. `consume-callback` must be called once and its sole
   board change committed.
6. Re-run read-only Inspect and require `running/awaiting_user_approval`, no pending callback, no host,
   no implementation path changes, and clean primary. Any mismatch stops before User approval.

These three internal state-writer events are not Submit, Approve, or Close entry actions. User entry
actions continue to use only `scripts/run_task.ps1`. The later Approve call remains forbidden until the
User explicitly approves the new committed Plan ref and exact approved-request hash.

## 5. Frozen Entry Payload Contracts

The implementation must state and test these exact contracts; no alternate schema retry or payload
copy between actions is allowed.

### Submit

`scripts/run_task.ps1 -Action Submit -RequestJson <single JSON object>` accepts exactly:

```text
schema, version, task_id, summary, root_cause_clear, expected_result_clear,
may_touch, targeted_validation, requires_independent_review, forbidden_categories
```

`schema=connlab.serial-task-request`, `version=1`. The `kind` field is forbidden. Missing decision
fields may classify as discovery only when the submitted object follows the classifier contract; an
unknown key is a terminal zero-write classification error, never a signal to try another payload.
Its `forbidden_categories` object has exactly ten keys:
`api_contract`, `database`, `schema_or_migration`, `persistence`, `authority`,
`public_drive_workflow`, `business_rule_semantics`, `destructive_action`, `external_mutation`, and
`push_or_release`.

### Approve

`scripts/run_task.ps1 -Action Approve -ApprovedRequestJson <single JSON object>` accepts exactly:

```text
schema, version, task_id, summary, kind, may_touch, expected_file_count,
classification_reason, targeted_validation, forbidden_categories
```

`schema=connlab.personal-task-approved-request`, `version=1`, and `kind=planned` are mandatory. It also
requires the committed `PlanRef` and explicit `ApprovalRef`; no Submit fields are copied into it.
Its `forbidden_categories` object has exactly the first nine Submit category keys and explicitly
forbids `push_or_release`, matching `scripts/connlab_serial_board.py::FORBIDDEN_KEYS`.

### Close

Close deliberately has no JSON payload. The exact entry is
`scripts/run_task.ps1 -Action Close -DecisionRef <non-empty explicit User decision>`. Supplying or
inventing a close JSON schema is forbidden; missing `DecisionRef` fails before the writer runs.

The bounded tests import/call the existing classifier and approved-payload validator where applicable,
and statically verify the PowerShell action-to-argument mapping. They include canonical positive cases
and negatives for Submit-with-`kind`, copying the ten-key Submit categories into Approve,
Approve-without/wrong-`kind`, and Close-without-`DecisionRef`.

## 6. Model Routing And Audit Evidence

No board or invocation schema is changed. Model routing is proven at three fixed existing layers:

1. **Actual dispatch action:** every complex `spawn_agent` call explicitly supplies both `model` and
   `reasoning_effort`; inherited/default model selection is forbidden.
2. **Role evidence:** every Developer, Reviewer, QA, and Integrator evidence document contains exactly
   one value for each fixed field near its header:
   `MODEL`, `REASONING_EFFORT`, and `MODEL_ROUTE_REASON`. The reason is either
   `default_complex`, `qa_bounded_low`, or `risk:<frozen-category>`.
3. **Acceptance summary:** Integrator evidence and the final User summary contain an
   `ACTUAL_MODEL_ROUTING` table with role, model, effort, reason, and evidence ref. Reviewer verifies
   the dispatch capsule against the subject role evidence; QA verifies the complete route table and
   forbidden-Luna assertion. A missing/mismatched field blocks the gate.

Because native action and board schemas have no model field, they are not falsely presented as the
audit store. The tool dispatch record plus content-addressed role evidence is the audit proof; the
static test proves the mandatory contract text, while Reviewer/QA/Integrator prove the actual values
used for this run.

## 7. Validation And Gates

Run on the exact clean implementation HEAD:

```powershell
py -m pytest tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q
py -m pytest tests/integration/test_connlab_execution_gate_recovery.py tests/integration/test_connlab_serial_complex_recovery.py -q
git diff --check
```

Also inspect the exact changed-path list and verify every Must Not Touch path is unchanged. The
automatic chain remains Developer -> Reviewer -> mandatory QA -> Integrator. For this Task the
deterministic route is Developer/Reviewer/QA/Integrator = `gpt-5.6-terra / medium`; any later
high-risk escalation must cite its frozen category. The final completion summary lists the actual
route table and evidence refs. No browser smoke is required because this governance task has no
user-visible UI change.

Runtime acceptance additionally checks that the written contract enforces: no simple-task schema
retry; submit-and-close only when uninterrupted; no duplicate activation on recovery; explicit complex
role model/effort; no Luna. Three later simple-task durations are observed toward approximately ten
minutes without making timing a hard failure.

## 8. Risks And Rollback

- **Documentation/runtime mismatch:** bounded static tests bind the skill and protocol to the same
  route table and canonical entry. Integration suites protect the unchanged runtime behavior.
- **Underpowered routing:** frozen high-risk categories force role-specific Sol escalation; ambiguous
  or repeated unexplained failure stops or escalates rather than silently continuing.
- **Over-routing/cost regression:** Terra remains the complex default; simple work stays on the
  permanent Sol Orchestrator without another hop.
- **Recovery duplication:** board/Git/evidence identity is read before action; uncertainty fails closed.
- **Rollback:** before integration, retain the clean task host and return to Developer. After local
  integration, first verify the target is the exact accepted two-parent merge, its first parent is the
  recorded pre-integration primary HEAD, its second parent is the accepted clean task HEAD, and no
  later commit has changed the four locked paths. Only a separate User-approved governance action may
  run `git revert -m 1 <exact-merge-commit>`, followed by the full validation matrix. Never use a
  one-parent revert, reset, restore, stash, clean, history rewrite, or retained-resource deletion.

## 9. Exact Approved-Request Contract

Canonicalization: the SHA-256 is over the exact single-line UTF-8 JSON bytes below, with no BOM and no
trailing newline.

```json
{"schema":"connlab.personal-task-approved-request","version":1,"task_id":"TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING","summary":"Reduce Personal Serial Workflow V2 retry latency and execution cost through explicit role model routing and deterministic daily orchestration guidance.","kind":"planned","may_touch":[".agents/skills/connlab-lane-orchestrator/SKILL.md","docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md","tests/unit/test_task_scoped_role_thread_lifecycle_governance.py","docs/task_board.md"],"expected_file_count":4,"classification_reason":"Governance-only four-path change with mandatory independent Reviewer, QA, and Integrator gates; no runtime, schema, product, authority, or persistence changes.","targeted_validation":["py -m pytest tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q","py -m pytest tests/integration/test_connlab_execution_gate_recovery.py tests/integration/test_connlab_serial_complex_recovery.py -q","git diff --check"],"forbidden_categories":{"api_contract":false,"database":false,"schema_or_migration":false,"persistence":false,"authority":false,"public_drive_workflow":false,"business_rule_semantics":false,"destructive_action":false,"external_mutation":false}}
```

SHA-256:
`43d110d8f7a3e87859f59b72c62cd295d214fa86e3bb60e5d091587587a74d3a`

Explicit approval must identify this committed Plan ref and authorize this exact approved-request
contract. Approval authorizes implementation only; it does not authorize push, cleanup, Task B, or
any scope expansion.

`STATUS: REVISION_3_READY_FOR_USER_APPROVAL`
