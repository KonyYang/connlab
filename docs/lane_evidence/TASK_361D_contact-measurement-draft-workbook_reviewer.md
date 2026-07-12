# TASK_361D Contact Measurement Draft Workbook Reviewer Evidence

Status: reviewer_pass
Task: `TASK_361D_CONTACT_MEASUREMENT_DRAFT_WORKBOOK`
Lane: `contact-measurement-draft-workbook`
Date: 2026-07-12
Role: Reviewer

## Gate

Reviewer plan gate only. No product code, schema, workbook, API, client, or test
implementation was changed or authorized by this review.

Current phase: Phase 11, Project Workbench / Matrix / Approval Package controlled
foundation.
Current active task: `TASK_361D_CONTACT_MEASUREMENT_DRAFT_WORKBOOK`, planned-only.
Why allowed: TASK_361A/B/C are accepted, including TASK_361C local commit `5d754bb1`.
The board records TASK_361D as the current planned lane pending this gate.

## Review Findings

### Draft source and stale protection

The source contract is correctly narrow: preview and generation accept only the
project's current editable Measurement Plan revision and its persisted target/family
snapshots, review state, revision fingerprint, and Matrix binding. Confirmed Plan or
Confirmed Matrix fallback is prohibited. The fingerprint covers the output/layout
contract, source revision and binding, normalized projection/diagnostics, and visible
output label. Generation recomputes and returns typed stale `409` without writing
when any protected input changes.

### Status and authority labels

The `ready` versus structurally-valid `review_required` distinction is sound. Ready
output is labelled `DRAFT`; review-required output is labelled `NEEDS REVIEW`. Empty
or structurally blocked projections produce neither a fingerprint nor a workbook.
The label is required in the summary and every record sheet, and metadata explicitly
identifies the draft Plan and Matrix source. Draft artifacts remain review material,
never authority for Fee, formal specialized workbooks, generic Test Record, Report,
or Matrix.

### Artifact containment and lifecycle

The proposed separate app-owned root, strict project/artifact binding, fixed
filename, sidecar manifest, contained latest/download lookup, temporary write then
atomic publication, and manifest-backed retention are adequate. Cleanup occurs only
after a successful publication and may remove only validated owned artifact/manifest
pairs. Unknown files are preserved. The retention limit of ten is localized to the
new draft store and does not change TASK_360B's accepted confirmed-artifact behavior.

### Reuse and isolation

Sharing only a pure LLCR/CR row-expansion primitive and a code-owned `openpyxl` layout
primitive is an appropriate reuse boundary. Existing TASK_360B confirmed projection,
route/client/UI, fingerprint, artifact root/name, and Matrix compatibility row must
remain behaviorally unchanged and receive regression coverage. TASK_361E remains the
sole owner of Fee/formal specialized-workbook and other confirmed-consumer migration.

### UI and validation

The inline setup-workspace surface is appropriately distinct from the Matrix-only
TASK_360B compatibility row. Preview, Generate, and Download remain distinct actions;
blocked diagnostics, busy/focus recovery, restrained DRAFT/NEEDS REVIEW status, and
no modal-first flow are explicit. The planned projection, store, gateway, API,
frontend, confirmed-path regression, controlled temp-dir, build/static, and browser
smoke checks are proportionate.

## Scope and validation

The future May Touch list is exact enough for a separate draft projection/preview/
generation path, shared pure expansion/layout extraction, separate artifact store and
router, typed client, inline setup-workspace panel/model, scoped styles, and focused
tests. Schema, repository writes, lifecycle/classifier/command semantics, Matrix
confirmation/persistence, TASK_360B confirmed behavior, TASK_361E, generic Test
Record, parser/import, Fee, Basic Information, LTR/public-drive, StepInstance,
Report, real files, VBA/XLSM/COM, release/settings, `.agents/**`, and
`docs/project_management/**` remain locked.

## Validation Performed

- Re-read AGENTS, board, orchestration controls, TASK_361D task/plan/Planner evidence,
  accepted TASK_361A/B/C and TASK_360B workbook context, and current artifact/
  workbook patterns.
- Confirmed the board records TASK_361C accepted in local commit `5d754bb1` and
  TASK_361D as planned-only pending this review.
