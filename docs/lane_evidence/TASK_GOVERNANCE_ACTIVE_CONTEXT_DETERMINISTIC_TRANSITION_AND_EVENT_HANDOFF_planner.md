# TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF Planner Evidence

Status: `integration_reconciliation_amendment_pending_user_approval`

Date: 2026-08-02

Role: permanent Planner

Planning base: `cdb96b4ed80143ba40d571615282f0ee95708a0f`

## Authority Audit

- Primary was clean at `master@cdb96b4ed80143ba40d571615282f0ee95708a0f` before planning.
- Production `Inspect=ALLOW_INSPECT`; execution state is `complete`; Current Active Task is None;
  token, active, queue, paused, Quick Fix, and parallel records are empty.
- This revision made no execution/lane/worktree/token/queue/role/product/remote/runtime change.
- The original umbrella is `superseded_by_split_plans`; A is the first approval-eligible package.

## Developer To Reviewer Legacy Transition Audit

- Primary was reverified clean on
  `master@916f1846dd745d22fc8fb99463442d0691078265`, with no `MERGE_HEAD`.
- Exact lane branch/worktree are clean at final Developer/evidence HEAD
  `28d15b71dcd66d2befbb292e049446d11da0ec26` over approved base
  `15c3120a6d889e97d098c2cb9f8c8ef852d74f69`; the base is an ancestor of final HEAD.
- Developer evidence at final commit has Git blob
  `12c510f3e4bfed1f48cde3f7952723d6bbb8a02a` and status `ready_for_review`.
- Exact base..HEAD comparison contains the 23 authorized implementation paths plus Developer
  evidence only. `git diff --check` and final `git show --check` pass.
- Developer records `105 passed`, Python compilation, three PowerShell AST parses, exact allowlist
  and protected-equality checks, production zero-write inspect/maintenance planning, all hard byte
  budgets, and a simulated 45-second callback-to-dispatch result. Reviewer must verify these
  independently; this transition does not accept or waive them.
- Decision: retain Task A as sole token owner, set `gate_running/Reviewer`, update active HEAD and
  evidence to the immutable Developer package, preserve all locks/gates/queue/residuals, and route
  to permanent Reviewer. The candidate transition helper is not integrated and was not used.

## Reviewer Blocked To Developer Legacy Transition Audit

- Primary was reverified clean on
  `master@5c596de0e969b458bb72ea9339be4f260a9a4716`, with no `MERGE_HEAD` and valid current
  `gate_running/Reviewer` authority.
- Exact lane branch/worktree are clean at Reviewer evidence HEAD
  `1e4d080fb0b17a520aa5afb924fd62ffe4bf2203`; approved base and Developer HEAD are ancestors.
- Reviewer evidence at that commit has Git blob
  `8f8534adc660f71f2fbe435404699e321acc5174` and status `reviewer_blocked`. The delta from the
  reviewed Developer HEAD adds only that Reviewer evidence path; final `git show --check` and full
  base..HEAD `git diff --check` pass.
- B1-B5 require only existing Task A helper/capsule wiring, corresponding bounded tests, and
  Developer evidence. They do not change the approved contract, product behavior, authority,
  schema, WIP, gate order, migration boundary, or performance thresholds.
- Exact bounded implementation subset: the three Task A Python helpers; `scripts/run_task.ps1`
  only if required for B2 capsule generation; existing Task A bounded helper/integration/static
  tests needed to prove B1-B5; and Developer evidence. Contract/protocol/skill, primary board/
  history, Task B/umbrella, execution gate, registry/bundle, V1/V2, product, and protected lanes
  remain read-only.
- Decision: retain Task A as sole token owner, return to `implementation_running/Developer`, update
  active HEAD/evidence to the Reviewer block, preserve locks/gates/queue/residuals, and require a
  clean bounded-fix checkpoint followed by full Reviewer re-gate and mandatory QA. The candidate
  transition helper is not integrated and was not used.

## Developer Fix To Reviewer Re-Gate Legacy Transition Audit

- Primary was reverified clean on
  `master@b246e194c075f0f6a3038d043fe459a43876a088`, with no `MERGE_HEAD` and valid current
  `implementation_running/Developer` authority.
- Exact lane branch/worktree are clean at final fix/evidence HEAD
  `6d449262473e628cdf239c5d9b54ae3a2ff2c4c8`. Approved base, original Developer package, and
  Reviewer evidence HEAD `1e4d080fb0b17a520aa5afb924fd62ffe4bf2203` are ancestors.
- Updated Developer evidence at final HEAD has Git blob
  `75b80e0e131a84bb1e3176225e6173dc95dd7700` and status `ready_for_review`. Reviewer evidence is
  unchanged across the fix at blob `8f8534adc660f71f2fbe435404699e321acc5174`.
- Exact Reviewer-HEAD..fix-HEAD comparison contains only
  `scripts/connlab_active_context.py`, `scripts/connlab_execution_transition.py`,
  `scripts/connlab_handoff_contract.py`, four corresponding approved bounded tests, and Developer
  evidence. No `run_task.ps1`, contract/policy/skill, primary board/history, Task B/umbrella,
  product, execution gate, registry/bundle, V1/V2, archive/index, or protected-lane path changed.
- Developer claims B1-B5 direct reproductions `7 passed`, expanded helper matrix `41 passed`, full
  approved matrix `129 passed`, compilation/PowerShell/line/zero-write/protected-equality gates
  passed. Reviewer must independently verify all claims; none is accepted by this transition.
- Decision: retain Task A as sole token owner, set `gate_running/Reviewer`, update active HEAD and
  evidence to the clean fix package, preserve locks/gates/queue/residuals, and require full B1-B5
  re-gate before mandatory QA. The candidate transition helper is not integrated and was not used.

## User-Approved Final R1-R3 Reconciliation Audit

- On 2026-08-01 the User explicitly approved: “我批准 Task A 的 R1–R3 最终 bounded
  reconciliation fix pass，并继续自动推进 Reviewer、QA、Integrator。” This approval covers
  one final bounded fix pass inside the existing Task A contract; it does not amend Task/Plan,
  product behavior, execution authority, gate order, or live-migration semantics.
