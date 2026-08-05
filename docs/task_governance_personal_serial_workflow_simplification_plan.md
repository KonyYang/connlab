# ConnLab Personal Serial Workflow Simplification Plan

Status: `IMPLEMENTED_PENDING_HUMAN_REVIEW`
Task: `TASK_GOVERNANCE_PERSONAL_SERIAL_WORKFLOW_SIMPLIFICATION`
Date: 2026-08-06
Original planning base: `ae33faa38894c26245397226d8e4357512c77b91`
Revision-1 commit: `34379138df1fcd70ee305076662a502fb30389ff`
Revision-2 commit: `37e9a4d5570fe739a6648aeb092f2d0e2e31eb46`
Revision-3 commit: `75619c67f73ba330f8aa2085b5de120777ae64b8`
Revision-4 commit: `a796d574bf6747ee091adbf4881aa8cb623a7a36`

Approval: User approved Revision 4 for implementation on 2026-08-06 in thread
`019fc491-21b0-77b0-bf18-53f53a366a7c`.

Scope correction: after the committed `SCOPE_EXPANDED` blocker proved that the required legacy
`inspect` command rejected the new personal board schema, the User explicitly approved adding
`scripts/connlab_active_context.py` on 2026-08-06. The correction is limited to read-only
`inspect` compatibility. Archive, maintenance, rollback, and mixed-EOL behavior remain frozen.
The runtime did not expose a side-conversation thread ID, so none is asserted. Durable approval
evidence is instead the exact User wording `请解决`, sent directly in response to the selected
scope-correction request. The later exact direction beginning `我也发现注意点` and ending
`请按照你的建议执行下一步。` explicitly authorizes correcting this evidence and the self-review
findings without expanding the approved path set.

Self-review corrective scope remains within the existing allowlist: prevent idle-state FIFO
bypass, expose `run_task.ps1 -ActivateNext/-Json`, validate stored nested authority fail-closed,
reject incompatible CLI arguments, and replace the imprecise approval reference with the exact
wording above.

## 1. Outcome

ConnLab will use one personal active task and one durable FIFO queue. The current conversation is
the executor. It does not dispatch Planner, Developer, Reviewer, QA, Integrator, Quick Fixer, or
any other task conversation. Implementation occurs directly in the primary worktree.

A qualifying simple task skips plan creation and plan approval. Every implemented task still runs
bounded validation, creates a local commit, and remains active as
`implemented_pending_human_review` until the User says `关闭`.

This revision adds the missing atomic board writer, activation-before-implementation commit,
explicit simple-task classification record, blocked/dirty-worktree behavior, immutable history
checks, and an exact implementation allowlist.

Review disposition:

| Finding | Revision-2 resolution |
|---|---|
| no board write entry | one CAS/lock/atomic-replace helper is the sole post-migration writer |
| WIP gap during implementation | activation commit precedes every implementation edit |
| unprovable/expanded simple scope | structured classification; 1–3 total paths including tests and board |
| missing failure semantics | blocked task retains active slot; dirty close/cancel is forbidden |
| history compatibility | active-context helper/archive/index are protected and hash-checked |
| expandable test scope | commands may change; file allowlist may not change without new approval |
| queued head cannot restart | explicit `activate-next` atomically dequeues only the FIFO head |
| incomplete CLI contract | exact flags, request/validation schemas, output envelope, and codes frozen |
| Git/lock contradiction | helper never stages/commits; lock moves to ignored primary `tmp/` |
| residual migration ambiguity | four current residuals receive exact frozen migration rows |
| planned approval visibility | approval transition receives its own clean primary commit |
| planned intake requires unknown scope | minimal planned intake; approval atomically binds full approved request |
| blocker has no legal payload | independent typed `connlab.personal-task-blocker` schema |
| legacy inspect rejects the personal board | approved scope rebind plus read-only personal-schema inspect compatibility |

## 2. Discovery And Frozen User Decisions

Confirmed by the User:

- only one person develops ConnLab, so implementation concurrency is unnecessary;
- exactly one task may be active; every later task waits in FIFO order;
- a simple task has a clear root cause, is limited to one to three files, and changes no API,
  database, persistence, or business-rule semantics;
- simple tasks require neither a prior plan nor plan approval;
- completed implementation becomes `implemented_pending_human_review`; only `关闭` closes it;
- work happens directly in primary without lane branches or sibling worktrees;
- former roles are not dispatched and Task-A remains cancelled and retained.

