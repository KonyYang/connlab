# TASK 156 执行方案（Real LTR Application Smoke And Failure Handling）

## 1. 当前阶段与任务许可

- 当前阶段：`Phase 10F - Real public-drive LTR workbook operational closure`
- 当前活动任务：`TASK_156_REAL_LTR_APPLICATION_SMOKE_AND_FAILURE_HANDLING`
- 许可依据：`docs/task_board.md` 已将 TASK_156 作为下一实施任务，且你已明确“同意”。

## 2. 目标（本任务要解决什么）

围绕真实业务主线“申请 LTR 编号并写入公共盘 LTR 工作簿”，完成一次可复现的烟雾验证，并补齐关键失败场景的可操作提示，确保：

1. 主流程可用（确认 -> 写入 -> 返回结果）
2. 失败可诊断（路径/密码/结构/锁冲突等）
3. 权威源仍是工作簿，SQLite 只做次级记录

## 3. 实施范围

1. 手工烟雾路径验证（以当前 Settings 配置资源为准）
2. 后端失败语义与消息补强（仅限 LTR 申请相关路径）
3. 必要测试补充（单测/集成测试）
4. 文档与任务看板回填

不包含：

- 服务器化改造
- 标准件/设备台账读写扩展
- 与 LTR 主线无关的 UI 重构

## 4. 代码改动计划（文件级）

优先检查并按需改动以下模块：

1. LTR 申请编排与 authority 边界
   - `backend/application/ltr_authority.py`
   - `backend/application/ltr_excel_authority_adapter.py`
   - `backend/api/routes_new_project_completion.py`
2. 工作簿提交服务与事务网关
   - `backend/application/ltr_workbook_write_commit_service.py`
   - `backend/infrastructure/office/ltr_workbook_transaction_gateway.py`
3. 错误映射与可读消息
   - `backend/api/routes_ltr_workbook_write_commit.py`
   - 相关 error 类型定义文件（若已有统一错误模块则沿用）
4. 测试
   - `tests/unit/test_ltr_workbook_write_commit_service.py`
   - `tests/integration/test_ltr_workbook_write_commit_api.py`
   - `tests/integration/test_new_project_completion_api.py`

说明：只在 TASK_156 范围内最小改动，不做跨任务重构。

## 5. 场景化验证清单（执行口径）

1. 成功路径：
   - 资源已激活，路径有效，写开关开启，密码正确
   - 返回包含：LTR 号、sheet、row、backup 信息
2. 路径无效/资源未激活：
   - 返回业务可读错误（不是泛化 500）
3. 密码不正确或不可修改：
   - 返回明确“写权限/密码”指向
4. 锁冲突/超时：
   - 返回“稍后重试/检查占用者”的指引
5. 结构不满足（缺年表等）：
   - 返回结构性 blocker，提示处理路径

## 6. 风险与控制

1. 风险：真实公共盘文件被并发占用导致偶发失败
   - 控制：保持短事务，严格 lock timeout，失败消息明确重试策略
2. 风险：错误类型在 route 层被吞并成 500
   - 控制：补全应用异常 -> API 状态码映射测试
3. 风险：成功写入后本地记录状态不一致
   - 控制：维持 authority-first，提交成功后再写本地记录，并在返回中携带关键写入元数据

## 7. 验收与测试计划

计划执行：

1. `py -m pytest tests\unit\test_ltr_workbook_write_commit_service.py -q`
2. `py -m pytest tests\integration\test_ltr_workbook_write_commit_api.py tests\integration\test_new_project_completion_api.py -q`
3. 如有必要，补一条针对 lock/password/path 的回归用例并执行

手工验证：

1. 调用现有 New Project 完成路径（或对应 commit API）进行一次真实 LTR 申请
2. 核对返回值、工作簿写入结果与本地记录一致性

## 8. 交付物

1. 代码改动（仅 TASK_156 范围）
2. 测试用例与测试结果
3. `docs/task_board.md` 状态更新（TASK_156 -> done，并标注下一任务建议）

