# ConnLab Serial Complex Role-Chain Automation Plan

Status: `DRAFT_FOR_REVIEW`

Revision: `5`

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
agents**, split across a pre-approval read-only Planner agent on primary and one post-approval
task-scoped worktree host per complex task.

Why not A (five task-level Codex worktree tasks): native `create_thread(...worktree...)` creates a
worktree for each task; no current tool contract proves that five independent task threads can all be
bound to one existing worktree. A therefore conflicts with the one-worktree invariant.

Why not a single long-lived role conversation: it would mix Planner, Developer, Reviewer, and QA
history and weaken independent review.

Option B uses:

1. the permanent runtime orchestrator only as board router and native-tool adapter;
2. a fresh read-only Planner agent on primary before approval; it returns bounded proposed task/plan
   content to the runtime orchestrator, which alone writes and commits planning authority;
3. one task-scoped Codex worktree host task, created only after the approval commit;
4. a fresh, minimal-context agent for each Developer, Reviewer, QA, and Integrator attempt in that host;
5. committed role evidence and bounded callbacks as the only transition input;
6. probe-approved closeout of the one task-scoped host task after User close.

The pre-approval Planner has no implementation worktree and no write authority. The worktree-host task
is infrastructure for one approved complex Task ID, not a second authority. Role agents are not reused
across tasks or stages. A retry creates a new attempt with the same task/worktree and an incremented
attempt number.

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

### 2.2.1 Frozen first-approval binding

The complete `connlab.personal-task-approved-request` v1 object is normative in the Task section
“Frozen First-Approval Payload”. Its canonical JSON (`UTF-8`, recursively sorted object keys, compact
separators, array order preserved) has SHA-256:

```text
084ce08da66870ebde4d0bd0f929c310fce4ce8aa4204338aa95608e94fcd4be
```

It contains exactly 18 ordered paths, `expected_file_count=18`, seven validation entries and all nine
current v1 forbidden-category booleans. Approval uses that object unchanged, plus separate exact
`--plan-ref` and `--approval-ref` arguments. The current helper already requires precisely those keys;
there is no implementation-time discretion to add a field, path or validation.

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
4. stop the task, prove the worktree is clean, and test both technically available retirement/archive
   order candidates without assuming either one is safe;
5. for any archive attempt, use the exact ID, try list/read verification, then unarchive and verify
   history if supported;
6. persist the observed order, exact commands/tool receipts, reversibility and failure behavior in the
   allowed capability-evidence file;
7. present exactly one proven order for the second User cutover approval; the implementer may not
   choose or change it independently;
8. if neither order and archive semantics can be proven safe, stop before cutover.

The probe may create temporary Codex/Git state but may not change product files or push. Any destructive
cleanup remains forbidden; an unclean probe worktree is retained and recorded as a blocker. Before the
second approval, all plan language that mentions retirement/archive order is conditional on this probe.

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
developer_subject_commit / reviewer_subject_commit / qa_subject_commit / integrated_commit
evidence_refs[]
pending_callback
archive_target_ids[] / archived_ids[] / archive_attempts[]
close_decision_ref
probe_approved_closeout_order
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
  -> execute the exact probe-proven, cutover-approved retirement/archive order
  -> finalize-close -> idle
```

`needs_discovery` activates at `planning` with a `discovery_required` reason and invokes Planner only.
The runtime orchestrator creates a fresh read-only Planner agent on primary; no host/worktree exists.
Planner returns bounded proposed task/plan/evidence content, and the runtime orchestrator alone writes
and commits it before changing phase to `awaiting_user_approval`.

Stable blocker codes are the exact uppercase values frozen in section 7.4:
`DISCOVERY_REQUIRED`, `APPROVAL_REQUIRED`, `DEVELOPER_BLOCKED`, `REVIEWER_BLOCKED`, `QA_BLOCKED`,
`INTEGRATION_BLOCKED`, `DIRTY_WORKTREE`, `CALLBACK_PENDING`, `ARCHIVE_PENDING`,
`ARCHIVE_PENDING_UNVERIFIABLE`, `WORKTREE_RETIREMENT_PENDING`, `SCOPE_EXPANDED`,
`VALIDATION_FAILED`, `NATIVE_ACTION_FAILED`, and `CUTOVER_FAILED`.

Every blocker retains active, Task ID, WIP, Git facts and evidence. It never starts FIFO, skips a role,
or discards/stashes/restores. Resume requires exact corrective evidence or explicit User direction as
defined by the blocker. Unknown transitions fail closed.

Simple continues to use its existing v1-equivalent path: activation commit, direct primary
implementation, targeted validation, local implementation/board commit, human review, explicit close
commit, idle. It creates no worktree, host task, role agent, archive target, or automatic FIFO action.

### 7.1 Public Writer And Argument Contract

`scripts/connlab_personal_task.py` remains the only public board writer. The existing v1 commands and
their parameters/results remain stable. New behavior is implemented in imported bounded modules but is
exposed only through this writer. `scripts/connlab_serial_complex.py` is not a second writer.

Every command requires `--repo-root`; `--json` selects machine output. Every mutating command requires
`--expected-board-sha256` and `--task-id`. An absent required argument, an extra incompatible argument,
an unknown JSON key or an unknown enum returns `BLOCKED_ARGUMENT_COMBINATION` or the schema-specific
blocked code with zero writes.

| Command | Additional exact parameters | Repository-content write | Legal purpose |
|---|---|---:|---|
| `inspect` | none | no | Validate and report current authority. |
| `check` | `--intent Inspect|Implementation|Close|Cutover`; Task ID required except Inspect | no | Gate one requested operation. |
| `classify` | `--request-json` | no | Return only simple, complex or needs_discovery. |
| `submit` | `--request-json` | yes | Activate when idle/queue-empty or append FIFO. |
| `activate-next` | v2 additionally requires current `--request-json` for FIFO-head reclassification | yes | Activate only exact FIFO head; never automatic. |
| `approve` | `--approved-request-json`, `--plan-ref`, `--approval-ref` | yes | Bind committed scope and explicit approval. |
| `begin-role` | `--role`, `--native-action-json` | yes | Persist one pending Planner/Developer/Reviewer/QA/Integrator action before native dispatch. |
| `record-invocation` | `--role`, `--native-action-id`, `--invocation-json` | yes | Bind the returned exact agent/thread identity to the pending action. |
| `consume-callback` | `--callback-json` | yes | Validate evidence/subject and apply one legal role transition. |
| `begin-host` | `--native-action-json` | yes | Persist the sole post-approval worktree-host creation action. |
| `record-host` | `--native-action-id`, `--worktree-json` | yes | Bind exact host/thread/branch/worktree/base/HEAD facts. |
| `record-integration` | `--integration-json` | yes | Record only the already-created, verified primary merge and enter human review. |
| `request-close` | `--decision-ref` | yes | Retain active and enter complex closing after explicit User close. |
| `record-closeout` | `--closeout-json` | yes | Record one step in the cutover-approved closeout order. |
| `finalize-close` | `--decision-ref` | yes | Release active only after complete closeout proof; never starts FIFO. |
| `block` | `--blocker-json` | yes | Persist a typed blocker without releasing active. |
| `resume` | `--decision-ref` | yes | Resume only the blocker-recorded phase when its policy permits. |
| `cancel` | `--decision-ref`, `--disposition` | yes | Before host creation, or after explicit clean retain/retire proof only. |
| `mark-review`, `close` | existing v1 parameters | yes | Simple workflow only; complex use returns `BLOCKED_STATE`. |
| `plan-cutover` | `--expected-primary-head`, `--closeout-order` | no | Intrinsically probe eight paths and emit the deterministic manifest payload; it never accepts permission JSON or writes the manifest. |
| `apply-cutover` | `--cutover-manifest-ref`, `--expected-primary-head`, `--approval-ref` | yes | Re-run the intrinsic probe, then materialize and verify only the eight manifest-bound worktree targets; never stage or commit. |
| `verify-cutover-commit` | `--cutover-manifest-ref`, `--cutover-commit`, `--approval-ref` | no | Verify the Controller-created cutover commit, parent/tree/index and approval before any runtime message. |

The new parser arguments are frozen as:

```text
--role
--native-action-json
--native-action-id
--invocation-json
--callback-json
--worktree-json
--integration-json
--closeout-json
--cutover-manifest-ref
--expected-primary-head
--closeout-order
--cutover-commit
```

Existing arguments retain their current spelling. No alias or positional payload is accepted.

### 7.2 Frozen Input Schemas

All objects use exact keys and version 1:

- `connlab.serial-native-action`: `schema, version, action_id, action, role, attempt,
  prompt_sha256, title, recorded_at`. `action` is one of `planner_dispatch, host_create,
  developer_dispatch, reviewer_dispatch, qa_dispatch, integrator_dispatch`; `action_id` is the
  SHA-256 of canonical task/phase/role/attempt/board/subject facts.
- `connlab.serial-invocation`: `schema, version, action_id, role, attempt, thread_id, agent_id,
  host_id, status, recorded_at`. Exactly one of `thread_id` or `agent_id` is non-null; status is
  `started|completed|unavailable`.
- `connlab.serial-callback`: `schema, version, task_id, role, status, subject_commit, evidence,
  next, blocker`. The last seven fields render the canonical seven-line capsule; evidence is
  `path@40hex#sha256`; status/next/subject/blocker combinations are exactly those in section 7.3.1.
