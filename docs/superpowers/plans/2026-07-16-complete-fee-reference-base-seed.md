# Complete Fee Reference Base Seed Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and activate a complete, versioned Fee Evaluation rule seed covering all 44 effective `Unit Price Reference` rows while preserving existing reviewed ConnLab extensions.

**Architecture:** A source-faithful JSON snapshot stores workbook facts, a curated extension JSON stores reviewed aliases and automation decisions, and a deterministic compiler produces the existing runtime `FeeRuleLibrary` JSON shape. Normal Fee Evaluation requests continue loading only the compiled bundled seed; the external `.xls` file is never a runtime dependency.

**Tech Stack:** Python 3.11+, dataclasses, `Decimal`, JSON, pytest, existing ConnLab fee-rule loader/matcher/default-fill modules.

## Global Constraints

- Source workbook: `D:\Template\FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls`.
- Source sheet: `Unit Price Reference`.
- Source SHA256: `FB788038631AA0A12F1A052B630513718D9FA1BB64BAE647E897E18529EF8A5D`.
- Source coverage is exactly rows `4-47` plus policy row `49`.
- Old seed `fee_rules_v2026_06_03.json` is immutable for this task, including its current working-tree edits.
- No runtime Excel/COM parsing, no external workbook write, no database migration, and no frontend redesign.
- Complex, ranged, conditional, or mixed-mode prices remain `review_required` unless an existing approved evaluator covers them.
- Row 49 is policy metadata only; TASK_362A does not calculate discounts from it.
- Before editing any already-dirty file, record its existing diff and preserve those changes; stage only TASK_362A hunks and never use a whole-file restore to separate work.
- Python files must remain below the 500-line hard limit and should target less than 300 lines.
- Every Python function added by this task has typing and a concise docstring.

---

## File Map

### New production/maintenance files

- `backend/modules/fee_evaluation/fee_reference_snapshot.py`
  - typed source snapshot and policy models;
  - strict JSON loading and row/hash validation.
- `backend/modules/fee_evaluation/fee_rule_extensions.py`
  - typed source-row mappings and extension-only rule loading;
  - validates one mapping per source row.
- `backend/modules/fee_evaluation/fee_rule_seed_compiler.py`
  - composes snapshot plus extensions into `FeeRuleLibrary`;
  - writes deterministic compiled seed artifacts only when explicitly called.
- `backend/modules/fee_evaluation/seeds/fee_reference_rows_v2026_07_16.json`
  - source-faithful rows 4-47 and policy row 49.
- `backend/modules/fee_evaluation/seeds/fee_rule_extensions_v2026_07_16.json`
  - reviewed mappings, aliases, numeric interpretations, and extension-only rules.
- `backend/modules/fee_evaluation/seeds/fee_rules_v2026_07_16.json`
  - compiled runtime seed.

### Existing files modified

- `backend/modules/fee_evaluation/fee_rule_models.py`
  - add backward-compatible optional source provenance.
- `backend/modules/fee_evaluation/fee_rule_candidate_builder.py`
  - carry provenance through candidate construction and serialization.
- `backend/modules/fee_evaluation/fee_rule_seed_loader.py`
  - load optional provenance while preserving old seeds.
- `backend/modules/fee_evaluation/fee_rule_library_diff.py`
  - include provenance in controlled diffs.
- `backend/modules/fee_evaluation/__init__.py`
  - export the new maintenance interfaces.
- `backend/modules/fee_evaluation/seeds/active_fee_rule_seed.json`
  - switch to the new seed only after all pre-activation tests pass.
- `tests/unit/test_fee_rule_seed_loader.py`
  - assert new active metadata and backward compatibility.
- `tests/unit/test_fee_rule_matcher.py`
  - assert all 44 source English names match and reviewed aliases remain.
- `tests/unit/test_fee_default_fill.py`
  - assert IR/DWV partial defaults and protected existing behavior.
- `tests/unit/test_confirmed_matrix_fee_draft_service.py`
  - assert Matrix rows receive known rules rather than `no_rule_match`.
- `tasks/TASK_362A_COMPLETE_FEE_REFERENCE_BASE_SEED.md`
  - implementation state and final evidence.
- `docs/task_board.md`
  - activation and closeout only after implementation gates pass.

### New tests

- `tests/unit/test_fee_reference_snapshot.py`
- `tests/unit/test_fee_rule_extensions.py`
- `tests/unit/test_fee_rule_seed_compiler.py`

---

### Task 1: Source Snapshot Model And Strict Loader

**Files:**
- Create: `backend/modules/fee_evaluation/fee_reference_snapshot.py`
- Create: `tests/unit/test_fee_reference_snapshot.py`

**Interfaces:**
- Produces: `FeeReferenceSource`, `FeeReferenceRow`, `FeeReferencePolicy`, `FeeReferenceSnapshot`.
- Produces: `load_fee_reference_snapshot(path: Path) -> FeeReferenceSnapshot`.
- Consumes: no workbook or COM object; JSON files only.

- [ ] **Step 1: Write the failing happy-path test**

```python
def test_load_fee_reference_snapshot_requires_exact_authority_rows(tmp_path: Path) -> None:
    path = _write_snapshot(tmp_path, rows=_rows(4, 47), policies=[_policy(49)])

    snapshot = load_fee_reference_snapshot(path)

    assert snapshot.source.source_file_name == "FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls"
    assert snapshot.source.source_sheet == "Unit Price Reference"
    assert snapshot.source.source_hash == (
        "sha256:fb788038631aa0a12f1a052b630513718d9fa1bb64bae647e897e18529ef8a5d"
    )
    assert tuple(row.source_row for row in snapshot.rows) == tuple(range(4, 48))
    assert tuple(policy.source_row for policy in snapshot.policies) == (49,)
```

