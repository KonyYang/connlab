# Orchestrator Latency And Model Routing — Short Implementation Plan

Task: `TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING`

Status: `INTEGRATION_ANCESTRY_RECONCILIATION_AMENDMENT_PENDING_USER_APPROVAL`

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
completed; local merge exists; acceptance remains blocked.`

Repository facts frozen by this amendment are:

- At the start of this planning-only revision, primary was clean at
  `5ce3ca0eca760314e7b26a385f681cb5c2b314e0`.
- Board machine authority remains `state=running`, `phase=blocked`,
  `blocker=INTEGRATION_BLOCKED`, and `resume_phase=integration`.
- Board `active.scope_contract.may_touch` and `complex_context.approved_code_paths` each remain the
  original four-path scope. The eight-path authority chain has not run.
- Board `complex_context.head_sha=3d0884e12cc39e7b416da75ab01aaffd36c6418c`,
  `integrated_commit=null`, and `worktree_lifecycle=integration_ready`.

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
- The existing merge is present in primary ancestry but has not been recorded as accepted by the
  board. No reconciliation branch/worktree exists; reconciliation Developer/Reviewer/QA/Integrator
  have not begun; and final CAS, human review, and closeout have not run.

These frozen facts must not be restated as `integrator_accepted`, task complete, integration recorded,
or ready for close.

The first committed amendment is
`e07c2ec07cb741ebb91cc335566e5dd91ee47c75`, whose parent is exact `82370aeb...` and whose path
delta is only the Task, this Plan, and Planner evidence. The machine-authority correction is
`5ce3ca0eca760314e7b26a385f681cb5c2b314e0`, a clean child of `e07c2ec0...` with the same
three-path delta. This review-order correction must be one further clean child of `5ce3ca0e...`, again
with only those three paths. The later User approval must
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

Create the branch/worktree from the exact committed final approval-authority checkpoint. Until live
rebind succeeds it is a Plan-bound candidate review resource owned by the already registered durable
host and its pending role actions; it is not yet the board's active host. Under the live Developer
invocation, Developer completes the entire task-specific writer/helper and both tests on the four new
paths, producing immutable implementation subject `B`. The Developer evidence-only commit `D` must
bind `B`, its base/path digest, clean candidate branch/worktree/index, scope/approval digest, and the
pending Developer action. The normal Developer callback records subject `B` and evidence `D` before
any live rebind.

The current durable host then dispatches independent Reviewer and mandatory QA normally. Reviewer
reviews exact `B`, the relocation/final-CAS code, tests, and all negative matrices, then commits
evidence-only `R` and returns pass for subject `B`. QA independently reruns the complete bounded suite
on `B`, checks the candidate through evidence heads, commits evidence-only `Q`, and returns pass for
subject `B`. The exact candidate topology must be
`approval-authority-base -> B -> D -> R -> Q`, with only the four fixed reconciliation evidence paths
after `B`. These are genuine existing-writer `begin-role` / `record-invocation` / `consume-callback`
events owned by the already registered durable host; they are not synthesized transition history and
do not change the board's Git host fields. The existing state machine permits the callback subject to
bind `B` while the role inspects the Plan-bound candidate resource. A Reviewer/QA blocker follows the
normal callback route and forbids rebind. If the production commands cannot reproduce this exact
sequence without a new state-machine exception, execution stops with an authority blocker before any
live task-specific board write.

Only after the committed QA-pass transition has entered `integration` may Integrator be dispatched.
Integrator performs a pre-rebind audit, commits evidence-only `I`, and keeps its real invocation/
callback pending. The physical candidate must be clean at `I`, and the executable bytes at `I` must be
identical to reviewed subject `B`. Integrator then runs the reviewed `rebind-reconciliation-host`
command. It atomically changes `task_branch`, `task_worktree`, `base_sha`, `head_sha`, and
`worktree_lifecycle=integration_ready` to the candidate resource while preserving the exact pending
Integrator action, subject `B`, D/R/Q/I evidence refs, scope, approved paths, locks, Plan/approval refs,
original-lane evidence, and WIP=1. The original branch/worktree stays clean and unchanged at
`f7770b6a`.

The rebind board checkpoint must be exact-path committed and re-read before final CAS. If Reviewer/QA
attestation is missing, their subjects differ from `B`, code bytes changed after `B`, the Integrator
action/evidence is incomplete, or the candidate is dirty, live rebind returns a stable zero-write
blocker. No role may write the primary board except through normal reviewed writer transitions or,
after Reviewer/QA pass, these two reviewed task-specific commands. Thus both task-specific live writes
use code that has already passed independent Reviewer and QA.

Immediately before live rebind, the source board must have these exact facts:

- `control.state=running`, `active.phase=integration`, `complex_context.current_role=Integrator`;
- `pending_callback.state=callback_pending`, bound to the exact live Integrator action ID, role,
  attempt, invocation, and evidence checkpoint `I`;
- `host_thread_id=019fb3d4-12a5-73b3-be8e-e59686fa39a9`,
  `host_id=host-task-governance-orchestrator-latency-and-model-routing`;
- `task_branch=codex/task-governance-orchestrator-latency-and-model-routing`,
  `task_worktree=D:\\PythonProject\\connlab-worktrees\\task-governance-orchestrator-latency-and-model-routing`,
  `base_sha=3d0884e12cc39e7b416da75ab01aaffd36c6418c`,
  `head_sha=3d0884e12cc39e7b416da75ab01aaffd36c6418c`;
- the exact approved eight-path scope, Plan/approval refs, D/R/Q evidence, and
  `worktree_lifecycle=integration_ready`; and
- original worktree clean at `f7770b6a...`, candidate worktree clean at `I`, with executable bytes at
  `I` identical to `B`.

The atomic rebind target preserves `control.state=running`, `active.phase=integration`, the same
`current_role=Integrator`, pending callback/action/attempt/invocation, host thread/ID, scope,
Plan/approval refs, locks, subject `B`, and D/R/Q/I evidence. It changes only the registered Git host
facts to `task_branch=codex/task-governance-orchestrator-latency-model-routing-reconciliation`,
`task_worktree=D:\\PythonProject\\connlab-worktrees\\task-governance-orchestrator-latency-model-routing-reconciliation`,
`base_sha=<exact committed final approval-authority checkpoint>`, `head_sha=<I>`, and
`worktree_lifecycle=integration_ready`. Exact committed replay may be a zero-write no-op; partial,
different, or divergent registration is blocked. Rebind does not consume the Integrator callback or
claim integration acceptance.

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
- `docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_developer.md@<D>#<exact-blob-sha256>`, with `STATUS: ready_for_review`;
- `docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_reviewer.md@<R>#<exact-blob-sha256>`, with `STATUS: reviewer_pass`;
- `docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_qa.md@<Q>#<exact-blob-sha256>`, with `STATUS: qa_pass`;
- `docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_integrator.md@<I>#<exact-blob-sha256>`, with `STATUS: pre_rebind_attestation_ready`.

The command must verify each future commit/path/blob hash, role `STATUS`, model-routing header,
ancestry `approval-authority-base -> B -> D -> R -> Q -> I`, exact path delta for each role, and a clean reconciliation
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
- top-level `retained_history` appends the exact frozen executor-resource record defined below; and
- all unrelated control, queue, approved eight-path scope, role invocation, and task fields remain
  byte-for-byte semantically unchanged.

The executor retained-history record reuses the existing top-level `retained_history` array; it adds no
board schema or second resource registry. Its object has exactly these fifteen keys and values—no
omissions or extras. `recorded_at` is the resource's retained timestamp (`retained_at` semantics) and
must equal the single attested final-CAS timestamp:

```json
{"schema":"connlab.retained-task-resource","version":1,"task_id":"TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING","status":"retained","owner":"permanent Orchestrator governance","disposition":"retained unmerged one-time reconciliation executor","branch":"codex/task-governance-orchestrator-latency-model-routing-reconciliation","worktree":"D:\\PythonProject\\connlab-worktrees\\task-governance-orchestrator-latency-model-routing-reconciliation","head_sha":"<I>","clean":true,"evidence_ref":"docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_integrator.md@<I>#<sha256>","integrated_commit":null,"plan_ref":"<exact-approved-plan-ref>","approval_ref_sha256":"<sha256-of-exact-approval-ref>","recorded_at":"<same-attested-CAS-timestamp>"}
```

Before append, the writer verifies Git worktree registration, exact branch/HEAD `I`, clean index,
evidence bytes/status/model route, Plan/approval hashes, and the D/R/Q/I ancestry/path manifest. The
record identity is `(schema, version, task_id, branch, worktree)`. If no identity exists, append once.
`integrated_commit` is required to be JSON null because this executor is intentionally unmerged. If an
existing record is byte-for-byte identical and its current branch/worktree/HEAD/clean state and
evidence hash still match, exact replay may return `ALREADY_APPLIED` with zero writes. If the same
identity differs in any field, or branch/worktree/HEAD/evidence/Git facts drift, return
`BLOCKED_RETAINED_RESOURCE_CONFLICT` with zero writes.

