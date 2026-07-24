# Fee Default-Fill Dependent Field Corrections - Reviewer Evidence

Date: 2026-07-23
Role: Reviewer
Status: `reviewer_plan_dependency_release_blocked / pending Planner docs-only fix`

Task: `FEE_DEFAULT_FILL_DEPENDENT_FIELD_CORRECTIONS`
Lane: `fee-default-fill-dependent-field-corrections`
Parent: `FEE_DEFAULT_FILL_RESIDUAL_PACKAGE_RECONCILIATION`

## Gate Context

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task: none. Child 2 is planned-only and this is a plan/dependency-release gate only.
- Child 1 accepted commit `c5d91c36c5e1d54885fc0a3b406c92ff9aa0cb6b` is the checked-out `HEAD` and was independently verified as a `HEAD` ancestor. It is read-only baseline, not Child 2 implementation scope.

## Dependency Confirmation

- Accepted Child 1 owns final Base Fee precedence and metadata: proven manual, then explicit structured rule Base Fee, then automatic `0`; it does not use `matrix_group_count` as a trigger.
- The Child 2 task correctly retains the 2B/3B exclusions: only the approved normalized high-temperature label may reach High temperature Life; the two rejected labels remain no-rule/manual-review; plain Contact Resistance does not fall back to LLCR.
- TASK_361L/TASK_363D provenance, attestation, reviewed rebase, currentness, CAS, and no-write ownership remain correctly locked for this child.

## Blocking Findings

### B1 - Planned missing-duration Base Fee behavior overlaps accepted Child 1 ownership

The Child 2 task still names "Temperature-duration rows with missing duration and potential Base Fee `0`" as its purpose. The current unaccepted default-fill residual likewise computes a generic temperature `base_fee=0` and changes the Base Fee manual-field state before the accepted Child 1 final policy runs. That is a Base Fee default/metadata decision, not a dependent-field correction.

The plan must state that Child 2 does not write or classify Base Fee or Base Fee metadata for a missing duration. It may only decide whether explicit Units exist and whether Testing Fee remains unset/review-required. The accepted Child 1 final policy remains the sole owner of the automatic Base Fee baseline and metadata. This correction must cover all duration-rule paths, not only a text regex for generic "temperature" rows.

### B2 - Explicit-hour validation and test package are not frozen enough to implement safely

"Explicit valid hours" is not defined for the proposed Salt Spray and approved temperature-duration changes. The plan must freeze the authority sources read by Child 2, numeric validity (including zero, negative, malformed, and non-finite values), and the resulting Units/manual-review/no-write state. It must also name exact bounded test modules and line budgets rather than "such as" a test module.

Required coverage must distinguish:

- `fee_rule_salt_spray_nss` with explicit valid hours versus missing/invalid hours;
- the single approved High temperature Life alias with explicit valid hours versus missing/invalid hours;
- rejected aliases and plain CR with no new automatic rule/LLCR path;
- Temperature Rise with missing current but valid versus invalid sample quantity, preserving automatic Units only when valid;
- final Child 1 Base Fee metadata/fingerprint and V2 manual-field preservation as read-only regressions.

## Verification Performed

- Read `AGENTS.md`, board, Child 2 task/plan/Planner/dependency-release evidence, accepted Child 1 Reviewer evidence, and current default-fill/common residual code.
- Verified the Child 1 commit ancestor relation and the current `fee_default_fill.py` / `fee_default_fill_common.py` candidate boundaries. No product code or test was modified and no real DB/file/generated artifact was accessed.
- Current candidate facts: `fee_default_fill.py` is `470` UTF-8 physical lines and `fee_default_fill_common.py` is `98`; the existing legacy default-fill test remains oversized and must stay read-only.

## Next Legal Role

Planner docs-only fix. Do not route Developer planning-first or product implementation until B1/B2 are closed. Child 3 and the umbrella remain blocked.

## Plan/Dependency-Release Re-Gate

Date: 2026-07-23

### Result

Blocked. Planner closed the prior Base Fee overlap and test-package gaps, but the stricter explicit-hour contract cannot be implemented within the current Child 2 May Touch boundary.

### Confirmed Closure

- Child 2 no longer claims a missing-duration Base Fee value or metadata write. Child 1 is now explicitly the exclusive final Base Fee/metadata owner.
- The hour contract now defines positive finite owning-row authority, invalid/fallback exclusions, typed no-write behavior, and four exact bounded test modules.
- The 2B/3B alias and CR boundaries, V2/manual protections, Child 3 block, and twelve-path isolation remain intact.

### B3 - No structured duration authority exists in the permitted implementation boundary

The revised contract forbids arbitrary text and requires a typed, lineage-bound duration fact for the owning Fee row. Actual code does not expose such a fact to Child 2:

- `FeeDefaultFillContext` contains only `test_item`, `method`, `condition`, `requirement`, sample quantity, step tokens/quantities, and CR authority; it has no structured duration value, unit, row identity, or duration lineage/fingerprint.
- `confirmed_matrix_fee_draft_service.py` builds that context from the Matrix row's text fields and is locked for Child 2.
- The two authorized product modules currently derive hours only by scanning `_combined_text(context)`, exactly the fallback source the revised plan forbids.

Therefore, implementing the stated authority rule would require an unplanned context/authority transport change outside the current May Touch list. Treating current free text as typed authority would silently weaken the newly frozen contract.