Conservative clarification adopted by this revision:

- the one-to-three-file limit includes every changed repository file for the simple task,
  including tests and the mandatory `docs/task_board.md` state update;
- exceeding that total is not a simple task and requires the planned flow;
- closing makes the FIFO head eligible but never starts it automatically.

Repository evidence:

- planning began from clean `master@ae33faa38894c26245397226d8e4357512c77b91`;
- the board was valid `cancelled` state with `active=null` and no token owner;
- current WIP policy already says WIP=1/FIFO but retains parallel, preemption, reconciliation,
  worktrees, role gates, handoffs, and Integrator closeout;
- `scripts/run_task.ps1` promises execution through Integrator and has no board-state writer;
- `scripts/connlab_execution_gate.ps1` is read-only and validates the obsolete state model.

No implementation is authorized by this revision. The approved planning commit will be the
required clean primary HEAD before activation.

## 3. Single Board Writer

Add one bounded helper:

`scripts/connlab_personal_task.py`

After the migration activation commit, it is the only supported writer of the marker-delimited
control block in `docs/task_board.md`. Agents and PowerShell entry points must call it; they must
not independently patch control JSON.

Because the helper does not exist before this task is implemented, the migration has one explicit
bootstrap exception: immediately after plan approval, the current conversation applies one exact
`apply_patch` transition from the verified legacy cancelled block to the personal
`running/implementation` block and commits it before touching any other implementation path. The
patch is bound to the approved board bytes/HEAD, preserves retained-history pointers, and is
validated by independent JSON/hash checks. No later manual control-block patch is allowed.

### 3.1 Atomicity

Every write command must:

1. resolve and verify the primary repository;
2. resolve `<primary>/tmp/connlab_personal_task.lock`, prove its canonical parent is exactly the
   primary repository's ignored `tmp` directory, and acquire it using create-new semantics;
3. parse exactly one control block and validate its complete schema;
4. compare the current board SHA-256 with the caller's `expected_board_sha256`;
5. validate the requested transition and current Git facts;
6. render the complete new board in memory;
7. write, flush, and `fsync` a sibling temporary file, then atomically replace the board;
8. re-read and validate the resulting bytes;
9. release the lock in `finally`.

A pre-existing lock, path escape, hash mismatch, malformed board, failed replacement, or failed
post-write validation returns stable `BLOCKED_*` output without attempting a second transition. A
stale lock is reported for manual inspection and is never deleted automatically. Repository
`.gitignore` already contains `tmp/`; the helper neither writes to `.git` nor adds the lock to Git.

### 3.2 Commands

The helper exposes only:

- `inspect`: zero-write schema, board hash, active, queue, and Git-status summary;
- `check`: zero-write `Inspect | Implementation | Close` decision for the PowerShell gate;
- `submit`: atomically activates when idle or idempotently appends to FIFO when occupied;
- `activate-next`: when idle, atomically removes and activates only the exact FIFO head after an
  explicit execute/continue command;
- `approve`: atomically binds the complete approved scope/validation contract and moves a planned
  task from planning to implementation after explicit plan and approval refs; when an already
  approved planned task is committed as blocked with `SCOPE_EXPANDED`, it may instead record a
  User-approved strict path superset and new plan/approval refs while preserving the blocker until
  a separate explicit `resume`;
- `mark-review`: records passed validation and enters `implemented_pending_human_review`;
- `block`: keeps `running` and records one typed blocker payload;
- `resume`: clears a blocker only after explicit User direction while retaining the same task;
- `cancel`: releases a task only after explicit User direction and a clean worktree;
- `close`: closes only a clean, validated `implemented_pending_human_review` task.

No command stages, commits, restores, discards, cleans, pushes, implicitly starts a queued task,
creates a branch/worktree, or dispatches a conversation. The current conversation performs every
exact-path stage and local commit after independently checking helper output and board bytes.

### 3.3 Frozen CLI And JSON Contract

Common helper arguments:

- every command requires `--repo-root <absolute-or-resolvable-primary-path>` and supports `--json`;
- every writer requires `--expected-board-sha256 <64-lowercase-hex>`;
- task-specific writers require `--task-id <TASK_ID>`;
- `submit` additionally requires `--request-json <JSON-string>`;
- `approve` additionally requires `--approval-ref <non-empty-user-approval-reference>` and
  `--plan-ref <committed-plan-path@commit#sha256>` plus
  `--approved-request-json <JSON-string>`;
