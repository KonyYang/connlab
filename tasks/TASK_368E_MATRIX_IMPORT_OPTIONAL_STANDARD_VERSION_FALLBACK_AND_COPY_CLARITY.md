# TASK_368E_MATRIX_IMPORT_OPTIONAL_STANDARD_VERSION_FALLBACK_AND_COPY_CLARITY

Status: `approved_worktree_preparation`

Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

Current gate owner: permanent Orchestrator for isolated worktree preparation only. User approval
is recorded; no implementation branch/worktree exists yet, no execution token is held, and no
Developer dispatch or product/test change has started.

## User Approval Record

- On 2026-08-01 the User explicitly approved the exact task and plan at planning checkpoint
  `5dff98af9d0f93770962a9a672d7610d0cef4936`.
- The User authorized automatic execution through local Integrator acceptance within the exact
  approved scope and mandatory `Developer -> Reviewer -> QA -> Integrator` route.
- This approval does not authorize push, publication, release build, runtime restart, real
  DB/Excel/PDF/public-drive mutation, destructive cleanup, or changes to retained/cancelled/frozen
  lanes.
- Approval preserves WIP=`1`, the exact May Touch/Must Not Touch/Locked Paths, positive
  availability allowlist, integrity fail-closed boundary, UX copy, and all acceptance tests.
- Current durable state is only `approved_worktree_preparation`; token acquisition and Developer
  dispatch require later primary governance after Orchestrator has created and verified the exact
  isolated worktree.

## Goal

Make the Settings copy describe the Standard resource as a version-file path and make
Matrix Import Replace resilient when that resource is not available. For an eligible
availability failure, offer an explicit choice to select/configure a file or `Skip for now`.
Skip must immediately preserve every imported Method value, selected Group, and source-lineage
fact, persist the editable Matrix draft, close the dialogs, and show a calm non-red warning. A
configured resource that can be read safely keeps the existing automatic synchronization.

## Product Decision

- Exact Settings row label: `Standard version file path`.
- Exact path-input accessible name/title: `Standard version file path`; do not produce
  `Standard version file path path`.
- `Standard record sheet` remains unchanged.
- Exact fallback warning:
  `Standard version file unavailable. Original Method values were kept. You can update them later in Standard Method versions.`
- The warning is an amber/non-danger status with `role="status"` and
  `aria-live="polite"`.
- On an eligible availability failure, open an accessible choice dialog with exact title
  `Standard version file unavailable`, body
  `Choose a Standard version file, or skip for now and keep the original Method values.`, and
  actions `Choose file` and `Skip for now`.
- `Choose file` reuses the existing native picker plus resource save/validation behavior. It is
  an explicit user configuration, not automatic configuration. Cancel writes nothing.
- `Skip for now` cannot be coercive or terminally blocked; it immediately retries the same
  Replace using a narrow preserve-source policy and, while availability remains eligible,
  completes the editable draft.
- `Standard Method versions` Preview/Apply remains the later update path.
- `Confirm Matrix` remains the only authority-publication boundary.

## Fallback And Fail-Closed Boundary

The implementation must classify failures by evidence, not by broad message matching.

### Choice then explicit fallback

These availability states make the initial Replace return a typed, zero-write action-required
detail. Choose may configure/validate a file and retry normally; Skip rechecks the facts and
returns successful Replace with `source_preserved` plus the warning:

1. no registered Standard version resource;
2. a registered resource is inactive;
3. the configured path is absent or no longer names a file;
4. the configured path is temporarily inaccessible because of an explicitly recognized
   filesystem availability condition, including not-found, access-denied, share/network
   unavailable, or sharing violation;
5. legacy `.xls` cannot be read because the Microsoft Excel COM runtime itself is
   unavailable.

Unknown exceptions are not availability evidence and must fail closed.

The action-required state is a recoverable choice, not a generic red error. Integrity failures
below do not show or honor Skip.

### Still fail closed with typed `422` and zero write

These integrity/configuration states are not downgraded to warnings:

1. unsupported extension or workbook type;
2. corrupt XLSX package/XML or a legacy workbook that cannot be opened/read for an
   unclassified reason;
