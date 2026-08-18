# TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP Plan

Status: `ready_for_user_approval`

Planner: `gpt-5.6-sol / medium / risk:authority`

Developer, Reviewer, QA and Integrator are all `gpt-5.6-sol / medium / risk:authority`.

## 1. Root Cause And Existing Contracts

`Settings.load()` resolves and reads administrator configuration through `backend/shared/config.py::_load_admin_config`, but the loader returns an empty mapping when the file is absent. Thus a clean development or packaged installation never establishes the approved public workbook default.

Existing surrounding behavior is already correct: development uses `<base_dir>\connlab.admin.toml`; packaged runtime defaults to `%PROGRAMDATA%\ConnLab\config\connlab.admin.toml`; explicit administrator paths are preserved; the real file is Git-ignored; releases ship only the example; explicit password environment presence including blank already wins; local-config password is inert; safe summaries expose only a configured Boolean. Runtime path selection, release scripts, UI, API, workbook services, database and public-drive logic remain unchanged.

## 2. Single Bootstrap Seam

Modify only `_load_admin_config` and tightly scoped private helpers/constants in `backend/shared/config.py`:

1. Resolve the administrator path exactly as today.
2. If it exists, write nothing and parse normally.
3. If absent, create missing parents, then exclusively create a unique temporary file in the same directory.
4. Write exactly `[ltr_workbook]\nmodify_password = "DGLAB"\n` as UTF-8 without BOM, flush, synchronize, and close.
5. Publish the completed file through an atomic exclusive same-filesystem hard-link operation that cannot replace an existing destination.
6. If another process wins publication, delete only this invocation's temporary name and read the winner normally.
7. After successful publication, delete the temporary name and parse the final file normally.
8. For every non-race filesystem failure, raise an actionable administrator-config error containing the path and failed operation but no password value. Never use truncate/write, overwrite-capable replace/rename, template copying, alternate-path fallback, or in-memory default restoration.

Unsupported exclusive publication is fail-closed. Existing blank, malformed or unreadable files remain operator-owned and receive no automatic repair.

## 3. Precedence And Packaging

Effective precedence remains: explicitly present `CONNLAB_LTR_WORKBOOK_PASSWORD` (including empty), administrator file, then unset. Bootstrap establishes a missing administrator file but does not weaken environment presence semantics. `connlab.local.toml` password remains inert.

`connlab.admin.example.toml` changes to the public `DGLAB` value. Both Windows release scripts continue copying only `config\connlab.admin.example.toml`; they do not create ProgramData or copy development/local configuration. `backend/desktop/runtime_paths.py`, `.gitignore`, and both release scripts remain byte-unchanged.

## 4. Exact Allowlist

Implementation and tests:

- `backend/shared/config.py`
- `connlab.admin.example.toml`
- `tests/unit/test_config.py`
- `tests/unit/test_desktop_packaged_runtime_paths.py`
- `tests/unit/test_desktop_release_scripts.py`

Governance and evidence:

- `tasks/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP.md`
- `docs/task_ltr_workbook_public_default_admin_config_bootstrap_plan.md`
- `docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_planner.md`
- `docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_developer.md`
- `docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_reviewer.md`
- `docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_qa.md`
- `docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_integrator.md`
- `docs/task_board.md`

Expected changed-file count: `13`.

## 5. File-Level Work

- `backend/shared/config.py`: deterministic bootstrap bytes, exclusive publication helper, missing-only loader path, actionable redacted errors.
- `connlab.admin.example.toml`: public `DGLAB` default.
- `tests/unit/test_config.py`: exact development/nested-path bootstrap, environment nonblank/blank, existing nonblank/blank/malformed byte preservation, local-password inertness, concurrent first load, and filesystem-failure coverage.
- `tests/unit/test_desktop_packaged_runtime_paths.py`: disposable ProgramData composition proving exact packaged target and no development/local/example copying.
- `tests/unit/test_desktop_release_scripts.py`: public template expectation and unchanged example-only release behavior.

## 6. Frozen Validation Manifest

Developer runs all checks last on the final subject; Reviewer runs only the authority/concurrency check; QA independently runs the complete manifest once.

