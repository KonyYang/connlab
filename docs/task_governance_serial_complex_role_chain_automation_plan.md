# ConnLab Serial Complex Role-Chain Automation Plan

Status: `DRAFT_FOR_REVIEW`

Task: `TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION`

Planning activation commit: `a5286688`

Planning controller: `019fc491-21b0-77b0-bf18-53f53a366a7c`

Future runtime orchestrator: `019fb3d4-12a5-73b3-be8e-e59686fa39a9`

This document plans implementation only. It does not approve implementation, create a complex
worktree, dispatch a role, message the runtime orchestrator, archive a task, cut over, or push.

## 1. Outcome And Design Choice

Keep the completed personal serial workflow as the outer control plane and add one bounded complex
submachine. The runtime orchestrator classifies each intake as `simple`, `complex`, or
`needs_discovery`. Simple remains direct-primary. Complex uses one task-scoped Codex worktree task and
fresh role agents created only when their stage becomes eligible.

Recommended role-context option: **B, permanent runtime orchestrator plus task-scoped ephemeral role
agents**, with one task-scoped worktree host task per complex task.

Why not A (five task-level Codex worktree tasks): native `create_thread(...worktree...)` creates a
worktree for each task; no current tool contract proves that five independent task threads can all be
bound to one existing worktree. A therefore conflicts with the one-worktree invariant.

Why not a single long-lived role conversation: it would mix Planner, Developer, Reviewer, and QA
history and weaken independent review.

Option B uses:

1. the permanent runtime orchestrator only as board router and native-tool adapter;
2. one task-scoped Codex worktree host task, created after approval;
3. a fresh, minimal-context agent for each Planner, Developer, Reviewer, QA, and Integrator attempt;
4. committed role evidence and bounded callbacks as the only transition input;
5. archive of the one task-scoped host task after User close and safe retirement.

The worktree-host task is infrastructure for one complex Task ID, not a second authority. Role agents
are not reused across tasks or stages. A retry creates a new attempt with the same task/worktree and
an incremented attempt number.

## 2. Preflight Facts

### 2.1 Board and Git

- Before activation, primary was `master` at `17207db931cbe75d31c05fa1ee58257b4e88e1a9`,
  worktree/index were clean, and no untracked paths existed.
- Board SHA-256 was `3f7864a547de97f5d6f218e773cba54fc5d03a0c3c72dd7930e36ce154c7aa38`.
- Board was schema `connlab.personal-serial-control` v1, `idle`, `active=null`, FIFO empty, no
  blocker or human review, with four retained-history records.
- `a5286688` is the board-only commit that activated this task as `running/planning`.
- Current gate and helper both returned `ALLOW_INSPECT` before activation.

### 2.2 Stable simple baseline

The current helper supports `inspect`, `check`, `submit`, `activate-next`, `approve`, `mark-review`,
`block`, `resume`, `cancel`, and `close`. It already provides:

- one active owner and strict FIFO;
- minimal planned intake and complete simple intake;
- explicit approved scope binding;
- blocker retention and explicit resume;
- passed validation before human review;
- explicit User close with no automatic FIFO activation;
- primary-root verification, expected-board SHA CAS, an ignored `tmp` lock, atomic replace and
  readback;
- no stage, commit, push, thread, archive, worktree, or dispatch side effects.

The current simple/gate/history/worktree governance regression command passed 62 tests in 75.17s.

### 2.3 Frozen history and residual facts

- generation-1: 798,128 bytes; SHA-256
  `3e57b913098e565de3fee8f4a0ffdff597e3d7fdfec5232fe63027298f1a2507`; Git blob
  `972b1c2386145114cb3daa35037913d709bb5180`.
- canonical index: 6,787 bytes; SHA-256
  `cc732a742f60914e8c922d9f91f05d93fcd3bf4ec0f3483b1248a9e64c094aae`; Git blob
  `77f43609e1b8ecde0e058c5e0d24d4e554a2f895`.
- Task-A remains `cancelled`; its lane HEAD is
  `85e71dfa212c57c26527fad42eaf00a83b19c935` and its worktree is clean.
