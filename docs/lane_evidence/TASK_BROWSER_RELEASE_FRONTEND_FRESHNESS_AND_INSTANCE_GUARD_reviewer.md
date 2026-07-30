# TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD Reviewer Evidence

Date: 2026-07-30
Role: Reviewer
Status: `reviewer_plan_blocked`
Task: `TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD`
Lane: `browser-release-frontend-freshness-instance-guard`
Planning base: `02517ba968f1a16d5ddda6ba038411ef4133226d`

## Anti-Skip

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current task state: `planned`; Reviewer plan gate and explicit User approval are still required.
- Allowed action: independent plan review and this Reviewer evidence only.
- Forbidden action observed: no implementation, approval, Developer/QA/Integrator creation,
  branch/worktree creation, commit, push, cleanup, archive, release build, server launch, browser
  launch, or Controlled Lane V2 action.
- Next legal role after this blocking review: Planner.

## Scope And Inputs Reviewed

The review read the required governance, task, plan, Planner evidence, bundle, product/design,
frontend architecture, and parallel-lane protocols. It also inspected the current:

- browser release build and smoke scripts;
- BAT launcher and operator documents;
- PyInstaller browser spec;
- packaged server, static mount, runtime paths, and global `/health`;
- focused packaged runtime/static/server/release tests;
- RELEASE_003 packaging task and plan;
- TASK_355B packaged Fee child-mode plan and accepted code;
- TASK_367A task, current `Export Matrix` code/test, and accepted Reviewer/QA/Integrator evidence;
- current `frontend/dist` and the read-only 202607270802 release artifact.

`$impeccable` product guidance was applied only to operator flow, error copy, browser behavior, and
frontend smoke review. It did not expand UI or product scope.

## Verified Baseline

- Primary `HEAD` is the recorded planning base
  `02517ba968f1a16d5ddda6ba038411ef4133226d`.
- No branch or worktree exists for this task.
- The primary changes are limited to planned governance files. No product/release implementation
  path is changed.
- Board, task, plan, Planner evidence, and bundle consistently keep the task `planned` and
  `planned_not_approved`.
- Bundle values remain: Developer `null`, QA `null`, Integrator `null`, base/branch/worktree
  `null`, and reviewed/accepted commits `null`.
- Current `frontend/dist` and the inspected 202607270802 packaged frontend each contain seven files
  with zero inventory/hash drift.
- Both inspected entry JS files have SHA-256
  `6BDF5A2EDE105188724E8F8E3789B64D5888BFEC85903FC5B3415EE31C0E5F61`
  and contain `Export Matrix`.
- The full inspected release has 1,275 files. Only seven are frontend files; 1,263 are other
  `_internal` runtime files.
- Current packaged `/health` remains only `{"status":"ok"}`. Existing historical releases have no
  browser release identity endpoint.
- Current Fee child mode is routed before normal web-server startup and must remain unchanged.

## Findings

### Blocking 1: the old-process classifier cannot identify the historical release involved in the incident

Plan section 3 classifies an old ConnLab process through a different identity/PID response, while
section 4.6 only says an occupied port is identified "if possible." The identity endpoint is new.
The existing releases that can already occupy `8765` expose only generic `/health`, so the proposed
preflight cannot distinguish a legacy ConnLab server from an unknown listener. The manual smoke
starts a previous release but does not define how the launcher proves which category it observed.

Required Planner correction:

1. Freeze an ordered, read-only occupant classification contract for:
   - a prior guarded ConnLab release with valid identity;
   - a legacy ConnLab release without identity;
   - an unknown listener;
   - a malformed or spoof-like identity response.
2. Name the exact evidence used for legacy recognition, such as listener PID plus executable
   identity/path and a bounded legacy HTTP signature. A generic `{"status":"ok"}` alone is not
   sufficient proof.
3. If legacy identity cannot be proven safely, label it `occupied_unverified` instead of claiming
   an exact old-ConnLab diagnosis, keep the operator action business-readable, and preserve support
   diagnostics separately.
4. Add deterministic tests/smokes for all four cases. Every occupied-port case must stop without
   opening a browser, reusing the service, changing port, or terminating anything.

### Blocking 2: the copy-completeness manifest omits most required packaged runtime content

