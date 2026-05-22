# TASK_255 Project Matrix Draft Persistence Model Plan

## 0) Anti-Skip Protocol

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task for this plan: `TASK_255_PROJECT_MATRIX_DRAFT_PERSISTENCE_MODEL`
- Why this task is allowed now:
  - `TASK_253` defined the Matrix persistence model sequence.
  - `TASK_254` completed Source Matrix import persistence.
  - The next approved design step is editable Project Matrix Draft persistence, before confirmed authority.

This document is a plan only. No implementation should start until user approval.

## 1) Task Goal

Create the backend persistence layer for editable Project Matrix Draft working copies derived from immutable Source Matrix snapshots.

The draft is the editable project-specific working state. Source Matrix remains the immutable imported source record. Confirmed Matrix authority remains a future task.

## 2) Inputs And Outputs

Input:

- Existing persisted `SourceMatrixImportRecord`
- Existing persisted `SourceMatrixSnapshot`
- Optional selected source group keys for draft initialization

Output:

- Persisted Project Matrix Draft record
- Persisted draft groups, rows, and sparse cells
- Stable lineage from draft back to Source Matrix import/snapshot
- Draft-local selected group state and group-level sample quantity state

## 3) Proposed Data Boundary

Project Matrix Draft owns editable working-copy state:

- draft identity and lifecycle status
- source import lineage
- selected groups for the draft
- group display label and sample quantity expression
- row order, test item, source section
- sparse group-cell values

Source Matrix owns immutable import source truth:

- imported rows/groups/cells
- parser/import metadata
- original source table identity
- import warnings/blockers

Selection default:

- If the create command provides explicit selected group keys, use those keys.
- If no explicit selection is provided, initialize from `selected_group_keys_at_import`.
- If import metadata has no selected group keys, initialize with all Source Matrix groups.
- This is draft-local state only. It is not confirmed authority and must not be exposed as active execution authority.

Sample quantity:

- `sample_quantity_expression` on draft group is the single editable draft truth.
- Source sample rows are preserved for traceability only.
- Source sample rows must not become a parallel editable truth for draft sample quantity.

Cell storage:

- Draft cells are sparse and non-empty.
- Empty source cells are not persisted as draft cells.
- Later update semantics for an empty string must delete the draft cell row for that row/group intersection rather than preserving an empty-value row.

Confirmed Matrix authority is out of scope.

## 4) File-Level Change Plan

1. Domain
   - Add `backend/domain/project_matrix_draft_models.py`
   - Export new draft domain classes through `backend/domain/__init__.py`
   - Add draft status enum only if existing `ProjectTestPlanDraftStatus` is insufficient for the new structured draft boundary.

2. Storage
   - Add `backend/infrastructure/storage/models_project_matrix_draft.py`
   - Register the model module in `init_db`.
   - Keep the module separate from `backend/infrastructure/storage/models.py`.

3. Repository
   - Add `backend/infrastructure/storage/repositories/project_matrix_draft.py`
   - Implement create/load/list operations for draft record + groups + rows + sparse cells.
   - Keep repository operations session-scoped and atomic through caller transaction.
   - Draft root, groups, rows, and cells must be flushed as one atomic unit. Any failure rolls back the entire draft creation.
   - Reject repeated creation for the same `project_id + source_import_id` in this task with a conflict-style application error.

4. Application service
   - Add `backend/application/project_matrix_draft_persistence_service.py`
   - Create draft from Source Matrix import snapshot.
   - Apply selected group subset when provided.
   - Apply default selected-group behavior from `selected_group_keys_at_import`, then all Source Matrix groups as fallback.
   - Initialize draft group sample quantity from source group sample data.
   - Preserve lineage and avoid modifying Source Matrix.

5. API integration
   - Add only a minimal backend route if required by acceptance tests.
   - Route must call the application service only.
   - Route must not directly call repositories.
   - Do not wire Matrix Editor frontend save behavior in this task.

6. Tests
   - Add unit tests for service mapping.
   - Add repository tests for persistence and sparse cells.
   - Add integration test for API/service path if a minimal route is introduced.
   - Add an atomic rollback test that deliberately triggers a uniqueness failure and verifies no draft root/group/row/cell rows remain.

## 5) Data Model Sketch

Draft root:

- `project_matrix_draft_id`
- `project_id`
- `source_import_id`
- `source_snapshot_id`
- unique draft creation guard for `project_id + source_import_id`
- `status`
- `created_at`
- `updated_at`

Draft group:

- `draft_group_id`
- `project_matrix_draft_id`
- `source_group_snapshot_id`
- `group_order`
- `group_key`
- `group_label`
- `is_selected`
- `sample_quantity_expression`
- `sample_note`

Draft row:

- `draft_row_id`
- `project_matrix_draft_id`
- `source_row_snapshot_id`
- `row_order`
- `test_item`
- `source_section`
- `is_sample_row`

Draft cell:

- `draft_cell_id`
- `project_matrix_draft_id`
- `draft_row_id`
- `draft_group_id`
- `cell_value`

## 6) Risks And Controls

Risk: Draft persistence accidentally becomes confirmed authority.

- Control: no active-confirmed flag, no confirmation endpoint, no unique active authority constraint.

Risk: Source Matrix mutable state leaks into draft edits.

- Control: draft stores copies with lineage IDs; Source Matrix tables are read-only inputs for this task.

Risk: selected groups are confused with authority projection.

- Control: selected groups are draft-local working-copy state only.

Risk: duplicate row/group/cell ordering creates ambiguous drafts.

- Control: add unique constraints for draft row order, group order, and row/group cell identity.

Risk: repeated source import draft creation creates ambiguous editable working copies.

- Control: reject duplicate `project_id + source_import_id` creation in TASK_255. Superseded multi-draft behavior belongs to a later revision-flow task.

Risk: sample quantity exists as both editable group field and editable sample row.

- Control: only group-level `sample_quantity_expression` is editable draft truth. Source sample rows remain trace lineage.

Risk: partial draft rows are committed if child insert fails.

- Control: create draft root, groups, rows, and cells inside one transaction and test rollback on a deliberate uniqueness failure.

Risk: API route bypasses application rules.

- Control: any route introduced in this task must call application service only and never directly instantiate repository operations for business behavior.

## 7) Validation Plan

Run:

```powershell
py -m pytest tests\unit\test_project_matrix_draft_persistence_service.py tests\unit\test_project_matrix_draft_repository.py -q
```

Run:

```powershell
py -m pytest tests\integration\test_project_matrix_draft_from_source_matrix_api.py tests\unit\test_source_matrix_persistence_service.py -q
```

Required test cases:

- Happy path creates draft root/groups/rows/sparse cells from Source Matrix.
- Selected group subset is persisted as draft-local state.
- No explicit selection defaults to `selected_group_keys_at_import`.
- Empty import selection defaults to all Source Matrix groups.
- Group-level `sample_quantity_expression` initializes from source group data.
- Sparse cell behavior stores only non-empty values.
- Empty string update/delete semantics removes draft cell row when update support is introduced.
- Duplicate `project_id + source_import_id` creation returns a conflict-style application error.
- Deliberate uniqueness failure rolls back draft root/group/row/cell writes.
- Source Matrix tables remain unchanged after draft creation.

Optional broader check:

```powershell
py -m pytest tests\unit\test_project_test_plan_draft_service.py tests\integration\test_project_test_plan_draft_api.py -q
```

## 8) Out Of Scope

- Frontend Matrix Editor save wiring
- Confirmed Matrix authority
- Matrix revision flow
- Runtime execution projection
- StepInstance persistence
- Report, fee, duration, and equipment assessment
