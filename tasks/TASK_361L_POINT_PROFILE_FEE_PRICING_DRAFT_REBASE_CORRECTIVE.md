# TASK_361L Point Profile Fee Pricing Draft Rebase Corrective

## Status

Complete/accepted locally after Developer implementation, Reviewer implementation
re-gates, QA disposable smoke, and Integrator hunk-isolated packaging. Remote push
was intentionally not performed.

## Lane

`point-profile-fee-pricing-draft-rebase-corrective`

## Current Phase / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- TASK_361K is complete/accepted in local commit
  `4a70ae9ac118c946da65415c20c2fb74eaf0bb94`.
- Current role: Integrator closeout completed after Reviewer and QA gates passed.
- The accepted package remains limited to the frozen TASK_361L corrective scope.

## Goal

Prevent a saved Fee Evaluation pricing draft from silently overriding newer automatic
LLCR Units produced from the active confirmed Project Point Profile. Bind saved pricing
draft freshness to all authority inputs that affect automatic Fee defaults, rebase
compatible manual edits field by field, and fail closed when legacy payloads or changed
source rows do not provide enough provenance for a safe merge.

The accepted formula remains unchanged:

```text
LLCR Units = confirmed Point Profile readings_per_sample
             * current Confirmed Matrix group sample quantity
```

## Confirmed Defect

- Confirmed Point Profile revision 4 for the supplied project is `P / 1-3`, hence
  `3 readings/sample`.
- The current backend Fee source preview correctly returns LLCR Units `15` for sample
  quantity `5` and `9` for sample quantity `3`, with profile revision/id/fingerprint
  lineage.
- The Fee page displays `1` because the saved pricing draft is still classified
  `current` by only Confirmed Matrix id/revision and fee-rule version.
- The frontend hydrator applies every saved editable field, including `units`, over
  the newly built source preview.
- The saved payload has no per-field manual/default provenance, so an old value cannot
  be safely inferred as an operator edit or an obsolete automatic seed.

## Planned Contract

### Versioned Draft Context

Keep the existing `fee_evaluation_pricing_draft_edits` table and its non-destructive
project/Matrix/rule uniqueness. Store a versioned V2 envelope in `payload_json`; no
SQLite schema migration is planned for V1.

The V2 envelope must include:

- Confirmed Matrix id and revision;
- fee-rule version id;
- effective Point Profile status, confirmed revision id/sequence/fingerprint when
  applicable;
- a deterministic automatic-defaults fingerprint over stable source-row identities,
  row kind/rule identity, backend default editable values, and field metadata
  state/source;
- per-row and summary-field provenance identifying fields explicitly edited by the
  operator.

Legacy unversioned payloads remain readable but are `legacy_unclassified` and may not
be reported `current` or silently hydrated.

### Source Row Identity And Freshness

Matrix-step identity remains the canonical tuple already used by the frontend:

```text
source_line_id + confirmed_group_id + confirmed_row_id + step_token + step_index
```

Manual rows retain their existing typed row-kind/group identity. Current status
requires an exact V2 context and automatic-defaults fingerprint match. Point Profile,
Matrix, rule, row identity, selected Measurement Plan source, or automatic-default
metadata changes produce `rebase_required` or `blocked`, never silent `current`.

### Field Provenance And Rebase

Track explicit operator edits for these existing editable fields:

- row fields: `spend_time`, `unit_price`, `unit_type`, `units`, `base_fee`,
  `discount`, `notes`;
- summary fields: `condition_confirmation_spend_time`, `external_cost`,
  `external_cost_note`, `lab_manpower_hourly_rate`.

`testing_fee` is always derived from the merged values and is never manual provenance.

For a compatible profile-lineage rebase with stable Matrix/rule/row identity:

- LLCR `units` always comes from the current backend default, even if a previous
  payload marked Units as edited; the confirmed Point Profile formula is authority;
- LLCR `testing_fee` is recalculated from current Units plus the merged pricing fields;
- operator-edited `spend_time`, `unit_price`, `unit_type`, `base_fee`, `discount`, and
  `notes` are preserved;
- untouched fields are refreshed from the current backend source preview;
- CR and non-LLCR retain existing semantics, with manual values preserved only when
  their stable row and rule context remain compatible.

