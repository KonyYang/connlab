# Contact Measurement Plan Independent Lifecycle Discovery Plan

## Current Phase / Active Task / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Repository baseline: TASK_360A, TASK_360B, TASK_360C, and TASK_360G are complete/accepted. TASK_360G is accepted in `b6c05123` even though the current board was later regressed by an unrelated commit and needs source-of-truth correction.
- Role: Planner Discovery Gate.
- Why allowed: the user approved planning for a new Contact Measurement Plan lifecycle, but explicitly limited this turn to discovery and planned documentation.

## User Goal

Move Contact Measurement Plan editing out of the long embedded Matrix Editor card into a dedicated setup workspace. Give the plan its own draft and confirmed lifecycle, allow clearly labeled draft workbook output before confirmation, and keep Fee and formal outputs on confirmed Measurement Plan authority. Bind plan revisions to Matrix revisions through deterministic impact analysis so harmless Matrix changes synchronize automatically while identity or eligibility changes create a review draft and never silently confirm suggestions.

## Confirmed By User

- Matrix Editor keeps a compact read-only summary and a `Contact measurement setup` entry action.
- The dedicated workspace owns families, counts, prefixes, target coverage, overrides, validation, draft save, plan confirmation, and draft workbook actions.
- Draft workbooks do not require Matrix confirmation and must show `DRAFT` / `NEEDS REVIEW`, Matrix revision, plan revision, generation time, and fingerprint.
- Fee, formal LLCR/CR workbook, and future formal consumers read confirmed Measurement Plan only.
- Description, Method, or Requirement text changes auto-refresh when target identity and eligibility remain stable.
- Sample quantity changes auto-sync and trigger Fee unit recalculation.
- Eligible target add/delete/move, LLCR/CR kind change, Group/sequence/suffix change, or stable identity change creates `Needs review` and does not auto-confirm.
- Unrelated non-LLCR/CR Step changes do not trigger review.
- The previous confirmed plan remains available during review. Only compatible unaffected targets remain effective for formal consumers; changed or new targets are excluded until plan confirmation.
- The system creates a review draft with a difference summary and suggestions, but suggestions require explicit acceptance and plan confirmation.

## Confirmed By Repository Evidence

- Current contact plans are serialized as `contact_plan_json` inside draft and confirmed Matrix Step quantity rows.
- Current plan promotion is coupled to Matrix confirmation. TASK_360G fixed persistence in that path but did not create an independent plan lifecycle.
- Confirmed Group and Row ids are regenerated across Matrix revisions. Source snapshot ids provide some lineage but may be absent, so they are not a complete stable target identity contract.
- Current specialized workbook preview/generation reads active `ConfirmedMatrixSnapshot.step_quantities` only and protects generation with a confirmed-Matrix fingerprint.
- Current Matrix Editor renders `MatrixContactMeasurementPlanCard` below Project Schedule and mixes configuration, target status, save, preview, generate, and download in one surface.
- Current frontend routing already has a dedicated Basic Information page/workspace pattern that can be reused for setup navigation.
- TASK_360G accepted tests prove canonical contact plans can survive Matrix confirmation and that Fee/TASK_360B remain confirmed-only consumers.
- The design audit recommends a compact summary, dedicated setup workspace, independent confirmation, explicit draft output labels, and stale-state display.

## Planner Inference

- An independent authority model is required. Continuing to store the only plan lifecycle inside Matrix Step quantities cannot safely represent independent plan revisions, old confirmed retention, review drafts, partial compatibility, or separate stale detection.
- A non-destructive schema addition is required, but no schema change is authorized by this Discovery Gate.
- The authority should use immutable plan versions plus target snapshots and impact records. Current embedded contact plans remain compatibility input until an explicit migration lane is reviewed.
- Formal consumers need an effective confirmed projection: latest confirmed plan intersected with the latest Matrix compatibility result. New, changed, moved, deleted, or kind-changed targets must not enter formal output until reconfirmed.
- Plan confirmation needs an expected draft fingerprint and expected Matrix binding fingerprint to reject stale confirmation.

