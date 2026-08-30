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
    "task_id": "REPORT-003B",
    "summary": "Implement Equipment List source inspection, preview, and controlled report-region update from EquipmentID.docx and the configured calibration workbook.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Read and deduplicate equipment references from the project EquipmentID.docx, enrich them from the active Settings Equipment calibration Excel using the legacy All Equip. mapping or the current structured layout, preview matches, unresolved external-equipment overrides, and expiry warnings, then update only the 7. EQUIPMENTS table after source/report fingerprints and required acknowledgements are verified. Archive the prior report through the existing publication kernel. Do not modify EquipmentID.docx, the calibration workbook, controlled templates, golden reports, or other real project files.",
    "scope_paths": [
      "docs/task_board.md",
      "docs/report_generation_architecture.md",
      "backend/application/external_resource_service.py",
      "backend/application/external_excel_read_service.py",
      "backend/application/equipment_report_update_service.py",
      "backend/application/current_report_update_service.py",
      "backend/infrastructure/office/equipment_id_document_reader.py",
      "backend/infrastructure/office/__init__.py",
      "backend/infrastructure/office/test_report_document_gateway.py",
      "backend/api/dependencies.py",
      "backend/api/routes_report_workspace.py",
      "frontend/src/api/client.ts",
      "frontend/src/features/report-workspace/reportWorkspaceModel.ts",
      "frontend/src/features/report-workspace/reportWorkspaceModel.test.ts",
      "frontend/src/features/report-workspace/ReportWorkspace.tsx",
      "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
      "frontend/src/workbench.css",
      "tests/unit/test_external_resource_service.py",
      "tests/unit/test_external_excel_read_service.py",
      "tests/unit/test_equipment_id_document_reader.py",
      "tests/unit/test_equipment_report_update_service.py",
      "tests/unit/test_current_report_update_service.py",
      "tests/unit/test_test_report_document_gateway.py",
      "tests/integration/test_report_workspace_api.py"
    ],
    "risk_reasons": [
      "The feature replaces a current Word report artifact in an official project workspace through a scoped update.",
      "The current report may contain authoritative manual or reviewer edits that must be preserved outside the Equipment List table.",
      "The source EquipmentID.docx and configured calibration workbook are external authorities and must remain read-only."
    ],
    "activation_head": "7e000c5919889d9b93f9b5522ea51efb5790a9c9",
    "started_at": "2026-08-30T16:14:23.026146Z",
    "updated_at": "2026-08-30T22:55:52.719068Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "REPORT-003B",
      "stage": "revision",
      "status": "running",
      "summary": "用户已补齐 EquipmentID.docx 和 Equipment calibration Excel，要求重新执行真实冒烟测试。",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "REPORT-003A",
    "tier": "high_risk",
    "subject": "4cbc68bdbb2c08fbd689939f89817c936d54f580",
    "summary": "Implement the current internal report section-update and safe publication kernel, using existing LLCR Result/Comment synchronization as the first adapter.",
    "disposition": "completed",
    "decision_ref": "用户明确回复：关闭",
    "closed_at": "2026-08-30T14:03:30.904124Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
