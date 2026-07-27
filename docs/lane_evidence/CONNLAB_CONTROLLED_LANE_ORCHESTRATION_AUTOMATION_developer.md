# CONNLAB_CONTROLLED_LANE_ORCHESTRATION_AUTOMATION Developer Evidence

Date: 2026-07-27
Role: Developer
Status: `implementation_checkpoint_accepted_at_76a6e736_pending_user_bootstrap_and_pilot_authorization`
Implementation/tests: accepted in exact local 35-path checkpoint `76a6e736`
Bootstrap/real runtime side effects: unauthorized

## Current Implementation Result

The authorized deterministic orchestration package is implemented without activating it:

- schema-v2 canonical JSON CLI with the exact 39 `CTL_*` codes and stable exit classes;
- Git-common-dir registry-v2 model with exclusive token lock, expected-generation CAS,
  idempotent replay, adjacent atomic replace, pre-replace durable recovery intent and
  transaction-visible post-write verification;
- all six mutation commands, including direct B6 coverage for `mark-invocation-started`;
- immutable dispatch task/lane/route/scope binding, receipt/read-back acknowledgement and
  prepared-state-bound advance;
- journal-backed possible-start recovery that ignores caller claims and never resends after a
  durable invocation-start marker without one exact read-back match;
- one-action state routing across planning, authorization, Developer/fix, Reviewer, QA,
  Integrator and closeout states;
- ownership normalization/conflict detection and governance-owner checks;
- read-only scan of Git cleanliness, frozen authority file digests, registry recovery/dispatch
  state and shared-owner conflicts before returning one action; `prepare-dispatch` runs that
  authoritative scan again and recomputes the legal action from registry lane state/proof;
- `route-plan` retained as diagnostic-only projection; only authoritative `scan` may precede an
  external action;
- bounded Git create/adopt/retire preflights with exact HEAD/common-dir/base/scope and closeout
  gates derived from registry facts rather than caller-provided advance/CLI booleans;
- canonical callback IDs plus exact role-specific status, evidence/HEAD, route, operation,
  thread, worktree and payload binding; delayed callbacks and stale gate proof fail closed;
- exact non-empty native target/read-back binding plus canonical read-back digest for
  acknowledgement and possible-start adoption; Git paths additionally bind exact
  repo/worktree/branch/base/HEAD/scope topology;
- acknowledged state advances maintain registry worktree, owner, role binding, callback
  consumption and closeout facts; retirement derives gates from those facts and live Git
  cleanliness, not caller booleans;
- completion callbacks update only the state-specific authoritative proof field, entering a new
  gate clears its prior completion/approval proof, one lane may have only one unfinished dispatch,
  and advance CAS rechecks the lane's current state;
- thin PowerShell and skill adapters plus exact v2 governance hooks.

No real native Codex task, automation, heartbeat, registry, branch, worktree, migration,
retirement, archive, remote or generated-product action was executed.

## TDD Evidence

Observed RED checkpoints:

1. contracts module absent: `1 failed`;
2. registry/ownership/state/callback/Git modules absent: `5 collection errors`;
3. v2 governance hook absent: `1 failed`;
4. owner/native decisions absent: `2 collection errors`;
5. state/action validation absent: focused RED;
6. Git CLI preflight returned `CTL_NO_ACTION` instead of `CTL_OK`;
7. canonical callback event ID absent: focused RED;
8. complete state-table additions: `3 failed, 22 passed`;
9. immutable dispatch/recovery/scan/native/Git proof matrix: `11 failed, 57 passed`.

Each RED was followed by the smallest in-scope implementation. Final exact gate:

```text
py -m pytest tests/unit/test_connlab_controlled_lane_contracts.py
  tests/unit/test_connlab_controlled_lane_registry.py
  tests/unit/test_connlab_controlled_lane_ownership.py
  tests/unit/test_connlab_controlled_lane_state_machine.py
  tests/unit/test_connlab_controlled_lane_callbacks.py
  tests/unit/test_connlab_controlled_lane_git_preflight.py
  tests/integration/test_connlab_controlled_lane_dry_run.py
  tests/unit/test_connlab_lane_worktree_script.py -q
101 passed in 17.36s
```

The integration tests use only temporary registry roots and disposable Git repositories. The
PowerShell adapter test executed only `--dry-run` against a temporary registry path and proved
stable one-JSON output with zero write.

## Exact Implementation Paths

New runtime/skill/protocol paths:

- `scripts/connlab_controlled_lane/{__init__,contracts,registry,ownership,state_machine,git_preflight,callbacks,cli}.py`
- `scripts/connlab_controlled_lane.ps1`
- `.agents/skills/connlab-controlled-lane/SKILL.md`
- `.agents/skills/connlab-controlled-lane/agents/openai.yaml`
- `docs/project_management/CONTROLLED_LANE_ORCHESTRATION_V2.md`

