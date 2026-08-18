# TASK_GOVERNANCE_REGATE_EVIDENCE_REUSE_BASELINE_LEDGER_AND_VALIDATION_RUNNER

Status: closed (archived 2026-08-18; superseded by Sol-native manual task publishing; only planning evidence delivered)

Type: governance / validation-evidence / execution-runner

Planning base: `cdb96b4ed80143ba40d571615282f0ee95708a0f`

Hard dependency: local Integrator acceptance of
`TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF`.

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

Owner at this gate: permanent Planner. Next gate: User review after Task A acceptance.

## Approval Boundary And Serial Gate

This package may be reviewed now but cannot be approved, queued, activated, assigned a token, given
a branch/worktree, or implemented before Task A is locally accepted. Approval of Task A does not
approve Task B. After A acceptance, the User must separately approve this exact B Task/Plan; B then
uses one isolated WIP=`1` lane with Developer, Reviewer, mandatory QA, and Integrator.

No product/API/schema/database/Office code, real business data, push, publication, restart,
destructive cleanup, retained lane, or frozen V2 change is authorized.

## Goal

Reduce redundant Reviewer and Integrator validation without weakening failure detection:

1. decide reuse per command from immutable evidence and declared dependency closure;
2. run validation deterministically on Windows from argv manifests with safe local shards;
3. replace full base archives for known unchanged failures with a committed hash-bound debt ledger;
4. require one independent final complete QA matrix on the final reviewed HEAD;
5. allow Integrator differential validation only when QA-to-merged-tree equivalence is proven;
6. prove the contract with the exact TASK_368E bounded-fix history and a measured medium pilot.

## User-Confirmed Reuse Contract

Every command record binds command ID, argv/cwd, covered paths, direct dependencies, impact
domains, immutable input commit, relevant environment/fixture/lock hashes, prior pass result/hash,
and evidence commit/blob/hash.

Decision is command-local:

- A command reruns when its covered path or direct dependency changed.
- A command may be reused only when every bound input is identical and its dependency closure is
  complete and proven.
- A bounded authority/API/persistence fix does not invalidate independent unchanged commands; all
  commands covering or depending on that fix must rerun.
- Unchanged frontend tests/build may reuse prior Reviewer evidence only when their paths,
  dependencies, environment, fixtures, locks, command, result, and evidence hashes all match.

Global `FULL_REGATE` is mandatory for missing/ambiguous/mismatched/stale facts, unknown failure,
unprovable dependency closure, schema or migration change, shared-ownership drift, or expanded,
removed, incompatible public contract. There is no force, ignore, assume-safe, or override option.

## Decision State Machines

### Reviewer command decision

```text
UNASSESSED
  -> FULL_REGATE (any global or unprovable fact)
  -> REQUIRED_RERUN (covered/dependency/command/environment/fixture/lock input changed)
  -> REUSE_CANDIDATE (all immutable facts equal)

REQUIRED_RERUN -> PASSED | FAILED
REUSE_CANDIDATE -> REUSED only after prior pass/evidence blob verification
FAILED or missing result -> FULL_REGATE / blocker
```

The aggregate can be `PROPORTIONATE_REGATE` only when every manifest command is exactly
`REQUIRED_RERUN` or `REUSED` and every rerun passed. Otherwise it is `FULL_REGATE` or failure.

### QA

`reviewer_pass -> FULL_QA_REQUIRED -> QA_PASS|QA_FAIL`. Reviewer reuse never marks a QA command
complete. QA executes the full frozen risk-proportionate matrix once at final reviewed HEAD.

### Integrator

`QA_PASS -> DIFFERENTIAL_ALLOWED` only when QA HEAD ancestry, conflict-free merge, exact package,
unchanged covered/dependency domains and environment/fixture/lock hashes, and QA binding to merged
tree are all proven. Conflict, drift, package change, unknown failure, or unprovable binding gives
`FULL_VALIDATION_REQUIRED`.

## Helper Interfaces

### Evidence decision

