# TASK_363D Developer Evidence

Date: 2026-07-19

Role: Developer

Status: ready_for_reviewer_implementation_gate

TASK_ID: `TASK_363D_FEE_PRICING_DRAFT_PRIOR_DEFAULTS_ATTESTATION`

Lane: `fee-pricing-draft-prior-defaults-attestation`

## Implementation Authorization

Reviewer implementation-readiness passed, the user explicitly approved product
implementation, and Planner reconciliation authorized this bounded Developer pass.
Schema/migration, repository, public API/client, frontend, Fee formula/rule/seed,
authority write, real database/file, TASK_363C/364B/365A, staging, commit, and push
remained locked.

## Repository Findings

- Current save builds automatic defaults once for provenance, then builds them again
  while independently rereading Point Profile and Measurement Plan for source context.
- Current load/rebase can repeat `_source_context()` and current-default provider reads.
  This can split values, safety, and lineage across different authority snapshots.
- `ConfirmedMatrixFeeDraftService.build_draft()` already reads Confirmed Matrix, rule
  library, effective Measurement Plan, and effective Point Profile in one application
  build, but returns only the flattened public draft boundary.
- `edited_values_from_fee_draft()` converts missing values to editable `0`/`1`, so it
  cannot be the source of row safety. Safety must be captured from the unflattened line
  and field metadata first.
- The production dependency already injects one correctly composed
  `ConfirmedMatrixFeeDraftService`; no API/dependency change is required if the
  persistence service consumes its private single-build result.
- `confirmed_matrix_fee_draft_service.py` is exactly 500 checked-out physical lines and
  includes external TASK_363C candidate hunks. The plan now requires a mechanical
  status/warning helper split, at most 20 TASK_363D orchestration lines in that service,
  a final service size below 480 lines, and hunk-level package isolation.
- Existing pricing-draft persistence and safe-rebase test modules are already above or
  near the hard line limit, so all TASK_363D coverage is assigned to four new bounded
  modules.

## Refined Contract

The plan now freezes two private immutable boundaries:

1. `ConfirmedMatrixFeeAuthorityBuildResult`, containing the draft and the exact Matrix,
   rule, Measurement Plan, and Point Profile facts read by that build.
2. `FeePricingDraftAutomaticBuildResult`, containing canonical automatic values,
   ordered existing row identities, pre-flattening row safety, captured Matrix for
   basic-fill validation, and exact source context derived from the first result.

The future `automatic_defaults_attestation` is a typed optional object inside existing
V2 `payload_json`. It binds generation, source-context fingerprint, canonical automatic
values/default fingerprint, ordered matrix+manual identities, ordered matrix-row safety,
and safety fingerprint under the existing whole-envelope fingerprint and validation
token. It copies no Measurement Plan targets and adds no database object.

CR safety is field-specific. `unit_price`, `unit_label`/serialized `unit_type`, `units`,
and `testing_fee` must be authoritative from the same target-first CR build. Missing or
unsafe target lineage/coverage/kind/readings/quantity/diagnostics blocks before
flattening. Manual CR Base Fee is recorded as nonrequired and does not falsely block
valid automatic values.

Save and load each perform one current authority build. Save derives basic-fill
validation, provenance, context, safety, and attestation from it before existing CAS.
Load passes the already-built current result into rebase policy. Reviewed save repeats
the same checks under CAS and requires reload as `current_v2`. Existing TASK_363A fee-
rule transition, TASK_361L merge/CAS/token/current-v2 consumer guards, V1 behavior, and
unattested-V2 fail-closed behavior remain unchanged.

## Exact Future May Touch

- `backend/application/confirmed_matrix_fee_draft_build_result.py` (new)
- `backend/application/confirmed_matrix_fee_draft_build_support.py` (new, mechanical
  existing status/warning/time helpers only)
- `backend/application/confirmed_matrix_fee_draft_service.py` (private result only,
  <=20 TASK_363D added lines, final <480 physical lines)
- `backend/application/fee_evaluation_pricing_draft_automatic_build.py` (new)
- `backend/application/fee_evaluation_pricing_draft_prior_defaults_attestation.py`
  (new)
- `backend/application/fee_evaluation_pricing_draft_v2_contract.py`
- `backend/application/fee_evaluation_pricing_draft_v2_authority_context.py`
- `backend/application/fee_evaluation_pricing_draft_persistence_service.py`
- `backend/application/fee_rule_transition_safe_rebase.py`
- Four new bounded test modules named in the plan
- TASK_363D task/plan/evidence and exact board row during later authorized governance

