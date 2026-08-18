# TASK_283D Implementation Plan - Matrix Editor MCR Review UX

## 1. Task Identity

- Task: `TASK_283D_MATRIX_EDITOR_MCR_REVIEW_UX`
- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Plan status: Draft for review (no implementation yet)
- Execution mode: `superpowers:executing-plans` + `$impeccable` for UI decisions

## 2. Why This Task Is Allowed Now

`TASK_283A/B/C/E` are complete and now provide stable backend signals (detail extraction status, fallback notes, normalization notes). `TASK_283D` is a bounded frontend UX slice to make provenance/review state visible without changing authority flow.

Execution dependency order (fixed):

1. `TASK_283C` first: historical candidate source contract stabilized.
2. `TASK_283E` second: Condition/Requirement normalization notes/status stabilized.
3. `TASK_283D` third: frontend status mapping implemented once upstream signals are stable.

## 3. Objective

Improve Matrix Editor readability for MCR review with low-noise status signals so operators quickly spot:

1. extracted from spec section,
2. template fallback,
3. missing/needs review,
4. manually edited.

## 4. Scope Control

### In Scope

1. Add compact per-cell or per-row provenance hints for MCR columns.
2. Show `Needs review` only from explicit signals (empty value / backend `missing` status / explicit unresolved note).
3. Keep MCR cells directly editable.
4. Preserve existing `Confirm Matrix` flow and guards.

### Out Of Scope

1. No new workflows/pages.
2. No historical library maintenance UI.
3. No backend Office parsing in frontend.
4. No StepInstance/report/fee/evidence/permission expansion.

## 5. Proposed UX Pattern

1. Add micro-status badge/text in M/C/R columns (or row metadata strip):
   - `Spec`
   - `Template`
   - `Needs review`
   - `Edited`
2. Use restrained styling, no large cards/popups.
3. Keep table density and existing keyboard editing behavior.

Status dictionary (fixed labels in UI):

1. `Spec`: value is section-derived and not template-filled.
2. `Template`: value includes `template-fallback-*` notes.
3. `Needs review`: value missing or unresolved.
4. `Edited`: local current value differs from initial imported session value.

## 6. Technical Design

1. Extend frontend row model selectors to map backend `detail_extraction_status` and `detail_extraction_notes`.
2. Add deterministic UI mapping function:
   - priority 1 (highest): local current value differs from imported snapshot -> `Edited`
   - priority 2: current field value empty, or backend row status `missing`, or explicit unresolved note -> `Needs review`
   - priority 3: notes contain `template-fallback-*` -> `Template`
   - priority 4: notes contain normalization notes from TASK_283E and no template note -> keep `Spec`
   - default: `Spec`
3. Keep API calls in `frontend/src/api/client.ts` only.

Needs review signal contract (fixed):

1. Do not infer low-confidence from free text.
2. Only use explicit structured signals already available in backend payload:
   - empty M/C/R value
   - `detail_extraction_status == "missing"`
   - explicit unresolved marker note if present

## 7. File-Level Change Plan

1. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
2. `frontend/src/features/matrix-editor/*selectors*.ts`
3. `frontend/src/workbench.css` (prefer existing global workbench stylesheet; use feature-local styles only if implementation already has a stable local boundary)
4. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

## 8. Test Plan (Required)

1. `Spec` status rendering when extracted values exist without template note.
2. `Template` status rendering when fallback note exists.
3. `Needs review` rendering when field missing.
4. `Edited` rendering after local change.
5. Existing confirm/sample/group validation behavior unchanged.
6. No-section fallback row from TASK_283E appears as `Template` or `Needs review` per note/value state, not misclassified as section-derived `Spec`.
7. Normalized requirement text from TASK_283E (for example `<= 30 ℃`) does not get mislabeled as `Edited` on first render.
8. Edited status priority:
   - editing a template fallback value must show `Edited` (not `Template`)
   - filling an initially missing value must show `Edited` (not `Needs review`)

## 9. Risks and Mitigations

1. Risk: UI noise in dense matrix.
   - Mitigation: micro-copy and subtle styling only.
2. Risk: status confusion.
   - Mitigation: one deterministic mapper function and tests.
3. Risk: coupling with future tasks.
   - Mitigation: no new backend contract unless strictly required.

## 10. Validation Commands (Implementation Phase)

1. `cd frontend; npm test -- --run MatrixEditorWorkspace --watch=false`
2. `cd frontend; npm run build`
3. `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task283 or matrix_editor"`
4. `git diff --check`

## 11. Completion Criteria

1. Operators can identify MCR provenance/review state in-place.
2. Matrix edit/confirm flow remains unchanged.
3. UI is concise and workbench-like.

## 12. Implementation Preflight

Before writing frontend code for TASK_283D, implementation must explicitly read:

1. `docs/02_ARCHITECTURE_RULES.md`
2. `docs/frontend_architecture_rules.md`
3. `$impeccable` guidance documents already referenced by project rules
