# TASK_361H Reviewer Plan Gate

Status: reviewer_blocked
Task: `TASK_361H_CONTACT_MEASUREMENT_FREEFORM_CATEGORIES`
Lane: `contact-measurement-freeform-categories`
Date: 2026-07-13
Role: Reviewer

## Gate

Reviewer plan gate only. No product code, schema, API/client, workbook, or test
implementation was changed or authorized by this review.

Current phase: Phase 11, Project Workbench / Matrix / Approval Package controlled
foundation.
Current active task: `TASK_361H_CONTACT_MEASUREMENT_FREEFORM_CATEGORIES`, planned
only.
Why allowed: TASK_361A-E, TASK_361F, and TASK_361G are accepted; the board records
TASK_361H as the current planned corrective lane and assigns this plan gate.

## Finding

### B1: Stable family identity and resolved-prefix contract is not implementation-exact

The plan correctly removes High Power/Low Power/Signal as fixed authority and keeps
the family snapshot schema vocabulary-neutral. Its one-starter-row, freeform label,
included positive-count, shared-profile, blank-only apply, target override, and
non-destructive compatibility directions are sound.

However, it does not freeze the collision-safe issuance and persistence algorithm for
new `family_id` values or the exact resolved-prefix compatibility rule. This is a
material gap because the current frontend adds `custom-N` by scanning only the current
in-memory target array, while persisted family ids must remain unique per target. A
delete/reload/stale re-apply sequence can otherwise reissue an id. The plan also says
the visible prefix is optional with a stable fallback, but does not specify the exact
fallback derivation, normalized collision domain, or preservation of the existing
persisted prefix grammar used by TASK_360B/TASK_361D expansion.

**Required Planner fix pass:** add one precise, source-of-truth contract that:

1. Names a collision-safe opaque-id strategy. For example, a generated id must be
   fresh against the latest persisted target family ids before a PATCH, never be
   label-derived, and remain unchanged through add/reorder/remove/save/reload/draft
   copy/stale re-apply/confirmation. Define retry or fail-closed behavior if a latest
   reload detects a collision.
2. Defines resolved prefix as the sole persisted value when the operator leaves the
   optional field blank, including stable derivation from the immutable family id,
   display behavior, normalization and uniqueness domain, and the existing accepted
   prefix character/length contract. No post-save silent rename may occur.
3. Adds focused acceptance cases: add A, add B, remove A, add C; persisted/reloaded
   id collision; stale re-apply collision; blank-prefix stability through reorder and
   reload; normalized label/prefix collision; and distinct-prefix workbook regression.

The fix must remain schema-free and preserve existing family snapshots, blank-only
apply, override precedence, Fee's derived-total-only boundary, and TASK_360B/TASK_361D
category/prefix behavior.

## Verified Non-Blocking Facts

- The existing authority family snapshot model is vocabulary-neutral and stores id,
  ordinal, label, count, record label, prefix, inclusion, and compatibility metadata;
  a schema migration is not required for freeform categories.
- The proposed UI is appropriately product-register, compact, inline, and accessible:
  one starter row, no modal-first flow, keyboard-reachable add/remove/reorder, dense
  desktop rows, and narrow-width stacking.
- The task correctly locks Fee rules/pricing/UI, TASK_361E consumers, TASK_360B/TASK_361D
  workbook behavior, authority lifecycle/schema, generic Test Record/Report, parser,
  LTR/public drive, real files, frontend API client, and external residuals.

## Validation Performed

- Re-read AGENTS, task board, task, plan, Planner evidence, accepted TASK_361A-E/F/G
  context, and current status/diff.
- Loaded `$impeccable` product context and read frontend architecture controls.
- Verified current code facts: the workspace removes only `is_custom` rows; the
  selector currently issues `custom-N` from current local state; current validation
  permits non-negative counts and requires stored prefixes; the Matrix validation
  preserves an existing constrained prefix contract.
- Confirmed the Planner pass is documentation-only. Existing TASK_361F operational
  evidence and board changes are external; no TASK_361H product code changed.

## Decision

`reviewer_blocked`

Recommended next role/action: Planner fix pass limited to B1 contract and acceptance
coverage refinement. Do not route Developer planning-first or implementation.

Blocking summary: stable freeform family ids and optional-prefix fallback must be
collision-safe and workbook-compatible before implementation planning can begin.

---

# TASK_361H Reviewer Plan Re-Gate: B1

Status: reviewer_pass
Task: `TASK_361H_CONTACT_MEASUREMENT_FREEFORM_CATEGORIES`
Lane: `contact-measurement-freeform-categories`
Date: 2026-07-13
Role: Reviewer

## B1 Resolution

