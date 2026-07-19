# TASK_363D Reviewer Plan Gate

Date: 2026-07-19

Role: Reviewer

Status: reviewer_blocked

TASK_ID: `TASK_363D_FEE_PRICING_DRAFT_PRIOR_DEFAULTS_ATTESTATION`

Lane: `fee-pricing-draft-prior-defaults-attestation`

## Review Result

The proposed additive `payload_json` attestation is the right non-destructive
direction for preserving prior automatic defaults across a genuine Measurement Plan
change. It correctly avoids SQLite DDL, repository/schema changes, target-snapshot
copying, background rewrites, and public API/client changes. Binding canonical
server-generated defaults to the V2 envelope, source context, CAS generation, and
existing manual provenance can address the prior-default fingerprint gap found in
TASK_363C B4.

However, the plan cannot yet enforce its required fail-closed rule for unsafe current
Measurement Plan authority.

## Blocking Finding: Values-Only Attestation Loses Current Authority Safety

`current_automatic_values()` maps a `FeeEvaluationDraft` to
`FeeEvaluationEditedExportValues`. That conversion intentionally serializes missing
automatic fields as editable `0`/`1` fallbacks and does not preserve the originating
line's `review_required`, review reason, field metadata, exact CR authority, target
coverage, or diagnostic state. The current V2 source context also records only a
whole-plan status/revision/fingerprint.

As written, the proposed attestation stores canonical editable automatic values plus
row identities. It therefore cannot distinguish a current CR line whose exact target
is omitted, excluded, wrong-kind, affected, or otherwise review-required from an
ordinary numeric defaults row with the same identity. Returning `rebase_required` in
that state would violate the frozen requirement that unsafe authority is
`blocked`/no-write/no-artifact. A whole-plan `partial_compatible` or `needs_review`
status is not sufficient to decide whether the specific Fee row remains safe.

## Required Planner Fix

Keep the no-DDL/no-target-snapshot boundary, but make the future data contract
implementable by defining a private, server-generated automatic-default build result
that includes both:

1. canonical editable automatic values for the prior-default attestation; and
2. a canonical per-row safety attestation derived directly from the current Fee draft
   before it is flattened to editable values. It must identify the stable Fee row
   identity and whether automatic values are safe to rebase; for CR rows it must
   reflect the already-resolved exact target authority and reject review-required,
   omitted, excluded, affected, wrong-kind, mixed, or diagnostic states.

The saved attestation must explicitly bind this safety object and the exact canonical
source-context fingerprint inside the envelope fingerprint. Rebase must rebuild the
current values and current safety evidence once, require both saved and current
matching-safe identities, then merge only accepted manual provenance. Any absent,
malformed, duplicate, oversize, or unsafe safety evidence remains typed
`blocked`/zero-write.

The revised plan must specify the smallest allowed module boundary for producing that
evidence. It may reuse the existing read-only Fee-draft provider, but must not change
Fee formulas/rules, authority write paths, V2 consumer guards, public DTO/API/client,
or copy Measurement Plan target snapshots. Add bounded test cases for an unsafe
current exact CR target despite stable row identity, an unsafe saved attestation, and
the required no-write/no-artifact outcomes.

## Verification

- Read AGENTS, board, TASK_363D task/plan/Planner and TASK_363C dependency evidence,
  the prior Reviewer B4 finding, and accepted TASK_361L evidence.
- Reviewed the V2 envelope/source-context codec, pricing-draft persistence and CAS
  flow, transition/rebase policy, manual provenance, and automatic Fee-draft-to-edit
  mapping.
- Confirmed `edited_values_from_fee_draft()` flattens absent automatic fields to
  fallback values and does not carry line review state or field metadata.
- Confirmed board state: TASK_363D is planned-only and TASK_363C remains blocked by
  this dependency. No product code/tests, real DB/files, staging, commit, or push
  were performed by Reviewer. External TASK_363C/TASK_364B and dirty-worktree
  residuals remain excluded.

## Decision

`reviewer_blocked`

Recommended next role/action: Planner docs-only fix, then Reviewer plan re-gate.
Implementation remains unauthorized; do not resume TASK_363C or request Developer
implementation approval yet.

---

# TASK_363D Reviewer Plan Re-Gate

Date: 2026-07-19

Role: Reviewer

Status: reviewer_pass

TASK_ID: `TASK_363D_FEE_PRICING_DRAFT_PRIOR_DEFAULTS_ATTESTATION`

Lane: `fee-pricing-draft-prior-defaults-attestation`

## Re-Gate Result

