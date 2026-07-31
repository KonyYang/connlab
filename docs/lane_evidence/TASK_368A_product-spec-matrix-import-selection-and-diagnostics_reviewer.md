# TASK_368A Reviewer Evidence

Date: 2026-07-31
Task: `TASK_368A_PRODUCT_SPEC_MATRIX_IMPORT_SELECTION_AND_DIAGNOSTICS_QUICK_FIX`
Lane: `task-368a-product-spec-matrix-import-quick-fix`
Role: permanent Reviewer
Status: `reviewer_blocked`

## Authorization And Governance

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- The permanent Orchestrator dispatched this implementation review gate with the exact worktree,
  branch, base, implementation checkpoint, and evidence-only HEAD.
- The primary-worktree `docs/task_board.md` confirms TASK_368A is the sole active task and the
  browser-release task is `cancelled_by_user` / `closed_without_integration`.
- The lane copy of `docs/task_board.md` is an older fork snapshot. It was not modified because
  global board governance belongs to Orchestrator/Integrator.

## Inspected Commits

- Review base: `6c16cbcb7d10e6f88829ff823c05dd4ee36f92a7`
- Product implementation checkpoint:
  `a3d77c789bfe21c1b90e9e36f7f78913dfea8223`
- Quick Fixer evidence-only lane HEAD:
  `144aeb8395ef8f873c59300636d673f877fc8ebe`

The base is an ancestor of the implementation checkpoint, and the implementation checkpoint is
an ancestor of the evidence-only HEAD. Pre-review status showed the expected branch and a clean
worktree/index.

## Scope Inspection

Product implementation review was limited to
`6c16cbcb7d10e6f88829ff823c05dd4ee36f92a7..a3d77c789bfe21c1b90e9e36f7f78913dfea8223`.
It contains exactly:

- `backend/modules/test_plan/product_spec_matrix_parser.py`
- `backend/modules/test_plan/product_spec_matrix_parser_support.py`
- `backend/application/project_test_plan_matrix_preview_service.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `tests/unit/test_task_368a_product_spec_matrix_import_selection.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

The evidence-only range
`a3d77c789bfe21c1b90e9e36f7f78913dfea8223..144aeb8395ef8f873c59300636d673f877fc8ebe`
changes only the Quick Fixer evidence file.

No API/DTO/client, Office, persistence/schema/data, release, task-board, layout/style/label, or
other locked path appears in the implementation diff. The oversized Matrix Editor test contains
one bounded 30-line regression hunk; no opportunistic refactor is present.

## Findings

### Blocking

1. `backend/modules/test_plan/product_spec_matrix_parser_support.py:320-328` retains legacy broad
   Revision Record detection after adding the new strict three-marker check.

   The task requires one header row to establish all three marker groups before fail-closed
   rejection: `Rev`/`Revision`, `Page`/`Pages`, and `Description`/`Date`. It also explicitly
   forbids rejecting a real Matrix because matching words occur in body text.

   Two remaining branches violate that contract:

   - line 320 rejects a row containing `Revision` plus `Description` or `Date` even when
     `Page`/`Pages` is absent;
   - lines 322-328 aggregate marker words across the first three rows, so body-row words can
     combine into a false Revision Record classification.

   Read-only in-memory reproductions:

   ```powershell
   py -c "from backend.modules.test_plan.product_spec_matrix_parser_support import looks_like_revision_record_table; a=[['Test Description','Section','Group 1','Revision','Date'],['Visual Examination','1.1','1','A','2026']]; b=[['Test Description','Section','Group 1','Version','Effective Date'],['Visual Examination','1.1','1','A','2026']]; print({'revision_date_no_page': looks_like_revision_record_table(a), 'control': looks_like_revision_record_table(b)})"
   ```

   Observed:

   ```text
   {'revision_date_no_page': True, 'control': False}
   ```

   ```powershell
   py -c "from backend.modules.test_plan.product_spec_matrix_parser_support import looks_like_revision_record_table; t=[['Test Item','Section','Group 1'],['Revision durability','1.1','1'],['Pages description date check','1.2','2']]; print(looks_like_revision_record_table(t))"
   ```

   Observed: `True`.

   Required repair: make Revision Record rejection depend on the strict same-header-row
   three-marker predicate, remove or narrow the legacy broader paths, and add bounded negative
   regressions for no-Page and body-word cases while retaining the required positive
   `Rev`/`Revision`, `Page`/`Pages`, `Description`/`Date` coverage.

### Non-Blocking

- None.

## Acceptance Review

- Comparison-only `SECTIO N` canonicalization is confined to header matching; body/test item,
  section, notes, and step-token storage are not normalized by the new helper.
- Explicit locator misses fail closed; Page + Keyword filters candidates by page first; no-locator
  flow retains automatic parser scoring.
- A located table that the parser blocks retains selected page and table-on-page diagnostics.
- Frontend stale Replace presents the backend blocker before the synthetic locator-mismatch
  fallback and does not change layout, styling, labels, or modal structure.
- Synthetic coverage includes eleven Groups, singular `Page`, `CHANGE GROUP P TEST ITEM`,
  page-scoped keyword lookup, explicit no-fallback, selected-location diagnostics, and frontend
  blocker priority.
- The Revision Record negative-boundary requirement is not satisfied because of the blocking
  finding above.

## Validation

Reviewer reran:

```powershell
py -m pytest tests\unit\test_task_368a_product_spec_matrix_import_selection.py tests\unit\test_product_spec_matrix_parser.py -q
```

Result: `28 passed`.

```powershell
py -m py_compile backend\modules\test_plan\product_spec_matrix_parser.py backend\modules\test_plan\product_spec_matrix_parser_support.py backend\application\project_test_plan_matrix_preview_service.py
```

Result: exit code `0`.

From `frontend/`:

```powershell
npm test -- MatrixEditorWorkspace.test.tsx
```

Result: `45 passed`.

```powershell
npm run build
```

Result: passed; Vite emitted the existing non-blocking chunk-size warning.

`git diff --check`, `git diff --cached --check`, and post-validation `git status --short` were
clean before this Reviewer evidence was authored.

## Conclusion And Handoff

- Conclusion: `reviewer_blocked`
- Blocking findings: `1`
- Next role: permanent Quick Fixer
- Required next action: correct the bounded Revision Record guard and add the missing negative
  regressions, then return a new clean implementation checkpoint for Reviewer re-gate.
- Reviewer did not modify product code, merge, push, run real attachments, or perform release
  validation.
