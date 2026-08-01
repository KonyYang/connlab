# TASK_368E Matrix Import Optional Standard Version Fallback And Copy Clarity — QA Evidence

Date: 2026-08-01
Role: permanent QA / Smoke Owner
Status: `qa_pass`
Next: permanent Integrator

## Authority And Immutable Input

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Task: `TASK_368E_MATRIX_IMPORT_OPTIONAL_STANDARD_VERSION_FALLBACK_AND_COPY_CLARITY`.
- Why allowed: primary records TASK_368E as the sole WIP=1 token owner in `gate_running`, with
  permanent QA as the read-only gate owner and Reviewer `reviewer_pass` complete.
- Primary governance: `master@7d670148d63f2dc209084567c6718f644bc24db0`, clean.
- Lane base: `e226bf1e54db4de54eb2366e96895999ce54652d`.
- Reviewed QA input: `77fe429eea59d2908c2f57d9243e8fd893488ad5`.
- Branch: `lane/task-368e-matrix-import-optional-standard-version-fallback-and-copy-clarity`.
- Worktree:
  `D:\PythonProject\connlab-worktrees\task-368e-matrix-import-optional-standard-version-fallback-and-copy-clarity`.

QA read `AGENTS.md`, the current primary board, task, plan, Planner/Developer/Reviewer evidence,
execution and parallel-lane policies, review checklist, frontend architecture rules, and the
`impeccable` product/design context. The initial branch, HEAD, ancestry, worktree, and index were
exact and clean. Validation used only the immutable reviewed lane.

## Environment And Data Isolation

- OS: `Microsoft Windows NT 10.0.26200.0`
- Windows PowerShell: `5.1.26100.8875`
- Python: `3.13.3`
- Git: `2.51.0.windows.1`
- Frontend dependencies: existing primary dependency tree, linked only into disposable frontend
  archives; no install, package, or lockfile mutation.
- Backend tests used pytest-owned disposable SQLite/XLSX paths, fake COM/catalog readers, and
  in-memory Matrix sources.
- No operator DB, repository DB, real Excel/PDF/DOCX, configured resource, public-drive path,
  current localhost, or live operator project was opened, read, or mutated.

## Backend And API Validation

```text
py -m pytest tests\unit\test_task_368e_matrix_import_optional_standard_fallback.py tests\integration\test_task_368e_matrix_import_optional_standard_fallback_api.py -q
31 passed in 24.40s

py -m pytest <12 TASK_366B/C, source-persistence, Matrix-session, Confirm-authority compatibility modules> --deselect=tests/unit/test_matrix_editor_session_service.py::test_confirm_first_authority_initializes_default_fee_authority -q
65 passed, 1 deselected in 34.21s

py -m pytest tests\unit\test_excel_standard_record_layout_xlsx.py tests\unit\test_excel_standard_record_layout_com.py tests\unit\test_standard_record_catalog_read_service.py tests\unit\test_external_excel_read_service.py tests\integration\test_external_excel_read_api.py tests\unit\test_excel_com_readonly_tabular_gateway.py -q
38 passed in 7.00s

py -m pytest tests\unit\test_frontend_shell_files.py::test_task285a_settings_file_locations_simplified_ui_is_wired -q
1 passed in 0.05s

py -m pytest <TASK_368E unit/API modules> -k cleanup_integrity_wrapper -q
8 passed, 23 deselected in 3.50s
```

The fresh TASK_368E matrix covers all five positive availability states, typed action-required
zero-write responses, Skip for every allowed state, exact Method/selected-Group/source lineage,
fallback fingerprints and ordered row audit, strict replay reuse, newly readable/changed context
conflicts, configured-success v1 metadata, transaction rollback, corrupt/unsupported/worksheet/
header/empty/range/cleanup/unknown integrity negatives, and API nullability.

The cleanup B1 matrix independently proves both default and explicit-preserve requests return
typed `422`, expose no action-required detail, and perform zero source/draft writes for nested
`PermissionError` and allowlisted Windows-code causes. Genuine open/read and COM-unavailable
availability cases remain eligible.

Compatibility coverage retains TASK_366B/C Standard parsing/synchronization, source persistence,
selected-only import, strict reuse, Matrix session, Standard Method versions, and Confirm Matrix
authority. Configured XLSX and fake-COM XLS cases pass without accessing a real workbook.

## Independently Attributed Baseline Deselect

The initially attempted Windows-backslash `--deselect` did not match pytest's slash-form node ID,
so the run reproduced the documented failure and ended `65 passed, 1 failed`. The failure is the
unchanged fake constructing `MatrixImportCommitResult` without `method_authority_sync`.

