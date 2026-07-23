# FEE_RULE_RESOLUTION_MATRIX_BASE_FEE_POLICY Reconciliation Planner Evidence

Date: 2026-07-23
Role: Planner
Status: `complete_accepted_after_integrator_packaging`

Task: `FEE_RULE_RESOLUTION_MATRIX_BASE_FEE_POLICY`
Lane: `fee-rule-resolution-matrix-base-fee-policy`
Parent: `FEE_DEFAULT_FILL_RESIDUAL_PACKAGE_RECONCILIATION`

## Reconciliation

- Reviewer umbrella/Child 1 plan re-gate passed.
- User approved Child 1 Developer planning-first only.
- Developer docs-only planning-first is complete.
- Child 1 previously reached Reviewer implementation-readiness gate.
- Reviewer implementation-readiness passed.
- User explicitly approved Child 1 product implementation.
- Child 1 product implementation was authorized and has now been reviewed; product code is locked pending the tests-only fix.
- Child 2 and Child 3 remain blocked.
- The twelve-path umbrella residual is planning evidence only and is not an implementation authorization.
- Reviewer implementation gate later confirmed the product implementation matches the Child 1 contract and the new bounded suite passed `23/23`, but blocked QA pending a formal tests-only scope reconciliation for four exact stale legacy assertions.

## Tests-Only Scope Reconciliation

Date: 2026-07-23

Authorized tests-only fix scope:

- `tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py::test_plain_contact_resistance_uses_llcr_when_matrix_has_no_explicit_llcr` must migrate to plain `CONTACT RESISTANCE` no LLCR fallback / typed review expectation.
- `tests/unit/test_confirmed_matrix_fee_draft_service.py::test_fee_draft_uses_temperature_rise_rule_for_current_rating` must migrate the superseded suggested Base Fee `500` / Testing Fee `3500` assertions to the accepted Base Fee precedence behavior.
- `tests/unit/test_confirmed_matrix_fee_draft_service.py::test_fee_draft_defaults_non_rise_temperature_items_to_per_hour[Long-term temperature cycle with load]` must migrate to rejected-alias no-rule/manual-review expectation.
- `tests/unit/test_confirmed_matrix_fee_draft_service.py::test_fee_draft_defaults_non_rise_temperature_items_to_per_hour[Long-term damp heat]` must migrate to rejected-alias no-rule/manual-review expectation.

The tests-only fix must not add lines to either legacy file. It must not modify product code, other test nodes, seeds, V2 modules, API, frontend, Child 2/3, external LLCR residual, real data/files, staging, commit, or push.

## Frozen Contract Retained

- Every Fee line uses proven manual Base Fee first, explicit accepted rule-specific Base Fee second, otherwise automatic Base Fee `0`.
- Single-Group and multi-Group use identical precedence; `matrix_group_count` must not decide whether fallback `0` is applied.
- Automatic default Base Fee metadata must identify the field as automatic default and bind source/fingerprint under accepted TASK_361L/TASK_363D V2 attestation/currentness/reviewed rebase/CAS/no-write semantics.
- Only `Long-term high temperature zone load` is approved as High temperature Life `15/per hour` with Units from explicit valid hours.
- `Long-term temperature cycle with load`, `Long-term damp heat`, and plain `CONTACT RESISTANCE` remain no-fallback/manual-review boundaries as recorded.

## Validation

- This was a governance-only reconciliation.
- No product code, tests, frontend, API client, schema, database, real DB/file, public-drive, generated artifact, stage, commit, or push action is authorized by this evidence.

## Integrator Closeout Reconciliation

Date: 2026-07-23

- The authorized four-node legacy assertion migration is complete; the Reviewer implementation re-gate and QA gate both passed.
- Integrator may package only the reconciled Child 1 source, three bounded test modules, the exact four legacy assertion nodes, and lane governance.
- Child 2, Child 3, the twelve-path umbrella, default-fill/common, seeds/manifests, frontend/API/schema/database, and the external LLCR residual remain excluded.
- Remote push is not performed. This closeout does not activate Child 2.

## Next Legal Role

User / Orchestrator task selection. Do not automatically start Child 2.
