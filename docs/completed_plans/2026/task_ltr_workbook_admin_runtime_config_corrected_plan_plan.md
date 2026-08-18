# TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN Plan

Status: `ready_for_user_approval`

Planner: `gpt-5.6-sol / medium / risk:authority`

Developer, Reviewer, QA and Integrator are all `gpt-5.6-sol / medium / risk:authority`.

## 1. Purpose

The original product implementation completed successfully and remains clean at `ff01fb1d725c98fb58a3e343cf241076853e8cfa`. The prior task was production-cancelled because its committed Plan used execution-route wording that the production evidence verifier could not parse. This corrected Plan changes no writer, verifier, protocol, product requirement, or retained implementation byte.

## 2. Reverified Retained Topology

- Branch: `codex/task-ltr-workbook-admin-runtime-config`
- Worktree: `D:\PythonProject\connlab-worktrees\task-ltr-workbook-admin-runtime-config`
- Base: `4540da65516b4c0fd2a0e7442f05ada8bfc8f917`
- Head/subject: `ff01fb1d725c98fb58a3e343cf241076853e8cfa`
- Worktree and index: clean
- The base is an ancestor of current primary and of the subject.
- The subject is not already integrated into primary.
- Base-to-subject diff: exactly the approved 25 product/test paths; `git diff --check` passes.
- Historical Developer evidence is retained but is not accepted evidence for this new Task ID.

## 3. Non-Destructive Host Reuse

After approval and its board-only durability commit:

1. Build the canonical `host_create` action.
2. Commit `begin-host` as a unique board-only transition.
3. Reactivate the existing completed host identity `/root/ltr_admin_runtime_config_host` without creating or moving a branch/worktree.
4. Reverify exact branch, worktree, base ancestry, head, and cleanliness.
5. Record the existing host with base `4540da65...`, head `ff01fb1d...`, integration target `master`, and `clean=true`.
6. Commit `record-host` as a unique board-only transition.
7. Dispatch fresh corrected-task Developer, Reviewer, QA, and Integrator invocations.

Host unavailability or any Git fact drift is a typed blocker. Do not repair or recreate resources.

## 4. Developer

Developer performs no planned product/test edit. It verifies the exact retained subject and 25-path diff, reviews the retained implementation against this Task and the original product contract, runs the complete matrix, and returns fresh corrected-task evidence. Any tracked-byte change, failed validation, secret exposure, external mutation, or scope discrepancy is `DEVELOPER_BLOCKED`; no descendant implementation commit is authorized.

## 5. Reviewer

Reviewer uses `$code-review` on the exact retained diff and fresh Developer evidence. It verifies requirement fit, administrator path/precedence, secret-free release template, upgrade-safe mutable location, complete Settings UI/client/API/service removal, preserved workbook consumers, exact scope, subject stability, evidence identity, and route headers. It runs risk-targeted tests only.

## 6. QA

QA independently runs the complete matrix once on the clean reviewed subject and performs disposable Settings browser smoke at desktop and 514 px. QA confirms no password request/UI/exposure, no real secret or external mutation, stable existing controls, exact subject, route identities, and forbidden-Luna condition.

## 7. Integrator

Integrator does not repeat the full matrix. It verifies the committed Plan path/raw SHA, 33-path authority, host facts, exact 25-path diff, fresh invocation/evidence pairing and raw hashes, same D/R/QA subject, absence of historical evidence in this task's accepted evidence list, evidence outside subject ancestry, and exact non-conflicting local merge parents/tree. Any conflict or identity/topology drift is `INTEGRATION_BLOCKED`.

## 8. Exact Allowlist

Retained product/test paths:

- `.gitignore`
- `backend/api/main.py`
- `backend/api/routes_settings.py`
- `backend/application/ltr_workbook_password_settings_service.py`
- `backend/desktop/runtime_paths.py`
- `backend/shared/config.py`
- `connlab.admin.example.toml`
- `connlab.local.example.toml`
- `docs/packaging_notes.md`
- `frontend/src/api/client.ts`
- `frontend/src/features/settings/SettingsExternalResourcesPanel.tsx`
- `frontend/src/features/settings/SettingsStandardRecordSheet.test.tsx`
- `frontend/src/pages/SettingsPage.test.tsx`
- `frontend/src/pages/SettingsPage.tsx`
- `frontend/src/settings.css`
- `packaging/README_FOR_BROWSER_OPERATOR.md`
- `packaging/README_FOR_OPERATOR.md`
- `scripts/build_windows_browser_release.ps1`
- `scripts/build_windows_desktop_release.ps1`
- `tests/integration/test_ltr_workbook_admin_runtime_config_api.py`
- `tests/unit/test_config.py`
- `tests/unit/test_desktop_packaged_runtime_paths.py`
- `tests/unit/test_desktop_release_scripts.py`
- `tests/unit/test_ltr_workbook_password_settings_service.py`
- `tests/unit/test_packaging_notes.py`

Current task governance/evidence:

- `tasks/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN.md`
- `docs/task_ltr_workbook_admin_runtime_config_corrected_plan_plan.md`
- `docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_planner.md`
- `docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_developer.md`
- `docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_reviewer.md`
- `docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_qa.md`
- `docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_integrator.md`
- `docs/task_board.md`

No other path may change.

## 9. Complete Validation

Developer and QA independently run:

```powershell
py -m pytest tests/unit/test_config.py tests/unit/test_desktop_packaged_runtime_paths.py tests/unit/test_desktop_release_scripts.py tests/unit/test_packaging_notes.py tests/integration/test_ltr_workbook_admin_runtime_config_api.py tests/unit/test_ltr_workbook_local_config_service.py tests/unit/test_ltr_workbook_transaction_gateway.py tests/unit/test_ltr_workbook_readonly_open_gateway.py tests/unit/test_excel_com_ltr_workbook_gateway.py -q
```

