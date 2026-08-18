# SPEC_PARSER Damp Heat Residual Package Reconciliation

Date: 2026-07-22

Status: complete / accepted after Integrator package gate

Lane: `spec-parser-damp-heat-residual-package-reconciliation`

Role: Integrator closeout

Implementation authorization: authorized for the exact May Touch listed in Final Authorization Reconciliation

## Current Phase / Active Task / Why Allowed

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task: none, per `docs/task_board.md`.
- Why allowed: Developer implementation, Reviewer, QA, and the controlled Integrator package gate passed. This closeout does not activate another parser or product lane.

## User Goal

Assess the current Damp Heat parser residual as an independent package candidate. The dirty hunks are limited to `backend/modules/test_plan/spec_section_text_extractor.py` and `tests/unit/test_spec_section_text_extractor.py`, but the accepted parser baseline and file-size rules must decide whether those hunks can be packaged as-is or require a narrower helper-based corrective lane.

## Confirmed By User

- Spec parser residual is the priority over Fee/default-fill and Contact Measurement Summary UI residuals.
- Discovery must compare accepted TASK_365A/B/C parser baselines and current dirty hunks.
- Historical before final authorization: product implementation remained unauthorized until Reviewer implementation-readiness re-gate passed and User explicitly approved implementation.
- Fee/default-fill, frontend/UI, API/schema/database, Matrix, LTR, release packaging, real data/files, and all other dirty residuals are locked.

## Confirmed By Repository Evidence

- `TASK_365A_MFG_CONDITION_AND_FEE_DURATION` is complete/accepted and explicitly excluded damp heat from its package.
- `TASK_365B_TEXT_PDF_DOCX_MATRIX_EXTRACTION_PARITY` is complete/accepted and locks `backend/modules/test_plan/spec_section_text_extractor.py` production logic as read-only for that lane.
- `TASK_365C_MATRIX_THERMAL_AND_VOLTAGE_SURGE_MCR_EXTRACTION` is complete/accepted and added Thermal Shock / Voltage Surge through small helper parsers plus narrow dispatches.
- Current dirty product hunk adds a direct Damp Heat branch to `_extract_condition()` using `_collect_condition_segments(...)`.
- Current dirty test hunk adds one Damp Heat case plus two accepted-baseline replay cases for Thermal Shock and Voltage Surge.
- Current checked-out UTF-8 physical line counts including blanks, measured with `(Get-Content <path> -Encoding UTF8).Count`:
  - `backend/modules/test_plan/spec_section_text_extractor.py`: 596 lines.
  - `tests/unit/test_spec_section_text_extractor.py`: 786 lines.
- Superseded historical checkpoint: prior `527` / `670` values came from the non-blank `Measure-Object -Line` count and are not the current physical-line source of truth.
- Current residual numstat remains:
  - `backend/modules/test_plan/spec_section_text_extractor.py`: `5/0`.
  - `tests/unit/test_spec_section_text_extractor.py`: `51/0`.
- Focused existing parser test run passed: `py -m pytest tests\unit\test_spec_section_text_extractor.py -q` -> `52 passed`.

## Planner Decision

Create a corrective/package lane and hold it at implementation-readiness review. The current two-path residual is coherent and testable, but it is not implementation-ready as a two-path product package because `spec_section_text_extractor.py` is already above the 500-line hard limit and the existing parser test module is 786 physical lines. The lane must follow the TASK_365A/C pattern and also perform a behavior-preserving mechanical split before adding Damp Heat behavior.

## Source-Of-Truth Reconciliation

Date: 2026-07-22

