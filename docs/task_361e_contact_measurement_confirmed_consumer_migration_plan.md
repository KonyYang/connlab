# TASK_361E Contact Measurement Confirmed Consumer Migration Plan

## Status

Paused by explicit user instruction on 2026-07-13. Reviewer plan gate and the
user-approved docs-only Developer planning-first pass remain completed historical
facts. Reviewer implementation-readiness and Developer implementation routing are
stopped; product implementation is not authorized. TASK_361F is accepted, and
TASK_361G owns the independent CHECK compatibility corrective. Resume requires
TASK_361G acceptance and a later explicit user decision.

## Discovery Gate

### Current Phase / Active Task / Role / Why Allowed

- Phase: Phase 11 controlled Matrix foundation.
- Active task: TASK_361E paused by user; TASK_361F is the current planned corrective.
- Role: paused; no TASK_361E role routing is legal.
- TASK_361A-D are complete/accepted. The frozen contract makes TASK_361E serial last
  because it changes formal consumer authority.
- Reviewer plan gate passed, the user approved Developer planning-first, and the
  Developer completed the planning-first refinement as docs-only.

### Confirmed By User

- TASK_361E must be a separate lane after TASK_361D acceptance.
- V1 must define the confirmed consumer authority, isolate TASK_361D draft output,
  migrate Fee/formal workbook only within an explicit boundary, and preserve package
  locks.
- This Planner pass must not write product code, schema, API client, or tests and must
  stop at Reviewer plan gate.

### Confirmed By Repository Evidence

- `ContactMeasurementPlanProjectionService.get_effective()` returns only active
  confirmed authority and omits structural/new/deleted/unmatched targets with
  `complete`, `partial_compatible`, `needs_review`, `not_started`, `disabled`, or
  `authority_corrupt` status. Editable revisions never enter this projection.
- Fee currently reads `ConfirmedMatrixSnapshot.step_quantities[*].contact_plan` in
  `confirmed_matrix_fee_step_quantities.py` and can fall back to text rules when
  structured quantities are absent.
- TASK_360B formal workbook currently builds directly from active Confirmed Matrix
  Step `contact_plan` snapshots and exposes stable preview/generate/download routes.
- TASK_361D accepted a separate editable-revision-only draft API, artifact root,
  labels, client, and setup-workspace output panel.
- TASK_361A freezes deterministic legacy compatibility until bootstrap/confirmation,
  feature-flag rollback to existing Confirmed Matrix projection, and no fallback
  after an independent root exists.

### Planner Inference And Decisions

- One backend-only migration lane is sufficient. Existing frontend actions and API
  client do not need to change because the formal workbook endpoint remains stable
  and Fee API shape does not change.
- Add a typed internal consumer adapter rather than letting Fee/workbook services
  parse opaque stable keys or query authority tables independently.
- Preserve active Confirmed Matrix for current display/sample quantity and join it to
  effective confirmed plan targets by explicit lineage fields.
- Partial-compatible formal workbooks may generate only compatible confirmed targets,
  with a visible `PARTIAL COMPATIBLE` summary and omission diagnostics. This is not a
  draft artifact and never includes editable targets.
- Active-root omissions block Fee text/legacy fallback. Only `not_started` or explicit
  feature-disabled rollback may use the old read-only adapter.

### Not Yet Confirmed

None that blocks plan review. Partial-compatible formal generation and stable API
preservation are explicit V1 Planner decisions for Reviewer scrutiny.

## Authority Data Flow

```text
TASK_361B effective confirmed projection
  + active Confirmed Matrix display/sample context
  -> typed confirmed consumer adapter
       -> Fee LLCR/CR per-Step readings context
       -> TASK_360B formal workbook compatible-only projection

TASK_361D editable draft projection -> draft workbook only (isolated)
```

## Fee Migration Design

The active Matrix traversal remains unchanged. Build one contact lookup keyed by
`(confirmed_group_id, confirmed_row_id, step_sequence, normalized_suffix)` from the
effective projection. For LLCR/CR tokens, use this lookup before constructing the
existing `FeeStepQuantityContext`.

- Included match: effective readings, current Matrix sample count.
- Excluded/omitted under an active root: review-required with no units/testing fee.
- Non-contact Step: existing confirmed Step quantity behavior.
- Not-started/disabled: explicit old adapter.
- Corrupt: review-required, no fallback.

No matcher, seed, pricing, discount, base-fee, manual-edit, export, or frontend logic
belongs to TASK_361E.

## Formal Workbook Migration Design

Keep existing formal routes and UI. The preview service obtains active Matrix plus
effective confirmed plan and passes both to a new formal adapter. The adapter creates
the existing row/section shape from compatible targets and the current sample count.

- Complete projection: `CONFIRMED` metadata, normal ready behavior.
- Partial-compatible/needs-review: compatible sections only, `PARTIAL COMPATIBLE`
  summary, omission diagnostics, fingerprint over both authorities, generation
  allowed only when non-empty and structurally valid.
- Corrupt/empty: blocked/no file.
- Not-started/disabled: old confirmed-Matrix projection adapter.

The generated artifact remains in TASK_360B's formal root and download lifecycle.
No TASK_361D route, manifest, filename, retention, label, client, or UI is reused.

## Exact File Boundary

The task file is authoritative. Expected implementation is limited to the effective
projection/consumer adapter, Fee contact quantity bridge, formal workbook source and
metadata, dependency composition, and focused backend/API regressions. No frontend
or API-client implementation is planned.

## Locked Scope

