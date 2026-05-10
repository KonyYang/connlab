# TASK_160 执行方案（New Project LTR 原子完成闸门）

## 1. 当前阶段与任务许可

- 当前阶段：`Phase 10F - Real public-drive LTR workbook operational closure`
- 当前任务：`TASK_160_NEW_PROJECT_LTR_ATOMIC_COMPLETION_GATE`
- 触发原因：用户明确要求先修正 New Project 申请 LTR 主流程，避免 workbook 写入失败后仍创建 Project。

## 2. 问题判断

当前前端流程是：

1. `confirmIntakeCase(activeCase.case_id)` 创建/确认 Project
2. `commitLtrWorkbookWrite(projectId, ...)` 写 `LTR.XLS`
3. `completeNewProject(caseId, ...)` 再做最终完成

这会导致第 1 步成功、第 2 步失败时，Project 已进入 Project Registry，但没有有效 LTR。

正确流程应该是：

1. 前端只调用 `completeNewProject(caseId, ...)`
2. 后端在同一个请求/事务上下文里协调 intake confirm、workbook authority commit、本地 LTR 记录与 Project 状态
3. 任一关键步骤失败时返回错误，前端留在 New Project，不跳转

## 3. 实施范围

### 前端

- 修改 `frontend/src/features/new-project/useNewProjectCompletion.ts`
  - 移除 `confirmIntakeCase`
  - 移除 `commitLtrWorkbookWrite`
  - 只调用 `completeNewProject`
  - 使用后端返回的 `ltr_number/workbook_sheet_name/workbook_row_number/workbook_backup_path` 写入结果快照
  - 失败时只显示错误，不调用 `onCompleted`

- 修改 `frontend/src/api/client.ts`
  - 保持 `CompleteNewProject` workbook 元数据字段
  - 不删除通用 API 函数，因为 Workbench 或其他路径仍可能使用

### 后端

- 检查 `backend/application/new_project_completion_service.py`
  - 当前已经通过 `LtrAuthorityPort` 做后端编排
  - 如测试发现事务行为不足，再补最小修正

### 测试

- 更新或新增：
  - `tests/integration/test_new_project_completion_api.py`
  - `tests/unit/test_frontend_shell_files.py`

## 4. 验收标准

1. 前端 New Project completion hook 中不再出现：
   - `confirmIntakeCase(activeCase.case_id)`
   - `commitLtrWorkbookWrite(projectId`
2. 前端只调用：
   - `completeNewProject(activeCase.case_id`
3. workbook 失败时：
   - API 返回错误
   - 本地 LTR 不创建
   - 前端不跳转 Project Registry
4. 成功时：
   - Project 进入 Registry
   - 结果 banner 可显示 LTR number、sheet、row、backup path

## 5. 风险与控制

- 风险：现有静态测试仍期望前端直接调用 workbook commit。
  - 控制：同步测试断言到新的业务规则。
- 风险：后端 confirm 与 workbook commit 的事务边界仍可能留下 Project。
  - 控制：用集成测试覆盖 workbook commit failure 后无本地 LTR，并检查 Project 状态/可见性语义；如发现仍持久化 Project，再在 service 层调整顺序或 rollback 行为。
- 风险：直接删除通用 API 函数影响其他页面。
  - 控制：本任务只移除 New Project hook 的直接调用，不删除 API client 函数。

## 6. 验证计划

- `py -m pytest tests/integration/test_new_project_completion_api.py -q`
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "new_project or project"`
- `npm run build` from `frontend`