Missing, corrupt, stale, or divergent profile/source lineage is typed blocked or
review-required. Legacy V1 payloads have no trustworthy provenance: retain the stored
record unchanged for audit, show current backend defaults, do not auto-apply any saved
row field, suppress load-time autosave, and require an explicit reviewed V2 save. If
the operator chose Update Fee, that action must perform and revalidate the V2 save
before confirmation. Do not delete or guess-convert legacy records.

### Write And Consumer Consistency

- Loading/rebasing is read-only. Cancel after load/rebase and no user edit performs no
  write.
- Autosave persists V2 only after a real operator edit; it uses expected Matrix/rule/
  profile/default-fingerprint tokens and returns typed `409` on stale context.
- Reload must reproduce the same rebased values and provenance.
- Update Fee and every export/required-form/rebase production consumer must consume
  only a server-validated `current_v2` snapshot. Frontend hydration/button state is
  never the authority guard.
- Profile reconfirm, Matrix change, rule change, row mismatch, and authority corruption
  must not be hidden by an older saved payload.

### Frozen Pricing Draft State Machine

The V2 DTO uses exactly these five semantic states. The current legacy `stale` response
is folded into `rebase_required`; it is not a sixth consumable state.

| State | Meaning | Load behavior | Save/consume behavior |
|---|---|---|---|
| `missing` | No saved pricing draft exists for the project. | Show current backend defaults; zero-write. | Explicit reviewed save may create V2; Update/export/required forms reject. |
| `current_v2` | V2 envelope, context, automatic-defaults fingerprint, payload fingerprint, and provenance all validate against the current backend source. | Apply only persisted manual fields to current defaults. | The only state allowed for Update Fee, direct/export child, required forms, and rebase/other production consumption. |
| `rebase_required` | A valid V2 exists, but Matrix/rule/profile/default/source-row context changed and a reviewable merge may be built. | Show the current defaults plus deterministic provenance merge for operator review; zero-write. | Reject every production consumer until reviewed V2 save and server revalidation succeed. |
| `legacy_unclassified` | Saved V1/unversioned payload lacks trustworthy context or field provenance. | Preserve the record, show current defaults and a review warning; do not hydrate or rewrite. | Reject every production consumer. Explicit review and V2 save is required; no guessed conversion. |
| `blocked` | Unknown/malformed V2, mixed or invalid provenance, missing/corrupt/stale authority, divergent source, or unsafe row mapping. | Show a typed blocker; zero-write. | Save/rebase/Update/export/required forms all reject until the underlying blocker is corrected and reloaded. |

Transitions are fail-closed: `current_v2` may become `rebase_required` or `blocked` as
soon as context changes; only explicit reviewed save may move `missing`,
`rebase_required`, or `legacy_unclassified` to `current_v2`. `blocked` cannot transition
through a save command.

### Explicit Reviewed-Rebase Sequence

1. Load current backend defaults and current Matrix/rule/profile/source fingerprints.
2. Classify the saved envelope and build only the deterministic in-memory merge
   allowed by provenance.
3. Show that merged result to the operator. Load and Cancel are zero-write.
4. On explicit save or Update Fee intent, submit the reviewed values, provenance,
   expected prior draft id, and expected current context/default fingerprints.
5. The server rebuilds current defaults, repeats the merge/validation, and atomically
   saves a new V2 envelope. It then reloads and revalidates it as `current_v2`.
6. Only after that revalidation may Update Fee or export continue. A changed token at
   either save or consume returns typed `409` with no pricing overwrite, Confirmed Fee
   version, output directory/file, artifact record, or required-form write.

### Shared Server Consumer Guard

After a successful V2 save/reload, the server returns a deterministic
`pricing_draft_validation_token` bound to:

```text
draft_edit_id
+ source_context_fingerprint
+ canonical_payload_fingerprint
```

The token is opaque to the frontend. Confirm Fee and edited export requests must send
the expected draft id and validation token. Direct edited export additionally binds
the submitted edited payload fingerprint; the guard requires an exact match and the
writer consumes the server-loaded saved V2 values, not an untrusted request payload.
Missing tokens, V1 snapshots, all non-`current_v2` states, payload mismatch, or a
context change return a typed conflict before any Confirmed Fee or file side effect.

