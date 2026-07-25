# RELEASE_006B Test Residual Ownership Audit

Date: 2026-07-25
Role: Planner
Status: `audit_complete / pending Reviewer Child B audit gate`
Parent task: `RELEASE_006_POST_PUSH_WORKTREE_RESIDUAL_COMMIT_AND_CLEANUP_RECONCILIATION`
Child: `RELEASE_006B_TEST_RESIDUAL_OWNERSHIP_AUDIT`
Lane: `post-push-worktree-residual-commit-and-cleanup-reconciliation`
Implementation authorization: none
Discard or restore authorization: none
Commit or push authorization: none

## 1. Audit Boundary

This is a read-only ownership audit of exactly three unaccepted test residuals:

```text
frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts
tests/unit/test_confirmed_matrix_fee_draft_service.py
tests/unit/test_spec_section_text_extractor.py
```

The three files remain unmodified. This audit does not accept their working-tree
content as evidence. Accepted commits, their bounded tests, and accepted
Reviewer, QA, and Integrator evidence are the authority.

Child C, the other tracked and untracked residuals, product code, the board,
cleanup, staging, commit, and push are excluded.

## 2. Repository Baseline

Audit-start facts:

```text
HEAD        267eb50a4247082344e3d7a64a7e58353540d4be
origin      580fbb5ecc5a7fb8ffbdd151fb5198bd1db51db5
left/right  0/1
index       empty
status      46 = 37 tracked + 9 untracked
```

`267eb50a...` is the accepted local Child A docs-only commit. The one local
commit is not a push authorization.

Target inventory:

| Path | Numstat | UTF-8 physical lines | HEAD blob | Working-tree blob | SHA-256 |
|---|---:|---:|---|---|---|
| `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts` | `114/0` | `1389` | `375affbbd5b0d791cbc82a52a210959ff46726b0` | `b3967c8a3526c4d759c1b9a6275040b3d43ce601` | `D2BF49BBDDCCC3971D81594B98208B5BC979344CAA74C64996F2AB1D64BACD95` |
| `tests/unit/test_confirmed_matrix_fee_draft_service.py` | `38/13` | `683` | `ef767f42df2a8245942f01bfac494f69afc19537` | `c53207e9cba3a7916e2db76780f0ea69e0b2804e` | `716D76D265FFC892146C0271F543455E004E8E649629733BAB125453B3FFBBF0` |
| `tests/unit/test_spec_section_text_extractor.py` | `51/0` | `786` | `4c6c9acf6adbb14f36ab295feb0c13e226572a24` | `463422b48e4cb106ae37a712e2a9e9a08c294d13` | `BC6D61558C7113003ADB8A338BB69D266C1642459D952D23C09530F9F063AF42` |

All three files exceed the bounded-test target and are read-only. No future
lane may stage any of them whole or add lines to them.

## 3. Accepted Authorities Used

### 3.1 Pricing Draft Hydration

Accepted Child 3:

```text
c2104e106bad81a827e49714fb6d84ef4b9c09dd
```

Accepted bounded coverage includes:

- `feeEvaluationPricingDraftHydration.test.ts`:
  manual-required blanks remain blank in compatibility mode;
- `FeeEvaluationReviewExportPage.pricingDraftHydration.test.tsx`:
  current-v2, rebase-candidate, Cancel, reload, and CAS behavior;
- the committed read-only preview-model tests:
  manual-required Unit Price and Units remain blank/Pending.

### 3.2 Base Fee Policy

Accepted Child 1:

```text
c5d91c36c5e1d54885fc0a3b406c92ff9aa0cb6b
```

Accepted bounded coverage includes:

- `test_confirmed_matrix_fee_base_fee_policy.py`:
  common automatic zero fallback, explicit rule Base Fee, manual preservation,
  Pending dependent fields, and metadata source;
- `test_confirmed_matrix_fee_draft_rule_resolution.py`:
  single-Group common fallback, one/two-Group explicit rule Base Fee
  preservation, automatic-default fingerprint, and reviewed manual merge.

### 3.3 Damp Heat And TASK_365C

Accepted Damp Heat package:

```text
44a6153ff4a16674bb15cb804887b774ebdae61f
```

Accepted TASK_365C:

```text
71203210
```

Accepted bounded coverage includes:

- Damp Heat parser unit behavior in `test_damp_heat_condition_parser.py`;
- extractor dispatch isolation in `test_spec_section_damp_heat_dispatch.py`;
- Thermal Shock and Voltage Surge parser units;
- real higher-level Product Spec Matrix integration for both TASK_365C rows in
  `test_task_365c_product_spec_matrix_parser.py`.

