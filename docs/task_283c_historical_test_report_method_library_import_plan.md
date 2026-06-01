# TASK_283C Implementation Plan - Historical Test Report Method Library Import

## 1. Task Identity

- Task: `TASK_283C_HISTORICAL_TEST_REPORT_METHOD_LIBRARY_IMPORT`
- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Plan status: Draft for review (no implementation yet)
- Execution mode: `superpowers:executing-plans` (serial, bounded slices)

## 2. Why This Task Is Allowed Now

`TASK_283A/B` established deterministic spec-based extraction + fallback. `TASK_283C` is the next bounded backend slice to ingest approved historical report rows as traceable candidates (not authority overwrite).

## 3. Objective

Parse historical `.docx` Test Reports and extract `5. TEST METHODS/REQUIREMENTS` table rows into structured Method Library candidates with source traceability.

## 4. Source Dataset (Current User-Provided Seed)

Current available seed folder:

`C:\Users\White\Desktop\AI information\Matrix Fill`

Deterministic seed inventory (8 real `.docx`, excluding `~$*.docx` lock files):

- See: `docs/task_283c_matrix_fill_seed_inventory.md`

## 5. Scope Control

### In Scope

1. Word gateway extraction for report table candidate:
   - heading/title evidence around section 5 (`TEST METHODS/REQUIREMENTS` variants).
2. Row extraction fields:
   - `test_item`, `method`, `condition`, `requirement`.
3. Traceability fields:
   - source file path, source file hash, source table index, extraction timestamp.
4. Deterministic normalization at ingestion boundary:
   - whitespace cleanup only (no semantic rewrite in this task).
5. Lightweight candidate index read path for backend consumers.

### Out Of Scope

1. No automatic update of Matrix Editor values.
2. No UI management page.
3. No AI semantic clustering.
4. No binary file migration into DB.
5. No authority precedence change.

## 6. Proposed Design

### 6.1 Backend modules

1. Office extractor (infrastructure):
   - locate candidate table(s), parse rows.
2. Application service:
   - orchestrate ingestion, apply minimal validation, attach traceability.
3. Candidate repository (fixed for TASK_283C):
   - workspace-local JSON candidate index file.
   - no SQLite schema change in this task.

### 6.2 Extraction contract

1. Keep source row raw text snapshot for audit/debug.
2. Skip empty/structural rows.
3. Preserve original row order.

### 6.3 Safety contract

1. Ingestion output is candidate data only.
2. No write-back to Matrix/session/authority flows.

## 7. File-Level Change Plan

1. Add office extractor in `backend/infrastructure/office/` (small focused module).
2. Add application ingestion service in `backend/application/`.
3. Add repository adapter in `backend/infrastructure/storage/repositories/`.
4. No new API route in TASK_283C.
   - ingestion and readback validation are done via service/repository tests and dry-run output artifact.
5. Add tests:
   - unit extractor tests with compact fixtures.
   - service tests for dedupe/hash/traceability.

## 8. Test Plan (Required)

1. Automated fixture tests cover at least 3 representative report-table layout variants.
2. Hash/traceability fields present and stable.
3. Non-target tables are skipped.
4. Duplicate same-file ingest policy deterministic (no uncontrolled duplication).
5. No Matrix/session behavior change regression.
6. Real-seed dry-run covers all 8 inventory files and produces per-file summary:
   - extracted row count
   - skipped reason when extraction is empty/blocked

## 9. Risks and Mitigation

1. Risk: report table layout variations.
   - Mitigation: heading-evidence + column-intent checks + robust skip.
2. Risk: code growth.
   - Mitigation: split extractor/service/repository; keep each file small.
3. Risk: accidental authority coupling.
   - Mitigation: explicit candidate-only contract + regression tests.

## 10. Validation Commands (Implementation Phase)

1. `py -m pytest tests/unit/test_historical_test_report_method_extractor.py -q`
2. `py -m pytest tests/unit/test_historical_method_library_import_service.py -q`
3. `py -m pytest tests/unit/test_historical_method_library_seed_dry_run.py -q`
4. `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task283 or matrix_editor"`
5. `git diff --check`

## 11. Completion Criteria

1. All 8 files in `docs/task_283c_matrix_fill_seed_inventory.md` are processed by dry-run with per-file outcome summary.
2. No UI or authority flow side effects.
3. Tests pass and task board/index are updated in completion turn.