- `connlab.serial-worktree`: `schema, version, action_id, thread_id, host_id, branch, worktree,
  base_sha, head_sha, integration_target, clean, recorded_at`.
- `connlab.serial-integration`: `schema, version, subject_commit, branch_head, primary_parent,
  merge_commit, merge_tree, parents, evidence_refs, command, clean, recorded_at`. `parents` is exactly
  `[primary_parent, branch_head]`; `command` is exactly
  `["git","merge","--no-ff","--no-edit","--no-autostash",branch]`.
- `connlab.serial-closeout`: `schema, version, action_id, step, order, thread_id, worktree,
  receipt_sha256, status, recorded_at`. `step=retired|archived|retained`; `order` must equal the
  manifest-approved order; status is `completed|pending|failed`.

There is deliberately no permission-proof CLI parameter or caller-supplied permission schema.
`--permission-preflight-json` is unknown and returns `BLOCKED_ARGUMENT_COMBINATION`. The intrinsic
proof emitted by the helper is frozen separately in section 7.2.1.

### 7.2.1 Intrinsic Permission-Proof Contract

Both `plan-cutover` and `apply-cutover` call the same internal function in their own helper process
before returning a manifest or materializing any target. Its result has schema
`connlab.serial-cutover-permission-proof` version 1 and exact top-level keys:

```text
schema, version, task_id, source_head, observation_source, algorithm,
process_id, started_at, finished_at, paths, probe_receipt_sha256
```

`observation_source` has the sole legal value `same_process_write_handle_probe` and `algorithm` has
the sole legal value `python_os_open_rdwr_binary_no_write_v1`; neither is free text. `process_id` is
the actual helper PID. `probe_receipt_sha256` is SHA-256 of canonical UTF-8 JSON for every other proof
field (sorted object keys, compact separators, ordered paths).

Codex sandboxing exposes no repository-readable signed grant ID, so the contract does not accept or
store an unverifiable caller `grant_ref`. The verifiable receipt identifier is
`probe_receipt_sha256`, backed by actual same-process handle acquisition; apply never trusts the old
receipt alone and must acquire new handles itself.

`paths` contains the exact eight cutover paths in manifest order. Each record has exact keys:

```text
path, resolved_path, existed, regular_file, open_flags, handle_opened,
pre_bytes, pre_sha256, pre_blob, post_bytes, post_sha256, post_blob,
unchanged, error_code
```

For each path, the helper resolves the existing regular file inside the primary root, reads raw bytes,
then calls `os.open(path, os.O_RDWR | os.O_BINARY)` (with `O_BINARY=0` where the platform does not
define it), without `O_CREAT`, `O_TRUNC`, `O_APPEND` or any `os.write`/file-write call. It closes the
handle, reads raw bytes again, and recomputes byte count, SHA-256 and Git blob. Success requires
`existed=true`, `regular_file=true`, `handle_opened=true`, `unchanged=true`, null `error_code`, and
identical pre/post triples. The frozen failure enums are `NOT_FOUND`, `NOT_REGULAR`, `OUTSIDE_REPO`,
`READ_ONLY`, `CONTENT_DRIFT`, and `OS_ERROR`; any failure aborts the whole probe.

`resolved_path` is `Path.resolve(strict=True)` and must remain under the resolved primary root using
Windows case-insensitive containment. Git blob is computed locally as SHA-1 of
`b"blob " + ascii(len(bytes)) + b"\0" + bytes`; no Git write or object creation is performed.

The function catches `PermissionError`/access-denied as `READ_ONLY` and returns
`BLOCKED_CUTOVER_PATH_READ_ONLY`; other probe failures return `BLOCKED_CUTOVER_PERMISSION_PROBE`.
The result is derived from actual handle acquisition, not a caller assertion. `plan-cutover` embeds
the successful proof in its manifest payload. `apply-cutover` produces a fresh proof in the same
process that would materialize content and completes it before decoding or writing any target bytes.

On success, `apply-cutover` returns `connlab.serial-cutover-apply-receipt` version 1 in `payload` with
exact keys `schema, version, task_id, manifest_ref, permission_proof, target_set_sha256, changed_paths,
unchanged_head, unchanged_index_tree, created_at`. `permission_proof` is the fresh complete object,
`changed_paths` is the ordered eight-path list, and both unchanged Git fields equal the approved
manifest source. The Controller must retain this command result until post-commit verification.

### 7.3 Frozen State/Command Matrix

