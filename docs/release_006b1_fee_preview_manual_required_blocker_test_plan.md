# RELEASE_006B1 Fee Preview Manual-Required Blocker Test Plan

Date: 2026-07-25
Status: `tests-only implementation authorized / pending Developer implementation`
Task: `RELEASE_006B1_FEE_PREVIEW_MANUAL_REQUIRED_BLOCKER_TEST`
Lane: `fee-preview-manual-required-blocker-test`
Current role: Planner final source-of-truth reconciliation
Product implementation authorization: none
Test implementation authorization: explicit User approval, exact bounded module only

## 1. Planning Decision

Formalize only the first unique Child B coverage item as an independent
tests-only lane.

The other two unique items remain future choices:

- multi-Group common Base Fee fallback service integration;
- real Damp Heat `extract_row_details()` integration.

Duplicate/support hunks and Child C remain out of scope.

## 2. Evidence And Baseline

Current formalization baseline:

```text
HEAD          267eb50a4247082344e3d7a64a7e58353540d4be
origin/master 580fbb5ecc5a7fb8ffbdd151fb5198bd1db51db5
left/right    0/1
index         empty before Planner documentation
```

Authoritative evidence:

```text
docs/lane_evidence/RELEASE_006B_test-residual-ownership-audit_planner.md
docs/lane_evidence/RELEASE_006B_test-residual-ownership-audit_reviewer.md
```

Reviewer froze:

- frontend unique coverage: `16/0`;
- frontend duplicate coverage: `98/0`;
- old test size: `1389` UTF-8 physical lines;
- old test status: oversized, mixed, read-only;
- future bounded path and maximum: one new module, `<=250` lines.

Accepted HEAD already exposes the public functions required by the bounded
test:

```text
buildFeeEvaluationPreviewRows
applyFeeEvaluationPreviewEdits
buildFeeEvaluationUpdateBlockers
```

No production change or new dependency is required.

## 3. Exact Contract Under Test

Input row:

| Field | Value |
|---|---|
| Group | `Group 1` |
| Step | `1` |
| Test item | `DIELECTRIC WITHSTANDING VOLTAGE` |
| Status | `review_required` |
| Unit Price | `null` |
| Unit Price metadata | `manual_required` |
| Unit type | `reading` |
| Units | `1` |
| Base Fee | `0` |
| Testing Fee | `null` |

Preview output:

```text
unitPrice=""
unitType="per reading"
units="1"
baseFee="0"
testingFee="Pending"
```

First blocker:

```text
rowLabel="Group 1, Step 1, DIELECTRIC WITHSTANDING VOLTAGE"
fields=["Unit Price"]
rowMessage="Complete Unit Price."
```

This test is intentionally narrow. It does not own the general hydration
contract, LLCR behavior, Base Fee policy, formula implementation, backend
metadata, or page rendering.

## 4. File-Level Plan

### Step 1 - Establish coverage RED

Read only:

```text
frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts
frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts
frontend/src/features/fee-evaluation/feeEvaluationPricingDraftHydration.test.ts
```

On a clean-HEAD isolate:

- confirm the bounded file is absent;
- confirm no accepted node asserts all three blocker outputs together;
- record this as a coverage gap, not a production failure.

### Step 2 - Add one bounded test

Create:

```text
frontend/src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts
```

The module owns:

- a local minimal Fee draft factory;
- a local minimal manual-required line factory;
- one focused behavior node;
- exact preview and blocker assertions.

It must not import fixtures from another test file.

### Step 3 - GREEN

Run the new node against accepted production without changing any product
file. A product diff is a scope failure.

### Step 4 - Regression

Run the new bounded test, accepted hydration test, and clean-HEAD legacy model
test together, followed by the TypeScript/Vite build.

### Step 5 - Package gate

Construct an isolated package containing only:

```text
frontend/src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts
RELEASE_006B1 governance/evidence approved by later gates
```

Do not stage the mixed working-tree copy of the old test.

## 5. Exact May Touch

Future test implementation:

```text
frontend/src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts
```

Current/future governance:

```text
tasks/RELEASE_006B1_FEE_PREVIEW_MANUAL_REQUIRED_BLOCKER_TEST.md
docs/release_006b1_fee_preview_manual_required_blocker_test_plan.md
docs/lane_evidence/RELEASE_006B1_fee-preview-manual-required-blocker-test_planner.md
docs/task_board.md
future RELEASE_006B1 role evidence
```

No other path is authorized.

## 6. Locked Paths

Read-only:

```text
frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts
frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts
frontend/src/features/fee-evaluation/feeEvaluationPricingDraftHydration.test.ts
```

Locked categories:

- every frontend production component, page, hook, model, selector, CSS, API
  client, configuration, and dependency;
- every backend, API, schema, database, seed, manifest, Matrix, Fee, parser,
  workbook, and release path;
