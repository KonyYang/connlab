# SPEC_PARSER Damp Heat Residual Package Reconciliation - Source-Of-Truth Reconciliation

Date: 2026-07-22

Role: Planner

Status: `complete_accepted_after_integrator_packaging`

Task: `SPEC_PARSER_DAMP_HEAT_RESIDUAL_PACKAGE_RECONCILIATION`

Lane: `spec-parser-damp-heat-residual-package-reconciliation`

Implementation authorization: authorized for the exact May Touch listed in Final Authorization Reconciliation

## Current Phase / Active Task / Why Allowed

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task: none; this is an independent residual package lane.
- Why allowed: Reviewer implementation-readiness re-gate passed and User explicitly approved product implementation. Planner was asked to reconcile final source-of-truth authorization only.

## Gate Chain Reconciled

- Reviewer plan re-gate: passed.
- User approval: Developer planning-first approved only.
- Developer pass: docs-only planning-first complete.
- Reviewer implementation-readiness re-gate: passed.
- User approval: product implementation explicitly approved.
- Current state: complete/accepted after Developer implementation, Reviewer, QA, and Integrator package isolation.

## Current Source Facts

- Checked-out UTF-8 physical-line counts including blanks, measured with `(Get-Content <path> -Encoding UTF8).Count`:
  - `backend/modules/test_plan/spec_section_text_extractor.py`: `596`.
  - `tests/unit/test_spec_section_text_extractor.py`: `786`.
- Superseded historical counts: `527` / `670` came from the non-blank `Measure-Object -Line`口径 and are not current physical-line facts.
- Current residual numstat:
  - `backend/modules/test_plan/spec_section_text_extractor.py`: `5/0`.
  - `tests/unit/test_spec_section_text_extractor.py`: `51/0`.
- Developer recorded read-only parser regression: `py -m pytest tests/unit/test_spec_section_text_extractor.py -q` -> `52 passed`.

## Mechanical Split Contract Reconciled

The earlier collector-only split is insufficient to bring the 596-line extractor below the 500-line hard limit. Future implementation must use `backend/modules/test_plan/condition_text_collectors.py` for the behavior-preserving extraction of:

- `_CONDITION_TOKEN_RE`;
- `_collect_condition_segments(...)`;
- `_collect_condition_tokens(...)`;
- electrical condition helper behavior;
- temperature-rise current helper behavior;
- dust exposure condition helper behavior;
- durability condition helper behavior.

`backend/modules/test_plan/damp_heat_condition_parser.py` remains the new Damp Heat parser helper, and `spec_section_text_extractor.py` remains limited to narrow imports, call-site renames, and Damp Heat dispatch. The expected extractor result is approximately `494` physical lines, but the formal gate is actual checked-out UTF-8 physical lines including blanks below `500`.

## B3 Line-Budget Reconciliation

Date: 2026-07-22

- Reviewer B3 found a mismatch between the task's earlier under-120 helper target and the plan's `<=150` helper budget.
- Current effective maximum: `backend/modules/test_plan/condition_text_collectors.py <=150` UTF-8 physical lines including blanks.
- This maximum is now the controlling value for task, plan, board, Planner evidence, reconciliation evidence, and future validation scans.
- Developer evidence is preserved as a historical planning-first checkpoint. To the extent it lacks this B3 budget correction, this reconciliation supersedes it as the current source of truth.
- The `<=150` limit accommodates the approved collector regex/functions plus electrical condition, temperature-rise current, dust exposure, and durability behavior-preserving helpers while remaining materially below the project 500-line hard limit.
- Unchanged gates: extractor final `<500`; `damp_heat_condition_parser.py` remains bounded; three new test modules remain bounded; the old 786-line parser test remains read-only; dirty TASK_365C replay hunk remains excluded; TASK_365A/B/C accepted behavior remains read-only regression locked.

## Final Authorization Reconciliation

Date: 2026-07-22

- Reviewer implementation-readiness re-gate passed.
- User explicitly approved product implementation.
- Current state: complete/accepted after Developer implementation, Reviewer, QA, and Integrator package isolation.
- Authorized product May Touch is exactly:
  - `backend/modules/test_plan/spec_section_text_extractor.py`
  - `backend/modules/test_plan/condition_text_collectors.py`
  - `backend/modules/test_plan/damp_heat_condition_parser.py`
- Authorized test May Touch is exactly:
  - `tests/unit/test_damp_heat_condition_parser.py`
  - `tests/unit/test_spec_section_damp_heat_dispatch.py`
  - `tests/unit/test_condition_text_collectors.py`
- Current facts remain extractor `596`, old parser test `786`, and residual numstat extractor `5/0`, old parser test `51/0`.
- Frozen implementation contract remains: mechanical split, Damp Heat helper/parser contract, narrow extractor dispatch, rollback, line budgets, hunk isolation, and package whitelist.
- Locked paths remain: old parser test read-only, TASK_365C replay hunk excluded, TASK_365A/B/C behavior locked, no Fee/default-fill, no Contact Measurement Summary UI, no frontend/API/schema/database, no Matrix/Fee/LTR/release packaging, no real data/files, no generated artifacts, no historical governance residuals, no TASK_364A/TASK_363D untracked docs, no external residuals.

## May Touch / Read-Only / Locks

Future May Touch after explicit implementation approval remains:

- `backend/modules/test_plan/spec_section_text_extractor.py`
- `backend/modules/test_plan/condition_text_collectors.py` (`<=150` UTF-8 physical lines including blanks)
- `backend/modules/test_plan/damp_heat_condition_parser.py`
- `tests/unit/test_condition_text_collectors.py`
- `tests/unit/test_damp_heat_condition_parser.py`
- `tests/unit/test_spec_section_damp_heat_dispatch.py`
- lane governance docs and narrow board hunk

Read-only regression execution only:

- `tests/unit/test_spec_section_text_extractor.py`; no lane hunk is authorized. Its dirty TASK_365C replay hunk remains excluded.

Locked:

- Fee/default-fill, Contact Measurement Summary UI, TASK_365A/B/C accepted behavior, frontend/API/schema/database, Matrix/Fee/LTR/release packaging, real data/files, generated artifacts, historical governance residuals, TASK_364A/TASK_363D untracked docs, stage/commit/push, and all other dirty residuals.

## Validation

- Reconciled `docs/task_board.md`, task, plan, Planner evidence, and this reconciliation evidence.
- Verified current physical-line counts with `(Get-Content <path> -Encoding UTF8).Count`.
- Verified residual numstat remains extractor `5/0`, old parser test `51/0`.
- No product or test implementation files were edited by this Planner pass.
- No real data, public-drive file, attachment, source workbook, generated artifact, staging, commit, or push.

## Next Legal Role

User/Orchestrator. This closeout does not activate another candidate group.
