# TASK_367A Matrix Editor Live XLSX Export Developer Evidence

Date: 2026-07-26
Role: Developer
Status: `ready_for_review`
Current source-of-truth status: `complete_accepted_with_post_accept_correctives_pending_reviewer_docs_only_source_of_truth_re_gate`
Task: `TASK_367A_MATRIX_EDITOR_LIVE_XLSX_EXPORT`
Lane: `matrix-editor-live-xlsx-export`
Implementation authorization: User-authorized product/test implementation completed in lane

## Current Phase And Allowed Action

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Reviewer passed the plan gate and the User explicitly approved Developer docs-only
  planning-first.
- This pass is allowed only to inspect real boundaries and refine TASK_367A planning
  governance. It does not authorize product code, tests, an implementation worktree, staging,
  commit, push, QA, or integration.

## Read And Inspected

- `AGENTS.md`
- `docs/task_board.md`
- TASK_367A task, plan, Planner, Reviewer, and reconciliation evidence
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/project_management/TASK_REVIEW_CHECKLIST.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- project `impeccable` product/design context
- current Matrix Editor state, validation, action, schedule, and Test Record projection paths
- existing project identity helper, Blob client, Test Record route, FastAPI router composition,
  and openpyxl workbook gateway patterns

## Repository-Backed Findings

1. `MatrixEditorWorkspace.tsx` owns `editableRows`, `groupColumns`, `sampleValues`,
   `scheduleCalculation`, `hasStepTokenError`, `stepTokenErrorMessage`, and
   `lifecycleReadonlyView`.
2. Existing selected-Group validation skips sample rows, parses only selected Group cells, and
   rejects malformed/duplicate/gapped step sequences. Export can reuse that boolean/message gate
   and only needs a nonblank selected-cell check after it passes.
3. `showSelectedGroupsOnly` changes visible Groups/rows only. `group.isSelected` is the export
   authority.
4. The page renders Time as
   ```${formatPlanningDays(scheduleCalculation.groupDays[group.id] ?? 0)} d``` and current
   sample values as `sampleValues[group.id] ?? ""`.
5. `deriveProjectReference()` is already public and implements latest LTR, `project_no`, then
   `TMP-<first 8 uppercase>`; the file remains read-only.
6. `requestBlobResponse()` already returns `{blob, fileName}` and prefers RFC 5987
   `filename*`. No feature-level `fetch` or native Save As is needed.
7. Existing Test Record generation writes a file and uses external resources; it is a behavioral
   reference only. TASK_367A instead needs a new in-memory application/gateway boundary with no
   Settings, template, database, output record, or filesystem dependency.
8. `backend/api/main.py` is 208 lines and can accept only the exact import/include hunk while
   remaining below the Python hard limit. `backend/api/dependencies.py` remains excluded.
9. Existing target actions use a wrapping flex container and native buttons. A third adjacent
   command is feasible, with an optional narrow <=20-line CSS hunk only if the controlled 514 px
   smoke proves it necessary.

## Frozen Implementation Contract

The refined plan freezes every mandatory readiness detail:

- endpoint `POST /api/projects/{project_id}/matrix-editor/live-xlsx-export`;
- exact nested request DTO for source, project reference, ordered Groups, ordered rows, and
  ordered per-Group cells;
- caps: 64 Groups, 512 qualifying rows, 16,384 Group cells, and explicit limits for every string
  family;
- complete pre-gateway validation, typed `422`, and zero gateway calls/bytes for oversized,
  empty, nonqualifying, duplicate, or nonrectangular input;
- frontend use of read-only `deriveProjectReference()` and backend-owned deterministic
  Windows-safe filename sanitization;
- exact filename `<safe reference> Matrix Draft <local YYYYMMDDHHmmss>.xlsx`;
- disabled-reason priority: lifecycle message, busy, no Group, existing step error, no
  qualifying row;
- lifecycle-readonly no-request behavior and deliberate exclusion of autosave/CAS from
  availability;
- raw in-memory XLSX response with UTF-8 `Content-Disposition`;
- exact bounded RED/GREEN nodes, line budgets, rollback, package isolation, browser/build/XLSX
  content, and zero-write gates.

## Exact Future May Touch

No future scope was expanded beyond the task/plan:

- exact wiring hunks in `MatrixEditorWorkspace.tsx`, `client.ts`, `main.py`, and optional CSS;
- three new bounded frontend product modules;
- four new bounded backend product modules;
- six new bounded test modules;
- TASK_367A governance.

`projectIdentity.ts`, the 1934-line workspace test, Matrix persistence/session/Confirm paths,
Test Record product paths, database/schema, Settings, desktop/native bridges, and all external
residuals remain locked.

## Physical-Line And Hash Baseline

