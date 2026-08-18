# TASK_361H Contact Measurement Freeform Categories

## Status

Developer implementation and B1-B3 fix pass complete; Reviewer implementation
re-gate, QA re-smoke, and Integrator packaging/readiness passed. The lane is
complete and accepted for local integration; remote push is intentionally outside
this lane.

## Gate History

- Reviewer plan re-gate passed after the B1 identity/prefix contract fix.
- The user approved Developer planning-first.
- Developer planning-first completed as docs-only evidence.
- Reviewer implementation-readiness passed with no technical blocker.
- The user explicitly approved source-of-truth reconciliation and product
  implementation. This authorization does not mark implementation complete.
- Developer completed the authorized implementation and reported `ready_for_review`.
- The initial Reviewer implementation gate blocked B1-B3: transactional sibling
  identity/label collision enforcement, semantic-edit identity renewal, and legacy
  `record_label` preservation.
- Developer completed the scoped B1-B3 fix pass. Reviewer implementation re-gate
  passed and recommended QA.
- QA completed the final disposable-data, focused regression, build, static, and
  browser re-smoke gate with `QA gate: pass`.
- Integrator isolated the approved TASK_361H package and accepted it after rerunning
  the focused backend/frontend suites, py_compile, and frontend build.

## Lane

`contact-measurement-freeform-categories`

## Current Phase / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Role: Integrator closeout. Reviewer and QA gates have passed, so controlled local
  packaging is allowed; no subsequent lane is started by this task.
- TASK_361A-E are complete/accepted. TASK_361E is accepted in local commit
  `7e2409b4`; remote push is outside this lane.
- The user corrected the category-entry model after acceptance: connector-specific
  High Power/Low Power/Signal examples must not be required product categories.

## Goal

Make Contact measurement setup category-first and user-defined. A new or empty
shared profile starts with one editable category row. Operators may add, remove,
include, reorder, label, count, and assign an optional record series/prefix to any
number of categories. High Power Pin, Low Power Pin, and Signal Pin may be offered
only as an optional template, never as required persisted categories.

## Authority And Compatibility Contract

- Confirmed Measurement Plan target snapshots remain authority. No second profile
  table or parallel category authority is introduced.
- A shared profile is a UI projection over canonically equal non-override targets.
  Applying it remains explicit and blank-target-only. Existing target overrides and
  confirmed revisions are never silently overwritten.
- Existing built-in family rows remain readable and editable as ordinary categories.
  `is_custom=false` is compatibility metadata only and cannot make a row mandatory or
  non-removable.
- Existing `family_id` values are preserved. New rows receive a stable opaque client
  id once and retain it through reorder, save, draft copy, and confirmation.
- Existing confirmed revisions and prior family snapshots are never deleted. Removing
  a category edits only the current draft target/profile application.
- `readings_per_sample` is derived as the sum of included category counts. Fee reads
  only that total through the accepted TASK_361E adapter. TASK_360B and TASK_361D
  continue consuming category detail and resolved prefixes without behavior changes.

## Stable Family Identity Contract

- New ids use `ff-llcr-N` or `ff-cr-N`, where `N` is an unpadded positive decimal.
  The namespace is one Measurement Plan root plus contact kind; LLCR and CR allocate
  independently.
- One id denotes one logical category across the shared profile and targets of that
  kind. Count, inclusion, and order overrides retain the id. Explicit label or
  resolved-prefix changes create a new id rather than redefining the old identity.
- The workspace read model exposes the maximum parseable sequence per kind across all
  persisted family snapshots for the root, including active, editable, superseded,
  and bootstrap revisions. Legacy ids remain unchanged outside the `ff-*` namespace.
- Allocation uses `max(server historical high-water, reloaded workspace ids, pending
  local ids) + 1`. Deletion never lowers the high-water or permits reuse.
- Before Save, apply, or stale re-apply, the client reloads latest state and validates
  pending ids. A collision with a different logical category fails closed without
  PATCH or automatic renaming.
- Backend validation is final: duplicate ids within a target, or divergent normalized
  label/prefix use of one `ff-*` id in the same revision/kind, raises
  `family_identity_collision` and writes no family rows.

## Resolved Prefix Contract

