# ConnLab Planner Discovery Protocol

Last Updated: 2026-07-25
Status: active governance protocol
Scope: product/technical planning, task decomposition, and controlled-parallel lane creation

## 1. Goal

This protocol prevents ConnLab Planner from turning a short or ambiguous user request directly into an executable task or lane.

Planner must first understand the user goal, current project state, existing evidence, constraints, and unknowns. A plan that looks complete but is based on weak assumptions is not ready.

## 2. When To Use

Use this protocol whenever the user asks Planner to:

- plan the next task, phase, or lane
- split work into controlled-parallel lanes
- create or activate a task after a completed lane
- interpret a broad product direction
- convert a short request into implementation work
- reconcile board/evidence/scope before Developer starts

Do not use this protocol for pure orchestration handoffs where the board/evidence already identify the next role and no new scope is being planned.

## 3. Discovery Gate

Before proposing tasks or lanes, Planner must produce a Discovery Gate.

The Discovery Gate must include:

1. Current phase, current active task/lane, current role, and why Planner is allowed to act.
2. User goal restatement in 3-5 sentences.
3. Evidence read: board, task files, plans, evidence, architecture docs, skill docs, or code areas that shape the request.
4. Confirmed facts: facts directly supported by user instruction or repository evidence.
5. Planner assumptions: inferences that are useful but not yet confirmed.
6. Missing information: unknowns that can change scope, UX, API, data ownership, validation, or task ordering.
7. Planning risk: what is likely to go wrong if Planner creates lanes immediately.
8. Clarifying questions, maximum 3, only when answers materially affect the plan.
9. Recommended stop/continue decision:
   - stop and wait for answers
   - continue with explicitly named assumptions
   - continue because evidence is already sufficient

## 4. Assumption Labeling

Planner must not present inferred scope as user-approved scope.

Use this structure when scope is not fully explicit:

```text
Confirmed by user:
- ...

Confirmed by repository evidence:
- ...

Inferred by Planner:
- ...

Not yet confirmed:
- ...
```

If any "Not yet confirmed" item affects May Touch, Must Not Touch, validation gates, data model, API shape, UX behavior, or serial/parallel ordering, Planner must either ask a question or keep the lane `proposed`/`planned`.

## 5. Definition Of Ready For Lane Approval

Planner may mark a lane `approved` only when all items below are satisfied:

- user goal and operator/user scenario are clear
- current board state and dependencies are verified from files
- existing behavior or authority path has been checked from relevant docs or code, not only chat memory
- task/lane has a formal task file or the approved Planner action is to create one
- dependencies and serialization constraints are explicit
- May Touch, Must Not Touch, Locked Paths, evidence file, validation gate, and merge gate are concrete
- controlled-parallel implementation has a concrete `lane/*` branch, sibling worktree path, and clean base commit; `TBD` is not approval-ready
- no active lane owns the same shared file, oversized mixed test, or authority path
- Developer clean-commit handoff, clean Reviewer/QA input, Integrator residual ledger, and worktree retirement are declared
- at least one acceptance path is testable or reviewable
- at least one explicit non-goal prevents scope creep
- unresolved assumptions are either confirmed by the user or documented as out of scope

If this Definition of Ready is not met, the lane may be `proposed` or `planned`, but must not be `approved`.

## 6. Clarification Rules

Ask questions when:

- the user describes a product outcome but not the user workflow
- two or more plausible scopes would produce different tasks
- frontend and backend boundaries are unclear
- a request could touch authority data, Office files, public-drive workflows, lifecycle state, Matrix/Fee authority, or global board state
- the right validation gate cannot be named

Do not ask questions when:

- the answer is already in current board/task/evidence files
- the uncertainty can be safely handled as a non-goal
- the user explicitly requested a narrow governance update and the required fields are already known

Prefer 1-3 high-impact questions over long questionnaires.

## 7. Planning Output Levels

Planner should distinguish four levels:

| Level | Meaning | File changes allowed |
|---|---|---|
| Discovery | understand goal, evidence, assumptions, blockers | none unless user asks to document discovery |
| Proposed lanes | candidate task/lane split for discussion | none by default |
| Planned lanes | task/evidence/board draft exists but not executable | only after user approval to write planning docs |
| Approved lanes | executable after gates and explicit user approval | board/task/evidence updates allowed by Planner |

Short user approval such as "sounds good" approves the discussed direction only. Planner must still ensure the lane Definition of Ready is met before marking it `approved`.

## 8. Interaction With Controlled Parallel Execution

This protocol sits before `docs/project_management/PARALLEL_EXECUTION_MODEL.md`.

Planner Discovery decides whether a lane is ready to be proposed, planned, or approved. The Parallel Execution Model then governs role boundaries, evidence, review, QA, and integration.

Automatic orchestration must not use this protocol to silently create or approve new scope. If orchestration reaches a missing future task, it should route to Planner Discovery first.

## 9. Minimal Planner Response Template

```text
Current phase:
Current active task/lane:
Current role:
Why allowed:

User goal restatement:

Evidence read:

Confirmed by user:

Confirmed by repository evidence:

Inferred by Planner:

Not yet confirmed:

Planning risk:

Questions:

Recommendation:
```

For very small governance-only tasks, Planner may compress this template, but must still separate confirmed facts from assumptions before creating approved lanes.
