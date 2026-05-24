# TASK_161 执行方案（历史 Project/LTR 清理 Dry-run）

## 1. 当前阶段与任务许可

- 当前阶段：`Phase 10F - Real public-drive LTR workbook operational closure`
- 当前任务：`TASK_161_HISTORICAL_PROJECT_LTR_CLEANUP_DRY_RUN`
- 任务性质：只读审计报告，不执行删除、不回收编号、不修改 workbook。

## 2. 目标

先把现有混乱数据列清楚，避免直接清理造成二次损害。

本任务只回答：

- 哪些 Project 没有有效 LTR？
- 哪些 LTR 编号格式不合规？
- 哪些 Project 有多个 registered LTR？
- 哪些 LTR 指向不存在的 Project？

## 3. 设计

新增一个 application service：

- `backend/application/project_ltr_cleanup_audit_service.py`

输入：

- Project repository
- LTR repository

输出：

- `ProjectLtrCleanupAuditReport`
  - `generated_at`
  - `total_projects`
  - `total_ltr_records`
  - `issues`

每条 issue 包含：

- `issue_type`
- `severity`
- `project_id`
- `project_name`
- `project_status`
- `ltr_id`
- `ltr_number`
- `message`
- `suggested_action`

新增 API：

- `GET /api/cleanup/project-ltr/dry-run`

## 4. 分类规则

1. `project_without_registered_ltr`
   - Project 没有任何 `REGISTERED` LTR。
   - 用于识别历史残留 Project。

2. `invalid_registered_ltr_number`
   - LTR 状态是 `REGISTERED`，但 `parse_ltr_number()` 失败。
   - 例如 `DL-2026-04-075810`、`DL-2026-04-080341`。

3. `project_multiple_registered_ltrs`
   - 同一个 Project 有超过一个 `REGISTERED` LTR。

4. `orphan_ltr_record`
   - LTR 的 `project_id` 找不到 Project。

## 5. 文件级改动

- 新增：
  - `backend/application/project_ltr_cleanup_audit_service.py`
  - `backend/api/routes_cleanup.py`
  - `tests/unit/test_project_ltr_cleanup_audit_service.py`
  - `tests/integration/test_cleanup_api.py`

- 更新：
  - `backend/api/dependencies.py`
  - `backend/api/main.py`
  - `docs/task_board.md`
  - `tasks/TASK_161_HISTORICAL_PROJECT_LTR_CLEANUP_DRY_RUN.md`

## 6. 风险控制

- 只读：service 不调用 repository update/create/delete。
- 不碰 Excel：不读写 `LTR.XLS`。
- 不做自动判断删除，只提供 `suggested_action` 给后续人工确认任务使用。

## 7. 验证计划

- `py -m pytest tests/unit/test_project_ltr_cleanup_audit_service.py -q`
- `py -m pytest tests/integration/test_cleanup_api.py -q`