Plan sections 4.2 and 4.3 cover the frontend tree plus an EXE, launchers, index, and entry assets.
The inspected onedir release contains 1,263 non-frontend `_internal` files, including the Python
runtime, DLLs, extension modules, packages, and bundled data. Removing one of those files would not
fail the proposed launcher preflight; it would reach EXE start and be reported as a generic startup
failure. That does not satisfy the planned whole-folder completeness classification.

Required Planner correction:

1. Define a canonical inventory/digest for the complete final release tree, excluding only the
   manifest itself and any explicitly named generated/mutable file that is not part of the copied
   release.
2. Keep the dedicated frontend tree digest and capability probe, but do not use them as a
   substitute for the complete release inventory.
3. Make both launcher and packaged server validate the relevant complete inventory before normal
   startup. Define a bounded startup-time budget for hashing.
4. Parse and validate every local `index.html` resource reference, including icon, preload,
   modulepreload, script, and stylesheet references, not only script/style entry assets.
5. Add missing/altered non-frontend runtime-file tests, extra-file policy tests, duplicate/path
   traversal tests, and cross-language PowerShell/Python manifest compatibility coverage.

### Blocking 3: external manifest path ownership is unresolved against the real PyInstaller path contract

The plan places `release-manifest.json` at the outer release root. Current packaged
`default_app_root()` resolves to `sys._MEIPASS`, which is the `_internal` resource root, and
`PackagedRuntimePaths` has no outer release-root field. Plan section 7 leaves
`backend/desktop/runtime_paths.py` read-only unless Developer later proves a hunk is needed. The
path mismatch is already proven at this gate and must not be deferred into implementation.

Required Planner correction:

1. Freeze one explicit outer release-root contract. The recommended bounded change is an immutable
   `release_root` in `PackagedRuntimePaths`, resolved from `Path(sys.executable).parent` in frozen
   mode and injectable in tests, while `app_root` continues to represent `_internal`.
2. Authorize the exact minimal `backend/desktop/runtime_paths.py` and
   `tests/unit/test_desktop_packaged_runtime_paths.py` hunks if that design is selected.
3. State whether `packaging/connlab_browser_server.spec` remains read-only after the corrected path
   design.
4. Prove Fee child mode returns before manifest/path loading and preserves JSON-only stdout.

### Blocking 4: publishable-source provenance and release-folder collision behavior are not frozen

The manifest records only `source_commit` plus a Boolean `source_dirty`. A dirty backend/package
source can therefore produce a different EXE without a canonical source-state identity. The
proposed `release_id` includes only release name, source commit, and frontend digest. In addition,
the current build script deletes an existing release folder with the same name, while the task
locks every existing release folder read-only.

Required Planner correction:

1. Choose one publishable-source policy before User approval:
   - recommended: require a clean committed source tree and fail closed when dirty; or
   - define a canonical full source fingerprint and explicit dirty-build authorization that is
     incorporated into release identity.
2. Make an existing final release folder a hard collision error. Do not remove, replace, or merge
   into it.
3. Keep deletion limited to explicitly bounded intermediate PyInstaller build/dist paths after
   their resolved targets are verified.
4. Add tests for dirty source, clean source, repeated release name, existing-folder preservation,
   and deterministic identity inputs.

### Blocking 5: cache behavior and the verified operator entry are still alternatives, not one contract

Plan section 4.5 says hashed assets may be immutable "only after" validation and otherwise use
`no-cache`, but it does not freeze exact header values or the policy for non-hashed static files.
The current operator README also tells the operator to type the bare URL when the browser does not
open, which bypasses the planned identity read-back and release-query entry.

Required Planner correction:

1. Freeze exact response headers for `/`, `/index.html`, every SPA fallback, identity, hashed
   assets, and non-hashed static files.
2. Recommended contract:
   - entry, fallback, and identity: `Cache-Control: no-store`;
   - manifest-validated content-hashed assets:
     `Cache-Control: public, max-age=31536000, immutable`;
   - non-hashed static files: `Cache-Control: no-cache`.
3. Require the identity route to be mounted before static fallback and retain API 404 behavior.
4. Remove bare-URL/manual-address fallback from operator guidance. Browser opening occurs only
   after identity/PID read-back; failure stays in the launcher with business-readable guidance.
