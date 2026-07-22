# SPEC_PARSER Damp Heat Residual Package Reconciliation Plan

Date: 2026-07-22

Status: complete / accepted after Integrator package gate

Task: `SPEC_PARSER_DAMP_HEAT_RESIDUAL_PACKAGE_RECONCILIATION`

Lane: `spec-parser-damp-heat-residual-package-reconciliation`

Implementation authorization: authorized for the exact May Touch listed in this plan

## Current Phase / Role / Why Allowed

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current role: Planner final source-of-truth reconciliation, docs-only.
- Why allowed: Reviewer implementation-readiness re-gate passed and User explicitly approved product implementation.
- This reconciliation aligns board/task/plan/Planner evidence for Developer implementation routing. Product/test edits still belong to the next Developer pass.

## Live Repository Facts

- Accepted parser baselines:
  - TASK_365A MFG condition parsing: `13079a37`.
  - TASK_365B PDF/DOCX extraction parity: `a58c96a371a541e97514f424b67d0341e5d01fa3`.
  - TASK_365C Thermal Shock / Voltage Surge parsing: `71203210`.
- Current HEAD is `1cc97408d1532f2a07e4153b4aad5d37ce982755`.
- UTF-8 physical lines including blanks, measured with `(Get-Content <path> -Encoding UTF8).Count` / `ReadAllLines`:
  - current `backend/modules/test_plan/spec_section_text_extractor.py`: `596`;
  - HEAD version of that file: `591`;
  - current `tests/unit/test_spec_section_text_extractor.py`: `786`;
  - HEAD version of that test: `735`.
- Current lane-related dirty hunks remain exactly:
  - extractor: `5/0`, the direct Damp Heat branch;
  - old test: `51/0`, one Damp Heat case plus accepted TASK_365C Thermal Shock / Voltage Surge replay cases.
- Read-only old parser regression currently passes: `52 passed`.
- The index is empty.

The older `527` / `670` facts in Planner governance are superseded historical checkpoints from the non-blank `Measure-Object -Line` count and are no longer the physical-line source of truth in this worktree. The previously approved collector-only extraction would leave the extractor above 500 lines. Future implementation must therefore use the exact expanded mechanical split below; this scope change is now reconciled for Reviewer implementation-readiness.

## Exact Future May Touch

Product paths:

1. `backend/modules/test_plan/spec_section_text_extractor.py`
2. `backend/modules/test_plan/condition_text_collectors.py` (new)
3. `backend/modules/test_plan/damp_heat_condition_parser.py` (new)

Test paths, all new:

4. `tests/unit/test_condition_text_collectors.py`
5. `tests/unit/test_damp_heat_condition_parser.py`
6. `tests/unit/test_spec_section_damp_heat_dispatch.py`

Governance:

- this plan;
- `docs/lane_evidence/SPEC_PARSER_DAMP_HEAT_RESIDUAL_PACKAGE_RECONCILIATION_developer.md`;
- future lane-only task/Planner/Reviewer/board status hunks when the corresponding role is authorized.

Read-only regression dependency:

- `tests/unit/test_spec_section_text_extractor.py`; it must receive no lane hunk. Its dirty Thermal Shock / Voltage Surge replay cases remain excluded.

## Exact Mechanical Extraction

`condition_text_collectors.py` will own source-text condition collection and the small pure condition normalizers that currently make the extractor exceed the hard limit. The move is behavior-preserving: copy bodies and regexes first, rename exports, then update only the listed call sites.

Move these symbols from the extractor and expose the following public names:

- `_CONDITION_TOKEN_RE` -> private `_CONDITION_TOKEN_RE` in the helper;
- `_collect_condition_segments(...)` -> `collect_condition_segments(...)`;
- `_collect_condition_tokens(...)` -> `collect_condition_tokens(...)`;
- `_extract_electrical_condition(...)` -> `extract_electrical_condition(...)`;
- `_extract_temperature_rise_current(...)` -> `extract_temperature_rise_current(...)`;
- `_extract_dust_exposure_condition(...)` -> `extract_dust_exposure_condition(...)`;
- `_extract_durability_condition(...)` -> `extract_durability_condition(...)`.

