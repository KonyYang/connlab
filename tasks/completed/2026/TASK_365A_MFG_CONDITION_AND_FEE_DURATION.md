# TASK_365A MFG Condition And Fee Duration

## Status

Complete/accepted by Integrator on 2026-07-19 after Developer implementation,
Reviewer/QA passes, user acceptance, and controlled package isolation. Product
changes remain restricted to the reviewed TASK_365A plan and exact package boundary
below. The accepted package is local only; no remote push was performed.

## Phase / Lane

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Lane: `mfg-condition-and-fee-duration`.
- TASK_364B/C and TASK_365C are accepted independent baselines; TASK_365B remains a
  separate locally reviewed candidate.
- TASK_365A must not absorb TASK_365B, TASK_365C, TASK_363C/D, TASK_364B/C, or
  unrelated dirty-worktree changes.

## Goal

Carry explicit MFG Class IIA conditioning facts from the specification section into
Matrix and then into Fee Evaluation:

1. Matrix Condition becomes
   `Class IIA; unmated 224 hours; mated 112 hours`.
2. Fee Evaluation maps `MFG` to the existing Class IIA rule at `1000 / per day`.
3. Fee Units equals `(224 + 112) / 24 = 14 days`.
4. Base Fee is `0` for this 336-hour case and Testing Fee is `14000`.

## Confirmed Business Contract

- The source must explicitly provide Class IIA plus labeled unmated and mated
  durations. No missing phase is inferred.
- Accepted duration spellings for the two phases are narrow hour forms such as
  `224h`, `224 hr`, or `224 hours`; Matrix output is canonical English text.
- Fee conversion uses exact decimal arithmetic. It does not round hours or days.
- Existing explicit `day/days` MFG conditions remain supported.
- Missing, malformed, conflicting, or incomplete phase durations remain
  review-required/Pending.
- This task does not change the existing MFG rule id, price, Unit Type, seed,
  alias library, or Base Fee behavior outside the explicit 336-hour case.

## May Touch After Explicit Implementation Approval

- `backend/modules/test_plan/mfg_condition_parser.py` (new)
- `backend/modules/test_plan/spec_section_text_extractor.py` (one narrow dispatch)
- `backend/modules/fee_evaluation/mfg_duration.py` (new)
- `backend/modules/fee_evaluation/fee_default_fill.py` (one narrow MFG call)
- `tests/unit/test_spec_section_text_extractor.py`
- `tests/unit/test_product_spec_matrix_parser.py` only for the public parser path
- `tests/unit/test_fee_default_fill.py`
- `tests/unit/test_confirmed_matrix_fee_draft_service.py` only for one cross-layer draft case
- TASK_365A task, plan, Planner evidence, and narrow board status entries

## Must Not Touch / Locked Paths

- `frontend/**`, public API DTO/client modules, routes, database schema, repositories,
  migrations, and authority lifecycle
- Fee rule seeds, active manifest, matcher aliases, prices, Unit Types, exports,
  workbook writers, and Required Forms
- Current Rating / `EIA-364-70` page-continuation correction
- CR/LLCR, TASK_363C/D, Point Profile, Measurement Plan, and TASK_364B behavior
- Matrix persistence/confirmation semantics and existing confirmed records
- Real databases, real specification files, generated output, public-drive paths,
  release folders, and remote Git operations

## Acceptance Criteria

1. The quoted 8.2 MFG source text produces exactly
   `Class IIA; unmated 224 hours; mated 112 hours`.
2. Method remains `EIA-364-65` and existing Requirement normalization is unchanged.
3. Both labeled durations survive source-section extraction and Matrix preview parsing.
4. The existing `fee_rule_mfg_class_iia` produces Unit Price `1000`, Unit Type
   `day`, Units `14`, Base Fee `0`, Discount `0`, and Testing Fee `14000`.
5. Missing either labeled phase leaves Fee Units and Testing Fee Pending.
6. Explicit `14 days` remains calculated as before.
7. Unrelated parser and Fee families do not change.

## Validation Gate

- Focused red/green parser tests with inline source text only
- Focused Fee default-fill tests for 224+112 hours, explicit days, and incomplete data
- One confirmed-Matrix Fee draft regression using disposable in-memory fixtures
- Existing focused parser and Fee suites
- `py_compile`, `git diff --check`, file-size check, scope whitelist, and
  no-real-file/no-real-database verification

## Merge Gate

User plan approval, Developer implementation, Reviewer implementation review,
focused QA, and user acceptance are complete. Integrator must now package only the
following exact candidate boundary:

- whole files: `backend/modules/test_plan/mfg_condition_parser.py`,
  `backend/modules/fee_evaluation/mfg_duration.py`,
  `tests/unit/test_mfg_condition_parser.py`, and
  `tests/unit/test_mfg_duration.py`;
- exact shared-file hunks: the `extract_mfg_condition` import plus MFG branch in
  `backend/modules/test_plan/spec_section_text_extractor.py`; the
  `resolve_mfg_duration_days` import, obsolete local day-pattern removal, and
  `_duration_day_result` delegation in
  `backend/modules/fee_evaluation/fee_default_fill.py`;
- exact test hunks: the MFG condition assertion in
  `tests/unit/test_spec_section_text_extractor.py` and the three MFG draft cases in
  `tests/unit/test_confirmed_matrix_fee_draft_service.py`;
- TASK_365A task, plan, Planner/Developer/Reviewer/QA evidence, acceptance
  reconciliation evidence, and the exact board hunks.

`tests/unit/test_product_spec_matrix_parser.py`, `tests/unit/test_fee_default_fill.py`,
all PDF gateway/rebuilder hunks, Current Rating, damp-heat, thermal/surge, Salt Spray,
temperature, multi-group fixture, and unrelated Fee changes are excluded. Mixed
files require hunk-level staging; wholesale staging is forbidden. Remote push is
not authorized.