5. Add exact-header tests for direct entry, query entry, Matrix SPA fallback, identity, hashed
   asset, non-hashed file, and unknown API route.

### Blocking 6: PowerShell execution policy and disposable smoke cleanup remain ambiguous

The plan says the BAT uses the "least broad local-file mode" but does not name the command or
whether a process-scoped execution-policy override is approved. This is a core target-Windows
behavior that the User must approve knowingly. The generated-artifact gate also says a disposable
process may be retained if cleanup is considered outside approval, which would make repeated smoke
non-reproducible and can create the exact occupied-port condition under test.

Required Planner correction:

1. Freeze the exact BAT-to-PowerShell command, profile/noninteractive behavior, exit-code
   propagation, quoting, and current-folder binding.
2. State explicitly whether a process-scoped `-ExecutionPolicy` value is used. Forbid global
   `Set-ExecutionPolicy`, registry mutation, policy weakening outside the child PowerShell process,
   hidden download, or unsigned helper binary fallback.
3. Define one business-readable policy-blocked message and make the second-Windows-11 corporate
   image smoke a hard QA gate.
4. Require automated smoke to use `try/finally` and terminate only the exact disposable process it
   created after verifying recorded PID plus release identity. A pre-existing occupant is never a
   cleanup target.
5. Record cleanup outcome and fail smoke if the owned disposable process cannot be closed. Remove
   the alternative that intentionally leaves it running.

## Non-Blocking Observations

- Rejecting unverified `-SkipFrontendBuild` for the publishable path is the correct bounded choice.
- The package-only endpoint before SPA fallback can preserve global source `/health`, existing API
  ordering, and SPA behavior once the release-root contract is explicit.
- PID plus release/frontend read-back closes the bind race for a newly started process when the
  launcher also verifies that the recorded process remains alive.
- The operator copy is short and business-readable. It correctly excludes cache clearing, port/PID
  inspection, JSON reading, Task Manager, developer commands, automatic termination, port takeover,
  and silent reuse.
- New bounded test modules, existing-test exact hunks, locked paths, manual Win11 smoke, rollback,
  and role/merge gates are otherwise appropriately scoped.

## Checklist Result

- Architecture: package-only identity/static changes are directionally valid; the external
  release-root dependency must be made explicit.
- Scope: no product frontend, Matrix, Fee, LTR, Office, schema, database, global `/health`, Vite,
  PyWebView, installer, LAN, permissions, or multi-user expansion was found in the plan.
- Design: the freshness chain is sound in principle, but manifest completeness, provenance,
  cache values, legacy occupant classification, and launcher policy are not implementation-ready.
- Runtime: Fee child ordering and SPA/API boundaries are preserved in the intended design; the
  six blocking contracts prevent reproducible acceptance today.
- Code quality: the proposed bounded Python/PowerShell modules and focused tests are appropriate;
  no implementation was reviewed or authorized.

## Gate Result

`reviewer_plan_blocked`

This plan must return to Planner for the six bounded corrections above. A corrected plan requires
another Reviewer plan gate. A future Reviewer pass would mean only that the exact corrected plan
may be submitted to the User for explicit approval; it would not authorize implementation.

NEXT: Planner
BLOCKER: legacy occupant classification, whole-release inventory, outer release-root wiring,
publishable provenance/collision, exact cache/operator entry, and PowerShell/smoke cleanup
contracts are not closed.

## Reviewer Plan Re-Gate

Date: 2026-07-30
Current status: `reviewer_plan_pass`
Reconciliation evidence:
`docs/lane_evidence/TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD_reconciliation_planner.md`

This section supersedes the first-gate result for current routing. The historical blocking
findings above remain unchanged as the audit record of why Planner reconciliation was required.

### Re-Gate Anti-Skip