| Source authority | Command/event | Target authority | Success code |
|---|---|---|---|
| `idle`, queue empty | `submit(simple)` | `running/implementation` | `ALLOW_ACTIVATE` |
| `idle`, queue empty | `submit(complex|needs_discovery)` | `running/planning` | `ALLOW_ACTIVATE` |
| occupied | `submit(other Task ID)` | unchanged + FIFO append | `QUEUED_NEW` |
| `idle`, FIFO non-empty | `activate-next` exact head + reclassification | simple implementation or complex planning | `ALLOW_ACTIVATE_NEXT` |
| `running/planning`, no pending action | `begin-role(Planner)` | planning + `dispatch_pending` | `ALLOW_BEGIN_ROLE` |
| any eligible role stage + matching pending action | `record-invocation` | same phase + `callback_pending` | `ALLOW_RECORD_INVOCATION` |
| planning + Planner `ready` callback | `consume-callback` | `running/awaiting_user_approval` | `ALLOW_CONSUME_CALLBACK` |
| awaiting approval | `approve` | `running/development`, host absent | `ALLOW_APPROVE` |
| development, host absent | `begin-host` | development + `host_creation_pending` | `ALLOW_BEGIN_HOST` |
| matching host action | `record-host` | development + host ready | `ALLOW_RECORD_HOST` |
| development + host ready | `begin-role(Developer)` | development + `dispatch_pending` | `ALLOW_BEGIN_ROLE` |
| Developer ready callback | `consume-callback` | `running/review` | `ALLOW_CONSUME_CALLBACK` |
| Developer blocking callback | `consume-callback` | `running/blocked`, resume=`development` | `ALLOW_CONSUME_CALLBACK` |
| review | Reviewer pass callback | `running/qa` | `ALLOW_CONSUME_CALLBACK` |
| review | Reviewer blocked callback | `running/development` + retryable blocker | `ALLOW_CONSUME_CALLBACK` |
| qa | QA pass callback | `running/integration` | `ALLOW_CONSUME_CALLBACK` |
| qa | QA blocked callback | `running/development` + retryable blocker | `ALLOW_CONSUME_CALLBACK` |
| integration | Integrator pass callback | integration + `integration_ready` | `ALLOW_CONSUME_CALLBACK` |
| integration | Integrator blocked callback | `running/blocked`, resume=`integration` | `ALLOW_CONSUME_CALLBACK` |
| integration-ready + verified merge | `record-integration` | `implemented_pending_human_review/human_review` | `ALLOW_RECORD_INTEGRATION` |
| human review | `request-close` | `running/closing` | `ALLOW_REQUEST_CLOSE` |
| closing | `record-closeout` next manifest step | closing with step proof | `ALLOW_RECORD_CLOSEOUT` |
| closing, all proofs complete | `finalize-close` | `idle`, exact last_closed | `ALLOW_FINALIZE_CLOSE` |
| any occupied legal stage | `block` | `running/blocked`, same active | `ALLOW_BLOCK` |
| blocked + satisfied policy | `resume` | exact blocker `resume_phase` | `ALLOW_RESUME` |
| governance v1 human review + eight writable paths | `plan-cutover` | zero-write manifest payload | `ALLOW_PLAN_CUTOVER` |
| same + exact second approval/manifest | `apply-cutover` | eight verified worktree targets; HEAD/index unchanged | `ALLOW_APPLY_CUTOVER` |
| cutover commit is current HEAD | `verify-cutover-commit` | zero-write verified cutover receipt | `ALLOW_VERIFY_CUTOVER_COMMIT` |

Any unlisted pair returns `BLOCKED_STATE` with zero writes. Routine Reviewer/QA blockers may route to
Developer without User approval but remain attached until the next Developer attempt starts; every
other blocker uses `running/blocked` and its frozen resume policy.

### 7.3.1 Frozen Role Callback Combinations

Callback strings are lowercase and case-sensitive. No other `ROLE + STATUS + NEXT` tuple is legal.
`blocker=null` is mandatory for `ready|pass`; the named blocker code is mandatory otherwise.

| ROLE | STATUS | NEXT | Target phase | SUBJECT_COMMIT rule | Blocker |
|---|---|---|---|---|---|
| `Planner` | `ready` | `User` | `awaiting_user_approval` | Exact committed Task/Plan planning subject | null |
| `Planner` | `discovery_required` | `User` | `blocked` | Current committed planning subject | `DISCOVERY_REQUIRED` |
| `Developer` | `ready` | `Reviewer` | `review` | New clean approved-path code commit | null |
| `Developer` | `blocked` | `User` | `blocked` | Current Developer subject, or recorded task base if none exists | `DEVELOPER_BLOCKED` |
| `Reviewer` | `pass` | `QA` | `qa` | Exact current Developer subject | null |
| `Reviewer` | `blocked` | `Developer` | `development` | Exact current Developer subject | `REVIEWER_BLOCKED` |
| `QA` | `pass` | `Integrator` | `integration` | Exact Reviewer-passed Developer subject | null |
| `QA` | `blocked` | `Developer` | `development` | Exact Reviewer-passed Developer subject | `QA_BLOCKED` |
| `Integrator` | `pass` | `User` | `integration` + `integration_ready` | Exact Reviewer- and QA-passed Developer subject | null |
| `Integrator` | `blocked` | `User` | `blocked` | Exact Reviewer- and QA-passed Developer subject | `INTEGRATION_BLOCKED` |

Planner evidence commits after the planning subject; execution-role evidence commits after the named
subject/evidence chain without changing the subject tree. `consume-callback` independently proves the
subject rule, exact evidence-only diff, role attempt and tuple. A mismatched `next`, status alias,
missing blocker or blocker on a pass returns `BLOCKED_CALLBACK_INVALID` with zero writes.

### 7.4 Frozen Complex Blocker Schema

```json
{
  "schema": "connlab.serial-task-blocker",
  "version": 1,
  "code": "REVIEWER_BLOCKED",
  "stage": "review",
  "reason": "bounded non-empty explanation",
  "dirty_paths": [],
  "failed_validation": null,
  "subject_commit": "0000000000000000000000000000000000000000",
  "evidence_ref": "path@0000000000000000000000000000000000000000#0000000000000000000000000000000000000000000000000000000000000000",
  "native_action_id": null,
  "related_ids": ["finding-1"],
  "retryable": true,
  "requires_user": false,
  "resume_phase": "development",
  "recorded_at": "RFC3339 UTC"
}
```

Exact codes are `DISCOVERY_REQUIRED`, `APPROVAL_REQUIRED`, `DEVELOPER_BLOCKED`,
`REVIEWER_BLOCKED`, `QA_BLOCKED`, `INTEGRATION_BLOCKED`, `DIRTY_WORKTREE`, `CALLBACK_PENDING`,
`ARCHIVE_PENDING`, `ARCHIVE_PENDING_UNVERIFIABLE`, `WORKTREE_RETIREMENT_PENDING`,
`SCOPE_EXPANDED`, `VALIDATION_FAILED`, `NATIVE_ACTION_FAILED`, and `CUTOVER_FAILED`. Nullable fields
remain present. `reason` and `recorded_at` are required for every code. “Required” below means non-null
and non-empty; every unlisted nullable field must be null and every unlisted array must be empty.
`same` means the exact phase captured as `stage` immediately before the block, not caller input.