## Not Yet Confirmed

- The exact stable target key representation. Current source snapshot ids are useful lineage evidence but do not cover every manually created target.
- Whether contact families should use child rows or one controlled serialized snapshot per target version. This affects migration, diffing, and query boundaries.
- Whether legacy confirmed Matrix contact plans are backfilled eagerly during migration or exposed through a temporary read adapter until the operator confirms the first independent plan.

These are contract decisions for TASK_361A and Reviewer review. They block TASK_361B implementation approval, but they do not block creating TASK_361A as a planned contract lane.

## Approaches Considered

### Recommended: Independent versioned Measurement Plan authority

Create plan draft/confirmed versions, target snapshots, Matrix binding metadata, and impact-analysis records. This is the only option that directly satisfies independent confirmation, history, partial compatibility, review drafts, and stale detection without weakening Matrix authority.

### Rejected: Continue embedding plan state in Matrix Step quantities

This minimizes schema work but keeps plan confirmation coupled to Matrix confirmation and cannot retain a confirmed plan while a structurally changed Matrix creates a separate review draft.

### Rejected: General event-sourced project authority

An event log could model every transition but would introduce a project-wide architecture not required for this workflow. Immutable plan versions plus focused impact records are sufficient.

## Proposed Authority Contract

### Version lifecycle

- `draft`: editable saved plan revision.
- `needs_review`: system-created draft after a structural Matrix impact.
- `confirmed`: immutable operator-confirmed plan revision.
- `superseded`: prior confirmed revision retained for history after a new confirmation.
- At most one editable draft/review draft and one active confirmed plan per project.

### Matrix binding

- Every plan version records its source confirmed Matrix id/revision and a canonical Matrix target-set fingerprint.
- Target identity must be independent from generated confirmed/draft row ids. TASK_361A must define a stable lineage key that works for imported and manually created groups/rows before schema implementation is approved.
- Text metadata may refresh without changing target identity.
- Sample quantity is a compatible binding fact, not contact configuration. It updates the effective projection and Fee units with an audit record.

### Impact taxonomy

| Matrix change | Plan effect | Formal consumer effect |
|---|---|---|
| Description, Method, Requirement only | Auto-refresh display metadata; no review | Continue using confirmed target |
| Group sample quantity | Auto-sync binding and recalculate units | Continue using confirmed target with new sample quantity |
| Unrelated non-contact Step | No plan impact | No change |
| New eligible LLCR/CR target | Create/update review draft with suggested blank target | Exclude new target until confirmed |
| Deleted eligible target | Mark removed in review draft | Omit removed target from current effective projection |
| Move, sequence/suffix, Group identity, stable identity, or LLCR/CR kind change | Mark old/new target pair for review, never auto-confirm | Exclude changed target until confirmed |

### Review workflow

1. Matrix confirmation or revision publication invokes impact analysis.
2. Compatible changes update binding metadata and append an audit result.
3. Structural changes create or refresh one review draft from the active confirmed plan.
4. The workspace shows difference rows and suggestions.
5. `Accept suggested changes` copies suggestions into the editable draft only.
6. `Confirm measurement plan` validates an expected plan fingerprint and Matrix fingerprint, then creates a new immutable confirmed plan.

### Legacy compatibility

- Existing `contact_plan_json` remains readable and is not deleted.
- A reviewed migration must bootstrap an initial independent plan from the latest valid confirmed Matrix contact snapshots or retain a temporary compatibility adapter.
- No consumer switches authority until the independent confirmed projection has parity tests and migration coverage.

## UX Boundary

### Matrix Editor summary

- Replace the long editor with one compact read-only summary near Project Schedule.
- Show status, active plan revision, bound Matrix revision, LLCR/CR readings summary, included/affected target counts, last confirmation, and concise blockers.
- Primary action: `Contact measurement setup`.
- No family inputs, target table, workbook preview table, or generation controls remain in Matrix Editor.

