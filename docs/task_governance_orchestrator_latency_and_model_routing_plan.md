# Orchestrator Latency And Model Routing — Short Implementation Plan

Task: `TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING`

Status: `INTEGRATION_RECONCILIATION_AUTHORITY_REVISION_PENDING_USER_APPROVAL`

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

Historical Revision 3 status before implementation: `REVISION_3_READY_FOR_USER_APPROVAL`.

## 10. Bounded Integration Reconciliation Amendment

### 10.1 Discovery And Exact Source Facts

This section is a separate amendment authorization contract and supersedes only the incomplete
integration/acceptance portion of Revision 3, including the runtime prohibition only for the exact
unmerged executor artifact in section 10.6. Section 9 continues to describe the already completed
original implementation and does not authorize this reconciliation. The model
routing implementation and its original four-path scope remain unchanged and already passed the
independent Reviewer and QA gates. The exact current statement is: `Integrator pre-integration audit
completed; acceptance blocked.`

Repository facts frozen by this amendment are:

- QA subject: `ad7dac819268ae77781709b626aea4f624a7a740`.
- Final original lane HEAD: `f7770b6a6a82a36f946d16145a2124f6330961e1`, clean on
  `codex/task-governance-orchestrator-latency-and-model-routing` in the registered sibling worktree.
- `ad7dac81..f7770b6a` is a linear three-commit range. It adds only the fixed Reviewer, QA, and
  Integrator evidence paths, in that order, at `d5e82f2e`, `d6c7eba5`, and `f7770b6a`.
- Existing merge: `093d48966b15c536b7411b3cc4cdca1e1e0d4faf`; parents are exact first parent
  `a632f01c96de457deec901fedb271addfd0b77fb` and second parent `f7770b6a...`; merge tree is
  `891f0cd28ebfd86d8ae8b1fff6e92160b16b71ca`.
- Exact blocker baseline: clean `master@82370aeb1690f1a6e1ebda7d37048f5f926d7570`; it is the
  single direct first-parent descendant of the merge, and `093d4896..82370aeb` changes only
  `docs/task_board.md` to record `INTEGRATION_BLOCKED`.
- The committed source board blob SHA-256 is
  `9083399d2a3a091afc634ab3253df86e8f3c0754fd73558bdc0b959b0c336d88`; the clean Windows
  worktree bytes consumed by the writer/CAS are CRLF-normalized and have SHA-256
  `295974ff98e874862d2505e8ff05ebab6977d738f74e40a6937bcbe165bc6696`. Both must match. The board records phase
  `blocked`, resume phase `integration`, stale `head_sha=3d0884e1...`, no integrated commit, and the
  five exact Planner/Developer/Reviewer/QA/Integrator evidence refs listed in section 10.5.

The first committed amendment is
`e07c2ec07cb741ebb91cc335566e5dd91ee47c75`, whose parent is exact `82370aeb...` and whose path
delta is only the Task, this Plan, and Planner evidence. This authority correction must be one further
clean primary child of `e07c2ec0...` with the same exact three-path delta. The later User approval must
bind the resulting final Plan commit and blob SHA-256. At execution time, primary must still be that
exact approved authority-correction commit; all commits in `82370aeb..<approved-plan-commit>` must be
linear, planning-only, and limited to those three paths. This preserves the frozen blocker baseline
while allowing the requested committed review correction.

### 10.2 Why The Normal Integration Command Cannot Be Relaxed

The normal `record-integration` contract correctly requires the physical lane HEAD to equal the QA
subject and the physical primary HEAD to equal the merge. Here, mandatory role evidence commits moved
the lane from the reviewed subject to `f7770b6a`, and the blocker governance commit moved primary from
the existing merge to `82370aeb`. A general descendant allowance would weaken every future task.

Therefore this amendment does not change `connlab_serial_complex.py`, `connlab_serial_board.py`, the
normal `record-integration` payload, or the board schema. It introduces a task-ID-specific, one-time
command in a reviewed executor artifact. The executor is run commit-addressed against the primary
repository, calls the existing sole writer and writer lock, and is never merged or cherry-picked into
master. The original lane remains immutable at `f7770b6a`; the existing merge remains the sole product/
governance implementation merge.

### 10.3 Pre-Implementation Machine Authority

The final integration CAS may not retroactively authorize implementation. Before a reconciliation
worktree is created or any executor path is modified, use the existing reviewed writer/state machine
to create a committed machine-authority chain:

1. From the exact committed `INTEGRATION_BLOCKED` board, call `block` with a truthful
   `connlab.serial-task-blocker` whose code is `SCOPE_EXPANDED`, stage is `blocked`, resume phase is
   `planning`, dirty-path manifest is exactly the four new executor paths, and evidence ref is the
   committed authority-correction Planner evidence. This preserves the old blocker in Git history and
   identifies the newly discovered implementation need without inventing a product failure.
2. Call `Approve` with the canonical strict-superset request in section 10.9. Existing behavior must
   return `ALLOW_SCOPE_AMEND`, bind the new Plan/approval refs, update `scope_contract`, and preserve
   the blocker. Commit the board-only transition.
3. Call `resume` with the same exact User approval identity. It must clear only the scope blocker and
   enter `planning`. Commit the board-only transition.
4. Record a real Planner `begin-role`, invocation, and `ready -> User` callback in the current
   permanent Orchestrator conversation. The callback uses the final amendment commit as subject and
   the exact committed Planner-evidence ref. It must enter `awaiting_user_approval`; no synthetic
   callback is permitted. Commit each normal board transition as required by V2.
5. Call `Approve` again with byte-identical approved-request JSON, Plan ref, and approval ref. In this
   normal phase, the current writer must set `phase=development` and atomically set both
   `scope_contract.may_touch` and `complex_context.approved_code_paths` to the same exact eight paths.
   Commit and verify this authority checkpoint.

The eight paths are the original four-path strict-superset required by the existing reapproval rule;
the original four remain immutable inputs during reconciliation. Only the four new executor paths may
have a code/test delta. Forbidden-category facts remain byte-identical to the original scope; the
`authority=false` category continues to mean product/business authority, not this governance control
transition.

Mandatory pre-worktree assertions are: current task/Plan/approval refs match; phase is `development`;
blocker and pending callback are null; scope and approved-code-path arrays equal the canonical request;
primary and original lane are clean; board host identity is the exact original branch/worktree with the
known frozen stale `head_sha=3d0884e12cc39e7b416da75ab01aaffd36c6418c`; physical original lane is
exact clean `f7770b6a`; the already verified `3d0884e1..f7770b6a` package/evidence topology still
matches; and the board/approval checkpoint is committed. This exact legacy mismatch is an input to the
one-time relocation, not a general host tolerance. Any mismatch stops before `git worktree add` or
executor modification.

An executable negative in disposable repositories must prove that the expanded request sent directly
against the original `INTEGRATION_BLOCKED` state returns `BLOCKED_APPROVED_SCOPE_INVALID`, leaves the
board hash unchanged, creates no branch/worktree, and leaves all executor paths absent. Further
negatives must prove that missing the second normal approval, mismatched scope versus
`approved_code_paths`, a stale Plan/approval ref, or an uncommitted authority checkpoint blocks both
host relocation and executor writes.

### 10.4 Durable Host Relocation And Role Chain

After the committed machine-authority checkpoint, use the already registered host to record a normal
Developer `begin-role` and invocation. That durable Developer action, the eight-path board scope, and
the committed Plan/approval refs jointly authorize one host-relocation operation; before those facts
exist, the new worktree may not be created. The relocation target names are fixed as:

- branch: `codex/task-governance-orchestrator-latency-model-routing-reconciliation`;
- worktree: `D:\\PythonProject\\connlab-worktrees\\task-governance-orchestrator-latency-model-routing-reconciliation`.

Create the branch/worktree from the exact committed final approval-authority checkpoint. Under the
live Developer invocation, the only pre-relocation code/test work permitted is the bounded relocation
and reconciliation writer plus its tests on the four new paths. The first clean bridge checkpoint must
prove its parent/base, exact path delta, branch, worktree, clean index, scope/approval digest, and
pending Developer action. Its one-time `rebind-reconciliation-host` transition then atomically changes
`task_branch`, `task_worktree`, `base_sha`, `head_sha`, and `worktree_lifecycle=ready` to the new host,
while preserving the exact live Developer action, callback state, scope, approved paths, locks,
Plan/approval refs, original-lane evidence, and WIP=1. The original branch/worktree stays clean and
unchanged at `f7770b6a`.

Only after the rebind board checkpoint is committed and the physical new worktree matches it may
Developer continue or issue a callback. The same normal callback state machine then drives complete
Developer -> Reviewer -> mandatory QA -> Integrator. Because this is an integration-conflict repair,
every role is explicitly dispatched as `gpt-5.6-sol / medium / risk:integration_conflict`; Luna is
forbidden. Reviewer and QA review the exact executor subject and host-relocation proof. No role may
write the primary board except through the normal writer transitions or the two reviewed task-specific
atomic commands. Integrator may execute final reconciliation only after all reconciliation evidence
commits are immutable, hash-addressed, linearly ordered, and the executor worktree/index is clean.