Exact compatibility hooks:

- `scripts/connlab_lane_worktree.ps1`
- `scripts/run_task.ps1`
- `AGENTS.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md`

Bounded tests are the eight modules in the final pytest command above. Task/plan/Planner evidence
and board changes are the retained lane governance package; this evidence is the only governance
file updated by the implementation pass.

## Exact Package Numstat

```text
17/0  AGENTS.md
17/0  docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md
22/0  docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md
7/5   docs/task_board.md
100/13 scripts/connlab_lane_worktree.ps1
19/2  scripts/run_task.ps1
71/0  .agents/skills/connlab-controlled-lane/SKILL.md
4/0   .agents/skills/connlab-controlled-lane/agents/openai.yaml
853/0 docs/connlab_controlled_lane_orchestration_automation_plan.md
331/0 docs/lane_evidence/CONNLAB_CONTROLLED_LANE_ORCHESTRATION_AUTOMATION_planner.md
112/0 docs/project_management/CONTROLLED_LANE_ORCHESTRATION_V2.md
61/0  scripts/connlab_controlled_lane.ps1
5/0   scripts/connlab_controlled_lane/__init__.py
166/0 scripts/connlab_controlled_lane/callbacks.py
279/0 scripts/connlab_controlled_lane/cli.py
207/0 scripts/connlab_controlled_lane/contracts.py
246/0 scripts/connlab_controlled_lane/git_preflight.py
239/0 scripts/connlab_controlled_lane/ownership.py
270/0 scripts/connlab_controlled_lane/registry.py
237/0 scripts/connlab_controlled_lane/state_machine.py
583/0 tasks/CONNLAB_CONTROLLED_LANE_ORCHESTRATION_AUTOMATION.md
328/0 tests/integration/test_connlab_controlled_lane_dry_run.py
233/0 tests/unit/test_connlab_controlled_lane_callbacks.py
73/0  tests/unit/test_connlab_controlled_lane_contracts.py
187/0 tests/unit/test_connlab_controlled_lane_git_preflight.py
129/0 tests/unit/test_connlab_controlled_lane_ownership.py
314/0 tests/unit/test_connlab_controlled_lane_registry.py
250/0 tests/unit/test_connlab_controlled_lane_state_machine.py
114/0 tests/unit/test_connlab_lane_worktree_script.py
```

This Developer evidence is also new and therefore has its current physical line count as its
addition count; it is intentionally omitted from the self-referential static numstat block above.

## Physical Line Results

Blank-inclusive UTF-8 counts:

| Path | Lines |
|---|---:|
| `contracts.py` | 207 |
| `registry.py` | 270 |
| `ownership.py` | 239 |
| `state_machine.py` | 237 |
| `git_preflight.py` | 246 |
| `callbacks.py` | 166 |
| `cli.py` | 279 |
| `__init__.py` | 5 |
| registry unit test | 314 |
| dry-run integration test | 328 |
| other six bounded tests | 73 / 129 / 250 / 233 / 187 / 114 |
| `connlab_controlled_lane.ps1` | 61 |
| `connlab_lane_worktree.ps1` | 268 |
| `run_task.ps1` | 103 |
| skill / metadata / v2 protocol | 71 / 4 / 112 |

Every candidate is below its frozen cap and below the plan's 80-percent split trigger.

## Current Validation

- exact callback/proof focused regression: `60 passed in 1.87s`;
- exact bounded pytest after B7-B9: `101 passed in 17.36s`;
- `py -m py_compile` on all eight runtime modules and eight tests: passed;
- PowerShell parser on all three candidate scripts: `errors=0`;
- tracked `git diff --check`: passed (only expected LF/CRLF notices);
- 24 untracked paths, `git diff --no-index --check`: no whitespace diagnostic;
- UTF-8 trailing scan across all 30 candidate paths: clean;
- exact 30-path whitelist: `unexpected=0`, `missing=0`;
- staged index: empty;
- current repository Git-common-dir has no `connlab-controlled-lane` registry directory;
- `HEAD`, `master`, and `origin/master` remain
  `6767a3ae4116185d8ed27b53cfdc050975efce2e` with `0/0` delta;
- retained TASK_367A worktree remains clean/index-empty at
  `53840b42ea73358c31fe40c5225646363d485829` on its original branch;
- no credential/runtime-copy import; v2 does not invoke `_codex_runtime.ps1`;
- no real data, DB, public-drive, generated artifact, native task or remote operation.

## Prior Planning-First Record

