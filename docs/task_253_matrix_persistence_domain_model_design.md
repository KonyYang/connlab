# TASK_253 Matrix Persistence Domain Model Design

## 1. Purpose

Matrix is becoming an execution authority model, not a UI-only preview. This design stabilizes the persistence domain model before database, API, or frontend persistence implementation.

The model separates:

- the complete imported source Matrix
- editable project Matrix drafts
- selected group execution projection
- immutable confirmed project Matrix authority
- revision lineage and source traceability

This document intentionally does not define physical database tables.

## 2. Core Principles

Project remains the lifecycle container. Matrix owns the authoritative test execution map.

The full imported source Matrix is retained as a traceable source snapshot. The project execution Matrix is a selected and possibly edited projection from that source.

Drafts are editable. Confirmed matrices are immutable authority snapshots. Any change after confirmation creates a new draft and a new confirmed revision.

Sample Quantity / Sample Size is group-level data. It must not be modeled as a normal test item row or step cell.

## 3. Object Relationship

```text
Project
  -> SourceMatrixImport*
       -> SourceMatrix
            -> SourceMatrixRow*
            -> SourceMatrixGroup*
            -> SourceMatrixCell*

  -> ProjectMatrixDraft*
       -> DraftMatrixRow*
       -> DraftMatrixGroup*
       -> DraftMatrixCell*
       -> DraftStepOutputOverride*
       -> GroupSelectionProjection

  -> ConfirmedMatrixVersion*
       -> ConfirmedMatrixRow*
       -> ConfirmedMatrixGroup*
       -> ConfirmedMatrixCell*
       -> ConfirmedStepOutput*

  -> MatrixRevisionEvent*
```

Cardinality rules:

- One project can have many source Matrix imports.
- One project can have many drafts.
- One project can have many confirmed Matrix versions.
- One project can have only one active confirmed Matrix version.
- One draft can be based on a source Matrix, a previous confirmed Matrix, or both.
- One confirmed Matrix is produced from exactly one draft.

## 4. Domain Objects

### 4.1 SourceMatrixImport

Represents one import event from a source document. It is the traceability envelope around the parsed full Matrix.

Long-term persisted.

Recommended fields:

- `source_import_id`
- `project_id`
- `source_type`: `word_import | manual_seed | future_historical_project | future_library_template`
- `source_file_name`
- `source_format`: `docx | doc | pdf | xlsx | manual`
- `source_asset_id`
- `source_hash`
- `source_spec_number`
- `source_revision`
- `parse_time`
- `parser_version`
- `parse_status`: `previewed | imported | blocked`
- `warnings`
- `blockers`
- `selected_group_keys_at_import`
- `metadata`

Notes:

- `selected_group_keys_at_import` is trace metadata only. The authoritative selection lives in the draft/confirmed group model.
- Source metadata must survive even if the user selects only some groups.

### 4.2 SourceMatrix

Immutable parsed full source Matrix. It preserves all imported rows, groups, cells, notes, and sample expressions from the product specification Matrix.

Long-term persisted.

Recommended fields:

- `source_matrix_id`
- `source_import_id`
- `project_id`
- `source_matrix_version`
- `table_locator`: page, table index, keyword, sheet/table reference where available
- `row_count`
- `group_count`
- `status`

Rules:

- Never overwrite a SourceMatrix in place after import.
- Re-import creates a new SourceMatrix version/import.
- Full source Matrix is required for audit, comparison, re-import diffing, and future reuse.

### 4.3 SourceMatrixRow

One source test item row.

Long-term persisted.

Recommended fields:

- `source_row_id`
- `source_matrix_id`
- `row_order`
- `test_item`
- `section`
- `method`
- `condition`
- `requirement`
- `source_location`
- `raw_row_payload`

### 4.4 SourceMatrixGroup

One group column found in the source Matrix.

Long-term persisted.

Recommended fields:

- `source_group_id`
- `source_matrix_id`
- `group_order`
- `source_group_key`
- `raw_header_text`
- `group_label`
- `sample_quantity_expression`
- `sample_quantity_note`
- `source_location`

Notes:

- `source_group_key` is a stable imported identity, not only a display label.
- The imported group label may be edited later in a draft; source group content remains immutable.

### 4.5 SourceMatrixCell

One source row/group intersection.

Long-term persisted.

Recommended fields:

- `source_cell_id`
- `source_row_id`
- `source_group_id`
- `raw_step_token_value`
- `parsed_step_numbers`
- `token_markers`
- `source_note`
- `source_item_section_note`
- `parse_warning`

### 4.6 ProjectMatrixDraft

Editable project Matrix working copy. It can be created from a SourceMatrix import, a previous confirmed Matrix, manual seed, or future library/history source.

Long-term persisted while active or as audit history.

Recommended fields:

- `draft_id`
- `project_id`
- `base_source_matrix_id`
- `base_confirmed_matrix_id`
- `draft_revision`
- `status`: `editing | validation_blocked | ready_to_confirm | confirmed | abandoned | superseded`
- `created_at`
- `updated_at`
- `created_by`
- `updated_by`
- `validation_summary`
- `change_summary`