The sole final integration operation is one writer-lock-protected compare-and-swap of the
marker-delimited board JSON. It consumes the exact committed `integration` state produced by the
approved scope/host/role chain, while re-verifying the immutable original `INTEGRATION_BLOCKED`
lineage, and writes all target fields in one rendered board replacement. There is no integration-stage
`resume`, HEAD prewrite, or second integration board mutation. The resulting
board must then be exact-path staged and committed as one board-only durability checkpoint. If that
commit fails, stop with the bytes preserved and report the dirty state; do not restore or retry by
hand.

### 10.5 Exact Evidence Inputs And Target State

Existing immutable evidence inputs are:

1. `docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_planner.md@ec7af84879a8ddd300f310af62ed46480341bee1#c1d85c2dfbb5fcb0bc39e76cf0b23e97efab9ab2c300f669495526608ff64f10`
2. `docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_developer.md@ad7dac819268ae77781709b626aea4f624a7a740#0985f2ed69d88f58962b2ab3e29d100b45596647b6c9ab9423146332fb3bed7c`
3. `docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_reviewer.md@d5e82f2ea6ab18c979540c226811c2a20978f48e#27488e4d5001edff3a45770d0140fe694fc43c867f7f109274b76d0291161c96`
4. `docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_qa.md@d6c7eba5b7cfe8dfb41e82575dc94404e8e2f5ae#5c22e90893a4e87d3609d03f4e2c910069c53640c35b4d6f09cc02292c96915a`
5. `docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integrator.md@f7770b6a6a82a36f946d16145a2124f6330961e1#8c15467010e3693ada5247ed3dd011c5334d736012dee7a94d1a8f9664cd05f0`

The target evidence list preserves those five refs and appends, in order, the exact committed
amendment Planner evidence and four fixed-path reconciliation evidence refs:

- `..._planner.md@<amendment-commit>#<exact-blob-sha256>`;
- `..._integration-reconciliation_developer.md@<D>#<exact-blob-sha256>`;
- `..._integration-reconciliation_reviewer.md@<R>#<exact-blob-sha256>`;
- `..._integration-reconciliation_qa.md@<Q>#<exact-blob-sha256>`;
- `..._integration-reconciliation_integrator.md@<I>#<exact-blob-sha256>`.

The command must verify each future commit/path/blob hash, role `STATUS`, model-routing header,
ancestry `amendment -> D -> R -> Q -> I`, exact path delta for each role, and a clean reconciliation
worktree at `I`. The atomic target is exactly:

- `active.plan_ref` becomes the User-approved committed amendment Plan ref;
- `active.approval_ref` becomes the exact later User approval identity;
- `active.updated_at` becomes the single attested reconciliation timestamp used by the rendered target;
- `active.blocker=null` and `active.phase=human_review`;
- top-level `control.state=implemented_pending_human_review`;
- `complex_context.head_sha=f7770b6a6a82a36f946d16145a2124f6330961e1`;
- `complex_context.integrated_commit=093d48966b15c536b7411b3cc4cdca1e1e0d4faf`;
- `complex_context.worktree_lifecycle=integrated`;
- `complex_context.task_branch`, `task_worktree`, `base_sha`, `host_thread_id`, and `host_id` return
  to the original registered lane/host facts, so human-review closeout can verify the actually
  integrated `f7770b6a` resource;
- `complex_context.current_role=null`, `pending_callback=null`, and the complete ten-ref evidence
  list above;
- `complex_context.retained_resource_refs` appends the exact reconciliation Integrator evidence ref;
- top-level `retained_history` appends one exact same-task resource record naming the clean
  reconciliation branch/worktree/head, evidence, owner `permanent Orchestrator governance`, and
  disposition `retained unmerged one-time reconciliation executor`; and
- all unrelated control, queue, approved eight-path scope, role invocation, and task fields remain
  byte-for-byte semantically unchanged.

Exact replay may return `ALREADY_APPLIED` with zero writes only when the committed board, target state,
Plan/approval refs, all ten evidence refs, merge proof, original lane proof, and board-only transition
commit all match. Any partial or divergent state remains blocked.

### 10.6 Exact Future May Touch And Locked Paths

