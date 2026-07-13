# TASK_361H Contact Measurement Freeform Categories Developer Evidence

Date: 2026-07-13

Role: Developer

Status: ready_for_review - Reviewer retained-ineligible resolver fix complete; Reviewer focused re-gate required before QA re-smoke.

## Current Phase / Why Allowed

Phase 11 controlled Matrix foundation. TASK_361H was implementation authorized after
the Reviewer implementation-readiness gate and user reconciliation. TASK_361E remains
accepted upstream; this lane neither revisits its confirmed consumer migration nor
changes Fee/workbook behavior.

## Repository Facts Used

- `contactMeasurementPlanSelectors.ts` currently allocates `custom-N` from the local
  target array and permits non-negative counts. `useContactMeasurementPlanModel.ts`
  owns the existing stale-safe single-target PATCH/reload workflow.
- `ContactMeasurementSetupWorkspace.tsx` currently treats `is_custom` rows as the
  only removable rows. Its selected target already exposes family label, record label,
  prefix, inclusion, count, and derived reading display.
- `ContactMeasurementPlanWorkspaceReadService` is the existing narrow workspace read
  boundary. The family snapshot table already stores vocabulary-neutral id, ordinal,
  label, count, record label, prefix, inclusion, and compatibility metadata.
- The existing lifecycle command replaces draft target families atomically while
  confirmed revisions remain historical. No new mutation route is required.

## Implementation-Readiness Strategy

- New ids are per-root/per-kind `ff-llcr-N` and `ff-cr-N`. Frontend allocation is
  `max(server historical high-water, reloaded rows, pending local ids) + 1`; deletion,
  reorder, reload, and stale re-apply cannot reuse an issued number.
- The only server addition is a typed workspace read field calculated from all
  persisted family history. Existing PATCH remains final collision rejection and
  fails closed with no family writes.
- New/explicitly edited prefixes normalize once through NFKC, trim, uppercase, ASCII
  `A-Z0-9`, 1..64. Blank input resolves from label or immutable `C{N}` and is
  persisted. Reorder/reload/rename do not recompute it. Legacy ids/prefixes round-trip
  unchanged until explicitly edited.
- UI begins with exactly one local freeform row when uniform data is absent. Built-in
  connector rows are optional templates only. Shared apply remains blank-only, and
  target overrides retain precedence.
- Included counts alone derive `readings_per_sample`; no duplicate generic quantity
  inputs are introduced. Fee stays a passive confirmed-total consumer, while TASK_360B
  and TASK_361D retain existing category/prefix consumers unchanged.

## Future May Touch And Locks

Exact future paths are recorded in the task and plan: contact-measurement workspace,
selectors/model/CSS/tests; an additive typed client workspace field; narrow read-only
repository/read-service/route projection; focused family validation/lifecycle
delegation; and only proven-dead Matrix fixed-profile cleanup. Schema, authority
lifecycle/commands, Fee rules/pricing/UI, TASK_360B/TASK_361D workbooks, generic Test
Record/Report, parser/import, LTR/public drive, frontend raw fetch, real databases or
files, `.agents/**`, `docs/project_management/**`, staging, commit, and push remain
locked.

## Validation Plan

Run focused selector/model/workspace/backend temporary-SQLite tests for issuance,
stale collision, resolved prefix stability, duplicate no-write, derived totals,
blank-only apply, and override preservation. Re-run accepted TASK_361B/C/E,
TASK_360B, and TASK_361D regressions; run build, compile, diff/trailing/line/scope
scans; then perform safe desktop and narrow browser smoke using only disposable data.

## Planning-First Validation

- Updated only this evidence and the TASK_361H plan.
- No backend/frontend product file, test implementation, dependency, schema,
  database, real workbook/folder, staging, commit, or push was performed.
- Required plan/evidence docs exist. Targeted `git diff --check` passed and the UTF-8
  trailing-whitespace scan is clean. Targeted status shows no backend, frontend, or
  test implementation change from this planning-first pass; existing board and
  TASK_361F operational evidence are external governance residuals.