At later User close, pre-close read-only reconciliation must verify both resources: the normal
`record-closeout` proof continues to bind the original integrated lane at `f7770b6a`, while the frozen
executor record, physical clean worktree at `I`, evidence ref, and
`complex_context.retained_resource_refs` entry must still agree. Normal closeout must preserve the
executor retained-history object byte-for-byte. Post-close verification requires the object to remain
in `retained_history` with the same owner/disposition and the original lane to be the resource recorded
in `last_closed`. The original integrated lane is owned by the normal task closeout and remains in
`complex_context` until close and then `control.last_closed`; the unmerged executor is owned by
`permanent Orchestrator governance` and remains separately in `retained_history` plus
`complex_context.retained_resource_refs`. Neither record may overwrite, impersonate, or replace the
other. Any mismatch blocks close before a board write.

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
managed as evidence, not implementation scope. The only task-specific primary writes after independent
review are the atomic host rebind and the final atomic `docs/task_board.md` target; each must be
followed by its own exact-path board-only durability commit. Existing reviewed V2 commands remain the
only writers for the earlier scope and normal role transitions.

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
unregistered host; live role or Integrator action mismatch; executor manifest drift; retained-resource target
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
no worktree creation when the second Approve is absent; no creation or rebind when
`scope_contract.may_touch` and `approved_code_paths` differ; no executor write before that checkpoint;
live rebind before Reviewer pass, before QA pass, with missing/mismatched B/D/R/Q/I proof, or with
attestation commit/evidence/hash/status/ancestry drift or post-review code drift is zero-write blocked;
reviewed host relocation exact success and exact committed replay; dirty, stale, unapproved,
wrong-branch, wrong-worktree, wrong-head, wrong-action, or partially registered host zero-write blocks;
retained record exact append/replay, same-identity divergent replay, pre-close reconciliation, close
preservation, and post-close reconciliation; final exact success and proof that final CAS cannot
retroactively authorize an unapproved worktree, unreviewed rebind, or incomplete role chain; exact
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
{"schema":"connlab.integration-reconciliation-amendment","version":3,"task_id":"TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING","planning_revision_parent":"5ce3ca0eca760314e7b26a385f681cb5c2b314e0","legacy_board_head":"3d0884e12cc39e7b416da75ab01aaffd36c6418c","qa_subject":"ad7dac819268ae77781709b626aea4f624a7a740","lane_head":"f7770b6a6a82a36f946d16145a2124f6330961e1","merge_commit":"093d48966b15c536b7411b3cc4cdca1e1e0d4faf","merge_parents":["a632f01c96de457deec901fedb271addfd0b77fb","f7770b6a6a82a36f946d16145a2124f6330961e1"],"merge_tree":"891f0cd28ebfd86d8ae8b1fff6e92160b16b71ca","blocker_head":"82370aeb1690f1a6e1ebda7d37048f5f926d7570","blocker_parent":"093d48966b15c536b7411b3cc4cdca1e1e0d4faf","source_board_blob_sha256":"9083399d2a3a091afc634ab3253df86e8f3c0754fd73558bdc0b959b0c336d88","source_board_worktree_sha256":"295974ff98e874862d2505e8ff05ebab6977d738f74e40a6937bcbe165bc6696","source_state":"running","source_phase":"blocked","source_resume_phase":"integration","source_integrated_commit":null,"source_worktree_lifecycle":"integration_ready","original_scope_paths":[".agents/skills/connlab-lane-orchestrator/SKILL.md","docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md","tests/unit/test_task_scoped_role_thread_lifecycle_governance.py","docs/task_board.md"],"blocker_code":"INTEGRATION_BLOCKED","approved_request_sha256":"5eb00a105d1e0b5a047423c46b84436d854bf9c4ee85a54546c23932cedb2d34","authority_sequence":["SCOPE_EXPANDED","ALLOW_SCOPE_AMEND","ALLOW_RESUME","PLANNER_READY","ALLOW_APPROVE","DEVELOPER_INVOCATION","DEVELOPER_READY_B_D","REVIEWER_PASS_R","QA_PASS_Q","INTEGRATOR_INVOCATION_I","HOST_REBIND","FINAL_CAS"],"pre_rebind_gate":"reviewer_and_qa_pass_on_exact_B_before_live_write","attestation_statuses":{"D":"ready_for_review","R":"reviewer_pass","Q":"qa_pass","I":"pre_rebind_attestation_ready"},"pre_rebind_host":{"state":"running","phase":"integration","current_role":"Integrator","pending_callback_state":"callback_pending","host_thread_id":"019fb3d4-12a5-73b3-be8e-e59686fa39a9","host_id":"host-task-governance-orchestrator-latency-and-model-routing","branch":"codex/task-governance-orchestrator-latency-and-model-routing","worktree":"D:\\PythonProject\\connlab-worktrees\\task-governance-orchestrator-latency-and-model-routing","base_sha":"3d0884e12cc39e7b416da75ab01aaffd36c6418c","head_sha":"3d0884e12cc39e7b416da75ab01aaffd36c6418c"},"post_rebind_host":{"state":"running","phase":"integration","current_role":"Integrator","pending_callback_state":"callback_pending","host_thread_id":"019fb3d4-12a5-73b3-be8e-e59686fa39a9","host_id":"host-task-governance-orchestrator-latency-and-model-routing","branch":"codex/task-governance-orchestrator-latency-model-routing-reconciliation","worktree":"D:\\PythonProject\\connlab-worktrees\\task-governance-orchestrator-latency-model-routing-reconciliation","base_sha":"<approval-authority-checkpoint>","head_sha":"<I>"},"executor_paths":["scripts/connlab_personal_task.py","scripts/connlab_model_routing_integration_reconciliation.py","tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py","tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py"],"retained_record_keys":["schema","version","task_id","status","owner","disposition","branch","worktree","head_sha","clean","evidence_ref","integrated_commit","plan_ref","approval_ref_sha256","recorded_at"],"retained_identity_keys":["schema","version","task_id","branch","worktree"],"executor_integrated_commit":null,"target_state":"implemented_pending_human_review","target_phase":"human_review","target_head":"f7770b6a6a82a36f946d16145a2124f6330961e1","target_integrated_commit":"093d48966b15c536b7411b3cc4cdca1e1e0d4faf","target_worktree_lifecycle":"integrated","executor_disposition":"retained unmerged one-time reconciliation executor","forbidden":["unreviewed_live_writer","remerge","history_rollback","manual_board_edit","generic_relaxation","push","cleanup","task_b"]}
```

SHA-256: `a882f4a9eb89b342c27ade4d01db0c03b53db11a7ccc878c75abb7d8f4eab0c0`

Explicit approval must bind this committed Plan ref, the manifest SHA-256, the exact May Touch and
evidence paths, and the one-time no-merge executor design. Approval does not authorize Task B, product
changes, push, cleanup, or any general runtime relaxation.

`STATUS: INTEGRATION_RECONCILIATION_AUTHORITY_REVISION_PENDING_USER_APPROVAL`

## 11. Bounded Integration Ancestry Reconciliation Amendment

### 11.1 Discovery And Frozen Baseline

Confirmed by the User:

- approval checkpoint remains immutable authority, but the one-edge direct-parent assumption must be
  replaced by a fail-closed Reviewer/QA fix-loop grammar;
- every commit/path/evidence/status/subject/model/hash must be verified; arbitrary ancestry is not
  sufficient;
- the final direct tail remains `final B -> Developer ready -> Reviewer pass -> QA pass -> Integrator
  ready`;
- product code, normal workflow schema, original lane, existing merge, history and remote state remain
  immutable; no rebind or Final CAS is authorized before this amendment is approved and reviewed.

Confirmed by repository evidence:

- primary is clean at `d2b9b3a3b68970d261678989b249b3a6477bfde6`;
- raw board SHA-256 is
  `b5c132c16762e6a1f5545a2ffc4c9af7219776067b0a254a6221c1c2817e389d`, with
  `running/blocked/INTEGRATION_BLOCKED`, null role/pending callback, and exact blocker evidence
  `docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_integrator.md@11cf2532e0275d07c3fb9ba8d7a85d7d710a6e69#ea23c4cc2a0ad7a819e1c83fba78c954c50216de09108074f879a9d93904e477`;
- scope contract and approved code paths are the same previously approved ordered eight paths;
- candidate and index are clean at `11cf2532e0275d07c3fb9ba8d7a85d7d710a6e69`; original lane remains clean at
  `f7770b6a6a82a36f946d16145a2124f6330961e1`; existing merge remains
  `093d48966b15c536b7411b3cc4cdca1e1e0d4faf`;
- approval checkpoint `666a20d745fd72f6cbfd280d6ed1e29c0b023dda` is an ancestor of final reviewed subject
  `8c9f3a31ac44e03df8087684a038602e5532fefb`, but its direct child is initial implementation
  `ee35dbc2...`, not the final subject;
- the range is single-parent and contains only approved implementation deltas and fixed role evidence,
  but four real Reviewer-blocked events caused four Developer fix commits before `8c9f3a31...`;
- the reviewed helper currently constructs a literal
  `[approval_base, B, D, R, Q, I]` direct-parent list, causing the zero-write blocker.

Planner inference: no API/data/product scope change is needed. The correction belongs entirely to the
existing task-specific executor and its bounded tests. The current `resume_phase=integration` cannot
legally dispatch Developer, so implementation authority also needs a one-use review-before-write
adoption transition; omitting it would reproduce an authority deadlock. No blocking question remains.

### 11.2 Exact Frozen Historical Ledger

The canonical ledger is a compact JSON array of `[commit, token, bound-subject]` entries. SHA-256 of
the exact single-line UTF-8 JSON below, without BOM or trailing newline, is
`e2aa3a04075ded4d60919da10a2c530bae8832f2b60084c92a94d4fb54cbbf40`.

