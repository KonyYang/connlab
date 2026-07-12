# TASK_361E Contact Measurement Confirmed Consumer Migration

## Status

Paused by explicit user instruction on 2026-07-13. Reviewer plan gate and the
docs-only Developer planning-first pass remain completed historical facts, but no
Reviewer implementation-readiness routing or Developer implementation is allowed.
Product implementation is not authorized. TASK_361F is accepted, and TASK_361G owns
the new separate CHECK compatibility corrective; neither may be folded into this
lane. Resume requires TASK_361G acceptance and a later explicit user decision.

## Lane

`contact-measurement-confirmed-consumer-migration`

## Current Phase / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Role: paused; no role routing is legal until an explicit user resume decision.
- TASK_361A/B/C/D are complete/accepted. TASK_361D local commit is
  `0fa429f53662addfe7fac86a12f73aad836c95fa`; remote was not pushed.
- The accepted TASK_361A contract reserves TASK_361E as the serial-final lane that
  migrates confirmed consumers after independent authority, setup UI, and draft
  output integration are accepted.
- Reviewer plan gate passed, the user approved Developer planning-first, and the
  Developer completed that pass as docs-only with no design blocker.

## Goal

Migrate the two V1 formal contact-quantity consumers from legacy Confirmed Matrix
`contact_plan` JSON to TASK_361B's effective confirmed Measurement Plan projection:

1. Fee Evaluation LLCR/CR per-reading quantity contexts.
2. TASK_360B formal LLCR/CR specialized workbook preview/generate source.

No draft Measurement Plan or TASK_361D artifact may enter either formal consumer.

## V1 Authority Contract

- Independent confirmed Measurement Plan is the authority for contact families,
  inclusion, and `readings_per_sample` once an independent root is active.
- Active Confirmed Matrix remains the execution-map/source for current Group/Row/Step
  display, sample quantity, and stable lineage matching.
- Consumer matching uses explicit confirmed Group id, Row id, Step sequence, and
  normalized suffix carried by a typed effective target. UI/client code never parses
  opaque `cmp-target:v1` keys.
- Draft or needs-review revision snapshots are never read directly. Consumers call
  the existing effective confirmed projection boundary only.
- Basic Information and Fee are not quantity authority. TASK_361D draft workbooks
  are review artifacts only.

## Effective Projection Status Policy

### `complete`

- Fee consumes every included effective LLCR/CR target.
- Formal workbook builds from every included effective target and is `ready` when
  structurally valid and non-empty.

### `partial_compatible` or `needs_review`

- Effective projection includes only unchanged/text-compatible/sample-compatible
  targets and omits structural, invalid, new, deleted, or unmatched targets.
- Fee consumes included compatible targets. Every current eligible LLCR/CR Step that
  has no effective target is `review_required`, with no units/testing fee and no
  legacy text/contact fallback.
- Formal workbook includes only compatible confirmed targets, carries projection
  diagnostics, and is visibly marked `PARTIAL COMPATIBLE` in its summary metadata.
  Generation is allowed only when at least one compatible section exists and all
  projected sections are structurally valid. Omitted targets never enter rows.
- Preview fingerprint includes active confirmed plan revision/fingerprint, active
  Matrix id/revision, effective status, included sections, and omission diagnostics.

### `not_started` or feature `disabled`

- Use the existing read-only Confirmed Matrix contact-plan adapter as the explicit
  compatibility/rollback path frozen by TASK_361A.
- This fallback is allowed only while no independent root exists or the independent
  resolver feature is disabled. It is never used after an active root exists.

### `authority_corrupt`

- No legacy fallback. Fee contact lines become `review_required`; formal workbook
  preview is blocked and generation writes nothing.

### Empty effective output

- Fee contact lines are review-required when current eligible Steps exist.
- Formal workbook returns empty/blocked diagnostics and produces no file.

## Fee Consumer Contract

- Keep Confirmed Matrix group/row/token traversal, non-contact Step quantities,
  sample quantity, fee rule matching, pricing, discounts, base fees, manual edits,
  exports, and UI unchanged.
