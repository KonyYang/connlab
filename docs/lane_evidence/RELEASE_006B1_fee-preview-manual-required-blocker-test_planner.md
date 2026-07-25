# RELEASE_006B1 Fee Preview Manual-Required Blocker Test Planner Evidence

Date: 2026-07-25
Role: Planner
Status: `tests-only implementation authorized / pending Developer implementation`
Task: `RELEASE_006B1_FEE_PREVIEW_MANUAL_REQUIRED_BLOCKER_TEST`
Lane: `fee-preview-manual-required-blocker-test`
Parent: `RELEASE_006_POST_PUSH_WORKTREE_RESIDUAL_COMMIT_AND_CLEANUP_RECONCILIATION`
Implementation authorization: tests-only, exact bounded module only

## 1. Discovery Gate

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

Current active task:

```text
RELEASE_006B1_FEE_PREVIEW_MANUAL_REQUIRED_BLOCKER_TEST
tests-only implementation authorized / pending Developer implementation
```

Why Planner may act:

- Child B ownership audit passed Reviewer;
- Reviewer named B1 as the first formalizable bounded lane;
- Reviewer plan and implementation-readiness gates passed;
- User explicitly authorized tests-only implementation;
- Planner is reconciling the final source of truth before Developer starts.

User goal:

Preserve the unique manual-required Unit Price blocker assertion in a new
bounded test while keeping the oversized mixed legacy test and all production
code untouched.

## 2. Confirmed Facts

Confirmed by User:

- formalize only the first unique coverage item;
- do not bundle B2 or B3;
- do not modify tests or products;
- keep duplicate/support hunks and Child C locked;
- after reconciliation, route only Developer tests-only implementation.

Confirmed by repository evidence:

- Reviewer chose
  `RELEASE_006B1_FEE_PREVIEW_MANUAL_REQUIRED_BLOCKER_TEST`;
- the exact unique residual is `16/0` inside the current dirty
  `feeEvaluationPreviewModel.test.ts`;
- the old test is 1389 UTF-8 physical lines and mixed;
- accepted HEAD has the required public preview-model functions;
- accepted HEAD has no assertion combining the exact row label,
  `["Unit Price"]`, and `Complete Unit Price.`;
- `PRODUCT.md`, `DESIGN.md`, `$impeccable` product guidance,
  `docs/02_ARCHITECTURE_RULES.md`, and
  `docs/frontend_architecture_rules.md` confirm that blocker copy belongs to
  feature/model state and must remain concise, operational, and
  business-readable;
- this test-only lane preserves existing copy and architecture; it introduces
  no UI design, component, state, API, or styling decision;
- the index was empty before this Planner formalization;
- HEAD is `267eb50a4247082344e3d7a64a7e58353540d4be`;
- origin/master is `580fbb5ecc5a7fb8ffbdd151fb5198bd1db51db5`.

Planner inference:

- lane slug is the direct kebab-case form
  `fee-preview-manual-required-blocker-test`;
- a local minimal fixture is sufficient because the public model functions
  accept typed Fee draft data without page or backend setup.

Authorized now:

- Developer may create only
  `frontend/src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts`;
- the new module must remain `<=250` UTF-8 physical lines including blanks.

Still not authorized:

- changes to any product path or the old mixed test;
- discard, restore, cleanup, staging, commit, or push.

No unresolved question changes May Touch, behavior, validation, or ordering.
Reviewer implementation-readiness passed and the User authorization is
explicit.

## 3. Exact Unique Hunk

Source residual:

```text
frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts
existing node:
"keeps a manually required unit price pending instead of defaulting it to zero"
current added assertion:
buildFeeEvaluationUpdateBlockers(...)[0]
```

Exact expected object:

```text
rowLabel: "Group 1, Step 1, DIELECTRIC WITHSTANDING VOLTAGE"
fields: ["Unit Price"]
rowMessage: "Complete Unit Price."
```

This is the only dirty-test behavior owned by B1.

Explicitly excluded from B1:

```text
saved manual-required LLCR hydration 98/0
multi-Group Base Fee fallback 22/0
backend fixture support 16/13
real Damp Heat integration 15/0
Thermal Shock replay 19/0
Voltage Surge replay 17/0
```

## 4. Frozen Future Scope

Only future test May Touch:

```text
frontend/src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts
```

Maximum:

```text
250 UTF-8 physical lines including blanks
```

The test will own one local minimal draft/line fixture and exact assertions for:

- empty manual-required Unit Price;
- Pending Testing Fee;
- exact row label;
- Unit Price-only blocker ownership;
- exact row message.

No product implementation is needed or permitted.

## 5. TDD Interpretation

This is a tests-only characterization migration. The accepted production
behavior already satisfies the dirty assertion.

RED is therefore a coverage RED:

- clean accepted HEAD lacks the bounded module;
- clean accepted tests lack the complete exact assertion.

GREEN is:

- add the one bounded module;
- pass it against accepted production with zero product diff.

A fabricated product failure or deliberate product mutation is forbidden.

## 6. Validation Contract

Future focused command:

```powershell
Set-Location frontend
npm test -- --run src/features/fee-evaluation/feeEvaluationPreviewManualRequiredBlockers.test.ts src/features/fee-evaluation/feeEvaluationPricingDraftHydration.test.ts src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts
npm run build
```

The old test must be reconstructed from clean accepted HEAD for validation.

Package checks:

```text
new test module only
<=250 physical lines
no product diff
no old-test diff
exact whitelist
UTF-8 and trailing clean
diff-check clean
no real-data/generated-output mutation
```

## 7. Old-Hunk Disposition

The dirty `16/0` assertion remains untouched.

It becomes only a candidate for later exact discard/restore after the bounded
replacement is accepted. Reviewer confirmation and explicit User cleanup
authorization remain mandatory. No cleanup action belongs to B1 planning or
implementation.

## 8. Package Isolation

Locked:

- old frontend test;
- all frontend production;
- all backend/API/schema/database code;
- B2/B3 unique hunks;
- all duplicate/support hunks;
- Child C and external residuals;
- real data/files, generated artifacts, remote refs.

Whole-file staging of any mixed path is forbidden.

## 9. Planner Validation

Planner must verify:

- task, plan, evidence, and board use one exact task ID and lane;
- status is tests-only implementation authorized / pending Developer
  implementation;
- product, old-test edit, discard, commit, and push remain unauthorized;
- no test or product path changed;
- index remains empty;
- UTF-8, trailing, diff-check, stale-status, and scope scans pass.

## 10. Next Legal Role

```text
Developer tests-only implementation pass
```

Do not route QA, Integrator, discard, cleanup, commit, or push before the
Developer candidate and later gates.