```text
py scripts/connlab_regate_evidence.py decide --repo-root <root> --manifest <json> --json
py scripts/connlab_regate_evidence.py integrator-decide --repo-root <root> --manifest <json> --qa-result <json> --merge-commit <sha> --json
```

Outputs sorted command IDs and stable reasons: `FULL_REGATE`, `PROPORTIONATE_REGATE`,
`DIFFERENTIAL_ALLOWED`, or `FULL_VALIDATION_REQUIRED`. Both commands are zero-write.

### Deterministic runner

```text
py scripts/connlab_validation_runner.py validate-manifest --manifest <json> --repo-root <root> --json
py scripts/connlab_validation_runner.py run --manifest <json> --role <Reviewer|QA|Integrator> --artifact-root <empty-temp-dir> --json
py scripts/connlab_validation_runner.py aggregate --manifest <json> --results <dir> --json
```

Commands are argv arrays and are started without shell evaluation. Pytest node IDs use canonical
repository-relative POSIX separators even on Windows; deselect IDs are validated against
collection before execution. Every result records command/shard ID, argv, cwd, start/end/duration,
exit code, stdout/stderr SHA-256, input HEAD, environment/fixture/lock digests, and result digest.

Frontend runtime may use a declared read-only dependency directory only when repository root,
`package-lock.json`, Node/npm, package-manager metadata, and required executable hashes match the
manifest. The runner never installs dependencies or changes `node_modules`/lockfiles. Each shard
gets distinct OS-temp, pytest cache, coverage, frontend cache, and dist paths. Backend/frontend may
run concurrently only inside one role, against one immutable HEAD, with one token owner and no
additional implementation worktree.

### Baseline debt ledger

```text
py scripts/connlab_baseline_debt_ledger.py verify --repo-root <root> --ledger <json> --head <sha> --json
py scripts/connlab_baseline_debt_ledger.py decide --repo-root <root> --ledger <json> --test-id <canonical-id> --head <sha> --json
```

The committed v1 ledger records canonical test/node ID, baseline commit, failure class and stable
signature, source/test/fixture Git blob hashes, first-confirmation evidence ref, expiry condition,
owner, and `active|resolved|superseded` status. If all hashes match, Git blobs + ledger prove the
known debt without a full base archive. Drift, expiry, unknown failure, or related blob change
requires a fresh baseline comparison and fails closed until committed evidence exists.

## Exact TASK_368E Replay

The committed fixture binds this actual chain:

- base `e226bf1e54db4de54eb2366e96895999ce54652d`;
- first Developer evidence `bb9734830b41c3a86c1cd5542d34a0832cd990d4`;
- Reviewer blocker evidence `68a337678dfaa35fbfac987c36027c605d3e0668`;
- bounded fix `1882c1b04937f0c576ddd2350407edc91b990217`;
- Developer fix evidence `f924c33deb92be269150085c9e8982f152d3b809`;
- Reviewer pass `77fe429eea59d2908c2f57d9243e8fd893488ad5`;
- QA pass `c9a61bcb701178c1042d99ca8011d138e0420330`;
- local merge `634279b7ced1306092e8e2e7f39705eb7f0942d5`.

Fix delta is the authority classifier, bounded unit/API tests, and Developer evidence. Replay must
classify backend B1/authority/API/direct-dependency commands as rerun and the unchanged frontend
`8 files / 61 tests` plus build commands as reusable at Reviewer re-gate. QA must actually rerun
the final complete frontend tests/build. The frozen seven-command Reviewer baseline contains four
affected groups (TASK_368E unit/API, cleanup-wrapper matrix, authority/API compatibility, and
changed-Python compilation) plus three unchanged groups (disposable XLSX/catalog/external-read
compatibility, frontend 61 tests, and frontend build). It must reduce from seven executions to
four, a `42.9%` reduction, without counting cached/no-op work as execution.

## Exact May Touch

### Governance contract and active role references

