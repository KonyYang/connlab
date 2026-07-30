# TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD Planner Reconciliation Evidence

Date: 2026-07-30
Role: Planner
Status: `planned_ready_for_review`
Task: `TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD`
Lane: `browser-release-frontend-freshness-instance-guard`
Planning base: `02517ba968f1a16d5ddda6ba038411ef4133226d`
Predecessor review:
`docs/lane_evidence/TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD_reviewer.md`

## Anti-Skip

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current task status remains `planned` / `planned_not_approved`.
- Reviewer gate result was `reviewer_plan_blocked`, NEXT Planner.
- Allowed work: bounded corrections to task, plan, Planner evidence, board, and bundle only.
- Not performed: product/release implementation, branch/worktree/role creation, approval, commit,
  push, fetch, cleanup, archive, release build, server/browser launch, `dist_release/**` mutation,
  real data access, or Controlled Lane V2 action.

## Discovery Gate Reconciliation

### Confirmed by User

- The copied full Windows 11 browser release must not connect to an old ConnLab service or wrong
  frontend instance.
- Acceptance must distinguish old process, wrong URL/port, stale frontend build, browser cache, and
  incomplete copy without presuming one unique historical cause.
- Planning must include frontend freshness, final package guard, release identity, port/instance
  handling, fail-closed launcher, server identity read-back, zero-technical operator steps,
  automation, and a second Windows 11 smoke.
- Production launcher may only explain and stop. Termination, forced takeover, replacement, and
  alternate-port behavior are not authorized.

### Confirmed by repository/release evidence

- Current and inspected packaged frontend entry JS are hash-identical and contain `Export Matrix`.
- Current Matrix export control is always rendered, though state may disable it.
- Current launcher opens a bare fixed URL after a delay without bind/process/identity proof.
- Current build can reuse frontend output, checks one historical phrase, broadly cleans
  intermediate paths, and deletes a same-name final release.
- Current global `/health` is only `{"status":"ok"}`.
- Historical release identity is absent.
- The inspected onedir release contains 1,275 files, including 1,263 required non-frontend
  `_internal` runtime/package/data files.
- Frozen runtime `app_root` is `_MEIPASS`; outer root is executable parent and has no current
  `PackagedRuntimePaths` field.
- Fee child mode currently returns before normal web-server startup.
- Static fallback preserves unknown API 404 but has no exact cache contract.

### Planner inference

- The available release proves the accepted button asset exists, not which process/tree/browser
  response was observed.
- Complete release inventory is required; frontend and selected critical files cannot prove that a
  copied PyInstaller onedir runtime is complete.
- A generic health response cannot identify a legacy ConnLab listener.
- Access-denied or conflicting owner evidence must degrade to `occupied_unverified`, not a guessed
  diagnosis.
- An explicit outer release-root path is the bounded fix for manifest ownership.

### Still unconfirmed

- The incident workstation's exact prior listener, URL, and cache history.
- Corporate antivirus/storage hashing performance and PowerShell enforcement behavior.

These unknowns no longer leave implementation contracts ambiguous: the plan freezes conservative
behavior and makes the second corporate-image Windows 11 smoke a hard QA gate. They prevent a
historical root-cause claim, not Reviewer re-gating.

## Reviewer Finding Closure Matrix

### Finding 1 - Legacy occupant classification

Corrected contract:

- Ordered read-only outcomes are
  `guarded_connlab_valid`, `identity_malformed_or_spoof_like`,
  `legacy_connlab_verified`, `unknown_listener_verified`, then `occupied_unverified`.
- Valid guarded identity requires strict schema, bounded content type/size, digest formats,
  loopback binding, and PID.
- Verified legacy requires identity absence, safe listener PID, readable existing executable path
  with basename `ConnLab_Server.exe`, exact health JSON, and ConnLab HTML plus same-origin resource
  signature. Health alone is insufficient.
- Safe proof failure, timeout, access denial, conflicting listener/PID, or incomplete signature is
  `occupied_unverified`.
- Operator copy never reports old ConnLab unless verified; support diagnostics are separate and
  bounded.
- Every occupied result fails closed with no browser, reuse, port change, termination, or
  replacement.

Affected files/tests:

- new `packaging/Start_ConnLab.ps1`;
- `scripts/smoke_windows_browser_release.ps1`;
- new `tests/unit/test_browser_release_occupant_contract.py`;
- exact launcher static assertions in `tests/unit/test_desktop_release_scripts.py`.

Acceptance:

- deterministic valid guarded, verified legacy, verified unknown, malformed/spoof-like, and
  unverified fixtures all stop;
- generic health-only fixture is `occupied_unverified`;
- every fixture asserts no browser/start reuse/port switch/kill.

### Finding 2 - Whole-release completeness

Corrected contract:

- `release-manifest.json` is the sole inventory exclusion.
- Canonical inventory covers every file and directory in the outer tree: EXE, launchers, docs,
  complete `_internal` runtime/packages/data/frontend.
