# TASK_345D QA Evidence

Status: qa_pass
Task: TASK_345D_WORKBENCH_LIFECYCLE_PRIMARY_ACTION_UI
Lane: workbench-lifecycle-primary-action-ui
Role: QA / Smoke Owner
Date: 2026-06-29

## Summary

QA reran the required focused frontend suite, frontend build, static scope/copy scans, and browser-rendered Workbench smoke for currently available local lifecycle fixtures.

QA gate: pass.

Recommended next role: Integrator packaging/readiness.

Residual risk: the current local dataset has no closed lifecycle rows, so closed Completed and closed other-reason Workbench states could not be real-browser smoked without mutating local data. This is recorded as a non-blocking data fixture gap because focused component/model coverage includes closed Completed and closed other Activate behavior, and this QA pass was not authorized to create lifecycle fixture data.

## Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `$impeccable` product context
- Browser control skill instructions
- `tasks/TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT.md`
- `docs/task_345a_project_lifecycle_business_model_contract_plan.md`
- `docs/lane_evidence/TASK_345A_project-lifecycle-business-model-contract_planner.md`
- `tasks/TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API.md`
- `docs/task_345b_project_lifecycle_activation_model_api_plan.md`
- `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_developer.md`
- `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_reconciliation_planner.md`
- `tasks/TASK_345C_PROJECT_LIFECYCLE_WRITE_GUARD_RULES.md`
- `docs/task_345c_project_lifecycle_write_guard_rules_plan.md`
- `docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_developer.md`
- `docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_reconciliation_planner.md`
- `tasks/TASK_345D_WORKBENCH_LIFECYCLE_PRIMARY_ACTION_UI.md`
- `docs/task_345d_workbench_lifecycle_primary_action_ui_plan.md`
- `docs/lane_evidence/TASK_345D_workbench-lifecycle-primary-action-ui_planner.md`
- `docs/lane_evidence/TASK_345D_workbench-lifecycle-primary-action-ui_reconciliation_planner.md`
- `docs/lane_evidence/TASK_345D_workbench-lifecycle-primary-action-ui_developer.md`
- Current Workbench lifecycle UI/API client tests and fixtures by focused validation.

Board note:

- `docs/task_board.md` still showed TASK_345D as implementation-authorized / pending implementation during QA read, while the delegation supplied `Reviewer implementation gate passed` and QA routing. QA proceeded from the newer Orchestrator delegation and recorded the mismatch.

## Validation Commands

Focused frontend tests:

```powershell
cd frontend
npm test -- --run projectLifecycleReadonlyModel projectWorkbenchLifecycleSelectors ProjectWorkbenchCloseConfirmation useProjectWorkbenchModel ProjectWorkbenchLayout projectWorkbenchShellModel --watch=false
```

Observed:

- Test files: 6 passed
- Tests: 81 passed

Frontend build:

```powershell
cd frontend
npm run build
```

Observed:

- Build passed.
- Existing Vite chunk-size warning only.

Package diff check:

```powershell
git diff --check -- frontend/src/api/client.ts frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.ts frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.test.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts frontend/src/features/project-workbench/projectWorkbenchShellModel.ts frontend/src/features/project-workbench/projectWorkbenchShellModel.test.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.tsx frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.test.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts docs/lane_evidence/TASK_345D_workbench-lifecycle-primary-action-ui_developer.md
```

Observed:

- Passed with LF/CRLF working-copy warnings only.

## Static Scans

Workbench old-copy scan:

```powershell
rg -n "Close as completed|Close administratively|Administrative reason|\badministrative\b|permanent archive|Archive project|Resume project|Stop project|Reopen project|close_completed|closed_administrative|closed_completed" frontend/src/features/project-workbench frontend/src/features/project-lifecycle -g "*.ts" -g "*.tsx" -g "!*.test.ts" -g "!*.test.tsx"
```

Observed:

- No matches.

Projects registry mutation-helper scan:

```powershell
rg -n "stopProjectLifecycle|resumeProjectLifecycle|activateProjectLifecycle|closeProjectLifecycle|closeProjectCompletedLifecycle|closeProjectAdministrativeLifecycle|deleteTemporaryProject|previewTemporaryProjectDelete|Close project|Activate project|Stop project|Resume project|Close as completed|Close administratively" frontend/src/pages/ProjectListPage.tsx frontend/src/features/projects-registry -g "*.ts" -g "*.tsx"
```

Observed:

- No matches.

Future-scope scan:

```powershell
rg -n "StepInstance|Report generation|AI review|permissions|LAN|multi-user|public-drive LTR|Apply LTR|Register LTR|Office workbook|LTR workbook" frontend/src/features/project-workbench frontend/src/api/client.ts -g "*.ts" -g "*.tsx"
```

