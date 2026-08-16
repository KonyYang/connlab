# TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP

Status: `ready_for_user_approval`

Implementation authorization: none until the User approves the exact committed Plan and approved-request contract.

## Goal

When the resolved administrator configuration file is entirely absent, ConnLab creates its parent directory when needed, exclusively publishes one complete deterministic UTF-8 TOML file, and then reads it normally:

```toml
[ltr_workbook]
modify_password = "DGLAB"
```

`DGLAB` is an approved public business default, not a secret. Development continues using `<base_dir>\connlab.admin.toml`; packaged execution continues using `%PROGRAMDATA%\ConnLab\config\connlab.admin.toml`; explicit `CONNLAB_ADMIN_CONFIG_PATH` remains authoritative.

## Frozen Behavior

- Bootstrap only when the resolved real administrator file is absent.
- Existing files, including explicit blank, malformed, unreadable, or customized files, are never overwritten, rewritten, supplemented, migrated, or repaired.
- Concurrent first start cannot expose partial content or overwrite a competing winner.
- Filesystem failure is actionable and path-bearing without exposing a password or falling back elsewhere.
- Explicitly present `CONNLAB_LTR_WORKBOOK_PASSWORD` remains highest precedence, including empty; `connlab.local.toml` password remains inert.
- Packaged startup never copies development/local configuration or the release example into ProgramData.
- No Settings/API password editor, database/schema, workbook, numbering, transaction, lock, backup, public-drive authority, release publication, or deployment behavior is added.

## Exact May Touch

Implementation and tests:

1. `backend/shared/config.py`
2. `connlab.admin.example.toml`
3. `tests/unit/test_config.py`
4. `tests/unit/test_desktop_packaged_runtime_paths.py`
5. `tests/unit/test_desktop_release_scripts.py`

Governance and evidence:

6. `tasks/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP.md`
7. `docs/task_ltr_workbook_public_default_admin_config_bootstrap_plan.md`
8. `docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_planner.md`
9. `docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_developer.md`
10. `docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_reviewer.md`
11. `docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_qa.md`
12. `docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_integrator.md`
13. `docs/task_board.md`

`.gitignore`, `backend/desktop/runtime_paths.py`, and both release build scripts are inspected and tested but remain unchanged because their current contracts already match the request.

## Acceptance

- Missing development and disposable packaged files are created with exact complete UTF-8 bytes and load `DGLAB` immediately.
- Two concurrent first loads both read one complete final file.
- Existing custom and blank files are byte-preserved; explicit environment nonblank/blank values still win; local password stays inert.
- Unwritable/unsupported targets fail clearly without alternate-path fallback or password disclosure.
- The repository example contains the public default while releases still ship only the example.
- All tests use disposable roots and never touch real ProgramData, development config, public drives, workbooks, installed releases, or user configuration.

## Approval Gate

This is planned/complex because it changes administrator configuration authority, persistent external file creation, and a public business default. Implementation requires explicit approval of the committed Plan ref and approved-request SHA-256.
