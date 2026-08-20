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
    "task_id": "TASK_SOL56_DOCUMENTATION_AND_RULES_OPTIMIZATION",
    "summary": "Replace duplicated and stale ConnLab instructions with a lean GPT-5.6 Sol authority set.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Optimize ConnLab documentation and execution rules for GPT-5.6 Sol without changing product behavior, APIs, databases, or external data.",
    "scope_paths": [
      "AGENTS.md",
      "README.md",
      "docs/INDEX.md",
      "docs/PROJECT_CONTEXT.md",
      "docs/FRONTEND_GUIDE.md",
      "docs/project_management/SOL_NATIVE_WORKFLOW.md",
      "docs/project_management/TASK_WORKFLOW.md",
      "docs/task_board.md",
      "docs/markdown_management_rules.md",
      "docs/02_ARCHITECTURE_RULES.md",
      "docs/03_DOMAIN_MODEL.md",
      "docs/04_API_CONTRACTS.md",
      "docs/frontend_architecture_rules.md",
      "docs/intake_precheck_field_contract.md",
      "docs/matrix_execution_phase_principles.md",
      "docs/archive/historical_context/02_ARCHITECTURE_RULES.md",
      "docs/archive/historical_context/03_DOMAIN_MODEL.md",
      "docs/archive/historical_context/04_API_CONTRACTS.md",
      "docs/archive/historical_context/frontend_architecture_rules.md",
      "docs/archive/historical_context/intake_precheck_field_contract.md",
      "docs/archive/historical_context/matrix_execution_phase_principles.md",
      ".agents/skills/connlab-lane-orchestrator/SKILL.md",
      ".agents/skills/connlab-lane-orchestrator/agents/openai.yaml",
      "tests/unit/test_frontend_architecture_rules.py"
    ],
    "risk_reasons": [],
    "activation_head": "d5932d6ed2f2710da3cffda7ef4eafa72f246528",
    "started_at": "2026-08-20T11:24:31.915638Z",
    "updated_at": "2026-08-20T11:24:31.915638Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_IMPORT_PREVIEW_SHARED_PDF_PREPARATION",
    "tier": "high_risk",
    "subject": "7c65975e6d924583fe88ae67d69eeb0c8d38e5aa",
    "summary": "Use one shared PDF preview preparation flow for resolved-directory candidates, uploaded files, and direct desktop paths.",
    "disposition": "cancelled",
    "decision_ref": "User requested stale-task cleanup on 2026-08-20; prior explicit Close followed successful manual verification; cancel stale tracking record only, implementation retained at 3b3c8419.",
    "closed_at": "2026-08-20T11:05:12.427967Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