The preceding docs-only Developer planning-first pass read the approved task, plan, Planner
evidence, board, lane orchestration protocol, parallel operations guide, role registry, current
scripts, current orchestrator skill, Git topology, and native task topology. The B6 docs-only
planning fix refined only:

- `tasks/CONNLAB_CONTROLLED_LANE_ORCHESTRATION_AUTOMATION.md`
- `docs/connlab_controlled_lane_orchestration_automation_plan.md`
- this Developer evidence
- exact B6 status/TDD hunks in `docs/task_board.md`.

No product code, tests, scripts, skills, AGENTS rules, registry, task, branch, worktree,
automation, heartbeat, or native task was created or changed.

## Reviewer Gate Fact

The final Planner authorization reconciliation records Reviewer implementation-readiness passed
with B1-B6 closed and User product/test implementation approval. This Developer pass does not
create or impersonate Reviewer evidence.

## Current Phase And Authorization

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Task: `CONNLAB_CONTROLLED_LANE_ORCHESTRATION_AUTOMATION`.
- Allowed now because Reviewer implementation-readiness passed, User approved implementation, and
  Planner completed final authorization reconciliation.
- Product/test/script/skill implementation is authorized only within the frozen exact May Touch.
- Bootstrap, controller/task creation, automation/heartbeat, worktree creation, migration, pilot,
  retirement, and archival each remain separate later User gates.
- Planner aligned task, board, plan, and evidence to the frozen authorized implementation scope.

## Planning Decisions Frozen

1. The deterministic core is a standard-library Python package with canonical schema-v2 JSON.
2. Production registry writes are restricted to Git common-dir `registry-v2.json` with
   expected-generation CAS, token-matched exclusive locking, adjacent temp write, atomic replace,
   and post-write digest verification.
3. Synthetic v1-to-v2 conversion is testable, but no real registry import/migration is part of
   implementation or this pass.
4. Dispatch stages are `prepared -> invocation_started -> sent/result_recorded -> acknowledged ->
   advanced`; role completion is a later independent event.
5. A durable invocation-start marker precedes the one external call. After that marker, zero
   read-back matches never authorize resend.
6. The pure state machine returns exactly one action or one fail-closed result. Reviewer/QA fixes
   reuse the same Developer task and worktree.
7. QA is skipped only with both User-approved `qa_required=false` and Reviewer confirmation for
   the reviewed commit.
8. Manual smoke has three top-level outcomes: active bounded fix, Planner reconciliation, or a new
   corrective lane after acceptance.
9. Repository helpers never call Codex task APIs. The future skill is the sole controlled native
   adapter and may use create/send/read-back/adopt/archive only at the corresponding gate.
10. Dry-run performs no registry write and no native/Git mutation.
11. Worktree create/adopt/retire use one canonical repo/path/lane/branch/base/HEAD/scope identity
    and fail closed on ownership or topology ambiguity.
12. All future paths, line budgets, split triggers, TDD phases, recovery points, rollback, and
    package-isolation commands are recorded in the updated plan.

## Exact Future May Touch

Future implementation remains limited to:

- new `scripts/connlab_controlled_lane/` package and thin PowerShell entry;
- exact JSON/dry-run/adopt hooks in `scripts/connlab_lane_worktree.ps1`;
- exact v2 delegation hunk in `scripts/run_task.ps1`;
- new `.agents/skills/connlab-controlled-lane/` skill and metadata;
- new v2 protocol and exact compatibility hooks in the three approved governance files;
- the eight bounded test modules listed by the task;
- this lane's task/plan/evidence/board hunks at the owning role gates.

`scripts/task_complete_commit.ps1`, `_codex_runtime.ps1`,
`ROLE_THREAD_REGISTRY.md`, the current orchestrator skill, all product/test paths, remote refs,
real data, and TASK_367A topology remain locked.

## Real File Facts

Blank-inclusive UTF-8 physical lines and SHA-256 before this docs update:

