# Matrix optimization items 6-10

Task: `TASK_MATRIX_OPTIMIZATION_6_10`. Goal remains active until all five items are verified.
Baseline: clean primary after the completed Workbench feedback task (2026-09-05).

## Scope and acceptance

| Original item | Acceptance | State |
| --- | --- | --- |
| 6 | Main table gains usable space; details can collapse/reopen without losing edits; readable typography; validation errors locate the relevant input; browser checks at laptop/narrow widths | In progress |
| 7 | Record comparable input/derived-work baseline; reduce demonstrated unnecessary whole-table work; export-only payloads built on demand; preserve save/confirm/export results | Pending measurement |
| 8 | Candidate listing avoids full content validation; selected source receives full validation before import; errors/stale selection/cancellation remain safe | Pending |
| 9 | Backend owns continuous output chain, with durable progress and safe interruption/retry; no duplicate outputs or unintended overwrite; preserve conflict previews and business authority | Independent planning in progress |
| 10 | Inspect actual dependency/Mixin/migration hotspots; implement only justified cohesive improvements or record evidence for no change; keep needed migration history | Pending |

## Execution and constraints

- Follow original numbering, incremental implementation, focused self-review and risk-proportionate validation.
- Use existing workflow; independent contexts for the high-risk generation/recovery batch, not role ceremony for UI edits.
- User authorized behavior-bounded file selection across these items; report the exact Git diff instead of guessing future paths.
- Preserve completed items 3-5. Search placeholders and deferred item 2 stay unchanged.
- Step execution/automatic status coloring is excluded. Preview steps stay at the black initial state.
- Do not mutate real project data, execute live DB migrations, overwrite existing outputs/releases, push or deploy.
- Browser modification tests use isolated fixtures; existing real projects may only be inspected/navigated.
- Reuse existing test infrastructure, no telemetry framework or generic workflow engine.
- Persist useful checkpoints here/board; resume committed work after interruption, never replay completed transitions.

## Evidence and recovery

Initial discovery: primary clean, board idle, existing MatrixEditorWorkspace/MatrixStepWorkspace and
ProjectWorkbenchActiveMatrixWorkspace are the current UI seams. Legacy simulated step statuses were
already removed and must remain removed. Independent item-9 planner is inspecting the existing chain.

No item is marked complete yet. Test results and immutable source subjects will be appended per batch.
