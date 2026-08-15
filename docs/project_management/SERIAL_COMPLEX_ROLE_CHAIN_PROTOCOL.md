# ConnLab Serial Complex Role-Chain Protocol

Status: `NORMATIVE_V2`

The personal serial complex workflow is active. A normal complex task has exactly three User interactions:

1. submit the requirement;
2. approve the Planner plan;
3. inspect the completed result and say `关闭`.

After plan approval, Developer -> Reviewer -> QA -> Integrator proceeds automatically. The runtime
returns to the User only for an approved-scope change, a destructive action, or an unresolved
blocker.

## Authority and WIP

- The version-2 `connlab.personal-serial-control` block in `docs/task_board.md` is the sole machine
  authority.
- `scripts/connlab_personal_task.py` is the sole board writer. Every write uses expected board
  SHA-256, the ignored lock, atomic replacement and readback.
- WIP is one from activation through User close. Submit reads and parses the board, then checks
  occupancy before repository Git verification, worktree inspection, writer-lock acquisition, JSON
  parsing or classification. While occupied it returns `BLOCKED_ACTIVE_TASK_RUNNING`, changes no
  board byte and stores no request. After close, the User submits the next requirement again.
- Conversation memory is not authority. Board, Git, task, plan and evidence must reconstruct the
  next legal action.
- No helper stages, commits, pushes, messages, restores, stashes, deletes branches or force-removes
  worktrees.

## Daily flow

```text
requirement -> classify/submit
  simple -> direct primary implementation -> human review
  complex/needs_discovery -> Planner -> User approval
    -> one task host -> Developer -> Reviewer -> QA -> Integrator
    -> verified primary integration -> human review
User 关闭 -> retained closeout verification -> idle
```

Planner is read-only and runs before host creation. Approval binds the exact plan, `may_touch` and
validation contract in a committed board transition. One task branch/worktree host is then shared
sequentially by Developer, Reviewer, QA and Integrator. Reviewer or QA findings return automatically
to Developer within approved scope. Integrator binds the accepted subject and evidence before the
runtime performs the approved non-conflicting local integration transaction.

Primary is the sole execution-evidence owner. After the committed Planner-evidence prefix, every
execution callback uses exactly this primary sequence:

```text
B_r  begin-role board-only commit
-> A_r  record-invocation board-only commit
-> E_r  one evidence-only commit at docs/lane_evidence/<TASK_ID>_<role>.md
-> C_r  consume-callback board-only commit
```

`A_r`, `E_r`, and the working primary board have identical authority bytes. `E_r` is single-parent,
its parent is the matching durable invocation state, and it changes exactly the fixed role evidence
path. The shared task branch/worktree remains clean and fixed at the exact callback subject; roles run
against that host but do not write evidence there. Fix loops append the same four-step sequence in
actual invocation order, without a fixed evidence count or route-length allowlist.

Planner `ready` enters `awaiting_user_approval`; User approval enters `development` before host
creation. A complex blocker resumes only to its validated `resume_phase`. User `Close` records
`request-close` and keeps WIP occupied while the Orchestrator automatically records the retained
closeout and calls `finalize-close`; only that final transition releases active. Simple-task close
retains its direct validated close behavior.

The public complex writer commands are `begin-role`, `record-invocation`, `consume-callback`,
`begin-host`, `record-host`, `record-integration`, `request-close`, `record-closeout` and
`finalize-close`. Callback schemas, blocker policies and phase order are closed tables in
`scripts/connlab_serial_complex.py`; unknown combinations fail closed. There is no public cutover,
manifest, permission-receipt or lifecycle-cleanup command family.

`scripts/run_task.ps1` exposes only `Submit`, `Approve` and `Close`. The helper's legacy
`activate-next` parser token remains only for version-1 rollback compatibility; a version-2 board
always returns `BLOCKED_LEGACY_MODE_FROZEN` with zero writes.

Controlled Lane V2 is retained historical audit material, not an alternate daily entry. Its adapter
must fail closed before consuming legacy request or registry inputs while this version-2 board is
authoritative.

The common `block` command is also the legal non-callback failure writer for a v2 complex task. It
accepts only `connlab.serial-task-blocker` version 1, enforces the frozen code policy and requires the
blocker's `stage` to equal the active phase. `record-integration` writes human review only after the
integration-ready board is committed and Git independently proves the current primary merge commit,
its parents/tree, the exact QA-accepted task branch/worktree HEAD and clean state, and every accepted
evidence reference's committed byte hash.