Machine-approved strict-superset May Touch, only after the two-approval authority chain:

1. `.agents/skills/connlab-lane-orchestrator/SKILL.md` (immutable during reconciliation)
2. `docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md` (immutable during reconciliation)
3. `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py` (immutable during reconciliation)
4. `docs/task_board.md` (writer-only authority transitions)
5. `scripts/connlab_personal_task.py`
6. `scripts/connlab_model_routing_integration_reconciliation.py` (new, task-specific)
7. `tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py` (new)
8. `tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py` (new)

The executor implementation delta is limited to paths 5-8:

1. `scripts/connlab_personal_task.py`
2. `scripts/connlab_model_routing_integration_reconciliation.py` (new, task-specific)
3. `tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py` (new)
4. `tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py` (new)

Reconciliation role evidence is restricted to the four fixed evidence paths in section 10.5 and is
managed as evidence, not implementation scope. The only authorized primary write is the final atomic
`docs/task_board.md` target followed by its exact-path board-only commit.

Locked paths/facts are the original lane branch/worktree/ref, both Git ranges in section 10.1, the
merge object/parents/tree, all five existing evidence objects, the amendment Task/Plan/Planner evidence,
the candidate executor files/tests/evidence, and the primary board. No parallel owner or exception is
allowed.

Must Not Touch:

- `scripts/run_task.ps1`, `scripts/connlab_serial_complex.py`, `scripts/connlab_serial_board.py`, and
  every normal Submit/Approve/Close/record-integration contract;
- the original four implementation files, original lane, existing role evidence bytes, merge commit,
  blocker commit, retained/frozen/cancelled resources, registry, legacy V1/V2 assets, or Task B;
- product/backend/frontend, API/database/schema/migration/persistence/business authority, browser,
  remote state, publication/restart, push, cleanup, reset, restore, stash, rebase, cherry-pick, or any
  new merge.

### 10.7 Fail-Closed Proof And Validation Matrix

The one-time command must return stable zero-write blockers for any task/board hash/state/blocker/
plan/approval mismatch; dirty primary or executor; original lane branch/HEAD/index drift; non-linear or
extra-path evidence range; evidence path/blob/status/model mismatch; merge parent/tree/ancestry drift;
unexpected `093d4896..82370aeb` topology/path; amendment package not being the exact three-path child of
`82370aeb`; missing/partial machine scope approval; scope/approved-path disagreement; unauthorized or
unregistered host; live Developer action mismatch; executor manifest drift; retained-resource target
drift; target render drift; or duplicate proof mismatch.

Required validation on the exact reconciliation Integrator evidence HEAD:

```text
py -m pytest tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py -q
py -m pytest tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py -q
py -m pytest tests/unit/test_connlab_serial_complex_state.py tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q
py -m py_compile scripts/connlab_personal_task.py scripts/connlab_model_routing_integration_reconciliation.py
git diff --check
```

The integration tests must use disposable local clones/worktrees and cover: direct expanded approval
against `INTEGRATION_BLOCKED` is zero-write blocked; complete two-approval scope authority succeeds;
no-worktree/no-executor-write before that checkpoint; host relocation exact success and replay; dirty,
stale, unapproved, wrong-branch, wrong-path, wrong-action, or partially registered host zero-write
blocks; final exact success; exact
committed replay; every mismatch listed above; injected pre-write failure; rendered-target equality;
one board write only; one board-only durability commit; no merge creation; unchanged original lane;
and unchanged primary on every failed case. Before the live command, Integrator repeats all Git/evidence
hashes against real objects and performs a zero-write plan/dry run whose source/target/manifest digests
must equal the apply invocation.

### 10.8 Risk, Recovery, And Stop Conditions

The central risk is accepting a convenient descendant instead of the exact historical package. It is
mitigated by task-specific constants, commit-addressed evidence, exact topology/path manifests, CAS on
the source board bytes, immutable reviewed executor code, and no installation on primary. A crash or
failure before the atomic board replacement writes nothing. A failure after replacement but before the
board-only commit preserves the dirty board and stops; no automatic rollback is authorized. Any later
correction requires a new User-approved governance action.

No destructive rollback exists for this amendment. The old merge and original lane are preserved.
Any scope expansion, unknown commit/path, validation failure, inability to prove clean state, need for
a second board write, or need to merge/cherry-pick/install the executor returns to Planner/User.

### 10.9 Exact Amendment Approved-Request

Canonicalization is the exact single-line UTF-8 JSON below, with no BOM and no trailing newline.

