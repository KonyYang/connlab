# TASK_346G Workbench Project Folder Open Action Wiring - Planner Evidence

Status: ready_for_review
Date: 2026-07-01
Role: Planner
Task: `TASK_346G_WORKBENCH_PROJECT_FOLDER_OPEN_ACTION_WIRING`
Lane: `workbench-project-folder-open-action-wiring`

## 1. Current Phase / Task / Lane

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current task: `TASK_346G_WORKBENCH_PROJECT_FOLDER_OPEN_ACTION_WIRING`.
- Current lane: `workbench-project-folder-open-action-wiring`.
- Current role: Planner.
- Allowed reason: `TASK_346E_FOLDER_WORKFLOW_INTEGRATION_QA` is complete/accepted in `docs/task_board.md`, and Orchestrator/User requested formal planning-first lane creation for the discovered `Project folder -> Open` gap.
- Stop point: Reviewer plan gate.

## 2. Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `$impeccable` context via `node .agents/skills/impeccable/scripts/load-context.mjs`
- `PRODUCT.md`
- `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- TASK_346A/B/F/C/D/E task, plan, evidence, QA, and board context
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- read-only code search for open-folder / Explorer / clipboard capabilities
- current `git status --short`

## 3. Discovery Gate Result

Confirmed by user / Orchestrator:

- User observed `Project folder -> Open` disabled for project `72fbbfa290294da9a507344b68ff900f`.
- Local folder exists and backend public-folder context returns an existing `local_official_folder_path`.
- Legacy `/folder/latest` is not reliable for this fixture.
- Root cause is a TASK_346D follow-up gap: Sync/Submit/Pull are wired, but Project folder Open is still placeholder/old-model.
- This turn must create a formal planning-first lane only.

Confirmed by repository evidence:

- `docs/task_board.md` shows `TASK_346E` complete/accepted and no active implementation lane.
- `projectFolderTaskSelectors.ts` hard-codes `Project folder` `actionTarget: null`.
- `useProjectWorkbenchModel.ts` derives `folderReady` from old `folder_created` / `officialWorkspacePreview` logic.
- `ProjectWorkbenchLayout.tsx` still routes `actionTarget === "folder"` to create/update folder, not open existing folder.
- `frontend/src/api/client.ts` contains the accepted `local_official_folder_path` DTO fields.
- No existing safe open-folder bridge or Explorer launcher was found.

Planner decision:

- Create `TASK_346G_WORKBENCH_PROJECT_FOLDER_OPEN_ACTION_WIRING`.
- Keep status as planned/ready for Reviewer plan gate.
- Plan a narrow vertical slice that may include frontend wiring, clipboard fallback, and a tiny non-mutating backend open-folder bridge if Reviewer accepts it as necessary.
- Do not authorize implementation in this Planner pass.

Definition of Ready for Reviewer plan gate: satisfied.

Blocker questions: none.

## 4. Created / Updated Files

- `tasks/TASK_346G_WORKBENCH_PROJECT_FOLDER_OPEN_ACTION_WIRING.md`
- `docs/task_346g_workbench_project_folder_open_action_wiring_plan.md`
- `docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_planner.md`
- `docs/task_board.md`

## 5. May Touch / Must Not Touch / Locked Paths

See the task and plan files for the full lane schema.

Key May Touch summary:

- Workbench Folder Actions frontend files needed to enable and handle the Open action.
- `frontend/src/api/client.ts` only for a narrow open-local-project-folder helper.
- A tiny backend open-folder bridge only if Reviewer accepts it as non-mutating and necessary.
- TASK_346G docs/evidence/board through normal lane flow.

Key locks:

- no Sync/Submit/Pull behavior changes;
- no public folder resolver changes;
- no real folder create/move/delete/copy/overwrite;
- no LTR workbook or public-drive authority writes;
- no Projects registry, Matrix Editor, StepInstance, Report, AI, permissions, LAN/server, multi-user;
- no Settings/LTR helper residuals, release/packaging residuals, `.agents/**`, `docs/project_management/**`, or `temp_agents_stash.md`.

## 6. Validation / Merge Gate

Reviewer plan gate should confirm:

- the lane is correct after TASK_346D/E;
- `local_official_folder_path` is the source of truth for local folder availability;
- browser fallback and optional desktop/backend bridge behavior are safe;
- all locks are concrete.

Future implementation validation should include focused frontend tests, build, optional mocked backend tests, browser smoke on the reported project URL, no-real-folder-mutation scan, and forbidden-scope checks.

## 7. Validation Performed By Planner

Docs diff check:

```powershell
git diff --check -- docs/task_board.md tasks/TASK_346G_WORKBENCH_PROJECT_FOLDER_OPEN_ACTION_WIRING.md docs/task_346g_workbench_project_folder_open_action_wiring_plan.md docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_planner.md
```

Result: passed with the existing `docs/task_board.md` LF/CRLF working-copy warning only.

Trailing whitespace scan:

```powershell
rg -n "[ \t]$" docs/task_board.md tasks/TASK_346G_WORKBENCH_PROJECT_FOLDER_OPEN_ACTION_WIRING.md docs/task_346g_workbench_project_folder_open_action_wiring_plan.md docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_planner.md
```

Result: no matches.

Source-of-truth reference scan:

```powershell
rg -n "TASK_346G_WORKBENCH_PROJECT_FOLDER_OPEN_ACTION_WIRING|workbench-project-folder-open-action-wiring|TASK_346G Workbench Project Folder" docs/task_board.md tasks/TASK_346G_WORKBENCH_PROJECT_FOLDER_OPEN_ACTION_WIRING.md docs/task_346g_workbench_project_folder_open_action_wiring_plan.md docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_planner.md
```

Result: expected references present in task, plan, evidence, and board.

Targeted status note:

- New/changed TASK_346G Planner files are docs/board/evidence only.
- Existing unrelated dirty residuals remain visible in status, including Settings/LTR helper files, intake/parser/Office gateway files, backend settings/release files, packaging/release files, release tests/scripts, and `temp_agents_stash.md`.
- Those residuals are explicitly excluded from TASK_346G and were not adopted into this lane.

## 8. Next Role

Recommended next role: Reviewer plan gate for `TASK_346G_WORKBENCH_PROJECT_FOLDER_OPEN_ACTION_WIRING`.

Planner gate: ready.
