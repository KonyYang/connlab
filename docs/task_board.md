# ConnLab Task Board

> Authority: the compact control block below. Workflow: `docs/project_management/SOL_NATIVE_WORKFLOW.md`.
> WIP=1. GPT-5.6 Sol routes work as micro, standard, or high risk and runs routine stages
> automatically until the User's final Close.

<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->
```json
{
  "schema": "connlab.sol-task-control",
  "version": 1,
  "mode": "sol_native",
  "wip_limit": 1,
  "state": "running",
  "active": {
    "task_id": "TASK_PROJECT_FOLDER_BLOCKER_VISIBILITY",
    "summary": "Keep Project Folder generation blockers visible until the user corrects the input or explicitly starts a new recovery action.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Frontend Project Folder generation error lifetime, recovery presentation, and regression coverage.",
    "scope_paths": [
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
      "frontend/src/features/project-workbench/useProjectFolderGeneration.ts",
      "frontend/src/features/project-workbench/useProjectFolderGeneration.test.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "d139cac7dc07ed0d2b6cef1b1f09beafe145f42c",
    "started_at": "2026-09-09T11:08:32.976159Z",
    "updated_at": "2026-09-09T11:28:12.969985Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_PROJECT_FOLDER_BLOCKER_VISIBILITY",
      "stage": "revision",
      "status": "running",
      "summary": "用户实际冒烟测试确认阻塞提示仍一闪而过，要求在指定项目上点击复现并继续修复。",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_BASIC_INFORMATION_LEGACY_CLEANUP",
    "tier": "micro",
    "subject": "b47d51e412054ef02f8df07afc489e92567c8d4e",
    "summary": "Remove verified dead Basic Information schedule UI configuration and unused application-form date projections without changing legacy compatibility behavior.",
    "disposition": "completed",
    "decision_ref": "用户明确要求关闭当前任务，并修复项目文件夹阻塞提示一闪而过。",
    "closed_at": "2026-09-09T11:08:32.976159Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
