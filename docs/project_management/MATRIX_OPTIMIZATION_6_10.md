# Matrix optimization items 6-10

Task: `TASK_MATRIX_OPTIMIZATION_6_10`. Goal remains active until all five items are verified.
Baseline: clean primary after the completed Workbench feedback task (2026-09-05).

## Scope and acceptance

| Original item | Acceptance | State |
| --- | --- | --- |
| 6 | Main table gains usable space; details can collapse/reopen without losing edits; readable typography; validation errors locate the relevant input; browser checks at laptop/narrow widths | Completed in batch 1 |
| 7 | Record comparable input/derived-work baseline; reduce demonstrated unnecessary whole-table work; export-only payloads built on demand; preserve save/confirm/export results | Completed in batch 2 |
| 8 | Candidate listing avoids full content validation; selected source receives full validation before import; errors/stale selection/cancellation remain safe | Completed in batch 3 |
| 9 | Backend owns continuous output chain, with durable progress and safe interruption/retry; no duplicate outputs or unintended overwrite; preserve conflict previews and business authority | Completed; independent Review and full QA passed |
| 10 | Inspect actual dependency/Mixin/migration hotspots; implement only justified cohesive improvements or record evidence for no change; keep needed migration history | Completed in batch 4; no broad rewrite justified |

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

All five items have implementation/evidence and completed validation. Final mechanical integration
verification precedes the sole-writer finish transition; user Close remains separate.

### Item 6 verification

Source: `e00ffd7c951b8948ab5057f48ecedcdef7f20fc2`.
- Editor: details toggle keeps current step text; full-width mode; table text 8.5 -> 13px,
  headers/group inputs 12px, detail inputs 13px. Workbench tokens 11 -> 13px, still initial black.
- Errors: current step format/sequence, sample quantity, group-name and row-duration errors have
  clickable input locations and aria-invalid feedback. Targets use stable IDs even with duplicate labels.
  Existing validation semantics are unchanged; no new requirement or execution state introduced.
- RED: public UI tests failed because Hide step/workbench details buttons were absent.
  GREEN: 69 affected editor/layout tests passed. Final full frontend Vitest (`--maxWorkers=2`) and
  TypeScript/Vite build passed on the committed source (Vite 1.06s); no backend code changed.
- Browser at 1366px: active Workbench main width 842 -> 1214px (+372px); editor grid 920 -> 1240px
  (+320px) when details collapsed. Real page only inspected/toggled, never edited.
- Isolated backend/API fixture at ports 8017/5187: edited step description, collapsed/reopened and verified
  exact text retained. Invalid Row 1 Group 1 became a clickable issue; click focused that textarea with
  aria-invalid=true; restoring 1 removed the issue. 616px viewport: document width 601px, no page overflow.
  Screenshot inspected, temporary viewport reset, isolated browser tab closed.
- Standards review: no remaining finding after replacing label-based focus with stable input identity.
  Spec review: no finding; existing design/business actions retained. Same-agent passes, not independent roles.

### Item 7 measurement and implementation

Baseline source: `2907b9da` (same implementation as item-6 source). Opt-in diagnostic
`frontend/src/features/matrix-editor/MatrixEditorWorkspace.profile.test.tsx` uses the real Workspace,
80 synthetic rows x 8 groups, ten description edits then ten cell edits. React Profiler measures render
work; call-through wrappers count selected derived functions without replacing their behavior.
Run with `VITE_MATRIX_PROFILE=1`, `npm.cmd exec -- vitest run src/features/matrix-editor/MatrixEditorWorkspace.profile.test.tsx --maxWorkers=1 --reporter=dot`
from frontend. It is skipped by default; no machine-dependent timing gate or telemetry framework.

| Ten changes | Before | After |
| --- | --- | --- |
| Description: save payload / record payload / XLSX payload / schedule calls | 20 / 20 / 20 / 20 | 10 / 0 / 0 / 0 |
| Description: validation parse calls | 12,800 | 0 |
| Cell: save payload / record payload / XLSX payload / schedule calls | 20 / 20 / 20 / 20 | 10 / 0 / 0 / 10 |
| Cell: validation parse calls | 12,800 | 6,400 |