Counts include blank lines and were measured with
`(Get-Content <path> -Encoding UTF8).Count`.

| Path | Lines | SHA-256 |
|---|---:|---|
| `MatrixEditorWorkspace.tsx` | 4093 | `EE4E762F6C6D38449404EE3449BBF54F047C2A820F06532D1073F88495C3A503` |
| `client.ts` | 4600 | `A1DD8AD0C7BB1BD6C8C729DB3E64E99064FEA22BEE8FA0637E7C832C860A9BF8` |
| `workbench.css` | 9455 | `C0E31B7A23FF79040E2DCBBEE4129F728325F814A50176D7149F64067DC56A65` |
| `projectIdentity.ts` | 58 | `40AFB979135A6E0E85015C089E020A893FF04DB2460EEDE2190D97446528B36C` |
| `backend/api/main.py` | 208 | `0EFE4A34F641736C90CECE348AE09FB05225C88C05A381893964899FAB76D21B` |
| `MatrixEditorWorkspace.test.tsx` | 1934 | `3016492934D2185D56C5AEC9DC79D2CA3FEF63E657FAC8F229330C4278556883` |

Oversized files are exact-hunk/read-only surfaces as declared. Every new Python module remains
below 500 lines and within its tighter plan budget.

## Worktree And Package Isolation

- Planning occurred in primary `master`; no TASK_367A branch or worktree was created.
- The implementation sequence remains:
  Planner reconciliation -> Reviewer readiness -> explicit User implementation approval ->
  controlled local docs-only governance checkpoint -> clean primary/index verification ->
  Orchestrator-created/reused lane worktree.
- Future branch: `lane/task-367a-matrix-editor-live-xlsx-export`.
- Future sibling worktree:
  `D:\PythonProject\connlab-task-367a-matrix-editor-live-xlsx-export`.
- Mixed oversized files must be hunk-staged only in the future lane checkpoint. No whole-file
  staging is permitted.

## Validation And Stop

Recorded checks:

- `git diff --check`: passed; only the pre-existing LF/CRLF notice for
  `docs/task_board.md` was printed.
- `git diff --no-index -- NUL <new planning document>` for the plan and Developer evidence:
  expected add-file exit `1`; no whitespace error.
- explicit UTF-8 trailing-whitespace scan for the plan and Developer evidence: clean.
- `git diff --cached --name-only`: empty.
- `git worktree list --porcelain`: only primary
  `D:/PythonProject/connlab` at
  `033e530c2d6a9c01c210f35b938678672b6449ad`; no lane branch/worktree.
- `git status --short --branch`: only the existing TASK_367A board/governance package plus this
  Developer evidence; no product or test path.
- implementation readiness scan: exact DTO/caps, typed zero-byte `422`, project-reference
  precedence, Windows filename sanitization, disabled-reason ordering, lifecycle no-request,
  test nodes, line budgets, rollback, and package isolation are all explicit.

No implementation tests or generated-artifact commands are run during planning-first.

Historical planning-first route (completed): Planner source-of-truth reconciliation, followed by
Reviewer implementation-readiness. Product/test implementation was unauthorized at that
checkpoint and was authorized later.

## Authorized Implementation Pass

The Orchestrator delegation superseded the historical planning-only stop point after the
controlled governance checkpoint `405c0c80ed93756080099b378d490ae875f7e8a6`.

- Worktree: `C:\Users\White\.codex\worktrees\705b\connlab`
- Branch: `lane/task-367a-matrix-editor-live-xlsx-export`
- Base/HEAD before implementation: `405c0c80ed93756080099b378d490ae875f7e8a6`
- Isolation at start: clean branch/index; primary worktree not edited
- Stage/commit/push: intentionally not performed per delegation

### Changed Product Paths

- `backend/api/main.py`, exact router import/include
- `backend/api/dependencies_matrix_editor_live_xlsx_export.py`
- `backend/api/routes_matrix_editor_live_xlsx_export.py`
- `backend/application/matrix_editor_live_xlsx_export_service.py`
- `backend/infrastructure/office/matrix_editor_live_xlsx_workbook_gateway.py`
- `frontend/src/api/client.ts`, exact DTO/download wrapper
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, exact live-state wiring
- `frontend/src/features/matrix-editor/matrixEditorXlsxExportProjection.ts`
- `frontend/src/features/matrix-editor/useMatrixEditorXlsxExport.ts`
- `frontend/src/features/matrix-editor/MatrixEditorXlsxExportButton.tsx`

No CSS change was needed. Existing wrapping action layout passed the controlled 514 px gate.
`projectIdentity.ts`, `MatrixEditorWorkspace.test.tsx`, persistence, Confirm Matrix, autosave,
CAS, Test Record product code, Settings, desktop/native paths, schema/database, output
registration, and external workbook paths remain unchanged.

