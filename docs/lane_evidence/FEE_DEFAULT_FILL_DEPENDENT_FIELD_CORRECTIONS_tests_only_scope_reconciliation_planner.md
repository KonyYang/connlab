# FEE_DEFAULT_FILL_DEPENDENT_FIELD_CORRECTIONS Tests-Only Scope Reconciliation

Date: 2026-07-24
Role: Planner
Status: `completed_reviewer_pass_product_locked`
Task: `FEE_DEFAULT_FILL_DEPENDENT_FIELD_CORRECTIONS`
Lane: `fee-default-fill-dependent-field-corrections`

## Reviewer Result

Reviewer B1 passed production routing. Only
`fee_rule_high_temperature_life` and `fee_rule_salt_spray_nss` use typed
confirmed duration authority. The four accepted legacy rule families retain
their prior behavior. Product code is locked.

## Exact Tests-Only Authorization

The only writable assertion locations are:

1. `tests/unit/test_fee_default_fill.py::test_temperature_named_duration_rules_default_base_fee_to_zero_without_duration[fee_rule_high_temperature_life-Temperature life-unit_price0]`.
2. `tests/unit/test_fee_default_fill.py::test_salt_spray_uses_hour_duration_from_matrix_condition`.
3. `tests/unit/test_confirmed_matrix_fee_draft_service.py::test_fee_draft_defaults_non_rise_temperature_items_to_per_hour[Long-term high temperature zone load]`.
4. `tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py::test_approved_temperature_alias_uses_hours_and_common_base_fee[1]`.
5. The same parameterized node at `[2]`.
6. `tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py::test_approved_temperature_alias_without_hours_keeps_dependencies_pending`.

Items 4 and 5 are two cases of one assertion location, yielding five exact
locations and six pytest cases.

Allowed expectation changes:

- High-temperature/Salt Spray without typed confirmed owning-row duration
  authority is manual-review/no-write.
- Condition text cannot supply duration authority.
- Valid exact owning-row authority is required for Units and Testing Fee.
- Missing/invalid diagnostics identify the typed confirmed authority
  requirement.

No other assertion or fixture semantics may change. Temperature & Humidity is
an unchanged regression guard. Current blank-inclusive physical-line counts
are:

- `tests/unit/test_fee_default_fill.py`: `912`;
- `tests/unit/test_confirmed_matrix_fee_draft_service.py`: `683`;
- `tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py`: `301`.

The oversized files must not increase; prefer line-neutral replacement. New
coverage, if required, belongs only in existing approved bounded modules.

## Locked External Dependency

Historical B2 note: the TASK_366C-owned Matrix Editor composition defect was
excluded from Child 2. Its owner subsequently restored `method_authority`, and
Reviewer closed those failures. It is no longer the QA blocker.

Child 3 and the umbrella remain blocked. No product code, schema, API, frontend,
seed, real data, stage, commit, or push is authorized by this reconciliation.

Closure: Developer completed this exact High/Salt assertion migration and
Reviewer passed it. The later Fee-rebase fixture-context residual is separately
owned by the external residual reconciliation and is not part of this evidence.
