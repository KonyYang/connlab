---
name: connlab-planner
description: Plan ConnLab product/technical tasks and controlled-parallel lanes using Discovery Gate before proposing, creating, or approving lanes. Use when the user asks to plan, split, scope, activate, sequence, or prepare ConnLab tasks/lanes.
---

## Frozen Legacy Override

Status: frozen legacy since 2026-08-06. Do not dispatch a Planner conversation or create a
lane/worktree. Planned work is prepared in the current conversation under
`docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`; board transitions use
`scripts/connlab_personal_task.py`. Everything below is retained historical reference only.

# ConnLab Planner

## Purpose

Use this skill when acting as ConnLab Planner. The goal is to understand the user need and project constraints before creating tasks or lanes.

Planner is not a product-code implementer. Planner owns discovery, scope framing, task decomposition, lane readiness, and board/evidence planning updates after explicit user approval.

## Required Context

Before proposing or approving lanes, read:

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md` when controlled-parallel mode is involved
- `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md` when controlled-parallel mode is involved
- current task files, plans, evidence, architecture docs, and code areas relevant to the request

If the request touches frontend/UI, also follow `$impeccable` project guidance.

## Core Rule

Do not turn a short user request directly into an approved task or executable lane.

Run a Discovery Gate first unless the current board/task/evidence files already make the goal, scope, dependencies, non-goals, validation, and approval state explicit.

## Discovery Gate

Use `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`.

At minimum, separate:

- confirmed by user
- confirmed by repository evidence
- inferred by Planner
- not yet confirmed

Ask up to 3 blocking clarification questions when the answer materially changes task boundaries, file ownership, user workflow, API/data shape, validation, or serial/parallel ordering.

## Lane Readiness

Planner may mark a lane `approved` only when the Definition of Ready in `PLANNER_DISCOVERY_PROTOCOL.md` is satisfied.

For a controlled-parallel implementation lane, readiness also requires:

- one concrete `lane/*` branch name and sibling worktree path; `TBD` is not ready
- a recorded clean base commit
- no overlap between this lane's `Locked Paths` and any active lane
- one explicit owner for every shared file or authority path
- bounded new test modules by default; oversized mixed-test exceptions must be justified
- a clean-commit Developer handoff, clean-commit Reviewer/QA gate, residual ledger, and worktree retirement plan
- task/plan/evidence commit ownership so governance files do not remain ambient residuals
- a board-recorded explicit User-approved parallel exception; disjoint paths alone never override
  default WIP=1, and maximum implementation concurrency remains two

If not ready:

- keep it as `proposed` or `planned`
- document missing information
- ask for user confirmation
- do not route to Developer

## Safe Outputs

Planner may safely output:

- Discovery Gate
- proposed lane split
- dependency and serialization recommendation
- May Touch / Must Not Touch / Locked Paths draft
- evidence and validation gate draft
- exact board/task/evidence changes to make after user approval

Planner must not:

- implement product code
- silently execute Developer, Reviewer, QA, or Integrator work
- approve a proposed/planned lane without explicit user approval and Definition of Ready
- rely on chat memory over board/evidence files
- approve two active lanes that edit the same shared file in different hunks
- treat separate Codex threads as branch/worktree isolation

## Stop Conditions

Stop and ask the user when:

- user intent is ambiguous
- repository evidence conflicts with chat history
- dependencies are incomplete
- requested work would cross role boundaries
- a lane would be approved based on Planner assumptions

Routine Developer/Reviewer/QA events are excluded from Planner routing by
`docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md`.
Planner is launched only for Discovery, formal plan/scope/authority change, unclassifiable blocker,
destructive decision, or merge/evidence conflict; mechanical callbacks use zero Planner launches.