- The other three retained worktrees are clean at
  `600bbf2d8d6b7884fed6a3af4e46f56cce3fe3a3`,
  `45f345f49c43eece139245b00048c74e8c83f73b`, and
  `c9a61bcb701178c1042d99ca8011d138e0420330`.
- The external governance-migration repository was read-only checked at
  `7a9a27405278aad904686108de2b9aec73268870` and is out of scope.

Implementation must re-check full exact values from Git before any migration write; abbreviated hashes
above are human summary only and never machine input.

## 3. Evidence: Reusable Versus Frozen

### 3.1 Reuse as narrow logic

- `connlab_personal_task.py`: primary-root proof, strict FIFO, CAS, lock, atomic board replacement,
  structured result codes, approval/blocker/validation shapes.
- `connlab_lane_worktree.ps1`: read-only design patterns for normalized paths, exact branch/base/HEAD,
  cleanliness, ancestry, dry-run, refuse-force retirement. The file itself stays frozen.
- `connlab_execution_transition.py`: deterministic transition IDs, exact commit/evidence binding,
  ancestry and scope-drift checks as reference algorithms only.
- `connlab_handoff_contract.py`: the bounded seven-line callback shape and exact
  `path@commit#sha256` references. Cadence, heartbeat, and legacy routing are not reused.
- Existing role evidence: task/role/status plus exact commit and hash. New evidence receives a new
  complex-workflow schema; old evidence is never rewritten.

### 3.2 Do not restore

Do not reuse the legacy board schema, permanent role registry, StartTask/CreateWorktree gate,
parallel exception, Quick Fix preemption, pause/preempt/resume, shared-path ownership,
reconciliation, lease, heartbeat, V1-Lite, Controlled Lane V2, Task-A pilot/corrective, or automatic
maintenance role rules. Frozen files continue to fail closed and remain audit references.

## 4. Codex Capability Findings And Required Probe

Current native tool contracts prove callable operations for task creation, fork, list/read, send,
wait, title, archive/unarchive, and handoff. `create_thread` can create a project worktree from an
existing ref. `set_thread_archived` accepts an exact thread ID and supports both archive and unarchive.

They do **not** currently prove:

- that list/read exposes an authoritative archived boolean;
- whether archive only hides the task, how history restoration behaves, or whether exact read remains
  available after archive;
- the exact worktree lifecycle when a worktree-host task is retired or archived;
- that a task-created worktree can be safely retired without confusing its still-unarchived host task.

Automatic context compaction is unrelated: it summarizes model context to continue a conversation;
it neither archives a Codex task nor proves hidden/reversible/exact-ID state. Neither compaction nor
chat history is durable workflow authority.

Before cutover, the implementation controller performs one bounded, non-product capability probe:

1. create one disposable Codex project task in worktree mode from an exact clean commit;
2. obtain exact thread ID, host ID, cwd, branch, worktree and HEAD;
3. verify fresh-agent minimal-context behavior without product edits;
4. stop the task, prove the worktree is clean, test the chosen retire/archive order;
5. archive by exact ID, try list/read verification, then unarchive and verify history if supported;
6. archive again and persist the exact observed results in the allowed capability-evidence file;
7. if safe cleanup or archive semantics cannot be proven, stop before cutover.

The probe may create temporary Codex/Git state but may not change product files or push. Any destructive
cleanup remains forbidden; an unclean probe worktree is retained and recorded as a blocker.

## 5. Unified Classification Contract

### 5.1 Input

Use `connlab.serial-task-request` v1 with exact keys:

```json
{
  "schema": "connlab.serial-task-request",
  "version": 1,
  "task_id": "TASK_ID",
  "summary": "bounded summary",
  "root_cause_clear": true,
  "expected_result_clear": true,
  "may_touch": ["path"],
  "targeted_validation": ["command or bounded manual smoke"],
  "requires_independent_review": false,
  "forbidden_categories": {
    "api_contract": false,
    "database": false,
    "schema_or_migration": false,
    "persistence": false,
    "authority": false,
    "public_drive_workflow": false,
    "business_rule_semantics": false,
    "destructive_action": false,
    "external_mutation": false,
    "push_or_release": false
  }
}
```

