# TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING — Planner Evidence

ROLE: Planner (inline in the permanent Orchestrator conversation)

STATUS: line_budget_scope_expansion_pending_user_approval

TASK_ID: `TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING`

## Identity

- No Planner agent, thread, branch, lane, host, or worktree was created.
- The current permanent Orchestrator conversation
  `019fb3d4-12a5-73b3-be8e-e59686fa39a9` performed the read-only Discovery and plan review.
- Board activation commit: `6227acb7cfccaab276194d2a7cbda96bc1f09a89`.
- Initial Plan commit: `a97b918672c2887baf5324d14bb1ba093674a1a9`.
- Revision-2 Plan ref:
  `docs/task_governance_orchestrator_latency_and_model_routing_plan.md@b70e78d14987a0c8a50400475e19a9e2243be530#27ce7b4cc39c6e0a42ec43828c7afceeff03d63e90e6e88f3a075e86d5d7cdb1`.
- Exact approved-request SHA-256:
  `b3caa75c1cf2678fec1b2d06ced4bb9e551b49e75767aba3564d6f7537b7b19c`.
- Primary HEAD before this evidence commit: `b70e78d14987a0c8a50400475e19a9e2243be530`.
- Board SHA-256 before Planner-ready transitions:
  `59ea9c1133c1843271ae0fd602be3d5e744698ddec4c8f0718e4b2d1342bc23c`.

## Review Findings Resolved

1. Defined the legal inline Planner `planning -> awaiting_user_approval` event path using the existing
   state machine, real current-thread identity, and committed evidence; no agent or synthetic result.
2. Froze exact Submit/Approve/Close entry contracts and executable positive/negative test obligations.
3. Fixed model audit locations at explicit dispatch parameters, fixed role-evidence fields, and the
   Integrator/final `ACTUAL_MODEL_ROUTING` table without changing board schema.
4. Corrected rollback to a separately authorized, parent-verified `git revert -m 1` of the exact merge.
5. Made QA low/medium selection deterministic; this Task routes QA to Terra medium.

No implementation path was edited and User approval remains required.

## Revision 3 Approved-Request Correction

- User approved Revision 2, but the exact `scripts/run_task.ps1 -Action Approve` call returned
  `BLOCKED_APPROVED_SCOPE_INVALID` with identical before/after board SHA-256 and no file change.
- Repository proof: Submit classification uses the ten-key
  `scripts/connlab_serial_complex.py::FORBIDDEN_KEYS`, while Approve validation uses the nine-key
  `scripts/connlab_serial_board.py::FORBIDDEN_KEYS` and rejects `push_or_release`.
- Revision 3 removes only that invalid Approve key, updates the approved-request hash, and adds the
  precise cross-copy negative to the existing bounded test obligation.
- Implementation May Touch, Must Not Touch, model routing, QA route, rollback, WIP, and all product/
  runtime/schema boundaries are unchanged.

The corrected approved payload was passed read-only through
`scripts.connlab_serial_board.approved_payload` before this amendment was committed. A new exact User
approval is required; no host or role may be created before it.

## Bounded Integration Reconciliation Discovery

User-authorized planning-only Discovery confirmed the following immutable facts:

- primary was clean at `5ce3ca0eca760314e7b26a385f681cb5c2b314e0` at the start of this final
  planning revision;
- board remains `state=running`, `phase=blocked`, `blocker=INTEGRATION_BLOCKED`, and
  `resume_phase=integration`; both `scope_contract.may_touch` and `approved_code_paths` remain the
  original four paths; board `head_sha=3d0884e12cc39e7b416da75ab01aaffd36c6418c`,
  `integrated_commit=null`, and `worktree_lifecycle=integration_ready`;
- primary was clean at `82370aeb1690f1a6e1ebda7d37048f5f926d7570` before this three-file
  amendment, with committed board blob SHA-256
  `9083399d2a3a091afc634ab3253df86e8f3c0754fd73558bdc0b959b0c336d88`, physical Windows
  worktree/CAS SHA-256 `295974ff98e874862d2505e8ff05ebab6977d738f74e40a6937bcbe165bc6696`, and exact
  `INTEGRATION_BLOCKED` authority;
