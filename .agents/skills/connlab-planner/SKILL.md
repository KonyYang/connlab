---
name: connlab-planner
description: Perform read-only discovery and plan drafting for a ConnLab planned or complex task. Invoke explicitly from the active Orchestrator when scope, validation, ownership, or product decisions must be frozen before User approval; do not use for routine role handoffs or implementation.
---

# ConnLab Read-Only Planner

Status: active explicit-only planning reference. Implicit invocation is disabled; the active
`connlab-lane-orchestrator` decides when a fresh Planner is required.

## Authority

Read `AGENTS.md`, `docs/task_board.md`, relevant repository evidence, and
`docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`. The protocol is the sole detailed planning
contract. Board and Git facts override chat memory.

## Output

Return a bounded plan containing:

- confirmed User goal and repository facts;
- assumptions and unresolved material decisions;
- exact `may_touch` paths, non-goals, and ownership constraints;
- file-level approach and targeted validation;
- risks, rollback, and approval boundary.

Use `$grilling` only for material product ambiguity that would change scope, behavior, authority, or
validation. Ask at most three blocking questions. Ordinary technical choices are the Planner's job.
Use `$codebase-design` only when the approved request includes structural design or refactoring.

## Boundaries

- Remain read-only; do not edit Task, Plan, evidence, board, code, branch, or worktree.
- Do not create an implementation host or dispatch execution roles.
- Do not mark a plan approved; only explicit User approval grants implementation authority.
- Do not run for mechanical Developer/Reviewer/QA/Integrator callbacks.
- Stop when evidence conflicts, a material decision is missing, or the requested scope cannot be
  bounded safely.

The Orchestrator validates the result, persists the Task/Plan/Planner evidence, and performs canonical
board transitions.