Unknown keys fail closed. A provisional queued intake may omit decision fields and is then
`needs_discovery`; it stores only Task ID, summary, provisional result/reason and FIFO sequence.

### 5.2 Deterministic result

- `needs_discovery`: any required classification fact is absent, ambiguous, contradictory, or cannot
  be verified.
- `simple`: root cause and expected result are explicit; `may_touch` has one to three **total** paths
  including tests and board; every forbidden flag and `requires_independent_review` is false; validation
  is non-empty and bounded.
- `complex`: facts are sufficient but at least one simple predicate fails, or the User explicitly
  requires the complex chain.

No heuristic can override a missing fact. At FIFO head activation, run classification again against
current authority. Provisional classification never starts work. Existing active always causes queue;
close never auto-activates the head.

## 6. Versioned Board Model

Migrate only at cutover from `connlab.personal-serial-control` v1 to
`connlab.personal-serial-control` v2. Preserve WIP=`1`, FIFO order/sequence, `last_closed`, and each
retained-history object byte-for-byte at the JSON value level. Do not create a history generation or
modify the canonical index.

Top-level state remains intentionally small:

```text
idle | running | implemented_pending_human_review
```

The active record adds:

```text
classification: simple | complex | needs_discovery
phase: planning | awaiting_user_approval | implementation
       | development | review | qa | integration
       | blocked | human_review | closing
scope_contract
approval_ref / plan_ref
blocker
validation
complex_context (null for simple)
```

`complex_context` contains only durable routing facts:

```text
workflow_version
task_branch / task_worktree / base_sha / head_sha / integration_target
worktree_lifecycle
current_role / current_attempt
role_invocations[] (role, attempt, exact agent/invocation ID when available, status)
host_thread_id / host_id
approved_code_paths / required_gates
developer_commit / reviewed_commit / qa_commit / integrated_commit
evidence_refs[]
pending_callback
archive_target_ids[] / archived_ids[] / archive_attempts[]
close_decision_ref
```

Conversation text is never stored. Arrays have bounded lengths; completed attempt detail lives in
task-scoped evidence, while the board keeps only current and final refs.

## 7. State Machine And Legal Commands

The same Python writer remains the only board mutator. It delegates validation and pure transitions to
small modules. New commands use expected board SHA and exact JSON schemas; every write remains locked,
atomic, read-back verified, and Git staging/commit stays the controller's responsibility.

```text
idle
  -> submit/activate complex
running/planning
  -> planner-ready / discovery-required blocker
running/awaiting_user_approval
  -> approve (committed before worktree creation)
running/development
  -> developer-ready -> review
running/review
  -> reviewer-pass -> qa
  -> reviewer-blocked -> development
running/qa
  -> qa-pass -> integration
  -> qa-blocked -> development (then review, then qa)
running/integration
  -> integrator-pass -> implemented_pending_human_review
implemented_pending_human_review/human_review
  -> User request-close -> running/closing
running/closing
  -> retire worktree -> archive host task -> finalize-close -> idle
```

`needs_discovery` activates at `planning` with a `discovery_required` reason and invokes Planner only.
Planner completion writes a proposed complex scope and changes phase to `awaiting_user_approval`.

Stable blockers:

- `discovery_required`
- `approval_required`
- `developer_blocked`
- `reviewer_blocked`
- `qa_blocked`
- `integration_blocked`
- `dirty_worktree`
- `callback_pending`
- `archive_pending`
- `worktree_retirement_pending`

Every blocker retains active, Task ID, WIP, Git facts and evidence. It never starts FIFO, skips a role,
or discards/stashes/restores. Resume requires exact corrective evidence or explicit User direction as
defined by the blocker. Unknown transitions fail closed.

Simple continues to use its existing v1-equivalent path: activation commit, direct primary
implementation, targeted validation, local implementation/board commit, human review, explicit close
commit, idle. It creates no worktree, host task, role agent, archive target, or automatic FIFO action.

## 8. Commit Boundaries

### 8.1 This governance task