The revised plan now freezes a collision-safe, schema-free identity contract. New
ids are `ff-llcr-N` and `ff-cr-N`, scoped by Measurement Plan root and contact kind.
The backend derives per-kind high-water from all persisted target-family snapshots,
including active, editable, superseded, and bootstrap history. The client allocates
above the maximum of server high-water, reloaded state, and local pending ids, so
delete/reorder cannot reuse an identity. Save, apply, and stale re-apply reload first;
a different logical category with the same pending id fails closed before PATCH, while
backend validation remains the transactional final reject.

Resolved prefix behavior is also implementation-exact. Persisted `record_prefix` is
the only workbook prefix. Explicit input or label-derived blank fallback is NFKC-
normalized, trimmed, uppercased, reduced to ASCII alphanumeric content, and bounded
to the accepted 1..64 DTO contract. An empty normalized label resolves once to
`C{N}` from the immutable family sequence. The resolved value is displayed and sent
on first write, then is never recomputed by reorder, reload, or label rename. Its
normalized uniqueness is scoped to included families in one Group-Step/contact-kind
section; legacy ids and prefixes round-trip unchanged. This preserves TASK_360B and
TASK_361D category/prefix expansion without changing either implementation.

The expanded acceptance gate directly covers add A/add B/remove A/add C, historical
high-water after reload, stale collision before PATCH, transactional backend
collision/no-write, blank-prefix reorder/reload stability, label rename semantics,
normalized duplicate blocking, and legacy/workbook regressions.

## Scope And Readiness

The B1 refinement adds no schema or mutation command. The only justified boundary
extension is a typed read-only workspace high-water field and its repository query;
the existing PATCH request remains unchanged. The rest of the lane remains limited
to freeform setup UX/selectors/model/CSS/tests, narrow application validation and
lifecycle delegation, and proven-dead Matrix fixed-profile cleanup. Fee rules/pricing/
UI, TASK_361E consumers, TASK_360B/TASK_361D behavior, authority lifecycle/schema,
generic Test Record/Report, parser, LTR/public drive, real files, and external
residuals remain locked.

The compact inline product-register UX remains appropriate: one starter row, optional
template, explicit blank-only apply, target overrides, keyboard-addressable reorder
and removal, row-level validation, and narrow-width stacking without modal-first or
fixed category authority.

## Validation Performed

- Re-read the updated task, plan, Planner evidence, prior Reviewer B1 finding, board,
  accepted TASK_361A-E/F/G context, and current authority/API/repository contracts.
- Confirmed `family_id` and `record_prefix` are existing bounded persisted fields, the
  family schema remains vocabulary-neutral, and no schema migration is required.
- Confirmed the plan preserves current target replacement, confirmed-history, and
  consumer/workbook boundaries while adding only a read-only high-water projection.
- Verified the Planner pass is documentation-only; current status shows no TASK_361H
  product, schema, test, database, or real-file modification.

## Decision

`reviewer_pass`

Recommended next role/action: User approval, then Developer planning-first. Do not
route Developer implementation directly.

Blocking summary: none. B1 identity and resolved-prefix contracts are closed.

---

# TASK_361H Reviewer Implementation-Readiness Gate

Status: reviewer_pass
Task: `TASK_361H_CONTACT_MEASUREMENT_FREEFORM_CATEGORIES`
Lane: `contact-measurement-freeform-categories`
Date: 2026-07-13
Role: Reviewer

## Planning-First Verification

Developer planning-first is documentation-only. Current status contains TASK_361H
task/plan/evidence documents but no TASK_361H frontend, backend, schema, test, API
client, real database, or file mutation. Existing TASK_361F operational evidence and
board edits remain external governance residuals.

## Implementation Readiness

The future UX is concrete and compatible with the product register: one unsaved blank
freeform category starter, inline add/remove/reorder/include controls, arbitrary
label, positive whole-number included count, optional visible prefix, and explicit
target override editing. High Power/Low Power/Signal are an opt-in template only;
they are not fixed authority. Derived readings are the included-count sum, so no
generic duplicate quantity entry surface is added. Shared categories remain a
transient equal-non-override projection, preview and apply only to blank eligible
targets, and never overwrite divergent, override, confirmed, or nonblank targets.

The `ff-llcr-N` / `ff-cr-N` root-and-kind contract is sufficiently exact: historical
high-water plus reloaded and pending maxima issue monotonic ids; delete/reorder does
not reuse them; stale collisions stop before PATCH; lifecycle validation provides the
transactional no-write final rejection. Resolved prefix behavior is likewise ready:
NFKC/trim/uppercase/ASCII normalization, 1..64 bound, immutable `C{N}` fallback,
one-time persistence, no recomputation after reorder/reload/label rename, normalized
duplicate no-write, and legacy round-trip compatibility.

The sole API/client adjustment is an additive read-only workspace high-water field.
Existing PATCH semantics and all authority lifecycle/mutation commands remain fixed.
The exact May Touch list, focused selector/model/component/backend tests, consumer
workbook regressions, build/static scans, and disposable-data desktop/narrow browser
smoke are proportionate. Fee rules/pricing/UI, TASK_361E, TASK_360B/TASK_361D,
authority schema/lifecycle, generic Test Record/Report, parser/import, LTR/public
drive, real files, and other locked paths remain excluded.