- Primary was reverified clean on
  `master@e5de0c4f2ecb0d01a33dabcacdcbd4549f186d8f`, with no `MERGE_HEAD` and valid current
  `gate_running/Reviewer` authority. Legacy production `Inspect` returned `ALLOW_INSPECT`.
- The exact lane branch/worktree are clean at Reviewer evidence HEAD
  `9a644cc6d4631d1fd0649179db7fab80313f0561`. Approved base
  `15c3120a6d889e97d098c2cb9f8c8ef852d74f69` and reviewed fix HEAD
  `6d449262473e628cdf239c5d9b54ae3a2ff2c4c8` are ancestors.
- Reviewer evidence at that commit has Git blob
  `73590abf5bdedf5e7ecb41b9204035343b7da9a8` and status `reviewer_blocked`. Its independent
  disposable-repository reproductions prove: R1 stale actual primary facts and a dirty lane can
  reach the duplicate path; R2 forged event/state/role tuples and post-QA helper drift can reach
  maintenance; and R3 a recomputed canonical generation-2 index/archive can remove a non-terminal
  active authority line and still plan generation 3.
- Each repair is within the already approved Task A helper/test semantics. Exact Developer fix
  allowlist is `scripts/connlab_execution_transition.py`, `scripts/connlab_active_context.py`,
  `tests/unit/test_connlab_execution_transition.py`,
  `tests/integration/test_connlab_execution_transition_recovery.py` only if direct R1 coverage
  requires it, `tests/unit/test_connlab_active_context.py`,
  `tests/integration/test_connlab_board_closeout_maintenance.py`, and Developer evidence. No other
  implementation, governance-contract, Task/Plan, board/history/archive/index, product, registry,
  V1/V2, or protected-lane path may change.
- Required validation is bounded and fail-closed: R1 later-primary-commit and dirty-lane duplicate
  negatives; R2 exact legal event/state/role/transition-ID tuple enforcement, Reviewer/QA
  attestation of the current helper checkpoint, and post-QA drift rejection; R3 generation-2/3
  recomputed canonical archive/index negatives for active/current/queue/paused/Quick Fix/parallel/
  residual/proposed authority lines; then the affected Task A helper/recovery/maintenance matrix,
  compilation, exact allowlist/diff checks, clean lane, and immutable ancestry/evidence checks.
- Decision: retain Task A as the sole WIP=`1` token owner, return to
  `implementation_running/Developer`, update active HEAD/evidence to the immutable Reviewer block,
  and require a clean bounded fix followed by full Reviewer re-gate, mandatory QA, and local
  Integrator acceptance. The candidate transition helper is not integrated and was not used.

## Final R1-R3 Developer To Reviewer Legacy Transition Audit

- Primary was reverified clean on
  `master@7f34c5a786b179e5da1cdcda8fe5cee3b8a00e9c`, with no `MERGE_HEAD` and valid
  `implementation_running/Developer` authority. Legacy production `Inspect` returned
  `ALLOW_INSPECT` before the transition.
- The exact lane branch/worktree are clean at final Developer/evidence HEAD
  `1fd726b08b7e49a32341d49e4439c889c4c6ab7b`. Approved base
  `15c3120a6d889e97d098c2cb9f8c8ef852d74f69`, prior Reviewer block HEAD
  `9a644cc6d4631d1fd0649179db7fab80313f0561`, and implementation checkpoint
  `9f939d84db5567826a19be992e6de168c88ea400` form continuous ancestry.
- Developer evidence at final HEAD has Git blob
  `6bd2703d6f280b9eec2fa01e59173149bd894c98` and status `ready_for_review`. The exact
  Reviewer-block..final-HEAD delta contains only `scripts/connlab_execution_transition.py`,
  `scripts/connlab_active_context.py`, four authorized bounded test modules, and Developer
  evidence. `git diff --check` and final `git show --check` pass.
- Developer records focused R1-R3 reproductions `4 passed`, affected matrix `46 passed`, full
  Task A suite `133 passed`, compilation, three PowerShell AST parses, helper line ceilings,
  production read-only validation, exact allowlist, and protected-worktree equality. Reviewer must
  independently verify these claims; this transition does not accept or waive any safety,
  performance, ancestry, or scope gate.
- Decision: retain Task A as sole WIP=`1` token owner, set `gate_running/Reviewer`, update active
  HEAD/evidence to the immutable final Developer package, preserve locks/gates/queue/residuals,
  and require full R1-R3 re-gate before mandatory QA. Task B and the umbrella remain unchanged and
  unapproved. The candidate transition helper is not integrated and was not used.

## Final Reviewer Pass To QA Legacy Transition Audit

- Primary was reverified clean on
  `master@87cbd2ec729a6a390a96c14ce2b8b434e915b63d`, with no `MERGE_HEAD` and valid
  `gate_running/Reviewer` authority. Legacy production `Inspect` returned `ALLOW_INSPECT`.
- The exact lane branch/worktree are clean at Reviewer evidence HEAD
  `84503d16e2638a827ecd3ef6704d0fe6bfed72ca`. Approved base
  `15c3120a6d889e97d098c2cb9f8c8ef852d74f69` and final Developer/evidence HEAD
  `1fd726b08b7e49a32341d49e4439c889c4c6ab7b` are ancestors. The delta from Developer HEAD adds
  only Reviewer evidence; `git diff --check` and final `git show --check` pass.
- Reviewer evidence at final HEAD has Git blob
  `165ebfab7f198953539a371c7c56e114ccba6a91`, status `reviewer_pass`, and `NEXT: QA`.
  Reviewer independently closed R1-R3, reran the adversarial cases and complete `133`-test Task A
  matrix, verified the exact package/ancestry/cleanliness and safety/performance contract, and
  recorded no blocking finding. The narrow `<500` helper-line margin remains non-blocking and does
  not waive future extraction discipline.
- Decision: retain Task A as sole WIP=`1` token owner, remain in `gate_running`, change the active
  role to QA, and update active HEAD/evidence to the immutable Reviewer pass. Mandatory QA must
  independently validate the final reviewed HEAD before Integrator. Task B and the umbrella remain
  unchanged and unapproved. The candidate transition helper is not integrated and was not used.

