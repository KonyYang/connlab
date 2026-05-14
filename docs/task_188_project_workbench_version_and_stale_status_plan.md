# TASK_188 Plan - Project Workbench Output Version Ledger And Stale Status

## 1. Execution Gate (Anti-Skip Protocol)

- Current phase: `Phase 11 - Project planning data foundation before downstream document automation`.
- Current active task ID at original plan time: `TASK_188_PROJECT_WORKBENCH_VERSION_AND_STALE_STATUS`.
- Current local board state observed on 2026-05-14: `TASK_188` is already marked complete and `TASK_189` is pending approval.
- Why this document is updated now:
  - User confirmed the real lab workflow and Matrix/test-record rules after the first TASK_188 plan.
  - The original frontend-only stale-status plan is not enough for the confirmed traceability goal.
  - This document records the corrected implementation direction for TASK_188-compatible follow-up work and TASK_189+ planning.

This document is still a plan/decision record. Do not implement new code from this document unless the active task board explicitly approves the relevant task.

## 2. Required Read Order Check

Inputs used for this plan:

1. `AGENTS.md` project rules supplied in the conversation.
2. `docs/task_board.md`
3. Prior Workbench task chain:
   - `tasks/TASK_184_PROJECT_WORKBENCH_MATRIX_FIRST_REDESIGN_BASELINE.md`
   - `docs/task_184_project_workbench_matrix_first_redesign_baseline_plan.md`
   - `docs/task_185_project_workbench_state_model_and_layout_refactor_plan.md`
   - `docs/task_186_project_workbench_matrix_review_surface_plan.md`
   - `docs/task_187_project_workbench_document_pipeline_autofill_plan.md`
4. UI and architecture rules:
   - `docs/02_ARCHITECTURE_RULES.md`
   - `docs/frontend_architecture_rules.md`
   - `$impeccable` product context from `PRODUCT.md` and `DESIGN.md`
5. User-confirmed lab workflow details from 2026-05-14:
   - Matrix is the spec/test project table from Word or Excel.
   - Project owner can edit Matrix in the single-machine edition.
   - One project normally has one current Matrix, but it may be revised.
   - Downstream outputs must follow the latest confirmed Matrix.
   - Test records are Word forms, one table per group, generated from Matrix and manually filled before import.
   - Long-term reuse requires structured historical Matrix, result, image, fee, and report data.

## 3. Corrected Task Understanding

### 3.1 Goal

The corrected goal is to establish a minimal persistent output-version ledger, then display `current` / `stale` / `missing` / `manual` / `failed` status in Project Workbench.

The ledger must answer:

- Which Matrix/TestPlan draft version is currently active for the project?
- Which draft version produced Section 2, test record form, fee evaluation, and approval package outputs?
- Did the active Matrix change after an output was generated or manually attached?
- Which downstream files need regeneration, re-preview, or manual review?

### 3.2 Why Frontend-Only Status Is Not Enough

Frontend-only status can warn inside the current browser session, but it cannot solve the real lab problems:

- Reopening ConnLab must still show whether a generated test record is stale.
- Approval package review must know whether included files came from the current Matrix.
- Future report generation must know which Matrix version the report is based on.
- Future similar-project reuse needs historical Matrix/output/result metadata, not only files on disk.

Therefore, the preferred implementation direction is minimal backend persistence, not only frontend-derived hints.

## 4. Business Decisions To Preserve

### 4.1 Authority Model

Use this authority hierarchy:

```text
Original spec / Word Matrix / Excel Matrix = source evidence
ConnLab confirmed ProjectTestPlanDraft = project plan authority
Generated Word / Excel / PDF files = output artifacts
```

Downstream files and reports should be based on the latest confirmed ConnLab Matrix draft, not directly on the original spec file.

### 4.2 Matrix Scope

Matrix is not a giant Excel replacement. It is the project test-plan entry point:

- overview of test groups and steps;
- source traceability;
- group/step status;
- access point to generated record forms, imported results, images, references, and later report evidence.