- Persisted `record_prefix` is the sole workbook prefix and is never recomputed at
  render time after persistence.
- New or explicitly edited input is Unicode NFKC-normalized, trimmed, uppercased,
  stripped to ASCII `A-Z0-9`, and limited to `1..64` characters, matching the
  accepted DTO limit and TASK_360B/TASK_361D normalized collision key.
- Blank input resolves once before first apply/save from the current label using the
  same rule. If the label yields no ASCII alphanumeric content, use `C{N}` from the
  immutable family sequence. Persist and display the resolved value.
- Reorder/reload never recalculates a persisted prefix. Label rename also preserves
  it. An explicit prefix edit/clear requests new resolution and a new family id.
- Normalized prefixes must be unique among included families within one confirmed
  Group-Step/contact-kind section. A duplicate blocks apply/save with no write.
  Separate sections may reuse a prefix, preserving accepted workbook behavior.
- Existing legacy ids/prefixes round-trip unchanged unless explicitly edited.

## UX Contract

- The independent setup workspace presents a compact `Default categories` editor
  before target detail. Empty state contains one local starter row, not three fixed
  fields and not a modal.
- Row controls: included checkbox, editable label, positive whole-number count,
  optional series/prefix, remove, and accessible move up/down controls.
- `Add category` appends one blank row. An optional `Use connector pin example`
  command may add High Power/Low Power/Signal as editable rows only after explicit
  operator action.
- A blank prefix uses the row's stable generated fallback such as `C1`; the resolved
  prefix is shown before apply/save and persisted nonblank so workbook behavior does
  not change.
- Applying shared categories previews the number of blank eligible targets and
  changes only those targets. Divergent/nonblank targets remain untouched and are
  edited individually as explicit overrides.
- Removing a row is a reversible local edit until Save. No native confirm dialog is
  used. Removing a row from the shared profile does not remove it from existing
  overrides.
- Desktop uses dense aligned rows. Narrow viewports stack each row's fields without
  horizontal overflow; remove/reorder actions remain keyboard reachable and have
  accessible names.

## Validation Rules

- Included categories require a nonblank trimmed label and a positive integer count.
- Excluded categories contribute zero and may preserve their prior count.
- A saved included target requires at least one included valid category.
- Normalized labels and resolved prefixes must be unique within one shared profile or
  target. Duplicate values block apply/save with row-level guidance; values may recur
  in separate Group-Step targets.
- Zero, negative, decimal, NaN, and overflow values block apply/save. No rounding.
- Order is explicit through `family_ordinal`; reordering never changes stable ids or
  generated fallback prefixes.

## Authorized May Touch

- `frontend/src/features/contact-measurement-plan/ContactMeasurementSetupWorkspace.tsx`
- `frontend/src/features/contact-measurement-plan/contactMeasurementPlanSelectors.ts`
- `frontend/src/features/contact-measurement-plan/useContactMeasurementPlanModel.ts`
- focused tests beside those files
- `frontend/src/contact-measurement-plan.css`
- `frontend/src/api/client.ts` only for one additive workspace high-water field
- `frontend/src/features/matrix-editor/matrixContactMeasurementPlanSelectors.ts`
  and `MatrixEditorWorkspace.tsx` only to remove proven-dead fixed-family profile
  state/handlers left after TASK_361C; Matrix editing behavior otherwise stays locked
- focused Matrix Editor compatibility tests if that dead-code removal is required
- `backend/application/contact_measurement_plan_family_validation.py` (new focused
  validation helper)
- `backend/application/contact_measurement_plan_lifecycle_service.py` only to delegate
  family validation without growing the existing 450-line service
- `backend/application/contact_measurement_plan_workspace_read_service.py` only to
  project per-kind persisted family-id high-water
- `backend/infrastructure/storage/repositories/contact_measurement_plan_authority.py`
  only for a read-only max historical `ff-*` sequence query scoped to one root/kind
- `backend/api/routes_contact_measurement_plan.py` only for the additive typed
  workspace high-water response field; mutation requests remain unchanged
- focused backend lifecycle/API tests using temporary SQLite only
- TASK_361H task/plan/evidence and `docs/task_board.md`

## Must Not Touch / Locked Paths