```json
{"schema":"connlab.personal-task-approved-request","version":1,"task_id":"TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING","summary":"Complete the already-reviewed model-routing task through an exact, one-time integration reconciliation without relaxing normal workflow contracts.","kind":"planned","may_touch":[".agents/skills/connlab-lane-orchestrator/SKILL.md","docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md","tests/unit/test_task_scoped_role_thread_lifecycle_governance.py","docs/task_board.md","scripts/connlab_personal_task.py","scripts/connlab_model_routing_integration_reconciliation.py","tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py","tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py"],"expected_file_count":8,"classification_reason":"Strict superset of the already-approved four paths, adding only the task-specific unmerged reconciliation writer/helper and bounded proof tests; product behavior and normal workflow contracts remain unchanged.","targeted_validation":["py -m pytest tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py -q","py -m pytest tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py -q","py -m pytest tests/unit/test_connlab_serial_complex_state.py tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q","py -m py_compile scripts/connlab_personal_task.py scripts/connlab_model_routing_integration_reconciliation.py","git diff --check"],"forbidden_categories":{"api_contract":false,"database":false,"schema_or_migration":false,"persistence":false,"authority":false,"public_drive_workflow":false,"business_rule_semantics":false,"destructive_action":false,"external_mutation":false}}
```

SHA-256: `5eb00a105d1e0b5a047423c46b84436d854bf9c4ee85a54546c23932cedb2d34`

Both Approve calls must receive byte-identical JSON and the same exact committed Plan/approval refs.
The first call is legal only under the truthful `SCOPE_EXPANDED` blocker and records the strict
superset. The second is legal only after the real Planner-ready transition and creates the complete
pre-implementation machine authority, including `approved_code_paths`.

### 10.10 Canonical Reconciliation Manifest

SHA-256 is over the exact single-line UTF-8 JSON below, with no BOM and no trailing newline.

```json
{"schema":"connlab.integration-reconciliation-amendment","version":2,"task_id":"TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING","legacy_board_head":"3d0884e12cc39e7b416da75ab01aaffd36c6418c","qa_subject":"ad7dac819268ae77781709b626aea4f624a7a740","lane_head":"f7770b6a6a82a36f946d16145a2124f6330961e1","merge_commit":"093d48966b15c536b7411b3cc4cdca1e1e0d4faf","merge_parents":["a632f01c96de457deec901fedb271addfd0b77fb","f7770b6a6a82a36f946d16145a2124f6330961e1"],"merge_tree":"891f0cd28ebfd86d8ae8b1fff6e92160b16b71ca","blocker_head":"82370aeb1690f1a6e1ebda7d37048f5f926d7570","blocker_parent":"093d48966b15c536b7411b3cc4cdca1e1e0d4faf","source_board_blob_sha256":"9083399d2a3a091afc634ab3253df86e8f3c0754fd73558bdc0b959b0c336d88","source_board_worktree_sha256":"295974ff98e874862d2505e8ff05ebab6977d738f74e40a6937bcbe165bc6696","blocker_code":"INTEGRATION_BLOCKED","approved_request_sha256":"5eb00a105d1e0b5a047423c46b84436d854bf9c4ee85a54546c23932cedb2d34","authority_sequence":["SCOPE_EXPANDED","ALLOW_SCOPE_AMEND","ALLOW_RESUME","PLANNER_READY","ALLOW_APPROVE","DEVELOPER_INVOCATION","HOST_REBIND"],"executor_paths":["scripts/connlab_personal_task.py","scripts/connlab_model_routing_integration_reconciliation.py","tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py","tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py"],"target_state":"implemented_pending_human_review","target_phase":"human_review","target_head":"f7770b6a6a82a36f946d16145a2124f6330961e1","target_integrated_commit":"093d48966b15c536b7411b3cc4cdca1e1e0d4faf","target_worktree_lifecycle":"integrated","executor_disposition":"retained unmerged one-time reconciliation executor","forbidden":["remerge","history_rollback","manual_board_edit","generic_relaxation","push","cleanup"]}
```

SHA-256: `28546d74d94f8b32f1a2ce5e57951b9855ee87692c7b2cf8c6f04746867238c7`

Explicit approval must bind this committed Plan ref, the manifest SHA-256, the exact May Touch and
evidence paths, and the one-time no-merge executor design. Approval does not authorize Task B, product
changes, push, cleanup, or any general runtime relaxation.

`STATUS: INTEGRATION_RECONCILIATION_AUTHORITY_REVISION_PENDING_USER_APPROVAL`