The helper owns a private whitespace cleaner exactly equivalent to the current `_clean(...)`: replace `\x07` with a space, collapse all whitespace with `\s+`, trim. It must not import the extractor, so no cycle is introduced.

Only these extractor call sites may change:

- DWV and insulation-resistance calls to `extract_electrical_condition(...)`;
- Current Rating / Temperature Rise calls to `extract_temperature_rise_current(...)`;
- Dust Exposure call to `extract_dust_exposure_condition(...)`;
- Durability call to `extract_durability_condition(...)`;
- generic humidity, thermal disturbance, high temperature, vibration, shock, and default-token fallback calls to the public collectors;
- one Damp Heat import and one narrow dispatch call.

Method extraction, Requirement extraction, force/mating functions, Reseating, MFG, Thermal Shock, Voltage Surge, public dataclass, and public extractor entry points remain in their existing ownership.

### Physical-Line Budget

- Current extractor: `596`.
- Exact moved source ranges at the current checkpoint: regex `65-68`, condition functions `313-384`, collectors `521-554`; `110` physical lines before import adjustments.
- New grouped collector imports: budget `8` lines.
- Damp Heat direct five-line body becomes a one-call dispatch; its grouped import consumes the corresponding saved lines.
- Projected final extractor: approximately `494` physical lines, hard gate `<=500` and target `<=495`.
- `condition_text_collectors.py`: budget `<=150`.
- `damp_heat_condition_parser.py`: budget `<=80`.
- each new test module: budget `<=220`.
- B3 current effective budget: `condition_text_collectors.py <=150` UTF-8 physical lines including blanks is the single controlling maximum across task, plan, board, Planner evidence, and reconciliation evidence. Any smaller historical helper target is superseded for this expanded helper.

No blank-line suppression, compressed top-level definitions, or line-count pipeline that drops blank lines may be used.

## Damp Heat Parser Contract

Public API:

```python
def extract_damp_heat_condition(text: str) -> str | None:
    ...
```

The helper is pure and delegates source-faithful segment handling to `collect_condition_segments(...)` with the frozen labels `damp heat condition`, `temperature`, `humidity`, `rh`, `duration`, and `hours`.

Rules:

1. Normalize whitespace only; do not rewrite numeric values or units.
2. Return explicit source condition segments only, joined by the existing `; ` behavior and existing two-segment cap.
3. Exclude segments beginning with `EIA `, containing `in accordance with EIA`, `EIA 364`, or `EIA-364` exactly as the shared collector already does.
4. Return `None` for blank text or when no explicit labeled Damp Heat condition fact survives filtering.
5. Do not infer temperature, RH, duration, mating state, aging result, Method, or Requirement.
6. Malformed or unsupported text is a normal no-match (`None`), not an exception and not a generic parser fallback inside the helper.
7. The extractor dispatches only when normalized `test_item` contains `damp heat`, before generic `humidity`.
8. Generic humidity, MFG, Thermal Shock, Voltage Surge, and default condition-token behavior remain unchanged.

Canonical acceptance example:

```text
Damp Heat Condition: 85℃, 85% RH, 1000h (mated test)
```

## TDD And Implementation Order

1. Add red tests in `test_condition_text_collectors.py` for copied behavior before moving code.
2. Mechanically create `condition_text_collectors.py`, update the exact extractor imports/calls, and run collector plus old read-only regression.
3. Add red pure-parser tests in `test_damp_heat_condition_parser.py`.
4. Implement `extract_damp_heat_condition(...)` without changing shared collector semantics.
5. Add red dispatch/priority tests in `test_spec_section_damp_heat_dispatch.py`.
6. Replace the dirty inline Damp Heat body with the helper call and run all parser regressions.
7. Perform physical-line, diff, trailing, scope, staging, and no-real-file checks.

Exact planned nodes:

- `test_collect_condition_segments_preserves_order_filtering_and_two_segment_cap`
- `test_collect_condition_segments_excludes_eia_method_clauses`
- `test_collect_condition_tokens_preserves_deduplication_cap_and_numeric_a_filter`
- parameterized parity for humidity, thermal disturbance, high temperature, vibration, shock, DWV/IR, Current Rating/Temperature Rise, Dust Exposure, and Durability;
- `test_extract_damp_heat_condition_returns_explicit_temperature_rh_duration`
- `test_extract_damp_heat_condition_normalizes_spacing_without_rewriting_values`
- `test_extract_damp_heat_condition_returns_none_without_explicit_condition_fact`
- `test_extract_damp_heat_condition_excludes_eia_method_segment`
- `test_damp_heat_dispatch_precedes_generic_humidity`
- `test_generic_humidity_does_not_enter_damp_heat_parser`
- `test_damp_heat_dispatch_does_not_infer_missing_method_or_requirement`.

## Validation Commands

```powershell
py -m pytest tests/unit/test_condition_text_collectors.py tests/unit/test_damp_heat_condition_parser.py tests/unit/test_spec_section_damp_heat_dispatch.py tests/unit/test_spec_section_text_extractor.py -q
py -m py_compile backend/modules/test_plan/condition_text_collectors.py backend/modules/test_plan/damp_heat_condition_parser.py backend/modules/test_plan/spec_section_text_extractor.py
git diff --check -- backend/modules/test_plan/spec_section_text_extractor.py backend/modules/test_plan/condition_text_collectors.py backend/modules/test_plan/damp_heat_condition_parser.py tests/unit/test_condition_text_collectors.py tests/unit/test_damp_heat_condition_parser.py tests/unit/test_spec_section_damp_heat_dispatch.py
py -c "from pathlib import Path; limits={Path('backend/modules/test_plan/spec_section_text_extractor.py'):499,Path('backend/modules/test_plan/condition_text_collectors.py'):150,Path('backend/modules/test_plan/damp_heat_condition_parser.py'):80,Path('tests/unit/test_condition_text_collectors.py'):220,Path('tests/unit/test_damp_heat_condition_parser.py'):220,Path('tests/unit/test_spec_section_damp_heat_dispatch.py'):220}; [(print(f'{p}\t{len(p.read_text(encoding=\"utf-8\").splitlines())}\tlimit<={limit}') or (_ for _ in ()).throw(SystemExit(1))) if len(p.read_text(encoding='utf-8').splitlines())>limit else print(f'{p}\t{len(p.read_text(encoding=\"utf-8\").splitlines())}\tlimit<={limit}') for p,limit in limits.items()]"
git diff --name-only --cached
```

The implementation gate also requires a UTF-8 trailing-whitespace scan, exact path whitelist, confirmation that the old 786-line test file has no lane hunk, and confirmation that no real DB/file/public-drive/generated artifact was accessed.

## Locked Paths And Package Isolation

- No changes to TASK_365A MFG, TASK_365B document gateways, TASK_365C Thermal Shock / Voltage Surge helpers, or their accepted tests.
- No changes to Fee/default-fill/rules/seeds, Contact Measurement Summary UI, frontend, API/client/routes, schema/database/repositories, Matrix persistence/confirmation, Settings, LTR, release packaging, `.agents/**`, or `docs/project_management/**`.
- No access to real DB, public-drive files, attachments, source workbooks/specifications, or generated artifacts.
- Do not absorb the old test module's dirty Damp Heat/Thermal Shock/Voltage Surge hunk. Future Damp Heat coverage lives only in the new modules.
- Do not clean, revert, stage, commit, or push unrelated worktree residuals.
- Candidate packaging must use path and hunk whitelists because the extractor already contains an unstaged Damp Heat residual and the worktree contains unrelated Fee/UI/governance changes.

## Rollback

Rollback removes the two new helpers and three new test modules, then restores only the extractor import/call-site/dispatch hunks. There is no database, source document, generated artifact, or authority state rollback.

## Readiness And Next Legal Route

Developer planning-first, Reviewer implementation-readiness re-gate, Developer implementation, QA, and Integrator package isolation are complete, including the B3 line-budget fix and explicit User product implementation approval. The lane is **complete/accepted**. The next legal role is User/Orchestrator; no next candidate group is activated by this closeout.
