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
    "task_id": "TASK_QA_TEMP_RETENTION_SAFE_20261110",
    "tier": "high_risk",
    "subject": "9c169b8a8863dac4e5446a0217cd587b565122a0",
    "summary": "Manage isolated pytest artifacts on D with completed-run-only seven-day retention",
    "disposition": "completed",
    "decision_ref": "User confirmed final Close after local integration. Preserve all local commits and acceptance evidence; existing no-push/no-publication restriction remains in force. The User explicitly approved same-context self-review, automated tests and isolated acceptance instead of independent checks. Close locally only; --publish-close intentionally omitted. No real legacy cleanup or business-file operations.",
    "closed_at": "2026-11-09T23:59:43.167424Z"
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
    }
  ],
  "tasks": {
    "TASK_PROJECT_FILE_GENERATION_PHASE2_20261110": {
      "slot": "main",
      "state": "running",
      "worktree": "C:\\Users\\White\\.codex\\worktrees\\import-folder-picker\\connlab",
      "branch": "codex/project-file-generation-phase2-20261110",
      "resources": [
        "phase2-isolated-filesystem-and-database"
      ],
      "integrated_head": null,
      "task": {
        "task_id": "TASK_PROJECT_FILE_GENERATION_PHASE2_20261110",
        "summary": "Independent Generate files with per-file prerequisites, protected replacement, recovery and isolated validation",
        "tier": "high_risk",
        "route": "full_chain",
        "scope": "Implement approved eight-kind second-batch Generate files on trusted existing workspaces; preserve phase-one and legacy behavior, public sync rules and manual files; isolated validation and local integration only. No push, publication, real business data or automatic public folder rename.",
        "scope_paths": [
          "backend/api/dependencies.py",
          "backend/api/main.py",
          "backend/api/project_customer_report_runner.py",
          "backend/api/project_file_generation_composition.py",
          "backend/api/project_file_generation_runner.py",
          "backend/api/project_folder_generation_composition.py",
          "backend/api/project_folder_write_guard.py",
          "backend/api/project_registry_access_guard.py",
          "backend/api/routes_project_file_generation.py",
          "backend/application/project_application_form_write_back_service.py",
          "backend/application/project_file_generation_guard.py",
          "backend/application/project_file_generation_service.py",
          "backend/application/project_file_generation_sources.py",
          "backend/application/project_file_generation_staging.py",
          "backend/application/project_file_generation_types.py",
          "backend/application/project_registry_management_service.py",
          "backend/infrastructure/files/project_file_generation_journal.py",
          "backend/infrastructure/files/recoverable_project_file_publisher.py",
          "backend/infrastructure/project_library/assets.py",
          "backend/infrastructure/project_library/files.py",
          "backend/infrastructure/project_library/portability.py",
          "docs/PROJECT_CONTEXT.md",
          "docs/architecture/project_file_generation.md",
          "frontend/src/api/client.ts",
          "frontend/src/features/project-workbench/ProjectFilesDialog.css",
          "frontend/src/features/project-workbench/ProjectFilesDialog.test.tsx",
          "frontend/src/features/project-workbench/ProjectFilesDialog.tsx",
          "frontend/src/features/project-workbench/ProjectFolderTaskList.tsx",
          "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
          "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
          "frontend/src/features/project-workbench/useProjectFiles.ts",
          "tests/integration/test_project_file_generation_api.py",
          "tests/unit/test_project_file_generation_protocol.py",
          "tests/unit/test_project_file_generation_service.py",
          "tests/unit/test_project_file_generation_sources.py",
          "tests/unit/test_project_file_generation_staging.py"
        ],
        "risk_reasons": [
          "Recoverable filesystem mutation and explicit replacement of authoritative external outputs",
          "Cross-writer durable mutual exclusion, idempotence and output registration"
        ],
        "activation_head": "12179ef09021ff12182b5b51596c213b195e0a46",
        "started_at": "2026-11-10T05:07:04.315007Z",
        "updated_at": "2026-11-10T05:47:28.565976Z",
        "checkpoint": {
          "schema": "connlab.sol-task-checkpoint",
          "version": 1,
          "task_id": "TASK_PROJECT_FILE_GENERATION_PHASE2_20261110",
          "stage": "validation",
          "status": "running",
          "requires_user": false,
          "summary": "Clean candidate2fa147a225f06ada72e821af8cf83aa59925d31b contains all8 generators, source/UI integration and recoverable protection; scope corrected to exact36paths. Independent static Reviewer PASS Standards0/Spec0. Final independent QA started69backend-file risk matrix, affectedfrontend/build,4realPopen.kill SQLite/XLSX windows and isolatedactualdialogbrowser. Codex Security immutable diff scan e5d17a77-2587-4993-8945-a5462c405bef running after preflightREADY. No real business/publicdata, push/publication or primary product integration. Await QA/security then independent localIntegrator; stop ready_for_close awaiting User."
        },
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
