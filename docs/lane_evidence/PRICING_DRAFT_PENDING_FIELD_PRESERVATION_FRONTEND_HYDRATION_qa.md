# QA Evidence - PRICING_DRAFT_PENDING_FIELD_PRESERVATION_FRONTEND_HYDRATION

Date: 2026-07-24

Role: QA / Smoke Owner

Task: `PRICING_DRAFT_PENDING_FIELD_PRESERVATION_FRONTEND_HYDRATION`

Lane: `pricing-draft-pending-field-preservation-frontend-hydration`

## Gate Result

`qa_pass` after the authorized legacy-tests-only re-gate.

The former legacy-suite blocker is closed by the Reviewer-approved migration
of exactly 16 legacy nodes. The product candidate remains unchanged.

## Environment And Safety Boundary

- Repository: `D:\PythonProject\connlab`
- No product or test source was edited by QA.
- No real database, workbook, public-drive path, attachment, generated output,
  or operator-configured application was accessed.
- Backend tests used disposable fixtures only. The staged index was empty;
  `data`, `dist_release`, and `frontend/dist` had no tracked changes.

## Passing Validation

| Command | Result | Coverage |
| --- | --- | --- |
| `npm test -- --run feeEvaluationPricingDraftHydration.test.ts FeeEvaluationReviewExportPage.pricingDraftHydration.test.tsx feeEvaluationPreviewModel.test.ts` | 3 files / 37 passed | Pending/null/empty-string/explicit-zero hydration, manual-field protection, compatibility and server-rebase modes, missing/reload/Cancel/CAS behaviour, and fresh-GET current-V2 gating. |
| Read-only six-node model compatibility selector from the approved plan | 6 passed, 23 skipped | Existing public wrapper remains usable through `feeEvaluationPreviewModel.ts`. |
| `py -m pytest tests/integration/test_fee_evaluation_pricing_draft_compatibility_api.py -q` | 3 passed | Pending dependent-field API mapping and explicit-zero distinction. |
| TASK_361L/TASK_363D V2 persistence/contract/repository/attestation/rebase/Measurement Plan/CR/API regression set | 37 passed | Currentness, attestation, CAS/no-overwrite, reviewed rebase, and compatibility behaviour. |
| `npm run build` | passed | TypeScript/Vite build passed; only the existing Vite chunk-size warning appeared. |
| `py -m py_compile` candidate route/API test; candidate diff/trailing checks | passed | No compile, diff-check, or trailing-whitespace issue. |

Static inspection confirmed the helper has only type imports from the model,
and the model imports the helper in the approved one-way runtime direction.
The route preserves pending Unit Price, Units, and Testing Fee as blank strings
while retaining explicit zero.

## Superseded Blocking Failure

Command executed:

```powershell
npm test -- --run src/features/fee-evaluation/feeEvaluationPricingDraftHydration.test.ts src/features/fee-evaluation/FeeEvaluationReviewExportPage.pricingDraftHydration.test.tsx src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx
```

Observed result: the new helper/model/page contract tests passed, but the
locked `FeeEvaluationReviewExportPage.test.tsx` had `16 failed / 28 total`.
One direct reproducible failure is:

```text
FeeEvaluationReviewExportPage > sends current edited preview values to the Fee Form download
expected export spy to be called at least once
at FeeEvaluationReviewExportPage.test.tsx:1217
```

The page now correctly requires saved page state plus a fresh server GET
classified as `current_v2` before enabling Fee Form/export. The old test
fixtures/assertions do not establish that condition, so they expect an export
path that Reviewer B2 explicitly closed. The test is recorded in Developer
evidence as a 1718-line read-only legacy file and is not an authorized Child 3
test path. Updating it requires a Planner scope/compatibility decision; QA
must not change it and Developer must not silently absorb it as an unbounded
whole-file change.

## Browser Smoke Limitation

Independent controlled-browser smoke could not be reproduced safely in this
thread. The machine has Chrome processes but no CDP endpoint on 9222/9223, no
Playwright/Puppeteer/browser runner dependency, no running Vite mock harness,
and the remaining normal application path would read operator configuration.
That is outside the disposable-only contract. Developer evidence records a
prior disposable mock-API/Vite smoke at `1280x720` and `514x831`, including
candidate/save-before-fresh-GET/fresh-current-V2 Fee Form states, no console
warnings/errors, and no viewport overflow. This evidence is not substituted
for the unresolved locked-test failure.

## Package And Scope Checks

- Candidate physical lines are within frozen budgets: route 319, API test 209,
  model 925, helper 288, page 1425, helper test 198, and page test 422.
- Candidate `git diff --check` passed with only existing LF/CRLF notices.
- Candidate UTF-8 trailing-whitespace scan was clean.
- No forbidden frontend API client, CSS, schema/database, fee-rule/default-fill,
  Matrix, or export-service candidate change was found.
- Mixed files require hunk isolation. Integrator must not stage whole
  `FeeEvaluationReviewExportPage.tsx`, `feeEvaluationPreviewModel.ts`, route,
  or compatibility API test while unrelated worktree residuals are present.

## Former Required Next Role

Planner source-of-truth / scope-reconciliation pass.

This required a Planner/Reviewer reconciliation and an authorized tests-only
migration. It is now closed by the re-gate below.

## QA Re-Gate - Legacy Tests-Only Closure

Date: 2026-07-24

Reviewer confirmed the test-only diff maps to exactly the 16 authorized legacy
nodes. The original 12 passing nodes and the shared
`arrangeSuccessfulContext()` definition remain unchanged. The migrated export
tests establish a saved page plus a fresh `current_v2` GET before their
positive export assertions.

### Re-run Results

| Command | Result |
| --- | --- |
| Full legacy Fee page plus Child 3 helper/model/page suite | 4 files / 65 passed |
| V2 persistence/contract/repository/attestation/rebase/Measurement Plan/CR/API set plus compatibility API | 37 passed |
| `npm run build` | passed, existing Vite chunk-size warning only |
| Candidate `py_compile`, diff-check, trailing-whitespace, line, staging, protected-output, and forbidden-path checks | passed; LF/CRLF notices only |

The re-run proves the former 16 failures are closed. It covers positive export
only after fresh `current_v2` and saved state, while rebase, save-before-GET,
missing, stale/blocked/loading/error, and CAS-conflict states stay guarded by
the bounded page hydration tests and the migrated legacy module. No production
consumer call is authorized before that transition.

React `act(...)` notices still appear on several existing, unchanged Fee page
test nodes. They were warnings only: the complete suite passed, and no product
console/browser error was observed. They remain non-blocking test-harness
noise outside this tests-only migration.

### Browser Re-Smoke Residual

Independent controlled-browser re-smoke remains unavailable in this QA thread:
no CDP endpoint on 9222/9223, no Playwright/Puppeteer/browser-runner package,
and no running disposable mock/Vite harness. Starting the normal application
would read operator configuration and violates the disposable-only gate.
Developer's already-recorded disposable mock-browser smoke covered 1280x720
and 514x831: rebase candidate visible, Fee Form disabled before fresh GET,
enabled only at fresh `current_v2`, no overflow/overlap, and no console
warnings/errors. This is a non-blocking environment residual, not a product
finding.

## Final Recommendation

Integrator packaging/readiness. Stage only the exact Child 3 candidate paths
and the 16 authorized test-node hunks; do not stage whole mixed files or any
umbrella/external residual.
