# TASK_353B Registered LTR Workbook Row Preview - Reviewer Evidence

Task ID: `TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW`
Lane: `registered-ltr-workbook-row-preview`
Role: Reviewer
Date: 2026-07-07
Status: reviewer_plan_gate_pass

## Gate Summary

Reviewer plan gate passed with no blocking findings.

TASK_353B remains a planned lane only. This gate does not authorize Developer implementation. The next legal action should be User approval / Developer planning-first or source-of-truth reconciliation according to Orchestrator policy.

## Facts Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `tasks/TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW.md`
- `docs/task_353b_registered_ltr_workbook_row_preview_plan.md`
- `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_planner.md`
- Current status/diff for TASK_353B docs/board and external residual classification
- Existing read-only specified LTR workbook authority preview service/API/tests
- Existing Basic Information LTR workbook sync service/API/frontend card/tests

## Review Findings

No blocking findings.

- The lane is correctly scoped as formal planning-first work, not a quick implementation or Developer authorization.
- The target behavior is clear: registered-LTR projects get a read-only public LTR workbook row preview independent of Basic Information confirmed state.
- The existing write-capable Basic Information sync remains separate and should only receive copy clarification such as `Update LTR from Basic Information`.
- The plan explicitly blocks workbook write/commit/backup/save behavior for the new preview action and preserves the existing Basic Information sync commit gate.
- The plan correctly identifies reuse candidates: TASK_349A business row labels and the existing exact-DL row lookup behavior from Basic Information sync.
- May Touch / Must Not Touch / Locked Paths are sufficiently precise for a downstream planning-first pass.
- Validation gates are reviewable: registered-LTR read without Basic Information Confirm, no-LTR and not-found blockers, no write path, Basic Information sync regressions, TASK_349A preview regressions, focused frontend action/copy tests, build, diff, trailing whitespace, and forbidden-scope scans.

## Scope Boundary

The plan keeps these locked:

- No LTR workbook write/commit path for the new registered row preview.
- No weakening of existing Basic Information sync preview/commit gating.
- No Intake specified-LTR or local duplicate behavior changes.
- No Basic Information schema/migration changes.
- No Matrix parser/import, Fee calculation/export, Folder Actions/public folder workflow, Report, StepInstance, AI, permissions, LAN/server, or multi-user scope.
- No real workbook/public-drive/folder mutation in tests.
- No release/settings/template residual cleanup, `.agents/**`, `docs/project_management/**`, unrelated dirty files, remote push, or packaging.

Visible external residuals remain excluded from TASK_353B, including release/settings/template/desktop packaging work, TASK_352 PDF import files, Word/Fee output files, and unrelated backend/frontend tests.

## Reviewer Validation

Documentation/static checks:

```powershell
git diff --check -- docs/task_board.md tasks/TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW.md docs/task_353b_registered_ltr_workbook_row_preview_plan.md docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_planner.md
```

Result: passed with only the existing `docs/task_board.md` LF/CRLF warning.

```powershell
Select-String -Path tasks/TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW.md,docs/task_353b_registered_ltr_workbook_row_preview_plan.md,docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_planner.md -Pattern '\s+$' -Encoding UTF8
```

Result: no matches.

Repository fact checks confirmed:

- `SpecifiedLtrWorkbookAuthorityPreviewService` is read-only and already provides business row-value labels suitable as a reuse reference.
- `LtrWorkbookBasicInformationSyncService` currently requires confirmed Basic Information for sync preview/commit and contains a write-capable commit path that must remain separate from TASK_353B.
- `ProjectBasicInformationSummaryCard` currently labels the existing write-capable action as `LTR update preview` and shows `Confirm update`, supporting the planned copy clarification and separate read-only action.

## Recommendation

Recommended next role: User approval / Developer planning-first.

Do not route Developer implementation directly from this plan gate. Downstream Developer planning-first should refine the exact read-only service/API/client helper shape and package isolation before implementation authorization.

---

## Implementation-Readiness Gate

Date: 2026-07-07
Status: reviewer_implementation_readiness_pass

### Facts Read

- `AGENTS.md`
- `docs/task_board.md`
- `tasks/TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW.md`
- `docs/task_353b_registered_ltr_workbook_row_preview_plan.md`
- `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_planner.md`
- `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_reviewer.md`
- `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_developer.md`
- Current git status/diff for TASK_353B docs and external residuals
- Existing TASK_349A read-only LTR workbook authority preview code
- Existing Basic Information LTR workbook sync code and frontend summary card tests

