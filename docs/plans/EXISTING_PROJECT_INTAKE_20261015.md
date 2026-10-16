# Existing project intake — first usable increment

Task: `TASK_EXISTING_PROJECT_INTAKE_20261015`. Baseline: `0d9b62a4`.

## Outcome and boundaries

Existing manual and foreign-computer project folders can enter ConnLab without rebuilding them.
Project remains the lifecycle container; Matrix remains confirmed test authority. Files alone never
establish a confirmed Matrix, fee, LTR workbook registration, result dataset or released report.
All development and QA use disposable storage. Do not write the user's business database, source
folders, manifests or the separate DL-2026-09-018 report task. No push, publish or deployment.

## Ordered implementation

1. Show actual runtime/database/data/config locations and available application/release metadata.
   Report SQLite `user_version` accurately; this repository currently has distributed startup schema
   checks/migrations, not a unified schema version. Explain separate development/production stores.
   No database switch, merge or automatic upgrade of another selected database.
2. Bound discovery over operator-selected directory roots. Skip redirected paths, internal/history
   directories and inaccessible entries with explicit diagnostics; never traverse arbitrary trees
   without limits. Read only names and bounded `.connlab/manifest.json` metadata for preview.
3. Preview identity and local conflicts, then register in place in one local database transaction.
   Use a dedicated existing-project location table, not generated-folder authority. Bind approval to
   source identity and current conflict state; retain foreign identity only after supported manifest
   validation and local identity checks. Repeated confirmation/import is idempotent. Never replace
   projects merely because their DL numbers match. Offer explicit link, independent import with
   resolved display-number conflict, and skip. Hidden matches must be restored rather than silently
   duplicated/reactivated. Keep original source number/provenance when a local display number changes.
4. Registered directories are browseable/openable by stored project/location identity, without
   requiring Matrix. Relocate a missing/moved location through a reviewed rebind rather than global
   path replacement. Inspect files lazily and enforce root containment and reparse-point protection.
5. Add temporary/history selection and batch reversible registry moves using existing trash/history
   contracts, generation locks and conflict previews. Preserve all files, ownership and associations.
   Never infer deletability from a filename; preview retained formal outputs and shared references.

## Acceptance and validation

- Manual folder: preview/cancel writes nothing; confirmed import appears once, browses source files,
  can open project and continues managing files without a Matrix or a new LTR application.
- Foreign supported manifest: preserve validated identity when unused locally; moved absolute paths
  are evidence only. Colliding internal ID/DL, malformed/unsupported manifest and hidden local records
  need explicit resolution. No fabricated authority history.
- Same directory or repeated clicks: no duplicate records. Source/conflict changes after preview
  fail safely, keep inputs and allow fresh preview/retry. New independent number cannot collide.
- Directory changes: reviewed relocation succeeds; stale approvals, junctions, escape paths and
  inaccessible/disappeared sources cannot open or register unintended files.
- Bulk trash/restore: cancellation, stale items, generation in progress and duplicate conflicts
  preserve complete state. Normal moves/restores retain source bytes and formal associations.
- Workspace panel: actual paths and runtime are visible; failures are actionable; no other database
  is initialized merely to inspect its version. Empty user_version is not a schema compatibility claim.
- Developer: meaningful RED/GREEN tests at application/HTTP/UI seams. Independent Reviewer checks
  exact diff. Independent QA runs complete non-Office Python, frontend tests and sequential build,
  plus real UI confirmation/cancellation/double-submit/failure/retry/restore using isolated storage.
- Independent Integrator verifies exact scope/evidence and local integration. User Close remains
  pending; this task explicitly forbids publication even if local commits are needed.

## Deferred, not implied by this increment

Full cross-computer semantic project packages, arbitrary database merge, global versioned schema
migration orchestration and physical file deletion. Formal upgrades need consistent backup, exclusive
writer/version checks and recovery; do not share writable production SQLite with development or
unknown older executables. Directory intake does not reconstruct lost confirmed Matrix history.

## Progress

- Implemented: bounded multi-root discovery; reviewed registration/link/independent decisions;
  provenance-aware conflicts and idempotence; source-preserving locations with reviewed relocation;
  lazy contained file browsing/download; actual workspace diagnostics; atomic batch recycle/restore.
  Entries are reachable from Projects, Workbench and Settings. No Matrix/LTR authority is fabricated.
- Developer feedback: first intake RED was missing application module; batch RED was missing
  preview_batch method (2 failures); source-alias RED reproduced an empty conflict list (IndexError).
  Initial UI slices failed missing imports before their implementations. Subsequent targeted results:
  Python 31 passed / 1 skipped (host symlink-creation privilege), HTTP 13 passed; frontend affected
  page/workflow regressions 105 passed; TypeScript tsc -b passed before the last context-isolation fix.
- Ordinary HTTP execution hung in Windows asyncio socketpair initialization (faulthandler evidence);
  isolated HTTP passed after narrow escalation. Existing temp-config hardlink tests likewise needed
  escalation. No business database, source folder or manifest was touched by development validation.
- Approval recovery: automatic review initially rejected the final Python and scoped FilesPanel
  commands before execution, citing superseded read-only instructions. Main agent obtained current
  trusted implementation/isolated-test authorization and retried those exact actions once in its
  context. Root reported Python 45 passed / 1 skipped, final source-identity service + HTTP 12 passed,
  FilesPanel 4 passed and other affected frontend 7 files / 103 passed. These are root executions,
  not independent Developer or complete QA evidence. No workaround or business-data write occurred.
- Developer code/test freeze: all implementation is complete. Final frontend-only refinements bind
  file/batch sessions to their location, ignore late initial location lists after registration, and
  keep confirmation stale after a failed review refresh. Root reported the intake panel's 4 tests
  passed (2.74s); TypeScript/build and independent Review/complete QA/browser
  verification are pending, not claimed passed. This increment manages files/provenance only: no
  cross-database semantic import, confirmed-history reconstruction, database switch or physical delete.
- Focused review correction: the download response now owns its opened handle at ASGI `__call__`
  scope, including response-start failure before the file iterator begins. Added a disposable-file
  ASGI 2.4 disconnect regression. Root reported the affected API file's 4 tests passed (2.21s).
- Final identity-review correction: conflict and link choices now include the existing canonical
  DL/TMP display identity alongside the distinct management number and immutable record ID. Added
  service/UI cases where the Project's legacy number differs from its actual registered LTR.
  Product and test bytes are frozen. Root reran the final identity service (10 passed, 1.68s) and
  intake panel (5 passed, 3.36s). Independent final review and complete QA/browser checks remain
  pending; these targeted checks are not substitutes for the complete final-state validation.