Expected retained baseline: `62 passed`.

From `frontend`:

```powershell
npm test -- --run src/features/settings/SettingsStandardRecordSheet.test.tsx src/pages/SettingsPage.test.tsx --watch=false
npm run build
```

Expected focused baseline: `2 files / 4 tests passed`; production build passes with only the previously recorded non-blocking chunk advisory allowed.

```powershell
py -m py_compile backend/api/main.py backend/desktop/runtime_paths.py backend/shared/config.py tests/integration/test_ltr_workbook_admin_runtime_config_api.py tests/unit/test_config.py tests/unit/test_desktop_packaged_runtime_paths.py tests/unit/test_desktop_release_scripts.py tests/unit/test_packaging_notes.py
```

Static gates include exact clean HEAD/branch/worktree, exact 25-path whitelist, `git diff --check`, no cached or untracked product changes, deleted UI/client/API/service references absent, API path only in negative tests, ignored/untracked `connlab.admin.toml`, exactly one blank tracked password placeholder, and no real password or external mutation.

## 10. Safety And Failure Policy

Preserve old Task/Plan/evidence/branch/worktree exactly. No cleanup, push, archive, retire, reset, restore, stash, rebase, cherry-pick, force update, worktree movement/deletion, verifier bypass, SHA allowlist, or external mutation. Host drift, dirty state, failed validation, required code change, merge conflict, or evidence mismatch is a typed blocker and stops the task.

## 11. Stop Point

After this planning bundle and Planner callback are committed, stop at `awaiting_user_approval`. After approval, complete the fresh D/R/QA/I chain, verified local integration, and stop at `implemented_pending_human_review` until explicit User `关闭`.

## 12. Canonical Approved Request

```json
{"schema":"connlab.personal-task-approved-request","version":1,"task_id":"TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN","summary":"Complete the same LTR workbook administrator runtime configuration goal through a corrected production-parser-readable Plan and a fresh normal V2 role/evidence chain while non-destructively reusing the retained clean implementation subject ff01fb1d725c98fb58a3e343cf241076853e8cfa.","kind":"planned","may_touch":[".gitignore","backend/api/main.py","backend/api/routes_settings.py","backend/application/ltr_workbook_password_settings_service.py","backend/desktop/runtime_paths.py","backend/shared/config.py","connlab.admin.example.toml","connlab.local.example.toml","docs/packaging_notes.md","frontend/src/api/client.ts","frontend/src/features/settings/SettingsExternalResourcesPanel.tsx","frontend/src/features/settings/SettingsStandardRecordSheet.test.tsx","frontend/src/pages/SettingsPage.test.tsx","frontend/src/pages/SettingsPage.tsx","frontend/src/settings.css","packaging/README_FOR_BROWSER_OPERATOR.md","packaging/README_FOR_OPERATOR.md","scripts/build_windows_browser_release.ps1","scripts/build_windows_desktop_release.ps1","tests/integration/test_ltr_workbook_admin_runtime_config_api.py","tests/unit/test_config.py","tests/unit/test_desktop_packaged_runtime_paths.py","tests/unit/test_desktop_release_scripts.py","tests/unit/test_ltr_workbook_password_settings_service.py","tests/unit/test_packaging_notes.py","tasks/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN.md","docs/task_ltr_workbook_admin_runtime_config_corrected_plan_plan.md","docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_planner.md","docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_developer.md","docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_reviewer.md","docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_qa.md","docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_integrator.md","docs/task_board.md"],"expected_file_count":33,"classification_reason":"Planned/complex authority recovery because the task must bind a corrected committed Plan, safely reuse a retained divergent implementation branch/worktree, freshly validate an API/persistence/administrator-authority and cross-frontend/backend subject, reconstruct exact V2 evidence topology, and integrate only after independent Reviewer, QA, and Integrator gates.","targeted_validation":["Verify the retained registered branch/worktree is clean at ff01fb1d725c98fb58a3e343cf241076853e8cfa with base 4540da65516b4c0fd2a0e7442f05ada8bfc8f917 and exact ancestry.","Verify the retained base-to-subject diff contains exactly the approved 25 product/test paths, passes git diff --check, and has no tracked or untracked drift.","Run the approved backend and packaging pytest matrix; expected retained baseline is 62 passed.","Run the two focused Settings Vitest files; expected retained baseline is 2 files and 4 tests passed.","Run the production frontend build and compile all eight surviving touched Python files.","Verify deleted password UI/client/API/write-service references remain absent, the removed API path remains only in negative tests, connlab.admin.toml is ignored and untracked, and tracked TOML password assignments contain only the blank administrator placeholder.","Run QA browser smoke with disposable state at desktop and 514px, proving Settings loads without password request/UI/console error and existing resource controls remain usable.","Verify no real password, ProgramData file, deployment config, workbook, installed release, public-drive resource, or user data is read, printed, created, changed, copied, or deleted.","Verify fresh corrected-task Planner/Developer/Reviewer/QA/Integrator evidence identity, raw SHA-256, exact route, ordered primary ancestry, and unchanged subject.","At integration, verify exact non-conflicting merge parents/tree, clean states, accepted evidence refs, and absence of forbidden Git or lifecycle operations."],"forbidden_categories":{"api_contract":true,"database":false,"schema_or_migration":false,"persistence":true,"authority":true,"public_drive_workflow":true,"business_rule_semantics":false,"destructive_action":true,"external_mutation":false}}
```