Rules:

- Draft is editable.
- Draft may contain only selected groups for the project working surface, but must retain lineage to full source groups.
- Draft cannot become execution authority until confirmed.

### 4.7 DraftMatrixRow

Editable test item row inside a draft.

Recommended fields:

- `draft_row_id`
- `draft_id`
- `source_row_id`
- `row_order`
- `test_item`
- `section`
- `method`
- `condition`
- `requirement`
- `row_state`: `imported | edited | added | removed_from_projection`

### 4.8 DraftMatrixGroup

Editable group column inside a draft.

Recommended fields:

- `draft_group_id`
- `draft_id`
- `source_group_id`
- `group_order`
- `group_label`
- `selected`
- `samples_quantity_pcs`
- `sample_quantity_expression`
- `sample_quantity_note`
- `selection_reason`
- `excluded_reason`
- `group_state`: `imported | edited | added | removed_from_projection`

Rules:

- `selected` controls whether the group participates in project execution.
- `samples_quantity_pcs` is group-level authority data after user confirmation.
- Sample quantity is not stored as a special row in DraftMatrixRow.
- Unselected groups can be hidden from execution views but remain traceable through draft/source lineage.

### 4.9 DraftMatrixCell

Editable draft row/group cell.

Recommended fields:

- `draft_cell_id`
- `draft_row_id`
- `draft_group_id`
- `step_token_value`
- `parsed_step_numbers`
- `token_markers`
- `cell_state`
- `validation_state`

### 4.10 DraftStepOutputOverride

Editable preview/output content derived from Matrix steps. This stores user edits to generated requirement/description text.

Recommended fields:

- `draft_step_output_id`
- `draft_id`
- `draft_group_id`
- `draft_row_id`
- `step_number`
- `requirement_text`
- `step_description`
- `remark_template`
- `source`: `auto_generated | user_edited`

Rules:

- If requirement/description remains generated and unedited, it can be recomputed.
- Once user edits it, it must be persisted in draft and carried into confirmed Matrix.

### 4.11 GroupSelectionProjection

Derived project execution selection view.

Recommended shape:

```text
project_id
draft_id or confirmed_matrix_id
groups:
  - group_identity
    group_label
    selected
    selection_order
    samples_quantity_pcs
    source_group_id
```

Rules:

- It should not be stored only as group-name strings.
- It may be materialized for consumers later, but the authority remains draft/confirmed group records.
- Execution views default to selected groups only.
- Unselected groups remain available for traceability and revision comparison.

### 4.12 ConfirmedMatrixVersion

Immutable authority snapshot for project execution.

Long-term persisted.

Recommended fields:

- `confirmed_matrix_id`
- `project_id`
- `confirmed_revision`
- `source_matrix_id`
- `draft_id`
- `is_active_authority`
- `status`: `active | superseded | withdrawn`
- `confirmed_by`
- `confirmed_at`
- `superseded_by`
- `superseded_at`
- `superseded_reason`
- `validation_summary_at_confirm`

Rules:

- Confirmed Matrix cannot be directly modified.
- A project can have only one `is_active_authority = true` confirmed Matrix.
- Confirming a new revision must deactivate/supersede the previous active confirmed Matrix in the same transaction.
- Fee, duration, equipment, test record, and report consumers should later read only the active confirmed Matrix, not draft or source Matrix.

### 4.13 ConfirmedMatrixRow

Immutable confirmed row snapshot.

Recommended fields:

- `confirmed_row_id`
- `confirmed_matrix_id`
- `source_row_id`
- `draft_row_id`
- `row_order`
- `test_item`
- `section`
- `method`
- `condition`
- `requirement`

### 4.14 ConfirmedMatrixGroup

Immutable confirmed selected group snapshot.

Recommended fields:

- `confirmed_group_id`
- `confirmed_matrix_id`
- `source_group_id`
- `draft_group_id`
- `group_order`
- `group_label`
- `selected`
- `samples_quantity_pcs`
- `sample_quantity_expression`
- `sample_quantity_note`

Rules:

- Confirmed execution views should normally include only `selected = true`.
- Unselected groups may be omitted from confirmed execution rows, but their source lineage must remain available through SourceMatrix.

### 4.15 ConfirmedMatrixCell

Immutable confirmed row/group cell snapshot.

Recommended fields:

- `confirmed_cell_id`
- `confirmed_row_id`
- `confirmed_group_id`
- `step_token_value`
- `parsed_step_numbers`
- `token_markers`

### 4.16 ConfirmedStepOutput

Immutable confirmed step output text used later by test records and reports.

Recommended fields:

- `confirmed_step_output_id`
- `confirmed_matrix_id`
- `confirmed_group_id`
- `confirmed_row_id`
- `step_number`
- `requirement_text`
- `step_description`
- `remark_template`
- `source`: `auto_generated | user_edited`

### 4.17 MatrixRevisionEvent

Audit/event record for import, draft creation, confirmation, supersession, and revision.

Recommended fields:

- `event_id`
- `project_id`
- `source_import_id`
- `source_matrix_id`
- `draft_id`
- `confirmed_matrix_id`
- `event_type`
- `actor`
- `created_at`
- `reason`
- `metadata`

## 5. Lifecycle

### 5.1 Import

```text
Word product specification
  -> parse preview
  -> SourceMatrixImport
  -> SourceMatrix full immutable snapshot
```

Preview is transient until the operator commits import. After commit, the full source Matrix is persisted.

### 5.2 Draft Creation

```text
SourceMatrix
  -> ProjectMatrixDraft
  -> Draft rows/groups/cells
  -> selected groups and samples quantity edited
```

The draft can start from all groups or an operator-selected subset. Unselected groups remain traceable through SourceMatrix.

### 5.3 Confirm

```text
ProjectMatrixDraft ready_to_confirm
  -> validation
  -> ConfirmedMatrixVersion active authority
  -> previous active confirmed Matrix superseded
```

Confirmation creates immutable execution authority.

### 5.4 Revision After Confirmation

```text
Active ConfirmedMatrixVersion
  -> create new ProjectMatrixDraft from confirmed version or new SourceMatrix
  -> edit groups/content/sample quantities
  -> confirm new revision
  -> old confirmed version superseded
```

No direct edit of confirmed authority is allowed.

## 6. Status Flow

Source import:

```text
previewed -> imported
previewed -> blocked
```

Draft:

```text
editing -> validation_blocked -> editing
editing -> ready_to_confirm -> confirmed
editing -> abandoned
confirmed -> superseded
```

Confirmed Matrix:

```text
active -> superseded
active -> withdrawn
```

## 7. Recommended Persistence Schema

This is a logical schema, not a physical database table design.

```text
SourceMatrixImport
SourceMatrix
SourceMatrixRow
SourceMatrixGroup
SourceMatrixCell

ProjectMatrixDraft
DraftMatrixRow
DraftMatrixGroup
DraftMatrixCell
DraftStepOutputOverride

ConfirmedMatrixVersion
ConfirmedMatrixRow
ConfirmedMatrixGroup
ConfirmedMatrixCell
ConfirmedStepOutput

MatrixRevisionEvent
```

Recommended invariants:

- Unique active confirmed Matrix per project.
- SourceMatrix is immutable after import.
- ConfirmedMatrixVersion is immutable after confirmation.
- Draft is the only editable Matrix persistence object.
- Group selection uses stable group identities, not display labels.
- Samples quantity is group-level and required for selected confirmed groups.

## 8. Transient Preview vs Long-Term Persistence

Transient:

- file picker state
- parser preview before import commit
- selected row/cell/group UI state
- hover tooltip state
- debounce locator/reparse input state
- validation messages derived from unsaved UI edits

Long-term:

- full imported SourceMatrix
- source metadata and parser warnings/blockers
- project draft rows/groups/cells
- selected group state
- group-level samples quantity
- user-edited step output requirement/description
- confirmed active authority snapshot
- revision events

## 9. Future Reuse Fields And Boundaries

Reserved but not implemented now:

- `source_type = historical_project`
- `source_project_id`
- `source_confirmed_matrix_id`
- `library_template_id`
- `lineage_parent_matrix_id`
- `business_domain`
- `product_family`
- `standard_refs`
- `method_refs`
- `equipment_hint_refs`
- `duration_hint_refs`
- `fee_category_hint_refs`

These fields should not trigger Matrix Library, historical reuse, fee, duration, equipment, or report implementation in this task.

## 10. Non-Goals

This task does not implement:

- database migrations or ORM models
- repositories
- API routes
- Matrix Editor save/confirm wiring
- Matrix Library
- historical project reuse
- fee assessment
- duration assessment
- equipment assessment
- test record persistence
- report generation
- StepInstance execution persistence

## 11. Suggested Follow-Up Tasks

1. `TASK_254_SOURCE_MATRIX_IMPORT_PERSISTENCE_MODEL`
   Define and implement persistence for SourceMatrixImport, SourceMatrix, SourceMatrixRow, SourceMatrixGroup, and SourceMatrixCell.

2. `TASK_255_PROJECT_MATRIX_DRAFT_PERSISTENCE_MODEL`
   Implement editable ProjectMatrixDraft persistence from SourceMatrix, including selected groups and group-level sample quantity.

3. `TASK_256_MATRIX_EDITOR_SAVE_TO_DRAFT_WIRING`
   Connect Matrix Editor current edit state to draft persistence without confirm semantics.

4. `TASK_257_CONFIRMED_MATRIX_AUTHORITY_MODEL`
   Implement confirmation from draft into immutable ConfirmedMatrixVersion with unique active authority per project.

5. `TASK_258_MATRIX_REVISION_FLOW`
   Implement create-new-revision flow from active confirmed Matrix or new source import.

6. `TASK_259_SELECTED_GROUPS_PROJECTION_CONSUMER`
   Expose selected groups projection for execution views while hiding unselected groups by default.

Downstream fee/duration/equipment/report tasks should wait until confirmed authority exists.
