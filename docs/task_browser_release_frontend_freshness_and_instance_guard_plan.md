# TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD Plan

Date: 2026-07-30
Status: `approved`; corrected plan passed the same Reviewer re-gate and received explicit User
implementation approval on 2026-07-30
Planning base: `02517ba968f1a16d5ddda6ba038411ef4133226d`
Lane: `browser-release-frontend-freshness-instance-guard`

## Approval Checkpoint

- Reviewer re-gate: `reviewer_plan_pass`.
- User approval: exact corrected plan approved for implementation on 2026-07-30.
- Design and scope below are unchanged from the Reviewer-passed plan.
- Next legal action is a clean isolated lane/worktree and task-specific Developer routing.
- Remote push, destructive cleanup, pre-existing process termination, scope expansion, and
  Controlled Lane V2 remain unauthorized.

## 1. Objective

Produce a portable Windows browser release whose source, complete copied tree, running process,
served frontend, browser entry, and visible `Export Matrix` capability are joined by one
fail-closed identity chain:

```text
clean committed source
-> mandatory frontend build
-> complete staged release inventory
-> manifest-bound release identity
-> launcher whole-tree validation
-> free fixed port
-> recorded new PID
-> server whole-tree validation
-> exact identity/PID read-back
-> release-query browser entry
-> Matrix Editor smoke
```

This plan does not assume whether the reported incident was caused by an old process, wrong URL,
stale build, cache, or incomplete copy. It gives each class a separate deterministic signal.

## 2. Discovery Gate

### Current phase / active task / why allowed

- Phase 11 remains the frozen product baseline.
- This task is `planned_not_approved`.
- Reviewer returned six blocking plan findings and routed the same task to Planner.
- This revision may change only planning governance. It cannot implement release code, approve the
  plan, create a worktree/branch/role, or run generated release/browser validation.

### Confirmed by User

- Solve the copied-full-folder Windows 11 browser release freshness/instance problem.
- Cover frontend freshness, final static guard, manifest/identity, port/old-instance handling,
  fail-closed launcher, server health/identity read-back, zero-technical operator steps, automation,
  and another-Windows-11 manual smoke.
- Keep process termination, forced port takeover, and automatic replacement as unauthorized
  options requiring separate explicit approval.
- Keep Controlled Lane V2 frozen.

### Confirmed by repository evidence

- Current source and inspected 202607270802 packaged entry JS are hash-identical and contain
  `Export Matrix`.
- The export button is not conditionally hidden by project state.
- The current BAT starts the EXE, sleeps two seconds, and opens a bare URL without bind or identity
  verification.
- Current build can skip the frontend, checks only an old negative phrase, removes the same-name
  final release, and cleans broad `build`/`dist` paths.
- Current `/health` is generic and historical browser releases do not expose the planned identity.
- A real onedir package depends on 1,263 non-frontend `_internal` files in addition to the frontend.
- Current frozen `default_app_root()` resolves `_MEIPASS`; the manifest's outer release root has no
  runtime-path field.
- Static fallback currently returns index for SPA paths and protects unknown `/api/**` as 404, but
  has no explicit release cache policy.
- Fee child mode currently routes before normal server startup.

### Planner inference

- The observed missing button is evidence that the browser did not render the verified packaged
  frontend, but available evidence cannot identify which of the five failure classes produced it.
- A complete-tree digest is necessary because frontend-only and selected critical-file checks
  cannot detect a missing DLL, extension module, package, or bundled seed.
- Port occupation must be treated as a safety boundary. A historical service cannot be trusted
  merely because `/health` returns `ok`.
- The external manifest requires an explicit outer release-root path rather than an implicit
  `_MEIPASS` assumption.

### Unconfirmed information that does not block planned status

- The exact operator workstation policy/antivirus hashing performance is not known; the 60-second
  per-verifier limit and corporate-image QA gate make it an acceptance fact rather than an
  implementation guess.
- The incident workstation's prior listener/cache state is unavailable; acceptance covers all
  classes without claiming one historical root cause.

### Definition of Ready result

