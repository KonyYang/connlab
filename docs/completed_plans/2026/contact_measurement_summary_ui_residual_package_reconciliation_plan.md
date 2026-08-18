# Contact Measurement Summary UI Residual Package Reconciliation Plan

Date: 2026-07-22

Status: complete / accepted after Integrator packaging

Task: `CONTACT_MEASUREMENT_SUMMARY_UI_RESIDUAL_PACKAGE_RECONCILIATION`

Lane: `contact-measurement-summary-ui-residual-package-reconciliation`

Implementation authorization: authorized for the exact May Touch in this plan

## Current Phase / Role / Why Allowed

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current role: Integrator package closeout.
- Why allowed: Developer implementation, Reviewer implementation gate, and QA gate passed.
- The package remains limited to the exact two SummaryCard paths and lane governance.

## Product Design Basis

Physical scene: a laboratory engineer scans the Matrix on a daytime Windows workstation and needs confirmed test-point facts without leaving the execution flow. The existing light, restrained ConnLab product system is therefore the correct surface. This lane adds no decorative treatment, nested card, modal, animation, or new navigation.

The SummaryCard stays a compact operational status surface adjacent to Matrix work. It does not become an editor, coverage authority, workbook control, or error console.

## Accepted Baselines And Live Facts

- TASK_364C backend/API/storage CR coverage baseline: `b34f2c2cbcc3b27266b480d6ff76a604f06be452`.
- TASK_364B CR coverage UI baseline: `9ac410b7c029c294e3b72bb1aaeca2c15c4d4cbd`.
- TASK_364B accepted `ProjectPointProfileCrCoverage` and the SummaryCard test fixture field, but explicitly excluded the SummaryCard production and visual test residuals.
- Current candidate numstat:
  - `ContactMeasurementPlanSummaryCard.tsx`: `13/2`;
  - `ContactMeasurementPlanSummaryCard.test.tsx`: `8/2`.
- Current UTF-8 physical lines including blanks:
  - component: `30`;
  - focused test: `48`.
- Current candidate hashes:
  - component: `3EB8F661CAB3533E7E931AF246B8A9E118716A58C64EB865630AFAB89AE57210`;
  - focused test: `E7C17B00BD3854998F1CC9F7177B4F0735A6E616901257F7A78A23DD966AF136`.
- The candidate already uses semantic `dl` / `dt` / `dd` and accepted `confirmed_revision.cr_coverage` facts.
- The candidate null copy, `Confirm a project point profile to make it available to Matrix summary.`, is not neutral. It implies a known no-confirmed-profile cause even though upstream also maps fetch failure to `summary=null`. Future implementation must replace it with the exact neutral copy below.

## Source-Of-Truth Reconciliation

Date: 2026-07-22

- Reviewer plan re-gate passed.
- User approved Developer planning-first.
- Developer docs-only planning-first complete.
- Historical state at the planning-first checkpoint: ready for Reviewer implementation-readiness gate.
- Historical authorization at that checkpoint: product implementation was not yet authorized.
- Current candidate numstat remains component `13/2` and test `8/2`.
- Current UTF-8 physical lines including blanks are component `30`, test `48`.
- Earlier `28` / `43` line-count facts are superseded historical checkpoints.
- Current candidate fingerprints are the SHA-256 values listed above.
- The current environment lacks the Vitest executable; focused tests/build remain future implementation environment prerequisites.
- Loading/resolved/null-neutral, no error disambiguation, accessibility, 514px/desktop, browser/build/test, exact May Touch/locks/package isolation, and client/model/parent/CSS/TASK_364B/TASK_364C locks remain unchanged.

## Final Authorization Reconciliation

Date: 2026-07-22

- Reviewer implementation-readiness gate passed.
- User explicitly approved product implementation.
- Current state: implementation authorized / pending Developer implementation.
- Authorized implementation remains limited to `ContactMeasurementPlanSummaryCard.tsx`, `ContactMeasurementPlanSummaryCard.test.tsx`, and lane governance docs.
- Current candidate numstat remains `13/2` and `8/2`.
- Current physical lines remain `30` and `48`.
- Current SHA-256 fingerprints remain:
  - component `3EB8F661CAB3533E7E931AF246B8A9E118716A58C64EB865630AFAB89AE57210`;
  - focused test `E7C17B00BD3854998F1CC9F7177B4F0735A6E616901257F7A78A23DD966AF136`.
- Loading/resolved/null-neutral unavailable semantics, no fetch-error disambiguation, accepted CR coverage display, accessibility, responsive no-overflow/no-overlap, console-clean, focused Vitest/build/controlled browser contracts, line budgets, rollback, hunk isolation, and package whitelist remain frozen.
- Vitest/build/browser validation still requires a complete preconfigured frontend environment.
- Client/model/parent/CSS/backend/API/schema, TASK_364B/TASK_364C accepted source, dependencies, real DB/files, generated artifacts, stage/commit/push, and external residuals remain locked.