### Required Planner Follow-Up

Perform a new docs-only discovery/re-scope. It must either:

1. identify an existing typed owning-row duration authority and its actual transport path, then narrow the plan to consume it; or
2. propose a separately approved authority-transport lane with its exact model/service/source/lineage changes and no cross-lane implementation.

Do not relax the contract to arbitrary text parsing without an explicit new User decision. Developer planning-first and product implementation remain unauthorized.

## Next Legal Role

Planner docs-only discovery/re-scope. Child 3 and the umbrella remain blocked.

## Option A Plan/Dependency-Release Re-Gate

Date: 2026-07-23

### Result

Blocked. The new helper/DTO/transport scope closes the prior May Touch omission, but it does not identify a lawful duration authority from which that helper can create a fact.

### Confirmed Boundaries

- Child 1 remains the accepted, read-only owner of Base Fee value and metadata. The revised Child 2 documents no longer assign Base Fee writes to missing or invalid duration handling.
- The proposed `FeeDurationAuthority` DTO, one-build transport, lineage/fingerprint binding, fail-closed diagnostics, five bounded test modules, and the 2B/3B/V2 locks are directionally correct scope controls.
- The authority build reads one `ConfirmedMatrixSnapshot` and constructs each default-fill context from `ConfirmedMatrixRow.test_item`, `method`, `condition`, `requirement`, and `day_expression`, plus group quantity and existing step/CR facts. `ConfirmedMatrixRow` itself has no typed duration value, unit, duration-source identity, or duration lineage/fingerprint field.

### B4 - Option A still has no exact non-text duration source

The plan says that a new helper will create a typed duration fact inside the single build, but it does not freeze the authoritative source field, source representation, or bounded parsing/normalization grammar. In the actual accepted authority model, the only plausible row-local inputs are the textual `condition`, `requirement`, and `day_expression` fields. Re-parsing any of those fields and then labelling the result `FeeDurationAuthority` is still the arbitrary free-text authority path the Child 2 contract expressly forbids.

The repository does have structured duration compatibility data on project-plan step payloads, but that is not represented in the active `ConfirmedMatrixSnapshot` and the current plan continues to forbid legacy Step fallback. It cannot silently serve as this helper's source.

Planner must choose one explicit, reviewable contract before implementation:

1. identify an already persisted, typed, owning confirmed-row duration field with its identity and fingerprint transport; or
2. obtain a new User decision that permits a narrowly specified parser over one named confirmed-row source field, including its exact accepted grammar, cardinality/conflict rule, unit aliases, source-field fingerprint, and the reason it is not treated as a fallback; or
3. defer the automatic 15/hour duration behavior until a separate confirmed-authority persistence lane makes such a fact available.

Until then, every candidate duration must remain review-required/no-write. A generic helper test cannot prove authority that the underlying confirmed model does not carry.

### B5 - Hard service-size mitigation is not executable yet

`backend/application/confirmed_matrix_fee_draft_service.py` is already 479 UTF-8 physical lines. The planned import, single-build projection, and context transport cannot safely fit in its remaining 21 lines. The plan permits a "mechanical split if needed" but does not identify the exact existing symbols to move, their destination module, the final line budgets, or regression nodes that prove the move behavior-preserving. That is insufficient to authorize a hard-limit exception or an opportunistic refactor.

The Planner follow-up must freeze the split as an exact hunk-level May Touch change (or prove the final measured service stays below 500 without it), with all moved behavior and bounded regressions named. It must not use the new duration helper as a catch-all for unrelated service extraction.

### Verification Performed

- Read the current task, plan, Planner and dependency-release evidence, prior Reviewer findings, board status, `FeeDefaultFillContext`, `ConfirmedMatrixFeeDraftService`, and `ConfirmedMatrixRow` authority model.
- Confirmed the service is 479 UTF-8 physical lines; `fee_default_fill_models.py`, `fee_default_fill.py`, and `fee_default_fill_common.py` are 118, 470, and 98 lines respectively.
- No product code or test was modified. No real DB, public-drive file, attachment, or generated artifact was accessed; staging remains untouched.

## Next Legal Role

Planner docs-only discovery/re-scope. Do not route Developer planning-first or implementation. Child 3 and the umbrella remain blocked.

## Option 1 Plan/Dependency-Release Re-Gate

Date: 2026-07-23

### Result

Blocked. User Option 1 correctly authorizes an additive confirmed-duration authority path and the proposed line-builder split names the relevant service symbols. The plan still leaves the producer, existing-database migration, and hard file-size execution contracts under-specified.

### Confirmed Closure

- The earlier B4 source gap is substantively addressed in direction: Fee no longer needs to manufacture authority from `condition`, `requirement`, or `day_expression`; only a published confirmed-row duration fact may reach default-fill.
- The proposed source/draft/confirmed domain and repository chain, legacy-null manual-review behavior, same-build consumer boundary, Child 1 Base Fee lock, 2B/3B exclusions, and five bounded new regression modules are appropriate boundaries.
- The B5 service split is now concrete: move the listed row-to-line symbols to `confirmed_matrix_fee_draft_line_builder.py`, leave orchestration in the service, and preserve the listed read-only authority dependencies before any duration behavior is added.

### B6 - Explicit producer and migration contract is still incomplete

