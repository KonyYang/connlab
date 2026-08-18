# TASK_361L Point Profile Fee Pricing Draft Rebase Corrective Plan

## Status

Complete/accepted locally after Developer implementation, Reviewer implementation
re-gates, QA disposable smoke, and Integrator hunk-isolated packaging. Remote push
was intentionally not performed.

## Discovery Gate

### Current Phase / Active Task / Role / Why Allowed

- Current phase: Phase 11 controlled Matrix foundation.
- TASK_361K is complete/accepted at `4a70ae9a`; no implementation lane is active.
- Current role: Planner, requested to isolate a post-acceptance pricing-draft defect.
- This lane is allowed because it corrects saved-draft freshness without reopening the
  accepted Point Profile calculation or Fee pricing rules.

### Confirmed By User

- Confirmed Point Profile `P / 1-3` means `3 readings/sample`.
- LLCR Units is readings/sample multiplied by the current Fee row's Matrix group
  sample quantity.
- Current backend values `15` and `9` are correct; browser values `1` are stale saved
  pricing-draft overlays.
- Saved-draft freshness must include confirmed Point Profile lineage.
- Compatible manual pricing edits must be preserved field by field; the whole draft
  must not be indiscriminately cleared.
- Where manual/default provenance cannot be proved, behavior must fail closed.
- This pass may create planning governance only and may not write real DB/files.

### Confirmed By Repository Evidence

- `FeeEvaluationPricingDraftContext` contains only project id, Confirmed Matrix id/
  revision, and fee-rule version id.
- The persistence repository stores one `payload_json` for that tuple; the table has no
  Point Profile/default fingerprint or provenance columns.
- Saved rows serialize every editable value but no edited-field set or source context.
- `hydrateFeeEvaluationPreviewEditsFromSavedDraft()` overlays spend time, unit price,
  unit type, Units, base fee, discount, and notes for every matched saved row.
- `testingFee` is recalculated by the frontend model from the merged pricing fields.
- The page already records actual edit events in `handlePreviewRowEditChange`, but that
  field identity is not persisted.
- TASK_361K's read-only adapter provides confirmed profile status, revision id,
  revision sequence, fingerprint, and readings/sample without changing DTOs.
- Existing working-tree changes are an unrelated TASK_361F operational evidence file
  and two TASK_361H QA images; they are excluded from this lane.

### Planner Decisions

1. Use a versioned V2 JSON envelope inside the existing pricing-draft `payload_json`.
   An additive SQLite column/table migration is not necessary for V1 because context,
   provenance, and fingerprints are cohesive payload metadata and the existing record
   remains non-destructively readable. Any future implementation that proves a query
   or index requirement must return for a separate schema re-gate.
2. Add typed application/API/client context fields despite retaining the physical
   table. The service, not display copy, decides `current`, `rebase_required`,
   `legacy_unclassified`, or `blocked`.
3. Compute one canonical automatic-defaults fingerprint from stable source row
   identity, row/rule kind, backend automatic values, and field metadata state/source.
   This captures profile, exact Measurement Plan override, and other automatic source
   changes without parsing human-readable lineage strings as authority.
4. Persist explicit per-field provenance from real edit events. Never infer manual
   intent by comparing saved values with old or new defaults.
5. On a profile-only compatible rebase, LLCR Units and derived testing fee are replaced
   by current backend defaults. Preserve explicitly edited spend time, unit price, unit
   type, base fee, discount, and notes. CR/non-LLCR retain their accepted semantics.
6. Treat V1 drafts as unclassified. Keep them intact for audit, do not hydrate them,
   do not autosave on load, and require an explicit reviewed V2 save. Update Fee intent
   must complete and revalidate that save before confirmation. This is fail-closed
   without deleting the whole draft.

### Not Yet Confirmed

None blocking. Reviewer should challenge the exact canonical fingerprint fields and
manual-field allowlist, but neither requires a user product decision before plan gate.

### Planning Risks

- Comparing only profile revision while ignoring source-row metadata would miss
  target-specific Measurement Plan or other automatic-default changes.