- Canonical records are UTF-8 no BOM
  `type<TAB>path<TAB>length<TAB>lowercase_sha256<LF>`, sorted by ordinal UTF-8 path.
- Reparse, traversal, absolute/drive/UNC, duplicate Windows-case, type drift, forbidden control
  characters, missing, altered, and extra entries fail.
- A separate frontend digest and `Export Matrix` capability remain mandatory supplements.
- Launcher and server each reconstruct the complete inventory within a 60-second wall-clock budget.
- Index validation covers icon, preload, modulepreload, script, and stylesheet local references.
- PowerShell and Python share compatibility fixtures.

Affected files/tests:

- `scripts/build_windows_browser_release.ps1`;
- new `backend/desktop/browser_release_manifest.py`;
- new launcher, `backend/desktop/packaged_server.py`, and `backend/desktop/packaged_static.py`;
- new `tests/unit/test_browser_release_manifest.py`;
- new `tests/integration/test_browser_release_manifest_compatibility.py`;
- focused static/server tests.

Acceptance:

- missing/altered/extra non-frontend runtime cases fail before normal startup;
- duplicate/traversal/reparse/type cases fail;
- every local index reference is present and hashed;
- PowerShell/Python fixture produces identical full/frontend digests and release ID;
- timeout/read failure is a hard error.

### Finding 3 - Outer release-root contract

Corrected contract:

- `PackagedRuntimePaths` gains immutable injectable `release_root`.
- Frozen `release_root` is `Path(sys.executable).resolve().parent`.
- Frozen `app_root` remains resolved `_MEIPASS`.
- Non-frozen release root defaults to resolved app root.
- Manifest lookup is outer-root relative.
- `packaging/connlab_browser_server.spec` remains read-only.
- Fee child returns before argument parsing, runtime-path construction, manifest read, app import,
  or Uvicorn startup and preserves JSON-only stdout.

Affected files/tests:

- `backend/desktop/runtime_paths.py`;
- `backend/desktop/packaged_server.py`;
- `tests/unit/test_desktop_packaged_runtime_paths.py`;
- `tests/unit/test_desktop_packaged_server.py`.

Acceptance:

- frozen and injected path tests prove outer root versus `_internal`;
- server finds outer manifest without spec changes;
- fail-fast normal-loader doubles are untouched in Fee child test and stdout is JSON-only.

### Finding 4 - Publishable provenance/collision

Corrected contract:

- Publishable source policy is clean committed tree only.
- Git porcelain with tracked and untracked non-ignored files must be empty before build and before
  manifest generation.
- Manifest uses full `source_commit` and `source_state: clean_committed`; no dirty Boolean.
- Release ID binds release name, version, source commit, full-tree digest, and frontend digest.
- Existing final release path is a hard error before any final mutation and is checked again before
  the one-time complete move.
- Cleanup is limited to the resolved exact task intermediate root under
  `tmp/browser-release-build/<ReleaseName>` after path/reparse validation. Existing `build`, `dist`,
  and `dist_release` are never cleanup targets.

Affected files/tests:

- `scripts/build_windows_browser_release.ps1`;
- manifest module;
- `tests/unit/test_desktop_release_scripts.py`;
- `tests/unit/test_browser_release_manifest.py`.

Acceptance:

- clean tree accepted; tracked/untracked dirty rejected;
- deterministic identity vectors pass;
- repeated release name preserves existing sentinel exactly;
- only validated intermediate cleanup target is admitted.

### Finding 5 - Exact cache/operator entry

Corrected contract:

- `/`, `/index.html`, query variants, every SPA fallback, and identity use
  `Cache-Control: no-store`.
- Manifest-listed validated hashed `/assets` files use
  `Cache-Control: public, max-age=31536000, immutable`.
- Every manifest-listed non-hashed static file uses `Cache-Control: no-cache`.
- Unknown `/api/**` remains JSON 404 and uses `Cache-Control: no-store`.
- Identity is mounted before static fallback.
- Operator docs contain no manual bare-URL fallback.
- Browser opens only after recorded-PID identity equality, at the release-query URL.

Affected files/tests:

- `backend/desktop/browser_release_identity.py`;
- `backend/desktop/packaged_static.py`;
- `backend/desktop/packaged_server.py`;
- launcher and operator docs;
- `tests/unit/test_browser_release_identity.py`;
- exact updates in packaged static/server tests.

Acceptance:

- exact headers pass for direct/query entry, index, Matrix fallback, identity, hashed asset,
  non-hashed icon/static, and unknown API;
- unknown API never returns shell;
- no operator instruction or launcher branch opens a bare/manual address.

### Finding 6 - PowerShell/smoke cleanup

Corrected contract:

- BAT command is exactly
  `powershell.exe -NoLogo -NoProfile -NonInteractive -WindowStyle Normal -ExecutionPolicy Bypass -File "%~dp0Start_ConnLab.ps1" -ReleaseRoot "%~dp0"`.
- BAT uses its own current folder, quotes paths, keeps failure visible, and propagates exit code.
- `Bypass` is process-scoped only. Global `Set-ExecutionPolicy`, registry mutation, broader policy
  weakening, download, and unsigned helper fallback are forbidden.