| Path | Lines | SHA-256 |
|---|---:|---|
| plan | 483 | `EBD08D12D445E4F0F560DFC3904E8944ECE58FF08A8C864ADBFF1F8A3B7E8F8A` |
| task | 539 | `909D4111965BC823D854E5669BCF946E37551BE56B94B88D9FA88357E595ABFE` |
| Planner evidence | 276 | `744DF96E76F4F022F8E8A1373489E4C80AF71EA2372740E8DEC6E0C3CB74AC17` |
| `connlab_lane_worktree.ps1` | 181 | `785411BE96C9E90783FD913BCF2FDE6467C57187E59AD15DD8AC3828BE925E87` |
| `run_task.ps1` | 86 | `E5235566A56F4ECB3C6C7917DA8684536B791C151D8D9A8B86B29197C21E5A81` |
| `task_complete_commit.ps1` | 136 | `37CB242726C7D97A48508CE9F11B7D5763D9964DCD0F01162CF966CD499D3CA7` |
| current orchestrator skill | 268 | `53DD5E336042758C8FB630D000EC83BDF4AA11335E47FF0047DA1446A6000B08` |
| lane protocol | 270 | `1B4CDB9F9FD3AA00ACA49B4B378B4F4173821BB796D811C7C899FDE4A353FE26` |
| operations guide | 297 | `943D20C3263C8927212A280CCAA4B5A3897512E15A63AFDC7799CD00547964E7` |
| role registry | 22 | `354F96A7249B996AE2D494AAF062161E207BC4CC4F78E5F72FD35D7F90A55305` |

## Preserved Topology

- `HEAD == master == origin/master ==
  6767a3ae4116185d8ed27b53cfdc050975efce2e`.
- `origin/master...master = 0/0`.
- Primary index was empty.
- Retained TASK_367A:
  - branch `lane/task-367a-matrix-editor-live-xlsx-export`;
  - worktree `C:\Users\White\.codex\worktrees\705b\connlab`;
  - task `019f9c46-d3be-7c72-bafd-5412a054cfa8`.
- Existing Orchestrator, Planner, Developer, Reviewer, QA, and Integrator tasks remain present.
- No topology or native task mutation was performed.

## Prior Planning Validation

Closing results:

- blank-inclusive UTF-8 physical lines:
  - task after final authorization reconciliation: `583`;
  - plan after final authorization reconciliation: `853`;
  - Developer evidence after final authorization reconciliation: `173`;
  - board: `2407`;
- UTF-8 trailing-whitespace scan: clean;
- tracked `git diff --check`: exit `0`;
- plan and Developer evidence no-index `--check`: exit `1` only because each is an added
  untracked file; no whitespace diagnostic;
- B6 changed only the tracked board hunk plus the untracked task, plan, and this Developer
  evidence; Planner evidence remains unchanged and no product/script/test/skill path was touched;
- staged index: empty;
- `HEAD == master == origin/master`, delta `0/0`;
- retained TASK_367A worktree and its index: clean;
- unexpected path scan against the known governance-only set: none.

No implementation test or generated-artifact command belongs to this pass.

## Blockers

None. The exact frozen implementation/test scope is now authorized; bootstrap and real runtime
side effects remain unauthorized by design.

## Planner Reconciliation Record

Planner confirmed that the Developer freeze introduces no product-scope expansion. Registry-v2,
the six CAS mutation commands including the durable invocation-start marker, the unified typed
error catalog, state machine, native adapter, worktree lifecycle, migration markers, tests,
budgets, locks, and separate User gates now match the controlling task and plan.

## Reviewer B6 Bounded Planning Fix

Reviewer implementation-readiness found one documentation-only TDD omission:
`mark-invocation-started` lacked direct command-level coverage even though the command surface
already contained all six CAS mutations. This pass:

- added `mark-invocation-started` to the direct six-command TDD matrix;
- froze exact-`prepared` stage as its only legal source;
- froze first-write generation `+1`;
- froze identical canonical operation/route/key/payload replay as `CTL_ALREADY_APPLIED` with no
  generation increment;
- froze stale generation as `CTL_CAS_CONFLICT`;
- froze changed payload or key reuse as `CTL_IDEMPOTENCY_CONFLICT`;
- froze wrong stage as `CTL_DISPATCH_STAGE_MISMATCH`;
- froze the command itself as marker-only with zero native/Git external action;
- kept crash-at-`invocation_started` and possible-start/no-resend as separate integration tests.

No implementation, test, script, skill, AGENTS, registry, controller, task, worktree, branch,
automation, heartbeat, rename, archive, stage, commit, fetch, or push action occurred.

## Reviewer B7-B9 Bounded Fix

Reviewer B7-B9 were reproduced against the authorized package and fixed without creating a new
Developer task or worktree:

1. **B7 exact selected role identity**
   - `prepare-dispatch` now derives the action again from authoritative lane state/proof and
     requires the selected role's exact `thread_id` and `worktree_path`.
   - Planner/readiness/Reviewer/QA/Integrator and same-Developer fix routes reject missing or
     mismatched identity with `CTL_DISPATCH_ACK_MISMATCH`.
   - For an already known target binding, completion authority was frozen at prepare time.
     Option A's first Developer target is unknown at prepare; B11 supersedes that case with
     post-hoc authority binding after complete identity adoption. B11 remains open.