### Changed Test Paths

- `tests/unit/test_matrix_editor_live_xlsx_export_service.py`
- `tests/unit/test_matrix_editor_live_xlsx_workbook_gateway.py`
- `tests/integration/test_matrix_editor_live_xlsx_export_api.py`
- `frontend/src/features/matrix-editor/matrixEditorXlsxExportProjection.test.ts`
- `frontend/src/features/matrix-editor/useMatrixEditorXlsxExport.test.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorXlsxExportButton.test.tsx`

### TDD Evidence

Backend RED failed at collection because the service/gateway modules did not exist. Backend
GREEN passed `10` focused tests. Frontend RED first failed because Vitest dependencies were not
available in this isolated worktree; after locked dependency installation, the new modules
were exercised and GREEN passed `5` focused tests. A read-only workspace regression initially
exposed an old complete-module mock that lacked the new API export; production hook dependency
resolution was deferred until click without editing the locked oversized test, then the exact
workspace/new-feature gate passed `49/49`.

### Fresh Validation

- backend feature plus Matrix session/Test Record regressions: `24 passed`
- exact new backend modules plus `backend/api/main.py`: `py_compile` passed
- focused frontend workspace/new feature: `4 files / 49 tests` passed
- full frontend suite: exit `0`
- frontend `tsc -b && vite build`: passed; existing >500 kB chunk warning only
- browser smoke at `1280x720`: actions width `279.109375`, page horizontal overflow `false`
- browser smoke at `514x760`: actions left/right `181.890625/461`, page horizontal overflow
  `false`; Import Matrix, historical pre-corrective `导出 Matrix`, and Test record remained
  adjacent and enabled
- browser DOM: one uniquely named historical pre-corrective `导出 Matrix` native button;
  keyboard focus reached it;
  console error/warning log remained empty during the controlled layout smoke
- `git diff --check`: passed; only existing LF/CRLF notices on tracked exact-hunk surfaces
- new production/test line budgets: all passed (`13..165` production, `15..95` tests)
- forbidden runtime reference/save/confirm/direct-fetch scan on new bounded modules: no match

### Developer Self-Review

- Frontend calls only the typed API client; openpyxl remains behind the infrastructure gateway.
- Application validation completes before `gateway.render()`.
- Empty/oversized/nonqualifying/duplicate/nonrectangular requests return typed `422`; no
  workbook bytes exist before validation succeeds.
- The workbook is created in `BytesIO`, uses no external template, and has true blank Fee cells.
- Time remains the page-generated display string; backend does not parse or recompute it.
- Availability priority is lifecycle, busy, no Group, existing step error, no qualifying row.
- No autosave/CAS/save/confirm state participates in export availability.
- No TODO, hard-coded operator path, direct filesystem write, database access, or hidden
  exception was introduced.

Next legal role: Reviewer implementation gate. QA and Integrator are not routed from this
Developer stop point.

## Reviewer Blocking Fix Pass: Formula Literalization

Reviewer found that openpyxl interpreted user-editable values beginning with `=` as formulas.
The bounded fix changes only the existing XLSX gateway and its existing unit test:

- dynamic Group headers, row fields, step cells, Sample size, and Time strings are explicitly
  serialized with Excel string data type;
- their original visible text is unchanged and no apostrophe is added;
- `None` values and every non-label Fee cell remain true blanks;
- fixed workbook labels and all frontend/DTO/projection behavior remain unchanged.

TDD evidence:

- RED: the new formula-shaped input test failed because reloaded cells had `data_type == "f"`;
- GREEN: gateway test `2 passed`;
- regression: backend feature plus Matrix session/Test Record gates `25 passed`;
- frontend exact workspace/new-feature gate `49 passed`;
- exact backend `py_compile` passed;
- frontend TypeScript/Vite build passed with only the existing chunk-size warning.

This fix pass is prepared for a second clean local lane checkpoint. No push, primary edit,
QA routing, or Integrator routing is authorized.

## Post-Accept Source Of Truth

The role status and browser wording above record the historical Developer gate. Current accepted
behavior is:

- accepted lane HEAD `53840b42ea73358c31fe40c5225646363d485829`;
- post-accept commit `f0880310f786ac98ad0f8437db02fc22cca93f08` changes the idle title to
  `Export Matrix`, superseding the historical Chinese title;
- post-accept commit `1c9f8fc58ca72d21e020576d5aa611a307c335c3` removes fixed row height
  `15`, retains wrapped cells, and leaves row heights unset for automatic fitting;
- current primary/master HEAD is
  `1c9f8fc58ca72d21e020576d5aa611a307c335c3`;
- no further Developer action is routed by this docs-only reconciliation.
