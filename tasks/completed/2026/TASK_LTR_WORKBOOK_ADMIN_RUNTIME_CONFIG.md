# TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG

Status: `ready_for_user_approval`

Implementation authorization: none until the User approves the exact committed Plan and approved-request contract.

## Goal

Establish one administrator-managed runtime configuration contract for the LTR workbook modify password while:

- keeping the password invisible and immutable through the ordinary ConnLab Settings UI and public Settings API;
- shipping a secret-free administrator template with both packaged release variants;
- keeping the real deployment file outside replaceable release folders;
- preserving the existing `CONNLAB_LTR_WORKBOOK_PASSWORD` override and all runtime workbook password consumers;
- making the file contract reusable by a future network deployment without implementing that deployment;
- removing the obsolete hidden Settings password component, state, typed client calls, public API routes, and write service.

## Confirmed Administrator Configuration Contract

### Committed and shipped template

The sole committed password template is:

```text
connlab.admin.example.toml
```

It contains only the current task's administrator setting:

```toml
[ltr_workbook]
modify_password = ""
```

Both release build scripts copy this secret-free file to:

```text
<release-folder>\config\connlab.admin.example.toml
```

The release copy is documentation/bootstrap material only. It never contains a real password and is safe for a later release to replace.

### Mutable deployment-specific file

The real administrator-managed file is:

```text
%PROGRAMDATA%\ConnLab\config\connlab.admin.toml
```

Packaged desktop and packaged local-browser runtimes set the default `CONNLAB_ADMIN_CONFIG_PATH` to that exact path without overwriting an already supplied environment value.

The executable does not create, copy, update, migrate, delete, or overwrite the mutable administrator file. Deployment administrators copy the shipped template outside the release directory, enter the real value, and apply the organization's file-permission policy. Copying or replacing a release folder therefore cannot overwrite the real secret.

For repository/development execution, the default is:

```text
<base_dir>\connlab.admin.toml
```

That mutable filename is ignored by Git. `CONNLAB_ADMIN_CONFIG_PATH` may select another absolute or base-directory-relative location.

### Future network reuse

A future server deployment may point `CONNLAB_ADMIN_CONFIG_PATH` at a deployment-managed file using the same TOML section/key and may retain the same environment override. This task adds no server, LAN, credential store, secret distribution, permissions service, or network configuration implementation.

## Exact Precedence

The current effective precedence is environment over file:

1. `CONNLAB_LTR_WORKBOOK_PASSWORD`, including an explicitly present blank value;
2. administrator file `[ltr_workbook].modify_password`;
3. unset (`None`).

This precedence remains unchanged in meaning. The only source relocation is from ordinary `connlab.local.toml` to the administrator contract. `[ltr_workbook].modify_password` in `connlab.local.toml` becomes inert and is not automatically copied, displayed, logged, deleted, or rewritten.

All other existing LTR workbook settings remain in the operator-local configuration and keep their current environment override behavior.

## Removed Surface

Delete or remove:

- `frontend/src/pages/SettingsPage.tsx` password status/save state, loading call, handler, props, and imports;
- `SettingsExternalResourcesPanel` password props, hidden feature flag, password row component, and supporting state;
- the typed `LtrWorkbookPasswordStatus`, `getLtrWorkbookPasswordStatus`, and `updateLtrWorkbookPassword` client contract;
- password-only CSS selectors;
- the public `GET` and `PUT /api/settings/ltr-workbook-password` routes and their router registration;
- `LtrWorkbookPasswordSettingsService` and its obsolete service tests.

The ordinary Settings page continues to manage only its existing non-secret external resource/path fields.

## Preserved Runtime Read Path

Keep `LtrWorkbookSettings.modify_password` and the existing dependency/gateway consumers unchanged. `Settings.load()` still supplies the effective password to:

- LTR workbook write/transaction gateways;
- Basic Information synchronization;
- read-only workbook opening;
- specified-workbook preview and compatibility diagnostics.

Safe summaries continue to expose only `modify_password_configured`, never the value.

## Exact May Touch