`ConfirmedFeeVersionService` is the confirmation guard. Its confirmed pricing snapshot
must retain the validated V2 source-context/payload lineage in its existing JSON
boundary so `get_latest()` becomes stale when that context changes. Required Forms
already requires `get_latest().status == current`; it must therefore inherit the same
expanded V2 current check. Child/subprocess export and Matrix Fee rebase promotion
must compose the same guard. Matrix rebase-created defaults use empty manual
provenance, save a valid V2 first, revalidate, and only then auto-confirm.

## Future May Touch After Gates

- `backend/application/fee_evaluation_pricing_draft_persistence_service.py`
- `backend/infrastructure/storage/repositories/fee_evaluation_pricing_draft_edit.py`
- `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py`
- `backend/application/confirmed_fee_version_service.py`
- `backend/api/routes_confirmed_fee_version.py` only for typed V2 conflict mapping and
  expected validation-token DTO fields
- `backend/application/confirmed_matrix_fee_evaluation_export_service.py`
- `backend/api/routes_confirmed_matrix_fee_evaluation_export.py`
- `backend/infrastructure/office/fee_evaluation_export_child.py` only to compose and
  enforce the same pricing-draft guard; no workbook writer/layout change
- `backend/application/matrix_fee_rebase_promotion_service.py` only to create,
  revalidate, and consume a V2 default snapshot before existing auto-confirm behavior
- `backend/application/project_folder_required_forms_service.py` only if needed for a
  typed non-current V2 blocker; its existing confirmed-fee current gate remains the
  semantic boundary
- `backend/api/dependencies.py` only for read-only confirmed Point Profile context
  and shared pricing-draft consumer-guard composition if required
- a narrowly named pricing-draft context/fingerprint/rebase helper under
  `backend/application/` if needed to keep service files within repository limits
- `frontend/src/api/client.ts` only for the typed pricing-draft V2 context/provenance
  contract
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
- focused backend/frontend tests named in the plan
- TASK_361L task/plan/evidence and `docs/task_board.md`

## Must Not Touch / Locked Paths

- No Fee rule, price tier, unit price, base-fee, discount, man-hour, or pricing formula
  business change.
- No TASK_361K confirmed Point Profile formula/adapter/context-selection change.
- No Point Profile schema, expression parser, editor, lifecycle, API command, or
  confirmed-authority mutation.
- No Measurement Plan authority schema/lifecycle/consumer semantic change.
- No workbook, Generic Test Record, Report, Matrix parser/import, LTR/public drive,
  real DB, real workbook, or real project-folder operation.
- No frontend visual redesign; only existing Fee status/error affordances may receive
  concise rebase/blocker copy.
- No unrelated API-client changes, TASK_361F evidence, TASK_361H artifacts, external
  residual cleanup, `.agents/**`, `docs/project_management/**`, staging, commit, or
  remote push during Planner/Reviewer gates.

## Acceptance Criteria

1. Confirmed profile `P / 1-3` with group quantities `5` and `3` yields Fee UI Units
   `15` and `9` respectively.
2. An old saved LLCR `units=1` does not override those current backend defaults.
3. A profile reconfirm changes source lineage and rebases LLCR Units/testing fee.
4. Compatible, explicitly edited unit price/base fee/discount/notes/spend time and
   unit type survive profile-only rebase.
5. Untouched/default values refresh from current backend defaults.
6. `testing_fee` is recalculated and is never restored as an independent manual field.
7. V1 drafts without provenance are retained but fail closed as
   `legacy_unclassified`; no load-time write or guessed merge occurs.
8. Matrix/rule/source-row mismatch is stale/rebase-required, never `current`.
9. Missing/corrupt/stale profile or divergent source lineage is typed blocked with no
   saved-value fallback.
10. Exact target-specific Measurement Plan precedence and no-double-counting from
    TASK_361K remain intact.
11. CR and non-LLCR default/manual behavior does not regress.
12. Cancel is zero-write; autosave, reload, Update Fee, and export share the same
    current context and merged values.
13. Only `current_v2` may create a Confirmed Fee version, any direct/browser/child Fee
    export (including calls without an edited payload), Required Forms output, or a
    rebase-created confirmed Fee. Every other state rejects server-side before
    write/artifact creation.
14. Direct edited export requires draft id, validation token, and matching canonical
    payload fingerprint; a raw edited payload cannot bypass saved V2 validation.
15. The explicit reviewed-rebase sequence saves and revalidates V2 before Update Fee
    or export, while load and Cancel remain zero-write.
16. All storage/API tests use disposable SQLite; no real project or file is mutated.