The plan is implementation-specific enough for a Reviewer re-gate: May Touch, Must Not Touch,
locks, ownership, canonical bytes, classification, cache values, launcher command, cleanup,
tests, and manual smoke are frozen. It is not ready for implementation until that Reviewer passes
and the User explicitly approves the exact revision.

## 3. Diagnostic and Acceptance Boundaries

| Failure class | Authoritative evidence | Acceptance |
|---|---|---|
| guarded ConnLab occupant | strict identity schema plus release/tree/PID fields | classify `guarded_connlab_valid`; stop, no browser/reuse/kill |
| legacy ConnLab occupant | no identity; safe listener PID/path is `ConnLab_Server.exe`; exact health plus ConnLab HTML/local-resource signature | classify `legacy_connlab_verified`; stop, no browser/reuse/kill |
| unknown listener | no identity; safe PID/path proves a different executable | classify `unknown_listener_verified`; stop, no browser/reuse/kill |
| malformed/spoof-like identity | endpoint responds but schema/size/content type/digest/binding consistency fails | classify `identity_malformed_or_spoof_like`; stop, no browser/reuse/kill |
| occupied but not provable | access denied, timeout, missing/conflicting PID/path/signature evidence | classify `occupied_unverified`; stop without claiming old ConnLab |
| wrong URL/port | launcher contract and observed identity do not equal fixed loopback 8765 | never open 5173/localhost/alternate port; fail |
| stale frontend build | mandatory build/source-final inventory/capability mismatch | fail before publish |
| browser cache | current identity passes but entry could be reused | no-store entry/fallback/identity plus release-query URL |
| incomplete/altered copy | complete manifest misses/changes/adds any entry or reference | launcher fails before EXE start |

Generic `/health {"status":"ok"}` alone is never enough to classify ConnLab. The visible operator
message and support diagnostics are separate outputs:

- operator: short action and support direction with no PID, port, JSON, hash, or cache terminology;
- support: stable class code, safely observed PID/executable path, HTTP status/content type, and
  individual check result; never raw body, credentials, or environment secrets.

## 4. Frozen Design

### 4.1 Publishable clean-source policy

The build script performs:

1. resolve repository root;
2. resolve release name and intended final path;
3. fail if final path already exists;
4. require full HEAD SHA;
5. require empty `git status --porcelain=v1 --untracked-files=all`;
6. run focused tests unless explicitly skipped for developer diagnostics;
7. reject `-SkipFrontendBuild`, then run `npm run build`;
8. assemble the entire output inside a task-dedicated intermediate root;
9. repeat clean-tree check before inventory generation;
10. generate and validate manifest in staging;
11. recheck final-path collision and move the complete staged folder once;
12. clean only the resolved task-dedicated intermediate root.

`-SkipTests` may remain a developer build switch but cannot change manifest truth. A release built
with it is not QA-accepted until the declared test and generated-artifact gates run separately.
`-SkipFrontendBuild` cannot yield publishable success.

Intermediate layout:

```text
<repo>/tmp/browser-release-build/<ReleaseName>/
  work/
  dist/
```

Deletion requires all of:

- resolved target is below resolved `<repo>/tmp/browser-release-build`;
- parent equals that fixed parent;
- leaf equals the already validated release name;
- target is not repository root, `tmp`, `build`, `dist`, or `dist_release`;
- no parent/target reparse-point escape exists.

No existing final release is ever removed or overwritten. A failed stage may be retried only after
the exact intermediate target passes the same validation; final collision remains a hard stop.

### 4.2 Manifest schema and deterministic release identity

Outer root file: `release-manifest.json`.

Required fields:

```text
schema_version
release_id
release_name
project_version
source_commit
source_state = "clean_committed"
built_at_utc
host = "127.0.0.1"
port = 8765
capabilities = ["matrix_editor_xlsx_export"]
full_tree_sha256
frontend_tree_sha256
entries[]
frontend_entries[]
```

`built_at_utc` is evidence only and is excluded from identity inputs. No `source_dirty` Boolean is
accepted.

Inventory rules:

- manifest itself is the only excluded path;
- include every other regular file and directory;
- reject reparse points and paths containing NUL/tab/CR/LF;
- normalize separator to `/`, reject absolute/drive/UNC/`.`/`..` paths;
- preserve case but reject duplicates by case-insensitive Windows key;
- entry types are `f` and `d`;
- file entry has byte length and lowercase SHA-256;
- directory entry has length `0` and digest `-`;
- sort by ordinal UTF-8 path bytes.

Canonical bytes per entry are:

```text
<type>\t<relative-path>\t<length>\t<lowercase-sha256>\n
```

encoded UTF-8 without BOM. `full_tree_sha256` hashes the concatenated complete records.
`frontend_tree_sha256` hashes records relative to `_internal/frontend_dist` with the same rules.

Deterministic release ID:

```text
sha256(
  "connlab-browser-release-v1\n"
  + release_name + "\n"
  + project_version + "\n"
  + source_commit + "\n"
  + full_tree_sha256 + "\n"
  + frontend_tree_sha256 + "\n"
)
```

The manifest is written only after all files are staged because the complete-tree digest includes
the EXE, launchers, operator documents, all `_internal` runtime/data/packages, and frontend. Both
PowerShell and Python parse the same JSON fields and independently reconstruct the canonical bytes.
Shared fixture tests prevent cross-language drift.

Extra-file policy is strict: any unlisted file or directory, missing entry, type change, length/hash
mismatch, duplicate, traversal, or reparse point fails. No mutable/generated release-root
exclusion exists. Mutable runtime state stays under `%LOCALAPPDATA%\ConnLab`.

### 4.3 Frontend and HTML reference guard

After the mandatory frontend build:

1. build canonical inventory for `frontend/dist`;
2. place that exact tree under `_internal/frontend_dist`;
3. reconstruct final frontend inventory and require exact entry/length/hash equality;
4. scan final JS for `Export Matrix`;
5. parse final `index.html`;
6. enumerate same-origin local references for:
   - `link[rel~="icon"]`;
   - `link[rel="preload"]`;
   - `link[rel="modulepreload"]`;
   - `link[rel="stylesheet"]`;
   - `script[src]`;
7. strip query/fragment for lookup, percent-decode once, normalize, and require it remains under
   frontend root and appears exactly once in manifest;
8. reject external schemes, protocol-relative/data/blob references, traversal, duplicate normalized
   references, missing files, or hash drift.

The dedicated frontend digest and `Export Matrix` capability are independent gates and do not
substitute for complete release validation.

### 4.4 Explicit outer release-root

`PackagedRuntimePaths` gains immutable `release_root: Path`.

Resolution:

```text
frozen:
  release_root = Path(sys.executable).resolve().parent
  app_root = Path(sys._MEIPASS).resolve()

non-frozen:
  app_root = current repository/resource root
  release_root = app_root
```

`build_packaged_runtime_paths()` accepts injectable `release_root`, `app_root`, `frontend_dist`, and
`user_root`. Existing mutable user-root behavior is unchanged. Manifest lookup uses
`paths.release_root / "release-manifest.json"`. The PyInstaller spec stays read-only because the
outer manifest must not be bundled inside `_internal`.

`main()` checks Fee child mode before `parse_args`, runtime-path construction, manifest read,
FastAPI app import, or Uvicorn start. A focused test replaces all normal-mode loaders with
fail-fast doubles and requires the child return code/argv plus JSON-only stdout to remain intact.

### 4.5 Server manifest/identity contract

Normal packaged server startup:

1. build runtime paths;
2. load outer manifest with bounded size/schema;
3. reconstruct and verify the full inventory within 60 seconds;
4. verify frontend digest, local index references, and capability;
5. prepare mutable user directories;
6. create FastAPI app;
7. mount package identity route before static fallback;
8. start Uvicorn on fixed loopback/8765.

Identity path is package-only and precedes the catch-all static route. Response contains:

```text
schema_version
release_id
release_name
source_commit
full_tree_sha256
frontend_tree_sha256
capabilities
pid
host
port
```