```json
[["ee35dbc255962624f928a58c84bad85246171bc7","implementation","ee35dbc255962624f928a58c84bad85246171bc7"],["673a9a276209c497fbda186ac347950a7cb56abf","developer_ready","ee35dbc255962624f928a58c84bad85246171bc7"],["cfa5a5b5e765046283c60daf889e8c5586871fbb","reviewer_blocked","ee35dbc255962624f928a58c84bad85246171bc7"],["6aab0b22cc348d70bfa075126a9d8c6a0a7ec0ed","implementation","6aab0b22cc348d70bfa075126a9d8c6a0a7ec0ed"],["2e25ace1bb0600fd9c9e8fae502687734cc71574","developer_ready","6aab0b22cc348d70bfa075126a9d8c6a0a7ec0ed"],["e58e8235e24fc5a3e0a49a879f7223008b0a5933","reviewer_blocked","6aab0b22cc348d70bfa075126a9d8c6a0a7ec0ed"],["bded8f2f626f68ef9795d694e2e6a4475629a117","implementation","bded8f2f626f68ef9795d694e2e6a4475629a117"],["cd1dfb160ff2b00542002999ff890b6284886cd5","developer_ready","bded8f2f626f68ef9795d694e2e6a4475629a117"],["7231d4cc6ad03d2723c614955b8ae1c97f7e86c1","reviewer_blocked","bded8f2f626f68ef9795d694e2e6a4475629a117"],["df5ee4e1e48f8a813430ae7facbcde1af3ecbd3e","implementation","df5ee4e1e48f8a813430ae7facbcde1af3ecbd3e"],["03d49ffc92470c47feb4b8856efaf4bf26366209","developer_ready","df5ee4e1e48f8a813430ae7facbcde1af3ecbd3e"],["96ed540569bda4a105d1ec18190f519162edb8e7","reviewer_blocked","df5ee4e1e48f8a813430ae7facbcde1af3ecbd3e"],["8c9f3a31ac44e03df8087684a038602e5532fefb","implementation","8c9f3a31ac44e03df8087684a038602e5532fefb"],["a6efc77a520112107bfd7ea3313f229e0b57a47b","developer_ready","8c9f3a31ac44e03df8087684a038602e5532fefb"],["ac4ec55878b46c7c61b84fba35169322e265ba3b","reviewer_pass","8c9f3a31ac44e03df8087684a038602e5532fefb"],["3ab4b1ec0bb9ebe683deefbf7ee44d4a0cec850f","qa_pass","8c9f3a31ac44e03df8087684a038602e5532fefb"],["34afed59ae24b2790340baa29c0ac0fb00221b6b","integrator_ready","8c9f3a31ac44e03df8087684a038602e5532fefb"],["11cf2532e0275d07c3fb9ba8d7a85d7d710a6e69","integrator_blocked","8c9f3a31ac44e03df8087684a038602e5532fefb"]]
```

The ledger is not trusted merely because the commit IDs are listed. Implementation must recompute
every parent, changed-path set, committed evidence bytes/SHA-256 and exact evidence fields. A mismatch
between recomputed classification and the ledger blocks the operation.

### 11.3 Executable Commit Grammar

The validator walks `git rev-list --reverse --topo-order --parents
approval-authority-base..final-subject` and rejects merges or missing commits. Each commit receives
exactly one token:

- `implementation`: changes a non-empty subset of the four approved executor paths and no other path;
- `developer_ready`: changes only the fixed Developer evidence path; exact task/role/status
  `ready_for_review`, subject equal the immediately preceding implementation, model
  `gpt-5.6-sol/medium/risk:integration_conflict`, and committed blob hash each occur exactly once;
- `reviewer_blocked` or `reviewer_pass`: changes only the Reviewer evidence path and binds the same
  subject/model tuple with exact status;
- `qa_blocked` or `qa_pass`: changes only the QA evidence path and binds the same subject/model tuple;
- `integrator_ready` or `integrator_blocked`: changes only the Integrator evidence path and binds the
  same subject/model tuple.

The deterministic state grammar is:

```text
implementation -> developer_ready -> reviewer_blocked -> implementation
implementation -> developer_ready -> reviewer_pass -> qa_blocked -> implementation
implementation -> developer_ready -> reviewer_pass -> qa_pass -> integrator_ready
```

Only the exact frozen historical prefix may additionally end
`integrator_ready -> integrator_blocked -> user-approved ancestry-amendment implementation`. That
edge is bound to source head `11cf2532...`, this committed Plan/approval, the source blocker evidence
and unchanged eight-path scope. It is not a reusable Integrator-to-Developer rule.

The future success tail must be a direct-parent chain:

```text
final implementation B_A -> Developer ready D_A -> Reviewer pass R_A
-> QA pass Q_A -> Integrator ready I_A
```

An unknown token, extra path, repeated/missing field, forged suffix/prefix, wrong subject, wrong hash,
role skip, non-linear parent, merge, post-review implementation, generic ancestor substitution or
history rewrite returns a stable zero-write blocker.

### 11.4 Review-Before-Write Adoption Authority

No production board writer runs while the amendment code is only Developer-reviewed. After the User
approves this committed Plan:

1. Existing reviewed `approve` may record the byte-identical eight-path request with the new Plan and
   approval refs; because scope is unchanged, the exact expected result is
   `ALLOW_APPROVAL_EVIDENCE_CORRECTION`, and the blocker remains.
2. The retained candidate at `11cf2532...` receives one bounded implementation `B_A`; its delta is
   limited to the four executor paths. Real Developer, independent Reviewer and mandatory QA agents
   produce the direct evidence tail `B_A -> D_A -> R_A -> Q_A`. Their capsules, actual agent IDs,
   model route and committed evidence are recorded in those evidence files. Reviewer/QA blocking
   findings may only route to a same-task implementation fix and restart the final tail.
3. Only after Reviewer and QA pass may the reviewed task-specific command
   `adopt-model-routing-ancestry-reconciliation` run. Plan mode must produce source/target/manifest
   digests without writing. Apply must consume exactly the blocked primary/board/Plan/approval,
   candidate start, `B_A/D_A/R_A/Q_A` chain, clean Git facts and unchanged original lane/merge.
4. Adoption performs one atomic board replacement and one board-only durability commit. It clears the
   exact blocker, records `developer_subject_commit=reviewer_subject_commit=qa_subject_commit=B_A`,
   appends exact `D_A/R_A/Q_A` evidence, preserves WIP/scope/host/merge facts, and enters
   `running/integration` with null current role and pending callback.
5. Normal production `begin-role`/`record-invocation` then creates the real Integrator authority.
   Integrator commits `I_A` as the direct child of `Q_A`; only then may the existing reviewed rebind
   and Final CAS plan/apply sequence run with the new committed Plan/manifest and `B_A/D_A/R_A/Q_A/I_A`.

Exact committed adoption replay may return `ALREADY_APPLIED` only after reconstructing the complete
transition from the parent board-only commit. Partial, divergent or later descendants block. Final
CAS cannot retroactively authorize the candidate, offline role attestations or adoption transition.

### 11.5 Exact May Touch, Must Not Touch And Locks

The machine-approved eight paths remain unchanged. Future implementation code may modify exactly:

1. `scripts/connlab_personal_task.py` — only registration/argument routing for the one task-specific
   adoption command;
2. `scripts/connlab_model_routing_integration_reconciliation.py`;
3. `tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py`;
4. `tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py`.

Role evidence is limited to the four fixed task-derived integration-reconciliation evidence paths.
`docs/task_board.md` is locked to reviewed writer transitions and exact board-only durability commits.
All eight approved paths are exclusive task locks; the original lane/worktree/branch, existing merge,
product/backend/frontend, normal serial schema/state tables, `run_task.ps1`, serial-board helper,
registry, frozen V1/V2, database/API/persistence/authority, remotes and retained resources are Must Not
Touch. No new worktree is created; the existing clean candidate is reused.

This planning turn itself changes exactly the Task, this Plan and Planner evidence. It does not modify
board/runtime/tests/candidate/original lane.

### 11.6 Validation Matrix

Required bounded TDD and disposable-repository proof:

- reproduce the current real `BLOCKED_RECONCILIATION_EVIDENCE` direct-parent failure before repair;
- exact frozen ledger and multiple Reviewer-blocked/Developer-fix rounds pass;
- Reviewer-blocked or QA-blocked followed by any token other than same-task implementation blocks;
- implementation extra path, evidence wrong path/task/role/status/subject/model/hash, duplicate or
  missing field, unknown commit, merge, skipped role, post-review code drift, ordinary arbitrary
  ancestor, rewritten parent and truncated/extended ledger all block with zero writes;
- final `B_A/D_A/R_A/Q_A/I_A` direct-parent tail is mandatory;
- adoption before Reviewer pass, before QA pass, with wrong Plan/approval/source board/candidate base,
  dirty worktree, wrong action/agent/model, scope mismatch or changed original lane/merge blocks;
- exact adoption plan/apply succeeds once, makes one board write and one board-only durability commit;
  exact committed replay is zero-write and divergent replay blocks;
- existing rebind/final success, replay, retained-resource, closeout and all prior negative matrices
  remain green; final CAS cannot recognize an unreviewed adoption;
- every failed case preserves board SHA and primary/candidate/original HEAD/status.

Commands:

```text
py -m pytest tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py -q
py -m pytest tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py -q
py -m pytest tests/unit/test_connlab_serial_complex_state.py tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q
py -m pytest tests/unit/test_connlab_personal_serial_workflow.py -q
py -m py_compile scripts/connlab_personal_task.py scripts/connlab_model_routing_integration_reconciliation.py
git diff --check
```

Reviewer performs a complete re-gate of the ancestry parser, adoption writer and all replay/negative
proof. QA independently reruns the complete matrix on the final reviewed HEAD. Integrator repeats a
zero-write plan whose source/target/manifest digests must be byte-identical to apply.

### 11.7 Risk And Recovery

The main risks are accepting arbitrary ancestry, treating evidence prose as authority, or using final
CAS to legitimize an unreviewed state transition. Mitigation is an exact frozen prefix plus executable
state grammar, commit-addressed evidence blobs, exact field cardinality, review-before-write adoption,
single-write CAS and committed replay reconstruction. A crash before replace is zero-write; a failure
after replace preserves dirty board bytes and stops without restore. No automatic rollback, rebase,
cherry-pick, reset, cleanup or branch deletion is authorized. Any path/behavior/authority expansion or
new unexplained failure returns to User.

The planning commit itself is independently reversible only by a separately authorized normal
single-parent `git revert <planning-commit>` after confirming it has not been approved or consumed.
Implementation/integration history is never rewritten.

### 11.8 Canonical Ancestry Amendment Manifest

SHA-256 is over the exact single-line UTF-8 JSON below, without BOM or trailing newline:
`1f715cc17617f831986768a9f6ae31b63e7b6f14a38b711b61aec39a5d7144a4`.

