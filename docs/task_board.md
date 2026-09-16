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
    "task_id": "TASK_FEE_CONFIRMED_DRAFT_HYDRATION",
    "summary": "Restore confirmed Fee Form authority after reopening Fee Evaluation instead of incorrectly reverting to Draft.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Preserve current-v2 saved Sample preparation values when hydrating the Fee page so displayed content remains identical to the confirmed pricing draft, keep rebase behavior authoritative to the refreshed Matrix, and add page-level and hydration regression coverage for the official Fee Form action.",
    "scope_paths": [
      "frontend/src/features/fee-evaluation/feeEvaluationPricingDraftHydration.ts",
      "frontend/src/features/fee-evaluation/feeEvaluationPricingDraftHydration.test.ts",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "bf3fd3035d1808c3cfe33165358b25ee14289300",
    "started_at": "2026-09-16T16:47:12.437479Z",
    "updated_at": "2026-09-16T22:27:12.710142Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_FEE_CONFIRMED_DRAFT_HYDRATION",
      "stage": "revision",
      "status": "running",
      "summary": "Verify LLCR/CR test-point quantity propagation into Fee Evaluation and confirmed/draft Fee Form action state.",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_FEE_GROUP_SUMMARY_PLACEMENT",
    "tier": "micro",
    "subject": "7cead4553eddf3b9691a9377aacc5f056182c523",
    "summary": "Move the Preview group and Total Testing Fee card into the totals row and replace the redundant Grand Cost card.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested 关闭.",
    "closed_at": "2026-09-16T16:39:33.014967Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
