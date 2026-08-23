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
    "task_id": "TASK_FEE_SAMPLE_PREPARATION_MATRIX_QUANTITY",
    "summary": "Use confirmed Matrix Samples Quantity (PCS) as Sample preparation Units instead of stale saved default 1.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Correct Fee Evaluation Sample preparation Units in server rebase and frontend saved-draft hydration while preserving other compatible manual fields.",
    "scope_paths": [
      "backend/application/fee_evaluation_pricing_draft_v2_rebase.py",
      "tests/unit/test_fee_evaluation_pricing_draft_v2_rebase.py",
      "frontend/src/features/fee-evaluation/feeEvaluationPricingDraftHydration.ts",
      "frontend/src/features/fee-evaluation/feeEvaluationPricingDraftHydration.test.ts"
    ],
    "risk_reasons": [],
    "activation_head": "e41787cf073fb363e0e8a8a0dacb32af31f34453",
    "started_at": "2026-08-23T04:23:26.705709Z",
    "updated_at": "2026-08-23T04:29:08.725667Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_FEE_SAMPLE_PREPARATION_MATRIX_QUANTITY",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_FEE_SAMPLE_PREPARATION_MATRIX_QUANTITY",
      "subject": "ab58a3f695d1c44b40b087bb5165c6f6db30998b",
      "summary": "Sample preparation Units now use the current confirmed Matrix sample quantity across rebase and saved-draft hydration.",
      "scope_ok": true,
      "changed_paths": [
        "backend/application/fee_evaluation_pricing_draft_v2_rebase.py",
        "frontend/src/features/fee-evaluation/feeEvaluationPricingDraftHydration.test.ts",
        "frontend/src/features/fee-evaluation/feeEvaluationPricingDraftHydration.ts",
        "tests/unit/test_fee_evaluation_pricing_draft_v2_rebase.py"
      ],
      "validation": [
        {
          "name": "backend_fee_pricing_qa",
          "status": "passed",
          "summary": "56 tests passed"
        },
        {
          "name": "frontend_fee_evaluation_qa",
          "status": "passed",
          "summary": "68 tests passed"
        },
        {
          "name": "frontend_production_build",
          "status": "passed",
          "summary": "TypeScript and Vite build passed"
        },
        {
          "name": "browser_project_verification",
          "status": "passed",
          "summary": "Groups 1-8b show 5 and group 9 shows 10"
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "summary": "TDD red-green implementation and exact affected checks passed."
        },
        "reviewer": {
          "status": "passed",
          "summary": "Standards and specification review passed after one bounded typing fix."
        },
        "qa": {
          "status": "passed",
          "summary": "Complete affected backend, frontend, build, and browser matrix passed."
        }
      },
      "integration": {
        "status": "passed",
        "mode": "direct_primary"
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_FEE_CONTAINMENT_UNIT_TYPES",
    "tier": "standard",
    "subject": "7266c99ed26dea506b9ee38434f1aa777f641c3d",
    "summary": "Extend reviewed Fee matching for durability, dust, thermal cycling, and contact retention labels.",
    "disposition": "completed",
    "decision_ref": "user:关闭",
    "closed_at": "2026-08-23T04:09:32.746577Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