Before that transition, repository verification treats Planner evidence as the pre-host prefix and
dynamically pairs each later evidence ref with its durable Developer/Reviewer/QA/Integrator invocation.
It revalidates fixed path, exact identity/model headers, frozen committed-Plan route, raw SHA-256,
single-parent evidence-only topology and ordered primary ancestry. The merge first parent is the final
callback board commit and the second parent is the unchanged task subject; no execution evidence commit
may be an ancestor of that subject. Code-mixed evidence, unknown commits, dirty or moved worktrees, and
identity/order/route drift fail closed before board mutation. No reset, restore, rebase, cherry-pick or
branch-pointer repair is part of normal execution or recovery.

## Stop and recovery

Failures keep the active slot and record a typed blocker with exact Git/evidence facts. Automatic
routing stops for scope or behavior change, destructive work, conflict, dirty/divergent state that
the approved transaction cannot resolve, ambiguous identity/evidence, or a repeated unresolved
failure. It never silently discards or cleans.

User `关闭` moves a complex task through retained closeout verification. Clean integrated task/thread/
worktree/branch/HEAD/evidence references remain retained; archive and retirement are not daily
gates. Close ends at idle; there is no queue activation action.

The first ordinary complex task is the monitored first real run, not a pilot or another governance
task. Repository-level validation proves the workflow contract but does not claim that the native
role chain has already passed end to end.

## Frozen user entry contracts

All User entry uses `scripts/run_task.ps1` only. Do not directly invoke Python with request JSON, retry
schemas, or copy a payload across actions. Submit uses
`-Action Submit -RequestJson <single JSON object>` with exactly:

```text
schema, version, task_id, summary, root_cause_clear, expected_result_clear,
may_touch, targeted_validation, requires_independent_review, forbidden_categories
```

Submit requires `schema=connlab.serial-task-request` and `version=1`; `kind` is forbidden. Its
`forbidden_categories` has exactly ten keys: `api_contract`, `database`, `schema_or_migration`,
`persistence`, `authority`, `public_drive_workflow`, `business_rule_semantics`, `destructive_action`,
`external_mutation`, and `push_or_release`. Missing decision facts may yield discovery only under this
contract; an unknown key is a terminal zero-write classification error.

Approve uses `-Action Approve -ApprovedRequestJson <single JSON object> -PlanRef <committed Plan ref>
-ApprovalRef <explicit User approval>` with exactly:

```text
schema, version, task_id, summary, kind, may_touch, expected_file_count,
classification_reason, targeted_validation, forbidden_categories
```

Approve requires `schema=connlab.personal-task-approved-request`, `version=1`, and `kind=planned`.
Its `forbidden_categories` has exactly the first nine Submit category keys; `push_or_release` is
forbidden. Close deliberately has no JSON payload and is exactly
`-Action Close -DecisionRef <non-empty explicit User decision>`; missing `DecisionRef` fails before the
writer runs.

## Routing, evidence, and bounded checks

The permanent Orchestrator and direct simple task remain `gpt-5.6-sol / medium`. Simple work has the
shortest path: Submit, one preflight and activation commit, direct primary implementation, one bounded
validation, human inspection, and Close; it has no additional Task/Plan, role hop, branch, worktree,
intermediate `继续`, or implicit model switching. Every complex `spawn_agent` dispatch explicitly passes
both `model` and `reasoning_effort`; inherited/default routing is forbidden.

### Simple-fast execution optimization

`simple-fast` is an execution optimization inside an already classified `simple` request, not a task
kind, state, role, or approval. It does not alter the writer schema, board lifecycle, WIP=1, model route,
human review, Close contract, or the three-path simple limit.

Use it only when all of these facts are mechanically true before implementation:

- the request is unambiguous and changes one existing default value, literal, or fixed local mapping;
- the complete scope is one implementation path, at most one existing test path, and the board;
- the expected semantic diff is at most 20 lines and adds no file, dependency, import, type, state,
  abstraction, component seam, build configuration, or generated artifact;
- copy, visual design, layout, styling, interaction structure, API, database, schema/migration,
  persistence, authority, public-drive workflow, business semantics, destructive behavior, and
  external mutation are unchanged; and
- one targeted test command at an existing public seam can prove the requested result and its direct
  toggle or fallback behavior when applicable.

