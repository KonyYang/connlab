---
name: connlab-lane-orchestrator
description: Execute, continue, recover, or close ConnLab repository tasks with the Sol-native three-tier workflow. Use for any ConnLab task that changes the repository or its task board; classify work as micro, standard, or high risk, automate routine review and validation, preserve scope, and stop for the User only at final Close or a genuine authority decision.
---

# ConnLab Sol-Native Orchestrator

Use GPT-5.6 Sol as the default reasoning and implementation model. Assume it can plan, implement,
self-review, recover, and make ordinary technical decisions. Add constraints only for repository facts,
the User's scope, or real irreversible risk.

## Start or resume

1. Run `py -m scripts.connlab_sol_task inspect --repo-root <root> --json`.
2. If idle, inspect only enough code to understand the likely seam and classify the task. Submit the
   compact requirement through `scripts/run_task.ps1`.
3. If running, continue from the compact checkpoint and Git. Do not recreate a Plan, branch, role,
   evidence file, or test result merely because the conversation restarted.
4. Read `docs/project_management/TASK_WORKFLOW.md` only when the tier or next action is unclear. Read
   product/architecture documents relevant to the actual change, not the whole governance history.

## Route proportionately

- **Micro:** Sol implements, self-reviews, runs targeted validation, and finishes. Do not spawn roles.
- **Standard:** one Sol work unit plans and implements; use an independent Reviewer, then one independent
  QA pass. Apply bounded findings in the same work unit. Integrate automatically when clean.
- **High risk:** use Planner, Developer, Reviewer, QA, and Integrator sequentially. Keep handoffs
  automatic and compact.

Choose standard by default. Raise to high risk for database/schema migration, permissions/security,
authoritative or external mutation, destructive work, broad architecture change, or an unresolved
product decision. Never downgrade a known risk to save time.

## Work autonomously

Make ordinary implementation, test, naming, module, and tool decisions without asking the User. Use
supporting skills only when their own trigger applies; they are methods, not required workflow stages.

Do not ask for routine plan approval. Ask only when proceeding would expand the submitted behavior,
requires new authority, chooses between materially different product outcomes, or performs an
irreversible action not already authorized.

## Persist only useful recovery facts

Use `checkpoint` after a meaningful long-running stage or when blocked. Do not record role begin,
invocation, callback, prompt hash, model route, or duplicate evidence commits. Git is the source for
HEAD and changed paths.

Use `finish` once on the clean final subject. The report must show:

- the exact changed paths and that behavior stayed in scope;
- proportional role results for the selected tier;
- passing validation and integration facts;
- a concise summary and any residual risk.

Then stop at `ready_for_close`. Only the User's explicit Close releases WIP.

## Safety

Preserve unrelated changes. Do not silently reset, restore, stash, clean, delete, rebase, push, or
overwrite external data. Stop on scope expansion, new destructive authority, unresolvable dirty state,
or repeated failure whose cause cannot be established. A transport typo may be corrected once after
confirming no repository state changed.
