# TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD

Status: `approved`; Reviewer plan re-gate passed and User explicitly approved implementation
Planning base: `02517ba968f1a16d5ddda6ba038411ef4133226d`
Revision: Reviewer blocking findings 1-6 reconciled on 2026-07-30
Owner now: Controller -> isolated worktree gate -> Developer

## Current Phase / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Active task: this task is `approved`; the Reviewer plan re-gate passed and the User explicitly
  approved the corrected implementation plan on 2026-07-30.
- Controller may persist the planning package and create one isolated lane after primary
  cleanliness and shared-owner checks pass.
- Product/release implementation is allowed only in the recorded lane worktree. Remote push,
  destructive cleanup, scope expansion, and Controlled Lane V2 remain unauthorized.

## Goal

Make a complete folder produced by `scripts/build_windows_browser_release.ps1` self-identifying,
copy-verifiable, and fail-closed on Windows 11 so the browser cannot be opened against an old
ConnLab service, a wrong local service, or an unverified package. The acceptance boundary must
distinguish:

1. a genuinely old or wrong process on `127.0.0.1:8765`;
2. a wrong URL/port, including the Vite development URL;
3. stale `frontend/dist` used during packaging;
4. browser entry/resource cache reuse;
5. an incomplete or altered copied release tree.

The operator action remains: copy the whole folder and double-click `Start_ConnLab.bat`. Cache
clearing, Task Manager, PID/port inspection, JSON inspection, or developer commands are not normal
operator steps.

## Confirmed Baseline

- The inspected 202607270802 package and current `frontend/dist` entry JS have SHA-256
  `6BDF5A2EDE105188724E8F8E3789B64D5888BFEC85903FC5B3415EE31C0E5F61` and contain
  `Export Matrix`.
- `MatrixEditorXlsxExportButton` renders unconditionally; state can disable it but does not hide it.
- Browser release authority is `127.0.0.1:8765`; `localhost:5173` is development only.
- The current BAT does not verify bind success, port ownership, release identity, or served
  frontend identity before opening the browser.
- The current build accepts `-SkipFrontendBuild`, checks only one historical negative phrase, and
  deletes an existing same-name release folder.
- The current packaged `/health` is generic `{"status":"ok"}` and cannot alone identify ConnLab.
- The inspected one-folder release has 1,275 files; 1,263 non-frontend `_internal` files are part of
  the required runtime.
- In frozen mode current `app_root` resolves to PyInstaller `_internal`; the outer release folder
  is `Path(sys.executable).parent` and is not represented in `PackagedRuntimePaths`.
- Fee export child mode currently returns before normal web-server startup and must stay isolated.

These facts do not prove which failure class caused the reported browser page. No single root cause
is presumed.

## Frozen Implementation Contracts

### 1. Publishable source and frontend freshness

- The publishable build requires a clean committed Git tree. Both tracked changes and untracked
  non-ignored files reported by `git status --porcelain=v1 --untracked-files=all` are blockers.
- Check clean state before tests/build and again immediately before final inventory generation.
- Record `source_commit` and `source_state: clean_committed`; do not use `source_dirty: true/false`
  as publishable provenance.
- `-SkipFrontendBuild` is rejected on the publishable path. `npm run build` is mandatory.
- The final copied frontend must be compared to the just-built source frontend by canonical
  inventory, per-file SHA-256, and dedicated frontend-tree digest.
- Final JavaScript must contain the current capability marker `Export Matrix`.
- A pre-existing final `dist_release/<ReleaseName>` is a collision hard error. Never delete,
  replace, merge into, or partially reuse it.
- Destructive cleanup is limited to an exact, task-dedicated PyInstaller intermediate root under
  `tmp/browser-release-build/<ReleaseName>`. The script must resolve and validate the repository
  root, fixed parent, leaf release name, and absence of reparse-point escape before deleting only
  that intermediate root. Existing `build/`, `dist/`, and every `dist_release/**` tree are not
  cleanup targets.

### 2. Canonical complete release inventory