- `mark-review` additionally requires `--validation-json <JSON-string>`;
- `block` additionally requires `--blocker-json <JSON-string>` and does not accept
  `--validation-json` separately;
- `resume`, `cancel`, and `close` additionally require
  `--decision-ref <non-empty-user-decision-reference>`;
- `cancel` also requires `--disposition <non-empty-text>`;
- `inspect` omits expected hash and task ID; `check` omits expected hash, requires
  `--intent <Inspect|Implementation|Close>`, and requires `--task-id` except for `Inspect`;
- `activate-next` uses the complete stored FIFO-head request and accepts no replacement request
  payload.

`--request-json` uses discriminated schema `connlab.personal-task-request`, version `1`.

A simple intake must provide the complete contract at first submit:

```json
{
  "schema": "connlab.personal-task-request",
  "version": 1,
  "task_id": "TASK_ID",
  "summary": "bounded human-readable summary",
  "kind": "simple",
  "may_touch": ["docs/task_board.md", "path/to/change"],
  "expected_file_count": 2,
  "classification_reason": "root cause and expected result",
  "targeted_validation": ["exact command or bounded manual smoke"],
  "forbidden_categories": {
    "api_contract": false,
    "database": false,
    "schema_or_migration": false,
    "persistence": false,
    "authority": false,
    "public_drive_workflow": false,
    "business_rule_semantics": false,
    "destructive_action": false,
    "external_mutation": false
  },
  "plan_ref": null
}
```

A planned intake has exactly the minimal keys below because scope is not known before planning:

```json
{
  "schema": "connlab.personal-task-request",
  "version": 1,
  "task_id": "TASK_ID",
  "summary": "bounded human-readable summary",
  "kind": "planned"
}
```

No `may_touch`, file count, validation, classification, forbidden-category, or plan field is legal
in planned intake. It queues or activates as `running/planning` with `scope_contract:null`.
`activate-next` preserves that minimal record and enters planning; it does not invent scope.

`--approved-request-json` uses exactly schema `connlab.personal-task-approved-request`, version `1`:

```json
{
  "schema": "connlab.personal-task-approved-request",
  "version": 1,
  "task_id": "TASK_ID",
  "summary": "approved bounded summary",
  "kind": "planned",
  "may_touch": ["docs/task_board.md", "approved/path"],
  "expected_file_count": 2,
  "classification_reason": "approved scope and risk explanation",
  "targeted_validation": ["approved validation command"],
  "forbidden_categories": {
    "api_contract": false,
    "database": false,
    "schema_or_migration": false,
    "persistence": false,
    "authority": false,
    "public_drive_workflow": false,
    "business_rule_semantics": false,
    "destructive_action": false,
    "external_mutation": false
  }
}
```

For a planned task these booleans are explicit scope facts and may be true; they are not a fast-path
eligibility test. `approve` requires the approved request task ID to match the active planning task,
requires normalized unique paths including `docs/task_board.md`, requires file count to equal path
count, binds the separate committed `--plan-ref` and `--approval-ref`, and atomically replaces
`scope_contract:null` with this complete contract. It cannot change queue order or another task.

Simple requests permanently use the first full shape, require all forbidden booleans false, and
remain subject to the strict 1–3-total-path rule. For both intake shapes the top-level `task_id`
must equal `--task-id`. Unknown/missing keys, a mixed shape, duplicate/non-normalized paths,
non-string validation entries, or wrong types fail closed.

`--validation-json` must use exactly schema `connlab.personal-task-validation`, version `1`:

```json
{
  "schema": "connlab.personal-task-validation",
  "version": 1,
  "status": "passed",
  "checks": [
    {"command": "exact command", "exit_code": 0, "summary": "observed result"}
  ],
  "observed_paths": ["docs/task_board.md", "path/to/change"],
  "manual_checks": [],
  "recorded_at": "RFC3339 timestamp"
}
```

`status` is `passed | failed`. `mark-review` requires `passed`, all check exit codes `0`, and
observed paths exactly within approved `may_touch`. The helper validates supplied evidence but
never runs commands itself.

`--blocker-json` uses exactly schema `connlab.personal-task-blocker`, version `1`:

```json
{
  "schema": "connlab.personal-task-blocker",
  "version": 1,
  "code": "VALIDATION_FAILED",
  "reason": "bounded explanation",
  "dirty_paths": ["path/to/partial-change"],
  "failed_validation": {
    "schema": "connlab.personal-task-validation",
    "version": 1,
    "status": "failed",
    "checks": [
      {"command": "exact failing command", "exit_code": 1, "summary": "observed failure"}
    ],
    "observed_paths": ["path/to/partial-change"],
    "manual_checks": [],
    "recorded_at": "RFC3339 timestamp"
  },
  "recorded_at": "RFC3339 timestamp"
}
```