2. **B8 evidence and HEAD authority**
   - Completion callback validation first proves the active lane gate and frozen role binding,
     then compares the exact frozen evidence path/digest/HEAD.
   - It reads the evidence only beneath the frozen worktree, recomputes SHA-256, reads that
     worktree's actual Git HEAD, and rejects tamper, stale/late gate, cross-role/lane, wrong path,
     wrong digest, or wrong HEAD with stable typed failure.
   - The explicit User approval null stage performs no evidence/Git read; all other null or
     partial authority forms fail closed.
3. **B9 interleaved owner acquisition**
   - The historical implementation rechecked owner claims under the same registry lock and
     expected-generation CAS immediately before prior-contract `worktree_ready` effects. Option A
     moves that check to complete-identity adoption.
   - The latest lane scope, canonical claim content/digest, and all other-lane exact,
     directory-ancestor, and authority-ancestor owners are revalidated.
   - An owner held by another lane returns `CTL_OWNER_CONFLICT` and is never overwritten.
     Same-lane identical claims were intended to be idempotent; B12 remains open to make that
     guarantee correct for provisional-to-exact Option A owner materialization.

### B7-B9 TDD

Reviewer probe reproduction:

```text
11 failed in 1.92s
```

This comprised six wrong-role-thread/worktree cases, evidence/HEAD tamper and legal-null cases,
and three interleaved exact/directory/authority owner cases. A follow-up missing selected-identity
matrix produced six focused RED failures before the fail-closed prepare check was added.

Final focused result:

```text
py -m pytest
  tests/unit/test_connlab_controlled_lane_state_machine.py::test_prepare_rejects_wrong_existing_role_target
  tests/unit/test_connlab_controlled_lane_ownership.py::test_owner_claims_must_match_canonical_requested_scope
  tests/unit/test_connlab_controlled_lane_git_preflight.py::test_callback_binds_actual_evidence_digest_and_lane_head
  tests/unit/test_connlab_controlled_lane_git_preflight.py::test_user_approval_allows_only_explicit_null_completion_authority
  tests/unit/test_connlab_controlled_lane_git_preflight.py::test_owner_acquisition_rechecks_interleaved_latest_registry -q
12 passed in 1.76s
```

Final full bounded package:

```text
py -m pytest tests/unit/test_connlab_controlled_lane_contracts.py
  tests/unit/test_connlab_controlled_lane_ownership.py
  tests/unit/test_connlab_controlled_lane_state_machine.py
  tests/unit/test_connlab_controlled_lane_callbacks.py
  tests/unit/test_connlab_controlled_lane_git_preflight.py
  tests/unit/test_connlab_controlled_lane_registry.py
  tests/integration/test_connlab_controlled_lane_dry_run.py
  tests/unit/test_connlab_lane_worktree_script.py -q
101 passed in 17.36s
```

### B7-B9 Exact Paths And Lines

All B7-B9 implementation/test changes stay inside the frozen package:

| Path | UTF-8 physical lines |
|---|---:|
| `scripts/connlab_controlled_lane/state_machine.py` | 239 |
| `scripts/connlab_controlled_lane/ownership.py` | 239 |
| `scripts/connlab_controlled_lane/registry.py` | 276 |
| `scripts/connlab_controlled_lane/callbacks.py` | 166 |
| `scripts/connlab_controlled_lane/git_preflight.py` | 285 |
| `tests/unit/test_connlab_controlled_lane_state_machine.py` | 318 |
| `tests/unit/test_connlab_controlled_lane_ownership.py` | 146 |
| `tests/unit/test_connlab_controlled_lane_git_preflight.py` | 325 |
| `tests/unit/test_connlab_controlled_lane_callbacks.py` | 239 |
| `tests/unit/test_connlab_controlled_lane_registry.py` | 319 |
| `tests/integration/test_connlab_controlled_lane_dry_run.py` | 335 |

Because these package files remain untracked pending the later integration gate, their current
Git package numstat is their full physical addition count (`<lines>/0`). The six pre-existing
tracked compatibility hunks are unchanged by B7-B9.

### B7-B9 Validation And Topology

- all package runtime Python modules: `py_compile` passed;
- all three candidate PowerShell files: parser errors `0`;
- tracked `git diff --check`: passed, with only expected LF/CRLF notices;
- 24 untracked paths: no-index checks emitted only expected LF/CRLF notices and no whitespace
  diagnostics;
- exact UTF-8 trailing scan across all 30 candidate paths: `0`;
- exact package whitelist: `unexpected=0`, `missing=0`;
- physical-line scan: all runtime/test files remain below their frozen caps and 80-percent split
  triggers;
- staged index: empty;
- no `.db`, `.sqlite*`, `.xls*`, or `.doc*` candidate path;
- no current-repository registry, lock, native task, branch, worktree, automation, migration,
  archive, cleanup, fetch, stage, commit, or push action;
