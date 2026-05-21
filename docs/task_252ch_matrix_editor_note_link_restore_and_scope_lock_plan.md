# TASK_252CH Plan - Matrix Note Link Restore And Scope Lock

## 1. Context

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `TASK_252CH_MATRIX_EDITOR_NOTE_LINK_RESTORE_AND_SCOPE_LOCK` (proposed)
- Why allowed now: task board currently has no active task and user explicitly requested full recovery of the previously accepted behavior after an over-broad rollback.

## 2. Problem Statement

After recent rollback/rebuild churn, note parsing and presentation behavior regressed:

- note cards are mixed by origin (`Step Notes` vs `Item/Section Notes`)
- row-level note leakage (one noted token contaminates all steps in row)
- sample note/data display inconsistencies
- risk of losing marker linkage when step number changes but suffix marker remains
- potential over-revert side effects in unrelated files

## 3. Goal (Execution-Focused)

Restore exactly the accepted behavior set validated with user screenshots and sample docs, with minimal bounded changes and explicit regression guards.

## 4. Inputs / Outputs

### Inputs

- Existing Matrix import preview payload
- Parsed docx table content and post-table note paragraphs/list items
- Current group-selected Step preview model

### Outputs

- Stable note-aware preview mapping:
  - step-token marker notes
  - item/section marker notes
  - sample marker notes
- UI cards with strict source separation
- marker-preserving matrix cell display and sample expression display

## 5. File-Level Change Plan

1. Backend parser and mapping restoration
- `backend/modules/test_plan/product_spec_matrix_parser.py`
  - restore/verify extraction of:
    - step token raw text + numeric index + suffix marker
    - item/section cell marker symbols (`*`, `#`, etc.)
    - sample expression markers (e.g., `(5e)` => `e`)
  - keep origin metadata for each marker reference
  - ensure no row-wide promotion behavior

2. API/DTO wiring (if missing)
- `frontend/src/api/client.ts` and related backend DTO mapping
  - restore typed fields used by UI:
    - raw token / marker / source note text / note origin

3. Frontend Step preview restoration
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
  - rebuild derived models:
    - `stepNotes[]` from visible step markers only
    - `itemSectionNotes[]` from referenced item/section markers only
    - `samplesNotes[]` from sample markers only
  - preserve matrix cell token display with markers
  - keep `Samples` label + editable input same row
  - preserve full sample expression literal text

4. Styling adjustment
- `frontend/src/workbench.css`
  - only layout/typography refinements for:
    - samples row inline alignment
    - note card visual separation

5. Tests
- backend parser/API targeted tests (extend existing)
- frontend shell/static assertions for key strings/structures

## 6. Dependency / Boundary Check

- No new dependency introduction.
- No persistence schema change.
- No cross-task feature expansion.
- UI consumes existing preview contracts only.

## 7. Risks And Mitigations

Risk 1: Overwriting unrelated user-edited files in dirty worktree.
- Mitigation: edit only scoped files; inspect `git diff` after each change.

Risk 2: Marker parsing ambiguity across docs.
- Mitigation: keep deterministic regex + explicit precedence by origin.

Risk 3: UI card duplication/cross-contamination.
- Mitigation: derive cards from separate filtered note maps keyed by origin and visible-step references.

## 8. Validation Plan

1. Automated
- `py -m pytest tests\unit\test_product_spec_matrix_parser.py tests\integration\test_project_test_plan_preview_api.py -q`
- `cd frontend; npm run build`
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task252 or matrix_editor or samples or notes"`

2. Manual smoke
- import `GS-12-1880...A2.docx`
- import `GS-12-1507...Rev7 (3).docx`
- verify strict origin-separated notes + marker-preserving displays + step-marker renumber resilience

## 9. Out Of Scope

- New formats (`.doc`, PDF, Excel)
- Workflow redesign
- board-wide cleanup unrelated to this hotfix

## 10. Approval Gate

Await explicit user approval before implementation (per AGENTS and task execution protocol).