- Confirmed the Planner pass changed governance documentation only. Visible MCR/parser
  tests, TASK_360Q/R/S, and superpowers plan files are external residuals and excluded.
- Targeted documentation diff-check passed with only the known board LF/CRLF warning;
  UTF-8 trailing-whitespace scans found no matches.

## Decision

`reviewer_pass`

Recommended next role/action: explicit User approval, then Developer planning-first.
Do not route Developer implementation directly. A later implementation requires
source-of-truth reconciliation and a Reviewer implementation-readiness gate.

Blocking summary: none for the planned-only Reviewer plan gate.

---

# TASK_361D Reviewer Implementation-Readiness Gate

Status: reviewer_pass
Task: `TASK_361D_CONTACT_MEASUREMENT_DRAFT_WORKBOOK`
Lane: `contact-measurement-draft-workbook`
Date: 2026-07-12
Role: Reviewer

## Gate

Reviewer implementation-readiness gate only. Developer planning-first is docs-only;
no product code, schema, workbook, API, client, or test implementation was changed or
authorized by this review.

## Readiness Assessment

### Source, status, and stale contract

The implementation strategy is concrete: resolve only the current editable revision,
project persisted revision/target/family/impact snapshots into a canonical draft
projection, and classify it before any artifact reservation. `ready` produces
`DRAFT`; structurally valid `review_required` produces `NEEDS REVIEW`; `blocked` and
`empty` have no fingerprint and cannot write. Preview and generation share a versioned
canonical fingerprint serializer, and generation recomputes before any output to
reject changed revision, review, target/family, Matrix binding, or layout state as a
typed stale `409`.

### Draft artifact lifecycle

The separate app-owned draft root, strict filename and manifest binding, project plus
opaque artifact-id lookup, temporary-write/atomic-publication order, latest complete
manifest, retention of ten validated pairs, unknown-file preservation, and traversal/
containment tests give the implementation a safe, bounded artifact boundary. Latest
metadata remains draft-only and may not be displayed as a formal output.

### Reuse and consumer isolation

The exact shared boundary is a pure contact expansion primitive and code-owned
macro-free layout primitive only. TASK_360B continues using confirmed Matrix source,
route/client/UI, fingerprint, file naming, and artifact store without semantic change.
TASK_361E remains the exclusive future formal-consumer migration lane. The draft path
does not confirm a Plan or Matrix and cannot become Fee, generic Test Record, Report,
or Matrix authority.

### UI, tests, and file boundary

The inline setup-workspace panel and model have concrete typed preview/generate/
download, busy, stale/error, accessibility focus, and status-label requirements. The
exact May Touch list covers draft projection/preview/generation, pure extraction,
draft gateway/store/router, typed client, named frontend panel/model/styles, and
focused tests. The temp SQLite/temp-dir/API/UI/confirmed-regression/browser plan is
proportionate and includes no-real-file mutation checks.

## Source-Of-Truth

The board now records TASK_361D as ready for Reviewer implementation-readiness and
implementation unauthorized. Planner reconciliation supersedes the stale wording in
the earlier Developer evidence. No further reconciliation is needed for this gate;
explicit user implementation approval remains required before Developer coding.

## Validation Performed

- Re-read AGENTS, board, TASK_361D task/updated plan/Planner and Developer evidence,
  prior Reviewer plan evidence, accepted TASK_361A/B/C and TASK_360B context, and
  current workbook/artifact patterns.
- Confirmed planning-first is docs-only; visible parser/test and TASK_360Q/R/S/
  superpowers residuals are external and excluded.
- Verified the source/status/fingerprint, label/no-output, artifact containment/
  retention/latest/download, TASK_360B, TASK_361E, UX, exact-file, and validation
  contracts.
- Documentation diff-check is clean apart from the existing board LF/CRLF working-copy
  warning; UTF-8 trailing-whitespace scan found no matches.

## Decision

`reviewer_pass`

Recommended next role/action: explicit User approval and Planner/Integrator
source-of-truth confirmation, then Developer implementation. Do not route Developer
implementation from this gate alone.

Blocking summary: no implementation-design blocker; explicit user implementation
approval remains required.

---

# TASK_361D Reviewer Implementation Gate

Status: reviewer_blocked
Task: `TASK_361D_CONTACT_MEASUREMENT_DRAFT_WORKBOOK`
Lane: `contact-measurement-draft-workbook`
Date: 2026-07-12
Role: Reviewer

