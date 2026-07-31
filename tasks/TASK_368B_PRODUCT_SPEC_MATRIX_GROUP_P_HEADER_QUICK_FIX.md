# TASK_368B_PRODUCT_SPEC_MATRIX_GROUP_P_HEADER_QUICK_FIX

Status: approved and dispatched for bounded Quick Fixer implementation
Lane: `task-368b-product-spec-matrix-group-p-header-quick-fix`
Owner role: permanent Quick Fixer
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
- `docs/task_board.md` records no current active task. TASK_368A is complete and its parser paths
  are no longer actively locked. The cancelled browser-release lane does not own Matrix parser
  paths.
- The user requested formal Quick Fixer dispatch after the read-only diagnosis, satisfying the
  implementation approval gate for this exact scope.

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
6. No API, DTO, frontend, application service, persistence, schema, Office gateway, locator,
   scoring, or Matrix authority behavior changes.
7. The real PDF smoke is read-only and records the same table/page/table-on-page with final
   `Group P`; it performs no Replace, Confirm Matrix, persistence, upload mutation, or file write.

## May Touch

- `backend/modules/test_plan/product_spec_matrix_parser.py`
- `tests/unit/test_task_368b_product_spec_matrix_group_p_header.py`
- `docs/lane_evidence/TASK_368B_product-spec-matrix-group-p-header_quick-fixer.md`

Governance before dispatch and Integrator closeout may additionally update:

- this task file;
- `docs/task_368b_product_spec_matrix_group_p_header_quick_fix_plan.md`;
- `docs/task_board.md`;
- role-specific Reviewer/Integrator evidence.

## Must Not Touch

- `backend/modules/test_plan/product_spec_matrix_parser_support.py`
- `backend/application/**`
- `backend/api/**`
- `backend/domain/**`
- `backend/infrastructure/**`
- `frontend/src/**`
- existing mixed parser tests other than running them read-only
- Matrix persistence/authority, schema/database, Office/PDF extraction, locator/scoring behavior
- real attachments or extracted user data
- release/launcher/cache paths
- cancelled browser-release retained branch/worktree/checkpoint
- frozen Controlled Lane V2 worktrees or runtime state

## Validation Gate

Required RED/GREEN:

```powershell
py -m pytest tests\unit\test_task_368b_product_spec_matrix_group_p_header.py -q
py -m pytest tests\unit\test_task_368b_product_spec_matrix_group_p_header.py tests\unit\test_product_spec_matrix_parser.py -q
py -m py_compile backend\modules\test_plan\product_spec_matrix_parser.py
```

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
- permanent Integrator package/ancestry/merged-tree validation;
- exact residual ledger and safe worktree lifecycle;
- no push, publication, or service restart.

QA is not mandatory for this one-file parser fast path unless Reviewer or Integrator identifies a
new risk, the real-PDF smoke cannot be attributed, or validation exposes behavior outside this
task.

## Stop Conditions

Quick Fixer must stop and return to Orchestrator if:

- a second existing production file is required;
- support-parser, locator, PDF extraction, API/DTO, frontend, persistence, or schema behavior must
  change;
- acceptance would require bare arbitrary alphabetic headers rather than an explicit `Group`
  prefix;
- the synthetic regression cannot reproduce the omission;
- the selected table/page changes;
- tests fail outside the declared parser boundary without a clear cause;
- any destructive action, remote push, shared-path conflict, or real-file mutation is required.
