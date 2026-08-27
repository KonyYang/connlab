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
    "task_id": "TASK_FEE_REBASE_DERIVED_TOTAL_RESAVE",
    "summary": "Ensure Update Fee re-saves normalized derived fees after a Matrix rebase before confirming.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Fix current V2 pricing-draft hydration baseline tracking so server payloads with stale derived testing fees are normalized, saved, reloaded, and only then confirmed; preserve backend summary guard.",
    "scope_paths": [
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.pricingDraftHydration.test.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "82d831103f64f0d3dc7e42819622077702637d90",
    "started_at": "2026-08-27T23:44:27.398899Z",
    "updated_at": "2026-08-27T23:44:27.398899Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_TEST_RECORD_DIRECT_PUBLISH",
    "tier": "high_risk",
    "subject": "c509a62a3a819402a2beed8fd515ab24551bb413",
    "summary": "Publish the current Matrix Editor Test Record directly into an existing official project folder with authoritative headers and explicit archive, recycle-bin, or cancel conflict handling.",
    "disposition": "completed",
    "decision_ref": "用户明确回复：关闭",
    "closed_at": "2026-08-27T23:33:20.681566Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
