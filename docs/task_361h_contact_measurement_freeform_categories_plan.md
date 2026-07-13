# TASK_361H Contact Measurement Freeform Categories Plan

## Status

Developer implementation and B1-B3 fix pass complete; Reviewer implementation
re-gate, final QA re-smoke, and Integrator packaging/readiness passed. The lane is
complete/accepted locally. Remote push remains outside this lane.

### Authorization Checkpoint

Authorization is limited to the freeform category UX, included-count derivation,
blank-only shared apply and target overrides, monotonic `ff-llcr-N` / `ff-cr-N`
historical high-water and collision handling, persisted prefix resolution, the narrow
read-only workspace high-water DTO, existing single-target PATCH semantics, and the
focused validation/browser gates in this plan. It does not authorize any locked
consumer, workbook, authority-schema/lifecycle, parser, LTR, or real-file scope.

### Implementation And Review Checkpoint

- Developer completed the authorized implementation and reported `ready_for_review`.
- Initial Reviewer findings B1-B3 required sibling-target identity/label collision
  checks with no-write rollback, fresh identity issuance for semantic edits, and
  preservation of distinct legacy `record_label` values.
- Developer completed the focused fix pass. Reviewer implementation re-gate passed.
- The earlier governance-only QA checkpoint is superseded by the final QA re-smoke
  evidence. That final gate passed focused backend/frontend validation, build/static
  checks, and controlled disposable-data browser smoke.
- Integrator package isolation is complete; no external residual is part of this
  accepted lane.

## Discovery Gate

### Current Phase / Active Task / Role / Why Allowed

- Phase: Phase 11 controlled Matrix foundation.
- TASK_361A-E are complete/accepted; TASK_361E is accepted at `7e2409b4`.
- Active planning task: TASK_361H, the next unused TASK_361 sub-number.
- Role: Planner. The user requested a post-acceptance category-entry correction and
  explicitly limited this pass to Discovery and planned governance documents.

### Confirmed By User

- Contact categories are user-defined; High Power/Low Power/Signal are one connector
  example, not mandatory domain vocabulary.
- The primary input is one starter category row with add/remove for arbitrary rows.
- `readings_per_sample` is the included-count sum. Fee consumes only the total, while
  LLCR/CR workbooks retain category/prefix detail.
- Shared profile, target override, stable identity, lifecycle, confirmed consumer,
  and no-silent-overwrite semantics must remain.
- The cited XLSM is read-only UI/structure reference. No VBA execution or workbook
  mutation belongs to this lane.

### Confirmed By Repository Evidence

- `ContactMeasurementSetupWorkspace.tsx` renders every target family but only exposes
  Remove for `is_custom=true`, preserving built-in rows as special UI categories.
- `contactMeasurementPlanSelectors.ts` creates `custom-N` rows and validates only ids,
  required text, and non-negative counts.
- legacy Matrix selector defaults still define `high_power_pin`, `low_power_pin`, and
  `signal_pin`; after TASK_361C the related Matrix profile state/handlers appear
  disconnected from rendered setup UI and require implementation-time dead-code proof.
- The authority family table already stores arbitrary id, ordinal, label, integer
  count, record label, prefix, included, and custom metadata. It has no fixed-family
  enum or foreign-key vocabulary.
- The target patch command replaces one draft target's complete family snapshot,
  derives readings from included counts, and preserves prior confirmed revisions.
- TASK_361A intentionally materializes target families as authority and permits a
  common profile only as a UI projection over canonically equal non-overrides.
- TASK_361E formal consumers are already accepted and consume effective confirmed
  target facts, so this lane need not change Fee or workbook source authority.

### Planner Inference And Decisions

- No schema migration is necessary. Arbitrary categories and stable ordering already
  fit the accepted model.
- `is_custom` remains compatibility metadata but loses UI privilege. All rows are
  editable/removable in a draft.
- The shared profile remains transient/derived. It is not persisted separately and
  applies only through existing target patch commands to blank targets.
- New category ids should be opaque and stable, not label-derived. Existing ids are
  never rewritten.
- Prefix remains nonblank in persisted authority to preserve TASK_360B/361D behavior.
  The operator may leave the visible field blank only because the row owns a shown,
  stable generated fallback prefix; no silent post-save renaming occurs.
- Backend application validation should enforce included positive counts and
  normalized label/prefix uniqueness. This is a narrow validation correction, not a
  lifecycle-state or schema change, and requires Reviewer plan re-gating.

### Not Yet Confirmed

- None that blocks Reviewer plan gate. Optional connector templates are explicitly
  non-authoritative and may be omitted from V1 if Reviewer judges them unnecessary.

## Product And Data Design

### Shared Profile Projection

1. Canonicalize included non-override target families by stable id, order, normalized
   label/count/resolved prefix/included state.
2. If all eligible non-override targets agree, hydrate the shared editor from that
   profile.