- Inferring manual edits from unequal values would preserve obsolete seeds as if they
  were operator decisions.
- Refreshing `units` but restoring saved `testing_fee` would create an internally
  inconsistent row.
- Performing rebase on load via autosave would violate Cancel/no-write and erase the
  evidence needed to diagnose legacy drafts.
- Updating only the browser path would leave Update Fee/export semantics inconsistent.

## V2 Data Contract

The stored V2 envelope is conceptually:

```json
{
  "schema_version": 2,
  "source_context": {
    "confirmed_matrix_id": "...",
    "confirmed_revision": 1,
    "fee_rule_version_id": "...",
    "point_profile_status": "confirmed",
    "point_profile_revision_id": "...",
    "point_profile_revision_sequence": 4,
    "point_profile_fingerprint": "...",
    "automatic_defaults_fingerprint": "..."
  },
  "rows": [
    {
      "source_line_id": "...",
      "confirmed_group_id": "...",
      "confirmed_row_id": "...",
      "step_token": "1",
      "step_index": 1,
      "manual_fields": ["unit_price", "discount", "notes"],
      "values": {}
    }
  ],
  "summary": {
    "manual_fields": ["external_cost_note"],
    "values": {}
  }
}
```

The exact serializer may retain the current flat row-value shape for backward
compatibility, but `schema_version`, source context, and manual field sets are
mandatory. Unknown versions and malformed provenance fail closed.

### Canonical Automatic-Defaults Fingerprint

Hash UTF-8 canonical JSON with sorted keys and deterministic row order. Include:

- the canonical stable row identity tuple;
- row kind and backend fee-rule/calculation identity when exposed;
- automatic `spend_time`, `unit_price`, `unit_type`, `units`, `base_fee`, `discount`,
  `notes`, and derived/review state inputs;
- field metadata state and machine-owned source identifiers/lineage;
- current Point Profile status/revision/fingerprint as explicit context.

Exclude display order unrelated to identity, localized copy, timestamps, UI formatting,
and calculated totals. Fingerprint production belongs in an application helper and is
shared by load/save/conflict validation.

## Frozen State Machine

The public/application contract uses five states. Existing `stale` is mapped to
`rebase_required`; there is no compatibility state that is accidentally consumable.

| State | Classification | Allowed transition | Production consumption |
|---|---|---|---|
| `missing` | no saved snapshot | explicit reviewed save -> `current_v2` | forbidden |
| `current_v2` | V2 schema/context/default/payload fingerprints and provenance all validate now | matching save -> `current_v2`; source change -> `rebase_required`/`blocked` | allowed after guard token revalidation |
| `rebase_required` | valid V2, changed Matrix/rule/profile/default/source-row context, deterministic review merge possible | explicit reviewed V2 save and reload -> `current_v2` | forbidden |
| `legacy_unclassified` | V1/unversioned saved payload, no trustworthy provenance | explicit review against current defaults and V2 save -> `current_v2` | forbidden |
| `blocked` | malformed/unknown V2, mixed provenance, unsafe mapping, or missing/corrupt/stale/divergent authority | fix authority then reload; save is forbidden | forbidden |

Load never transitions state by writing. Only `current_v2` is valid for Confirm/Update
Fee, browser/direct/child export, Required Forms, Matrix Fee rebase promotion, or any
other production consumer.

### Field Merge Matrix

| Field | Profile-only rebase | Reason |
|---|---|---|
| LLCR `units` | current backend default | confirmed profile formula is authority |
| `testing_fee` | always recalculate | derived from merged pricing values |
| `spend_time` | preserve only explicit manual | operator estimate |
| `unit_price` | preserve only explicit manual | permitted pricing review |
| `unit_type` | preserve only explicit manual when rule compatible | existing editable field |
| `base_fee` | preserve only explicit manual | permitted pricing review |
| `discount` | preserve only explicit manual | permitted pricing review |
| `notes` | preserve only explicit manual | operator annotation |
| CR/non-LLCR `units` | preserve explicit manual only when source/rule compatible | no semantic migration in this lane |
| summary fields | preserve only explicit manual | existing operator inputs |