Complex group/step operations should live in group/step detail panels, not inside every Matrix cell.

### 4.3 Test Record Workflow

ConnLab should adapt to the current lab workflow first:

1. Confirm or edit Matrix.
2. Freeze/confirm a Matrix draft version.
3. Generate Word test record forms from the confirmed Matrix.
4. Project owner or engineer manually fills the Word form.
5. ConnLab imports the filled Word form and stores structured group/step results.

Do not jump directly to a full online test execution system.

## 5. Matrix And Step Rules For Future Tasks

These rules must guide TASK_189 and later Matrix implementation.

### 5.1 Step Token Parsing

Matrix cells may contain tokens such as:

```text
1,8
1,14
3(a)
4(b)
2(c)
```

Parsing rules:

- Comma, whitespace, and newline are separators.
- Each token contributes one step.
- The step sequence is the leading integer in the token.
- Any trailing non-numeric text is a suffix note, not part of the numeric sequence.

Examples:

```text
3(a) -> step_sequence = 3, suffix_note = "(a)"
4(b) -> step_sequence = 4, suffix_note = "(b)"
2(c) -> step_sequence = 2, suffix_note = "(c)"
```

### 5.2 Step Continuity Validation

Within one group, parsed step sequences must be unique and continuous from 1.

Allowed:

```text
1,2,3,4,5
1,2,3,4,5,6,7
```

Blockers:

```text
2,3,4       # missing 1
1,2,3,4,6  # missing 5
1,2,2,3    # duplicate 2
```

Gaps or duplicates must block Matrix freeze/confirmation until corrected.

### 5.3 Repeated Test Items

The same test item can appear multiple times in the same group and must be treated as different steps.

Example:

```text
Step 2  LLCR  Initial LLCR
Step 5  LLCR  After Thermal Shock
Step 11 LLCR  Final LLCR
```

The stable identity is group + step sequence, not only test item name.

### 5.4 Result Comment Vocabulary

Comment/status values must support at least:

```text
Pass
Fail
Ref
NA
Waive
Pending
```

The original human-entered text must also be retained because reports often need the exact wording.

### 5.5 Duration And Fee

- Duration belongs to group/step execution planning.
- Test item may provide a default duration, but final schedule uses step-level duration.
- Fee estimation depends on test item, step count, sample size, and a standard price mapping.
- Fee mapping from the real fee evaluation workbook should be handled in a dedicated fee task, not inside Matrix editing.

## 6. Minimal Persistent Ledger Design

### 6.1 Domain Concept

Add a lightweight Project output record concept:

```text
ProjectOutputRecord
```

Purpose:

- track downstream output artifacts;
- record which Matrix draft/version produced or justified the output;
- allow stale detection after Matrix changes;
- support future historical reuse.

### 6.2 Suggested Fields

```text
output_record_id
project_id
draft_id
draft_version
output_kind
output_path
status
source
created_at
updated_at
note
```

Optional later fields:

```text
operator
checksum
source_template_path
approval_package_item_count
warning_count
```

### 6.3 Output Kinds

Initial `output_kind` values:

```text
section2_write_back
test_record_form
fee_evaluation
approval_package
```

Reserved future values:

```text
record_import
test_image_set
report_draft
final_report
```

### 6.4 Status Values

Initial `status` values:

```text
missing
current
stale
manual
failed
```

Semantics:

- `missing`: no known output exists for the active Matrix.
- `current`: output is associated with the active draft/version.
- `stale`: output is associated with an older draft/version.
- `manual`: operator supplied or corrected a path and ConnLab cannot prove generation lineage.
- `failed`: generation, write-back, preview, import, or placement failed.

### 6.5 Stale Rule

When a new Matrix draft is confirmed as the project authority:

```text
all current output records tied to older draft_id/draft_version -> stale
missing placeholders or Workbench status rows appear for required outputs for the new draft
```

Do not delete old output records. Old outputs are historical evidence.

## 7. Backend Boundary Plan

Implementation should follow ConnLab layering:

```text
api -> application -> domain/ports -> infrastructure
```