Baseline Profiler render total/median: description 406.17/13.20 ms, cell 135.74/12.86 ms.
After runs: description 243.47/12.30 and 196.60/11.65 ms; cell 148.36/13.38 and 249.44/11.49 ms.
Totals are noisy (JSDOM, warmup/GC); do NOT claim consistent whole-page/input latency improvement.
Deterministic evidence is removal of export-only work and reuse of unchanged validation/schedule/save data.
Rendering itself is not virtualized or rewritten. Realistic browser responsiveness still needs operator feedback.

Word/Test Status/LLCR/CR/XLSX construct live requests on demand. XLSX availability checks only existence
of a selected, non-sample populated row, preserving the original export predicate. Memo dependencies
include all data they consume; no stale caches or changed business validation rules.
RED: public LLCR component using the new request factory sent missing draft data before implementation.
GREEN: 43 affected editing/lifecycle/duration/export tests, plus final profile/component checks passed.
Added public Workspace/API test verifies unsaved XLSX values and stable request snapshot while the
operator continues editing during preview. Existing Word, LLCR, Test Status, save and confirm tests retained.
Standards and spec review: same-agent separate passes, no remaining finding. Source `c4309299` final
clean-source QA: full frontend 487 passed, 1 opt-in diagnostic skipped, 46.64s; TypeScript/Vite build
passed (Vite 1.02s). No layout/observable UI change in this batch; public UI tests cover affected behavior.

### Item 8 lightweight discovery and selected validation

Baseline `c4309299`: eight synthetic 1 MiB files; listing read 8 MiB and resolving one candidate read
another 8 MiB. Measured listing 102.71 ms. After: both operations read zero document bytes; listing
1.50 ms on this machine's temporary local directory (not a network-drive latency promise).
`test_candidate_listing_and_resolution_do_not_read_all_file_contents` supplies reproducible filesystem
read evidence and was RED on baseline before implementation. Final per-file content parsing remains in
the selected preview; import validation, authority fingerprints and source snapshots are unchanged.

Picker identifiers now bind project, current directory, filename and file metadata (device/inode/size/
modification/change time), not an upfront content digest. Metadata changes, rename, directory change,
missing file, cross-project selection and symlink protections remain. This deliberately moves content
verification out of the filename list: preserving all metadata can retain an ID, but does NOT approve
the bytes; the selected source must still pass full preview/commit checks. The old same-metadata test
was replaced with a real XLSX public-API test: a valid workbook becomes corrupt at identical size and
restored timestamps, and selected preview blocks it. Ordinary changed-metadata expiry remains tested.

A Windows-native ChangeTime experiment failed the same-tick replacement case and was removed rather
than adding an OS-specific journal dependency. No new modules, caches, schema or dependencies remain.
Developer checks: 24 passed, 1 symlink skip (host privilege unavailable), 2 real-Word tests deselected.
Final QA on clean detached source `4f99491d4784a08d73a907117cb7e0c13ad6f186`: 38 passed,
1 symlink skip, 2 real-Word tests deselected, 14.10s. Covers candidate service/API, actual XLSX parsing,
import commit, selected groups and method authority. Real Word/COM was not invoked. Frontend request
cancellation/stale-response logic is unchanged. Standards/spec review: same-agent, no remaining finding.

### Item 10 dependency, Mixin and migration inspection

AST inspection of clean batch-3 source found 33 top-level application modules with 46 explicit
infrastructure `from` imports. This is a coupling inventory, not proof every import should be abstracted.
Contact-measurement lifecycle directly creates ORM revision models and mutates repository state inside
transactions; replacing that seam would change several authority operations, not merely remove imports.
MSG intake already accepts storage/Office dependencies but defaults to OfficeFacade and translates its
specific import error. Introducing one-use wrappers here has no demonstrated Matrix performance benefit.
Keep these working seams; address them when a concrete change needs an alternative implementation.