1. `AGENTS.md`
2. `docs/project_management/REGATE_EVIDENCE_REUSE_BASELINE_LEDGER_AND_VALIDATION_RUNNER_CONTRACT.md` (new)
3. `docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`
4. `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
5. `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md`
6. `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
7. `docs/project_management/TASK_EXECUTION_SKILL.md`
8. `docs/project_management/TASK_REVIEW_CHECKLIST.md`
9. `.agents/skills/connlab-lane-orchestrator/SKILL.md`

### Helpers, ledger, fixtures, and bounded tests

10. `scripts/connlab_regate_evidence.py` (new)
11. `scripts/connlab_validation_runner.py` (new)
12. `scripts/connlab_baseline_debt_ledger.py` (new)
13. `docs/project_management/baseline_debt_ledger.v1.json` (new)
14. `tests/fixtures/governance/task_368e_regate_replay/manifest.v1.json` (new)
15. `tests/fixtures/governance/task_368e_regate_replay/evidence_hashes.v1.json` (new)
16. `tests/fixtures/governance/task_368e_regate_replay/qa_matrix.v1.json` (new)
17. `tests/fixtures/governance/task_368e_regate_replay/medium_pilot.v1.json` (new)
18. `tests/unit/test_connlab_regate_evidence.py` (new)
19. `tests/integration/test_task_368e_regate_replay.py` (new)
20. `tests/unit/test_connlab_validation_runner.py` (new)
21. `tests/integration/test_connlab_validation_runner_windows.py` (new)
22. `tests/unit/test_connlab_baseline_debt_ledger.py` (new)
23. `tests/integration/test_connlab_integrator_validation_decision.py` (new)
24. `tests/unit/test_connlab_regate_validation_governance.py` (new)

### Task-owned and primary-only paths

25. `tasks/TASK_GOVERNANCE_REGATE_EVIDENCE_REUSE_BASELINE_LEDGER_AND_VALIDATION_RUNNER.md`
26. `docs/task_governance_regate_evidence_reuse_baseline_ledger_and_validation_runner_plan.md`
27. `docs/lane_evidence/TASK_GOVERNANCE_REGATE_EVIDENCE_REUSE_BASELINE_LEDGER_AND_VALIDATION_RUNNER_planner.md`
28. Task B Developer/Reviewer/QA/Integrator evidence with the same exact task prefix.
29. `docs/task_board.md` (primary Planner/Integrator lifecycle only; Developer lane must not edit it)

No additional path is authorized without Planner/User reconciliation.

## Must Not Touch

- All `backend/**`, `frontend/**`, product/API/schema/database/migration/Office/business tests,
  real data, operator files, public drive, and Standard/Matrix authority.
- Task A helpers `scripts/connlab_execution_transition.py`, `scripts/connlab_active_context.py`,
  `scripts/connlab_handoff_contract.py`, its board archive/index, and `scripts/run_task.ps1`.
- Read-only execution gate, lane worktree/commit helpers, completed-Markdown archive helper.
- Role registry, active bundle, V1-Lite/V2 contract/skill/helper/registry/heartbeat/pilot/corrective.
- TASK_368E code/lane/evidence content; its commits/evidence are immutable replay inputs only.
- Retained/frozen/cancelled worktrees, dependencies/locks/node_modules, release output, push,
  publication, restart, reset, restore, clean, discard, force removal, or destructive cleanup.

## Locked Paths

After separate approval and A acceptance, every B May Touch contract/helper/ledger/fixture/test path
is exclusively locked to B. Board remains primary Planner/Integrator-only. No parallel exception,
second implementation owner, or product-lane overlap is permitted.

## Validation Matrix