## Final QA Pass To Integrator Legacy Transition Audit

- Primary was reverified clean on
  `master@62874a215f540666564b51fe595580b083bf587d`, with no `MERGE_HEAD` and valid
  `gate_running/QA` authority. Legacy production `Inspect` returned `ALLOW_INSPECT`.
- The exact lane branch/worktree are clean at QA evidence HEAD
  `e958ba37df216c1690434ed7f9f40d4a436a88c5`. Approved base
  `15c3120a6d889e97d098c2cb9f8c8ef852d74f69`, final Developer HEAD
  `1fd726b08b7e49a32341d49e4439c889c4c6ab7b`, and Reviewer pass HEAD
  `84503d16e2638a827ecd3ef6704d0fe6bfed72ca` are ancestors. The Reviewer-to-QA delta adds only QA
  evidence; `git diff --check` and final `git show --check` pass.
- QA evidence at final HEAD has Git blob
  `49dc936e67a31fd53d616ee0b9e51bc5702819e8`, status `qa_pass`, and `NEXT: Integrator`.
  QA independently ran the complete `133`-test Task A matrix, focused R1-R3 `4`, generation/
  rollback, handoff budget, compilation, PowerShell parse, quantitative, exact-package, ancestry,
  protected-state, and production zero-write gates with no blocker.
- Exact reviewed/QA/current-helper binding for Integrator is immutable: Reviewer pass commit
  `84503d16e2638a827ecd3ef6704d0fe6bfed72ca` with evidence blob
  `165ebfab7f198953539a371c7c56e114ccba6a91`; QA pass commit
  `e958ba37df216c1690434ed7f9f40d4a436a88c5` with evidence blob
  `49dc936e67a31fd53d616ee0b9e51bc5702819e8`; and identical reviewed/QA helper blobs
  `e51a6ef7950c60b6e0b4b6122cc705e7b840413d` for `connlab_active_context.py` and
  `c20d65b764819f075b27c53e1680564ff584e3b4` for `connlab_execution_transition.py`. No helper
  drift exists after review or QA.
- Decision: retain Task A as sole WIP=`1` token owner, keep `gate_running`, change active role to
  Integrator, and update active HEAD/evidence to the immutable QA pass. This is the legal
  `gate_running/Integrator` tuple. Integrator alone may now verify, merge, and only after the
  reviewed/QA package is proven on primary run the guarded first live migration while Task A is
  still the sole token owner. This Planner transition performs neither merge nor migration. Task B
  and the umbrella remain unchanged and unapproved; the candidate helper was not used here.

## User Approval Record

- On 2026-08-01 the User explicitly approved Task A only and authorized automatic isolated
  Developer -> Reviewer -> mandatory QA -> local Integrator acceptance.
- On 2026-08-01 the User separately approved the final bounded R1-R3 reconciliation fix pass and
  continuation through Reviewer, mandatory QA, and local Integrator acceptance.
- Approved planning HEAD: `d791e74a9811033058c38ee329bb3be8ee1f6504`.
- Task B was not approved and remains serially blocked. The umbrella remains non-executable.
- Approval/worktree base is the committed approved package
  `15c3120a6d889e97d098c2cb9f8c8ef852d74f69`.
- Primary authority retains Task A as the sole token owner in `implementation_running/Developer`;
  exact branch/worktree/base/Reviewer HEAD, locks, mandatory Reviewer/QA/Integrator route, and
  clean state are recorded. Planner does not dispatch Developer.
- No queue, parallel exception, live migration, product, retained-lane, remote, or runtime action
  occurs in this governance transition.

## Integration Reconciliation Amendment Discovery

### User approval and reconciliation preparation audit

- The User explicitly approved the exact Task A integration-reconciliation amendment at primary
  anchor `3e73761673fd75de4e79028b0b8d0b89979bbd1a` and authorized automatic bounded
  Developer -> independent Reviewer -> mandatory QA -> local Integrator continuation.
- Primary was reverified clean at that exact anchor with no `MERGE_HEAD`. Preserved local merge
  `a42ca37e205127afd87d4cdc1d26ede53830522c` is its ancestor. The existing lane/worktree/index is
  clean at `e958ba37df216c1690434ed7f9f40d4a436a88c5` on the exact approved branch; its base remains
  `15c3120a6d889e97d098c2cb9f8c8ef852d74f69`.
- Pre-transition production Inspect returned `ALLOW_INSPECT` with Task A as sole WIP=`1` owner in
  `gate_running/Integrator` and snapshot digest
  `a1f0422506ffb124e14fac69c3cc51a4b2a56087c981c8c657aa06f9ec0755d4`.
- This formal scope/authority action retains the same token and changes authority to
  `implementation_running/Developer`, with expected reconciliation target/head
  `3e73761673fd75de4e79028b0b8d0b89979bbd1a`. The physical lane is intentionally still at its
  prior clean QA HEAD until Orchestrator performs the approved non-destructive fast-forward.
- Developer dispatch is not authorized by this commit. Orchestrator must prove the exact
  fast-forward, lane/worktree/index clean at the target HEAD, and a fresh
  `ImplementationDispatch=ALLOW_DISPATCH`; otherwise it stops fail-closed.
- All amendment May Touch/Must Not Touch/Locked Paths and bootstrap prohibitions remain exact.
  Queue stays empty; paused/Quick Fix/parallel remain null; residuals and retained/frozen facts
  remain unchanged. Task B and the umbrella remain unapproved/non-executable. No lane, helper,
  tests, attestation, migration, archive/index/audit, remote, runtime, or destructive action was
  performed by Planner.
- Post-transition production Inspect returned `ALLOW_INSPECT`, zero-write, with
  `implementation_running/Developer`, the same Task A token, and execution-control digest
  `124cbc003ab8322cf2208d742e9a59d971875ab44773400d3607833cab283be8`. The bounded legacy
  governance regression passed `47`; Developer dispatch was not attempted and still requires the
  later physical-lane proof plus fresh `ALLOW_DISPATCH`.

### Current authority and why Planner may act

