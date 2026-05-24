# TASK_162 执行方案（无 LTR Project 清理执行）

## 1. 当前阶段与任务许可

- 当前阶段：`Phase 10F - Real public-drive LTR workbook operational closure`
- 当前任务：`TASK_162_NO_LTR_PROJECT_CLEANUP_EXECUTION`
- 前置任务：`TASK_161_HISTORICAL_PROJECT_LTR_CLEANUP_DRY_RUN` 已完成。

## 2. 目标

把历史遗留的“没有 registered LTR 的 Project”从正常 Projects 管理视图中清出去，但不物理删除。

执行结果：

- Project 状态改为 `cancelled`
- 写入清理审计记录
- 后续 Project Registry 可以继续按现有规则隐藏/区分 cancelled 项目（若 UI 仍显示 cancelled，另开 UI 过滤任务）

## 3. 执行原则

1. 必须显式传入 project IDs，不允许“一键清全部”。
2. 必须填写 reason。
3. 执行时重新检查，不信任旧 dry-run：
   - Project 必须存在
   - Project 不能已经有 `REGISTERED` LTR
4. 不删除任何行，不删除文件，不修改 workbook。
5. 已经 `cancelled` 的项目可视为 idempotent，不重复改状态，但仍返回 skipped/unchanged。

## 4. 数据库设计

新增表：

`project_cleanup_audit_records`

字段：

- `cleanup_id`
- `project_id`
- `previous_status`
- `new_status`
- `reason`
- `operator`
- `created_at`
- `details_json`

新增 domain/application DTO：

- `ProjectCleanupAuditRecord`
- `ExecuteNoLtrProjectCleanupCommand`
- `NoLtrProjectCleanupResult`

## 5. API 设计

新增：

`POST /api/cleanup/project-ltr/no-ltr-projects/execute`

请求：

```json
{
  "project_ids": ["..."],
  "reason": "cleanup historical no-LTR residues",
  "operator": "White"
}
```

响应：

```json
{
  "cancelled_count": 25,
  "skipped_count": 0,
  "rejected": [],
  "changed": []
}
```

## 6. 文件级改动

- `backend/domain/enums.py`
  - 复用 `ProjectStatus.CANCELLED`，不新增状态。
- `backend/infrastructure/storage/models.py`
  - 新增 audit ORM model。
- `backend/infrastructure/storage/database.py`
  - 新增 lightweight migration/create-table helper。
- `backend/infrastructure/storage/repositories/project_cleanup.py`
  - 新增 audit repository。
- `backend/application/no_ltr_project_cleanup_service.py`
  - 新增执行服务。
- `backend/api/routes_cleanup.py`
  - 增加 execute endpoint。
- `backend/api/dependencies.py`
  - 注入 service。
- 测试：
  - `tests/unit/test_no_ltr_project_cleanup_service.py`
  - `tests/integration/test_cleanup_api.py`

## 7. 验证计划

- `py -m pytest tests/unit/test_no_ltr_project_cleanup_service.py -q`
- `py -m pytest tests/integration/test_cleanup_api.py -q`

## 8. 风险控制

- 本任务只处理 no-LTR Project，不处理错误 LTR 编号。
- 审计表先最小化，不引入全局事件系统。
- 若 Project Registry 仍展示 cancelled 项目，下一任务单独做 UI 默认过滤。