- `release-manifest.json` is at the outer release root and is the sole inventory exclusion.
- The final publishable release must contain no mutable/generated release-root file. Runtime data,
  configuration, logs, and temporary data remain under `%LOCALAPPDATA%\ConnLab`.
- The inventory covers every regular file and directory under the outer release root, including
  EXE, BAT/PowerShell launchers, operator documents, and all `_internal` runtime, packages, bundled
  data, and frontend files.
- Reparse points and paths containing NUL, CR, LF, or tab are rejected.
- Paths are `/`-separated, relative, case-preserving, traversal-free, and unique under
  case-insensitive Windows comparison. Entries are sorted by ordinal UTF-8 path bytes.
- Canonical record bytes are UTF-8 without BOM:
  `type<TAB>path<TAB>length<TAB>lowercase_sha256<LF>`. Type is `f` or `d`; directory length is `0`
  and digest is `-`. `full_tree_sha256` hashes the concatenated records.
- `frontend_tree_sha256` applies the same contract to `_internal/frontend_dist`.
- Missing, altered, duplicate, traversal, reparse, type-changed, or extra file/directory entries
  fail closed. Frontend digest/capability checks supplement, never replace, full-tree verification.
- Launcher and packaged server each verify the entire inventory before their respective normal
  startup step. Each verifier has a 60-second wall-clock budget, checked between entries; timeout,
  read error, or incomplete verification is a hard failure.
- `index.html` validation covers every same-origin local reference in icon, preload,
  modulepreload, script, and stylesheet declarations. Queries/fragments are removed for lookup;
  external/protocol-relative/data references, traversal, duplicate normalized references, missing
  entries, or hash mismatch fail the build.
- PowerShell and Python must implement the same canonical-byte contract and pass shared fixtures.

### 3. Outer release-root and Fee child boundary

- Add immutable `release_root: Path` to `PackagedRuntimePaths`.
- Frozen default: `Path(sys.executable).resolve().parent`.
- Non-frozen default: the resolved `app_root`; both `release_root` and `app_root` are injectable in
  tests.
- `app_root` continues to mean the PyInstaller resource root (`_internal` when frozen).
- The manifest path is `paths.release_root / "release-manifest.json"`.
- `packaging/connlab_browser_server.spec` remains read-only; the manifest is intentionally external
  to `_internal`.
- Fee child mode must branch before argument parsing, runtime-path creation, manifest loading,
  application import, or Uvicorn startup, and retain its JSON-only stdout contract.

### 4. Ordered read-only port occupant classification

The launcher first probes fixed loopback port `8765`. If occupied, it performs only bounded,
read-only inspection in this order:

1. `guarded_connlab_valid`: identity endpoint returns within timeout with expected content type,
   strict schema/size, valid release and tree digests, loopback URL, and numeric PID.
2. `identity_malformed_or_spoof_like`: an identity response exists but violates schema, size,
   content type, digest format, loopback binding, or internal consistency.
3. `legacy_connlab_verified`: identity is absent/404; Windows listener PID is safely resolved;
   executable path is readable, resolves to an existing `ConnLab_Server.exe`; and a no-redirect
   bounded HTTP signature matches both exact `/health` JSON and a ConnLab HTML shell with at least
   one same-origin local referenced resource. Generic `/health` alone is never proof.
4. `unknown_listener_verified`: identity is absent and safely obtained PID/executable evidence
   proves the listener is not `ConnLab_Server.exe`.
5. `occupied_unverified`: safe PID/path/signature evidence is unavailable, incomplete, conflicting,
   access-denied, timed out, or otherwise cannot prove a narrower class.

PID discovery is limited to read-only Windows TCP owner lookup and `Get-Process`; executable path
is support evidence only when `MainModule.FileName` can be read safely. HTTP probes are loopback,
no-redirect, response-size-bounded, and timeout-bounded. Operator copy never claims “old ConnLab”
unless `legacy_connlab_verified`; support diagnostics may record class code, safely obtained PID and
path, status/content type, and check outcomes, but not raw response bodies or credentials.

Every occupied classification stops. It must not open a browser, reuse the service, change ports,
terminate a process, or replace an instance.