- [ ] **Step 2: Write failing invalid-shape tests**

```python
@pytest.mark.parametrize(
    ("rows", "message"),
    [
        (_rows(5, 47), "Missing effective source rows: 4"),
        (_rows(4, 47) + [_row(47)], "Duplicate source row: 47"),
        (_rows(4, 48), "Unexpected effective source rows: 48"),
    ],
)
def test_load_fee_reference_snapshot_rejects_invalid_row_coverage(
    tmp_path: Path,
    rows: list[dict[str, object]],
    message: str,
) -> None:
    path = _write_snapshot(tmp_path, rows=rows, policies=[_policy(49)])

    with pytest.raises(FeeReferenceSnapshotValidationError, match=message):
        load_fee_reference_snapshot(path)
```

- [ ] **Step 3: Run the tests and verify the expected import failure**

Run:

```powershell
py -m pytest tests/unit/test_fee_reference_snapshot.py -q
```

Expected: collection fails because `fee_reference_snapshot` does not exist.

- [ ] **Step 4: Implement the typed snapshot and loader**

```python
EXPECTED_EFFECTIVE_ROWS = frozenset(range(4, 48))
EXPECTED_POLICY_ROWS = frozenset({49})


@dataclass(frozen=True, slots=True)
class FeeReferenceSource:
    source_file_name: str
    source_sheet: str
    source_hash: str
    captured_at: str


@dataclass(frozen=True, slots=True)
class FeeReferenceRow:
    source_row: int
    english_description: str
    chinese_description: str
    base_fee_text: str
    unit_price_text: str
    applicable_standard: str
    range_condition: str
    chamber_or_note: str


@dataclass(frozen=True, slots=True)
class FeeReferencePolicy:
    source_row: int
    policy_type: str
    text: str


@dataclass(frozen=True, slots=True)
class FeeReferenceSnapshot:
    source: FeeReferenceSource
    rows: tuple[FeeReferenceRow, ...]
    policies: tuple[FeeReferencePolicy, ...]


def load_fee_reference_snapshot(path: Path) -> FeeReferenceSnapshot:
    """Load and strictly validate one reviewed Unit Price Reference snapshot."""
```

Validation must require the exact filename, sheet name, normalized SHA256 value, rows
4-47, policy row 49, non-empty English descriptions, and unique row numbers. It must not
open the workbook or inspect the filesystem outside the supplied JSON path.

- [ ] **Step 5: Run the focused tests**

Run:

```powershell
py -m pytest tests/unit/test_fee_reference_snapshot.py -q
```

Expected: all snapshot tests pass.

- [ ] **Step 6: Commit the independently testable loader**

```powershell
git add backend/modules/fee_evaluation/fee_reference_snapshot.py tests/unit/test_fee_reference_snapshot.py
git commit -m "feat(fee): add strict fee reference snapshot loader"
```

---

### Task 2: Curated Extension Layer Loader

**Files:**
- Create: `backend/modules/fee_evaluation/fee_rule_extensions.py`
- Create: `tests/unit/test_fee_rule_extensions.py`

**Interfaces:**
- Consumes: `CalculationStrategy`, `FeeRule`, and `FeeRuleVersion`.
- Produces: `FeeSourceRuleExtension`, `FeeRuleExtensionSet`.
- Produces: `load_fee_rule_extensions(path: Path) -> FeeRuleExtensionSet`.

- [ ] **Step 1: Write failing exact-coverage and extension-preservation tests**

```python
def test_extension_loader_requires_one_mapping_for_every_source_row(tmp_path: Path) -> None:
    path = _write_extensions(tmp_path, source_rules=_source_rules(4, 47))

    extensions = load_fee_rule_extensions(path)

    assert tuple(item.source_row for item in extensions.source_rules) == tuple(range(4, 48))
    assert "fee_rule_reseating" in {rule.rule_id for rule in extensions.extension_rules}


def test_extension_loader_rejects_missing_source_mapping(tmp_path: Path) -> None:
    path = _write_extensions(tmp_path, source_rules=_source_rules(5, 47))

    with pytest.raises(FeeRuleExtensionValidationError, match="Missing source mappings: 4"):
        load_fee_rule_extensions(path)
```

- [ ] **Step 2: Write failing duplicate rule ID and invalid review tests**

```python
def test_extension_loader_rejects_duplicate_rule_ids(tmp_path: Path) -> None:
    mappings = _source_rules(4, 47)
    mappings[1]["rule_id"] = mappings[0]["rule_id"]
    path = _write_extensions(tmp_path, source_rules=mappings)

    with pytest.raises(FeeRuleExtensionValidationError, match="Duplicate rule_id"):
        load_fee_rule_extensions(path)


def test_extension_loader_requires_reason_for_manual_rule(tmp_path: Path) -> None:
    mappings = _source_rules(4, 47)
    mappings[0].update(review_required=True, review_reason=None)
    path = _write_extensions(tmp_path, source_rules=mappings)

    with pytest.raises(FeeRuleExtensionValidationError, match="review_reason"):
        load_fee_rule_extensions(path)
```