- QA subject is `ad7dac819268ae77781709b626aea4f624a7a740`;
- the original lane is clean and immutable at
  `f7770b6a6a82a36f946d16145a2124f6330961e1`;
- `ad7dac81..f7770b6a` is the exact linear Reviewer/QA/Integrator evidence-only range;
- existing merge `093d48966b15c536b7411b3cc4cdca1e1e0d4faf` has exact parents
  `a632f01c...` and `f7770b6a...` and tree `891f0cd2...`;
- `82370aeb...` is the direct first-parent child of that merge and changes only
  `docs/task_board.md` to record the blocker;
- all five existing evidence refs in the board resolve to the exact committed bytes and declared
  SHA-256 values.
- merge `093d48966b15c536b7411b3cc4cdca1e1e0d4faf` exists in primary ancestry but is not recorded by
  the board as accepted; no reconciliation branch/worktree exists, the eight-path authority chain has
  not run, reconciliation Developer/Reviewer/QA/Integrator have not begun, and final CAS, human review,
  and closeout have not run.

The only accurate progress statement is: `Integrator pre-integration audit completed; local merge
exists; acceptance remains blocked.` This evidence does not claim `integrator_accepted`, task complete,
integration recorded, or ready for close.

The root cause has two independent halves: the normal contract requires lane HEAD equal the QA
subject, and repository proof requires primary HEAD equal the merge. A generic descendant allowance,
two-step resume/record sequence, or another merge would violate the User boundary.

The amendment therefore specifies one task-specific reviewed executor artifact on a new same-task
reconciliation worktree. It preserves the original lane and merge, is not installed/merged/cherry-
picked into primary, and can perform only the reviewed atomic host rebind followed by the one exact
final CAS through the existing sole writer. The exact future code/test scope is four paths;
reconciliation evidence uses four fixed task-derived paths. Developer, Reviewer, QA, and Integrator
route to `gpt-5.6-sol / medium / risk:integration_conflict`; they may cause only normal writer-owned
state transitions and never hand-edit the board. Integrator alone may execute either task-specific live
write after the full independent evidence chain is committed and clean.

Success atomically consumes the blocker and records `head_sha=f7770b6a`,
`integrated_commit=093d4896`, `phase=human_review`,
`state=implemented_pending_human_review`, `worktree_lifecycle=integrated`, complete evidence refs,
and `blocker=null`. Every drift is zero-write blocked. Exact replay is a no-op only on complete
committed target proof.

No board, runtime, test, original lane, merge, role evidence, product, remote, or retained resource was
modified during planning. Only the Task, Plan, and this Planner evidence are authorized in the current
turn. The amendment remains pending exact User approval.

## Machine Authority Review Correction

The User review correctly found that the first amendment deferred scope/host authority until final
CAS. Read-only inspection of the current writer proved two relevant facts:

1. blocked reapproval can add paths only under a truthful `SCOPE_EXPANDED` blocker and initially
   updates `scope_contract`, but not `complex_context.approved_code_paths`;
2. after resume to planning, a real Planner-ready callback followed by normal Approve updates both
   arrays and enters development, while the existing durable host can own a real Developer invocation.

The revised Plan therefore freezes a pre-implementation existing-command chain:
`SCOPE_EXPANDED -> ALLOW_SCOPE_AMEND -> ALLOW_RESUME -> PLANNER_READY -> ALLOW_APPROVE`. The canonical
eight-path strict-superset approved-request has SHA-256
`5eb00a105d1e0b5a047423c46b84436d854bf9c4ee85a54546c23932cedb2d34`; the version-2
reconciliation manifest was superseded by the final version-3 review-before-rebind manifest with
SHA-256 `a882f4a9eb89b342c27ade4d01db0c03b53db11a7ccc878c75abb7d8f4eab0c0`. No reconciliation worktree or
executor write is legal until the committed board proves the final scope, `approved_code_paths`, Plan/
approval refs, development phase, clean facts, and null blocker/pending callback.

After that checkpoint, the old durable host records a real Developer invocation that owns exactly one
host relocation. The target worktree is created only under that invocation and exact Plan binding; the
task-specific atomic rebind replaces host Git facts while preserving the live action and WIP. Normal
Developer/Reviewer/QA/Integrator callbacks then provide durable role authority. Final CAS is not an
approval mechanism.