Two Matrix session Mixins retained copied, unused imports from an earlier split. Remove 125 unused
named imports: publication 84 -> 23 (415 -> 344 lines), draft-state 85 -> 21 (387 -> 306 lines).
Their only repository consumer is matrix_editor_session_service; it imports the two classes and the
timestamp helper, not the removed names. All non-import AST nodes are identical to batch-3 source.
Both Mixins use the owning session's stores/context and publication calls draft-state helpers; their
method sets are disjoint. Preserve that inheritance rather than replacing it with a larger pass-through
interface. No business method, signature, domain type, fee hook or validation changed.

Database startup still calls the eight imported migration modules plus dedicated schema bootstraps.
Draft lifecycle reconciliation preserves confirmed-source lineage and removes only unreferenced stale
drafts. These are active compatibility paths, not dead historical files: retain them unchanged. No live
database was opened or migrated. Existing temporary-DB migration tests provide regression coverage.

Baseline Matrix session unit/API/database suite: 47 passed in 14.11s. Post-cleanup Developer checks:
22 Matrix session tests passed in 1.01s. Same-agent Standards pass: no finding (unused dependencies only);
Spec pass: no finding (evidence-led cleanup, no behavior/schema expansion). Final QA on clean detached
source `afbdf76e19a94090cf12ca9e0b34cb96df7e98a6`: all 47 Matrix session unit/API/database tests passed
in 13.64s. Existing Starlette/httpx deprecation warning only; no frontend changes or duplicate full suite.

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

Item-9 in-progress checkpoint (not final acceptance): independent Reviewer
`generation_recovery_reviewer` found preview-token drift after conflict choice, pre-intent partial
workspace staging blocking recovery, missing configured Test Record template binding, published staging
links polluting output folders, project-switch start-state leakage, and unhandled completion-refresh errors.
Developer is fixing these in the same batch. Also check actual chain composition, subprocess crash windows,
legacy XLS metadata behavior, and supported file identity/concurrent-writer assumptions before approval.

Preliminary browser feedback used isolated ports 5197/8027, temporary project P1, actual operation
service/journal and synthetic generation steps (not the real file-generation chain). UI displayed progress,
then a synthetic step-3 failure with Resume. Resume followed by closing the tab completed the same
operation `5ea88f49d4ff42f3983dc62697db6f5f`, eight recorded steps exactly once; reopened UI was no longer busy.
Source was still evolving, so final stable-source browser acceptance remains required. Test services/tabs
were stopped/closed; user services/data were untouched. Helpers remain outside the repository in the
current Codex workspace (`generation_ui_fixture.py`, `generation-ui-vite.config.mjs`).

Retained-write guard slice: four legacy HTTP mutations (workspace create, material collect,
required forms generate, Application Form write-back) now acquire the same project lock before
service/session construction and retain it through request-session commit. Unfinished queued or
blocked operations refuse separate writes even without a live worker; completed operations allow them.
Eight public-route bypass regressions were RED, then the final affected 26 API tests passed in 3.88s,
including actual temporary workspace/SQLite creation, lock lifetime through commit, lock contention,
damaged journal, and existing API compatibility. Three old API test files now explicitly isolate Settings
to temporary directories. Independent Reviewer passed this exact slice (Standards 0, Spec 0), without
repeating tests. Whole-item review/QA still pending; guard source is intentionally not committed alone
because it imports the new generation journal from the same unfinished batch.

Item-9 Developer handoff: 11 lifecycle/API tests, 10 hard-exit/new-process recovery tests,
79 existing generation-service tests, 60 frontend observer/model/layout tests and TypeScript passed.
Independent final review and QA remain pending. Parent added public Start acceptance with real
context, eight application steps, temporary SQLite/files, confirmed Matrix/Fee/Basic Information,
and only Office gateways replaced (Test Status creates a real workbook). Both complete-material and
optional-email-missing cases complete; repeated Start/Resume preserve output bytes, timestamps and
exactly five output records. This caught and fixed a real integration regression: missing optional
email was incorrectly treated as a fatal partial collection. Missing/failed/conflicting files still stop.
Fixture setup errors were corrected without changing product validation; they are not regression RED evidence.