- [ ] **Step 3: Run tests and verify they fail because the loader is absent**

Run:

```powershell
py -m pytest tests/unit/test_fee_rule_extensions.py -q
```

Expected: collection fails on the missing module.

- [ ] **Step 4: Implement the extension models and loader**

```python
@dataclass(frozen=True, slots=True)
class FeeSourceRuleExtension:
    source_row: int
    rule_id: str
    aliases: tuple[str, ...]
    base_fee_amount: Decimal | None
    unit_price_amount: Decimal | None
    unit_label: str
    calculation_strategy: CalculationStrategy
    review_required: bool
    review_reason: str | None


@dataclass(frozen=True, slots=True)
class FeeRuleExtensionSet:
    version: FeeRuleVersion
    source_rules: tuple[FeeSourceRuleExtension, ...]
    extension_rules: tuple[FeeRule, ...]


def load_fee_rule_extensions(path: Path) -> FeeRuleExtensionSet:
    """Load reviewed source mappings and extension-only fee rules."""
```

The loader must enforce exact source-row coverage, unique source rows, unique rule IDs
across both sections, supported strategies and units, normalized alias uniqueness, and a
review reason for every review-required entry.

- [ ] **Step 5: Run focused tests**

Run:

```powershell
py -m pytest tests/unit/test_fee_rule_extensions.py -q
```

Expected: all extension-loader tests pass.

- [ ] **Step 6: Commit the extension loader**

```powershell
git add backend/modules/fee_evaluation/fee_rule_extensions.py tests/unit/test_fee_rule_extensions.py
git commit -m "feat(fee): add reviewed fee rule extension layer"
```

---

### Task 3: Backward-Compatible Provenance And Deterministic Compiler

**Files:**
- Modify: `backend/modules/fee_evaluation/fee_rule_models.py`
- Modify: `backend/modules/fee_evaluation/fee_rule_candidate_builder.py`
- Modify: `backend/modules/fee_evaluation/fee_rule_seed_loader.py`
- Modify: `backend/modules/fee_evaluation/fee_rule_library_diff.py`
- Modify: `backend/modules/fee_evaluation/__init__.py`
- Create: `backend/modules/fee_evaluation/fee_rule_seed_compiler.py`
- Create: `tests/unit/test_fee_rule_seed_compiler.py`
- Modify: `tests/unit/test_fee_rule_candidate_builder.py`
- Modify: `tests/unit/test_fee_rule_seed_loader.py`
- Modify: `tests/unit/test_fee_rule_library_diff.py`

**Interfaces:**
- Consumes: `FeeReferenceSnapshot`, `FeeRuleExtensionSet`.
- Produces: `compile_fee_rule_library(snapshot, extensions) -> FeeRuleLibrary`.
- Produces: `compile_fee_rule_seed_files(snapshot_path, extensions_path, output_path) -> FeeRuleLibrary`.
- `FeeRule` gains optional `source_kind` and `source_row` fields with backward-compatible defaults.

- [ ] **Step 1: Write failing provenance compatibility tests**

```python
def test_old_seed_loads_with_backward_compatible_provenance_defaults() -> None:
    library = load_fee_rule_library(SEEDS / "fee_rules_v2026_06_03.json")

    assert all(rule.source_kind == "legacy_seed" for rule in library.rules)
    assert all(rule.source_row is None for rule in library.rules)


def test_candidate_serialization_preserves_source_provenance() -> None:
    row = _candidate_row(
        "fee_rule_ir",
        source_kind="unit_price_reference",
        source_row=30,
    )
    library = build_fee_rule_library_candidate(version=_version("fee_rules_v2026_07_16"), rows=(row,))

    payload = json.loads(fee_rule_library_to_seed_json(library))

    assert payload["rules"][0]["source_kind"] == "unit_price_reference"
    assert payload["rules"][0]["source_row"] == 30
```

- [ ] **Step 2: Write failing compiler tests**

```python
def test_compiler_creates_one_base_rule_per_source_row() -> None:
    library = compile_fee_rule_library(_snapshot(), _extensions())

    base_rules = [rule for rule in library.rules if rule.source_kind == "unit_price_reference"]
    assert tuple(rule.source_row for rule in base_rules) == tuple(range(4, 48))
    assert len(base_rules) == 44


def test_compiler_uses_raw_source_text_and_reviewed_numeric_values() -> None:
    library = compile_fee_rule_library(_snapshot(), _extensions())
    ir = next(rule for rule in library.rules if rule.rule_id == "fee_rule_insulation_resistance")

    assert ir.source_row == 30
    assert ir.base_fee.text == "（100~300）\n基于样品准备状况决定"
    assert ir.unit_price.text == (
        "测试规格为1分钟/reading: 5/reading\n测试规格为2分钟/reading: 10/reading"
    )
    assert ir.unit_label == "reading"
    assert ir.unit_price.amount is None
    assert ir.review_required is True
```

- [ ] **Step 3: Write failing mismatch and no-write tests**

```python
def test_compiler_rejects_snapshot_extension_version_mismatch() -> None:
    extensions = replace(_extensions(), version=_version(source_hash="sha256:" + "0" * 64))

    with pytest.raises(FeeRuleCompileError, match="source hash"):
        compile_fee_rule_library(_snapshot(), extensions)


def test_compile_file_does_not_replace_output_when_validation_fails(tmp_path: Path) -> None:
    output = tmp_path / "candidate.json"
    output.write_text("preserve-me", encoding="utf-8")

    with pytest.raises(FeeRuleCompileError):
        compile_fee_rule_seed_files(_bad_snapshot_path(tmp_path), _extensions_path(tmp_path), output)

    assert output.read_text(encoding="utf-8") == "preserve-me"
```