Final CAS restores the current task resource to the original integrated lane and appends the clean
unmerged executor worktree/branch/head to retained history with permanent Orchestrator ownership and
its Integrator evidence ref. Thus no residual is unnamed and closeout can still verify the original
integrated lane.

The revised executable negatives require direct expanded approval from the current blocker, incomplete
two-approval authority, or unregistered/mismatched host attempts to block with zero writes and no
worktree/executor creation. Planning still changed only the Task, Plan, and Planner evidence.

A disposable minimal V2 repository using the current production writer ran the complete existing-command
scope sequence and returned `AUTHORITY_CHAIN_OK`: first Approve returned `ALLOW_SCOPE_AMEND` with eight-path
`scope_contract` while `approved_code_paths` correctly remained four; resume and a real
`planner_dispatch` invocation/callback entered `awaiting_user_approval`; the second byte-identical
Approve returned `ALLOW_APPROVE`, entered `development`, cleared blocker/pending callback, and made
both authority arrays exactly the same eight paths. The disposable repository was isolated from the
primary board and original lane. This proof is intentionally limited to scope approval; it does not
claim to test branch/worktree creation, live host relocation, replay, failure zero-write behavior, or
retained-resource closeout. Those require the not-yet-implemented task-specific writer and are frozen
as mandatory Developer/Reviewer/QA test gates rather than being represented as completed evidence.

## Review-Before-Rebind Correction

The User review correctly found that the previous sequence let Developer-only writer bytes perform
the first live host rebind. The corrected Plan chooses the strict independent-attestation option:

- Developer completes the entire writer/helper/tests at immutable subject `B` in the Plan-bound
  candidate resource and commits evidence `D` without live rebind;
- normal callbacks dispatch independent Reviewer and mandatory QA against exact `B`, producing
  evidence-only `R` and `Q` and blocking on any drift;
- only after QA pass may Integrator commit pre-rebind evidence `I` and run the reviewed rebind bytes;
- rebind preserves the pending Integrator action, and final CAS follows only after the rebind board
  checkpoint is committed and reverified.

The fixed evidence contracts are:

- `docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_developer.md@D#sha256`, `STATUS: ready_for_review`;
- `docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_reviewer.md@R#sha256`, `STATUS: reviewer_pass`;
- `docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_qa.md@Q#sha256`, `STATUS: qa_pass`;
- `docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_integrator.md@I#sha256`,
  `STATUS: pre_rebind_attestation_ready`.

They must form `approval-authority-base -> B -> D -> R -> Q -> I`; every ref is commit/blob/hash/status
bound, only Integrator may perform live rebind, and inability to express this with the existing normal
role commands is a stop condition rather than authority for an implicit bypass.

The revised retained-resource contract reuses `retained_history` and freezes fifteen exact keys:
`schema`, `version`, `task_id`, `status`, `owner`, `disposition`, `branch`, `worktree`, `head_sha`,
`clean`, `evidence_ref`, `integrated_commit`, `plan_ref`, `approval_ref_sha256`, and `recorded_at`.
It also freezes an exact identity tuple,
byte-identical replay semantics, same-identity conflict blocking, physical clean-worktree/evidence
verification, and pre-/post-close reconciliation. The final board restores the original integrated
lane as the normal closeout resource and retains the unmerged executor under permanent Orchestrator
ownership. No host/rebind test is claimed as already run; the implementation validation matrix now
requires those executable proofs before either live task-specific write.

## Bounded Integration Ancestry Reconciliation Discovery

Confirmed by User: approval checkpoint remains immutable authority; the verifier must evaluate every
commit in a fail-closed Reviewer/QA fix-loop grammar; implementation and role-evidence paths are
closed; the final direct tail is mandatory; arbitrary ancestry, unknown commits, forged evidence,
history rewrite and all forbidden Git/remote actions remain blocked. Only Task/Plan/Planner evidence
may change before a new explicit approval.

Confirmed by repository:

- primary is clean at `d2b9b3a3b68970d261678989b249b3a6477bfde6`; physical board SHA-256 is
  `b5c132c16762e6a1f5545a2ffc4c9af7219776067b0a254a6221c1c2817e389d`;
