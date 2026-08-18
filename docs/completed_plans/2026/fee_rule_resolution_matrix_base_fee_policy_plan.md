# Fee Rule Resolution Matrix Base Fee Policy Plan

Status: complete / accepted after Integrator packaging
Date: 2026-07-23
Task: `FEE_RULE_RESOLUTION_MATRIX_BASE_FEE_POLICY`
Lane: `fee-rule-resolution-matrix-base-fee-policy`
Parent: `FEE_DEFAULT_FILL_RESIDUAL_PACKAGE_RECONCILIATION`
Implementation authorization: authorized for Child 1 only

## Purpose And Stop Gate

This Child 1 lane owns only the confirmed-Matrix Fee rule-resolution correction and the common Base Fee automatic-default policy. It must establish the metadata and automatic-default contract before Child 2 default-fill corrections or Child 3 frontend Pending-field hydration can proceed.

This document includes the docs-only Developer planning-first refinement and the subsequent Planner source-of-truth/final authorization reconciliation. Reviewer umbrella/Child 1 plan re-gate has passed, the User approved Child 1 Developer planning-first, Developer docs-only planning-first is complete, Planner source-of-truth reconciliation is complete, Reviewer implementation-readiness passed, and the User explicitly approved Child 1 product implementation. The four exact legacy assertions were then migrated under their tests-only authorization; Reviewer re-gate and QA passed. Integrator packaging is the final permitted lane action.

## Read-Only Code Facts

The implementation plan is based on the current code, not the candidate filenames alone:

- `confirmed_matrix_fee_draft_service.py` currently builds row matches once, calls default fill per row, and can apply a final policy before constructing the line. It is already close to the Python hard limit and must remain a thin coordinator.
- `confirmed_matrix_fee_base_fee_policy.py` currently gates Base Fee `0` on `matrix_group_count > 1`, rewrites generic temperature unit labels, and stamps `Multiple Matrix groups` metadata. That behavior is not accepted.
- `confirmed_matrix_fee_rule_resolution.py` currently maps three long-term aliases to High temperature Life and rewrites plain `CONTACT RESISTANCE` to LLCR when no LLCR row exists. Only one alias is accepted, and plain CR fallback is forbidden.
- `fee_default_fill.py` calculates Testing Fee as `Unit Price * Units * (1 - discount / 100) + Base Fee`. It is locked for Child 1 and remains the source of branch-specific automatic defaults before the final policy is applied.
- `FeeFieldMetadata` exposes `field`, `state`, `source`, and `message`; no DTO expansion is needed.
- TASK_363D derives automatic values, ordered row identities, pre-flattening row safety, and source context from one authority build. Automatic values participate in the automatic-default fingerprint; metadata source participates in the row-safety fingerprint.
- TASK_361L V2 provenance protects proven manual `unit_price`, `units`, `base_fee`, `discount`, `notes`, and `spend_time` during reviewed rebase. The final Base Fee policy must emit a deterministic automatic baseline; it must not attempt to infer saved manual provenance inside the calculation helper.
- Existing oversized tests contain stale assertions for the rejected aliases, multi-Group-only Base Fee zeroing, and plain CR-to-LLCR fallback. They are read-only residuals for this child and cannot be silently edited.

## Frozen Business Contract

### Base Fee precedence

Every Fee line uses the same precedence, regardless of Group count:

1. A V2-proven manual Base Fee remains authoritative and is never overwritten during save/rebase.
2. Otherwise, an explicit accepted rule-specific Base Fee is the automatic value.
3. Otherwise, the automatic Base Fee is `0`.

`matrix_group_count` is not an authority and must not appear in the policy API or decide whether fallback `0` is applied.

The calculation helper operates before pricing-draft manual provenance is merged. It therefore produces rule-specific or fallback automatic defaults only. TASK_361L/TASK_363D remain responsible for preserving a proven manual Base Fee over that automatic baseline.

### Testing Fee derivation

Testing Fee is recalculated only after the final effective automatic Unit Price, Units, Base Fee, and discount are known:

```text
Testing Fee = Unit Price * Units * (1 - discount / 100) + Base Fee
```