- [ ] **Step 4: Run tests and verify expected failures**

Run:

```powershell
py -m pytest tests/unit/test_fee_rule_seed_compiler.py tests/unit/test_fee_rule_candidate_builder.py tests/unit/test_fee_rule_seed_loader.py tests/unit/test_fee_rule_library_diff.py -q
```

Expected: failures identify missing provenance fields/compiler behavior.

- [ ] **Step 5: Add backward-compatible provenance**

```python
FeeRuleSourceKind = Literal["legacy_seed", "unit_price_reference", "reviewed_extension"]


@dataclass(frozen=True, slots=True)
class FeeRule:
    # Existing fields remain unchanged and in the same order.
    source_kind: FeeRuleSourceKind = "legacy_seed"
    source_row: int | None = None
```

`FeeReferenceCandidateRow` receives the same fields and defaults. The seed loader treats
missing fields as legacy defaults. Serialization always writes the explicit fields for
new seeds. The diff reports changes to `source_kind` and `source_row`.

- [ ] **Step 6: Implement deterministic compilation**

```python
def compile_fee_rule_library(
    snapshot: FeeReferenceSnapshot,
    extensions: FeeRuleExtensionSet,
) -> FeeRuleLibrary:
    """Compile source facts and reviewed extensions into one validated library."""


def compile_fee_rule_seed_files(
    snapshot_path: Path,
    extensions_path: Path,
    output_path: Path,
) -> FeeRuleLibrary:
    """Compile validated JSON inputs and atomically replace the requested output file."""
```

Compilation must:

- compare source filename, sheet, and hash with `extensions.version`;
- pair each source row with exactly one reviewed mapping;
- build aliases from English description, non-empty Chinese description, and reviewed
  aliases while preserving order and removing only exact normalized duplicates;
- use raw source base-fee/unit-price text and reviewed numeric amounts;
- append extension-only rules with `source_kind="reviewed_extension"`;
- call existing seed validation before returning;
- write through a sibling temporary file and `Path.replace()` only after validation.

- [ ] **Step 7: Run compiler and compatibility tests**

Run:

```powershell
py -m pytest tests/unit/test_fee_rule_seed_compiler.py tests/unit/test_fee_rule_candidate_builder.py tests/unit/test_fee_rule_seed_loader.py tests/unit/test_fee_rule_library_diff.py -q
```

Expected: all focused compiler/compatibility tests pass.

- [ ] **Step 8: Check file sizes before commit**

Run:

```powershell
Get-ChildItem backend/modules/fee_evaluation/*.py | ForEach-Object {
  [pscustomobject]@{ File = $_.Name; Lines = (Get-Content $_.FullName -Encoding UTF8).Count }
} | Where-Object { $_.Lines -ge 500 }
```

Expected: no output.

- [ ] **Step 9: Commit compiler and provenance support**

```powershell
git add backend/modules/fee_evaluation/fee_rule_models.py backend/modules/fee_evaluation/fee_rule_candidate_builder.py backend/modules/fee_evaluation/fee_rule_seed_loader.py backend/modules/fee_evaluation/fee_rule_library_diff.py backend/modules/fee_evaluation/fee_rule_seed_compiler.py backend/modules/fee_evaluation/__init__.py tests/unit/test_fee_rule_seed_compiler.py tests/unit/test_fee_rule_candidate_builder.py tests/unit/test_fee_rule_seed_loader.py tests/unit/test_fee_rule_library_diff.py
git commit -m "feat(fee): compile traceable fee reference seeds"
```

---

### Task 4: Encode All 44 Source Rows And Reviewed Extensions

**Files:**
- Create: `backend/modules/fee_evaluation/seeds/fee_reference_rows_v2026_07_16.json`
- Create: `backend/modules/fee_evaluation/seeds/fee_rule_extensions_v2026_07_16.json`
- Modify: `tests/unit/test_fee_reference_snapshot.py`
- Modify: `tests/unit/test_fee_rule_extensions.py`
- Modify: `tests/unit/test_fee_rule_seed_compiler.py`

**Interfaces:**
- Consumes: the exact workbook facts already captured from `Unit Price Reference!B4:H49`.
- Produces: complete source snapshot and reviewed extension inputs for the compiler.

- [ ] **Step 1: Add failing production-artifact coverage tests**

```python
SEEDS = Path("backend/modules/fee_evaluation/seeds")


def test_production_snapshot_has_exact_source_coverage() -> None:
    snapshot = load_fee_reference_snapshot(SEEDS / "fee_reference_rows_v2026_07_16.json")

    assert len(snapshot.rows) == 44
    assert tuple(row.source_row for row in snapshot.rows) == tuple(range(4, 48))
    assert snapshot.policies[0].source_row == 49


def test_production_extensions_cover_source_and_protect_reviewed_rules() -> None:
    extensions = load_fee_rule_extensions(SEEDS / "fee_rule_extensions_v2026_07_16.json")
    protected = {
        "fee_rule_sample_preparation",
        "fee_rule_reseating",
        "fee_rule_dust_benign",
        "fee_rule_mechanical_force",
        "fee_rule_contact_resistance_specified_current",
        "fee_rule_visual_exam",
        "fee_rule_temperature_rise",
        "fee_rule_report_preparation",
    }

    all_ids = {item.rule_id for item in extensions.source_rules} | {
        rule.rule_id for rule in extensions.extension_rules
    }
    assert protected <= all_ids
```

