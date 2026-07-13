# TASK_361H Contact Measurement Freeform Categories Planner Evidence

Date: 2026-07-13

Role: Planner

Status: Developer implementation and B1-B3 fix pass complete; Reviewer implementation
re-gate passed; pending QA re-run. Not Integrator accepted.

## Current Phase / Why Allowed

Phase 11 controlled Matrix foundation. TASK_361A-E are complete/accepted, with
TASK_361E accepted at `7e2409b4`. The user requested a post-acceptance correction to
the Contact measurement setup category model and authorized planning documents only.
TASK_361H is the next unused TASK_361 sub-number.

## User Goal

Replace the implied fixed High Power/Low Power/Signal vocabulary with user-defined
category rows. Start with one editable row, allow arbitrary add/remove/reorder, derive
readings from included counts, preserve category detail for workbooks, and keep
shared-profile/target-override/confirmed-authority semantics intact.

## Repository Evidence

- The setup workspace renders arbitrary family DTO rows but only allows removal when
  `is_custom=true`.
- The current frontend custom-row helper uses sequence ids and non-negative validation.
- Legacy Matrix selectors still declare three built-in defaults, though TASK_361C
  moved the visible editor to the independent workspace.
- Authority storage is already vocabulary-neutral and versioned per target snapshot;
  no schema migration is required.
- Existing target patch/repository replacement preserves confirmed history and
  derives readings from included family counts.
- TASK_361A defines common profile as a UI projection, not a second authority.
- Accepted TASK_361E keeps Fee and formal workbook consumption confirmed-only.

## Planner Decision

Create planned lane `contact-measurement-freeform-categories`. Use a derived transient
shared profile with one blank starter, stable opaque category ids, visible stable
prefix fallback, strict included-row validation, blank-only apply, and explicit
target overrides. Existing built-in rows become ordinary compatible rows. No schema,
consumer, workbook, Fee, parser, or real-file change is planned.

## Reviewer B1 Fix

- New ids are `ff-llcr-N` / `ff-cr-N`, scoped to Measurement Plan root and contact
  kind. Same-kind shared categories retain the same id across targets.
- A schema-free backend high-water scans all historical snapshots; frontend allocates
  above server, reloaded, and pending maxima. Delete cannot reuse a sequence.
- Save/apply/stale re-apply reload and fail closed on logical identity collisions;
  backend validation is final and transactional.
- Blank prefixes resolve once from NFKC/uppercase ASCII-alphanumeric label content or
  `C{N}`, persist as the sole prefix, and never change on reorder/reload/label rename.
- New/edited prefixes are 1..64 ASCII alphanumeric after normalization. Uniqueness is
  per included Group-Step/contact kind; separate sections may reuse values.
- Legacy ids/prefixes remain unchanged. TASK_360B/361D behavior and schema/Fee/
  consumer boundaries remain locked.
- Acceptance covers add A/B, remove A/add C, historical reload high-water, stale
  collision, prefix stability, explicit rename behavior, duplicate no-write, and
  legacy/workbook regressions.

## Risks Controlled

- No silent rewrite of existing ids or confirmed snapshots.
- No automatic fixed-category insertion.
- No silent overwrite of divergent/nonblank targets.
- No rounding or silent duplicate-label/prefix repair.
- No hidden workbook behavior change; resolved nonblank prefixes preserve existing
  expansion contracts.
- No native confirm or modal-first row editing; local removal remains reversible
  until Save.

## Definition Of Ready

Satisfied. Reviewer plan re-gate and implementation-readiness passed. Scope,
authority, identity issuance, persisted prefix resolution, compatibility, edge cases,
May Touch, locks, validation, browser smoke, and merge isolation are concrete.
Blocking questions: none.

## Implementation Authorization Reconciliation

- Reviewer plan re-gate passed after the B1 fix.
- The user approved Developer planning-first.
- Developer planning-first completed as a docs-only pass.
- Reviewer implementation-readiness passed with `reviewer_pass` and no technical
  blocker.
- On 2026-07-13, the user explicitly approved source-of-truth reconciliation and
  product implementation.
- TASK_361H is therefore `implementation_authorized` and pending Developer
  implementation; it is not complete.

Authorization is strictly limited to the freeform category UX, optional connector
template, included-count sum, blank-only shared apply, target overrides, monotonic
per-root/per-kind `ff-*` issuance, stale/collision fail-closed behavior, persisted
prefix normalization/fallback, additive read-only workspace high-water projection,
existing single-target PATCH semantics, and focused tests/browser smoke. Fee
rules/pricing/UI, TASK_360B/TASK_361D workbook behavior, authority schema/lifecycle,
generic Test Record/Report, Matrix parser/import, LTR/public drive, real databases or
files, and external residuals remain locked.

## Post-Implementation Gate Reconciliation

- Developer completed the authorized implementation and set evidence to
  `ready_for_review`.
- The initial Reviewer implementation gate blocked B1-B3: transactional sibling
  category identity/normalized-label enforcement, identity renewal for label or
  resolved-prefix edits, and preservation of distinct legacy `record_label` values.
- Developer completed the bounded B1-B3 fix pass.
- Reviewer implementation re-gate passed and directed the lane to QA.
- QA did not execute tests or browser smoke because board/task still declared pending
  Developer implementation. The QA checkpoint is governance-only, not a failed
  product validation.
- The reconciled lane state is pending QA re-run. Integrator has not accepted the
  lane, so TASK_361H remains incomplete.

## Evidence Paths

- `tasks/TASK_361H_CONTACT_MEASUREMENT_FREEFORM_CATEGORIES.md`
- `docs/task_361h_contact_measurement_freeform_categories_plan.md`
- `docs/lane_evidence/TASK_361H_contact-measurement-freeform-categories_planner.md`
- `docs/task_board.md`

## Next Legal Role

QA re-run gate.