Untouched fields always come from the current backend preview. An explicit edit marker
is added only by a user input event, not by initial seeding or hydration.

## API And UI Boundary

- Extend the pricing-draft response/save contract with typed source context,
  provenance, rebase status, and concise diagnostics.
- Save requests carry expected automatic-default/profile tokens; a changed token is a
  typed `409` and triggers reload, not overwrite.
- The Fee page uses existing dense operational status/error patterns. No modal-first
  flow or visual redesign is planned.
- Rebase is in-memory/read-only until a real edit or explicit Update Fee intent. Update
  Fee must first save/revalidate V2, then confirm; Cancel with no edits is zero-write.
- Update Fee and export are disabled for every state except `current_v2`, but the
  server guard remains authoritative even when callers bypass the frontend.

## Explicit Reviewed-Rebase Transaction Order

1. Server builds current backend defaults and typed Matrix/rule/profile/source
   context.
2. Server classifies the saved envelope and returns a deterministic review merge only
   where V2 provenance allows it. V1 returns current defaults plus a legacy warning,
   never guessed fields.
3. Operator reviews the visible merged values. Load and Cancel do not save.
4. Explicit save or Update Fee intent submits reviewed values/provenance plus expected
   prior draft id, source-context fingerprint, and defaults fingerprint.
5. Server rebuilds current defaults, validates the submitted field merge, atomically
   writes V2, reloads it, and proves `current_v2`.
6. Server returns an opaque validation token. Only then may Update Fee/export proceed.
7. Any changed token/context at save or consumption returns typed `409` with no draft
   overwrite, Confirmed Fee version, writer call, directory/file, artifact record, or
   Required Forms placement.

## Shared Server Consumer Guard

Create a narrow pricing-draft validation boundary that returns a
`ValidatedCurrentFeePricingDraft` only for `current_v2`. Its opaque
`pricing_draft_validation_token` is a deterministic hash over:

```text
draft_edit_id
+ source_context_fingerprint
+ canonical_payload_fingerprint
```

The guard is used by:

- `ConfirmedFeeVersionService.confirm()` before creating a version;
- browser/direct `matrix_basic` edited export before output directory creation,
  template resolution, writer invocation, or output registration;
- every direct `fee_draft` or `matrix_basic` export and every child/subprocess export;
  no production Fee workbook may bypass current-V2 validation by omitting edited
  values;
- Required Forms through the expanded Confirmed Fee `get_latest().status == current`
  boundary;
- Matrix Fee rebase promotion before an automatically created default draft is
  confirmed; and
- any production dependency composition that can reach those services.

Confirm requests carry expected draft id and validation token. Edited export requests
carry expected draft id, validation token, and canonical payload fingerprint. The
server requires the request payload fingerprint to equal the validated saved V2
snapshot and passes the server-loaded snapshot values to the writer. Requests without
V2 tokens, raw edited payload-only calls, and mismatches fail with typed `409`.

Confirmed Fee `pricing_snapshot_json` keeps the validated V2 source-context/payload
lineage in its existing JSON storage boundary. `get_latest()` compares that lineage
with the current pricing context, so Point Profile/default changes make the Confirmed
Fee stale and Required Forms remains blocked without a schema change.

Matrix rebase-created defaults use V2 with an empty manual-field set. The promotion
service must save, reload, and validate `current_v2` before its existing auto-confirm
step. Failure produces no pricing-draft overwrite or Confirmed Fee version.

## File-Level TDD Plan

1. Add backend tests for V2 serialization/context/fingerprint/provenance and legacy
   fail-closed behavior.
2. Add a narrow application helper only if needed for canonical context/fingerprint
   and row merge; keep route/repository thin.
3. Extend persistence service and repository JSON compatibility without table rebuild
   or data rewrite.
4. Add the shared current-V2 guard and first cover Confirmed Fee rejection/allowance.
5. Guard direct/browser export before any filesystem/writer side effect, then compose
   the same guard in child/subprocess export.
