# DISCOVERY Worktree Residual Package Reconciliation

Date: 2026-07-21

Role: Planner discovery / governance ownership

Status: `discovery_complete_user_decision_required`

Identifier: `DISCOVERY_WORKTREE_RESIDUAL_PACKAGE_RECONCILIATION`

## 2026-07-22 Execution Follow-up

- The TASK_366C rollback fields in `docs/task_board.md` were reconciled at hunk level. Current Active Task is `none`, Proposed Next Task is user-directed, and the TASK_366C lane row records local acceptance at `0f51848f9fb64d326d5b95ddbee9cebb07fab9f1`.
- Six detached TASK_364B/C worktrees were audited without modifying their indexes or files.
- `task_364b_ninepath_isolated` reports 1,234 working-tree status entries caused by checkout/line-ending metadata, but `git diff` contains no content hunk.
- `task_364b_ninepath_isolated2` is clean.
- The eight substantive dirty files in each TASK_364B `isolated3`/`isolated4` worktree equal current `master`; their only difference from `master` is an older `frontend/src/api/client.ts` that lacks later accepted TASK_366A/B/C additions.
- Eleven substantive dirty files in each TASK_364C worktree equal current `master`; the remaining `backend/infrastructure/storage/database.py` and, in one worktree, `frontend/src/api/client.ts`, are older snapshots that lack later accepted TASK_366A/B/C additions.
- Therefore none of the six worktrees contains implementation content that is newer than or unique relative to current `master`. Removal is technically safe from a source-preservation perspective, but remains a destructive action requiring explicit user confirmation because these worktrees were created by earlier task sessions.
- The four untracked `dist_release` directories contain 5,555 generated files totaling about 566.47 MB. `dist_release/` is not currently ignored. The safe default remains to add a dedicated ignore rule and leave physical deletion for a separate explicit confirmation.
- After the user supplied the required `discard` confirmation, all six detached TASK_364B/C worktrees were removed with path/registration checks and `git worktree prune`; `git worktree list` now contains only the main `master` worktree.
- Root-level `/dist_release/` is now ignored. `git check-ignore` resolves the generated folders to that rule, while all existing release artifacts remain on disk and were not modified or deleted.

## Current Phase / Active Task / Why Allowed

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Accepted HEAD: `0f51848f9fb64d326d5b95ddbee9cebb07fab9f1`.
- Current branch: `master`.
- Current active task in accepted HEAD: none. HEAD board records TASK_366C complete/accepted and no automatic next lane.
- Why Planner may act: User requested a docs-only/worktree residual ownership discovery after TASK_366C acceptance, with no cleanup, restore, staging, commit, push, product implementation, real DB, public-drive, attachment, or source-workbook access.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- Git facts: `git rev-parse HEAD`, `git branch --show-current`, `git log --oneline origin/master..HEAD`, `git rev-list --count origin/master..HEAD`, `git merge-base --is-ancestor`, `git diff --name-status`, `git diff --numstat`, `git ls-files --others --exclude-standard`, `git status --short`, `git status --ignored --short -- dist_release`.
- Targeted diff/hunk reads for board, Fee/default-fill, parser, Contact Measurement summary, release packaging, and TASK_362A/364B/364C/365B governance residual groups.

## Confirmed By User

- TASK_366A/B/C are accepted local commits and HEAD ancestors: `2e8d7ddd`, `18df3f34`, `0f51848f`.
- Current uncommitted `docs/task_board.md` regresses TASK_366C from complete/accepted to pending Integrator and is an external residual requiring isolation.
- Worktree contains many tracked modifications plus untracked backend/docs/tasks and large `dist_release` generated folders.
- This pass must not modify product code/tests, clean, restore, stash, delete generated output, access real DB/public-drive/attachment files, stage, commit, push, or auto-route Developer/QA/Integrator.

## Confirmed By Repository Evidence

- `git rev-parse HEAD` returned `0f51848f9fb64d326d5b95ddbee9cebb07fab9f1`.
- `git branch --show-current` returned `master`.
- `origin/master..HEAD` contains 14 local commits. Relevant recent commits include:
  - `0f51848f feat(matrix): implement TASK_366C import method authority sync`
  - `18df3f34 feat(matrix): implement TASK_366B method version sync`
  - `2e8d7ddd feat(office): implement TASK_366A xls read compatibility`