- `HEAD == master == origin/master ==
  6767a3ae4116185d8ed27b53cfdc050975efce2e`, local delta `0/0`;
- retained TASK_367A worktree remains clean/index-empty at
  `53840b42ea73358c31fe40c5225646363d485829` on
  `lane/task-367a-matrix-editor-live-xlsx-export`.

## Reviewer B10 Capability Preflight

Reviewer B10 required the unseeded `create-new-developer-thread` path to bind the new native
Codex task to the lane's already-created worktree. The current real Codex app capability was
checked read-only before any B10-B12 implementation:

- `create_thread` accepts a saved `projectId` plus either `environment: local` or
  `environment: worktree`;
- the only local ConnLab saved project returned by `list_projects` is
  `D:\PythonProject\connlab`, the primary checkout;
- `environment: local` therefore targets primary, not an arbitrary existing lane worktree;
- `environment: worktree` creates a new Codex worktree and cannot adopt the lane worktree path;
- `fork_thread(environment: same-directory)` can reuse a directory only when a source task
  already exists in that directory, which is false for the first Developer task after
  `worktree_ready`;
- `handoff_thread` can toggle a task's associated checkout/worktree but exposes no destination
  path for adopting the already-created lane worktree.

Therefore the frozen order
`create/adopt lane worktree -> create first Developer task in that exact existing worktree`
is not reachable through the current native adapter. The existing implementation's preseeded
`developer_thread_id` test setup hides this capability gap.

Resolving B10 requires a governance/state-machine decision, for example one of:

1. create the Developer task with a native-created worktree and adopt that exact worktree as the
   lane worktree in a revised atomic protocol;
2. create/fork a task before the separate worktree gate so a same-directory source exists;
3. add a real native capability that accepts an existing worktree/project path.

Options 1 and 2 change the frozen worktree/task ordering and combine or reorder externally
authorized actions. Option 3 is unavailable in the current tool schema. The 39-code catalog also
contains no dedicated capability code; adding one or redefining a current code requires the same
source-of-truth review.

Per the Reviewer stop condition, no B10 create lifecycle was fabricated with fake IDs, and no
B11/B12 product or test edit was started after this capability conflict was confirmed. B11 and
B12 remain open for the subsequently reconciled scope.

## B10 Capability Validation

- native tool schema inspection: read-only; no tool mutation;
- `list_projects`: one ConnLab local project at the primary checkout, no retained lane-worktree
  project target;
- no `create_thread`, `fork_thread`, `handoff_thread`, task send, archive, automation, registry,
  branch, or worktree mutation;
- exact 30-path candidate scope retained; only this Developer evidence changed in this pass;
- staged index remains empty; no stage/commit/fetch/push or real data/file action.

## Next Role

The User selected Option A. Planner redrew B10 as one native project-bound
`create_thread(worktree)` action followed by asynchronous complete-identity adoption through one
expected-generation acknowledgement CAS. The old worktree-first/task-second sequence is
superseded.

Reviewer B13-B16 returned the contract to Planner. B13 now reuses the existing `CTL_NO_ACTION`
catalog entry for typed pending observations. B14 freezes B11 on the existing `record-callback`
CAS with post-role evidence/HEAD observation. B15 freezes direct B12 identical and non-identical
same-lane owner tests.

B16 proves the current 30 paths do not have honest line-budget headroom. The User approved four
bounded split paths for native-environment and completion-authority logic/tests, with exact caps
and mandatory net reductions in the existing pressured files. The authorized files remain
uncreated pending the same Developer bounded B10-B12 implementation pass.

The historical capability checkpoint above was superseded by the approved Option A contract:
one native project-bound `create_thread(worktree)` action may create both the first Developer
task and its native worktree, after which the observed complete identity is adopted through the
existing CAS journal. The bounded implementation below closes B10-B12 without performing that
real action.

## B10-B12 Bounded Implementation Result

### B10 Native Environment Lifecycle

- Added `native_environment.py` as a pure native-environment protocol boundary.
- `authorized` prepares `create_developer_environment` without inventing a thread, worktree,
  branch, HEAD, or native project identity.
- The prepared action freezes the canonical client request, route/operation identity, lane,
  role, expected project authority and capability proof.
- After the single fake/dry-run external action, `record-action-result` validates and stores the
  complete native receipt, then moves the lane to `developer_environment_pending`.
- Pending scans return typed `CTL_NO_ACTION` and never resend.
- Exact read-back acknowledgement adopts the observed thread, worktree, branch, base, HEAD and
  project identity in one expected-generation CAS; only that bound thread can complete.
