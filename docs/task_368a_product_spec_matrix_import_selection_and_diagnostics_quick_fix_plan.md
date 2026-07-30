# TASK_368A Product Spec Matrix Import Selection And Diagnostics Quick Fix Plan

Date: 2026-07-31
Status: approved bounded plan
Register: product
Lane: `task-368a-product-spec-matrix-import-quick-fix`

## 1. Discovery Gate

Current phase: Phase 11.

Current active work: the browser-release instance-guard Developer lane remains active in its
retained worktree. TASK_368A is an independent Matrix parser/import quick-fix lane.

Why planning is allowed: the user supplied a real failing document, reviewed the diagnosis, asked
the permanent Quick Fixer to start resolving it, and requested formal Orchestrator dispatch.

Confirmed by user:

- Automatic Import Matrix selects the page 11 Revision Record.
- Manual Page/Keyword reparse fails despite the correct Matrix being on page 10.
- The user authorized implementation after the root-cause discussion.

Confirmed by repository evidence and read-only reproduction:

- The correct Matrix is document table 6, page 10, table 1.
- Its `SECTION` header reaches the parser as `SECTIO N`; current `_find_header()` rejects it.
- The following Revision Record uses singular `Page`; current revision guard covers plural
  `Pages`.
- Revision text containing `CHANGE GROUP P TEST ITEM` can pass loose Matrix scoring.
- Page + Keyword currently searches all tables because page scoping is applied only when both Page
  and Table on page are supplied.
- Reparse currently evaluates page/table mismatch before applying the response blocker.
- Existing parser unit tests pass but cover only the plural `PAGES` rejection.

Inferred and frozen as task scope:

- This is one defect chain: table classification, explicit locator selection, then precise
  diagnostic presentation.
- Four product files are justified despite the Quick Fixer guideline's usual 1-3 range because
  each file owns one already-existing layer of that chain and no API/data contract changes.

Not yet confirmed:

- None that changes scope, behavior, ownership, or validation. Real-file production smoke is
  deliberately outside implementation and may be performed later as read-only QA.

Decision: Definition of Ready is satisfied. The lane is approved under the user's explicit start
instruction and Quick Fixer fast path.

## 2. Design

### 2.1 Header-only canonical matching

Keep stored/extracted cell text unchanged. Add a narrow canonical comparison form used only for
known header labels so whitespace created inside alphabetic header tokens does not prevent
`SECTION` recognition. Do not remove whitespace globally from body rows, test names, section
values, notes, or step tokens.

Expected internal shape:

```python
def _canonical_header_label(value: str) -> str:
    """Return a comparison-only canonical header label."""
```

The implementation may keep this helper private in the parser module. It must be applied only
where `_find_header()` classifies item/section/group header cells.

### 2.2 Revision Record fail-closed guard

Harden `looks_like_revision_record_table()` before loose header inference. Normalize header cells
with existing conservative normalization and reject when the header row establishes:

- `rev` or `revision`;
- `page` or `pages`;
- at least one revision-description marker: `description` or `date`.

The rule must not reject a valid Matrix merely because unrelated body text contains one marker.

### 2.3 Explicit locator semantics

Refine `_select_table_index()` and the neutral preview assembly so:

- Page + Table on page resolves that exact pair;
- Page + Keyword filters candidates to the requested page before keyword matching;
- Keyword without Page may search the document as today;
- any supplied explicit locator that resolves no candidate produces a deterministic no-match
  blocker and never gives the parser `None` as permission to auto-score another table;
- selected location metadata remains present when a table was found but its parser result is
  blocked, allowing diagnostics without inventing a successful Matrix.

No route, request DTO, response DTO, persistence, or Office behavior changes are needed.

### 2.4 Frontend blocker priority

In the stale Replace/reparse path, apply the preview's authoritative blocker/group status before
synthetic locator mismatch checks. Locator mismatch remains a fallback only when no blocker
exists. Preserve existing layout, labels, actions, aria behavior, and copy.

This follows ConnLab's product rule: show current blocker and next action in business-readable
language, without exposing stack traces or backend implementation names.

## 3. File-Level Changes

| Path | Planned change |
|---|---|
| `backend/modules/test_plan/product_spec_matrix_parser.py` | Comparison-only split-header canonicalization in `_find_header()` |
| `backend/modules/test_plan/product_spec_matrix_parser_support.py` | Singular/plural Revision Record fail-closed guard |
| `backend/application/project_test_plan_matrix_preview_service.py` | Explicit locator no-fallback and page-scoped keyword selection |
| `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` | Blocker-first reparse decision |
| `tests/unit/test_task_368a_product_spec_matrix_import_selection.py` | Synthetic eleven-Group, Revision Record, locator, and fail-closed regression |
| `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx` | One focused blocker-priority regression in the existing import section |

No new dependency, API, schema, config, styling, or fixture file is planned.

## 4. Risks And Controls

| Risk | Control |
|---|---|
| Over-normalization changes business text | Canonicalize only known header comparisons |
| Revision guard rejects a real Matrix | Require the combined revision marker set in a header row |
| Explicit locator changes auto-import | Preserve auto-scoring only when no locator is supplied |
| Page + Keyword selects first global match | Filter by page before keyword evaluation |
| Frontend hides a precise error | Blocker/group validation precedes mismatch fallback |
| Oversized frontend test grows broadly | One exact regression only; no fixture/refactor cleanup |
| Parallel lane ownership conflict | TASK_368A owns only Matrix paths; board remains serialized |

## 5. Validation

RED first:

- split `SECTIO N` Matrix plus singular-Page Revision Record reproduces the wrong selection;
- Page + Keyword demonstrates global search;
- explicit locator miss demonstrates auto-fallback;
- frontend demonstrates mismatch text replacing a precise blocker.

GREEN:

- task-specific backend regression;
- existing parser suite;
- exact Python compilation;
- focused Matrix Editor test;
- frontend build.

No test may read the real GS-12-2186 file. A later QA may use it read-only only with explicit
access and must not store or mutate it.

## 6. Rollback And Stop Conditions

Rollback is the exact TASK_368A lane commit range. No data migration or cleanup is required.

Quick Fixer stops and returns to Orchestrator if:

- a route/DTO/API contract must change;
- a fifth existing production file becomes necessary;
- parser body-text normalization becomes necessary;
- the focused regression reveals an unrelated Matrix authority defect;
- tests fail outside the declared defect chain without a clear attribution;
- any active-lane path overlap or destructive action is required.