## Gate

Reviewer implementation gate only. No product code was changed by this review.

## Findings

### B1 - Artifact cleanup is not restricted to validated owned manifest pairs

`DraftMeasurementPlanWorkbookArtifactStore._cleanup()` treats every non-`latest.json`
JSON file with a same-stem `.xlsx` sibling as an owned pair and deletes it after the
retention threshold. It does not validate the strict generated filename, manifest
version, artifact id, project binding, filename equality, or containment before
deletion. An operator-created or unrelated `*.json` plus `*.xlsx` pair in the managed
project directory can therefore be deleted, contrary to the task's unknown-file-safe
cleanup contract. In addition, a cleanup exception propagates after publication;
generation then deletes the newly published pair while leaving the latest pointer
potentially stale. The plan requires cleanup failure to be a warning, not a failed
publication.

Smallest fix: create one strict owned-pair validator used by resolve/latest/cleanup,
and only retain/delete pairs that pass filename, manifest, artifact-id, project, and
containment checks. Preserve unknown or malformed pairs. Make post-publication cleanup
best-effort with a returned warning, retaining a valid newly published artifact and a
valid latest pointer. Add temp-dir regressions for an unknown `.json/.xlsx` pair,
malformed/forged manifest, cleanup failure after publish, latest consistency, and
retention of exactly ten valid owned pairs.

### B2 - Draft workbook does not implement the promised fixed layout and metadata contract

The draft gateway imports only the confirmed layout constant, then reimplements a
reduced writer. It omits the accepted Group-Step block details, guarded statistics
formulas, column widths, and shared layout primitive. It also leaves a record sheet
blank when that type has no section, so not every record sheet visibly carries the
required `DRAFT` or `NEEDS REVIEW` label. Summary/manifest metadata omit required
source Matrix id, Plan revision fingerprint, Matrix binding fingerprint, generated UTC
time in the workbook, layout version, and review diagnostics/count. This allows the
draft output to drift from the fixed TASK_360B record structure and fails the explicit
draft-identification/traceability contract.

Smallest fix: extract and reuse a code-owned layout primitive that emits the same fixed
sheets, Group-Step blocks, columns, guarded formulas, and widths for both paths while
keeping TASK_360B's current label and metadata unchanged. Pass complete draft metadata
to the gateway/manifest, write the DRAFT or NEEDS REVIEW banner on all record sheets,
and add workbook/manifest tests for every required metadata field, formulas, blank-type
sheet banner, macro-free output, and unchanged TASK_360B regression.

## Passed Review Areas

- Preview service enforces requested revision equality with the current editable
  revision. Projection reads the workspace boundary only, has no confirmed fallback,
  and classifies ready/review-required/blocked/empty before generation.
- Generation recomputes before preparing an artifact and rejects a mismatched preview
  fingerprint without writing. The new route/client/UI path is typed and separate from
  the TASK_360B confirmed route and Matrix compatibility row.
- Candidate scope remains within TASK_361D paths. No schema, repository/lifecycle,
  Matrix confirmation, Fee, TASK_361E, generic Test Record, parser, LTR/public-drive,
  VBA/COM, or other locked product scope change was found.

## Validation Performed

- Re-read board, TASK_361D task/plan/evidence/reconciliation, actual candidate code,
  focused tests, current TASK_360B gateway/layout, and candidate status/diff.
- `py -m pytest` focused draft projection/artifact/gateway/generation/workspace/API
  suite passed: `11 passed`.
- `npm test -- DraftMeasurementPlanWorkbookPanel ContactMeasurementSetupWorkspace
  useContactMeasurementPlanModel contactMeasurementPlanSelectors
  MatrixEditorWorkspace ContactMeasurementPlanSummaryCard --run` passed:
  `7 files / 61 tests`.
- Python compile and `npm run build` passed; build has only the existing Vite
  chunk-size warning. Candidate files remain below the hard limit. `git diff --check`
  and UTF-8 trailing scans are clean apart from known LF/CRLF working-copy warnings.
  External parser/test and TASK_360Q/R/S residuals remain excluded.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer fix pass for B1 and B2 only. Do not route QA
or Integrator until the artifact ownership/cleanup and layout/metadata re-gate passes.