Observed:

- Matches were limited to static test guard assertions and the existing safety copy `Delete this mistaken temporary project from ConnLab? This does not touch public-drive files or LTR workbooks.`
- No active StepInstance, Report, AI, permissions, LAN/server, multi-user, public-drive LTR authority, Apply/Register LTR, or Office/LTR workbook implementation surfaced in TASK_345D production UI paths.

Forbidden-scope status:

- No modified `backend/**`.
- No modified `frontend/src/features/projects-registry/**`.
- No modified `frontend/src/pages/ProjectListPage.tsx`.
- `frontend/src/api/client.ts` is modified as an allowed TASK_345D API-client helper path.
- `docs/task_board.md` was already dirty and was not edited by QA.

## Local Data Sweep

Read-only registry/lifecycle sweep:

- Registry rows swept: 46
- Lifecycle summary: `active = 21`, `stopped = 25`, `closed = 0`

Available real browser fixtures:

Active registered:

- Project ID: `7c55618e2acc41bd9973b7e4eaaf7e0f`
- Display ID: `DL-2026-05-002`
- Lifecycle: `active`
- Status: `ltr_registered`
- Allowed actions: `stop,close`

Stopped registered:

- Project ID: `1ee3f8389c2243b0b324247ae5555bd3`
- Display ID: `dl-2026-04-001`
- Lifecycle: `stopped`
- Status: `cancelled`
- Readonly: `true`
- Allowed actions: `activate,resume,close`

Temporary/no-LTR:

- Project ID: `c4f39233742949febda453a428bd5e42`
- Display ID: `TMP-C4F39233`
- Lifecycle: `active`
- Status: `draft`
- Allowed actions: `stop,close`

Unavailable real browser fixtures:

- Closed Completed project: unavailable in current local data.
- Closed other-reason project: unavailable in current local data.

QA did not create closed data because this gate was not authorized to mutate local project lifecycle state or create fixture data.

## Browser Smoke

Browser method:

- Temporary local system Chrome headless screenshots.
- CDP interaction for opening inline Close/Activate forms.
- No confirm/submit action was performed.

Screenshot artifacts:

- `docs/lane_evidence/artifacts/TASK_345D_qa/active_registered_DL-2026-05-002.png`
- `docs/lane_evidence/artifacts/TASK_345D_qa/active_close_form_DL-2026-05-002.png`
- `docs/lane_evidence/artifacts/TASK_345D_qa/stopped_registered_dl-2026-04-001.png`
- `docs/lane_evidence/artifacts/TASK_345D_qa/stopped_activate_form_dl-2026-04-001.png`
- `docs/lane_evidence/artifacts/TASK_345D_qa/temporary_no_ltr_TMP-C4F39233.png`
- `docs/lane_evidence/artifacts/TASK_345D_qa/temporary_close_form_TMP-C4F39233.png`

Active registered smoke:

- Exactly one visible primary lifecycle action: `Close project`.
- No visible `Activate project`, `Resume project`, `Stop project`, `Close as completed`, `Close administratively`, `Administrative reason`, or `Archive project`.
- Clicking `Close project` opened an inline `Confirm close project` form.
- Business reasons present: `Completed`, `Failed`, `Cancelled`, `Cannot test`, `Duplicate`, `Other`.
- No user-facing `administrative`.

Stopped registered smoke:

- Exactly one visible primary lifecycle action: `Activate project`.
- No visible `Close project`, `Resume project`, `Stop project`, `Close as completed`, `Close administratively`, `Administrative reason`, or `Archive project`.
- Clicking `Activate project` opened an inline `Confirm activate project` form.
- Form copy: `Record why project work should continue before editing is restored.`
- No mutation was submitted.

Temporary/no-LTR smoke:

- No unauthorized `Apply LTR` or `Register LTR` implementation/entrypoint was visible.
- Visible lifecycle actions were `Delete temporary project` and `Close project`.
- `Close project` matched exactly one button and opened the same unified close form.
- Business reasons present: `Completed`, `Failed`, `Cancelled`, `Cannot test`, `Duplicate`, `Other`.
- No user-facing `administrative`, no old completed/admin split labels, and no Apply/Register LTR authority wording.
- No mutation was submitted.

Closed Completed / closed other smoke:

- Not browser-smoked because current local data has zero closed lifecycle rows.
- Non-blocking residual risk: focused tests cover closed Completed and closed other Activate behavior, including old copy exclusion, but a real closed-data fixture is still needed for full manual/browser coverage in a future fixture or QA closeout lane.

## QA Result

QA gate: pass.

Blocking findings: none.

Recommended next role: Integrator packaging/readiness.