- board is `running/blocked/INTEGRATION_BLOCKED` with null role/pending callback, unchanged ordered
  eight-path scope/approved paths, subject fields `8c9f3a31...`, lifecycle `integration_ready`, and
  exact blocker evidence at `11cf2532...#ea23c4cc...`;
- candidate and index are clean at `11cf2532...`; original lane is clean at `f7770b6a...`; existing
  merge remains `093d4896...` in primary ancestry;
- approval base `666a20d7...` is an ancestor of `8c9f3a31...`; the range is a single-parent chain of
  approved executor deltas and fixed evidence commits, including four genuine Reviewer-blocked fix
  loops;
- the reviewed helper's literal direct-parent chain is the sole reproduced cause of the zero-write
  Integrator blocker;
- normal `resume` would return this blocker to `integration`, so it cannot lawfully dispatch the
  Developer amendment. A reviewed one-use adoption transition is required to avoid another authority
  deadlock.

Planner inference: this is bounded task-specific governance repair inside the already approved eight
paths. No product/API/data/schema scope changes. The immutable historical ledger SHA-256 is
`e2aa3a04075ded4d60919da10a2c530bae8832f2b60084c92a94d4fb54cbbf40`; the new canonical manifest
SHA-256 is `1f715cc17617f831986768a9f6ae31b63e7b6f14a38b711b61aec39a5d7144a4`. Existing approved-request
SHA-256 remains `5eb00a105d1e0b5a047423c46b84436d854bf9c4ee85a54546c23932cedb2d34`.

The future route is review-before-write: same-scope approval evidence correction; candidate-only
Developer implementation; independent Reviewer and mandatory QA evidence; one reviewed atomic
adoption from the exact blocked source into clean `running/integration`; normal Integrator
begin/invocation and evidence; then existing rebind/Final CAS plan/apply. The adoption command records
real committed evidence and does not fabricate normal callback history or create a generic state
bypass. Any mismatch produces zero writes.

Exact future implementation paths are `scripts/connlab_personal_task.py`, the task-specific
reconciliation helper, and its bounded unit/integration tests. Role evidence uses only four fixed
task-derived paths. Board is writer-only; original lane, merge, product/runtime schema, remote state
and retained resources are locked. The complete validation matrix covers the real history, grammar
transitions, wrong paths/fields/hashes/parents, adoption review gate, one-write durability, replay,
rebind/final compatibility and preservation on every failure.

This planning turn changes exactly the Task, Plan and Planner evidence. It has not modified the board,
runtime, tests, candidate, original lane, existing merge or retained resources; it has not run an
authority transition, role dispatch, rebind, Final CAS, push or cleanup. Implementation remains
forbidden until User approves the exact committed Plan and manifest.

`STATUS: integration_ancestry_reconciliation_amendment_pending_user_approval`

## Bounded Line-Budget Scope Expansion Discovery

Confirmed by User: resolve the retained ancestry implementation blocker without discarding the safe
checkpoint.

Confirmed by repository:

- primary is clean at `36936c1426d46f7bef2062f6caaf05d466cd4a09`; board SHA-256 is
  `1553b78b25da8f996f407e7863f2f226ca06eacf46a58be0f1bd38d5aa519c3b`;
- board remains `running/blocked/INTEGRATION_BLOCKED`; its `scope_contract` and
  `approved_code_paths` are matching ordered eight-path arrays bound to Plan `7ea0f5f3...`;
- candidate branch/worktree/index is clean at
  `481c5b81fc2e6457c066268ef998844d6fa3fc1d`, direct child of `11cf2532...`, and changes exactly
  the four approved executor paths;
- the candidate passed 47 unit, 71 integration, 43 compatibility and 13 personal-workflow tests,
  `py_compile` and `git diff --check`;
- the reconciliation helper is 715 lines and the integration test is 578 lines, violating the
  `AGENTS.md` Python 500-line hard limit;
- no Developer evidence child exists; no Reviewer/QA/Integrator/adoption/rebind/Final CAS action was
  performed for this checkpoint;
- original lane remains clean at `f7770b6a6a82a36f946d16145a2124f6330961e1`.