Blocking summary: B1 unsafe artifact-pair cleanup and post-publication cleanup error
handling; B2 incomplete shared fixed layout and draft metadata/label contract.

---

# TASK_361D Reviewer Implementation Re-Gate - B1/B2 Review

Status: reviewer_blocked
Task: `TASK_361D_CONTACT_MEASUREMENT_DRAFT_WORKBOOK`
Lane: `contact-measurement-draft-workbook`
Date: 2026-07-12
Role: Reviewer

## B1 Review - Ownership validation closed, cleanup observability still missing

The strict owned-pair validator now correctly protects cleanup/resolve/latest from
forged same-stem pairs. It checks the owned filename/id, manifest version, artifact
id, project binding, manifest filename, and contained directory. The new artifact and
latest pointer survive an `OSError` from retention cleanup, which closes the unsafe
deletion/publication half of B1.

However, `publish()` catches the cleanup `OSError` and silently executes `pass`.
Neither its returned metadata, the generation result, typed API response, nor inline
UI can show the planned concise warning that publication succeeded but old-pair
cleanup could not complete. This is an unreported degraded state, contrary to the
artifact lifecycle contract and error-handling rules.

Smallest fix: preserve the successful artifact/latest behavior, but return a concise
cleanup warning through generation result and typed API/client/UI state. Add a focused
regression proving a cleanup failure keeps the artifact/latest valid and exposes the
warning without turning the generate request into failure.

## B2 Review - summary metadata rows still overwrite one another

The shared `llcr_cr_record_workbook_layout.py` now correctly owns Group-Step blocks,
formulas, and widths; both confirmed and draft gateways call it. Draft record sheets
also receive banners even with no sections. This closes the shared record-layout part
of B2.

The draft summary writes eleven metadata values starting at row 3, then writes the
draft disclaimer at `A10` and section rows starting at row 12. Those later writes
overwrite the `Layout version` label at row 10 and the `Generated UTC`/`Generated
rows` metadata at rows 12 and 13 whenever a section exists. Thus the workbook does
not reliably contain the required complete source/review/layout/generation metadata,
despite the manifest carrying it.

Smallest fix: reserve a non-overlapping summary metadata region, move the disclaimer
and section table below it, and add exact workbook-cell regressions for all required
metadata fields in a multi-section output. Include the open-review impact count rather
than only the number of structural diagnostics when exposing review count.

## Validation Performed

- Re-read B1/B2 code and tests: artifact store, shared layout, draft and confirmed
  gateways, generation service, API boundary, and Developer evidence.
- Re-ran focused draft/confirmed gateway/generation/API suite: `16 passed`.
- Re-ran frontend suite: `7 files / 61 tests passed`.
- Re-ran `npm run build`: passed with the existing Vite chunk-size warning only.
  Existing compile, diff, line-count, trailing-whitespace, and locked-scope checks
  remain clean apart from known LF/CRLF warnings and excluded external residuals.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer fix pass for B1 cleanup-warning propagation
and B2 non-overlapping summary metadata only. Do not route QA or Integrator yet.

Blocking summary: silent post-publication cleanup degradation and overwritten draft
summary metadata rows.

---

# TASK_361D Reviewer Implementation Re-Gate - Warning/Summary Follow-Up

Status: reviewer_blocked
Task: `TASK_361D_CONTACT_MEASUREMENT_DRAFT_WORKBOOK`
Lane: `contact-measurement-draft-workbook`
Date: 2026-07-12
Role: Reviewer

## B1/B2 Closure

The non-fatal cleanup warning now propagates from artifact store through generation
result, typed API response, client DTO, and the inline panel while preserving the
published artifact and latest pointer. The strict owned-pair validation remains in
place. Draft summary metadata now occupies rows 3 through 13, the disclaimer is at
row 15, and the section table starts at row 18, so the required cells no longer
overlap. Both draft and confirmed gateways use the shared fixed record layout, and
both record sheets receive the draft/review banner.

## Finding

### B3 - Draft workbook workflow logic remains inside a presentational panel

The task and approved plan explicitly reserve
`useDraftMeasurementPlanWorkbookModel.ts` plus its focused test as the feature model
that owns preview, latest artifact, generate, busy, stale/error, and download state.
That file is absent. `DraftMeasurementPlanWorkbookPanel.tsx` instead imports the API
client, owns several `useState` values, performs `useEffect` fetches, and implements
both asynchronous preview/generate workflows directly. This violates the project
frontend architecture boundary and leaves a reusable operational panel coupled to
transport/workflow decisions.

