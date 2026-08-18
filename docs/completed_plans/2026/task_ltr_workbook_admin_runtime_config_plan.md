# TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG Plan

Status: `ready_for_user_approval`

Planner route: `gpt-5.6-sol / medium / risk:authority`

After approval, the serialized route is Developer -> Reviewer -> QA -> Integrator, each using `gpt-5.6-sol / medium / risk:authority`.

## 1. Repository Baseline

The current code has two overlapping password paths:

- Runtime consumption is correctly centralized in `Settings.load()` as `LtrWorkbookSettings.modify_password`, then injected into existing LTR workbook gateways and services.
- Ordinary Settings still performs a hidden password status request, retains password state/handlers, contains a dormant password editor, and exposes a public GET/PUT route backed by a file-writing application service.

The previous simple task only set `SHOW_LTR_WORKBOOK_PASSWORD_EDITOR = false`; it did not remove the data flow. The current GET response can return the effective password value, so leaving the endpoint registered would continue a public exposure even though the card is hidden.

Packaged runtime data currently lives under `%LOCALAPPDATA%\ConnLab`, and release upgrades already preserve that directory. That user-local location is appropriate for ordinary paths and data but is not a formal administrator configuration boundary.

Both build scripts assemble replaceable portable release folders. Neither currently ships a dedicated administrator template.

## 2. Frozen Configuration Design

### Schema

Create one template and runtime schema:

```toml
[ltr_workbook]
modify_password = ""
```

Do not add other administrator defaults.

### Path resolution

Add a dedicated admin-config loader to `backend/shared/config.py`:

- `CONNLAB_ADMIN_CONFIG_PATH` when present;
- otherwise `<base_dir>/connlab.admin.toml`.

Packaged startup uses `backend/desktop/runtime_paths.py` to set, with `setdefault`:

```text
CONNLAB_ADMIN_CONFIG_PATH=%PROGRAMDATA%\ConnLab\config\connlab.admin.toml
```

Use `PROGRAMDATA` when supplied and the Windows `C:\ProgramData` convention as the packaged fallback. Do not add the administrator directory to `ensure_user_directories()` and do not write the admin file at runtime.

### Password precedence

Load non-secret LTR settings from `connlab.local.toml` exactly as today, but source `modify_password` from:

```text
present CONNLAB_LTR_WORKBOOK_PASSWORD
    > administrator [ltr_workbook].modify_password
    > None
```

Use presence-aware environment lookup so an explicitly present blank value retains today's behavior and disables the file value. Do not fall back to `connlab.local.toml` for the password.

Keep `safe_summary()` unchanged.

### Upgrade behavior

- Add `connlab.admin.toml` to `.gitignore`.
- Remove `modify_password` from `connlab.local.example.toml`.
- Ship `connlab.admin.example.toml` into each release folder's `config` directory.
- Never copy the example onto `%PROGRAMDATA%`.
- Never overwrite, migrate, read back through API, log, or delete a real secret.
- Document a one-time administrator migration for deployments that previously relied on the local file. The old key remains inert until an administrator removes it.

## 3. Frontend Removal

Use a test-first bounded removal:

1. Add `SettingsPage.test.tsx` proving Settings loads through `listExternalResources()` alone and does not call a password endpoint.
2. Keep and simplify the existing panel absence assertion.
3. Remove password imports, status/saving state, concurrent status request, save handler, and password props from `SettingsPage`.
4. Remove the password props, feature flag, dormant `LtrWorkbookPasswordRow`, and its internal state from `SettingsExternalResourcesPanel`.
5. Remove the password DTO and GET/PUT functions from `frontend/src/api/client.ts`.
6. Remove only the now-unused `.settings-password-*` and `.settings-secret-*` CSS rules.

No replacement copy, panel, administrator link, or visual redesign is added. `$impeccable` product guidance therefore results in a smaller existing operational surface rather than a new settings affordance.

## 4. Backend API And Service Removal

1. Add an API regression proving both methods return `404` and the path is absent from OpenAPI.
2. Remove `settings_router` import and registration from `backend/api/main.py`.
3. Delete password-only `backend/api/routes_settings.py`.
4. Delete `LtrWorkbookPasswordSettingsService` and its obsolete unit test.

`backend/application/ltr_workbook_local_config_service.py` remains unchanged because it manages non-secret workbook path/write prerequisites and already preserves unknown keys. Its existing tests remain regression coverage.

## 5. Packaging Contract

Update both release scripts to:

1. create `<release-folder>\config` after the PyInstaller folder is placed;
2. copy `connlab.admin.example.toml` to that directory;
3. never reference, create, remove, or overwrite `%PROGRAMDATA%` or `connlab.admin.toml`.

Update release-script tests to statically verify the exact copy source/destination and absence of mutable-file operations.

Update both operator READMEs and `docs/packaging_notes.md` to distinguish:

- ordinary mutable data/path settings in `%LOCALAPPDATA%\ConnLab`;
- the administrator password file in `%PROGRAMDATA%\ConnLab\config`;
- the release-local secret-free template;
- administrator-only provisioning and one-time upgrade migration;
- future network reuse through `CONNLAB_ADMIN_CONFIG_PATH`;
- the fact that Settings no longer manages the password.

## 6. Test-Driven Implementation Sequence

1. Extend `test_config.py` with red tests for admin-file loading, local-file password rejection, env precedence including blank, redaction, missing file, and unrelated local setting preservation.
2. Extend packaged runtime-path tests for exact ProgramData resolution, `CONNLAB_ADMIN_CONFIG_PATH` setdefault behavior, and no administrator-file creation/overwrite.
3. Add API-removal and Settings-page tests.
4. Implement the shared config and packaged path seam.
5. Remove the frontend/API/write-service chain and obsolete CSS/tests.
6. Add the template, ignore rule, build-script copy contract, and documentation.
7. Run the complete approved matrix last on the clean final subject.

## 7. Targeted Validation

### Backend and packaging

```powershell
py -m pytest tests/unit/test_config.py tests/unit/test_desktop_packaged_runtime_paths.py tests/unit/test_desktop_release_scripts.py tests/unit/test_packaging_notes.py tests/integration/test_ltr_workbook_admin_runtime_config_api.py tests/unit/test_ltr_workbook_local_config_service.py tests/unit/test_ltr_workbook_transaction_gateway.py tests/unit/test_ltr_workbook_readonly_open_gateway.py tests/unit/test_excel_com_ltr_workbook_gateway.py -q
```

Assertions must cover:

- admin file and exact deployed path;
- environment-over-file precedence, including explicitly blank environment value;
- local config password ignored while non-secret settings remain;
- existing config preservation and no ProgramData write;
- template copied by both release scripts;
- GET/PUT route and OpenAPI absence;
- effective password still reaches existing workbook gateway behavior;
- no real workbook or external configuration mutation.

### Frontend

From `frontend`:

```powershell
npm test -- --run src/features/settings/SettingsStandardRecordSheet.test.tsx src/pages/SettingsPage.test.tsx --watch=false
npm run build
```

Assertions must cover:

- no password editor, reveal control, status, or update action;
- no password API request;
- Settings external resources still load and save;
- Standard record sheet behavior remains intact.

### Python and static gates

Run `py -m py_compile` on every touched surviving Python product/test file. Then verify:

- `git diff --check`;
- exact changed-path whitelist equals the approved 33-path allowlist;
- `git diff --cached` is empty before integration staging;
- deleted modules have no remaining imports;
- `/api/settings/ltr-workbook-password` has no production/frontend occurrence;
- tracked TOML templates contain only blank password assignments;
- `connlab.admin.toml` is ignored and untracked;
- no real password appears in source, tests, docs, evidence, command output, or diff;
- no access or mutation under real `data/**`, `%PROGRAMDATA%`, public-drive paths, release installations, or real workbooks.

### Browser smoke

QA uses `$playwright` against disposable local runtime state:

- open Settings at normal desktop width and at 514 px;
- confirm the page loads without a password endpoint request or console error;
- confirm no password label/input/reveal/update/status is present;
- confirm external path controls and Standard record sheet remain reachable and do not overflow.

The smoke must not enter a secret, write an administrator file, open Excel, or touch a public-drive workbook.

## 8. Risks And Controls

- API removal is intentional and tested through OpenAPI and direct request absence.
- Password source relocation may require deployment preparation; document and fail safely rather than silently accepting a user-local fallback.
- ProgramData directory creation and ACLs belong to administrators/installers, not the application.
- The build scripts may replace only their release-local example.
- Large shared files receive narrow hunks and exact import/reference scans.
- Synthetic test sentinels may be used in memory or temporary files, but no real password may be printed or persisted in evidence.

## 9. Rollback

A code rollback reverts repository changes only. It must preserve every deployment-specific administrator file and must not migrate a value back to `connlab.local.toml`. No rollback step may delete configuration, workbooks, user data, release folders, or public-drive content.

