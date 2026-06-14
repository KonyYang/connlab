# TASK_315B_PENDING_REBASE_PERSISTENCE_AND_MATRIX_AUTOSAVE_CANCEL_LIFECYCLE

Status: Complete.

Executable plan: `docs/task_315b_pending_rebase_persistence_and_matrix_autosave_cancel_lifecycle_plan.md`

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Parent umbrella: `TASK_315_MATRIX_DRAFT_TO_FEE_DRAFT_INCREMENTAL_REBASE`.

Prerequisite: `TASK_315A_MATRIX_TO_FEE_REBASE_CORE` is complete.

TASK_315B is the second executable slice of TASK_315. It adds persistence for pending Matrix-to-Fee rebase output and wires Matrix Editor autosave/cancel lifecycle to that pending state. It must not promote pending rebase into a current Fee pricing draft after Matrix Confirm; that belongs to TASK_315C.

## Why This Task Was Allowed

TASK_315A created the pure backend rebase core and validated matching behavior. The user explicitly approved TASK_315B implementation after the reviewable task file and executable plan were created. TASK_315B was allowed because it is the next controlled slice after completed TASK_315A.

TASK_315C still requires a separate task file, reviewable plan, and explicit approval.

## Goal

After Matrix Editor autosave successfully saves a current Matrix draft, run a non-fatal best-effort Matrix-to-Fee rebase and persist one pending rebase snapshot for that Matrix draft and fee rule version.

Canceling the Matrix draft must delete the matching pending rebase.

Autosave/Cancel race behavior must be deterministic:

- if rebase succeeds, Matrix autosave response returns current rebase status and summary;
- if rebase fails, Matrix autosave itself still succeeds and returns failed rebase status;
- if a stale autosave/rebase completes after a newer autosave, strict compare-and-swap guards must prevent it from overwriting the newer pending rebase;
- if Cancel deletes the Matrix draft while a rebase is running or about to save, no pending rebase may be recreated for the deleted draft.

## Inputs

- Saved Matrix Editor draft snapshot from `MatrixEditorSessionService.save_editor_draft`.
- Active Confirmed Matrix authority for the project.
- Current/base Fee pricing draft for the active Confirmed Matrix context, when present.
- Existing Fee Evaluation default draft/basic-fill construction path.
- `MatrixFeeDraftRebaseService` output from TASK_315A.

## Outputs

- A pending Fee rebase record bound to `project_matrix_draft_id` and `fee_rule_version_id`.
- Extended Matrix autosave response fields:
  - `fee_rebase_status`
  - `fee_rebase_summary`
  - `fee_rebase_error`
- Matrix draft discard deletes pending Fee rebase state for the discarded Matrix draft.

## V1 Status Contract

Use these backend/API status strings:

```text
not_required | current | failed
```

Meanings:

- `not_required`: no active Confirmed Matrix exists, no saved Matrix draft exists, or Matrix autosave did not need/could not start rebase in this scope.
- `current`: pending rebase was saved for the current Matrix draft and current fee rule version.
- `failed`: Matrix autosave succeeded, but pending rebase was not saved. Response must include an actionable `fee_rebase_error`.

Fee rebase failure must never change Matrix autosave HTTP success into a failure.

## In Scope

- Pending rebase application value models and store Protocol.
- Pending rebase SQLAlchemy model/table and repository.
- SQLite migration/helper for existing local databases.
- Non-fatal best-effort rebase application service that:
  - loads base active Confirmed Matrix and current/base Fee pricing draft/default values;
  - verifies the saved Matrix draft `base_confirmed_matrix_id` still matches the active Confirmed Matrix before rebasing;
  - builds source and target inputs for `MatrixFeeDraftRebaseService`;
  - upserts pending rebase only if the saved Matrix draft still exists, the saved signature still matches, and the stale-write token/generation is newer than the stored pending record;
  - returns failed status on rebase/storage error without failing Matrix autosave.
- Matrix Editor autosave integration after the Matrix draft is saved.
- Matrix Editor discard integration that deletes pending rebase for the discarded Matrix draft.
- Backend API response extension for Matrix autosave rebase status.
- Backend unit/integration tests for persistence, autosave status, cancel cleanup, and stale/race guards.

## Out Of Scope

- No Matrix Confirm promotion to current Fee pricing draft.
- No confirm-time synchronous rebase fallback.
- No Fee Evaluation UI display of inactive rows.
- No frontend Matrix Editor status display or UI copy changes unless the backend API response type requires a minimal TypeScript compile follow-up in a later approved UI slice.
- No Confirm Fee behavior change.
- No Project Folder Required forms behavior change beyond regression expectations.
- No pricing formula/rule changes.
- No StepInstance, report generation, evidence/image, AI, permissions, LAN/server, or multi-user scope.

If implementation needs any out-of-scope behavior, stop and split it into TASK_315C or TASK_315D.

## Acceptance Criteria

