# TASK_283C_HISTORICAL_TEST_REPORT_METHOD_LIBRARY_IMPORT

## Status

Planned follow-up. Do not implement until TASK_283A and TASK_283B decisions are accepted and a separate execution plan is approved.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Objective

Extract Method/Condition/Requirement examples from already completed historical Test Reports, especially the `5. TEST METHODS/REQUIREMENTS` table, and store them as traceable Method Library candidates.

The goal is to reuse the laboratory's already approved human wording without treating Word files as the long-term data model.

## Architecture Position

TASK_283C should stay lightweight:

```text
Historical Test Report file path/hash -> extracted table rows -> Method Library candidate index
```

It should not copy every original report into the database. Original reports can remain in project folders or user-selected source locations. ConnLab should store structured extracted rows plus traceability back to the source file path, checksum, document title/project context when available, and extraction timestamp.

## Scope

### In Scope

1. Add a backend Office gateway/parser path for reading the `5. TEST METHODS/REQUIREMENTS` table from `.docx` Test Reports.
2. Extract rows:
   - test item.
   - method.
   - condition.
   - requirement.
   - source report path/hash.
   - source table index or heading evidence.
3. Store or expose a lightweight Method Library candidate index.
4. Add tests using small `.docx` fixtures with the report table shape.
5. Avoid changing Matrix Editor behavior unless a later task explicitly consumes the library.

### Out Of Scope

- No broad document management system.
- No binary file storage migration.
- No full report-generation feature.
- No AI/LLM learning.
- No automatic trust of every historical row as active truth.
- No UI maintenance screen unless a later approved task requests it.

## Code Size Control

This task should not cause code explosion if implemented as small pieces:

1. A focused Word table extractor in `backend/infrastructure/office`.
2. A small application service that normalizes extracted rows.
3. A repository or JSON-backed index only if the approved plan requires persistence.
4. Unit tests with compact fixtures.

Avoid a generic "knowledge ingestion platform". Do not parse every historical project artifact in TASK_283C.

## Acceptance Criteria

1. A historical Test Report `.docx` containing a `5. TEST METHODS/REQUIREMENTS` table can be parsed into structured rows.
2. The result includes traceability to the source report file path/hash.
3. Original report files are not treated as source of truth after extraction; structured rows are.
4. No Matrix values are automatically changed by this task alone.
5. No new future scope is introduced.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for execution if the task remains limited to `.docx` table extraction and candidate-index creation. It is not suitable as a single task for building a broad historical-project knowledge platform.

## Stop Rule

Create a separate implementation plan before coding.

