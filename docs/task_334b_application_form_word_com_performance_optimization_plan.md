# TASK_334B Application Form Word COM Performance Optimization Plan

## Summary

Application Form write-back is now the remaining large Project Folder update cost after TASK_334A reduced Fee Form generation to about `6.5s`.

The current Application Form write-back is functionally safer than the old implementation: it writes only the stable laboratory/header fields, uses Word COM for real form documents, normalizes the header LTR layout, and verifies visible values. The performance risk is that the gateway still performs repeated Word COM document/table scans for a small fixed field set.

TASK_334B optimizes only this Word COM hot path. It does not change which Application Form fields are written, the visible header layout rule, Basic Information semantics, Project Folder orchestration, frontend progress UI, or any Report/LTR/Fee behavior.

## Current Evidence

Measured before TASK_334A, the full Project Folder update flow was about `40s-44s`, with Application Form Word COM write-back around `14.9s-15.3s`.

After TASK_334A, Fee Form generation is no longer the primary bottleneck. The expected remaining large cost is Application Form Word COM write-back.

Current code path:

1. `ProjectApplicationFormWriteBackService.write_back()`
2. Resolve the selected copied Application Form in `Submitted Material`
3. Read confirmed Basic Information
4. Build six required write-back fields
5. `OfficeFacade.write_word_application_form_fields(...)`
6. `application_form_word_gateway.write_application_form_fields_with_com(...)`
7. Pre-normalize header LTR with DOCX XML helper
8. Open Word through `DispatchEx`
9. Write header LTR through COM
10. For each field, scan document tables to locate the target cell
11. Write content control / form field / plain cell value
12. Read visible value back
13. Save, close, quit Word
14. Post-normalize header LTR with DOCX XML helper

Current static observations:

- `application_form_word_gateway.py` is `582` lines, above the project hard limit of `500`.
- `_find_application_form_cell_with_com()` scans `document.Tables` for each field.
- Location fallback scans tables again when direct label lookup fails.
- Header LTR scanning is separate from body field scanning.
- The task writes only six canonical fields, so a one-pass target index is a better fit than repeated COM lookup.

## Goal

Reduce Application Form Word COM write-back time while preserving visible correctness and recovery-safe document output.

Target outcome:

- Real write-back should be materially faster than the current `~15s` observed baseline.
- The implementation must first capture a current-version focused baseline after TASK_334A, then compare the optimized result against that same code branch and project context.
- If profiling proves Word startup/open/save dominates and code-level gains are bounded, the task must document the measured floor and avoid unsafe shortcuts.

## In Scope

- Add focused timing instrumentation around Application Form Word write-back stages.
- Split the oversized `application_form_word_gateway.py` into smaller focused modules under the file-size hard limit.
- Add a one-pass Word COM target/index helper for Application Form fields.
- Avoid repeated full-document table scans for the fixed critical write-back fields.
- Reuse found target references for write and visible read-back where safe.
- Keep one Word COM document session per write-back operation.
- Preserve existing pre/post DOCX header LTR normalization unless profiling proves it is a material cost and a safe narrowing is obvious.
- Add fake-COM tests proving bounded scans and existing correctness behavior.
- Run a real timing smoke on the same project path to compare before/after Application Form write-back time.

## Out Of Scope

- No new Application Form fields.
- No re-enabling multi-row fields such as Description P/N, Product Description, Test Item, or Applicable Specifications.
- No change to the critical required field list.
- No change to Basic Information schema, source providers, confirmation logic, or API.
- No Project Folder API contract change.
- No Workbench/progress UI change.
- No Word template redesign.
- No replacing Word COM with python-docx for real form documents.
- No Report generation.
- No LTR workbook sync behavior.
- No StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.

## Design

### 1. Capture The Current-Version Baseline First

Before changing the Word COM implementation, run a focused Application Form write-back baseline on the current code after TASK_334A.

The baseline must use project `72fbbfa290294da9a507344b68ff900f` or an equivalent copied smoke fixture with the same selected Application Form shape.

Record:

- total Application Form write-back service time
- gateway total time
- pre/post header XML normalization time
- Word dispatch/open time
- header LTR COM write time
- body field target lookup time
- body field write/read-back time
- save/close/quit time

