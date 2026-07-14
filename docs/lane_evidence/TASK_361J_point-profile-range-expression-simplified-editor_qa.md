# TASK_361J QA Evidence

- Gate: QA gate
- Result: `qa_blocked`
- Date: 2026-07-15
- Role: QA / Smoke Owner

## Environment And Safety

- Used only disposable workspace `tmp/task_361j_qa/` with SQLite `authority.sqlite3`, temporary API `127.0.0.1:8015`, and temporary Vite `127.0.0.1:5180`.
- Seeded disposable project: `P1` / `DL-QA-361J-P1`. No real `data/connlab.sqlite3`, workbook, public-drive, LTR, Fee, Matrix parser, or generated output was accessed or mutated.
- Browser artifacts: `docs/lane_evidence/artifacts/TASK_361J_qa/initial-empty-editor.png` and `confirmed-matrix-editor.jpg`.

## Passed Validation

1. Backend focused suite:
   ```powershell
   py -m pytest -p no:cacheprovider --basetemp=tmp\task_361j_qa_full_pytest tests\unit\test_contact_point_profile_fingerprint.py tests\unit\test_contact_point_profile_legacy_suggestion.py tests\unit\test_contact_point_profile_expression.py tests\unit\test_contact_point_profile_lifecycle.py tests\unit\test_contact_point_profile_schema.py tests\integration\test_contact_point_profile_api.py -q
   ```
   Result: `33 passed in 10.11s`. This suite covers V1-to-V2 migration/idempotency/malformed fail-closed, expression canonicalization and invalid/no-write cases, duplicate retained identity typed 422, 256 boundary, old draft 410, and confirmation atomicity.
2. Frontend focused suite:
   ```powershell
   cd frontend
   npm test -- projectPointProfileSelectors useProjectPointProfileModel ContactMeasurementSetupWorkspace ContactMeasurementPlanSummaryCard MatrixEditorWorkspace --run
   ```
   Result: `5 files / 55 tests passed`.
3. `py -m py_compile` for all touched Point Profile backend modules passed. `cd frontend; npm run build` passed; only the established Vite chunk-size warning remained.
4. Controlled browser smoke:
   - Direct setup route with no confirmed profile showed exactly one blank row and the simplified Prefix / Test points / delete-column UI.
   - Added `HP` / `1-4`, `HighP` / `1,2,3,4,5`, and `Signal` / `1-24`, then confirmed. The route returned to Matrix Editor with no console errors or warnings.
   - Read-only workspace result confirmed revision 1 with raw prefixes `HP`, `HighP`, `Signal`; canonical expressions `1-4`, `1-5`, `1-24`; counts 4, 5, 24; and total 33. No unconfirmed draft was present.
5. `git diff --check` found no trailing-whitespace errors. Only existing LF/CRLF normalization warnings appeared. Candidate Point Profile package files remained distinguishable from 34 working-tree entries; known board, TASK_361F evidence, and user button-style residuals remain excluded.

## Blocking Finding B1: Trash Icon Is Not Keyboard-Operable

Severity: blocking for this QA gate because TASK_361J acceptance explicitly requires the delete trash icon to be keyboard usable.

Reproduction in the controlled browser:

1. Open `http://127.0.0.1:5180/projects/P1/contact-measurement-setup` after confirming the disposable `HP`, `HighP`, and `Signal` profile.
2. Focus visible button `Delete point profile row Signal` (DOM marks it active; it has the expected accessible name).
3. Invoke `Enter` using the locator keyboard path, then the native browser keyboard path. The row remains visible.
4. Invoke `Space` using the locator keyboard path. The row remains visible.

Expected: either Enter or Space should activate the focused native delete button and remove only the local row.

Observed: the focused button did not delete the row in all three attempts. Pointer behaviour was not used to mask the keyboard failure. No console warning/error accompanied the failure.

Recommended owner: Developer fix pass. Add a browser-realistic regression for focused trash-button Enter and Space activation, then return for QA re-smoke. Do not alter the accepted Point Profile authority contract or package unrelated residuals.

## Residual And Scope Notes

- The gate stopped before the 514px visual pass because B1 is already a concrete acceptance blocker.
- TASK_360B/TASK_361D compatibility remains covered by the focused suite; QA did not generate a real workbook/artifact.
- Package integration must continue to hunk-isolate external `docs/task_board.md`, TASK_361F operational evidence, and the three user button-style residuals.

---

