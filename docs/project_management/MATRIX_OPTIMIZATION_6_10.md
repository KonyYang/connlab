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

### Item 9 independent planning evidence

Planner `generation_recovery_planner` completed read-only inspection. Current chain lives in
`useProjectWorkbenchModel.ts` onCreateOfficialWorkspace (create -> collect -> check -> four Required forms
batches -> Application Form writeback -> display refresh). Browser lifetime currently owns continuation.
The plan is a dedicated backend generation operation, not a generic workflow engine or new DB schema:
start/read/resume, project lock, short sessions per step, atomic job journal under Settings.data_dir.
Bind operation to project/source versions/config/targets and explicit conflict choice. Browser only starts,
observes/reconnects and resumes. Never run a real user's generation as an acceptance fixture.

Critical recovery windows (must test, not just wrap calls):
- RequiredForms service places file before output registration; repository flush is committed at request end.
- OfficialWorkspace moves directory then writes manifest then registers DB; an interrupted own directory
  currently appears inconsistent.
- ApplicationForm writeback edits final DOCX via COM before output registration.

Use operation-owned staged outputs and durable publish intent (target prior hash/absence, complete staged
hash, source context, intended record identity). On restart reconcile matching outputs/records without
regeneration; only claim a file when provenance is proven. Unknown files, changed inputs/targets, damaged
journal, closed project and repeated conflicting requests must stop safely. Stage COM edits before publish.
Do not repeat destructive conflict choices or overwrite unknown artifacts. Preserve existing per-step APIs.

Candidate seams: new project_folder_generation_service, routes_project_folder_generation, generation_journal,
generation_runner and recoverable_output_publisher; existing dependencies/main, official workspace service/
manifest, required forms service/gateway, request material service/copy gateway, ApplicationForm writeback,
output record service, typed frontend client and workbench hook. Inspect exact paths/tests before edits.
Validation must force interruption around file publish/DB commit/checkpoint and workspace move/manifest,
then recover in a new process; verify no duplicate records, no partial final files and untouched foreign bytes.
Independent Developer/Reviewer/QA/Integrator contexts remain required for this high-risk batch.
