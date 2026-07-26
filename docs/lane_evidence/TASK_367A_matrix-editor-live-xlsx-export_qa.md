# TASK_367A Matrix Editor Live XLSX Export QA Evidence

Date: 2026-07-26
Role: QA / Smoke Owner
Status: `qa_pass`
Current source-of-truth status: `complete_accepted_with_post_accept_correctives_pending_reviewer_docs_only_source_of_truth_re_gate`
Task: `TASK_367A_MATRIX_EDITOR_LIVE_XLSX_EXPORT`
Lane: `matrix-editor-live-xlsx-export`
Reviewed base: `405c0c80ed93756080099b378d490ae875f7e8a6`
Reviewed clean commit: `fb2b91c8a49a7b03d1afc07c519f4d156c12ba42`

## Isolation And Package Boundary

- All validation source came from a fresh archive created directly from reviewed commit
  `fb2b91c8a49a7b03d1afc07c519f4d156c12ba42` in a temporary directory. The primary dirty
  worktree was not used as test input; the implementation worktree was read only for the
  clean-index check.
- The commit diff exactly matched the approved 17-path whitelist and measured `1091` additions
  and `3` deletions. `git diff --check 405c0c80..fb2b91c8` passed.
- The reviewed implementation worktree had an empty index and no unstaged change. Candidate
  paths contain no database/schema, operator path, public-drive, runtime-template loader, or
  external-file surface.
- New bounded production modules are within limits: backend `13/117/165/76` lines and frontend
  `24/85/51` lines for composition, route, service, gateway, button, projection, and hook.

## Validation Results

Commands were run from the clean archive unless stated otherwise.

```powershell
py -m pytest --basetemp .qa367a_feature \
  tests/unit/test_matrix_editor_live_xlsx_export_service.py \
  tests/unit/test_matrix_editor_live_xlsx_workbook_gateway.py \
  tests/integration/test_matrix_editor_live_xlsx_export_api.py -q
# 11 passed

py -m pytest --basetemp .qa367a_regress \
  tests/integration/test_matrix_editor_session_api.py \
  tests/integration/test_confirmed_matrix_test_record_preview_api.py -q
# 15 passed

py -m py_compile backend/api/main.py \
  backend/api/dependencies_matrix_editor_live_xlsx_export.py \
  backend/api/routes_matrix_editor_live_xlsx_export.py \
  backend/application/matrix_editor_live_xlsx_export_service.py \
  backend/infrastructure/office/matrix_editor_live_xlsx_workbook_gateway.py
# passed

npm test -- --run src/features/matrix-editor/matrixEditorXlsxExportProjection.test.ts \
  src/features/matrix-editor/useMatrixEditorXlsxExport.test.tsx \
  src/features/matrix-editor/MatrixEditorXlsxExportButton.test.tsx \
  src/features/matrix-editor/MatrixEditorWorkspace.test.tsx
# 4 files / 49 tests passed

npm test -- --run --reporter=json --outputFile .qa367a_full.json
# 115 files / 389 tests passed

npm run build
# passed; existing Vite chunk-size warning only
```

## Contract Smoke

- Service/API coverage confirmed typed pre-gateway `422` rejection with zero gateway calls/bytes
  for empty, cap-exceeding, duplicate, and non-rectangular payloads.
- The generated workbook is in-memory and reloads with the required one-sheet layout, selected
  Group ordering, exact page-projected Sample size and Time text, and blank Fee cells.
- Formula/literal safety was verified after reload: dynamic formula- and HYPERLINK-shaped input
  values remained literal (`data_type != "f"`), all cells had no hyperlink, workbook external
  links and defined names were empty, and Fee non-label cells were `None`.
- Projection/hook tests verified selected Groups plus qualifying non-sample rows, click-time
  state, lifecycle/busy/no-Group/step/no-row disabled-reason precedence, Blob download, object
  URL revoke, and retry. No autosave/CAS or lifecycle write behavior entered the package.

## Controlled Browser Smoke

A temporary Vite harness imported the committed `MatrixEditorXlsxExportButton` directly and
used only synthetic selected-Group/step state. It did not connect to an operator database,
backend project, or real file.

- Desktop `1280x800`: one enabled native historical pre-corrective `导出 Matrix` button appeared
  between Import Matrix and Test record in the Matrix action region; pointer activation
  incremented the controlled export signal once; `scrollWidth == clientWidth == 1280`;
  application console error/warning log was empty.
- Narrow `514x831`: the action buttons wrapped to readable full-width rows; no horizontal
  overflow (`scrollWidth == clientWidth == 514`), overlap, or text clipping was observed; the
  export button received visible focus and the application console error/warning log was empty.
- Browser automation could focus the button but its injected `Enter` and `Space` events did not
  dispatch a click in this in-app browser client. This is a non-blocking browser-tooling residual,
  not a product failure: the committed control is a native `type="button"`, the focused component
  and complete frontend suite passed, and pointer activation was observed. No real download was
  attempted; the disposable Blob-download behavior is covered by the hook test and the raw-byte
  API/gateway tests.

## Scope And Residual Risk

- No QA product or test edits, staging, commit, push, operator DB read, or real-file action was
  performed. This evidence file is the only QA worktree change.
- Residual: native-key dispatch in the in-app automation client could not be made to invoke the
  already-focused button. A manual physical-key check in a standard browser remains optional
  follow-up, but focused component/DOM semantics make it non-blocking for this isolated gate.

## QA Conclusion

`QA gate: pass`

Historical recommended next role (completed): `Integrator packaging/readiness`, staging only the
reviewed 17-path commit package and excluding all external residuals.

## Post-Accept Source Of Truth

The smoke result above remains valid historical QA evidence for placement, native-button
semantics, and responsive layout. Its visible title is superseded by post-accept commit
`f0880310f786ac98ad0f8437db02fc22cca93f08`; the current title is `Export Matrix`.
Post-accept commit `1c9f8fc58ca72d21e020576d5aa611a307c335c3` also supersedes fixed row
height `15`: wrapped rows now keep height unset for automatic fitting. TASK_367A remains
complete/accepted at current primary/master HEAD
`1c9f8fc58ca72d21e020576d5aa611a307c335c3`; only Reviewer docs-only
source-of-truth re-gate is pending.
