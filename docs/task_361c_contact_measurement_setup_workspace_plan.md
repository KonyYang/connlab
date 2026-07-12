# TASK_361C Contact Measurement Setup Workspace Plan

## Status

Complete / Integrator accepted on 2026-07-12 after Developer implementation,
Reviewer implementation re-gate, QA gate, and controlled Integrator
packaging/readiness. The responsive browser narrow-width limitation is recorded
as a non-blocking tooling residual in QA evidence.

## Current Facts

### Confirmed By User

- Replace the long Matrix Contact Measurement Plan editor with a compact read-only
  summary and a dedicated `Contact measurement setup` workspace.
- The workspace owns families/counts/prefixes, target decisions, overrides, impact
  review, draft save, and independent plan confirmation.
- Matrix confirmation is not Measurement Plan confirmation.
- TASK_361D draft workbook behavior and TASK_361E confirmed-consumer migration remain
  separate.
- Use the Basic Information navigation pattern and restrained operational UI.

### Confirmed By Repository Evidence

- TASK_361A/B are accepted; TASK_361B commit `8cafc79e` supplies independent
  authority storage/lifecycle and typed backend routes.
- Current `MatrixContactMeasurementPlanCard.tsx` mixes family editing, target
  coverage, save/apply, workbook preview/generation, messages, and errors.
- Matrix Editor mounts that card below the main table beside Project Schedule.
- `App.tsx` uses hand-written project route parsing; Basic Information demonstrates
  a route page -> feature workspace -> model pattern.
- `frontend/src/api/client.ts` has no independent Measurement Plan DTO/helpers yet.
- Current TASK_361B workspace response omits operator-readable Group/Step fields,
  impacts/candidates, selected revision/Matrix binding context, and exclusion/
  override detail.
- TASK_360B generated response exposes only current-session artifact id/file name;
  there is no persistent latest-artifact list/read API.

### Planner Inference And Decision

- A frontend-only implementation would either expose opaque `cmp-*` keys or invent
  impact context. TASK_361C therefore includes one additive read-only backend
  workspace service/DTO bridge, explicitly excluding lifecycle/storage/classifier
  semantic changes.
- The existing per-target PATCH and stale fingerprint contract is safe when V1 edits
  one selected target at a time and reloads after every command. TASK_361C does not
  add a bulk-write endpoint.
- Existing TASK_360B controls stay outside the setup workspace as a compact
  compatibility output row. Their confirmed-Matrix source is unchanged until
  TASK_361E; they must not be labeled as independent draft-plan output.

### Not Yet Confirmed

No blocking product question remains for plan review. Reviewer must explicitly
accept or reject the narrow read-model bridge because TASK_361A originally assigned
backend API ownership to TASK_361B.

## Additive Workspace Read Model

`ContactMeasurementPlanWorkspaceReadService` composes the accepted authority
repository and active Confirmed Matrix read port without writes. The existing
`GET .../summary` and `GET .../workspace` may add:

- selected revision id, sequence, state, and fingerprint;
- base confirmed Matrix id/revision and Matrix binding fingerprint;
- active confirmed and editable revision references;
- target display context: stable key for commands, Group label, test item, contact
  kind, Step sequence/suffix, sample quantity, inclusion/exclusion, override,
  readings, families, and target review state;
- impact rows: hidden command keys, category, severity, resolution, reason, and typed
  before/after operator context resolved from stored target plus current Matrix
  candidate;
- counts/diagnostics required for compact summary.

Opaque keys and fingerprints stay in the client model and are never rendered as
operator copy. Existing request shapes, lifecycle commands, error codes, formal
effective projection, and storage remain unchanged.

### Exact Read Contract

The new read service owns operator-facing enrichment only. The additive workspace
response must keep the current typed fields and add these grouped values:

- `plan`: active confirmed and editable revision references, sequence, editable
  state, current revision fingerprint, authority status, and concise diagnostics;
- `matrix_binding`: active confirmed Matrix id, revision/sequence, binding
  fingerprint, and compatibility status;
- `targets`: hidden `stable_target_key`, readable Group label/id label, test item,
  contact kind, Step sequence/suffix, sample quantity, inclusion, exclusion reason,
  override flag, readings per sample, families, target review state, and coverage
  state;
- `impacts`: hidden impact/candidate command keys, category, severity, resolution,
  concise reason, and server-resolved current-candidate Group/Step context; and
- `summary`: included/total counts, per-kind uniform-or-multiple readings facts,
  needs-review count, and the TASK_360B compatibility-row eligibility fact.

The bridge returns no write affordance, raw storage ids, artifact history, or
workbook data. It reads the accepted TASK_361B repository plus the active confirmed
Matrix through existing read ports. Missing/corrupt/matrix-unbound states are
typed status values with concise diagnostics, not guessed frontend fallbacks.

## Frontend Data Flow

1. Matrix summary loads the typed summary/workspace read model.
2. `Contact measurement setup` navigates to the dedicated project route.
3. Workspace loads read model; `not_started` offers `Open measurement plan`.
4. Only one target can be locally dirty. Selecting another target or leaving the
   page requires Save or Cancel in an inline prompt, never native `window.confirm`.