It returns `Cache-Control: no-store`. The source application's global `/health` remains unchanged.
Unknown `/api/**` remains a JSON 404 and receives `Cache-Control: no-store`, never SPA HTML.

### 4.6 Exact cache contract

| Response | Exact `Cache-Control` |
|---|---|
| `/`, `/index.html`, query variants | `no-store` |
| every SPA fallback, including Matrix Editor | `no-store` |
| package identity | `no-store` |
| manifest-listed Vite content-hashed asset matching reviewed hashed-name rule | `public, max-age=31536000, immutable` |
| manifest-listed non-hashed static file | `no-cache` |
| unknown `/api/**` 404 | `no-store` |

The hashed-name rule is frozen to a file under `/assets/` whose final filename stem ends with
`-[A-Za-z0-9_-]{8,}` before its extension and whose exact path/hash is present in the manifest.
Files that do not satisfy both conditions use `no-cache`. Direct and query entries have identical
no-store behavior.

### 4.7 Fail-closed PowerShell launcher

`Start_ConnLab.bat`:

```bat
@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoLogo -NoProfile -NonInteractive -WindowStyle Normal -ExecutionPolicy Bypass -File "%~dp0Start_ConnLab.ps1" -ReleaseRoot "%~dp0"
set "CONNLAB_EXIT=%ERRORLEVEL%"
if not "%CONNLAB_EXIT%"=="0" (
  echo.
  echo ConnLab's startup check could not run. If Windows says it was blocked, contact support. Do not change Windows security settings.
  pause
)
endlocal & exit /b %CONNLAB_EXIT%
```

The BAT quotes its own folder/script, binds current folder with `cd /d`, and propagates the child
exit code. `-ExecutionPolicy Bypass` applies only to this child process. The implementation must not
call global `Set-ExecutionPolicy`, write policy registry keys, weaken policy outside the child,
download code, or fall back to an unsigned helper binary.

`Start_ConnLab.ps1`:

1. resolve `-ReleaseRoot` and require it equals its own script folder;
2. load bounded manifest;
3. reconstruct/verify complete inventory within 60 seconds;
4. verify frontend digest, local references, capability, and stable EXE;
5. probe fixed loopback port;
6. if occupied, run the ordered classifier below and stop;
7. if free, start the exact resolved EXE with fixed host/port arguments and record `Process.Id`;
8. poll bounded identity while also checking that recorded process remains alive;
9. require identity PID, release ID, complete/frontend digest, capability, host, and port equality;
10. open only
    `http://127.0.0.1:8765/?release=<url-encoded-release-id>`;
11. return deterministic nonzero codes for validation, occupation, startup, identity, or browser
    launch failure.

Production launcher never calls `Stop-Process`, `.Kill()`, `taskkill`, alternate-port logic, or
service reuse.

### 4.8 Ordered occupant classifier

All network probes are loopback-only, no-redirect, response-size-bounded, and short-timeout.
Classification order:

1. valid strict identity -> `guarded_connlab_valid`;
2. identity response exists but violates schema/size/content type/digest/binding consistency ->
   `identity_malformed_or_spoof_like`;
3. identity absent/404; safely obtain Windows listener PID and process path:
   - readable existing basename `ConnLab_Server.exe`;
   - exact `/health` JSON;
   - `/` HTML includes `<title>ConnLab</title>` and at least one same-origin local reference that
     can be fetched without redirect;
   -> `legacy_connlab_verified`;
4. identity absent and safe executable evidence proves a different executable ->
   `unknown_listener_verified`;
5. otherwise -> `occupied_unverified`.

Read-only evidence sources are `Get-NetTCPConnection` for port/listener owner, `Get-Process -Id`,
and `MainModule.FileName` when permitted. Any access denial or inconsistent multi-listener/PID
result falls to `occupied_unverified`. Generic health alone never upgrades a result.

All five outcomes return nonzero without browser opening, reuse, port change, replacement, or
termination. The operator message is action-focused; support diagnostics hold only stable class,
safe PID/path, HTTP status/content type, and check booleans.

### 4.9 Operator copy

The normal steps remain:

1. copy the complete release folder;
2. open that folder;
3. double-click `Start_ConnLab.bat`;
4. wait for the verified browser window;
5. if the launcher stops, follow its message or contact support.

Remove the instruction to type the bare URL. Do not advise cache clearing, Task Manager, port/PID
inspection, PowerShell commands, JSON inspection, or security-policy changes.

Messages:

- incomplete/altered copy:
  `ConnLab could not verify this release folder. Copy the complete release folder again, then try once more.`
- occupied but specific identity is not safely proven:
  `ConnLab cannot start because its local address is already in use. Close the other application or contact support, then try again.`
- verified earlier ConnLab:
  `Another ConnLab release is already running. Close its server window, then start this release again.`
- startup/read-back mismatch:
  `ConnLab did not start from this release folder. Close this window and contact support.`
- policy fallback:
  `ConnLab's startup check could not run. If Windows says it was blocked, contact support. Do not change Windows security settings.`

### 4.10 Automated smoke ownership and cleanup

The generated-artifact smoke uses `try/finally` and tracks:

```text
preexisting_occupant
started_process_id
expected_release_id
identity_verified_for_started_pid
cleanup_attempted
cleanup_succeeded
```

- If the port is occupied before the smoke starts, no disposable process is created and no cleanup
  action targets the occupant.
- The smoke may terminate only its recorded PID after live identity proves both that PID and the
  expected release ID.
- Verified owned cleanup is bounded to 15 seconds and its outcome is evidence.
- Failure to close that verified process fails the smoke.
- If identity ownership cannot be proven, the process is not terminated; QA treats containment as
  a blocking cleanup failure. There is no successful or optional “leave it running” branch.

This smoke-only owned-process termination does not authorize the production launcher to terminate
anything.

## 5. File-Level Implementation Plan

| File | Planned change |
|---|---|
| `scripts/build_windows_browser_release.ps1` | clean-source gates, frontend mandatory build, dedicated intermediate staging, collision hard error, complete manifest and HTML/capability guard, exact final move |
| `scripts/smoke_windows_browser_release.ps1` | complete manifest/HTTP/Matrix checks, conflict fixtures, try/finally and verified-owned PID cleanup |
| `packaging/Start_ConnLab.bat` | exact PowerShell command, current-folder binding, visible failure, exit propagation |
| `packaging/Start_ConnLab.ps1` | full-tree preflight, occupant classifier, start/PID/identity read-back, verified query URL |
| `packaging/README_FOR_BROWSER_OPERATOR.md` | zero-technical steps; remove manual bare URL/cache/security workaround |
| `packaging/RELEASE_NOTES_BROWSER.md` | identity/fail-closed startup and copy-completeness operator contract |
| `backend/desktop/browser_release_manifest.py` | bounded schema, canonical inventory bytes, complete/frontend validation, HTML reference validation |
| `backend/desktop/browser_release_identity.py` | package-only identity model/route and exact no-store response |
| `backend/desktop/runtime_paths.py` | immutable outer `release_root`, frozen/non-frozen defaults and injection |
| `backend/desktop/packaged_server.py` | Fee-child-first branch; normal manifest validation; identity before static; fixed identity contract |
| `backend/desktop/packaged_static.py` | exact cache headers, hashed-name+manifest decision, no-store SPA, unknown API 404 |
| existing focused tests | exact small updates for new fields/ordering/headers/static script contracts |
| four new bounded test modules | manifest, identity, occupant script contract, cross-language compatibility |

`packaging/connlab_browser_server.spec` remains read-only. No frontend source file changes.

## 6. Test-First Plan

### 6.1 Manifest/provenance tests

- clean committed tree accepted;
- tracked dirty and untracked non-ignored source rejected;
- `source_state` is exactly `clean_committed`, no Boolean dirty provenance;
- same release name collision fails before mutation and sentinel remains byte-identical;
- only exact validated intermediate path is deletable;
- stable canonical records and release-ID input vector;
- manifest sole exclusion;
- missing/altered/extra non-frontend DLL/package/data/file/directory rejected;
- missing/altered/extra frontend entry rejected;
- duplicate Windows-case path, traversal, absolute/drive/UNC path, forbidden control character,
  reparse point, type change, and malformed digest rejected;