6. Carry V2 lineage into Confirmed Fee currentness; prove Required Forms blocks stale
   or non-V2 confirmed pricing.
7. Make Matrix rebase promotion create/revalidate V2 before auto-confirm.
8. Extend typed routes/client tokens and frontend model/page review/save order.
9. Run disposable backend/API/frontend/browser regressions and package scans.

## May Touch

Exact candidate paths are listed in the task. New files, if any, must be narrowly
named pricing-draft context/fingerprint/rebase application helpers or focused tests.
No existing unrelated Fee module may be pulled in merely for convenience.

## Must Not Touch / Locked Paths

The task's locked list is binding. In particular, this lane does not alter pricing
rules/formulas, TASK_361K authority selection, Point Profile or Measurement Plan
authority, workbook/generic outputs, parser/import, LTR/public drive, or real data.
Current TASK_361F/TASK_361H residuals remain excluded.

## Validation And Merge Gates

Use the task's focused validation matrix. Each `missing`, `legacy_unclassified`,
`rebase_required`, `blocked`, malformed/mixed-provenance, and stale-token case must be
attempted against Confirm Fee, browser/direct export, child/subprocess export,
Required Forms, and Matrix rebase promotion. Tests assert typed rejection plus zero
Confirmed Fee, pricing overwrite, writer call, artifact, output directory/file, and
Required Forms placement. The successful path must prove reviewed V2 save -> server
reload/revalidation -> Update/export with visible `15`/`9`. Integrator must isolate
only approved hunks and verify no real DB/file mutation or residual inclusion.

## Definition Of Ready

Ready for Reviewer implementation-readiness. Reviewer B1 is resolved in the written
contract by the five-state machine, explicit reviewed-rebase order, opaque current-V2
validation token, server-side confirmation/export/required-form/rebase guards, and
disposable zero-side-effect regressions. Reviewer plan re-gate passed and Developer
docs-only planning-first is complete. Implementation remains unauthorized.

## Reviewer B1 Fix Record

- Reviewer correctly found that frontend hydration protection did not cover
  `ConfirmedFeeVersionService` or raw edited export payloads.
- Planner froze `current_v2` as the sole consumable state and mapped existing `stale`
  into non-consumable `rebase_required`.
- Every server production consumer now has an explicit guard/composition/test owner.
- No Fee formula/rule/UI redesign, workbook behavior, authority mutation, schema
  migration, or real-data operation is added.

## Developer Planning-First Refinement (2026-07-15)

### Implementation Reality And File Order

The live persistence service currently classifies only `missing`, `current`, and
`stale`; its `payload_json` is an unversioned values-only document. The repository
keeps project/confirmed-Matrix/rule tuple columns for lookup, so V2 is an additive
JSON-envelope migration, not a table migration. Existing V1 JSON must remain readable
for audit and classify `legacy_unclassified` without an update.

The current service is 543 lines, the direct export service is 515 lines, the export
route is 519 lines, and the Fee page/model/test files are already large. Implementation
must not compress whitespace or append another orchestration block to them. The exact
implementation order is:

1. Create `backend/application/fee_evaluation_pricing_draft_v2_contract.py` for the
   pure envelope codec, canonical JSON/fingerprints, source-context types, provenance
   validation, and the five-state result types. It owns no database or application
   side effects and remains below 300 lines.
2. Create `backend/application/fee_evaluation_pricing_draft_v2_rebase.py` for pure
   stable-row identity matching and field-level merge. It returns an immutable
   review candidate or typed unsafe/mixed mapping result, and remains below 300 lines.
3. Refactor
   `backend/application/fee_evaluation_pricing_draft_persistence_service.py` into a
   thin orchestration service: build current backend defaults, construct source
   context, classify saved V1/V2, expose a read-only review candidate, validate an
   explicit reviewed save, atomically persist V2, then reload/revalidate. The existing
   values-only serializer remains as a V1 reader only; the repository persists the
   V2 envelope through its existing `payload_json` column.