Planner B1 is closed. The revised design no longer infers authority safety from
flattened editable values. One private, read-only build produces the unflattened
`FeeEvaluationDraft`, canonical editable defaults, stable ordered identities,
pre-flattening row safety, and exact source context from the same Confirmed Matrix,
effective Measurement Plan, and Point Profile facts. The contract expressly prohibits
a second provider read for that pair, preventing a TOCTOU split between automatic
values, safety evidence, and lineage.

The additive `automatic_defaults_attestation` is now sufficiently bound: it carries
the automatic values/default fingerprint, ordered identity fingerprint, canonical
row-safety objects/fingerprint, source-context fingerprint, and enclosing generation
inside the existing canonical V2 payload. The decoder, payload hash, and validation
token retain their existing integrity roles. There is no target snapshot copy, SQLite
DDL, schema/model/repository change, background rewrite, or public DTO/client change.

## Safety And Rebase Contract

Per-row safety is explicit and implementable from the unflattened draft: stable
identity, row kind, matched rule, automatic field states, `safe_for_rebase`, and a
typed diagnostic. For CR it must come from the same target-first resolver result, so
missing lineage/readings, invalid owning quantity, omitted/excluded/affected/wrong-
kind/mixed/diagnosed targets, or any review-required automatic authority are blocked
before flattening. An intentional manual CR Base Fee review does not invalidate
otherwise authoritative automatic Units or Unit Price.

Rebase independently validates saved attestation/safety/context/generation, builds
current values+safety+context once, requires matching identities and safety on both
sides, then applies existing provenance merge. Reviewed save repeats the evidence
checks under the existing CAS boundary and reloads as `current_v2`. V1 and unattested
V2 compatibility remain fail-closed under source change; rollback merely ignores the
optional field and returns to the stricter old transition behavior.

## Scope And Validation

- The four bounded test modules cover codec/attestation, single-build call count and
  row safety, transition policy, and disposable persistence/API rebase behavior.
- The permitted `confirmed_matrix_fee_draft_service.py` refactor is private,
  facts/result-only, capped at 20 added physical lines, and must keep the file at or
  below 500 lines. No Fee formula/rule/authority-selection behavior is authorized.
- Existing TASK_361L V2 generation, CAS, token, manual provenance, reload/revalidation,
  and current-v2-only consumer guards are locked and run only as regressions.
- TASK_363C candidate, TASK_364B, frontend/API client, Fee rules/seeds/UI, authority
  writes, outputs, real DB/files, and external worktree residuals remain excluded.
- Read AGENTS, board, TASK_363D task/plan/Planner evidence, prior Reviewer finding,
  TASK_363C dependency evidence, and current V2 envelope/source-context/persistence/
  safe-rebase/Fee-draft mapping code. The Planner pass is governance-only; staging is
  empty and no product/test/real-data mutation occurred.

## Decision

`reviewer_pass`

Recommended next role/action: User approval for a Developer planning-first pass only.
Implementation remains unauthorized, and TASK_363C must remain blocked until TASK_363D
is accepted and its dependency reconciliation completes.

---

# TASK_363D Reviewer Implementation-Readiness Gate

Date: 2026-07-19

Role: Reviewer

Status: reviewer_pass

TASK_ID: `TASK_363D_FEE_PRICING_DRAFT_PRIOR_DEFAULTS_ATTESTATION`

Lane: `fee-pricing-draft-prior-defaults-attestation`

## Readiness Result

Developer planning-first is docs-only and makes the implementation sequence concrete.
The private `ConfirmedMatrixFeeAuthorityBuildResult` exposes the same confirmed
Matrix, rule library, effective Measurement Plan, effective Point Profile, and
unflattened Fee draft that one existing authority build already reads. The subsequent
automatic-build result derives basic-fill validation from that captured Matrix and
derives editable values, ordered identities, pre-flattening safety, and source context
from the same facts. This removes the current double defaults/provider reads without
introducing a public API or storage boundary.

The save/load/rebase sequence is complete enough to implement: validate saved
attestation and safety independently; perform one current build; require matching safe
identities/context; merge only accepted manual provenance; then repeat checks beneath
the existing CAS and reload as `current_v2`. The V2 attestation remains optional for
compatibility, server-owned, canonical, bounded, and inside the existing payload/token
integrity boundary. V1 and unattested V2 behavior stays fail-closed after a source
change, while rollback can ignore the additive object.

## Scope And Risk Review

- `confirmed_matrix_fee_draft_service.py` is currently 500 physical lines, so the
  plan correctly requires a mechanical status/warning/time-helper extraction before
  adding the private result method. The service must finish below 480 lines and the
  TASK_363D orchestration hunk is capped at 20 lines; no calculation, rule, or
  authority-selection behavior may move or change.