- Zero, multiple, unreadable, wrong, partial or possible-start observations fail closed. No test
  or runtime path calls a real Codex task API.

### B11 Post-Role Completion Authority

- Added `completion_authority.py` as the post-role evidence and Git authority boundary.
- Dispatch freezes only the expected evidence path, role/gate, starting lane HEAD, allowed
  changed paths, checkpoint policy and exact thread/worktree attribution.
- `record-callback` uses the existing expected-generation CAS to read the bound isolated
  worktree, hash the actual evidence, inspect the actual clean HEAD and ancestry, and freeze the
  observed completion authority with the callback.
- Callback-supplied digest or final HEAD is not trusted. Predispatch evidence, unchanged HEAD,
  tampering, dirty worktree/index, wrong ancestry, disallowed changes, late/cross-gate or
  cross-lane attribution fail closed and do not advance generation.
- Explicit User/no-evidence stages retain a separately tested legal-null contract.

### B12 Exact Owner Materialization

- Owner records now bind owner kind/key, canonical scope, authority, worktree, branch, thread and
  operation identity.
- The first provisional-to-exact native adoption materializes the claim inside the same latest
  registry expected-generation CAS used for acknowledgement.
- Same-lane exact replay is idempotent with no generation drift.
- Same-lane changed key, content, path, directory, authority, branch, worktree, thread or
  operation fails closed before effects can overwrite the registry.
- Cross-lane contention remains `CTL_OWNER_CONFLICT`; the interleaved lane-a prepare, lane-b
  acquire, lane-a acknowledge/advance path cannot replace lane-b.

## B10-B12 TDD Evidence

RED:

- the first focused run of the two approved new modules failed collection because
  `native_environment` and `completion_authority` did not exist;
- after the first implementation, six same-lane changed-claim probes failed because exact
  native adoption had not yet materialized owners in the acknowledgement CAS;
- the full bounded package exposed stale preseeded-thread fixtures and one old monkeypatch seam,
  which were migrated to the approved unseeded Option A lifecycle without weakening assertions.

GREEN:

- `tests/unit/test_connlab_controlled_lane_native_environment.py`: prepare without invented
  identity, capability proof, single fake action, pending/no-resend, receipt binding, exact
  read-back adoption, lost receipt and zero/multiple/wrong/unreadable/partial observations;
- `tests/unit/test_connlab_controlled_lane_completion_authority.py`: real disposable Git
  post-role evidence/HEAD mutation, actual digest observation, tamper, predispatch, dirty tree,
  wrong ancestry, disallowed path and explicit null authority;
- `tests/unit/test_connlab_controlled_lane_ownership.py`: exact same-lane replay, all changed
  claim dimensions and cross-lane interleaving;
- six CAS mutation commands retain direct first-write, replay, stale-generation,
  idempotency/stage and zero-external-action coverage;
- final bounded package:
  `126 passed in 16.58s`.

## Final Validation

- all 20 candidate runtime/test Python modules: `py_compile` passed;
- PowerShell parser errors: `0` for `connlab_controlled_lane.ps1`,
  `connlab_lane_worktree.ps1` and `run_task.ps1`;
- UTF-8 physical lines/caps:
  `native_environment.py 218/220`,
  `completion_authority.py 179/180`,
  native tests `207/230`,
  completion tests `180/200`,
  `contracts.py 299/300`,
  `registry.py 276/276`,
  `state_machine.py 230/230`,
  `ownership.py 226/235`,
  `callbacks.py 160/170`,
  dry-run integration `429/450`; every other candidate also remains within its frozen cap;
- tracked `git diff --check`: passed; all 28 untracked paths returned the expected clean
  add-file no-index result; exact UTF-8 trailing scan: `0`;
- exact 34-path whitelist: `unexpected=0`, `missing=0`; staged index: empty;
- no runtime `_codex_runtime`, credential/config copy or real native task invocation;
- current Git common dir contains no controlled-lane v2 registry;
- no real task, automation, branch/worktree, migration, archive, cleanup, fetch, stage, commit or
  push action occurred;
- primary remains `master` at
  `6767a3ae4116185d8ed27b53cfdc050975efce2e`, with
  `origin/master...HEAD = 0/0`;
- retained TASK_367A worktree remains clean/index-empty at
  `53840b42ea73358c31fe40c5225646363d485829` on
  `lane/task-367a-matrix-editor-live-xlsx-export`.

## Next Role

Historical checkpoint: `ready_for_reviewer_implementation_re_gate`; satisfied by Reviewer pass.

Historical checkpoint after Reviewer pass: QA was the next required isolated gate. That gate has
now passed with task-specific persisted evidence. Integrator, bootstrap, migration, archival, real
native task/worktree/automation actions, stage, commit, fetch and push remained unauthorized at
that checkpoint.

