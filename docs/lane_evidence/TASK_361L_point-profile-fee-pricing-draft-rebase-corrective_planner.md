# TASK_361L Point Profile Fee Pricing Draft Rebase Corrective Planner Evidence

Date: 2026-07-15

Role: Planner

Status: Reviewer implementation-readiness re-gate passed / User implementation
approval recorded / implementation authorized / pending Developer implementation

## Current Phase / Why Allowed

Phase 11 controlled Matrix foundation. TASK_361K is complete/accepted in local commit
`4a70ae9ac118c946da65415c20c2fb74eaf0bb94`, no implementation lane was active, and
the user requested a separate post-acceptance corrective rather than reopening
TASK_361K.

## Confirmed User Evidence

- Real read-only backend output correctly calculated Point Profile-based LLCR Units
  `15` and `9` for group sample quantities `5` and `3`.
- The browser displayed `1` for those rows after loading a saved pricing draft.
- Saved pricing freshness must include confirmed Point Profile lineage.
- Compatible manual pricing edits must survive rebase, but uncertain legacy fields
  must fail closed rather than be guessed.
- No real database/file write or product implementation is allowed in this pass.

## Repository Evidence

- Pricing draft context currently contains only Confirmed Matrix id/revision and
  fee-rule version.
- Storage is one JSON payload keyed by that tuple; payload rows have complete values
  but no schema version, source fingerprint, or per-field provenance.
- Frontend hydration applies every saved editable row field, including Units, over the
  freshly calculated source preview.
- The page already knows which field receives an operator edit, but discards that
  identity when serializing the draft.
- TASK_361K's accepted adapter exposes confirmed Point Profile revision/id/fingerprint
  and calculated readings/sample through a read-only boundary.
- Existing working-tree changes are unrelated TASK_361F operational evidence and
  TASK_361H QA images; they are excluded.

## Planner Decision

Create one formal corrective lane. Use a typed V2 pricing-draft JSON envelope in the
existing table rather than an additive SQLite schema migration. V2 binds the saved
draft to Matrix/rule/profile and a canonical automatic-defaults fingerprint, and
persists explicit manual field sets. Legacy V1 remains stored but is unclassified and
cannot hydrate or autosave silently.

For profile-only compatible rebase, LLCR Units and testing fee refresh from current
backend defaults; explicitly edited spend time, unit price, unit type, base fee,
discount, and notes are preserved. CR/non-LLCR semantics remain unchanged. Matrix,
rule, source-row, missing/corrupt profile, or malformed provenance states fail closed.

## Reviewer B1 And Resolution

Reviewer correctly found a server-side consumption gap:

- `ConfirmedFeeVersionService._require_current_pricing_snapshot()` currently rejects
  only `missing` and `stale`, so a newly named non-current state could fall through.
- Browser generation posts an edited payload directly to the export route, and the
  export service validates row shape but does not bind it to a saved current pricing
  snapshot.
- Required Forms trusts Confirmed Fee `current`, while currentness currently compares
  only Matrix/rule context; child export and Matrix rebase construct services through
  separate production paths.

The fixed contract now freezes:

1. Five states only: `missing`, `current_v2`, `rebase_required`,
   `legacy_unclassified`, and `blocked`. Existing `stale` maps to
   `rebase_required`. Only `current_v2` is consumable.
2. Explicit reviewed-rebase order: read current defaults -> provenance merge ->
   visible review -> atomic V2 save -> server reload/revalidation -> Update/export.
   Load and Cancel remain zero-write.
3. An opaque validation token binds draft id, source-context fingerprint, and
   canonical payload fingerprint. Confirm and export must revalidate it server-side.
4. Direct edited export payloads must fingerprint-match the validated saved V2, and
   the writer receives server-loaded values. Raw payload-only calls fail before any
   filesystem/writer/output side effect.
5. Confirmed Fee, all direct/browser/child exports, Required Forms, Matrix Fee rebase
   promotion, and production dependency composition receive the same guard. Confirmed
   Fee JSON retains V2 lineage so Required Forms' existing current gate observes
   profile/default staleness.
6. Disposable tests reject V1 and every non-current/mismatched state at each consumer,
   with no draft overwrite, Confirmed Fee write, writer call, output/artifact, or
   required-form placement. Reviewed V2 then permits UI `15`/`9` and production use.