1. `a5286688`: board-only planning activation (complete).
2. planning commit: Task and Plan only (this turn).
3. after User approval: board-only approval commit with exact plan ref and allowlist.
4. implementation commits: allowed scripts/docs/tests while current v1 remains runtime authority.
5. capability-probe evidence commit.
6. implementation completion commit: validation plus `implemented_pending_human_review` under v1.
7. User close commit: close this governance task to idle under v1.
8. separate explicit cutover commit: v1-to-v2 board migration plus entry/contract switch.

This ordering prevents the workflow from modifying itself while it is executing itself. The target
runtime orchestrator remains inactive until step 8 is accepted. The governance controller uses the
already-stable v1 path through its own close; only an idle board is migrated.

### 8.2 Future complex tasks

Each durable transition that changes active phase or authority is a board/evidence commit before the
next role starts. Approval commit precedes worktree creation. Developer produces a clean code commit.
Reviewer and QA bind exact commits. Integrator creates/authorizes the local integration commit. User
close is committed before retirement begins; final closeout to idle is committed only after all
required retirement/archive conditions pass. No push occurs.

## 9. Git And Worktree Model

- Exactly one active complex Task ID owns exactly one Codex-created task branch/worktree.
- Creation occurs only after a committed User approval and clean primary.
- The worktree host is created from the exact approval commit; actual returned branch/path/HEAD are
  independently read from Git and atomically recorded before Developer dispatch.
- Recovery with the same Task ID adopts the exact recorded clean worktree; it never creates another.
- A different Task ID cannot create a worktree while active is occupied.
- All role attempts use the same worktree sequentially. No per-role branch or worktree exists.
- `scripts/connlab_serial_worktree.ps1` is a bounded `Inspect|Retire` verifier. It has JSON/dry-run,
  exact root/path containment, Task ID/branch/HEAD/cleanliness/ancestry checks, refuses force, refuses
  unknown paths, and does not call legacy gates.
- Worktree creation remains a native Codex task action. Repository scripts never call or imitate the
  Codex API and never store credentials.
- Retirement requires integration ancestry, exact expected HEAD, clean worktree/index, no callback,
  User close evidence, and a stopped host task. Failure records `worktree_retirement_pending` or
  `dirty_worktree` and retains everything.

Only one active complex worktree is needed because WIP is one and roles are sequential. More worktrees
would add synchronization and reconciliation without enabling any authorized concurrency.

## 10. Role Lifecycle, Independence And Evidence

The runtime orchestrator creates roles lazily. Each role attempt receives a context-free prompt plus:

- current board active ref/digest;
- task and approved plan refs;
- exact base/current commit;
- current-stage evidence refs;
- the role section of the new serial-complex protocol;
- exact May Touch/Must Not Touch and validation contract.

Planner is read-only discovery/planning and cannot implement. Developer writes only approved paths and
commits cleanly. Reviewer is a fresh agent that reviews approved base..Developer commit and cannot
reuse Developer chat. QA is another fresh agent that validates the exact reviewed code commit. The
Integrator agent verifies approval, Reviewer/QA evidence, ancestry, clean state and exact package;
the runtime orchestrator performs only the authorized mechanical board/native-tool action.

Formal result is one committed evidence document per role attempt. It contains one exact machine
record and a bounded human explanation. Callback is exactly seven ordered lines and <=1024 bytes:

```text
TASK_ID: <TASK_ID>
ROLE: <Planner|Developer|Reviewer|QA|Integrator>
STATUS: <allowed status>
COMMIT: <40-hex exact commit>
EVIDENCE: <repo-path@40-hex-commit#64-hex-sha256>
NEXT: <role|User|closeout>
BLOCKER: <none|bounded blocker>
```

The board writer validates schema, Task ID, current role/attempt, commit/hash, ancestry, allowed status,
scope, worktree cleanliness and duplicate identity. Exact duplicates are no-op; divergent duplicates
block. A `callback_pending` state survives a process interruption. No next role starts until callback
evidence is committed and the phase-transition commit is clean.