## Source-Of-Truth Residual

The task/plan/Developer evidence record plan re-gate pass and docs-only planning-first
completion, but the current board still says Reviewer plan re-gate pending. This gate
does not authorize implementation. Before implementation, Planner must reconcile the
board/task/plan/evidence to the readiness outcome and the user must provide separate,
explicit implementation approval.

## Validation Performed

- Re-read AGENTS, board, TASK_361H task/plan/Planner/Developer/prior Reviewer
  evidence, and accepted TASK_361A-E/F/G context.
- Reconfirmed current workspace/model/selector, lifecycle, API family DTO, and family
  storage facts supporting the narrow high-water/read-only and validation plan.
- Confirmed planning-first is docs-only and no product validation is due at this
  readiness gate. Existing external residuals remain excluded.

## Decision

`reviewer_pass`

Recommended next role/action: User implementation approval, then Planner/source-of-
truth reconciliation before Developer implementation. Do not route Developer
implementation from this gate.

Blocking summary: none for technical readiness; source-of-truth reconciliation is
mandatory before implementation authorization.

---

# TASK_361H Reviewer Implementation Gate

Status: reviewer_blocked
Task: `TASK_361H_CONTACT_MEASUREMENT_FREEFORM_CATEGORIES`
Lane: `contact-measurement-freeform-categories`
Date: 2026-07-13
Role: Reviewer

## Findings

### B1: The freeform identity collision contract is not enforced at the PATCH boundary

The task plan requires the existing target PATCH transaction to reject a pending
`ff-*` id when the same revision/contact kind already uses that id for a different
normalized label or resolved prefix, before replacing any family snapshot. It also
requires normalized label and prefix uniqueness within the edited target.

`validate_contact_measurement_families()` currently checks only duplicate ids in the
incoming target payload and normalized prefixes for `ff-*` rows. It neither checks
normalized labels nor queries sibling targets in the editable revision for divergent
same-id logical categories. `replace_families()` then deletes and inserts only the
selected target. Therefore a stale/reloaded client can persist the same `ff-*` id
with different label/prefix semantics in another same-kind target, rather than
returning the planned no-write `family_identity_collision` result.

Required Developer fix: add a narrow repository-backed, transactional pre-replacement
identity check for the editable revision/contact kind; reject divergent same-id
normalized label/prefix and duplicate normalized labels/prefixes with no family
write. Add temporary-SQLite regressions for shared same-id/same-semantics acceptance,
divergent same-id rejection, duplicate normalized label rejection, and unchanged
target rows after rejection.

### B2: Editing a freeform label or resolved prefix does not issue a new stable identity

The accepted contract permits count/include/order changes to retain identity, but
requires an explicit label or resolved-prefix change to receive a new monotonic id.
The current `updateFamily()` path changes label/prefix in place, while
`resolveSelectedFamilyPrefix()` only changes the prefix. Neither route issues a new
`ff-llcr-N` / `ff-cr-N` identity or advances pending issuance state. This makes B1
observable in ordinary target editing and breaks the stated immutable-category
identity rule.

Required Developer fix: distinguish semantic edits from count/include/order edits;
allocate a fresh per-kind id before PATCH for a changed freeform label or resolved
prefix, preserve the resolved prefix after issuance, and add selector/model coverage
for label edit, prefix edit, stale reapply collision, and reload persistence.

### B3: Existing distinct `record_label` values are overwritten by the visible label field

The plan preserves a pre-existing distinct `record_label` for compatibility with the
TASK_360B/TASK_361D expansion paths. The workspace label handler currently writes
both `label` and `record_label`, and the former record-label control was removed.
Editing an imported legacy category therefore loses a distinct persisted record label
instead of preserving it or exposing an explicit compatible edit path.

Required Developer fix: preserve an existing distinct `record_label` during label
edits, or provide a deliberate target-detail control with tests. Do not introduce a
second hidden label authority.

## Verified Non-Blocking Facts

- The candidate remains within the approved contact-measurement backend/workspace/API
  client/frontend/test surface. No Fee, workbook, schema, authority lifecycle,
  generic Test Record/Report, parser, LTR/public-drive, real-file, or governance-path
  implementation hunk was found. External board and TASK_361F QA evidence remain
  excluded.
- The starter row, add/remove/reorder/include controls, optional HP/LP/Signal
  templates, derived included-count display, blank-only non-override apply, read-only
  high-water DTO, and existing single-target PATCH transport are present.
- Historical root/kind high-water scanning is read-only and includes revision history.
  Python module sizes remain below the hard limit.

## Validation Performed

- Re-read AGENTS, board, TASK_361H task/plan/Planner/Developer/prior Reviewer evidence,
  actual candidate diff, and the applicable TASK_360B/TASK_361D compatibility bounds.