### 5. Server identity, launch read-back, and cache

- Mount package-only identity before static fallback and preserve global source `/health`.
- Unknown `/api/**` remains JSON 404, never SPA HTML.
- Identity returns manifest release ID, full/frontend tree digests, capability list, server PID,
  fixed host/port, and schema version with `Cache-Control: no-store`.
- After a free-port preflight the PowerShell launcher starts `ConnLab_Server.exe` directly, records
  its PID, then polls identity. Success requires the recorded process still alive plus exact PID,
  release ID, full-tree digest, frontend digest, capability, host, and port equality.
- Any bind race, early exit, timeout, malformed response, or mismatch fails closed and does not
  open the browser.
- The only launcher-opened URL is
  `http://127.0.0.1:8765/?release=<url-encoded-release-id>`.
- Exact cache contract:
  - `/`, `/index.html`, query variants, and every SPA fallback: `Cache-Control: no-store`;
  - identity: `Cache-Control: no-store`;
  - manifest-listed Vite content-hashed assets matching the reviewed hashed-name rule:
    `Cache-Control: public, max-age=31536000, immutable`;
  - every manifest-listed non-hashed static file: `Cache-Control: no-cache`;
  - unknown `/api/**` 404: `Cache-Control: no-store`.
- Operator docs remove all bare-URL/manual-address fallback. Failure remains in the visible launcher
  with business-readable guidance; cache clearing is diagnostic evidence, not the default fix.

### 6. BAT/PowerShell and smoke cleanup

`Start_ConnLab.bat` must bind to its own folder and invoke exactly:

```bat
powershell.exe -NoLogo -NoProfile -NonInteractive -WindowStyle Normal -ExecutionPolicy Bypass -File "%~dp0Start_ConnLab.ps1" -ReleaseRoot "%~dp0"
```

The BAT uses `cd /d "%~dp0"`, quotes every path, captures `%ERRORLEVEL%`, keeps the window visible on
failure, and returns the same exit code with `exit /b`. `Bypass` applies only to that child
PowerShell process. Global `Set-ExecutionPolicy`, registry mutation, policy weakening outside that
process, downloads, and unsigned helper-binary fallback are forbidden.

Policy-blocked fallback copy is:

> ConnLab's startup check could not run. If Windows says it was blocked, contact support. Do not
> change Windows security settings.

The generated-artifact smoke uses `try/finally`. It may terminate only the exact disposable process
it created after both recorded PID and release identity prove ownership. A pre-existing occupant is
never a cleanup target. Cleanup is recorded, bounded to 15 seconds, and smoke fails if the verified
owned process cannot be closed. There is no accepted “leave it running” alternative. If ownership
cannot be proven, the smoke does not terminate the process and QA records a blocking cleanup
failure for manual containment rather than treating the run as acceptable.

## Planned May Touch

- `scripts/build_windows_browser_release.ps1`
- `scripts/smoke_windows_browser_release.ps1`
- `packaging/Start_ConnLab.bat`
- new `packaging/Start_ConnLab.ps1`
- `packaging/README_FOR_BROWSER_OPERATOR.md`
- `packaging/RELEASE_NOTES_BROWSER.md`
- new bounded `backend/desktop/browser_release_manifest.py`
- new bounded `backend/desktop/browser_release_identity.py`
- `backend/desktop/runtime_paths.py`
- `backend/desktop/packaged_server.py`
- `backend/desktop/packaged_static.py`
- exact focused hunks in:
  - `tests/unit/test_desktop_packaged_runtime_paths.py`
  - `tests/unit/test_desktop_packaged_server.py`
  - `tests/unit/test_desktop_packaged_static.py`
  - `tests/unit/test_desktop_release_scripts.py`
- new bounded independent tests:
  - `tests/unit/test_browser_release_manifest.py`
  - `tests/unit/test_browser_release_identity.py`
  - `tests/unit/test_browser_release_occupant_contract.py`
  - `tests/integration/test_browser_release_manifest_compatibility.py`
- this task, plan, lane evidence, board, and active bundle.