Allowed blocker codes are `VALIDATION_FAILED`, `UNEXPECTED_PATHS`, `SCOPE_EXPANDED`,
`IMPLEMENTATION_FAILED`, `DIRTY_WORKTREE`, and `EXTERNAL_BLOCKER`. `reason` is always required.
`dirty_paths` is a normalized unique string array and may include out-of-scope paths specifically
so the board can fail closed and disclose them. `VALIDATION_FAILED` requires a complete nested
failed validation object; every other code requires `failed_validation:null`. Unknown fields,
unknown codes, mismatched validation status, or invalid paths return `BLOCKED_BLOCKER_INVALID`.
The blocker payload is stored unchanged in `active.blocker` except for canonical JSON formatting.

Every JSON response uses exactly schema `connlab.personal-task-result`, version `1`, with fields:

```text
schema, version, code, allowed, changed, command, task_id,
state, active_task_id, queue_position, board_sha256_before,
board_sha256_after, primary_root, reason
```

`task_id` and `queue_position` are nullable where inapplicable. Read/no-op results have equal
before/after hashes. Writers return the post-write hash only after successful re-read validation.
Exit code is `0` for `ALLOW_*`, `QUEUED_*`, and `NOOP_*`; it is `2` for `BLOCKED_*`.

Stable result codes are:

- `ALLOW_INSPECT`, `ALLOW_ACTIVATE`, `ALLOW_ACTIVATE_NEXT`, `ALLOW_APPROVE`,
  `ALLOW_IMPLEMENTATION`, `ALLOW_MARK_REVIEW`, `ALLOW_BLOCK`, `ALLOW_RESUME`, `ALLOW_CANCEL`,
  `ALLOW_CLOSE`;
- `QUEUED_NEW`, `QUEUED_EXISTING`;
- `NOOP_ALREADY_ACTIVE`, `NOOP_ALREADY_APPROVED`, `NOOP_ALREADY_BLOCKED`,
  `NOOP_ALREADY_PENDING_REVIEW`, `NOOP_ALREADY_CLOSED`, `NOOP_QUEUE_EMPTY`;
- `BLOCKED_PRIMARY_UNVERIFIED`, `BLOCKED_BOARD_HASH_MISMATCH`, `BLOCKED_SCHEMA_INVALID`,
  `BLOCKED_LOCKED`, `BLOCKED_LOCK_PATH`, `BLOCKED_STATE`, `BLOCKED_TASK_MISMATCH`,
  `BLOCKED_FIFO_ORDER`, `BLOCKED_CLASSIFICATION_INVALID`, `BLOCKED_APPROVAL_REQUIRED`,
  `BLOCKED_PLAN_REQUIRED`, `BLOCKED_VALIDATION_FAILED`, `BLOCKED_UNEXPECTED_PATHS`, `BLOCKED_WORKTREE_DIRTY`,
  `BLOCKED_APPROVED_SCOPE_INVALID`, `BLOCKED_BLOCKER_INVALID`, `BLOCKED_TRANSITION_UNCOMMITTED`,
  `BLOCKED_LEGACY_MODE_FROZEN`, `BLOCKED_WRITE_FAILED`.

`scripts/run_task.ps1 -ControlledLaneV2` and every former gate intent (`StartTask`,
`CreateWorktree`, `ImplementationDispatch`, `QuickFixPreempt`, `Reconcile`, `Resume`) return the
same structured `BLOCKED_LEGACY_MODE_FROZEN` result and perform zero writes/actions. They do not
invoke Controlled Lane V2, worktree, transition, handoff, role, or Codex-runtime code.

## 4. Minimal Board Schema

Keep one marker-delimited JSON object with:

- `schema: connlab.personal-serial-control` and `version: 1`;
- `mode: personal_serial` and `wip_limit: 1`;
- global `state: idle | running | implemented_pending_human_review`;
- nullable `active`;
- ordered `queue` and monotonic `next_enqueue_sequence`;
- bounded `last_closed` summary;
- short `retained_history` entries for every currently retained residual.

An active record contains:

- `task_id`, `summary`, and `kind: simple | planned`;
- `phase: planning | implementation | blocked | human_review`;
- nullable `scope_contract` containing exact `may_touch`, `expected_file_count`,
  `classification_reason`, `targeted_validation`, and named forbidden-category checks;
- `plan_ref` and `approval_ref` for planned implementation;
- `activation_parent_sha`, timestamps, nullable `blocker`, and nullable validation result.

For `kind=simple`, `scope_contract` is required from initial submit; `expected_file_count` must be
1–3, equal `may_touch` length, include
`docs/task_board.md`, and every forbidden check must be explicitly false:

- API contract;
- database;
- schema or migration;
- persistence;
- authority;
- public-drive workflow;
- business-rule semantics;
- destructive action;
- remote/publication/service/external mutation.

For `kind=planned`, `scope_contract`, `plan_ref`, and `approval_ref` are null during queue/planning;
the approved transition atomically makes all three non-null before phase `implementation`. The
helper validates complete declarations and observed paths. It does not claim to infer semantic
safety from a Task ID; the current conversation supplies the classification from repository
evidence and stops on ambiguity.

Queue records contain task ID, summary, requested kind, enqueue sequence, and timestamp. A simple
queue record additionally contains its complete immutable `scope_contract`; a planned queue record
contains `scope_contract:null`. Repeated submission of the same active or queued ID is idempotent.
FIFO order cannot be rewritten by ordinary task commands.

### 4.1 Exact Retained-History Migration Table

The activation bootstrap must create exactly these four `retained_history` records. It may shorten
no listed field and may add no inferred status, owner, or disposition.

| Task | Status | Owner | Disposition | Evidence | Git locator |
|---|---|---|---|---|---|
| `TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF` | `cancelled` | `User / manual governance` | `retain clean Task-A lane and all evidence; no automatic adoption, merge, rewrite, deletion, or role dispatch` | `docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_reviewer.md@85e71dfa212c57c26527fad42eaf00a83b19c935#f1ca9341149d567958d837c18932e25ddee1ad47189266d0de73a03540e6de3a` | branch `lane/task-governance-active-context-deterministic-transition-and-event-handoff`; worktree `D:\PythonProject\connlab-worktrees\task-governance-active-context-deterministic-transition-and-event-handoff`; HEAD `85e71dfa212c57c26527fad42eaf00a83b19c935` |
| `TASK_GOVERNANCE_WIP1_AND_PROPORTIONATE_QUICK_FIX_FAST_PATH` | `retained` | `permanent Orchestrator governance` | `retain clean integrated lane branch/worktree until separately authorized safe maintenance retirement` | `docs/lane_evidence/TASK_GOVERNANCE_WIP1_AND_PROPORTIONATE_QUICK_FIX_FAST_PATH_integrator.md` | branch `lane/task-governance-wip1-and-proportionate-quick-fix-fast-path`; worktree `D:\PythonProject\connlab-worktrees\task-governance-wip1-and-proportionate-quick-fix-fast-path`; HEAD `600bbf2d8d6b7884fed6a3af4e46f56cce3fe3a3` |
| `TASK_368D_PDF_QUALIFICATION_MATRIX_MERGED_CELL_ALIGNMENT_QUICK_FIX` | `retained` | `permanent Orchestrator governance` | `retain clean integrated lane branch/worktree until separately authorized safe maintenance retirement` | `docs/lane_evidence/TASK_368D_pdf-qualification-matrix-merged-cell-alignment_integrator.md` | branch `lane/task-368d-pdf-qualification-matrix-merged-cell-alignment-quick-fix`; worktree `D:\PythonProject\connlab-worktrees\task-368d-pdf-qualification-matrix-merged-cell-alignment-quick-fix`; HEAD `45f345f49c43eece139245b00048c74e8c83f73b` |
| `TASK_368E_MATRIX_IMPORT_OPTIONAL_STANDARD_VERSION_FALLBACK_AND_COPY_CLARITY` | `retained` | `permanent Orchestrator governance` | `retain clean integrated lane branch/worktree until separately authorized safe maintenance retirement` | `docs/lane_evidence/TASK_368E_matrix-import-optional-standard-version-fallback-and-copy-clarity_integrator.md` | branch `lane/task-368e-matrix-import-optional-standard-version-fallback-and-copy-clarity`; worktree `D:\PythonProject\connlab-worktrees\task-368e-matrix-import-optional-standard-version-fallback-and-copy-clarity`; HEAD `c9a61bcb701178c1042d99ca8011d138e0420330` |