The current source import, editable draft, and confirmed-row models only carry text row fields. Option 1 authorizes adding duration fields, but the plan does not yet state which *explicit structured input* may populate them. It must explicitly say whether a Source Matrix import may pass only named raw payload fields, whether an editable Matrix request may set them, and how omission, `null`, replacement, and conflicting `duration_value` / `normalized_hours` are handled. It must also state that `condition`, `requirement`, `day_expression`, and compatibility prose cannot be parsed to populate the new fields at either producer boundary.

The storage contract likewise cannot stop at "additive nullable shape". It must freeze the exact nullable columns (including their SQLite affinities), the table that owns each source/row/revision/fingerprint value, required foreign-key or identity consistency checks, existing-DB recognition, partial-schema fail-close behavior, migration transaction/read-verify/rollback, and the precise legacy-null result. `init_db()` currently creates metadata before applying several bespoke migrations; a vague bootstrap rule is not enough to prove that a partially upgraded local database cannot publish corrupt duration authority.

### B7 - Remaining oversized May-Touch files have no executable line-budget plan

The only named split addresses `confirmed_matrix_fee_draft_service.py`. The Option 1 May Touch list also includes existing oversized production modules: `backend/infrastructure/storage/database.py` (990 UTF-8 physical lines), `backend/application/project_matrix_draft_persistence_service.py` (507), and `backend/api/routes_project_matrix_drafts.py` (600). They cannot receive new behavior under the project hard limit without an exact mechanical split or an explicitly approved narrow exception. No such split/exception, destination module, final budget, or behavior-preserving regression is frozen for them.

There is also a count-method discrepancy: the documents call `(Get-Content ... | Measure-Object -Line)` a UTF-8 physical-line count and report the Fee draft service as 451, while direct UTF-8 physical-line reading reports 479. The source of truth must use one method that includes blank lines and correct the effective budgets before implementation.

### Required Planner Follow-Up

Perform one docs-only refinement that:

1. freezes allowed structured producer inputs, field-presence/update semantics, conflict rules, and the exact non-text source identity;
2. specifies the additive SQLite/domain/repository migration and fail-closed/idempotent bootstrap contract; and
3. supplies an executable hunk-level line strategy and corrected physical counts for every oversized May-Touch production file, or removes those files from the lane.

Developer planning-first and product implementation remain unauthorized until these items pass a further readiness re-gate. Child 3 and the umbrella remain blocked.

### Verification Performed

- Read the revised Child 2 and umbrella task/plan/evidence, current source/draft/confirmed domain and storage models, import/draft services, API surfaces, `init_db()` migration order, and Fee draft authority build.
- Confirmed that the existing producer models carry only text row fields; the current Matrix edit compatibility duration fields do not flow into Source Matrix or Confirmed Matrix authority.
- Measured UTF-8 physical lines including blanks: Fee draft service 479, draft persistence service 507, Matrix draft route 600, and database bootstrap module 990. No product code or test was changed and no real data or external artifact was accessed.

## Next Legal Role

Planner docs-only refinement. Do not route Developer planning-first or implementation.

## Option 1 Plan/Dependency-Release Re-Gate 2

Date: 2026-07-23

### Result

Blocked. The B6/B7 migration, producer, API/CAS, and split plans materially close the prior governance gaps. Three exact SQLite/data-model details still make the proposed authority contract unsafe to implement as written.

### Confirmed Closure

- The plan now freezes a field-presence-aware, non-text `duration_authority` producer object; omission, explicit `null`, full replacement, typed `400/409`, Confirm Matrix publication, legacy-null review behavior, and same-build Fee consumption are correctly separated.
- The new dedicated source/draft/confirmed authority tables, marker, zero-shape upgrade, partial-shape fail-close, transaction/read-verify/rollback/idempotency, and disposable migration suite are the right persistence boundary.
- The database, route, Fee draft service, and conditional draft-persistence splits are now named with destinations, target budgets, and behavior-preserving regression expectations.

### B9 - Nullable suffix breaks the stated SQLite unique authority identity

The contract specifies `step_suffix_note TEXT NULL`, normalizes empty suffixes to `NULL`, and then relies on a composite `UNIQUE` containing that nullable column. SQLite permits multiple rows where a unique-key component is `NULL`, so it would allow duplicate duration authorities for the same parent/group/row/sequence with a missing suffix. That defeats the plan's own "one owning-row authority" and conflict/no-write guarantee.

Freeze one exact representation before implementation: either store suffix as `TEXT NOT NULL DEFAULT ''` and include it in the unique key, or create a canonical expression/index using `COALESCE(step_suffix_note, '')`. The same canonical value must be used in domain DTOs, repositories, API normalization, migration read-verify, and the duplicate/conflict regressions.

### B10 - The producer object has unresolved per-group cardinality

`duration_authority` is described as one object on a source-import or Matrix-edit *row*, while every persisted authority identity includes an owning group and Fee consumes a group/row line. A Matrix row can appear in multiple groups. The plan does not say whether one object applies identically to every selected group, whether the input is a keyed collection of per-group objects, or how a group-key mismatch and two different group-specific durations are represented.

The Planner must freeze one model and its payload shape. If group-specific values are allowed, use a bounded collection keyed by the current group identity and validate every element. If a single row-level value is intentionally copied to selected groups, state that deterministic fan-out, its source identity/fingerprint, selection-change behavior, and conflict rule. The current singular object cannot be both a row field and a complete group/row authority without that decision.

