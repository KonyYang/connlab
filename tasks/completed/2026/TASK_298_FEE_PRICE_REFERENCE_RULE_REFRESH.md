# TASK_298 Fee Price Reference Rule Refresh

Status: Complete.

Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Allowed reason: TASK_297 is complete, TASK_298 task definition and executable plan were prepared, and the user explicitly approved TASK_298 implementation.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task. TASK_298 is a deterministic, codebase-aware rule-library task: it requires preserving the existing fee-rule model, extending validation carefully, hardening matcher behavior, and adding regression tests. The model must not make business-pricing judgment calls; uncertain source rows must remain review-required.

## Goal

Refresh and harden the fee pricing reference layer so later tasks can default Fee Evaluation editable fields from the reviewed `Unit Price Reference` source.

TASK_298 prepares the rule/default layer only. It does not make the Fee Evaluation table editable and does not export edited values.

## Source Baseline

The current business reference baseline is documented as:

```text
D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls
Sheet: Unit Price Reference
```

Production runtime must not hardcode this absolute path and must not depend on Excel COM to load active rules. Runtime active rules continue to load from bundled JSON via `load_active_fee_rule_library()`.

The optimized template path may be used only as a documented current baseline and in controlled maintenance/manual verification boundaries.

TASK_298 implementation note: the active bundled seed data/version was not replaced because TASK_289 documented that the optimized workbook preserved `Unit Price Reference` unchanged. The active seed therefore intentionally retains the TASK_285 reviewed source snapshot metadata (`Testing Fee Evaluation-Even.xls`, `fee_rules_v2026_06_03`) until a controlled reference-update task creates and reviews a new pricing-rule snapshot.

## Scope

### In Scope

- Fee rule seed schema and validation refinement.
- Active bundled fee rule seed refresh evaluation. If the source reference snapshot is unchanged, retain the current seed and document why.
- Canonical backend unit-label validation.
- Deterministic alias and keyword/contains matching hardening.
- Preservation of numeric recommended `Unit Price` and `Base Fee` values when unambiguous.
- Review-required handling for ambiguous, conditional, ranged, or lab-judgment pricing.
- Unit and regression tests for seed loading, validation, matching, and existing fee draft/export consumers.
- Task-board update after documentation preparation and after any future implementation completion.

### Out Of Scope

- Frontend editable fee cells.
- Frontend local fee calculation.
- Exporting edited values into the Fee Form.
- Fee edit persistence or reload.
- Database migration.
- Rule-maintenance UI.
- New production API endpoint.
- Runtime Excel/COM dependency for active rule loading.
- Matrix Editor changes.
- StepInstance, execution persistence, report generation, AI review, permissions, or multi-user workflow.

## Unit Label Design

TASK_298 must preserve existing behavior and add validation without narrowing currently valid seeds.

Allowed backend canonical `unit_label` values:

```text
sample
reading
cycle
hour
day
photo
specimen
group
contact
time
report
```

Existing compatibility requirements:

- Keep `group` valid for `fixed_per_group`.
- Keep `specimen` valid for `per_specimen`.
- Keep existing calculation strategies unchanged.

`time` is a backend canonical unit label with the business meaning `per occurrence` / `每次`. It does not mean test duration and must not be converted to `hour` or `day`. Source rows that are explicitly billed by duration should continue to use `hour` or `day`.

## Matcher And Status Design

Do not change `FeeRuleMatchStatus`.

Allowed statuses remain:

```text
matched
no_rule_match
```

Required matching order:

1. Exact normalized alias match.
2. Deterministic keyword/contains alias match.
3. Longest or more-specific alias wins.
4. Ties return `status="no_rule_match"`, `review_required=true`, and an ambiguity reason.

Ambiguous matches must not be guessed.

## Required Behavior

- Active fee rule loading remains bundled JSON.
- Active seed metadata remains the TASK_285 reviewed source snapshot when the optimized workbook did not change `Unit Price Reference`.
- Source metadata remains traceable:
  - source file name
  - source sheet
  - source hash
  - `effective_from_basis`
  - created/version id
- `effective_from_basis` remains `project.sample_received_date`.
- Numeric `Unit Price` and `Base Fee` are preserved as structured recommended defaults only when unambiguous.
- Blank, ranged, conditional, or judgment-based pricing remains review-required with source text retained.
- Existing `fixed_per_group` and `per_specimen` behavior must not regress.

## Acceptance Criteria

- TASK_298 executable plan exists and is reviewable.
- Active seed refresh decision is explicit: no new seed version was created because the reference sheet is documented as unchanged.
- `ALLOWED_UNIT_LABELS` design is explicit and preserves `group` / `specimen`.
- `FeeRuleMatchStatus` remains unchanged.
- Ambiguous keyword ties keep the existing no-match/review path.
- Production runtime does not load active rules from Excel or a hardcoded absolute path.
- Tests cover unit-label validation, existing compatibility labels, matcher ambiguity, and fee draft/export regressions.

## Validation Plan

Implementation validation completed:

```powershell
py -m pytest tests/unit/test_fee_rule_seed_loader.py tests/unit/test_fee_rule_matcher.py -q -> 17 passed
py -m pytest tests/unit/test_confirmed_matrix_fee_draft_service.py tests/integration/test_confirmed_matrix_fee_draft_api.py -q -> 12 passed
py -m pytest tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_confirmed_matrix_fee_template_basic_fill_service.py -q -> 16 passed
```

The seed-loader tests explicitly assert that active seed metadata remains the original reviewed `Unit Price Reference` snapshot. Final whitespace validation is recorded in `docs/task_board.md`.

## Stop Point

TASK_298 stops after rule-library validation/matcher implementation and task-board update. Do not implement TASK_299 editable UI until separately approved.