| BLOCKER_CODE | Additional required fields | retryable | requires_user | resume_phase |
|---|---|---:|---:|---|
| `DISCOVERY_REQUIRED` | `evidence_ref`, `related_ids` missing-fact IDs | true | true | `planning` |
| `APPROVAL_REQUIRED` | `related_ids` containing committed plan ref | true | true | `awaiting_user_approval` |
| `DEVELOPER_BLOCKED` | `evidence_ref`, `subject_commit`, `failed_validation` | true | true | `development` |
| `REVIEWER_BLOCKED` | `evidence_ref`, `subject_commit`, `related_ids` finding IDs | true | false | `development` |
| `QA_BLOCKED` | `evidence_ref`, `subject_commit`, `failed_validation`, `related_ids` finding IDs | true | false | `development` |
| `INTEGRATION_BLOCKED` | `evidence_ref`, `subject_commit`, `failed_validation` Git proof | false | true | `integration` |
| `DIRTY_WORKTREE` | `dirty_paths`, `subject_commit` | true | true | `same` |
| `CALLBACK_PENDING` | `native_action_id`, `related_ids` invocation/attempt IDs | true | false | `same` |
| `ARCHIVE_PENDING` | `native_action_id`, `related_ids` exact task/receipt IDs | true | true | `closing` |
| `ARCHIVE_PENDING_UNVERIFIABLE` | `native_action_id`, `evidence_ref`, `related_ids` exact task/receipt IDs | true | true | `closing` |
| `WORKTREE_RETIREMENT_PENDING` | `dirty_paths`, `related_ids` host/worktree IDs | true | true | `closing` |
| `SCOPE_EXPANDED` | `dirty_paths`, `evidence_ref` | true | true | `planning` |
| `VALIDATION_FAILED` | `subject_commit`, `failed_validation` | true | true | `same` |
| `NATIVE_ACTION_FAILED` | `native_action_id`, `failed_validation`, `related_ids` invocation IDs | true | true | `same` |
| `CUTOVER_FAILED` | `subject_commit`, `failed_validation`, `evidence_ref` manifest ref, `related_ids` cutover IDs | false | true | `human_review` |

`failed_validation` is an exact structured object, never free text. For `same`, schema validation
restricts `stage` and `resume_phase` to the same legal pre-block phase. Callback-produced blockers are
legal only in the matching row of section 7.3.1. Unknown codes, wrong booleans, wrong resume phase,
missing required values or populated forbidden values return `BLOCKED_BLOCKER_INVALID`.

When required, `failed_validation` has schema `connlab.serial-failure-proof` version 1 and exact keys
`schema, version, operation, command, exit_code, summary, recorded_at`. `operation` is a non-empty
stable operation ID, `command` is the exact argv array (empty only for a native action), `exit_code` is
an integer or null only for a native action, and `summary` is bounded non-empty text. `dirty_paths` are
normalized repository-relative paths; `related_ids` are bounded non-empty opaque identifiers. These
shapes are validated before the code-policy table is applied.

### 7.5 Stable Result Schema And Codes

New complex commands return `connlab.serial-task-result` v1 with exactly:

```text
schema, version, code, allowed, changed, command, task_id, classification,
state, phase, active_task_id, queue_position, next_action, native_action_id,
board_sha256_before, board_sha256_after, primary_head, primary_root,
changed_paths, reason_codes, payload, reason
```

Non-applicable fields are null; arrays remain arrays. Existing v1 commands retain
`connlab.personal-task-result` v1 until cutover. Stable new success codes are
`ALLOW_CLASSIFY_SIMPLE`, `ALLOW_CLASSIFY_COMPLEX`, `ALLOW_CLASSIFY_NEEDS_DISCOVERY`,
`ALLOW_BEGIN_ROLE`, `ALLOW_RECORD_INVOCATION`, `ALLOW_CONSUME_CALLBACK`, `ALLOW_BEGIN_HOST`,
`ALLOW_RECORD_HOST`, `ALLOW_RECORD_INTEGRATION`, `ALLOW_REQUEST_CLOSE`,
`ALLOW_RECORD_CLOSEOUT`, `ALLOW_FINALIZE_CLOSE`, `ALLOW_PLAN_CUTOVER`, and
`ALLOW_APPLY_CUTOVER`, and `ALLOW_VERIFY_CUTOVER_COMMIT`. `payload` is null except that
`ALLOW_PLAN_CUTOVER` returns the exact manifest object, `ALLOW_APPLY_CUTOVER` returns the exact apply
receipt from section 7.2.1, and `ALLOW_VERIFY_CUTOVER_COMMIT` returns the bounded verified-commit
receipt.

Stable idempotent codes are `NOOP_ACTION_ALREADY_BEGUN`, `NOOP_INVOCATION_ALREADY_RECORDED`,
`NOOP_CALLBACK_ALREADY_CONSUMED`, `NOOP_HOST_ALREADY_RECORDED`,
`NOOP_CLOSEOUT_ALREADY_RECORDED`, and `NOOP_CUTOVER_ALREADY_APPLIED`.

All current v1 `ALLOW_*`, `QUEUED_*`, `NOOP_*`, and `BLOCKED_*` codes remain stable. New blocked codes
are `BLOCKED_CALLBACK_INVALID`, `BLOCKED_CALLBACK_STALE`, `BLOCKED_EVIDENCE_INVALID`,
`BLOCKED_SUBJECT_MISMATCH`, `BLOCKED_ROLE_ORDER`, `BLOCKED_NATIVE_ACTION_PENDING`,
`BLOCKED_NATIVE_ID_MISMATCH`, `BLOCKED_HOST_REQUIRED`, `BLOCKED_HOST_DUPLICATE`,
`BLOCKED_WORKTREE_FACTS`, `BLOCKED_INTEGRATION_PRECONDITION`, `BLOCKED_INTEGRATION_CONFLICT`,
`BLOCKED_INTEGRATION_PROOF`, `BLOCKED_CLOSEOUT_ORDER`, `BLOCKED_ARCHIVE_PENDING`,
`BLOCKED_RETIREMENT_PENDING`, `BLOCKED_CUTOVER_NOT_AUTHORIZED`, `BLOCKED_CUTOVER_MANIFEST`,
`BLOCKED_CUTOVER_TARGET_HASH`, `BLOCKED_CUTOVER_PATH_READ_ONLY`,
`BLOCKED_CUTOVER_PERMISSION_PROBE`, `BLOCKED_CUTOVER_INDEX_DRIFT`, `BLOCKED_CUTOVER_MATERIALIZATION`,
`BLOCKED_CUTOVER_COMMIT`, `BLOCKED_CUTOVER_ROLLBACK_FAILED`, and
`BLOCKED_LEGACY_MODE_FROZEN`. All blocked results are zero-write unless the command is explicitly
recording that blocker. `BLOCKED_CUTOVER_MATERIALIZATION` is the sole file-write exception: it may
leave only the eight authorized worktree paths dirty, after which the Controller must execute the
manifest's exact uncommitted rollback before any other action. No code is inferred from free text.

## 8. Commit Boundaries

### 8.1 This governance task

1. `a5286688`: board-only planning activation (complete).
2. `1afbfdf1`: initial Task and Plan planning commit (complete).
3. Revision 5 planning commit: Task, Plan and board human-summary correction only.
4. after the first User approval: board-only approval commit binding only the
   `implementation-before-cutover` allowlist.
5. implementation commits: only pre-cutover helpers/modules/protocol/tests while v1 remains the
   normative runtime authority and every new complex entry stays unreachable.
