# TASK_366B Standard Record Method Version Sync And Sheet Configuration

Status: `complete / accepted`

Implementation authorization: TASK_366B frozen scope only.

## Current Phase And Role

- Phase: Phase 11 controlled Project Workbench / Matrix foundation.
- Active task: `TASK_366B_STANDARD_RECORD_METHOD_VERSION_SYNC_AND_SHEET_CONFIGURATION`.
- Active role: Integrator closeout.
- Why allowed: TASK_366A is complete/accepted at
  `2e8d7ddd2b7d08bff49987763cbdce66c0ebc4c6`; Reviewer implementation re-gates,
  QA B3 re-gate, and Integrator package isolation passed for the frozen TASK_366B
  scope. This closeout activates no new product lane.

## Goal

Add a configurable Standard record worksheet name and a review-first Matrix Method
version synchronization flow. The source Standard record workbook remains read-only.
The flow proposes updates for Matrix draft row `method` values, applies only explicitly
selected safe proposals to the editable Matrix draft, and relies on the existing
`Confirm Matrix` action to publish a new confirmed authority revision.

## Confirmed Product Contract

1. Settings shows a `Standard record sheet` text field immediately after the Standard
   record Excel path. Its effective default is `认可标准`.
2. The sheet name is a distinct persisted setting, never encoded into the path.
3. Standard record validation/read uses the configured sheet, row 2 as the header,
   and row 3 onward as data. Column B must be `文 件 编 号`; columns C and D may map
   `文 件 名 称` and `备注` when present.
4. `.xlsx` keeps its accepted ZIP/XML read-only route. `.xls` keeps the TASK_366A
   hidden read-only Excel/COM route. Neither route may save, convert, copy, or mutate.
5. The ConnLab equivalent of legacy `ConfirmSpec!Test Method` is Matrix row `method`:
   editable `ProjectMatrixDraftRow.method`, then immutable
   `ConfirmedMatrixRow.method` after `Confirm Matrix`. Generic Test Record is a
   downstream projection and is not edited directly. TASK_360B specialized LLCR/CR
   workbook is unrelated and remains unchanged.
6. Preview and apply operate only on the currently persisted editable Matrix draft.
   Apply updates only selected `method` fields and writes no confirmed authority.
7. Existing `Confirm Matrix` remains the only publication gate. Before confirmation,
   generic Test Record and other confirmed consumers remain unchanged.
8. The source workbook is read-only. No VBA is executed or copied into runtime.

## Worksheet Configuration Contract

- Persistence candidate: additive nullable `external_resources.worksheet_name`.
- Legacy/null Standard record rows resolve to effective `认可标准` without a
  background write.
- Standard record upsert must distinguish field presence:
  - omitted `worksheet_name`: preserve the existing persisted value; for a new Standard
    row store `NULL` and return effective `认可标准`;
  - explicit `null`: reset to default by persisting `NULL`; response returns effective
    `认可标准`;
  - explicit whitespace-only string after trim: reset to default by persisting `NULL`;
    response returns effective `认可标准`;
  - explicit trimmed nonblank valid text: persist the trimmed value independently from
    the path; response returns that value;
  - control characters, more than 31 characters after trim, or Excel-invalid sheet
    characters (`[ ] : * ? / \\`) are rejected with a typed no-write validation
    message.
- Non-Standard resource types reject any supplied `worksheet_name`, including explicit
  `null` or whitespace-only values. Omitted `worksheet_name` for non-Standard resources
  is ignored/preserved for backward compatibility.
- API responses expose the effective value: Standard rows return the trimmed persisted
  value or `认可标准` when stored `NULL`; non-Standard rows return `null`.
- Matching is trim plus Unicode `casefold`; one exact logical match is required.
  Missing or ambiguous matches are invalid and list the configured name without a raw
  COM traceback.
- Header validation is positional: row 2, column B, normalized whitespace, exact
  `文 件 编 号`. A title in row 1 is expected and ignored.

## Standard Number And Method Parsing Contract

- Matrix methods are eligible only when they contain exactly one case-insensitive
  `364-\d{2}` core after normalizing whitespace and Unicode hyphen variants.
