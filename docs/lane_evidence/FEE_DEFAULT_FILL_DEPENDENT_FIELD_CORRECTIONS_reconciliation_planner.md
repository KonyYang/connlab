# FEE_DEFAULT_FILL_DEPENDENT_FIELD_CORRECTIONS Final Authorization Reconciliation

Date: 2026-07-24
Role: Planner
Status: `reviewer_pass_qa_pass_ready_for_integrator_packaging`
Task: `FEE_DEFAULT_FILL_DEPENDENT_FIELD_CORRECTIONS`
Lane: `fee-default-fill-dependent-field-corrections`
Parent: `FEE_DEFAULT_FILL_RESIDUAL_PACKAGE_RECONCILIATION`

## Gate Facts

- Child 1 `FEE_RULE_RESOLUTION_MATRIX_BASE_FEE_POLICY` is complete/accepted at `c5d91c36c5e1d54885fc0a3b406c92ff9aa0cb6b` and remains read-only.
- User approved Option 1 additive typed duration authority.
- Developer docs-only planning-first completed.
- Planner reconciled the complete publication, carry-forward, session, signature, and mechanical-split scope.
- Reviewer scope and implementation-readiness re-gate passed.
- User explicitly authorized Child 2 product implementation.

## Authorized Boundary

- Structured selected source-to-draft authority transport.
- First Confirm Matrix publication.
- Revision carry-forward and revision confirmation.
- Matrix Editor source replacement, session persistence, and canonical signature binding.
- Confirmed owning-row Fee consumption from the same authority build.
- `Long-term high temperature zone load` only: Unit Price `15`, Unit Type `per hour`, Units equal `normalized_hours`.
- Typed no-write/manual-review for invalid, missing, stale, conflicting, or wrong-row authority.
- Mandatory behavior-preserving splits, all candidate Python below 500 physical lines, bounded tests, disposable DB/API/frontend validation, and mixed-file hunk isolation.

Confirm Matrix remains the sole publication boundary. Duration inference from arbitrary text, legacy Step quantity, readings, Point Profile, LLCR/CR, saved draft values, or another row/Group remains forbidden.

## Locked Boundary

- Accepted Child 1 Base Fee final value and metadata are read-only; Child 2 cannot modify, recalculate, classify, or re-attest them.
- TASK_361L/TASK_363D attestation, currentness, reviewed rebase, CAS/no-write, and manual-field protection remain authoritative.
- Child 3 and the twelve-path umbrella remain blocked and unauthorized.
- Fee hydration, seeds/manifest, real databases/files, generated artifacts, unrelated residuals, whole-file mixed staging, stage, commit, and push remain outside this Planner action.

## Planner Action

Only governance documents were reconciled. No product code, tests, schema, database, frontend, API client, real data, or generated artifact was modified or accessed.

Historical authorization route (completed): Developer implementation pass for Child 2 exact authorized scope.

## Reviewer B1 Tests-Only Scope Reconciliation

Reviewer accepted the production routing and locked all Child 2 product code.
The remaining authorized work is limited to five exact assertion locations
and six pytest cases:

1. `tests/unit/test_fee_default_fill.py::test_temperature_named_duration_rules_default_base_fee_to_zero_without_duration[fee_rule_high_temperature_life-Temperature life-unit_price0]`.
2. `tests/unit/test_fee_default_fill.py::test_salt_spray_uses_hour_duration_from_matrix_condition`.
3. `tests/unit/test_confirmed_matrix_fee_draft_service.py::test_fee_draft_defaults_non_rise_temperature_items_to_per_hour[Long-term high temperature zone load]`.
4. `tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py::test_approved_temperature_alias_uses_hours_and_common_base_fee[1]`.
5. The same parameterized node at `[2]`.
6. `tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py::test_approved_temperature_alias_without_hours_keeps_dependencies_pending`.

Only assertion/expectation migration to the accepted typed confirmed duration
authority contract is allowed. No fixture business semantics, Temperature &
Humidity guard, other legacy rule, product code, fallback, or diagnostic
outside these nodes may change. Existing oversized files must not gain
physical lines.

The external TASK_366C missing `method_authority` composition remains excluded
from this lane and must be corrected by its owner before QA. Child 3 and the
umbrella remain blocked.

Historical High/Salt route (completed): Developer bounded tests-only fix, then
Reviewer implementation re-gate.

## External Fee-Rebase Fixture Context Reconciliation

The remaining `preserved_count` failure is a stale fixture context, not a
production regression. The integration fixture persists and queries
`fee_rules_v2026_06_03`; Matrix Editor correctly uses accepted active
`fee_rules_v2026_07_17_r6`. TASK_361L/TASK_363D exact currentness therefore
requires no source match and `preserved_count=0`.

Planner's disposable in-memory replay changed only both obsolete version
literals to r6 and passed the full exact lifecycle node.

No tests-only change is authorized yet. Proposed scope is one file, one node,
and two line-neutral literal replacements. No assertion, product, fixture
pricing values, provenance, CAS, rebase, fallback, TASK_366C, Child 3, or
umbrella change is included.

Next legal role: Reviewer tests-only scope confirmation.

## Final Gate Reconciliation

The two fixture-context migrations were subsequently authorized, implemented,
and independently re-gated. QA passed the Child 2 bounded, rebase, V2,
legacy, publication, and frontend payload validation suites. This evidence
therefore releases only Integrator packaging/readiness. Child 1 remains
read-only; Child 3 and the parent umbrella remain blocked.