4. Create `backend/application/fee_evaluation_current_pricing_draft_guard.py` with a
   single `validate_current_v2(...)` boundary. It returns server-loaded edited values
   and V2 context only after id/token/canonical-payload validation. It owns no writer
   or filesystem calls.
5. Extend the repository and pricing-draft route solely for the typed V2 envelope,
   five-state load response, review candidate, expected context/default tokens, and
   typed `409` conflicts. Route bodies remain DTO mapping only.
6. Make `ConfirmedFeeVersionService`, direct/browser export, child export, Required
   Forms, and Matrix Fee rebase consume the shared guard before their existing write
   or writer boundary. Do not modify workbook layout/writer code, fee rules, or the
   Point Profile/Measurement Plan adapters.
7. Extend `frontend/src/api/client.ts` only for the typed V2 DTOs and opaque token.
   Create `frontend/src/features/fee-evaluation/useFeePricingDraftModel.ts` for
   hydration, local operator provenance, autosave/review-save sequencing, Cancel, and
   stale recovery. `FeeEvaluationReviewExportPage.tsx` becomes a declarative caller of
   that feature model, rather than gaining more async state. Add
   `feePricingDraftSelectors.ts` only for display-only action eligibility/copy.
8. Update the existing preview model only for typed V2 hydration/merge inputs. Keep
   all automatic calculation, fee formula, discount, and visual table column behavior
   unchanged. The page may show concise inline state/review copy, not a modal or a
   redesign.

### Exact V2 Envelope And Classification

`payload_json` V2 has this logical shape, serialized with sorted-key canonical JSON:

```text
{
  schema_version: 2,
  source_context: {
    confirmed_matrix_id, confirmed_revision, fee_rule_version_id,
    point_profile: { status, revision_id, revision_sequence, fingerprint },
    automatic_defaults_fingerprint
  },
  edited_values: <existing FeeEvaluationEditedExportValues shape>,
  operator_provenance: {
    rows: { <stable-row-identity>: [editable-field-name...] },
    summary: [summary-field-name...]
  },
  canonical_payload_fingerprint: <hash>
}
```

The stable identity is the existing tuple
`source_line_id + confirmed_group_id + confirmed_row_id + step_token + step_index`.
Manual rows retain their existing typed row-kind/group identity. The source-context
fingerprint includes canonical Matrix/rule identifiers, Point Profile machine facts,
and the automatic-defaults fingerprint. The automatic-defaults fingerprint includes
stable row identities, row/rule kind, backend automatic editable values, and field
metadata state/source. It excludes localized labels, display order, timestamps, and
derived `testing_fee`.

Classification precedence is deterministic:

- no snapshot: `missing`;
- unversioned/V1 payload: `legacy_unclassified`;
- malformed/unknown V2, invalid provenance, authority unavailable/corrupt/stale,
  duplicate identity, mixed selected source, or unsafe row mapping: `blocked`;
- valid V2 whose current canonical context/default fingerprint differs but whose
  source rows are safely matchable: `rebase_required`;
- only a V2 whose source context, defaults fingerprint, payload fingerprint and
  provenance all revalidate exactly: `current_v2`.

Load computes a review candidate only. It writes nothing. Cancel after any load or
rebase remains zero-write. A legacy V1 candidate is current defaults plus explicit
review state, with no V1 values or inferred manual fields applied.

### Reviewed Rebase And Field Semantics

The model records a manual field only on a real operator input event. Hydration,
initial seed, rebase candidate construction, reload, and Cancel never create manual
provenance. On an explicit reviewed Save or Update Fee intent, the client submits the
reviewed values, provenance, expected prior draft id, source-context fingerprint, and
automatic-defaults fingerprint. The server rebuilds defaults and repeats every
classification and merge check inside the persistence transaction before replacing the
V2 envelope. It then reloads and must classify `current_v2` before returning a token.

For a compatible Point Profile-only rebase, LLCR `units` always refreshes from the
confirmed Profile formula and `testing_fee` always recalculates. Explicit manual
`spend_time`, `unit_price`, `unit_type`, `base_fee`, `discount`, and `notes` survive
only on a stable, rule-compatible row. CR/non-LLCR rows and summary fields preserve
only explicit compatible manual values. Any source/rule/identity ambiguity blocks,
rather than guessing. This does not alter any price, discount, or formula.