The after-optimization smoke must use the same measurement shape so the comparison is meaningful.

### 2. Add Structured Stage Timing For The Word Path

Add an internal timing collector for the COM write-back path. It must produce a structured timing snapshot that can be read by unit tests or a focused smoke runner without depending on loose log text.

The snapshot should record at least:

- `header_xml_pre_normalize`
- `word_dispatch`
- `document_open`
- `header_ltr_com_write`
- `target_index_build`
- `field_write_and_readback`
- `document_save`
- `document_close_quit`
- `header_xml_post_normalize`
- total gateway time

Timing may also be logged for operator diagnostics, but logs alone are not sufficient for TASK_334B completion.

The timing snapshot must not require frontend changes or a Project Folder public API contract change.

### 3. Split Gateway Responsibilities

Keep `backend/infrastructure/office/application_form_word_gateway.py` as the public gateway entry module, but move focused implementation into smaller modules such as:

- `application_form_word_targets.py`
  - target/index dataclasses
  - one-pass table scan
  - same-row / next-row target resolution
  - constrained location fallback
- `application_form_word_header.py`
  - COM header LTR write/read-back helpers if this keeps modules clearer

Exact filenames may change during implementation, but every Python file must stay under the project hard limit.

### 4. Build A One-Pass Target Index

Build an `ApplicationFormWordTargetIndex` once after the document opens.

Responsibilities:

- Iterate Word document tables once.
- Collect label cells matching the aliases in `application_form_word_mapping.py`.
- Resolve target cells for same-row and next-row fields.
- Resolve the constrained Business Unit row site fallback only once.
- Return targets by canonical field key.
- Preserve target label and location metadata used in `WordSection2FieldChange`.

The index should only collect targets needed by the provided fields, not every possible legacy field.

Fake-COM tests must assert that body table scanning is bounded to one pass per document. `table.Cell(row, column)` calls should be close to `sum(rows * columns)` for the scanned tables, not multiplied by the number of fields.

### 5. Write And Verify From Cached Targets

For each provided field:

- Resolve target from the index.
- Read old visible value once.
- Skip write if already equivalent.
- Write through content control, form field, or cell text.
- Read back from the same target.
- Treat critical failures exactly as today.

Do not weaken visible read-back semantics.

### 6. Keep Header LTR Safety Intact

The header LTR path must continue to enforce:

- Label: `Lab Test Request Number:`
- one blank paragraph after the label
- one `DL-...` value paragraph
- one page paragraph
- no extra blank paragraphs after page
- safe blocker behavior when the layout is ambiguous

TASK_334B may cache or narrow header scans only if tests prove the same safety behavior.

Any header XML normalization adjustment must continue to pass no-recovery-prompt smoke, normalized LTR layout checks, and ambiguous-layout blocker tests. If safety cannot be proven, TASK_334B should only record header normalization timing and leave header behavior unchanged.

## Files

Likely create:

- `backend/infrastructure/office/application_form_word_targets.py`
- optional `backend/infrastructure/office/application_form_word_timing.py`

Likely modify:

- `backend/infrastructure/office/application_form_word_gateway.py`
- `backend/infrastructure/office/application_form_word_mapping.py` only if helper exports are needed
- `backend/infrastructure/office/office_facade.py` only if result plumbing requires it
- `tests/unit/test_application_form_word_gateway.py`
- possible new `tests/unit/test_application_form_word_targets.py`

Do not modify:

- frontend files
- Basic Information service/API/schema
- Project Folder orchestration APIs
- Fee Form or Customer Feedback generators
- LTR workbook sync services

## Test Plan

Add or update fake-COM tests:

- one-pass target index finds all six critical body fields without repeated full-table scans
- fake COM counters prove body table scanning is one pass per document and does not multiply by field count
- missing critical field still raises the same blocker
- location fallback still only applies to the known six-column Business Unit row shape
- locked content control already holding the requested value still counts as unchanged
- content control, form field, and plain cell write/read-back behavior still works
- header LTR ambiguous layout still blocks
- header LTR normalized layout still remains unchanged
- gateway files stay under the hard file-size limit

Run:

```powershell
py -m pytest tests/unit/test_application_form_word_gateway.py tests/unit/test_project_application_form_write_back_service.py -q
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
```

