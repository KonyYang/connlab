# RELEASE_006B2 Multi-Group Base Fee Fallback Test Plan

Date: 2026-07-25
Status: Developer tests-only implementation complete / pending Reviewer tests-only diff re-gate
Task: `RELEASE_006B2_MULTI_GROUP_BASE_FEE_FALLBACK_TEST`
Lane: `multi-group-base-fee-fallback-test`
Role: Planner post-implementation source-of-truth reconciliation
Product implementation authorization: none
Test implementation authorization: exact bounded B2 module only

## 1. Planning Decision

Formalize only the second unique Child B coverage item as an independent
bounded tests-only lane.

In scope:

```text
22/0 multi-Group common Base Fee fallback service-integration node
```

Out of scope:

```text
16/13 old _snapshot fixture generalization
B1 frontend residual
B3 Damp Heat integration
all duplicate/support and Child C items
```

## 2. Baseline

```text
HEAD          168871302b4ad3522b803391b8d7be9838e96570
origin/master 580fbb5ecc5a7fb8ffbdd151fb5198bd1db51db5
B1            complete/accepted at HEAD
index         empty before Planner formalization
```

Audited old file:

```text
tests/unit/test_confirmed_matrix_fee_draft_service.py
683 UTF-8 physical lines including blanks
dirty numstat 38/13
SHA-256 716D76D265FFC892146C0271F543455E004E8E649629733BAB125453B3FFBBF0
```

Child B Reviewer evidence confirms:

- `22/0` is unique;
- `16/13` is support-only;
- the replacement must use a local fixture;
- future bounded path is
  `tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py`;
- maximum is `<=300` physical lines.

## 3. Accepted Authorities

Read-only accepted Child 1:

```text
c5d91c36c5e1d54885fc0a3b406c92ff9aa0cb6b
```

It owns:

- Base Fee precedence;
- automatic fallback value and metadata;
- identical single/multi-Group policy;
- derived Testing Fee behavior;
- manual-field preservation and V2 ownership.

Read-only accepted Child 2:

```text
dff635a6489f2664f7e496c424ceff8400237283
```

It owns typed duration authority and dependent-field corrections. B2 does not
touch or reinterpret that behavior.

Read-only accepted V2 authority:

- TASK_361L currentness/rebase/CAS/no-write;
- TASK_363D automatic-default attestation;
- accepted Child 3 frontend hydration/currentness.

B2 only verifies the final service composition already produced by those
contracts.

## 4. Implementation Design

### 4.1 Local Store

Define one local in-memory store implementing only:

```text
get_active_by_project("P1") -> local ConfirmedMatrixSnapshot
other project ids -> None
```

Do not import a test helper or modify production dependency injection.

### 4.2 Snapshot

Build one confirmed active version, one Current Rating row, two Groups, and
two Cells using public domain types.

Stable identities:

```text
matrix-b2
draft-b2
import-b2
snapshot-b2
row-current-rating
draft-row-current-rating
source-row-current-rating
group-1 / draft-group-1 / source-group-1 / g1
group-2 / draft-group-2 / source-group-2 / g2
cell-1 / cell-2
```

Business data:

```text
CURRENT RATING
condition 300A
sample quantity 5 in each Group
cell value 1 in each owning Group
```

The fixture contains no optional authority that could affect Units or price.

### 4.3 Service

Instantiate accepted `ConfirmedMatrixFeeDraftService` with only the local
confirmed store and build:

```text
BuildConfirmedMatrixFeeDraftCommand(project_id="P1")
```

Do not inject a custom rule library. The accepted default library must resolve
the deterministic Current Rating rule.

### 4.4 Assertions

Assert:

- exactly two draft Groups in the expected order;
- exactly one line per Group;
- group identity remains distinct;
- both lines match `fee_rule_temperature_rise`;
- both lines are calculated and not review-required;
- Unit Price `600`, Units `5`, Base Fee `0`, discount `0`, Testing Fee `3000`;
- each line has exactly one Base Fee metadata entry with state `auto_filled`
  and source `Matrix Fee automatic Base Fee fallback`.

The test must not assert that multiple Groups cause the zero. It proves only
that the accepted line-level fallback is applied independently in a
multi-Group composition.

## 5. Exact May Touch

Future tests-only implementation:

```text
tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py
```

Governance:

```text
tasks/RELEASE_006B2_MULTI_GROUP_BASE_FEE_FALLBACK_TEST.md
docs/release_006b2_multi_group_base_fee_fallback_test_plan.md
docs/lane_evidence/RELEASE_006B2_multi-group-base-fee-fallback-test_planner.md
docs/task_board.md
future RELEASE_006B2 role evidence
```