- Saving a Matrix Editor draft for an existing active Confirmed Matrix attempts a pending Fee rebase after the Matrix draft save succeeds.
- A successful rebase creates or replaces one pending record for `project_matrix_draft_id + fee_rule_version_id`.
- Repeated autosaves for the same draft/rule update the same pending record rather than creating duplicates.
- Autosave response includes `fee_rebase_status="current"` and preserved/added/removed summary when pending rebase is saved.
- Rebase failure returns `fee_rebase_status="failed"` and an actionable error while Matrix autosave response remains successful.
- Cancel Matrix deletes pending rebase for the discarded Matrix draft.
- Cancel after a pending or slow autosave/rebase cannot leave a recreated pending rebase for a deleted Matrix draft.
- A stale autosave/rebase generation, including equal-generation out-of-order completion, cannot overwrite a newer pending rebase for the same Matrix draft/rule.
- If the saved Matrix draft `base_confirmed_matrix_id` no longer matches the active Confirmed Matrix, no pending rebase is saved.
- Pending payload preserves active rows, inactive removed rows, manual rows, and summary metadata from the TASK_315A rebase result.
- No current Fee pricing draft is created or modified by TASK_315B.
- No Confirmed Fee authority is created or modified by TASK_315B.
- No API route outside Matrix Editor session draft save/discard is changed.

## Required Validation

```powershell
py -m pytest tests/unit/test_matrix_fee_pending_rebase_service.py tests/unit/test_matrix_fee_pending_rebase_repository.py -q
```

```powershell
py -m pytest tests/unit/test_matrix_editor_session_service.py tests/integration/test_matrix_editor_session_api.py -q
```

```powershell
py -m pytest tests/unit/test_matrix_fee_draft_rebase_service.py -q
```

If storage model/database migration is touched:

```powershell
py -m pytest tests/unit/test_database.py -q
```

No frontend test/build is required unless frontend code is changed, which should not happen in TASK_315B.

## Stop Point

Stop after TASK_315B implementation, validation, and task board update if and only if the user explicitly approves implementation. Do not proceed to TASK_315C, TASK_315D, Matrix Confirm promotion, Fee UI, Project Folder, StepInstance, report, AI, permissions, LAN/server, or multi-user scope without separate explicit approval.

## Completion Notes

Implemented pending Matrix-to-Fee rebase persistence and Matrix autosave/cancel lifecycle integration:

- Added `MatrixFeePendingRebaseService`, pending rebase commands/results/snapshot, payload serialization, and a default builder that rebases current basic-fill/pricing draft values onto the saved Matrix draft target rows.
- Added `MatrixFeePendingRebaseModel` and `MatrixFeePendingRebaseRepository` with one pending row per Matrix draft/rule and strict generation guards that reject older or equal stale writes.
- Matrix Editor autosave now returns `fee_rebase_status`, `fee_rebase_summary`, and `fee_rebase_error`; Fee rebase failures do not fail Matrix autosave.
- Matrix Editor discard deletes pending rebase rows for the discarded draft and surfaces cleanup failure as an actionable draft conflict.
- Integration tests verify autosave creates pending storage and Cancel removes it.

Validation:

```powershell
py -m pytest tests/unit/test_matrix_fee_pending_rebase_service.py tests/unit/test_matrix_fee_pending_rebase_repository.py -q
# 13 passed

py -m pytest tests/unit/test_matrix_editor_session_service.py tests/integration/test_matrix_editor_session_api.py -q
# 20 passed

py -m pytest tests/unit/test_matrix_fee_draft_rebase_service.py -q
# 15 passed

py -m pytest tests/unit/test_database.py -q
# 5 passed
```

## Review Follow-Up

Completed on 2026-06-15:

- Fixed target Matrix draft token `step_index` to use the same 0-based indexing as Confirmed Matrix basic-fill rows, preserving existing pricing edits for unchanged Matrix rows.
- Matrix Editor Cancel now performs pending rebase cleanup before and after Matrix draft deletion, closing the interleaving where a slow autosave rebase could recreate pending rows between cleanup and draft deletion.
- `MatrixFeePendingRebaseRepository.upsert_current()` now uses SQLite `INSERT ... ON CONFLICT DO UPDATE ... WHERE existing.generation < incoming.generation`, making stale generation rejection database-level compare-and-swap rather than read-then-update.
- Added regression coverage for pricing edit preservation, post-delete Cancel cleanup, and cross-session stale generation overwrite.

Validation:

```powershell
py -m pytest tests/unit/test_matrix_fee_pending_rebase_service.py tests/unit/test_matrix_fee_pending_rebase_repository.py -q
# 13 passed

py -m pytest tests/unit/test_matrix_editor_session_service.py tests/integration/test_matrix_editor_session_api.py -q
# 20 passed

py -m pytest tests/unit/test_matrix_fee_draft_rebase_service.py -q
# 15 passed

py -m pytest tests/unit/test_database.py -q
# 5 passed
```