For every row, `task_id`, `status`, `owner`, `disposition`, `evidence`, `branch`, `worktree`, and
`head` are required schema fields. Activation must compare each registered worktree's branch, HEAD,
and clean status before writing. Any mismatch blocks migration; no row is silently omitted or
reclassified.

## 5. State And Commit Protocol

### 5.1 New simple task

1. Read-only inspect and classification.
2. `submit` writes `running/implementation` or queues the task atomically.
3. If activated, exact-stage the board and create an activation commit before any implementation
   file is edited.
4. Implement only declared paths and run targeted validation.
5. On pass, `mark-review` writes pending-human-review state; exact-stage payload plus board and
   create the implementation commit.
6. Stop for human review.

When the task was previously queued, the explicit execute/continue command calls `activate-next`
instead of `submit`. The helper requires global idle state, non-empty queue, and exact
`--task-id == queue[0].task_id`; it atomically removes only that head and activates its stored
request. An empty queue returns `NOOP_QUEUE_EMPTY`; a non-head ID returns
`BLOCKED_FIFO_ORDER`. `submit` for an existing queued ID remains zero-write `QUEUED_EXISTING`.

### 5.2 New planned task

Under the installed personal workflow, minimal planned `submit` records only task identity/summary
and `running/planning` with `scope_contract:null`, so planning also occupies the single active slot.
The short plan is committed and reviewed. `approve --approved-request-json` atomically freezes the
complete approved paths, file count, classification, validation, forbidden-category results,
plan ref, and explicit approval before implementation. Immediately after `approve`, the current conversation
must independently inspect the new board hash, exact-stage only `docs/task_board.md`, create a
local approval commit, and verify primary clean. No implementation edit begins until that approval
commit is current HEAD. Implementation then follows the same validation, pending-review, and
local-commit path.

This governance migration is a one-time bootstrap exception because its plan predates the new
helper. After User approval it must create two primary commits:

1. activation commit: migrate the board and record this task `running/implementation` before any
   rule, helper, script, or test implementation edit;
2. implementation commit: include approved implementation paths, passed validation summary, and
   board state `implemented_pending_human_review`.

The activation commit is not a role dispatch or implementation acceptance.

### 5.3 Failure, dirty worktree, and cancellation

- A validation failure, unexpected path, expanded scope, or partial implementation remains
  `running` and uses `block` to record the blocker and observed dirty paths.
- `mark-review`, `close`, and promotion of a queued task are forbidden while blocked, dirty,
  validation-failed, or out of scope.
- After `block` atomically edits only the board, the current conversation may exact-stage and commit
  only `docs/task_board.md` while task files remain dirty, so all other conversations fail closed
  without hiding partial work. The helper itself performs no Git write.
- Only explicit User direction may choose: continue; preserve an exact checkpoint commit and keep
  working; or cancel after separately resolving the modifications.
- `resume` never alters files. `cancel` requires a clean worktree and records the User-approved
  disposition; it never restores, discards, stashes, or cleans.
- `关闭` requires pending-human-review state, passed validation, and clean primary. It writes a
  closeout board change and requires a separate exact local board commit. It releases the slot but
  does not auto-start the queue head.

## 6. Entry Points

- `scripts/run_task.ps1` becomes a thin local adapter to `connlab_personal_task.py submit` with
  parameters `-Task`, `-RequestJson`, `-ExpectedBoardSha256`, `-Preview`, `-Json`, and the retained
  compatibility switch `-ControlledLaneV2`, plus `-ActivateNext` for the explicit FIFO-head path.
  Normal new-task execution requires the first three parameters; `-ActivateNext` requires Task and
  expected hash but reuses the stored queue request; `-Preview` performs zero-write
  inspect/classification only. It returns the helper's unchanged
  result envelope and invokes no Codex runtime, old role, V2 path, worktree, or external process
  beyond Python/helper execution. `-ControlledLaneV2` always returns
  `BLOCKED_LEGACY_MODE_FROZEN` with exit code 2.
- `scripts/connlab_execution_gate.ps1` becomes a thin read-only adapter with parameters `-Intent`,
  `-TaskId`, `-RepositoryRoot`, and `-Json`. New intents are `Inspect`, `Implementation`, and
  `Close`. The six former intents remain accepted only to return the frozen structured response;
  they never call legacy code. The adapter preserves the helper result fields/codes verbatim.
- Direct natural-language execution in the current conversation calls the helper itself.
- Old lane, transition, handoff, role-registry, parallel, and Controlled Lane V2 materials remain
  frozen historical references and are not daily entry points.

