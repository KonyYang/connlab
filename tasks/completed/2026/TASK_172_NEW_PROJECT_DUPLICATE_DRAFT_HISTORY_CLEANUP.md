# TASK_172 New Project Duplicate Draft History Cleanup

> Status: complete
> Created: 2026-05-11
> Phase: Phase 10F - Real public-drive LTR workbook operational closure

---

## 0. Execution Gate

- Current phase: `Phase 10F`
- Current active task in board: `none` (user-directed controlled task activation)
- Why this task is allowed now: user explicitly requested cleanup of historical duplicate draft/package records to enforce one active draft identity and prevent `Load existing` opening old packages.

---

## 1. Purpose

Eliminate legacy duplicate intake draft history for the same email identity so New Project duplicate resolution (`Load existing`) cannot jump to stale historical packages.

Target business state:

- same identity keeps one active draft package only;
- old duplicate draft/case/package records are removed;
- filesystem intake package folders for removed records are also removed.

---

## 2. Scope

In scope:

- Add a backend cleanup service that groups duplicate unconfirmed draft packages by email source identity and keeps only one canonical package per group.
- Hard-delete redundant records in dependency order:
  - drafts
  - cases
  - assets
  - package
- Remove corresponding storage folder under `Data/intake/<package_id>`.
- Add dry-run preview mode and execute mode.
- Add tests for grouping/selection/deletion safety.
- Add a small admin API endpoint (or internal command service path) to run dry-run then execute.

Out of scope:

- No change to confirmed project records.
- No change to LTR workbook write path.
- No UI redesign in this task.
- No SQLite schema migration in this task.

---

## 3. Design

### 3.1 Duplicate Group Key

Use source-email asset identity:

- preferred: `(email_source.sha256, email_source.size_bytes)`
- fallback: `(email_source.original_name, email_source.size_bytes)` when hash missing

Only include packages that satisfy all:

- source type = `outlook_msg`
- has unconfirmed reusable case
- has draft linked to that case
- no confirmed project in grouped cases

### 3.2 Keep/Remove Rule

For each duplicate group (`count >= 2`):

- keep the newest package by:
  1. package `updated_at` (desc)
  2. fallback `created_at` (desc)
  3. tie-breaker `package_id` (desc)
- remove all others.

### 3.3 Safety Guard

Skip deletion for any package where:

- any case is confirmed, or
- draft/case chain is incomplete, or
- package source is not MSG.

Return skip reasons in dry-run report.

---

## 4. File-Level Change Plan

- `backend/application/`:
  - add `duplicate_draft_history_cleanup_service.py`
- `backend/api/`:
  - add route mapping for dry-run / execute (under controlled admin/local endpoint group)
- `backend/infrastructure/storage/`:
  - reuse existing repositories; no schema change
- `tests/unit/`:
  - add cleanup service selection/deletion tests
- `tests/integration/`:
  - add API dry-run/execute smoke test with temp data + temp intake folders
- `docs/task_board.md`:
  - set TASK_172 active during implementation, then mark complete with validation

---

## 5. Risks And Mitigation

1. Accidental deletion of wanted package  
Mitigation: dry-run first, explicit keep/remove list, confirmed-case protection.

2. Filesystem/DB mismatch after partial deletion  
Mitigation: perform record deletion in transaction boundary first, then storage delete; return detailed failure report.

3. Wrong “newest” selection  
Mitigation: deterministic ordering + unit tests for tie cases.

---

## 6. Validation Plan

- Unit tests:
  - group detection by hash/size
  - fallback grouping by name/size
  - keep newest package selection
  - skip confirmed/incomplete chains
  - deletion order and count
- Integration tests:
  - dry-run report correctness
  - execute removes redundant DB rows + intake folders, keeps canonical package

Manual smoke:

1. Import same `request.msg` multiple times to create duplicates.
2. Run cleanup dry-run and verify keep/remove list.
3. Execute cleanup.
4. Click `Load existing` repeatedly and verify it always opens the same current draft package.

---

## 7. Acceptance Criteria

- Duplicate history cleanup leaves one active draft package per identity.
- Confirmed projects are never deleted.
- Dry-run provides operator-visible keep/remove/skip details.
- Execute mode cleans DB + storage for removed package IDs.
- `Load existing` no longer opens stale historical duplicate package after cleanup.

---

## 8. Completion Notes

- Added backend service: `backend/application/duplicate_draft_history_cleanup_service.py`.
- Added cleanup API endpoints:
  - `GET /api/cleanup/intake-drafts/duplicate-history/dry-run`
  - `POST /api/cleanup/intake-drafts/duplicate-history/execute`
- Added dependency wiring in `backend/api/dependencies.py`.
- Added tests:
  - `tests/unit/test_duplicate_draft_history_cleanup_service.py`
  - `tests/integration/test_cleanup_api.py` (new duplicate cleanup API case)
- Behavior:
  - Groups unconfirmed Outlook MSG draft packages by email identity.
  - Keeps one latest package per duplicate group.
  - Deletes redundant package graph in order `draft -> case -> asset -> package`.
  - Deletes corresponding intake folder under `Data/intake/<package_id>`.
  - Skips confirmed/incomplete chains and reports skip reasons.

Validation:

- `py -m pytest tests/unit/test_duplicate_draft_history_cleanup_service.py tests/integration/test_cleanup_api.py -q` passed (`5 passed`).
