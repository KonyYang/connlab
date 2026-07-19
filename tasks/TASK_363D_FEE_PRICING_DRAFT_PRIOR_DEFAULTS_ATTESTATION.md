# TASK_363D Fee Pricing Draft Prior Defaults Attestation

## Status

`complete / Integrator accepted`

## Lane

`fee-pricing-draft-prior-defaults-attestation`

## Current Phase / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Role: Planner source-of-truth reconciliation.
- TASK_363C B3 is complete, but B4 is blocked because accepted V2 persistence stores
  only the old defaults fingerprint and authority lineage metadata, not the prior
  automatic-default payload and per-row pre-flattening safety needed to attest a
  changed CR source.
- Reviewer plan re-gate passed; the user approved Developer planning-first; Developer
  completed a docs-only planning-first pass; Reviewer implementation-readiness passed;
  and the user explicitly approved TASK_363D product implementation.
- Implementation is authorized only within this task's exact May Touch and frozen
  contracts. TASK_363C remains blocked until TASK_363D is accepted or an explicit
  dependency-release gate says otherwise.

## Goal

Persist a server-generated, canonical prior automatic-default attestation bound to the
existing authority source context in Fee pricing-draft V2 `payload_json`. Use it to distinguish a safely
reviewable Measurement Plan lineage/default change from an unattested or unsafe change
without weakening TASK_361L fingerprints, row identity, manual provenance, CAS,
validation token, `current_v2`, or server consumer guards.

The attestation must never infer safety from flattened editable placeholders. A private
single-build result must preserve the full `FeeEvaluationDraft` line state and the same
read-only authority snapshots used to calculate it before producing editable values.

## Frozen Data Contract

The existing V2 envelope gains an optional, additive internal object:

```text
automatic_defaults_attestation:
  kind: fee-automatic-defaults:v1
  automatic_values_payload: canonical server-generated automatic Fee values
  automatic_defaults_fingerprint: exact source_context.automatic_defaults_fingerprint
  ordered_row_identity_fingerprint: canonical ordered row identities
  source_context_fingerprint: exact canonical saved source context
  row_safety: canonical per-row safety objects from the pre-flattened draft
  row_safety_fingerprint: canonical fingerprint of ordered row safety
  attested_generation: exact enclosing V2 generation
```

Rules:

- The server builds the attestation from current backend defaults during an explicit
  save. The client cannot submit or override it.
- One private server build must produce the `FeeEvaluationDraft`, editable automatic
  values, row safety, Confirmed Matrix facts, Point Profile facts, Measurement Plan
  facts, and source context. Calling providers again for another snapshot is forbidden.
- The attestation is included in the envelope canonical payload fingerprint and opaque
  validation token through the existing full-payload hash.
- The stored automatic-default fingerprint must equal
  `source_context.automatic_defaults_fingerprint`;
  ordered row identities must match the canonical automatic values and saved edited
  rows. Existing source context remains the authority-lineage attestation.
- Each row safety object contains stable edited-row identity, matched rule id, canonical
  automatic field states, `safe_for_rebase`, and typed diagnostic class/text. Its
  identity must match exactly one automatic row.
- Manual-required fields are not treated as failed automatic fields. A row is safe only
  when every field that would be refreshed automatically is proven safe from the full
  line metadata and authority result.
- For `fee_rule_contact_resistance_specified_current`, safety is derived from the actual
  target-first resolver against the same Confirmed Matrix and effective Measurement
  Plan snapshots. Omitted, excluded, affected, wrong-kind, mixed, diagnostic, missing
  lineage, invalid readings, or invalid owning Group quantity is always unsafe.
- `review_required`, `review_reason`, warnings, field metadata, and exact CR authority
  result are evaluated before `_rows_from_fee_line()` can turn missing values into
  editable `0`/`1` placeholders. Those placeholders can never prove safety.
- The attestation is limited to 2,000 automatic rows and 1,048,576 canonical UTF-8
  bytes. Exceeding either bound fails closed before CAS.
- Duplicate identities, missing required source metadata, malformed payload, excessive
  size, unknown attestation kind, or fingerprint mismatch fail closed before write.
- The existing SQLite table and `payload_json` column remain unchanged. No table,
  column, index, trigger, or data rewrite is planned.

