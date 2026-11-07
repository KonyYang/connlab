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
    "task_id": "TASK_REPORT_TEMPLATE_PHOTOS_PREVIEW_20261107",
    "tier": "high_risk",
    "subject": "d22ae1f5bb5ba104e0d78bd144dc669117c2f30b",
    "summary": "Report automation batch 5: approved-original coverage, batch photo candidates and confirmation, figure numbering/reference checks, and version-bound Word visual preview.",
    "disposition": "cancelled",
    "decision_ref": "User explicitly requested task closure on 2026-11-07. Stop batch 5 before final browser and all-page Word acceptance and integration. Preserve clean candidate 360d100ee330e9c06168dd1daea7de8c641d74e4 in the isolated resumed branch and all test evidence. QA reports 288 Python and 137 frontend tests passed plus build; full acceptance remains incomplete. No integration, push, cleanup or real file changes.",
    "closed_at": "2026-11-07T04:14:15.094568Z"
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
    },
    {
      "task_id": "TASK_LLCR_RESULT_SEMANTICS_20261023",
      "tier": "standard",
      "subject": "1c5c8a07701860d827ac0b0032e1040bf6b76a16",
      "summary": "Correct LLCR absolute resistance versus delta semantics without changing real reports",
      "disposition": "completed",
      "decision_ref": "User explicitly confirmed final Close after 261-test LLCR acceptance",
      "closed_at": "2026-10-22T23:55:52.392518Z"
    },
    {
      "task_id": "TASK_REPORT_CAPABILITIES_3_7_20261026",
      "tier": "high_risk",
      "subject": "41e6caed8dc1621d25065e0c54bfe1963922d3bf",
      "summary": "Report Workspace: persistent provenance, temperature/CR, mechanical appendices, photo slots and checked customer copies",
      "disposition": "completed",
      "decision_ref": "User explicitly confirmed closing the current Report Workspace capabilities 3-7 task on 2026-10-27.",
      "closed_at": "2026-10-26T23:47:10.164767Z"
    },
    {
      "task_id": "TASK_UNIFIED_PROJECT_LIBRARY_20261027",
      "tier": "high_risk",
      "subject": "f46aa1defba6442bcfe057fd976ef5566e4e577f",
      "summary": "Unified project library: managed batch intake, mutable titles, portable project data and offline takeover",
      "disposition": "completed",
      "decision_ref": "User explicitly requested closing this task, retaining local commits, with no push or publication.",
      "closed_at": "2026-10-27T23:03:07.142347Z"
    },
    {
      "task_id": "TASK_GROUP_COMPLETION_20261028",
      "tier": "high_risk",
      "subject": "5ad3ba35ac03251caf39e83396b18c3b7da09d78",
      "summary": "Group completion tracking and project registry summary",
      "disposition": "completed",
      "decision_ref": "用户确认关闭组别完成统计任务",
      "closed_at": "2026-10-27T23:53:40.876783Z"
    },
    {
      "task_id": "TASK_MECHANICAL_SUMMARY_TOOL_20261028",
      "tier": "standard",
      "subject": "b74f4d0847ed5be7cc42cba57b4438518d2ca4cf",
      "summary": "Standalone mechanical test summary tool",
      "disposition": "completed",
      "decision_ref": "用户确认关闭 Tools 独立机械 Summary 第一部分",
      "closed_at": "2026-10-28T14:02:09.933828Z"
    },
    {
      "task_id": "TASK_PROJECT_IMPORT_ENTRY_20261028",
      "tier": "standard",
      "subject": "a7a547ecde2b7b76247ee25c4c57a803b84300f3",
      "summary": "Consolidate project import entry under Projects",
      "disposition": "completed",
      "decision_ref": "User explicitly requested closing this task, retaining local commits, with no push or publication. Local close only; --publish-close intentionally omitted.",
      "closed_at": "2026-10-29T00:11:03.627184Z"
    },
    {
      "task_id": "TASK_IMPORT_PROJECTS_UX_20261029",
      "tier": "standard",
      "subject": "6f2b6f8ee517bd47df32b9daf06a09f1cc9ab373",
      "summary": "Simplify Import Projects selection, preview, results and restore entry",
      "disposition": "completed",
      "decision_ref": "User explicitly requested closing this completed task; preserve local commits. Existing no-push/no-publication instruction remains in force. Local close only; --publish-close omitted.",
      "closed_at": "2026-10-29T22:42:59.921841Z"
    },
    {
      "task_id": "TASK_EQUIPMENT_MERGED_TABLE_20261030",
      "tier": "standard",
      "subject": "33f26b1814b4ecca95614ea3d4f0fdfe755d1766",
      "summary": "Recognize horizontally merged equipment tables and explain reports without equipment tables",
      "disposition": "completed",
      "decision_ref": "User explicitly requested final Close of the completed equipment-table source-code repair after 123 passing tests and successful browser upload/download validation on 2026-10-30.",
      "closed_at": "2026-10-30T00:00:01.969757Z"
    },
    {
      "task_id": "TASK_EQUIPMENT_TABLE_FONT_20261030",
      "tier": "standard",
      "subject": "d1ee9f3c58be943f5ec4e7e6536e2e7020e93b7c",
      "summary": "Preserve equipment table typography after clearing and refilling cells",
      "disposition": "completed",
      "decision_ref": "User explicitly requested closing the current equipment-table font repair task after 127 affected tests, 164 release checks, and successful new-EXE validation of three real document scenarios.",
      "closed_at": "2026-10-30T05:59:50.377281Z"
    },
    {
      "task_id": "TASK_TOOLS_FOLDER_ENCRYPTION_20261030",
      "tier": "standard",
      "subject": "60b5f073724cd0d78e2168a1d1ad518d4e21eebf",
      "summary": "Batch encrypted Word/Excel copies from a selected folder without modifying originals",
      "disposition": "completed",
      "decision_ref": "User explicitly requested final task close after the Tools layout, encryption and copy refinements; final UI matrix 33 passed, production build and isolated browser checks completed.",
      "closed_at": "2026-10-31T08:53:23.134515Z"
    },
    {
      "task_id": "TASK_IMPORT_FLOW_COMPACT_20261030",
      "tier": "micro",
      "subject": "35c18660c16871513836c7fab9da4fdd50f6e726",
      "summary": "Simplify import controls and confirmation; return to full Projects",
      "disposition": "completed",
      "decision_ref": "User explicitly approved local close of prior task and start of full managed project import implementation; retain all commits and evidence; no push or publication.",
      "closed_at": "2026-10-31T21:21:46.655993Z"
    },
    {
      "task_id": "TASK_MANAGED_PROJECT_IMPORT_20261101",
      "tier": "standard",
      "subject": "4f9fe9fb08fb793000f7272a1f7508b662e1d5b4",
      "summary": "Imported projects use the standard project catalog and workbench with truthful completeness",
      "disposition": "completed",
      "decision_ref": "User explicitly confirmed task Close. Preserve local commits, isolated copies and acceptance records. Existing no-push/no-publication restriction remains in force; local close only, --publish-close omitted.",
      "closed_at": "2026-11-01T10:42:49.086984Z"
    },
    {
      "task_id": "TASK_BASIC_INFO_RESULT_DEFAULT_20261101",
      "tier": "micro",
      "subject": "23df9f3ae2701d83eca8db11d97c880109486892",
      "summary": "Default Basic Information Test Result to In progress",
      "disposition": "completed",
      "decision_ref": "User explicitly requested closing the current Basic Information field refinements task. Preserve local commits and acceptance records; existing no-push/no-publication restriction remains. Local close only; --publish-close omitted.",
      "closed_at": "2026-11-01T11:30:40.142659Z"
    },
    {
      "task_id": "TASK_GROUP_COMPLETION_DESCRIPTION_20261101",
      "tier": "high_risk",
      "subject": "bca6b7ebe4994480d6127976e81b84d31e42e6ee",
      "summary": "Compact group completion controls with saved descriptions",
      "disposition": "completed",
      "decision_ref": "User explicitly requested closing the current group completion description task. Preserve local commits, consistent development database backups and acceptance records. Existing no-push/no-publication restriction persists. Local close only; --publish-close omitted. Leave authorized running development backend unchanged.",
      "closed_at": "2026-11-01T14:02:54.674013Z"
    },
    {
      "task_id": "TASK_PROJECTS_DEFAULT_ONGOING_20261101",
      "tier": "micro",
      "subject": "3b473cc2cd203ebb2165eedd25fb7ae6789dfb19",
      "summary": "Default Projects view to On-going",
      "disposition": "completed",
      "decision_ref": "User explicitly authorized local closing of accepted Projects default On-going micro task to release App.test.tsx scope for the single-project import task. Retain commits and evidence; no push/publication; --publish-close omitted.",
      "closed_at": "2026-11-02T00:20:02.997114Z"
    },
    {
      "task_id": "TASK_SINGLE_PROJECT_IMPORT_20261102",
      "tier": "standard",
      "subject": "e02b11e8b06d58c6cbcdb0ddc729abc708d0f187",
      "summary": "Make Import Projects default to one complete project folder",
      "disposition": "completed",
      "decision_ref": "用户明确要求仅本地关闭单项目导入任务，不推送、不发布",
      "closed_at": "2026-11-02T10:21:08.363527Z"
    },
    {
      "task_id": "TASK_LTR_REMARKS_DEFAULT_20261102",
      "tier": "high_risk",
      "subject": "dba951276d3da39cdda78039804087bb95e53c3d",
      "summary": "Correct Remarks PO defaults for Basic Information and LTR registration",
      "disposition": "completed",
      "decision_ref": "用户明确要求仅本地关闭，不推送、不发布",
      "closed_at": "2026-11-02T10:32:44.622761Z"
    },
    {
      "task_id": "TASK_PUBLIC_PROJECT_PATHS_20261102",
      "tier": "high_risk",
      "subject": "2732e17a4a683d9332c6156ed13bfae99d95c105",
      "summary": "Correct public project folder names",
      "disposition": "completed",
      "decision_ref": "User authorized local close only; no push or publication.",
      "closed_at": "2026-11-02T23:01:39.946185Z"
    },
    {
      "task_id": "TASK_PUBLIC_PARTIAL_SYNC_20261103",
      "tier": "high_risk",
      "subject": "0429140e295d23a064249c9ee58c1d1d05f752b8",
      "summary": "Safely synchronize non-conflicting project files",
      "disposition": "completed",
      "decision_ref": "User requested local close only; no push or publication.",
      "closed_at": "2026-11-02T23:27:01.838552Z"
    },
    {
      "task_id": "TASK_SAMPLE_DEPOSITION_20261102",
      "tier": "micro",
      "subject": "8fabcd24c0aadae48e40de816a67723e7141f00f",
      "summary": "Shorten automatic sample deposition",
      "disposition": "completed",
      "decision_ref": "User requested local close only; no push or publication.",
      "closed_at": "2026-11-02T23:35:38.490026Z"
    },
    {
      "task_id": "TASK_PUBLIC_EXISTING_DIRS_20261103",
      "tier": "high_risk",
      "subject": "f3248ad35b3ffc8b35b81699742af9764ce20f3d",
      "summary": "Require existing public root and year directories",
      "disposition": "completed",
      "decision_ref": "User requested local close only; no push or publication.",
      "closed_at": "2026-11-02T23:42:25.372915Z"
    },
    {
      "task_id": "TASK_PUBLIC_FOLDER_MESSAGE_20261103",
      "tier": "standard",
      "subject": "84899bf91a10467347cb0853c007c1fc379341d2",
      "summary": "Clarify missing public folder guidance",
      "disposition": "completed",
      "decision_ref": "User requested local close only; no push or publication.",
      "closed_at": "2026-11-03T00:09:00.843899Z"
    },
    {
      "task_id": "TASK_OPEN_PUBLIC_FOLDER_20261103",
      "tier": "standard",
      "subject": "5b3d1b53952cc54d0197cde01865fe5c2c584428",
      "summary": "Open synced public project folder",
      "disposition": "completed",
      "decision_ref": "User explicitly requested local close only, no push or publication.",
      "closed_at": "2026-11-03T10:09:11.879533Z"
    },
    {
      "task_id": "TASK_PUBLIC_SYNC_CURRENT_20261103",
      "tier": "standard",
      "subject": "8ed113d0f9e0b4062d42ebb4844da5b4df1ab855",
      "summary": "Show public folder for current and partial sync",
      "disposition": "completed",
      "decision_ref": "User requested local close only; no push or publication.",
      "closed_at": "2026-11-03T15:06:34.859125Z"
    },
    {
      "task_id": "TASK_SIDEBAR_PROJECT_FOLDER_20261103",
      "tier": "standard",
      "subject": "6c32846fcb3ba56ecc18a16c601717dc8415b888",
      "summary": "Open current project folder from sidebar",
      "disposition": "completed",
      "decision_ref": "User explicitly requested local close of both ready_for_close tasks; preserve commits and do not push or publish.",
      "closed_at": "2026-11-04T22:22:07.622933Z"
    },
    {
      "task_id": "TASK_IMPORT_RECYCLE_CONSISTENCY_20261105",
      "tier": "micro",
      "subject": "e1e8a2a8f47d19cd4e85aa8d51e570abf9fad8cb",
      "summary": "Give imported projects the same Recycle action as local projects",
      "disposition": "completed",
      "decision_ref": "User explicitly requested local close of both ready_for_close tasks; preserve commits and do not push or publish.",
      "closed_at": "2026-11-04T22:22:16.639026Z"
    },
    {
      "task_id": "TASK_ONE_CLICK_PROJECT_INTAKE_20261105",
      "tier": "standard",
      "subject": "30c36e4190ce947ee1823a11945e713eb43c9cf7",
      "summary": "Receive or restore one project from a folder with one normal action",
      "disposition": "completed",
      "decision_ref": "User explicitly authorized closing the task and pushing current master to origin/master on 2026-11-05.",
      "closed_at": "2026-11-05T00:05:55.274746Z"
    },
    {
      "task_id": "TASK_DIRECT_PROJECT_IMPORT_20261105",
      "tier": "standard",
      "subject": "18ebdc74d9f8d88621d1ed36c6508e7f385806e2",
      "summary": "Open the native project-folder picker directly from Projects and show import UI only for exceptions or recovery.",
      "disposition": "completed",
      "decision_ref": "White 已验收：受影响测试 89/89 通过，TypeScript tsc -b 0 错误；Vite 生产构建由 White 在本机无沙箱环境复核通过（EXIT=0, built in 2.03s）。保留既有 commits；仅本地关闭，不推送、不发布。",
      "closed_at": "2026-11-05T05:55:31.532314Z"
    },
    {
      "task_id": "TASK_LTR_EXCEL_SAVE_20261105",
      "tier": "high_risk",
      "subject": "74607313ae834e84997b13fb0368eba0b30c114c",
      "summary": "Fix LTR workbook save after Excel data recovery open",
      "disposition": "completed",
      "decision_ref": "User explicitly authorized local Close of completed LTR Excel Save fix and starting temporary-to-formal conversion; preserve commits, no push or publication.",
      "closed_at": "2026-11-05T14:15:10.369920Z"
    },
    {
      "task_id": "TASK_TEMPORARY_FORMAL_20261105",
      "tier": "high_risk",
      "subject": "ee9f7f990efb37f7e2f3e5c4596519eeb39eaeec",
      "summary": "Register a formal LTR on an existing temporary project without losing its data",
      "disposition": "completed",
      "decision_ref": "User requested closing the current task. Local close only under persistent no-push/no-publication instruction; latest draft and folder redesign remains discussion only.",
      "closed_at": "2026-11-05T23:57:51.361754Z"
    },
    {
      "task_id": "TASK_MECHANICAL_FOLDER_20261106",
      "tier": "standard",
      "subject": "b5328e733c43919772ec6ace460755a0a8ce3711",
      "summary": "Generate mechanical summaries from a folder with evidence-bound review and approved layouts",
      "disposition": "completed",
      "decision_ref": "User explicitly requested closing the completed mechanical folder summary task. Preserve local commits; no push or publication under the persistent session preference.",
      "closed_at": "2026-11-06T05:01:56.900493Z"
    },
    {
      "task_id": "TASK_MATERIALS_TOOLS_20261106",
      "tier": "high_risk",
      "subject": "5c8ced47830f878bde55c8daec5d742c2d69fef1",
      "summary": "Replace temporary-project creation with material folders and standalone Matrix/Fee tools",
      "disposition": "cancelled",
      "decision_ref": "User requested closing the current task on 2026-11-07. Stop before final independent review, QA and integration. Preserve development commit 5f5361faf4839e7628488058454366a7a8275912 on codex/materials-tools-20261106 and its worktree. Local close only; no push or publication; not accepted as complete.",
      "closed_at": "2026-11-06T16:06:14.113769Z"
    },
    {
      "task_id": "TASK_MATERIALS_TOOLS_20261107",
      "tier": "high_risk",
      "subject": "98cce66f778d6ef98fc09b1fc403edd8af1c5fd7",
      "summary": "Resume materials saving and standalone Matrix/Fee tools final review and local integration",
      "disposition": "completed",
      "decision_ref": "User explicitly requested closing the completed materials saving and standalone Matrix/Fee tools task on 2026-11-07. Preserve integrated local commits. Persistent local-only instruction remains: no push or publication; publish-close intentionally omitted.",
      "closed_at": "2026-11-06T21:01:34.514404Z"
    },
    {
      "task_id": "TASK_REPORT_TOOLS_BRIDGE_20261107",
      "tier": "standard",
      "subject": "ea7434e293ab61d3522857368748e8297b77d70e",
      "summary": "Unify report working copy and bridge reviewed mechanical/temperature Tools outputs into Report",
      "disposition": "completed",
      "decision_ref": "User explicitly confirmed closing the completed report working-copy and Tools bridge task, including native Word visual acceptance. Preserve all local commits; no push or publication. Local close only; --publish-close intentionally omitted.",
      "closed_at": "2026-11-06T21:58:12.773252Z"
    },
    {
      "task_id": "TASK_REPORT_BATCH_ASSEMBLY_20261107",
      "tier": "standard",
      "subject": "a2c926a3bec1b9711b9de69285fad92ced895595",
      "summary": "Report batch 3: controlled evidence inventory, Matrix coverage and one-copy batch assembly",
      "disposition": "completed",
      "decision_ref": "User explicitly accepted and closed batch 3 and authorized starting batch 4. Preserve local commits; no push, publication or real business file changes.",
      "closed_at": "2026-11-07T01:23:17.767261Z"
    },
    {
      "task_id": "TASK_REPORT_RESULT_SEMANTICS_20261107",
      "tier": "high_risk",
      "subject": "3b5e4bed89210e4cbbcf4827a3963f2d63b963e6",
      "summary": "Report automation batch 4: scoped electrical/qualitative and related-report evidence, precise fact roles and multistage semantics.",
      "disposition": "completed",
      "decision_ref": "User accepted batch 4 and explicitly requested task closure; retain local commits and preserve the existing no-push instruction.",
      "closed_at": "2026-11-07T02:47:48.494929Z"
    },
    {
      "task_id": "TASK_REPORT_TEMPLATE_PHOTOS_PREVIEW_20261107",
      "tier": "high_risk",
      "subject": "15000413ef8899eaaac44f65d5a9f2061cde9c9b",
      "summary": "Report automation batch 5: approved-original coverage, batch photo candidates and confirmation, figure numbering/reference checks, and version-bound Word visual preview.",
      "disposition": "cancelled",
      "decision_ref": "User explicitly requested task closure while batch 5 remains unfinished. Stop implementation; retain 12 modified and 13 untracked files in isolated worktree and all test evidence. No integration, deletion, reset, restore, stash or push. Final QA, browser and Word visual acceptance remain incomplete.",
      "closed_at": "2026-11-07T03:39:19.537465Z"
    }
  ],
  "tasks": {
    "TASK_REPORT_TEMPLATE_PHOTOS_PREVIEW_20261107": {
      "slot": "main",
      "state": "ready_for_close",
      "worktree": "C:\\Users\\White\\.codex\\worktrees\\report-tools-bridge\\connlab",
      "branch": "codex/report-batch5-final-acceptance-20261107",
      "resources": [],
      "integrated_head": "ad18b550aea326a6a9b620d025f610d13e45ba88",
      "task": {
        "task_id": "TASK_REPORT_TEMPLATE_PHOTOS_PREVIEW_20261107",
        "summary": "Report automation batch 5: approved-original coverage, batch photo candidates and confirmation, figure numbering/reference checks, and version-bound Word visual preview.",
        "tier": "high_risk",
        "route": "full_chain",
        "scope": "Implement complete batch 5 and applicable sections 8/11 of report_automation_plan_20261107.md in the existing Report Workspace, using isolated data/copies. Real reports/templates/project materials read-only; no push, no formal publication, no batch6 expansion. User authorized autonomous acceptance and local task close after verified completion.",
        "scope_paths": [
          "backend/api/dependencies.py",
          "backend/api/report_authoring_schemas.py",
          "backend/api/routes_report_authoring.py",
          "backend/application/report_authoring/assembly.py",
          "backend/application/report_authoring/document_review.py",
          "backend/application/report_authoring/photo_plan.py",
          "backend/application/report_authoring/service.py",
          "backend/infrastructure/office/report_authoring/batch_document.py",
          "backend/infrastructure/office/report_authoring/document_review.py",
          "backend/infrastructure/office/report_authoring/visual_preview.py",
          "backend/infrastructure/office/report_authoring/word_copy.py",
          "backend/infrastructure/office/word_document_gateway.py",
          "docs/PROJECT_CONTEXT.md",
          "docs/operational/report_automation_plan_20261107.md",
          "docs/operational/report_template_photos_preview_20261107.md",
          "frontend/src/api/reportAuthoring.ts",
          "frontend/src/api/reportAuthoringBatch.ts",
          "frontend/src/features/report-workspace/ReportAuthoringPanel.tsx",
          "frontend/src/features/report-workspace/ReportBatchPreparation.tsx",
          "frontend/src/features/report-workspace/ReportDocumentReview.test.tsx",
          "frontend/src/features/report-workspace/ReportDocumentReview.tsx",
          "frontend/src/features/report-workspace/ReportPhotoPlan.test.tsx",
          "frontend/src/features/report-workspace/ReportPhotoPlan.tsx",
          "frontend/src/features/report-workspace/ReportVisualPreview.test.tsx",
          "frontend/src/features/report-workspace/ReportVisualPreview.tsx",
          "frontend/src/features/report-workspace/reportAuthoringPanel.css",
          "tests/integration/test_report_document_review_api.py",
          "tests/unit/report_authoring/test_document_review.py",
          "tests/unit/report_authoring/test_photo_plan.py",
          "tests/unit/report_authoring/test_visual_preview.py",
          "tests/unit/test_word_document_gateway.py"
        ],
        "risk_reasons": [
          "Native Word fidelity, cross-project original coverage and executable Office rendering require independent review and QA."
        ],
        "activation_head": "75d9eb36512f67d4ee22eda070876f0e527b11ad",
        "started_at": "2026-11-07T04:33:36.854373Z",
        "updated_at": "2026-11-07T05:05:19.294268Z",
        "checkpoint": {
          "schema": "connlab.sol-task-checkpoint",
          "version": 1,
          "task_id": "TASK_REPORT_TEMPLATE_PHOTOS_PREVIEW_20261107",
          "stage": "final_visual_revalidation",
          "status": "running",
          "summary": "User approved word_copy.py scope; productionwriter amendment completed. Clean reviewed fix cdaf429b818f6f0782cb6c949e90570856a8b6bd adds bounded flowing-heading protection and publicAPI regression, Developer34passed. IndependentQA rerendering021 layout on new process/final bytes and checking all pages; original288/137/build and032/031/synthetic evidence retained by product-path equivalence. No integration/push/real writes.",
          "requires_user": false
        },
        "report": {
          "schema": "connlab.sol-task-report",
          "version": 1,
          "task_id": "TASK_REPORT_TEMPLATE_PHOTOS_PREVIEW_20261107",
          "subject": "15d9208be47f26f1b0354d3f04aab55c779f9eb8",
          "summary": "Batch5: scoped original-content review, confirmed batch photo plans, precise figure/reference numbering, immutable version-bound Word preview; bounded reference-result pagination repair. Isolated acceptance only; no real-file mutation or formal release.",
          "scope_ok": true,
          "changed_paths": [
            "backend/api/dependencies.py",
            "backend/api/report_authoring_schemas.py",
            "backend/api/routes_report_authoring.py",
            "backend/application/report_authoring/assembly.py",
            "backend/application/report_authoring/document_review.py",
            "backend/application/report_authoring/photo_plan.py",
            "backend/application/report_authoring/service.py",
            "backend/infrastructure/office/report_authoring/batch_document.py",
            "backend/infrastructure/office/report_authoring/document_review.py",
            "backend/infrastructure/office/report_authoring/visual_preview.py",
            "backend/infrastructure/office/report_authoring/word_copy.py",
            "backend/infrastructure/office/word_document_gateway.py",
            "docs/PROJECT_CONTEXT.md",
            "docs/operational/report_automation_plan_20261107.md",
            "docs/operational/report_template_photos_preview_20261107.md",
            "frontend/src/api/reportAuthoring.ts",
            "frontend/src/api/reportAuthoringBatch.ts",
            "frontend/src/features/report-workspace/ReportAuthoringPanel.tsx",
            "frontend/src/features/report-workspace/ReportBatchPreparation.tsx",
            "frontend/src/features/report-workspace/ReportDocumentReview.test.tsx",
            "frontend/src/features/report-workspace/ReportDocumentReview.tsx",
            "frontend/src/features/report-workspace/ReportPhotoPlan.test.tsx",
            "frontend/src/features/report-workspace/ReportPhotoPlan.tsx",
            "frontend/src/features/report-workspace/ReportVisualPreview.test.tsx",
            "frontend/src/features/report-workspace/ReportVisualPreview.tsx",
            "frontend/src/features/report-workspace/reportAuthoringPanel.css",
            "tests/integration/test_report_document_review_api.py",
            "tests/unit/report_authoring/test_document_review.py",
            "tests/unit/report_authoring/test_photo_plan.py",
            "tests/unit/report_authoring/test_visual_preview.py",
            "tests/unit/test_word_document_gateway.py"
          ],
          "validation": [
            {
              "status": "passed",
              "kind": "related_full_matrix",
              "subject": "360d100ee330e9c06168dd1daea7de8c641d74e4",
              "summary": "288 Python, 137 frontend, typecheck/build passed; bytes-equivalent recovery plus affected delta retested.",
              "evidence": {
                "path": "D:\\PythonProject\\connlab\\tmp\\report_batch5_20261107\\qa_360d100e\\matrix.json",
                "raw_sha256": "37a686a48822cebebf4903d19879a1b336a25d3c7a128af2d3314e1e5fed393f"
              }
            },
            {
              "status": "passed",
              "kind": "final_affected_matrix",
              "subject": "cdaf429b818f6f0782cb6c949e90570856a8b6bd",
              "summary": "52 independent Python tests after local pagination fix; final subject is docs-only successor.",
              "evidence": {
                "path": "D:\\PythonProject\\connlab\\tmp\\report_batch5_20261107\\qa_cdaf429b\\matrix.json",
                "raw_sha256": "0ec5c530c60a6c1a3faae3469e4073761e5c960b76a1eddc64a7efc37437bc4c"
              }
            },
            {
              "status": "passed",
              "kind": "actual_product_ui",
              "summary": "032 base/photo comparison/confirmation/batch/Word preview/reload, visually_reviewed without content approval.",
              "evidence": {
                "path": "D:\\PythonProject\\connlab\\tmp\\report_batch5_20261107\\browser_acceptance_c9f1dc0c.md",
                "raw_sha256": "e039aefb93cc5656cf7768f1089a7be497755cf7e0f85901bcbd3b5f78a85a0d"
              }
            },
            {
              "status": "passed",
              "kind": "actual_word_all_pages_and_inputs",
              "summary": "4 final PDF cases, 63 pages inspected; final021 orphan headings fixed;198 original/copied inputs SHA unchanged. Final8793 drain logged two nonfatal IUnknown release diagnostics despite successful exact PDF/HTTP200 and no new leaked Word; retained as residual, not hidden.",
              "evidence": {
                "path": "D:\\PythonProject\\connlab\\tmp\\report_batch5_20261107\\finalQA.md",
                "raw_sha256": "7053dd9470048b2a970822fa505b4da5c958afc96f96dd1d295008f089dd2e02"
              },
              "shutdown_evidence": {
                "path": "D:\\PythonProject\\connlab\\tmp\\report_batch5_20261107\\service_shutdown.md",
                "raw_sha256": "ed47f9bfdc10241464feff27e00ddc9ce0d18d2f05e504a7cf95a9c77943c7d2"
              }
            }
          ],
          "roles": {
            "planner": {
              "status": "passed",
              "identity": "/root/batch5_planner",
              "ref": "docs/operational/report_automation_plan_20261107.md",
              "summary": "Independent original planning context; retained scope batch5 and applicable sections8/11."
            },
            "developer": {
              "status": "passed",
              "identity": "/root/batch5_developer",
              "subject": "cdaf429b818f6f0782cb6c949e90570856a8b6bd",
              "docs_subject": "15d9208be47f26f1b0354d3f04aab55c779f9eb8",
              "summary": "Implemented candidate and bounded RED/GREEN fix,34 affected Developer checks, clean final commits."
            },
            "reviewer": {
              "status": "passed",
              "identity": "/root",
              "summary": "Independent exact candidate and bounded-fix reviews plus final docs-only diff review.",
              "refs": [
                {
                  "path": "D:\\PythonProject\\connlab\\tmp\\report_batch5_20261107\\review_360d100e.md",
                  "raw_sha256": "2b4acd3059cf75ee2bffabe21261004914efb2e13c29e458d4ebd7a5fe1c3e1d"
                },
                {
                  "path": "D:\\PythonProject\\connlab\\tmp\\report_batch5_20261107\\review_cdaf429b.md",
                  "raw_sha256": "9af26154d0bfbccb07af8733b8668dfc0ac49bd5dd083ad228983992f4f1e479"
                }
              ]
            },
            "qa": {
              "status": "passed",
              "identity": "/root/batch5_qa",
              "subject": "cdaf429b818f6f0782cb6c949e90570856a8b6bd",
              "ref": {
                "path": "D:\\PythonProject\\connlab\\tmp\\report_batch5_20261107\\finalQA.md",
                "raw_sha256": "7053dd9470048b2a970822fa505b4da5c958afc96f96dd1d295008f089dd2e02"
              },
              "summary": "Independent full/delta automated verification, actual API and all-page Word checks; final docs-only successor."
            },
            "integrator": {
              "status": "passed",
              "identity": "/root/batch5_integrator",
              "subject": "15d9208be47f26f1b0354d3f04aab55c779f9eb8",
              "summary": "Independent exact identity/scope/Git topology/clean worktrees/raw-evidence verification; actual integration remains pending until writer call succeeds."
            }
          },
          "integration": {
            "status": "passed",
            "mode": "serial_local_merge",
            "subject": "15d9208be47f26f1b0354d3f04aab55c779f9eb8",
            "primary_before": "6a57fd9380be6f85b41e720f5d993c418f470ed0",
            "integrated_head": "ad18b550aea326a6a9b620d025f610d13e45ba88",
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