- PowerShell/Python shared fixture yields identical full/frontend digests and release ID.

### 6.2 HTML/frontend tests

- icon, preload, modulepreload, script, and stylesheet local references found and hashed;
- query/fragment resolution works;
- external/protocol-relative/data/traversal/duplicate/missing reference rejected;
- source/final frontend inventories match;
- `Export Matrix` capability present and missing capability blocks.

### 6.3 Runtime-path/Fee tests

- frozen `release_root == Path(sys.executable).parent`;
- frozen `app_root == sys._MEIPASS`;
- non-frozen release root follows app root;
- explicit release-root injection works;
- manifest reads outer root, not `_internal`;
- spec remains unchanged/read-only contract;
- Fee child calls no path/manifest/app/Uvicorn loader and preserves child argv, return code, and
  JSON-only stdout.

### 6.4 Occupant tests

Deterministic fixtures for:

- valid guarded identity;
- verified legacy ConnLab without identity;
- verified unknown executable listener;
- malformed/spoof-like identity;
- access-denied/timeout/conflicting evidence -> `occupied_unverified`.

Every fixture asserts nonzero exit, no EXE start for pre-existing occupation, no browser, no port
change, no reuse, and no process termination. Generic health-only fixture must be
`occupied_unverified`.

### 6.5 Static/identity/cache tests

- direct `/`, query `/`, `/index.html`, query `/index.html`: `no-store`;
- Matrix Editor SPA fallback: `no-store`;
- identity: strict body plus `no-store`;
- manifest-listed hashed asset: exact one-year immutable value;
- non-hashed icon/static file: `no-cache`;
- unknown `/api/does-not-exist`: JSON 404, no shell, `no-store`;
- identity route wins before static fallback;
- missing/malformed manifest or full-tree timeout prevents normal server startup.

### 6.6 Launcher/smoke tests

- BAT exact command includes NoLogo/NoProfile/NonInteractive/Normal/process-only Bypass, quotes,
  current folder, and exit propagation;
- no global policy mutation, registry, download, helper-binary fallback, kill, taskkill, alternate
  port, or bare URL;
- free port + correct new PID/identity opens exact release-query URL;
- early exit, bind race, timeout, PID/release/tree/frontend/capability mismatch never opens browser;
- incomplete copy stops before EXE;
- try/finally cleanup targets only verified owned PID;
- pre-existing occupant is never cleanup target;
- cleanup failure makes smoke fail.

New behavior stays in bounded independent modules rather than adding another large mixed release
test.

## 7. Generated Artifact and HTTP Gate

On an explicitly approved implementation lane:

1. run focused Python tests;
2. parse both PowerShell scripts;
3. run frontend tests/build required by current release gate;
4. build a new unique release name from a clean committed tree;
5. prove final path did not exist and no historical release changed;
6. independently reconstruct complete/frontend inventory;
7. verify server identity/PID and cache headers;
8. open Matrix Editor through verified query entry and see `Export Matrix`;
9. run each occupied-port fixture;
10. record try/finally cleanup evidence;
11. leave no verified owned disposable process.

No current/historical `dist_release/**` artifact is modified during planning.

## 8. Windows 11 Corporate-Image Hard QA Gate

Copy the entire new release folder to a different Windows 11 corporate image. The QA record must
identify release ID, source commit, full/frontend digests, and machine class without private
machine data.

Run:

1. fresh launch from `Start_ConnLab.bat`;
2. direct/query entry headers and exact identity;
3. Matrix Editor visible `Export Matrix`;
4. a prior guarded release on 8765;
5. a historical no-identity ConnLab server meeting the legacy signature;
6. an unknown listener;
7. a malformed identity listener;
8. an occupied listener whose PID/path cannot safely be proven;
9. one copied non-frontend runtime file missing/altered;
10. one extra file;
11. prior browser session/cache scenario without clearing cache;
12. policy-restricted corporate behavior;
13. cleanup outcome for every disposable process.

