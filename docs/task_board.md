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
  "state": "ready_for_close",
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
    "updated_at": "2026-09-16T22:32:56.413966Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_FEE_CONFIRMED_DRAFT_HYDRATION",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_FEE_CONFIRMED_DRAFT_HYDRATION",
      "subject": "0869c0bcb9b3d8cf5de0955d887dba8aabb6a96d",
      "summary": "Detect Matrix-aligned quantity drift before Fee confirmation and verify confirmed LLCR/CR point-profile changes propagate into Fee units and action state.",
      "scope_ok": true,
      "changed_paths": [
        "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx",
        "frontend/src/features/fee-evaluation/feeEvaluationPricingDraftHydration.test.ts",
        "frontend/src/features/fee-evaluation/feeEvaluationPricingDraftHydration.ts"
      ],
      "validation": [
        {
          "name": "Focused Fee hydration and page regression suite",
          "status": "passed",
          "summary": "48 tests passed."
        },
        {
          "name": "Frontend production build",
          "status": "passed",
          "summary": "TypeScript and Vite production build completed successfully."
        },
        {
          "name": "LLCR point-profile quantity and rebase checks",
          "status": "passed",
          "summary": "The focused backend quantity multiplication and point-profile rebase tests passed."
        },
        {
          "name": "Current project read-only authority audit",
          "status": "passed",
          "summary": "Confirmed 5 points per sample, calculated LLCR units, current V2 pricing draft, and matching confirmed Fee draft identity."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "summary": "Implemented the minimal Sample preparation units drift check with RED/GREEN coverage."
        },
        "reviewer": {
          "status": "passed",
          "summary": "Standards and spec review found no actionable findings or scope creep."
        },
        "qa": {
          "status": "passed",
          "summary": "Focused frontend regressions, backend point-profile linkage tests, production build, and read-only live authority audit passed."
        }
      },
      "integration": {
        "status": "passed",
        "summary": "The exact clean HEAD contains only the scoped frontend fix, regression tests, and task-control records; live project data was not mutated."
      }
    }
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