5. Save patches that target with the current fingerprint, then reloads workspace to
   receive the next fingerprint before any further write.
6. Impact refresh uses current Matrix binding fingerprint. Compatible acceptance and
   explicit rebind use accepted commands, each followed by reload.
7. Confirm uses the latest revision fingerprint. A stale `409` keeps the page open,
   discards no local input silently, and offers Reload.
8. Returning to Matrix reloads the compact summary. Matrix `Confirm Matrix` remains
   unrelated to plan confirmation.

### Command And Recovery Contract

- `Open measurement plan`, `Save draft`, target PATCH, impact refresh, compatible
  acceptance, target rebind, and plan confirm use the existing TASK_361B typed
  endpoints only. TASK_361C introduces no command endpoint and no bulk operation.
- Every successful command immediately reloads the workspace read model and replaces
  the in-memory fingerprint before another write is enabled. The command response
  revision id alone is not treated as a current token.
- A stale `409` leaves the selected local editor intact, marks it conflicted, and
  exposes a single inline Reload action. Reload must require explicit discard or
  re-application of the dirty local target values; it must never silently merge.
- A disabled `503/contact_measurement_plan_authority_disabled`, authority-corrupt,
  missing Matrix binding, or business validation error blocks only the relevant
  action and keeps readable context visible. Navigation and Matrix confirmation
  remain separate.

## UI Structure

### Matrix Summary

- One flat compact section adjacent to Project Schedule, not a nested card.
- Header: `Contact Measurement Plan`, state badge, `Contact measurement setup`.
- Dense facts: included/total targets; LLCR and CR readings/sample; Matrix revision;
  plan revision.
- Readings selector rule: no included target -> `-`; one distinct value -> value;
  multiple values -> `Multiple` plus concise target-count context.
- One inline warning for needs review/stale/corrupt/disabled; diagnostics are mapped
  to business copy.
- Separate compact `Specialized record workbook` row preserves TASK_360B actions and
  current-session filename only.

The summary states are exact:

| State | Compact status | Facts and action |
| --- | --- | --- |
| `not_started` | Not started | No revision; show `Contact measurement setup`. |
| editable `draft` / `needs_review` | Draft or Needs review | Plan revision, Matrix revision, included/total, readings selector, review count, and setup action. |
| `confirmed` / `complete` | Confirmed | Confirmed plan revision, Matrix revision, included/total, and uniform-or-multiple readings. |
| `partial_compatible` | Partially compatible | Confirmed facts plus one concise compatibility warning and setup action. |
| `authority_corrupt`, `disabled`, or unbound | Blocked | One concise blocked diagnostic; no invented readings or revision fact. |

The readings selector is calculated independently for LLCR and CR specified-current:
no included target is `-`; one distinct positive readings-per-sample value is shown;
otherwise it shows `Multiple` with the included-target count. It never sums across
targets. The compatibility row appears below the summary facts, is visible only when
the existing TASK_360B confirmed-Matrix eligibility says it is applicable, and stays
outside the workspace.

### Dedicated Workspace

- Route: `/projects/{project_id}/contact-measurement-setup`.
- Header: Back to Matrix, project identity, plan state/revision, Matrix revision.
- Needs-review band: affected count, concise difference summary, Review changes,
  Accept suggested changes when allowed.
- Main unframed split: target list/table and selected-target editor. At narrow width
  they stack; no viewport-scaled type.
- Selected target editor uses compact native controls for included state and family
  rows (label, count/sample, record label, prefix). Custom family add/remove is local
  to the selected target.
- Bottom action region is in normal/sticky flow with reserved content padding. It
  never overlays rows. Actions: Cancel local edits, Save draft, Confirm measurement
  plan. Only one primary action is emphasized for the current state.
- No draft workbook buttons, long explanatory copy, oversized checkboxes, nested
  cards, raw ids, or modal-first flow.

### Route, Return, And Accessibility

- `App.tsx` adds only `/projects/{project_id}/contact-measurement-setup`, parsed with
  the same decoded project id rule as Basic Information and Matrix Editor. It remains
  a Workbench-active route and gives the top bar `Contact measurement setup`.
- `ProjectContactMeasurementSetupPage` is a thin route page that composes
  `ContactMeasurementSetupWorkspace`, mirroring the existing Basic Information
  page-to-feature-workspace boundary. The Matrix summary navigates to this route;
  Back returns to `/projects/{project_id}/matrix-editor` and requests a summary
  reload there.
- On first successful load, focus moves to the page heading. After an inline target
  save/reload, focus returns to the selected target row or its status message. On
  stale/error/review state, focus moves to the inline status region only when the
  action initiated that state. Native buttons, labelled controls, `aria-live`
  inline status, visible focus, and table/list semantics are required.
- No focus trap or modal is introduced. At narrow widths the target list precedes
  the editor in source order; the normal/sticky action area reserves bottom padding
  and cannot obscure controls or the app shell dock.

