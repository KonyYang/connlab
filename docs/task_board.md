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
    "task_id": "TASK_MATRIX_RELEASE_SMOKE_20260905",
    "summary": "Build the Matrix reliability browser release and validate its isolated local operator flow; deliver a second-computer smoke checklist.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Package existing verified code in a new directory; isolate all runtime data, preserve current installation and real data; no unrelated UI changes or deployment to other computers.",
    "scope_paths": [
      "docs/project_management/MATRIX_RELEASE_SMOKE_20260905.md"
    ],
    "risk_reasons": [],
    "activation_head": "ef44aca3986716a4681372a96ed28a3b5e7c8785",
    "started_at": "2026-09-05T02:08:04.985893Z",
    "updated_at": "2026-09-05T02:29:16.684449Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_RELEASE_SMOKE_20260905",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_MATRIX_RELEASE_SMOKE_20260905",
      "subject": "f2cf42ccce56156ed5ba9e3f5e7a5f15c581b49f",
      "summary": "New portable browser release built and locally accepted with isolated synthetic data. Source unchanged; restart persistence, confirmation/output isolation, manual flow, diagnostics and fresh-profile startup passed. Second-PC and actual template/Office acceptance remain operator work; slow initial DOCX preview recorded.",
      "scope_ok": true,
      "changed_paths": [
        "docs/project_management/MATRIX_RELEASE_SMOKE_20260905.md"
      ],
      "validation": [
        {
          "status": "passed",
          "check": "Fresh frontend typecheck/build and PyInstaller packaging",
          "source": "c94eb2d64c49b4f993de1a8041aeb776fc51fa21",
          "frontend_seconds": 10.2,
          "pyinstaller_seconds": 110.9
        },
        {
          "status": "passed",
          "check": "Actual EXE isolated browser/API smoke",
          "coverage": "import parser/commit; UI save/reopen; process restart; group isolation; Confirm; DOCX/XLSX bytes; stale-confirm retention; manual draft; diagnostics"
        },
        {
          "status": "passed",
          "check": "Delivered copy hash comparison and ZIP CRC",
          "files": 1301,
          "zip_sha256": "6ddab486ac23bd8ef5d95773fadc5564678495972741e38ffd88454883ad5329"
        },
        {
          "status": "passed",
          "check": "Delivered EXE fresh-profile startup",
          "coverage": "health, app shell, empty registry; owned test servers stopped"
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "execution": "main agent build/fixture preparation; no product code changes"
        },
        "reviewer": {
          "status": "passed",
          "execution": "same-agent focused artifact/scope/evidence review; not independent"
        },
        "qa": {
          "status": "passed",
          "execution": "same-agent packaged smoke pass; not independent",
          "limitations": "no second computer, full file-dialog upload, real old DB migration or exhaustive Office COM acceptance"
        }
      },
      "integration": {
        "status": "passed",
        "subject": "f2cf42ccce56156ed5ba9e3f5e7a5f15c581b49f",
        "tree": "7eb8e5073aab9a411ddca7e7b3ec1a45fb125d43",
        "parents": [
          "c94eb2d64c49b4f993de1a8041aeb776fc51fa21"
        ],
        "clean": true,
        "artifact": "C:\\Users\\White\\Documents\\Codex\\ConnLab_Releases\\ConnLab_Web_202609051010_v0.1.0-matrix1.zip",
        "artifact_sha256": "6ddab486ac23bd8ef5d95773fadc5564678495972741e38ffd88454883ad5329",
        "source": "c94eb2d64c49b4f993de1a8041aeb776fc51fa21",
        "report_raw_sha256": "dd38bc29dfe28b749b49ca21f63f45ca30631e673d8d29c968dc1be1f83b4626",
        "fact": "Report committed locally, verified portable artifact delivered; no deployment/push, no merge required."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_EXPERIENCE_RELIABILITY_BATCH1",
    "tier": "standard",
    "subject": "7ddd40a14fa8ce82423c07ffa53d25dfa1a1cb57",
    "summary": "Improve Matrix loading, registry status consistency, and edit-save-reopen-confirm-export reliability.",
    "disposition": "completed",
    "decision_ref": "user:关闭 Matrix 优化任务",
    "closed_at": "2026-09-05T01:53:25.379609Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
