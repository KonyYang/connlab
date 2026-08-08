---
name: connlab-lane-orchestrator
description: Run ConnLab's active personal-serial complex workflow from plan through automatic Developer, Reviewer, QA, and Integrator handoffs.
---

# ConnLab Personal Serial Orchestrator

Status: active version-2 runtime.

Use this skill when the User submits, approves, resumes, inspects or closes a ConnLab complex task.
Read `AGENTS.md`, `docs/task_board.md`, the active Task/Plan and relevant evidence first. The board's
version-2 control block and Git facts override conversation memory.

## User contract

A normal complex task has only three User interactions:

1. requirement submission;
2. Planner-plan approval;
3. completed-result inspection and `关闭`.

Do not request routine approvals for host creation, Developer -> Reviewer -> QA -> Integrator, an approved
bounded fix, non-conflicting local integration, or retained closeout. Return to the User only for a
scope/behavior/authority change, a destructive action, or an unresolved blocker.

## Event loop

Perform one durable state transition at a time with `scripts/connlab_personal_task.py`, using the
fresh expected board SHA-256. Exact-stage and locally commit each authority transition before the
next write-capable action. Never use chat text as a substitute for board state.

```text
idle -> submit/classify
planning -> fresh read-only Planner -> awaiting_user_approval
User approval commit -> create one task branch/worktree host
development -> Developer
review -> Reviewer
qa -> QA
integration -> Integrator -> verified primary integration
human_review -> User
User 关闭 -> retained closeout -> idle
```

Planner runs before the host and cannot write. After approval, Developer, Reviewer, QA and Integrator
run sequentially in the same isolated task host. Spawn only the role required by the current durable
phase, record its native action and returned identity, wait for its exact callback, validate the
subject/evidence, then consume it. Reviewer or QA blocking findings route back to Developer without
new approval when the fix remains inside approved scope.

## Canonical user entry payloads

Use only `scripts/run_task.ps1`; never construct request JSON for a direct Python entry, probe legacy
schemas, or retry another schema after a validation error. Submit is exactly
`-Action Submit -RequestJson <single JSON object>` with these ten keys:

```text
schema, version, task_id, summary, root_cause_clear, expected_result_clear,
may_touch, targeted_validation, requires_independent_review, forbidden_categories
```

Its identity is `connlab.serial-task-request` version `1`; `kind` is forbidden. Its
`forbidden_categories` has exactly ten keys: `api_contract`, `database`,
`schema_or_migration`, `persistence`, `authority`, `public_drive_workflow`,
`business_rule_semantics`, `destructive_action`, `external_mutation`, and `push_or_release`.
Missing decision facts may classify as discovery only under that schema. An unknown field is a terminal,
zero-write classification error, not a signal to copy or retry an alternate payload.

Approve is separately `-Action Approve -ApprovedRequestJson <single JSON object> -PlanRef <committed
Plan ref> -ApprovalRef <explicit User approval>` with exactly these nine top-level decision keys plus
identity: `schema`, `version`, `task_id`, `summary`, `kind`, `may_touch`, `expected_file_count`,
`classification_reason`, `targeted_validation`, and `forbidden_categories`. It requires
`schema=connlab.personal-task-approved-request`, `version=1`, and `kind=planned`. Its forbidden map has
only the first nine Submit category keys: `push_or_release` is explicitly forbidden. Do not copy Submit
fields into Approve.

Close has no JSON payload: use only `-Action Close -DecisionRef <non-empty explicit User decision>`.
Do not invent a close schema; a missing `DecisionRef` fails before the writer runs.

## Model routing and audit

The permanent Orchestrator and direct simple task stay `gpt-5.6-sol / medium`; the shortest simple path
is Submit, one preflight and activation commit, direct primary implementation, one bounded validation,
then human inspection and Close. It adds no Task/Plan, role agent, branch, worktree, intermediate
`继续`, or model-switching hop. Complex role dispatches must explicitly pass both `model` and
`reasoning_effort` to `spawn_agent`; inherited/default selection is forbidden.

| Role | Default model | Effort | Reason |
| --- | --- | --- | --- |
| Developer | `gpt-5.6-terra` | medium | `default_complex` |
| Reviewer | `gpt-5.6-terra` | medium | `default_complex` |
| QA | `gpt-5.6-terra` | low only for bounded documentation/copy-only work; otherwise medium | `qa_bounded_low` or `default_complex` |
| Integrator | `gpt-5.6-terra` | medium | `default_complex` |

QA uses low only when all frozen risk flags are false, no operational skill/protocol/runtime/product
behavior changes, no blocker/fix loop, and validation is fully enumerated; every other non-high-risk
case is Terra medium. The affected role escalates to `gpt-5.6-sol / medium` for API contract;
database/schema/migration/persistence; authority/public-drive/business semantics; cross-frontend/backend
or multi-layer work; unexplained repeated test failure; integration conflict; or security-sensitive
change. High effort is limited to migration, authority, or a hard-to-diagnose failure. Luna is not used.

Every Developer, Reviewer, QA, and Integrator evidence header contains exactly one each of `MODEL`,
`REASONING_EFFORT`, and `MODEL_ROUTE_REASON` (`default_complex`, `qa_bounded_low`, or
`risk:<frozen-category>`). Reviewer reconciles its dispatch capsule with subject evidence; QA verifies
the complete route and the forbidden-Luna assertion. Integrator evidence and the final User summary
contain an `ACTUAL_MODEL_ROUTING` table with role, model, effort, reason, and evidence reference.
Missing or mismatched audit values block the gate.

## Recovery and UI smoke

Recovery first reconstructs the durable active task and host from board, Git, and evidence; it reuses
the recorded host and never duplicates activation. If identity cannot be proved, stop fail-closed with
the typed blocker. A browser smoke is required only for a user-visible UI change, and then uses a
documented load state or deterministic selectors; unsupported `networkidle` probing is forbidden.

## Safety

WIP is one. When a task is active, a new submission returns `BLOCKED_ACTIVE_TASK_RUNNING` immediately
after board parsing, before Git verification, lock acquisition, request parsing or classification;
the User submits it again after close. Reuse an already-recorded
host and never create a duplicate. Do not push, rebase, force-remove, restore, reset, stash, discard,
delete a branch, archive or retire resources automatically. Stop and record a typed blocker on
unprovable identity/evidence, dirty/divergent state, conflict, scope expansion, destructive work or
repeated failure.

Integrator must bind the accepted Developer subject, Reviewer and QA evidence, and the exact clean
host HEAD before the runtime performs the approved local integration. The completed task remains
`implemented_pending_human_review` until the User says `关闭`. Closeout retains clean task/thread/
worktree/branch/HEAD/evidence references; lifecycle cleanup is outside the daily gate.

The first ordinary complex task is a monitored first real run, not a pilot or governance project.
If it fails, keep it active with its blocker and report the exact stopping fact.