## TASK_360B / TASK_361D / TASK_361E Compatibility

- TASK_360B formal specialized-workbook API and hook remain unchanged in 361C.
- Its controls are visually separated from independent plan editing and continue to
  mean current confirmed Matrix snapshot, not draft or newly confirmed independent
  plan authority.
- Persistent latest artifact history, draft labels/fingerprints, draft preview, and
  draft generation belong to TASK_361D. Since current APIs cannot read this history,
  361C omits it rather than showing placeholders or fake timestamps.
- TASK_361E later migrates Fee and formal specialized-workbook consumers to the
  effective confirmed Measurement Plan projection. Until then 361C must not claim
  that those consumers have migrated.

## Exact Authorized May Touch

Use the complete path list in the task file. Backend changes are limited to the new
read service plus additive GET DTO/composition/tests. Frontend changes are limited to
typed client helpers, route/page, new feature boundary, replacement of the legacy
Matrix card, scoped styles, and focused tests.

The exact implementation package is:

- `backend/application/contact_measurement_plan_workspace_read_service.py`;
- `backend/application/contact_measurement_plan_projection_service.py` only for
  delegation without a projection-semantic change;
- `backend/api/routes_contact_measurement_plan.py` and
  `backend/api/dependencies.py` only for additive GET response composition;
- workspace-read unit/projection regression/API tests listed in the task file;
- `frontend/src/api/client.ts`, `frontend/src/App.tsx`,
  `frontend/src/pages/ProjectMatrixEditorPage.tsx`, and new
  `frontend/src/pages/ProjectContactMeasurementSetupPage.tsx`;
- `frontend/src/features/contact-measurement-plan/**` for the workspace/model,
  selectors, compact summary, and focused tests;
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`,
  `MatrixContactMeasurementPlanCard.tsx`, their focused tests, and legacy selector
  files only to remove the old runtime editor after replacement;
- `frontend/src/contact-measurement-plan.css`, `frontend/src/workbench.css` only for
  scoped layout/legacy-class retirement, `tests/unit/test_frontend_shell_files.py`,
  and TASK_361C governance/evidence files.

No other route, client, backend application, storage, or stylesheet is implicitly
authorized. Any required move of TASK_360B controls must use its current frontend
hook/API without backend changes; otherwise it is a scope blocker.

## Locked Paths

All schema/models/migrations/repositories and TASK_361B write/lifecycle/classifier/
bootstrap semantics are locked. TASK_361D/E, TASK_360B backend generation,
Matrix confirmation/persistence, generic Test Record, parser/import, Fee rules,
Basic Information, LTR/public-drive, StepInstance/Report, real files, release/
settings, `.agents/**`, and `docs/project_management/**` remain locked.

## Authorized Implementation Sequence

1. Add backend workspace read service and additive typed GET fields with unit/API
   regressions; do not touch commands or storage.
2. Add independent Measurement Plan DTOs/helpers to `frontend/src/api/client.ts`.
3. Add feature selectors/model and focused state/stale-command tests.
4. Add dedicated page/route and navigation regression.
5. Replace the Matrix long editor with compact summary; retire legacy editor state
   and selectors only after no runtime caller remains.
6. Reposition TASK_360B controls into the separate compatibility row without API or
   semantic changes.
7. Add scoped responsive styles, focused frontend tests, build, and browser smoke.

## Validation Gate

- Backend: focused workspace-read service and API tests plus full TASK_361B
  projection/lifecycle regressions.
- Frontend: summary, selectors/model, workspace, Matrix integration, route/static
  boundary, TASK_360B hook regression, and accessibility interactions.
- Browser: controlled project at desktop/narrow widths; no modal, no bottom overlap,
  keyboard focus visible, stale/review states readable, Matrix and plan confirmation
  visibly separate.
- Build/static: `npm run build`, focused `npm test`, focused `py -m pytest`, Python
  compile, diff/trailing/forbidden-scope/no-real-mutation scans.

## Merge Gate

Package isolation accepted. The package excludes TASK_361D/E, backend authority
writes/storage, external parser/TASK_360Q-R-S residuals, release/settings
residuals, real-file scope, `.agents/**`, `docs/project_management/**`, and
unrelated board changes. Reviewer plan/readiness gates, both user approvals,
Developer implementation, Reviewer implementation review, QA, and Integrator
gates are complete.

## Dependencies And Parallelism

1. TASK_361A/B: complete/accepted prerequisites.
2. TASK_361C: complete/accepted setup workspace/client/UI lane.
3. TASK_361D: may plan after TASK_361B, but implementation must coordinate shared
   summary/API-client ownership with 361C and cannot package mixed hunks.
4. TASK_361E: serial last after 361C and 361D integration facts; owns confirmed
   Fee/specialized-workbook consumer migration.

## Definition Of Ready

Complete. No blocking questions remain for TASK_361C. Future TASK_361D/E work
requires separate approved lanes and cannot inherit TASK_361C package acceptance.
