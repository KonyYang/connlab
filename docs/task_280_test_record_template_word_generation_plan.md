# TASK_280 Test Record Template Word Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task.

## Current Phase And Task Gate

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task before approval: none.
- Proposed task: `TASK_280_TEST_RECORD_TEMPLATE_WORD_GENERATION`.
- Allowed reason: TASK_279 is complete and user requested the next controlled task to make Workbench `Test record` generate a Word document from approved template + active ConfirmedMatrix.

Do not implement until user explicitly approves TASK_280 execution and board status stays consistent.

## Goal

Enable:

```text
Project Workbench -> Test record -> generate/download .docx
```

Source of truth is fixed:

```text
Active ConfirmedMatrix -> ConfirmedMatrixTestRecordPreview -> Word template writer
```

No Excel runtime parsing, no frontend temp-state source, no unconfirmed draft source.

## Inputs / Outputs

Input:
- Active ConfirmedMatrix preview DTO.
- Approved template: `FDQF-E-036 Test Record Template-Even.docx`.

Output:
- `<project_no> Test Record.docx`.
- Preferred path: `<project_folder>/Submitted Material/<project_no> Test Record.docx`.
- Fallback path: `<settings.data_dir>/generated_test_records/...`.

## Fixed Contracts (This Plan Revision)

1. **No fallback-only template testing**
   - Writer tests must include a real-template-structure path as primary coverage.
   - Minimal template tests are supplemental only.
2. **Overwrite behavior is fixed**
   - If target file already exists, overwrite it deterministically.
   - Service/API/unit tests must assert overwrite behavior.

## Observed Template Shape

- table 0: 9-column step table (`Step`, `Test items`, `Test Method`, `Test conditions`, `Start Date/Time`, `Complete Date/Time`, `Equipment ID No.`, `Tested By`, `Remarks`)
- table 1: 7-column equipment table
- historical output pattern: one group paragraph + one step table + one equipment table per selected group

Example paragraph format:

```text
Group Number: 1 ; Sample Quantity & Number: 5 sets (Group1-1#~5#)
```

## File-Level Design

### Backend

- `backend/shared/config.py`
  - add `TestRecordSettings.template_path`
  - load from env/local config

- `backend/application/confirmed_matrix_test_record_document_generation_service.py`
  - extend command with `template_path`
  - resolve output target path (project folder preferred)
  - keep data source as active ConfirmedMatrix preview only

- `backend/infrastructure/office/test_record_document_gateway.py`
  - validate template path + suffix
  - copy template to output
  - clone template group block (paragraph + step table + equipment table) per selected group
  - fill step columns:
    - `Step` <- `step.sequence`
    - `Test items` <- `step.test_item`
    - `Test Method` <- `step.method`
    - `Test conditions` <- `step.condition`
    - `Remarks` <- `step.requirement`
    - execution columns remain blank

- `backend/api/routes_confirmed_matrix_test_record_generation.py`
  - pass configured template path
  - error contracts:
    - no active confirmed matrix: 404
    - missing/invalid template config: 422
    - no preview groups: 422
  - keep download as `FileResponse`

### Frontend

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
  - enable `Test record` when preview ready
  - call `generateConfirmedMatrixTestRecordDraft(projectId)`
  - download blob
  - show compact `Generating...` and error state

- `frontend/src/api/client.ts`
  - keep existing generation API function

## Implementation Tasks

1. Config + command wiring.
2. Writer implementation with template cloning.
3. Service output path resolution (project folder preferred, fallback otherwise).
4. API download route integration and error mapping.
5. Workbench button enablement + download flow.
6. Tests + board sync.

## Test Strategy

### Writer tests (hard requirement)

- Primary: real-template-structure test path (approved template or structurally equivalent checked fixture).
- Supplemental: minimal template builder tests.
- Assertions:
  - repeated group sections count
  - repeated step/equipment tables count
  - filled step cells correct
  - manual execution columns blank

### Service/API tests

- source must be active confirmed preview only
- missing template -> 422
- no active matrix -> 404
- overwrite existing target file -> overwritten content/path behavior asserted

### Frontend tests

- `Test record` enabled/disabled by preview readiness
- click triggers API and download
- generating/error states render as expected

## Validation Commands

```powershell
py -m pytest tests\unit\test_test_record_document_gateway.py -q
py -m pytest tests\unit\test_confirmed_matrix_test_record_document_generation_service.py -q
py -m pytest tests\integration\test_confirmed_matrix_test_record_generation_api.py -q
cd frontend
npm test -- --run ProjectWorkbenchMatrixProjectionPanel --watch=false
npm run build
cd ..
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task280 or task279 or project_workbench"
git diff --check
```

## Risks And Controls

- Risk: OOXML clone fidelity issues.
  - Control: clone template XML blocks, avoid rebuilding layout tables from scratch, assert structure in writer tests.

- Risk: accidental behavior drift for existing files.
  - Control: deterministic overwrite rule fixed in this task and locked by tests.

- Risk: no project folder exists.
  - Control: fallback controlled output directory, still downloadable.

- Risk: expectation of header/footer auto-fill.
  - Control: explicitly out of scope.
