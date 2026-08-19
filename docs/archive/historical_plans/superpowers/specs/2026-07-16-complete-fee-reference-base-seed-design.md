# Complete Fee Reference Base Seed Design

Status: approved by user on 2026-07-16

Task: `TASK_362A_COMPLETE_FEE_REFERENCE_BASE_SEED`

Date: 2026-07-16

## 1. Decision

ConnLab will replace the current representative-only fee seed with a new versioned,
complete seed derived from every effective test/report row in:

- source file: `D:\Template\FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls`
- source sheet: `Unit Price Reference`
- source SHA256: `FB788038631AA0A12F1A052B630513718D9FA1BB64BAE647E897E18529EF8A5D`
- effective test/report rows: `4-47` (44 rows)
- global discount policy row: `49`

The design uses two maintained layers plus one compiled runtime artifact:

1. A source-faithful base snapshot containing all workbook facts.
2. A curated extension layer containing reviewed aliases and automation decisions.
3. A compiled, versioned runtime seed consumed by the existing fee-rule loader.

The existing seed remains available for historical traceability. Runtime code will not
open or parse the external workbook.

## 2. Discovery Gate

### Confirmed by the user

- Every effective `Unit Price Reference` row must enter the base fee-rule seed.
- Existing reviewed aliases and business rules must be retained as an extension layer.
- Workbook rows must not overwrite or delete the reviewed extension rules.
- The source authority for this task is the exact workbook path above.

### Confirmed by repository evidence

- The active seed `fee_rules_v2026_06_03.json` contains only representative rules.
- `INSULATION RESISTANCE` currently produces `no_rule_match`.
- TASK_302 already provides structured candidate building, validation, diff, and explicit
  version activation foundations.
- Runtime currently loads a bundled JSON seed through `active_fee_rule_seed.json`.
- The current worktree contains reviewed but not yet packaged fee-rule extensions; those
  changes must be preserved and reconciled, not reset.

### Planner decisions now approved by the user

- Row 49 is source policy metadata, not a test rule.
- Complex, ranged, conditional, or multi-mode prices enter the seed but remain
  `review_required` until a later task implements a proven calculation strategy.
- Existing extension-only rules such as Reseating remain available even when they have no
  one-to-one source row.

### Board reconciliation

The board header said TASK_361L was blocked, while its detailed entry said it was
complete/accepted. TASK_361L is treated as complete/accepted because the detailed entry
records the later Integrator acceptance and validation. TASK_362A is the proposed next
task and remains non-executable until this written design and its implementation plan are
approved.

## 3. Source Coverage

The base snapshot must contain these source families without omission:

| Rows | Family | Source items |
| --- | --- | --- |
| 4-15 | Environmental/aging | High/low temperature life, temperature and humidity, steam aging, thermal shock/cycling, whisker environmental stress, salt spray, MFG IIA/IIIA, dust |
| 16-25 | Dynamic/mechanical | Vibration, two shock modes, vibration plus temperature cycling, micro/nanosecond discontinuity, mechanical force, automotive force, offset durability, cable bending |
| 26-35 | Electrical/durability | Durability, LLCR, DCR, CR, IR, DWV, capacitance/inductance, two temperature-rise modes, current cycling |
| 36-46 | Material/analysis/support | Solderability, solder heat, porosity, SEM/EDS, FTIR, cross section, compressive whisker, hardness, plating thickness, visual exam, PCB/fixture design |
| 47 | Reporting | Report preparation |
| 49 | Global policy | Discount principles; preserved as policy metadata only |

## 4. Data Architecture

### 4.1 Source snapshot layer

Add a versioned JSON snapshot under the fee-evaluation seed area. It records:

- workbook identity and hash;
- source sheet and extraction timestamp;
- exactly 44 source rows;
- source row number;
- English and Chinese descriptions;
- raw base-fee text;
- raw unit-price text;
- applicable standard;
- range/condition text;
- chamber/note text;
- row 49 as a separate global policy record.

Source text is preserved verbatim apart from stable line-ending normalization. The
snapshot is a maintenance artifact and is not loaded during normal Fee Evaluation page
requests.

### 4.2 Curated extension layer

Add a versioned extension JSON keyed by stable rule ID. It records only reviewed ConnLab
decisions:

- English/Chinese/acronym aliases;
- canonical unit label;
- calculation strategy;
- numeric value only where the source is unambiguous;
- review-required classification and reason;
- extension-only rules and their provenance;
- existing user-confirmed rules such as Examination of Product, Reseating, Dust exposure,
  force-family variants, latch variants, LLCR tiers, CR fallback behavior, and the
  temperature-rise current tiers.