## QA Re-Smoke: Keyboard Delete Fix (2026-07-15)

- Gate: QA re-smoke
- Result: `qa_pass`
- Role: QA / Smoke Owner

### Environment And Safety

- Reused only the disposable `tmp/task_361j_qa/authority.sqlite3` fixture and its
  temporary API (`127.0.0.1:8015`) / Vite (`127.0.0.1:5180`) processes. The fixture
  project was `P1` / `DL-QA-361J-P1`.
- No real `data/connlab.sqlite3`, user project, workbook, LTR/public-drive folder,
  Test Record output, Fee workflow, Matrix confirmation, or generated document was
  accessed or mutated.

### B1 Re-Smoke Results

1. On the controlled Contact Measurement Setup route, the confirmed fixture rendered
   `HP` / `1-4`, `HighP` / `1-5`, and `Signal` / `1-24` (33 points/sample). Local
   edits renamed the second row to `LP` solely to make the three-row keyboard case
   explicit; the edit was later cancelled.
2. Focused visible `Delete point profile row Signal` and sent real browser `Enter`.
   Signal count became `0`; `HP` and `LP` button counts remained `1` each. This is
   one deletion only.
3. Re-added Signal locally, then sent real browser `Space` to the focused Signal
   delete button. Again Signal count became `0`; HP and LP stayed present exactly
   once. No page-scroll anomaly was observed.
4. Re-added Signal and used pointer click on its own icon button. Only Signal was
   removed; adjacent HP and LP remained. The button exposes `type=button`,
   `title="Delete row"`, and the row-specific `aria-label`; the focused test suite
   also covers disabled/busy no-delete behavior.
5. Clicked `Cancel`. The route returned to Matrix Editor. A read-only request to
   `GET /api/projects/P1/contact-point-profile/summary` still returned confirmed
   revision 1 with `HP`, `HighP`, `Signal`, expressions `1-4`, `1-5`, `1-24`, and
   `points_per_sample: 33`: local delete/rename attempts performed zero authority
   writes.
6. Desktop browser smoke showed the direct editor's Prefix / Test points / delete
   table and Add row action header, then Matrix summary's confirmed revision/33-point
   result after Cancel. Browser console error/warning query returned `[]`.

### Validation Commands

```powershell
cd frontend
npm test -- projectPointProfileSelectors useProjectPointProfileModel ContactMeasurementSetupWorkspace ContactMeasurementPlanSummaryCard ProjectPointProfileEditor MatrixEditorWorkspace --run
npm run build

py -m pytest -p no:cacheprovider --basetemp=tmp\task_361j_qa_resmoke_pytest tests\unit\test_contact_point_profile_fingerprint.py tests\unit\test_contact_point_profile_legacy_suggestion.py tests\unit\test_contact_point_profile_expression.py tests\unit\test_contact_point_profile_lifecycle.py tests\unit\test_contact_point_profile_schema.py tests\integration\test_contact_point_profile_api.py -q
py -m py_compile backend\application\contact_point_profile_expression.py backend\application\contact_point_profile_lifecycle_service.py backend\application\contact_point_profile_read_service.py backend\infrastructure\storage\contact_point_profile_schema_migration.py backend\api\routes_contact_point_profile.py
git diff --check
```

- Frontend focused suite: `6 files / 59 tests passed`.
- Frontend build: passed; only the established Vite chunk-size warning remained.
- Backend focused suite: `33 passed in 11.29s`.
- `py_compile`: passed.
- `git diff --check`: no errors; existing LF/CRLF normalization warnings only.
- Candidate trailing-whitespace scan: no matches.

### Residual And Package Isolation

- Tried the in-app browser viewport override at `514 x 900`, including a new tab.
  The attached browser retained a 1280px document width and screenshot capture timed
  out, so a true 514px screenshot could not be captured in this environment. This is
  a non-blocking tooling residual for this keyboard-fix re-smoke; desktop visual smoke,
  source/table structure, and the focused component suite are the fallback evidence.
- The existing desktop artifact remains
  `docs/lane_evidence/artifacts/TASK_361J_qa/confirmed-matrix-editor.jpg`.
- `docs/task_board.md`, TASK_361F operational evidence, TASK_361H artifacts, and
  the user-owned button-style residuals remain external and must be excluded during
  packaging. No production source or test file was modified by QA.

### Gate Decision

`qa_pass`. Original B1 keyboard blocker is closed. Recommend **Integrator packaging/readiness** with the stated external-residual isolation.