```json
{"schema":"connlab.model-routing-ancestry-reconciliation-amendment","version":1,"task_id":"TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING","planning_base":"d2b9b3a3b68970d261678989b249b3a6477bfde6","source_board_sha256":"b5c132c16762e6a1f5545a2ffc4c9af7219776067b0a254a6221c1c2817e389d","source_blocker":"INTEGRATION_BLOCKED","source_blocker_evidence":"docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_integrator.md@11cf2532e0275d07c3fb9ba8d7a85d7d710a6e69#ea23c4cc2a0ad7a819e1c83fba78c954c50216de09108074f879a9d93904e477","approval_authority_base":"666a20d745fd72f6cbfd280d6ed1e29c0b023dda","frozen_history_head":"11cf2532e0275d07c3fb9ba8d7a85d7d710a6e69","historical_final_subject":"8c9f3a31ac44e03df8087684a038602e5532fefb","frozen_history_ledger_sha256":"e2aa3a04075ded4d60919da10a2c530bae8832f2b60084c92a94d4fb54cbbf40","implementation_paths":["scripts/connlab_personal_task.py","scripts/connlab_model_routing_integration_reconciliation.py","tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py","tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py"],"evidence_paths":{"developer":"docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_developer.md","reviewer":"docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_reviewer.md","qa":"docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_qa.md","integrator":"docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_integrator.md"},"grammar":["implementation","developer_ready","reviewer_blocked","implementation","developer_ready","reviewer_pass","qa_blocked","implementation","developer_ready","reviewer_pass","qa_pass","integrator_ready"],"final_tail":["final_implementation","developer_ready","reviewer_pass","qa_pass","integrator_ready"],"adoption_command":"adopt-model-routing-ancestry-reconciliation","adoption_source_head":"11cf2532e0275d07c3fb9ba8d7a85d7d710a6e69","adoption_target_phase":"integration","adoption_review_gate":["developer_ready","reviewer_pass","qa_pass"],"forbidden":["arbitrary_ancestor","unknown_commit","extra_path","forged_evidence","role_skip","history_rewrite","manual_board_edit","rebind_before_adoption_review","remerge","push","cleanup"]}
```

The existing eight-path approved-request JSON remains byte-identical with SHA-256
`5eb00a105d1e0b5a047423c46b84436d854bf9c4ee85a54546c23932cedb2d34`; scope and risk facts do not
change. A later User approval must bind this new committed Plan ref, the manifest hash, ledger hash,
exact source blocker evidence and unchanged approved-request identity. Approval authorizes no
implementation until its same-scope approval-evidence correction is durably committed.

`STATUS: INTEGRATION_ANCESTRY_RECONCILIATION_AMENDMENT_PENDING_USER_APPROVAL`

## 12. Bounded Line-Budget Scope Expansion Amendment

### 12.1 Discovery And Frozen State

Confirmed by repository evidence:

- primary is clean at `36936c1426d46f7bef2062f6caaf05d466cd4a09`;
- the physical board SHA-256 is
  `1553b78b25da8f996f407e7863f2f226ca06eacf46a58be0f1bd38d5aa519c3b`;
- board authority is still `running/blocked/INTEGRATION_BLOCKED`, with the exact ancestry-amendment
  Plan/approval identity and matching ordered eight-path `scope_contract` and `approved_code_paths`;
- the sole approval-evidence correction is already committed; no later board transition occurred;
- candidate branch/worktree/index is clean at
  `481c5b81fc2e6457c066268ef998844d6fa3fc1d`, whose sole parent is the frozen history head
  `11cf2532e0275d07c3fb9ba8d7a85d7d710a6e69`;
- `11cf2532..481c5b81` changes exactly the four approved executor paths;
- the candidate passes 47 reconciliation unit tests, 71 reconciliation integration tests,
  43 compatibility tests, 13 personal-workflow tests, both `py_compile` checks and
  `git diff --check`;
- `scripts/connlab_model_routing_integration_reconciliation.py` is 715 lines and
  `tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py` is
  578 lines, violating the project-wide Python 500-line hard limit;
- no `D_A` Developer evidence exists, so `481c5b81...` is a safe intermediate checkpoint, not a
  reviewable final subject;
- original integrated lane remains clean at
  `f7770b6a6a82a36f946d16145a2124f6330961e1`;
- adoption, rebind, Final CAS, new merge, push and cleanup have not run.

Confirmed by User: resolve the blocker without discarding the safe checkpoint. Planner inference: a
mechanical two-file split is the minimum compliant correction. Waiving the hard limit or continuing
with an oversized subject is forbidden.

### 12.2 Exact Scope Amendment

The machine-approved scope must expand from eight to ten paths by adding only:

1. `scripts/connlab_model_routing_ancestry_contract.py`
2. `tests/integration/test_task_governance_orchestrator_latency_model_routing_ancestry_adoption.py`

The complete ten-path machine scope is:

1. `.agents/skills/connlab-lane-orchestrator/SKILL.md`
2. `docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md`
3. `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py`
4. `docs/task_board.md`
5. `scripts/connlab_personal_task.py`
6. `scripts/connlab_model_routing_integration_reconciliation.py`
7. `scripts/connlab_model_routing_ancestry_contract.py`
8. `tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py`
9. `tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py`
10. `tests/integration/test_task_governance_orchestrator_latency_model_routing_ancestry_adoption.py`

The bounded Developer continuation may modify only executor paths 5-10 plus the fixed Developer
evidence path. Paths 1-4 remain governed by the original accepted model-routing package and board-only
writer transitions; they are not refactoring scope. Task, this Plan and Planner evidence belong only
to the current planning commit. Reviewer, QA and Integrator may change only their fixed task-derived
evidence paths.

Locked and Must Not Touch remain: product/backend/frontend code, API/database/schema/migration/
persistence/authority/public-drive/business semantics, normal serial state-machine behavior, board
schema, original lane, existing merge, retained/frozen/cancelled resources, remote state and Task B.
No path outside the ten-path authority and fixed evidence paths may be added implicitly.

### 12.3 File-Level Split Contract

`scripts/connlab_model_routing_ancestry_contract.py` receives the cohesive repository-proof boundary:

- commit-addressed Git reads and exact changed-path checks;
- exact one-occurrence evidence-field parsing;
- evidence path/blob/hash/task/role/status/subject/model validation;
- commit classification and the frozen Reviewer/QA fix-loop grammar;
- ancestry/adoption repository verification used by the transition helper.

`scripts/connlab_model_routing_integration_reconciliation.py` retains:

- payload and active-context validation;
- rebind/adoption/final target rendering;
- live Integrator and retained-resource validation;
- committed replay reconstruction;
- transition/CAS orchestration.

The split must use explicit imports and preserve stable blocker codes and zero-write behavior. It must
not introduce a second state machine, a generic ancestry allowance or a compatibility fallback.

`tests/integration/test_task_governance_orchestrator_latency_model_routing_ancestry_adoption.py`
receives the adoption-specific disposable-repository success/replay/drift matrix and only the minimal
fixtures needed by those tests. The existing integration module retains rebind, Final CAS,
retained-resource, durability and closeout coverage. Test cases may be mechanically relocated but not
dropped or replaced by source-string assertions.

Line gates at the final split subject:

- every modified Python file is at most 500 physical lines;
- the new ancestry contract and adoption integration modules target fewer than 300 lines each;
- no semicolon compression, generated minification or test-parametrization trick may be used merely
  to evade the line count.

### 12.4 Machine Authority And Continuation

The current board has eight approved paths, so neither new file may be created before a new exact User
approval is durably reflected in machine authority. After approval, use only the existing reviewed
writer and canonical argv-array transport:

1. record a truthful `SCOPE_EXPANDED` blocker whose `dirty_paths` are exactly the two new paths and
   whose evidence ref binds this committed Plan/Planner evidence;
2. first Approve records the ten-path `scope_contract` while leaving the old eight
   `approved_code_paths` unchanged;
3. resume to planning, record the real inline Planner-ready event, and perform the byte-identical
   second Approve;
4. verify a committed board checkpoint with matching ordered ten-path `scope_contract` and
   `approved_code_paths`, the new Plan/approval refs, clean primary/candidate/original lane and no
   pending callback;
5. only then continue the existing candidate from exact `481c5b81...`.

No duplicate worktree or branch is created. `481c5b81...` remains immutable in history and is the
continuation base. The next implementation commit must be a direct child, change only executor paths
5-10, and produce the final line-compliant subject. Its evidence-only child is the first legal `D_A`.
Normal independent Reviewer and mandatory QA follow. Only their pass chain may authorize the already
planned one-use ancestry adoption, normal Integrator authority, rebind and Final CAS.

If the production writer cannot express this exact scope sequence, or any board/head/hash/scope/
evidence/cleanliness fact drifts, stop zero-write and return to User. Final CAS cannot retroactively
approve either new path.

### 12.5 Validation Matrix

Required validation on the final split subject:

```text
py -m pytest tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py -q
py -m pytest tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py tests/integration/test_task_governance_orchestrator_latency_model_routing_ancestry_adoption.py -q
py -m pytest tests/unit/test_connlab_serial_complex_state.py tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q
py -m pytest tests/unit/test_connlab_personal_serial_workflow.py -q
py -m py_compile scripts/connlab_personal_task.py scripts/connlab_model_routing_integration_reconciliation.py scripts/connlab_model_routing_ancestry_contract.py
git diff --check
```

Executable assertions must additionally prove:

- all modified Python files are at most 500 physical lines;
- the complete pre-split 47/71 behavior matrix remains represented and green after relocation;
- exact real history and multiple Reviewer-blocked fix loops pass;
- wrong path/task/role/status/subject/model/hash, unknown commit, skipped role, merge, rewritten
  parent, arbitrary ancestry and truncated/extended ledger remain stable zero-write blockers;
- adoption exact plan/apply/replay remains one-use and fail-closed;
- rebind, Final CAS, retained-resource and closeout suites remain green;
- any failure preserves board SHA and primary/candidate/original-lane HEAD and clean status;
- absence of either newly approved path, partial ten-path authority, or execution before the second
  Approve blocks before candidate modification.

Reviewer performs a complete re-gate of the split boundary and all moved tests. QA independently runs
the complete matrix on the final reviewed HEAD. Integrator must repeat exact zero-write plan proof
before any live adoption/rebind/Final CAS.

### 12.6 Risk And Recovery

Primary risk is behavior drift hidden by a structural split. Mitigations are an immutable continuation
base, exact path-delta checks, full pre-split behavior preservation, explicit import boundary and
independent Reviewer/QA gates. No automatic rollback is authorized. A failed split remains on the
candidate branch with its exact owner and evidence; primary, original lane and existing merge remain
untouched. Reset, restore, stash, rebase, cherry-pick, history rewrite, push and cleanup are forbidden.

