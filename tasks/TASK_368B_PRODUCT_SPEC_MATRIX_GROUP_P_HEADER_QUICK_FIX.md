# TASK_368B_PRODUCT_SPEC_MATRIX_GROUP_P_HEADER_QUICK_FIX

Status: `complete` / `accepted` / `locally_integrated`
Lane: `task-368b-product-spec-matrix-group-p-header-quick-fix`
Owner role: Integrator closeout complete; no active implementation owner
Date: 2026-07-31

## Dispatch Worktree

- Branch: `lane/task-368b-product-spec-matrix-group-p-header-quick-fix`
- Worktree:
  `D:\PythonProject\connlab-worktrees\task-368b-product-spec-matrix-group-p-header-quick-fix`
- Governance/base commit:
  `b671bb493a683529cfe64ab320df4f90914406c8`
- Creation verification: the branch, worktree HEAD, worktree status, and index match the exact
  recorded base and are clean.
- Global board dispatch metadata is committed only on primary. The lane Quick Fixer owns its
  evidence file and must not edit task/board during implementation.

## Current Phase / Why Allowed

- Current phase:
  `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- The user explicitly requested a fix for the attached
  `PRODSPEC GS-12-1941 CoolPowerHD_Rev4.pdf`.
- Read-only reproduction is stable: current localhost selects document table `16`, page `11`,
  table-on-page `2`, but returns only Groups
  `1, 2, 3, 4, 5, 6a, 6b, 7, 8, 9, 10`; the final `Group P` is absent without a blocker or warning.
- The correct Matrix table is already selected. The missing column is caused by the parser's
  bounded header-token classification, not by locator, API, persistence, frontend, or PDF
  extraction ownership.
- At TASK_368B activation, `docs/task_board.md` recorded no active implementation task. TASK_368A
  is complete and its parser paths are no longer actively locked. The cancelled browser-release
  lane does not own Matrix parser paths.
- The user requested formal Quick Fixer dispatch after the read-only diagnosis, satisfying the
  implementation approval gate for this exact scope.

## Scope Reconciliation Authority

- Quick Fixer stopped correctly after the parser-only synthetic change passed but the required
  real-PDF smoke returned
  `Selected table 16 is not a valid Matrix table.`.
- The blocked WIP is preserved at `b36c95d3aababe5421c09b2e3532d67317331f82`;
  evidence-only lane HEAD is
  `fb6d102d54d72d252a1f7415fb8cffd648c1ea42`.
- The lane worktree/index are clean. `base..HEAD` contains exactly parser.py, the new bounded
  TASK_368B test, and Quick Fixer evidence. The support file is unchanged.
- Repository evidence confirms the same defect crosses one additional comparison boundary:
  raw `Group P` is now a parser group column, but
  `GROUP_TOKEN_HEADER_RE` does not recognize an explicit `Group` prefix and therefore withholds
  the existing `+12` complete-token score. The real selected table falls below the unchanged
  `_MIN_MATRIX_SCORE = 45`.
- Existing user authorization and `AGENTS.md` sections 18.12/19.1 cover this bounded same-defect
  amendment: two existing implementation files, one bounded test, no new task/worktree, and no
  product contract, authority, persistence, API, or data change.
- Continuation may change only the support comparison used to decide whether all raw
  `header.group_columns` labels earn the existing token bonus. It must not change the score
  threshold, bonus value, any other weight, table selection flow, or stored raw labels.
- Because this support predicate affects Matrix table acceptance globally, QA is mandatory after
  Reviewer pass.

## Local Integration Acceptance

- Quick Fixer ready HEAD:
  `59ea8455d2283bce3411a1031a3867331783a8d7`.
- Reviewer evidence HEAD:
  `1b41bd5f71679e7cd1188d1da5a6502eb2292e8c`.
- QA/lane HEAD:
  `5cac86b60c728bcbb6a1b72a9e3d340fc976d21b`.
- Primary pre-merge HEAD:
  `d3314a047f69dffd497927dc0e95802e04f17259`.
- Local non-fast-forward merge commit:
  `acceeb04241e57d77634f8dbb7f4f9cdef6bba55`.
- The merge was conflict-free. Its first-parent delta is exactly the six authorized parser,
  bounded-test, and Quick Fixer/Reviewer/QA evidence paths; the amended primary task, plan, and
  board were preserved.
- Merged-tree validation passed: bounded TASK_368B `3 passed`, combined parser regression
  `27 passed`, exact two-module pycompile, package/forbidden-path checks, `diff --check`,
  `git show --check`, and ancestry checks.
- `_MIN_MATRIX_SCORE` remains `45`; the complete-token bonus remains `+12`; every other
  score weight and scoring/selection branch remains unchanged.
- Integrator did not access the real PDF. QA's read-only smoke provenance records the same table
  `16`, page `11`, table-on-page `2`, all twelve groups ending in raw `Group P`, and no warnings
  or blockers.
- No push, publication, or localhost restart occurred. An already-running localhost may continue
  using old process code until a separately authorized future restart; local integration is not
  runtime refresh.
- The clean integrated TASK_368B lane branch/worktree is retained under permanent Orchestrator
  governance for a future safe maintenance retirement. No removal was attempted in this gate.
- TASK_368A residuals and the cancelled browser-release checkpoint remain separate existing
  `retain` items and were not touched.

## Goal

Recognize a prefixed single-letter Matrix group header such as `Group P` in the ordinary Product
Specification Matrix header path while preserving the exact raw source label and all body values.

## Confirmed Input

- A neutral Matrix table with fourteen columns:
  test item, section, Groups `1` through `10` including `6a` and `6b`, and final `Group P`.
- The final column has independent step tokens and sample quantity values.
- The real PDF remains external, read-only validation evidence and must not be copied into the
  repository.

## Expected Output

- The selected table remains unchanged.
- Parsed Groups are:
  `1, 2, 3, 4, 5, 6a, 6b, 7, 8, 9, 10, Group P`.
- `Group P` retains:
  - raw `group_label == "Group P"`;
  - stable `group_key == "group_p"`;
  - its own step tokens;
  - its own sample quantity expression and numeric sample size when parseable.
- Existing numeric and numeric-suffix headers continue to behave unchanged.
- Frontend display continues to derive `P` through its existing prefix-normalization logic; no
  frontend change is required.

## Acceptance Criteria

1. A bounded synthetic fourteen-column Matrix reproduces the missing final column before the
   change and returns all twelve groups after the change.
2. Header comparison recognizes a fully prefixed single-letter token such as `Group P`.
3. The implementation preserves raw source label `Group P`; it must not globally remove
   `Group ` from stored labels, body rows, notes, test items, or step tokens.
4. A broad phrase such as `Group Purpose` is not accepted as a group column.
5. Existing `Group 1`, bare numeric, and numeric-suffix group headers remain supported.
6. The existing complete-group-token score recognizes an explicit `Group` prefix followed by the
   same controlled token domain, including `Group P`, `Group 1`, and `Group 6a`; `Group Purpose`
   does not earn the token bonus and cannot promote an otherwise invalid table.
7. `_MIN_MATRIX_SCORE` remains `45`; the token bonus remains `+12`; every other score weight and
   scoring/selection branch remains unchanged.
8. No API, DTO, frontend, application service, persistence, schema, Office gateway, locator, PDF
   extraction, or Matrix authority behavior changes.
9. The real PDF smoke is read-only and records the same table/page/table-on-page with final
   `Group P`; it performs no Replace, Confirm Matrix, persistence, upload mutation, or file write.

## May Touch

- `backend/modules/test_plan/product_spec_matrix_parser.py`
- `backend/modules/test_plan/product_spec_matrix_parser_support.py`
- `tests/unit/test_task_368b_product_spec_matrix_group_p_header.py`
- `docs/lane_evidence/TASK_368B_product-spec-matrix-group-p-header_quick-fixer.md`

Governance before dispatch and Integrator closeout may additionally update:

- this task file;
- `docs/task_368b_product_spec_matrix_group_p_header_quick_fix_plan.md`;
- `docs/task_board.md`;
- role-specific Reviewer/Integrator evidence.

## Must Not Touch

- `backend/application/**`
- `backend/api/**`
- `backend/domain/**`
- `backend/infrastructure/**`
- `frontend/src/**`
- existing mixed parser tests other than running them read-only
- Matrix persistence/authority, schema/database, Office/PDF extraction, locator behavior
- `_MIN_MATRIX_SCORE`, the `+12` token bonus value, all other scoring weights, table-score flow,
  and selection/tie-breaking behavior
- real attachments or extracted user data
- release/launcher/cache paths
- cancelled browser-release retained branch/worktree/checkpoint
- frozen Controlled Lane V2 worktrees or runtime state

## Validation Gate

Required RED/GREEN:

```powershell
py -m pytest tests\unit\test_task_368b_product_spec_matrix_group_p_header.py -q
py -m pytest tests\unit\test_task_368b_product_spec_matrix_group_p_header.py tests\unit\test_product_spec_matrix_parser.py -q
py -m py_compile backend\modules\test_plan\product_spec_matrix_parser.py backend\modules\test_plan\product_spec_matrix_parser_support.py
```

The bounded TASK_368B module must additionally prove:

- `Group P`, `Group 1`, and `Group 6a` satisfy the controlled prefixed-token comparison;
- `Group Purpose` does not earn the `+12` complete-token score;
- a broad phrase cannot promote an otherwise below-threshold invalid table;
- raw group labels remain unchanged.

Required read-only attachment smoke when the attachment is available in the permanent Quick
Fixer thread:

- current localhost baseline remains recorded as eleven groups without `Group P`;
- lane parser/service result selects table `16`, page `11`, table-on-page `2`;
- result contains the original eleven groups plus raw label `Group P`;
- no blocker/warning attributable to this change;
- no real-file write, persistence, Replace, Confirm Matrix, push, publication, or service restart.

## Merge Gate

- clean exact-path Quick Fixer checkpoint;
- targeted validation and read-only real-PDF smoke recorded;
- permanent Reviewer pass;
- mandatory permanent QA validation on the clean reviewed commit;
- permanent Integrator package/ancestry/merged-tree validation;
- exact residual ledger and safe worktree lifecycle;
- no push, publication, or service restart.

QA is mandatory because the amended support predicate participates in global Matrix table scoring.

## Stop Conditions

Quick Fixer must stop and return to Orchestrator if:

- a third existing production file is required;
- support-parser behavior beyond the exact controlled-token comparison, locator, PDF extraction,
  API/DTO, frontend, persistence, or schema behavior must change;
- `_MIN_MATRIX_SCORE`, the `+12` token bonus value, another score weight, or scoring/selection flow
  must change;
- acceptance would require bare arbitrary alphabetic headers rather than an explicit `Group`
  prefix;
- the synthetic regression cannot reproduce the omission;
- the selected table/page changes;
- tests fail outside the declared parser boundary without a clear cause;
- any destructive action, remote push, shared-path conflict, or real-file mutation is required.