- No authority schema/model/migration/bootstrap/classifier/root/revision state change;
  repository scope is the single read-only high-water query only; no real database
  access or data rewrite.
- No TASK_360B/TASK_361D workbook projection, generation, layout, artifact, route, or
  download behavior change beyond regression verification.
- No TASK_361E adapter, Fee pricing/rules/default-fill/manual/export/UI, generic Test
  Record, Report, StepInstance, Matrix parser/import, Basic Information, LTR/public
  drive, real workbook/folder, release/settings, or unrelated cleanup.
- Frontend API client and backend route scope is limited to the additive read-only
  high-water field. No new endpoint, mutation command, or unrelated DTO change.
- `.agents/**`, `docs/project_management/**`, destructive git operations, commit,
  remote push, and external residuals remain locked.

## Acceptance Criteria

1. A plan with no uniform categories opens with one editable starter row and no
   automatic High/Low/Signal rows.
2. Operators can create a simple `Pin`, count `4`, prefix `P` profile and derive
   `readings_per_sample = 4`.
3. Operators can add arbitrary rows and optionally apply the connector pin example;
   the example rows are editable and removable like every other row.
4. Existing built-in rows load unchanged but are no longer protected or required.
5. Shared apply changes only blank eligible targets and preserves every nonblank,
   confirmed, divergent, or manual override target.
6. Target override editing preserves stable ids, order, draft/needs-review/confirmed
   lifecycle, stale fingerprint recovery, and no-silent-overwrite behavior.
7. Invalid counts, empty included labels, duplicate normalized labels/prefixes, and
   an empty included target block apply/save with row-level guidance.
8. Fee totals continue to consume only confirmed derived readings. TASK_360B and
   TASK_361D category expansion/prefix behavior remain unchanged.
9. Keyboard and narrow-width tests prove focusable add/remove/reorder controls and no
   horizontal page overflow.
10. Add A, add B, remove A, then add C issues increasing ids and never reuses A;
    save/reload and superseded history preserve the high-water.
11. A stale re-apply collision fails before PATCH; backend collision validation also
    rolls back with no family writes.
12. Blank-prefix save persists one normalized value; reorder/reload keep it stable;
    label rename does not change it unless prefix is explicitly edited.
13. Duplicate normalized prefixes block with no write, while distinct prefixes still
    expand unchanged through TASK_360B/TASK_361D regressions.
14. Legacy built-in ids/prefixes round-trip unchanged until explicitly edited.

## Validation Gate

- Focused selector/model/component tests for blank starter, arbitrary categories,
  template opt-in, stable ids, ordering, removal, derived totals, duplicate/number
  validation, blank-only apply, override preservation, stale reload, and accessibility.
- Focused backend validation tests for included positive integers, normalized
  duplicate labels/prefixes, historical high-water, identity collision no-write,
  excluded rows, and unchanged snapshot replacement.
- Existing TASK_361B/C lifecycle/workspace API regressions.
- TASK_361E Fee adapter regressions and TASK_360B/TASK_361D workbook regressions,
  without changing those implementations.
- `npm test -- ContactMeasurementSetupWorkspace contactMeasurementPlanSelectors useContactMeasurementPlanModel --run`
- focused `py -m pytest` temporary-SQLite suites, `npm run build`, `py_compile`,
  diff/trailing/line-count/forbidden-scope/no-real-file scans.
- Browser smoke at desktop and narrow width: open setup, create `P` x 4, add/remove a
  second row, apply to blank targets, save, confirm, reopen, and verify total/order.

## Merge Gate

Reviewer plan gate, explicit planning-first approval, Developer planning-first,
Reviewer implementation-readiness, explicit implementation approval, Developer
implementation, Reviewer implementation review, QA browser/regression gate, and
Integrator hunk-level package isolation are required. No workbook/Fee/schema/parser
or external residual hunk may enter the package.

## Definition Of Ready

Satisfied. Reviewer plan re-gate and implementation-readiness passed, and explicit
user approval authorizes the bounded Developer implementation. B1 freezes id
namespace, monotonic issuance, historical high-water, collision fail-closed behavior,
resolved persisted prefix, normalization/uniqueness, and focused acceptance cases.

## Blocking Questions

None.