QA then used the correct node ID and obtained `65 passed, 1 deselected`. Independent Git-blob
proof establishes that the debt is not attributable to TASK_368E:

- `tests/unit/test_matrix_editor_session_service.py` is unchanged from base through reviewed HEAD;
- base and reviewed test blob are both
  `822dfc80de70e73d99f7f11753bbd28924d51e25`;
- the base result type already requires `method_authority_sync`;
- the same base fake omits it.

A full base archive attempt timed out during extraction, before producing a product verdict. Its
single prefix-controlled temp directory was removed, and the smaller immutable-blob proof above
replaced that unnecessary archive operation.

## Frontend, Accessibility, And Build

A disposable archive of reviewed `frontend/` was linked to the existing dependency tree. The
exact focused set passed:

```text
8 test files passed
61 tests passed
```

The files cover the choice dialog, choice hook, optional fallback workspace behavior, Settings
sheet/path behavior, Standard Method versions panel/hook, Matrix Editor workspace, and duration
authority compatibility. Fresh assertions include:

- exact dialog title/body and `Choose file` / `Skip for now` actions;
- primary-action focus, Escape close, and focus return;
- picker cancel performs no save/validation/import write and remains recoverable;
- Choose saves and validates the selected existing resource, preserves worksheet configuration,
  and retries normal Replace;
- validation failure stays inside the dialog and does not import;
- Skip immediately retries with preserve policy, applies the draft, closes both dialogs, clears
  generic error presentation, and shows the exact warning;
- the component-level integrity `422` case does not expose the choice flow; independent source
  inspection confirms the typed predicate rejects every non-409 status and every generic 409 whose
  code, controlled reason, or nonblank message does not match the action-required contract;
- configured success, Standard Method versions Preview/Apply, and Confirm Matrix behavior remain
  compatible.

Exact Settings and status contracts were independently inspected:

- visible label and normal input accessible name/title: `Standard version file path`;
- no generated `Standard version file path path`;
- `Standard record sheet` unchanged;
- exact fallback warning:
  `Standard version file unavailable. Original Method values were kept. You can update them later in Standard Method versions.`
- warning element: `role="status"`, `aria-live="polite"`;
- warning CSS uses amber border/background/text (`#d8b76a`, `#fff8e6`, `#704d08`) and no danger
  token/color.

The disposable frontend build passed `tsc -b` and Vite (`132 modules transformed`, build complete
in `3.69s`). The only message was the existing chunk-size advisory. The first successful run hit
a PowerShell 5.1 NullReferenceException only while deleting its temporary dependency junction;
QA removed that exact junction/temp directory safely and reran the full 61-test plus build command
end-to-end with exit `0`. No temp runtime remains.

No safe standalone live-browser fixture was available without connecting to current localhost or
an operator project, both prohibited. QA therefore made no live/514px claim. Deterministic jsdom
component coverage verifies keyboard/focus/cancel/actions, and the reviewed responsive CSS keeps
the dialog at `min(520px, calc(100vw - 48px))`; at 514px this is a 466px bounded surface with
minimum 116px actions. This is component/CSS evidence, not a live operator smoke.

## Compile, Lines, Package, And Write Scans

- `py -m py_compile` passed for the three changed backend product modules and both TASK_368E
  backend test modules.
- Physical lines: authority `499`, commit service `449`, route `291`, unit/API tests `336/285`,
  dialog/hook `96/113`, and new frontend tests `73/98/269`; all applicable Python hard limits pass.
- Base..Reviewer contains exactly 17 approved product/test paths plus Developer and Reviewer
  evidence (`19` total); no task-board copy or hidden path is present.
- All six commits after base passed `git show --check`; full range `git diff --check` passed.
- Office gateways, persistence/schema, dependencies/main, Standard Method versions product files,
  Confirm Matrix product files, packages/lockfiles, `data/**`, release output, project-management
  protocols, skills, and retained/frozen lanes are absent from the diff.
- Product-diff scan found no absolute user path, `openpyxl`, `win32com`, `SaveAs`, workbook-save,
  or public-drive write primitive.
- All QA temporary directories were removed. Lane and index remained clean after validation.
- Reviewed HEAD was not contained by a remote branch; QA did not push.

## Conclusion

- Result: `qa_pass`
- Blocker: none
- Next role: `Integrator`
- QA changed only this evidence file and performed no product/test fix, merge, push, restart,
  release build, worktree retirement, real-data access, or destructive repository action.
