# TASK_GOVERNANCE_PROPORTIONATE_REGATE_EVIDENCE_REUSE_AND_COMPACT_HANDOFF

Status: `superseded_by_split_plans`

Type: non-executable governance umbrella / audit trace

Planning base: `4e7ce7ffa040039e8c7ebb659efe8cba5e00eeff`

Revision base: `cdb96b4ed80143ba40d571615282f0ee95708a0f`

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Non-Executable Boundary

The User rejected this task as one executable package. It must never be approved, queued, assigned
an execution token, given a branch/worktree, or dispatched to an implementation role.

This file now preserves only the original goal and the reason for the split. The two approval-
eligible packages are:

1. `TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF` (Task A);
2. `TASK_GOVERNANCE_REGATE_EVIDENCE_REUSE_BASELINE_LEDGER_AND_VALIDATION_RUNNER` (Task B).

The dependency is strict:

```text
User approval of A
-> isolated A Developer -> Reviewer -> mandatory QA -> Integrator acceptance
-> separate User approval of B
-> isolated B Developer -> Reviewer -> mandatory QA -> Integrator acceptance
```

Approval of A does not approve B. Task B cannot acquire a token, queue, create a worktree, or be
implemented until Task A is locally accepted and the User separately approves B's exact package.

## Preserved Umbrella Goal

Reduce routine role-transition latency, active-context growth, repeated reads, repeated Reviewer
commands, and duplicated QA/Integrator work without weakening WIP=`1`, immutable evidence,
independent roles, final QA, worktree isolation, no-push, or non-destructive closeout rules.

## Split Rationale

- Task A owns the prerequisite authority layer: lossless board history separation, automatic
  closeout maintenance, deterministic mechanical gate transitions, event-driven one-handoff-per-
  turn routing, compact references, minimal safe reads, strict callbacks, and cadence/budgets.
- Task B owns the dependent validation layer: per-command Reviewer reuse, dependency impact,
  baseline-debt ledger, deterministic command execution/sharding, final-full QA, and Integrator
  differential validation.
- The split prevents an unreviewed evidence-reuse mechanism from depending on an unimplemented
  board/transition authority and keeps each lane independently reviewable and reversible.

## Safety Invariants

- Current Active Task remains None at planning time; execution state remains terminal with null
  owner/active/queue/paused/Quick Fix/parallel records.
- Neither split task is a Quick Fix or a parallel exception.
- Neither task may modify product, API, schema, database, Office, or real business data.
- Retained, frozen, cancelled, V1-Lite, and Controlled Lane V2 artifacts remain untouched.
- No push, publication, restart, live compaction, destructive cleanup, or remote mutation is
  authorized by this umbrella or its planning commit.

## Stop Point

This umbrella is permanently non-executable. Review and approval decisions must target Task A and
Task B separately.