- Reviewer plan re-gate: passed.
- Historical user approval at planning-first stage: Developer planning-first approved only; product/test implementation remained unauthorized at that checkpoint.
- Developer planning-first: docs-only complete.
- Historical state at the B3 reconciliation checkpoint: pre-implementation authorization readiness.
- Current physical-line facts: extractor `596`, old parser test `786`, using checked-out UTF-8 physical lines including blanks.
- Superseded line facts: `527` / `670` may appear only as historical non-blank line-count checkpoints.
- Mechanical split decision: collector-only split is insufficient; future implementation must also move the four pure condition helpers for electrical condition, temperature-rise current, dust exposure, and durability into `condition_text_collectors.py`.
- B3 line-budget decision: `condition_text_collectors.py` has one current effective maximum of `<=150` UTF-8 physical lines including blanks. Any earlier smaller helper budget is superseded for this expanded helper.

## Final Authorization Reconciliation

Date: 2026-07-22

- Reviewer implementation-readiness re-gate: passed.
- User approval: product implementation explicitly approved.
- Current state: complete/accepted after Developer implementation, Reviewer, QA, and Integrator package isolation.
- Authorized product May Touch is exactly:
  1. `backend/modules/test_plan/spec_section_text_extractor.py`
  2. `backend/modules/test_plan/condition_text_collectors.py`
  3. `backend/modules/test_plan/damp_heat_condition_parser.py`
- Authorized test May Touch is exactly:
  1. `tests/unit/test_damp_heat_condition_parser.py`
  2. `tests/unit/test_spec_section_damp_heat_dispatch.py`
  3. `tests/unit/test_condition_text_collectors.py`
- All existing locks remain: old parser test read-only, TASK_365C replay hunk excluded, TASK_365A/B/C behavior locked, no Fee/UI/API/schema/database/Matrix/LTR/release/real data/generated artifact/residual scope.

## May Touch After Future Explicit Implementation Approval

- `backend/modules/test_plan/damp_heat_condition_parser.py` (new helper; target under 120 physical lines).
- `backend/modules/test_plan/condition_text_collectors.py` (new behavior-preserving split helper; hard maximum `<=150` UTF-8 physical lines including blanks).
- `backend/modules/test_plan/spec_section_text_extractor.py` (narrow imports, Damp Heat dispatch, and call-site renames only; final file under 500 physical lines).
- `tests/unit/test_damp_heat_condition_parser.py` (new focused helper tests; target under 180 physical lines).
- `tests/unit/test_spec_section_damp_heat_dispatch.py` (new bounded extractor integration/dispatch tests; target under 160 physical lines).
- `tests/unit/test_condition_text_collectors.py` (new bounded behavior-preserving split tests; target under 160 physical lines).
- This task, plan, Planner evidence, Reviewer evidence, and narrow `docs/task_board.md` status hunk.

Read-only regression execution only:

- `tests/unit/test_spec_section_text_extractor.py`; no new hunks may be added. Its current dirty Thermal Shock / Voltage Surge replay hunk belongs to accepted TASK_365C and is explicitly excluded from this lane.

## Must Not Touch

- Fee/default-fill paths and Fee rules/seeds/pricing.
- Contact Measurement Summary UI residuals.
- TASK_365A MFG helper/Fee behavior, TASK_365B PDF/DOCX infrastructure behavior, and TASK_365C Thermal Shock / Voltage Surge helpers.
- Frontend, API/client/routes, schema/database/repositories, Matrix persistence/confirmation, Settings, LTR, release packaging, real DB/files, public-drive paths, generated artifacts, `.agents/**`, and `docs/project_management/**`.
- Historical governance residuals, TASK_364A/TASK_363D untracked docs, and all other dirty worktree hunks.

## Frozen Parser Contract

- Trigger only when normalized Test Item contains `damp heat`.
- Damp Heat takes priority over generic `humidity` so long-term damp heat does not fall through to broader cyclic humidity extraction.
- Extract source-faithful condition text only from explicit Damp Heat condition / temperature / humidity / RH / duration / hour facts.
- Preserve the accepted segment filtering that excludes EIA method clauses from Condition.
- Do not infer missing temperature, humidity, RH, duration, mating state, aging outcome, or Requirement.
- Output for the confirmed example remains exactly:
  `Damp Heat Condition: 85℃, 85% RH, 1000h (mated test)`.