## Next Role

Reviewer implementation-readiness gate.

## Blocking Summary

No implementation blocker. Controlled browser smoke remains a QA residual because this
Developer environment has no callable in-app browser control surface. The focused
component and model suites cover the operator flow without a live project or real DB.

## Developer Implementation

### Implemented Boundary

- Added the read-only `family_id_high_water_by_kind` workspace projection. The
  repository scans root-owned historical snapshots for parseable `ff-llcr-N` and
  `ff-cr-N` identifiers, while the route and typed client expose only the two numeric
  maxima. No schema, counter, allocation endpoint, or PATCH DTO changed.
- Replaced selector-local `custom-N` generation with per-kind freeform `ff-*` ids.
  Allocation uses server, reloaded, and pending maxima, so add A/add B/remove A/add C
  cannot reuse an issued number. An empty selected target receives one local blank row.
- Added editable category controls for include, label, count, optional prefix,
  remove, move up/down, and optional High Power, Low Power, and Signal templates.
  Templates are convenience values only; every persisted row remains a vocabulary-free
  category. `readings_per_sample` remains the included-count sum.
- Kept the existing single-target PATCH contract. The model applies a selected profile
  only to blank eligible, non-override targets through individual fingerprinted PATCH
  calls and skips populated or override targets.
- Added one-time prefix resolution for freeform rows: NFKC, uppercase ASCII
  alphanumeric, with `C{N}` fallback. Reorder and label edits retain the stored
  prefix. Client and backend reject normalized duplicate prefixes before replacement;
  the existing revision fingerprint remains the transactional stale-write rejection.
- Delegated server-side freeform validation to
  `contact_measurement_plan_family_validation.py`, preserving the lifecycle command
  and authority state-machine boundaries.

### Changed Files

- `backend/application/contact_measurement_plan_family_validation.py`
- `backend/application/contact_measurement_plan_lifecycle_service.py`
- `backend/application/contact_measurement_plan_workspace_read_service.py`
- `backend/infrastructure/storage/repositories/contact_measurement_plan_authority.py`
- `backend/api/routes_contact_measurement_plan.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/contact-measurement-plan/contactMeasurementPlanSelectors.ts`
- `frontend/src/features/contact-measurement-plan/useContactMeasurementPlanModel.ts`
- `frontend/src/features/contact-measurement-plan/ContactMeasurementSetupWorkspace.tsx`
- `frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.test.tsx`
- `frontend/src/features/contact-measurement-plan/ContactMeasurementSetupWorkspace.test.tsx`
- `frontend/src/features/contact-measurement-plan/contactMeasurementPlanSelectors.test.ts`
- `frontend/src/features/contact-measurement-plan/useContactMeasurementPlanModel.test.tsx`
- `tests/unit/test_contact_measurement_plan_family_validation.py`
- `tests/unit/test_contact_measurement_plan_workspace_read_service.py`
- `tests/integration/test_contact_measurement_plan_freeform_categories.py`
- `tests/integration/test_contact_measurement_plan_workspace_api.py`

### Validation

- Backend temporary SQLite and API/workbook regression suite: 38 passed.
- Frontend focused contact-measurement suite: 18 passed.
- `py -m py_compile` passed for all changed backend modules.
- `npm run build` passed. Existing Vite chunk-size warning remains.
- `git diff --check` passed. The existing LF/CRLF warnings are informational only;
  UTF-8 trailing-whitespace, line-count, locked-path, and no-real-DB/real-file scans
  are clean. Existing TASK_361F operational QA evidence and board changes remain
  external residuals and are not part of TASK_361H.

## Next Role

Reviewer implementation gate.

## Developer Fix Pass: Reviewer B1-B3

### B1: Transactional Freeform Authority Validation

- Moved family validation into the existing `set_target_inclusion` savepoint before
  target or family replacement. The command and PATCH DTO remain single-target.
