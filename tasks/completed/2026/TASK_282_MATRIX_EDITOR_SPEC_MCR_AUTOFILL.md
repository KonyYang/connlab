# TASK_282_MATRIX_EDITOR_SPEC_MCR_AUTOFILL

## Status

Complete.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Allowed Reason

TASK_281 is complete and the task board currently has no active implementation task. The user approved planning the next controlled Matrix Editor task: automatically prefill Method, Condition, and Requirement from the imported engineering specification so operators do not copy/paste those fields manually.

## Objective

When a user imports an engineering specification into Matrix Editor, ConnLab should not only parse the Matrix table rows and group tokens. It should also use each Matrix row's `Section` value to read the matching specification chapter text and prefill these Matrix Editor columns when deterministically available:

- `Method`
- `Condition`
- `Requirement`

The values are prefilled into the editable Matrix Editor table before confirmation. The operator can review, modify, or leave blank values before clicking `Confirm Matrix`.

## Business Context

Real engineering specifications contain the source authority for each test item. The Matrix table normally identifies `Test Items` and `Section`; the corresponding section body contains the test method standard, conditions, and acceptance requirement. Lab engineers currently read those sections and manually copy the values into Matrix/Test Record/Report material. TASK_282 starts automating that work while preserving human review.

## Scope

### In Scope

1. Extend source Matrix/specification parsing so parsed Matrix preview rows may include:
   - `method`
   - `condition`
   - `requirement`
   - extraction status metadata for those fields.
2. Extract details by matching Matrix row `section` values to specification section body text.
3. Prefill Matrix Editor rows with extracted Method/Condition/Requirement values during import/session seed.
4. Preserve existing editable behavior: users can manually edit the prefilled values before `Confirm Matrix`.
5. Keep missing or low-confidence fields blank instead of inventing values.
6. Add backend tests using a representative `.docx` fixture shape.
7. Add frontend tests proving imported rows show prefilled values in Matrix Editor.
8. Preserve existing selected-group, sample guard, note, source lineage, and confirm behavior.

### Out Of Scope

Do not implement in TASK_282:

- AI or LLM extraction.
- StepInstance, execution persistence, evidence/image management, report generation, fee calculation, permissions, multi-user behavior, or LAN deployment.
- A full method-library maintenance UI.
- Silent overwrite of user-edited Method/Condition/Requirement values after the editor is loaded.
- Cross-project method learning.
- Parsing arbitrary non-Matrix documents as runtime authority.
- Replacing Confirm Matrix or changing Matrix authority lifecycle semantics.

## Extraction Decision

### Primary Source

Use the imported engineering specification itself:

```text
Matrix row Section -> matching specification section body -> Method / Condition / Requirement
```

Example:

```text
Test Item: Contact Resistance (Low Level)
Section: 6.1
Section body contains: EIA-364-23, 20mV max, 100mA max, resistance limit.
```

### Fallback Source

TASK_282 may introduce a small internal deterministic fallback only for very stable cases already visible in the reference modules, but it must not override specification-section extraction. A broader method library should be deferred to a later task.

## Extraction Rules

1. Match section headings by exact section number first, for example `6.1`, `6.3.1`, `8.6`.
2. Capture section text until the next peer/next section heading.
3. Extract Method from deterministic standard patterns such as:
   - `EIA-364-23`
   - `EIA 364-23`
   - `EIA-364-70D`
   - project-specific method text when explicitly stated.
4. Extract Condition only when deterministic condition phrases are present in the same section body.
5. Extract Requirement only when deterministic acceptance/limit phrases are present in the same section body.
6. If extraction is partial, fill only the fields that were extracted confidently.
7. If the section is missing or ambiguous, leave fields blank and mark extraction as missing/partial.
8. Do not invent limits, units, or standard revisions.

## Data Contract

Extend the existing Matrix import preview row shape without replacing it:

```text
test_item
source_section
method
condition
requirement
detail_extraction_status
detail_extraction_source_section
detail_extraction_notes
```

The status should be business-readable and deterministic:

```text
matched
partial
missing
ambiguous
```

If implementation needs a narrower internal structure, the API response may still expose a compact equivalent, as long as tests prove Method/Condition/Requirement are preserved through:

```text
preview -> Matrix Editor session -> editable draft -> Confirm Matrix
```

### Existing Data Flow Gap To Close

Current storage/session infrastructure already preserves `method`, `condition`, and `requirement` in Matrix Editor session rows, draft rows, and confirmed Matrix rows. TASK_282 must close the remaining source-preview gaps:

1. `MatrixRowPreview` must carry row-level `method`, `condition`, `requirement`, and extraction status fields.
2. `SourceMatrixRowSnapshot` must carry row-level `method`, `condition`, and `requirement` so persisted Source Matrix snapshots do not lose extracted details.
3. Source Matrix persistence and repository mapping must write/read those row-level fields.
4. `matrix_editor_session_service._build_source_preview_payload()` must output those fields when reconstructing `source_preview_payload` from a persisted source snapshot.
5. Cached `source_preview_payload` and rebuilt `source_preview_payload` must expose equivalent row-level MCR fields.