- `git merge-base --is-ancestor` returned success for `2e8d7ddd2b7d08bff49987763cbdce66c0ebc4c6`, `18df3f34ce0f3bbac8c714b38f9b8aa747d100d7`, and `0f51848f9fb64d326d5b95ddbee9cebb07fab9f1`.
- Staging was empty.
- Tracked modifications are concentrated in 39 paths; untracked non-ignored paths total 5341, including 5332 under `dist_release`.
- `.gitignore` ignores `dist/`, `build/`, `tmp/`, `data/`, databases, logs, and local files, but does not ignore `dist_release/`.

## Residual Ownership Groups

### G1 - `docs/task_board.md` rollback hunk

- Paths: `docs/task_board.md`.
- Diff shape: 25 additions / 25 deletions.
- Most likely owner: stale Planner/Integrator package-state residual from pre-acceptance TASK_366C routing.
- Current governance state: accepted HEAD already has TASK_366C complete/accepted, Current Active Task none, Proposed Next Task user-directed.
- Current worktree state: rewrites top status, Current Active Task, Proposed Next Task, active execution model, and the active-lanes row to `Developer implementation complete / Reviewer pass / QA pass / pending Integrator packaging-readiness`.
- Recommendation: hunk-level restore the TASK_366C board rollback to HEAD after explicit user approval. Do not use whole-file restore unless no other board hunks are present at that time.
- Whitelist for that future cleanup: only the exact top status / Current Active Task / Proposed Next Task / Active Execution Model / TASK_366C active-lane row hunks that differ from HEAD.
- Next legal role: User approval for cleanup, then Planner docs-only board hunk reconciliation or Integrator if the user wants a controlled cleanup commit.

### G2 - Fee/default-fill and pricing-draft residual

