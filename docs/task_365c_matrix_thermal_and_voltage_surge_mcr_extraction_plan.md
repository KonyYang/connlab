# TASK_365C Matrix Thermal And Voltage Surge MCR Extraction Plan

## Discovery Gate

### Current Context

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package
  controlled foundation.
- Current active task: TASK_365B Developer implementation is complete locally
  and pending focused Reviewer/QA plus user acceptance.
- Parallel residuals: TASK_365A and TASK_364B are also pending their own
  Reviewer/QA and user-acceptance gates.
- Current role: Planner discovery and queued task preparation only.
- Why planning is allowed: the user explicitly asked to formulate a task plan
  from the board and asked whether it can later execute synchronously.

### User Goal Restatement

Matrix should turn explicit environmental and surge specification prose into
compact, report-ready Condition values rather than retaining narrative text or
isolated numeric tokens. Thermal Shock must expose enough structured duration
text for the existing hourly Fee rule to calculate 25 hours. Thermal Shock and
Temperature life use `No damage` as empty-only Requirement defaults. Voltage
surge must preserve Pin scope and the labels attached to `kA` and waveform
values.

### Evidence Read

- `docs/task_board.md`, AGENTS, Planner and lane orchestration protocols
- current TASK_365A/TASK_365B status and shared dirty parser paths
- DOCX and PDF GS-12-2268 source text for sections 8.3 and 8.6
- `spec_section_text_extractor.py`, `mcr_text_normalizer.py`, and
  `method_template_library.py`
- active Thermal Shock Fee seed and `fee_default_fill.py`

### Confirmed By User

- Thermal Shock source facts are Method A, -40 ℃ for 30 minutes, +105 ℃ for
  30 minutes, repeated 25 cycles; hourly Units equal 25 hours.
- Temperature life and Thermal Shock default Requirement are `No damage`.
- Voltage surge Condition must retain `Power Pin`, `Differential Mode 10 kA`,
  `Common Mode 20 kA`, `Waveform 8/20 μs`, and `Signal Pin: Not involved`.
- Pin labels, preceding parameter names, and unit-bearing values are semantic
  bindings rather than independent tokens.

### Confirmed By Repository Evidence

- Current Thermal Shock extraction returns only `repeat 25 cycles`; the Fee
  result remains `Confirm duration` with Units/Testing Fee absent.
- The active Thermal Shock Fee rule already provides `30/hour` and
  `calculation_strategy=per_hour`; no price-seed change is needed.
- Environmental Requirement fallback can be bypassed when incidental section
  prose causes CR family classification.
- Plain `Temperature life` is not included in the current no-damage aliases.
- The generic Condition token pattern does not support `kA` or `μs` and cannot
  preserve Pin/parameter labels.
- TASK_365A currently changes the shared extractor and TASK_365B is the active
  review lane, so TASK_365C product edits cannot start safely yet.

### Planner Assumptions / Bounded Decisions

- TASK_365C derives duration only from explicitly labeled temperature dwell
  pairs and explicit cycles in the same Thermal Shock section.
- This first lane accepts the confirmed Method A shape; other method-specific
  schedules remain unsupported unless they expose the same complete facts.
- Voltage surge Requirement is not inferred.
- Existing confirmed Matrix data is not migrated; behavior applies to a new
  import/reparse.

### Planning Risk And Decision

The main risks are mixing current parser lanes, over-generalizing unit token
capture, and allowing source prose to override Test Item family identity.
TASK_365C is therefore queued as planned-only and serial behind TASK_365A/B
hunk isolation. Definition of Ready is sufficient for plan review, but product
implementation remains unauthorized.

## Design

### Data Flow

```text
Specification section + Matrix Test Item
  -> Test Item family selection
  -> family-specific pure Condition parser
  -> canonical Matrix Condition
  -> empty-only Requirement seed fallback
  -> existing MCR normalization
  -> existing Matrix preview/import path
  -> existing Thermal Shock per-hour Fee consumer
```

No API, schema, persistence, frontend, or Fee seed contract changes are needed.

### Thermal Shock Parser

Add a small pure helper:

```python
def extract_thermal_shock_condition(text: str) -> str | None:
    """Return canonical Method A temperature, dwell, cycle, and duration facts."""
```

It extracts one method token, two ordered temperature/dwell pairs, and one
cycle count. Exact Decimal arithmetic converts the dwell sum to hours. Output
includes `total N hours` only when every required fact is unambiguous. Missing
facts produce source-supported partial output or `None`; they never create an
invented duration.