If Unit Price, Units, or discount is missing, invalid, unsafe, or review-required, the policy may still resolve Base Fee to its accepted automatic value but must leave Testing Fee unset/Pending and retain a concise review reason. It must not fabricate dependent values to make the formula executable.

### Metadata and fingerprints

The exact deterministic fallback metadata source is frozen as:

```text
Matrix Fee automatic Base Fee fallback
```

For an explicit accepted rule-specific Base Fee, the existing rule display name remains the metadata source. Explicit numeric zero is still an explicit rule value and must not be mistaken for the common fallback.

The implementation must emit exactly one final Base Fee metadata entry. If Testing Fee is safely derived, it must emit exactly one final Testing Fee metadata entry whose source identifies the final automatic calculation source. Existing metadata for unrelated fields must be preserved.

No V2 schema, DTO, public API, or token change is required:

- final automatic Base Fee and Testing Fee values flow into the existing automatic-default fingerprint;
- Base Fee/Testing Fee metadata source flows into the existing TASK_363D row-safety fingerprint;
- the existing source-context fingerprint binds the automatic-default fingerprint;
- generation, CAS, validation token, current-v2, reload, and reviewed-rebase guards remain unchanged.

Mixed, malformed, unsafe, or stale provenance continues to fail closed through the accepted V2 services. This child must not weaken those gates.

### Rule resolution

Only the normalized full label `Long-term high temperature zone load` is added as an alias for the existing High temperature Life rule:

- Unit Price: `15`
- Unit Type: `per hour`
- Units: explicit valid hours only
- missing or invalid hours: typed review-required with no automatic Units or Testing Fee

The following remain no-rule/manual-review and must not be rewritten:

- `Long-term temperature cycle with load`
- `Long-term damp heat`

Plain `CONTACT RESISTANCE` must never be rewritten as LLCR and must never consume LLCR authority, quantity, or price. Existing matcher results for accepted exact rules remain unchanged.

## Authorized Implementation Design

### 1. Rule-resolution helper

`backend/application/confirmed_matrix_fee_rule_resolution.py` will remain a pure bounded helper:

- normalize labels with the existing Fee matcher normalization contract;
- preserve any accepted matcher result already returned for the row;
- add only the approved High temperature Life alias;
- never inspect global presence/absence of LLCR rows;
- never rewrite plain Contact Resistance;
- return a deterministic row-identity-to-match mapping without persistence or provider reads.

No seed, manifest, rule identity, matcher priority, or default-fill branch changes are authorized.

### 2. Base Fee policy helper

`backend/application/confirmed_matrix_fee_base_fee_policy.py` will own only final Base Fee selection and dependent Testing Fee derivation. It must not own generic temperature matching or unit-label correction.

The bounded API will receive the existing calculation result plus the matched accepted rule or its explicit Base Fee fact. It will not receive `matrix_group_count`.

Selection algorithm:

1. If the matched accepted rule has `base_fee.amount is not None`, use that exact amount and the rule display name as source.
2. Otherwise use Decimal `0` and source `Matrix Fee automatic Base Fee fallback`.
3. Replace/deduplicate Base Fee metadata without changing unrelated field metadata.
4. Recalculate Testing Fee only when Unit Price, Units, and discount are valid and present.
5. If dependencies are unsafe or absent, leave Testing Fee unset and preserve review-required state/reason.

The helper must treat an explicit rule Base Fee of zero as rule-specific. It must not infer authority from the pre-policy `calculation.base_fee` alone because existing default-fill branches can contain hard-coded zeros that are not explicit rule values.

### 3. Confirmed Matrix Fee draft orchestration

`backend/application/confirmed_matrix_fee_draft_service.py` will receive narrow hunk-level changes only:

- build the row rule map once for the confirmed snapshot;
- remove all `matrix_group_count` plumbing introduced solely for Base Fee fallback;
- call default fill exactly once per row;
- pass the row match and calculation into the final Base Fee policy;
- construct the Fee line from the final calculation;
- preserve TASK_363D's one-authority-build/no-second-provider-read boundary.

The route/API response, provider contracts, confirmed Matrix ownership, and pricing-draft persistence remain unchanged.

