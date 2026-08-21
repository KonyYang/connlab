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
    "task_id": "TASK_FEE_FOOTNOTED_SAMPLE_QUANTITY_UNITS",
    "summary": "Calculate Fee Evaluation units from simple footnoted Matrix sample quantities such as 5(a).",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Normalize simple numeric sample quantities with alphabetic footnotes at the shared Fee Evaluation boundary while preserving manual review for compound expressions; cover LLCR through the public Fee Draft API.",
    "scope_paths": [
      "backend/modules/fee_evaluation/fee_default_fill.py",
      "backend/modules/fee_evaluation/fee_default_fill_common.py",
      "backend/modules/fee_evaluation/fee_reviewed_extension_defaults.py",
      "backend/modules/fee_evaluation/fee_step_quantity_defaults.py",
      "tests/integration/test_confirmed_matrix_fee_draft_api.py"
    ],
    "risk_reasons": [],
    "activation_head": "4189718a899229018a0d63de9e625b498c7daaae",
    "started_at": "2026-08-21T10:07:42.437565Z",
    "updated_at": "2026-08-21T10:07:42.437565Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_TEST_POINTS_FEE_EVALUATION_SYNC",
    "tier": "standard",
    "subject": "7a69fa028becbfbd96abe51243e71480d1ac5059",
    "summary": "Ensure Matrix test-point setup is consistently propagated into Fee Evaluation derived pricing data.",
    "disposition": "completed",
    "decision_ref": "User: 修复已经修改好了，该提交提交，可以直接关闭当前任务",
    "closed_at": "2026-08-21T10:07:02.941215Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
