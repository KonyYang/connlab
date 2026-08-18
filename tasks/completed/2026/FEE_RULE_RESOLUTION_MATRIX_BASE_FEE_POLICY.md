# FEE_RULE_RESOLUTION_MATRIX_BASE_FEE_POLICY

Status: complete / accepted after Integrator packaging
Lane: `fee-rule-resolution-matrix-base-fee-policy`
Parent: `FEE_DEFAULT_FILL_RESIDUAL_PACKAGE_RECONCILIATION`
Implementation authorization: authorized for Child 1 only
Date: 2026-07-23

## Purpose

Freeze and later implement, only after approval, the backend Matrix-wide Fee rule resolution and general Base Fee fallback/precedence/metadata residual currently visible in:

- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/application/confirmed_matrix_fee_base_fee_policy.py`
- `backend/application/confirmed_matrix_fee_rule_resolution.py`

## Dependencies

- Accepted TASK_361L V2 pricing-draft provenance/currentness.
- Accepted TASK_362A r5/r6 Fee rule baseline.
- Accepted TASK_363A/B/C/D Fee alias, CR authority, and automatic-default attestation contracts.
- Reviewer umbrella/Child 1 plan re-gate passed.
- User approved Child 1 Developer planning-first only.
- Developer docs-only planning-first is complete.
- Planner source-of-truth reconciliation is complete.
- Reviewer implementation-readiness passed.
- User explicitly approved Child 1 product implementation.
- The latest User command supersedes the earlier no-family/no-op checkpoint.
- User decisions for Base Fee fallback/precedence, high-temperature aliases, and plain Contact Resistance fallback were recorded on 2026-07-23.
- No Base Fee family whitelist is needed because the approved fallback applies to every Fee line after manual/rule-specific precedence.

## User Decisions Recorded

1. Base Fee fallback/precedence:
   - Every Fee line applies common precedence: proven manual Base Fee first, explicit accepted rule-specific Base Fee second, otherwise automatic Base Fee `0`.
   - Proven manual Base Fee is never overwritten.
   - Explicit rule-specific Base Fee takes precedence over fallback `0`.
   - Single-Group and multi-Group use the same precedence.
   - `matrix_group_count` must not decide whether to fill `0`.
   - Automatic default metadata must mark Base Fee as automatic default and bind source/fingerprint.
   - Candidate `matrix_group_count > 1` blanket zero logic must be rewritten before implementation.
2. High-temperature alias approval:
   - Selected option: 2B.
   - Approved exact label: `Long-term high temperature zone load`.
   - It maps to High temperature Life, Unit Price `15`, Unit Type `per hour`.
   - Units may come only from explicit hour authority.
   - Missing/invalid hours produce typed review/no automatic write.
   - `Long-term temperature cycle with load` and `Long-term damp heat` are not approved and remain no-rule/manual-review.
3. Plain Contact Resistance fallback:
   - Selected option: 3B.
   - Plain `CONTACT RESISTANCE` must not fallback to LLCR.
   - It must not consume LLCR authority, quantity, or price.
   - It remains typed review/no automatic LLCR authority.

## Base Fee / Metadata / Rebase Contract

- Policy may write automatic Base Fee `0`, Base Fee metadata, and derived Testing Fee only after proving no manual Base Fee and no explicit accepted rule-specific Base Fee.
- Multi-Group context is not an authority and must be equivalent to single-Group behavior.
- It must never override a V2-proven manual Base Fee, Unit Price, Units, discount, notes, or spend time.
- Automatic Base Fee changes must be represented in TASK_363D automatic-default attestation, source context fingerprint, and reviewed rebase/currentness checks.
- Any conflict between saved manual provenance and a new automatic Base Fee policy is typed review-required or blocked/no-write, not silent overwrite.

## Authorized May Touch

Product code is now locked after Reviewer implementation review. The product implementation matched the Child 1 contract and the new bounded suite passed `23/23`.

- `backend/application/confirmed_matrix_fee_draft_service.py` narrow composition/import/call-site hunks only; final file `<500` UTF-8 physical lines.
- `backend/application/confirmed_matrix_fee_base_fee_policy.py` bounded helper, `<500`, only after replacing `matrix_group_count > 1` blanket logic with field-level precedence for all lines.
- `backend/application/confirmed_matrix_fee_rule_resolution.py` bounded helper, `<500`.
- New bounded tests only:
  - `tests/unit/test_confirmed_matrix_fee_base_fee_policy.py`
  - `tests/unit/test_confirmed_matrix_fee_rule_resolution.py`
  - `tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py`

## Tests-Only Legacy Assertion Exception

Reviewer implementation gate found four exact stale legacy assertions that contradict the accepted Child 1 contract. Developer may perform an equal-or-smaller tests-only migration of only these nodes:

- `tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py::test_plain_contact_resistance_uses_llcr_when_matrix_has_no_explicit_llcr`:
  - migrate expectation to plain `CONTACT RESISTANCE` no LLCR fallback / typed review boundary.
- `tests/unit/test_confirmed_matrix_fee_draft_service.py::test_fee_draft_uses_temperature_rise_rule_for_current_rating`:
  - migrate superseded suggested Base Fee `500` / Testing Fee `3500` assertion to the accepted Base Fee precedence contract: manual > explicit rule-specific > automatic Base Fee `0`.
- `tests/unit/test_confirmed_matrix_fee_draft_service.py::test_fee_draft_defaults_non_rise_temperature_items_to_per_hour[Long-term temperature cycle with load]`:
  - migrate expectation to no-rule/manual-review; the label is rejected.
- `tests/unit/test_confirmed_matrix_fee_draft_service.py::test_fee_draft_defaults_non_rise_temperature_items_to_per_hour[Long-term damp heat]`:
  - migrate expectation to no-rule/manual-review; the label is rejected.

The two legacy files remain locked outside these exact assertion/fixture expectation nodes. Their UTF-8 physical line counts must not increase; prefer equal replacement. No product logic, seed, V2, API, frontend, Child 2/3, external LLCR residual, or other test node change is authorized.

## Must Not Touch

- Existing oversized `tests/unit/test_confirmed_matrix_fee_draft_service.py` except the four-node tests-only exception above and read-only execution.
- `tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py` except the single exact tests-only exception above and read-only execution.
- `backend/modules/fee_evaluation/fee_default_fill.py` and `fee_default_fill_common.py`.
- Pricing-draft route, frontend model/page/tests.
- Seeds/manifest/rule identity, TASK_362A governance residuals, TASK_363D old Planner evidence, real DB/files, stage/commit/push.

## Validation Gate

Reviewer/User-approved contract first. Future validation must include bounded unit/service tests for manual Base Fee preservation, explicit rule-specific Base Fee preservation, automatic fallback `0`, single/multi-Group equivalence, no `matrix_group_count` trigger, metadata/source/fingerprint, LLCR/CR no-regression, V2 attestation/currentness/reviewed rebase/CAS checks, `py_compile`, and line-count gates.

## Integrator Closeout

Date: 2026-07-23

- Reviewer implementation re-gate and QA gate passed after the four authorized legacy assertion migrations.
- Integrator accepted only Child 1 product code, bounded tests, the exact four legacy assertion nodes, and lane governance.
- Child 2, Child 3, the twelve-path umbrella, default-fill/common, seeds/manifests, frontend, API/schema/database, and the external LLCR residual remain excluded.
- Remote push is not performed and this closeout does not activate Child 2.

## Stop Point

Child 1 is complete/accepted. Child 2 and Child 3 remain blocked until separately approved; the twelve-path umbrella is not an implementation authorization.