### B11 - The stated line-count command is not a physical-line count

`(Get-Content <path> -Encoding UTF8 | Measure-Object -Line).Lines` counts nonblank line records, not UTF-8 physical lines including blanks. Direct UTF-8 physical reading reports 479 lines for the Fee draft service, 507 for draft persistence, 600 for the Matrix draft route, and 990 for `database.py`; the documents label the lower `451/448/525/939` values as physical and supersede the actual counts. This would let the conditional persistence split avoid the hard 500-line limit despite touching a 507-line Python module.

Use one blank-inclusive command (for example `(Get-Content <path> -Encoding UTF8).Count`) across the task, plan, evidence, board, and gates. Recalculate the split thresholds and final budgets from that metric; the draft-persistence split must be mandatory before adding behavior, not conditional on the nonblank count.

### Required Planner Follow-Up

Perform a docs-only correction for B9-B11. Preserve all closed Option 1 boundaries; do not start Developer planning-first or product implementation. Child 3 and the umbrella remain blocked.

### Verification Performed

- Read the revised task, plan, Planner and dependency-release evidence, board entry, current source/draft/confirmed models, storage migration order, and relevant producer/route surfaces.
- Verified SQLite's nullable unique-key semantics against the proposed `step_suffix_note TEXT NULL` contract and confirmed the source/draft row model is row-scoped while the proposed authority identity is group/row-scoped.
- Compared the declared count command with direct UTF-8 physical-line reads. No product code, test, database, real file, or generated artifact was touched; staging remains unchanged.

## Next Legal Role

Planner docs-only correction. Do not route Developer planning-first or implementation.

## Option 1 Plan/Dependency-Release Re-Gate 3

Date: 2026-07-23

### Result

Passed. The B9-B11 corrections make the Option 1 duration-authority lane implementable without reopening Child 1 or weakening the confirmed-authority boundary.

### Accepted Contract

- `duration_authorities` is now an explicit per-group collection. Each entry binds one current group/row/sequence/canonical-suffix identity; no implicit cross-group fan-out is permitted. The narrowly defined singleton convenience path must otherwise reject with typed `409` and no write.
- `step_suffix_note` is normalized to `''` and persisted as `TEXT NOT NULL DEFAULT ''`. The composite unique identity therefore cannot be bypassed by SQLite nullable-key semantics. The round-trip/migration test package explicitly covers this uniqueness and per-group cardinality.
- Only structured import/edit objects can create the authority. Text fields, legacy quantities, readings, Point Profile, contact authorities, and saved drafts remain prohibited inputs; Confirm Matrix remains the only publication step and legacy absent authority remains review-required/no-write.
- The three dedicated tables, marker, zero-shape upgrade, partial-shape fail-close, transaction/read-verify/rollback/idempotency, field-presence API behavior, source signature/CAS/currentness, and same-build Fee consumption remain frozen.
- Blank-inclusive line measurement is now consistently `(Get-Content <path> -Encoding UTF8).Count`, matching the checked-out facts: database 990, draft persistence 507, Matrix draft route 600, and Fee draft service 479. Required mechanical splits now cover every touched oversized path before duration behavior.
- Child 1 Base Fee ownership, 2B's only approved high-temperature alias, 3B plain-CR no-LLCR behavior, TASK_361L/TASK_363D protections, and Child 3/umbrella isolation remain intact.

### Verification Performed

- Read the corrected task, plan, Planner and dependency-release evidence, board entry, and previous Reviewer findings.
- Independently confirmed the four blank-inclusive UTF-8 counts and reviewed the per-group collection, canonical suffix, migration, and split contracts.
- No product code, test, real database/file, or generated artifact was modified or accessed; staging remains unchanged.

## Next Legal Role

User approval for Developer planning-first. Product implementation remains unauthorized; do not route Developer implementation.

## Scope And Implementation-Readiness Re-Gate

Date: 2026-07-23

### Result

Passed. The publication/carry-forward/signature reconciliation closes the remaining transport gap between structured source/edit authority and the confirmed-only Fee consumer.

### Confirmed Readiness

- The exact transport ownership now covers selected source-to-draft remapping (`matrix_import_draft_builder.py`), first Confirm Matrix publication (`confirmed_matrix_authority_service.py`), revision draft carry-forward and revision confirmation (`matrix_revision_flow_service.py` plus its bounded snapshot builder), and Matrix Editor source replacement, saved-draft persistence, and canonical signatures.
- Every path preserves per-group authority identity, canonical non-null suffix, source lineage, currentness/CAS, and sorted signature inputs. Missing, unselected, mismatched, or stale identity fails closed before persistence; Confirm Matrix remains the only Fee publication boundary.
- The required mechanical splits are concrete and sequenced before duration behavior: database, draft persistence, Matrix-draft route, Fee line builder, revision flow, Matrix Editor session, and Matrix Editor route. The stated targets keep every candidate Python module below 500 physical lines while retaining orchestration at the public service boundaries.
- Bounded projection, signature, publication/API, Fee/default-fill, V2 rebase/CAS, and non-visual Matrix Editor preservation tests cover the added paths. Existing oversized authority/session/default-fill tests remain read-only regressions and external dirty hunks remain excluded.
- `frontend/src/api/client.ts` remains typed-contract-only. The narrowly admitted `MatrixEditorWorkspace.tsx` hunk is limited to lossless seed/save/confirm payload preservation; the plan records that `$impeccable` and frontend architecture rules were reviewed and forbids UI controls, copy, layout, or inference changes.
- Child 1 Base Fee ownership, approved 2B alias, 3B no-LLCR rule, TASK_361L/TASK_363D safeguards, Child 3, the umbrella, Fee frontend hydration, seeds, real data, and all external residuals remain locked.