## Validation Gate

- Backend unit tests for V2 serialization, context fingerprint, V1 compatibility,
  exact/current/rebase/blocked classification, field provenance, LLCR-authoritative
  rebase, manual preservation, and stale `409`.
- Disposable SQLite repository/API tests for idempotent V2 persistence, legacy record
  no-rewrite, profile reconfirm, Matrix/rule mismatch, source-row mismatch, missing or
  corrupt lineage, and zero-write load/Cancel.
- Confirmed Fee tests for `missing`, `legacy_unclassified`, `rebase_required`,
  `blocked`, malformed/mixed provenance, stale token, and payload mismatch: each must
  reject with no Confirmed Fee write; reviewed V2 save/revalidation then succeeds.
- Direct browser/API export, child/subprocess export, Required Forms, and Matrix rebase
  production tests must reject every non-`current_v2` state with no writer call,
  output directory/file, artifact record, confirmed write, or draft overwrite.
- Frontend model/page tests for `15`/`9`, old `1` suppression, manual-field retention,
  derived testing fee, autosave/reload, Cancel, Update Fee/export gating, and unchanged
  CR/non-LLCR behavior.
- Controlled browser smoke against disposable/mock data only. The real project id may
  be used as a read-only reference but must not be written.
- Focused existing TASK_351, TASK_357D, TASK_361E/K, pricing-draft, export, and Fee page
  regressions; frontend build; py_compile; diff/trailing/line-count/whitelist/
  forbidden-scope/no-real-mutation checks.

## Merge Gate

Reviewer plan gate -> explicit user approval for Developer planning-first -> Developer
docs-only planning-first -> Reviewer implementation-readiness -> explicit user
implementation approval -> Developer implementation -> Reviewer implementation gate ->
QA disposable/API gate -> Integrator hunk-isolated packaging and acceptance.

## Definition Of Ready

Satisfied and accepted. V2 context/provenance, the five-state machine, reviewed
rebase ordering, shared server-side validation token, compare-and-swap generation,
consumer idempotency/revalidation, confirmation/export guards, legacy fail-closed
behavior, file ownership, and disposable validation were verified in the isolated
package.

## Blocking Questions

None.

## Planning-First Source-Of-Truth Reconciliation

- Reviewer initially blocked B1; the Planner fix froze server-side guards for every
  Confirm/Update/export/rebase production consumer.
- Reviewer plan re-gate passed with no remaining plan blocker.
- The user approved Developer planning-first only.
- Developer completed the docs-only planning-first refinement and changed no product,
  test, schema, API-client, real database, or real file path.
- Reviewer implementation-readiness initially blocked B2; Developer completed the
  docs-only CAS/replay/idempotency fix and Reviewer re-gate passed.
- Developer, Reviewer, QA, and Integrator gates are complete; TASK_361L is accepted
  locally.

## Final Implementation Authorization

Authorized implementation is limited to:

- the V2 pricing-draft JSON envelope, source context, field provenance, confirmed
  Point Profile lineage fingerprint, and canonical automatic-default fingerprint;
- the five states `missing`, `current_v2`, `rebase_required`,
  `legacy_unclassified`, and `blocked`, with only server-validated `current_v2`
  consumable;
- explicit reviewed rebase that refreshes auto-derived LLCR Units/testing fee while
  preserving only provably compatible manual unit price, base fee, discount, notes,
  and spend time fields;
- generation and old-snapshot compare-and-swap, typed `409` conflict/no-overwrite,
  transactional post-write revalidation, and opaque currentness/integrity tokens;
- frontend V2 hydration, provenance-aware autosave/review, stale-CAS reload, and
  load/Cancel zero-write behavior;
- shared server guards for Confirm/Update Fee, direct/browser/child export, Required
  Forms, and Matrix Fee rebase, using server-loaded V2 values;
- transactionally idempotent Confirm/rebase retries and stateless repeat exports that
  reload/revalidate before every writer or artifact action;
- focused disposable backend/frontend tests, including `P / 1-3` producing UI Units
  `15` for group quantity `5` and `9` for group quantity `3` while old saved `1`
  never overrides current defaults.

V1 and every non-current state fail closed with no write or artifact. Existing records
remain additive/non-destructive and are neither guessed nor rewritten implicitly.
All Must Not Touch and Locked Paths remain unchanged.