## 10. Forbidden Categories And Non-Goals

Frozen risk flags:

- `api_contract`: true
- `database`: false
- `schema_or_migration`: false
- `persistence`: true
- `authority`: true
- `public_drive_workflow`: true
- `business_rule_semantics`: false
- `destructive_action`: true
- `external_mutation`: false

The task deletes obsolete repository code but performs no destructive deployment action. No database/schema work, future network implementation, unrelated administrator defaults, workbook behavior change, push, or release publication is authorized.

## 11. Approval And Route

Implementation begins only after the User approves the exact committed Plan ref and canonical approved-request JSON. After approval, one shared task host executes Developer -> Reviewer -> QA -> Integrator serially. Every role uses:

```text
MODEL: gpt-5.6-sol
REASONING_EFFORT: medium
MODEL_ROUTE_REASON: risk:authority
```

## 12. Canonical Approved Request

The User approval must bind this exact single-line UTF-8 JSON object:

```json
{"schema":"connlab.personal-task-approved-request","version":1,"task_id":"TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG","summary":"Establish one administrator-managed LTR workbook password runtime configuration contract with a secret-free packaged template, an upgrade-safe mutable ProgramData file, preserved environment override and runtime consumers, and removal of the ordinary Settings UI/API/write-service password chain.","kind":"planned","may_touch":[".gitignore","backend/api/main.py","backend/api/routes_settings.py","backend/application/ltr_workbook_password_settings_service.py","backend/desktop/runtime_paths.py","backend/shared/config.py","connlab.admin.example.toml","connlab.local.example.toml","docs/packaging_notes.md","packaging/README_FOR_BROWSER_OPERATOR.md","packaging/README_FOR_OPERATOR.md","scripts/build_windows_browser_release.ps1","scripts/build_windows_desktop_release.ps1","frontend/src/api/client.ts","frontend/src/pages/SettingsPage.tsx","frontend/src/features/settings/SettingsExternalResourcesPanel.tsx","frontend/src/settings.css","frontend/src/features/settings/SettingsStandardRecordSheet.test.tsx","frontend/src/pages/SettingsPage.test.tsx","tests/unit/test_config.py","tests/unit/test_desktop_packaged_runtime_paths.py","tests/unit/test_desktop_release_scripts.py","tests/unit/test_packaging_notes.py","tests/integration/test_ltr_workbook_admin_runtime_config_api.py","tests/unit/test_ltr_workbook_password_settings_service.py","tasks/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG.md","docs/task_ltr_workbook_admin_runtime_config_plan.md","docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_planner.md","docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_developer.md","docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_reviewer.md","docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_qa.md","docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_integrator.md","docs/task_board.md"],"expected_file_count":33,"classification_reason":"Planned/complex because the change intentionally removes a public API contract, relocates a persisted secret authority from ordinary local configuration to an administrator-managed deployment contract, changes packaged runtime path policy and release assembly, and crosses frontend, backend, packaging, documentation, and test boundaries.","targeted_validation":["Run focused backend configuration, packaged runtime-path, release-script, packaging-note, route-absence, local-config preservation, transaction, read-only-open, and Excel gateway pytest suites.","Run focused Settings panel and Settings page Vitest suites proving no password UI or password request while existing resource behavior remains.","Run the production frontend build.","Run py_compile for every touched surviving Python product and test module.","Verify both release scripts ship only config/connlab.admin.example.toml and never create or overwrite %PROGRAMDATA%/ConnLab/config/connlab.admin.toml.","Verify environment-over-admin-file precedence, explicit blank environment behavior, local-file password rejection, safe-summary redaction, and existing runtime password consumption.","Verify GET and PUT /api/settings/ltr-workbook-password return 404 and are absent from OpenAPI and the typed frontend client.","Verify tracked TOML templates contain only an empty password placeholder, connlab.admin.toml is ignored and untracked, and no real secret appears in source, tests, docs, evidence, or output.","Run QA browser smoke at desktop and 514px with disposable state, confirming Settings loads without password requests/UI/errors and existing resource controls remain usable.","Run git diff --check, exact changed-path whitelist, cached-diff-empty, deleted-import/reference, UTF-8, and no-real-data/config/workbook mutation checks."],"forbidden_categories":{"api_contract":true,"database":false,"schema_or_migration":false,"persistence":true,"authority":true,"public_drive_workflow":true,"business_rule_semantics":false,"destructive_action":true,"external_mutation":false}}
```
