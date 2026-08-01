# Proportionate Re-gate Evidence Reuse And Compact Handoff — Superseded Umbrella Plan

Status: `superseded_by_split_plans`

Revision base: `cdb96b4ed80143ba40d571615282f0ee95708a0f`

## Decision

The original single implementation plan is withdrawn from approval. Its responsibilities are
partitioned into two serial, independently approved and integrated plans:

- A: `docs/task_governance_active_context_deterministic_transition_and_event_handoff_plan.md`
- B: `docs/task_governance_regate_evidence_reuse_baseline_ledger_and_validation_runner_plan.md`

Task A is the prerequisite. Task B remains planning-only until A has local Integrator acceptance
and the User separately approves B. No lane, worktree, token, queue entry, or role dispatch belongs
to this umbrella.

## Responsibility Map

| Original concern | New owner |
| --- | --- |
| Active board/history migration and recurring maintenance | Task A |
| Deterministic routine governance transitions | Task A |
| Planner removal from mechanical handoffs | Task A |
| One-handoff-per-Orchestrator-turn and cadence | Task A |
| Compact references, minimal reads, callback/context budgets | Task A |
| Reviewer per-command evidence reuse | Task B |
| Direct-dependency and impact-domain decisions | Task B |
| Baseline-debt ledger | Task B |
| Deterministic validation runner and safe shards | Task B |
| Final QA non-substitution | Task B |
| Integrator differential validation and performance pilot | Task B |

## Compatibility And Rollback

The planning split changes no runtime governance. Until A is accepted, current manual governance
remains authoritative. Until B is accepted, every Reviewer re-gate continues using the existing
full validation behavior. Reverting either future implementation does not revive this umbrella as
an executable task.

## Stop Point

Return A and B to User review. Do not approve or implement this umbrella.