The accepted Damp Heat Integrator evidence explicitly excluded the old
extractor test's mixed `51/0` residual.

## 4. Frontend Residual Classification (`114/0`)

### F-B1 - Manual Unit Price Blocker Detail (`+530,16`)

Location:

```text
feeEvaluationPreviewModel.test.ts
existing node:
"keeps a manually required unit price pending instead of defaulting it to zero"
added assertion: current lines 530-545
```

Classification: **unique required coverage**.

The committed node already proves blank Unit Price and Pending Testing Fee. No
accepted test asserts that `buildFeeEvaluationUpdateBlockers()` identifies:

```text
rowLabel   Group 1, Step 1, DIELECTRIC WITHSTANDING VOLTAGE
fields     Unit Price
rowMessage Complete Unit Price.
```

Repository-wide HEAD search finds no other `Complete Unit Price.` assertion.
This is a user-visible blocker contract and should be retained, but not in the
1389-line mixed file.

Proposed tests-only child:

```text
RELEASE_006B1_FEE_PREVIEW_MANUAL_REQUIRED_BLOCKER_TEST
```

Exact future May Touch:

```text
frontend/src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts
```

Budget: `<=250` UTF-8 physical lines. Product model, page, API client, CSS, and
the old preview-model test remain locked.

Required assertions:

- manual-required Unit Price remains empty;
- Testing Fee remains `Pending`;
- first blocker owns only `Unit Price`;
- row label and `Complete Unit Price.` copy remain exact;
- manual-required Units and Base Fee blocker regressions remain unchanged.

Future validation:

```powershell
cd frontend
npm test -- --run src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts src/features/fee-evaluation/feeEvaluationPricingDraftHydration.test.ts src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts
npm run build
```

The old `+530,16` assertion becomes an exact discard candidate only after the
new bounded test is accepted.

### F-B2 - Saved Manual-Required LLCR Hydration (`+855,98`)

Location:

```text
new node:
"keeps saved manual-required LLCR price and units pending"
current lines 855-952
```

Classification: **semantic duplicate**.

Equivalence:

- accepted bounded hydration already preserves manual-required blank Unit Price
  and Units through the stable identity contract;
- committed preview-model nodes separately prove blank manual Unit Price and
  blank manual Units produce Pending Testing Fee;
- hydration has no LLCR-specific branch, so the 98-line fixture does not cover
  a distinct production decision.

Exact disposition: discard candidate for the complete `+855,98` node. It must
remain untouched until Reviewer confirms this classification and the User uses
the exact text `discard`.

## 5. Backend Fee Draft Residual Classification (`38/13`)

### B-B1 - Multi-Group Common Base Fee Fallback (`+414,22`)

Location:

```text
test_fee_draft_defaults_base_fee_to_zero_for_every_step_when_multiple_groups_exist
current lines 414-435
```

Classification: **unique required service-integration coverage**.

Accepted tests prove the common fallback policy itself and prove explicit
rule-specific Base Fee behavior across one and two Groups. They do not directly
prove that a non-explicit common fallback is applied independently to every
line of a multi-Group draft.

Proposed tests-only child:

```text
RELEASE_006B2_MULTI_GROUP_BASE_FEE_FALLBACK_TEST
```

Exact future May Touch:

```text
tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py
```

Budget: `<=300` UTF-8 physical lines. All production Fee modules and the
683-line old service test remain locked.

Required assertions:

- construct two owning Confirmed Matrix Groups with independent cells;
- both lines resolve the existing Current Rating rule;
- both lines receive automatic Base Fee `0`;
- both Testing Fees are derived from each line's final safe values;
- no `matrix_group_count` trigger or cross-Group aggregation exists;
- explicit rule-specific and proven manual Base Fee precedence remain covered
  by accepted read-only regressions.