Smallest fix: add the planned `useDraftMeasurementPlanWorkbookModel` hook and focused
test, moving the API calls, preview/artifact/busy/error/warning lifecycle, stale
recovery, and latest reload into it. Keep the panel declarative, rendering model state
and forwarding explicit callbacks only. Preserve the current typed client calls,
cleanup-warning visibility, busy lock, and download behavior; do not change backend,
authority, TASK_360B, or TASK_361E scope.

## Validation Performed

- Re-read the artifact store, shared layout, draft/confirmed gateways, generation/API
warning path, inline panel, exact task/plan file boundary, and focused tests.
- Re-ran isolated-temp draft/confirmed projection/artifact/gateway/generation/API
suite: `17 passed`.
- Re-ran frontend suite: `7 files / 62 tests passed`.
- Re-ran `npm run build`: passed with the existing Vite chunk-size warning only.
  Existing diff/trailing/line/scope checks remain clean apart from known LF/CRLF
  warnings and excluded external residuals.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer fix pass for B3 frontend model extraction
only. Do not route QA or Integrator until the planned feature boundary is restored.

Blocking summary: the draft workbook panel directly owns API/workflow state instead
of the required feature model.

---

# TASK_361D Reviewer Implementation Re-Gate - B3 Closure

Status: reviewer_pass
Task: `TASK_361D_CONTACT_MEASUREMENT_DRAFT_WORKBOOK`
Lane: `contact-measurement-draft-workbook`
Date: 2026-07-12
Role: Reviewer

## B3 Closure

`useDraftMeasurementPlanWorkbookModel` now owns typed latest-artifact loading,
preview, generation, busy, error, stale feedback, artifact, and cleanup-warning
state. `DraftMeasurementPlanWorkbookPanel` imports only the hook, renders model state,
and forwards explicit preview/generate callbacks. It no longer imports API helpers or
implements asynchronous workflow logic. Download remains a declarative contained
artifact URL supplied by the model's artifact state, so no panel-level transport or
workflow state was reintroduced.

## Regression and Scope Review

- B1 remains closed: strict owned manifest-pair validation protects resolve/latest/
  cleanup, and a non-fatal cleanup warning is visible through generation/API/client/
  UI without invalidating the published artifact or latest pointer.
- B2 remains closed: summary metadata, disclaimer, and section table have disjoint
  rows; draft and confirmed gateways share the fixed record layout; draft/review
  banners appear on both record sheets.
- No authority, schema, repository/lifecycle/command, Matrix confirmation, TASK_360B
  API/compatibility, TASK_361E consumer migration, Fee, generic Test Record, parser,
  LTR/public-drive, StepInstance/Report, or other locked scope changed.

## Validation Performed

- Re-read the B3 hook/panel/tests, the cleanup-warning and shared-layout paths, task
  boundary, frontend architecture rules, and locked-path status.
- Isolated-temp draft/confirmed projection/artifact/gateway/generation/API suite
  passed: `17 passed`.
- `npm test -- useDraftMeasurementPlanWorkbookModel
  DraftMeasurementPlanWorkbookPanel ContactMeasurementSetupWorkspace
  useContactMeasurementPlanModel contactMeasurementPlanSelectors
  MatrixEditorWorkspace ContactMeasurementPlanSummaryCard --run` passed:
  `8 files / 63 tests`.
- `py -m py_compile` passed. `npm run build` passed with the existing Vite chunk-size
  warning only. `git diff --check`, UTF-8 trailing-whitespace, line-count, and
  locked-scope scans are clean apart from known LF/CRLF working-copy warnings.

## Decision

`reviewer_pass`

Recommended next role/action: QA gate using a controlled editable Matrix-authority
fixture. QA should smoke ready and needs-review draft output, stale rejection, empty/
blocked no-output, generated artifact download and cleanup warning, draft labels/
metadata, TASK_360B confirmed isolation, keyboard/busy states, and no real file or
public-drive mutation.

Blocking summary: none for the Reviewer implementation re-gate. Controlled browser
and temp-artifact smoke remain the QA validation.