The execution sequence is fixed:

1. Read the board control block through `inspect` and its `active_snapshot` / `next_action`, then read
   only the exact implementation path, the optional existing test path, and locally applicable rules.
   Do not reread board history, unrelated protocols, architecture documents, or product context.
2. Preserve the normal activation commit. Use one `$tdd` vertical slice when observable behavior
   changes: one failing assertion, the minimal implementation, then the same targeted test command.
3. Self-review the exact diff. Eligible `simple-fast` does not load `$impeccable`, `$codebase-design`,
   `$code-review`, `$diagnosing-bugs`, or `$playwright` because its predicates exclude their triggers.
4. After the targeted test passes, run `git diff --check`, make the implementation commit, perform the
   normal human-review board transition, and stop. By default it does not run a production build or
   browser smoke. Add one only when the targeted test cannot prove the changed observable behavior or
   the User explicitly requested it; it must not probe, install, or download Playwright.

The expected elapsed time from committed activation to human review is one to three minutes. If it has
not completed, report the concrete delay once at five minutes and continue only the still-required
step; elapsed time never relaxes correctness or safety. If any predicate becomes false, stop the fast
sequence and fall back to ordinary `simple` when the request remains simple, or fail closed for a new
planned/complex submission when the simple classification no longer holds. Never stretch the fast
path by adding validation, documentation, skills, files, or abstractions merely to keep its label.

| Role | Default route |
| --- | --- |
| Developer | `gpt-5.6-terra / medium / default_complex` |
| Reviewer | `gpt-5.6-terra / medium / default_complex` |
| QA | `gpt-5.6-terra / low / qa_bounded_low` only for bounded documentation/copy-only work; otherwise `gpt-5.6-terra / medium / default_complex` |
| Integrator | `gpt-5.6-terra / medium / default_complex` |

QA is low only when all frozen risk flags are false, no operational skill/protocol/runtime/product
behavior changes, no blocker/fix loop occurred, and validation is fully enumerated. Every other
non-high-risk task uses Terra medium. The affected role escalates to `gpt-5.6-sol / medium` for API
contract; database/schema/migration/persistence; authority/public-drive/business semantics;
cross-frontend/backend or multi-layer work; unexplained repeated test failure; integration conflict; or
security-sensitive change. High effort is only for migration, authority, or hard-to-diagnose failure.
Luna is not used.

Developer, Reviewer, QA, and Integrator evidence each has exactly one header value for `MODEL`,
`REASONING_EFFORT`, and `MODEL_ROUTE_REASON` (`default_complex`, `qa_bounded_low`, or
`risk:<frozen-category>`). Reviewer reconciles dispatch to subject evidence; QA verifies the full route
and forbidden-Luna assertion. Integrator evidence and the final User summary include an
`ACTUAL_MODEL_ROUTING` table: role, model, effort, reason, evidence ref. A missing or mismatched field
blocks the gate.

Supporting engineering skills are role-local methods, not additional workflow roles. Developer uses
`$tdd` for substantive behavior and adds `$diagnosing-bugs` only for hard, repeated, flaky, or
unexplained software failures. Reviewer uses `$code-review`. Planner/Developer use `$codebase-design`
only for approved structural work. Planner/Orchestrator use `$grilling` only for material product
ambiguity and ask at most three blocking questions. UI work loads `$impeccable`; UI QA uses
`$playwright` only when browser-visible behavior changed. Supporting skills never change approved
scope, authority, routing, or evidence ownership.

## Validation efficiency and exact-subject evidence

Developer completes implementation and self-review before the final complete approved test matrix.
The matrix result binds the final exact subject. Any later implementation or test byte change
invalidates the old result; rerun every affected validation on the new exact subject before writing
Developer evidence. Evidence must never cite tests run before the final code/test change.

Reviewer inspects the exact diff, requirement fit, boundaries, safety, regression risk, and Developer
evidence. Reviewer runs only tests directly targeted at changed risk, a finding, or a critical negative
case; it does not unconditionally repeat Developer's complete matrix. After a bounded finding fix,
Reviewer confirms that finding with targeted checks. `$code-review` is the existing Reviewer's method,
not a second review workflow. QA owns the final independent complete-matrix gate.

QA runs the complete approved matrix once on a clean, exact reviewed subject. QA is the only default
independent repeat of the complete approved matrix in a normal complex task. QA must not mutate board,
phase, validation, or fixture state to manufacture a passing precondition.