- `py -m pytest -p no:cacheprovider --basetemp=tmp\\task_361h_reviewer_gate ... -q`
  over changed family/workspace/API coverage plus confirmed workbook regressions: `21 passed`.
- `npm test -- ContactMeasurementPlanSummaryCard ContactMeasurementSetupWorkspace
  contactMeasurementPlanSelectors useContactMeasurementPlanModel --run`: `5 files / 18 passed`.
- `py -m py_compile` for changed backend modules passed. Candidate `git diff --check`
  has only existing LF/CRLF warnings; locked-path scan found no candidate scope leak.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer fix pass limited to B1-B3 and their focused
temporary-SQLite/frontend regressions. Do not route QA or Integrator.

Blocking summary: the implemented high-water allocator is useful, but it lacks the
required authoritative collision/semantic-renewal enforcement and can overwrite a
distinct legacy record label.

---

# TASK_361H Reviewer Implementation Re-Gate: B1-B3

Status: reviewer_pass
Task: `TASK_361H_CONTACT_MEASUREMENT_FREEFORM_CATEGORIES`
Lane: `contact-measurement-freeform-categories`
Date: 2026-07-13
Role: Reviewer

## B1-B3 Resolution

- B1 is closed. `set_target_inclusion()` now invokes family payload and sibling
  authority validation inside the existing repository transaction before updating
  target fields or replacing family rows. The sibling query is scoped to the editable
  revision and contact kind, excluding the edited target. It accepts a shared same-id,
  same-semantics category, but rejects divergent normalized label/prefix reuse and
  duplicate normalized labels as the typed existing HTTP `422` conflict envelope.
  Temporary SQLite and API regressions assert no target-family write after rejection.
- B2 is closed. A label blur or resolved-prefix blur renews a changed freeform family
  through the per-kind high-water allocator. Count, inclusion, ordering, and removal
  retain identity; stale reapply carries the already-issued identity and the backend
  remains the final fail-closed boundary.
- B3 is closed. Display-label edits now patch only `label`; an existing distinct
  `record_label` survives. New freeform/template rows initialize their record label
  from their initial display label, so TASK_360B/TASK_361D consumers retain compatible
  persisted category metadata.

## Scope Review

The candidate remains restricted to the approved freeform validation/repository read,
existing lifecycle transaction, read-only workspace/client projection, setup
selectors/model/presentation, and focused tests. No schema, lifecycle-state, Fee,
TASK_360B/TASK_361D behavior, generic Test Record/Report, parser, LTR/public-drive,
real database/file, or governance-path product change was found. External board and
TASK_361F operational-QA residuals remain excluded.

## Validation Performed

- Temporary SQLite authority/API/confirmed-consumer/workbook suite: `27 passed`.
- Additional confirmed LLCR/CR projection regression: `4 passed`.
- `npm test -- ContactMeasurementPlanSummaryCard ContactMeasurementSetupWorkspace
  contactMeasurementPlanSelectors useContactMeasurementPlanModel
  DraftMeasurementPlanWorkbookPanel useDraftMeasurementPlanWorkbookModel
  matrixContactMeasurementPlanSelectors --run`: `7 files / 24 tests passed`.
- `py -m py_compile` passed for touched backend modules.
- `npm run build` passed with only the existing Vite chunk-size warning.
- Candidate diff-check has only existing LF/CRLF warnings; trailing-whitespace,
  locked-path, and line-count checks are clean. Touched Python modules remain below
  the project hard limit.

## Decision

`reviewer_pass`

Recommended next role/action: QA gate, including the deferred controlled-fixture
browser smoke. Do not route Integrator from this gate.

Blocking summary: none for Reviewer implementation re-gate. Browser smoke remains a
QA responsibility and must use disposable authority data only.

---

# TASK_361H Reviewer Focused Re-Gate: QA B1

Status: reviewer_blocked
Task: `TASK_361H_CONTACT_MEASUREMENT_FREEFORM_CATEGORIES`
Lane: `contact-measurement-freeform-categories`
Date: 2026-07-13
Role: Reviewer

## Finding

### B1R: Record-label initialization loses legacy provenance after semantic identity renewal

The QA B1 helper decides that a family is safe to initialize from its display label
when its current `ff-*` id is absent from the loaded target's persisted id set. That
is correct for the local blank starter, but not sufficient for provenance.

An existing persisted legacy/custom family may have an empty `record_label`. Its
label or prefix semantic edit correctly renews the family id. The renewed id is then
absent from the persisted-id set, so `initializePendingFreeformRecordLabels()` and
the stale-reapply variant treat it as a new blank row and write a guessed record
label. This violates the QA B1 contract: persisted legacy/custom empty record labels
must not be guessed, patched, or migrated, and semantic renewal must preserve the
record label.

