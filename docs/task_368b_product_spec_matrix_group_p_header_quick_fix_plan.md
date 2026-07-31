# TASK_368B Product Spec Matrix Group P Header Quick Fix Plan

Date: 2026-07-31
Status: `scope_reconciliation_approved`
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
| `backend/modules/test_plan/product_spec_matrix_parser_support.py` | Allow an optional explicit `Group` prefix for the existing controlled token score comparison only |
| `tests/unit/test_task_368b_product_spec_matrix_group_p_header.py` | New bounded synthetic positive/negative regression |
| `docs/lane_evidence/TASK_368B_product-spec-matrix-group-p-header_quick-fixer.md` | TDD, validation, smoke, checkpoint, and handoff evidence |

No existing frontend, API, DTO, application, Office/PDF gateway, persistence, schema, config,
fixture, or release file is planned.

## 4. Risks And Controls

| Risk | Control |
|---|---|
| Descriptive `Group ...` text becomes a column | Require a full prefixed token and a single alphabetic suffix |
| Raw source label is rewritten | Comparison-only recognition; keep `_clean(row[index])` as stored label |
| Existing numeric groups regress | Run bounded test plus the complete existing parser unit module |
| Special sequence Matrix behavior changes | Do not modify sequence helper functions; only the top-level token comparison is in scope |
| Broad prefixed phrases earn the table-score bonus | Keep the existing controlled token domain and add bounded negative promotion coverage |
| Real attachment leaks into Git | Read-only external smoke; no repository artifact |
| Frontend scope expands | Existing display normalization is read-only evidence; frontend remains locked |

## 5. Validation

RED:

- the new bounded positive test returns the existing eleven groups and omits `Group P`;
- the negative phrase remains unrecognized.

GREEN:

- bounded TASK_368B tests;
- existing product-spec parser tests;
- exact parser/support pycompile;
- direct negative scoring proof that `Group Purpose` earns no token bonus and cannot promote an
  otherwise invalid table;
- read-only real-PDF lane smoke.

## 6. Review And Integration

- Quick Fixer creates a clean exact-path checkpoint and updates its evidence.
- Reviewer inspects the governance base through lane HEAD and reruns targeted parser validation.
- QA is mandatory because the amended support predicate participates in global Matrix table
  scoring, even though API/frontend/persistence behavior remains unchanged.
- Integrator merges only after Reviewer pass, reruns targeted validation on primary, updates
  task/board/evidence, records residuals, and performs only safe no-force worktree retirement.

No remote push, publication, service restart, or current-localhost refresh is authorized.

## 7. Stop Conditions

Stop if:

- a third existing production file is needed;
- the fix must recognize unprefixed arbitrary alphabetic headers;
- the score threshold, token bonus value, another weight, or scoring/selection flow must change;
- PDF extraction or table location changes are required;
- API/frontend/persistence/schema behavior changes;
- real attachment mutation or destructive cleanup is required;
- validation reveals an unrelated Matrix parser defect.

## 8. Scope Reconciliation Amendment

This amendment supersedes any conflicting initial-plan statement about one production file,
support-parser exclusion, or optional QA.

### 8.1 Discovery Gate

Current phase:

- `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current active task/lane:

- `TASK_368B_PRODUCT_SPEC_MATRIX_GROUP_P_HEADER_QUICK_FIX`
- `task-368b-product-spec-matrix-group-p-header-quick-fix`
- pre-reconciliation state: `blocked_scope_expansion`

Why Planner is allowed:

- The required real-PDF smoke exposed one additional scoring-comparison boundary after the
  approved parser-only probe.
- Quick Fixer stopped at the declared scope boundary, preserved an exact local checkpoint, and
  returned the conflict to Orchestrator/Planner.
- Orchestrator authoritatively received the checkpoint callback and independently verified the
  clean three-path package.

Confirmed by user:

- The user asked to fix the missing final `Group P` from
  `PRODSPEC GS-12-1941 CoolPowerHD_Rev4.pdf`.
- The goal is the same selected Matrix and same raw source data with the final Group P included.
- No new product behavior, authority path, or deployment action was requested.

Confirmed by repository evidence:

- Primary is clean on `master` at
  `d3ef8745389bf7b7c2774abfc99e691228f1804a`, with no merge in progress.
- The existing lane/base/worktree are concrete and unchanged:
  `lane/task-368b-product-spec-matrix-group-p-header-quick-fix`,
  `D:\PythonProject\connlab-worktrees\task-368b-product-spec-matrix-group-p-header-quick-fix`,
  base `b671bb493a683529cfe64ab320df4f90914406c8`.
- WIP checkpoint `b36c95d3aababe5421c09b2e3532d67317331f82` and evidence-only
  HEAD `fb6d102d54d72d252a1f7415fb8cffd648c1ea42` leave the lane worktree/index clean.
- `base..HEAD` contains exactly:
  `backend/modules/test_plan/product_spec_matrix_parser.py`,
  `tests/unit/test_task_368b_product_spec_matrix_group_p_header.py`, and Quick Fixer evidence.
- `backend/modules/test_plan/product_spec_matrix_parser_support.py` is unchanged at blob
  `3fa4423b414dd4844f2bb6e641c0c8fb02f9ec8e`.
- The parser-only comparison admits raw `Group P` and preserves the label. The bounded synthetic
  test passes.
- The real-PDF application-service smoke retains table `16`, page `11`, table-on-page `2`, but
  returns exact blocker `Selected table 16 is not a valid Matrix table.`.
- `GROUP_TOKEN_HEADER_RE` accepts only bare controlled tokens. `table_score()` awards `+12` only
  when all raw `header.group_columns` labels match; raw `Group P` therefore withholds that bonus
  and the real table falls below `ProductSpecMatrixParser._MIN_MATRIX_SCORE = 45`.

Inferred by Planner:

- This is the same defect crossing two adjacent existing comparison boundaries, not a new
  capability or scoring policy.
- A narrow optional explicit `Group` prefix followed by the existing controlled token domain is
  the smallest consistent comparison. It covers `Group P`, `Group 1`, and `Group 6a` while
  rejecting `Group Purpose`.
- The support predicate has broader selection risk than the parser-only comparison, so QA must be
  mandatory.

Not yet confirmed:

- The final implementation and real-PDF GREEN result are not yet known; they belong to the resumed
  Quick Fixer and later Reviewer/QA gates.
- No unknown changes May Touch, Must Not Touch, acceptance, data/API ownership, or role ordering.

Planning risk:

- A broad `Group ...` regex could award `+12` to descriptive phrases and promote an invalid table.
- Changing the threshold or weights would turn a token-compatibility fix into a scoring-policy
  change.
- Skipping QA would leave a global table-acceptance boundary validated only by the implementer.

Decision:

- Continue without new user approval. Existing Goal authorization plus `AGENTS.md` sections
  18.12 and 19.1 cover this bounded same-defect amendment.
- Definition of Ready is satisfied after the authoritative clean checkpoint callback.
- Reuse the existing lane/worktree. Do not create a replacement task or lane.

### 8.2 Revised May Touch

- `backend/modules/test_plan/product_spec_matrix_parser.py`
- `backend/modules/test_plan/product_spec_matrix_parser_support.py`
- `tests/unit/test_task_368b_product_spec_matrix_group_p_header.py`
- `docs/lane_evidence/TASK_368B_product-spec-matrix-group-p-header_quick-fixer.md`

Primary governance only:

- `tasks/TASK_368B_PRODUCT_SPEC_MATRIX_GROUP_P_HEADER_QUICK_FIX.md`
- this plan
- `docs/task_board.md`
- later role-specific Reviewer/QA/Integrator evidence

### 8.3 Revised Must Not Touch

- Any third existing production file.
- `backend/application/**`, `backend/api/**`, `backend/domain/**`,
  `backend/infrastructure/**`, and `frontend/src/**`.
- Existing mixed parser tests other than running them read-only.
- `_MIN_MATRIX_SCORE`, the `+12` complete-token bonus value, every other score weight,
  `table_score()` control flow, and parser selection/tie-breaking.
- Matrix persistence/authority, schema/database, Office/PDF extraction, locator behavior,
  API/DTO, frontend, release paths, or real attachment contents.
- Cancelled browser-release retained state, TASK_368A residuals, and frozen V2 state.
- Push, merge, cherry-pick, restart, destructive cleanup, or worktree retirement.

### 8.4 Exact Implementation Boundary

The support comparison may accept an optional explicit `Group` prefix followed by the same
controlled token domain already allowed by `GROUP_TOKEN_HEADER_RE`. It must:

- accept at minimum `Group P`, and consistently accept `Group 1` and `Group 6a`;
- reject `Group Purpose` and other broad phrases;
- preserve the raw labels supplied by `header.group_columns`;
- leave `_MIN_MATRIX_SCORE = 45`, the `+12` bonus, every other weight, and scoring flow unchanged.

### 8.5 Acceptance And Validation

Quick Fixer must extend the already-owned bounded test/evidence only. Required proof:

1. Synthetic fourteen-column parsing returns exact groups
   `1, 2, 3, 4, 5, 6a, 6b, 7, 8, 9, 10, Group P`.
2. Raw `Group P`, key, steps, sample expression, and sample size remain correct.
3. Controlled prefixed forms `Group P`, `Group 1`, and `Group 6a` are scoring-compatible.
4. `Group Purpose` does not earn the complete-token `+12` bonus.
5. A broad phrase cannot promote an otherwise below-threshold invalid table.
6. Existing parser regression remains green.
7. Real-PDF smoke keeps table `16`, page `11`, table-on-page `2`, returns all twelve groups with
   no repair-attributable blocker/warning, and performs no write or persistence.

Commands:

```powershell
py -m pytest tests\unit\test_task_368b_product_spec_matrix_group_p_header.py -q
py -m pytest tests\unit\test_task_368b_product_spec_matrix_group_p_header.py tests\unit\test_product_spec_matrix_parser.py -q
py -m py_compile backend\modules\test_plan\product_spec_matrix_parser.py backend\modules\test_plan\product_spec_matrix_parser_support.py
git diff --check
```

### 8.6 Role Gates

- Quick Fixer: resume only from clean lane HEAD
  `fb6d102d54d72d252a1f7415fb8cffd648c1ea42`; produce a new exact-path implementation
  checkpoint and final evidence-only HEAD.
- Reviewer: mandatory committed-diff gate from base through final lane HEAD; inspect the exact
  scoring predicate, raw-label preservation, negative promotion regression, and line limits.
- QA: mandatory clean-reviewed-commit validation, including bounded/existing parser regressions
  and read-only real-PDF smoke provenance.
- Integrator: only after Reviewer and QA pass; verify package/ancestry, run merged-tree validation,
  record residuals, and perform no push/publication/restart.
