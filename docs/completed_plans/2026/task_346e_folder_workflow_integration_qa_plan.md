# TASK_346E Folder Workflow Integration QA Plan

Status: complete/accepted after Reviewer plan gate, QA execution gate, and Integrator packaging/readiness
Task: `TASK_346E_FOLDER_WORKFLOW_INTEGRATION_QA`
Lane: `folder-workflow-integration-qa`
Date: 2026-06-30
Owner Roles: Planner / Reviewer / QA / Integrator

## 1. Current Phase / Task / Lane

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current task: `TASK_346E_FOLDER_WORKFLOW_INTEGRATION_QA`.
- Current lane: `folder-workflow-integration-qa`.
- Current role: Planner.
- Allowed reason: Orchestrator/User requested the next formal TASK_346E+ Planner scan after `TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING` was accepted.
- Stop point: Reviewer plan gate. No QA execution, Developer implementation, product code change, commit, push, or real folder operation is authorized by this Planner pass.

## 2. Fact Source Summary

Sources read or re-read:

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `$impeccable` UI context, `PRODUCT.md`, `DESIGN.md`, `docs/02_ARCHITECTURE_RULES.md`, and `docs/frontend_architecture_rules.md`
- `tasks/TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT.md`
- `docs/task_346a_project_workbench_folder_actions_contract_plan.md`
- `docs/lane_evidence/DISCOVERY_project-workbench-folder-actions-workflow_planner.md`
- TASK_346B, TASK_346F, TASK_346C, and TASK_346D task/plan/evidence/QA context from repository files
- current `git status --short`

Repository-proven facts:

- `TASK_346A` accepted the Folder Actions contract and explicitly lists `TASK_346E_FOLDER_WORKFLOW_INTEGRATION_QA` after TASK_346B/C/D.
- `TASK_346B` and `TASK_346F` accepted the quiet contextual Folder Actions panel.
- `TASK_346C` accepted backend public-folder workflow APIs, preview/execute semantics, operation/audit records, submit lock, and temp-dir safety.
- `TASK_346D` accepted frontend API-client and Workbench wiring for Auto sync, Sync, Submit, and Pull.
- `docs/task_board.md` currently shows no active implementation lane after TASK_346D acceptance and asks Planner/Orchestrator to decide the next formal TASK_346E+ lane.
- Current dirty workspace includes unrelated Settings/LTR, backend/settings/release, packaging/release, `docs/task_board.md` release note, and `temp_agents_stash.md` residuals that are not owned by TASK_346E.

Planner inference:

- The next correct lane is not a code lane. It is the contract-defined integration QA lane that validates the accepted backend and frontend workflow together under safe temp directories.

## 3. Definition Of Ready

Definition of Ready is satisfied for a planned lane:

- Upstream dependencies are complete/accepted.
- The task is explicitly named in the accepted TASK_346A downstream sequence.
- Scope can be bounded to QA/evidence only.
- May Touch, Must Not Touch, Locked Paths, Validation Gate, and Merge Gate can be stated without ambiguity.
- No blocker questions are required before Reviewer plan gate.

Definition of Ready is not satisfied for implementation or QA execution:

- Reviewer plan gate has not yet run for TASK_346E.
- User has not approved QA execution for this lane.
- No role should mutate product source or real folders from this Planner pass.

Blocker questions: none.

## 4. Recommended Lane

Task ID: `TASK_346E_FOLDER_WORKFLOW_INTEGRATION_QA`

Lane: `folder-workflow-integration-qa`

Recommended next role: Reviewer plan gate.

Why this follows TASK_346D:

- TASK_346D wired the UI to the backend workflow.
- TASK_346E is the first point where a temp-dir end-to-end workflow can be meaningfully validated.
- Choosing Settings/LTR helper separation or backend/frontend hardening first would be guesswork and would mix unrelated dirty residuals into a contract-backed Folder Actions series.

## 5. Scope

TASK_346E validates the accepted Folder Actions workflow as an integration/QA package:

- prepare temp local root and temp public root fixtures;
- verify backend context and workflow state against temp roots;
- verify Workbench UI consumes workflow state and remains preview-first;
- verify Sync, Submit, and Pull do not touch real folders;
- verify Submit lock and operation/audit records;
- document browser/API/command evidence and residual risks.

This lane is QA/evidence only unless a later Reviewer/User gate explicitly authorizes a narrowly scoped fix lane.

## 6. May Touch

Planner creation May Touch:

- `tasks/TASK_346E_FOLDER_WORKFLOW_INTEGRATION_QA.md`
- `docs/task_346e_folder_workflow_integration_qa_plan.md`
- `docs/lane_evidence/TASK_346E_folder-workflow-integration-qa_planner.md`
- `docs/task_board.md`

Future QA May Touch after separate routing:

- `docs/lane_evidence/TASK_346E_folder-workflow-integration-qa_qa.md`
- `docs/lane_evidence/artifacts/TASK_346E_qa/**`
- `tmp/TASK_346E_folder_workflow/**` or an equivalent repository-local temp fixture directory
- QA-only checkpoints under normal lane evidence flow

## 7. Must Not Touch / Locked Paths

Must Not Touch:

- product backend code
- product frontend code
- product tests
- frontend API client implementation
- Settings/LTR helper residuals
- release-engineering residuals
- Projects registry/list
- Matrix Editor business logic
- real local/public folders
- real LTR workbook files
- public-drive LTR workbook authority writes
- StepInstance, Report, AI, permissions, LAN/server, multi-user

Locked paths:

- `backend/**`
- `frontend/**`
- `tests/**`
- `frontend/src/api/client.ts`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/**`
- `frontend/src/features/matrix-editor/**`
- `D:\Test Project/**`
- `D:\PublicProject/**`
- real public-drive folders
- real local project folders
- real LTR workbook files
- `.agents/**`
- `docs/project_management/**`
- `docs/packaging_notes.md`
- `pyproject.toml`
- `backend/desktop/**`
- `dist_release/**`
- `packaging/**`
- release scripts/tests/tasks/docs
- `temp_agents_stash.md`

## 8. Validation Gate

Reviewer plan gate should verify:

- QA scope is evidence-only and does not authorize code changes.
- All filesystem exercises use temp roots only.
- Real `D:\Test Project`, `D:\PublicProject`, public-drive roots, local project folders, and LTR workbooks are locked.
- Existing unrelated dirty residuals are explicitly excluded.
- QA stops and reports if temp-safe settings or fixtures are unavailable.

Future QA expectations:

- API smoke for public-folder workflow context and Auto sync preference with temp roots.
- Sync preview/execute into temp `Open\<year>\<project_folder_name>`.
- Submit preview/execute from temp Open to temp `Closed\<year>\<project_folder_name>` and Sync lock verification.
- Pull preview/execute from temp Closed back to local while preserving existing local history.
- Operation/audit record verification for Sync, Submit, Pull.
- Conflict/blocker checks for missing root, stale preview hash, existing destination, and ambiguous year where feasible.
- Browser smoke for Workbench Folder Actions showing context, controls, preview-first confirmation, short blockers/results, and no old readiness/status copy.
- Static checks proving no real path mutation and no product source changes.

## 9. Merge Gate

TASK_346E merge/acceptance requires:

- Reviewer plan gate pass.
- QA gate pass with evidence and artifacts only in approved paths.
- Integrator packaging/readiness check.
- `git diff --check` for included docs/evidence.
- trailing whitespace scan for included docs/evidence.
- targeted status proving no product code, real folder, LTR workbook, Settings/LTR residual, release residual, `.agents/**`, or `docs/project_management/**` changes are included.

If QA discovers a product defect or missing fixture support, it must stop and route a separate Planner/Developer fix lane.

## 10. Relationship To Upstream Lanes

- `TASK_346A`: source contract for path rules, preview-first safety, Submit lock, and downstream sequence.
- `TASK_346B`: first quiet Folder Actions UI shell.
- `TASK_346F`: contextual panel polish accepted before backend wiring.
- `TASK_346C`: backend/API/file-operation workflow foundation.
- `TASK_346D`: frontend API-client and Workbench wiring.
- `TASK_346E`: validates the accepted pieces together with temp-only fixtures.

## 11. Current Stop Point

TASK_346E is complete/accepted as QA/integration evidence only.

## 12. Integrator Packaging Closeout

TASK_346E is accepted after Reviewer plan gate, QA execution gate, and Integrator packaging/readiness.

Package scope:

- `tasks/TASK_346E_FOLDER_WORKFLOW_INTEGRATION_QA.md`
- `docs/task_346e_folder_workflow_integration_qa_plan.md`
- `docs/lane_evidence/TASK_346E_folder-workflow-integration-qa_planner.md`
- `docs/lane_evidence/TASK_346E_folder-workflow-integration-qa_qa.md`
- `docs/lane_evidence/artifacts/TASK_346E_qa/**`
- `docs/task_board.md` TASK_346E closeout only

Excluded residuals:

- product backend/frontend/API-client/test changes
- Settings/LTR helper residuals and backend/settings residuals
- release/packaging residuals
- `temp_agents_stash.md`
- real local/public folders and real LTR workbook files
- `.agents/**`, `docs/project_management/**`, and future scope

Integrator did not rerun product suites because the package is evidence-only and no product code was modified; QA evidence records the relevant TASK_346C/TASK_346D/backend/frontend/temp-dir/browser validations.

Next role: Reviewer plan gate.