3. configured worksheet missing, ambiguous, or different from the returned catalog;
4. required header/layout missing or invalid;
5. configured worksheet has no nonblank Standard-code rows;
6. oversized/invalid COM range, invalid row/value shape, unsafe cleanup failure, or other
   workbook-integrity failure;
7. returned catalog path differs from the configured path;
8. malformed or unverifiable authority/audit context.

Individual non-EIA or malformed Standard-code cells retain the accepted TASK_366B/C
row-level behavior; they are not reclassified as resource availability and do not broaden
automatic fallback.

## Authority And Audit Contract

- Fallback must not run the Method proposal as if a catalog had been synchronized.
- Every imported draft row keeps its exact imported `method`, including blanks and original
  spelling/punctuation. `current_method == resulting_method`, `applied=false`, and the
  row status is `source_preserved`.
- The selected-only Group projection, source import, source snapshot, stable row identity,
  payload/locator/selected-group/source/result fingerprints, and editable-draft transaction
  remain intact.
- A versioned fallback context must be stored in the existing
  `method_sync_context_json`; no schema/database migration is allowed. It records a
  controlled reason code, known nullable resource metadata, unchanged pre/post Method
  fingerprints, row results, and the normal source/draft lineage.
- The existing configured-success `matrix-import-method-sync:v1` context remains compatible.
  Existing accepted synchronized imports must continue strict reuse without rewriting their
  context.
- Exact replay under the same fallback facts may return `reused` only after the existing
  source, draft, context, and fingerprints are read-verified. A resource/context change,
  later draft edit, malformed context, or partial aggregate remains `409` zero-write. When
  a resource becomes available after a fallback import, the operator updates the editable
  draft through existing `Standard Method versions`; Replace does not silently rewrite a
  prior import.

## API Compatibility

- The request adds optional/defaulted
  `standard_version_unavailable_action: prompt_if_unavailable | preserve_imported_methods`.
  Initial/choose retry uses the default; only `Skip for now` sends preserve. The backend rechecks
  authority and never trusts the flag to suppress an integrity error.
- A typed action-required `409` detail uses code
  `matrix_import_standard_version_action_required`, a controlled availability reason code, and
  no path/OS detail.
- `method_authority_sync.status` adds `source_preserved` to the existing
  `synchronized | review_required` union.
- `standard_resource_id`, `effective_worksheet_name`, and `catalog_fingerprint` become
  nullable because fallback may have no readable authority. `context_fingerprint` remains
  required and nonblank.
- Add one nullable typed warning object with a controlled code and the locked user-facing
  message. Success has `warning=null`; fallback has a warning.
- Existing fields are retained, and configured-success response meaning is unchanged.

## May Touch

### Product

1. `backend/application/matrix_import_method_authority.py`
2. `backend/application/matrix_import_commit_service.py`
3. `backend/api/routes_matrix_import_commit.py`
4. `frontend/src/api/client.ts`
5. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
6. `frontend/src/features/matrix-editor/MatrixImportStandardVersionChoiceDialog.tsx`
7. `frontend/src/features/matrix-editor/useMatrixImportStandardVersionChoice.ts`
8. `frontend/src/features/settings/settingsResourceConfig.ts`
9. `frontend/src/features/settings/SettingsExternalResourcesPanel.tsx`
10. `frontend/src/workbench.css`

### Bounded tests

11. `tests/unit/test_task_368e_matrix_import_optional_standard_fallback.py`
12. `tests/integration/test_task_368e_matrix_import_optional_standard_fallback_api.py`
13. `frontend/src/features/matrix-editor/MatrixImportStandardVersionChoiceDialog.test.tsx`
14. `frontend/src/features/matrix-editor/useMatrixImportStandardVersionChoice.test.tsx`
15. `frontend/src/features/matrix-editor/MatrixImportOptionalStandardFallback.test.tsx`
16. `frontend/src/features/settings/SettingsStandardRecordSheet.test.tsx`
17. `tests/unit/test_frontend_shell_files.py`

### Task-owned governance/evidence

18. `tasks/TASK_368E_MATRIX_IMPORT_OPTIONAL_STANDARD_VERSION_FALLBACK_AND_COPY_CLARITY.md`
19. `docs/task_368e_matrix_import_optional_standard_version_fallback_and_copy_clarity_plan.md`
20. `docs/lane_evidence/TASK_368E_matrix-import-optional-standard-version-fallback-and-copy-clarity_planner.md`
21. role evidence for Developer, Reviewer, QA, and Integrator using the same TASK_368E
    evidence prefix