Planner inference: the minimum compliant repair adds the bounded production ancestry-contract module
and bounded adoption integration-test module named in Plan section 12. It preserves behavior and moves
cohesive code/tests rather than compressing or waiving the line limit. The exact ten-path
approved-request SHA-256 is
`b5490214cbd0753d24ae4d6dac944c7a07b2d38769f5e96b37362d2b457dde22`; the canonical line-budget
manifest SHA-256 is `557dcd22670eee1fcf8f5304200a9b324b734e1f533a25500ddd3cc85683e0ba`.
The previous ancestry manifest and frozen ledger remain bound and unchanged.

No blocking question remains, but this is a real scope expansion. Implementation is forbidden until
the User approves the exact committed Plan and the production writer durably records matching ten-path
`scope_contract` and `approved_code_paths`. The existing candidate is retained; no duplicate branch or
worktree is authorized.

This planning revision changes only the Task, Plan and Planner evidence. It does not modify board,
runtime, tests, candidate, original lane, existing merge or retained resources; it does not run a
role transition, adoption, rebind, Final CAS, push or cleanup.

`STATUS: line_budget_scope_expansion_pending_user_approval`

## Post-QA Adoption-Source Authority Reconciliation Discovery

Confirmed by User: keep the ten-path scope and repair only the adoption source so it is derived from
the normal post-QA production-writer authority rather than the obsolete pre-amendment blocked board.
Reviewer callback must remain pending until this exact planning amendment is committed and approved.

Confirmed by repository at discovery:

- primary/index are clean at `34e44ad7bfa902df29d3e22e1e98a322e9648999`; raw board SHA-256 is
  `707518c5b94daf95ba8efa6723d2891766ac98f43f18ebfb86879a505a7a9ecd`;
- board is `running/review`, Reviewer attempt 7, callback action
  `18bb5a4d695cbb95513be10a21cebd26b33e58cbe976ae195b1c6750a264fd5f` pending, with matching
  ten-path `scope_contract` and `approved_code_paths`;
- line-budget subject `f349382605ba1f372a0b43c50c331eb3573cb0b6`, Developer evidence
  `652b41329fe880491dfa93c53d8bf1ff7cb1317b` and Reviewer blocker evidence
  `aeb03bd9f72a68e6c66a06c788bfc0c55e19df62` form the exact direct-parent tail; candidate is clean
  at the Reviewer evidence commit and original lane is clean at `f7770b6a...`;
- Reviewer passed 48 unit, 71 integration, 43 compatibility and 13 workflow tests, compilation,
  diff, scope and line-budget checks; the sole P0 is the helper's hard-coded old primary/board and
  blocked source shape;
- the current helper changes the old blocked board directly to integration and appends D/R/Q; this is
  stale because lawful callbacks have already moved primary authority into the current review route.

Planner inference: normal role transitions must first consume the real blocker and produce a genuine
post-QA `running/integration` source. The one-use adoption then records only the newly approved
amendment authority using existing fields: update Plan/approval, append the exact Planner evidence
once and update time, preserving scope, lifecycle, host, subject and D/R/Q facts. This makes the
transition observable and auditable without adding a board schema key or fabricating role history.

The proof is stricter than ancestry. It validates the exact ordered board-only durability events from
the frozen primary/board through post-QA, reconstructs each transition with production semantics and
binds all actions, attempts, invocations, evidence and raw board bytes. Plan/apply/replay use one
source/target/manifest digest triple. Any arbitrary board-only descendant, later commit, partial or
divergent replay is zero-write blocked.

The machine scope stays at ten. The bounded implementation delta is only the reconciliation helper,
ancestry contract, bounded unit test and two bounded integration tests; `connlab_personal_task.py` and
the other machine-approved paths are locked. Role evidence and writer-only board commits remain
governance artifacts outside implementation scope.

This planning turn changes exactly the Task, Plan and Planner evidence. It does not consume the
Reviewer callback or modify board, runtime, tests, candidate, original lane, existing merge or
retained resources; it does not run adoption, rebind, Final CAS, push or cleanup. No blocking question
remains. Implementation requires the User's exact approval of the committed Plan and manifest.