- Added a repository sibling read scoped to the editable revision and contact kind.
  It rejects a reused `ff-*` id whose NFKC-normalized label or resolved prefix
  differs, and rejects normalized freeform-label collisions. Shared same-id,
  same-semantics rows remain valid.
- Rejection raises the existing lifecycle conflict path, returns typed HTTP 422, and
  leaves the selected target family rows unchanged.

### B2: Semantic Edit Identity Renewal

- The workspace model now records loaded and locally issued freeform semantics.
  A label blur or resolved-prefix blur renews only a changed freeform family with
  `max(server, reloaded, pending) + 1`; count, include, order, and removal do not
  renew identities.
- Reload and stale re-apply preserve the issued identity. The existing PATCH stays
  fail-closed for a server-side collision.

### B3: Record Label Compatibility

- The visible label editor patches only `label`. It no longer copies into
  `record_label`, so a distinct legacy or operator record label survives semantic
  label edits and remains available to TASK_360B/TASK_361D consumers.
- New freeform/template rows still initialize `record_label` from their initial
  label, preserving the approved new-row default without redefining existing rows.

### Fix-Pass Tests

- Temporary SQLite coverage verifies same-id/same-semantics cross-target acceptance,
  divergent same-id rejection, normalized duplicate-label rejection, and no-write
  behavior after rejection.
- API coverage verifies the existing typed 422 conflict envelope for an authority
  collision.
- Selector/model coverage verifies normalized label preflight, label and prefix ID
  renewal, monotonic stale re-apply, and preservation of a distinct legacy record
  label. Existing TASK_360B/TASK_361D projection/workbook regressions are included
  in the focused backend/frontend suite.

### Fix-Pass Validation

- Backend focused temporary SQLite/API/confirmed-consumer/workbook suite: `29 passed`.
- Frontend focused contact measurement and draft-workbook suite: `7 files / 24 tests passed`.
- `py -m py_compile` passed for touched backend modules.
- `npm run build` passed; only the existing Vite chunk-size warning remains.
- Browser smoke was not run: no callable in-app browser control surface is available
  in this Developer environment. No real database, workbook, or file was accessed.

### Fix-Pass Scope

- B1-B3 changes are limited to the existing contact-measurement validation,
  repository read, lifecycle transaction, workspace selector/model/presentation,
  focused tests, and this evidence.
- Fee, TASK_360B/TASK_361D workbook behavior, authority schema/lifecycle contracts,
  generic Test Record/Report, parser/import, LTR/public-drive, real databases/files,
  and external residuals remain unchanged and excluded.

## Developer Fix Pass: QA B1 Default Blank Record Label

### Root Cause And Fix

- The required local blank freeform row starts with an empty display label and an
  empty `record_label`. The UI exposes only Label, Count, and Prefix, while client
  validation correctly requires `record_label` before the existing PATCH command.
  A completed visible row therefore could not be saved or used as the blank-only
  shared profile.
- Added a narrow frontend normalization step immediately before Save target,
  blank-only apply, and stale re-apply. It initializes `record_label` from the
  trimmed visible label only when the row is an identifiable new local `ff-*`
  family whose ID is absent from the currently loaded target snapshot.
- Once initialized, `record_label` remains independent. Later label/prefix semantic
  edits continue to renew the `ff-*` identity but retain that record label. A loaded
  legacy/custom family with an empty record label is not guessed, repaired, or
  rewritten.
- Existing PATCH payload, backend validation, schema, lifecycle, Fee, and workbook
  consumer boundaries are unchanged.

### QA B1 Regression Coverage

- Default blank row with visible Label, positive Count, and Prefix saves through the
  existing single-target PATCH with an initialized `record_label`.
- The same initialized source applies to another blank eligible target through the
  existing per-target blank-only PATCH flow.
- The initialized record label survives later label and prefix identity renewals;
  an existing distinct legacy record label remains unchanged.