- Primary was reverified clean at
  `master@75565f7aed80e34844e626519cbc74c4cc49c0a2`, with no `MERGE_HEAD`.
- Task A remains the sole WIP=`1` token owner in `gate_running/Integrator`; queue is empty and
  paused/Quick Fix/parallel are null. Legacy production Inspect returned `ALLOW_INSPECT` and
  execution-control digest `a1f0422506ffb124e14fac69c3cc51a4b2a56087c981c8c657aa06f9ec0755d4`.
- The first live migration is a fail-closed merge/authority conflict, which is explicitly a
  Planner/User boundary rather than a routine transition. This planning turn keeps the active
  token/role unchanged and performs no migration.

### Confirmed by User

- Plan a one-time, auditable, fail-closed Task A legacy bootstrap attestation; this was the
  planning-stage instruction and the exact resulting amendment is now User-approved.
- Never fabricate/backfill `DEVELOPER_READY`, `REVIEWER_PASS`, or `QA_PASS` transition history;
  never weaken routine transition or maintenance gates.
- Bind only the exact legacy evidence, lane/merge/primary/authority/failed-plan facts and a
  single-use consumption proof; reject reuse for any other context or later closeout.
- Require explicit User approval followed by Developer, full Reviewer, mandatory QA, and
  Integrator retry. Task B stays stopped.

### Confirmed by repository

- Clean lane QA HEAD is `e958ba37df216c1690434ed7f9f40d4a436a88c5`; base -> Developer
  `1fd726b08b7e49a32341d49e4439c889c4c6ab7b` -> Reviewer
  `84503d16e2638a827ecd3ef6704d0fe6bfed72ca` -> QA ancestry is intact.
- Developer evidence: blob `6bd2703d6f280b9eec2fa01e59173149bd894c98`, SHA-256
  `0fa1abdffe4d93182c090ddbf227628aec039d91d50b76b9f5fe9763ef5d3a0e`,
  `ready_for_review`. Reviewer: blob `165ebfab7f198953539a371c7c56e114ccba6a91`, SHA-256
  `de9be8e4c47b04f8538eeb5e2b732932c607486b2b5e2ca9441b6c0803837d70`,
  `reviewer_pass`. QA: blob `49dc936e67a31fd53d616ee0b9e51bc5702819e8`, SHA-256
  `49e33a43138dffd9fa7145abac6a2693e9f8f5c589ea22281f30c65b4e199541`,
  `qa_pass`.
- Merge `a42ca37e205127afd87d4cdc1d26ede53830522c` has exact parents
  `fd6036d9fce106ea81991def0ec572dfe20cdcb0` / `e958ba37df216c1690434ed7f9f40d4a436a88c5`,
  tree `a59c65dc838bfe66e8a839603d263e4e2c467ad1`, and canonical sorted 26-path digest
  `765445286739a3fb256f47ad36b41dbddde0fa7e2ea8c5f5018b17323da2dd4a`.
- Integrator evidence at blocked primary has blob
  `dac23cd0d720583268920ab9112f402d09bf3717`, SHA-256
  `e2781d373f289f14b9fec2ba57338197958ac21a17e9cd5ac23b9ed0f836f156`.
  It records failed source-board SHA-256
  `922532265c3b27363c091ea6eae32420fdcc6c31832d44988bd5296a7cbcf2f6`, plan digest
  `519ee4f53e1887c524d59971b40a0e1749f4911cd2b032a41237584caaacc497`,
  `BLOCKED_MAINTENANCE_GATES`, zero writes, and absent archive/index.
- Current maintenance gate reads only actual `transition_history`; the legacy board has no such
  field. Active-context is `497` lines, requiring a separate Task-A-specific module to preserve
  the hard `<500` limit and avoid a generic bypass.

### Planner inference

- The old source hash/plan digest must remain a historical failure anchor. A reviewed retry after
  governance/code changes needs a fresh current source hash/plan digest bound to a derived
  one-time consumption identity; reusing `519ee4...` would be stale and unsafe.
- A canonical source attestation in Task A evidence plus an immutable helper-generated consumption
  audit referenced by generation-1 index gives lossless use-once proof without making the
  attestation routine execution authority.
- Reusing and fast-forwarding the existing lane after approval is non-destructive because the QA
  HEAD and old merge are already ancestors of current primary. No new task/worktree is needed.

### Unresolved items

- Exact approval/Developer/Reviewer/QA/retry-merge commits, reviewed helper blobs, fresh source
  hash/plan digest, bootstrap/consumption/audit/archive/index hashes, compacted metrics, and final
  Integrator acceptance commit.

These are future gated outputs with exact validation rules in the amended Task/Plan. They do not
change scope and create no blocking question.

### Continue/stop decision and risk

The planning-stage decision was to continue only to formal User review. That review is now complete
and the exact amendment is approved. Implementation dispatch is still not ready until the existing
lane is fast-forwarded to the approved anchor and fresh `ALLOW_DISPATCH` is proven. The dominant
risk is accidentally turning historical evidence into generic transition authority; structural
schema separation, hard Task A/generation-1 anchors, explicit CLI opt-in, consumption identity,
and later-generation replay rejection address it.

## Sources Read

- User rejection attachment in full and the original umbrella task/plan/Planner evidence.
- `AGENTS.md` sections 13-20 and current board execution JSON/active summary.
- Planner and Orchestrator skills; Planner Discovery, WIP/Quick Fix, parallel model/operations,
  lane orchestration, task execution, and review protocols.
- `scripts/run_task.ps1`, read-only execution gate, completed-Markdown archive helper, and directly
  affected execution gate/recovery, WIP/Quick Fix, archive, and permanent-role tests.
- TASK_368E Developer/Reviewer/QA/Integrator evidence and its exact bounded-fix history.
- Current Task A Task/Plan/Planner/Developer/Reviewer/QA/Integrator evidence, the merged
  active-context helper and its unit/integration maintenance tests, exact Git evidence/merge/board
  objects, worktree topology, and the failed migration source/plan record.

## Discovery Classification

### Confirmed by User