6. capability-probe evidence commit recording the one proposed closeout order.
7. implementation completion commit: validation plus `implemented_pending_human_review` under v1.
8. after exact cutover-path permission is granted, `plan-cutover` proves it through the intrinsic
   handle probe; the Controller commits the returned manifest and obtains the manifest-bound second
   User approval;
9. the helper materializes/verifies only the eight targets, the Controller exact-stages and creates one
   cutover Git commit, and read-only `verify-cutover-commit` must pass before any runtime message. That
   commit simultaneously migrates v1 to v2, records this governance task closed, releases active, and
   switches all cutover-only contracts/entry points.

This ordering prevents the workflow from modifying itself while it is executing itself. The target
runtime orchestrator remains inactive until step 9 is verified. The parent of the cutover commit still
has this governance task as the sole `implemented_pending_human_review` owner; the cutover commit has v2
idle plus the exact close record. There is no committed ordinary-idle window in which another task can
activate. During the helper-write-to-commit interval primary is deliberately dirty, so v1 activation
also fails closed. If the cutover commit cannot be created, the governance task is not considered
closed and no runtime message is sent.

### 8.2 Future complex tasks

Each durable transition that changes active phase or authority is a board/evidence commit before the
next role starts. Approval commit precedes worktree creation. Developer produces a clean code commit.
Reviewer and QA bind the same exact subject code commit. Integrator is read-only and emits a pass bound
to that subject. The runtime orchestrator alone performs primary Git integration using section 10.1.
User close is committed before the probe-approved closeout sequence begins; final closeout to idle is
committed only after all required retirement/archive conditions pass. No push occurs.

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

The runtime orchestrator creates roles lazily. The pre-approval Planner is a fresh read-only agent on
primary. It receives the active intake, repository refs and Planner contract, but no worktree or
implementation authority. Developer and later roles are fresh agents inside the one approved host.
Each role attempt receives a context-free prompt plus only the applicable items below:

- current board active ref/digest;
- task and approved plan refs;
- exact base/current commit;
- current-stage evidence refs;
- the role section of the new serial-complex protocol;
- exact May Touch/Must Not Touch and validation contract.

Planner cannot write or implement; it returns bounded proposed content and the runtime orchestrator
writes the task/plan subject commit and a separate Planner-evidence commit on primary. The raw Planner
response is not itself a transition callback: after both commits exist, the runtime orchestrator
constructs the canonical seven-line Planner capsule from those exact refs and stores the raw-response
hash in evidence. Developer writes only approved paths and commits cleanly.
Reviewer is a fresh agent that reviews approved base..Developer subject commit and cannot reuse
Developer chat. QA is another fresh agent that validates the exact Reviewer-passed subject commit.
The Integrator agent is read-only: it verifies approval, Reviewer/QA evidence, ancestry, clean state
and exact package, then returns pass/block. It never writes primary or runs the merge. The runtime
orchestrator owns board/native-tool actions and the exact primary integration transaction in 10.1.

Formal result is one committed evidence document per role attempt. It contains one exact machine
record and a bounded human explanation. Callback is exactly seven ordered lines and <=1024 bytes:

```text
TASK_ID: <TASK_ID>
ROLE: <Planner|Developer|Reviewer|QA|Integrator>
STATUS: <exact section-7.3.1 status>
SUBJECT_COMMIT: <40-hex exact code/planning subject commit>
EVIDENCE: <repo-path@40-hex-evidence-commit#64-hex-sha256>
NEXT: <exact section-7.3.1 next value>
BLOCKER: <none|exact section-7.4 blocker object>
```

`SUBJECT_COMMIT` is always the immutable content being decided: Planner uses the committed planning
subject; Developer uses its latest code commit; Reviewer, QA and Integrator all use that same latest
code commit until a Developer fix creates a new one. `EVIDENCE` names the separate commit containing
the evidence document. An evidence commit must descend from its subject/current evidence chain and its
diff may touch only the role's allowed evidence path; it must not change any approved code path. Thus
evidence commits may advance branch HEAD without changing the reviewed code tree.

The board writer validates schema, Task ID, current role/attempt, subject/evidence commit and hash,
ancestry, evidence-only diff, allowed status, scope, worktree cleanliness and duplicate identity. Exact
duplicates are no-op; divergent duplicates block. A `callback_pending` state survives a process
interruption. No next role starts until callback evidence is committed and the phase-transition commit
is clean.

Reviewer blocking returns to a new Developer attempt then a new Reviewer attempt. QA blocking returns
to Developer, then Reviewer, then QA. Integrator never accepts a commit not jointly bound by the most
recent passing Reviewer and QA evidence.

Independent Reviewer/QA is guaranteed by fresh agent identity, no inherited task chat, immutable refs,
read-only role contracts, and committed evidence—not by titles or conversational claims.

### 10.1 Frozen Primary Integration Transaction

After an Integrator pass, the runtime orchestrator—and no role agent—performs primary integration:

1. require clean primary `master`, exact expected primary HEAD, clean task worktree, exact branch HEAD,
   and no pending callback;
2. prove the latest Reviewer, QA and Integrator evidence all bind the same `SUBJECT_COMMIT`, and that
   branch HEAD descends from that subject through evidence-only commits;
3. run a read-only `git merge-tree` preflight for exact primary HEAD and exact branch HEAD; any conflict
   records `integration_blocked` without touching either worktree;
4. if and only if preflight is clean and HEADs remain unchanged, run the single non-interactive strategy
   `git merge --no-ff --no-edit --no-autostash <exact-task-branch>` on primary;
5. verify the resulting merge commit has parent 1 equal to the expected primary HEAD, parent 2 equal to
   the exact branch HEAD, and a tree equal to the preflight merge tree; also verify approved code paths
   contain the `SUBJECT_COMMIT` content and branch evidence is present;
6. only after those proofs, write and commit the board transition to
   `implemented_pending_human_review`.

The task worktree is never modified by primary integration. A race or unexpected merge failure is not
reconciled automatically. If Git created the exact expected `MERGE_HEAD` from a previously clean
primary, the controller may run only the explicitly authorized transactional `git merge --abort` and
must prove the original HEAD/index/worktree were restored exactly. If that bounded abort fails or the
facts differ, primary receives no further command, the task worktree is retained, and the task records
`integration_blocked` for User direction. No cherry-pick, rebase or alternate strategy is permitted.

## 11. Archive And Closeout

User close changes a complex task from human review to `closing`; it does not release active. Common
closeout prerequisites are:

1. all callbacks consumed and evidence committed;
2. integrated commit verified on clean primary;
3. task worktree clean, exact host task ID known, and no role agent running;
4. the board contains the exact closeout order proven by the capability probe and explicitly approved
   in the cutover authorization.

Only then does the runtime orchestrator execute that one frozen sequence. The two candidate orders are
`stop -> retire -> archive` and `stop -> archive -> retire`; Revision 5 approves neither. The capability
probe must prove one, the second User approval must name it, and the normative cutover protocol must
freeze it. The implementer and runtime orchestrator cannot switch orders dynamically. If neither is
proven, cutover is blocked.

After the approved sequence succeeds (or an explicit User-approved worktree retain record satisfies
the retirement side), the archive result is recorded and final board closeout may enter idle.

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
- Before the second cutover approval, `AGENTS.md`, the runtime-orchestrator skill, current normative
  policy, `run_task.ps1` and the execution gate are byte-unchanged; new complex behavior is therefore
  unreachable from the daily entry path.