## Scope / Isolation

Future May Touch includes the pricing-draft persistence/application/route/client/Fee
page boundary plus the narrow Confirmed Fee, direct export, child export, Required
Forms current guard, Matrix rebase promotion, and dependency-composition paths listed
exactly in the task. Those additions only enforce V2 currentness and do not change Fee
pricing, workbook layout, or authority semantics. Point Profile/Measurement Plan
authority, TASK_361K, generic outputs, parser/import, LTR/public drive, real DB/files,
frontend visual redesign, and external residuals remain locked.

## Definition Of Ready

Satisfied for planned-only status:

- operator scenario and defect are concrete;
- current context and hydration behavior are verified from code;
- V2 ownership, five-state machine, field provenance, explicit reviewed-rebase order,
  shared server consumer token/guard, exact May Touch, locks, acceptance, validation,
  and merge gates are documented;
- no unresolved assumption changes scope or user workflow.

Implementation is authorized only within the frozen TASK_361L boundary. The next legal
role is Developer implementation.

## Validation Performed

- Read AGENTS, board, Planner/orchestration protocols, TASK_361K task/plan/evidence,
  pricing-draft application/repository/model/API code, frontend hydration/page/client
  code, Point Profile confirmed adapter, and current status.
- Confirmed TASK_361L identifier and proposed paths are unused.
- Confirmed no product, test, schema, API-client, real DB/file, staging, commit, or push
  action occurred in this Planner pass.
- `git diff --check` passed for the TASK_361L governance paths; the existing board
  LF/CRLF conversion notice is non-blocking.
- UTF-8 trailing-whitespace scan found no matches.
- Targeted status shows only the TASK_361L task/plan/Planner evidence and board as this
  pass's changes. The pre-existing TASK_361F operational evidence modification and two
  TASK_361H QA images remain external and untouched.
- B1 fix pass re-read the Reviewer evidence, `ConfirmedFeeVersionService`, Confirmed
  Fee route, direct/browser export route and application service, child-process export
  composition, Matrix Fee rebase promotion, Required Forms current gate, frontend
  Update/export calls, and their focused test locations.
- Post-fix `git diff --check` passed for the governance paths with only the established
  board LF/CRLF notice; trailing-whitespace scan remained clean. No product/test/DB/
  file implementation, staging, commit, or push occurred.

## Blockers

Reviewer B1 and B2 are resolved in task/plan/Developer/Reviewer evidence; no open
Planner or implementation-readiness blocker.

## Next Legal Role

Developer implementation pass.

## Planning-First Source-Of-Truth Reconciliation

- Reviewer plan re-gate status: `reviewer_pass`.
- User approval: Developer planning-first only.
- Developer status: docs-only planning-first complete; implementation not started.
- Historical planning-first reconciled state: ready for Reviewer
  implementation-readiness.
- The V2 five-state contract, Point Profile/default fingerprints, explicit reviewed
  rebase, opaque validation token, server-side consumer guards, per-field merge rules,
  May Touch list, and locked paths remain unchanged.
- That planning-first reconciliation authorized no product change.

## Final Implementation Authorization Reconciliation

- Reviewer implementation-readiness initially blocked B2, then passed after the
  Developer docs-only fix froze generation/old-snapshot CAS, typed `409`, token
  currentness, Confirm/rebase idempotency, and repeat-export revalidation.
- The User explicitly approved TASK_361L product implementation.
- Current state: `implementation authorized / pending Developer implementation`.
- Authorized scope is limited to the V2 pricing-draft envelope/context/provenance,
  profile/default fingerprints, five states, reviewed field-level rebase, CAS and
  opaque integrity token, V2 frontend hydration/autosave review flow, shared server
  consumer guards, and focused disposable tests.
- Frozen acceptance includes old saved LLCR `units=1` never overriding current
  backend defaults and `P / 1-3` yielding UI Units `15` and `9` for group quantities
  `5` and `3`.
- V1/non-current states reject with no write/artifact; direct edited payloads cannot
  bypass the server-loaded V2; load/Cancel remain zero-write.
- All existing Fee formula/rules/pricing/discount visual, TASK_361K, Point Profile,
  workbook/generic output, parser/import, LTR/public-drive, real DB/file, and external
  residual locks remain unchanged.
- This Planner pass itself changes governance docs only and performs no implementation.