The extension layer never replaces raw source text. It may select one deterministic
interpretation only when that interpretation is already approved and testable.

### 4.3 Compiled runtime seed

A deterministic compiler composes the base snapshot and extension layer into a new
`FeeRuleLibrary` JSON file compatible with the existing runtime loader.

Compilation rules:

- every source row 4-47 produces exactly one base runtime rule;
- extension-only rules are appended with explicit extension provenance;
- every runtime rule has a unique stable ID and normalized aliases;
- single-price/single-unit rows may expose numeric defaults;
- tiered, conditional, ranged, or multi-mode rows preserve source text and use
  `manual_required` unless an existing approved evaluator covers them;
- mixed-unit rows use an explicit non-automatic representation instead of selecting a
  misleading unit;
- row 49 is not emitted as a matchable test rule;
- the old seed file is not edited or deleted;
- the active manifest changes only after compile, validation, diff, and regression gates
  pass.

## 5. Runtime Behavior

TASK_362A establishes complete rule coverage and safe partial defaults. It does not try
to automate every price expression.

Examples:

- IR and DWV match their source rules and expose `per reading`; their 1-minute and
  2-minute source prices remain reviewable unless an explicit duration is available to
  an already approved evaluator.
- Low temperature life matches and exposes the source `20/h` rule.
- Whisker, mechanical-force ranges, report-price conditions, and other complex rows match
  a known rule but remain review-required where no single price can be proved.
- Existing Reseating, Dust, force aliases, CR, LLCR, visual, and temperature-rise behavior
  must not regress.

A later `TASK_362B` may add new deterministic evaluators for explicit duration, current,
count, base-fee, or discount conditions. That follow-up cannot invent policy from raw
text.

## 6. Error Handling

Compilation fails without activation when:

- source hash or expected sheet identity differs;
- any source row 4-47 is missing or duplicated;
- an unexpected populated source row appears in the controlled range;
- aliases collide after normalization;
- a rule has an unsupported or misleading unit representation;
- a review-required rule lacks a review reason;
- changed content reuses an existing version ID;
- the compiled seed cannot be reloaded by the production seed loader;
- extension reconciliation would remove an existing reviewed extension rule.

Failure leaves `active_fee_rule_seed.json` unchanged.

## 7. Scope

### May touch in TASK_362A

- fee-rule models/validation only where required for source provenance or safe mixed units;
- TASK_302 candidate/compile/diff helpers or a narrowly named compiler module;
- new source snapshot, extension, and compiled seed JSON files;
- active seed manifest after all gates pass;
- focused fee-rule loader, compiler, matcher, default-fill, and draft-service tests;
- TASK_362A task, plan, evidence, and board files.

### Must not touch

- runtime Excel/COM parsing;
- the external source workbook;
- old seed deletion or in-place rewriting;
- database schema or pricing-draft persistence semantics;
- Fee Evaluation frontend redesign;
- Matrix authority, Matrix parser/import, Point Profile, Measurement Plan, Test Record,
  Report generation, LTR/public-drive workflows, project folders, release, or packaging;
- automatic application of row 49 discounts;
- new speculative calculation formulas for complex rows.

## 8. Validation

Required automated evidence:

- exact source hash and snapshot metadata;
- exactly 44 effective source rows plus one policy record;
- one-to-one source-row-to-base-rule coverage;
- extension-only rule preservation;
- stable serialization and reload;
- candidate diff against the old active seed;
- duplicate ID/alias and missing-row failures;
- activation version guard;
- matcher coverage for all 44 English source descriptions and reviewed aliases;
- focused default-fill checks for IR, DWV, low temperature life, and representative
  deterministic/manual-required rules;
- regression tests for LLCR, CR, Reseating, Dust, force families, visual, report, and
  temperature rise;
- no external workbook mutation and no runtime workbook dependency.

Manual smoke after implementation:

- open Fee Evaluation for a project containing IR/DWV and confirm both rows match known
  rules instead of `no_rule_match`;
- confirm review-required copy is specific when price duration/count is unresolved;
- confirm existing automatically filled rows retain their reviewed values.

## 9. Completion Boundary

TASK_362A is complete only when the new compiled seed is active, all 44 source rows are
traceable, all prior reviewed extensions remain available, focused regressions pass, and
the source workbook remains unchanged. TASK_362B remains a separate, explicitly approved
follow-up for additional calculation automation.