- RELEASE_006 B2/B3 unique coverage;
- all duplicate/support/discard candidates;
- Child C and all external residuals;
- real data/files, generated artifacts, Git refs, and remote operations.

## 7. Line Budget

```text
new bounded test <=250 UTF-8 physical lines including blanks
```

Count with:

```powershell
(Get-Content 'frontend/src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts' -Encoding UTF8).Count
```

The 1389-line old test may not grow or be rewritten. There is no mechanical
split of that file in this lane.

## 8. Validation Matrix

### Focused behavior

- manual-required Unit Price stays blank;
- Testing Fee stays Pending;
- row identity is Group 1 / Step 1 / exact test item;
- blocker owns only Unit Price;
- exact row message is `Complete Unit Price.`.

### Read-only regressions

- manual-required Units behavior remains unchanged;
- manual-required Base Fee behavior remains unchanged;
- accepted pricing-draft hydration remains unchanged;
- no LLCR-specific branch is introduced.

### Commands

Use a clean-HEAD isolate or equivalent exact-index reconstruction:

```powershell
Set-Location frontend
npm test -- --run src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts src/features/fee-evaluation/feeEvaluationPricingDraftHydration.test.ts src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts
npm run build
```

Governance/package:

```powershell
git diff --check
git diff --cached --check
git diff --numstat
git status --short
```

Also verify:

- exact whitelist;
- no old-test or product diff;
- no forbidden path/content;
- UTF-8 decode and trailing whitespace;
- staging empty before any separately authorized Integrator package;
- no real-data or generated-output mutation.

## 9. Risks And Controls

Risk: staging the old mixed test captures the duplicate LLCR node.

Control: old test is read-only and prohibited from the package.

Risk: a broad fixture accidentally tests hydration or LLCR behavior.

Control: use one local minimal line and assert only the exact blocker contract.

Risk: Developer changes production to satisfy a characterization test.

Control: product diff is an immediate scope failure.

Risk: accepted regressions are run from the dirty worktree.

Control: run validation from clean HEAD plus the one new bounded module.

Risk: old hunk is discarded before replacement acceptance.

Control: discard remains separately gated after Reviewer/QA/Integrator
acceptance and exact User authorization.

## 10. Rollback

Before acceptance, rollback is limited to omitting the new bounded test module
from a candidate package. Do not restore or delete the old dirty hunk.

After a later accepted tests-only commit, rollback reverts only that bounded
test commit. Product behavior is unaffected.

## 11. Gate Sequence

```text
Planner formalization
-> Reviewer plan gate
-> User approval for Developer tests-only planning/implementation as required
-> Developer bounded test-only pass
-> Reviewer diff gate
-> QA isolated regression/build
-> User package/commit authorization
-> Integrator exact package
```

No gate authorizes discard or push implicitly.

## 12. Historical Planning Stop (Superseded)

This earlier planning-first stop was:

```text
Reviewer implementation-readiness re-gate
```

Reviewer subsequently passed that gate and the User explicitly authorized
tests-only implementation. The current effective stop is recorded at the end
of this plan. Discard, cleanup, staging, commit, and push remain unauthorized.

## 13. Developer Planning-First Refinement

### 13.1 Gate And Repository Facts

This docs-only Developer pass is allowed because Reviewer recorded
`reviewer_plan_pass` and the User explicitly approved Developer tests-only
planning-first. That approval does not authorize test implementation.

Read-only facts on 2026-07-25:

```text
HEAD             267eb50a4247082344e3d7a64a7e58353540d4be
branch           master
origin/master    580fbb5ecc5a7fb8ffbdd151fb5198bd1db51db5
left/right       0/1
index            empty
legacy test      1389 physical lines, dirty 114/0, read-only
legacy SHA-256   d2bf49bbddccc3971d81594b98208b5bc979344caa74c64996f2ab1d64bacd95
bounded path     absent
```

The working tree contains many unrelated dirty and untracked paths. Future
implementation must use an accepted-HEAD isolate or exact reconstruction and
must never stage, restore, clean, or copy the legacy test residual.

### 13.2 Goal, Input, Output, And Ownership

Goal:

Create one future bounded characterization test proving the accepted
manual-required Unit Price preview and blocker contract without changing
production.

Input:

- one `FeeEvaluationDraft`;
- one Group labelled `Group 1`;
- one Step `1` line for `DIELECTRIC WITHSTANDING VOLTAGE`;
- `unit_price=null`, `unit_label="reading"`, `units="1"`,
  `base_fee="0"`, and `testing_fee=null`;
- `manual_required` metadata for `unit_price` and `testing_fee`.

Output:

- preview row values:
  `unitPrice=""`, `unitType="per reading"`, `units="1"`,
  `baseFee="0"`, `testingFee="Pending"`;
