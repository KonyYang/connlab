# TASK_254 Source Matrix Import Persistence Model Plan

## Phase / Active Task / Admission

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task for this plan: `TASK_254_SOURCE_MATRIX_IMPORT_PERSISTENCE_MODEL`
- Why allowed now:
  - `TASK_253` domain design is complete.
  - User explicitly approved executing `TASK_254`.

## Step 1: Task Understanding

1. Task goal:
   Persist imported full Source Matrix as long-term immutable structured records, including source metadata and parser diagnostics.
2. Inputs:
   Existing Matrix preview/import parse output (`groups`, `steps`, notes/metadata) and project/source identifiers.
3. Outputs:
   Persisted Source Matrix import records and structured row/group/cell snapshots.
4. Modules involved:
   `backend/domain`, `backend/application`, `backend/infrastructure/storage/models.py`, `backend/infrastructure/storage/repositories`, API import commit boundary, and related tests.
5. Forbidden:
   Draft/confirmed authority overhaul, matrix library/reuse consumers, downstream fee/report consumers, broad frontend refactor.

## Step 2: Design Summary

Implement this as a bounded persistence slice parallel to current `ProjectTestPlanDraft` flow:

1. Add domain objects for Source Matrix import snapshot.
2. Add storage models and repositories for these objects.
3. Add an application service to persist a committed import snapshot from existing parse output.
4. Wire import commit path to call that service.
5. Keep current preview response contracts stable.

Additional mandatory boundaries for this task:

- Avoid continuing monolithic growth in `backend/infrastructure/storage/models.py`.
- Persist SourceMatrixCell as sparse non-empty cells only.
- Persist `payload_schema_version` (separate from parser version).
- Enforce all-or-nothing transaction for import snapshot persistence.
- Treat `selected_group_keys_at_import` as trace metadata only.

## Target Domain Objects (logical)

- `SourceMatrixImportRecord`
- `SourceMatrixSnapshot`
- `SourceMatrixRowSnapshot`
- `SourceMatrixGroupSnapshot`
- `SourceMatrixCellSnapshot`

Initial statuses can be minimal (`imported`, `blocked`) and expanded in later tasks.

## Planned File-Level Changes

1. Domain
   - `backend/domain/enums.py`
   - `backend/domain/models.py`
   - `backend/domain/__init__.py`
2. Storage models
   - Create dedicated Matrix-source storage model module(s), for example:
     - `backend/infrastructure/storage/models_matrix_source.py`
   - Keep existing `backend/infrastructure/storage/models.py` compatibility stable.
   - Do not add the full Matrix source entity set directly into one monolithic `models.py`.
3. Repositories
   - new repository module under `backend/infrastructure/storage/repositories/` for Source Matrix entities
   - `backend/infrastructure/storage/repositories/__init__.py`
4. Application service
   - new `backend/application/source_matrix_import_persistence_service.py`
5. Dependency wiring
   - `backend/api/dependencies.py`
6. API integration
   - matrix import commit route module(s) only where needed to persist snapshot on import confirm/commit
7. Tests
   - new unit tests for service + repository behavior
   - focused integration test for import commit persistence side effect

## Data/Identity Rules In This Task

1. Persist full source matrix, not only selected groups.
2. Persist source metadata:
   - file name
   - format
   - spec number
   - revision
   - parse time
   - parser version
   - payload schema version
   - warnings/blockers
   - selected groups trace list
3. Persist row/group/cell ordering for deterministic reconstruction.
4. Snapshot immutability:
   - no in-place update API in this task
   - new import creates new snapshot/import record
5. SourceMatrixCell is sparse:
   - persist only non-empty cell intersections (non-empty token/note/sample-relevant cell payload)
   - empty intersections are reconstructed as implicit empty during read projection
6. `selected_group_keys_at_import` is non-authoritative trace metadata:
   - it must not drive execution authority state
   - it is retained for audit/debug/replay context only

## Risk Notes

1. Existing matrix payload has evolved with note fields; mapping must preserve unknown payload extensions safely.
2. Multiple `TASK_252*` changes touched import behavior; integration points must stay narrow to avoid regressions.
3. Existing `ProjectTestPlanDraft` remains active; this task must not accidentally change draft confirmation semantics.
4. Sparse cell persistence must not drop meaningful note-only cells; non-empty criteria must include token/note/sample expression payload.
5. If transaction boundary is not explicit, partial write risks corrupt lineage; this task must centralize write operations in one session transaction.

## Import Transaction Boundary

Source Matrix import commit persistence must be atomic:

- one transaction includes:
  - `SourceMatrixImportRecord`
  - `SourceMatrixSnapshot`
  - all rows
  - all groups
  - all sparse non-empty cells
- if any insert fails, the transaction is rolled back fully
- no partial snapshot is visible to readers

Repository/service boundary:

- application service orchestrates one transaction scope
- repository helpers may perform inserts, but must not commit independently mid-snapshot

## Validation Plan

1. Unit tests:
   - metadata required fields persisted
   - `payload_schema_version` persisted and retrievable
   - rows/groups/cells persisted with stable ordering
   - sparse cell persistence excludes empty intersections and retains non-empty note/token/sample cells
   - immutable snapshot behavior (no overwrite path)
   - `selected_group_keys_at_import` stored as trace metadata only
   - transaction rollback on mid-write failure leaves no partial snapshot
2. Integration tests:
   - import commit creates Source Matrix snapshot
   - import commit failure does not create partial persisted entities
   - existing preview endpoints still work
3. Build check:
   - `cd frontend && npm run build` to ensure no frontend type break from client contract drift

## Out Of Scope (Explicit)

- Confirmed matrix unique authority enforcement
- Draft/confirmed revision lifecycle rewrite
- Group selection projection consumer surfaces
- Fee/duration/equipment/report consumer integration
- Matrix library/historical reuse implementation

## Execution Readiness

Plan is ready for implementation after explicit user approval.
