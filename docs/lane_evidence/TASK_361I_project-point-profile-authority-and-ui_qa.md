# TASK_361I Project Point Profile Authority And UI QA Evidence

Date: 2026-07-14
Role: QA / Smoke Owner
Task: `TASK_361I_PROJECT_POINT_PROFILE_AUTHORITY_AND_UI`
Lane: `project-point-profile-authority-and-ui`
Result: `qa_pass`

## Phase And Boundary

- Phase 11, controlled Matrix foundation. The board records TASK_361I as the
  active authorized lane; Reviewer B1R3 final re-gate is `reviewer_pass`.
- QA made no product, test, task-board, staging, commit, or push change. This
  evidence and its screenshot artifacts are the only non-temporary QA outputs.
- All browser/API writes used only
  `tmp/task_361i_qa_browser/20260714T084100Z/authority.sqlite3`, synthetic
  project `P1` / `DL-QA-361I-P1`, and temporary data/project/template roots.
  The temporary backend used `127.0.0.1:8014`; its Vite proxy used `5179`.
- No request opened `data/connlab.sqlite3`, a real workbook/folder/LTR/public-drive
  path, or any generation/download/Cancel/project-delete/Fee/Generic output route.
  Point Profile draft save/confirm and one intentionally stale PUT were allowed only
  against the disposable database.

## Automated Validation

Passed:

```text
py -m pytest -p no:cacheprovider --basetemp=tmp\task_361i_qa_pytest \
  tests\unit\test_contact_point_profile_fingerprint.py \
  tests\unit\test_contact_point_profile_legacy_suggestion.py \
  tests\unit\test_contact_point_profile_schema.py \
  tests\unit\test_contact_point_profile_lifecycle.py \
  tests\integration\test_contact_point_profile_api.py -q
17 passed in 11.57s

cd frontend
npm test -- projectPointProfileSelectors ContactMeasurementPlanSummaryCard \
  ContactMeasurementSetupWorkspace useProjectPointProfileModel \
  MatrixEditorWorkspace --run
5 files / 55 tests passed

py -m py_compile [all TASK_361I Point Profile API/application/storage modules,
plus their narrow composition/startup files]
passed

cd frontend
npm run build
passed; only the existing Vite chunk-size warning (553.95 kB) remained
```

Focused selector coverage proves raw `"4"` is valid and rejects `1.5`, blank,
whitespace, zero, negative, sign, exponent, trailing-character, and unsafe-overflow
formats. The backend suite covers fresh/partial compatible schema bootstrap,
idempotency, incompatible CHECK fail-closed behavior, rollback/lock recovery,
no-target first save/confirm, stale fingerprints, legacy suggestion read-only
behavior, identity and confirmed-summary separation. The Matrix component suite
proves the summary consumes the dedicated confirmed-only endpoint rather than
editable workspace categories.

Candidate `git diff --check` exited `0`; only informational LF/CRLF notices were
printed. UTF-8 trailing-whitespace and changed-hunk locked/no-real-path scans had no
matches. New Point Profile Python modules range from 37 to 164 lines; the preexisting
`dependencies.py` and `database.py` hosts are larger but their TASK_361I hunks are
narrow composition/startup additions. No forbidden TASK_361I changed hunk referenced
real project paths, LTR/public drive, Fee, Report, StepInstance, AI, Projects list,
Matrix parser/import, `.agents`, or `docs/project_management`.

## Controlled Browser And API Smoke

1. Directly opened
   `http://127.0.0.1:5179/projects/P1/contact-measurement-setup` with a project
   that had no Point Profile target. It immediately showed an editable Project Point
   Profile starter row, with no technical `Open measurement plan` gate.
2. Entered `High Power / 4`, then added the optional Low Power and Signal templates
   and entered `5` and `24`. The live total displayed exactly `33 points / sample`.
   `More` expanded a native Prefix field; it was edited to `HP`.
3. Save succeeded with `Point Profile draft saved.`; a browser reload retained the
   saved draft rows. Confirm then succeeded with `Point Profile confirmed.`
4. Created a later disposable draft by changing Signal from `24` to `25` and saved.
   The setup UI showed `34 points / sample` and `Draft changes are not confirmed.`.
   A read-only `/summary` response remained confirmed revision `1`, High Power `4`,
   Low Power `5`, Signal `24`, total `33`, and `has_unconfirmed_draft=true`.
5. Entering `1.5` left it visible, reduced the derived total to `9`, and disabled
   both Save and Confirm. No request was made. `Discard changes` restored the saved
   `25` draft value. A local Signal removal reduced the total to `9`; a second
   discard restored all three saved rows and total `34`. Include-disable/re-enable
   visibly excluded and restored Signal from the total. Add/template/reorder controls
   were present; the focused selector suite covers deterministic reorder semantics.
6. A deliberate stale draft PUT returned `409`. Subsequent reads kept the editable
   total at `34`, confirmed total at `33`, the prior editable fingerprint, and the
   newer-draft flag. No authority row was lost.
7. The direct setup route loaded its feature CSS and displayed native labelled input,
   checkbox, button, and `details` controls. The keyboard probe focused a native
   checkbox; source and DOM snapshots expose accessible labels for the editable
   controls. Browser error/warning logs were empty.
8. At `514 x 900`, document/body scroll widths were `499` against viewport `514`.
   At desktop (`1280` width), they were `1265` against `1280`. No horizontal
   overflow or overlapping controls were observed.

The temporary Workbench did load its active Matrix region after a test-only confirmed
Matrix snapshot was seeded, but it reported no previewable Matrix tokens. The focused
Matrix component suite and the confirmed-only API result above therefore provide the
detail-card regression proof; no Matrix editing action was taken.

Artifacts:

- `docs/lane_evidence/artifacts/TASK_361I_qa/narrow-514px.png`
- `docs/lane_evidence/artifacts/TASK_361I_qa/desktop.png`

## Residual Risk

The disposable browser fixture intentionally did not drive a live Matrix editing
session or a visible stale-recovery dialog. Those surfaces remain covered by the
focused Matrix/model/API tests. This is non-blocking because the checked browser path
was profile-first, the summary API remained confirmed-only under a later draft, and
no product failure occurred.

## Decision

`QA gate: pass`

Recommended next role: Integrator packaging/readiness. Integrator must stage only
the reconciled TASK_361I candidate files and evidence; external board/TASK_361F
operational evidence, TASK_361H artifacts, and unrelated Settings/LTR/release/desktop
residuals must remain excluded.
