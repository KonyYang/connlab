# TASK_252CL Plan - Step Notes Prefix Coverage And Card Visual Restore

## 0. Protocol Snapshot

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `TASK_252CL_MATRIX_EDITOR_STEP_NOTES_PREFIX_COVERAGE_AND_CARD_VISUAL_RESTORE` (planned, awaiting approval)
- Why allowed now: user requested concrete Step preview note rendering and mapping corrections after TASK_252CK.

## 1. Task Understanding

1. Goal:
   - Show step-token prefixes in Step Notes (`3(a)` style).
   - Verify/patch remark extraction coverage for A2 marker list `(a)..(e)`.
   - Restore clear independent note-card backgrounds.
2. Input:
   - Imported matrix preview payload (`source_note`, `source_item_section_note`, `sample_note`).
   - Selected group step tokens and sample expression.
3. Output:
   - Prefixed Step Notes lines.
   - Complete marker-note mapping for referenced tokens.
   - Distinct note-card visual sections.
4. Modules:
   - parser/tests (if needed),
   - MatrixEditorWorkspace + workbench.css + frontend shell tests.
5. Forbidden:
   - no scope expansion beyond parser+display+style.

## 2. Root-Cause and Gap Hypotheses

- Prefix gap:
  - current Step Notes list uses payload note text directly, but does not prefix with the step token.
- “Incomplete” note perception:
  - selected group shows only notes whose markers are referenced in that group’s steps/samples;
  - possible parser gap if marker-line punctuation variants in A2 are not fully recognized.
- Card-style gap:
  - CSS currently lacks `.matrix-editor-notes-card*` style blocks, causing weak visual separation.

## 3. Design

### 3.1 Step Notes Prefix Rendering

- Build Step Notes entries as `"{rawToken} {noteTextWithoutLeadingMarker}"`.
- Keep dedupe by rendered string to avoid duplicates from repeated rows.

### 3.2 Marker Coverage Hardening (Conditional)

- Add/update parser tests to model A2-style notes `(a)..(e)` with trailing semicolons and mixed text.
- If tests reveal parser miss, minimally extend marker-note regex handling while keeping deterministic matching.

### 3.3 Card Visual Restore

- Add explicit card style blocks:
  - `.matrix-editor-notes-card` base box,
  - `.matrix-editor-notes-card-step` warm background,
  - `.matrix-editor-notes-card-item-section` cool background,
  - `.matrix-editor-notes-card-samples` neutral background.

### 3.4 Files

1. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
   - Step Notes prefix formatter
   - optional dedupe cleanup
2. `frontend/src/workbench.css`
   - note-card background/spacing styles
3. `tests/unit/test_frontend_shell_files.py`
   - assertions for prefix rendering and note-card class/style hooks
4. `tests/unit/test_product_spec_matrix_parser.py`
   - A2 marker list extraction/mapping tests
5. `tests/integration/test_project_test_plan_preview_api.py`
   - payload mapping assertion for `(c)/(d)/(e)` references when present
6. `backend/modules/test_plan/product_spec_matrix_parser.py`
   - only if parser test demonstrates real miss

## 4. Risks and Mitigations

1. Risk: aggressive prefix cleaning removes important marker text.
   - Mitigation: only trim duplicate leading marker from note body, keep full content otherwise.
2. Risk: parser tweak introduces false positives.
   - Mitigation: add negative tests and anchor-based regex.
3. Risk: CSS conflicts with existing panel styles.
   - Mitigation: scoped selectors under `.matrix-editor-step-workspace`.

## 5. Validation Plan

```powershell
py -m pytest tests\unit\test_product_spec_matrix_parser.py tests\integration\test_project_test_plan_preview_api.py -q
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task252cl or matrix_editor"
```

```powershell
cd frontend
npm run build
```

Manual smoke (A2):

1. Import `GS-12-1880_PwrBlade Pro BTB Product Specification_A2.docx`.
2. Select groups containing `3(a)`, `10(c)`, `5+5(d)`, `5+(5e)` references.
3. Confirm:
   - Step Notes shows `3(a) ...`, `10(c) ...` etc.
   - Samples Notes shows `(d)/(e)` note bodies when sample expressions reference them.
   - Card backgrounds match separated visual structure.

## 6. Acceptance Gate

Do not implement until user explicitly approves this plan.