Future validation:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py tests/unit/test_confirmed_matrix_fee_base_fee_policy.py tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py tests/unit/test_confirmed_matrix_fee_draft_service.py -q
```

### B-B2 - Mixed `_snapshot` Generalization (`16/13`)

Locations:

```text
_snapshot(group_count=1)
groups tuple construction
cells tuple construction
```

Classification: **support-only fixture change**, not independent coverage.

These edits exist only to support B-B1 inside the oversized mixed test. The
future bounded module must own a local minimal two-Group fixture instead.
After B-B1 is accepted in the bounded module, the complete old-file `38/13`
residual becomes an exact discard candidate. No helper hunk may be retained in
the old file.

## 6. Parser Residual Classification (`51/0`)

### P-B1 - Real Damp Heat Extractor Integration (`+226,15`)

Location:

```text
test_long_term_damp_heat_extracts_temperature_humidity_and_duration
current lines 226-240
```

Classification: **unique required integration coverage**.

Accepted tests separately prove the real Damp Heat parser and extractor
dispatch, but the dispatch test uses a monkeypatched parser. The accepted
Product Spec parity test compares PDF and DOCX results without asserting the
exact Damp Heat Condition. No accepted bounded test calls the real
`extract_row_details()` path and asserts the exact condition in one node.

Proposed tests-only child:

```text
RELEASE_006B3_DAMP_HEAT_EXTRACTOR_INTEGRATION_TEST
```

Exact future May Touch:

```text
tests/unit/test_spec_section_damp_heat_integration.py
```

Budget: `<=150` UTF-8 physical lines. Parser production and the 786-line old
extractor test remain locked.

Required assertions:

- real `extract_row_details()` dispatches to the real Damp Heat parser;
- exact explicit temperature, RH, duration, and mated note are retained;
- arbitrary prose after the explicit condition is excluded;
- missing explicit facts and generic humidity do not enter this rule.

Future validation:

```powershell
py -m pytest tests/unit/test_spec_section_damp_heat_integration.py tests/unit/test_damp_heat_condition_parser.py tests/unit/test_spec_section_damp_heat_dispatch.py tests/unit/test_condition_text_collectors.py tests/unit/test_spec_section_text_extractor.py -q
```

The old `+226,15` node becomes an exact discard candidate only after the new
bounded test is accepted.

### P-B2 - Thermal Shock Replay (`+241,19`)

Classification: **semantic duplicate**.

Accepted TASK_365C already has:

- exact Thermal Shock parser-unit output;
- real `ProductSpecMatrixParser` integration asserting EIA method, derived
  `total 25 hours`, and `No damage`.

Exact disposition: discard candidate for current lines 241-259 after Reviewer
confirmation and exact User `discard`.

### P-B3 - Voltage Surge Replay (`+260,17`)

Classification: **semantic duplicate**.

Accepted TASK_365C already has:

- exact Voltage Surge parser-unit output and conflict negatives;
- real `ProductSpecMatrixParser` integration asserting pin-scoped
  Differential/Common Mode, waveform, Signal Pin, and no Requirement.

Exact disposition: discard candidate for current lines 260-276 after Reviewer
confirmation and exact User `discard`.

## 7. Closed Classification

| Residual | Unique | Duplicate | Support-only | Pure formatting |
|---|---:|---:|---:|---:|
| Frontend `114/0` | `16/0` | `98/0` | `0/0` | `0/0` |
| Fee service `38/13` | `22/0` | `0/0` | `16/13` | `0/0` |
| Parser `51/0` | `15/0` | `36/0` | `0/0` | `0/0` |

No whole-file candidate is self-contained. The three unique contracts require
three separate tests-only lanes. The duplicate and support-only hunks remain
untouched discard candidates.

Recommended order:

1. B1 frontend blocker test;
2. B2 multi-Group Base Fee integration test;
3. B3 Damp Heat extractor integration test;
4. Reviewer verifies accepted replacement coverage;
5. User separately authorizes exact `discard` hunks.

The tests-only lanes are independent and may be reviewed independently, but
none is approved by this audit.

## 8. Locked Paths

Every product file is locked, including:

- Fee preview model and page production;
- Fee draft, rule-resolution, Base Fee policy, default-fill, V2, and API code;
- parser, collector, Damp Heat, Thermal Shock, Voltage Surge, and Matrix code;
- API client, schema, database, seeds, manifests, CSS, and build dependencies.

Also locked:

- the three audited old test files;
- Child C items;
- all other tracked and untracked residuals;
- real databases, public-drive files, attachments, source workbooks, generated
  artifacts, and remote refs.

## 9. Validation And Stop Point

This audit used:

```powershell
git rev-parse HEAD
git rev-parse origin/master
git rev-list --left-right --count origin/master...HEAD
git status --porcelain=v1 -uall
git diff --cached --name-only
git diff --numstat HEAD -- <three target files>
git diff --unified=0 HEAD -- <three target files>
git hash-object -- <three target files>
(Get-Content <path> -Encoding UTF8).Count
git grep <accepted contract text> HEAD -- <accepted test paths>
git diff --check -- <three target files>
```

No dirty test was run or treated as accepted evidence. No target file, product
file, board, existing governance residual, index entry, or remote ref was
modified.

Next legal role:

```text
Reviewer Child B audit gate
```

Reviewer should verify the three unique classifications, the three
duplicate/support classifications, exact hunk arithmetic, accepted-equivalence
evidence, future test module bounds, and all product locks. Do not route
Developer, QA, Integrator, discard, cleanup, commit, or push.
