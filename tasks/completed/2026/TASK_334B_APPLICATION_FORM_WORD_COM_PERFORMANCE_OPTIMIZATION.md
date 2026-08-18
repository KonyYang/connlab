# TASK_334B_APPLICATION_FORM_WORD_COM_PERFORMANCE_OPTIMIZATION

## Status

Complete. Created, approved, implemented, and validated on 2026-06-24.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Allowed

`TASK_334A_FEE_FORM_COM_HOTPATH_OPTIMIZATION` is complete and the task board explicitly stops before Application Form Word COM optimization.

The user explicitly requested a separate `TASK_334B` evaluation and plan for the remaining Application Form Word COM write-back bottleneck.

## Problem

After Fee Form hot-path optimization, the remaining large Project Folder update cost is expected to be Application Form Word COM write-back.

Prior real timing showed Application Form write-back around `14.9s-15.3s`.

Current Application Form behavior is functionally correct and must be preserved:

- write only stable laboratory/header fields
- normalize visible header LTR layout
- use Word COM for real form documents
- verify visible values after writing
- block critical write/read-back failures

The likely performance issue is repeated Word COM scanning and an oversized gateway module, not data assembly.

## Goal

Optimize Application Form Word COM write-back time while preserving visible output correctness, recovery-safe Word documents, and TASK_332C write-back scope.

## In Scope

- Capture a current-version focused Application Form write-back baseline before changing the Word COM implementation.
- Profile Application Form Word COM write-back stages.
- Produce a structured timing snapshot readable by tests or a focused smoke runner, not only loose log text.
- Split oversized Word gateway code into focused modules below the project file-size hard limit.
- Build a one-pass Word COM target index for the six supported critical fields.
- Replace repeated per-field full table scans with cached target lookup.
- Reuse resolved targets for write and visible read-back where safe.
- Keep one Word COM session per document.
- Preserve header LTR normalization and blocker semantics.
- Add fake-COM unit tests for target lookup, critical blockers, field writes, and no repeated full scans.
- Run a real timing smoke and reopen the Word document after write-back.

## Out Of Scope

- No new Application Form fields.
- No writing multi-row source fields such as Description P/N, Product Description, Test Item, or Applicable Specifications.
- No Basic Information schema/API/source-provider changes.
- No Project Folder API or frontend progress changes.
- No Fee Form, Customer Feedback, Test Record, or LTR workbook behavior changes.
- No Word template redesign.
- No replacing Word COM for real form documents.
- No Report generation.
- No StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.

## Acceptance Criteria

- The same six canonical fields remain the only required Application Form write-back fields:
  - `ltr_number`
  - `lab`
  - `project_leader`
  - `received_date`
  - `estimated_completion_date`
  - `sample_condition`
- Header LTR layout remains:
  - `Lab Test Request Number:`
  - blank paragraph
  - current `DL-...` value
  - page paragraph
  - no trailing blank paragraphs after page
- Critical missing/write/read-back failures still block.
- Body field target lookup is built once per document instead of scanning all tables once per field.
- Fake-COM tests prove body table scanning is bounded to one pass per document and not multiplied by field count.
- All touched Python modules are below the project hard file-size limit.
- Unit tests prove bounded target lookup and existing write/read-back safety behavior.
- Real timing smoke documents current-version before/after Application Form write-back time and remaining bottlenecks.
- Reopened output Word document shows no recovery prompt and visible updated values.

## Validation Plan

```powershell
py -m pytest tests/unit/test_application_form_word_gateway.py tests/unit/test_project_application_form_write_back_service.py -q
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
```

If a dedicated target-index test file is added:

```powershell
py -m pytest tests/unit/test_application_form_word_targets.py -q
```

Manual/real smoke:

1. Use project `72fbbfa290294da9a507344b68ff900f`.
2. Run Project Folder update or the Application Form write-back service path.
3. Capture Application Form step timings before/after.
4. Open the generated Application Form `.docx` in Word.
5. Confirm no recovery prompt, normalized header LTR, and visible critical fields.

## Plan

Detailed plan:

`docs/task_334b_application_form_word_com_performance_optimization_plan.md`

## Stop Point

Stop after completing TASK_334B. Do not start Report generation, broader Project Folder orchestration, additional Word template changes, or any next task without separate explicit approval.

## Completion Notes

- Captured a current-version baseline on a copied real Application Form from project `72fbbfa290294da9a507344b68ff900f`: total gateway call about `10.70s`, with `1` changed field and `5` unchanged fields.
- Added structured Office timing snapshots through `OfficeTimingSnapshot` / `OfficeTimingStage` and attached them to `WordSection2WriteResult`.
- Split Application Form Word COM header LTR helpers into `application_form_word_header.py`.
- Added `application_form_word_targets.py` with a one-pass body target index and early-stop behavior once all requested fields are resolved.
- Replaced repeated body-table lookup in `application_form_word_gateway.py` with cached target lookup while preserving visible read-back and critical blocker behavior.
- Kept the supported write-back field scope unchanged: `ltr_number`, `lab`, `project_leader`, `received_date`, `estimated_completion_date`, and `sample_condition`.
- Kept header LTR safety behavior unchanged and preserved existing header layout tests.
- Gateway/module sizes are below the hard file-size limit after the split.

## Timing Summary

Current-version baseline:

- total: about `10.70s`

Optimized smoke runs on copied real Word forms:

- best observed total: about `9.15s`
- final observed total: about `11.68s`
- final structured timing:
  - `word_dispatch`: about `2.48s`
  - `document_open`: about `1.05s`
  - `header_ltr_com_write`: about `0.80s`
  - `target_index_build`: about `3.51s`
  - `field_write_and_readback`: about `0.32s`
  - `document_save`: about `0.10s`
  - `document_close_quit`: about `3.33s`
  - `header_xml_pre_normalize` + `header_xml_post_normalize`: about `0.05s`

Conclusion: TASK_334B completed the observability and structure optimization, and removed repeated body lookup semantics. It did not produce a stable end-to-end runtime reduction: the best observed run improved to about `9.15s`, but the final observed run was about `11.68s`. The remaining large costs are Word process lifecycle and target-index table scanning, not field writing itself. Further performance work should be a separate task focused on Word COM session lifecycle and reducing/reusing open-close cost.

## Recovery/Open Smoke

The final generated smoke copy was independently reopened through Microsoft Word COM with `OpenAndRepair=False`:

```text
path: D:\PythonProject\connlab\tmp\task_334b_after\after_request_final.docx
opened: true
paragraph_count: 256
table_count: 18
```

No repair exception was raised during this independent open check.

## Validation Summary

```powershell
py -m pytest tests/unit/test_application_form_word_targets.py tests/unit/test_application_form_word_gateway.py -q
```

Result: `20 passed`.

```powershell
py -m pytest tests/unit/test_project_application_form_write_back_service.py -q
```

Result: `9 passed`.

```powershell
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
```

Result: `37 passed`.

```powershell
py -m pytest tests/unit/test_application_form_word_gateway.py tests/unit/test_application_form_word_targets.py tests/unit/test_project_application_form_write_back_service.py -q
```

Result: `29 passed`.
