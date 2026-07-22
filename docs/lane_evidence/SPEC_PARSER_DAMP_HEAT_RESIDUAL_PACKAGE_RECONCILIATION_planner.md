# SPEC_PARSER Damp Heat Residual Package Reconciliation - Planner Evidence

Date: 2026-07-22

Role: Planner

Status: implementation authorized / pending Developer implementation

Task: `SPEC_PARSER_DAMP_HEAT_RESIDUAL_PACKAGE_RECONCILIATION`

Lane: `spec-parser-damp-heat-residual-package-reconciliation`

## Current Phase / Active Task / Why Allowed

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task: none.
- Why allowed: Reviewer implementation-readiness re-gate passed and User explicitly approved product implementation. This pass reconciles governance source of truth only; product/test edits belong to the next Developer pass.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `tasks/TASK_365A_MFG_CONDITION_AND_FEE_DURATION.md`
- `tasks/TASK_365B_TEXT_PDF_DOCX_MATRIX_EXTRACTION_PARITY.md`
- `tasks/TASK_365C_MATRIX_THERMAL_AND_VOLTAGE_SURGE_MCR_EXTRACTION.md`
- TASK_365A/B/C lane evidence selected for parser ownership and package boundaries.
- `backend/modules/test_plan/spec_section_text_extractor.py`
- `tests/unit/test_spec_section_text_extractor.py` as dirty source evidence only; future use is read-only regression execution.
- `git diff`, `git diff --numstat`, `git log`, `git status`, UTF-8 line counts, and focused parser test output.

## Confirmed By User

- Prioritize Spec parser residual over Fee/default-fill and Contact Measurement Summary UI.
- Dirty candidate paths are exactly `spec_section_text_extractor.py` and `test_spec_section_text_extractor.py`.
- Strict exclusions: Fee/default-fill, Contact Measurement Summary UI, historical governance docs, TASK_364A/TASK_363D untracked docs, frontend/API/schema/database/Matrix/Fee/LTR/release, real DB/public-drive/files, generated artifacts, other residuals, stage/commit/push.
- Historical discovery-stage authorization: planned-only output was allowed if DoR was met; implementation remained unauthorized until the later Reviewer readiness pass and User implementation approval.

## Confirmed By Repository Evidence

- Current dirty product diff is a Damp Heat branch inserted before generic humidity.
- Current dirty test diff adds a Long-term Damp Heat test and two TASK_365C replay tests.
- Current checked-out UTF-8 physical-line counts including blanks, measured with `(Get-Content <path> -Encoding UTF8).Count`, are:
  - `spec_section_text_extractor.py`: 596.
  - `tests/unit/test_spec_section_text_extractor.py`: 786.
- Superseded historical checkpoint: prior 527/670 facts came from the non-blank `Measure-Object -Line` count and are not current physical-line source of truth.
- Current residual numstat remains extractor `5/0` and old parser test `51/0`.
- `py -m pytest tests\unit\test_spec_section_text_extractor.py -q` passed with `52 passed`.
- TASK_365A accepted MFG and TASK_365C accepted Thermal Shock / Voltage Surge use bounded helper modules and narrow extractor dispatches.
- TASK_365A evidence explicitly lists Damp Heat as excluded from its package. TASK_365B locks shared parser production logic for its package. TASK_365C scope does not include Damp Heat.

## Planner Inference

- Damp Heat is an unaccepted parser residual, not an accepted TASK_365A/B/C replay.
- It is small and suitable for an independent corrective/package lane.
- It should not be implemented by growing the oversized extractor or old test module. A helper module plus behavior-preserving collector split and new bounded test modules are required for a clean package.

## Not Yet Confirmed

- Whether Reviewer/User will accept adding helper/test helper paths beyond the two original dirty files. Planner recommends this because the file-size contract would otherwise be violated.

## B1/B2 Docs-Only Fix

Date: 2026-07-22

Status: `superseded_by_source_of_truth_reconciliation`

- Removed `tests/unit/test_spec_section_text_extractor.py` from future May Touch. It is read-only regression execution only.
- Explicitly excluded the dirty Thermal Shock / Voltage Surge replay hunk as accepted TASK_365C baseline residual.
- Added bounded future test modules:
  - `tests/unit/test_damp_heat_condition_parser.py`
  - `tests/unit/test_spec_section_damp_heat_dispatch.py`
  - `tests/unit/test_condition_text_collectors.py`
- Initial frozen behavior-preserving extractor split:
  - move `_CONDITION_TOKEN_RE`, `_collect_condition_segments(...)`, and `_collect_condition_tokens(...)` to `backend/modules/test_plan/condition_text_collectors.py`;
  - expose `collect_condition_segments(...)` and `collect_condition_tokens(...)`;
  - preserve current `_clean(...)` whitespace behavior through an equivalent private cleaner or non-cyclic utility;
  - update only generic humidity, thermal disturbance, high temperature, vibration, and default token fallback call sites.
- Frozen Damp Heat helper boundary:
  - `backend/modules/test_plan/damp_heat_condition_parser.py` owns Damp Heat condition keyword/segment extraction;
  - extractor owns only Test Item branch priority and dispatch.