### Dedicated setup workspace

- Route proposal: `/projects/{project_id}/contact-measurement-setup`.
- Use the existing project page/workspace shell pattern, not a modal.
- Main regions: plan status and lineage, common LLCR/CR family setup, target coverage/overrides, difference review, draft workbook preview, and a sticky completion dock.
- Actions remain distinct: `Save draft`, `Review changes`, `Accept suggested changes`, `Confirm measurement plan`, `Preview draft workbook`, `Generate draft workbook`.
- Draft output actions must never imply confirmation.

## Proposed Lane Split

### TASK_361A_CONTACT_MEASUREMENT_PLAN_AUTHORITY_IMPACT_CONTRACT

- Status: planned, contract-only, implementation not authorized.
- Owns lifecycle states, stable target identity contract, impact taxonomy, effective confirmed projection, stale tokens, schema/migration proposal, API DTO shapes, UX state contract, and legacy bootstrap rules.
- May Touch: TASK_361A task/plan/evidence and board only.
- Must Not Touch: all product code, schema, tests, API/client, real files.
- Validation: cross-check contract against TASK_360A/B/C/G models/services/tests; document state-transition and impact-case tables; Reviewer plan gate.
- Merge Gate: Reviewer accepts contract and user approves the first implementation lane.

### TASK_361B_CONTACT_MEASUREMENT_PLAN_AUTHORITY_BACKEND

- Status: proposed.
- Depends on accepted TASK_361A and explicit schema authorization.
- Owns non-destructive domain/storage/migration, plan draft/confirm services, stable target references, impact analysis, review-draft creation, stale guards, API routes, and migration compatibility tests.
- May Touch draft: focused backend domain/application/storage/API files, migration/database wiring, focused unit/integration tests, task evidence.
- Must Not Touch: frontend runtime, workbook generation, Fee rules, generic Test Record, Matrix parser, LTR/public-drive.
- Locked: real workbooks/folders, release/settings, `.agents/**`, `docs/project_management/**`.
- Validation: lifecycle transitions, one-active-confirmed/one-draft constraints, stale rejection, all impact taxonomy cases, legacy bootstrap, rollback-safe migration, no real mutation.
- Merge Gate: accepted TASK_361A schema contract, explicit user schema authorization, Reviewer implementation pass, migration/integration QA, and Integrator package isolation.

### TASK_361C_CONTACT_MEASUREMENT_SETUP_WORKSPACE

- Status: proposed.
- Depends on accepted TASK_361A API/UX contract and TASK_361B backend readiness.
- Owns the dedicated route/page/feature model, Matrix summary card, common families, target overrides, review-diff interaction, confirmation controls, accessibility, and browser smoke.
- May Touch draft: `frontend/src/App.tsx`, a dedicated page, `frontend/src/features/contact-measurement-setup/**`, focused Matrix Editor summary files, typed API client helpers, scoped CSS, tests.
- Must Not Touch: backend authority semantics, workbook gateway, Fee/Test Record consumers, Matrix parser.
- Validation: route/back navigation, loading/error/readonly states, no modal-first flow, compact Matrix summary, draft/confirm separation, keyboard/focus behavior, build and browser smoke.
- Merge Gate: TASK_361B API accepted, Reviewer UI gate, browser QA at desktop/narrow widths, and Integrator isolation from TASK_361D shared surfaces.

### TASK_361D_CONTACT_MEASUREMENT_DRAFT_WORKBOOK