### 4. Maintainability boundary

Future candidate line budgets, counted with UTF-8 `splitlines()` including blank lines:

| File | Current observed lines | Future budget |
|---|---:|---:|
| `confirmed_matrix_fee_draft_service.py` | 486 | target `<=480`, hard `<500` |
| `confirmed_matrix_fee_base_fee_policy.py` | 174 | `<=260` |
| `confirmed_matrix_fee_rule_resolution.py` | 78 | `<=180` |
| `test_confirmed_matrix_fee_base_fee_policy.py` | absent | `<=260` |
| `test_confirmed_matrix_fee_rule_resolution.py` | absent | `<=220` |
| `test_confirmed_matrix_fee_draft_rule_resolution.py` | absent | `<=480` |

The service reduction is mechanical: remove Group-count plumbing and keep DTO/text helpers in their already established bounded modules. No additional production helper is authorized by this plan. If the service cannot remain below 500 physical lines within these hunks, implementation must stop for Planner re-scope.

## Exact Authorized May Touch

Product:

- `backend/application/confirmed_matrix_fee_draft_service.py` - narrow imports/call sites and removal of Base-Fee-only Group-count plumbing.
- `backend/application/confirmed_matrix_fee_base_fee_policy.py` - bounded final Base Fee/Testing Fee policy.
- `backend/application/confirmed_matrix_fee_rule_resolution.py` - bounded exact alias resolution.

Tests, new bounded modules only:

- `tests/unit/test_confirmed_matrix_fee_base_fee_policy.py`
- `tests/unit/test_confirmed_matrix_fee_rule_resolution.py`
- `tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py`

Governance:

- this plan, task-specific evidence, and later task/board status updates performed by the authorized governance role.

## Locked Paths And Behaviors

- `backend/modules/fee_evaluation/fee_default_fill.py`
- `backend/modules/fee_evaluation/fee_default_fill_common.py`
- Fee seeds, manifests, matcher priorities, rule identities, and pricing formulas
- TASK_361L/TASK_363D persistence, attestation, CAS, token, currentness, and rebase modules
- pricing-draft routes and public DTOs
- frontend, API client, schema, database, migrations, real DB/files, generated artifacts
- Child 2 default-fill dependent-field corrections
- Child 3 frontend Pending-field preservation/hydration
- oversized `tests/unit/test_confirmed_matrix_fee_draft_service.py`
- oversized `tests/unit/test_fee_default_fill.py`
- any external residual or mixed dirty hunk

The stale assertions in locked oversized tests are known package residuals, not permission to edit them except for the formal tests-only exception below.

## Tests-Only B1 Exception

Reviewer implementation gate found four exact stale legacy assertions. Product implementation matched the Child 1 contract and the new bounded suite passed `23/23`; QA cannot rely on persistent deselection, so these exact tests must be migrated.

Allowed tests-only files and nodes:

| File | Current lines | Exact node / assertion scope | Required migration |
|---|---:|---|---|
| `tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py` | 223 | `test_plain_contact_resistance_uses_llcr_when_matrix_has_no_explicit_llcr` | Plain `CONTACT RESISTANCE` must not fallback to LLCR; migrate expected assertion to typed review/no LLCR authority. |
| `tests/unit/test_confirmed_matrix_fee_draft_service.py` | 684 | `test_fee_draft_uses_temperature_rise_rule_for_current_rating` suggested Base Fee `500` / Testing Fee `3500` assertions | Migrate expected Base Fee/Testing Fee behavior to manual > explicit rule-specific > automatic Base Fee `0`. |
| `tests/unit/test_confirmed_matrix_fee_draft_service.py` | 684 | `test_fee_draft_defaults_non_rise_temperature_items_to_per_hour[Long-term temperature cycle with load]` | Rejected alias must remain no-rule/manual-review. |
| `tests/unit/test_confirmed_matrix_fee_draft_service.py` | 684 | `test_fee_draft_defaults_non_rise_temperature_items_to_per_hour[Long-term damp heat]` | Rejected alias must remain no-rule/manual-review. |

No other test nodes, fixtures, product code, seeds, V2 modules, API, frontend, Child 2/3, or external LLCR residual may change. Both legacy files must not increase in UTF-8 physical line count; use equal replacement where possible.