- The exact new helper modules, codec/persistence/policy changes, and four bounded
  test modules are named. Tests cover single-build call counts, manual CR Base Fee
  non-blocking behavior, safe/unsafe CR target states, malformed and divergent
  attestation evidence, V1/unattested V2 compatibility, CAS/reload/current-v2,
  no-write/no-artifact consumers, and rollback.
- Schema/repository, routes/DTO/client/frontend, Fee formulas/rules/seeds/UI,
  authority writes, TASK_363C candidate, TASK_364B, real DB/files, and external
  residuals remain locked. Existing TASK_361L generation/CAS/token/provenance and
  consumer-guard paths are regression-only dependencies.

## Verification

- Read AGENTS, board, TASK_363D task/plan/Planner/Developer/Reviewer evidence,
  TASK_363C dependency state, current Fee-draft service, V2 envelope/source-context,
  persistence, and safe-rebase implementation.
- Confirmed the planning-first pass changed only its plan and Developer evidence;
  targeted no-index diff/trailing checks are clean and the stated plan/evidence counts
  are 428/123 physical lines. No product/test/schema/API-client/real-data operation,
  staging, commit, or push occurred.

## Decision

`reviewer_pass`

Recommended next role/action: User implementation approval followed by Planner final
source-of-truth reconciliation. Do not start Developer implementation until that
authorization checkpoint is recorded. TASK_363C remains blocked by TASK_363D.

---

# TASK_363D Reviewer Implementation Gate

Date: 2026-07-19

Role: Reviewer

Status: reviewer_pass

TASK_ID: `TASK_363D_FEE_PRICING_DRAFT_PRIOR_DEFAULTS_ATTESTATION`

Lane: `fee-pricing-draft-prior-defaults-attestation`

## Result

The candidate passes the implementation gate. `build_draft()` now delegates to one
private `build_authority_result()` call. The automatic-build boundary derives editable
defaults, ordered identities, pre-flattening field safety, captured-Matrix validation,
and source context from that same result, without rereading compatibility providers.

The optional `fee-automatic-defaults:v1` attestation is server-built inside the
existing V2 payload. Its canonical validation binds the envelope generation, source
context, defaults fingerprint, ordered identities, and row-safety evidence. Malformed,
duplicate, oversized, mismatched, or unsafe evidence fails closed. The CR required
automatic fields are checked before flattening; Base Fee remains nonrequired, so a
manual CR Base Fee does not block otherwise authoritative defaults.

Measurement Plan-only rebase is deliberately narrow: Matrix, fee-rule, and Point
Profile lineage must match; saved and current row identities and safety must match and
be safe; the saved attestation must decode against the saved V2 context. Only then is
existing provenance merge applied. The reviewed save still uses the established CAS
and returns `current_v2`; stale competing save is typed and leaves the winner intact.
V1 and unattested V2 source changes remain blocked.

## Scope And Isolation

- The service helper extraction is mechanical. The TASK_363D private-result hunk is
  isolated from the existing TASK_363C CR-routing and unrelated fee-policy hunks in
  `confirmed_matrix_fee_draft_service.py`.
- No schema, repository, public API/client, frontend, Fee rule/seed/formula, authority
  write, workbook, generic output, real database/file, or TASK_363C product change is
  part of this candidate. `TASK_363C` remains blocked pending TASK_363D acceptance and
  a separate dependency-release reconciliation.
- All inspected candidate Python files are below the 500-line hard limit (largest
  observed: persistence service 447 and core Fee service 450 under the checked-out
  UTF-8 line-count method). Staging and `data/` status are empty.

## Verification

- `py -m pytest` four bounded TASK_363D modules: `27 passed`.
- V2 persistence/rebase/export regression set: `23 passed`.
- Confirmed-Matrix/default-fill/pricing-compatibility/export regression set: `111
  passed`.
- `py -m py_compile` passed for all nine candidate application modules.
- Candidate `git diff --check`, UTF-8 trailing-whitespace, line-count, staging, and
  targeted scope scans passed; LF/CRLF notices are pre-existing working-copy warnings.
- One excluded adjacent LLCR API regression currently fails (`expected units 20`, got
  `None`) in `test_fee_draft_api_uses_confirmed_point_profile_for_llcr_units`. The
  test is unchanged and the responsible LLCR/Point Profile routing hunk is outside
  TASK_363D; it is recorded as an external dirty-worktree residual, not absorbed by
  this lane.

## Decision

`reviewer_pass`

Recommended next role/action: QA gate for TASK_363D only. Do not route Integrator and
do not release or resume TASK_363C.