- TASK_361B storage/migration/repository writes/lifecycle/classifier/commands.
- TASK_361D draft projection/services/routes/artifacts/gateway/client/UI.
- Fee rules/seeds/pricing/default-fill/manual/export semantics and Fee frontend.
- Generic Test Record, Report, StepInstance, Matrix parser/import/persistence,
  Basic Information, LTR/public drive, real files, release/settings, frontend/client,
  `.agents/**`, `docs/project_management/**`, and external residuals.

## Validation Gate

1. Effective adapter status/fallback/identity tests.
2. Fee complete/partial/review/rollback/corrupt/no-bypass tests plus TASK_351/357D
   pricing and export regressions.
3. Formal workbook complete/partial/omission/stale/empty/corrupt/rollback tests plus
   TASK_360B API/layout/artifact regressions.
4. TASK_361D draft API/gateway/client/UI tests prove isolation and labels.
5. Generic Test Record and TASK_361B lifecycle/projection tests prove no semantic
   expansion.
6. Focused pytest, compile, frontend build regression, diff/trailing/line-count/
   forbidden-scope/no-real-mutation, and temp-SQLite/temp-dir smoke.

## Merge Gate

All standard role gates are required. Integrator stages only TASK_361E backend/test/
governance paths and proves API compatibility, no frontend/client changes, no draft
artifact overlap, no schema/lifecycle/Fee-rule/Test Record/parser changes, and no
external residual inclusion.

## Dependencies And Parallelism

1. TASK_361A/B/C/D: complete/accepted prerequisites.
2. TASK_361E: current planned serial-final consumer migration lane.
3. Future Report/StepInstance consumption requires a separate later contract/lane and
   cannot inherit TASK_361E authorization.

## Definition Of Ready

Historically satisfied for Reviewer implementation-readiness, but the 2026-07-13
user pause overrides that route. TASK_361E remains frozen and unauthorized until
TASK_361F is accepted and the user explicitly resumes it.

---

## Developer Planning-First Refinement

### Typed Confirmed Consumer Adapter

Future implementation adds one backend-only `ContactMeasurementPlanConfirmedConsumerAdapter`.
It joins `ContactMeasurementPlanProjectionService.get_effective()` with the active
`ConfirmedMatrixSnapshot` and exposes a typed lookup keyed by confirmed Group id, Row
id, Step sequence, and normalized suffix. The adapter owns opaque-key isolation and
consumer matching. It supplies current Matrix display/sample context, effective
inclusion/readings/families, omission reason, effective status, confirmed-plan
revision/sequence, and diagnostics. Fee and workbook services must neither parse
`cmp-target:v1` nor query authority tables directly. Editable/draft data is never an
adapter input.

### V1 Status and No-Silent-Fallback Policy

| Effective status | Fee LLCR/CR | Formal TASK_360B workbook | Legacy adapter |
|---|---|---|---|
| `complete` | Consume each included effective target. | All valid included sections, `CONFIRMED`. | No. |
| `partial_compatible` / `needs_review` | Compatible included target only. Omitted/excluded current eligible Step is review-required with no units/fee. | Compatible-only, `PARTIAL COMPATIBLE`, with omissions. | No. |
| `not_started` | Existing Confirmed Matrix contact-plan adapter. | Existing TASK_360B projection. | Yes, root absent only. |
| `disabled` | Existing Confirmed Matrix contact-plan adapter. | Existing TASK_360B projection. | Yes, explicit feature rollback only. |
| `authority_corrupt` / empty active root | Review-required, no contact units or text fallback. | Blocked/empty, no file. | Never. |

After an independent root exists, omitted, excluded, unmatched, or incompatible
targets cannot fall through to legacy `contact_plan` JSON or TASK_351 text parsing.
Non-contact Step contexts remain unchanged.

### Exact Consumer Read Points

- Fee changes only contact-reading selection in
  `confirmed_matrix_fee_step_quantities.build_step_quantity_contexts()`. For LLCR and
  CR specified-current the adapter supplies effective `readings_per_sample`; active
  Matrix still supplies token traversal and current group sample multiplier. Keep
  pricing, rules, defaults, manual edits, exports, and frontend unchanged.
- Formal workbook keeps TASK_360B routes, client, artifact root/name, download, and
  Matrix compatibility row. Its preview service receives active Matrix plus typed
  effective adapter output. Existing legacy projection remains the frozen rollback
  adapter for only `not_started`/`disabled`.
- Formal fingerprint includes active Matrix id/revision, confirmed-plan revision/
  sequence, status, compatible sections, and omissions. `complete` is `CONFIRMED`;
  partial/review is `PARTIAL COMPATIBLE`. Empty/corrupt/stale/structural states do not
  reserve artifacts. TASK_361D draft routes, labels, manifests, retention, client,
  and UI are never reused.

### Compatibility, Tests, and Isolation

Feature-disabled and no-root paths preserve the frozen legacy read adapter. Active
root corruption/missing compatible target never falls back and does not repair or
rewrite authority data. Future May Touch remains the task-listed adapter, narrow
projection lineage helper, Fee contact-context bridge, effective formal projection,
formal preview/generation/gateway metadata wiring, dependency composition, and focused
backend/API tests only. No frontend/API client, Fee rules/pricing/UI, TASK_361D,
schema/repository/lifecycle, generic Test Record/Report, parser, LTR/public-drive, or
real-file paths are authorized.

Use temp SQLite/temp artifact fixtures for status/identity, Fee no-bypass/current
sample multiplier/no cross-Step aggregate, formal complete/partial/omission/stale/
no-output/rollback, TASK_360B API/layout/artifact regressions, TASK_361D isolation,
Fee export/generic Test Record/TASK_361B regressions, compile/build/diff/trailing/
line-count/forbidden-scope/no-real-mutation checks.
