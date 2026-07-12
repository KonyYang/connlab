# TASK_361A Contact Measurement Plan Authority Impact Contract Plan

## Status

Complete/accepted as the frozen contract and downstream planning basis after
Reviewer plan pass, user-approved docs-only Developer planning-first, Reviewer
implementation-readiness pass, and user-approved source-of-truth reconciliation on
2026-07-12. Product implementation, schema migration, API, UI, client, and test
changes were not authorized or completed by TASK_361A.

## Authority Decision

Use an independent Measurement Plan authority rooted at the Project, not an extension of Matrix Step `contact_plan_json`.

- A Matrix revision remains the execution map authority.
- A confirmed Measurement Plan revision owns LLCR/CR family, inclusion, target override, and review decisions.
- The effective formal projection joins the active confirmed Matrix with the active confirmed Measurement Plan. It never reads a Measurement Plan draft.
- During an unresolved Matrix impact review, unaffected compatible targets remain formal; changed, new, deleted, manually unmatched, or eligibility-changed targets are excluded from the effective formal projection.
- Basic Information is not an authority input. Fee and specialized record workbooks are downstream passive consumers. Generic Test Record remains out of this series.

## Frozen V1 Target Identity

The stable logical target key is not a generated draft or confirmed id. It is:

```text
cmp-target:v1|
group:<source_group_snapshot_id | manual_group_anchor_id>|
row:<source_row_snapshot_id | manual_row_anchor_id>|
step:<positive integer>|
suffix:<trimmed normalized suffix>
```

Rules:

1. `project_id` and the Measurement Plan root scope every key; they are not repeated in its display form.
2. Imported Group/Row components use the immutable source snapshot ids already carried by Matrix draft and confirmed models.
3. A manually created Group or Row has no stable cross-revision lineage today. The first independent-plan binding allocates a plan-owned manual anchor id and records the current Matrix entity id only as a binding locator.
4. A later Matrix revision must not auto-match a manual anchor by label, order, group key, or normalized test text. It creates an unmatched review candidate. The operator may explicitly rebind that candidate to the manual anchor in a `Needs review` draft.
5. `step_sequence` and the trimmed suffix are structural identity. Raw token spelling, generated ids, row/group order, and display text are evidence fields, not the target key.
6. Each binding snapshot additionally stores its `confirmed_matrix_id`, `confirmed_group_id`, `confirmed_row_id`, Matrix revision, display label, test item, contact kind, and sample quantity expression. These are locators and audit evidence, never replacements for the stable key.

This makes imported target correlation deterministic while making the unavoidable manual-lineage ambiguity visible and operator-confirmed instead of silently guessed.

## Independent Revision Lifecycle

`MeasurementPlan` is a Project-scoped root with one active confirmed revision and at most one editable revision. `MeasurementPlanRevision` is the auditable unit.

| State | Editable | Formal consumer visibility | Transition |
| --- | --- | --- | --- |
| `draft` | Yes | None | Explicit save; confirm when no unresolved impacts |
| `needs_review` | Yes | Only the previous confirmed revision's compatible projection | Resolve, accept/rebind/exclude, then confirm |
| `confirmed` | No | Active plan authority | Superseded only by a new confirmed revision |
| `superseded` | No | History only | Terminal |

- Save requires `expected_revision_fingerprint`.
- Confirm requires `expected_revision_id`, `expected_revision_fingerprint`, current `expected_matrix_binding_fingerprint`, and no unresolved structural impact.
- A Matrix change never mutates a confirmed plan. It creates or refreshes an editable review revision and impact records while the previous confirmed revision stays queryable.
- There is no implicit confirmation, no draft consumer fallback, and no global mutable review flag separate from the revision.

## Plan Snapshot And Storage Contract

TASK_361B must add an additive independent authority schema. Current Matrix `contact_plan_json` remains unchanged for compatibility and rollback.

Required conceptual records:

1. `measurement_plan_roots`: Project id, active confirmed revision reference, editable revision reference, bootstrap provenance, timestamps.
2. `measurement_plan_revisions`: immutable revision id, parent revision id, state, revision fingerprint, base confirmed Matrix id/revision, binding fingerprint, actor/timestamps, confirmation/supersession metadata.
3. `measurement_plan_target_snapshots`: one stable target key per revision with Matrix binding locator, eligibility/contact-kind snapshot, inclusion/coverage state, exclusion reason, override flag, impact status/reason, and display evidence.
4. `measurement_plan_family_snapshots`: materialized effective family rows for each target snapshot: family id, ordinal, label, count per sample, record label, prefix, included flag, and custom flag. The materialized rows avoid future consumers reconstructing authority from review text or mutable common UI state.
5. `measurement_plan_impacts`: classifier result from a base confirmed plan revision to a Matrix binding candidate, including category, severity, before/after evidence fingerprints, resolution state, and optional selected replacement target key.
6. `measurement_plan_audits`: append-only actor/time/action/reason rows for bootstrap, save, impact refresh, accept suggestion, explicit rebind, confirm, and supersede.