No other path is authorized.

## 6. Locked Paths

Read-only:

```text
tests/unit/test_confirmed_matrix_fee_draft_service.py
tests/unit/test_confirmed_matrix_fee_base_fee_policy.py
tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py
accepted Child 2 and V2 regression modules
```

Locked categories:

- all production Python and TypeScript;
- API, schema, database, seeds, manifests, rules, dependencies;
- old `22/0` node and `16/13` helper generalization;
- B1 accepted package and old frontend `114/0` residual;
- B3 parser and old parser residual;
- Child C and every external residual;
- real DB/files, generated artifacts, staging, commit, and push.

## 7. TDD

This is a characterization migration.

Coverage RED:

- on clean HEAD, the bounded module is absent;
- accepted tests do not directly assert common fallback on every line of a
  two-Group deterministic draft.

GREEN:

- add one bounded test module;
- pass against unchanged accepted product;
- require no production or old-test diff.

No production failure or policy mutation may be manufactured.

## 8. Validation

### 8.1 Focused Child 1 And Service

```powershell
py -m pytest `
  tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py `
  tests/unit/test_confirmed_matrix_fee_base_fee_policy.py `
  tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py `
  tests/unit/test_confirmed_matrix_fee_draft_service.py -q
```

### 8.2 Child 2

```powershell
py -m pytest `
  tests/unit/test_confirmed_matrix_fee_duration_authority.py `
  tests/unit/test_fee_default_fill_explicit_hour_authority.py `
  tests/integration/test_confirmed_matrix_fee_draft_dependent_fields_api.py `
  tests/integration/test_fee_default_fill_dependent_fields_v2_rebase.py -q
```

### 8.3 V2

```powershell
py -m pytest `
  tests/unit/test_fee_pricing_draft_prior_defaults_attestation.py `
  tests/unit/test_fee_pricing_draft_automatic_build_safety.py `
  tests/integration/test_fee_pricing_draft_measurement_plan_rebase_attestation.py -q
```

### 8.4 Compile And Package

```powershell
py -m py_compile tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py
(Get-Content 'tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py' -Encoding UTF8).Count
git diff --check
git diff --cached --check
git status --short
```

Run from a clean-HEAD isolate or exact reconstruction. The dirty legacy test
must not be part of accepted validation input.

## 9. Line Budget

```text
new test <=300 UTF-8 physical lines including blanks
```

Recommended allocation:

- imports/constants: `<=35`;
- one behavior node: `<=45`;
- local store and snapshot fixture: `<=170`;
- metadata helper: `<=20`;
- headroom: at least `30`.

No blank-line suppression and no shared helper extraction.

## 10. Risks And Controls

Risk: the test encodes multi-Group as the fallback trigger.

Control: wording and assertions state that fallback is line-level and Group
count is only the composition under test.

Risk: fixture helper edits leak into the old 683-line test.

Control: all fixture code is local to the new bounded module.

Risk: default rule-library drift makes the result non-deterministic.

Control: assert exact accepted rule id, values, and status; do not inject a
test-only rule that bypasses real composition.

Risk: dirty old test is used by the package.

Control: isolate clean HEAD plus the new bounded module and compare old-file
hash/numstat before and after.

Risk: cleanup occurs before replacement acceptance.

Control: old hunks remain locked until later Reviewer and explicit User
cleanup gates.

## 11. Rollback

Before acceptance, remove the new test from the candidate package only.
Do not restore or delete any old dirty hunk.

After a later accepted tests-only commit, rollback reverts only that commit.
Product behavior and old residuals remain untouched.

## 12. Gate Sequence

```text
Planner formalization
-> Reviewer plan gate
-> User approval for Developer planning-first/tests-only implementation
-> Developer bounded test-only pass
-> Reviewer diff gate
-> QA focused regressions/compile
-> User package/commit authorization
-> Integrator exact package
```

Discard and push require independent later authorization.

## 13. Historical Planner Stop

```text
Reviewer RELEASE_006B2 plan gate
```

Reviewer passed that plan gate and the User explicitly approved Developer
tests-only planning-first. Test implementation remains unauthorized.

## 14. Developer Planning-First Refinement

### 14.1 Repository And Gate Facts

Read-only facts confirmed on 2026-07-25:

```text
HEAD             168871302b4ad3522b803391b8d7be9838e96570
branch           master
origin/master    580fbb5ecc5a7fb8ffbdd151fb5198bd1db51db5
left/right       0/2
index            empty
worktree         51 paths = 37 tracked + 14 untracked
legacy test      683 physical lines, dirty 38/13, read-only
legacy SHA-256   716d76d265ffc892146c0271f543455e004e8e649629733bab125453b3ffbbf0
bounded path     absent
```

The accepted B1 commit is current HEAD. The working tree remains mixed and
dirty; future implementation must use a clean-HEAD isolate or equivalent
exact reconstruction and may add only the new B2 module.

### 14.2 Public Interfaces And One-Build Boundary

The bounded test consumes:

```python
ConfirmedMatrixFeeDraftService(
    confirmed_store: ConfirmedMatrixAuthorityStore,
    rule_library: FeeRuleLibrary | None = None,
    contact_measurement_adapter=None,
    contact_point_profile_adapter=None,
)