Cases 4-8 must stop without browser/reuse/port change/termination. Cases 9-10 must stop before EXE.
Case 12 must show the frozen guidance and must not ask the operator to weaken security. QA cannot
pass if an owned disposable process remains or if cleanup ownership was not proven.

## 9. Scope and Ownership

### May Touch

Exactly the paths listed in the formal task, including `backend/desktop/runtime_paths.py` and its
bounded tests.

### Must Not Touch

Frontend source/Matrix behavior, global `/health`, business APIs/services, Fee behavior, LTR,
Office, schema/database, user data, Vite/PyWebView, installer/updater, LAN/permissions/multi-user,
existing release folders, real data, V2, and unrelated dirty paths.

### Locked/shared ownership

- One future lane owns build/smoke/launcher/manifest/identity/static/runtime-path changes.
- Planner/Integrator share governance paths.
- Existing release trees remain read-only.
- Any same-file overlap or authority conflict serializes work.

## 10. Risks and Mitigations

- Full hashing may exceed the budget: fail closed; use corporate-image QA to prove the 60-second
  limit is viable rather than silently extending or skipping verification.
- PID/path inspection can be denied: classify `occupied_unverified`, do not claim legacy ConnLab.
- Strict extra-file policy can reject modified folders: intentional copy-integrity behavior.
- Identity could be spoofed by a local service: malformed/inconsistent identity stops; no identity
  is reused; launcher only trusts the newly recorded PID after starting from a verified tree.
- Corporate PowerShell policy may block process-scope Bypass: visible support guidance, no global
  policy workaround, hard QA result.
- Manifest/Python/PowerShell canonicalization may drift: shared byte-vector compatibility tests.

## 11. Rollback and Non-Goals

Rollback is an exact reversion of release-only scripts/docs/runtime modules/focused tests. There is
no schema, data, frontend-product, or authority migration.

Non-goals:

- terminate/replace an operator's old process;
- use another port or silently reuse a server;
- auto-update/installer/LAN/multi-user work;
- frontend redesign or Matrix business changes;
- use cache clearing as a universal fix;
- identify the historical incident root cause without evidence.

## 12. Reviewer-Finding Closure

| Reviewer finding | Corrected contract | Primary files/tests | Acceptance |
|---|---|---|---|
| 1 legacy occupant | ordered five-outcome read-only classifier; exact PID/path/HTTP evidence; health alone insufficient; operator/support separation | `Start_ConnLab.ps1`, smoke, occupant tests | every occupied case stops with no browser/reuse/port/kill |
| 2 whole release | sole-exclusion complete file+directory inventory; canonical bytes; 60s launcher/server validation; all local HTML refs; strict extras | build, manifest module, launcher/server, compatibility tests | non-frontend removal/alter/extra and path attacks fail |
| 3 outer root | immutable injectable `release_root`; frozen EXE parent; `app_root` remains `_internal`; spec read-only; Fee child first | runtime paths/server and focused tests | outer manifest found; child touches no normal loader |
| 4 provenance/collision | clean committed tree only; full-tree-bound identity; same-name hard error; bounded intermediate-only deletion | build and release script/manifest tests | dirty/repeated builds fail without final mutation |
| 5 cache/operator | exact header table; identity before fallback; API 404; no manual bare URL; verified query open only | static/identity/launcher/docs and exact-header tests | direct/query/Matrix/asset/API cases match |
| 6 policy/cleanup | exact BAT command and process-only Bypass; frozen policy copy; try/finally verified-owned cleanup; corporate hard gate | BAT/PS1/smoke/tests/docs | no global weakening; no pre-existing kill; cleanup failure blocks |

The durable detailed mapping and reconciliation checkpoint is:
`docs/lane_evidence/TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD_reconciliation_planner.md`.

## 13. Gate and Stop Point

1. Same Reviewer re-gate passed.
2. User explicitly approved this exact corrected plan.
3. Controller creates and records one clean isolated lane/worktree before Developer starts.
4. Implementation must pass Developer, Reviewer, QA corporate-image, and Integrator gates.

No role may skip the clean-worktree, committed-input, validation, or scope gates.