`backend/api/dependencies.py`, repository/schema, public routes/DTO/client, frontend,
Fee rules/formulae/seeds, authority writes, TASK_363C/364B, outputs, real DB/files, and
external residuals are locked. `fee_evaluation_pricing_draft_v2_rebase.py` and existing
TASK_361L consumer paths are read-only regression dependencies.

## Validation Plan

The plan names exact TDD nodes for single-build call counts, CR safety including manual
Base Fee, codec bounds/fingerprints, safe and unsafe Measurement Plan rebase, disposable
CAS/reload/current-v2 persistence, V1/unattested V2 compatibility, and no writer/artifact
calls. All new Python modules are capped below 500 physical lines, with smaller target
budgets recorded in the plan.

## Implemented Boundary

- Added the private immutable `ConfirmedMatrixFeeAuthorityBuildResult`; the existing
  public `build_draft()` delegates to one `build_authority_result()` call and returns
  only its draft as before.
- Mechanically extracted only the approved time, root-warning, and aggregate-status
  helpers. The core Fee draft service is now `479` UTF-8 physical lines and its Fee
  calculation, matching, and authority selection behavior was not changed by this
  lane.
- Added `FeePricingDraftAutomaticBuildResult`, deriving editable defaults, canonical
  ordered identities, pre-flattening row safety, captured Matrix, and exact source
  context from one authority result. Save/load counting fixtures prove one provider
  call and forbid compatibility provider rereads.
- Added the bounded, typed `fee-automatic-defaults:v1` codec. It validates generation,
  source-context/default/identity/safety fingerprints, ordering, duplicate identities,
  the 2,000-row cap, and the 1,048,576-byte cap before persistence CAS.
- Extended the existing V2 envelope with the optional server-owned attestation. No
  public DTO/client or SQLite shape changed; unattested V2 remains compatible and
  fail-closed when its source changes.
- Save and load now derive validation and source context from the same captured Matrix
  authority build. Reviewed Measurement Plan rebase requires safe saved/current rows,
  exact identities and compatible non-Measurement-Plan lineage, refreshes automatic CR
  Units/Testing Fee, and preserves only proven manual provenance.
- A disposable SQLite interleaving proves generation-2 reviewed save wins and a stale
  concurrent reviewed save raises the existing typed conflict without overwrite.
- Removed an intermediate unapproved persistence-helper split during implementation;
  final product/test paths are exactly within reconciled TASK_363D May Touch.

## Implementation Validation

- Four bounded TASK_363D modules: `27 passed`.
- Final combined TASK_363D + TASK_361L V1/V2 persistence/rebase + Confirmed Fee draft
  + default-fill + pricing API/export + disposable SQLite/CR read-only regressions:
  `169 passed`.
- The bounded suite includes unsafe current and saved CR evidence, all planned CR
  diagnostic classes, malformed safety fingerprint, identity/non-plan divergence,
  unattested V2 source change, changed-CR reviewed rebase, manual-field preservation,
  one-build call counts, and stale CAS no-overwrite.
- `py -m py_compile` passed for all nine candidate application modules.
- `git diff --check` passed; only existing LF/CRLF notices were emitted.
- UTF-8 trailing-whitespace scan passed for every candidate source/test file.
- UTF-8 physical lines: build result `29`, build support `49`, core Fee service `479`,
  automatic build `212`, persistence service `494`, attestation `253`, authority
  context `178`, V2 contract `256`, safe rebase `272`; bounded tests are `184`, `316`,
  `349`, and `261`. Every candidate Python file is below the 500-line hard limit.
- Staging is empty and targeted `data/` status is empty. No real database/file,
  artifact, frontend, API-client, schema/repository, stage, commit, or push action ran.
- Frontend build was not run because TASK_363D has no frontend/API-client diff; the
  existing API/export consumer regressions ran in the 169-test backend gate.
- External TASK_363C/364B/365A, Point Profile, parser, frontend, release/dist, and other
  dirty-worktree residuals were left unchanged and excluded.

## Blockers

None for Reviewer implementation review. TASK_363C remains blocked pending TASK_363D
acceptance and a later dependency-release reconciliation.

## Recommended Next Role

Reviewer implementation gate.
