# TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG Planner Evidence

TASK_ID: TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG
ROLE: Planner
STATUS: ready_for_user_approval
MODEL: gpt-5.6-sol
REASONING_EFFORT: medium
MODEL_ROUTE_REASON: risk:authority
ATTEMPT: 1
ACTION_ID: f85e2a37bbb95a6b8a012af1c4cdaeba2667e2757b56ca895023a44fa21dba8c
PROMPT_SHA256: 2f8ae2f1a58e3c067c9d68d0641780d508483dc1b75eed45473c9a18752417f9
NEXT: User
BLOCKER: none

## Machine Preflight

- Planning HEAD: `08b1e694fe5c84de78ebb3f18ae8b41227de741b`.
- Activation parent/base: `a61b7dc559a5122093ebaaa06476c0395e63321a`.
- Board raw SHA-256 at final read-only inspection: `a17dde5e1c6b57e2509ce2386989ee63a69b45f9ac6b172a881b7757d0276b8c`.
- Board state was `running`, active task matched this Task ID, phase was `planning`, current role was `Planner`, attempt was `1`, and the pending callback action matched the `ACTION_ID` above.
- Worktree was clean.
- No repository file, board byte, Git ref, branch, worktree, external configuration, release folder, workbook, or public-drive resource was modified by Planner.

## Evidence Read

- `AGENTS.md`, active `connlab-lane-orchestrator` skill, and the relevant normative Personal Serial Workflow V2 protocol sections.
- `docs/task_board.md` and the active Planner prompt.
- `PRODUCT.md`, `DESIGN.md`, `docs/02_ARCHITECTURE_RULES.md`, and `docs/frontend_architecture_rules.md`.
- `$impeccable` product context and product-register reference, used only to constrain the frontend removal.
- Settings page, settings feature component/config/selectors/test, CSS, and typed API client.
- Password-only Settings route and application write service.
- Shared configuration loading and focused configuration/service tests.
- LTR workbook dependency wiring, compatibility/transaction/read-only consumers, and gateway tests.
- Packaged runtime paths, desktop/browser launchers, PyInstaller specs, release build scripts, operator READMEs, packaging notes, ignore rules, and packaging tests.
- Previous password-card task commit history confirming that the earlier task hid the card with a false feature flag but retained the underlying chain.

## Confirmed Repository Facts

- `Settings.load()` currently reads all LTR workbook values, including `modify_password`, from `connlab.local.toml`, with `CONNLAB_LTR_WORKBOOK_PASSWORD` passed as the higher-precedence input.
- An explicitly present blank password environment value currently resolves to `None` instead of falling back to the file.
- Existing runtime services consume only `settings.ltr_workbook.modify_password`; they do not depend on the Settings password write service.
- `safe_summary()` exposes only `modify_password_configured`.
- The public password GET response model includes an optional password field, and the service returns the effective value.
- Settings still calls the password GET endpoint during page refresh even though the password row is hidden.
- The password route module contains no unrelated routes, so its router and service can be deleted safely after removing main registration and frontend callers.
- The local config sync service manages non-secret workbook path/write prerequisites and intentionally preserves unknown keys; it does not need modification.
- Packaged mutable data currently resolves beneath `%LOCALAPPDATA%\ConnLab`, while release folders are replaceable application code.
- Desktop and browser build scripts already perform post-PyInstaller release-folder assembly and are the correct seam for shipping a visible secret-free template.
- No installer, network server deployment, ACL manager, or credential store exists.

## Planner Decision

- Classification remains planned/complex because the request changes API, persistence, administrator authority, packaging, and cross-frontend/backend behavior.
- Use one `connlab.admin.toml` schema, not a second UI or database setting.
- Keep the committed/release template separate from the mutable deployment instance.
- Place the real packaged deployment file at `%PROGRAMDATA%\ConnLab\config\connlab.admin.toml`, outside all replaceable release folders and outside ordinary per-user settings.
- Ship only `config\connlab.admin.example.toml` inside each release folder.
- Runtime must never create or overwrite the real administrator file.
- Development defaults to `<base_dir>\connlab.admin.toml`; the new `CONNLAB_ADMIN_CONFIG_PATH` provides the shared deployment seam for future server reuse.
- Preserve password precedence exactly as environment over file over unset, including the explicit-blank environment case.
- Ignore any legacy local-file password at runtime. Do not automatically migrate, delete, print, or rewrite it.
- Remove the hidden frontend chain, password-only public API, and write service while preserving the shared runtime setting and every workbook consumer.
- Keep the implementation within the exact 33-path allowlist.
- Require Developer TDD, Reviewer `$code-review`, QA `$playwright` browser smoke, and the complete approved validation matrix.
- Route every execution role as `gpt-5.6-sol / medium / risk:authority`.

## Risks And Conservative Resolutions

- Existing local-only password deployments need an administrator migration step. Silent fallback was rejected because it would retain an ordinary-user-controlled second authority.
- Automatically provisioning ProgramData was rejected because ordinary application startup must not create or overwrite administrator secrets or permissions.
- Storing the mutable file under an example `dist\config` path was rejected because release replacement could overwrite or delete it.
- Credential Manager, encryption, ACL automation, and server secret distribution were rejected as unapproved future scope.
- No unresolved product choice remains. The file schema, default paths, precedence, migration boundary, removal scope, validation, rollback, and non-goals are explicit.

## Validation Performed

- Read-only Git status, log, commit, and file inspection.
- Read-only UTF-8 repository searches for password UI/API/config/runtime consumers.
- Read-only inspection of packaging specs, scripts, runtime paths, and tests.
- No test execution was required to establish the approval-ready plan.
- No secret value was read from an external deployment file or emitted in this evidence.

## Planned Source Of Truth

- Task: `tasks/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG.md`
- Plan: `docs/task_ltr_workbook_admin_runtime_config_plan.md`
- Planner evidence: this file
- Board: `docs/task_board.md`
- Fixed later evidence:
  - `docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_developer.md`
  - `docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_reviewer.md`
  - `docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_qa.md`
  - `docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_integrator.md`

## Definition Of Ready

Satisfied for User approval. The plan fixes one administrator configuration schema, exact development and packaged paths, release-template separation, environment/file precedence, upgrade preservation, legacy-local migration boundary, frontend/API/service removal, preserved runtime consumption, exact may-touch scope, tests, browser smoke, risks, rollback, and non-goals.

Implementation is not authorized until the User approves the exact committed Plan ref and canonical approved-request contract.

NEXT: User

BLOCKER: none