If a separate target-index test file is added:

```powershell
py -m pytest tests/unit/test_application_form_word_targets.py -q
```

## Real Timing Smoke

Use project `72fbbfa290294da9a507344b68ff900f` and its copied Application Form in `Submitted Material`.

Record current-version baseline and after-optimization timings for:

- full Project Folder update Application Form step
- gateway total
- Word dispatch/open
- target lookup/index build
- field write/read-back
- save/close/quit
- pre/post header XML normalization

The smoke must reopen the output Word document normally after write-back and confirm:

- no Word recovery prompt
- visible header LTR remains normalized
- visible critical fields are still present

## Risks

- Word COM startup/open/save may be the true floor. If so, optimization must not fake success by skipping validation or save.
- COM object references can become stale after structural edits. Build the target index after opening the document and avoid structural edits to body tables after indexing.
- Header LTR normalization is delicate. Do not rewrite the whole header cell or relax blocker behavior for ambiguous layouts.
- Fake COM tests can prove call bounds and branches, but real Word smoke is still required before completion because Word COM behavior differs from Python fakes.

## Acceptance Criteria

- Application Form write-back still updates exactly the same supported fields as TASK_332C.
- Critical missing/write/read-back failures still block.
- Header LTR layout remains normalized and recovery-safe.
- Word document can be reopened without recovery prompt after smoke.
- Repeated per-field full table scanning is removed from the body field hot path.
- `application_form_word_gateway.py` and any new Python modules are below the project hard file-size limit.
- Unit tests cover the target-index behavior and existing gateway safety behavior.
- Real timing smoke documents before/after timing and the remaining bottleneck.
- The before timing is captured from the current code immediately before optimization, not only from historical TASK_334 evidence.

## Stop Point

Stop after TASK_334B planning is reviewed and approved. Implementation must not begin until the user explicitly approves this task.

## Completion

Implemented and validated on 2026-06-24.

The implementation keeps the Application Form write-back scope unchanged and optimizes the Word COM body-field lookup path:

- added structured `OfficeTimingSnapshot` / `OfficeTimingStage` data;
- attached timing snapshots to `WordSection2WriteResult`;
- split header LTR COM helpers into `application_form_word_header.py`;
- added `application_form_word_targets.py` for one-pass body target indexing;
- replaced repeated per-field body table lookup in the gateway with cached target lookup;
- added early-stop behavior when all requested body targets have been found;
- kept header LTR normalization, visible read-back, critical blockers, and supported field list unchanged.

Current-version baseline on a copied real Application Form from project `72fbbfa290294da9a507344b68ff900f`:

| Run | Total |
| --- | ---: |
| baseline before implementation | `~10.70s` |

Optimized real smoke:

| Run | Total | Notes |
| --- | ---: | --- |
| after target index before early stop | `~11.87s` | showed `target_index_build ~4.42s` |
| after early stop | `~9.15s` | best observed optimized run |
| final smoke | `~11.68s` | Word COM cold/proxy variance remained high |

Final structured timing snapshot:

| Stage | Time |
| --- | ---: |
| `header_xml_pre_normalize` | `~0.01s` |
| `word_dispatch` | `~2.48s` |
| `document_open` | `~1.05s` |
| `header_ltr_com_write` | `~0.80s` |
| `target_index_build` | `~3.51s` |
| `field_write_and_readback` | `~0.32s` |
| `document_save` | `~0.10s` |
| `document_close_quit` | `~3.33s` |
| `header_xml_post_normalize` | `~0.04s` |
| `gateway_total` | `~11.65s` |

The field write/read-back work is now small. TASK_334B completed the observability and structure optimization, but it did not produce a stable end-to-end runtime reduction because Word COM process lifecycle variance remains high. Remaining large costs are Word process lifecycle and Word table target indexing.

Independent open smoke:

```text
path: D:\PythonProject\connlab\tmp\task_334b_after\after_request_final.docx
opened: true
paragraph_count: 256
table_count: 18
```

The generated document opened through Microsoft Word COM with `OpenAndRepair=False`; no repair exception was raised. Further optimization should be split into a later task focused on Word COM session lifecycle and reducing/reusing open-close cost.