- first blocker:
  exact row label, `fields=["Unit Price"]`, and
  `rowMessage="Complete Unit Price."`.

Ownership:

- the future test owns only this characterization;
- `feeEvaluationPreviewModel.ts` remains the accepted behavior source;
- B2/B3, LLCR hydration, Base Fee policy, formula logic, page rendering, and
  backend metadata are not inputs to this lane.

### 13.3 Existing Public Interfaces

Future test imports only:

```ts
import type {
  FeeEvaluationDraft,
  FeeEvaluationLineItem,
} from "../../api/client";
import {
  applyFeeEvaluationPreviewEdits,
  buildFeeEvaluationPreviewRows,
  buildFeeEvaluationUpdateBlockers,
} from "./feeEvaluationPreviewModel";
```

Verified signatures:

```ts
buildFeeEvaluationPreviewRows(
  draft: FeeEvaluationDraft | null
): FeeEvaluationPreviewRow[];

applyFeeEvaluationPreviewEdits(
  rows: FeeEvaluationPreviewRow[],
  edits: FeeEvaluationPreviewEditState
): FeeEvaluationPreviewRow[];

buildFeeEvaluationUpdateBlockers(input: {
  rows: FeeEvaluationPreviewRow[];
  totals: {
    testingFeeTotal: string;
    workingHours: string;
    labManpowerCost: string;
    externalCost: string;
    grandCost: string;
  };
}): FeeEvaluationUpdateBlocker[];
```

No new public type, helper export, runtime dependency, API, or shared fixture
is permitted.

### 13.4 Minimal Local Fixture

The future module should define one local complete
`FeeEvaluationLineItem` factory, three local line values, and one local
`FeeEvaluationDraft`. It must not import from the legacy test.

The complete base factory must populate every field required by
`FeeEvaluationLineItem` and use non-blocking defaults:

```ts
function completeLine(
  overrides: Partial<FeeEvaluationLineItem>
): FeeEvaluationLineItem {
  return {
    line_id: "line",
    status: "calculated",
    review_required: false,
    review_reason: null,
    confirmed_matrix_id: "cmv-1",
    confirmed_revision: 1,
    group_key: "g1",
    group_label: "Group 1",
    confirmed_group_id: "cmg-1",
    sample_quantity_expression: "1",
    confirmed_row_id: "row-1",
    source_row_id: "source-row-1",
    row_order: 1,
    test_item: "Line",
    section: "6.1",
    method: "",
    condition: "",
    requirement: "",
    step_tokens: ["1"],
    matched_rule_id: null,
    matched_rule_version_id: null,
    matched_rule_name: null,
    match_reason: "fixture",
    calculation_strategy: null,
    spend_time: "0",
    unit_label: "reading",
    unit_price: "1",
    units: "1",
    base_fee: "0",
    discount_percent: "0",
    testing_fee: "1",
    field_metadata: [],
    warnings: [],
    ...overrides,
  };
}
```

The target business row is frozen as:

```ts
const dwvLine = completeLine({
  line_id: "manual-unit-price",
  status: "review_required",
  review_required: true,
  review_reason: "Confirm 1-minute/2-minute price.",
  test_item: "DIELECTRIC WITHSTANDING VOLTAGE",
  method: "DWV",
  step_tokens: ["1"],
  match_reason: "manual review",
  unit_price: null,
  testing_fee: null,
  field_metadata: [
    {
      field: "unit_price",
      state: "manual_required",
      source: "DWV",
      message: "Confirm 1-minute/2-minute price.",
    },
    {
      field: "testing_fee",
      state: "manual_required",
      source: "DWV",
      message: "Confirm 1-minute/2-minute price.",
    },
  ],
});
```

The fixture must also provide two explicit completed manual rows. These rows
are support context only; they prevent the accepted model from synthesizing
Pending fallback rows:

```ts
const samplePreparation = completeLine({
  line_id: "sample-preparation:g1",
  test_item: "Sample preparation",
  confirmed_row_id: "",
  source_row_id: null,
  row_order: 0,
  step_tokens: [],
  spend_time: "0.5",
  unit_label: "sample",
  unit_price: "50",
  units: "1",
  base_fee: "0",
  discount_percent: "100",
  testing_fee: "0",
});

const reportPreparation = completeLine({
  line_id: "manual-report-preparation",
  group_key: "",
  group_label: "",
  confirmed_group_id: "",
  sample_quantity_expression: "",
  confirmed_row_id: "",
  source_row_id: null,
  row_order: 0,
  test_item: "Report preparation",
  step_tokens: [],
  spend_time: "4",
  unit_label: "report",
  unit_price: "600",
  units: "1",
  base_fee: "0",
  discount_percent: "100",
  testing_fee: "0",
});
```

The complete draft is frozen as:

```ts
const draft: FeeEvaluationDraft = {
  header: {
    project_id: "P1",
    confirmed_matrix_id: "cmv-1",
    confirmed_revision: 1,
    pricing_rule_version_id: "fee_rules_fixture",
    pricing_source_file_name: "fixture.json",
    pricing_source_hash: "sha256:fixture",
    pricing_effective_from: null,
    generated_at: "2026-07-25T00:00:00Z",
  },
  draft_status: "needs_review",
  total_fee: null,
  review_required_count: 1,
  groups: [{
    group_key: "g1",
    group_label: "Group 1",
    sample_quantity_expression: "1",
    manual_line_items: [samplePreparation],
    line_items: [dwvLine],
  }],
  manual_line_items: [reportPreparation],
  warnings: [],
};
```

After `buildFeeEvaluationPreviewRows()` and
`applyFeeEvaluationPreviewEdits(rows, {})`, expected row order is:

```text
sample-preparation:g1
manual-unit-price:1:0
manual-report-preparation
```

Sample preparation and Report preparation must each have complete Man-hour,
Unit Price, Unit Type, Units, Base Fee, and Discount values. The test must
assert they produce no blocker, then assert the complete blocker array has
exactly one entry and that entry belongs to the DWV row. It may not filter
fallback/manual rows out before calling `buildFeeEvaluationUpdateBlockers()`.

This remains one Group and one DWV business row. The two explicit manual rows
are only accepted-model support context and introduce no B2/B3, hydration,
LLCR, or multi-Group behavior.

### 13.5 Future TDD Order

Only after a separate explicit tests-only implementation authorization:

1. Materialize an accepted-HEAD source isolate without changing the current
   index or working tree.
2. Confirm the bounded path is absent and accepted tests do not contain one
   assertion covering all three exact blocker fields. Record this as coverage
   RED; do not manufacture a production failure.
3. Create only
   `feeEvaluationPreviewManualRequiredBlockers.test.ts`.
4. Add one node:
   `reports Unit Price as the only blocker for a manual-required DWV line`.
5. Build rows, apply `{}` edits, and assert the exact
   sample → DWV → report row order.
6. Find `manual-unit-price:1:0` and assert the five preview fields.
7. Build blockers with numeric completed totals; assert the full blocker
   array has length one and its only object is the exact DWV Unit Price
   blocker.
8. Run the new node as GREEN against unchanged accepted production.
9. Run the bounded test, accepted hydration test, clean-HEAD legacy model
   test, and `npm run build`.
10. Prove the candidate package contains only the new test plus separately
   authorized RELEASE_006B1 governance evidence.

No implementation step may edit a product file, the old test, package files,
or dependencies.

### 13.6 Clean-HEAD And Package Validation

Future implementation must:

- derive source from exact HEAD `267eb50a...`;
- reuse the existing preconfigured frontend dependency environment without
  `npm install`, `npm ci`, or package edits;
- run tests from the isolate or an equivalent exact-index reconstruction;
- count the new file with blank-inclusive UTF-8 semantics and require
  `<=250`;
- compare the old test's hash/line count/diff before and after and require no
  change;
- require zero product diff and an exact one-test-file whitelist;
- run UTF-8 decode, trailing-whitespace, diff-check, forbidden-path/content,
  index-empty, and no-real-data/generated-output checks.

Expected future commands:

```powershell
Set-Location frontend
npm test -- --run `
  src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts `
  src/features/fee-evaluation/feeEvaluationPricingDraftHydration.test.ts `
  src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts
npm run build
```

The build is validation only after implementation authorization. This
planning pass runs no npm command and creates no dependency or build output.

### 13.7 Risks, Rollback, Acceptance, And Stop

Risks and controls:

- Dirty legacy coverage absorption: isolate from HEAD and whitelist only the
  new path.
- Fixture expansion into B2/B3: keep one Group and one DWV business row; use
  only the two explicit completed manual rows required to suppress accepted
  fallback blockers.
- False RED: define RED as absent bounded coverage, never as a product defect.
- Product drift: any product diff is a scope failure.
- Cleanup before acceptance: old residual remains untouched until a separate
  Reviewer/QA/Integrator and explicit User cleanup gate.

Rollback before acceptance is omission of the new test from the candidate
package. After a later accepted commit, rollback reverts only that test
commit. No product, schema, data, dependency, or generated-output rollback
exists.

Acceptance requires:

- exact preview and blocker assertions pass;
- all declared read-only regressions and build pass;
- new module `<=250` lines;
- old mixed test unchanged;
- zero product/B2/B3/Child C/external residual inclusion;
- index empty and no stage/commit/push.

Current stop:

```text
Developer tests-only implementation pass
```

Tests-only implementation is authorized only for the exact bounded module.
Product changes, old-test edits, B2/B3, duplicate/support hunks, Child C,
discard, cleanup, staging, commit, and push remain unauthorized.