- No credentials, tokens, undocumented HTTP calls or direct Codex API emulation enter the repository.
- Board size remains under existing 400-line/65,536-byte thresholds; completed detail goes to evidence.

This split prevents a giant state machine: storage/CAS, pure complex rules, thin CLI, thin PowerShell
and native task actions remain separate and testable.

## 14. Exact Phased Implementation Boundary

The Task file freezes two distinct authorization phases. Task, Plan and board may appear in both only
for explicitly different lifecycle/status purposes; no cutover behavior is permitted during the first
phase. Any additional file edit stops for renewed approval. Commands may change; paths may not.

### 14.1 First approval: implementation before cutover

The 18 pre-cutover paths are Task, Plan, board for v1 lifecycle records only, the new non-normative
protocol, capability evidence and cutover manifest, the current helper plus three bounded new helper
modules, and the eight named test files. The helper may gain v1-compatible/dormant v2 support, but the
current entry, gate and normative instructions cannot call it. This phase ends at v1
`implemented_pending_human_review`.

```text
tasks/TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION.md
docs/task_governance_serial_complex_role_chain_automation_plan.md
docs/task_board.md
docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md
docs/lane_evidence/TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION_capability_probe.md
docs/lane_evidence/TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION_cutover_manifest.json
scripts/connlab_personal_task.py
scripts/connlab_serial_board.py
scripts/connlab_serial_complex.py
scripts/connlab_serial_worktree.ps1
tests/unit/test_connlab_personal_serial_workflow.py
tests/unit/test_connlab_serial_classifier.py
tests/unit/test_connlab_serial_complex_state.py
tests/unit/test_connlab_serial_complex_worktree.py
tests/unit/test_connlab_serial_complex_orchestrator_contract.py
tests/unit/test_connlab_execution_gate_script.py
tests/unit/test_task_scoped_role_thread_lifecycle_governance.py
tests/integration/test_connlab_serial_complex_recovery.py
```

### 14.2 Second approval: cutover only

Only after implementation review and the capability probe may the User authorize the eight cutover
paths: `AGENTS.md`, runtime-orchestrator skill, current policy, `run_task.ps1`, execution gate, board
atomic migration/close, and status-only Task/Plan edits. All eight are staged into the same cutover
commit where applicable. No earlier commit may modify them.

```text
AGENTS.md
.agents/skills/connlab-lane-orchestrator/SKILL.md
docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md
scripts/run_task.ps1
scripts/connlab_execution_gate.ps1
docs/task_board.md
tasks/TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION.md
docs/task_governance_serial_complex_role_chain_automation_plan.md
```

New pre-cutover files are the serial complex protocol, capability probe evidence, cutover manifest,
shared serial board module, pure classifier/complex transition module, bounded worktree verifier, four
unit modules and one recovery integration test.

Frozen and preserved:

- every product path and unrelated task/plan/protocol/skill/test;
- history generations/index;
- Task-A and all retained lane/evidence/worktrees;
- legacy transition/handoff/lane-worktree implementations and Controlled Lane V2;
- external governance-migration repository and all remotes.

## 15. Test Matrix

Automated or repeatable native validation must cover at least these acceptance groups:

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

Revision 2 adds these mandatory groups:

30. pre-approval Planner is read-only on primary and no worktree host exists yet;
31. every cutover-only file remains byte-unchanged through pre-cutover human review;
32. the cutover commit parent retains the v1 active governance task while the commit itself contains
    v2 idle plus the exact close record—there is no intermediate committed idle state;
33. `SUBJECT_COMMIT` remains stable across Reviewer/QA/Integrator while each `EVIDENCE` ref binds its
    separate evidence-only commit;
34. primary integration uses only the frozen no-ff merge, verifies both parents/tree, and a preflight
    conflict leaves both worktrees unchanged; the bounded abort path restores the exact original
    primary or blocks without further mutation;
35. the capability probe, second User approval and cutover protocol all name the same one closeout
    order, and runtime cannot substitute the other order.

Revision 3 adds these mandatory groups:

36. the Task's canonical approved-request JSON hash is
    `084ce08da66870ebde4d0bd0f929c310fce4ce8aa4204338aa95608e94fcd4be`, contains 18 paths and is
    accepted unchanged by a current-v1-helper fixture;
37. every frozen complex command accepts only its named parameters and every unlisted state/command
    pair is zero-write `BLOCKED_STATE` or `BLOCKED_ARGUMENT_COMBINATION`;
38. every blocker schema/code combination and stable result/no-op/blocked code is deterministic and
    rejects unknown or inconsistent fields;
39. the cutover manifest contains exactly eight reconstructible targets and recomputed target hashes,
    blobs and `TARGET_SET_SHA256` equal the second approval;
40. source Git-index entries and `git write-tree` equal the committed `MANIFEST_REF`; the target index
    deterministically overlays only the eight target blobs on that source, while both uncommitted
    exact-path restore and pre-activation committed revert prove the full source tree/index/board;
41. effective read-only permission for the orchestrator skill returns
    `BLOCKED_CUTOVER_PATH_READ_ONLY` before any board/other/index write;
42. the canonical history index guard remains exact through apply, failure rollback and committed
    revert.

Revision 4 adds these mandatory groups:

43. `apply-cutover` changes only eight worktree paths and never changes HEAD or the Git index; only the
    Controller exact-stages/commits, and runtime messaging is blocked until read-only
    `verify-cutover-commit` passes;
44. every legal `ROLE + STATUS + NEXT` tuple accepts only its frozen phase, subject and blocker
    combination, while aliases and cross-role combinations are zero-write rejected;
45. every blocker code enforces its exact required/null fields, retryable/requires-user booleans and
    resume policy;
46. read-only cutover paths block before manifest generation; after an explicit exact-path permission
    grant, manifest generation records eight writable observations before User approval;
47. apply rechecks all eight permissions against the approved manifest, and any drift forces a new
    manifest commit plus a new second approval before materialization.

Revision 5 adds these mandatory groups:

48. `--permission-preflight-json` and every other caller permission assertion are rejected; both
    commands obtain permission facts only from the shared intrinsic probe;
49. the probe opens every existing target with the exact non-truncating read/write flags, makes no
    write call, proves pre/post bytes/SHA-256/Git blob equality, freezes enums, and validates the
    canonical receipt hash;
50. one bounded permission-drift test allows manifest generation, denies one target's read/write
    handle before apply, and proves `BLOCKED_CUTOVER_PATH_READ_ONLY` with zero materialization calls,
    unchanged eight target bytes, unchanged Git index and unchanged HEAD.

Group 50 is exactly one test in the already approved
`tests/unit/test_connlab_serial_complex_orchestrator_contract.py`; it does not add a test path.

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

`plan-cutover` runs after implementation/probe completion and an explicit exact-path tool permission
grant, but before the second approval. It is zero-write and requires the exact v1
`implemented_pending_human_review` governance Task ID, passed validation, no blocker, empty FIFO,
clean primary, accepted helper ancestry, the probe-approved closeout order and a current permission
grant under which its own intrinsic handle probe proves all eight paths writable. It accepts no
permission proof from the caller. An idle source or any denied/unknown path is rejected before a
manifest payload exists. The Controller writes the returned exact `payload` and commits it under the
first approval as:

```text
docs/lane_evidence/TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION_cutover_manifest.json
```

### 17.1 Exact Cutover Manifest Contract

The manifest schema is `connlab.serial-cutover-manifest` version 1 with exact top-level keys:

```text
schema, version, task_id, authority_base_commit, authority_base_tree,
authority_base_board_sha256, authority_base_control_digest, closeout_order,
target_set_sha256, files, index_derivation, canonical_history_index_guard,
permission_proof, rollback, created_at
```

`files` contains exactly eight ordered records for:

```text
AGENTS.md
.agents/skills/connlab-lane-orchestrator/SKILL.md
docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md
scripts/run_task.ps1
scripts/connlab_execution_gate.ps1
docs/task_board.md
tasks/TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION.md
docs/task_governance_serial_complex_role_chain_automation_plan.md
```

Each record has exactly:

```text
path, mode, source_exists, source_bytes, source_sha256, source_blob,
target_exists, target_bytes, target_sha256, target_blob, target_bytes_base64
```

The base64 field makes every approved target reconstructible without chat, an ambient temp directory
or implementation judgment. `target_blob` is the Git blob ID computed from decoded target bytes.
`target_set_sha256` hashes the canonical ordered tuples
`path,mode,target_bytes,target_sha256,target_blob`. Nulls/placeholders and duplicate/reordered paths are
invalid. The board target must simultaneously contain v2 idle, exact governance `last_closed`, retained
history and FIFO invariants; all seven other targets are the exact cutover contract/entry/status bytes.

`authority_base_commit` is the clean implementation-completion commit before the first manifest
revision; it is not the self-referential manifest commit. `index_derivation` has exact keys
`authority_base_write_tree, authority_base_entries_sha256, manifest_commit_rule, source_index_rule,
target_index_rule, authorized_paths`. The base tree and ordered stage-zero index entries must equal
`authority_base_commit`. `manifest_commit_rule` requires a linear, no-merge chain from that base to the
commit component of the approved `MANIFEST_REF`; every commit in the range may change only this one
manifest path. This permits a permission-drift regeneration without rewriting history, while the
approved ref always selects the newest exact payload. The manifest never attempts to predict its own
blob, tree or commit ID.

At cutover, `source_index_rule` requires clean `HEAD` to equal `MANIFEST_REF.commit`, and derives the
complete source entries plus `git write-tree` directly from that immutable commit. `target_index_rule`
creates a temporary index from the same commit and overlays exactly the eight decoded target blobs;
no other entry may differ. The resulting target entries hash and `git write-tree` are recomputed before
writing and again before commit. Because the second approval binds both the exact `MANIFEST_REF` and
`TARGET_SET_SHA256`, the complete source and target index states are deterministic without a circular
self-hash in the manifest. `authorized_paths` is the same ordered eight-path list.

`canonical_history_index_guard` freezes path, byte count, SHA-256 and Git blob for
`docs/archive/task_board_history/index.v1.jsonl`; cutover neither stages nor rewrites it.

`permission_proof` is the exact intrinsic `connlab.serial-cutover-permission-proof` object from
section 7.2.1. The current Codex permission profile exposes
`.agents/skills/connlab-lane-orchestrator/SKILL.md` as read-only even though its Windows file attribute
is normal, so `plan-cutover` currently returns `BLOCKED_CUTOVER_PATH_READ_ONLY` with zero writes and no
manifest. The first implementation approval does not grant permission. The User must separately grant
the exact tool write permission for that path; the Controller does not change ACLs or attributes.

After the grant, the Controller calls `plan-cutover` without any permission payload. The helper's own
process performs the section-7.2.1 probe and embeds only a fully successful canonical proof. A
manifest with a missing proof, wrong enum/receipt, failed path, caller-added field or non-identical
pre/post content is schema-invalid and can never reach User approval.

Immediately before `apply-cutover`, the new helper process runs the same internal function before
decoding target content. The fresh proof must have the same frozen source/algorithm, path order,
resolved paths and source byte/hash/blob triples as the approved manifest; PID/timestamps and receipt
hash are expected to differ and are validated independently. If any read/write handle is denied or a
source fact drifts, apply returns the applicable blocked code with zero materialization calls and zero
content writes. The Controller must re-obtain permission if needed, regenerate and commit a new
manifest revision, and obtain a new exact second approval; an older approval cannot authorize it.

### 17.2 Second-Approval Binding

The User's second approval must quote all three values:

```text
MANIFEST_REF: docs/lane_evidence/TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION_cutover_manifest.json@<40hex>#<sha256>
TARGET_SET_SHA256: <64hex>
CLOSEOUT_ORDER: <the one probe-proven enum>
```

and explicitly authorize `atomic close + v1-to-v2 cutover + manifest-defined rollback`. Missing or
different values return `BLOCKED_CUTOVER_NOT_AUTHORIZED`. `apply-cutover` independently recomputes every
source/target/hash/blob/index/permission/history guard before writing; a mismatch returns the specific
blocked code with zero writes.

### 17.3 Complete Failure Rollback Manifest

`rollback` has exact keys `authorized_paths, source_ref_rule, expected_source_board_sha256,
uncommitted_restore_argv, committed_revert_argv, post_restore_checks`. `authorized_paths` is the same
ordered eight-path list and `source_ref_rule` is exactly `MANIFEST_REF.commit`.

- Before the cutover commit exists, the only rollback is the manifest-expanded exact command
  `git restore --source=<MANIFEST_REF.commit> --staged --worktree -- <eight exact paths>`. It is
  authorized solely because that approved commit was clean and every preimage/index derivation is in
  the approved manifest.
- After the cutover commit exists but before any runtime message or v2 activation, the only rollback is
  `git revert --no-edit <exact-cutover-commit>` while HEAD equals that commit; its result tree must
  equal `MANIFEST_REF.commit^{tree}`.
- Both paths must prove all eight source byte hashes/blobs, the source board/control digest, complete
  source index entries hash, source `git write-tree`, canonical history-index guard and clean
  `git status` against `MANIFEST_REF.commit`.
- If rollback itself differs or fails, stop immediately with `BLOCKED_CUTOVER_ROLLBACK_FAILED`; do not
  reset, clean, retry another strategy, message the runtime orchestrator or activate FIFO.

`apply-cutover` rechecks permission and all manifest/source/history guards, writes the seven non-board
targets first and the manifest-bound board target last, then verifies all eight worktree byte
hashes/blobs. It never changes the Git index or HEAD. Success requires clean source index, unchanged
HEAD, exactly eight dirty worktree paths and exact target bytes; it returns `ALLOW_APPLY_CUTOVER`.

The Controller then performs the only Git transaction, with no helper exception:

```text
git add -- AGENTS.md .agents/skills/connlab-lane-orchestrator/SKILL.md docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md scripts/run_task.ps1 scripts/connlab_execution_gate.ps1 docs/task_board.md tasks/TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION.md docs/task_governance_serial_complex_role_chain_automation_plan.md
git commit -m "governance: cut over serial complex role chain"
```