- A must own active board/history, recurring closeout maintenance, deterministic transitions,
  event handoffs, compact references/reads/callbacks/cadence, and quantitative budgets.
- Routine transitions cannot require Planner.
- Production compaction is sole-token `gate_running/Integrator` only; token-null audits cannot
  write.
- WIP/token/role/worktree/no-push/non-destructive/V2 safety remains unchanged.

### Confirmed by Repository

- Board is `2466` lines / `781091` bytes at revision base.
- Orchestrator skill is `305` lines / `17304` bytes; Planner skill `98` / `3972`; orchestration
  protocol `303` / `14120`; `run_task.ps1` `123` / `4854`.
- `run_task.ps1` copies long routing prose and a full worktree snapshot.
- The execution gate is read-only and already validates much of the state/Git foundation; it has
  no mutation interface and is locked from modification.
- Existing board has one execution JSON block but no generated active-summary marker contract,
  transition digest, recurring board-history index, or partial-write recovery tests.
- TASK_368E required repeated Planner governance transitions totaling about 32 minutes per User
  audit and used a long-lived Orchestrator turn with repeated context/waits.

### Planner inference

- Three single-purpose helpers prevent the 307-line execution gate from becoming a writer/god
  script.
- Future active records need immutable gate/scope digests so the transition helper can validate
  QA routing and changed paths without prose heuristics.
- Board is replaced last in a staged transaction; immutable generation files plus a chained index
  provide audit and rollback proof.
- Context budgets are hard acceptance gates, not documentation aspirations.

### Not yet confirmed

- The future Developer/Reviewer/QA/Integrator execution outputs, including fresh plan/source/
  consumption/archive/index hashes and accepted metrics.

These are future execution outputs and do not alter scope. No blocking planning question remains.

## Definition Of Ready

- Goal, authority, exact transition events/guards, production writer boundary, helper CLIs,
  migration/rollback, recurring thresholds, budgets, file ownership, validation, performance,
  lane identity, and role gates are explicit.
- No active or parallel owner conflicts with the planned paths.
- The branch/worktree identity is exact and physically verified at the recorded approval base.
- The amendment passed User review with exact anchors, one-time schema, May Touch/Must Not Touch/
  locks, existing-lane continuation, failure and rollback rules, role route, and full
  validation are explicit. User approval is now recorded; implementation dispatch remains
  fail-closed until the existing lane is fast-forwarded to the exact approved anchor, is clean,
  and fresh `ALLOW_DISPATCH` is proven.

## Risk And Mitigation

- Unsafe automatic transition: exact plan digest, evidence blob, Git/state/scope guards, zero-write
  failures, and legacy manual fallback.
- Split authority: JSON remains sole authority; summary is generated and verified.
- History loss: byte-exact archives, chained hashes/counts, board-last transaction, and rollback
  proof through third closeout.
- Context omission: verified refs and `FULL_READ_REQUIRED` on any unsafe omission.
- Hidden long turn: one transition/dispatch maximum, no same-turn wait, callback-driven next turn.

## Prior Reconciliation Stop Point (superseded)

This was the prior approved preparation stop. The fast-forward and bounded Developer package are
now complete at `aeb77091...`; the current stop is the routine-transition amendment below.

## Routine Transition Authority Reconciliation Discovery — 2026-08-02

### Current phase, authority, and why Planner may act