### Verification Performed

- Read the corrected task, implementation plan, Planner/reconciliation/Developer evidence, board, current publication call sites, and the public/helper boundaries of the revision and Matrix Editor services.
- Independently confirmed blank-inclusive counts for the newly admitted paths: import draft builder 152, first-confirm service 310, revision flow 491, Matrix Editor session service 1901, and Matrix Editor route 556. The planned splits cover the latter three before duration behavior.
- No product code, test, real database/file, generated artifact, staging, commit, or push was touched.

## Next Legal Role

User product implementation approval plus Planner final source-of-truth reconciliation. Do not route Developer implementation until that approval and reconciliation are recorded.

## Implementation Gate

Date: 2026-07-24

### Result

Blocked.

### B1 - The shared per-hour branch expands the approved authority migration

`backend/modules/fee_evaluation/fee_default_fill.py` replaces the former
condition-text hour extraction for the shared `_duration_hour_result()` path.
That path is used not only by the approved `fee_rule_high_temperature_life`
and the explicitly planned Salt Spray rule, but also by
`fee_rule_pre_high_temperature_life`, `fee_rule_thermal_shock`,
`fee_rule_temperature_humidity`, and `fee_rule_vibration`.  The Child 2
contract approves only `Long-term high temperature zone load` as the new
15/per-hour authority rule, plus the expressly listed Salt Spray structured
authority case.  It does not authorize changing the remaining legacy
per-hour families or their existing duration behavior.

This is an observable regression, not merely a stale assertion.  The
focused reproduction below now changes `Temperature & Humidity` to
`"Missing confirmed duration authority"` and removes its prior
condition-based calculation path.  Narrow the new confirmed-duration branch
to the approved High-temperature and Salt Spray rules, retain the accepted
legacy handling for every other per-hour rule, and add a bounded regression
that proves those families remain unchanged.  Do not broaden Child 2's
business contract to absorb them.

### B2 - Matrix Editor's production composition is currently unusable

`backend/api/dependencies.py` constructs `MatrixImportCommitService` inside
`get_matrix_editor_session_service()` without the mandatory
`method_authority` dependency.  The constructor requires that keyword-only
argument.  This makes the production Matrix Editor session endpoint fail
before it can exercise Child 2's source-replacement, signature, or
publication preservation paths.

The isolated reproduction `py -m pytest
tests/integration/test_matrix_editor_session_api.py -q` produced `8 failed,
3 passed`; all eight failures stop at
`backend/api/dependencies.py:720` with:

`TypeError: MatrixImportCommitService.__init__() missing 1 required keyword-only argument: 'method_authority'`.

This is identified as the external TASK_366C composition residual.  It must
be corrected in its owning bounded package and its Matrix Editor API
regression must pass before this Child 2 candidate can enter QA.  Do not
silently fold that dependency-composition change into the Child 2 package.

### Locked Regression Follow-Up

The legacy condition-text/old-diagnostic assertions are genuinely stale for
the approved High-temperature and Salt Spray contract.  The focused command
below reproduced seven failures: the High-temperature condition fallback,
the old `Confirm duration` diagnostic, and Salt Spray condition-text
fallback.  Those assertions need an explicitly authorized tests-only
migration after B1 narrows the production behavior; the currently failing
Temperature & Humidity assertion must instead remain as a regression guard
for B1's bounded fix.

### Verified Candidate Behavior

- The bounded Child 2 unit/API/V2/publication package passed: `34 passed`.
- `npm test -- --run
  src/features/matrix-editor/MatrixEditorWorkspace.durationAuthority.test.tsx
  src/features/matrix-editor/MatrixEditorWorkspace.test.tsx` passed:
  `46 passed`.  The non-visual seed/save/confirm preservation hunk is sound
  in isolation.
- The confirmed Fee resolver performs an exact confirmed-matrix/group/row/
  step/suffix lookup and returns a typed review-required diagnostic when
  absent, conflicting, stale, malformed, or mismatched.  The line builder
  uses the loaded confirmed snapshot's authority collection, rather than a
  second provider read.
- Mechanical splits put the inspected Child 2 Python modules below 500
  blank-inclusive lines; e.g. Fee default-fill 482, line builder 390,
  Matrix Editor signature 451, and duration schema 218.  Existing oversized
  legacy tests remain outside the authorized new-test package.
- Child 1 Base Fee ownership remains read-only in the inspected Child 2
  paths, and the bounded package preserves the confirmed-only, V2/CAS, and
  no-LLCR boundaries.

### Verification Performed

- Read the task, plan, Planner/final reconciliation, Developer evidence,
  board, `AGENTS.md`, and the task review checklist; inspected the actual
  domain/storage/publication/session/Fee and frontend diffs.