- [ ] **Step 2: Run tests and verify missing-artifact failures**

Run:

```powershell
py -m pytest tests/unit/test_fee_reference_snapshot.py tests/unit/test_fee_rule_extensions.py tests/unit/test_fee_rule_seed_compiler.py -q
```

Expected: production artifact tests fail because the two JSON files do not exist.

- [ ] **Step 3: Encode the source snapshot exactly**

The snapshot must include these one-to-one row identities:

```text
4 high temperature life
5 Low temperature life
6 Temperature & Humidity
7 Steam aging
8 Thermal shock
9 Thermal cycling (Ramp rating 3.5C/min)
10 Thermal cycling (Ramp rating 5C/min)
11 Whisker testing (Environmental stress)
12 Salt spray (NSS)
13 MFG (Class IIA)
14 MFG (Class IIIA) / VW75174 TG19
15 Dust (Benign)
16 Vibration
17 Shock (half sine)
18 Shock (Trapzoidal)
19 Vibration + Temp cycling
20 Microsecond discontinuity
21 Nanosecond dicontinuity
22 Mechanical force
23 Automotive connector Mechanical force
24 Offset durability
25 Cable bending
26 Durability
27 LLCR
28 DCR
29 Contact resistance (CR)
30 Insulation Resistance (IR)
31 Dielectric withstanding voltage (DWV)
32 Capacitance/Inductance
33 Temperature rise
34 Temperature rise with thermography
35 Current cycling (Current ON and OFF)
36 Solderability
37 Resistance to solder heat
38 Porosity
39 SEM/EDS analysis
40 FTIR analysis
41 Cross section
42 Compressive Whisker (Mechanical Stress)
43 Hardness Testing
44 Plating Thickness Measuring
45 Visual exam
46 PCB and test fixture design
47 Report preparation
```

For each row, transcribe columns B-H exactly into the snapshot schema. Store row 49 as:

```json
{
  "source_row": 49,
  "policy_type": "discount_principles",
  "text": "对于价格的打折， 请执行以下的原则：\n1. 对于仅仅是单项的总金额比较低的测试， 原则上不打折；\n2. 对于总金额比较大，但样品数量比较多或样品尺寸比较大的或测试条件独特不可并箱测试的， 原则上不额外给予折扣 ；\n3. 虽然金额比较大， 但测试条件相同， 样品数量和外形都比较小， 实验室方便并箱测试的， 可给予最多额外40%的折扣；\n4. 同意申请者或同一Site相同的产品， 但不同的配置同时安排测试， 如环境测试并箱执行，可以基于项目的数量给与相应的折扣， 比如4个项目同时执行， 可给予最多70%的折扣\n5. 虽然金额比较大且测试条件相同，但外形尺寸相对较大（如HSIO的Cable assembly）并箱会减少其它并箱样品的数量，可给予额外20%的折扣.\n"
}
```

Preserve that source text verbatim, including the source workbook's punctuation and wording.
Tests must reject an empty, abbreviated, or normalized replacement value.

- [ ] **Step 4: Encode reviewed source mappings**

Use these stable rule IDs for rows 4-47:

```text
4 fee_rule_high_temperature_life
5 fee_rule_low_temperature_life
6 fee_rule_temperature_humidity
7 fee_rule_steam_aging
8 fee_rule_thermal_shock
9 fee_rule_thermal_cycling_3_5c
10 fee_rule_thermal_cycling_5c
11 fee_rule_whisker_environmental
12 fee_rule_salt_spray_nss
13 fee_rule_mfg_class_iia
14 fee_rule_mfg_class_iiia
15 fee_rule_dust_benign
16 fee_rule_vibration
17 fee_rule_shock_half_sine
18 fee_rule_shock_trapezoidal
19 fee_rule_vibration_temperature_cycling
20 fee_rule_microsecond_discontinuity
21 fee_rule_nanosecond_discontinuity
22 fee_rule_mechanical_force
23 fee_rule_automotive_mechanical_force
24 fee_rule_offset_durability
25 fee_rule_cable_bending
26 fee_rule_durability
27 fee_rule_llcr
28 fee_rule_dcr
29 fee_rule_contact_resistance_specified_current
30 fee_rule_insulation_resistance
31 fee_rule_dielectric_withstanding_voltage
32 fee_rule_capacitance_inductance
33 fee_rule_temperature_rise
34 fee_rule_temperature_rise_thermography
35 fee_rule_current_cycling
36 fee_rule_solderability
37 fee_rule_resistance_to_solder_heat
38 fee_rule_porosity
39 fee_rule_sem_eds
40 fee_rule_ftir
41 fee_rule_cross_section
42 fee_rule_compressive_whisker
43 fee_rule_hardness_testing
44 fee_rule_plating_thickness
45 fee_rule_visual_exam
46 fee_rule_pcb_fixture_design
47 fee_rule_report_preparation
```

Rules 30 and 31 must use `unit_label="reading"`, `unit_price_amount=null`,
`calculation_strategy="manual_required"`, and a review reason that asks the operator to
confirm the 1-minute/2-minute price. Single-price source rows may carry a numeric amount.
Conditional base-fee text remains raw with `base_fee_amount=null` unless an existing
approved extension behavior already provides the value.