- Selector coverage proves only a locally new freeform row is initialized, while a
  persisted legacy freeform row with an empty record label remains untouched.

### QA B1 Validation

- Backend focused temporary SQLite/API/consumer/workbook suite: `26 passed`.
- Frontend focused suite: `7 files / 27 tests passed`.
- `py -m py_compile` passed for the touched contact-plan backend modules.
- `npm run build` passed; only the pre-existing Vite chunk-size warning remains.
- Browser smoke was not re-run in this Developer environment because no callable
  in-app browser control surface is available. No real database, workbook, or file
  was accessed.
- Pure target normalization and semantic snapshot helpers were moved into the
  existing selector boundary; `useContactMeasurementPlanModel.ts` is now 463 lines,
  below the 500-line hard limit with meaningful headroom.

### QA B1 Scope

- Product changes are limited to `contactMeasurementPlanSelectors.ts` and
  `useContactMeasurementPlanModel.ts`, plus their focused tests and this evidence.
- No backend command/API/schema/lifecycle, Fee, TASK_360B/TASK_361D workbook,
  generic Test Record/Report, parser/import, LTR/public-drive, or external residual
  was changed in this fix pass.

## Developer Fix Pass: Reviewer Provenance Blocker

### Root Cause And Fix

- QA B1 used an ID-difference heuristic to classify a freeform family as local-new.
  A persisted legacy/custom family with an empty `record_label` could renew its
  `ff-*` identity after a label or prefix semantic edit, then be incorrectly
  classified as local-new during Save or stale re-apply.
- The frontend model now keeps local-only freeform provenance: `starter`, `added`,
  `template`, or `persisted`. Workspace/reload families begin as `persisted`; the
  default blank row, explicit Add, and optional template rows retain their distinct
  local origins.
- Semantic ID renewal moves the same provenance to the renewed `ff-*` id. Stale
  re-apply consumes that retained provenance rather than reclassifying rows from
  current IDs. No provenance field enters the API payload or backend schema.
- Only `starter`, `added`, and `template` rows with an uninitialized record label
  may initialize it once from a valid display label. Persisted/reloaded rows keep an
  empty legacy/custom `record_label` unchanged and continue through the existing
  validation/no-write result. A distinct existing record label remains independent
  from later display-label and prefix edits.

### Provenance Regression Coverage

- Selector coverage verifies one-time initialization for starter/Add/template origins,
  and verifies a persisted family remains uninitialized after an ID renewal passed
  through stale re-apply normalization.
- Model coverage verifies a persisted empty-label family renews on both label and
  prefix edits, retains its empty record label, and sends no PATCH because the
  established validation remains fail-closed.
- Existing default blank Save and blank-only shared-apply tests continue to verify
  starter-origin initialization. Existing distinct legacy record-label regression
  remains green.

### Provenance Fix Validation

- Backend focused temporary SQLite/API/consumer/workbook suite: `26 passed`.
- Frontend focused suite: `7 files / 29 tests passed`.
- `py -m py_compile` passed for the existing contact-plan workspace/API modules.
- `npm run build` passed; only the pre-existing Vite chunk-size warning remains.
- `git diff --check` and UTF-8 trailing-whitespace scan are clean apart from the
  existing informational LF/CRLF warnings. `useContactMeasurementPlanModel.ts` is
  466 lines and `contactMeasurementPlanSelectors.ts` is 293 lines, both below the
  500-line hard limit.
- No real database, workbook, or operator file was accessed. Browser smoke remains
  unavailable in this Developer environment because no callable browser control
  surface is exposed.

### Provenance Fix Scope

- This pass changes only the existing contact-measurement selector/model and their
  focused tests, plus this TASK_361H evidence. It does not change backend commands,
  API payloads, schema/lifecycle, Fee, workbook consumers, generic Test Record/Report,
  Matrix parsing, LTR/public-drive, or external residuals.