- Paths:
  - `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py`
  - `backend/application/confirmed_matrix_fee_draft_service.py`
  - `backend/application/confirmed_matrix_fee_base_fee_policy.py`
  - `backend/application/confirmed_matrix_fee_rule_resolution.py`
  - `backend/modules/fee_evaluation/fee_default_fill.py`
  - `backend/modules/fee_evaluation/fee_default_fill_common.py`
  - `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`
  - `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
  - `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts`
  - `tests/integration/test_fee_evaluation_pricing_draft_compatibility_api.py`
  - `tests/unit/test_confirmed_matrix_fee_draft_service.py`
  - `tests/unit/test_fee_default_fill.py`
- Diff/stat: tracked Fee group is 373 additions / 93 deletions, plus two untracked backend helpers.
- Observed hunk themes:
  - Preserves Pending numeric fields as blank rather than `0/1/0`.
  - Introduces context-sensitive Fee rule resolution helper.
  - Applies Matrix-wide base-fee policy helper to Fee draft calculations.
  - Adds temperature-life / damp-heat / temperature-rise and multi-group default tests.
  - Frontend hydration uses manual-required-aware blank defaults and shorter blocker copy.
- Most likely owner: mixed Fee/default-fill corrective residual spanning accepted TASK_362A baseline notes and later Fee behavior work; not owned by accepted TASK_366C.
- Current governance state: no active lane in HEAD; no current approval to package these Fee/product/frontend hunks.
- Recommendation: do not absorb into any current task. Create a separate Planner discovery lane if the user still wants this behavior, or hunk-reset/discard only after explicit user approval if confirmed duplicate/stale.
- Potential package whitelist if a new lane is approved: the 12 paths above only, with the two untracked helpers treated as product May Touch and all Fee/frontend mixed hunks reviewed independently.
- Dependencies: would need to reconcile against accepted TASK_362A, TASK_363A/D, TASK_361L, and current Fee Evaluation behavior. It may conflict with active pricing-draft/rebase contracts.
- Next legal role: User decision -> Planner Discovery Gate for a Fee/default-fill residual package, not Developer.

### G3 - Spec section parser residual

- Paths:
  - `backend/modules/test_plan/spec_section_text_extractor.py`
  - `tests/unit/test_spec_section_text_extractor.py`
- Diff/stat: 56 additions / 0 deletions.
- Observed hunk themes:
  - Adds Damp Heat condition extraction with temperature/humidity/RH/duration segments.
  - Adds tests for long-term damp heat plus thermal-shock and voltage-surge assertions.
- Most likely owner: TASK_365C thermal/surge/parser follow-up or a future Damp Heat parser corrective.
- Current governance state: TASK_365C is complete/accepted in HEAD. These hunks are not part of the accepted HEAD package.
- Recommendation: treat as an unaccepted parser candidate. If needed, create a narrow new parser lane; otherwise obtain user approval before discard.
- Potential package whitelist if approved: only the two paths above; no Fee seed/default changes, source document writes, real files, Matrix persistence, or frontend.
- Next legal role: User decision -> Planner Discovery Gate for Damp Heat parser residual, not Developer.

### G4 - Contact Measurement Summary UI residual

- Paths:
  - `frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.tsx`
  - `frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.test.tsx`
- Diff/stat: 23 additions / 4 deletions.
- Observed hunk themes:
  - Summary card hides confirmed revision text.
  - Renders LLCR, CR, IR, DWV rows.
  - Uses `confirmed.cr_coverage` to display CR category count / points per sample.
- Most likely owner: unaccepted Contact Measurement summary UI follow-up around TASK_364B/CR coverage display. It is explicitly excluded from accepted TASK_364B package per board evidence: SummaryCard production and visual-test residuals were excluded.
- Current governance state: TASK_364B is complete/accepted at `9ac410b7`; this SummaryCard production residual is not accepted.
- Recommendation: do not package with completed TASK_364B. Create a new planned-only UI summary lane if the user wants it, with `$impeccable` and frontend architecture rules; otherwise user-approved discard.
- Potential package whitelist if approved: only the two SummaryCard paths plus any required exact DTO/client hunk if current accepted API lacks data. No backend/API/schema/Fee/workbook/parser changes without separate gate.
- Next legal role: User decision -> Planner Discovery Gate for Contact Measurement Summary UI.

### G5 - Browser release packaging residual and generated output

- Product/test paths:
  - `packaging/connlab_browser_server.spec`
  - `scripts/build_windows_browser_release.ps1`
  - `tests/unit/test_desktop_release_scripts.py`
- Untracked docs:
  - `docs/release_004_browser_release_packaging_performance_plan.md`
- Untracked generated dirs:
  - `dist_release/ConnLab_Web_202607170801_v0.1.0` (`1503` files, about `183.57` MB)
  - `dist_release/ConnLab_Web_202607171300_v0.1.0` (`1503` files, about `183.57` MB)
  - `dist_release/ConnLab_Web_202607200802_v0.1.0-release004-smoke` (`1274` files, about `99.41` MB)
  - `dist_release/ConnLab_Web_202607200813_v0.1.0` (`1275` files, about `99.92` MB)
- Observed hunk themes:
  - Browser PyInstaller spec excludes desktop-only backend prefixes and WebView/PyQt/pythonnet imports.
  - Release build script adds timed steps around tests, frontend build, PyInstaller, and release folder preparation.
  - Tests assert the timing and browser-only packaging changes.
- Most likely owner: release-engineering side task / RELEASE_004 browser packaging performance.
- Current governance state: untracked plan exists, but no accepted package in HEAD for this release residual. `dist_release/` is not ignored by `.gitignore`; many existing ignored subpaths appear under old release folders, while the four new folders are untracked.
- Recommendation: do not delete or package automatically. User should decide between:
  1. Formal release-engineering lane to package script/spec/test/docs only;
  2. Add `dist_release/` or specific generated folder pattern to `.gitignore` in a separate docs/build hygiene lane;
  3. User-approved deletion of generated output folders after confirming no operator artifact is needed.
- Potential package whitelist if lane approved: the three tracked release paths plus `docs/release_004_browser_release_packaging_performance_plan.md`; never include `dist_release/**` generated output unless a release artifact policy explicitly requires it.
- Next legal role: User decision -> Planner Discovery Gate for release/build hygiene or release packaging.

### G6 - Accepted governance completion wording duplicates

- Paths:
  - TASK_362A governance/evidence: `tasks/TASK_362A_COMPLETE_FEE_REFERENCE_BASE_SEED.md`, four TASK_362A evidence files.
  - TASK_364B governance/evidence/plan: task, plan, R1 plan, and four Planner reconciliation evidence files.
  - TASK_364C governance/evidence/plan: task, plan, and three Planner evidence files.
  - TASK_365B governance/evidence/plan: task, plan, Planner evidence, and user-acceptance evidence.
  - Untracked completion evidence: `docs/lane_evidence/TASK_364B_project-point-profile-cr-coverage-authority-and-ui_completion_reconciliation_planner.md`, `docs/lane_evidence/TASK_365B_text-pdf-docx-matrix-extraction-parity_completion_reconciliation_planner.md`.
- Observed hunk themes:
  - Adds exact accepted commit IDs and completion wording after the matching lanes were already accepted into HEAD.
  - Updates historical `pending Integrator` wording to complete/accepted.
- Most likely owner: stale governance closeout drafts created before or during accepted package commits.
- Current governance state: HEAD board already records TASK_364B/C/365B complete/accepted and current active task none. Some per-task/evidence files in HEAD may be less verbose than these residual drafts, but the accepted board is already authoritative.
- Recommendation: do not auto-absorb. If the user wants richer historical evidence, create a single docs-only governance cleanup package with exact file whitelist and no product/test paths. Otherwise user-approved discard.
- Next legal role: User decision -> Planner docs-only cleanup lane or hunk-level discard.

### G7 - TASK_364A visual alignment docs residual

- Paths:
  - `tasks/TASK_364A_POINT_PROFILE_EDITOR_VISUAL_ALIGNMENT.md`
  - `docs/task_364a_point_profile_editor_visual_alignment_plan.md`
  - `docs/lane_evidence/TASK_364A_point-profile-editor-visual-alignment_developer.md`
- Observed hunk themes: frontend-only visual alignment task documentation and developer evidence; board currently describes TASK_364A as complete locally, not complete/accepted.
- Most likely owner: TASK_364A local-only task package not accepted into HEAD.
- Current governance state: not an active lane; no current packaging authorization.
- Recommendation: keep as unaccepted docs candidate unless user wants to package or discard TASK_364A. If packaged, it needs its own accepted evidence/gates; do not mix with TASK_364B/C.
- Next legal role: User decision -> Planner/Reviewer package-scope reconciliation for TASK_364A if desired.

### G8 - Untracked TASK_363D Planner evidence

- Path: `docs/lane_evidence/TASK_363D_fee-pricing-draft-prior-defaults-attestation_planner.md`.
- Observed content: Planner evidence still says `implementation authorized / pending Developer implementation` even though TASK_363D is complete/accepted at `754b79bc`.
- Most likely owner: stale pre-implementation evidence leftover.
- Current governance state: accepted HEAD already records TASK_363D complete/accepted.
- Recommendation: do not package as-is; either discard with approval or supersede in a docs-only historical evidence cleanup.
- Next legal role: User decision.

## Board Reconciliation Strategy

Do not run a whole-file restore of `docs/task_board.md` while this shared dirty worktree remains mixed. The safe strategy is:

1. Use `git show HEAD:docs/task_board.md` as the accepted baseline.
2. Extract only the TASK_366C top-status, Current Active Task, Proposed Next Task, Active Execution Model, and active-lanes row hunks that currently regress from complete/accepted to pending Integrator.
3. Apply a hunk-level restore after explicit user approval.
4. Re-run targeted stale scan for `TASK_366C` current-state phrases, `git diff --check -- docs/task_board.md`, UTF-8 trailing scan, and `git diff --cached --name-only`.
5. Leave all non-board residuals untouched.

## Recommendations

1. First user decision: authorize a tiny docs-only board hunk reconciliation to restore `docs/task_board.md` to accepted HEAD for TASK_366C current state while preserving any unrelated board hunks.
2. Second user decision: choose which residual groups are still valuable:
   - Fee/default-fill package (G2)
   - Parser/Damp Heat package (G3)
   - Contact Measurement Summary UI package (G4)
   - Release packaging/build hygiene (G5)
   - Governance history cleanup (G6/G8)
   - TASK_364A local package closeout (G7)
3. Third user decision: decide whether `dist_release/` generated artifacts should be ignored or manually cleaned. Deletion requires explicit approval and must verify paths remain inside `D:\PythonProject\connlab\dist_release`.

## DoR Assessment

DoR is satisfied for this discovery evidence only. No implementation or cleanup lane is approved. Current active task should remain none based on accepted HEAD, but the working-tree board residual currently contradicts that and should be reconciled only after explicit user approval.

Blocking questions for the user:

1. Should Planner perform the exact `docs/task_board.md` TASK_366C hunk-level restore to accepted HEAD now?
2. Which residual group should be packaged next, if any: Fee/default-fill, parser/Damp Heat, Summary UI, release packaging, governance cleanup, or TASK_364A?
3. Should `dist_release/` be added to ignore policy or should generated folders be deleted under an explicit cleanup approval?

## Verification

- This pass did not modify product code, tests, schema, database, frontend/API client, generated release folders, real DB, public-drive files, attachments, or source workbooks.
- No stage, commit, push, restore, stash, cleanup, or deletion was performed.
- Staging was empty before evidence creation.
- Discovery commands were read-only Git/PowerShell inspections. The only file created by this Planner pass is this evidence file.