- Catalog cells accept `EIA` and `ANSI/EIA` prefixes, case-insensitively, with
  whitespace around `/` and hyphens normalized.
- The revision is one A-Z token immediately adjacent to the two-digit method number,
  such as `04B`. The parser must not scan the rest of the string for an arbitrary
  letter.
- A trailing four-digit catalog year is parsed for diagnostics only. It is not added
  to a Matrix method that did not already contain a year. Existing Matrix suffix text
  and year text are preserved while only the adjacent revision token is replaced or
  appended.
- Example: `EIA-364-04A` plus `ANSI/EIA-364-04B-2015` proposes
  `EIA-364-04B`. `ANSI / EIA-364-04A-2010` proposes
  `ANSI / EIA-364-04B-2010`.
- Duplicate catalog rows with the same normalized core and revision are deduplicated;
  the newest parsed year then lexical code order selects diagnostic metadata.
- Distinct revisions for one core are `ambiguous` and blocked. V1 never uses first
  match.
- A missing current revision may receive the unique catalog revision. Same revision is
  `current`. A higher A-Z revision is `update_available`. A lower revision is
  `downgrade_conflict` and cannot be applied in V1.
- No core, no match, malformed catalog code, multiple cores, missing catalog revision,
  or conflicting revisions leaves the method unchanged with a readable status.
- Parser state is row-local. No revision/match state may leak from a previous row.

## Preview, Apply, Confirmation, And Audit

Future typed endpoints:

- `POST /api/projects/{project_id}/matrix-method-version-sync/preview`
- `POST /api/projects/{project_id}/matrix-method-version-sync/apply`

Preview requires `project_matrix_draft_id` and the expected saved draft signature. It
returns source resource/sheet metadata, catalog fingerprint, target fingerprint,
preview fingerprint, and ordered row proposals with current/proposed methods and typed
statuses. Preview is zero-write.

Apply requires the same draft identity/signature, preview fingerprint, actor, and an
explicit list of selected draft row ids. It reloads the draft and catalog, recomputes
the preview, and returns typed `409` on any source/target mismatch. Only
`update_available` and `revision_missing` rows may be selected. The command atomically
replaces only those draft row methods while preserving groups, cells, quantities,
schedule, conditions, and requirements.

Audit candidate: additive nullable
`project_matrix_draft_records.method_sync_context_json`. It stores the resource id,
effective sheet name, canonical catalog/target/preview fingerprints, actor, timestamp,
and selected old/new row values. The confirmed Matrix already retains the draft id, so
confirmed revision history plus this context preserves source and old/new lineage.
Later manual edits are detectable because the stored post-apply method fingerprint no
longer matches the persisted draft rows. No new confirmed-Matrix column is planned.

## Future May Touch

Backend product, exact or bounded hunks only:

- `backend/domain/models.py`
- `backend/domain/project_matrix_draft_models.py`
- `backend/infrastructure/storage/models.py`
- `backend/infrastructure/storage/models_project_matrix_draft.py`
- `backend/infrastructure/storage/repositories/external_resources.py`
- `backend/infrastructure/storage/repositories/project_matrix_draft.py`
- create `backend/infrastructure/storage/standard_record_method_sync_schema_migration.py`
- `backend/infrastructure/storage/database.py` import/call only
- `backend/infrastructure/office/excel_workbook_gateway.py`
- `backend/infrastructure/office/excel_com_readonly_tabular_gateway.py`
- `backend/infrastructure/office/office_facade.py`
- `backend/application/external_resource_service.py`
- `backend/application/external_excel_read_service.py`
- create `backend/modules/test_plan/standard_method_version_parser.py`
- create `backend/application/matrix_method_version_sync_service.py`
- create `backend/api/routes_matrix_method_version_sync.py`
- `backend/api/routes_external_resources.py`
- `backend/api/routes_external_excel_resources.py`
- `backend/api/main.py` route registration only
- `backend/api/dependencies.py` exact provider wiring only
- `backend/application/matrix_editor_session_service.py` exact audit-context threading
  only
- `backend/api/routes_matrix_editor_session.py` exact optional context DTO threading
  only

Frontend product, exact or bounded hunks only:

- `frontend/src/api/client.ts` exact DTO/client additions
- `frontend/src/pages/SettingsPage.tsx`
- `frontend/src/features/settings/SettingsExternalResourcesPanel.tsx`
- `frontend/src/features/settings/settingsSelectors.ts`
- create `frontend/src/features/matrix-editor/MatrixMethodVersionSyncPanel.tsx`
- create `frontend/src/features/matrix-editor/useMatrixMethodVersionSync.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` narrow composition
  hunk only
- `frontend/src/workbench.css` exact Matrix sync panel and Settings field styles only

Focused tests may create bounded parser/service/component/integration modules and make
focused additions to the existing External Resource, Office gateway, Matrix session,
Settings, and API tests named in the plan. Governance is limited to TASK_366B files and
the exact board hunk.

## Must Not Touch

- Existing generic Test Record writer/layout/route/button semantics.
- TASK_360B/TASK_361D specialized workbook projection, generation, or artifact paths.
- Confirmed Matrix repository/schema except read-only consumption and existing confirm
  behavior.
- Matrix parser/import rules, Step quantities, Contact Measurement Plan, Fee rules,
  pricing, export, LTR/public-drive writes, Project lifecycle, Report, StepInstance.
- VBA/XLSM execution, workbook conversion, Save/SaveAs, copy/delete, or real file write.
- Equipment calibration semantics beyond regression.
- Release/dist, packaging, unrelated Settings/LTR work, or external dirty residuals.

## Locked Paths

- `data/**`, real operator/public-drive workbooks, and the discovery attachment.
- LTR gateways/transactions/write services.
- Fee, workbook output, Generic Test Record, Report, Matrix parser/import, and contact
  authority modules.
- `.agents/**`, `docs/project_management/**`, `dist_release/**`, `packaging/**`.
- Remote push and unrelated worktree paths.

## Acceptance Criteria

1. Legacy or new Standard record config with stored `NULL` displays effective
   `认可标准`; an explicit valid sheet name saves independently from the path and
   survives reload.
2. Omitted `worksheet_name` preserves an existing Standard value; explicit `null` and
   whitespace-only input reset Standard rows to stored `NULL` and effective `认可标准`;
   invalid characters/length remain typed no-write failures; non-Standard resources
   reject any supplied worksheet field.
3. Missing or ambiguous workbook sheet matches return clear typed errors without
   source-file writes.
4. Disposable `.xlsx` and fake-COM `.xls` fixtures with title row 1, header row 2,
   `文 件 编 号` in column B, and data row 3+ return equivalent catalog rows.
5. Existing TASK_366A `.xlsx` default-layout and `.xls` read-only/no-write behavior
   does not regress.
6. Parser examples cover case, spaces, slash/hyphen variants, immediate revision,
   year handling, duplicate same revision, conflicting revisions, no match, multiple
   cores, and row-state reset.
7. Preview is zero-write and reports current/proposed values and typed status for every
   Matrix row.
8. Apply changes only explicitly selected safe rows in the current draft, preserves
   every non-method field, persists bounded source context, and rejects stale
   source/target/fingerprint with `409` and no write.
8. Before `Confirm Matrix`, confirmed Matrix and generic Test Record remain unchanged.
   After confirmation, the new confirmed revision and generic Test Record show the
   updated methods.
9. Downgrades, ambiguities, missing/malformed catalog entries, and invalid draft
   lineage cannot be applied.
10. No source workbook, real DB, real file, Generic Test Record file, or specialized
    workbook is written during deterministic tests.

## Definition Of Ready

Complete/accepted. Reviewer plan and implementation re-gates, Developer implementation,
QA B3 re-gate, and Integrator package isolation are complete for the frozen TASK_366B
scope: worksheet-name
field-presence/reset/default behavior, additive migration, explicit `.xlsx`/COM Chinese
catalog layout, canonical saved signature, method-only root+row CAS, typed no-write
`400/404/409`, preview zero-write, selected apply to editable Matrix draft, existing
Confirm Matrix publication, focused bounded tests, and existing May Touch/locks.

## Next Legal Role

User/Orchestrator only. This closeout does not activate a later product lane.