Expected backend additions when approved:

- domain dataclass or value object for output records;
- SQLAlchemy model and repository;
- application service for create/list/mark-stale/current/manual/failed operations;
- typed API responses for Workbench read model;
- integration tests using temporary SQLite.

Office gateways are not part of this ledger task except that existing document-generation/write-back services may later call the ledger service after successful output creation.

## 8. Frontend Workbench Plan

Workbench should display a compact downstream output status panel:

```text
Section 2          current/stale/missing/manual/failed
Test record form   current/stale/missing/manual/failed
Fee evaluation     current/stale/missing/manual/failed
Approval package   current/stale/missing/manual/failed
```

UI rules:

- Matrix remains first visible work surface.
- Status colors must be paired with text.
- No decorative UI, no nested cards, no spreadsheet-like button overload.
- Manual paths are never presented as system-verified current outputs.
- Backend blockers remain authoritative for write/copy operations.

## 9. Expected File-Level Implementation Scope

When the persistent ledger implementation is approved, expected files include:

- `backend/domain/models.py` or adjacent domain module
- `backend/domain/enums.py`
- `backend/application/project_output_record_service.py`
- `backend/infrastructure/storage/models.py`
- `backend/infrastructure/storage/repositories/project_output_record.py`
- `backend/api/routes_project_output_records.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/*`
- `tests/unit/test_project_output_record_service.py`
- `tests/integration/test_project_output_record_api.py`
- `tests/unit/test_frontend_shell_files.py`

Keep implementation incremental. Do not combine this with Matrix editing, test record import, image management, or report generation.

## 10. Validation Plan

Backend tests:

```powershell
py -m pytest tests\unit\test_project_output_record_service.py tests\integration\test_project_output_record_api.py -q
```

Frontend build:

```powershell
cd frontend
npm run build
```

Frontend static guard:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix or approval"
```

Task-board guard:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

Manual smoke:

1. Open a project with active Matrix draft and no outputs.
   - Expected: downstream outputs show `missing`.
2. Record a generated or manual output.
   - Expected: Workbench shows `current` or `manual`.
3. Confirm a newer Matrix draft.
   - Expected: older outputs become `stale`.
4. Reopen Workbench.
   - Expected: persisted statuses remain visible.

## 11. Acceptance Criteria

- Output status is persisted, not only derived inside the browser session.
- Workbench can show current/stale/missing/manual/failed after reload.
- Stale detection is based on project active draft identity/version.
- Old output records are preserved for traceability.
- No Matrix editing, record import, image management, fee pricing overhaul, report generation, AI review, or LAN/multi-user scope is implemented in this ledger task.

## 12. Follow-Up Task Direction

Recommended follow-up sequence:

1. `TASK_189_MATRIX_EDIT_AND_FREEZE_FOUNDATION`
   - edit groups/steps/method/condition/requirement/duration;
   - parse step tokens with leading-integer rules;
   - block duplicate or non-continuous step sequences;
   - freeze/confirm the project authority Matrix.

2. `TASK_190_MATRIX_GROUP_STEP_DETAIL_PANEL`
   - Matrix overview remains compact;
   - group/step detail panel owns operations and status.

3. `TASK_191_GROUP_RECORD_FORM_GENERATION`
   - generate one Word test record table per group from confirmed Matrix.

4. `TASK_192_FILLED_RECORD_FORM_IMPORT`
   - import manually filled Word record forms;
   - store structured step results and comments.

5. `TASK_193_STEP_IMAGE_AND_EVIDENCE_MANAGEMENT`
   - attach before/after/equipment/failure images to steps;
   - support rule-based naming preview and correction.

6. `TASK_194_HISTORICAL_MATRIX_AND_PROJECT_REUSE`
   - search prior projects by product, part, test item, standard, requirement, group pattern, and result history;
   - copy prior Matrix as a new draft with traceability.

## 13. Stop Condition

This document records the corrected direction.

Do not implement the persistent ledger or follow-up Matrix work until the task board marks the relevant task active and the user explicitly approves implementation.
