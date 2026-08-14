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

Recovery reconstructs the durable active task and host from board, Git, and evidence before any action,
reuses the recorded host, and never duplicates activation. Unprovable identity fails closed with an exact
typed blocker. Browser smoke is required only for a user-visible UI change; use documented load state or
deterministic selectors and never unsupported `networkidle` probing.