- Superseded line facts recorded at this checkpoint: extractor `527`, old parser test `670`; these are retained as historical non-blank line-count facts only.
- Future implementation must end with every touched/new Python file below 500 lines, without blank-line suppression.

## Source-Of-Truth Reconciliation

Date: 2026-07-22

Status: `ready_for_reviewer_implementation_readiness_re_gate`

- Reviewer plan re-gate passed.
- User approved Developer planning-first.
- Developer docs-only planning-first complete.
- Historical B3 checkpoint: product/test implementation remained unauthorized before the later Reviewer readiness pass and User implementation approval.
- Current physical-line facts, using checked-out UTF-8 physical lines including blanks: extractor `596`, old parser test `786`.
- Current residual numstat remains extractor `5/0`, old parser test `51/0`.
- The collector-only split is insufficient. Future implementation must also move pure electrical condition, temperature-rise current, dust exposure, and durability condition helpers into `condition_text_collectors.py`.
- Expected final extractor is approximately `494` physical lines, but the formal gate is actual checked-out UTF-8 physical lines including blanks below `500`.
- The old `tests/unit/test_spec_section_text_extractor.py` remains read-only regression execution only; dirty accepted TASK_365C replay hunks are excluded.

## B3 Docs-Only Fix

Date: 2026-07-22

Status: `ready_for_reviewer_implementation_readiness_re_gate`

- Reviewer B3 found a controlling budget mismatch: task had `condition_text_collectors.py` under `120` lines while plan had `<=150`.
- Current effective contract freezes `backend/modules/test_plan/condition_text_collectors.py <=150` UTF-8 physical lines including blanks.
- The `<=150` maximum is required to contain the approved collector regex/functions plus the electrical condition, temperature-rise current, dust exposure, and durability behavior-preserving helpers while staying far below the 500-line hard limit.
- Any earlier smaller `condition_text_collectors.py` target is superseded. Developer evidence remains a historical planning-first checkpoint; this Planner reconciliation is the current controlling line-budget source of truth.
- Extractor `596`, old parser test `786`, final extractor `<500`, three bounded tests, old parser test read-only behavior, TASK_365C replay exclusion, and TASK_365A/B/C regression locks remain unchanged.

## Final Authorization Reconciliation

Date: 2026-07-22

Status: `implementation_authorized_pending_developer_implementation`

- Reviewer implementation-readiness re-gate passed.
- User explicitly approved product implementation.
- Current state: implementation authorized / pending Developer implementation.
- Current source facts remain extractor `596`, old parser test `786`, and residual numstat extractor `5/0`, old parser test `51/0`.
- Authorized product May Touch is exactly:
  - `backend/modules/test_plan/spec_section_text_extractor.py`
  - `backend/modules/test_plan/condition_text_collectors.py`
  - `backend/modules/test_plan/damp_heat_condition_parser.py`
- Authorized test May Touch is exactly:
  - `tests/unit/test_damp_heat_condition_parser.py`
  - `tests/unit/test_spec_section_damp_heat_dispatch.py`
  - `tests/unit/test_condition_text_collectors.py`
- `condition_text_collectors.py <=150` UTF-8 physical lines including blanks and final extractor `<500` remain controlling line-budget gates.
- Old `tests/unit/test_spec_section_text_extractor.py` remains read-only; the dirty TASK_365C replay hunk is excluded; TASK_365A/B/C accepted behavior remains locked.
- No Fee/default-fill, Contact Measurement Summary UI, frontend/API/schema/database, Matrix/Fee/LTR/release packaging, real data/files, generated artifacts, historical governance residuals, TASK_364A/TASK_363D untracked docs, or external residuals are authorized.

## Lane Decision

Route Developer implementation pass. Do not route QA or Integrator.

## May Touch / Locked Scope

Future May Touch after explicit approval:

- `backend/modules/test_plan/damp_heat_condition_parser.py`
- `backend/modules/test_plan/condition_text_collectors.py` (`<=150` UTF-8 physical lines including blanks)
- `backend/modules/test_plan/spec_section_text_extractor.py`
- `tests/unit/test_damp_heat_condition_parser.py`
- `tests/unit/test_spec_section_damp_heat_dispatch.py`
- `tests/unit/test_condition_text_collectors.py`
- this task/plan/evidence and narrow board status hunk

Read-only regression only:

- `tests/unit/test_spec_section_text_extractor.py`; no new hunk is authorized.

Locked:

- Fee/default-fill, Contact Measurement Summary UI, TASK_365A/B/C accepted code, old parser test edits, TASK_365C replay hunks, frontend/API/schema/database/Matrix/Fee/LTR/release, real DB/files, generated artifacts, historical governance residuals, TASK_364A/TASK_363D untracked docs, other dirty residuals, stage/commit/push.

## Validation Performed

- Read-only git diff/status/history and line-count checks.
- Focused parser suite: `52 passed`.
- No product/test code edits.
- No real data/file access.
- No staging, commit, or push.

## Next Legal Role

Developer implementation pass.