Required Developer fix: retain explicit local-new versus persisted-origin provenance
across a label/prefix identity renewal and stale reapply. Initialize only a family
originating from the blank starter or an explicit Add/template action; never infer
that status from the renewed id alone. Add a model regression that begins with a
persisted `ff-*` family whose `record_label` is empty, renews label and prefix, saves
and stale-reapplies it, and asserts every PATCH retains the empty record label. Keep
the existing positive default-blank save/apply regression.

## Verified Non-Blocking Facts

- The QA B1 normalization is invoked immediately before Save target, blank-only
  apply, and stale reapply. It leaves distinct nonempty legacy record labels intact.
- The fix does not change the single-target PATCH DTO, backend/API/schema/lifecycle,
  Fee, TASK_360B/TASK_361D workbook behavior, generic outputs, parser, LTR/public
  drive, or real files. Candidate locked-path scan is clean.
- Semantic id renewal and count/order/include behavior remain in the approved
  frontend model/selector boundary.

## Validation Performed

- Re-read QA B1 evidence, Developer evidence, actual selector/model/test diffs, and
  the previous Reviewer B1-B3 decision.
- `npm test -- ContactMeasurementPlanSummaryCard ContactMeasurementSetupWorkspace
  contactMeasurementPlanSelectors useContactMeasurementPlanModel
  DraftMeasurementPlanWorkbookPanel useDraftMeasurementPlanWorkbookModel
  matrixContactMeasurementPlanSelectors --run`: `7 files / 27 tests passed`.
- The passing tests cover the new blank starter, but no test covers a persisted empty
  record label followed by semantic id renewal; direct code inspection shows the
  incorrect id-only classification.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer fix pass limited to B1R provenance tracking
and its focused frontend regressions. Do not route QA re-smoke until B1R passes.

Blocking summary: no backend or scope issue; the remaining defect is a narrow
frontend compatibility write to a persisted empty legacy/custom record label.

---

# TASK_361H Reviewer Focused Implementation Re-Gate: Provenance Fix

Status: reviewer_blocked
Task: `TASK_361H_CONTACT_MEASUREMENT_FREEFORM_CATEGORIES`
Lane: `contact-measurement-freeform-categories`
Date: 2026-07-13
Role: Reviewer

## Finding

### B1R2: Freeform provenance is not scoped to the active project

The provenance registry is a single ref keyed only by `ff-*` id. Both the initial
project-load effect and `reload()` merge persisted family ids with `??=`, but neither
resets that registry when `projectId` changes. `ff-llcr-1` / `ff-cr-1` are deliberately
per-root/per-kind ids and therefore naturally recur across projects. The setup route
passes a changing `projectId` to the same page component, so React can retain this hook
instance during a project-to-project route transition.

Consequently, a local starter `ff-llcr-1` from project A can leave the origin recorded
as `starter`; when project B loads a persisted `ff-llcr-1` with an empty
`record_label`, the merge preserves `starter`. Save or blank-only apply can then
initialize project B's persisted legacy label, violating the promised no-guess,
no-migration rule. The semantic renewal and stale-reapply helpers correctly move an
existing origin, but they cannot make a globally reused id project-safe.

Required minimal Developer fix:

1. Scope/reset freeform origins to the active project before merging workspace data
   (and reset related local issuance/semantic state that is keyed by the same ids).
2. Add a hook rerender regression: load project A's blank starter, rerender for
   project B with persisted empty-label `ff-llcr-1`, renew and save it, and assert
   no record label is inferred and no PATCH is sent when the existing validation
   rejects it.
3. Add the explicitly required persisted-empty **prefix renewal then stale reapply**
   regression. The current stale test renews a label only, so it does not prove the
   requested prefix path preserves provenance and leaves `record_label` empty.

## Verified Non-Blocking Facts

- Within one project, provenance is explicitly represented as `starter`, `added`,
  `template`, or `persisted`; semantic renewal and stale reapply carry that origin.
  The initialization selector itself limits writes to the first three origins and
  provenance is not included in the PATCH payload.
- The current persisted-empty renewal test confirms that label and prefix renewals
  retain an empty `record_label` through a failed Save. The current stale-reapply test
  covers a label renewal, not the requested prefix renewal.
- Candidate changes remain frontend model/selector/test/evidence only. No schema,
  backend command/API contract, Fee rule/pricing/UI, TASK_360B/TASK_361D workbook
  behavior, generic Test Record/Report, parser, LTR/public-drive, real database/file,
  or governance-path implementation hunk was found. External residuals remain
  excluded.

## Validation Performed

- Re-read AGENTS, board, TASK_361H task/plan/Planner/Developer/QA/prior Reviewer
  evidence, the actual provenance selector/model/test diff, and route mounting facts.
- `npm test -- ContactMeasurementPlanSummaryCard ContactMeasurementSetupWorkspace
  contactMeasurementPlanSelectors useContactMeasurementPlanModel
  DraftMeasurementPlanWorkbookPanel useDraftMeasurementPlanWorkbookModel
  matrixContactMeasurementPlanSelectors --run`: `7 files / 29 tests passed`.