- Ran the nine bounded Child 2 test modules: `34 passed`.
- Ran the Matrix Editor duration-preservation and existing workspace tests:
  `46 passed`.
- Ran the focused legacy duration nodes: `7 failed, 2 passed`, with the
  expected condition-text/diagnostic conflicts described above.
- Ran the Matrix Editor session API module: `8 failed, 3 passed`, all due to
  the missing external `method_authority` composition dependency.
- `git diff --check` reported only existing LF/CRLF notices; staged index was
  empty.  No product code or test was modified, and no real database,
  public-drive file, attachment, or generated business artifact was used.

## Next Legal Role

Developer bounded fix for B1 only, in the existing Child 2 authorized Fee
default-fill surface.  In parallel governance, the TASK_366C owner must
restore the missing Matrix Editor `method_authority` composition in its own
bounded package; do not route Child 2 to QA until that external API module is
green.  After B1, route a narrowly authorized tests-only migration for only
the stale High-temperature/Salt Spray legacy assertions.  Child 3 and the
twelve-path umbrella remain blocked.

## B1 Implementation Re-Gate

Date: 2026-07-24

### Result

Blocked pending tests-only scope reconciliation.  The B1 product fix passes;
this is not a request to change further production behavior.

### B1 Closure

`fee_default_fill.py` now sends only `fee_rule_high_temperature_life` and
`fee_rule_salt_spray_nss` through the typed confirmed-duration path.
`fee_rule_pre_high_temperature_life`, `fee_rule_thermal_shock`,
`fee_rule_temperature_humidity`, and `fee_rule_vibration` route through the
restored legacy text-hour builder.  The shared helper preserves their accepted
prices (`15`, `30`, `25`, and `300`), automatic Base Fee `0`, and `Confirm
duration` pending behavior.  The new bounded test explicitly covers all four
legacy rules, and the Temperature & Humidity old guard passes.

This closes B1 without reopening Child 1 Base Fee ownership, Child 3, the
umbrella, or the TASK_366C dependency-composition residual.

### Required Tests-Only Reconciliation

The full locked legacy check is now `107 passed, 6 failed`.  Each failure
expects condition prose to be authority for one of the two Child 2 approved
typed-duration rules, or expects the old generic diagnostic.  The exact
tests-only migration must be restricted to these existing assertion nodes:

1. `tests/unit/test_fee_default_fill.py::test_temperature_named_duration_rules_default_base_fee_to_zero_without_duration[fee_rule_high_temperature_life-Temperature life-unit_price0]`:
   expect missing confirmed duration authority instead of `Confirm duration`.
2. `tests/unit/test_fee_default_fill.py::test_salt_spray_uses_hour_duration_from_matrix_condition`:
   replace condition-text calculation expectations with typed-authority/no-
   authority coverage; do not change the Temperature & Humidity parameter.
3. `tests/unit/test_confirmed_matrix_fee_draft_service.py::test_fee_draft_defaults_non_rise_temperature_items_to_per_hour[Long-term high temperature zone load]`:
   remove the condition-text fallback expectation and assert the confirmed-
   authority requirement.
4. `tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py::test_approved_temperature_alias_uses_hours_and_common_base_fee[1]` and `[2]`:
   supply confirmed per-group duration authority or move the scenario to the
   bounded authority fixture; never infer the same value from condition text.
5. `tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py::test_approved_temperature_alias_without_hours_keeps_dependencies_pending`:
   assert the typed missing-authority diagnostic.

No fixture or assertion outside these nodes is authorized.  In particular,
the Temperature & Humidity case is the B1 regression guard and must remain
unchanged.

### External B2 Status

The missing `method_authority` constructor injection in
`get_matrix_editor_session_service()` remains a TASK_366C-owned composition
defect.  It was not touched in this re-gate.  Child 2 must continue to exclude
it, but QA remains unavailable until its owner restores the API composition
and reruns the Matrix Editor session module.

### Verification Performed

- Inspected the B1 diff: the routing split is exact and the restored helper
  has no new seed, API, V2, or Matrix authority behavior.
- Ran the new authority-routing test plus the old Temperature & Humidity guard
  and fee-draft parameter test: `11 passed, 2 failed`; the two failures are
  the listed High-temperature stale assertions.
- Ran all three locked legacy modules: `107 passed, 6 failed`; every failure
  is one of the five exact assertion locations above (with the two
  parameterized Group cases counted separately).
- No product code or test was changed; no real data was accessed; staged
  index remains empty.

## Next Legal Role

Planner tests-only/scope reconciliation to formally authorize only the five
listed legacy assertion migrations.  The TASK_366C owner must separately
repair its production composition residual.  Do not route Child 2 to QA or
Integrator; Child 3 and the umbrella remain blocked.

## Tests-Only Implementation Re-Gate

Date: 2026-07-24

### Result

Child 2 passes its implementation gate.  QA remains blocked by the separate
TASK_366C production-composition dependency described below.

### Tests-Only Scope Verification

The reviewed migration now makes only the previously authorized High-
temperature/Salt Spray expectation changes:

- High-temperature missing authority expects `review_required`, unset Units
  and Testing Fee, and `Missing confirmed duration authority`.
- Salt Spray condition prose no longer supplies duration authority.
- The High-temperature Fee-draft and one-/two-Group rule-resolution scenarios
  no longer calculate from condition prose; their missing-authority states
  are asserted instead.