## 7. Exact Implementation Allowlist

Only these files may be added or modified after approval.

Core authority and policy:

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/project_management/TASK_REVIEW_CHECKLIST.md`

Frozen legacy labeling/references:

- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `.agents/skills/connlab-planner/SKILL.md`

Entry points:

- `scripts/connlab_personal_task.py` (new)
- `scripts/run_task.ps1`
- `scripts/connlab_execution_gate.ps1`
- `scripts/connlab_active_context.py` (read-only `inspect` compatibility for
  `connlab.personal-serial-control` only)

Governance tests:

- `tests/unit/test_connlab_personal_serial_workflow.py` (new)
- `tests/unit/test_connlab_execution_gate_script.py`
- `tests/integration/test_connlab_execution_gate_recovery.py`
- `tests/unit/test_execution_wip_and_quick_fix_governance.py`
- `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py`
- `tests/unit/test_connlab_lane_worktree_script.py`
- `tests/unit/test_connlab_active_context_governance.py`

Task-owned planning/status:

- `tasks/TASK_GOVERNANCE_PERSONAL_SERIAL_WORKFLOW_SIMPLIFICATION.md`
- `docs/task_governance_personal_serial_workflow_simplification_plan.md`

Test commands may be adjusted to obtain stronger evidence. Adding or modifying any unlisted file
path requires stopping and obtaining new explicit User approval.

## 8. Must Not Touch

- all product/backend/frontend/API/domain/database/schema/migration/Office/LTR/Matrix/Fee/report/
  release/runtime feature code and tests;
- all archive, maintenance, rollback, generation/index, reconstruction, and mixed-EOL behavior in
  `scripts/connlab_active_context.py`; only the read-only personal-schema `inspect` path may change;
- `docs/archive/task_board_history/**`, including generation-1 and `index.v1.jsonl`;
- every Task-A task/plan/evidence/transition/attestation file, retained lane/worktree, branch, and
  commit;
- the external `connlab-governance-migration` repository;
- Controlled Lane V2 helper, registry, heartbeat, pilot/corrective packages, skill, and tests;
- existing transition/handoff helpers and their tests;
- all other tasks, plans, evidence, retained worktrees, artifacts, real data, remotes, and services;
- deletion, restoration, merge, adoption, retirement, reconciliation, or cleanup of legacy state.

## 9. Implementation Sequence After Approval

1. Recheck clean primary at the approved revision and snapshot protected hashes/worktree facts.
2. Apply the one-time exact bootstrap board transition, update only this task/plan approval status,
   validate it, exact-stage those three paths, and create the activation commit before any helper,
   rule, entry-point, or test implementation edit.
3. Add the personal schema/helper failing tests.
4. Implement the complete atomic helper and its state transitions.
5. Simplify the two PowerShell entry points.
6. Replace daily multi-role rules with the personal policy; mark old routing documents/skills
   frozen without deleting them.
7. Update only allowlisted governance tests for the new contract.
8. Run the exact behavioral, PowerShell, history, protected-state, and diff checks.
9. On success, call `mark-review`, exact-stage the allowlist, and create the implementation commit.

If implementation reaches a committed `SCOPE_EXPANDED` blocker, a new explicit User approval may
rebind only a strict path superset through `approve`. That transition keeps the blocker and must be
committed separately; `resume` is a second explicit transition. For the current correction the
only added path is `scripts/connlab_active_context.py` and its behavior boundary is the read-only
`inspect` compatibility described above.
10. Verify clean primary and stop at `implemented_pending_human_review`; no push and no queued start.

If any step needs an unlisted path, destructive action, Task-A mutation, archive/index write, or
scope/semantic decision, stop for User approval.

## 10. Validation And Acceptance

Behavioral coverage must prove:

- idle submit activates exactly one task; occupied submit idempotently queues in FIFO order;
- after close, only `activate-next` with the exact FIFO-head ID dequeues/activates; empty and
  non-head requests are stable no-op/block results;
- activation board state is committed before implementation writes;
- pending human review and blocked/dirty states continue to occupy the slot;
- simple records require 1–3 total paths including tests and board, explicit classification,
  targeted validation, and all forbidden checks false;
- planned intake accepts exactly task ID, summary, and kind; queue/activate-next retain null scope;
- planned implementation requires approved-request JSON, committed plan ref, and explicit approval
  ref, and atomically replaces null scope with the complete approved contract;
- planned approval remains blocked from implementation until the approval board transition is a
  clean local commit and `check --intent Implementation` proves committed board equality;
- failed validation cannot mark review, close, cancel dirty work, or release the slot;
- close requires explicit User direction, passed validation, clean primary, and does not auto-start;
- no path dispatches old roles or creates a branch/worktree;
- malformed schema, hash race, duplicate queue ID/sequence, and lock conflict fail closed;
- blocker JSON requires a known code/reason/dirty-path shape and correctly typed nullable failed
  validation; unknown fields or overloaded validation payloads fail closed;
- injected pre-replace failures preserve prior bytes; replacement outcomes are verified as exactly
  prior bytes or the complete rendered bytes, never a partial board;
- helper source contains no stage/commit/push invocation; lock resolution is confined to the
  ignored primary `tmp/connlab_personal_task.lock` path;
- the migrated retained-history array exactly equals the four frozen rows, including branch,
  worktree, HEAD, owner, disposition, and evidence.

History compatibility must prove without modifying history files:

- generation-1 archive remains exactly 798128 bytes, SHA-256
  `3e57b913098e565de3fee8f4a0ffdff597e3d7fdfec5232fe63027298f1a2507`, Git blob
  `972b1c2386145114cb3daa35037913d709bb5180`;
- `index.v1.jsonl` remains exactly 6787 bytes, SHA-256
  `cc732a742f60914e8c922d9f91f05d93fcd3bf4ec0f3483b1248a9e64c094aae`, Git blob
  `77f43609e1b8ecde0e058c5e0d24d4e554a2f895`;
- no archive/index generation is rebuilt, appended, or rewritten;
- generation-1 direct `prove-rollback` returning `BLOCKED_ROLLBACK_CHAIN` after the later legitimate
  cancelled-board update is expected protection, not a failure;
- active-context `inspect` and the unchanged mixed-EOL/archive regression suite still pass.

Planned commands include:

```powershell
py -m pytest tests\unit\test_connlab_personal_serial_workflow.py -q
py -m pytest tests\unit\test_connlab_execution_gate_script.py -q
py -m pytest tests\integration\test_connlab_execution_gate_recovery.py -q
py -m pytest tests\unit\test_execution_wip_and_quick_fix_governance.py -q
py -m pytest tests\unit\test_task_scoped_role_thread_lifecycle_governance.py -q
py -m pytest tests\unit\test_connlab_lane_worktree_script.py -q
py -m pytest tests\unit\test_connlab_active_context_governance.py -q
py -m pytest tests\unit\test_connlab_active_context.py -q
powershell -NoProfile -Command "$null = [ScriptBlock]::Create((Get-Content 'scripts\connlab_execution_gate.ps1' -Raw -Encoding UTF8))"
powershell -NoProfile -Command "$null = [ScriptBlock]::Create((Get-Content 'scripts\run_task.ps1' -Raw -Encoding UTF8))"
py scripts\connlab_active_context.py inspect --repo-root . --json
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\connlab_execution_gate.ps1 -Intent Inspect -Json
git diff --check
git status --short
```

Before/after SHA-256, Git blob, branch/HEAD/status, Task-A retained-lane HEAD/status, external-repo
HEAD/status, and archive/index facts must match their protected baseline except for the approved
primary commits.

## 11. Rollback

The activation commit is the migration boundary. Before any later task uses the personal schema,
rollback requires explicit User authorization and exact reverts of the implementation commit and
activation commit in reverse order. Once later tasks depend on the schema, rollback becomes a new
explicit migration decision.

No reset, restore, archive rewrite, Task-A mutation, branch/worktree cleanup, or remote operation is
part of rollback.

## 12. Stop Point

Implementation is complete only when:

- the activation and implementation commits both exist on primary in order;
- only allowlisted paths changed;
- all required validation and history/protected-state checks pass;
- primary is clean at the implementation commit;
- board records this task as `implemented_pending_human_review` with no blocker;
- no old role/worktree/V2 dispatch occurred, no push occurred, and no queue item started.

Then stop for User review. Only `关闭` may create the later closeout board commit and release the
slot. The first review run passed 56 focused tests but missed the corrective cases listed above;
that result is retained as historical evidence rather than treated as final acceptance. Corrective
validation adds explicit FIFO-bypass, `ActivateNext/-Json`, nested-authority, incompatible-argument,
approval-evidence, and post-parameter-binding repository-root tests; the final validation result is
62 focused tests passing.