## Compatibility And Migration

- Existing V1/unversioned payloads remain `legacy_unclassified` and are never rewritten
  by load.
- Existing V2 without attestation remains valid `current_v2` while its full source
  context/default fingerprint is unchanged.
- Existing V2 without attestation whose source changes is `blocked`; it cannot claim
  reviewed rebase and is not silently upgraded.
- A normal explicit save while context is current may write the additive attestation as
  the next CAS generation. Load and Cancel remain zero-write.
- New attested payloads remain readable by the accepted decoder shape because the
  field is additive and included in the canonical fingerprint. A code rollback may
  ignore the optional field and returns to the stricter old behavior; it does not
  delete or rewrite data.
- No public API/client shape changes are planned. Existing typed load status/reason,
  reviewed-save request, generation, snapshot fingerprint, and validation token remain
  the boundary. If implementation proves a new public DTO field is necessary, return
  to Planner/Reviewer before changing it.

## Safe Rebase Contract

An authority/default change may return `rebase_required` only when:

1. the saved envelope has a valid prior-default attestation;
2. Confirmed Matrix identity/revision and fee-rule version are compatible under the
   accepted TASK_361L transition rules;
3. Point Profile and every unrelated authority lineage satisfy existing policy;
4. the saved attestation fingerprint equals the saved source-context defaults
   fingerprint, source-context fingerprint, and generation, and its ordered row
   identities match saved edited rows;
5. every saved row safety object is valid and safe for its automatic fields;
6. one current server build returns values, safety, and context with matching ordered
   identities, and every corresponding current row is safe;
7. saved/current safety and source contexts are compatible under TASK_361L policy;
8. saved manual provenance can be merged deterministically over current defaults.

Changed automatic CR Units/Testing Fee then come from current backend defaults. Only
explicit manual fields proven by saved provenance may survive. Any missing attestation,
identity change, malformed/mixed authority, unsafe source, or incompatible mapping is
`blocked`/no-write. `rebase_required` remains non-consumable until explicit reviewed
save, CAS, reload, and server validation as `current_v2`.

## Authorized May Touch

- new bounded
  `backend/application/confirmed_matrix_fee_draft_build_result.py` for the private
  immutable authority-build result
- new bounded
  `backend/application/confirmed_matrix_fee_draft_build_support.py` for mechanical
  extraction of existing status/warning/time helpers only
- `backend/application/fee_evaluation_pricing_draft_v2_contract.py`
- new bounded
  `backend/application/fee_evaluation_pricing_draft_prior_defaults_attestation.py`
- new bounded
  `backend/application/fee_evaluation_pricing_draft_automatic_build.py` for the private
  immutable build result and pre-flattening row-safety classifier
- `backend/application/confirmed_matrix_fee_draft_service.py` only for a narrow private
  single-build result method/refactor that exposes the already-read draft, Confirmed
  Matrix, rule library, effective Point Profile, and effective Measurement Plan; no
  formula, matcher, authority-selection, or public DTO behavior change; first perform
  the mechanical helper extraction, add no more than 20 TASK_363D orchestration lines,
  and finish below 480 checked-out UTF-8 physical lines
- `backend/application/fee_evaluation_pricing_draft_persistence_service.py`
- `backend/application/fee_evaluation_pricing_draft_v2_authority_context.py` only to
  derive source context from the private single-build result without another provider
  read
- `backend/application/fee_rule_transition_safe_rebase.py`
- new bounded tests:
  - `tests/unit/test_fee_pricing_draft_prior_defaults_attestation.py`
  - `tests/unit/test_fee_pricing_draft_automatic_build_safety.py`
  - `tests/unit/test_fee_rule_transition_safe_rebase_measurement_plan.py`
  - `tests/integration/test_fee_pricing_draft_measurement_plan_rebase_attestation.py`
- TASK_363D task/plan/evidence and exact board row

The repository is expected to persist the opaque `payload_json` unchanged and is
read-only by default. Any proved repository change requires a Planner/Reviewer scope
re-gate before implementation.

## Must Not Touch / Locked Paths