Reviewer blocking returns to a new Developer attempt then a new Reviewer attempt. QA blocking returns
to Developer, then Reviewer, then QA. Integrator never accepts a commit not jointly bound by the most
recent passing Reviewer and QA evidence.

Independent Reviewer/QA is guaranteed by fresh agent identity, no inherited task chat, immutable refs,
read-only role contracts, and committed evidence—not by titles or conversational claims.

## 11. Archive And Closeout

User close changes a complex task from human review to `closing`; it does not release active. Closeout
then requires, in order:

1. all callbacks consumed and evidence committed;
2. integrated commit verified on clean primary;
3. task worktree clean and safely retired, or an explicit User-approved retain record;
4. exact host task ID archived through native tooling;
5. archive result recorded; then final board closeout to idle.

Archive never means delete. It never removes task/plan/evidence/Git commits. Exact IDs, not titles, are
used. Repeated archive requests are idempotent. If native read/list can prove archived state, it is
recorded. If it cannot, a successful archive call plus exact attempt receipt is recorded as
`archive_pending_unverifiable`; active remains occupied until a later retry or explicit User waiver.
If the API fails, record `archive_pending`; completed integrated code is not reverted or discarded.

The safe fallback stores exact pending IDs and attempts, never reuses that host task for another Task
ID, and waits for User or bounded maintenance. It does not corrupt Git or auto-start FIFO.

## 12. Failure And Recovery

Recovery input is only board, task, approved plan, evidence refs, Git facts, exact host/agent IDs and
the current protocol. The runtime orchestrator re-runs read-only validation and resumes the same
active phase. It does not infer from its historical chat.

- missing/ambiguous facts -> blocker, no dispatch;
- dirty primary/worktree -> `dirty_worktree`, no cleanup;
- missing callback with a live role -> wait/read once; no duplicate agent;
- missing callback with a dead/unavailable role -> `callback_pending`; a retry needs exact attempt
  disposition and creates a new attempt, never accepts the old late callback as current;
- scope expansion/product-contract change -> retain active and return to User/Planner;
- Reviewer/QA finding -> bounded Developer rework loop;
- integration conflict -> `integration_blocked`, no automatic reconciliation;
- retirement/archive failure -> closing blocker, integrated product commit retained.

### 12.1 Simple-to-complex escalation

If simple exceeds three paths, touches a forbidden category, loses a clear root cause, needs destructive
work, has unexplained validation failure, or needs independent review/QA:

1. keep the same Task ID and active slot;
2. record exact dirty paths, HEAD/index, validation and blocker;
3. do not expand scope, close, requeue, discard, restore, or stash;
4. ask User to approve complex escalation;
5. after approval, start Planner Discovery for the same Task ID;
6. Planner decides how existing changes are retained or incorporated before any worktree creation.

## 13. Atomicity And Security Boundaries

- One writer: `connlab_personal_task.py` remains the CLI; `connlab_serial_board.py` owns board parsing,
  validation, CAS, lock, fsync/replace/readback and Git fact helpers; `connlab_serial_complex.py` owns
  pure classification and transition tables.
- Python owns schemas, state, hashes, CAS and decisions. PowerShell is a thin entry/worktree adapter;
  it contains no policy state and emits structured JSON.
- Every write requires primary root, expected board SHA-256, exact Task ID, command-specific frozen JSON
  and `tmp/connlab_personal_task.lock` containment. Unknown keys/versions fail closed.
- Helpers never stage, commit, push, message, create/archive tasks, or auto-run another command.
- The runtime orchestrator alone calls native Codex task tools after a helper returns a narrowly
  authorized action. It records the returned exact IDs/facts through a second CAS transition.
- No credentials, tokens, undocumented HTTP calls or direct Codex API emulation enter the repository.
- Board size remains under existing 400-line/65,536-byte thresholds; completed detail goes to evidence.

This split prevents a giant state machine: storage/CAS, pure complex rules, thin CLI, thin PowerShell
and native task actions remain separate and testable.

## 14. Exact Implementation Boundary

The exact allowlist is the 22 paths in the Task file. It is frozen on User approval. Any additional
file edit stops for renewed approval. Commands may change; paths may not.

New files:

- serial complex protocol;
- capability probe evidence;
- shared serial board module;
- pure classifier/complex transition module;
- bounded worktree verifier;
- four unit test modules and one recovery integration test.

Modified files:

- AGENTS/runtime orchestrator skill/personal policy at the eventual cutover contract boundary;
- current Task/Plan/board;
- personal helper, run entry, current gate;
- four existing governance test files.

Frozen and preserved:

- every product path and unrelated task/plan/protocol/skill/test;
- history generations/index;
- Task-A and all retained lane/evidence/worktrees;
- legacy transition/handoff/lane-worktree implementations and Controlled Lane V2;
- external governance-migration repository and all remotes.

## 15. Test Matrix

Automated or repeatable native validation must cover exactly these acceptance groups:

1. all simple predicates classify `simple`;
2. each forbidden category independently prevents simple;
3. incomplete facts classify `needs_discovery`;
4. simple creates no worktree/host task/role agent;
5. complex enters Planner and is not directly implemented by this controller;
6. occupied active queues every new task in strict FIFO;
7. close never auto-starts the FIFO head;
8. complex creates one branch/worktree only;
9. same Task ID recovery adopts the exact worktree;
10. different Task ID cannot create a worktree before final close;
11. Developer dispatch is blocked before committed User approval;
12. Reviewer is blocked before Developer handoff;
13. QA is blocked before Reviewer pass;
14. Integrator is blocked before QA pass;
15. Reviewer blocking returns to Developer;
16. QA blocking returns to Developer then Reviewer then QA;
17. Integrator rejects any commit not bound by current Reviewer and QA passes;
18. active cannot release before User close;
19. host task cannot archive before User close;
20. only a clean integrated worktree can retire after close;
21. dirty worktree is retained with blocker;
22. archive uses exact IDs and duplicate requests are no-op;
23. archive failure/unverifiable result records pending without Git/board corruption;
24. a new task's role context contains no old task chat/reference;
25. recovery succeeds from durable refs with empty conversational memory;
26. legacy StartTask/CreateWorktree/Reconcile/Controlled Lane V2 remain frozen;
27. Task-A, generation-1, index and retained evidence bytes/hashes do not change;
28. primary ends clean;
29. all commits are local and no push occurs.

Additional migration checks: v1 simple fixtures migrate deterministically to v2, rollback reconstructs
the exact pre-cutover board bytes, stale CAS/lock collision/injected replace failure are zero-write, and
the board stays below 400 lines and 65,536 bytes.

## 16. Validation Commands

The approved implementation must run at least:

```powershell
py -m pytest tests/unit/test_connlab_personal_serial_workflow.py `
  tests/unit/test_connlab_serial_classifier.py `
  tests/unit/test_connlab_serial_complex_state.py `
  tests/unit/test_connlab_serial_complex_worktree.py `
  tests/unit/test_connlab_serial_complex_orchestrator_contract.py `
  tests/unit/test_connlab_execution_gate_script.py `
  tests/unit/test_task_scoped_role_thread_lifecycle_governance.py `
  tests/integration/test_connlab_serial_complex_recovery.py -q

py scripts/connlab_personal_task.py inspect --repo-root D:\PythonProject\connlab --json
powershell -NoProfile -ExecutionPolicy Bypass -File `
  scripts/connlab_execution_gate.ps1 -RepositoryRoot D:\PythonProject\connlab -Intent Inspect -Json
git diff --check
git status --short
```

Also verify exact pre/post SHA-256 and Git blobs for generation-1, index, Task-A/retained evidence;
`git diff <approved-base>..<implementation-head> --name-only` must be a subset of the allowlist. Native
capability checks follow the bounded probe in section 4 and are committed as evidence.

## 17. Board Migration And Rollback

Implement a dry-run `plan-migration` that records current board bytes/hash/blob, proposed v2
bytes/hash, retained-value digests and rollback bytes/hash. `apply-migration` requires idle board,
clean primary, exact HEAD/hash, empty FIFO, no blocker/human review, accepted helper ancestry and an
explicit cutover reference. It writes only board atomically. The cutover commit stages only exact
allowed paths.