### Voltage Surge Parser

Add a second pure helper:

```python
def extract_voltage_surge_condition(text: str) -> str | None:
    """Return canonical Pin-scoped surge mode and waveform facts."""
```

It recognizes the `Power Pin` block, Differential/Common Mode labels and `kA`
values, the Waveform label and microsecond ratio, and the `Signal Pin` state.
Canonical output is emitted only from label-bound values. The implementation
does not widen the generic token regex.

### Requirement Seeds

Use the existing curated method-template fallback library to express:

```text
Thermal Shock aliases -> fallback Requirement: No damage
Temperature life aliases -> fallback Requirement: No damage
fill policy -> existing empty-only behavior
```

If MCR family normalization still overrides these due incidental source prose,
add one narrow Test Item-first precedence correction. Do not change unrelated
CR/LLCR normalization.

### Fee Compatibility

No Fee production or seed change is planned. The canonical Thermal Shock
Condition ends in `total 25 hours`, so the existing hour parser resolves Units
`25`; the existing active seed supplies Unit Price `30/hour`, yielding Base Fee
`0` and Testing Fee `750`.

## TDD Sequence

1. Add red pure-helper tests for the exact Thermal Shock source, incomplete
   dwell/cycle facts, duplicate conflicts, and Decimal duration formatting.
2. Implement the Thermal Shock helper without touching Fee code.
3. Add red tests for Thermal Shock/Temperature life empty Requirement defaults,
   explicit Requirement preservation, and incidental CR prose.
4. Add the narrow template seeds and only the necessary precedence correction.
5. Add red Voltage surge helper tests for exact source, unit variants,
   missing labels, conflicting values, and detached-token rejection.
6. Implement the Voltage surge helper and narrow extractor dispatch.
7. Add one existing Fee default-fill compatibility test for canonical `25 hours`.
8. Run focused parser/MCR/Fee suites and package-isolation gates.

## File-Level Plan

### New Production Files

- `backend/modules/test_plan/thermal_shock_condition_parser.py`
- `backend/modules/test_plan/voltage_surge_condition_parser.py`

### Narrow Existing-File Changes

- `backend/modules/test_plan/spec_section_text_extractor.py`: two family dispatches
- `backend/modules/test_plan/method_template_library.py`: two empty-only
  Requirement fallback entries
- `backend/modules/test_plan/mcr_text_normalizer.py`: only if required for
  Test Item-first precedence

### Tests

- new focused pure-helper test files preferred to avoid growing oversized files
- existing extractor/parser/method-template/MCR tests only for public-path cases
- one focused Fee default-fill compatibility assertion; no Fee production edit

## Risks And Controls

- **Cross-lane contamination:** do not implement before TASK_365A/B parser hunks
  are dispositioned; use strict hunk/path isolation.
- **Duration overclaim:** require all explicit dwell/cycle facts and exclude
  unstated transfer time.
- **Unit false positives:** retain label binding; never widen generic token capture.
- **Family misclassification:** Test Item family outranks incidental source prose.
- **Default overwrite:** existing explicit Requirement always wins.
- **Oversized extractor:** place parsing in new modules and add dispatches only.
- **Authority mutation:** no migration or real-data write.

## Validation Matrix

| Case | Expected Condition / Requirement | Fee |
|---|---|---|
| Method A, -40/30 min, +105/30 min, 25 cycles | canonical Condition ending `total 25 hours`; `No damage` if Requirement empty | 30/hour, Units 25, Base 0, Fee 750 |
| Thermal Shock with incidental contact-resistance prose | remains Thermal Shock; empty Requirement -> `No damage` | unchanged hourly rule |
| Temperature life with empty Requirement | `No damage` | unchanged |
| Explicit environmental Requirement | preserved | unchanged |
| Complete Power Pin surge facts | canonical Pin-scoped surge Condition | not applicable |
| Detached `20 kA` or `8/20 μs` without labels | no guessed canonical Condition | not applicable |
| Missing Signal Pin state | source-supported partial/reviewable result | not applicable |

## Approval And Orchestration Boundary

This plan authorizes no product code. After TASK_365A/B shared parser hunks are
isolated, the legal sequence is Reviewer plan gate -> explicit user approval ->
Developer -> Reviewer -> QA -> Integrator. The same conversation may orchestrate
those roles synchronously, but it must stop at the approval gate first.