3. If no target has categories, create one unsaved starter row.
4. If target families diverge, show `Targets use different categories`; do not choose
   one silently. The shared editor starts local and can apply only to blank targets.
5. `Apply to blank targets` previews count, then invokes existing stale-safe single
   target commands. A partial failure reloads latest state and reports which targets
   were not changed; it never retries over nonblank targets.

### Category Row

- stable internal id, not editable and not label-derived;
- include checkbox;
- operator label;
- positive whole-number count when included;
- optional operator series/prefix with visible stable fallback;
- move up/down and remove commands;
- read-only expanded example such as `P1-P4` when prefix/count are valid.

`record_label` remains compatible with the current DTO. V1 derives it from the
operator label unless an existing row already has a distinct record label, in which
case that value is preserved and remains editable only in target details if the
existing UI contract requires it. Reviewer should reject any duplicate hidden label
authority.

### Stable Identity Issuance

1. Namespace is one Measurement Plan root plus contact kind. New ids are
   `ff-llcr-N` and `ff-cr-N`; shared categories copy the same id across same-kind
   targets, while LLCR and CR sequences are independent.
2. Backend reads maximum parseable `N` from every persisted family snapshot under the
   root, including active, editable, superseded, and bootstrap history. The workspace
   response returns both high-water values. No schema counter is added.
3. Frontend allocates `max(server high-water, reloaded workspace ids, pending local
   ids) + 1`. Deleting a row cannot decrement or reuse the sequence.
4. Count/include/order overrides retain identity. Explicit label or resolved-prefix
   changes create a new id. Existing legacy ids are never rewritten.
5. Save/apply/stale re-apply reloads latest state. A pending id collision with a
   different logical category fails closed before PATCH. Backend rejects duplicate
   target ids and divergent same-id normalized label/prefix use within a revision and
   contact kind, with transaction rollback and no writes.

This requires one additive read-only workspace field and repository query. It adds
no table, counter, endpoint, or mutation command.

### Prefix Resolution

1. Persisted `record_prefix` is authoritative; render never recomputes it.
2. New/edited input is NFKC-normalized, trimmed, uppercased, stripped to ASCII
   `A-Z0-9`, and limited to `1..64` characters.
3. Blank input resolves once from the label by the same rule. If empty, fallback is
   `C{N}` using the immutable family sequence. The resolved value is displayed and
   sent in the first request.
4. Reorder/reload does not change it. Label rename preserves it. Explicit prefix
   edit/clear requests new resolution and a new family id.
5. Uniqueness uses the normalized alphanumeric value within one included
   Group-Step/contact-kind section. Duplicate blocks without write; separate sections
   may reuse a prefix. Legacy values round-trip unchanged until explicit edit.

### Edge Policy

- Blank starter: local only; no API call until valid apply/save.
- Zero/negative/decimal: included row blocked, no rounding. Excluded row contributes
  zero and may retain historical value.
- Duplicate label/prefix: trim, Unicode-normalize, case-fold, then block within one
  profile/target; cross-target reuse is allowed.
- Delete used row: remove only from current local draft target; Save creates a new
  draft snapshot, while prior confirmed revision remains intact. Shared-profile
  removal does not mutate existing overrides.
- Ordering: explicit ordinal, accessible move controls, stable id/prefix unaffected.
- Empty included target: blocked. Excluded target may have no included categories.

## File-Level Future Plan

1. Add selector-level freeform category row model, stable id/fallback prefix helper,
   canonical profile hydration, blank-only apply preview, and strict validation.
2. Reshape setup workspace into a compact shared category editor plus existing target
   list/override editor. Do not introduce nested cards or modal-first editing.
3. Update model orchestration to keep local edits, stale recovery, and target command
   reload semantics explicit.
4. Add a focused backend family-validation helper and delegate from the lifecycle
   service; do not grow the 450-line service or change revision-state semantics.
5. Add the read-only historical high-water query, workspace response field, and typed
   client field while leaving all mutation DTOs unchanged.
6. Remove the legacy fixed-family Matrix selector/state only if implementation proof
   confirms it has no rendered/runtime caller after TASK_361C. Otherwise adapt it to
   freeform rows without changing Matrix parser or Step quantity behavior.
7. Add focused tests, run accepted consumer/workbook regressions, and perform browser
   smoke at desktop/narrow widths.

## May Touch / Must Not Touch / Locked Paths

The exact future path list and locks are authoritative in
`tasks/TASK_361H_CONTACT_MEASUREMENT_FREEFORM_CATEGORIES.md`. In summary, the lane may
touch the contact-measurement frontend feature, its CSS/tests, a narrow backend
validation helper/lifecycle delegation, one read-only historical id high-water query,
one additive workspace/client field, and proven-dead Matrix fixed-profile code.
Schema, lifecycle state machine, mutation commands, Fee, workbooks, generic outputs,
parser, LTR/public drive, real files, and external residuals remain locked.

## Dependencies And Parallelism