- Generic humidity behavior, MFG behavior, Thermal Shock behavior, Voltage Surge behavior, Method extraction, Requirement fallback, and Fee behavior remain unchanged.

## Required Behavior-Preserving Split

Before adding Damp Heat behavior, Developer must mechanically move the existing generic condition collector logic and four pure condition helpers out of `spec_section_text_extractor.py`:

- Move `_CONDITION_TOKEN_RE`, `_collect_condition_segments(...)`, and `_collect_condition_tokens(...)` into `backend/modules/test_plan/condition_text_collectors.py` as public `collect_condition_segments(...)` and `collect_condition_tokens(...)`.
- Move `_extract_electrical_condition(...)`, `_extract_temperature_rise_current(...)`, `_extract_dust_exposure_condition(...)`, and `_extract_durability_condition(...)` into `condition_text_collectors.py` as behavior-preserving public helpers.
- The new helper may own a private cleaner equivalent to the current `_clean(...)` whitespace normalization, but must not change output formatting.
- Update extractor call sites only:
  - DWV and insulation-resistance electrical condition;
  - Current Rating / Temperature Rise current;
  - Dust Exposure;
  - Durability;
  - generic humidity;
  - thermal disturbance;
  - high temperature;
  - vibration;
  - shock;
  - default condition-token fallback.
- Do not move method extraction, requirement extraction, force/mating helpers, MFG helper, Thermal Shock helper, Voltage Surge helper, Reseating default, or public dataclass/API.
- Expected line effect: remove the collector regex/function block and four pure condition helper blocks from the 596-line extractor, projecting the final touched extractor to approximately 494 UTF-8 physical lines including blanks after import/dispatch adjustments. Formal acceptance must use checked-out UTF-8 physical lines including blanks and require the final extractor below 500.
- No blank-line suppression may be used as the line-count strategy.

## Validation Gate

- New helper unit tests for:
  - canonical long-term Damp Heat condition with temperature, RH, duration, and mated note;
  - lowercase/spacing variants;
  - no explicit Damp Heat condition returns `None`;
  - EIA method clauses are not emitted as Condition;
  - generic humidity remains outside Damp Heat helper ownership.
- Extractor integration test for `Long-term damp heat`.
- Existing focused parser regression:
  `py -m pytest tests\unit\test_spec_section_text_extractor.py -q`.
- Existing parser regression is read-only only; do not add new Damp Heat or TASK_365C replay tests to that old module.
- New focused helper regression:
  `py -m pytest tests\unit\test_damp_heat_condition_parser.py tests\unit\test_spec_section_damp_heat_dispatch.py tests\unit\test_condition_text_collectors.py tests\unit\test_spec_section_text_extractor.py -q`.
- `py_compile` for touched parser modules.
- UTF-8 trailing, `git diff --check`, line-count, scope whitelist, staging-empty, and no-real-file/no-real-database scans. The line-count scan must assert final extractor `<500` and `backend/modules/test_plan/condition_text_collectors.py <=150` UTF-8 physical lines including blanks.

## Merge Gate

- Reviewer plan gate pass.
- Explicit user approval before Developer implementation.
- Developer implementation must keep all touched/new Python files under 500 lines without blank-line count suppression.
- Reviewer/QA/Integrator must prove the old 786-line parser test module was not modified and the TASK_365C replay hunk was excluded.
- Reviewer/QA/Integrator must prove hunk isolation from accepted TASK_365A/B/C and all non-parser residuals.

## Definition Of Ready

DoR, Reviewer implementation-readiness, and user implementation approval are satisfied. Implementation is authorized only for the exact May Touch and locked boundaries above.

## Next Legal Role

User/Orchestrator. This closeout does not activate another candidate group.