Before commit it verifies the staged path set, stage-zero index entries and derived target
`git write-tree`; unstaged paths must be empty. If exact-stage or commit fails, the Controller executes
the manifest's uncommitted exact-path restore and proves the source commit tree/index/board. It never
uses `git add -A`, amend, stash, reset, clean, alternate merge or another message. Thus section 13's
“helpers never stage or commit” rule has no exception.

After commit, the Controller calls read-only `verify-cutover-commit` with the approved manifest ref,
exact new commit and approval ref. It requires current clean HEAD to equal that commit; exactly one
parent equal to `MANIFEST_REF.commit`; an exact eight-path diff; target hashes/blobs/tree/index equal
the manifest derivation; the v2 idle close record; and unchanged history guard. Failure triggers only
the manifest-authorized committed revert and verification against `MANIFEST_REF.commit`. No runtime
message or task activation is legal until `ALLOW_VERIFY_CUTOVER_COMMIT`. The commit parent retains the
v1 active governance task; the verified result is v2 idle with its close record, so there is no
committed authority gap.

Before any v2 task activation, a manifest-authorized committed revert restores the v1 parent with this
governance task still active in human review. After a v2 task activates, no automatic rollback is
allowed; the task stays active/blockered and this controller fixes forward. Parallel legacy automation
is never restored.

## 18. Cutover And Pilot

1. Current controller implements behind inactive entry points and runs offline tests.
2. It completes the capability probe; any unproven critical capability blocks cutover.
3. Current governance task enters human review under v1.
4. The current read-only orchestrator-skill path blocks here. User separately grants exact tool write
   permission; the Controller supplies no permission assertion. No repository target is written.
5. In its own process, `plan-cutover` probes all eight paths, proves unchanged contents, and emits the
   intrinsic receipt plus all exact target byte bundles/hashes and the complete rollback/index
   manifest; the Controller commits the exact payload while v1 active remains in human review.
6. User reviews and gives one explicit combined `close + cutover` authorization quoting the exact
   manifest ref, `TARGET_SET_SHA256` and probe-proven `CLOSEOUT_ORDER`; a plain `关闭` or unbound
   approval is insufficient.
7. In the same process that would materialize content, `apply-cutover` first runs the identical probe.
   Permission/content drift blocks before decoding/writing targets and requires a new manifest commit
   plus new approval. Otherwise it materializes/verifies eight paths without staging.
8. The Controller exact-stages and creates one cutover commit whose parent still has the v1 active
   governance task; read-only `verify-cutover-commit` must pass for the exact parent/tree/index/diff.
9. Only after that verification, Controller sends one bounded message to `019fb3d4...` telling it to
   discard chat memory as authority and reread exact AGENTS, board, skill, protocol and cutover commit.
10. Runtime orchestrator first performs read-only inspect/classifier self-check; it does not restore old
   roles or Task-A.
11. User approves one low-risk pilot that is intentionally complex enough to exercise every role.
12. Pilot validates Planner, approval, Developer, Reviewer, QA, Integrator, human review, User close,
   retirement and archive.
13. Pilot failure retains active/blocker and returns to this governance controller; no old-flow or
   direct-implementation fallback occurs.

`019fb3d4...` is currently addressable but `notLoaded` and its last content reflects frozen Task-A-era
authority. It is therefore not safe to use before step 8. No generation rollover is justified now.

After successful pilot, `019fb3d4...` is the sole daily runtime orchestrator. `019fc491...` remains an
out-of-band governance maintenance/recovery entry, not a competing daily router.

## 19. Direct Answers To Design Questions

1. **No self-modifying loop:** the stable v1 controller plans, implements and reaches human review
   while retaining active. After combined User authorization, one cutover commit simultaneously closes
   it and switches authority; the target runtime orchestrator is inactive until that commit is clean.
2. **One worktree:** WIP is one and roles are serial; one shared task worktree is the only mutable code
   authority. More would require forbidden synchronization/reconciliation.
3. **No parallel/preemption/reconciliation:** a single owner and FIFO eliminate every legitimate need
   for them; interruption recovery concerns only the same active Task ID.
4. **Independent Reviewer/QA:** each is a fresh minimal-context agent bound to immutable commits and
   committed evidence, never Developer chat.
5. **No historical contamination:** every complex task receives a new pre-approval Planner agent, a new
   post-approval host and new execution-role agents; recovery uses durable refs. Old contexts are never
   reused.
6. **Lifecycle choice:** Option B is selected because current native thread tools do not prove multiple
   task threads can share one existing worktree. Planner is read-only on primary before approval; only
   Developer through Integrator use the later host. A capability probe must validate that lifecycle.
7. **Runtime recovery:** after cutover, send one exact re-read capsule and require read-only authority
   validation before accepting a pilot or ordinary task.
8. **Controller after cutover:** keep `019fc491...` only for governance maintenance and fail-safe
   repair; it must not receive ordinary daily tasks in parallel with the runtime orchestrator.

## 20. Risks And Approval Decisions

1. Native archive state and Codex worktree retirement semantics are not fully observable today. Default
   decision: require a successful reversible capability probe and second User approval of one exact
   closeout order; otherwise block cutover.
2. Option B replaces five visible role tasks with one visible task-scoped worktree host plus ephemeral
   fresh role agents, plus a pre-approval read-only Planner agent. Default decision: approve this model
   because it is compatible with exactly one implementation worktree without unsupported binding.
3. Archive success may be callable but not independently readable. Default decision: keep active in
   `archive_pending_unverifiable` until a later proof or explicit User waiver; additionally, current
   Codex permissions make the orchestrator skill read-only, so manifest generation remains blocked
   until an explicit permission grant passes preflight. A manifest is never approved with read-only
   observations: the helper accepts no caller permission claim and records only its intrinsic
   handle-probe receipt. Permission drift forces regeneration/reapproval. Neither condition rolls back
   integrated code or auto-releases WIP.

## 21. Approval And Stop Point

The first User approval authorizes only the 18-path `implementation-before-cutover` allowlist and the
implementation/probe sequence up to v1 `implemented_pending_human_review`. It does not authorize any
cutover-only file, atomic close/migration, runtime-orchestrator message, real pilot, push, forced
cleanup, Task-A change, legacy recovery, or archive/deletion of existing tasks.

It must bind the exact Task JSON whose canonical SHA-256 is
`084ce08da66870ebde4d0bd0f929c310fce4ce8aa4204338aa95608e94fcd4be`, plus the committed Revision 5
Plan ref and exact User wording. Any JSON difference requires another planning revision.

A second explicit User approval is mandatory after implementation review. It must authorize the eight
cutover-only paths, combine governance close with v1-to-v2 cutover, quote the exact committed
`MANIFEST_REF` and `TARGET_SET_SHA256`, name the exact probe-proven `CLOSEOUT_ORDER`, and authorize the
manifest-defined failure rollback. Without every binding, the task remains active in v1 human review.

After approval, first call the current helper's `approve` with the committed Plan ref, exact approved
request JSON and exact User approval evidence; exact-stage only `docs/task_board.md`, commit it, confirm
primary clean, and only then edit implementation files.

Until then: `READY_FOR_USER_APPROVAL` and stop.