- Serial prerequisite: TASK_361A-E accepted.
- TASK_361H is one corrective lane; frontend and backend validation implementation
  may be developed in parallel only after one reviewed plan fixes the shared contract.
- No workbook, Fee, schema, or parser lane may run inside TASK_361H.

## Validation And Merge Gates

Use the task's focused selector/model/component/backend validation, accepted
TASK_361B/C/E and TASK_360B/361D regressions, build/static scans, and desktop/narrow
browser smoke. Integrator must package only reviewed TASK_361H hunks.

## Definition Of Ready

Satisfied for implementation. B1 is resolved with exact schema-free historical
high-water, monotonic allocation/collision behavior, persisted prefix normalization/
fallback, and acceptance cases. Reviewer plan re-gate and implementation-readiness
passed, and the user explicitly authorized the bounded implementation.

## Developer Planning-First Refinement

### Exact Implementation Order

1. Add a narrow repository read-only `family_id_high_water_by_kind(project_id)` that
   scans every root-owned target-family snapshot for parseable `ff-llcr-N` and
   `ff-cr-N` values. It returns only the greatest positive integer per kind and does
   not repair, rename, delete, or allocate persisted rows.
2. Project that data from `ContactMeasurementPlanWorkspaceReadService` as additive
   `family_id_high_water_by_kind: { llcr: number, cr_specified_current: number }`.
   Extend only the existing workspace response and typed client read model; existing
   PATCH request and authority command payloads remain unchanged.
3. Isolate backend family preparation/validation in a focused application helper:
   parse only the new `ff-*` namespace, derive a one-time resolved prefix for new or
   explicitly edited rows, enforce positive included counts and in-target normalized
   duplicate checks, then delegate through the existing lifecycle target replacement
   transaction. Its final collision result remains `family_identity_collision` with
   no snapshot-family write.
4. Replace selector-local `custom-N` issuance with a pure freeform category model.
   It allocates `max(server high-water, current reloaded ids, pending local ids) + 1`,
   tracks per-kind issuance through deletion, and returns explicit collision state
   rather than renaming a row. The selector owns NFKC/uppercase ASCII prefix
   normalization, fallback `C{N}`, derived included-count total, move operations,
   and uniform-profile detection.
5. Make the hook reload before save, blank-only shared apply, and stale re-apply;
   it compares pending `ff-*` logical identity against the latest workspace and stops
   before the existing PATCH if the same id identifies another label/prefix. It then
   sends the unchanged single-target command with already-resolved prefix values.
6. Reshape the workspace presentation into an inline default-category strip followed
   by selected-target override editing. Every row exposes include, label, count,
   optional prefix, remove, and move controls. An empty uniform profile has exactly
   one local starter row; connector pin examples are an explicit optional template.
   No modal, new route, bulk write, or nested card is introduced.
7. Remove fixed Matrix profile state only after an implementation-time call-site
   search proves it is disconnected. Otherwise keep it untouched and confine the
   migration to the independent workspace.

### Frozen Read And Write Boundaries

- `family_id_high_water_by_kind` is a workspace-only read field. There is no new
  endpoint, counter table, allocation command, schema change, or mutation DTO.
- The existing single-target PATCH remains the final write boundary. Its transaction
  must reject duplicate family ids and divergent normalized label/prefix uses for one
  `ff-*` id in one revision/kind before any family replacement is persisted.
- Shared profile apply fans out only through the existing per-target stale-safe
  command after determining eligible blank targets. Nonblank, override, divergent,
  or confirmed targets are skipped, never overwritten.
- Persisted legacy ids and prefixes bypass new namespace/prefix rewriting. The new
  normalizer applies only to newly created or explicitly edited values.

### Exact Future Tests

- Selector/model: default starter, optional template, positive included count,
  excluded zero contribution, sum derivation, move order, add A/add B/remove A/add C,
  per-kind high-water, reload/pending maxima, stale collision no PATCH, blank prefix
  fallback, reorder/reload/rename stability, explicit prefix edit identity renewal,
  and normalized duplicate no-write.
- Workspace/component: common profile only for equal non-overrides, blank-only apply
  preview, override preservation, all row controls keyboard reachable, and narrow
  rows stack without horizontal overflow.
- Backend temporary SQLite: full-history high-water, legacy-id exclusion, duplicate
  id/divergent logical identity rollback, positive included counts, prefix parser and
  duplicate domain, and additive workspace DTO/API response.
- Regressions: TASK_361B/C workspace/lifecycle, TASK_361E confirmed Fee adapter,
  TASK_360B formal workbook, and TASK_361D draft workbook. Browser smoke is limited
  to local workspace edits and read/write test fixtures, never real databases/files.

### Package Isolation

The future package may contain only the explicit task-file May Touch paths. In
particular, exclude `backend/api/dependencies.py` unless the existing workspace
provider requires only the additive read field, and stop for Planner reconciliation if
the implementation needs a new PATCH command, schema migration, authority lifecycle
change, workbook/Fee consumer alteration, or frontend raw fetch.
