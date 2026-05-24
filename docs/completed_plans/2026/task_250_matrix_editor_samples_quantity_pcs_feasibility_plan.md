# TASK_250 Matrix Editor Samples Quantity (PCS) Feasibility Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_250_MATRIX_EDITOR_SAMPLES_QUANTITY_PCS_FEASIBILITY`
- Allowed now: user requested feasibility assessment before implementation.

## Task Understanding

Goal:

- Evaluate whether Matrix Editor should add a final row `Samples Quantity (PCS)` where each group has a required quantity.
- Determine if this can remain frontend-local or must become a structured authoritative field for downstream modules.

Business context:

- This value is required by:
  - test form usage
  - fee calculation
  - report generation

This means long-term authority cannot remain only UI-local string state.

## Key Feasibility Conclusion (Planned)

Feasible, with staged rollout:

1. UI-first controlled prototype is feasible for interaction validation.
2. Production-feasible authoritative path requires structured Matrix draft representation and backend validation.
3. Downstream consumers (fee/report/test-form) should consume typed `samples_quantity_pcs_by_group` data, not ad-hoc row parsing.

## Proposed Data Boundary

Recommended logical field (authoritative target):

- `samples_quantity_pcs_by_group: Record<group_id, int>`

Rationale:

- aligns naturally with per-group columns
- avoids fragile parsing from a generic matrix row string
- supports strict validation and downstream deterministic use

## Validation Rule Recommendation

Per group:

- required
- integer only
- `>= 1`
- optional upper bound if business has cap (defer until confirmed)

Cross-group:

- all existing active groups must have a quantity
- when adding/removing group columns, quantity map must stay synchronized

## MVP Options

Option A (prototype-only, lower immediate cost, higher risk):

- Add fixed final row in Matrix Editor UI.
- Store values in local component state only.
- Show mandatory validation cues.
- No backend persistence.

Risk:

- downstream modules cannot reliably consume it
- user expectation gap if value disappears or is not used by fee/report

Option B (recommended implementation path):

- Add UI row + typed matrix draft field in API/backend.
- Persist and validate server-side.
- Expose to consumers (fee/report/test-form adapters).

Benefit:

- consistent source of truth
- avoids duplicate rules across frontend modules

## Recommended Next Task Split

1. `TASK_251` Frontend interaction slice:
   - add fixed final row in Matrix Editor
   - per-group required integer validation UI
   - no downstream wiring yet

2. `TASK_252` Backend authority slice:
   - extend matrix draft schema/API with typed `samples_quantity_pcs_by_group`
   - backend validation
   - migration/default handling for old drafts

3. `TASK_253` Consumer wiring slice:
   - fee/report/test-form consume authoritative quantities
   - add contract and integration tests

## Risks

- If only Option A is implemented and reused by downstream screens, hidden divergence risk is high.
- If parsing from generic matrix rows is adopted, maintenance and correctness risk increase.
- Group rename/reorder/delete operations must preserve mapping by stable `group_id`, not header display name.

## Output Of This Task

- Feasibility decision and implementation boundary only.
- No code implementation.

## Stop Point

After user approval of this assessment, open implementation task(s) sequentially starting from `TASK_251`.
