# TASK_254_SOURCE_MATRIX_IMPORT_PERSISTENCE_MODEL

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_254_SOURCE_MATRIX_IMPORT_PERSISTENCE_MODEL`.

## Why This Task Is Allowed Now

`TASK_253_MATRIX_PERSISTENCE_DOMAIN_MODEL_DESIGN` completed the domain boundary design and explicitly recommended Source Matrix persistence as the first implementation slice.

The user explicitly approved executing `TASK_254`.

## Model Fit Assessment

`GPT-5.3-codex` with `high` reasoning is suitable.

Reason:

- This task introduces a new persistence slice that becomes the long-term lineage foundation for later draft/confirmed matrix revisions.
- Correct identity, immutability, and source metadata boundaries are higher-risk than routine CRUD wiring.
- Existing Matrix preview/import flow must be integrated without breaking current APIs.

## Objective

Implement the first persistence slice for Source Matrix import authority:

1. Persist Source Matrix import records as structured objects.
2. Persist full parsed Source Matrix (rows/groups/cells) as immutable snapshots.
3. Persist required source metadata for traceability.
4. Keep current preview/import behavior compatible.
5. Do not implement draft persistence rewrite, confirmed authority rewrite, or downstream consumers in this task.
6. Persist Source Matrix cells using non-empty sparse strategy only.
7. Include `payload_schema_version` in persisted import snapshot metadata.
8. Enforce atomic import persistence transaction (all-or-nothing).

## Scope

Allowed:

- `backend/domain/*` for new Source Matrix domain objects/enums as needed.
- `backend/infrastructure/storage/models.py` for new storage models.
- `backend/infrastructure/storage/repositories/*` for Source Matrix repositories.
- `backend/application/*` for import persistence orchestration service.
- `backend/api/*` only where required to wire existing import commit path to persistence.
- `tests/unit/*` and `tests/integration/*` for new persistence behavior.
- task and board documentation.

Forbidden:

- Matrix Library / historical project reuse implementation.
- confirmed matrix authority implementation.
- full ProjectMatrixDraft model replacement.
- fee/duration/equipment/report consumer wiring.
- broad frontend redesign.
- destructive migration shortcuts.

## Required Business Rules

1. Full source matrix must be stored long term, not only selected groups.
2. Source matrix snapshots are immutable once committed.
3. Source metadata must include:
   - source file name
   - source format
   - source spec number
   - source revision
   - parse time
   - parser version
   - warnings/blockers
   - selected groups (trace metadata)
4. Task does not redefine active confirmed matrix authority yet; that remains for subsequent tasks.
5. `selected_group_keys_at_import` is trace metadata only and must not be interpreted as authority projection state.

## Storage Model Boundary

Avoid expanding a single giant `backend/infrastructure/storage/models.py`.

Implementation in this task must use a dedicated Matrix source storage module strategy:

- Prefer new module(s) under `backend/infrastructure/storage/` for Matrix source persistence models.
- Keep `models.py` compatibility surface stable for existing imports, but do not continue adding new Matrix source entities directly into one monolithic model file.
- Ensure model registration remains compatible with existing SQLAlchemy metadata bootstrap.

## Acceptance Criteria

- Source import commit creates a persisted Source Matrix snapshot (import + rows + groups + cells).
- Snapshot is retrievable by project and import identity.
- Snapshot stores metadata and parser diagnostics required by business rules.
- Snapshot includes `payload_schema_version` as explicit schema compatibility marker.
- SourceMatrixCell persistence is sparse: only non-empty source row/group intersections are saved.
- Import persistence is atomic; partial snapshot persistence is not allowed.
- Existing preview path remains functional.
- No regressions in current matrix preview API behavior.
- Tests cover happy-path persistence and key validation/error cases.

## Validation

```powershell
py -m pytest tests\unit\test_source_matrix_persistence*.py -q
```

```powershell
py -m pytest tests\integration\test_project_test_plan_preview_api.py -q
```

```powershell
cd frontend
npm run build
```