Constraints to implement only after future gate:

- unique `(revision_id, stable_target_key)`;
- unique `(target_snapshot_id, family_ordinal)` and `(target_snapshot_id, family_id)`;
- at most one `confirmed` revision per root and at most one editable (`draft` or `needs_review`) revision per root;
- positive revision sequence per root;
- a target family count is a non-negative integer string; `readings_per_sample` is the sum of included positive family counts and is stored with the target snapshot;
- contact kind is restricted to V1 `llcr` or `cr_specified_current`.

No migration is authorized in TASK_361A. Schema is nevertheless required: embedded JSON cannot represent independent immutable revision lineage, target-impact resolution, manual rebinding, or partial-compatible formal projection.

## Matrix Impact Classifier And Effective Projection

The classifier compares the active confirmed Measurement Plan's binding snapshot against the latest active confirmed Matrix and emits an ordered, fingerprinted result per stable target key.

| Matrix change | Classifier outcome | Formal projection |
| --- | --- | --- |
| No relevant change | `unchanged` | Current confirmed target |
| Method, condition, requirement, or display text only | `text_refresh_compatible` | Current plan target with current Matrix display fields; audit refresh |
| Valid selected-group sample quantity change only | `sample_quantity_compatible` | Current plan family/readings with current Matrix sample quantity; recalculate downstream units; audit refresh |
| Non-contact row/step change | `unrelated` | No plan effect |
| Added/deleted eligible target; Group/Row reassignment; step/suffix change; contact-kind change; selected membership change; unmatched manual candidate | `structural_review_required` | Exclude affected target; create or refresh `needs_review` draft |
| Invalid or non-deterministic sample quantity for an otherwise compatible target | `projection_review_required` | Exclude affected target until review; do not invent units |

`partial-compatible` is formal, not best-effort: an effective projection returns only target snapshots that are both confirmed and currently compatible. Every omitted target carries a concise review reason. Consumers must surface the projection status and must not use the obsolete Matrix embedded plan as a fallback once an independent plan root exists.

## Draft And Stale Semantics

- A save rejects a changed editable revision fingerprint with `409` and returns a reloadable summary.
- An impact refresh rejects a changed active Matrix id or binding fingerprint with `409`; it must recompute from the latest confirmed Matrix instead of applying stale suggestions.
- Confirm rejects any mismatch of revision id, revision fingerprint, or Matrix binding fingerprint, and rejects unresolved `structural_review_required` / `projection_review_required` impacts.
- Accept-all can only accept deterministic compatible suggestions. It cannot auto-rebind a manual candidate, include a new target, or overwrite an explicit target override.
- Explicit target rebind, include/exclude, and family override actions are auditable revision edits. They remain draft-only until confirmed.

## Legacy TASK_360 Bootstrap And Rollback

The migration path is non-destructive and idempotent.

1. Read only the active confirmed Matrix `step_quantities` and their typed `contact_plan_json` values. Do not bootstrap from open Matrix drafts.
2. If no eligible legacy plan exists, do not synthesize an empty independent plan. The first operator-created Measurement Plan draft is the bootstrap point.
3. For an eligible legacy snapshot, create one confirmed independent revision whose provenance is `(project_id, active_confirmed_matrix_id, canonical legacy contact-plan fingerprint)`. A unique bootstrap provenance constraint makes reruns idempotent.
4. Preserve each target's exact include/exclude/override and materialize its effective family snapshot. Canonically equal non-override targets may additionally be represented as a common profile in the UI, but target snapshots remain the historical authority.
5. Existing `contact_plan_json` rows are neither rewritten nor deleted. The new effective projection uses the independent plan only after bootstrap/confirmation succeeds; otherwise the compatibility adapter remains read-only.
6. Rollback disables the independent resolver/feature flag and restores the existing confirmed Matrix projection. Additive tables and audit rows remain for diagnosis; no destructive down migration or legacy data rewrite is permitted.