- Candidate diff-check has only existing LF/CRLF warnings. No locked candidate path
  or real-artifact mutation target was found.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer fix pass limited to B1R2 project-scoped
provenance and the two focused frontend regressions above. Do not route QA re-smoke
until this re-gate passes.

Blocking summary: provenance is currently local to a hook instance but not local to a
project, allowing an id collision across projects to turn persisted empty legacy
metadata into an inferred write.

---

# TASK_361H Reviewer Focused Implementation Re-Gate: B1R2

Status: reviewer_blocked
Task: `TASK_361H_CONTACT_MEASUREMENT_FREEFORM_CATEGORIES`
Lane: `contact-measurement-freeform-categories`
Date: 2026-07-13
Role: Reviewer

## Finding

### B1R3: `reloadLatest()` can still write old-project completion state after a project switch

The project-scoped provenance reset is correct: it clears local provenance, pending
high-water/semantics, workspace, selection, local target, and stale target before the
new project is hydrated. The initial load, `reload()`, command runner, blank apply,
and stale reapply also check `activeProjectId` after awaited work.

`reloadLatest()` is the remaining exception. It awaits guarded `reload()`, then
unconditionally calls `setMessage("Latest contact measurement plan loaded.")` and
unconditionally clears `busy` in `finally`. If an operator begins Reload latest in
project A, changes route to project B while A's fetch is pending, and project B starts
an operation before A resolves, A's completion clears B's busy lock and displays an
incorrect success message. `reload()` correctly avoids restoring A's workspace, but
its wrapper still backfills state into B.

Required minimal Developer fix:

1. Apply the same active-project guard in `reloadLatest()` after its await, in catch,
   and in finally; do not set message/error/busy for an inactive project.
2. Add a deferred-promise hook regression: start A `reloadLatest`, rerender to B and
   complete B's load, then resolve A. Assert that A neither restores state nor writes
   the A success message/clears B's busy state.

## Verified B1R2 Resolution

- `projectId` transitions now clear origins, issued high-water, semantic bookkeeping,
  workspace/selection/local/stale state, and operator feedback before B hydrates.
  B's workspace is therefore merged into a clean provenance map as `persisted`.
- The project A starter -> project B persisted-empty same-id regression is present.
  It proves issued IDs reset, B receives `ff-llcr-2` rather than A's pending sequence,
  empty `record_label` remains empty, and validation prevents PATCH.
- The required persisted-empty prefix-renewal -> stale-reapply regression is present;
  it asserts the reapply payload retains the renewed id and an empty `record_label`.
  Same-project renewal and stale provenance paths remain covered.
- The B1R2 changes remain frontend model/selector/tests/evidence only; no backend,
  API payload/schema, consumer, Fee, TASK_360B/TASK_361D workbook, or locked-scope
  implementation change was found.

## Validation Performed

- Re-read AGENTS, board, TASK_361H task/plan/Developer/Reviewer evidence, actual
  candidate diff, model async paths, and focused regressions.
- `npm test -- ContactMeasurementPlanSummaryCard ContactMeasurementSetupWorkspace
  contactMeasurementPlanSelectors useContactMeasurementPlanModel
  DraftMeasurementPlanWorkbookPanel useDraftMeasurementPlanWorkbookModel
  matrixContactMeasurementPlanSelectors --run`: `7 files / 31 tests passed`.
- Candidate diff-check has only existing LF/CRLF warnings; trailing whitespace is
  clean. The latest model/selector/test line counts are `477/310/457`.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer fix pass limited to B1R3's inactive-project
`reloadLatest()` guard and its deferred project-switch regression. Do not route QA
re-smoke until it passes.

Blocking summary: B1R2 fixes provenance and main async paths, but an old Reload latest
completion can still alter busy/message state in a newly selected project.

---

# TASK_361H Reviewer Focused Implementation Re-Gate: B1R3

Status: reviewer_blocked
Task: `TASK_361H_CONTACT_MEASUREMENT_FREEFORM_CATEGORIES`
Lane: `contact-measurement-freeform-categories`
Date: 2026-07-13
Role: Reviewer

## Finding

### B1R4: A reload token is not invalidated by a project transition (A-B-A ABA race)

The new `reloadLatest()` operation token correctly protects the reviewed A -> B path
when B starts its own reload: the second reload increments the token, so A can no
longer write B's busy/message state. The success and rejection regressions prove that
specific sequence.

The token is not advanced when `projectId` changes. An outstanding A reload can
therefore survive A -> B -> A when B does not invoke Reload latest. On the return to
A, both `activeProjectId === callerProjectId` and `reloadOperation === operation`
become true again. The original A request can then hydrate its old workspace and emit
the old reload completion state over the newly loaded A workspace. This is an ABA
route-transition race, not merely a cosmetic message issue.

Required minimal Developer fix:

1. Invalidate outstanding reload operations whenever a `projectId` transition resets
   local workflow state (advance the operation generation or use a project-generation
   token in `ownsReload`).
2. Add a deferred A -> B -> A regression without a B reload: load return-A with a
   newer fingerprint, resolve/reject the original A reload, and assert it cannot
   replace return-A workspace or write message/error/busy.

## Verified B1R3 Resolution

- `reloadLatest()` now captures its caller project and operation token; success,
  failure, and busy cleanup require both to match. Its cleanup only clears its own
  `"reload"` busy state.
- Existing A -> B resolved/rejected regressions prove the old operation does not
  alter B while B owns a newer reload, and B's own reload still completes normally.
- The re-gate candidate remains frontend model/project-switch test/evidence only;
  no backend/API/schema/PATCH/consumer/workbook or other locked-scope change was
  found.

## Validation Performed

- Directly inspected the token lifecycle, project-reset effect, `reloadLatest()`
  success/catch/finally branches, and the new deferred tests.
- `npm test -- ContactMeasurementPlanSummaryCard ContactMeasurementSetupWorkspace
  contactMeasurementPlanSelectors useContactMeasurementPlanModel
  useContactMeasurementPlanModel.projectSwitch DraftMeasurementPlanWorkbookPanel
  useDraftMeasurementPlanWorkbookModel matrixContactMeasurementPlanSelectors --run`:
  `8 files / 33 tests passed`.
- Candidate diff-check remains limited to existing LF/CRLF warnings; no locked-path
  candidate hunk or real-artifact target was found.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer fix pass limited to B1R4 reload-generation
invalidation and the deferred A -> B -> A regression. Do not route QA re-smoke until
this re-gate passes.

Blocking summary: token matching handles an A -> B operation only after B starts a
new reload; the token must also become stale across a project transition to prevent
an A -> B -> A old-response backfill.

---

# TASK_361H Reviewer Focused Implementation Re-Gate: B1R4

Status: reviewer_pass
Task: `TASK_361H_CONTACT_MEASUREMENT_FREEFORM_CATEGORIES`
Lane: `contact-measurement-freeform-categories`
Date: 2026-07-13
Role: Reviewer

## B1R4 Resolution

- A project transition now advances a local project generation before resetting the
  contact-plan workflow. `reload()` captures that generation before its fetch and
  hydrates workspace only when project id and generation both still match.
- `reloadLatest()` now owns a triple `(caller project id, generation, operation
  token)`. Success, error, and finally paths all require ownership, and the finally
  cleanup clears only its own current `"reload"` busy state.
- The deferred A -> B -> A regressions cover both old-resolution and old-rejection
  paths without a B reload. They prove the return-A workspace/fingerprint, message,
  error, and busy state remain untouched until the new return-A reload completes.
- Existing A -> B isolation, same-project reload completion, project-scoped
  provenance/high-water reset, persisted empty-label prefix stale reapply, and
  starter/Add/template initialization behavior remain covered by the focused suite.

## Scope Review

The B1R4 delta is confined to the contact-measurement frontend model, a focused
project-switch test, a small local error helper, and lane evidence. It introduces no
backend/API/schema/PATCH contract, Fee, TASK_360B/TASK_361D workbook, generic Test
Record/Report, parser, LTR/public-drive, real-file, or other locked-scope change.
External TASK_361F operational QA and board residuals remain excluded.

## Validation Performed

- Directly reviewed project-generation lifecycle, reload generation capture, token
  ownership checks, success/catch/finally cleanup, and all four deferred switch tests.
- `npm test -- ContactMeasurementPlanSummaryCard ContactMeasurementSetupWorkspace
  contactMeasurementPlanSelectors useContactMeasurementPlanModel
  useContactMeasurementPlanModel.projectSwitch DraftMeasurementPlanWorkbookPanel
  useDraftMeasurementPlanWorkbookModel matrixContactMeasurementPlanSelectors --run`:
  `8 files / 35 tests passed`.
- `npm run build`: passed with the existing Vite chunk-size warning only.
- `git diff --check`: no errors, only existing LF/CRLF warnings; trailing whitespace
  is clean. The model, switch test, and extracted error helper are `485/177/12` lines.

## Decision

`reviewer_pass`

Recommended next role/action: QA re-smoke gate using controlled/disposable fixtures,
including the deferred project-switch path and the existing browser smoke. Do not
route Integrator directly from this Reviewer gate.

Blocking summary: none for Reviewer B1R4 re-gate.

---

# TASK_361H Reviewer Focused Implementation Re-Gate: QA B2

Status: reviewer_blocked
Task: `TASK_361H_CONTACT_MEASUREMENT_FREEFORM_CATEGORIES`
Lane: `contact-measurement-freeform-categories`
Date: 2026-07-13
Role: Reviewer

## Finding

### B2R: Target resolver retains an ineligible preferred target

`resolveWorkspaceSelectedTarget()` returns a matching preferred stable key without
checking `target.eligible`:

```ts
return workspace.targets.find((target) => target.stable_target_key === preferredStableTargetKey)
  ?? workspace.targets.find((target) => target.eligible)
  ?? null;
```

That contradicts the QA B2 contract that ineligible targets are skipped and that a
workspace with no eligible target has no selection or starter row. A reload where the
old selected key still exists but becomes ineligible selects it anyway; when every
target is ineligible and that old key remains, the editor still creates a starter.
The current tests cover only an earlier ineligible target or an absent old key, so
they do not exercise this retained-ineligible branch.

Required minimal Developer fix:

1. Retain the preferred key only when its target is eligible; otherwise select the
   deterministic first eligible target, or `null` when none exists.
2. Add focused reload regressions for (a) preferred target becomes ineligible while a
   later eligible target exists, and (b) preferred target remains but all targets are
   ineligible. Assert key, target identity, and starter rows all come from the
   resolved eligible target or are explicitly empty.

## Verified Non-Blocking Facts

- Initial load and guarded reload now both use the same resolver. Their hydration
  writes selected key, local editor, starter provenance, and stale-target retention
  from that one result.
- The old-key-absent fallback correctly skips an earlier ineligible target, selects
  the first eligible target, and creates the blank `ff-llcr-1` starter immediately.
  The old-key-absent/no-eligible path clears selection and editor.
- Project generation/ABA reload guards remain present. The candidate is confined to
  frontend model/selector/hydration tests/evidence; no backend/API/schema/PATCH,
  consumer, or workbook scope change was found.

## Validation Performed

- Re-read QA B2 evidence, Developer evidence, actual resolver/model/hydration tests,
  and prior B1R4 Reviewer decision.
- `npm test -- ContactMeasurementPlanSummaryCard ContactMeasurementSetupWorkspace
  contactMeasurementPlanSelectors useContactMeasurementPlanModel
  useContactMeasurementPlanModel.projectSwitch
  useContactMeasurementPlanModel.targetHydration DraftMeasurementPlanWorkbookPanel
  useDraftMeasurementPlanWorkbookModel matrixContactMeasurementPlanSelectors --run`:
  `9 files / 37 tests passed`.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer fix pass limited to B2R eligible preferred
target resolution and the two focused hydration regressions. Do not route QA re-smoke
until this re-gate passes.

Blocking summary: the fallback is correct only after the old key disappears; an old
key that persists but becomes ineligible still violates the selected-target and
no-eligible contracts.

---

# TASK_361H Reviewer Focused Implementation Re-Gate: B2R

Status: reviewer_pass
Task: `TASK_361H_CONTACT_MEASUREMENT_FREEFORM_CATEGORIES`
Lane: `contact-measurement-freeform-categories`
Date: 2026-07-13
Role: Reviewer

## B2R Resolution

- The shared resolver now retains a preferred stable key only when the matching
  target is eligible. An absent or ineligible preferred target falls through to the
  first eligible target; no eligible target returns `null`.
- Reload hydration derives selected key, target identity, local editor, starter row,
  and stale-target retention from that single resolved target. No prior target edits
  or label are copied to a fallback target.
- Focused regressions now cover a retained key becoming ineligible while a later
  eligible target exists, and the retained key remaining while every target is
  ineligible. They prove deterministic fallback or a null editor without a starter.
- Project generation/ABA guards and all earlier provenance, stale-reapply, and
  same-project reload cases remain intact.

## Scope Review

The B2R delta remains within the approved contact-measurement frontend
resolver/model/hydration-test/evidence surface. No backend/API/schema/PATCH contract,
Fee, TASK_360B/TASK_361D workbook, generic Test Record/Report, parser,
LTR/public-drive, real-file, or other locked-scope implementation change was found.
External board and TASK_361F operational-QA residuals remain excluded.

## Validation Performed

- Reviewed actual resolver eligibility condition and the two retained-ineligible
  reload regressions.
- `npm test -- ContactMeasurementPlanSummaryCard ContactMeasurementSetupWorkspace
  contactMeasurementPlanSelectors useContactMeasurementPlanModel
  useContactMeasurementPlanModel.projectSwitch
  useContactMeasurementPlanModel.targetHydration DraftMeasurementPlanWorkbookPanel
  useDraftMeasurementPlanWorkbookModel matrixContactMeasurementPlanSelectors --run`:
  `9 files / 37 tests passed`.
- `npm run build`: passed with only the existing Vite chunk-size warning.
- `git diff --check`: no errors, only existing LF/CRLF warnings; trailing whitespace
  is clean. Current model/selector/hydration-test line counts: `491/318/102`.

## Decision

`reviewer_pass`

Recommended next role/action: QA re-smoke gate with its controlled fixture/browser
workflow, including the starter-on-open and retained-ineligible cases. Do not route
Integrator directly from this Reviewer gate.

Blocking summary: none for Reviewer B2R re-gate.