### Findings

No blocking findings for implementation readiness.

- Developer planning-first was docs-only. No product source, tests, API client, backend route/service, schema, frontend component, CSS, `.agents/**`, or `docs/project_management/**` product implementation files were changed by this pass.
- Future May Touch is narrow enough for an implementation pass: new registered-row preview service/API, route/dependency/main registration, API client helper, `ProjectBasicInformationSummaryCard` UI/copy, optional narrowly justified model/workbench bridge files, and focused tests.
- The planned API/service boundary is concrete: `GET /api/projects/{project_id}/ltr-workbook/registered-row-preview`, `project_id` as the only input, backend-resolved latest registered LTR, read-only workbook transaction only, TASK_349A-style row values, and no preview ack or commit-oriented fields.
- The write/read split is explicit: `LTR workbook row preview` is read-only and registered-LTR based; `Update LTR from Basic Information` remains the existing write-capable sync/update flow, still gated by confirmed Basic Information.
- The test plan covers the important safety cases: no confirmed Basic Information required for read-only preview, no registered LTR blocker, not-found row, duplicate exact DL rows, no write/commit/backup/save calls, existing Basic Information sync regressions, TASK_349A preview regressions, frontend no-commit UI, build, and scope scans.
- Locked scopes remain intact: no LTR workbook write/commit/backup/save in the new preview, no Basic Information sync gate weakening, no Intake specified-LTR/local duplicate changes, no schema/migration, no Matrix/Fee/Folder Actions/Report/StepInstance/AI/permissions/LAN/server/multi-user, no real workbook/folder mutation, no release/settings/template residual cleanup, no `.agents/**`, no `docs/project_management/**`, and no remote push.

### Source-Of-Truth Caveat

`docs/task_board.md` still records TASK_353B as `planned / ready for Reviewer plan gate`, while the lane evidence now records Reviewer plan gate pass and Developer planning-first complete. This is not a planning-quality blocker, but it is an implementation authorization blocker for the next route.

Before Developer implementation starts, Orchestrator should route User approval plus Planner/Integrator board/source-of-truth reconciliation so the board no longer contradicts the evidence.

### Readiness Validation

- `git diff --check -- docs/task_353b_registered_ltr_workbook_row_preview_plan.md docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_developer.md` passed.
- Trailing whitespace scan on `docs/task_353b_registered_ltr_workbook_row_preview_plan.md` and `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_developer.md` returned no matches.
- Targeted status shows the planning-first pass introduced TASK_353B plan/developer evidence only; visible backend/frontend/test/release/settings residuals remain external and excluded.

### Recommendation

Recommended next role: User approval + Planner/Integrator board/source-of-truth reconciliation before Developer implementation.

Do not route Developer implementation directly until the board/source-of-truth state is reconciled.

---

## Implementation Gate

Date: 2026-07-07
Status: reviewer_blocked

### Findings

#### B1 - Workbook open/read failures can escape as 500 instead of readable blocked preview

- Severity: blocking
- File: `backend/application/registered_ltr_workbook_row_preview_service.py`
- Evidence: `preview(...)` opens the workbook through `open_read_only_transaction()` and reads rows inside the `try` block, but only catches `RegisteredLtrWorkbookRowPreviewError` and `LtrNumberError`.
- Why this blocks: the TASK_353B plan requires readable `blocked` states for workbook/read failures and explicitly says the route should map workbook lock/read errors to business-readable `blocked` or HTTP conflict where consistent with existing workbook routes. The existing TASK_349A specified-LTR preview wraps workbook read failures and reports `Unable to read LTR workbook for preview: ...` as a blocked preview. The new TASK_353B service does not currently wrap arbitrary workbook open/read exceptions, so missing workbook, locked workbook, Office/read gateway failure, or unexpected workbook session read errors can bubble to the API as an unhandled 500.
- Minimal fix required: catch non-domain exceptions around `open_read_only_transaction()`, row lookup, and row read; convert them into a `blocked` preview with a concise business-readable message. Add a focused unit/API regression proving a transaction/open/read exception returns `status == "blocked"` with no write/commit path.

### Non-Blocking Notes