22. `docs/task_board.md`, only for approved dispatch/gate/closeout governance

Any additional product or test path is a scope expansion and must stop for Planner/User
reconciliation before modification.

## Must Not Touch

- `frontend/src/features/matrix-editor/MatrixMethodVersionSyncPanel.tsx` and
  `useMatrixMethodVersionSync.ts`; run their tests read-only.
- Standard parser/catalog layout, Office gateways/facade, external-resource service/routes,
  Settings page, desktop picker bridge implementation, Matrix confirmation/session persistence,
  source/draft repositories, SQLAlchemy models, schema, or migrations.
- `backend/api/dependencies.py`, `backend/api/main.py`, and any new endpoint.
- real database, development database copies, real Excel/PDF/DOCX files, public-drive paths,
  Standard workbook contents, output workbooks, or generated release artifacts.
- AGENTS, project-management protocols/skills/scripts, execution-control schema, role registry,
  or active-task bundle.
- TASK_368A/B/C/D packages, cancelled browser-release work, retained/frozen V2 lanes, or any
  existing worktree/branch.
- push, publication, release build, service restart, destructive cleanup, reset, restore,
  discard, worktree retirement, or remote-state mutation.

## Locked Paths

The ten product paths and seven bounded test paths listed under May Touch are exclusive to
this future lane from Developer dispatch until Integrator acceptance/cancelled closeout.
Existing read-only regressions remain unowned and must not be edited.

## Acceptance

1. Configured valid `.xlsx` and `.xls` resources preserve current automatic synchronization,
   counts, row decisions, and strict reuse behavior.
2. Each allowed availability state produces a typed zero-write choice; Choose explicitly
   saves/validates and retries, while Skip rechecks and immediately persists source/draft lineage,
   exact Method values, selected Groups, and `source_preserved`.
3. Fallback never claims synchronization and always has an auditable context fingerprint plus
   controlled reason code.
4. Every fail-closed integrity/configuration case returns typed `422` with zero writes.
5. Persistence/read-verify/reuse conflicts remain typed `409` with zero partial writes.
6. Matrix Editor shows the exact accessible choose/skip dialog without a red error. Cancel writes
   nothing; validation failure remains recoverable; Skip applies the returned draft, closes both
   dialogs, clears the error, and displays the exact amber warning.
7. Settings displays `Standard version file path` and exposes that exact accessible name.
8. `Standard Method versions` Preview/Apply and `Confirm Matrix` do not regress.
9. No Standard workbook, public-drive file, real DB, or confirmed Matrix is written by Replace.

## Risk And Required Gates

This is `QF-4`: it changes an accepted authority fallback/API/frontend contract across layers.
Quick Fix is forbidden. After explicit User approval, the only legal route is:

```text
Planner -> User approval -> Developer -> Reviewer -> QA -> Integrator
```

Reviewer, QA, and Integrator are mandatory. A blocking finding returns to Developer; a scope or
authority ambiguity returns to Planner/User.

## Planned Lane Identity

- Lane: `task-368e-matrix-import-optional-standard-version-fallback-and-copy-clarity`
- Branch: `lane/task-368e-matrix-import-optional-standard-version-fallback-and-copy-clarity`
- Sibling worktree:
  `D:\PythonProject\connlab-worktrees\task-368e-matrix-import-optional-standard-version-fallback-and-copy-clarity`
- Planning base: `7b2be466b283d53f88b93d365ed21f15269fa5a5`
- WIP: `1`; no parallel exception.

User approval is now recorded, but the branch/worktree still do not exist. Permanent Orchestrator
must run its own fresh worktree-preparation gate, create only the exact branch/path above, verify
clean base/HEAD/index, and return those facts for dispatch governance. The implementation base is
recorded from that verified creation, not inferred from planning history.

## Stop Point

Return to permanent Orchestrator for worktree preparation. Planner must not create the worktree,
acquire the execution token, dispatch Developer, or edit product/test code in this approval-only
pass.