- Phase remains `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Primary was reverified clean at
  `master@49911ae626daf646836471246a223496dc7ea771`, with no `MERGE_HEAD`.
- Board remains unchanged: Task A is the sole WIP=`1` token owner in
  `implementation_running/Developer`, durable active HEAD
  `3e73761673fd75de4e79028b0b8d0b89979bbd1a`, queue empty, paused/Quick Fix/parallel null, and
  payload digest `124cbc003ab8322cf2208d742e9a59d971875ab44773400d3607833cab283be8`.
- The exact existing lane branch/worktree/index is clean at
  `aeb7709128361782800d2da5a473d730d48df652`. This is a formal scope/authority conflict, not a
  routine event, so Planner is allowed. No authority or lane write occurred in Discovery.

### Confirmed by User

- Run one read-only Discovery and prepare a formal amendment for User review only.
- Keep the Developer candidate `ready_for_review`; do not dispatch Reviewer or modify board/lane.
- Initialize missing legacy active metadata through an auditable, single-use, fail-closed proof,
  structurally separate from transition history and incapable of fabricating old role events.
- Generalize the existing helper so durable board HEAD and callback candidate HEAD are distinct,
  proven facts and one atomic transition adopts the candidate plus state/role/evidence/history.
- Reject stale/divergent/dirty/rewritten/scope/evidence/post-review drift and allow
  `ALREADY_APPLIED` only for identical complete committed proof.
- Require real-shape four-event tests, complete Task A regression, independent Reviewer,
  mandatory QA, and Integrator. Task B stays stopped.

### Confirmed by repository evidence

- Candidate implementation checkpoint is
  `dc8f1fef42c874523b5706da3c8d92fa8391c475`; final evidence checkpoint is
  `aeb7709128361782800d2da5a473d730d48df652`. Base `15c3120...` and durable HEAD `3e737616...`
  are ancestors.
- Exact `3e737616...aeb77091` delta contains six approved paths only: Developer evidence,
  maintenance-bootstrap source attestation, active-context hook, Task-A bootstrap module, and two
  bounded bootstrap tests. `git diff --check` and final `git show --check` pass.
- Developer evidence at candidate has Git blob
  `104387574e995f2b6caf4bf1ceacfab76a748c64`, SHA-256
  `3d53242ba53f899bd9656e37e33508f6b74d57b711fd5926f39e1a4d67d2157c`, top-level role
  `Developer`, status `ready_for_review`, bootstrap `50 passed`, and prior Task A `133 passed`.
- Exact seven-field callback at candidate is `ALLOW_CALLBACK` and `318` bytes.
- Read-only production `ImplementationDispatch` returns `BLOCKED_ACTIVE_HEAD_DRIFT` because the
  board records the durable pre-callback HEAD while the physical lane correctly contains a later
  candidate. Read-only transition `plan` returns `BLOCKED_TRANSITION_METADATA` before it can
  reason about the candidate. Both returned `zero_write=true`.
- Current helper `validate_control` requires metadata on every active legacy record; its package
  validator requires board HEAD equal expected lane HEAD and compares base-to-candidate rather
  than durable-to-candidate. Its scope validator requires scope commit equal Git base and May
  Touch list equal board Locked Paths. These assumptions conflict with real approved amendments.
- Original Task A authorizes the helper/tests/contract, but the later maintenance-bootstrap
  amendment expressly locked them. The new behavior is therefore a material scope amendment.
- Approved base Task blob is `67156a9a2bb492b7a5a84ae960300255921e51e8`, SHA-256
  `9a1b13f0dbc129608293198548f22b114fb40cb590362496c1478e720effc349`.
  Its current parser yields a 28-entry May Touch digest
  `1ea93b7c92fd451cfb0ba51edba61fa55ed13f10c1b5f5933d03ab1b6f3e1fd3`; the board carries 29
  ordered operational locks with canonical digest
  `df114c309a21657d155401a591bb4a05b960ea9ef3854125713fe149509e2907`. Equality is neither true
  nor required by the approved prose contract.

### Planner inference

- The safe repair remains one state machine, but the 478-line coordinator cannot absorb the full
  amendment safely. `connlab_execution_transition.py` must keep sole CLI/read/state-machine/write/
  recovery authority while a new side-effect-free `connlab_execution_transition_proof.py` owns
  only proof, digest, bootstrap, delta, identity, and pure-rendering functions.
- Metadata initialization and first candidate adoption must share one atomic board replacement.
  Any preliminary board HEAD or metadata write would reproduce the authority gap.
- The bootstrap record should live separately in board control and be consumed once; the first
  real history entry remains only the current `DEVELOPER_READY` transition.
- Scope contract commit and lane Git base must be independent. Latest User-approved Task/Plan plus
  original base and board locks jointly define the effective frozen scope.
- Since the legacy gate/helper cannot authorize their own bounded repair, User approval must
  explicitly authorize one exact same-owner Developer continuation from `aeb77091...`. It is
  single-use, Task-A-specific, non-parallel, and ends at the first atomic transition.

### Unresolved items at Discovery time

- User approval was unresolved during Discovery and is now satisfied at `d7994d26...`. The future
  Developer fix/evidence candidate; bootstrap, transition, plan and rendered-board digests;
  Reviewer/QA evidence; retry merge/migration/audit/archive/index hashes; and final acceptance
  commit remain gated outputs.

These are gated outputs, not scope ambiguities. No blocking question remained at Discovery.

### Exact scope reconciliation decision

The maintenance-bootstrap scope was insufficient because it locked the needed helper, tests, and
normative contract. The User has now approved reopening exactly:

- `scripts/connlab_execution_transition.py`;
- `scripts/connlab_execution_transition_proof.py` (new pure support module);
- `tests/unit/test_connlab_execution_transition.py` (compatibility assertions only);
- `tests/unit/test_connlab_execution_transition_proof.py` (new bounded proof matrix);
- `tests/integration/test_connlab_execution_transition_recovery.py` (compatibility assertions only);
- `tests/integration/test_connlab_execution_transition_candidate_adoption.py` (new bounded
  disposable-Git real-shape matrix);
- `docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md`;
- Task A Developer evidence, followed by normal Reviewer/QA/Integrator evidence.

Current Task/Plan/Planner evidence are planning-owned. `docs/task_board.md` is future helper-owned
only for the one atomic transition and its exact commit; Planner must never pre-adopt candidate
HEAD or seed metadata manually. Active-context/bootstrap/handoff helpers/tests, execution gate,
all other governance/product/protected paths, Task B, archive/index/audit, and remote/runtime state
remain read-only.

### Risk, Definition of Ready, and continue/stop

Primary risks are using an unbound preliminary board update, treating evidence history as current
status, allowing Reviewer/QA implementation drift, or making the bootstrap reusable. The amended
Task/Plan counter these with exact anchors, separate bootstrap schema, durable-to-candidate range
proof, role-proportionate deltas, current-status/evidence blob binding, single replacement,
committed-topology idempotency, and complete recovery/replay tests.

Goal, anchors, exact expansion, interfaces, delta policies, one-use route, rollback behavior,
validation, role gates, lane identity, non-goals, and stop conditions are concrete. Definition of
Ready is satisfied for User review only. It is not implementation-ready until the User approves.

## P1 Executable-Scope Reconciliation — 2026-08-02

### Repository finding and selected strategy

- `scripts/connlab_execution_transition.py` is `478` physical lines and
  `tests/unit/test_connlab_execution_transition.py` is `394`; placing the amendment's substantive
  logic and real-shape matrix there would violate the executable scope and bounded-test policy.
- The amendment now chooses one strategy only: exact pure-support extraction. No unresolved
  extraction alternative or post-approval scope decision remains.
- The coordinator remains the sole CLI, repository/Git/evidence/cleanliness reader, legal state
  machine, board writer/recovery coordinator, and result-code emitter. The new
  `scripts/connlab_execution_transition_proof.py` is side-effect-free and cannot parse a CLI, run
  Git/subprocesses, inspect the filesystem/worktree, write/replace files, route roles, or mutate
  authority. It is not a second state machine.

### Exact revised implementation and test boundary

- Developer implementation/contract paths are exactly the coordinator, new proof support,
  existing transition unit compatibility module, new proof unit module, existing recovery
  compatibility module, new candidate-adoption integration module, and normative contract. The
  Developer evidence path is the eighth lane-owned path.
- Ceilings are coordinator `<=460`, support `<=360`, existing unit `<=399`, new proof unit `<=360`,
  existing recovery `<=120`, new candidate-adoption integration `<=380`, and contract `<=160`.
- The new proof unit module owns the pure bootstrap/scope/lock/delta/digest/spoof/replay matrix.
  The new disposable-Git integration module owns Developer-to-Reviewer, Reviewer-blocked-to-
  Developer, Reviewer-pass-to-QA, QA-pass-to-Integrator, duplicate, interruption, reconnect,
  rollback, and exact commit-topology cases without fixture pre-overwrite. Existing mixed modules
  receive compatibility assertions only.
- From durable board HEAD `3e737616...` to the final Developer candidate, the effective allowlist
  is the existing six-path bootstrap package plus seven implementation/contract paths, with the
  Developer evidence updated in place: exactly `13` distinct paths.

### Lock reconciliation and atomicity

- The present board remains byte-unchanged with the existing 29-path lock digest
  `df114c309a21657d155401a591bb4a05b960ea9ef3854125713fe149509e2907`.
- After User approval, the first atomic transition validates that exact source list/digest and an
  exact 32-path expanded list/digest
  `93bbeff0bc0a085c4e4321f5ceb1bea94e1977383cce2521f05e8ed46734c16c`. The only insertions are
  the proof support after the coordinator, proof unit after the existing transition unit, and
  candidate-adoption integration test after the existing recovery test.
- The same single board replacement adopts candidate HEAD/evidence, changes state/role, appends
  the real `DEVELOPER_READY`, initializes metadata/bootstrap, and installs the approved lock list.
  No preliminary board-HEAD, metadata, or lock write is authorized. Any different list/order/
  digest or delta blocks zero-write.

### Checkpoints, review, and Definition of Ready

- C0 is clean `aeb77091...`; C1 is extraction-preservation with current compatibility and full
  `133` baseline green; C2 is RED in the two new bounded modules; C3 is the seven-path behavior/
  contract implementation; C4 adds only updated Developer evidence and ends clean
  `ready_for_review`.
- Reviewer must independently prove the coordinator is the sole state machine/writer, the support
  import/static boundary is pure, every line ceiling and the exact 13-path package passes, no test
  pre-overwrites board HEAD, role-proportionate deltas and duplicate/recovery rules are complete,
  and the bootstrap `50`, Task A `133`, new focused suites, protected-state and production zero-
  write gates all pass. Mandatory QA and Integrator remain unchanged.
- User-confirmed behavior and frozen anchors are unchanged. Repository-confirmed P1 is fully
  resolved at planning level. Future candidate/digests and User approval remain gated outputs, not
  unresolved scope decisions. Definition of Ready is satisfied for User review only.

## Prior Dispatch-Preparation Stop Point (superseded)

### User approval and dispatch-preparation audit — 2026-08-02

- The User explicitly approved the exact routine-transition amendment at
  `d7994d264db1d7314d916a9773c95722e9201958` and authorized one bounded continuation in the
  existing Developer lane, followed by automatic atomic Developer-to-Reviewer, full Reviewer,
  mandatory QA, and Integrator. Task B remains unapproved and unstarted.
- Primary was clean at that exact approval anchor. Production `Inspect` returned `ALLOW_INSPECT`
  with payload digest `124cbc003ab8322cf2208d742e9a59d971875ab44773400d3607833cab283be8`;
  board bytes/hash remained unchanged. Task A remains the sole `implementation_running/Developer`
  token owner with durable HEAD `3e737616...`, queue empty, and paused/Quick Fix/parallel null.
- The existing exact lane/branch/worktree/index was clean at `aeb77091...`. The known
  `BLOCKED_ACTIVE_HEAD_DRIFT` and `BLOCKED_TRANSITION_METADATA` results remain expected zero-write
  facts. Approval authorizes only the same-token/same-lane bounded repair that closes them; it is
  not a reusable or general gate bypass.
- Approved scope is the chosen pure-support extraction: seven implementation/contract paths plus
  updated Developer evidence, producing the exact 13-path durable-to-final candidate allowlist.
  The first future atomic transition alone validates and installs the exact 29-to-32 ordered lock
  change/digests. All seven line ceilings, C0-C4 TDD checkpoints, full Reviewer, mandatory QA,
  Integrator, no-prewrite, no-fabricated-history, and Task B prohibitions remain binding.
- This primary checkpoint modifies only Task, Plan, and Planner evidence. It does not modify board,
  lane, helper/test/contract, role evidence, archive/index/audit, Task B, product/runtime/remote, or
  dispatch any role.

The earlier `developer_dispatch_ready` stop was consumed by the atomic transition committed at
`5cd7f02a...`. It is retained only as audit history and grants no current dispatch authority. The
current stop is the pending post-transition amendment below; board remains
`gate_running/Reviewer`, lane remains clean at `70e5c6a...`, and no role is dispatched.

## Post-Transition Dispatch/Idempotency Reconciliation Discovery — 2026-08-02

### Current phase, authority, and why Planner may act

- Phase remains Phase 11. Task A is the sole WIP=`1` token owner in
  `gate_running/Reviewer`; Task B is unapproved/unstarted.
- This is one bounded reconciliation amendment inside current Task A, not a new task, Discovery
  restart, lane, worktree, branch, or role thread. Planner is allowed because exact post-transition
  `BLOCKED_*` results expose scope/authority design issues; no routine event is being routed.
- Primary and lane were read-only verified clean. Planner changed no board/lane/helper/test/
  contract/skill/protocol and dispatched no role during Discovery.

### Confirmed by User

- Solve only committed exact duplicate/idempotency and Reviewer/QA/Integrator GateDispatch. The
  one-time current Reviewer attestation is the bounded bootstrap for GateDispatch, not a reusable
  third feature.
- Preserve atomic transition commit `5cd7f02a...`, board `gate_running/Reviewer`, clean lane
  `70e5c6a...`, one real history event, and separate consumed bootstrap.
- Keep existing Task A/permanent roles; no new task/branch/worktree/thread. Do not redesign state
  machine, maintenance, handoff, compression, Task B, product or release behavior.
- Use focused Developer RED/GREEN plus final Task A governance regression, complete Reviewer diff/
  adversarial review, one final-head full QA regression, and no unrelated/product/frontend/release
  matrix. One normal bounded fix is the maximum; repeated design/scope/authority growth stops.
- Required route remains one-time Reviewer dispatch -> genuine Reviewer result -> if blocked,
  atomic `REVIEWER_BLOCKED` -> Developer fix -> Reviewer re-gate -> mandatory QA -> Integrator.

### Confirmed by repository evidence

- Primary was reverified clean at `1e60af997e5ce042d9e2f9ae8cc7c4b4469a3570`; its delta after
  board-only atomic commit `5cd7f02acd02c03008f29de900e841a185a9d138` is exactly the current
  Task/Plan/Planner evidence. The `5cd7f02a...` sole parent is `329c0343...` and its sole path is
  `docs/task_board.md`. Current board
  blob is `972b1c2386145114cb3daa35037913d709bb5180`, SHA-256
  `3e57b913098e565de3fee8f4a0ffdff597e3d7fdfec5232fe63027298f1a2507`, payload
  `f2ddca5a8f84f4f8a966410852983571006f2810028ea0a82e33df8ed7ef0a03`.
- Board/lane HEAD is `70e5c6a7606284e1fc55ac6b0497c6d9756b665f`; branch/worktree/index are
  exact and clean. Authority is Task A/gate_running/Reviewer with 32 locks, empty queue, null pause/
  Quick Fix/parallel, transition ID `367e000d...`, plan `5ac92b50...`, bootstrap `b1605205...`, and
  exactly one real `DEVELOPER_READY` entry.
- Current Developer evidence is blob `e9d528a9c2b63b4a87dfcc6eaac74232942eeb54`, SHA-256
  `1bee1cfea13e128d92311457ff3d6c3ca02d57167e588f2d90290782a05e6e56`, status
  `ready_for_review`. Reviewer has not been dispatched.
- Exact identical plan probe returned zero-write `BLOCKED_TRANSITION_METADATA_BOOTSTRAP`; exact
  production ImplementationDispatch returned zero-write `BLOCKED_DISPATCH_STATE` and payload
  `f2ddca5a...`.
- Lane sizes are transition `460`, proof `300`, transition unit `390`, proof unit `153`, recovery
  `78`, candidate integration `165`, contract `123`. Primary gate is `307`; existing gate unit and
  recovery are `496/489`, so they cannot own the new matrix.
- Static coordinator evidence proves normal `validate_scope_metadata` requires scope-ref commit
  equal `base_sha` and May Touch equal locks. Live scope ref commit `d7994d26...` differs from base
  `15c3120a...`; the ordinary Reviewer-block/pass path therefore cannot currently plan.

### Planner inference and exact design

- Both transition `plan` and `apply` need one shared committed-duplicate classifier before
  consumed-bootstrap rejection. It must reconstruct the source-parent board and full candidate/
  evidence/transition/plan/bootstrap/render/board-only-commit proof. Plan and exact apply replay
  return the same `ALREADY_APPLIED`; uncommitted render remains recovery-required; all differing
  shapes fail closed.
- GateDispatch must be a new read-only execution-gate intent with `GateRole`, exact target evidence
  path and optional attestation ref. It validates primary/lane cleanliness, token/task/lane/role/
  required gate, board/physical HEAD, branch/worktree/index, locks/scope/evidence/transition/context
  and role write boundary. ImplementationDispatch stays Developer/Quick Fixer only.
- The current Reviewer attestation binds exact primary/board/lane/locks/Developer evidence/
  transition/context, permanent Reviewer thread and Reviewer evidence path. Same-input retry is one
  dispatch identity; any drift expires it. It cannot authorize code or board changes.
- Minimal implementation paths are transition coordinator/proof, proof unit, transition recovery,
  candidate adoption integration, execution gate, two new bounded GateDispatch tests, active-
  context contract, Orchestrator skill, orchestration protocol, and current role evidence. All
  other paths return User.
- The future legal scope transition adds exactly execution gate plus two new tests to current 32
  locks, producing 35-lock digest
  `a45c3bcd9051af6570bc386c0384aa11865d346e027f4d9f10afadaa16d51347`.

### User-authorized bridge resolution

- The User authorized planning one Task-A-only Reviewer-blocked atomic bridge. This removes the
  previously reported ordering question but does not approve implementation or Reviewer dispatch.
- `R` is genuine Reviewer-blocked evidence-only; `F` is the exact eleven-path fix descendant; `E`
  is the direct Developer-evidence child created only after bridge apply. The same Developer may
  form `F` while board stays Reviewer, but may not write board or `E` early.
- The final planning commit plus the later exact User approval message/digest is the immutable
  approval contract; `R` records both. Post-bridge `scope_contract_ref` points to that Task blob and
  frozen `scope_approval_ref` points to `R`, so no second amendment or ambient board write is needed.
- The repaired existing helper validates approval/source board/clean Git/`R`/`F`/scope/locks/
  evidence/helper/context and atomically adopts `F` into `implementation_running/Developer`. The
  unique history entry consumes the bridge. Normal `F -> E -> DEVELOPER_READY` is legal only by
  revalidating the immediate bridge-carried fix; it cannot replay after `last_transition` changes.
- Exact fix digest is `74a731dd33e912fe3fb55f18ace9cbc0c7e5f7f0ff1b917c74934968de6793d0`;
  route-wide 16-path May Touch digest is
  `b79e6f4b51d447efa3fe451af6155982d8a23d934c895a15cc1bf067a9b74c37`; 35-lock digest remains
  `a45c3bcd9051af6570bc386c0384aa11865d346e027f4d9f10afadaa16d51347`.

### Scope, efficiency, risk, and stop decision

- Task/Plan contain exact R/F/E checkpoints, eleven-path fix and 16-path route manifests/digests,
  32-to-35 lock order/digest, post-bridge field values, GateDispatch/duplicate/bridge validation
  order, TDD checkpoints, ceilings, role boundaries, one-fix maximum and bounded matrix. No
  post-approval scope or authority choice remains.
- Risks are duplicate proof that reopens bootstrap, GateDispatch that becomes implementation
  authority, repeated full-suite churn, or an implicit manual state reversal. Fail-closed proof,
  separate intents, bounded tests, risk-proportionate role budgets and the User stop boundary
  contain them.
- Definition of Ready is satisfied for User review only, not implementation. No further known
  bootstrap deadlock remains. Preserve primary board and clean lane, do not dispatch Reviewer, and
  return `integration_reconciliation_amendment_pending_user_approval`; any new deadlock must stop
  to User instead of broadening this bridge.