- TASK_363C CR helper/routing/default-fill candidate and tests
- Fee formulas, rules, seeds, prices, discounts, Base Fee policy, or UI
- LLCR, Project Point Profile, and Measurement Plan schema/lifecycle/write paths
- frontend, API client, public DTO, or visual behavior
- TASK_361L five-state semantics, manual provenance, CAS/token/current-v2 consumer
  guards, Confirm/Update/export/Required Forms/Matrix rebase write boundaries
- workbook/Generic Test Record/Report, Matrix parser/import, LTR/public drive
- real database/files/artifacts, release/dist, TASK_364B, and external residuals
- `.agents/**`, `docs/project_management/**`, stage/commit/push

## Acceptance Criteria

1. Explicit save writes one canonical, server-generated attestation inside existing
   V2 `payload_json`; load and Cancel write nothing.
2. One provider build produces the pre-flattened draft, editable values, row safety,
   source context, and authority facts; a counting fixture proves no second authority
   read and no TOCTOU split.
3. Attestation defaults, ordered identities, per-row safety, source-context, generation,
   envelope fingerprint, and token all validate deterministically.
4. Existing V2 without attestation remains current when context is unchanged and is
   blocked when authority/defaults change; no background rewrite occurs.
5. Safe saved plus safe current Measurement Plan reconfirm with the same row identities
   and changed CR
   readings returns `rebase_required`; reviewed merge refreshes automatic CR
   Units/Testing Fee and preserves only proven manual fields.
6. Every current CR target state that is review-required, omitted, excluded, affected,
   wrong-kind, mixed, diagnostic, missing-lineage, invalid-readings, or invalid-owning-
   quantity is unsafe and returns `blocked` even when row identity is unchanged.
7. Unsafe/malformed saved row safety, missing safety, changed safety identity,
   defaults/safety/context fingerprint divergence, duplicate/mixed source, stale CAS,
   invalid token, or unsafe authority is typed blocked/conflict with no overwrite,
   Confirmed Fee write, writer call, or artifact.
8. Reviewed save increments generation atomically, reloads, and must validate
   `current_v2` before any production consumer is permitted.
9. Repeated save/rebase is idempotent under the accepted generation/CAS contract;
   concurrent stale attempts return typed `409` and do not overwrite.
10. V1, unattested V2, current attested V2, rollback reader, and malformed payload
   compatibility are covered with disposable SQLite/API tests.
11. TASK_363C, TASK_364B, frontend/API client, Fee rules/seeds, authority writes, and
   real DB/files receive no TASK_363D diff.

## Validation Gate Draft

```powershell
py -m pytest tests/unit/test_fee_pricing_draft_prior_defaults_attestation.py -q
py -m pytest tests/unit/test_fee_pricing_draft_automatic_build_safety.py -q
py -m pytest tests/unit/test_fee_rule_transition_safe_rebase_measurement_plan.py -q
py -m pytest tests/integration/test_fee_pricing_draft_measurement_plan_rebase_attestation.py -q
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_v2_rebase.py tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py -q
py -m pytest tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py -q
py -m py_compile backend/application/confirmed_matrix_fee_draft_service.py backend/application/fee_evaluation_pricing_draft_automatic_build.py backend/application/fee_evaluation_pricing_draft_v2_contract.py backend/application/fee_evaluation_pricing_draft_prior_defaults_attestation.py backend/application/fee_evaluation_pricing_draft_persistence_service.py backend/application/fee_evaluation_pricing_draft_v2_authority_context.py backend/application/fee_rule_transition_safe_rebase.py
git diff --check
```

Also require disposable SQLite no-real-mutation checks, payload-size/duplicate identity
fail-closed cases, V1/V2 compatibility, consumer no-write/no-artifact checks, physical
line limits, exact whitelist, trailing whitespace, and package isolation.

## Dependencies And Merge Gate

TASK_361L is the accepted contract and implementation baseline. TASK_363D must be
reviewed, explicitly approved, implemented, reviewed, QA-validated, and accepted before
TASK_363C can resume B4 or seek renewed implementation authorization. TASK_364B is
independent and must remain hunk-isolated.

## Definition Of Ready

Reviewer implementation-readiness passed and the user explicitly approved product
implementation. The operator outcome, persisted boundary, compatibility, rollback,
May Touch, locks, acceptance, validation, line-count split, and package isolation are
explicit. Status is `implementation authorized / pending Developer implementation`.

## Next Legal Role

Developer implementation pass.