1. `.gitignore`
2. `backend/api/main.py`
3. `backend/api/routes_settings.py` (delete)
4. `backend/application/ltr_workbook_password_settings_service.py` (delete)
5. `backend/desktop/runtime_paths.py`
6. `backend/shared/config.py`
7. `connlab.admin.example.toml` (create)
8. `connlab.local.example.toml`
9. `docs/packaging_notes.md`
10. `packaging/README_FOR_BROWSER_OPERATOR.md`
11. `packaging/README_FOR_OPERATOR.md`
12. `scripts/build_windows_browser_release.ps1`
13. `scripts/build_windows_desktop_release.ps1`
14. `frontend/src/api/client.ts`
15. `frontend/src/pages/SettingsPage.tsx`
16. `frontend/src/features/settings/SettingsExternalResourcesPanel.tsx`
17. `frontend/src/settings.css`
18. `frontend/src/features/settings/SettingsStandardRecordSheet.test.tsx`
19. `frontend/src/pages/SettingsPage.test.tsx` (create)
20. `tests/unit/test_config.py`
21. `tests/unit/test_desktop_packaged_runtime_paths.py`
22. `tests/unit/test_desktop_release_scripts.py`
23. `tests/unit/test_packaging_notes.py`
24. `tests/integration/test_ltr_workbook_admin_runtime_config_api.py` (create)
25. `tests/unit/test_ltr_workbook_password_settings_service.py` (delete)
26. `tasks/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG.md`
27. `docs/task_ltr_workbook_admin_runtime_config_plan.md`
28. `docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_planner.md`
29. `docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_developer.md`
30. `docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_reviewer.md`
31. `docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_qa.md`
32. `docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_integrator.md`
33. `docs/task_board.md`

No other product, test, packaging, governance, evidence, or generated path is authorized.

## Acceptance Criteria

1. The committed and shipped administrator template contains an empty placeholder and no real secret.
2. Packaged desktop and browser runtimes resolve the mutable administrator file to `%PROGRAMDATA%\ConnLab\config\connlab.admin.toml`.
3. Release builds place only the secret-free example under the release folder and never copy to or overwrite the mutable ProgramData file.
4. Repository/development execution resolves the default administrator file to `<base_dir>\connlab.admin.toml`; explicit `CONNLAB_ADMIN_CONFIG_PATH` remains supported.
5. `CONNLAB_LTR_WORKBOOK_PASSWORD` remains higher precedence than the administrator file; an explicitly blank environment value continues to suppress the file value.
6. A local operator file password is ignored; all unrelated `connlab.local.toml` LTR settings continue to load.
7. Existing runtime LTR workbook consumers receive the effective administrator/env password without changing transaction, workbook, public-drive, backup, or locking behavior.
8. Neither OpenAPI nor direct requests expose `GET` or `PUT /api/settings/ltr-workbook-password`.
9. Settings renders and loads without a password request, password input, reveal toggle, update action, password status, or password-related error.
10. Existing external resource paths and Standard record worksheet settings continue to work.
11. Existing real deployment files are never created, changed, migrated, printed, committed, or deleted by implementation or tests.
12. Frontend tests/build, backend config/API/runtime-path tests, runtime-consumer regressions, Python compilation, diff checks, whitelist checks, and the approved browser smoke pass.

## Risks

- Existing workstations that rely only on `connlab.local.toml` for the password require an administrator-controlled one-time copy into the new file before using LTR workbook operations.
- A missing or unreadable administrator file leaves the effective password unset and existing workbook operations fail through their current actionable missing/invalid-password paths.
- `%PROGRAMDATA%` permissions are deployment-owned. ConnLab documents the boundary but does not introduce an installer or ACL manager.
- Removing the public route is an intentional API contract break for an obsolete ordinary-user surface.
- Broad edits to `backend/shared/config.py`, `runtime_paths.py`, `backend/api/main.py`, or the large typed client could absorb unrelated behavior; implementation must keep hunks bounded.

## Rollback

Rollback reverts this task's repository changes only. It must not delete or rewrite `%PROGRAMDATA%\ConnLab\config\connlab.admin.toml`, a development `connlab.admin.toml`, or any legacy local configuration. If rollback temporarily restores the former local-config/API contract, administrators decide separately whether to restore a local value; no automated secret transfer is authorized.

## Non-Goals

- No future network/server deployment.
- No Windows Credential Manager, vault, encryption, installer, ACL automation, secret rotation, or remote secret distribution.
- No unrelated administrator defaults, paths, database values, schema, migration, or persistence.
- No LTR workbook content, authority, number allocation, transaction, lock, backup, write, or public-drive workflow change.
- No redesign of Settings and no new administrator UI.
- No release publication, push, or external deployment mutation.

## Approval Gate

This is a planned/complex authority and API-contract task. Implementation requires explicit User approval of the exact committed Plan ref and canonical `connlab.personal-task-approved-request` version 1 payload.
