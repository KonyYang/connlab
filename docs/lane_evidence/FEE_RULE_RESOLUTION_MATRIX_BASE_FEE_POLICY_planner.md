# FEE_RULE_RESOLUTION_MATRIX_BASE_FEE_POLICY Planner Evidence

Date: 2026-07-23
Role: Planner
Status: `product_reviewed_pending_developer_tests_only_fix`

This formal child lane was created from Reviewer B1/B2 for `FEE_DEFAULT_FILL_RESIDUAL_PACKAGE_RECONCILIATION`.

Implementation remains unauthorized.

User decisions recorded on 2026-07-23:

- Latest User command supersedes the earlier no-family/no-op checkpoint.
- Final Base Fee fallback: every Fee line uses proven manual Base Fee first, explicit accepted rule-specific Base Fee second, otherwise automatic Base Fee `0`; manual and rule-specific Base Fee values are never overwritten.
- Single-Group and multi-Group use identical precedence; `matrix_group_count` must not decide whether to fill `0`. Candidate `matrix_group_count > 1` blanket zero logic must be rewritten before implementation.
- Automatic default `0` metadata must mark Base Fee as automatic default and bind source/fingerprint under TASK_361L/TASK_363D V2 attestation/currentness/reviewed rebase/CAS/no-write semantics.
- 2B: only `Long-term high temperature zone load` is approved as High temperature Life, `15/per hour`, Units from explicit hours only; `Long-term temperature cycle with load` and `Long-term damp heat` are not approved.
- 3B: plain `CONTACT RESISTANCE` must not fallback to LLCR.

No Base Fee family-list blocker remains because no whitelist is required. Reviewer umbrella/Child 1 plan re-gate passed; the User approved Child 1 Developer planning-first; Developer docs-only planning-first is complete; Planner source-of-truth reconciliation is complete; Reviewer implementation-readiness passed; the User explicitly approved Child 1 product implementation. Reviewer implementation gate found the product implementation matches the Child 1 contract and the new bounded suite passed `23/23`, but QA is blocked until four exact stale legacy assertions are migrated. Product code is locked; the next action is a Developer tests-only fix pass.

Exact future product May Touch is limited to `confirmed_matrix_fee_draft_service.py` narrow hunks and the two bounded helper modules named in the task, plus new bounded tests. Existing oversized tests are read-only only.

## Source-Of-Truth Reconciliation

Date: 2026-07-23

- Reviewer umbrella/Child 1 plan re-gate: passed, per umbrella Reviewer evidence.
- User authorization: Child 1 Developer planning-first completed earlier; Child 1 product implementation is now explicitly authorized after Reviewer implementation-readiness. Child 2/3 and the umbrella twelve-path package remain unauthorized.
- Developer docs-only planning-first: complete, per `docs/lane_evidence/FEE_RULE_RESOLUTION_MATRIX_BASE_FEE_POLICY_developer.md`.
- Reviewer implementation-readiness: passed, per `docs/lane_evidence/FEE_RULE_RESOLUTION_MATRIX_BASE_FEE_POLICY_reviewer.md`.
- User product implementation approval: explicit for Child 1 only.
- Current Child 1 state: product reviewed / pending Developer tests-only fix; product code locked.
- Child 2 / Child 3: blocked until Child 1 metadata/default contract is accepted.
- Umbrella twelve-path residual: not an implementation authorization and not a whole-package May Touch grant.

## Final Authorization Reconciliation

Date: 2026-07-23

- Authorized scope is Child 1 only: rule resolution plus general Base Fee fallback/precedence/metadata, exact hunk ownership, bounded tests, and any mechanical split required to keep product Python `<500`.
- Child 2 and Child 3 remain blocked.
- The twelve-path umbrella is not an implementation authorization.
- Frontend, schema, database, API client, seeds/manifest, real DB/files/generated artifacts, and external residuals remain locked.

## Tests-Only Scope Reconciliation

Date: 2026-07-23

Reviewer implementation gate froze four exact stale legacy assertion migrations:

- `tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py::test_plain_contact_resistance_uses_llcr_when_matrix_has_no_explicit_llcr`.
- `tests/unit/test_confirmed_matrix_fee_draft_service.py::test_fee_draft_uses_temperature_rise_rule_for_current_rating`.
- `tests/unit/test_confirmed_matrix_fee_draft_service.py::test_fee_draft_defaults_non_rise_temperature_items_to_per_hour[Long-term temperature cycle with load]`.
- `tests/unit/test_confirmed_matrix_fee_draft_service.py::test_fee_draft_defaults_non_rise_temperature_items_to_per_hour[Long-term damp heat]`.

Only assertion/fixture expectation migration for those nodes is authorized. The two legacy files remain locked outside those nodes; their UTF-8 physical line counts (`223` and `684`) must not increase. Product logic, other tests, Child 2/3, external LLCR residual, and the twelve-path umbrella remain excluded.