build_current_pricing_defaults(
    project_id: str,
    provider: ConfirmedMatrixFeeAuthorityBuildProvider,
) -> FeePricingDraftAutomaticBuildResult
```

The local store implements only:

```python
def get_active_by_project(
    self,
    project_id: str,
) -> ConfirmedMatrixSnapshot | None:
    return self.snapshot if project_id == "P1" else None
```

The test must call `build_current_pricing_defaults("P1", service)` once and
use `result.fee_draft` for all draft assertions. It must not first call
`build_draft()` and then build defaults, because the accepted private V2
boundary intentionally derives draft, identities, safety, and source context
from one authority build.

### 14.3 Exact Local Confirmed Matrix Fixture

The future module constructs these public frozen dataclasses directly:

```python
ConfirmedMatrixVersion(
    confirmed_matrix_id="matrix-b2",
    project_id="P1",
    project_matrix_draft_id="draft-b2",
    source_import_id="import-b2",
    source_snapshot_id="snapshot-b2",
    confirmed_revision=1,
    is_active_authority=True,
    status=ConfirmedMatrixStatus.CONFIRMED,
    confirmed_by="operator",
    confirmed_at="2026-07-25T09:00:00+08:00",
    sample_received_date="2026-07-25",
)
```

The one row is:

```python
ConfirmedMatrixRow(
    confirmed_row_id="row-current-rating",
    confirmed_matrix_id="matrix-b2",
    draft_row_id="draft-row-current-rating",
    source_row_snapshot_id="source-row-current-rating",
    row_order=1,
    test_item="CURRENT RATING",
    source_section="6.1",
    method="EIA-364",
    condition="300A",
    requirement="No damage",
)
```

The ordered Groups are:

```text
group-1 / draft-group-1 / source-group-1 / order 1 / g1 / Group 1 / 5
group-2 / draft-group-2 / source-group-2 / order 2 / g2 / Group 2 / 5
```

The two Cells are:

```text
cell-1 / row-current-rating / group-1 / draft-row-current-rating /
  draft-group-1 / value "1"
cell-2 / row-current-rating / group-2 / draft-row-current-rating /
  draft-group-2 / value "1"