## Developer Fix Pass: Reviewer B1R2 Project-Scoped Provenance

### Root Cause And Fix

- The provenance registry and the associated pending ID/high-water/semantic maps
  previously survived a `projectId` prop transition in the same hook instance. Because
  `ff-*` identities recur per project, a project A starter origin could incorrectly
  classify a project B persisted family with the same ID as local-new.
- The model now treats a project transition as an atomic local-workflow reset before
  fetching the new workspace: it clears provenance, pending issuance/semantic state,
  selected/local/stale targets, workspace, busy/error/message state, and selection.
  New workspace families are then hydrated only as `persisted` for that project.
- Active-project guards prevent an in-flight operation or old fetch from restoring
  project A state after a project B transition. Same-project reload and stale
  re-apply retain their current provenance and monotonic issued IDs.
- The existing ID renewal moves provenance only inside the active project. It never
  turns a persisted/reloaded row into starter/Add/template solely because its ID
  changes. API payloads, PATCH semantics, backend contracts, and consumer behavior
  remain unchanged.

### B1R2 Regression Coverage

- Hook rerender coverage starts with a project A blank starter and issued pending ID,
  switches to project B with a persisted empty-label `ff-llcr-1`, renews its display
  label, and proves project B receives `ff-llcr-2` rather than project A's pending
  sequence. Its empty `record_label` remains empty and local validation sends no
  PATCH.
- A focused prefix-renewal stale recovery regression exercises the actual stale and
  re-apply path. It proves the renewed persisted family keeps its empty record label
  in the re-apply PATCH payload rather than inferring a value from its display label.
  The test bypasses only local validation to reach the recovery branch; production
  validation remains unchanged and fail-closed.
- Existing starter blank Save/shared-apply, optional template/Add initialization,
  distinct legacy record-label, same-project reload, and monotonic renewal coverage
  remain green.

### B1R2 Validation

- Backend focused temporary SQLite/API/consumer/workbook suite: `26 passed`.
- Frontend focused suite: `7 files / 31 tests passed`.
- `py -m py_compile` passed for existing contact-plan workspace/API modules.
- `npm run build` passed; only the pre-existing Vite chunk-size warning remains.
- `git diff --check` and UTF-8 trailing-whitespace scan are clean apart from the
  existing informational LF/CRLF warnings. Line counts: model `477`, selector `310`,
  model test `457`, all below the 500-line hard limit.
- No real database, workbook, or operator file was accessed; no staging, commit, or
  push was performed. Browser smoke remains unavailable because this Developer
  environment exposes no callable browser control surface.

### B1R2 Scope

- The fix is frontend model/selector/test/evidence only. Existing backend, API client,
  schema/lifecycle, Fee, TASK_360B/TASK_361D workbooks, generic Test Record/Report,
  parser/import, LTR/public-drive, and external residuals are untouched and excluded.

## Developer Fix Pass: Reviewer reloadLatest Async Guard

### Root Cause And Fix

- `reload()` already guarded workspace hydration for an inactive project, but its
  `reloadLatest()` wrapper still unconditionally wrote a success message, error, and
  `busy` cleanup after awaiting it. A late project A reload could therefore alter
  project B feedback or clear project B's own busy lock.
- Each `reloadLatest()` invocation now captures its caller `projectId` and a monotonic
  reload operation token. Success, catch, and finally writes require both the active
  project and the same current token. Its busy cleanup additionally clears only a
  current `"reload"` state, preserving a newer operation's state.
- Same-project reload remains unchanged: it refreshes workspace, clears its own busy
  state, and displays the established success message. No backend/API/PATCH/consumer
  behavior changed.

### Reload Guard Regression Coverage

- Deferred hook regression starts a project A reload, transitions to project B, and
  starts B's own reload. Resolving A proves it cannot overwrite B workspace, set an
  A success message, write an error, or clear B's `"reload"` busy state.