- Policy copy tells the operator to contact support and not change security settings.
- Automated smoke uses `try/finally`, terminates only its recorded PID after exact release identity
  proves ownership, never targets a pre-existing occupant, waits at most 15 seconds, records
  cleanup, and fails on cleanup failure.
- There is no accepted retained-process alternative.
- Second Windows 11 corporate image is a hard QA gate.

Affected files/tests:

- `packaging/Start_ConnLab.bat`;
- new `packaging/Start_ConnLab.ps1`;
- `scripts/smoke_windows_browser_release.ps1`;
- operator docs;
- exact release-script tests and occupant contract tests.

Acceptance:

- static tests freeze flags, quoting, folder binding, exit propagation, forbidden policy/process
  operations, and policy copy;
- pre-existing occupant is never a cleanup target;
- verified-owned process closes in finally;
- cleanup failure blocks smoke;
- corporate-image smoke passes all required cases.

## Scope / Ownership Check

### May Touch after future approval

The corrected formal task now explicitly includes:

- browser build/smoke scripts;
- BAT plus a new bounded PowerShell launcher;
- browser operator documents;
- bounded manifest and identity modules;
- `runtime_paths.py`, packaged server/static;
- exact focused test hunks and four bounded independent test modules;
- task/plan/evidence/board/bundle governance.

### Must Not Touch

- product frontend/Matrix behavior, global `/health`, business APIs/services, Fee behavior, LTR,
  Office, schema/database, user/authority data;
- Vite/PyWebView, installer/updater, LAN/multi-user/permissions;
- existing release artifacts and unrelated dirty files;
- V2 frozen assets.

### Locked/shared ownership

- One future isolated lane owns all release implementation paths.
- Planner/Integrator share governance files.
- Existing `dist_release/**` is read-only.
- Any path/authority overlap serializes the lane; new tests remain bounded.

## Definition of Ready

Result: `ready for same Reviewer plan re-gate`, not ready for implementation.

Present:

- confirmed User target, repository facts, Planner inference, and remaining unknowns are separated;
- diagnosis does not presume a unique root cause;
- all six Reviewer contracts are frozen rather than deferred;
- exact May Touch, Must Not Touch, locked paths, dependency, ownership, validation, merge, risk,
  rollback, and non-goal boundaries exist;
- operator flow is zero-technical and does not use cache clearing as a universal fix;
- process termination remains prohibited in production; smoke-only cleanup is exact-owned and
  acceptance-bound;
- corporate-image Windows 11 QA is hard;
- task remains planned and no implementation authority is claimed.

Still required:

1. same Reviewer passes this corrected plan;
2. User explicitly approves the exact passed plan;
3. only then may task-specific implementation role/worktree/base be created and recorded.

## Governance Checkpoint

- Task and plan revisions contain the six frozen corrections.
- Historical Planner evidence points to this durable reconciliation evidence.
- Board header, Active Execution Model, lane row, bundle evidence list, and last handoff are updated
  to Reviewer re-gate while retaining `planned_not_approved`.
- Exact native IDs retained:
  - Controller: `019fb32a-ff19-7170-b87f-f77f12bddff6`;
  - Planner: `019fb330-a311-7af3-8977-ad14fe48260b`;
  - Reviewer: `019fb343-5d7e-77f3-a861-c8e92c94013f`.
- Developer, QA, Integrator, base, branch, worktree, reviewed commit, and accepted commit remain
  `null`.

## Reconciliation Validation

- `git rev-parse HEAD` remains
  `02517ba968f1a16d5ddda6ba038411ef4133226d`; no commit was created.
- Strict UTF-8 decoding with invalid-byte rejection passed for task, plan, both Planner evidence
  files, board, and bundle.
- The same files contain no Unicode replacement character and no trailing whitespace.
- Contract-marker scan found all ordered occupant outcomes, complete/frontend tree digests,
  `release_root`, clean committed provenance, collision behavior, three exact cache policies,
  process-scoped `-ExecutionPolicy Bypass`, `try/finally`, and corporate-image gate.
- Bundle invariant read-back passed for `state: planned`, `approval_state: planned_not_approved`,
  `reviewer_plan_re_gate`, and all downstream/base/branch/worktree/reviewed/accepted null fields.
- `git diff --check` passed for the tracked board/bundle changes; only the repository's normal
  LF-to-CRLF advisory was emitted.
- Scoped status contains only this task's task/plan/Planner evidence plus board/bundle governance.
  Pre-existing unrelated modified governance/test paths and the untracked Reviewer evidence were
  preserved and not cleaned, staged, committed, or altered by this reconciliation.
- No product, release script, packaging, backend, frontend, test implementation, generated release,
  or real-data path was modified in this Planner reconciliation.

## Next Legal Role

Same Reviewer plan re-gate only. A pass returns to the User for explicit approval; it does not
authorize implementation.

NEXT: Reviewer
BLOCKER: none