`packaging/connlab_browser_server.spec` is a read-only validation dependency, not May Touch.

## Must Not Touch

- `frontend/src/**`, Matrix behavior/copy, Vite configuration, and current accepted `Export Matrix`.
- global source `/health`, business APIs, domain/application services, Fee behavior, LTR, Office,
  schema/database, authority data, or `%LOCALAPPDATA%\ConnLab` data.
- PyWebView, installer/updater, LAN/multi-user/permissions, alternate ports, or auto-update.
- any existing `dist_release/**`, real user/public-drive files, or unrelated dirty paths.
- Controlled Lane V2 registry, heartbeat, pilot, corrective, helper, or tests.

## Locked Paths / Ownership

- Build/smoke/launcher/manifest/identity/static/runtime-path and focused test paths above have one
  future lane owner only.
- Board, task, plan, evidence, and bundle are Planner/Integrator shared governance.
- Existing release artifacts are read-only validation inputs.
- Any overlap with another active owner or oversized mixed test serializes the lane; new tests stay
  bounded and independent.

## Dependencies

- Accepted RELEASE_003 browser package shell.
- Accepted TASK_355B Fee child-mode routing.
- Accepted TASK_367A current `Export Matrix` behavior.
- Windows PowerShell 5.1, PyInstaller onedir, FastAPI/Starlette, and modern Edge/Chrome.
- Reviewer plan re-gate and explicit User approval before any implementation authority.

## Validation Gate

- Deterministic unit/integration tests cover clean/dirty provenance, same-name preservation,
  full-tree and frontend digest, non-frontend missing/altered/extra entries, path duplicates,
  traversal/reparse rejection, local HTML references, PowerShell/Python compatibility, release-root
  derivation, Fee child early return, cache headers, API 404, identity, all five occupant outcomes,
  bind race, early exit, timeout, and mismatch.
- PowerShell parser/static tests freeze the exact BAT command, quoting, process-only policy, no-kill
  production launcher, exit propagation, and try/finally owned-process cleanup.
- Generated-artifact smoke verifies complete manifest, identity/PID read-back, direct/query entry,
  hashed/non-hashed headers, Matrix SPA fallback, referenced resources, `Export Matrix`, and cleanup.
- Hard QA gate: copy the complete generated folder to a different Windows 11 corporate image and
  run fresh, prior guarded occupant, verified legacy occupant, unknown listener, malformed identity,
  unverified occupant, copied-file damage, and prior-browser-session/cache scenarios. The visible
  Matrix Editor must contain `Export Matrix`.

## Merge Gate

1. Same Reviewer passes this corrected plan.
2. User explicitly approves the exact reviewed plan.
3. Orchestrator creates one isolated lane branch/worktree from a fresh clean base and records owner.
4. Developer supplies a clean bounded checkpoint commit.
5. Reviewer passes base..lane HEAD.
6. QA passes automated gates and the second-Windows-11 corporate-image hard smoke.
7. Integrator proves exact package, residual ownership, clean lifecycle, and authorized merge.

No push is implied.

## Risks / Rollback / Non-Goals

- Full-tree hashing can be slowed by storage or antivirus; the explicit 60-second budget fails
  closed and the corporate-image gate validates practicality.
- Windows PID/path lookup may be access-denied; `occupied_unverified` avoids false identity claims.
- Strict extra-file policy intentionally rejects modified copied trees.
- Process-scoped `ExecutionPolicy Bypass` may still be prohibited by corporate policy; support copy
  tells operators not to weaken security.
- Rollback is file-level reversion of the approved release-only hunks. No database migration,
  authority-data change, or mutable-user-data rollback exists.
- Terminating/taking over an operator's old process, automatic replacement, alternate-port start,
  frontend redesign, and cache clearing as a universal fix are non-goals and unauthorized options.

## Stop Point

The plan and User approval gates are satisfied. Controller may commit the exact planning package,
create and record one clean isolated lane, then route the task-specific Developer. Developer must
stop at a clean local checkpoint for Reviewer; no later role may be skipped.