- Phase remains `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Task and bundle remain `planned` / `planned_not_approved`.
- Board and bundle route only `reviewer_plan_re_gate`.
- Developer, QA, Integrator, base commit, branch, worktree, reviewed commit, and accepted commit
  remain `null`.
- No branch or worktree exists for this task.
- No product/release implementation path has a current diff.
- This re-gate performed no implementation, approval, role/worktree creation, commit, push,
  cleanup, archive, release build, service/browser launch, real-data access, or Controlled Lane V2
  action.
- The pre-existing ambient AGENTS/orchestration/governance-test changes were read only where
  required and were not modified, attributed, cleaned, staged, or used to expand this task.

### Independent Re-Gate Findings

#### Blocking

None.

#### Non-Blocking

- The 60-second complete-tree verification budget remains a measured acceptance fact for the
  second Windows 11 corporate-image QA gate. The corrected plan properly fails closed rather than
  allowing an implementation-time bypass.
- Current source still contains historical bare-URL and fixed-delay server guidance because this
  is a plan-only gate. The corrected operator-entry contract and implementation scope cover its
  removal. Implementation review must compare all operator-visible release guidance, including
  launcher, README, release notes, and packaged-server console output, against the frozen
  verified-query-only contract.
- Strict extra-file rejection can make copied folders sensitive to third-party file injection.
  This is intentional integrity behavior and is explicitly covered by risk and corporate-image
  QA.

### Finding 1 Re-Gate: Occupant Classifier

Pass.

- The contract has one ordered result set:
  `guarded_connlab_valid`, `identity_malformed_or_spoof_like`,
  `legacy_connlab_verified`, `unknown_listener_verified`, and
  `occupied_unverified`.
- Guarded identity is bounded by content type, size, strict schema, digest/binding consistency,
  loopback host/port, and numeric PID.
- Legacy identity requires identity absence/404, safe listener PID, readable existing
  `ConnLab_Server.exe` path, exact health JSON, ConnLab HTML, and a fetchable same-origin local
  resource.
- Generic health alone, denied process evidence, timeout, conflict, or incomplete signature is
  `occupied_unverified`.
- Operator text and support diagnostics are separated, so an unverified occupant is never called
  an old ConnLab instance.
- Every occupied outcome returns nonzero with no browser, EXE start, reuse, port change,
  replacement, or termination.
- Deterministic fixtures cover all five outcomes plus the health-only negative boundary.

### Finding 2 Re-Gate: Whole-Release Inventory

Pass.

- `release-manifest.json` is the sole inventory exclusion.
- Inventory covers the EXE, launchers, operator documents, every directory, and all `_internal`
  runtime/package/data/frontend files.
- Canonical records freeze type, relative path, length, lowercase SHA-256, LF, UTF-8 without BOM,
  ordinal UTF-8 sorting, and Windows case-insensitive uniqueness.
- Absolute, drive, UNC, traversal, control-character, duplicate, reparse, type-change, extra,
  missing, and altered cases fail closed.
- Full-tree and independent frontend-tree digests are both required.
- Launcher and server independently validate within a 60-second wall-clock budget.
- HTML validation covers icon, preload, modulepreload, stylesheet, and script local references,
  including query/fragment normalization and external/traversal rejection.
- Shared PowerShell/Python byte-vector compatibility tests and non-frontend runtime damage tests
  close the cross-language and partial-copy boundaries.

The read-only artifact check still supports this scope: the inspected release has 1,275 files,
including 1,263 non-frontend `_internal` files, while source and packaged frontend each have seven
files and the same accepted entry hash.

### Finding 3 Re-Gate: Outer Release Root And Fee Child

Pass.

- `PackagedRuntimePaths.release_root` is immutable and injectable.
- Frozen `release_root` is the resolved EXE parent; frozen `app_root` remains resolved
  `sys._MEIPASS`.
- Non-frozen release root follows app root unless injected.
- Manifest lookup is explicitly outer-root relative.
- `runtime_paths.py` and its focused tests are May Touch.
- `packaging/connlab_browser_server.spec` is explicitly read-only.
- Fee child mode returns before argument parsing, runtime-path construction, manifest read,
  FastAPI application import, or Uvicorn startup, with argv, return code, and JSON-only stdout
  regression coverage.

This matches the current code boundary: current `default_app_root()` represents `_MEIPASS`, and
current Fee child dispatch already precedes the normal server path.

### Finding 4 Re-Gate: Provenance, Collision, And Cleanup

Pass.

- Publishable builds require a full clean committed Git tree both before build and immediately
  before manifest generation.
- Tracked changes and untracked non-ignored files from porcelain v1 are blockers.
- Manifest provenance is full `source_commit` plus `source_state: clean_committed`; dirty Boolean
  provenance is removed.
- Release identity binds release name, version, source commit, full-tree digest, and frontend
  digest.
- `-SkipFrontendBuild` cannot produce publishable success.
- A same-name final folder is a hard error before mutation and is checked again before the single
  final move.
- Existing `build`, `dist`, and `dist_release` are not cleanup targets.
- Deletion is limited to one resolved, leaf-checked, reparse-checked task intermediate under
  `tmp/browser-release-build/<ReleaseName>`.
- Tests freeze dirty/clean source behavior, deterministic identity, same-name sentinel
  preservation, and exact cleanup target admission.

### Finding 5 Re-Gate: Cache And Verified Operator Entry

Pass.

- `/`, `/index.html`, query variants, all SPA fallback, and identity are exactly `no-store`.
- Manifest-listed reviewed content-hashed assets are exactly
  `public, max-age=31536000, immutable`.
- Manifest-listed non-hashed static files are exactly `no-cache`.
- Unknown `/api/**` is JSON 404 with `no-store`, never SPA HTML.
- Identity is mounted before static fallback; global source `/health` remains unchanged.
- Browser opening requires the newly recorded process to remain alive and identity PID, release,
  full/frontend digests, capability, host, and port to match.
- The only launcher-opened address is the URL-encoded release-query URL.
- Operator guidance removes manual bare-address and cache-clearing fallback and retains concise,
  business-readable stop messages.
- Exact direct/query/index/Matrix/identity/hashed/non-hashed/API tests are declared.

The `$impeccable` product check passes: the operator flow is direct, operational, and does not
require technical stack, PID, port, JSON, Task Manager, cache, or security-policy knowledge.

### Finding 6 Re-Gate: BAT, PowerShell, And Smoke Cleanup

Pass.

- The exact BAT command freezes `NoLogo`, `NoProfile`, `NonInteractive`, `WindowStyle Normal`,
  child-process-only `ExecutionPolicy Bypass`, quoted script/release paths, current-folder binding,
  visible failure, and exit-code propagation.
- Global policy mutation, registry writes, broader weakening, download, and unsigned helper
  fallback are forbidden.
- Policy-blocked copy directs the operator to support and explicitly says not to change Windows
  security settings.
- Smoke cleanup is mandatory `try/finally`.
- Termination is limited to the exact smoke-created PID only after live identity proves both PID
  and expected release ID.
- A pre-existing occupant is never a cleanup target.
- Owned cleanup is bounded to 15 seconds, recorded, and failure blocks smoke. There is no accepted
  retained-process success branch.
- Production launcher termination/reuse/replacement remains prohibited.
- The second Windows 11 corporate-image smoke is a hard QA gate and includes all classifier,
  damage, cache, policy, and cleanup cases.

### Finding To Execution Mapping

Pass.

The corrected plan includes a one-to-one finding matrix from each historical blocking finding to:

1. one frozen contract;
2. explicit implementation files;
3. bounded unit/integration/static tests;
4. generated-artifact acceptance;
5. second-machine QA where environment evidence is required.

`May Touch`, `Must Not Touch`, locked paths, shared governance ownership, independent new tests,
validation, merge gate, rollback, and non-goals are concrete. Product frontend, Matrix/Fee/LTR/
Office/schema/database/global `/health`, PyInstaller spec, existing releases, user data, V2,
remote push, and unrelated ambient changes remain outside scope.

### Re-Gate Checklist

- Architecture: pass. Package identity remains release-only, global API health is unchanged,
  static/API ordering is explicit, and runtime root ownership is modeled rather than implicit.
- Scope: pass. No product/UI/business/data/authority expansion is authorized.
- Design: pass. Canonical manifest, ordered classifier, cache table, provenance, and cleanup
  contracts are deterministic and testable.
- Runtime: pass at plan gate. Current gaps are matched to explicit code and acceptance paths;
  implementation claims remain prohibited until later gates.
- Code quality: pass at plan gate. New behavior is assigned to bounded modules and focused tests;
  existing files receive exact hunks only.

## Current Final Gate Result

`reviewer_plan_pass`

This pass means only that the exact corrected plan may be submitted to the User for explicit
approval. It does not approve implementation, create a Developer/QA/Integrator, authorize a
branch/worktree, or permit product/release changes.

NEXT: User
BLOCKER: none