Item-9 immutable implementation: `90d6d60cb2eb0c3eb7935bf4aadf8355c1e57718`.
Independent Reviewer reproduced one P1: after the workspace checkpoint, replacing the official
directory while retaining the sibling manifest could allow subsequent writes into a foreign directory.
Bounded correction `dd8f8371e21754966e681b722e516bfee5c21bac` binds new and reused workspace,
official and Source Book directory IDs; checks before recovery and publication allow ordinary content
growth but refuse substituted directories. Developer: eight replacement/growth tests and 30 adjacent
recovery/service tests passed. Complete eight-step tests rerun after correction: 2 passed, 4.93s.
Independent Reviewer passed the exact clean corrected subject: Standards 0, Spec 0; independently
reran two replacement cases (2 passed, 2.56s). Final QA uses that exact subject in the reused clean
detached worktree; no product/test edits are permitted while it runs.

Final frontend browser check (unchanged frontend bytes from `90d6d60c`): isolated 5197/8027,
temporary P1 with actual public Matrix/Fee/Basic Information confirmations, real operation/journal
but synthetic generation steps. Observed progress dialog, failure message/Resume, disabled new-start
until fresh preview, then explicit new operation preserving prior history. After the Resume request
was visibly accepted, closed its tab; backend completed the same operation
`67405637744a411c92714feaa251af91`, all eight steps exactly once. Reopening had zero error alerts
and an enabled generation button. Screenshot inspected; no real project mutated. Browser checks were
performed by the parent, not claimed as independent QA; actual filesystem/SQLite chain is covered by
the separate complete-chain and hard-exit tests. Owned tabs and both isolated servers were stopped.

Completion audit so far: current Matrix Editor files exactly match item-7 validated source; candidate
implementation/tests exactly match item-8 validated source; cleaned Mixins exactly match item-10
validated source. Subsequent item-9 commits did not alter those completed batches or migration files.

### Final independent QA and delivery audit

QA context `generation_recovery_qa`: clean detached reviewed subject
`dd8f8371e21754966e681b722e516bfee5c21bac` before and after; no code/test/board modifications.

| Gate | Final result | Elapsed |
| --- | --- | --- |
| Complete Python `-m "not office_integration" -p no:cacheprovider` using the verified ConnLab interpreter | 2,610 passed, 4 skipped, 19 deselected | 290.54s |
| Full frontend Vitest, `--maxWorkers=2` | 492 passed, 1 opt-in profile skipped; 76 test files passed | 54.95s |
| Sequential TypeScript and Vite production build | Passed | 10.96s, including Vite 1.19s |

No failing gate or full-matrix retry. Python skips are explicit host/manual cases: manual COM disabled,
specified Fee template absent, historical seed manifest absent and unavailable symlink privilege.
The 19 deselected tests require real Office. Warnings were Starlette/httpx deprecation and duplicate
OpenAPI operation ID, neither a test failure. Do not describe excluded real-Office checks as passing.
The clean QA checkout and reusable dependency junction remain; no cleanup or installation was needed.

Integrator preaudit mechanically confirmed all changed paths belong to this task, clean local master,
linear commits with no merge, and only this report differs from the reviewed/QA implementation.
Item-6 Workbench/CSS are byte-equivalent to their validated source; items 7, 8 and 10 likewise match
their cited checkpoints. The final board report records exact paths, subject and raw evidence digest.

### Remaining operator acceptance (not hidden unfinished implementation)

- Exercise the generated build on the operator's actual Windows/Office setup with disposable copies:
  create/update a project folder, inspect the four Required forms and written-back Application Form.
  Automated Office gateway fakes validate orchestration and ownership, not document layout or COM availability.
- On the actual configured drive, confirm stable file IDs and same-volume hard-link/rename support.
  NTFS is the intended publication environment; unsupported/shared-drive behavior must fail clearly,
  not silently weaken recovery. Do not concurrently edit output files in external applications.
- Assess larger real Matrix inputs and network-drive latency; derived-work reductions and local
  candidate read measurements do not promise the same whole-page speedup on every computer.
- Recovery deliberately stops when source or target ownership cannot be proven. Existing output bytes,
  recovery backups and abandoned internal staging are retained for review, never broadly deleted.

Search placeholders, deferred item 2, completed core items 3-5 and black initial Steps remain unchanged.
No live data, real Office output, schema migration, release deployment, push or destructive Git operation
was performed. This goal delivers implementation and verified local commits, not unattended live acceptance.