- Replace only `_contact_plan_readings` for eligible LLCR and CR specified-current
  Steps with an effective confirmed target lookup.
- For a matched included target, construct the existing `FeeStepQuantityContext`
  using effective `readings_per_sample`; total readings and contact points use that
  value and readings per point remains `1`.
- An explicitly excluded target does not silently re-enable text fallback. It yields
  a review-required/no-units contact line with an authority reason.
- A missing target under an active independent root also blocks legacy/text fallback.
- Current Matrix sample quantity remains the multiplier, so compatible sample-count
  changes recalculate units without changing confirmed plan families.
- No cross-Step aggregation is introduced. Each Group-Step Fee line remains separate.

## Formal Specialized Workbook Contract

- Keep existing TASK_360B route names, request/response compatibility, download
  lifecycle, macro-free layout, artifact root, button, and client behavior.
- Replace the preview source with a formal consumer adapter that joins effective
  confirmed targets to the active Confirmed Matrix context.
- Keep the accepted positive-integer expansion, zero omission, no rounding, prefix
  collision, readings sum, deterministic ordering, stale fingerprint, no-empty, and
  contained artifact rules.
- Workbook summary must state `Confirmed Measurement Plan`, plan revision/sequence,
  active Matrix id/revision, effective projection status, and omission diagnostics.
- `complete` output is labelled `CONFIRMED`; partial-compatible/review output is
  labelled `PARTIAL COMPATIBLE`, never `DRAFT` or `NEEDS REVIEW`.
- TASK_361D draft routes, artifact root, manifests, labels, latest/download, retention,
  API client, and setup-workspace panel remain unchanged and isolated.

## Future May Touch After Separate Authorization

Shared confirmed projection/adapter:

- `backend/application/contact_measurement_plan_projection_service.py` only to expose
  typed internal lineage/context needed by formal consumers without changing draft
  leakage, lifecycle, storage, or existing API semantics
- `backend/application/contact_measurement_plan_confirmed_consumer_adapter.py` (new)
- `backend/application/contact_measurement_plan_identity.py` only if a narrow typed
  identity helper is required; no key format change

Fee consumer:

- `backend/application/confirmed_matrix_fee_step_quantities.py`
- `backend/application/confirmed_matrix_fee_draft_service.py` only to inject/pass the
  effective consumer lookup; no pricing/default-fill change

Formal specialized workbook:

- `backend/application/effective_contact_measurement_llcr_cr_record_projection.py`
  (new)
- `backend/application/confirmed_matrix_llcr_cr_record_preview_service.py`
- `backend/application/confirmed_matrix_llcr_cr_record_generation_service.py` only
  for source metadata/fingerprint compatibility if required
- `backend/application/confirmed_matrix_llcr_cr_record_projection.py` retained as the
  explicit not-started/disabled rollback adapter; behavior changes are prohibited
- `backend/infrastructure/office/llcr_cr_specialized_record_workbook_gateway.py` only
  for confirmed-plan/partial-compatible source metadata; row/layout semantics remain
  unchanged
- `backend/api/routes_confirmed_matrix_llcr_cr_record_workbook.py` only if optional
  source metadata is added without breaking existing response fields
- `backend/api/dependencies.py` only for projection/consumer composition

Focused tests:

- `tests/unit/test_contact_measurement_plan_projection_service.py`
- `tests/unit/test_contact_measurement_plan_confirmed_consumer_adapter.py` (new)
- `tests/unit/test_confirmed_matrix_fee_step_quantities.py`
- `tests/unit/test_confirmed_matrix_fee_draft_service.py`
- `tests/unit/test_effective_contact_measurement_llcr_cr_record_projection.py` (new)
- existing TASK_360B preview/projection/generation/gateway tests
- existing TASK_361B projection/lifecycle tests as regressions
- `tests/integration/test_llcr_cr_specialized_record_workbook_api.py`
- existing Fee API/export tests only for unchanged response/regression
- TASK_361D draft workbook and generic Test Record suites as locked regressions
- TASK_361E task/plan/evidence and `docs/task_board.md`