```json
{"schema":"connlab.validation-manifest","version":1,"task_id":"TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP","checks":[{"id":"config-bootstrap-authority","kind":"targeted","run_for":["Developer","Reviewer","QA"],"cwd":".","argv":["py","-m","pytest","tests/unit/test_config.py","-q"],"timeout_seconds":600,"permission":"pytest_temp","required":true},{"id":"packaged-path-and-release","kind":"full","run_for":["Developer","QA"],"cwd":".","argv":["py","-m","pytest","tests/unit/test_desktop_packaged_runtime_paths.py","tests/unit/test_desktop_release_scripts.py","-q"],"timeout_seconds":600,"permission":"pytest_temp","required":true},{"id":"config-bootstrap-compile","kind":"static","run_for":["Developer","QA"],"cwd":".","argv":["py","-m","py_compile","backend/shared/config.py","tests/unit/test_config.py","tests/unit/test_desktop_packaged_runtime_paths.py","tests/unit/test_desktop_release_scripts.py"],"timeout_seconds":120,"permission":"workspace","required":true}]}
```

Mechanical gates also require exact five-path implementation scope, `git diff --check`, unchanged runtime-path/release-script bytes, no real external paths in tests, no runtime password in evidence, and clean primary/task worktrees.

## 7. Acceptance And Stop Conditions

- Missing development and disposable packaged files receive exact complete UTF-8 content and load `DGLAB` in the same invocation.
- Concurrent first startup cannot truncate, partially expose, or overwrite the destination.
- Existing nonblank, blank, malformed and unreadable destinations receive zero write or repair.
- Environment presence including blank wins; local password remains inert.
- Unwritable or unsupported targets fail with a path-bearing actionable error and no fallback.
- Packaged path and example-only release shipping remain unchanged.
- No UI/API/database/workbook/public-drive or unrelated packaging behavior changes.

Stop with `SCOPE_EXPANDED` if implementation requires an unapproved path, runtime path/release-script changes, real external mutation in tests, password disclosure, or workbook/public-drive behavior changes. Rollback reverts repository changes only and never deletes an administrator file created by a deployed runtime.

## 8. Canonical Approved Request

```json
{"schema":"connlab.personal-task-approved-request","version":1,"task_id":"TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP","summary":"Bootstrap an entirely absent administrator LTR workbook config with the public DGLAB default using exclusive atomic publication while preserving existing files, precedence, development and packaged paths, and all workbook/public-drive boundaries.","kind":"planned","may_touch":["backend/shared/config.py","connlab.admin.example.toml","tests/unit/test_config.py","tests/unit/test_desktop_packaged_runtime_paths.py","tests/unit/test_desktop_release_scripts.py","tasks/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP.md","docs/task_ltr_workbook_public_default_admin_config_bootstrap_plan.md","docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_planner.md","docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_developer.md","docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_reviewer.md","docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_qa.md","docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_integrator.md","docs/task_board.md"],"expected_file_count":13,"classification_reason":"Planned/complex because application startup gains administrator-authority persistence and controlled external filesystem mutation, changes a public business default, requires race-safe exclusive publication, and needs independent Reviewer, QA, and Integrator verification.","targeted_validation":["py -m pytest tests/unit/test_config.py -q","py -m pytest tests/unit/test_desktop_packaged_runtime_paths.py tests/unit/test_desktop_release_scripts.py -q","py -m py_compile backend/shared/config.py tests/unit/test_config.py tests/unit/test_desktop_packaged_runtime_paths.py tests/unit/test_desktop_release_scripts.py","Verify the exact task diff contains only the five approved implementation/test paths and passes git diff --check.","Verify tests use only repository/disposable temporary roots and do not access or mutate real ProgramData, development administrator config, public drives, workbooks, installed releases, or user configuration.","Verify existing administrator files are byte-preserved, concurrent first loads publish one complete file, environment presence including blank stays highest precedence, local password remains inert, and filesystem failures are actionable without fallback.","Verify runtime_paths.py and both release scripts remain byte-unchanged while packaged path selection and example-only release shipping remain covered by tests."],"forbidden_categories":{"api_contract":false,"database":false,"schema_or_migration":false,"persistence":true,"authority":true,"public_drive_workflow":false,"business_rule_semantics":true,"destructive_action":false,"external_mutation":true}}
```

After approval, run one Developer -> Reviewer -> QA -> Integrator chain, locally integrate, and stop at `implemented_pending_human_review`. No push or cleanup.
