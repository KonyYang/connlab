# RELEASE_006B1 QA Evidence

Date: 2026-07-25
Role: QA / Smoke Owner
Status: `qa_pass`
Task: `RELEASE_006B1_FEE_PREVIEW_MANUAL_REQUIRED_BLOCKER_TEST`
Lane: `fee-preview-manual-required-blocker-test`

## Isolated Source

- Exact committed production baseline: `267eb50a4247082344e3d7a64a7e58353540d4be`.
- Created a disposable archive under `%TEMP%`; it was the only source tree used for test and build commands.
- Injected only the candidate path
  `frontend/src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts`.
- Reused the preconfigured frontend dependencies through a lock-compatible read-only junction. The filtered archive `package-lock.json` object matched HEAD: `56514af81d4277d8be1dcb7d7675d836d53ab9bf`.
- The filtered archive preview-model object matched HEAD. Raw hashes differ only because Windows checkout/archive handling uses CRLF; Git's filtered object hash matched the committed blob.
- No dirty legacy or product source file was copied into the isolate. No API, database, real file, or generated release artifact path was used.

## Validation

```text
cd <isolated archive>\frontend
npm test -- --run \
  src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts \
  src/features/fee-evaluation/feeEvaluationPricingDraftHydration.test.ts \
  src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts
=> 3 files / 33 tests passed

npm test -- --run --reporter=json --outputFile .qa_full_results.json
=> 109 files / 384 tests passed

npm run build
=> passed; existing Vite chunk-size warning only
```

The new test passed against unchanged committed production code. It verifies the complete unfiltered row order, blank manual-required DWV Unit Price, Pending Testing Fee, one Unit Price-only blocker, and the exact Group 1 / Step 1 / DWV message contract.

## Scope Checks

- Candidate is strict UTF-8, has no trailing whitespace, and is `181` physical lines (`<=250`).
- Candidate archive and working-tree SHA-256 matched: `907803d09e900bc277f7495406897a6b15b87fa3f6dd0cc5f6c23c9aaaf7af92`.
- Locked legacy test remains `1389` lines, SHA-256 `d2bf49bbddccc3971d81594b98208b5bc979344caa74c64996f2ab1d64bacd95`, and its existing `114/0` dirty hunk remains excluded.
- No RELEASE_006B1 diff in the preview model, API client, `package.json`, or `package-lock.json`.
- `git diff --check` and `git diff --cached --check` passed. The index is empty.
- B2/B3, the excluded LLCR duplicate node, Child C, and all external residuals were not exercised as package inputs.

## Residual Risk And Disposition

Full-suite stderr retained known test-fixture/React `act(...)` noise outside this candidate; no candidate failure or new product-console error was observed. The temporary archive is disposable and will be removed after this evidence checkpoint.

QA gate: pass.

Recommended next role: Integrator packaging/readiness. Package only the new bounded test plus approved RELEASE_006B1 governance/evidence; do not absorb the old mixed test or any residual.