## Must Not Touch / Locked Paths

- No TASK_361B schema, migration, ORM model, repository write, bootstrap, lifecycle,
  classifier, revision command, confirmation, audit, or feature-flag semantic change.
- No TASK_361D draft projection/service/route/gateway/artifact/client/UI behavior or
  label change.
- No Fee rule matcher, rule seed JSON, unit-price tier, man-hour, discount, base fee,
  manual review/export semantics, or Fee frontend change.
- No generic Test Record, Report, StepInstance/execution, Matrix parser/import,
  Matrix confirmation/persistence, Basic Information, Folder Actions, LTR/public
  drive, real workbook/folder mutation, release/settings cleanup, or unrelated work.
- No frontend runtime or `frontend/src/api/client.ts` changes in V1.
- `.agents/**`, `docs/project_management/**`, remote push, destructive git operations,
  and external parser/TASK_360Q-R-S/superpowers residuals remain locked.

## Acceptance Criteria

1. With effective status `complete`, Fee LLCR/CR units use confirmed Measurement Plan
   readings and current Matrix sample quantity; no legacy contact value is consumed.
2. Under `partial_compatible`/`needs_review`, compatible targets continue; changed,
   new, deleted, unmatched, or excluded targets do not receive units or testing fee.
3. Active-root missing/impacted targets cannot trigger TASK_351 text fallback.
4. `not_started` and disabled resolver paths deterministically retain the existing
   read-only Confirmed Matrix compatibility behavior; `authority_corrupt` never does.
5. Formal workbook preview/generation uses effective confirmed targets, excludes
   unconfirmed targets, includes plan/Matrix lineage, and labels partial output.
6. Formal generation remains preview-fingerprint protected, macro-free, contained,
   non-empty, and structurally validated.
7. Existing formal routes, frontend controls, API client behavior, artifact download,
   and file ownership remain compatible.
8. TASK_361D draft output can include current draft/review targets with draft labels,
   while formal output never reads or labels them as confirmed.
9. Generic Test Record and future Report behavior remain unchanged.

## Validation Gate

- Projection/adapter tests cover complete, partial-compatible, needs-review,
  not-started, disabled, corrupt, empty, included/excluded, and stable identity cases.
- Fee tests prove effective readings, sample quantity recalculation, no cross-Step
  aggregation, omitted-target review, no active-root fallback, deterministic legacy
  rollback, and unchanged pricing/default-fill/manual/export behavior.
- Workbook tests prove compatible-only sections, plan/Matrix metadata, partial label,
  omission diagnostics, deterministic fingerprint, stale `409`, no empty artifact,
  unchanged layout/formulas/artifact containment, and rollback behavior.
- Integration tests keep the existing TASK_360B API/client contract and Matrix
  compatibility row unchanged while authority source changes internally.
- TASK_361B projection/lifecycle, TASK_361D draft workbook/API/UI, Fee export, and
  generic Test Record suites pass as regressions.
- Focused `py -m pytest`, Python compile, `npm run build` as a static regression,
  diff/trailing/line-count/forbidden-scope/no-real-mutation scans, and controlled
  temp-SQLite/temp-dir smoke pass.

## Merge Gate

Reviewer plan gate, explicit user approval, Developer planning-first, Reviewer
implementation-readiness, explicit implementation approval, Developer implementation,
Reviewer implementation review, cross-consumer QA, and Integrator package isolation
are required. Integrator must prove no TASK_361D, frontend/client, schema/lifecycle,
Fee-rule, generic Test Record, parser, LTR/public-drive, real-file, or external
residual hunk entered the package.

## Definition Of Ready

Historically satisfied for Reviewer implementation-readiness review, but that route
is overridden by the 2026-07-13 user pause. No TASK_361E gate may proceed until
TASK_361F is accepted and the user explicitly resumes this lane. No implementation
authorization is implied.

## Blocking Questions

None in the frozen plan. Current stop reason is the explicit user pause, not a design
question.
