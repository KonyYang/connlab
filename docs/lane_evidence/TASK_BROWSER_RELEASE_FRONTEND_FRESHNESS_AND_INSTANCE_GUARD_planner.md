# TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD Planner Evidence

Date: 2026-07-30
Role: Planner
Status: `historical_planner_discovery`; superseded for routing by reconciliation evidence
Task: `TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD`
Lane: `browser-release-frontend-freshness-instance-guard`
Planning base: `02517ba968f1a16d5ddda6ba038411ef4133226d`

## Anti-Skip

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Board active task at discovery start: none.
- Allowed action: User-authorized Discovery and planning governance only.
- Forbidden in this role: product/release implementation, implementation worktree, downstream
  role creation, approval, merge, push, cleanup, archive, or Controlled Lane V2 action.

## Discovery Gate

### Confirmed by User

- Solve copied Windows 11 browser releases showing an older/wrong frontend instance.
- Distinguish old process, wrong port/URL, stale build, browser cache, and incomplete copy.
- Cover build freshness, final resource guard, manifest/identity, port recognition, fail-closed
  launcher, server read-back, zero-technical operator steps, automation, and second-PC smoke.
- Do not terminate or replace old processes without a separate approval.

### Confirmed by repository evidence

- 202607270802 packaged JS and current `frontend/dist` JS share SHA-256
  `6BDF5A2EDE105188724E8F8E3789B64D5888BFEC85903FC5B3415EE31C0E5F61`.
- The packaged JS contains `Export Matrix`.
- The accepted Matrix export button is always rendered and can only be disabled by state.
- Release URL is `127.0.0.1:8765`; Vite development is `localhost:5173`.
- Current BAT starts the EXE, waits two seconds, and opens the URL with no process, port, readiness,
  release-directory, or identity proof.
- Build allows unverified frontend skip and only has a narrow old-copy negative string guard.
- Final copied frontend assets, release identity, and package completeness are not verified.
- Packaged server has only generic health and no explicit index/identity cache contract.
- RELEASE_003 accepted the fixed-port browser shell and documented occupation as a risk.
- TASK_355B demonstrates packaged code changes require rebuild and restart.
- TASK_367A accepted `Export Matrix` with focused/full frontend tests, build, and browser smoke.
- Primary HEAD matches the delegated base and status/index are clean.
- No product lane is active; Controlled Lane V2 remains frozen.

### Inferred by Planner

- Old port ownership is plausible and structurally dangerous because the browser opens even when
  the new server cannot bind, but it is not proven on the target PC.
- One canonical manifest plus independent launcher/server read-back is the narrowest way to
  classify all five categories.
- A BAT wrapper plus bounded PowerShell helper preserves the non-programmer workflow.
- Package-only identity avoids broad product API or UI changes.

### Not yet confirmed

- Exact target-PC cause.
- Corporate PowerShell policy behavior.
- User acceptance of the recommended publishable-build rule that rejects unverified skip.
- Any future desire for controlled automatic process termination.

These facts keep the task `planned`. None justifies guessing a unique root cause or approving
implementation.

## Diagnostic Conclusion

The 202607270802 release artifact itself is not missing the accepted button asset. That closes only
the narrow stale-artifact hypothesis for the inspected source folder. It does not prove which
process, URL, cached entry, or copied file set served the reported browser page.

The planned acceptance boundary therefore uses:

- build inventory and positive capability probe for stale build;
- root manifest/hash validation for incomplete copy;
- port plus identity/PID read-back for old/wrong instance;
- fixed verified URL for wrong port;
- no-store entry/identity plus release query for cache;
- second Windows 11 evidence for the real copied-folder path.

## Planning Decisions

- Recommended normal publish path always rebuilds the frontend.
- Current unverified `-SkipFrontendBuild` cannot produce a publishable success.
- Final guard checks the final release folder and requires `Export Matrix`.
- Release manifest is canonical, deterministic, non-self-hashing, and carries frontend identity.
- Package-only endpoint returns identity plus current process id with no-store.
- Any occupied port blocks startup. Existing processes are never reused, terminated, or replaced.
- Browser opens only after expected release/frontend/PID read-back.
- Operator guidance never defaults to cache clearing, port inspection, Task Manager, or developer
  commands.
- New tests are bounded modules; existing mixed tests receive only exact regressions.

## Formal Outputs

- `tasks/TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD.md`
- `docs/task_browser_release_frontend_freshness_and_instance_guard_plan.md`
- this Planner evidence
- exact planned board and active bundle routing updates

## May Touch / Must Not Touch / Locks

The formal task and plan define exact future release-shell paths. Product frontend, Matrix/Fee/LTR/
Office/data authority, global source `/health`, existing release artifacts, real operator data,
Controlled Lane V2, fetch/push/cleanup/archive, and automatic process termination remain locked.

`docs/task_board.md` and `docs/project_management/ACTIVE_TASK_THREAD_BUNDLE.md` are shared
Planner/Integrator authority. They are not future Developer whole-file inputs.

## Definition Of Ready

Result: ready for Reviewer plan gate, not ready for implementation approval.

Present:

- formal task, executable plan, evidence, goal, operator flow, scope, dependencies, locks,
  validation, merge gate, risks, rollback, and explicit non-goals.

Missing by design:

- Reviewer plan pass;
- User plan approval;
- implementation branch/worktree and fresh base binding;
- Developer/Reviewer/QA/Integrator native IDs;
- pre-implementation shared-owner rescan.

## Git / Worktree Checkpoint

- Discovery base: `02517ba968f1a16d5ddda6ba038411ef4133226d`.
- Primary branch: `master`.
- Primary status/index before planning writes: clean.
- No branch, worktree, stage, commit, push, fetch, cleanup, or archive was created/performed.
- Frozen historical V2 worktrees were listed read-only and not used.

## Planning Validation

- Planning diff is limited to the formal task, executable plan, Planner evidence, exact board
  planned-state update, and active V1-Lite bundle routing manifest.
- `git diff --check` passed; only repository line-ending conversion warnings were emitted.
- UTF-8 read-back found no replacement characters in any changed governance file.
- Changed governance files contain no trailing spaces and no em dash copy.
- Bundle read-back keeps `state: planned`, `approval_state: planned_not_approved`,
  `closeout_archive_authorized: false`, all downstream role IDs `null`, and
  branch/worktree/reviewed/accepted commits `null`.
- Scope scan found no product/release implementation file change and no approved/implementation
  authority claim.
- No release build, PyInstaller, frontend build/test, server launch, port probe, browser action,
  `dist_release/**` mutation, or real data/file operation was run in Planner.

## Next Legal Role

The first Reviewer plan gate returned `reviewer_plan_blocked` with six bounded findings. Planner
reconciled the formal task and plan without implementation and recorded the current routing evidence
at:

`docs/lane_evidence/TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD_reconciliation_planner.md`

That reconciliation freezes:

- the ordered guarded/legacy/unknown/malformed/unverified occupant contract;
- complete release-tree inventory and PowerShell/Python canonical bytes;
- immutable outer `release_root` with `_internal` `app_root` preserved;
- clean committed publish provenance and same-name collision hard error;
- exact cache values and verified query-only browser entry;
- exact process-scoped PowerShell command and verified-owned smoke cleanup.

The same Reviewer plan re-gate is next. Reviewer must not implement or approve on the User's
behalf. After a pass, the Controller returns the exact plan to the User for explicit approval.
Developer/worktree creation remains forbidden until then.
