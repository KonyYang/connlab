# TASK_367A Matrix Editor Live XLSX Export Reviewer Evidence

Date: 2026-07-26
Role: Reviewer
Status: `reviewer_implementation_re_gate_pass`
Task: `TASK_367A_MATRIX_EDITOR_LIVE_XLSX_EXPORT`
Lane: `matrix-editor-live-xlsx-export`
Gate: implementation re-gate
Implementation authorization: yes; implementation completed and reviewed

## Findings

No blocking implementation finding remains.

The committed implementation range passed Reviewer re-gate after the bounded
formula-literalization fix. The reviewed clean commit is ready for downstream
packaging/readiness reconciliation. Remote push remains unauthorized.

## Historical Readiness Board And Git State

- Current phase is Phase 11.
- The board names TASK_367A as the current planned-only task and routes only
  this Reviewer implementation-readiness gate.
- `HEAD` is `033e530c2d6a9c01c210f35b938678672b6449ad`.
- The primary worktree contains only TASK_367A planning governance changes.
- The index is empty.
- `git worktree list` contains only the primary `master` worktree. No
  implementation worktree or duplicate TASK_367A branch exists.

## Contract Review

### Live snapshot and zero-write

- The current workspace owns `editableRows`, `groupColumns`, `sampleValues`,
  and `scheduleCalculation`, so one synchronous click-time projection can
  capture unsaved state without waiting for autosave.
- No Confirm Matrix, draft generation, saved signature, revision, or CAS token
  is required for this read-only derived output.
- The proposed API -> application service -> infrastructure workbook gateway
  layering keeps React and the route away from openpyxl and keeps the gateway
  away from Matrix persistence.
- A fresh `BytesIO` workbook and byte response can satisfy the no-DB,
  no-project-file, no-template, and no-output-registration contract.

### Selected Groups and row scope

- Current Test Record projection already filters Groups with
  `group.isSelected`; `showSelectedGroupsOnly` is presentation-only.
- Existing step-format and sequence validation iterates selected Groups only.
  Reusing its boolean gate, then checking nonblank selected-Group cells, does
  not require a second step parser.
- Excluding sample rows and rows with no selected-Group step is explicit and
  testable. Unchecked Group content cannot create an exported row.
- Dynamic Group columns in current order are consistent with the one-Group
  reference workbook; the observed `1` header is the reference example, not a
  literal header for every export.

### Time, sample, Fee, and workbook structure

- `formatPlanningDays()` is the actual page formatter and the workspace
  renders `${formatPlanningDays(groupDays[id] ?? 0)} d`.
- Sending that exact string makes `0 d`, integers, and trimmed two-decimal
  values stable and prevents a backend Day parser or recalculation.
- Current sample expressions can map directly to `Sample size`; blank remains
  blank.
- The one-sheet layout, fixed A:E fields, dynamic Group columns, final Notes
  column, and trailing `Sample size`, `Time`, `Fee` rows are implementable.
- Requiring every non-label Fee cell to reload as `None` is a strong,
  verifiable blank-value contract.
- Styles, dimensions, formula/link/macro absence, and in-memory reload checks
  adequately replace any runtime dependency on the external workbook.

### Download and UI

- `requestBlobResponse()` already parses `Content-Disposition` and returns
  Blob plus filename. Exact client reuse is feasible without direct fetch in
  the feature.
- A bounded hook can own busy, error, retry, object URL creation, click, and
  revoke; the button component can remain a standard accessible command.
- The existing action container wraps, but the source label and three actions
  still require the declared desktop and 514 px browser gate. The optional
  <=20-line exact CSS hunk is sufficiently narrow.
- The action remains operational rather than decorative and follows the
  existing Matrix target-action vocabulary.

## Scope And Maintainability

- Exact May Touch separates projection, hook, button, route, composition,
  application validation, and workbook writing.
- `backend/api/dependencies.py`, desktop/native Save As, Matrix authority,
  Test Record product paths, schema/database, Settings, Fee, project outputs,
  and real files remain locked.
- The 4093-line workspace, 4600-line client, 9455-line CSS, and 208-line
  `backend/api/main.py` are exact-hunk surfaces only.
- New production and test modules have explicit bounded budgets. The
  1934-line workspace test remains read-only.
- The planned branch `lane/task-367a-matrix-editor-live-xlsx-export` and
  sibling worktree are concrete and no shared product-path owner is active.

## Implementation-Readiness Closure

Developer planning-first and Planner reconciliation close all five details
required by the earlier plan gate:

1. The request is an ordered rectangular DTO with exact nested fields. It
   caps Groups at 64, qualifying rows at 512, total Group cells at 16,384,
   and every string field explicitly. Invalid, oversized, duplicate,
   reordered, nonrectangular, or zero-row requests return typed 422 before
   gateway invocation and produce zero bytes.
2. Exact filename input and sanitization. The read-only
   `deriveProjectReference()` precedence is latest LTR, `project_no`, then
   `TMP-<8 uppercase project-id characters>`. Backend sanitization covers
   invalid Windows characters, reserved device names, trailing spaces or
   periods, a 120-code-point segment limit, and deterministic `Project`
   fallback.
3. Disabled-reason priority is lifecycle message, busy, no checked Group,
   selected-Group step error, then no qualifying row. Lifecycle read-only
   dispatches no request. Autosave, saved draft, generation, signature, and
   CAS state are excluded from enablement.
4. The current primary worktree contains only TASK_367A governance, the
   index is empty, and no implementation worktree exists. After this pass,
   explicit User approval and a controlled local governance checkpoint are
   still required; only a clean primary/index may precede Orchestrator
   creation or reuse of the recorded lane worktree.