### 12.7 Exact Ten-Path Approved-Request

Canonicalization is the exact single-line UTF-8 JSON below, without BOM or trailing newline.

```json
{"schema":"connlab.personal-task-approved-request","version":1,"task_id":"TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING","summary":"Complete the already-reviewed model-routing task through an exact, one-time integration reconciliation without relaxing normal workflow contracts.","kind":"planned","may_touch":[".agents/skills/connlab-lane-orchestrator/SKILL.md","docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md","tests/unit/test_task_scoped_role_thread_lifecycle_governance.py","docs/task_board.md","scripts/connlab_personal_task.py","scripts/connlab_model_routing_integration_reconciliation.py","scripts/connlab_model_routing_ancestry_contract.py","tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py","tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py","tests/integration/test_task_governance_orchestrator_latency_model_routing_ancestry_adoption.py"],"expected_file_count":10,"classification_reason":"Strict superset of the approved eight paths, adding only one bounded ancestry contract module and one bounded adoption integration-test module so the reviewed implementation can satisfy the mandatory Python 500-line hard limit without changing product behavior or reconciliation authority semantics.","targeted_validation":["py -m pytest tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py -q","py -m pytest tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py tests/integration/test_task_governance_orchestrator_latency_model_routing_ancestry_adoption.py -q","py -m pytest tests/unit/test_connlab_serial_complex_state.py tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q","py -m pytest tests/unit/test_connlab_personal_serial_workflow.py -q","py -m py_compile scripts/connlab_personal_task.py scripts/connlab_model_routing_integration_reconciliation.py scripts/connlab_model_routing_ancestry_contract.py","git diff --check"],"forbidden_categories":{"api_contract":false,"database":false,"schema_or_migration":false,"persistence":false,"authority":false,"public_drive_workflow":false,"business_rule_semantics":false,"destructive_action":false,"external_mutation":false}}
```

SHA-256: `b5490214cbd0753d24ae4d6dac944c7a07b2d38769f5e96b37362d2b457dde22`

### 12.8 Canonical Line-Budget Amendment Manifest

SHA-256 is over the exact single-line UTF-8 JSON below, without BOM or trailing newline:
`557dcd22670eee1fcf8f5304200a9b324b734e1f533a25500ddd3cc85683e0ba`.

```json
{"schema":"connlab.model-routing-line-budget-scope-amendment","version":1,"task_id":"TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING","planning_base":"36936c1426d46f7bef2062f6caaf05d466cd4a09","source_board_sha256":"1553b78b25da8f996f407e7863f2f226ca06eacf46a58be0f1bd38d5aa519c3b","source_state":"running","source_phase":"blocked","source_blocker":"INTEGRATION_BLOCKED","source_plan_ref":"docs/task_governance_orchestrator_latency_and_model_routing_plan.md@7ea0f5f3b4439eab14a2fbe7d383db845617d1a6#4598a5e0f72e0ac820e57cd865117a74d1a492e1c508b305b0ad3268d1a47eaf","source_scope_count":8,"source_approved_count":8,"base_ancestry_manifest_sha256":"1f715cc17617f831986768a9f6ae31b63e7b6f14a38b711b61aec39a5d7144a4","frozen_ledger_sha256":"e2aa3a04075ded4d60919da10a2c530bae8832f2b60084c92a94d4fb54cbbf40","oversized_subject":"481c5b81fc2e6457c066268ef998844d6fa3fc1d","oversized_parent":"11cf2532e0275d07c3fb9ba8d7a85d7d710a6e69","oversized_subject_paths":["scripts/connlab_personal_task.py","scripts/connlab_model_routing_integration_reconciliation.py","tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py","tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py"],"observed_line_counts":{"scripts/connlab_model_routing_integration_reconciliation.py":715,"tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py":578},"new_paths":["scripts/connlab_model_routing_ancestry_contract.py","tests/integration/test_task_governance_orchestrator_latency_model_routing_ancestry_adoption.py"],"split_contract":{"production":"move commit-addressed Git primitives, exact evidence parsing, history classification, fix-loop grammar and adoption repository proof into the ancestry contract module; keep target rendering, transition orchestration and CAS in the reconciliation helper","tests":"move adoption-specific disposable-repository cases and only their bounded fixtures into the ancestry adoption module","behavior_change":false,"python_hard_limit":500},"continuation_base":"481c5b81fc2e6457c066268ef998844d6fa3fc1d","required_final_tail":["final_split_subject","developer_ready","reviewer_pass","qa_pass","integrator_ready"],"forbidden":["line_limit_waiver","generic_ancestor_relaxation","product_change","schema_change","manual_board_edit","remerge","rebase","push","cleanup"]}
```

This section supersedes only the implementation-path list and approved-request identity of section 11.
The frozen historical ledger, ancestry grammar, original lane/merge, review-before-write adoption,
retained-resource contract and all fail-closed conditions remain unchanged.

`STATUS: LINE_BUDGET_SCOPE_EXPANSION_PENDING_USER_APPROVAL`

## 13. Post-QA Adoption-Source Authority Reconciliation Amendment

### 13.1 Discovery And Frozen Baseline

User-confirmed objective: replace only the stale pre-amendment adoption source with a fail-closed
post-QA source produced by the normal Personal Serial Workflow V2 role chain. This is not a new
product behavior, state-machine bypass or scope expansion.

Repository-confirmed baseline at planning start:

- primary/index are clean at `34e44ad7bfa902df29d3e22e1e98a322e9648999`;
- raw `docs/task_board.md` SHA-256 is
  `707518c5b94daf95ba8efa6723d2891766ac98f43f18ebfb86879a505a7a9ecd`;
- board is `running/review`, current role `Reviewer`, attempt `7`, with callback action
  `18bb5a4d695cbb95513be10a21cebd26b33e58cbe976ae195b1c6750a264fd5f` pending;
- the ordered `scope_contract.may_touch` and `approved_code_paths` arrays are the same ten paths and
  are bound to Plan `0cf58120b5ced9580abb4a88daf5b4cc9c36f72c` and approved-request SHA-256
  `b5490214cbd0753d24ae4d6dac944c7a07b2d38769f5e96b37362d2b457dde22`;
- final line-budget subject `f349382605ba1f372a0b43c50c331eb3573cb0b6` is followed directly by
  Developer evidence `652b41329fe880491dfa93c53d8bf1ff7cb1317b` and Reviewer blocker evidence
  `aeb03bd9f72a68e6c66a06c788bfc0c55e19df62`;
- the candidate branch/worktree/index is clean at that Reviewer evidence commit; the original lane
  remains clean at `f7770b6a6a82a36f946d16145a2124f6330961e1`;
- Reviewer independently passed 48 reconciliation unit tests, 71 combined integration tests, 43
  compatibility tests, 13 personal-workflow tests, all line budgets, `py_compile` and
  `git diff --check`, then blocked because the helper still freezes primary `36936c1426...`, board
  SHA `1553b78b...` and `blocked/INTEGRATION_BLOCKED` as its only adoption source.

The current Reviewer callback is deliberately not consumed during planning. No implementation,
board transition, adoption, rebind or Final CAS is performed before exact User approval.

### 13.2 Authority Model And Exact Route

The complete planning range from baseline `34e44ad7...` through `P_REV`—the commit named by the future
approved Plan ref—changes only the Task, Plan and Planner evidence. Individual commits within that
range need not each contain all three paths; no commit in the range changes the board. After User
approval, the production writer must execute the following route without omissions or substitutions:

1. consume the exact pending Reviewer attempt-7 callback as `REVIEWER_BLOCKED`, producing one
   board-only durability commit and entering normal development;
2. record one canonical `APPROVAL_REQUIRED` blocker at stage `development`, with
   `resume_phase=awaiting_user_approval`, `retryable=true`, `requires_user=true`, non-empty
   `related_ids=["POST_QA_ADOPTION_SOURCE_AUTHORITY_RECONCILIATION"]`, all forbidden optional fields
   null/empty, and commit only the board;
3. resume that exact blocker using the same explicit User approval decision ref, enter
   `awaiting_user_approval`, and commit only the board;
4. run `Approve` with the byte-identical ten-path approved-request from section 12.7, the exact newly
   approved Plan ref and exact User approval ref, then commit only the board. This commit is `S_AUTH`;
5. begin and record one Developer invocation for the same task/host; create a bounded implementation
   fix `B_POSTQA` descended from `aeb03bd9...`, then its evidence-only `D_POSTQA` child; consume the
   exact Developer-ready callback with one board-only durability commit;
6. begin/record an independent Reviewer invocation, create an evidence-only `R_POSTQA` pass child,
   and consume its callback with one board-only durability commit;
7. begin/record mandatory QA, create an evidence-only `Q_POSTQA` pass child, and consume its callback
   with one board-only durability commit;
8. stop at the exact post-QA source `S_QA`: `state=running`, `active.phase=integration`,
   `active.blocker=null`, `current_role=null`, `pending_callback=null`, and
   `worktree_lifecycle=integration_ready`;
9. run the reviewed task-specific ancestry adoption in plan mode, then one byte-identical apply, and
   commit its sole `docs/task_board.md` mutation before any Integrator begin-role;
10. only after committed adoption may the normal Integrator, reviewed live rebind and Final CAS route
   continue under the existing approved contract.

The blocker in step 2 is the exact object below; `recorded_at` is replaced once by the attested UTC
timestamp and every other key/value is frozen:

```json
{"schema":"connlab.serial-task-blocker","version":1,"code":"APPROVAL_REQUIRED","stage":"development","reason":"Bind the approved post-QA adoption-source amendment before implementation.","dirty_paths":[],"failed_validation":null,"subject_commit":null,"evidence_ref":null,"native_action_id":null,"related_ids":["POST_QA_ADOPTION_SOURCE_AUTHORITY_RECONCILIATION"],"retryable":true,"requires_user":true,"resume_phase":"awaiting_user_approval","recorded_at":"<ATTESTED_UTC>"}
```