- [ ] **Step 5: Preserve extension-only and reviewed alias behavior**

The extension file must explicitly preserve:

```text
Sample preparation -> 50/sample, Matrix group sample quantity, 100% discount
Examination of Product -> Visual exam alias, 10/photo, Units 3, 100% discount
Reseating -> 2/cycle, sample quantity x parsed cycles, default 3 cycles
Dust exposure and Dust -> Dust (Benign)
Normal/Terminal/Floater/Side force -> Mechanical force per-reading path
Mating/Un-mating and latch variants -> Mechanical force 50/sample path
Contact Resistance, Specified Current -> CR rule and reviewed 10/reading fallback
Temperature Rise and T-rise -> reviewed current tiers
Report preparation -> existing 600/report, Units 1, Man-hour 4, 100% discount
```

Do not edit or stage `fee_rules_v2026_06_03.json`. Read it only to reconcile the current
working-tree aliases and values into the new extension file.

- [ ] **Step 6: Run artifact coverage tests**

Run:

```powershell
py -m pytest tests/unit/test_fee_reference_snapshot.py tests/unit/test_fee_rule_extensions.py tests/unit/test_fee_rule_seed_compiler.py -q
```

Expected: all artifact and compiler tests pass.

- [ ] **Step 7: Verify the workbook hash remains unchanged**

Run:

```powershell
Get-FileHash -LiteralPath 'D:\Template\FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls' -Algorithm SHA256
```

Expected hash: `FB788038631AA0A12F1A052B630513718D9FA1BB64BAE647E897E18529EF8A5D`.

- [ ] **Step 8: Commit only the new source/extension artifacts and tests**

```powershell
git add backend/modules/fee_evaluation/seeds/fee_reference_rows_v2026_07_16.json backend/modules/fee_evaluation/seeds/fee_rule_extensions_v2026_07_16.json tests/unit/test_fee_reference_snapshot.py tests/unit/test_fee_rule_extensions.py tests/unit/test_fee_rule_seed_compiler.py
git commit -m "data(fee): capture complete Unit Price Reference"
```

---

### Task 5: Compile, Diff, Reload, And Activate The New Seed

**Files:**
- Create: `backend/modules/fee_evaluation/seeds/fee_rules_v2026_07_16.json`
- Modify: `backend/modules/fee_evaluation/seeds/active_fee_rule_seed.json`
- Modify: `tests/unit/test_fee_rule_seed_loader.py`
- Modify: `tests/unit/test_fee_rule_library_diff.py`
- Modify: `tests/unit/test_fee_rule_activation_validator.py`

**Interfaces:**
- Consumes: production snapshot and extension JSON files.
- Produces: active `fee_rules_v2026_07_16` runtime library.

- [ ] **Step 1: Add failing activation tests before changing the manifest**

```python
def test_compiled_production_seed_is_complete_and_reloadable() -> None:
    library = load_fee_rule_library(SEEDS / "fee_rules_v2026_07_16.json")

    base_rules = [rule for rule in library.rules if rule.source_kind == "unit_price_reference"]
    assert len(base_rules) == 44
    assert {rule.source_row for rule in base_rules} == set(range(4, 48))


def test_candidate_diff_preserves_every_existing_rule_id() -> None:
    active = load_fee_rule_library(SEEDS / "fee_rules_v2026_06_03.json")
    candidate = load_fee_rule_library(SEEDS / "fee_rules_v2026_07_16.json")
    diff = diff_fee_rule_libraries(active, candidate)

    assert diff.removed_count == 0
    validate_candidate_activation(active, candidate, diff)
```

- [ ] **Step 2: Run tests and verify the compiled seed is missing**

Run:

```powershell
py -m pytest tests/unit/test_fee_rule_seed_loader.py tests/unit/test_fee_rule_library_diff.py tests/unit/test_fee_rule_activation_validator.py -q
```

Expected: new production seed tests fail because `fee_rules_v2026_07_16.json` is absent.

- [ ] **Step 3: Compile the production seed deterministically**

Run:

```powershell
py -c "from pathlib import Path; from backend.modules.fee_evaluation.fee_rule_seed_compiler import compile_fee_rule_seed_files; root=Path('backend/modules/fee_evaluation/seeds'); compile_fee_rule_seed_files(root/'fee_reference_rows_v2026_07_16.json', root/'fee_rule_extensions_v2026_07_16.json', root/'fee_rules_v2026_07_16.json')"
```

Expected: command exits 0 and creates only the requested new compiled seed.

- [ ] **Step 4: Run pre-activation validation**

Run:

```powershell
py -m pytest tests/unit/test_fee_rule_seed_loader.py tests/unit/test_fee_rule_candidate_builder.py tests/unit/test_fee_rule_seed_compiler.py tests/unit/test_fee_rule_library_diff.py tests/unit/test_fee_rule_activation_validator.py -q
```

Expected: all pre-activation tests pass.

- [ ] **Step 5: Update the active manifest**

```json
{
  "active_seed_name": "fee_rules_v2026_07_16.json"
}
```

- [ ] **Step 6: Update active metadata expectations and rerun loader tests**

