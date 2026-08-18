# TASK_365A MFG Condition And Fee Duration Plan

## Discovery Gate

### Current Context

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task: TASK_365A is user accepted after Developer implementation
  and focused Reviewer/QA passes; Integrator packaging/readiness is authorized.
- Current role: Integrator controlled package isolation and closeout.
- Why implementation was allowed: the user explicitly approved this reviewed plan
  on 2026-07-19. Product changes stayed within its May Touch boundaries.

### User Goal Restatement

The product specification contains one MFG Class IIA exposure with two explicit
phases: 224 hours unmated and 112 hours mated. Matrix must retain all three facts in
a compact Condition. Fee Evaluation must consume the confirmed Matrix Condition,
sum the two durations, convert 336 hours to 14 days, and use the existing MFG Class
IIA `1000/day` rule without operator re-entry.

### Evidence Read

- `docs/task_board.md`
- `AGENTS.md` and Planner/Task execution protocols
- `backend/modules/test_plan/spec_section_text_extractor.py`
- `backend/modules/fee_evaluation/fee_default_fill.py`
- active MFG Class IIA seed entry and focused parser/Fee tests
- live Matrix evidence for project `ce15026d119f408f80970ea7077f6e41`

### Confirmed By User

- Canonical Matrix facts are Class IIA, unmated 224 hours, and mated 112 hours.
- Fee Units must be `(224 + 112) / 24 = 14 days`.
- The MFG Fee rule is analogous to the existing MFG Class IIA/day rule.

### Confirmed By Repository Evidence

- Generic MFG extraction currently selects at most two broad text segments and can
  retain narrative text while dropping the mated 112-hour phase.
- The active matcher already resolves `MFG` to `fee_rule_mfg_class_iia` with Unit
  Price `1000` and Unit Type `day`.
- `_duration_day_result` recognizes explicit `day/days` only; two labeled hour
  durations currently produce review-required/Pending.
- `spec_section_text_extractor.py` is already above the project file-size hard limit,
  while `fee_default_fill.py` is close to it. New parsing logic must live in small
  focused modules.

### Planner Assumptions

- Both labeled phases are required before automatic summation. One available phase
  is insufficient authority for the total.
- Exact decimal division by 24 is safe; no rounding policy is introduced.
- Existing Matrix confirmation remains the authority boundary. Historical confirmed
  Matrix rows are not silently rewritten.

### Not Yet Confirmed / Explicitly Out Of Scope

- Class IIIA and other MFG standards/duration schedules are not generalized.
- The `<48 hours` Base Fee branch in source reference text is not redesigned.
- Existing confirmed data is not migrated or mutated.
- The separate Current Rating cross-page `EIA-364-70` parser defect is excluded.

### Planning Risk And Decision

The main risk is summing arbitrary hour tokens or accidentally changing unrelated
duration rules. The plan requires labeled unmated/mated phases and dispatches only
for the existing MFG Class IIA rule. Repository evidence and user confirmation are
sufficient for a planned-only lane; no blocking question remains.

## Design

### Authority And Data Flow

```text
Specification 8.2 text
  -> MFG-specific Matrix condition parser
  -> Matrix Condition authority
  -> confirmed Matrix Fee context
  -> MFG-specific labeled-hour parser
  -> (unmated hours + mated hours) / 24
  -> existing 1000/day calculation
```

No API, schema, persistence, or frontend contract changes are needed.

### Parser Contract

Add a small pure helper in `mfg_condition_parser.py`:

```python
def extract_mfg_condition(text: str) -> str | None:
    """Return canonical Class IIA MFG phase details from explicit source facts."""
```

It extracts:

- class: explicit `CLASS IIA`
- unmated phase: explicit `unmated ... 224h`
- mated phase: explicit `mated ... 112h`

When all facts exist, output exactly:

```text
Class IIA; unmated 224 hours; mated 112 hours
```

When facts are incomplete, preserve only source-supported facts for Matrix review;
do not invent the missing phase. `spec_section_text_extractor.py` receives one narrow
MFG dispatch to the helper. Method and Requirement extraction remain in their
existing paths.

### Fee Duration Contract

Add a small pure helper in `mfg_duration.py`:

```python
def resolve_mfg_duration_days(text: str) -> Decimal | None:
    """Return exact planned days from labeled unmated and mated hour phases."""
```

Resolution order:

1. Preserve existing explicit `day/days` handling.
2. Otherwise require both labeled unmated and mated hour values.
3. Sum the two Decimal hours and divide by `Decimal("24")`.
4. Reject absent, non-positive, duplicate/conflicting, or unlabeled hour values by
   returning `None`.

`fee_default_fill._duration_day_result` calls the helper only for
`fee_rule_mfg_class_iia`. Successful 336-hour resolution reuses
`calculated_result` with Unit Price `1000`, Unit Type `day`, Units `14`, Base Fee `0`,
Discount `0`, and Testing Fee `14000`. Failure retains the existing Pending/manual
contract.

## TDD Implementation Sequence

1. Add a red section-extractor test using the exact quoted source prose and assert
   canonical Condition, preserved `EIA-364-65`, and unchanged Requirement behavior.
2. Add focused pure-helper negative cases: missing class, missing unmated phase,
   missing mated phase, unlabeled hours, and conflicting duplicate phase values.
3. Implement `mfg_condition_parser.py` and the one-line family dispatch.
4. Add red Fee tests for canonical 224+112 hours -> 14 days/14000, incomplete
   phases -> Pending, and existing explicit 14 days -> unchanged.
5. Implement `mfg_duration.py` and the narrow Class IIA dispatch.
6. Add one confirmed-Matrix Fee draft regression proving the Matrix Condition reaches
   the Fee result without API/UI changes.
7. Run focused and regression validation, then perform review-checklist and package
   isolation checks.

## File-Level Plan

### New Production Files

- `backend/modules/test_plan/mfg_condition_parser.py`
- `backend/modules/fee_evaluation/mfg_duration.py`

### Narrow Existing-File Changes

- `backend/modules/test_plan/spec_section_text_extractor.py`: replace generic MFG
  segment collection with one helper call.
- `backend/modules/fee_evaluation/fee_default_fill.py`: route Class IIA day resolution
  through the helper while preserving explicit-day behavior.

### Tests

- `tests/unit/test_spec_section_text_extractor.py`
- optional `tests/unit/test_mfg_condition_parser.py` if negative cases would further
  grow the already oversized extractor test file
- `tests/unit/test_fee_default_fill.py`
- optional `tests/unit/test_mfg_duration.py` for pure duration boundaries
- `tests/unit/test_confirmed_matrix_fee_draft_service.py`

## Risks And Controls

- **Narrative over-capture:** dedicated labeled regexes and exact canonical output.
- **Double counting:** require one unambiguous value for each named phase.
- **Unrelated hour capture:** unlabeled hours never enter the MFG sum.
- **Silent authority mutation:** parser affects new imports/previews only; no data migration.
- **Oversized files:** new helpers hold new logic; existing production files receive
  only narrow dispatches.
- **Dirty worktree contamination:** hunk-level review and a strict path whitelist;
  TASK_363C/D and TASK_364B hunks remain excluded.

## Validation Matrix

| Case | Expected Matrix | Expected Fee |
|---|---|---|
| Class IIA + unmated 224h + mated 112h | canonical three-part Condition | 1000/day, Units 14, Base 0, Fee 14000 |
| Explicit `14 days` | unchanged | same existing calculated result |
| Missing mated phase | source-supported partial facts | Units/Fee Pending |
| Missing unmated phase | source-supported partial facts | Units/Fee Pending |
| Two unlabeled hour values | no guessed phase identity | Units/Fee Pending |
| Class IIIA text | no Class IIA auto-path | existing behavior unchanged |
| Other per-day rule | unchanged | existing behavior unchanged |

## Final Package Boundary

The user accepted the reviewed implementation on 2026-07-19. Integrator may package
only the exact MFG helper, dispatch, and focused-test hunks enumerated in the task
Merge Gate and the TASK_365A governance files. Shared production and test files
require hunk-level staging. TASK_365B PDF parity, TASK_365C thermal/surge work,
Current Rating, damp heat, Salt Spray, temperature/default-fill changes, API/schema/
frontend/seed/authority paths, real data/files, and all other residuals remain
excluded. No new implementation or remote push is authorized by this reconciliation.