### Row-Level And Step-Level Field Boundary

`MatrixStepPreview` already has step-level legacy fields:

```text
condition_summary
method_summary
reference_standard
judgement_criteria
```

TASK_282 must not repurpose or remove those fields. New `method`, `condition`, and `requirement` fields belong to `MatrixRowPreview` and represent the row-level authority values extracted from the specification section. Step-level fields remain token/step preview metadata.

### Parser Size Constraint

`backend/modules/test_plan/product_spec_matrix_parser.py` is already above the AGENTS.md hard limit. TASK_282 must not add section extraction and MCR extraction logic directly into that file.

Required split:

```text
backend/modules/test_plan/spec_section_text_extractor.py
```

The new module owns:

- section heading detection.
- section body collection.
- deterministic Method/Condition/Requirement extraction.
- extraction status calculation.

`product_spec_matrix_parser.py` should only call the extractor and attach returned row-level details to `MatrixRowPreview`. If practical in the same task, reduce `product_spec_matrix_parser.py` below 500 lines without unrelated refactors.

## UI/UX Requirements

Matrix Editor should treat extracted values as normal editable table values. It should not add a separate blocking preview screen in TASK_282.

Minimum UI clarity:

1. Prefilled values appear directly in the Method/Condition/Requirement cells.
2. Empty required cells continue to be visibly empty/required according to existing Matrix Editor behavior.
3. If status copy is added, it must be concise and non-technical, for example `Needs review`.
4. Do not add a large new panel or extra import step.
5. Do not expose parser internals, raw regexes, API paths, or backend error text to users.

## Expected Files

Backend:

- `backend/modules/test_plan/product_spec_matrix_parser.py`
- `backend/modules/test_plan/spec_section_text_extractor.py`
- `backend/domain/source_matrix_models.py`
- `backend/infrastructure/storage/models_matrix_source.py`
- `backend/infrastructure/storage/repositories/source_matrix_import.py`
- `backend/application/source_matrix_import_persistence_service.py`
- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/application/matrix_editor_session_service.py`
- `backend/application/matrix_import_commit_service.py` only if needed for source-replacement persistence.

Frontend:

- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/matrixImportSessionModel.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

Tests:

- `tests/unit/test_product_spec_matrix_parser.py`
- `tests/integration/test_project_test_plan_preview_api.py`
- `tests/unit/test_matrix_editor_session_service.py`
- `tests/unit/test_matrix_import_commit_service.py` only if commit mapping changes.
- `tests/unit/test_frontend_shell_files.py`

Task tracking:

- `tasks/TASK_282_MATRIX_EDITOR_SPEC_MCR_AUTOFILL.md`
- `docs/task_282_matrix_editor_spec_mcr_autofill_plan.md`
- `docs/task_board.md`
- `docs/task_plan_index.md`

## Acceptance Criteria

1. A `.docx` engineering specification with Matrix rows and matching section body text can produce preview rows with Method/Condition/Requirement populated.
2. Matrix Editor import loads those populated values directly into the editable Method/Condition/Requirement columns.
3. Partial extraction fills only confident fields and leaves uncertain fields blank.
4. Missing section text does not block Matrix import.
5. Persisted `SourceMatrixRowSnapshot` rows preserve Method/Condition/Requirement.
6. Rebuilt `source_preview_payload` from persisted source snapshots includes Method/Condition/Requirement.
7. Existing row metadata, step metadata, and note fields are preserved.
8. Step-level legacy fields remain distinct from row-level Method/Condition/Requirement.
9. Group selection, selected-only filtering, sample guard, and Confirm Matrix behavior remain unchanged.
10. Confirmed Matrix snapshots preserve the prefilled values after user confirmation.
11. No AI, StepInstance, execution persistence, report, fee, evidence/image, permission, or multi-user scope is introduced.
12. Tests cover at least:
   - exact section extraction.
   - partial extraction.
   - missing section behavior.
   - persisted source snapshot round trip.
   - rebuilt `source_preview_payload` output.
   - frontend import prefill display.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for execution.

Reason:

- The task is a bounded parser/application/frontend wiring task with existing Matrix import and session boundaries.
- The main risk is deterministic extraction quality, which can be controlled with fixtures and tests.
- The implementation should be serial and test-driven because Matrix import/session state is coupled.

## Validation Plan

```powershell
py -m pytest tests\unit\test_product_spec_matrix_parser.py -q
py -m pytest tests\integration\test_project_test_plan_preview_api.py -q
py -m pytest tests\unit\test_matrix_editor_session_service.py -q
cd frontend; npm test -- --run MatrixEditorWorkspace --watch=false
cd frontend; npm run build
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task282 or matrix_editor"
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
git diff --check
```

## Follow-Up Task Direction

Potential later tasks after TASK_282:

- `TASK_283`: Review affordances and filters for rows whose extracted details need manual review.
- `TASK_284`: Deterministic method-library fallback and library data maintenance.

Do not implement these follow-up tasks inside TASK_282.

## Stop Rule

After TASK_282 implementation and validation, stop. Do not continue into TASK_283/TASK_284 without a new approved task and plan.