- A companion deferred rejection regression proves the same isolation for A failure.
- The resolved project B operation then proves the normal same-project workspace,
  busy cleanup, and success-message behavior remains intact.

### Reload Guard Validation

- Backend focused temporary SQLite/API/consumer/workbook suite: `26 passed`.
- Frontend focused suite: `8 files / 33 tests passed`.
- `py -m py_compile` passed for existing contact-plan workspace/API modules.
- `npm run build` passed; only the pre-existing Vite chunk-size warning remains.
- `git diff --check` and UTF-8 trailing-whitespace scan are clean apart from the
  existing informational LF/CRLF warnings. Line counts: model `485`, main model test
  `457`, project-switch test `111`, all below the 500-line hard limit.
- No real database, workbook, or operator file was accessed; no staging, commit, or
  push was performed. Browser smoke remains unavailable because this Developer
  environment exposes no callable browser control surface.

### Reload Guard Scope

- This pass changes only the TASK_361H frontend model and focused project-switch test,
  plus Developer evidence. Backend/API/schema/PATCH, Fee, TASK_360B/TASK_361D
  workbooks, generic Test Record/Report, parser/import, LTR/public-drive, and external
  residuals remain untouched and excluded.

## Developer Fix Pass: Reviewer reloadLatest ABA Guard

### Root Cause And Fix

- The prior reload token compared only the active project ID and operation number.
  In an A to B to A transition where B did not start a reload, an old A operation
  could again match both values and let its guarded workspace hydration overwrite the
  return-A state.
- Project transitions now increment a local project generation. `reload()` captures
  that generation before its fetch, while `reloadLatest()` captures project ID,
  generation, and operation token. Both workspace hydration and all wrapper
  success/catch/finally writes require the captured generation to remain current.
- This invalidates every pending reload from before any project transition, including
  an ABA return to the same `projectId`. The reload finally still clears only its own
  current `"reload"` state. API/PATCH/schema/consumer behavior is unchanged.

### ABA Regression Coverage

- Deferred A to B to A regression starts an old A reload, returns to A without a B
  reload, starts a fresh return-A reload, then resolves the old request. The old
  request cannot replace the return-A workspace/fingerprint, message, error, or busy
  state; the fresh return-A reload completes normally.
- A matching rejected-old-reload regression proves the same isolation for the error
  path.
- Existing A to B resolve/reject guards, same-project reload behavior, and provenance
  / high-water contracts remain covered in the focused suite.

### ABA Guard Validation

- Backend focused temporary SQLite/API/consumer/workbook suite: `26 passed`.
- Frontend focused suite: `8 files / 35 tests passed`.
- `py -m py_compile` passed for existing contact-plan workspace/API modules.
- `npm run build` passed; only the pre-existing Vite chunk-size warning remains.
- `git diff --check` and UTF-8 trailing-whitespace scan are clean apart from the
  existing informational LF/CRLF warnings. Line counts: model `485`, error helper
  `12`, project-switch test `177`, all below the 500-line hard limit.
- No real database, workbook, or operator file was accessed; no staging, commit, or
  push was performed. Browser smoke remains unavailable because this Developer
  environment exposes no callable browser control surface.

### ABA Guard Scope

- This pass changes only TASK_361H frontend model/error-helper/project-switch tests
  and Developer evidence. Backend/API/schema/PATCH, Fee, TASK_360B/TASK_361D
  workbooks, generic Test Record/Report, parser/import, LTR/public-drive, and external
  residuals remain untouched and excluded.

## Developer Fix Pass: QA B2 Draft Target Hydration

### Root Cause And Fix

- `reload()` previously restored an editor only when the old local stable target key
  existed in the incoming workspace. Opening an editable draft can replace stable
  target keys, leaving the UI label selected while the local editor remained null
  until the operator clicked that same target again.
- Added one shared workspace target resolver. It retains a preferred stable key when
  present; otherwise it selects the deterministic first eligible target; with no
  eligible target it returns null. Initial workspace load and guarded reload now use
  this same resolver.