Canonical post-QA adoption-source manifest SHA-256:
`7e2db615afcabf90b64e05cdd73c83ad8da89a9ade6c90b865d4ee50704366ac`.

`STATUS: post_qa_adoption_source_authority_reconciliation_pending_user_approval`

## Post-QA Authority Review Revision

Review result: the first post-QA draft correctly bounded scope and adoption verification but placed
the new Plan/approval write inside adoption, after implementation. It also described
`34e44ad7..P_REV` as board-only even though that range lawfully contains planning commits. Both are
P0 authority defects in the Plan, not runtime defects.

Revised inference: after the User approves the new committed Plan, the exact pending Reviewer blocker
is consumed normally, followed by the existing frozen `APPROVAL_REQUIRED` policy at development,
resume to `awaiting_user_approval`, and a byte-identical same-ten-path `Approve`. Its durability commit
is `S_AUTH`. Developer writes remain prohibited until `S_AUTH` binds the new Plan/approval. Adoption
later preserves those fields and only appends the exact Planner evidence ref using existing schema.

The planning range `34e44ad7..P_REV` is verified separately as changes to only Task, Plan and Planner
evidence and no board. The pre-authority route from `P_REV` to `S_AUTH` is exactly four board-only
writer commits. The adoption source ledger begins at `S_AUTH`; only `S_AUTH..S_QA` is required to be
the exact normal Developer/Reviewer/QA board-only route. This removes both impossible assumptions
without a new state-machine path, scope expansion or post-hoc approval.

The Reviewer callback remains unconsumed and the board/runtime/candidate/original lane remain
untouched during this revision. Implementation still requires explicit approval of the final
committed Plan ref and revised manifest.

Revised post-QA adoption-source manifest SHA-256:
`76d0deb8aa4c8a81bbed7908d761ccaf8c82e606cf57264732c0dec814b51e96`.

`STATUS: post_qa_adoption_source_authority_reconciliation_revision_pending_user_approval`

## Final Reconciliation Verifier Architecture Discovery And Plan Evidence

Confirmed by User: stop recursively expanding route lengths, evidence combinations and commit-pair
exceptions. Replace all three shadow authorities with committed production-writer replay, evidence
derivation from successful callbacks and a finite-state candidate-history grammar. Keep the ten-path
machine scope, five-path implementation boundary, independent Reviewer/QA/Integrator gates and all
no-push/no-cleanup protections. This planning turn may change only Task, Plan and Planner evidence.

Confirmed by repository at discovery:

- primary is clean at `9ddf08cf992b2e67f3616adfab3e163a0ce5cff1`; raw board SHA-256 is
  `17bf90c1e85c9acef3cf6a0a7b856f9b5d8139508010270606b851fed81111f6`;
- board is `running/review`, Reviewer attempt 15, callback action
  `88eb65677db742a0e1d334e9421e78bafc473e0dd7b8723c6a243cce1009dffc` pending;
- Reviewer evidence ref is
  `docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_reviewer.md@391ba567347610879a59a30da4a057dfe480de82#342a4749edbfec8bfce804a4226a630e7744bfda9dc90f7d587ff96ed3036770`;
- candidate HEAD is `391ba567347610879a59a30da4a057dfe480de82`; its retained dirty patch is
  exactly three approved paths with binary-diff SHA-256
  `c53680e0f561d3e64f56ac180487545ce58f7e0c0c7ca5ce01be412b4c02a934`;
- original lane is clean at `f7770b6a6a82a36f946d16145a2124f6330961e1`;
- ordered scope and approved paths both contain ten entries and retain the committed Plan/approval;
- current helper source contains fixed route/evidence shape decisions and commit-pair exceptions; a
  zero-write prospective projection of the next legitimate fix loop is rejected solely because its
  evidence additions do not match one of the enumerated lengths/combinations.

Planner inference: the single durable authority is the exact committed history itself. Replaying each
board-only durability commit through the real writer contract proves event legality without predicting
how many loops exist. Evidence legality follows only from successfully replayed callbacks. Candidate
legality follows from a finite state machine over changed paths and exact evidence contents. Binding
the endpoints, route list, evidence refs, digests and three clean repositories keeps this bounded and
rejects later descendants.