## Reviewer B17-B20 Bounded Fix

Historical fix checkpoint status: `ready_for_reviewer_implementation_re_gate`; now satisfied.

### B17 Exact Native Receipt Identity

- Native create receipts now require exactly one identity: immediate `threadId` or asynchronous
  `pendingWorktreeId`.
- A receipt containing both identities or neither identity fails closed with the existing
  `CTL_DISPATCH_ACK_MISMATCH`.
- Immediate adoption compares receipt `threadId` to the observed read-back `thread_id`.
- Pending adoption compares `pendingWorktreeId` to the observed pending worktree identity.
- Receipt validation is shared by result recording, pending observation and exact adoption, so a
  changed receipt cannot reach owner materialization.

Direct RED:

- missing receipt identity, both identities and changed immediate `threadId` were all accepted;
- focused result: `4 failed, 33 passed`.

Direct GREEN:

- the same receipt matrix now fails closed, while exact immediate and pending receipts retain
  their legal paths.

### B18 Pending Scan Wiring

- The stable read-only CLI `scan` now recognizes only one exact unfinished
  `create_developer_environment` dispatch at `result_recorded` while the lane is
  `developer_environment_pending`.
- It validates the durable receipt against read-back and returns `CTL_NO_ACTION` with exit `0`,
  exact route/operation IDs, `native_worktree_status=pending`, `retry_allowed=false`,
  `adopted=false` and `external_action_count=0`.
- The path is read-only: the direct CLI test proves registry generation remains `3`; all other
  unfinished dispatch shapes retain `CTL_RECOVERY_REQUIRED`.

### B19 CLI Semantic Split

- Git-common-dir registry-root derivation and frozen authority-file verification moved to
  `git_preflight.py`.
- Generic exact native binding preflight moved to the same bounded preflight module.
- `cli.py` now contains only CLI/read-only coordination for these responsibilities and is
  `268/270` blank-inclusive physical lines.
- No blank-line suppression or statement compaction was used.

### B20 Direct Negative Matrix

- owner tests now directly vary same-lane `content_digest`, `directories` and `authorities`, in
  addition to key/path/worktree/branch/thread/operation identity;
- completion authority directly exercises a clean unrelated Git ancestry;
- `record-callback` directly rejects late/consumed role binding, cross-gate, cross-role,
  cross-lane and stale expected-generation attempts;
- every callback negative asserts the existing typed code, `zero_write=true`, unchanged
  generation and an empty callback registry.

Focused GREEN:

- B17-B20 exact set: `37 passed in 3.05s`;
- atomic-write fixture repair check: `2 passed in 1.04s`;
- final bounded package: `138 passed in 20.11s`.

### B17-B20 Final Validation

- all 20 runtime/test Python candidates: `py_compile` passed;
- PowerShell parser errors: `0/0/0`;
- stable CTL catalog: `39`;
- pressure files:
  - `cli.py 268/270`;
  - `native_environment.py 205/220`;
  - `completion_authority.py 179/180`;
  - `test_connlab_controlled_lane_native_environment.py 226/230`;
  - `test_connlab_controlled_lane_completion_authority.py 194/200`;
  - `test_connlab_controlled_lane_dry_run.py 450/450`;
  - `test_connlab_controlled_lane_ownership.py 220/220`;
  - `test_connlab_controlled_lane_registry.py 315/315`;
- exact package whitelist: `allowed=34 actual=34 extra=0 missing=0`;
- tracked diff-check passed; untracked no-index failures `0`; UTF-8 trailing hits `0`;
- staged index empty; runtime forbidden credential/native-call hits `0`;
- current Git common dir contains no controlled-lane v2 registry;
- primary remains clean topology at
  `6767a3ae4116185d8ed27b53cfdc050975efce2e` on `master`,
  `origin/master...HEAD=0/0`;
- retained TASK_367A worktree remains clean/index-empty at
  `53840b42ea73358c31fe40c5225646363d485829` on
  `lane/task-367a-matrix-editor-live-xlsx-export`.

No real task, worktree, branch, registry, automation, heartbeat, bootstrap, migration, archive,
cleanup, fetch, stage, commit or push action occurred.

Reviewer implementation re-gate, dedicated isolated QA, and Integrator packaging/readiness passed.
The exact local checkpoint is `76a6e736d66ca0207f262f597513a779a1634571` with 35 paths,
`8097/21`, parent `6767a3ae`, and excluded residual `0`. The next role after Planner
reconciliation is Reviewer docs-only closeout. Bootstrap, pilot, and all real runtime side effects
remain blocked pending separate User authorization.