- Hydration commits selected key, selected target, local editor, and starter origin
  from that one resolved target. An empty fallback target immediately receives the
  existing default blank freeform row. When there is no eligible target, selection
  and editor are explicitly cleared; stale local edits are retained only when their
  target remains resolved.
- Project generation and reload operation guards remain in force around all fallback
  hydration, so a late request cannot select a target in the wrong project.

### QA B2 Regression Coverage

- Opening a draft where the old key is absent selects the first eligible new target,
  exposes its Group 1 identity, and immediately provides `ff-llcr-1` with Count `1`
  and Prefix `C1`, without a redundant selection click.
- The deterministic fallback skips an earlier ineligible target. A reload with no
  eligible targets leaves `selectedTarget` null and creates no starter row.
- Existing project-switch generation/ABA and same-project reload regressions remain
  green.

### QA B2 Validation

- Backend focused temporary SQLite/API/consumer/workbook suite: `26 passed`.
- Frontend focused suite: `9 files / 37 tests passed`.
- `py -m py_compile` passed for existing contact-plan workspace/API modules.
- `npm run build` passed; only the pre-existing Vite chunk-size warning remains.
- `git diff --check` and UTF-8 trailing-whitespace scan are clean apart from the
  existing informational LF/CRLF warnings. Line counts: model `491`, selector `318`,
  hydration test `102`, all below the 500-line hard limit.
- No real database, workbook, or operator file was accessed; no staging, commit, or
  push was performed. Browser smoke remains unavailable because this Developer
  environment exposes no callable browser control surface.

### QA B2 Scope

- This pass changes only TASK_361H frontend selector/model/hydration tests and
  Developer evidence. Backend/API/schema/PATCH, Fee, TASK_360B/TASK_361D workbooks,
  generic Test Record/Report, parser/import, LTR/public-drive, and external residuals
  remain untouched and excluded.

## Developer Fix Pass: Reviewer Retained-Ineligible Resolver Branch

### Root Cause And Fix

- The new shared resolver initially retained a matching preferred stable key without
  checking eligibility. A target that remained in the workspace but changed to
  ineligible could still be selected and receive a starter row; all-ineligible input
  could therefore retain the old editor.
- Preferred-key retention now requires both key equality and `eligible === true`.
  A missing or ineligible preferred target falls through to the deterministic first
  eligible target, and no eligible target yields null. The existing atomic hydration
  then clears selected key/editor/starter rather than displaying stale target identity.

### Retained-Ineligible Regression Coverage

- A preferred key that remains present but becomes ineligible selects the later
  eligible Group 1 fallback. Its starter identity, key, and rows belong only to that
  fallback target.
- A preferred key that remains present while every target is ineligible clears
  selection and creates no starter/editor row.
- Existing key-absent fallback, project-generation/ABA, and same-project reload
  coverage remain green.

### Retained-Ineligible Validation

- Backend focused temporary SQLite/API/consumer/workbook suite: `26 passed`.
- Frontend focused suite: `9 files / 37 tests passed`.
- `py -m py_compile` passed for existing contact-plan workspace/API modules.
- `npm run build` passed; only the pre-existing Vite chunk-size warning remains.
- `git diff --check` and UTF-8 trailing-whitespace scan are clean apart from the
  existing informational LF/CRLF warnings. Line counts: model `491`, selector `318`,
  hydration test `102`, all below the 500-line hard limit.
- No real database, workbook, or operator file was accessed; no staging, commit, or
  push was performed. Browser smoke remains unavailable because this Developer
  environment exposes no callable browser control surface.

### Retained-Ineligible Scope

- This pass changes only TASK_361H frontend resolver/model/hydration tests and
  Developer evidence. Backend/API/schema/PATCH, Fee, TASK_360B/TASK_361D workbooks,
  generic Test Record/Report, parser/import, LTR/public-drive, and external residuals
  remain untouched and excluded.
