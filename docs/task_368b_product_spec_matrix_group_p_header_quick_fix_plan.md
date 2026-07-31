# TASK_368B Product Spec Matrix Group P Header Quick Fix Plan

Date: 2026-07-31
Status: approved; isolated worktree preparation pending
Task: `TASK_368B_PRODUCT_SPEC_MATRIX_GROUP_P_HEADER_QUICK_FIX`
Lane: `task-368b-product-spec-matrix-group-p-header-quick-fix`

## 1. Discovery Gate

Current phase:

- `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current active task/lane:

- None before TASK_368B activation.
- TASK_368A is complete/accepted and locally integrated.
- The cancelled browser-release lane remains retained but owns no Matrix parser path.

Why this planning is allowed:

- The user explicitly requested resolution of the missing final `Group P` from the attached PDF
  and requested formal Quick Fixer dispatch after read-only diagnosis.
- The defect, expected behavior, source path, validation path, and non-goals are explicit.

Confirmed by user:

- Attachment:
  `PRODSPEC GS-12-1941 CoolPowerHD_Rev4.pdf`.
- The Matrix's final Group P column must be extracted.
- The Quick Fixer candidate should be formally dispatched if ownership and board state allow it.

Confirmed by repository evidence:

- Primary `master` was clean at discovery HEAD
  `c1d1066d43639bdda31c76df59449722ee4f5709`.
- No `TASK_368B` task, branch, or worktree existed.
- `ProductSpecMatrixParser._GROUP_RE` accepts only numeric prefixed groups.
- `_GROUP_NUMERIC_RE` accepts only bare numeric/numeric-suffix group tokens.
- `_find_header()` preserves the raw source label after comparison.
- A synthetic fourteen-column Matrix selects successfully but omits only final `Group P`, with no
  blocker or warning.
- Existing frontend normalization strips a leading `Group ` for display and selection matching.
- The existing parser suite is an oversized mixed module, so new coverage belongs in a bounded
  task-specific test.
- The real PDF is not stored in the repository.

Confirmed by read-only attachment diagnosis:

- Current localhost selects table `16`, page `11`, table-on-page `2`.
- It returns eleven groups and silently omits `Group P`.
- Page 11 visually and through `pdfplumber` extraction has a separate fourteenth column headed
  `Group P`, with independent step and sample values.

Planner inference:

- A full-match, header-comparison-only prefixed group token rule can support `Group P` without
  changing stored values or accepting broad phrases.
- One existing product file plus one new bounded test is sufficient.

Not yet confirmed:

- The attachment's direct local filesystem path is not available in the Orchestrator workspace.
  It remains available to the permanent Quick Fixer thread that performed the reproduction.
- This does not alter May Touch, expected behavior, or formal synthetic validation.

Planning risk:

- Broadening the regex to arbitrary words after `Group` could misclassify descriptive headers.
- Globally stripping the prefix could change raw labels and downstream traceability.
- Reusing the oversized mixed parser test would weaken lane isolation.

Decision:

- Continue. Definition of Ready is satisfied for the Quick Fixer fast path.
- No clarification question is required.

## 2. Design

### 2.1 Narrow header-token comparison

Change only the ordinary Matrix header classification in
`ProductSpecMatrixParser._find_header()`.

The comparison rule must:

- continue accepting prefixed numeric groups such as `Group 1`;
- accept a prefixed single-letter group such as `Group P`;
- continue accepting bare numeric/numeric-suffix tokens through the existing rule;
- reject broad phrases such as `Group Purpose`;
- use the normalized header cell only for comparison.

The stored label must continue to come from:

```python
_clean(row[index])
```

Therefore `Group P` remains the raw label and produces the existing stable key `group_p`.

### 2.2 Bounded regression

Add a new task-specific unit test module with:

- a fourteen-column GS-12-1941-shaped Matrix;
- final raw header `Group P`;
- independent final-column step token and sample quantity;
- assertions for exact group order, raw label, key, steps, and sample values;
- a negative header phrase such as `Group Purpose`;
- a regression assertion for existing numeric/numeric-suffix behavior.

Do not add the new coverage to `tests/unit/test_product_spec_matrix_parser.py`.

### 2.3 Read-only real-PDF smoke

The permanent Quick Fixer may reuse the user-provided attachment only for read-only validation.
The attachment must not be copied, normalized, rendered into repository artifacts, staged, or
committed.

The smoke must compare:

- current localhost baseline: table `16`, page `11`, table-on-page `2`, eleven groups;
- lane behavior: same location, twelve groups including raw `Group P`.

## 3. File-Level Changes

| Path | Planned change |
|---|---|
| `backend/modules/test_plan/product_spec_matrix_parser.py` | Narrow prefixed single-letter group header recognition, comparison only |
| `tests/unit/test_task_368b_product_spec_matrix_group_p_header.py` | New bounded synthetic positive/negative regression |
| `docs/lane_evidence/TASK_368B_product-spec-matrix-group-p-header_quick-fixer.md` | TDD, validation, smoke, checkpoint, and handoff evidence |

No existing frontend, API, DTO, application, support-parser, Office/PDF gateway, persistence,
schema, config, fixture, or release file is planned.

## 4. Risks And Controls

| Risk | Control |
|---|---|
| Descriptive `Group ...` text becomes a column | Require a full prefixed token and a single alphabetic suffix |
| Raw source label is rewritten | Comparison-only recognition; keep `_clean(row[index])` as stored label |
| Existing numeric groups regress | Run bounded test plus the complete existing parser unit module |
| Special sequence Matrix behavior changes | Do not modify parser support helpers |
| Real attachment leaks into Git | Read-only external smoke; no repository artifact |
| Frontend scope expands | Existing display normalization is read-only evidence; frontend remains locked |

## 5. Validation

RED:

- the new bounded positive test returns the existing eleven groups and omits `Group P`;
- the negative phrase remains unrecognized.

GREEN:

- bounded TASK_368B tests;
- existing product-spec parser tests;
- exact parser pycompile;
- read-only real-PDF lane smoke.

## 6. Review And Integration

- Quick Fixer creates a clean exact-path checkpoint and updates its evidence.
- Reviewer inspects the governance base through lane HEAD and reruns targeted parser validation.
- QA is optional because the change is one parser header-comparison rule with direct real-file
  smoke and no API/frontend/persistence behavior.
- Integrator merges only after Reviewer pass, reruns targeted validation on primary, updates
  task/board/evidence, records residuals, and performs only safe no-force worktree retirement.

No remote push, publication, service restart, or current-localhost refresh is authorized.

## 7. Stop Conditions

Stop if:

- more than one existing production file is needed;
- the fix must recognize unprefixed arbitrary alphabetic headers;
- PDF extraction or table location changes are required;
- API/frontend/persistence/schema behavior changes;
- real attachment mutation or destructive cleanup is required;
- validation reveals an unrelated Matrix parser defect.
