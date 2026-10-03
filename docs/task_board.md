# ConnLab Task Board

> Authority: the compact control block below. Workflow: `docs/project_management/SOL_NATIVE_WORKFLOW.md`.
> Version 1 keeps one active task; an idle isolated Submit upgrades to version 2 with one main
> task and one independent micro task. GPT-6 Astra runs routine stages until each task's final Close.

<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->
```json
{
  "schema": "connlab.sol-task-control",
  "version": 1,
  "mode": "sol_native",
  "wip_limit": 1,
  "state": "ready_for_close",
  "active": {
    "task_id": "TASK_FEE_GROUP_BASE_DEFAULTS_20261003",
    "summary": "按 Matrix 组数设置默认基本费并显示参考条件悬浮提示",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Multiple confirmed Matrix groups default step Base Fee to zero; single group keeps existing rules; expose rule text on Base Fee hover without replacing manual Fee edits.",
    "scope_paths": [
      "backend/application/confirmed_matrix_fee_base_fee_policy.py",
      "backend/application/confirmed_matrix_fee_draft_line_builder.py",
      "backend/application/confirmed_matrix_fee_draft_models.py",
      "backend/api/routes_confirmed_matrix_fee_draft.py",
      "frontend/src/api/client.ts",
      "frontend/src/features/fee-evaluation",
      "tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py",
      "tests/integration/test_confirmed_matrix_fee_draft_api.py",
      "docs/fee_reference_20260915.md"
    ],
    "risk_reasons": [],
    "activation_head": "c664b1531508230504f428f4da9c3258dc20f6f3",
    "started_at": "2026-10-03T09:22:32.310889Z",
    "updated_at": "2026-10-03T09:31:16.339623Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_FEE_GROUP_BASE_DEFAULTS_20261003",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "integration": {
        "method": "Local master task commit; no remote publication",
        "status": "passed"
      },
      "version": 1,
      "schema": "connlab.sol-task-report",
      "validation": [
        {
          "result": "780 passed, 4 skipped; 76 fee-related unit/integration files; Office integration excluded",
          "name": "Python Fee regression",
          "status": "passed"
        },
        {
          "result": "142 passed across 11 test files",
          "name": "Frontend Fee regression",
          "status": "passed"
        },
        {
          "result": "TypeScript and Vite passed",
          "name": "Production build",
          "status": "passed"
        },
        {
          "result": "99 Base Fee inputs are zero; 86 Matrix step inputs have source reference titles; read-only verification",
          "name": "Live browser",
          "status": "passed"
        },
        {
          "result": "No whitespace errors",
          "name": "Diff check",
          "status": "passed"
        }
      ],
      "summary": "Multiple confirmed Matrix groups default step Base Fee to zero; single groups retain rules; inputs show source conditions on hover.",
      "task_id": "TASK_FEE_GROUP_BASE_DEFAULTS_20261003",
      "changed_paths": [
        "backend/api/routes_confirmed_matrix_fee_draft.py",
        "backend/application/confirmed_matrix_fee_base_fee_policy.py",
        "backend/application/confirmed_matrix_fee_draft_line_builder.py",
        "backend/application/confirmed_matrix_fee_draft_models.py",
        "docs/fee_reference_20260915.md",
        "frontend/src/api/client.ts",
        "frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.test.tsx",
        "frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx",
        "frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts",
        "frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts",
        "tests/integration/test_confirmed_matrix_fee_draft_api.py",
        "tests/integration/test_confirmed_matrix_fee_draft_dependent_fields_api.py",
        "tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py",
        "tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py"
      ],
      "subject": "84ffa8fbc887be6bb8695f86fd6e66186d6b0b05",
      "scope_ok": true,
      "roles": {
        "qa": {
          "method": "same-agent risk-proportionate complete fee regression and build on final reviewed code",
          "status": "passed"
        },
        "developer": {
          "method": "same-agent implementation and meaningful RED/GREEN tests",
          "status": "passed"
        },
        "reviewer": {
          "method": "same-agent focused standards and requirement review; no blocking findings",
          "status": "passed"
        }
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_REPORT_HEADER_ICON_TITLE_CASE_20261003",
    "tier": "micro",
    "subject": "d3d50bb550c81437cf16ab51d6f595488e8b2b54",
    "summary": "Report 页标题、工作台返回图标与按钮标题统一",
    "disposition": "completed",
    "decision_ref": "User final close: 关闭任务",
    "closed_at": "2026-10-03T09:07:42.991778Z"
  },
  "retained_history": [
    {
      "task_id": "TASK_361A_FEE_SUMMARY_ACCEPTANCE_CONTRACT",
      "tier": "standard",
      "closed_at": "2026-09-18T03:01:50.000000Z"
    },
    {
      "task_id": "TASK_PROJECT_FOLDER_FINALIZATION_ACCESS_COMPLETE",
      "tier": "high_risk",
      "closed_at": "2026-09-17T11:59:24.022479Z"
    }
  ]
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.

## Pending engineering-debt tasks ( backlog / not active )

These items are not in-flight; they are recorded here for prioritization. They do not
change the `active` field above.

### TASK_361B_TEST_RUNNER_INTERPRETER_ALIGNMENT

**Tier:** micro
**Revised from:** the stale broad test-environment proposal discovered during TASK_361A
**Goal:** Keep the supported test entry point on the same Python runtime as ConnLab development.

The original diagnosis was rechecked before implementation:

- `C:/PythonEnvs/connlab/.venv` is Python 3.11.9 and imports Tkinter 8.6 successfully; no
  dependency installation is needed.
- Office-dependent integration tests already use the `office_integration` marker. The normal gate
  excludes them and `-Suite Office` remains the explicit installed-Office check.
- WorkBuddy or Codex temporary-directory and safe-delete restrictions are host permissions, not
  ConnLab product behavior. They must be handled by the runner environment or an explicitly
  permitted pytest temp location, not by weakening repository cleanup or test semantics.

The remaining defect was limited to `scripts/run_tests.ps1`: it invoked the ambient `py` launcher,
which selected Python 3.13.3 instead of the Python 3.11.9 environment used by ConnLab. The revised
runner defaults to `C:/PythonEnvs/connlab/.venv/Scripts/python.exe`, supports an explicit
`-PythonExe` override, fails clearly when that interpreter is missing, and preserves the existing
normal/Office split.

**Validation:** the focused runner contract passes, and the complete non-Office Python gate passes
with 2954 tests, 7 skips, and 19 Office tests deselected on Python 3.11.9. No product code,
dependencies, Office implementation, or host safety policy changed.