5. The future Developer handoff is a clean lane checkpoint; Reviewer reviews
   base..lane HEAD, QA validates that reviewed clean commit, and Integrator
   accepts only the exact whitelist and records residual ownership.

These are frozen readiness constraints, not implementation authorization.

## Independent Readiness Verification

- `deriveProjectReference()` is a public existing helper and implements the
  frozen latest-LTR / project-number / temporary-project precedence.
- `formatPlanningDays()` is the current page formatter, and the workspace
  displays its exact result with the ` d` suffix.
- The current selected-Group step validation excludes unchecked Groups and
  exposes the existing detailed step error used by the frozen availability
  contract.
- The API client already owns Blob response parsing and UTF-8
  `Content-Disposition` filename handling; the new exact client wrapper can
  reuse it without feature-level direct fetch.
- The ordered DTO, pre-gateway validation, filename clock, bounded modules,
  six bounded test modules, read-only oversized regressions, desktop/514 px
  browser checks, rollback, May Touch, and locked paths are concrete and
  internally consistent.
- The workbook contract preserves click-time React values, selected Group
  order, qualifying non-sample rows, page-exact Time text, truly blank Fee
  cells, one-sheet in-memory output, runtime template independence, and the
  zero-write boundary.

## Validation Assessment

The proposed test matrix is adequate:

- pure projection tests for selected order, unsaved values, row filtering,
  exact Time text, samples, and blank Fee;
- service/gateway/API tests for bounds, identities, styles, workbook bytes,
  no formulas/links/macros, and zero writes;
- hook/button tests for one request, busy/error/retry, filename, download, and
  Blob revoke;
- read-only Matrix Editor/Test Record regressions, frontend build, pycompile,
  line/diff/whitelist/no-real-data checks;
- controlled desktop and 514 px browser validation with keyboard, overlap,
  overflow, console, download, and no-save/no-confirm assertions.

## Historical Readiness Route

The next legal role at that historical gate was:

`User explicit product/test implementation approval, followed by Planner
final source-of-truth reconciliation`

Developer implementation, QA, Integrator, and worktree creation were not
authorized by that historical readiness gate.

## Historical Plan-Gate Note

After the historical Reviewer plan gate, the User explicitly approved
Developer docs-only planning-first. That approval does not authorize
product/test implementation. That historical route is superseded by the
implementation re-gate pass recorded below.

## Implementation Gate Evidence Reconciliation

### Reviewed Range

- Base: `405c0c80ed93756080099b378d490ae875f7e8a6`.
- Initial implementation checkpoint:
  `cf37816e37ee727083b11f04a22f645015bd0adc`.
- Reviewed implementation HEAD:
  `fb2b91c8a49a7b03d1afc07c519f4d156c12ba42`.
- Exact base-to-reviewed-HEAD package: 17 TASK_367A whitelist paths,
  1,091 insertions and 3 deletions.
- The lane worktree and index were clean at the final review checkpoint.

### Implementation Review

- The frontend projects one click-time snapshot from current editable rows,
  checked Groups, sample expressions, and page-formatted Time strings.
- Only non-sample rows with at least one nonblank step in a checked Group are
  exported. Unchecked Groups and view-only filtering do not affect export
  authority.
- The ordered rectangular DTO, identity checks, 64-Group, 512-row,
  16,384-cell, and per-field limits are enforced before gateway invocation.
  Invalid requests return typed 422 and produce no workbook.
- The backend renders one in-memory workbook with the frozen Sheet layout,
  dynamic Group columns, exact Sample size and Time text, and truly blank Fee
  cells. It does not use a runtime template or write Matrix, project, file,
  database, output, autosave, Confirm, or CAS state.
- Project-reference precedence, Windows-safe filename handling, lifecycle and
  disabled-reason priority, Blob download behavior, retry state, line
  budgets, exact-hunk ownership, and locked paths match the approved task.

### Blocking Finding And Closure

The initial checkpoint was blocked because openpyxl interpreted editable
strings beginning with `=` as formulas, including a HYPERLINK-shaped Group
label. That violated the frozen no-formulas/no-links contract.

Commit `fb2b91c8a49a7b03d1afc07c519f4d156c12ba42` closes the finding:

- all dynamic Group headers, row fields, step text, Sample size, and Time
  values are stored as literal strings;
- original visible text remains unchanged;
- reload confirms dynamic cells are not formula cells;
- no cell hyperlink, external link, or defined name is introduced;
- Fee non-label cells remain `None`;
- DTO, filtering, frontend behavior, and Matrix state are unchanged.

### Independent Reviewer Validation

- Fresh backend feature suite: 11 passed.
- Fresh frontend projection/hook/button suite at the initial checkpoint:
  5 passed; the bounded fix did not touch frontend paths.
- Backend feature modules passed `py_compile`.
- Base-to-reviewed-HEAD `git diff --check` and final commit check passed.
- All new Python, TypeScript, TSX, and test modules remain within their
  frozen blank-inclusive budgets; oversized existing files are exact-hunk
  surfaces only.
- Final lane worktree status and staged index were empty.

## Final Gate Result

`reviewer_implementation_re_gate_pass`

No blocking finding remains for TASK_367A. The reviewed implementation HEAD is
`fb2b91c8a49a7b03d1afc07c519f4d156c12ba42`.

## Current Route

Next and only legal role:

`Integrator packaging/readiness reconciliation`

Do not repeat QA, modify product/tests, merge, push, or start another lane from
this Reviewer evidence reconciliation.