Before any v2 task activation, rollback is `git revert <cutover-commit>` plus exact board-byte proof;
it restores v1 entry contracts without touching history/index. After a v2 task activates, no automatic
rollback is allowed. The task stays active/blockered and this governance controller fixes forward;
parallel legacy automation is never restored.

## 18. Cutover And Pilot

1. Current controller implements behind inactive entry points and runs offline tests.
2. It completes the capability probe; any unproven critical capability blocks cutover.
3. Current governance task enters human review under v1.
4. User reviews and explicitly says close; v1 closes it to idle.
5. User separately authorizes cutover; the controller creates the exact migration/cutover commit.
6. Controller sends one bounded message to `019fb3d4...` telling it to discard chat memory as authority
   and reread exact AGENTS, board, skill, protocol and cutover commit.
7. Runtime orchestrator first performs read-only inspect/classifier self-check; it does not restore old
   roles or Task-A.
8. User approves one low-risk pilot that is intentionally complex enough to exercise every role.
9. Pilot validates Planner, approval, Developer, Reviewer, QA, Integrator, human review, User close,
   retirement and archive.
10. Pilot failure retains active/blocker and returns to this governance controller; no old-flow or
    direct-implementation fallback occurs.

`019fb3d4...` is currently addressable but `notLoaded` and its last content reflects frozen Task-A-era
authority. It is therefore not safe to use before step 6. No generation rollover is justified now.

After successful pilot, `019fb3d4...` is the sole daily runtime orchestrator. `019fc491...` remains an
out-of-band governance maintenance/recovery entry, not a competing daily router.

## 19. Direct Answers To Design Questions

1. **No self-modifying loop:** the stable v1 controller plans, implements, reviews and closes this
   governance task before an idle-only cutover. The target runtime orchestrator is inactive throughout.
2. **One worktree:** WIP is one and roles are serial; one shared task worktree is the only mutable code
   authority. More would require forbidden synchronization/reconciliation.
3. **No parallel/preemption/reconciliation:** a single owner and FIFO eliminate every legitimate need
   for them; interruption recovery concerns only the same active Task ID.
4. **Independent Reviewer/QA:** each is a fresh minimal-context agent bound to immutable commits and
   committed evidence, never Developer chat.
5. **No historical contamination:** every complex task receives a new host task and new role agents;
   recovery uses durable refs. Old host tasks are never reused.
6. **Lifecycle choice:** Option B is selected because current native thread tools do not prove multiple
   task threads can share one existing worktree; a capability probe must validate the selected host/
   agent lifecycle before cutover.
7. **Runtime recovery:** after cutover, send one exact re-read capsule and require read-only authority
   validation before accepting a pilot or ordinary task.
8. **Controller after cutover:** keep `019fc491...` only for governance maintenance and fail-safe
   repair; it must not receive ordinary daily tasks in parallel with the runtime orchestrator.

## 20. Risks And Approval Decisions

1. Native archive state and Codex worktree retirement semantics are not fully observable today. Default
   decision: require a successful reversible capability probe; otherwise block cutover.
2. Option B replaces five visible role tasks with one visible task-scoped worktree host plus ephemeral
   fresh role agents. Default decision: approve this simpler model because it is the only current model
   compatible with exactly one worktree without assuming unsupported thread binding.
3. Archive success may be callable but not independently readable. Default decision: keep active in
   `archive_pending_unverifiable` until a later proof or explicit User waiver; never roll back integrated
   code or auto-release WIP.

## 21. Approval And Stop Point

User approval authorizes only the 22-path implementation allowlist and the implementation/probe
sequence up to `implemented_pending_human_review`. It does not authorize cutover, runtime-orchestrator
messaging, a real pilot, push, forced cleanup, Task-A changes, legacy recovery, or archive/deletion of
existing tasks.

After approval, first call the current helper's `approve` with the committed Plan ref, exact approved
request JSON and exact User approval evidence; exact-stage only `docs/task_board.md`, commit it, confirm
primary clean, and only then edit implementation files.

Until then: `READY_FOR_USER_APPROVAL` and stop.