### Consumer Token Boundary

`pricing_draft_validation_token` is opaque to the client and is calculated from the
draft edit id, V2 generation, canonical source-context fingerprint, and canonical
payload fingerprint. It is a currentness/integrity attestation, not a one-time
credential. `validate_current_v2` reloads current authority and the V2 snapshot; it
rejects missing or stale generation/token, mismatched draft id, mismatched edited
payload fingerprint, and changed source context before exposing server-loaded values.

- Confirm Fee supplies expected draft id and token. Its version JSON retains the V2
  context/payload lineage so `get_latest()` becomes stale when revalidated context
  changes.
- Browser/direct edited export supplies id, token, and canonical payload fingerprint.
  The guard rejects raw payload bypass attempts; the writer receives the
  server-loaded V2 values only.
- Child/subprocess export receives the same validated values through dependency
  composition before subprocess or artifact/output work begins.
- Required Forms continues to use the Confirmed Fee current boundary. A confirmed
  fee whose embedded V2 lineage no longer matches is non-current and cannot place an
  output.
- Matrix Fee rebase starts with empty provenance, persists V2, reloads through the
  guard, and only then reaches existing auto-confirm logic.

Every non-`current_v2` status returns a typed review/block/conflict result, performs
no draft overwrite, Confirmed Fee creation, writer call, child process, output
directory/artifact operation, or Required Forms placement.

### Frontend Operating States

The feature model exposes `missing`, `current_v2`, `rebase_required`,
`legacy_unclassified`, `blocked`, `saving`, and `conflict` display state without
inventing authority. `current_v2` hydrates only server-declared manual fields over
current source defaults. `rebase_required` displays the server review candidate and
requires an explicit reviewed save. `legacy_unclassified` shows current defaults and
requires review, never silent hydration. `blocked` keeps editable source values
visible with a concise reason but disables Save/Update/export. Cancel restores the
server baseline and returns to Matrix with zero write.

The existing compact Fee screen retains dense operational hierarchy. The only added
copy is a small inline status/review line near Save/Update, plus nearby disabled reason
when a consumer is unavailable. No modal, nested card, visual metric, or workbook
control is introduced. Controls use existing button styles and accessible disabled
descriptions.

### Focused TDD Matrix

Backend disposable SQLite/API tests must cover:

- V1 decode preserves stored data and returns `legacy_unclassified` without rewrite;
- V2 canonical fingerprint stability and changes to Profile revision/fingerprint,
  Measurement Plan source metadata, Matrix/rule/row identity, or automatic defaults;
- `missing`, `current_v2`, `rebase_required`, `legacy_unclassified`, and `blocked`
  classifications with load/Cancel zero-write;
- profile-only rebase refreshing LLCR Units/testing fee while preserving compatible
  manual unit price/base fee/discount/notes/spend time;
- mixed/divergent source, corrupt Profile, invalid token, payload replay, concurrent
  save, stale context, and unsafe-row mapping as typed no-write conflicts;
- Confirm Fee, browser/direct/child export, Required Forms, and rebase rejecting every
  non-current state before version/writer/artifact/output/placement side effects;
- reviewed save -> server reload/revalidate -> valid token -> Confirm/export success
  using server-loaded values, including 15/9 LLCR Units fixtures.

Frontend focused tests must cover V2-only hydration, explicit manual provenance on
input, no hydration/autosave for legacy/rebase/blocked load, reviewed rebase save
order, token conflict reload, Cancel zero-write, and disabled Update/export copy. Use
the existing Fee page and preview model test fixtures; create focused model tests so
the 1,305-line route component does not gain workflow assertions.

Browser smoke uses a disposable seeded project at desktop and 514px: change confirmed
Profile from readings 3 to 5, reload Fee, verify the inline rebase state and Units
refresh from 15 to 25 for group quantity 5, preserve a deliberate unit-price edit,
review-save, Update Fee, reload latest, and verify Cancel after load produces no
network write. Browser smoke must not generate an actual workbook.