## TDD And Validation Matrix

### Rule-resolution tests

- approved alias resolves to existing High temperature Life rule;
- case/whitespace normalization remains consistent with the existing matcher;
- rejected two long-term labels remain no-rule/manual-review;
- plain Contact Resistance never resolves to LLCR, both with and without a separate LLCR row;
- an existing accepted matcher result is not overwritten.

### Base Fee policy tests

- no explicit rule Base Fee yields automatic `0` for every line;
- explicit rule-specific Base Fee, including explicit `0`, is preserved;
- API has no Group-count trigger and single/multi orchestration yields the same precedence;
- deterministic Base Fee source and metadata deduplication;
- complete dependencies recalculate Testing Fee with discount;
- missing Unit Price, Units, or discount leaves Testing Fee unset/review-required;
- unrelated manual/review metadata is unchanged.

### Service and V2 regression tests

- approved alias uses `15/per hour` only with explicit valid hours;
- missing/invalid hours do not create Units or Testing Fee;
- rejected aliases remain manual-review;
- plain CR does not consume LLCR or Point Profile authority;
- single-Group and multi-Group rows receive identical Base Fee precedence;
- final automatic values bind automatic-default/source-context fingerprints;
- final metadata source binds TASK_363D row-safety fingerprint;
- V2 reviewed rebase preserves proven manual Unit Price, Units, Base Fee, discount, notes, and spend time;
- stale generation/token/CAS conflicts are typed no-write;
- one authority build is retained and no second provider read is introduced.

All persistence tests use disposable SQLite only. No real database, operator configuration, workbook, public-drive file, or generated artifact may be accessed.

### Commands and gates

Developer implementation validation must include:

```text
py -m pytest tests/unit/test_confirmed_matrix_fee_rule_resolution.py -q
py -m pytest tests/unit/test_confirmed_matrix_fee_base_fee_policy.py -q
py -m pytest tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py -q
py -m pytest <accepted TASK_361L/TASK_363D focused read-only regressions> -q
py -m py_compile <three product candidates>
git diff --check -- <exact Child 1 whitelist>
```

Additional checks:

- UTF-8 trailing-whitespace scan;
- physical line count using `Path.read_text(encoding="utf-8").splitlines()`;
- exact-path diff and forbidden-scope scan;
- no real-data/path references;
- staging remains empty;
- no stage, commit, or push.

## Rollback And Package Isolation

The future package is limited to three product files, three new test modules, and lane governance. Rollback is hunk-level removal of Child 1 changes; no schema/data rollback exists. Child 2 and Child 3 remain unauthorized until Child 1 metadata and automatic-default behavior are accepted.

## Risks And Stop Conditions

- Manual precedence cannot be proven from a pre-persistence calculation alone. Any implementation that tries to infer manual state there is incorrect; V2 provenance must remain the authority.
- Hard-coded zeros in default-fill cannot be treated as explicit rule Base Fee. The matched rule's structured `base_fee.amount` is the discriminator.
- Resolving an unsafe dependent field to make Testing Fee calculable would violate the no-fabrication contract.
- Any need to edit locked oversized tests, default-fill, seeds, V2 modules, frontend, or schema requires Planner re-scope.
- Any candidate Python file reaching 500 physical lines blocks review.

## Planning-First Exit Criteria

- exact product/test May Touch is frozen;
- Base Fee precedence and deterministic metadata source are explicit;
- V2 fingerprint/provenance ownership is explicit without DTO/schema changes;
- alias and plain-CR negative boundaries are explicit;
- line budgets, tests, rollback, and package isolation are reviewable;
- Planner source-of-truth reconciliation has recorded Reviewer plan re-gate passed, User-approved Developer planning-first, and Developer docs-only planning-first complete;
- Reviewer implementation-readiness passed and User explicitly approved Child 1 product implementation;
- Child 2 and Child 3 remain blocked;
- the twelve-path umbrella remains planning evidence only and is not an implementation authorization;
- product implementation matched Reviewer gate, product code is locked, and only the four exact legacy assertion migrations are pending before QA.