The Temperature & Humidity parameter remains the regression guard for legacy
text-hour behavior, and the other legacy rules were not altered.  The current
product hashes match the Developer's pre/post tests-only record:

- `fee_default_fill.py`:
  `5B997F5F397EA85E18BE2631410E89CB27467A796B09D59E0F7EB6E6335B12A5`.
- `fee_default_fill_common.py`:
  `A7B747C9C016D9D98EF49F6178BC62F389D7AD76EE5ACF71CCDAB63492D8A8E9`.

The three affected legacy modules retain their declared blank-inclusive line
counts of `912`, `683`, and `301`.  Existing unrelated hunks in those dirty
files predate this tests-only handoff and are not attributed to the migration.

### Independent Verification

- Re-ran all three legacy modules: `113 passed`.
- Re-ran the bounded Child 2 unit/API/V2/publication package: `38 passed`.
- Verified B1's routing: only High-temperature Life and Salt Spray use typed
  duration authority; the four other per-hour families use the restored
  legacy builder.
- Verified no staged files and no data/generated-output changes.  No product
  code, test, real database, or external business file was modified or
  accessed by Reviewer.

### QA Dependency

The external TASK_366C defect remains: the production Matrix Editor service
composition constructs `MatrixImportCommitService` without its required
`method_authority`.  The earlier isolated API run remains `8 failed, 3
passed`, all at that construction boundary.  Since the Matrix Editor session
is one of Child 2's required source-replacement/signature transport paths,
QA cannot validate the full workflow until the TASK_366C owner fixes and
re-verifies that dependency.  Child 2 must not absorb the change.

## Next Legal Role

TASK_366C owner: Developer bounded fix for the missing production
`method_authority` composition, followed by its own Reviewer re-gate.  Only
after that external dependency is green may this accepted Child 2 candidate
route to QA.  Do not route Integrator; Child 3 and the umbrella remain
blocked.

## Matrix Editor DTO Implementation Re-Gate

Date: 2026-07-24

### Result

Child 2 passes this bounded implementation re-gate. QA remains held on one
pre-existing external Fee-rebase fixture failure; it is not a Child 2,
TASK_366C, or DTO ownership defect.

### DTO Contract Verification

`matrix_editor_session_dtos.py` now imports
`ConfirmedMatrixSnapshotResponse` from `project_matrix_draft_dtos.py`, the
module that defines the Pydantic contract. That module does not import Matrix
Editor DTOs, response mappers, or routes, so the import is DTO-to-DTO and
does not create a route cycle. The response contract is neither duplicated
nor weakened.

The bounded publication regression validates real first-confirm and
revision-confirm payloads with `MatrixEditorSessionConfirmResponse`, then
asserts that `ConfirmedMatrixSnapshotResponse` is present in the generated
JSON schema. This closes the five former Pydantic forward-reference errors.

### Independent Verification

- Re-ran `tests/integration/test_matrix_duration_authority_publication_api.py`
  together with `tests/integration/test_matrix_editor_session_api.py`:
  `11 passed, 1 failed`.
- The publication/schema regression passed. The session module now has `10
  passed, 1 failed`; there are no remaining forward-reference failures.
- The sole failure is
  `test_matrix_editor_session_autosave_restore_confirm_and_discard`, where
  the pre-existing Fee-rebase fixture expects
  `fee_rebase_summary.preserved_count >= 1` but receives `0` after a normal
  session draft save.

This exact residual was already documented before Child 2 in the accepted
TASK_366B review evidence as an excluded Fee pricing/default-fill rebase
failure. The present DTO-only pass leaves Base Fee, default-fill, pricing
draft rebase, fixture setup, and TASK_366C composition untouched. It cannot
be assigned to Child 2 without expanding its approved scope.

### Next Legal Role

Planner external-residual ownership/scope reconciliation under
`FEE_DEFAULT_FILL_RESIDUAL_PACKAGE_RECONCILIATION` must identify and authorize
the correct Fee-rebase owner for the `preserved_count` fixture regression.
After that owner fixes and re-gates it, rerun the full Matrix Editor session
module before Child 2 QA. Do not route QA or Integrator now; Child 3 and the
umbrella remain blocked.

## External Fee-Rebase Fixture Tests-Only Scope Confirmation

Date: 2026-07-24

### Result

`reviewer_pass_tests_only_scope`.

### Verified Root Cause And Boundary

The active seed manifest resolves to `fee_rules_v2026_07_17_r6`. The named
Matrix Editor session node contains exactly two obsolete
`fee_rules_v2026_06_03` literals: one in `_seed_previous_pricing_draft()` and
one in that node's promoted-draft repository lookup. The repository's current
lookup is exact on project, confirmed Matrix identity, revision, and Fee-rule
version. Consequently the r3-seeded source cannot match the runtime r6
pending-rebase context, and `preserved_count=0` is the correct result for the
stale fixture.

The pure rebase service counts source rows whose stable rebase identity matches
the target under that exact context; it does not count manual fields. No
cross-version fallback is permitted. This preserves TASK_361L/TASK_363D
currentness, provenance, fingerprint, CAS, reviewed-rebase, derived Testing
Fee, and zero-write rules.

### Authorized Tests-Only Hunk

Developer may modify only
`tests/integration/test_matrix_editor_session_api.py`:

1. replace the helper seed's `fee_rules_v2026_06_03` literal with
   `fee_rules_v2026_07_17_r6`;
2. replace the same obsolete literal in
   `test_matrix_editor_session_autosave_restore_confirm_and_discard`'s
   promoted-draft lookup.

The change must be line-neutral and retain the file's `1107` blank-inclusive
physical lines. Assertions, fixture pricing values, manual note, summaries,
production rebase code, persistence keys, API/CAS/provenance behavior, and
fallback policy are locked. No other test node is authorized.

### Required Re-Gate Evidence

Run the exact node, the complete Matrix Editor session API module, focused
Matrix Fee draft/pending/promotion rebase modules, and focused TASK_361L/
TASK_363D V2 contract/attestation/safe-rebase modules. Report line count,
diff/trailing, no-product-hunk, no-real-data, and staging checks. Child 2
product code and TASK_366C remain read-only; Child 3 and the umbrella remain
blocked.

## Next Legal Role

Developer tests-only fixture-context fix, followed by Reviewer implementation
re-gate. Do not route QA or Integrator from this scope confirmation.

## Soft-Removed Fee-Rebase Fixture Scope Confirmation

Date: 2026-07-24

### Result

The Matrix Editor fixture correction is accepted: its diff is exactly the two
authorized r3-to-r6 replacements, `2 additions / 2 deletions`, with the file
still at `1107` blank-inclusive lines. The repaired exact session node passes.

The remaining focused Fee-rebase failure is also a stale exact-context fixture,
not a product defect. Its exact node is
`tests/unit/test_matrix_fee_rebase_promotion_service.py::test_soft_removed_hidden_rows_survive_autosave_and_restore_when_reselected`.

### Verified Cause

That node's source pricing snapshot at line 324 and its
`RebaseAfterMatrixAutosaveCommand` at line 366 both use
`fee_rules_v2026_06_03`. The real persistence and pending-rebase services look
up an existing pricing draft by exact project, confirmed Matrix, revision, and
rule version. The current basic-fill/default context is r6, so the r3 fixture
cannot load its source inactive row; `inactive_rows == ()` is correct under
the mismatched context. Cross-version fallback would violate the accepted
currentness/provenance contract.

### Authorized Tests-Only Hunk

Developer may modify only
`tests/unit/test_matrix_fee_rebase_promotion_service.py`, and only in the
named soft-removed node:

1. replace the source `FeeEvaluationPricingDraftSnapshot` rule-version literal
   at line 324 with `fee_rules_v2026_07_17_r6`;
2. replace the matching `RebaseAfterMatrixAutosaveCommand` rule-version
   literal at line 366 with `fee_rules_v2026_07_17_r6`.

The file must remain `871` blank-inclusive physical lines. Assertions, all
fixture values and inactive-row semantics, production services, rebase keys,
cross-version behavior, provenance, CAS, API behavior, and every other test
node are locked.

### Required Re-Gate Evidence

Run the exact soft-removed node, all three focused Matrix Fee
draft/pending/promotion rebase modules, the full Matrix Editor session API
module, focused TASK_361L/TASK_363D V2 contract/attestation/safe-rebase
modules, and line/diff/trailing/scope/no-real-data/staging checks. Child 2
product code and TASK_366C remain read-only; Child 3 and the umbrella remain
blocked.

## Next Legal Role

Developer tests-only soft-removed fixture-context fix, followed by Reviewer
implementation re-gate. Do not route QA or Integrator yet.

## Final Child 2 Implementation Re-Gate

Date: 2026-07-24

### Result

`reviewer_pass`. Child 2 is ready for its QA gate.

### Tests-Only Package Verification

Both reconciled stale-fixture corrections exactly match their Reviewer scopes:

- `test_matrix_editor_session_api.py` changes only its two r3 rule-version
  literals to r6, is `2 additions / 2 deletions`, and remains `1107`
  blank-inclusive lines.
- `test_matrix_fee_rebase_promotion_service.py` changes only the two r3
  literals in
  `test_soft_removed_hidden_rows_survive_autosave_and_restore_when_reselected`,
  is `2 additions / 2 deletions`, and remains `871` blank-inclusive lines.

No assertion, pricing/manual fixture value, seed/manifest, production
default-fill/rebase/persistence code, rebase identity, provenance, CAS, API,
or cross-version fallback changed. Exact rule-version matching remains intact:
the fixtures now supply the same accepted r6 context as the active runtime,
while mismatched contexts remain non-preserving/no-fallback.

### Independent Verification

- Re-ran the three Matrix Fee draft/pending/promotion rebase modules plus the
  full Matrix Editor session API module: `53 passed`.
- `py_compile` passed for both changed test modules.
- Developer's unchanged focused TASK_361L/TASK_363D V2 contract,
  attestation, safe-rebase, currentness, and CAS package remains `47 passed`.
- Diff inspection, line counts, and staged-index checks confirm no scope
  expansion. No real database, public-drive file, attachment, or generated
  business artifact was accessed.

The prior TASK_366C composition and Matrix Editor DTO dependencies are now
closed. There is no remaining Child 2 implementation blocker. Child 1 remains
read-only; Child 3 and the parent umbrella remain blocked.

## Next Legal Role

QA gate for `FEE_DEFAULT_FILL_DEPENDENT_FIELD_CORRECTIONS`. Do not route
Integrator directly.