### May Touch And Isolation

Future implementation may touch only these paths plus narrowly named focused tests:

- `backend/application/fee_evaluation_pricing_draft_persistence_service.py`
- `backend/application/fee_evaluation_pricing_draft_v2_contract.py`
- `backend/application/confirmed_fee_pricing_snapshot.py`
- `backend/application/fee_evaluation_pricing_draft_v2_rebase.py`
- `backend/application/fee_evaluation_current_pricing_draft_guard.py`
- `backend/infrastructure/storage/repositories/fee_evaluation_pricing_draft_edit.py`
- `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py`
- `backend/application/confirmed_fee_version_service.py`
- `backend/api/routes_confirmed_fee_version.py`
- `backend/application/confirmed_matrix_fee_evaluation_export_service.py`
- `backend/api/routes_confirmed_matrix_fee_evaluation_export.py`
- `backend/infrastructure/office/fee_evaluation_export_child.py`
- `backend/application/project_folder_required_forms_service.py`
- `backend/application/matrix_fee_rebase_promotion_service.py`
- `backend/application/matrix_fee_rebase_pricing_draft_bridge.py`
- `backend/api/dependencies.py` only for shared composition
- `frontend/src/api/client.ts`
- `frontend/src/features/fee-evaluation/useFeePricingDraftModel.ts`
- `frontend/src/features/fee-evaluation/feePricingDraftSelectors.ts`
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
- their focused unit/integration/API/component/browser tests and TASK_361L governance.

No schema/model migration, Fee calculation/rule/price/discount change, Point Profile
write/parser/editor/lifecycle change, Measurement Plan authority change, workbook
layout change, generic output work, parser/import, LTR/public drive, real DB/file,
or external residual enters the candidate.

## Planning-First Source-Of-Truth Reconciliation

- Reviewer B1 was resolved by the frozen five-state V2 envelope, reviewed-rebase
  sequence, opaque validation token, and server-side guards across every production
  consumer listed in this plan.
- Reviewer plan re-gate passed.
- The user approved Developer planning-first only.
- Developer completed the docs-only planning-first refinement and verified the
  pricing persistence/API, Fee hydration/autosave/Cancel/Update paths, Confirmed Fee,
  direct/browser/child exports, Required Forms, Matrix rebase, and dependency
  composition boundaries.
- Historical planning-first state was ready for Reviewer implementation-readiness;
  the subsequent B2 fix and Reviewer re-gate are recorded below.

## Reviewer B2 Concurrency And Consumer Idempotency Fix

### Token And Compare-And-Swap Contract

The deterministic token is not called replay protection. It proves only that a
specific draft id, V2 generation, source context, and canonical payload are still
current when the server reloads them. It is never consumed and no consumed-token table
is introduced.

V2 envelope adds `generation: positive integer` in the existing `payload_json`. A
pricing-draft read response exposes `saved_generation` and an opaque exact persisted
`saved_snapshot_fingerprint`. These are required optimistic-concurrency preconditions:

- First V2 save from `missing`: `expected_pricing_draft_edit_id = null`,
  `expected_generation = 0`, no prior snapshot fingerprint. Repository conditionally
  inserts the existing project/Matrix/rule tuple; a competing unique insert becomes
  typed HTTP `409`, with no retry/upsert.
- Ordinary autosave, manual edit save, and reviewed rebase: request carries exact
  prior draft id, generation, and snapshot fingerprint. After current
  authority/default/merge preflight, repository conditionally updates the row by
  tuple, draft id, `updated_at`, and exact previous payload/snapshot condition.
  Success persists `generation = prior + 1`; zero rows is typed `409` and preserves
  the winning values and provenance.
- Explicit V1 review upgrade uses the stored raw V1 snapshot fingerprint as its CAS
  prior state, writes V2 generation 1, and never guesses provenance. A concurrent
  upgrade loses CAS and reloads.

