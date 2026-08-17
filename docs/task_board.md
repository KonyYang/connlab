# ConnLab Task Board

> Authority: the compact control block below. Workflow: `docs/project_management/TASK_WORKFLOW.md`.
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
    "task_id": "TASK_MATRIX_IMPORT_PREVIEW_SHARED_PDF_PREPARATION",
    "summary": "Use one shared PDF preview preparation flow for resolved-directory candidates, uploaded files, and direct desktop paths.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Generate preview PDF tokens consistently for .docx and .pdf sources without re-uploading local files or changing Matrix parsing authority.",
    "scope_paths": [
      "backend/api/routes_project_test_plan.py",
      "backend/api/routes_project_test_plan_source_candidates.py",
      "tests/integration/test_project_test_plan_preview_api.py",
      "tests/integration/test_project_test_plan_source_candidates_api.py"
    ],
    "risk_reasons": [
      "Three API entry points share temporary preview artifacts and Word COM conversion behavior."
    ],
    "activation_head": "858546e389461c17170e40aee27c80bc5424c902",
    "started_at": "2026-08-17T15:55:59.945063Z",
    "updated_at": "2026-08-17T15:55:59.945063Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_IMPORT_SOURCE_PICKER_FOOTER_BUTTON_STYLE",
    "tier": "micro",
    "subject": "f389ed0bce9e2fb8490a8bf73f5c656647ee579c",
    "summary": "Match the Matrix Import source picker footer buttons to the Matrix Editor button style with white default surfaces, rounded borders, bold text, and blue hover/focus feedback.",
    "disposition": "completed",
    "decision_ref": "User: 关闭",
    "closed_at": "2026-08-17T15:22:18.878757Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