```python
def test_load_active_fee_rule_library_uses_complete_reference_snapshot() -> None:
    library = load_active_fee_rule_library()

    assert library.version.version_id == "fee_rules_v2026_07_16"
    assert library.version.source_file_name == "FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls"
    assert library.version.source_hash == (
        "sha256:fb788038631aa0a12f1a052b630513718d9fa1bb64bae647e897e18529ef8a5d"
    )
```

Run:

```powershell
py -m pytest tests/unit/test_fee_rule_seed_loader.py tests/unit/test_fee_rule_library_diff.py tests/unit/test_fee_rule_activation_validator.py -q
```

Expected: all activation tests pass.

- [ ] **Step 7: Confirm the old seed has not been staged or modified by this task**

Run:

```powershell
git diff --cached --name-only | Select-String 'fee_rules_v2026_06_03.json'
```

Expected: no output.

- [ ] **Step 8: Commit the compiled seed and activation**

```powershell
git add backend/modules/fee_evaluation/seeds/fee_rules_v2026_07_16.json backend/modules/fee_evaluation/seeds/active_fee_rule_seed.json tests/unit/test_fee_rule_seed_loader.py tests/unit/test_fee_rule_library_diff.py tests/unit/test_fee_rule_activation_validator.py
git commit -m "feat(fee): activate complete fee reference seed"
```

---

### Task 6: Matcher, Default-Fill, And Draft Regressions

**Files:**
- Modify: `tests/unit/test_fee_rule_matcher.py`
- Modify: `tests/unit/test_fee_default_fill.py`
- Modify: `tests/unit/test_confirmed_matrix_fee_draft_service.py`

**Interfaces:**
- Consumes: active compiled seed through `load_active_fee_rule_library()`.
- Produces: regression evidence only; no new complex pricing evaluator.

- [ ] **Step 1: Add the all-source-name matcher test**

```python
@pytest.mark.parametrize(
    "test_item",
    [
        "high temperature life",
        "Low temperature life",
        "Temperature & Humidity",
        "Steam aging",
        "Thermal shock",
        "Thermal cycling (Ramp rating 3.5C/min)",
        "Thermal cycling (Ramp rating 5C/min)",
        "Whisker testing (Environmental stress)",
        "Salt spray (NSS)",
        "MFG (Class IIA)",
        "MFG (Class IIIA) VW75174 TG19",
        "Dust (Benign)",
        "Vibration",
        "Shock (half sine)",
        "Shock (Trapzoidal)",
        "Vibration + Temp cycling",
        "Microsecond discontinuity",
        "Nanosecond dicontinuity",
        "Mechanical force",
        "Automotive connector Mechanical force",
        "Offset durability",
        "Cable bending",
        "Durability",
        "LLCR",
        "DCR",
        "Contact resistance (CR)",
        "Insulation Resistance (IR)",
        "Dielectric withstanding voltage (DWV)",
        "Capacitance/Inductance",
        "Temperature rise",
        "Temperature rise with thermography",
        "Current cycling (Current ON and OFF)",
        "Solderability",
        "Resistance to solder heat",
        "Porosity",
        "SEM/EDS analysis",
        "FTIR analysis",
        "Cross section",
        "Compressive Whisker (Mechanical Stress)",
        "Hardness Testing",
        "Plating Thickness Measuring",
        "Visual exam",
        "PCB and test fixture design",
        "Report preparation",
    ],
)
def test_every_effective_source_description_matches(test_item: str) -> None:
    result = FeeRuleMatcher(load_active_fee_rule_library()).match_test_item(test_item)

    assert result.status == "matched"
    assert result.rule is not None
```

- [ ] **Step 2: Add IR/DWV partial-default tests**

```python
@pytest.mark.parametrize(
    ("test_item", "rule_id"),
    [
        ("INSULATION RESISTANCE", "fee_rule_insulation_resistance"),
        ("DIELECTRIC WITHSTANDING VOLTAGE", "fee_rule_dielectric_withstanding_voltage"),
    ],
)
def test_ir_and_dwv_expose_per_reading_without_inventing_duration_price(
    test_item: str,
    rule_id: str,
) -> None:
    match = FeeRuleMatcher(load_active_fee_rule_library()).match_test_item(test_item)
    assert match.rule is not None and match.rule.rule_id == rule_id

    result = build_fee_default_fill(rule=match.rule, context=_context(test_item=test_item))

    assert result.unit_label == "reading"
    assert result.unit_price is None
    assert result.review_required is True
    assert "1-minute/2-minute" in (result.review_reason or "")
```

- [ ] **Step 3: Add draft-service proof that IR is a known review rule**

```python
def test_fee_draft_maps_insulation_resistance_to_known_review_rule() -> None:
    draft = _service_with_active_rules(_fixture_row("INSULATION RESISTANCE")).build("project-1")
    line = draft.groups[0].line_items[0]

    assert line.matched_rule_id == "fee_rule_insulation_resistance"
    assert line.status == "review_required"
    assert line.unit_label == "reading"
```

- [ ] **Step 4: Run focused tests and verify failures before adjusting data/compatibility**

Run:

```powershell
py -m pytest tests/unit/test_fee_rule_matcher.py tests/unit/test_fee_default_fill.py tests/unit/test_confirmed_matrix_fee_draft_service.py -q
```

Expected before final seed corrections: failures identify missing aliases, provenance, or
partial-default behavior. Fix only new seed/extension/compiler compatibility unless an
existing generic fallback cannot represent the approved partial result.

- [ ] **Step 5: Preserve the reviewed extension regression set**

Run:

```powershell
py -m pytest tests/unit/test_fee_rule_matcher.py tests/unit/test_fee_default_fill.py tests/unit/test_confirmed_matrix_fee_draft_service.py tests/unit/test_confirmed_matrix_fee_draft_step_quantities.py tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py -q
```

Expected: all focused matcher/default-fill/draft tests pass, including LLCR, CR,
Reseating, Dust, force, visual, report, and temperature-rise cases.

- [ ] **Step 6: Commit regression coverage and any minimal compatibility fix**

```powershell
git add tests/unit/test_fee_rule_matcher.py tests/unit/test_fee_default_fill.py tests/unit/test_confirmed_matrix_fee_draft_service.py
git commit -m "test(fee): cover complete fee reference matching"
```

If a production compatibility file is required, add only that explicitly approved
fee-evaluation file to this commit and record why in TASK_362A evidence.

---

### Task 7: Full Validation, Browser Smoke, And Governance Closeout

**Files:**
- Modify: `tasks/TASK_362A_COMPLETE_FEE_REFERENCE_BASE_SEED.md`
- Modify: `docs/task_board.md`
- Create: `docs/lane_evidence/TASK_362A_complete-fee-reference-base-seed_developer.md`
- Create after role gates: Reviewer/QA/Integrator evidence files following existing naming.

**Interfaces:**
- Consumes: completed TASK_362A implementation.
- Produces: reviewable validation evidence and board closeout.

- [ ] **Step 1: Run the complete focused backend suite**

Run:

```powershell
py -m pytest tests/unit/test_fee_reference_snapshot.py tests/unit/test_fee_rule_extensions.py tests/unit/test_fee_rule_seed_compiler.py tests/unit/test_fee_rule_seed_loader.py tests/unit/test_fee_rule_candidate_builder.py tests/unit/test_fee_rule_library_diff.py tests/unit/test_fee_rule_activation_validator.py tests/unit/test_fee_rule_matcher.py tests/unit/test_fee_default_fill.py tests/unit/test_confirmed_matrix_fee_draft_service.py tests/unit/test_confirmed_matrix_fee_draft_step_quantities.py tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py -q
```

Expected: zero failures.

- [ ] **Step 2: Run pricing-draft and export compatibility regressions**

Run:

```powershell
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py -q
```

Expected: zero failures; a rule-version change may mark old drafts stale through existing
semantics but must not corrupt or overwrite them.

- [ ] **Step 3: Compile all changed Python files**

Run:

```powershell
py -m py_compile backend/modules/fee_evaluation/fee_reference_snapshot.py backend/modules/fee_evaluation/fee_rule_extensions.py backend/modules/fee_evaluation/fee_rule_seed_compiler.py backend/modules/fee_evaluation/fee_rule_models.py backend/modules/fee_evaluation/fee_rule_candidate_builder.py backend/modules/fee_evaluation/fee_rule_seed_loader.py backend/modules/fee_evaluation/fee_rule_library_diff.py
```

Expected: exit code 0.

- [ ] **Step 4: Verify source and immutable old-seed boundaries**

Run:

```powershell
Get-FileHash -LiteralPath 'D:\Template\FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls' -Algorithm SHA256
git diff --cached --name-only | Select-String 'fee_rules_v2026_06_03.json'
```

Expected: workbook hash equals the approved SHA256 and the old seed is absent from the
TASK_362A staged package.

- [ ] **Step 5: Run diff, whitespace, and size gates**

Run:

```powershell
git diff --check
Get-ChildItem backend/modules/fee_evaluation/*.py | ForEach-Object {
  [pscustomobject]@{ File = $_.Name; Lines = (Get-Content $_.FullName -Encoding UTF8).Count }
} | Where-Object { $_.Lines -ge 500 }
```

Expected: `git diff --check` exits 0 apart from documented CRLF conversion warnings;
the line-count command produces no output.

- [ ] **Step 6: Perform the localhost Fee Evaluation smoke**

Use a disposable/local project containing IR and DWV. Confirm:

```text
INSULATION RESISTANCE -> matched rule, Unit Type per reading, review-required price
DIELECTRIC WITHSTANDING VOLTAGE -> matched rule, Unit Type per reading, review-required price
existing LLCR/visual/environment rows -> prior approved defaults remain
```

Do not click `Update Fee` against a real authority project during smoke unless the user
explicitly authorizes that write.

- [ ] **Step 7: Execute the ConnLab review checklist**

Record explicit results for:

```text
architecture boundaries
TASK_362A-only scope
no runtime Office access
no external file/database mutation
type/docstring coverage
no unfinished markers
Python hard-limit compliance
```

- [ ] **Step 8: Update TASK_362A evidence and board only after gates pass**

Set TASK_362A to Developer complete/review pending first. Do not mark it
complete/accepted until Reviewer, QA, and Integrator gates have all passed. Keep
TASK_362B proposed only; do not activate it.

- [ ] **Step 9: Commit governance closeout for the current role**

```powershell
git add tasks/TASK_362A_COMPLETE_FEE_REFERENCE_BASE_SEED.md docs/task_board.md docs/lane_evidence/TASK_362A_complete-fee-reference-base-seed_developer.md
git commit -m "docs(fee): record TASK_362A implementation evidence"
```

---

## Execution Stop

After the implementation plan is approved, execute TASK_362A only. Stop after its
Reviewer/QA/Integrator gates and wait for explicit user approval before planning or
implementing TASK_362B.