Not yet confirmed but non-blocking: exact internal function names and whether existing helper-local
functions are renamed or replaced. The Plan freezes behavior and forbidden source patterns, not an
unnecessary implementation name. No new module is permitted, so the work must remain within the five
existing paths and line budgets.

Risks and mitigations:

- false-positive replay acceptance is mitigated by full control-object and raw rendered-byte equality;
- evidence spoofing is mitigated by task-derived path, commit/blob hash, fixed-field and ancestry
  checks;
- unbounded history acceptance is mitigated by exact payload endpoints/list/digests and a terminal QA
  state with no following commit;
- accidental writer behavior change is prevented by locking both production writer modules and using
  their existing contracts read-only;
- recurrence of shadow authority is prevented by static tests forbidding the two named allowlist
  functions, SHA-pair exceptions and route/evidence length enumeration.

Planning May Touch is exactly Task, Plan and this Planner evidence. Future implementation May Touch is
exactly the existing reconciliation/ancestry helpers plus the existing unit and two integration tests.
Role evidence paths remain governance evidence. Board, writer, product, Task B, original lane, merge,
retained resources and remotes remain locked.

The Reviewer callback was not consumed. Candidate/runtime/tests/board were not modified. No adoption,
rebind, Final CAS, merge, push, cleanup or destructive action was performed. Implementation requires
explicit User approval of the exact committed Plan and a legal pre-implementation machine-authority
transition binding that Plan.

Canonical verifier-architecture manifest SHA-256:
`5c7e3d2def36b09e4c157d6ae961cb09776f467b42f2e1b6c0db8d9892704427`.

The unchanged ordered ten-path approved-request SHA-256 remains
`b5490214cbd0753d24ae4d6dac944c7a07b2d38769f5e96b37362d2b457dde22`. This amendment does not
change its paths, expected count, risk facts or validation commands; approval must bind the newly
committed Plan ref and this manifest rather than record implementation post hoc.

`STATUS: final_reconciliation_verifier_architecture_amendment_pending_user_approval`

## Final Architecture Clarification Evidence

User review identified two information-theoretic boundaries, and Planner confirms both from current
schema/runtime:

- the board does not persist full begin-role native-action input, resume `decision_ref` or external
  writer provenance, so committed replay can prove only a unique production-writer-equivalent state
  transition with complete control/raw-byte equality—not the real-world origin of identical bytes;
- `connlab.serial-invocation` persists action/role/attempt/agent identity but not model, effort or
  route reason, so adoption durably validates exact committed evidence and invocation identity while
  Reviewer/QA independently audit the actual dispatch capsule and Integrator reconciles
  `ACTUAL_MODEL_ROUTING`.

The revised Plan preserves every full-object, rendered-byte, topology and digest gate. Non-equivalent
manual edits, unknown/extra fields, partial edits, wrong persisted timestamps, multiparent,
non-board-only, missing/reordered/duplicate/later commits remain zero-write blockers. It adds no
schema, audit log, signature, invocation field or writer behavior.

The pre-implementation machine-authority chain is now explicit and mandatory: real Reviewer attempt
15 blocker callback and commit; canonical `APPROVAL_REQUIRED` with related ID
`FINAL_RECONCILIATION_VERIFIER_ARCHITECTURE` and commit; resume using the same User approval and
commit; byte-identical ten-path same-scope Approve with the new Plan ref/same approval and commit
`S_AUTH`; only then Developer implementation. Every step uses the production writer, safe argv-array
transport and fresh raw board SHA. Any `BLOCKED_*` stops before implementation.

Planning still changes only Task, Plan and Planner evidence. Board/raw SHA, Reviewer callback,
candidate dirty patch and original lane remain frozen. No runtime/test/candidate implementation,
adoption, rebind, Final CAS, merge, push or cleanup occurred.

The unchanged approved-request SHA-256 remains
`b5490214cbd0753d24ae4d6dac944c7a07b2d38769f5e96b37362d2b457dde22`.

Clarified architecture manifest v2 SHA-256:
`824a3b7cb023e5af29d187444d5b5835bc32461f359dbc1ee28663dc708aa948`.

`STATUS: final_reconciliation_verifier_architecture_amendment_pending_user_approval`