- Status: proposed.
- Depends on TASK_361A and TASK_361B draft authority. Backend planning-first may run in parallel with TASK_361C after the API contract freezes; implementation must avoid shared frontend files until TASK_361C establishes the workspace slots.
- Owns draft projection, preview fingerprint, draft artifact generation/download, visible workbook labels, lineage metadata, and contained artifact lifecycle.
- May Touch draft: new draft projection/service/routes, approved reuse or extraction around the current macro-free gateway/artifact store, focused API/client/workspace wiring, tests.
- Must Not Touch: formal confirmed workbook behavior, generic Test Record, Fee authority, Matrix parser, real files.
- Validation: `DRAFT` and `NEEDS REVIEW` visible in workbook and preview, matrix/plan revision plus generated time/fingerprint present, stale fingerprint blocks, no-write preview, one contained `.xlsx`, no VBA, cleanup.
- Merge Gate: draft authority API accepted, Reviewer workbook gate, temp-artifact QA, no-real-file scan, and Integrator isolation from formal TASK_360B output paths.

### TASK_361E_CONTACT_MEASUREMENT_CONFIRMED_CONSUMER_MIGRATION

- Status: proposed.
- Depends on TASK_361B, TASK_361C, and TASK_361D acceptance.
- Owns migration of Fee and formal LLCR/CR workbook reads to the effective confirmed Measurement Plan projection, plus generic Test Record and future Report boundary regressions.
- May Touch draft: confirmed projection adapter, Fee quantity consumer, formal specialized workbook preview/generation source, focused tests and evidence.
- Must Not Touch: Fee rule pricing logic, Fee-side contact editing, generic Test Record semantics/output, full Report generation, Matrix parser, plan authoring UI.
- Validation: unaffected targets continue during review; new/changed targets are excluded; sample quantity recomputes units; formal workbook excludes unconfirmed targets; draft workbook may include them with draft labels; historical fallback is deterministic.
- Merge Gate: TASK_361B/C/D accepted, Reviewer consumer-authority gate, cross-consumer integration QA, and Integrator proof that generic Test Record and future Report scope remain unchanged.

## Dependency And Parallel Model

```text
TASK_361A contract
  -> TASK_361B authority backend/schema
       -> TASK_361C setup workspace
       -> TASK_361D draft workbook backend planning (parallel with 361C planning)
  -> TASK_361C + TASK_361D accepted
       -> TASK_361E confirmed consumer migration/regression
```

- Implementation of TASK_361B is serial after TASK_361A.
- TASK_361C and TASK_361D planning-first may run in controlled parallel after TASK_361A, but product implementation depends on TASK_361B DTOs and stable identity.
- TASK_361C owns shared workspace UI files. TASK_361D must not edit those files concurrently unless a later scope reconciliation assigns exact non-overlapping components.
- TASK_361E is serial last because it changes formal consumer authority.

## Schema Decision

Schema is required for the new lifecycle, but not authorized by this Discovery Gate. TASK_361A must produce a Reviewer-approved schema contract before TASK_361B can be approved. Expected conceptual records are plan version, target snapshot, contact family snapshot, Matrix binding/impact result, and audit metadata. Exact tables, constraints, migration/backfill, and rollback behavior remain a contract decision.

## Cross-Lane Locked Paths

- Existing generic Test Record button, routes, Word output, and semantics.
- Matrix parser/import rules and source document parsing.
- Fee pricing/default-fill rules beyond reading confirmed quantities in TASK_361E.
- Basic Information, Folder Actions, LTR/public-drive, StepInstance/execution, full Report generation, permissions, LAN/server, multi-user.
- Real project folders, public-drive files, real workbooks, release/settings/packaging cleanup.
- `.agents/**`, `docs/project_management/**`, remote push, destructive git operations.

## Definition Of Ready

- Discovery: satisfied.
- TASK_361A contract lane: ready as planned only. User intent, repository facts, boundaries, acceptance, dependencies, and validation are explicit.
- TASK_361B-E implementation lanes: not ready. They require accepted TASK_361A, explicit schema approval for TASK_361B, and separate lane gates.
- Blocking user questions: none for TASK_361A. Stable target identity, bootstrap migration, and exact schema constraints are technical contract decisions for Reviewer review, not assumptions to hide in implementation.

## Stop Point

Create TASK_361A as planned only and recommend Reviewer plan gate. Do not route Developer or approve any implementation lane.
