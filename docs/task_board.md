# ConnLab Task Board

> Authority: the compact control block below. Workflow: `docs/project_management/SOL_NATIVE_WORKFLOW.md`.
> Version 1 keeps one active task; an idle isolated Submit upgrades to version 2 with one main
> task and one independent micro task. GPT-6 Astra runs routine stages until each task's final Close.

<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->
```json
{
  "schema": "connlab.sol-task-control",
  "version": 2,
  "mode": "sol_native",
  "wip_limit": 2,
  "last_closed": {
    "task_id": "TASK_LLCR_RESULT_SEMANTICS_20261023",
    "tier": "standard",
    "subject": "1c5c8a07701860d827ac0b0032e1040bf6b76a16",
    "summary": "Correct LLCR absolute resistance versus delta semantics without changing real reports",
    "disposition": "completed",
    "decision_ref": "User explicitly confirmed final Close after 261-test LLCR acceptance",
    "closed_at": "2026-10-22T23:55:52.392518Z"
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
  ],
  "tasks": {
    "TASK_REPORT_CAPABILITIES_3_7_20261026": {
      "slot": "main",
      "state": "ready_for_close",
      "worktree": "D:\\PythonProject\\connlab-report-capabilities-20261026",
      "branch": "codex/report-capabilities-20261026",
      "resources": [],
      "integrated_head": "d6672b503e5dbb45293c56f69ac5a31c68dce066",
      "task": {
        "task_id": "TASK_REPORT_CAPABILITIES_3_7_20261026",
        "summary": "Report Workspace: persistent provenance, temperature/CR, mechanical appendices, photo slots and checked customer copies",
        "tier": "high_risk",
        "route": "full_chain",
        "scope": "One main task, five milestones 3-7. Preserve existing LLCR and local-update protections. Isolated databases and file copies only; real reports/templates/project files read-only; no automatic official publication or force push. Missing decisions stay pending. Include latest 032 review regressions.",
        "scope_paths": [
          "backend/application/report_authoring",
          "backend/domain/report_authoring.py",
          "backend/infrastructure/office/report_authoring",
          "backend/infrastructure/files/report_authoring_assets.py",
          "backend/infrastructure/storage/models_report_authoring.py",
          "backend/infrastructure/storage/repositories/report_authoring.py",
          "backend/infrastructure/storage/report_authoring_schema.py",
          "backend/infrastructure/storage/database.py",
          "backend/api/routes_report_authoring.py",
          "backend/api/report_authoring_schemas.py",
          "backend/api/dependencies.py",
          "backend/api/main.py",
          "backend/api/routes_report_workspace.py",
          "backend/application/report_section_update_service.py",
          "backend/infrastructure/files/report_draft_workspace.py",
          "backend/infrastructure/office/test_report_document_gateway.py",
          "backend/infrastructure/office/customer_report_document_gateway.py",
          "backend/application/customer_report_projection_service.py",
          "backend/application/project_customer_report_job_service.py",
          "backend/api/project_customer_report_runner.py",
          "frontend/src/features/report-workspace",
          "frontend/src/api/reportAuthoring.ts",
          "frontend/src/api/reportAuthoring.test.ts",
          "frontend/src/styles.css",
          "tests/unit/report_authoring",
          "tests/integration/test_report_authoring_api.py",
          "tests/unit/test_report_authoring_schema.py",
          "tests/unit/test_report_draft_workspace.py",
          "tests/unit/test_customer_report_document_gateway.py",
          "tests/unit/test_test_report_document_gateway.py",
          "tests/unit/test_customer_report_projection_service.py",
          "tests/unit/test_project_customer_report_job_service.py",
          "tests/integration/test_project_customer_report_runner.py",
          "tests/integration/test_report_section_draft_api.py",
          "tests/fixtures/report_authoring",
          "docs/architecture/report_authoring.md"
        ],
        "risk_reasons": [
          "Additive report provenance persistence schema",
          "Report data semantics and confidential customer-copy verification"
        ],
        "activation_head": "cd6250e189e5ad67f4c005a3f32c3cfc92945884",
        "started_at": "2026-10-26T00:05:01.578908Z",
        "updated_at": "2026-10-26T15:14:21.363298Z",
        "checkpoint": {
          "schema": "connlab.sol-task-checkpoint",
          "version": 1,
          "task_id": "TASK_REPORT_CAPABILITIES_3_7_20261026",
          "stage": "revision",
          "status": "running",
          "summary": "User approved next improvement: visible report preparation entry, source/update/customer-review navigation and truthful status guidance; preserve existing business logic and file protection.",
          "requires_user": false
        },
        "report": {
          "schema": "connlab.sol-task-report",
          "version": 1,
          "task_id": "TASK_REPORT_CAPABILITIES_3_7_20261026",
          "subject": "41e6caed8dc1621d25065e0c54bfe1963922d3bf",
          "summary": "Five Report Workspace capabilities and customer layout previously accepted; bounded three-step report preparation navigation now independently reviewed and QA verified. No backend/API/Word changes. Await final user acceptance.",
          "scope_ok": true,
          "changed_paths": [
            "frontend/src/features/report-workspace/ReportAuthoringPanel.test.tsx",
            "frontend/src/features/report-workspace/ReportAuthoringPanel.tsx",
            "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
            "frontend/src/features/report-workspace/ReportWorkspace.tsx",
            "frontend/src/features/report-workspace/reportAuthoringPanel.css"
          ],
          "validation": [
            {
              "status": "passed",
              "subject": "7ed1e3dd88acde5da749aa4fd071a3b9e418b8c3",
              "kind": "independent_qa_final",
              "result": "36 affected Python; 1035 Vitest passed, 1 skip; TypeScript/build passed; real isolated UI findings closed and blank/current source positive paths verified",
              "evidence": {
                "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\qa\\qa_final.json",
                "raw_sha256": "cdd262b154974b3536a80908bbcba2f87882219cafef81e320c5fbb789796eb8"
              }
            },
            {
              "status": "passed",
              "subject": "8b406404daebfe599ed719c8f8e14c351665cb1c",
              "kind": "retained_backend_baseline",
              "result": "652 Python on prior subject; retained for unchanged backend with affected final checks, not a new full final-subject run"
            },
            {
              "status": "passed",
              "subject": "7ed1e3dd88acde5da749aa4fd071a3b9e418b8c3",
              "kind": "retained_word_visual_binding",
              "result": "Four previously reviewed Word render sets, 19/20/17/19 pages; generator code unchanged; no new rendering claimed",
              "evidence": [
                {
                  "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\visual_manifest.json",
                  "raw_sha256": "435e0c3229f5244640d2db8e7d4a0ae44ff97e4d82c804db6c9b4933d13ba296"
                },
                {
                  "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\visual_binding_final.json",
                  "raw_sha256": "d3f3714a47087c437091cbf1c726d26cbcff12b5a4ee1a6cd0c921e576f7406e"
                }
              ]
            },
            {
              "status": "passed",
              "subject": "199b109dc563ff3cdd44fd648f4b3f373b1c4798",
              "kind": "bounded_customer_layout",
              "result": "Developer 11 affected UI tests and build; independent Reviewer unchanged behavioral attributes; independent QA responsive and native control browser checks. Prior backend/Word validation retained because only JSX layout and scoped CSS changed.",
              "evidence": [
                {
                  "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\developer_customer_layout.json",
                  "raw_sha256": "56e7282b2d72024b3f5a1d34588933984c533f3105395c5487083d798e752a21"
                },
                {
                  "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\customer_layout_review.json",
                  "raw_sha256": "581161f2e8f3e958fbcffd494d2cef6552372f13bd93fea57b35972bcdbe3445"
                },
                {
                  "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\customer_layout_qa.json",
                  "raw_sha256": "1b0369299dcfe2e786b808a061bcf9bc11894928ab0c0934487ed64bf20e1523"
                }
              ]
            },
            {
              "status": "passed",
              "subject": "41e6caed8dc1621d25065e0c54bfe1963922d3bf",
              "kind": "bounded_report_navigation",
              "result": "Independent review and QA report-workspace tests/build plus isolated browser navigation acceptance; prior backend/Word evidence retained for unchanged code.",
              "evidence": [
                {
                  "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\report_navigation_developer.json",
                  "raw_sha256": "d4fb3e000c490b2eedc865f73437df0ffca1f7660a3eeaf8543ca32f78417222"
                },
                {
                  "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\report_navigation_review.json",
                  "raw_sha256": "a170aec159668d5bac553ac91089d4d4c2ad66009d49215f02649951b8aa6104"
                },
                {
                  "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\report_navigation_qa.json",
                  "raw_sha256": "e444dd32bdd639df16652690f43be11c11f39669567b076315fe462d3001146f"
                }
              ]
            }
          ],
          "roles": {
            "planner": {
              "status": "passed",
              "evidence": [
                {
                  "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\planner_final.json",
                  "raw_sha256": "ae53f1be595e8473e8fd17e0d39a489093fe5ed2b6ddfc10f0d6571c2b88579b"
                }
              ]
            },
            "developer": {
              "status": "passed",
              "evidence": [
                {
                  "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\developer_final.json",
                  "raw_sha256": "5d0783346e9250d63219dde38d43dc481bd08d212c2f4692bf1b537a1c17d62c"
                },
                {
                  "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\developer_qa_fix.json",
                  "raw_sha256": "a1f9aa8b7d1e7c765f9931b4961e88fa1f02ecff56fbf175229ba0f97675ead7"
                },
                {
                  "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\developer_customer_layout.json",
                  "raw_sha256": "56e7282b2d72024b3f5a1d34588933984c533f3105395c5487083d798e752a21"
                },
                {
                  "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\report_navigation_developer.json",
                  "raw_sha256": "d4fb3e000c490b2eedc865f73437df0ffca1f7660a3eeaf8543ca32f78417222"
                }
              ]
            },
            "reviewer": {
              "status": "passed",
              "evidence": [
                {
                  "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\reviewer_final.json",
                  "raw_sha256": "467bb9072484510919df1b6d3850aafb95d72085b4c3f5961f5a5e5556435914"
                },
                {
                  "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\reviewer_qa_fix.json",
                  "raw_sha256": "843e41bcc22213d66e1a5dbc1c015c14e213c47a03b81d31f2c453165312b34a"
                },
                {
                  "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\customer_layout_review.json",
                  "raw_sha256": "581161f2e8f3e958fbcffd494d2cef6552372f13bd93fea57b35972bcdbe3445"
                },
                {
                  "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\report_navigation_review.json",
                  "raw_sha256": "a170aec159668d5bac553ac91089d4d4c2ad66009d49215f02649951b8aa6104"
                }
              ]
            },
            "qa": {
              "status": "passed",
              "evidence": [
                {
                  "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\qa\\qa_final.json",
                  "raw_sha256": "cdd262b154974b3536a80908bbcba2f87882219cafef81e320c5fbb789796eb8"
                },
                {
                  "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\customer_layout_qa.json",
                  "raw_sha256": "1b0369299dcfe2e786b808a061bcf9bc11894928ab0c0934487ed64bf20e1523"
                },
                {
                  "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\report_navigation_qa.json",
                  "raw_sha256": "e444dd32bdd639df16652690f43be11c11f39669567b076315fe462d3001146f"
                }
              ]
            },
            "integrator": {
              "status": "passed",
              "scope": "Exact navigation revision pre-integration checks",
              "evidence": [
                {
                  "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\customer_layout_integrator.json",
                  "raw_sha256": "2a7a8503ec09756389d6e597fa539f941df52c9d9fbe77b204c67bef6e50d03b"
                },
                {
                  "path": "C:\\Users\\White\\Documents\\Codex\\report_goal_20261026\\report_navigation_integrator_precheck.json",
                  "raw_sha256": "029cc1f7bb9455237905748d507150570b3e8434e0a692a183139a23fab9b15c"
                }
              ]
            }
          },
          "integration": {
            "status": "passed",
            "mode": "serial_local_merge",
            "subject": "41e6caed8dc1621d25065e0c54bfe1963922d3bf",
            "primary_before": "72c1a479fb0c3c43afa5e17359d29831a786e041",
            "integrated_head": "d6672b503e5dbb45293c56f69ac5a31c68dce066",
            "recovered": false
          }
        }
      }
    }
  }
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