TASK_361B must re-gate its exact migration before implementation with temporary SQLite upgrade, repeated bootstrap, partially bootstrapped database, and rollback-adapter tests.

## API And UX Boundary For Future Lanes

Future API commands are typed application-service requests, not direct Matrix or Office calls:

- read plan summary/workspace and effective confirmed projection;
- create or save one editable revision;
- read current impact summary;
- accept compatible suggestions, explicitly rebind manual candidates, or edit inclusion/family overrides;
- confirm with both stale fingerprints;
- preview/generate/download clearly labeled draft output;
- read confirmed effective projection for downstream consumers.

The future UI is a dedicated Contact Measurement Setup workspace plus a compact Matrix summary. It is not a second editor card nested below the Matrix, and it is not modal-first. It shows current confirmed revision, review status, affected-target count, and the single next action. Draft output must visibly identify plan revision, base Matrix revision, and `Draft` / `Review` lineage. Operator copy uses business states such as `Needs review`, never raw ids, hashes, or backend enum names.

## Downstream Dependency And Package Plan

| Lane | Depends on | Owns | Must not own |
| --- | --- | --- | --- |
| `TASK_361B_CONTACT_MEASUREMENT_PLAN_AUTHORITY_BACKEND` | Accepted TASK_361A | Additive schema, domain/repository/application classifier, bootstrap, API DTO/routes, effective projection read model, backend tests | Setup UI, draft workbook, Fee/Test Record consumer migration |
| `TASK_361C_CONTACT_MEASUREMENT_SETUP_WORKSPACE` | Accepted TASK_361B | Frontend typed client helpers, dedicated setup workspace, compact Matrix summary, interaction/accessibility tests | Schema/classifier semantics, workbook generation, consumer migration |
| `TASK_361D_CONTACT_MEASUREMENT_DRAFT_WORKBOOK` | Accepted TASK_361B; can implement after `361B` in parallel with `361C` | Draft-only preview/generate/download, managed artifact lineage, temp-file tests | Generic Test Record, confirmed consumer migration, LTR/public-drive files |
| `TASK_361E_CONTACT_MEASUREMENT_CONFIRMED_CONSUMER_MIGRATION` | Accepted `361B`, then re-gated after `361C`/`361D` integration facts | Move specialized workbook and Fee consumers to effective confirmed projection; consumer regressions | Fee authoring rules, generic Test Record, StepInstance/Report |

TASK_361A May Touch remained docs only. Its accepted package contains the task,
plan, Discovery/Planner/Developer/Reviewer/reconciliation evidence, and board
source-of-truth updates.

TASK_361B now owns the planned backend authority foundation described in its own
task/plan/evidence. It remains planned-only. Future lanes must declare exact files
after their own Discovery and readiness gates. No lane may silently take ownership
of `MatrixEditorWorkspace.tsx`, existing TASK_360B workbook code, generic Test
Record, Fee rule/default-fill modules, Matrix parser/import, Basic Information,
LTR/public-drive, StepInstance, Report, release/settings, `.agents/**`, or
`docs/project_management/**` without separate authorization.

## Future Validation And Merge Gates

- Unit/repository: imported stable-key continuity, manual-anchor non-auto-match, explicit rebind, family sum/inclusion validation, revision state constraints, immutable history.
- Migration: empty database, legacy active snapshot bootstrap, idempotent rerun, invalid legacy JSON as readable blocked state, fallback adapter, rollback with no legacy mutation.
- Classifier/projection: each taxonomy row above; partial-compatible output omits impacted targets; compatible sample changes recalculate units without changing plan families; stale fingerprints reject safely.
- API: typed 409 reload paths, save/confirm guards, draft-versus-confirmed isolation, no direct Office/file operation.
- Frontend: compact summary and dedicated workspace states, review cues, focus/keyboard behavior, no nested cards/modal-first, no raw ids/hashes.
- Artifact/consumer: temporary directories only, draft labels/lineage, confirmed-only consumer regression, no real workbook or public-drive mutation.
- Package gate: focused tests, build, `py_compile`, `git diff --check`, trailing-whitespace, line-count, forbidden-scope, migration idempotency, and no-real-file scans. Each downstream lane stops at its Reviewer/QA/Integrator gate; no remote push is implied.

## Stop Point

Recommended next legal role: Reviewer implementation-readiness gate.

Blocking summary: none for Developer planning-first. Implementation remains unauthorized until the Reviewer readiness gate, source-of-truth reconciliation, and explicit user implementation approval.
