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
    "task_id": "TASK_PROJECT_FOLDER_ACTIONS_20261119",
    "tier": "micro",
    "subject": "427807f12a89582d064fffa8ab7d4cf372cb3014",
    "summary": "Move the project-folder button out of the sidebar and onto the four project subpage headers.",
    "disposition": "completed",
    "decision_ref": "User asked to close the just-delivered project-folder action task. Local closure under the standing no-push workflow; preserve the separate encryption task and evidence.",
    "closed_at": "2026-11-19T11:10:42.083993Z"
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
    },
    {
      "task_id": "TASK_REPORT_TEMPLATE_PHOTOS_PREVIEW_20261107",
      "tier": "high_risk",
      "subject": "d22ae1f5bb5ba104e0d78bd144dc669117c2f30b",
      "summary": "Report automation batch 5: approved-original coverage, batch photo candidates and confirmation, figure numbering/reference checks, and version-bound Word visual preview.",
      "disposition": "cancelled",
      "decision_ref": "User explicitly requested task closure on 2026-11-07. Stop batch 5 before final browser and all-page Word acceptance and integration. Preserve clean candidate 360d100ee330e9c06168dd1daea7de8c641d74e4 in the isolated resumed branch and all test evidence. QA reports 288 Python and 137 frontend tests passed plus build; full acceptance remains incomplete. No integration, push, cleanup or real file changes.",
      "closed_at": "2026-11-07T04:14:15.094568Z"
    },
    {
      "task_id": "TASK_REPORT_TEMPLATE_PHOTOS_PREVIEW_20261107",
      "tier": "high_risk",
      "subject": "15d9208be47f26f1b0354d3f04aab55c779f9eb8",
      "summary": "Report automation batch 5: approved-original coverage, batch photo candidates and confirmation, figure numbering/reference checks, and version-bound Word visual preview.",
      "disposition": "completed",
      "decision_ref": "User explicitly authorized autonomous acceptance and local close after batch5 completion. Independent code review, QA matrices, actual publicUI/API and all63 final Word pages passed; bounded pagination repair approved and verified. Preserve all local commits/evidence; no push or publication; publish-close intentionally omitted.",
      "closed_at": "2026-11-07T05:05:58.880106Z"
    },
    {
      "task_id": "TASK_REPORT_DELIVERY_CONTROLLED_SAVE_20261107",
      "tier": "high_risk",
      "subject": "81b6934643cce76f748770343e9a717c0527ac14",
      "summary": "Report batch 6 part 1: exact-version delivery checks and controlled Internal/Customer save through existing History protections",
      "disposition": "completed",
      "decision_ref": "User explicitly authorized autonomous acceptance and local completed close of batch6 part1. Independent Reviewer, QA, actual UI/API, all9 native Word pages, real file-lock partial/save/restart/resume, raw target/History identities and source preservation passed. Independent Integrator performed verified serial local merge. Preserve all commits/evidence; no push or formal issuance; publish-close intentionally omitted.",
      "closed_at": "2026-11-07T07:19:39.211426Z"
    },
    {
      "task_id": "TASK_FOLDER_PARTIAL_GENERATION_20261107",
      "tier": "high_risk",
      "subject": "78e416e2ac95c24480af368b03b36c9da4b83325",
      "summary": "Generate independent project folder outputs despite individual artifact failures and summarize missing outputs",
      "disposition": "completed",
      "decision_ref": "User explicitly requested closing current task locally only on 2026-11-08. Preserve integrated partial-generation fix, all API test repairs, package and evidence. No push or publication; publish-close intentionally omitted.",
      "closed_at": "2026-11-08T01:38:18.677248Z"
    },
    {
      "task_id": "TASK_REPORT_EXISTING_TARGET_SELECTION_20261108",
      "tier": "standard",
      "subject": "ee78bf1e7b56c88af4253f95271a59320639ffca",
      "summary": "Make existing report result and appendix targeting discoverable and editable in the batch UI",
      "disposition": "completed",
      "decision_ref": "User requested acceptance and local Close only, preserving commits without push. Acceptance passed: integrated bytes and raw evidence match; 19 focused regressions passed, prior 145 frontend and 15 backend tests plus isolated browser/file acceptance verified; no blocking Standards or Spec findings. No real report, template or project material modified. Publication explicitly not authorized.",
      "closed_at": "2026-11-08T02:18:00.842368Z"
    },
    {
      "task_id": "TASK_SAVE_MATERIALS_DIALOG_STYLE_20261108",
      "tier": "micro",
      "subject": "382d52a644bb597d470722d4c1faa45d76f0697d",
      "summary": "Unify Save materials dialog with existing ConnLab visual styles",
      "disposition": "completed",
      "decision_ref": "User explicitly permits closing previous Save materials style task while continuing Import Projects picker optimization. Close locally and preserve integrated style, screenshot and validation evidence; no push or release in current work.",
      "closed_at": "2026-11-08T10:41:16.238599Z"
    },
    {
      "task_id": "TASK_IMPORT_FOLDER_PICKER_20261108",
      "tier": "standard",
      "subject": "ac2289143f8c833474bc1ffa41bd5e8e410f1604",
      "summary": "Modernize Import Projects folder selection and show immediate progress",
      "disposition": "completed",
      "decision_ref": "User explicitly requested local-only close of the current task on 2026-11-08; retain integrated code and validation evidence, including the documented native-window screenshot limitation. No push, no publication; publish-close intentionally omitted.",
      "closed_at": "2026-11-08T11:30:42.405240Z"
    },
    {
      "task_id": "TASK_IMPORT_PICKER_COMPACT_20261108",
      "tier": "standard",
      "subject": "309f00ab040687e5bf2c4bdedadc748f1089ffec",
      "summary": "Hide routine import progress overlays and size folder picker compactly",
      "disposition": "completed",
      "decision_ref": "User explicitly requests local-only close of compact picker task then settings automatic validation repair. Preserve commits and evidence; no push or publication.",
      "closed_at": "2026-11-08T11:56:20.017340Z"
    },
    {
      "task_id": "TASK_SETTINGS_AUTO_VALIDATION_20261108",
      "tier": "standard",
      "subject": "cfee828966377665d366bbdd552278a06f86c3b9",
      "summary": "Automatically refresh Settings validation without stale results overwriting edits",
      "disposition": "completed",
      "decision_ref": "User requested closing the completed Settings automatic validation task. Preserve integrated code and verification records; local-only, no push or publication; publish-close intentionally omitted.",
      "closed_at": "2026-11-08T12:22:25.508029Z"
    },
    {
      "task_id": "TASK_CLOSE_PROJECT_DIALOG_20261108",
      "tier": "standard",
      "subject": "5746b66eff7de83ff0f05323b203ec07710ce850",
      "summary": "Simplify and unify the Close project confirmation dialog",
      "disposition": "completed",
      "decision_ref": "User explicitly requested closing the current task locally only, with no push or publication. Preserve integrated code and validation records; publish-close intentionally omitted.",
      "closed_at": "2026-11-08T14:30:53.965058Z"
    },
    {
      "task_id": "TASK_REOPEN_PROJECT_ACTION_20261108",
      "tier": "standard",
      "subject": "23988f3e200cf4fab0915d920b4a0dda2a649c2c",
      "summary": "One-click Reopen project action without a reason form",
      "disposition": "completed",
      "decision_ref": "User explicitly requested closing the current task locally only, with no push or publication. Preserve integrated code and validation records; publish-close intentionally omitted.",
      "closed_at": "2026-11-08T14:58:17.746469Z"
    },
    {
      "task_id": "TASK_REMOVE_WORKBENCH_ACTIONS_TOGGLE_20261108",
      "tier": "micro",
      "subject": "28dd24ab9e5414dbcbcde1218c663a1be7077dfd",
      "summary": "Remove Hide/Show Actions toggle and keep Workbench action panels visible",
      "disposition": "completed",
      "decision_ref": "User explicitly confirmed closing this completed task. Persistent local-only instruction applies: preserve integrated code and validation, no push or publication; publish-close intentionally omitted.",
      "closed_at": "2026-11-08T15:30:23.201007Z"
    },
    {
      "task_id": "TASK_P3_STORAGE_MAINTENANCE_20261108",
      "tier": "high_risk",
      "subject": "b45a46f7d5b45cd9fa8000f437d1e6d15b613524",
      "summary": "Safely reclaim closed development copies and document minimal retention rules",
      "disposition": "completed",
      "decision_ref": "User explicitly accepted P3 maintenance and requested local Close, preserving all local commits without push. No publication authorized; --publish-close omitted.",
      "closed_at": "2026-11-08T22:02:43.332269Z"
    },
    {
      "task_id": "TASK_LTR_INFORMATION_WITHOUT_MATRIX_20261109",
      "tier": "micro",
      "subject": "760e90988ca3edd9cee7fc8a16f46375c2dceb48",
      "summary": "Show LTR Information before Matrix confirmation",
      "disposition": "completed",
      "decision_ref": "User explicitly authorized closing the completed LTR Information task locally before starting phase-one folder separation implementation. Preserve commits and evidence; no push or publication.",
      "closed_at": "2026-11-09T14:27:46.097903Z"
    },
    {
      "task_id": "TASK_PROJECT_FOLDER_BASIC_PHASE1_20261109",
      "tier": "high_risk",
      "subject": "461f7e7f54cc90bb89508e82d3ae4fed57ff8449",
      "summary": "Separate basic project folder creation and preserve public folder identity",
      "disposition": "completed",
      "decision_ref": "User explicitly requested final Close of the completed phase-one project-folder creation separation task after local integration and acceptance. Existing no-push/no-publication instruction remains in force: local close only, no publish-close flag. Preserve local commits, workspaces and acceptance evidence; no real business/public-drive mutations.",
      "closed_at": "2026-11-09T23:32:38.617342Z"
    },
    {
      "task_id": "TASK_QA_TEMP_RETENTION_SAFE_20261110",
      "tier": "high_risk",
      "subject": "9c169b8a8863dac4e5446a0217cd587b565122a0",
      "summary": "Manage isolated pytest artifacts on D with completed-run-only seven-day retention",
      "disposition": "completed",
      "decision_ref": "User confirmed final Close after local integration. Preserve all local commits and acceptance evidence; existing no-push/no-publication restriction remains in force. The User explicitly approved same-context self-review, automated tests and isolated acceptance instead of independent checks. Close locally only; --publish-close intentionally omitted. No real legacy cleanup or business-file operations.",
      "closed_at": "2026-11-09T23:59:43.167424Z"
    },
    {
      "task_id": "TASK_PROJECT_FILE_GENERATION_PHASE2_20261110",
      "tier": "high_risk",
      "subject": "6cd6ec7b5da9b0f4a5d23c2abbe84e3b46fa2683",
      "summary": "Independent Generate files with per-file prerequisites, protected replacement, recovery and isolated validation",
      "disposition": "completed",
      "decision_ref": "User explicitly confirmed final Close after accepted local integration. Close this task locally only; retain all product commits and acceptance evidence. The explicit no-push/no-publication restriction persists, and --publish-close is intentionally omitted. No real business files, public drive, database, application startup or release operation.",
      "closed_at": "2026-11-10T11:34:39.845485Z"
    },
    {
      "task_id": "TASK_DELETE_PROJECT_DIALOG_COMPACT_20261112",
      "tier": "micro",
      "subject": "3a7ac9a1a43fb8837179cb3dc91b96e94bc78960",
      "summary": "Compact Delete project confirmation using established dialog styling",
      "disposition": "completed",
      "decision_ref": "User explicitly confirmed closing the completed deletion confirmation dialog task locally only. Preserve implementation commits and acceptance evidence. Do not push or publish; --publish-close is intentionally omitted. Leave the separate existing-project-admission task unchanged. No business file or database operations.",
      "closed_at": "2026-11-11T22:25:15.103411Z"
    },
    {
      "task_id": "TASK_EXISTING_PROJECT_ADMISSION_20261111",
      "tier": "high_risk",
      "subject": "edbbf91472355cf4ee19f57e1a483793a56bdc6b",
      "summary": "Single-project existing-project adoption with authoritative LTR reuse, starter Matrix, stable identity, and automatic portable snapshots",
      "disposition": "completed",
      "decision_ref": "User conditionally authorized local Close of Add Existing Project once completion was verified. Verified ready_for_close, successful validation/review records, and implementation/integration retained in current master. Close locally only, preserve code and acceptance evidence. No push or publication; --publish-close intentionally omitted. No business files or databases are modified.",
      "closed_at": "2026-11-11T23:27:15.967530Z"
    },
    {
      "task_id": "TASK_DELETE_CONFIRMATION_MINIMAL_20261112",
      "tier": "micro",
      "subject": "73f526ce1b7b1b993e27901ad1e5359f61d26302",
      "summary": "Reduce deletion confirmation to project number, description and two actions",
      "disposition": "completed",
      "decision_ref": "User explicitly confirmed local Close of the completed minimal deletion confirmation task. Preserve implementation and acceptance evidence. No push or publication; --publish-close intentionally omitted. No business files or database operations.",
      "closed_at": "2026-11-11T23:46:50.999417Z"
    },
    {
      "task_id": "TASK_DATABASE_INIT_RACE_20261112",
      "tier": "high_risk",
      "subject": "48a5f3bf408ecbce6ab5f2600329b8d817117ede",
      "summary": "Fix repeated SQLite migration and concurrent cold database initialization; assess existing-project admission UX",
      "disposition": "completed",
      "decision_ref": "User accepted and explicitly closed this materials library task. Preserve all local commits and validation records. NO push or publication; --publish-close deliberately omitted. No cleanup of business data or test evidence/worktrees.",
      "closed_at": "2026-11-14T05:00:54.099923Z"
    },
    {
      "task_id": "TASK_LIBRARY_REPORT_SHORTCUTS_20261114",
      "tier": "high_risk",
      "subject": "2fdbceb3d48cf8ff34cac28682731f6bae759cca",
      "summary": "Common internal/customer report shortcuts and explicit Workbench-bound copy context",
      "disposition": "completed",
      "decision_ref": "User accepted and explicitly closed common internal/customer report shortcuts and Workbench copy target task. Preserve all local implementation commits, task worktree, isolated databases, test folders and validation evidence, including real Word/Excel UI edits and four explicitly unverified symlink cases. Only verified isolated demo processes on5211/8831 were stopped;17 test material files retain identical SHA256. NO push or publication; --publish-close deliberately omitted. No business-data mutation or cleanup.",
      "closed_at": "2026-11-14T13:34:48.468379Z"
    },
    {
      "task_id": "TASK_MATERIAL_LIBRARY_SETTINGS_20261115",
      "tier": "standard",
      "subject": "7576b56a0758b19e8e0c479dc421a5f3d585da36",
      "summary": "Centralize Receive save location in Settings and simplify daily material browsing",
      "disposition": "completed",
      "decision_ref": "User explicitly confirmed local Close of the current task only. Preserve implementation commits 7576b56a and a20176c1, task worktree and all validation evidence. Do not push or publish; --publish-close intentionally omitted. No cleanup, file moves or business data operations.",
      "closed_at": "2026-11-15T08:30:59.434998Z"
    },
    {
      "task_id": "TASK_MATERIAL_ARCHIVE_20261116",
      "tier": "high_risk",
      "subject": "ad8fafdc04bcf1ce189173a204d0cce47af2d77d",
      "summary": "Historical materials archive: one confirmation, safe independent copies, recoverable operations and folder discovery",
      "disposition": "completed",
      "decision_ref": "User explicitly confirmed local-only Close of the completed task. Preserve implementation commits 608bce14,818c8edf,48f3a84d,297a2b01,ad8fafdc, task worktree and all validation evidence including original full-Python failure records and bounded replay results. No push, publication or packaging. --publish-close intentionally omitted; no cleanup or business-file operations.",
      "closed_at": "2026-11-16T11:01:49.274121Z"
    },
    {
      "task_id": "TASK_PYTHON_TEST_HARNESS_20261116",
      "tier": "standard",
      "subject": "0e41331a1ee695b6aa33ffcf85c379b89005d824",
      "summary": "Fix Python test path-budget failures and obsolete native folder picker mocks",
      "disposition": "completed",
      "decision_ref": "User explicitly confirmed local-only Close of the completed Python test harness task. Preserve implementation commits 1d59806c and 0e41331a, the task worktree, all RED/GREEN evidence, original full-run failure records, final affected replay and integration verification. No push, publication or packaging. --publish-close intentionally omitted; no cleanup, file moves or business-file operations.",
      "closed_at": "2026-11-16T11:51:02.837983Z"
    },
    {
      "task_id": "TASK_LEGACY_IMPORT_CLEANUP_20261116",
      "tier": "high_risk",
      "subject": "7457d4c56b2dcbbea98d906009e556ce14777332",
      "summary": "Back up and clear exactly nine approved legacy import copies plus one database-only remainder; recycle copies locally",
      "disposition": "completed",
      "decision_ref": "User explicitly confirmed local-only Close on 2026-11-17. Preserve implementation7457d4c, integration417e2b7b, task checkout, complete database/tree backups and all audit/validation/recycle evidence at D:/ConnLabCleanupBackups/20261116-235317-legacy-import-cleanup. No backup/worktree/recycle cleanup, no database or directory mutation, no push, publication or packaging. --publish-close intentionally omitted.",
      "closed_at": "2026-11-16T22:39:10.776852Z"
    },
    {
      "task_id": "TASK_RENAMED_IMPORT_CLEANUP_20261117",
      "tier": "high_risk",
      "subject": "c46be8246ca79efc2a67d3340f597f40fe14bab3",
      "summary": "Back up and unlink the single approved DL-2026-11-013 [56cdd25d] legacy copy, then recycle it locally",
      "disposition": "completed",
      "decision_ref": "User explicitly confirmed Close on 2026-11-17. Existing local-only authority persists: preserve implementation c46be824, integration f958e071, task checkout, full DB/tree backups and audit/validation/recycle evidence at D:/ConnLabCleanupBackups/20261117-070750-renamed-import-cleanup, including original strict check differences and User-confirmed MaterialsDev/rev2 configuration. Preserve previous cleanup backups/evidence too. No business-data/config changes, no backup/worktree/bin cleanup, no push/publication/packaging. --publish-close intentionally omitted.",
      "closed_at": "2026-11-16T23:20:12.858153Z"
    },
    {
      "task_id": "TASK_DEV_STORAGE_ISOLATION_20261117",
      "tier": "high_risk",
      "subject": "23a951501cf2d107177cd544a34ff27e9e52e768",
      "summary": "Lazy environment output defaults, runtime/browser data-instance isolation and bounded local development material migration with old copies retained",
      "disposition": "completed",
      "decision_ref": "User explicitly closes this completed task locally only. Preserve implementation commits, old directory copies, database backups, audit and validation evidence. No push, publication, packaging, or checkout reclamation.",
      "closed_at": "2026-11-17T10:33:15.512206Z"
    },
    {
      "task_id": "TASK_FOLDER_SYNC_RENAME_20261117",
      "tier": "high_risk",
      "subject": "6ecb3dbd73f3c132c29778df1cdbd6337acce6c3",
      "summary": "Fix public working copy confirmation/execution and preserve verified project child-folder description renames in development and release environments.",
      "disposition": "completed",
      "decision_ref": "User accepted all three directory rules and explicitly requested local Close on 2026-11-18. Stop only isolated acceptance services; retain local commits, branch/worktree, test database/files and validation records. Do not push or publish; --publish-close intentionally omitted. Services 5217/8837 stopped with ownership evidence in tmp/folder-root-acceptance-20261118-071621/services-stopped.json. No real business data mutation.",
      "closed_at": "2026-11-17T23:29:27.592510Z"
    },
    {
      "task_id": "TASK_LIBRARY_STATUS_HINTS_20261118",
      "tier": "standard",
      "subject": "5484492210ecb56262dec8c1288981e27bff2c82",
      "summary": "Finish compact material-library browsing, selected-file and explicit Workbench copy-target guidance; correct boundary documentation.",
      "disposition": "completed",
      "decision_ref": "User accepted and requested completed local Close. Verified only isolated acceptance services on 5238/8858 stopped. Preserve local commits, worktree, acceptance database, sample files and validation evidence. No push or publication; --publish-close intentionally omitted. No real business data operation.",
      "closed_at": "2026-11-17T23:58:15.759335Z"
    },
    {
      "task_id": "TASK_STEP_REPORT_EVIDENCE_20261118",
      "tier": "standard",
      "subject": "432255a19702962481c94a92a090dabf6a66d7ef",
      "summary": "Show current report evidence for the exact selected Matrix step in Workbench and open its read-only source detail in Report Workspace.",
      "disposition": "completed",
      "decision_ref": "User accepted the step report evidence feature and requested local close only; retain local commits, no push.",
      "closed_at": "2026-11-18T09:52:03.957237Z"
    },
    {
      "task_id": "TASK_TOOLS_WRENCH_ICON_20261118",
      "tier": "micro",
      "subject": "9842e14eaeef29405420517e4bf322bd67ed2333",
      "summary": "Use an outlined wrench for the Tools icon.",
      "disposition": "completed",
      "decision_ref": "User requested Close. Local task closure under the established no-push workflow.",
      "closed_at": "2026-11-18T10:17:03.342458Z"
    }
  ],
  "tasks": {
    "TASK_ENCRYPTION_PICKER_20261118": {
      "slot": "main",
      "state": "ready_for_close",
      "worktree": "D:\\PythonProject\\connlab-worktrees\\encryption-picker-20261118",
      "branch": "codex/encryption-picker-20261118",
      "resources": [],
      "integrated_head": "a7886919695ea11c76659455530fc8cf15e04299",
      "task": {
        "task_id": "TASK_ENCRYPTION_PICKER_20261118",
        "summary": "Combine Tools encryption actions and use foreground Windows file/folder selection.",
        "tier": "standard",
        "route": "sol_build_review_qa",
        "scope": "One Tools entry plus explicit single-file/folder choices. Reuse the existing native Windows common dialog and encryption APIs; preserve current file protection and output policy. Local isolated validation.",
        "scope_paths": [
          "backend/infrastructure/files/windows_path_picker.py",
          "backend/infrastructure/files/windows_project_folder_dialog.py",
          "backend/infrastructure/files/windows_dialog_layout.py",
          "backend/api/routes_tools_folder_encryption.py",
          "frontend/src/features/tools/EncryptionTool.tsx",
          "frontend/src/features/tools/EncryptionTool.test.tsx",
          "frontend/src/pages/ToolsPage.test.tsx",
          "frontend/src/tools.css",
          "tests/unit/test_windows_project_folder_dialog.py",
          "tests/unit/test_windows_dialog_layout.py",
          "tests/integration/test_tools_local_folder_encryption_api.py",
          "docs/PROJECT_CONTEXT.md"
        ],
        "risk_reasons": [],
        "activation_head": "47c38fba032c74ba1777652b842a09b247092d8a",
        "started_at": "2026-11-18T10:32:54.583972Z",
        "updated_at": "2026-11-19T00:03:53.793577Z",
        "checkpoint": {
          "schema": "connlab.sol-task-checkpoint",
          "version": 1,
          "task_id": "TASK_ENCRYPTION_PICKER_20261118",
          "stage": "revision",
          "status": "running",
          "summary": "User clarified that the main encryption button should display the exact currently selected menu action, explicitly distinguishing one file from files inside a folder. Local copy revision.",
          "requires_user": false
        },
        "report": {
          "schema": "connlab.sol-task-report",
          "version": 1,
          "task_id": "TASK_ENCRYPTION_PICKER_20261118",
          "subject": "00b7ac2a8cca1211ea82dbf0085607b08bbe75ae",
          "summary": "The main button now uses the selected menu action label, explicitly distinguishing one file from the files in a folder. The existing behavior for opening selectors, cancelling and remembering the mode stays in force.",
          "scope_ok": true,
          "changed_paths": [
            "docs/PROJECT_CONTEXT.md",
            "frontend/src/features/tools/EncryptionTool.test.tsx",
            "frontend/src/features/tools/EncryptionTool.tsx",
            "frontend/src/pages/ToolsPage.test.tsx"
          ],
          "validation": [
            {
              "name": "Relevant frontend tests",
              "status": "passed",
              "summary": "25 passed: Tools page and encryption actions.",
              "evidence": "D:/PythonProject/connlab-worktrees/encryption-picker-20261118/tmp/encryption-action-copy/frontend.log"
            },
            {
              "name": "Frontend build",
              "status": "passed",
              "summary": "TypeScript and Vite succeeded after the tests.",
              "evidence": "D:/PythonProject/connlab-worktrees/encryption-picker-20261118/tmp/encryption-action-copy/build.log"
            },
            {
              "name": "Isolated Chrome",
              "status": "passed",
              "summary": "320 and 540px: full folder label fits, menu fits, refresh remembers the label, mock endpoints only.",
              "evidence": "D:/PythonProject/connlab-worktrees/encryption-picker-20261118/tmp/encryption-action-copy/browser-qa.log"
            }
          ],
          "roles": {
            "developer": {
              "status": "passed",
              "summary": "Shared the labels between the main button and the menu and updated the existing acceptance checks."
            },
            "reviewer": {
              "status": "passed",
              "summary": "Same-agent focused review of exact diff: copy only, existing selection and native API behavior preserved."
            },
            "qa": {
              "status": "passed",
              "summary": "25 existing behavior checks, build and browser at 320 and 540 pixels passed."
            }
          },
          "integration": {
            "status": "passed",
            "mode": "serial_local_merge",
            "subject": "00b7ac2a8cca1211ea82dbf0085607b08bbe75ae",
            "primary_before": "bb6f27288afcb93ca66b72e0a8c5701ff4e3dc64",
            "integrated_head": "a7886919695ea11c76659455530fc8cf15e04299",
            "recovered": false
          }
        }
      }
    },
    "TASK_RETIRE_LEGACY_ENTRY_20261119": {
      "slot": "micro",
      "state": "running",
      "worktree": "D:\\PythonProject\\connlab-worktrees\\retire-legacy-entry-20261119",
      "branch": "codex/retire-legacy-entry-20261119",
      "resources": [],
      "integrated_head": null,
      "task": {
        "task_id": "TASK_RETIRE_LEGACY_ENTRY_20261119",
        "summary": "Retire legacy folder linking and Continue Testing entry points",
        "tier": "micro",
        "route": "sol_direct",
        "scope": "Disable the two retired UI and HTTP workflows while preserving existing project and material access, batch receive, and portable snapshot restore.",
        "scope_paths": [
          "backend/api/project_library_schemas.py",
          "backend/api/routes_project_library.py",
          "backend/api/routes_tools_legacy_projects.py",
          "backend/application/project_library/service.py",
          "backend/infrastructure/project_library/portability.py",
          "docs/architecture/project_library.md",
          "frontend/src/App.test.tsx",
          "frontend/src/App.tsx",
          "frontend/src/api/legacyProjects.ts",
          "frontend/src/api/projectLibrary.ts",
          "frontend/src/features/legacy-projects/LegacyProjectPreview.test.tsx",
          "frontend/src/features/legacy-projects/LegacyProjectPreview.tsx",
          "frontend/src/features/project-library/ProjectLibraryMember.test.tsx",
          "frontend/src/features/project-library/ProjectLibraryMember.tsx",
          "tests/integration/test_legacy_project_registration_api.py",
          "tests/integration/test_project_library_portability.py",
          "tests/integration/test_tools_legacy_projects_api.py"
        ],
        "risk_reasons": [],
        "activation_head": "8064b324aeaa25ad45fc5165b6bcd47594b31c15",
        "started_at": "2026-11-19T11:34:58.415591Z",
        "updated_at": "2026-11-19T11:39:09.230558Z",
        "checkpoint": null,
        "report": null
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