Integrator does not repeat the complete pytest matrix. It verifies only exact subject, approved scope,
evidence topology and raw-byte digests, task/primary HEAD, Git parents/tree, clean worktrees, and actual
integration facts. On a deterministically proved blocker, stop remaining unrelated checks, emit concise
typed blocker evidence, and do not merge or call `record-integration`. Only a blocker-free gate proceeds
to the already approved non-conflicting local integration.

For sibling worktrees, disposable Git repositories, and pytest temporary roots that are already known
to require additional permission, request the complete command's required permission boundary first.
Do not intentionally run a setup-only permission probe and then repeat the same command. Permission,
authority, dirty, identity, or partial-state failures are not mechanical retries. Only argv, encoding,
JSON compression, or equivalent transport errors may be corrected and retried once in the same turn,
after proving board, HEAD, worktree registration, and relevant file bytes are unchanged.

Obtain primary HEAD/approved base, task branch/worktree/HEAD, Plan path/commit/raw SHA-256, evidence
path/commit/raw SHA-256, and pending action/attempt/role/thread/agent identity mechanically from board,
Git, and original file bytes. Never write a truncated SHA, manually complete a digest, or assemble an
unescaped ad-hoc PowerShell command for authority writes.

After interruption or reconnection, reconstruct from board, Git, worktree, and committed evidence.
Do not repeat a durable transition. Reuse an identity-exact host, and do not duplicate a branch,
worktree, role invocation, or evidence commit. The User may resume with: `继续当前活动任务，从
board/Git/evidence 恢复；不得重复已完成步骤`.

Evidence contains only required identity, subject, model route, findings, validation conclusions, and
exact Git/evidence facts. Do not paste the complete Plan, complete test output, or large board content.
The final summary reports approximate elapsed time for planning, host setup, Developer, Reviewer, QA,
Integrator, integration, and tests, plus automatic retry count and reason, using existing commit, turn,
and test timing only. Do not add telemetry, a database, or a monitoring framework.

## Phase 2 runtime recovery

Phase 2 extends the existing V2 production writer; it does not create another authority or task tier.

- For a same-scope bounded fix, use `reenter-development` once. Reviewer/QA reuse the existing explicit
  `approval_ref` without a fourth routine User interaction; `INTEGRATION_BLOCKED` requires a new explicit
  User decision because it is an unresolved integration blocker. The writer
  mechanically verifies the committed clean primary and the recorded task worktree branch, HEAD and
  cleanliness, then atomically performs `REVIEWER_BLOCKED / QA_BLOCKED / INTEGRATION_BLOCKED ->
  development`. It preserves Plan, scope, host and identity, archives the typed blocker in
  `blocker_history`, increments Developer attempt, clears the current blocker, and creates exactly one
  pending Developer action. Missing approval, scope/subject/host drift, dirty state, or an existing
  pending action fails closed with zero board write. Planner and Approve are not replayed.
- After explicit exact-scope amendment approval, the existing `approve` writer performs one atomic
  amendment transition. It records the old `SCOPE_EXPANDED` blocker in `blocker_history`, synchronizes
  `scope_contract`, `approved_code_paths`, `plan_ref`, and `approval_ref`, clears the blocker, and resumes
  `development`. The next step is the normal Developer begin; Planner lifecycle and a second identical
  Approve call are forbidden.
- Every writer result and `inspect` expose compact `active_snapshot` and `next_action`. Recovery reads
  these board-derived facts first and follows the pending durable action directly; it does not reread
  the complete Task, Plan, board prose, and protocol on every turn.
- Build native-action JSON with `scripts/connlab_serial_payload.py native-action`. The builder reads the
  active board, increments the durable attempt, hashes the raw prompt bytes, and derives the action ID;
  use its `git-reference` command for Plan/evidence path, commit, and raw byte SHA-256. Do not copy SHA
  values or assemble escaped PowerShell JSON manually.
- A context without `blocker_history` remains readable for interruption recovery. The first Phase 2
  resolution creates the history field atomically; newly activated complex tasks initialize it empty.

Recovery reconstructs the durable active task and host from board, Git, and evidence before any action,
reuses the recorded host, and never duplicates activation. Unprovable identity fails closed with an exact
typed blocker. Browser smoke is required only for a user-visible UI change; use documented load state or
deterministic selectors and never unsupported `networkidle` probing.