`S_AUTH` must be `running/development`, blocker/current role/pending callback null, matching ten-path
scope and approved paths, and bound to the new Plan/approval before the candidate changes. The exact
pre-authority chain `P_REV -> REVIEWER_BLOCKED callback -> APPROVAL_REQUIRED block -> resume ->
Approve/S_AUTH` is separately verified as four production-writer, single-parent, board-only durability
commits. Any implementation delta before committed `S_AUTH` blocks.

Every production-writer transition from `S_AUTH` through `S_QA` is a single-parent primary commit
whose only changed path is `docs/task_board.md`. The adoption proof must read every committed
parent/current board blob and classify the exact ordered events:

```text
Developer begin-role
-> Developer record-invocation
-> DEVELOPER_READY callback
-> Reviewer begin-role
-> Reviewer record-invocation
-> REVIEWER_PASS callback
-> QA begin-role
-> QA record-invocation
-> QA_PASS callback
```

For each event, reconstruct the expected target with the production writer contract and compare the
complete parsed control object and rendered bytes. Commit count, order, action/attempt/role identity,
source and target board SHA, and before/after state must match. A board-only commit is necessary but
not sufficient; any extra, missing, reordered, repeated, unknown or later board descendant blocks.

### 13.3 Post-QA Source Contract

The adoption payload binds runtime facts that cannot exist at planning time. All are mandatory exact
values, not inferred from the mutable current board:

- `S_AUTH` primary HEAD/raw board SHA and exact `running/development` authority, amendment Plan
  ref/hash, exact User approval ref/hash, amendment Planner evidence ref/blob hash and
  the manifest SHA-256 from section 13.8;
- planning baseline/head/board SHA, exact planning-range path set, Reviewer attempt-7 action and
  blocker evidence, and the four exact pre-authority writer commits;
- `S_QA` primary HEAD, its single-parent chain back to `S_AUTH`, and raw board SHA-256;
- exact ten-path `scope_contract`, `approved_code_paths`, newly approved amendment Plan/approval and
  approved-request SHA-256;
- task branch/worktree/base/head, host/thread/lifecycle and primary/candidate/original-lane clean Git
  facts;
- every allowed role action, attempt and invocation object in the durability route;
- `B_POSTQA`, `D_POSTQA`, `R_POSTQA`, `Q_POSTQA`, their direct-parent ancestry, exact evidence refs,
  committed blobs/SHA-256 and task/role/status/subject/model tuple;
- exact evidence-ref prefix before the route and exact D/R/Q suffix after it;
- `recorded_at`, expected source digest, expected target digest and manifest digest.

The final candidate tail must be direct parentage:

```text
B_POSTQA
-> D_POSTQA (Developer ready evidence only)
-> R_POSTQA (Reviewer pass evidence only)
-> Q_POSTQA (QA pass evidence only)
```

Earlier approved Reviewer-blocked fix loops remain validated by the frozen ancestry ledger. The new
route may add only the current exact Reviewer blocker followed by this one final fix/pass tail.
Unknown commits, extra paths, skipped roles, forged evidence, merge parents, rewritten history or an
ordinary arbitrary ancestor are not accepted.

### 13.4 Atomic Adoption Target And Replay

The adoption builder starts only from the verified `S_QA` committed object. It preserves state,
phase, blocker, lifecycle, host/lane facts, subject commits, D/R/Q evidence, required gates, the
ordered ten-path scope and the Plan/approval already committed at `S_AUTH`. Without adding a schema
key, the single atomic target:

- appends the exact committed Planner amendment evidence ref once to
  `active.complex_context.evidence_refs`;
- sets `active.updated_at` to the attested `recorded_at`;
- leaves `current_role` and `pending_callback` null and remains `running/integration`.

Plan mode computes canonical source, target and manifest digests from immutable committed inputs and
performs zero writes. Apply accepts those three exact digests and the identical payload, re-runs all
repository/source proofs, requires raw current bytes to equal the planned source, writes exactly once
through the production board writer and verifies the complete rendered target. The durability commit
must be a single-parent, board-only commit.

Exact committed replay reads `HEAD^:docs/task_board.md` and `HEAD:docs/task_board.md`, reconstructs the
same target from the committed parent and exact payload, and returns zero-write `ALREADY_APPLIED` only
when the complete objects, rendered bytes, source/target/manifest digests, Plan/approval/evidence refs
and Git topology all match. Partial application, stale input, forged target, divergent payload,
different digest or any later descendant returns a stable `BLOCKED_*` result with zero writes.

### 13.5 Exact May Touch, Must Not Touch And Locks

The machine scope remains the existing ordered ten paths. One same-scope `Approve` is mandatory before
implementation solely to bind the new committed Plan/approval; it must not change either path array.
The future bounded implementation delta is restricted further to these five paths:

1. `scripts/connlab_model_routing_integration_reconciliation.py`
2. `scripts/connlab_model_routing_ancestry_contract.py`
3. `tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py`
4. `tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py`
5. `tests/integration/test_task_governance_orchestrator_latency_model_routing_ancestry_adoption.py`

The fixed task-derived Developer evidence path is governance evidence, not implementation scope.
Reviewer, QA and Integrator may change only their fixed task-derived evidence paths. The production
writer alone may change `docs/task_board.md` after approval. This planning turn changes only the Task,
Plan and Planner evidence.

Locked and Must Not Touch:

- `scripts/connlab_personal_task.py` (the existing command route is reused; no writer/state-machine
  change is authorized);
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`,
  `docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md`, and
  `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py`;
- product/backend/frontend code, API/database/schema/migration/persistence/authority/business logic;
- original lane/worktree/branch, existing merge and retained resources;
- Task/Plan after approval, normal workflow schema and any other task.

No manual board edit, reset, restore, stash, rebase, cherry-pick, remerge, push, cleanup, rebind or
Final CAS is authorized before successful reviewed adoption. Any need to expand these paths returns to
Planner/User.

### 13.6 Implementation And Review Gates

Only after committed `S_AUTH` may the same candidate worktree continue from Reviewer evidence
`aeb03bd9...`; no second worktree is created. Developer uses TDD to replace only the old
adoption-source constants/shape and source proof,
keeps every Python file at or below 500 physical lines, and commits one implementation subject plus
one evidence-only child. Independent Reviewer re-gates the P0 and complete matrix. Mandatory QA runs
the full matrix on the reviewed head. Reviewer and QA evidence must use the explicitly dispatched
model/effort/reason and exact fixed fields.

Neither Reviewer nor QA may run live adoption. After QA pass/callback, the Orchestrator reconstructs
the payload directly from committed board/Git/evidence facts, runs zero-write plan mode and owns the
single byte-identical apply/durability sequence. No pre-adoption Integrator evidence or invocation is
created. A different source after plan invalidates apply. Normal Integrator begin-role starts only
after adoption is committed.

### 13.7 Executable Validation Matrix

Run the complete section 12.5 matrix unchanged. Add disposable-repository tests using real Git commits
and the real post-QA board shape for:

- exact consumption of the frozen Reviewer callback, canonical `APPROVAL_REQUIRED` block, resume,
  byte-identical same-scope Approve and exact `S_AUTH` success;
- rejection of implementation before committed `S_AUTH`, old Plan/approval after `S_AUTH`, changed
  scope during Approve, wrong decision ref and partial authority-chain durability;
- the exact `S_AUTH` through Developer/Reviewer/QA production-writer sequence and exact `S_QA`
  success;
- exact plan, byte-identical apply, one board-only durability commit and committed replay;
- baseline primary/board/action/evidence drift;
- missing, extra, reordered, duplicated or forged board durability commits;
- a board-only commit with invalid event semantics and an arbitrary later board-only descendant;
- post-QA state, phase, blocker, role, callback, lifecycle, scope, Plan/approval, host/thread/action/
  attempt/invocation and evidence-prefix drift;
- B/D/R/Q path, direct-parent, task/role/status/subject/model/blob/hash drift;
- dirty primary/candidate/original lane, wrong branch/worktree/head, merge parent or history rewrite;
- source/target/manifest digest mismatch, partial write, injected pre-write failure, forged committed
  replay and replay after a later commit;
- preservation of board raw SHA, primary/candidate/original-lane HEAD and clean status for every
  failed plan/apply/replay case;
- preservation of all line budgets and existing rebind/Final CAS/retained-resource/closeout tests.

Tests must construct the real `running/review -> development -> blocked/APPROVAL_REQUIRED ->
awaiting_user_approval -> development/S_AUTH -> review -> qa -> integration/S_QA` board sequence in a
disposable repository. Monkeypatching the source to the obsolete blocked HEAD/board, bypassing
Approve or overwriting `active.head_sha` to manufacture authority is forbidden.

### 13.8 Canonical Post-QA Adoption-Source Manifest

SHA-256 is over the exact single-line UTF-8 JSON below, without BOM or trailing newline:
`76d0deb8aa4c8a81bbed7908d761ccaf8c82e606cf57264732c0dec814b51e96`.

```json
{"schema":"connlab.model-routing-post-qa-adoption-source-amendment","version":2,"task_id":"TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING","planning_baseline":{"primary_head":"34e44ad7bfa902df29d3e22e1e98a322e9648999","board_sha256":"707518c5b94daf95ba8efa6723d2891766ac98f43f18ebfb86879a505a7a9ecd","state":"running","phase":"review","role":"Reviewer","attempt":7,"action_id":"18bb5a4d695cbb95513be10a21cebd26b33e58cbe976ae195b1c6750a264fd5f","subject":"f349382605ba1f372a0b43c50c331eb3573cb0b6","developer_evidence_commit":"652b41329fe880491dfa93c53d8bf1ff7cb1317b","reviewer_blocker_commit":"aeb03bd9f72a68e6c66a06c788bfc0c55e19df62","reviewer_blocker_evidence":"docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_reviewer.md@aeb03bd9f72a68e6c66a06c788bfc0c55e19df62#744ab3ba706ccf43bafcde344952f25566ebd504b42c6e33998970b2cba07229"},"planning_range":{"start":"34e44ad7bfa902df29d3e22e1e98a322e9648999","end":"approved_amendment_commit","allowed_paths":["tasks/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING.md","docs/task_governance_orchestrator_latency_and_model_routing_plan.md","docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_planner.md"],"board_changed":false},"scope":{"count":10,"previous_plan_ref":"docs/task_governance_orchestrator_latency_and_model_routing_plan.md@0cf58120b5ced9580abb4a88daf5b4cc9c36f72c#4991f1619ff18d1bc41c5750c4c46faf1d7ec4b339a3418e2b3fcca9b1dc4bfa","approved_request_sha256":"b5490214cbd0753d24ae4d6dac944c7a07b2d38769f5e96b37362d2b457dde22","line_budget_manifest_sha256":"557dcd22670eee1fcf8f5304200a9b324b734e1f533a25500ddd3cc85683e0ba","ancestry_manifest_sha256":"1f715cc17617f831986768a9f6ae31b63e7b6f14a38b711b61aec39a5d7144a4","frozen_ledger_sha256":"e2aa3a04075ded4d60919da10a2c530bae8832f2b60084c92a94d4fb54cbbf40"},"pre_implementation_authority":{"events":["REVIEWER_BLOCKED_CALLBACK","APPROVAL_REQUIRED_BLOCK","RESUME_AWAITING_USER_APPROVAL","APPROVE_SAME_TEN_PATHS"],"approval_required":{"stage":"development","resume_phase":"awaiting_user_approval","retryable":true,"requires_user":true,"related_ids":["POST_QA_ADOPTION_SOURCE_AUTHORITY_RECONCILIATION"]},"s_auth":{"runtime_bound_primary_head":true,"runtime_bound_raw_board_sha256":true,"state":"running","phase":"development","blocker":null,"current_role":null,"pending_callback":null,"require_exact_scope":true,"require_new_plan_approval":true},"implementation_before_s_auth":false},"required_board_route":["DEVELOPER_BEGIN","DEVELOPER_INVOCATION","DEVELOPER_READY_CALLBACK","REVIEWER_BEGIN","REVIEWER_INVOCATION","REVIEWER_PASS_CALLBACK","QA_BEGIN","QA_INVOCATION","QA_PASS_CALLBACK"],"post_qa_source":{"runtime_bound_s_auth_head":true,"runtime_bound_primary_head":true,"runtime_bound_raw_board_sha256":true,"state":"running","phase":"integration","blocker":null,"current_role":null,"pending_callback":null,"worktree_lifecycle":"integration_ready","require_exact_scope":true,"require_exact_new_plan_approval":true,"require_exact_invocations":true,"require_direct_candidate_tail":["B_POSTQA","D_POSTQA","R_POSTQA","Q_POSTQA"]},"adoption_target":{"preserve_state_phase_scope_host_subject_evidence":true,"preserve_plan_ref":true,"preserve_approval_ref":true,"append_evidence_ref":"committed_amendment_planner_evidence_ref_once","set_updated_at":"recorded_at","new_schema_keys":false},"digest_contract":["source_sha256","target_sha256","manifest_sha256"],"implementation_paths":["scripts/connlab_model_routing_integration_reconciliation.py","scripts/connlab_model_routing_ancestry_contract.py","tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py","tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py","tests/integration/test_task_governance_orchestrator_latency_model_routing_ancestry_adoption.py"],"forbidden":["implementation_before_s_auth","post_hoc_approval","obsolete_blocked_source","arbitrary_board_descendant","normal_schema_change","manual_board_edit","original_lane_change","remerge","rebase","push","cleanup","pre_review_rebind","pre_review_final_cas"]}
```

This section supersedes only the adoption source/target contract in sections 11 and 12. The ordered
ten-path machine scope, line-budget split, frozen historical ledger, retained-resource contract,
existing merge proof and all rebind/Final CAS fail-closed gates remain unchanged.

`STATUS: POST_QA_ADOPTION_SOURCE_AUTHORITY_RECONCILIATION_PENDING_USER_APPROVAL`

## 14. Final Bounded Reconciliation Verifier Architecture Amendment

### 14.1 Discovery And Frozen State

Confirmed by the User:

- stop adding route lengths, evidence-count cases and commit-pair constants;
- replace the recursive shadow authorities with one production-writer replay proof, derived evidence
  proof and finite-state candidate-history proof;
- retain the existing ten-path machine scope and narrow the implementation delta to the five existing
  reconciliation helper/test paths;
- submit only Task, Plan and Planner evidence for review before implementation.

Confirmed by the repository at planning start:

- primary/index are clean at `9ddf08cf992b2e67f3616adfab3e163a0ce5cff1`; raw board SHA-256 is
  `17bf90c1e85c9acef3cf6a0a7b856f9b5d8139508010270606b851fed81111f6`;
- the board is `running/review`, Reviewer attempt 15, callback action
  `88eb65677db742a0e1d334e9421e78bafc473e0dd7b8723c6a243cce1009dffc` pending;
- Reviewer evidence commit `391ba567347610879a59a30da4a057dfe480de82` is the direct evidence-only
  child of Developer evidence `a2898d407fbd6deaa75bfadb2b0286f76f2cec39`, and its committed blob SHA-256
  is `342a4749edbfec8bfce804a4226a630e7744bfda9dc90f7d587ff96ed3036770`;
- candidate HEAD is `391ba567347610879a59a30da4a057dfe480de82` with exactly three retained
  uncommitted paths and frozen binary-diff SHA-256
  `c53680e0f561d3e64f56ac180487545ce58f7e0c0c7ca5ce01be412b4c02a934`;
- original lane is clean at `f7770b6a6a82a36f946d16145a2124f6330961e1`;
- the board's ordered `scope_contract` and `approved_code_paths` both contain the same ten paths and
  retain the committed Plan/approval authority;
- a zero-write prospective check proved the current fixed evidence-combination grammar cannot express
  another valid fix loop without another constant, confirming the architecture defect.

Planner inference: the durable board history and candidate Git history already contain all facts
needed to validate an arbitrary bounded number of legitimate Reviewer/QA fix loops. Legality must be
derived by replaying actual writer transitions and parsing actual evidence, never by matching an
expected count, a frozen event sequence, or a commit hash exception.

No unresolved question changes scope, authority, validation or sequencing. Definition of Ready for a
planning amendment is met. Implementation remains forbidden pending explicit approval of the exact
committed Plan ref.

### 14.2 Single Production-Writer-Equivalent Route Replay

The adoption payload continues to bind exact `S_AUTH`, `S_AUTH` raw board SHA-256, exact `S_QA`,
`S_QA` raw board SHA-256 and the complete ordered `route_commits` list. The verifier performs these
steps for every adjacent parent/child pair and never searches beyond the supplied endpoint:

1. require `child^ == parent`, exactly one parent, and changed paths exactly
   `docs/task_board.md`;
2. load `parent:docs/task_board.md` and `child:docs/task_board.md` as committed raw bytes and parse
   both control objects;
3. derive exactly one legal event and all of its persisted payload fields from the parent/child
   delta;
4. for role events, call the real `complex_transition` contract in memory; for `block` and `resume`,
   call the real `connlab_personal_task.transition` contract in memory against a detached control
   copy. Use every value persisted in the child exactly. For validator inputs that the current schema
   deliberately does not persist—such as the full begin-role native-action payload and resume
   `decision_ref`—use fixed deterministic non-empty placeholders and never claim to recover their
   original external values;
5. require the rebuilt complete child control object to equal the committed child control object;
6. render the rebuilt board with the parent's immutable prefix/suffix and require exact byte equality
   with `child:docs/task_board.md`.

The derivation recognizes only contracts already owned by the production writer: `begin-role`,
`record-invocation`, `consume-callback`, `block` and `resume`. It proves that the committed child is a
**production-writer-equivalent unique deterministic state transition**, not that a particular
external process actually invoked the writer. The current board does not persist the full
begin-role native-action payload, resume decision reference or external origin identity. Therefore,
if an external edit is byte-for-byte identical to the unique reconstructed writer result, its origin
is information-theoretically indistinguishable and is not rejected on provenance grounds. This task
does not add a schema field, audit log, signature or writer provenance marker to close that gap.

Exactly one existing transition contract must reconstruct the complete child. Zero matches or
multiple matches return a stable `BLOCKED_*` result. Any manual edit that is not completely equal to
the reconstructed control object and raw rendered bytes is blocked. Unknown or extra fields, state
drift, partial edits, wrong persisted timestamps, missing/reordered/duplicated commits, multiparent
commits, non-board-only commits and later descendants are zero-write failures. Full-object,
rendered-byte, commit-topology and source/target/manifest-digest checks remain mandatory.

No new writer command, state, schema, event ledger or workflow behavior is added. Production
`scripts/connlab_personal_task.py` and `scripts/connlab_serial_complex.py` remain locked.

### 14.3 Evidence Derivation And Model-Audit Boundary

`S_AUTH.evidence_refs` is the immutable prefix. The verifier does not compare later evidence to a
fixed list or count. During successful route replay it collects the exact evidence ref from each
`consume-callback` event, in order. For every collected ref it requires:

- the Task-derived fixed evidence path for the callback role;
- the exact commit and committed blob SHA-256 encoded in the ref;
- exactly one each of `TASK_ID`, `ROLE`, `STATUS`, `SUBJECT`, `MODEL`, `REASONING_EFFORT`,
  `MODEL_ROUTE_REASON`, `ACTION_ID` and `ATTEMPT`;
- `ACTION_ID`, `ROLE` and `ATTEMPT` exactly matching the durable board invocation and callback;
- `MODEL=gpt-5.6-sol`, `REASONING_EFFORT=medium` and
  `MODEL_ROUTE_REASON=risk:integration_conflict`, with no prefix, suffix, duplicate, missing or mixed
  forged value;
- the evidence commit to be on the exact candidate ancestry and to change only its fixed evidence
  path;
- role/status/next and blocker content to satisfy the existing production callback contract.

The committed `S_QA.evidence_refs` must equal `S_AUTH.evidence_refs + replayed_callback_refs` as a
complete ordered list. Missing, duplicate, reordered, forged, additional or stale refs fail closed.
No static evidence prefix extension, evidence-count branch or fallback is allowed.

This durable adoption proof does not claim that the board independently proves the actual spawn
model. `connlab.serial-invocation` does not persist model, effort or route reason. The independent
execution audit is separate:

1. Reviewer reconciles the real role dispatch capsule and agent identity against the Developer
   evidence and durable invocation identity;
2. mandatory QA independently repeats the dispatch/evidence/model audit on the reviewed head;
3. Reviewer and QA evidence record the audit result and their own actual route;
4. Integrator produces the final `ACTUAL_MODEL_ROUTING` table from all committed role evidence.

The adoption helper validates the independently reviewed, committed evidence and its durable
invocation identity. It does not reconstruct or certify unpersisted spawn parameters from the board.
Any evidence path/blob/hash/ancestry or fixed-field discrepancy remains fail closed.

### 14.4 Candidate History Finite-State Grammar

Candidate validation walks every commit from the immutable candidate-history start through the exact
payload-bound QA evidence commit. It classifies commits solely from their committed changed paths and
evidence content:

- an implementation commit changes a non-empty subset of the approved implementation paths and no
  other path;
- consecutive implementation commits are one bounded round and remain in `implementation_open`;
- Developer evidence changes only the fixed Developer evidence path, has status
  `ready_for_review`, and binds the last implementation commit as its `SUBJECT`;
- Reviewer evidence changes only the fixed Reviewer evidence path, binds that same subject and is
  either `reviewer_blocked` or `reviewer_pass`;
- Reviewer blocked opens a new implementation round; Reviewer pass advances to QA;
- QA evidence changes only the fixed QA evidence path, binds the reviewed subject and is either
  `qa_blocked` or `qa_pass`;
- QA blocked opens a new implementation round; QA pass is terminal.

The terminal suffix must be exactly the final implementation subject followed by its Developer-ready,
Reviewer-pass and QA-pass evidence commits as direct parents. No implementation or evidence commit
may follow terminal QA. The verifier rejects an evidence commit in the wrong state, an unknown path,
empty implementation round, subject drift, role/status/model drift, divergent ancestry or history
rewrite. It contains no event-length table, evidence-count table, commit-pair allowlist or SHA-based
exception.

### 14.5 Bounded Authority And Digest Contract

The derived verifier is not a general descendant allowance. Adoption still requires all of:

- exact task ID, committed Plan ref, approval identity and identical ordered ten-path
  `scope_contract`/`approved_code_paths`;
- exact `S_AUTH` commit plus raw board SHA-256 and exact `S_QA` commit plus raw board SHA-256;
- exact ordered route commit list whose last item is `S_QA`;
- exact final candidate subject and exact D/R/Q commits/evidence refs;
- exact source, target and architecture-manifest digests;
- clean primary, candidate branch/worktree/index and original lane at the payload-bound heads;
- terminal `running/integration`, `worktree_lifecycle=integration_ready`, `blocker=null`,
  `current_role=null` and `pending_callback=null`.

Any commit after the payload-bound endpoint changes the primary/head or board digest and is rejected.
Committed adoption replay remains valid only when `HEAD` is the unique single-parent, board-only
durability commit and rebuilding the complete target from `HEAD^` plus the exact payload produces the
committed control object and raw board bytes. Partial, divergent, forged or later replay is blocked.

### 14.6 Exact May Touch, Must Not Touch And Locks

Planning changes exactly:

1. `tasks/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING.md`
2. `docs/task_governance_orchestrator_latency_and_model_routing_plan.md`
3. `docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_planner.md`

After explicit approval and committed same-scope machine authority, implementation May Touch is
exactly:

1. `scripts/connlab_model_routing_ancestry_contract.py`
2. `scripts/connlab_model_routing_integration_reconciliation.py`
3. `tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py`
4. `tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py`
5. `tests/integration/test_task_governance_orchestrator_latency_model_routing_ancestry_adoption.py`

Fixed Task-derived Developer, Reviewer, QA and Integrator evidence paths are governance evidence, not
implementation paths. `docs/task_board.md` is writer-only.

Must Not Touch and Locked Paths include `scripts/connlab_personal_task.py`,
`scripts/connlab_serial_complex.py`, every product/backend/frontend path, normal workflow schema,
Task B, the original lane, existing merge, retained resources and remotes. No new helper, test module,
schema, state machine, event ledger, route/evidence length case, SHA pair, manual board edit, remerge,
reset, restore, stash, rebase, cherry-pick, push, cleanup or worktree deletion is authorized.

The current Reviewer callback and candidate dirty patch remain frozen until approval. After approval,
machine authority must bind this exact committed Plan before Developer implementation through the
following sole legal chain, without omissions or substitutions:

1. consume the current real Reviewer attempt 15 `REVIEWER_BLOCKED` callback;
2. exact-stage and commit that sole `docs/task_board.md` transition;
3. record canonical `APPROVAL_REQUIRED` at `stage=development`, with
   `resume_phase=awaiting_user_approval`, `retryable=true`, `requires_user=true`,
   `related_ids=["FINAL_RECONCILIATION_VERIFIER_ARCHITECTURE"]`, and every other field exactly as the
   frozen blocker policy requires;
4. exact-stage and commit that sole board transition;
5. use the User's approval of this committed Plan as `decision_ref` and run production `resume`;
6. exact-stage and commit that sole board transition;
7. run same-scope `Approve` with the byte-identical ordered ten-path approved-request, this new
   committed Plan ref and the same User approval identity;
8. exact-stage and commit that sole board transition, defining the new `S_AUTH`;
9. only after committed `S_AUTH` may Developer modify the existing five implementation paths.

Every action uses the production writer, safe argv-array transport and the freshly computed raw board
SHA-256. Any `BLOCKED_*`, payload/hash drift or non-board-only durability result stops before
implementation. The Plan may not be recorded after implementation as post-hoc authority. If the
production writer cannot express this exact chain without a new state transition, stop with an
authority blocker.

### 14.7 Executable Validation Matrix

Retain the complete existing matrix:

```text
py -m pytest tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py -q
py -m pytest tests/integration/test_task_governance_orchestrator_latency_model_routing_ancestry_adoption.py -q
py -m pytest tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py -q
py -m pytest tests/unit/test_connlab_serial_complex_state.py tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q
py -m pytest tests/unit/test_connlab_personal_serial_workflow.py -q
py -m py_compile scripts/connlab_personal_task.py scripts/connlab_model_routing_integration_reconciliation.py scripts/connlab_model_routing_ancestry_contract.py
git diff --check
```

Add real disposable-Git regressions proving:

- zero, one and two legitimate Reviewer/QA fix loops pass through the same replay/finite-state
  algorithms without test-specific constants;
- consecutive approved-path implementation commits bind to the last subject and pass;
- an implementation commit containing any out-of-scope path blocks with zero writes;
- missing, reordered or duplicate route/callback commits block;
- forged evidence path, blob, hash, task, role, status, model or subject blocks;
- any manual board-only edit whose complete control object or raw bytes differ from the unique
  writer-equivalent reconstruction blocks; a byte-identical edit cannot be distinguished by the
  current persistence model and is outside this task's provenance claim;
- a later descendant, multiparent or non-board-only route commit blocks;
- exact plan/apply and committed replay pass, while partial/divergent/later replay blocks;
- every negative preserves board SHA and primary/candidate/original-lane HEAD and clean state;
- production source contains none of `_route_tokens_are_approved`,
  `_route_additions_are_approved`, an exact recovery/test commit-pair SHA allowlist, or route/evidence
  length enumeration.

All governed Python files remain at or below 500 physical lines. Any need for another path, helper,
schema, writer behavior or exception returns to User rather than weakening the verifier.

### 14.8 Canonical Clarified Architecture Manifest

SHA-256 over the exact single-line UTF-8 JSON below, without BOM or trailing newline, is
`824a3b7cb023e5af29d187444d5b5835bc32461f359dbc1ee28663dc708aa948`:

```json
{"schema":"connlab.model-routing-reconciliation-verifier-architecture-amendment","version":2,"task_id":"TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING","frozen_primary":"9ddf08cf992b2e67f3616adfab3e163a0ce5cff1","frozen_board_sha256":"17bf90c1e85c9acef3cf6a0a7b856f9b5d8139508010270606b851fed81111f6","frozen_candidate":"391ba567347610879a59a30da4a057dfe480de82","reviewer_evidence":"docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_reviewer.md@391ba567347610879a59a30da4a057dfe480de82#342a4749edbfec8bfce804a4226a630e7744bfda9dc90f7d587ff96ed3036770","scope_count":10,"approved_request_sha256":"b5490214cbd0753d24ae4d6dac944c7a07b2d38769f5e96b37362d2b457dde22","implementation_paths":["scripts/connlab_model_routing_ancestry_contract.py","scripts/connlab_model_routing_integration_reconciliation.py","tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py","tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py","tests/integration/test_task_governance_orchestrator_latency_model_routing_ancestry_adoption.py"],"proofs":["production_writer_equivalent_unique_transition","derived_callback_evidence","finite_state_candidate_history","complete_committed_replay"],"proof_limitations":["external_writer_origin_not_persisted","begin_role_full_payload_not_persisted","resume_decision_ref_not_persisted","spawn_model_not_persisted"],"model_audit":{"durable_fields":["TASK_ID","ROLE","STATUS","SUBJECT","MODEL","REASONING_EFFORT","MODEL_ROUTE_REASON","ACTION_ID","ATTEMPT"],"fixed_route":["gpt-5.6-sol","medium","risk:integration_conflict"],"independent_roles":["Reviewer","QA","Integrator"]},"pre_implementation_authority":["REVIEWER_BLOCKED_CALLBACK","APPROVAL_REQUIRED_FINAL_RECONCILIATION_VERIFIER_ARCHITECTURE","RESUME_AWAITING_USER_APPROVAL","APPROVE_SAME_TEN_PATHS","S_AUTH_COMMITTED"],"forbidden":["route_length_allowlist","evidence_count_allowlist","commit_pair_allowlist","arbitrary_descendant","post_hoc_approval","new_helper","new_schema","new_state_machine","product_change","remerge","push","cleanup"]}
```

`STATUS: FINAL_RECONCILIATION_VERIFIER_ARCHITECTURE_AMENDMENT_PENDING_USER_APPROVAL`