```

Every object's `confirmed_matrix_id` is `matrix-b2`. The snapshot leaves
`step_quantities` and `duration_authorities` empty. It contains no Point
Profile, Measurement Plan adapter, manual pricing draft, legacy quantity, or
other row.

`sample_received_date` is non-null so the fixture does not introduce the
unrelated root warning.

### 14.4 Exact Draft Assertions

The test first requires:

```text
draft_status           ready
review_required_count  0
warnings               ()
group order            g1, g2
group labels           Group 1, Group 2
one matrix line in each Group
```

For Group 1 and Group 2 respectively, the exact line identities are:

```text
matrix-b2:g1:row-current-rating / group-1 / g1 / Group 1
matrix-b2:g2:row-current-rating / group-2 / g2 / Group 2
```

Both lines must retain:

```text
confirmed_row_id     row-current-rating
source_row_id        source-row-current-rating
step_tokens          ("1",)
matched_rule_id      fee_rule_temperature_rise
status               calculated
review_required      false
review_reason        null
spend_time           "4"
unit_label           sample
unit_price           Decimal("600")
units                Decimal("5")
base_fee             Decimal("0")
discount_percent     Decimal("0")
testing_fee          Decimal("3000")
```

For each line, select all `field_metadata` entries whose field is
`base_fee` and require exactly:

```python
(
    FeeFieldMetadata(
        field="base_fee",
        state="auto_filled",
        source="Matrix Fee automatic Base Fee fallback",
        message=None,
    ),
)
```

This proves the common fallback value and source on each owning line without
claiming that two Groups caused the fallback. Testing Fee is asserted per
line only; no Group sum or `matrix_group_count` branch is asserted.

### 14.5 Exact Automatic-Default Identity And Fingerprint Assertions

The two Matrix row identities are:

```python
(
    (
        "matrix-b2:g1:row-current-rating:1:0",
        "group-1",
        "row-current-rating",
        "1",
        0,
    ),
    (
        "matrix-b2:g2:row-current-rating:1:0",
        "group-2",
        "row-current-rating",
        "1",
        0,
    ),
)
```

The complete accepted ordered identity sequence also contains the two
backend-owned Sample preparation rows and one Report preparation row:

```python
(
    *matrix_row_identities,
    ("sample_preparation", "group-1", "g1", "Group 1"),
    ("sample_preparation", "group-2", "g2", "Group 2"),
    ("report_preparation", "", "", ""),
)
```

Require `result.ordered_row_identities` to equal this literal tuple.
Require each of the two `result.row_safety` entries to:

- own the matching Matrix row identity;
- have `matched_rule_id="fee_rule_temperature_rise"`;
- be `safe_for_rebase=True` with diagnostic `safe`;
- contain exactly one `base_fee` automatic field with state `auto_filled`,
  source `Matrix Fee automatic Base Fee fallback`, and
  `required_for_rebase=True`.

Finally require:

```python
result.source_context.automatic_defaults_fingerprint == canonical_fingerprint(
    edited_values_to_payload(result.automatic_values)
)
```

The expected fingerprint is derived through the accepted canonical serializer,
not copied from a timestamp-dependent literal and not recreated from test
logic.

### 14.6 Future Test Shape And TDD Order

The single future module may contain:

1. imports and the fallback source constant;
2. local `_Store`;
3. local `_snapshot()` with explicit public dataclasses;
4. local `_base_fee_metadata(line)` selector;
5. one test named
   `test_multi_group_draft_applies_common_base_fee_fallback_per_owning_line`.

Future implementation order:

1. Reconstruct exact clean HEAD `168871302b...` without changing this dirty
   index or worktree.
2. Record coverage RED: the bounded path is absent and clean accepted tests
   do not contain the exact two-Group per-line identity/metadata/fingerprint
   assertion.
3. Create only
   `tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py`.
4. Run the exact new node against unchanged accepted product for GREEN.
5. Run the focused Child 1/service, Child 2, and V2 commands already frozen
   in section 8.
6. Run `py_compile`, physical-line, UTF-8, trailing, diff, whitelist,
   forbidden-path, index, and no-real-data checks.
7. Require a candidate delta of one new test plus separately authorized B2
   governance evidence.

No test implementation step may import from or edit the old mixed test,
inject a custom fee rule library, change a product file, or run cleanup,
staging, commit, or push.

### 14.7 Line Budget, Rollback, And Package Isolation

The Reviewer-approved maximum remains:

```text
<=300 UTF-8 physical lines including blanks
```

Executable allocation:

```text
imports/constants       <=30
local store             <=12
explicit snapshot       <=105
one behavior node       <=95
metadata selector       <=15
headroom                >=43
```

The 683-line legacy file remains read-only at its frozen hash and `38/13`
numstat. Before acceptance, rollback means omitting the new bounded file from
the candidate package; it does not mean restoring or deleting either legacy
hunk. No generated artifact, database, source file, dependency, or product
rollback exists.

### 14.8 Developer Self-Review

- Scope coverage: one unique `22/0` contract only.
- Type consistency: every fixture field matches current public frozen
  dataclasses.
- Dependency direction: test -> public application/domain contracts only.
- Single build: no duplicate authority/provider read.
- Policy ownership: no Base Fee calculation is recreated in the fixture.
- Group isolation: exact Group, row, and flattened row identities are
  independently asserted.
- V2 compatibility: automatic source, safety, and canonical fingerprint are
  asserted without changing V2 behavior.
- Placeholders/TODOs: none.
- Product, old mixed test, B1/B3, Child C, and external residuals: locked.

## 15. Current Stop

```text
Reviewer tests-only diff re-gate
```

Developer completed the exact bounded test at 276 UTF-8 physical lines.
Reviewer independently confirmed its behavior, SHA-256
`E5AD7212F5751DB49E25535471DFE4A2EA9139E031668270B6E292E1D28A181D`,
`18 + 21 + 20` passing regressions, and py_compile. Product and test
candidates are locked pending Reviewer re-gate. QA, Integrator, discard,
cleanup, staging, commit, and push remain unauthorized.