1. exact unchanged command inputs/evidence -> reusable; affected command -> required rerun;
2. authority/API/persistence bounded fix reruns dependent commands but not independent frontend;
3. schema/migration, public breaking contract, shared-owner drift, or unprovable closure -> full;
4. missing/ambiguous/mismatch/stale/unknown/dirty/ancestry/evidence drift -> full;
5. no override/force/ignore/assume flags exist;
6. TASK_368E replay reruns backend B1/API/authority/dependencies and reuses frontend 61/build;
7. QA executes final full frozen matrix including frontend 61/build despite Reviewer reuse;
8. Windows slash/backslash node IDs canonicalize and deselect collection is verified;
9. manifest argv arrays execute without shell evaluation or injection;
10. read-only frontend runtime matches lock/runtime/executable hashes; mismatch blocks; no install;
11. every shard has isolated temp/cache/coverage/frontend cache/dist and one immutable HEAD;
12. missing/duplicate/stale/failed shard blocks deterministic aggregate;
13. result metadata/digests are complete and deterministic;
14. unchanged baseline debt uses Git blobs/ledger without full base archive;
15. ledger/source/test/fixture drift or expiry requires fresh baseline comparison and blocks;
16. Integrator differential path requires all QA/merge/package/drift bindings;
17. merge conflict/dependency/environment/fixture/lock/package/unknown drift -> full validation;
18. WIP/token/worktree/roles, A contract, V2, product, remote, and real data remain unchanged;
19. Reviewer command executions reduce by >=40% in the controlled TASK_368E medium pilot;
20. pilot records command count, Planner transitions, context bytes, wall-clock, retries, and actual
    pass/fail; missing performance target blocks acceptance.

## Performance Baseline And Acceptance

User-audited TASK_368E baseline: Developer `~46.3m`, first Reviewer `~23.2m`, bounded fix
`~12.2m`, Reviewer re-gate `~13m`, QA `>23m`, routine Planner transitions `~32m`; frontend full
Reviewer and QA paths each included `61` tests plus build. Board/context baselines are owned by A.

B acceptance requires:

- Reviewer executes <=4 of the seven frozen replay command groups (>=40%; target `42.9%`);
- QA executes all seven frozen replay command groups (`7/7`) at final reviewed HEAD;
- frontend 61 tests/build are not re-executed by Reviewer but are re-executed by QA;
- no full base archive for unchanged committed debt;
- zero Windows node-selection errors and zero lane dependency installs;
- role-local shards retain one immutable HEAD, one owner/token, isolated artifacts;
- Integrator avoids full QA repetition only on exact differential proof;
- Developer/Reviewer/QA/Integrator evidence records before/after command count, Planner transition
  count, context bytes, wall-clock, retries, and result digests;
- a controlled medium TASK_368E replay pilot executes real commands after implementation, not
  only static/synthetic assertions, and writes measured results to Integrator evidence.

Correctness without the quantitative pilot and target is not acceptance.

## Planned Lane And Gates

- Lane: `task-governance-regate-evidence-reuse-baseline-ledger-and-validation-runner`
- Branch: `lane/task-governance-regate-evidence-reuse-baseline-ledger-and-validation-runner`
- Sibling worktree:
  `D:\PythonProject\connlab-worktrees\task-governance-regate-evidence-reuse-baseline-ledger-and-validation-runner`
- Planning base: `cdb96b4ed80143ba40d571615282f0ee95708a0f`
- Worktree creation base: future B approval-governance HEAD after A acceptance.
- Route: A accepted -> separate User approval -> Developer -> Reviewer -> mandatory QA ->
  Integrator.
- Reviewer performs a full review of B and cannot use B to reduce its own gate. QA executes the
  complete final matrix. Integrator requires the real controlled medium pilot and quantitative
  target before local acceptance.

No branch/worktree exists or is authorized at this planning gate.

## Compatibility And Rollback

- Reuse is opt-in/versioned. Missing manifests and all existing tasks retain full re-gate.
- Runner never replaces arbitrary task commands; manifests are reviewed task contracts.
- Ledger entries do not waive failures and expire/fail closed on drift.
- Local Git revert disables helpers/contracts; removing an opt-in manifest returns to full re-gate.
- A's transition/context authority remains unchanged and must be revalidated as a dependency.

## Stop Point

Keep B planned and serially blocked. Do not seek B approval or implementation before A local
Integrator acceptance; then require separate User approval of this exact package.