## Exact Future May Touch

Product:

1. `frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.tsx`

Tests:

2. `frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.test.tsx`

Governance:

- this plan;
- `docs/lane_evidence/CONTACT_MEASUREMENT_SUMMARY_UI_RESIDUAL_PACKAGE_RECONCILIATION_developer.md`;
- future lane-only task, Planner, Reviewer, and board status hunks when the matching role is authorized.

No third product or test path is approved.

## Observable State Contract

The component continues to receive only:

```ts
summary: ProjectPointProfileSummary | null;
loading: boolean;
onOpenSetup: () => void;
```

It must not infer or synthesize fetch-error state.

### Loading

- Set `aria-busy={loading}` on the existing `section`.
- Keep the native `Setup` button disabled while `loading=true`.
- Disabled pointer or keyboard interaction must not call `onOpenSetup`.
- Do not add a spinner, skeleton, error banner, or loading card.
- Preserve the body selected by the existing `summary` prop so the compact surface does not reflow solely because `loading` changes.
- If `summary` is null while loading, the same neutral unavailable copy is shown. `aria-busy` communicates that the region is still resolving without making a success/failure claim.

### Resolved Summary Available

Authority source is only `summary.confirmed_revision`. Ignore editable/draft facts and diagnostics for display.

Render one semantic definition list in this exact order:

1. `LLCR`: `${confirmed.points_per_sample} points / sample`.
2. `CR`:
   - `follow_llcr`: `Same as LLCR · ${crCoverage.points_per_sample} points / sample`;
   - `custom`: `${selectedCount} category/categories · ${crCoverage.points_per_sample} points / sample`;
   - absent runtime coverage: `Not set`.
3. `IR`: `Not set`.
4. `DWV`: `Not set`.

Use the CR coverage object's accepted `mode`, `selected_category_ids.length`, and `points_per_sample` directly. Do not recalculate from category rows.

Do not display confirmed revision sequence, category bullets, target coverage, draft warning, Method, Matrix revision, workbook controls, or editor actions in this card.

IR/DWV remain display placeholders only. They do not claim new authority, setup support, Fee behavior, or output support.

### Resolved Summary Unavailable

When `summary=null` or `summary.confirmed_revision=null`, render exactly:

```text
Test point summary is not available.
```

This wording is deliberately neutral. It does not claim:

- no confirmed authority exists;
- loading succeeded;
- a request failed;
- the operator must confirm a profile;
- the unavailable state is permanent.

No error propagation, retry action, or diagnostic rendering is authorized.

## Content Hierarchy And Native Semantics

- Existing `section` remains the region with `aria-label="Test points"`.
- Existing `h3` remains the single compact heading.
- `Setup` remains a native `<button type="button">`; no div-button or custom keyboard handler.
- The facts remain a single `dl`; each row contains one `dt` and one `dd`.
- Semantic order is LLCR, CR, IR, DWV in both DOM and visual reading order.
- `Not set` is text, not color-only status.
- No nested cards, badges, icons, tooltips, explanatory feature copy, or oversized heading are added.

## Responsive Contract

Accepted `frontend/src/contact-measurement-plan.css` is read-only and already provides:

- desktop two-column summary grid;
- one-column summary grid at `max-width: 760px`;
- `min-width: 0` on fact rows;
- `overflow-wrap: anywhere` on values;
- stacked header at the narrow breakpoint.

At `514x831` and desktop `1280x800`:

- document and SummaryCard `scrollWidth` must not exceed `clientWidth`;
- heading, Setup button, every `dt`, and every `dd` remain visible and non-overlapping;
- long custom CR text wraps inside its own row;
- the Setup button remains reachable by keyboard;
- no console warning or error is emitted.

No CSS change is permitted. If the two-file implementation cannot satisfy these checks with accepted CSS, stop and route Planner re-scope rather than editing CSS.

## TDD Implementation Order

1. Record current hashes, numstat, line counts, and locked dependency hashes.
2. Expand only the focused test with red cases for loading, neutral null, custom CR, follow-LLCR CR, runtime missing coverage, semantic structure, native Setup activation, and removed legacy content.
3. Run the focused test and confirm failures are caused by the missing neutral/loading/coverage behavior, not environment or fixture errors.
4. Make the smallest component change:
   - preserve compact `dl` rendering;
   - add `aria-busy`;
   - replace null copy with the exact neutral wording;
   - retain native button and accepted CR formatting.
5. Run focused and read-only parent regression, then build.
6. Run the controlled browser smoke in an isolated temporary harness.
7. Run exact diff, trailing, line, scope, locked-hash, and staging checks.

## Focused Test Matrix

The bounded component test must cover:

- custom CR: `1 category · 4 points / sample` and plural categories;
- follow-LLCR: `Same as LLCR · 33 points / sample`;
- LLCR confirmed total comes from `confirmed_revision.points_per_sample`;
- IR and DWV each render `Not set`;
- runtime missing CR coverage renders `Not set` without throwing;
- `summary=null` and confirmed-revision-null both use only the neutral unavailable copy;
- null state contains no `Not confirmed`, `Confirm a project point profile`, failure, or retry claim;
- `loading=true` sets region busy, disables Setup, and does not invoke the callback;
- enabled Setup is focusable and native Enter activation calls the callback once;
- region label, heading level, `dl`, four `dt`, and four `dd` are present in DOM order;
- confirmed revision label, category list, category prefix/count text, target text, and draft warning are absent.

Read-only related regression:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx` to prove parent composition/route callback remains compatible.

## Frontend Dependency Gate

- `frontend/package-lock.json` exists and is the dependency authority.
- `frontend/package.json` defines `vitest run`, `tsc -b`, and Vite build.
- Current worktree has a partial `frontend/node_modules` but no `frontend/node_modules/.bin`; Vitest is not runnable now.
- Do not edit `package.json`, lockfiles, Vite config, or dependency versions.
- Future implementation may proceed only in a pre-provisioned dependency environment or after separately authorized environment restoration from the existing lockfile.
- If Vitest/build remain unavailable, stop with an environment blocker. Do not report ready for review on static inspection alone.

Required future commands from `frontend/`:

```powershell
npm test -- --run src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.test.tsx --watch=false
npm test -- --run src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.test.tsx src/features/matrix-editor/MatrixEditorWorkspace.test.tsx --watch=false
npm run build
```

## Controlled Browser Smoke

Use a temporary Vite harness under `tmp/`, importing the actual SummaryCard and accepted CSS but using local React fixture state only. It must issue no API request and must not use operator configuration or real project data.

Fixture states:

- loading with disabled Setup;
- neutral null summary;
- confirmed custom CR with long numeric/category text;
- confirmed follow-LLCR CR.

Checks:

- `514x831` and `1280x800` viewport screenshots for inspection, stored only under temporary workspace and removed after the run;
- document/card overflow and bounding-box assertions;
- pointer and native keyboard Setup behavior;
- semantic region/heading/fact visibility;
- console warning/error collection is empty;
- no network request outside the local Vite harness.

Browser smoke is mandatory for future implementation readiness. If browser tooling is unavailable, record the blocker and do not substitute DOM unit tests for the visual contract.

## Line Budget

- `ContactMeasurementPlanSummaryCard.tsx`: target `<=100` UTF-8 physical lines including blanks.
- `ContactMeasurementPlanSummaryCard.test.tsx`: target `<=150` UTF-8 physical lines including blanks.
- No blank-line suppression or compressed unreadable JSX may be used to meet the budget.

## Locked Dependency Baseline

These paths are read-only and must retain their pre-implementation hashes:

- `frontend/src/api/client.ts`: `171B4708ABC840F5ABE9B6432D05B094367340EAFFB96E35B905DE3C7136BCAE`.
- `frontend/src/contact-measurement-plan.css`: `695F33D7C1F23CA04519B3AD71450787B1C77D66DDCF5F92E67E0DA7204BFCA3`.
- `frontend/src/features/contact-measurement-plan/useProjectPointProfileSummaryModel.ts`: `1E5AC125E542B3D51E86B9C7701FCCB560E3B862F6D64099C4FD3E596D31D820`.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`: `012B42819C5057B328B8B16AE2FA3521074C88E76143A73186481B36D8A7C98C`.

Hash mismatch caused by external work must be reconciled before packaging. Do not overwrite or absorb it.

## Package Isolation And Rollback

- Candidate product/test whitelist is exactly the two SummaryCard paths.
- Preserve unrelated dirty residuals without cleanup or rollback.
- No client/model/parent/CSS/backend/API/schema/database/Fee/parser/LTR/release path may appear in the candidate.
- No real DB, public-drive path, attachment, operator project, generated output, staging, commit, or push.
- Use hunk-level review because both candidate files already contain dirty residuals.
- Rollback restores only the two SummaryCard files to the accepted HEAD behavior. No data or authority rollback exists.

## Integrator Closeout

Date: 2026-07-23

- Historical planning-first and implementation-readiness wording above is superseded by the completed Developer, Reviewer, QA, and Integrator gate chain.
- Integrator reran the focused SummaryCard plus Matrix parent regression: `2 files / 50 tests passed`.
- `npm run build` passed with the existing Vite chunk-size warning only.
- Final package source facts are component `14/3`, focused test `83/15`, physical lines `30` / `110`, and SHA-256 `727D95A7C0BDF404B12C4B5E1E917F0394B9AB6318FB2982D0157CA72843C893` / `1C0710AC49459A3BD5C29DD4C04B215C06AEFADBD42EB7C40711C996E3B8161B`.
- Remote push is not performed. No future error-propagation or Fee/default-fill lane is activated by this closeout.

## Next Legal Role

User / Orchestrator task selection.