- The core read-only path is otherwise aligned: project-id-only route/service, latest registered local LTR resolution, `open_read_only_transaction()` only, no preview ack/commit/backup/save fields, and tests preventing write/short transaction calls.
- The frontend action split is directionally correct: `LTR workbook row preview` is separate from `Update LTR from Basic Information`, and the existing `Confirm update` commit flow remains tied to the Basic Information sync helper.
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx` passes `deriveRegisteredProjectReference(latestLtr, project.project_no)` as the preview availability value. Existing Workbench semantics treat this as the registered project reference; if project records can have `project_no` without a registered LTR row, the backend blocker path must remain readable and QA should smoke that case.
- `backend/api/dependencies.py` currently contains unrelated accepted residual hunks for template resource work in the same file as the TASK_353B dependency addition. This is not the implementation blocker above, but Integrator will need hunk-level package isolation after the fix.

### Reviewer Validation

Commands rerun:

```powershell
py -m pytest tests/unit/test_registered_ltr_workbook_row_preview_service.py tests/integration/test_registered_ltr_workbook_row_preview_api.py -q
```

Result:

```text
6 passed
```

```powershell
py -m pytest tests/unit/test_registered_ltr_workbook_row_preview_service.py tests/integration/test_registered_ltr_workbook_row_preview_api.py tests/unit/test_ltr_workbook_basic_information_sync_service.py tests/integration/test_ltr_workbook_basic_information_sync_api.py tests/unit/test_specified_ltr_workbook_authority_preview_service.py -q
```

Result:

```text
39 passed
```

```powershell
npm test -- ProjectBasicInformationSummaryCard --run
```

Result:

```text
1 file / 10 tests passed
```

```powershell
npm run build
```

Result: passed with existing Vite chunk-size warning only.

```powershell
py -m py_compile backend/application/registered_ltr_workbook_row_preview_service.py backend/api/routes_ltr_workbook_registered_row_preview.py backend/api/dependencies.py backend/api/main.py
```

Result: passed.

Package `git diff --check` passed with existing LF/CRLF warnings only. Trailing whitespace scan on TASK_353B package files returned no matches. Static scan found no new write transaction / commit / backup / save behavior in the registered-row preview path.

### Recommendation

Recommended next role: Developer fix pass.

Fix only B1. Do not expand scope, do not alter existing Basic Information sync commit behavior, and keep external residuals excluded.

---

## Implementation Re-Gate - B1 Fix

Date: 2026-07-07
Status: reviewer_pass

### Findings

No blocking findings.

- B1 is closed. `backend/application/registered_ltr_workbook_row_preview_service.py` now catches non-domain workbook open/read/gateway exceptions around the read-only registered-row preview and returns a readable `status="blocked"` preview with `Unable to read LTR workbook for preview: ...`.
- The fix remains read-only. Static inspection of the registered-row preview service/route found no new write transaction, short transaction, commit, backup, save, `preview_ack`, or write-enabled behavior.
- The new unit/API regressions cover read-only transaction open failure, workbook row read failure, and API mapping to `blocked` with empty row values. Existing safety tests still assert the preview path does not open write or short transactions.
- Existing Basic Information sync commit behavior remains separate and unchanged. Existing TASK_349A specified-LTR preview and Basic Information sync regressions still pass.
- Scope remains aligned with TASK_353B. External dirty residuals are still visible in the worktree, including TASK_352/PDF, Settings/LTR/template, release/desktop/packaging, `frontend/src/workbench.css`, and unrelated tests/docs. They remain excluded from this gate and must be package-isolated by Integrator.

### Reviewer Validation

Commands rerun:

```powershell
py -m pytest tests/unit/test_registered_ltr_workbook_row_preview_service.py tests/integration/test_registered_ltr_workbook_row_preview_api.py -q
```

Result:

```text
9 passed
```

```powershell
py -m pytest tests/unit/test_registered_ltr_workbook_row_preview_service.py tests/integration/test_registered_ltr_workbook_row_preview_api.py tests/unit/test_ltr_workbook_basic_information_sync_service.py tests/integration/test_ltr_workbook_basic_information_sync_api.py tests/unit/test_specified_ltr_workbook_authority_preview_service.py -q
```

Result:

```text
42 passed
```

```powershell
npm test -- ProjectBasicInformationSummaryCard --run
```

Result:

```text
1 file / 10 tests passed
```

```powershell
npm run build
```

Result: passed with existing Vite chunk-size warning only.

```powershell
py -m py_compile backend/application/registered_ltr_workbook_row_preview_service.py backend/api/routes_ltr_workbook_registered_row_preview.py backend/api/dependencies.py backend/api/main.py
```

Result: passed.

Package `git diff --check` passed with existing LF/CRLF warnings only. Trailing whitespace scan on TASK_353B package files returned no matches. Static read-only scan found no write transaction / commit / backup / save behavior in the registered-row preview service or route; existing API client / Basic Information sync commit fields remain outside the new registered-row read-only preview path.

### Recommendation

Recommended next role: QA gate.

QA should smoke the Workbench / Basic Information side-card flow for registered LTR row preview, including found, blocked/read failure, and separation from `Update LTR from Basic Information`.

---

## Correction Implementation Re-Gate - User Direction Alignment

Date: 2026-07-07
Status: reviewer_pass

### Context

After TASK_353B acceptance, the user corrected the product direction: the separate `LTR workbook row preview` button/card/API/service/client workflow was over-scoped. The desired behavior aligns with TASK_353C: keep one original `LTR update preview` entry, allow registered-LTR projects to preview before Basic Information confirmation, use draft/initial Basic Information values for preview, and keep `Confirm update` / commit safety tied to confirmed Basic Information.

### Findings

No blocking findings.

- The over-scoped TASK_353B surface is removed from the candidate product/test package. The registered-row preview route, service, client DTO/helper, independent button/panel, and focused registered-row preview tests are deleted or removed from runtime references.
- The Basic Information side card now presents one LTR workbook action, `LTR update preview`. The rejected `LTR workbook row preview` and `Update LTR from Basic Information` split-action labels are absent from product/test code.
- Preview enablement matches the correction: the existing preview action is enabled when either confirmed Basic Information is available or a registered LTR number is present.
- Unconfirmed Basic Information preview uses `BasicInformationPreviewSnapshot` with `version=None` and `source_signature_hash=None`. The frontend keeps `Confirm update` disabled when those confirmed fields are null.
- Commit/update safety is not weakened. `LtrWorkbookBasicInformationSyncService.commit(...)` still calls `_require_basic_information(...)`, still requires `preview_acknowledged`, `operator_confirmed`, expected confirmed Basic Information version/hash, lifecycle write guard, exact row lookup, and the existing workbook write transaction path.
- No schema/migration, Intake specified-LTR/local duplicate semantics, Matrix, Fee, Folder Actions, Report, StepInstance, AI, permissions, LAN/server, multi-user, real workbook/folder mutation, `.agents/**`, or `docs/project_management/**` changes were introduced by the correction package.

### Non-Blocking Notes

- `docs/task_board.md` still presents TASK_353C as planned / Reviewer plan gate, while this correction arrived as a TASK_353B correction fix pass aligned with TASK_353C direction. The implementation evidence is reviewable and passes this gate, but Orchestrator/Planner should reconcile board/source-of-truth wording before integration packaging.
- `backend/api/dependencies.py` still contains unrelated template-resource residual hunks in the same file. They remain external to this correction and need hunk-level package isolation by Integrator.
- Existing release/settings/template/desktop/TASK_352/Fee/Word residuals remain visible in `git status` and are excluded from this gate.

### Reviewer Validation

Commands rerun:

```powershell
py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py -q
```

Result:

```text
19 passed
```

```powershell
py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py tests/integration/test_ltr_workbook_basic_information_sync_api.py tests/unit/test_specified_ltr_workbook_authority_preview_service.py -q
```

Result:

```text
34 passed
```

```powershell
npm test -- ProjectBasicInformationSummaryCard --run
```

Result:

```text
1 file / 10 tests passed
```

```powershell
npm run build
```

Result: passed with existing Vite chunk-size warning only.

```powershell
py -m py_compile backend/application/project_basic_information_output.py backend/application/ltr_workbook_basic_information_sync_service.py backend/api/dependencies.py backend/api/main.py
```

Result: passed.

Package `git diff --check` passed with existing LF/CRLF warnings only. Trailing whitespace scan on the correction package returned no matches. Rejected-surface scan found no product/test references to `registered-row-preview`, `RegisteredLtrWorkbookRowPreview`, `previewRegisteredLtrWorkbookRow`, `LTR workbook row preview`, or `Update LTR from Basic Information`; remaining generic "workbook row preview" hits belong to older LTR write-preview code paths.

### Recommendation

Recommended next role: QA gate.

QA should smoke the Workbench / Basic Information side-card flow for: registered LTR + unconfirmed Basic Information preview enabled, `Confirm update` disabled for unconfirmed/draft preview, confirmed Basic Information preview/commit still works, no registered LTR remains blocked/disabled, and no second LTR preview button/card appears.