Authority/default preflight, conditional insert/update, and transaction-visible
post-write `current_v2` revalidation execute in one transaction. Any CAS miss,
revalidation failure, or repository failure rolls back the write. The repository
returns a typed compare-and-swap result, replacing unconditional `upsert_current`.
The feature model never retries a conflict blindly; it reloads the authoritative
baseline and leaves the review state visible.

### Consumer-Specific Repeat Policy

**Confirm Fee:** transactional idempotency is selected. The command carries expected
draft id, generation, token, canonical payload fingerprint, and summary. In the
Confirmed Fee store transaction, an exact prior confirmation for the same validated
V2 generation/lineage and summary is returned. A matching draft identity with a
different summary or lineage is HTTP `409`. Absent an exact prior confirmation, one
version is created. SQLite transaction locking must serialize lookup/create, so a
duplicate call never creates a second revision.

**Matrix Fee rebase promotion:** retries are idempotent only for the same promotion
identity, V2 generation, empty manual provenance, and confirmed lineage. Such a retry
returns the prior promotion/Confirmed Fee result. Changed pending input, generation,
or lineage is typed conflict/blocked. It uses the same V2 CAS and Confirm idempotency
boundary, not a separate auto-confirm write path.

**Browser/direct/child export:** generation is repeatable, not token-consuming. Every
request reloads and validates current V2 before writer/subprocess work, then uses only
server-loaded values. A repeat is allowed to reach the existing immutable output-path
policy: it may produce a permitted separate output, or return the existing typed
no-overwrite/output-conflict result. The token is never an artifact identifier. Stale
generation/token/context/payload rejects before writer, child process, artifact,
directory, or file action.

**Required Forms:** each request revalidates the Confirmed Fee's embedded V2 lineage.
Existing placement idempotency remains unchanged, but non-current lineage never reaches
the placement boundary.

### Mandatory Disposable Regression Nodes

1. Two first reviewed saves against `missing`: exactly one V2 generation-1 insert;
   loser is typed `409`, winner provenance unchanged.
2. Two saves against the same V2 generation: exactly one generation increment;
   loser is typed `409`, with no manual-field/provenance loss.
3. Competing V1 upgrades: raw V1 snapshot CAS blocks overwrite and preserves V1 bytes
   on failure.
4. Duplicate Confirm with same validated generation/summary returns one version;
   divergent summary/token yields typed `409` and no second revision.
5. Repeat browser/direct/child export revalidates every time and follows existing
   output collision policy; stale token/context/payload calls no writer, subprocess,
   directory, artifact, or file work.
6. Matrix rebase retry returns its existing promotion for same V2 lineage and creates
   neither another draft generation nor another Confirmed Fee; changed input conflicts.
7. Required Forms rejects stale embedded V2 lineage before placement.

Focused frontend autosave tests add stale-CAS reload with no client retry. All nodes
use disposable SQLite/temp output fixtures, preserve V1 load/Cancel zero-write, and
remain within the existing locked paths.

## Final Source-Of-Truth Authorization

Reviewer implementation-readiness re-gate passed after the B2 compare-and-swap and
consumer-idempotency contract was frozen. The User explicitly authorized product
implementation. Developer, Reviewer, QA, and Integrator gates are complete; TASK_361L
is accepted locally.

Authorized implementation is limited to the V2 envelope/context/provenance and
profile/default fingerprints; five-state classification; reviewed rebase and
field-level merge; generation/old-snapshot CAS; opaque integrity token; V2-only
frontend hydration/autosave review flow; server-loaded consumer guards; transactional
Confirm/rebase idempotency; repeat-export reload/revalidation; and focused disposable
tests. The observable correction remains LLCR UI Units `15` and `9` for confirmed
Profile `P / 1-3` and group quantities `5` and `3`, with stale saved `1` suppressed.

No Fee formula/rule/pricing/discount visual change, TASK_361K adapter/formula change,
Point Profile schema/parser/editor/lifecycle change, workbook layout or generic output
change, Matrix parser/import, LTR/public-drive, real DB/file access, or external
residual is authorized.
