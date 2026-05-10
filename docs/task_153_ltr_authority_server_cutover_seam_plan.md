# TASK_153 可执行方案（LTR Authority Server Cutover Seam）

## 0. 执行前声明（Anti-Skip）

- 当前 Phase：`Phase 10E - External resource settings and LTR workbook authority`
- 当前 Active Task：`TASK_153_LTR_AUTHORITY_SERVER_CUTOVER_SEAM`
- 允许原因：`docs/task_board.md` 已将 `TASK_152` 标记完成，并把 `TASK_153` 作为下一推荐任务（待批准后实施）。

---

## 1. 任务目标（Step 1）

1. 目标  
   固化并文档化 LTR“权威源”切换边界：当前权威源是 Excel 适配器，未来可切换到服务端权威源，而不改 UI / 路由编排语义。

2. 输入数据  
   - 现有 LTR 提交流程代码（New Project + Workbench）
   - 当前 workbook 提交服务与依赖注入实现
   - 现有测试基线

3. 输出数据  
   - 一套显式 authority interface（应用层协议/端口）
   - Excel authority adapter（对现有 workbook commit 的薄封装）
   - 静态约束测试：阻止 UI/API route 直接触达 Excel/COM gateway 细节
   - cutover 迁移说明文档

4. 涉及模块  
   - `backend/application`（新增 authority 端口和 adapter）
   - `backend/api/dependencies.py`（注入从具体 workbook 服务改为 authority 端口）
   - `backend/application/new_project_completion_service.py`（依赖 authority 抽象）
   - `tests/unit`（新增边界/静态约束测试）
   - `docs/`（cutover 迁移说明）

5. 不允许做什么  
   - 不实现 server authority 本体  
   - 不引入认证/LAN/报表  
   - 不改动现有业务路径和返回契约（除非必须修复边界冲突）

---

## 2. 设计方案（Step 2）

### 2.1 边界设计

新增应用层 authority 抽象：

- `LtrAuthorityPort`（Protocol）
  - `commit_project(project_id: str, command: CommitLtrAuthorityCommand) -> LtrAuthorityCommitResult`

新增 authority 命令与结果 DTO（尽量复用现有字段）：

- `CommitLtrAuthorityCommand`
  - 保留 New Project 所需字段（plan_date、number_input、operator_confirmed、setup confirmation 字段等）
- `LtrAuthorityCommitResult`
  - `ltr`
  - `workbook_path/sheet/row/backup`（当前 Excel 模式仍可返回，未来 server 模式可为空或改为 server 元信息）

Excel 适配器：

- `ExcelWorkbookLtrAuthorityAdapter`
  - 内部调用现有 `LtrWorkbookWriteCommitService`
  - 将 authority 命令映射为 `CommitLtrWorkbookWriteCommand`
  - 将 workbook 结果映射回 `LtrAuthorityCommitResult`

### 2.2 代码改动清单（计划）

1. 新增 `backend/application/ltr_authority.py`
   - authority protocol + command/result dataclass

2. 新增 `backend/application/ltr_excel_authority_adapter.py`
   - 适配 `LtrWorkbookWriteCommitService`

3. 更新 `backend/application/new_project_completion_service.py`
   - 构造函数依赖从 `LtrWorkbookWriteCommitService` 改为 `LtrAuthorityPort`
   - `_commit_or_load_ltr` 调 authority，不再引用 workbook 具体类型

4. 更新 `backend/api/dependencies.py`
   - 新增 `get_ltr_authority_service`（当前返回 Excel adapter）
   - `get_new_project_completion_service` 注入 authority 服务，而非 workbook commit service

5. 文档
   - 新增 `docs/ltr_authority_cutover_seam.md`
   - 记录：
     - 当前权威源（Excel）
     - 本地 SQLite 是结构化副本，不是官方号源
     - 将来 server cutover 仅替换 adapter 注入点

6. 测试
   - 新增/更新单测：
     - `tests/unit/test_new_project_completion_service.py`（用 fake authority 验证编排）
     - `tests/unit/test_ltr_authority_boundary.py`（静态检查 route/UI 不直接依赖 workbook gateway/COM）
   - 复用并最小调整现有 `tests/integration/test_new_project_completion_api.py`

### 2.3 静态边界防护（TASK_153 重点）

新增静态约束测试规则：

1. `backend/api/routes_*.py` 不允许 import：
   - `ExcelComLTRWorkbookGateway`
   - `LtrWorkbookTransactionGateway`
   - `OfficeLifecycleManager`

2. `frontend/src/**` 不允许出现 workbook/COM 低层术语或字段映射细节（继续只使用业务 API）。

3. `new_project_completion_service.py` 不允许 import workbook gateway 类，只允许 authority 抽象。

---

## 3. 风险与处理

1. 风险：重构抽象层时影响现有 New Project API 测试  
   - 处理：保持 `CompleteNewProjectResponse` 契约不变；优先小步改依赖注入。

2. 风险：静态检查过严导致误报  
   - 处理：限定扫描范围（route/UI/特定 service），避免误伤 infrastructure 层。

3. 风险：命名不清造成未来 cutover 仍耦合 Excel  
   - 处理：统一使用 `authority` 语义命名，禁止在高层接口使用 `workbook` 命名。

---

## 4. 验证计划（Step 5/7）

实施后运行：

```powershell
py -m pytest tests\integration\test_new_project_completion_api.py -q
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "new_project or ltr or authority"
py -m pytest tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py -q
```

若新增 `test_ltr_authority_boundary.py`，一并纳入执行。

---

## 5. 自检清单（对应 TASK_REVIEW_CHECKLIST）

- 架构：UI/API 不触达 Office 细节，符合。  
- 范围：只做 seam/边界，不做 server 实现，符合。  
- 设计：authority 抽象可替换，依赖方向清晰。  
- 质量：类型标注 + docstring + 关键静态防护测试。  

---

## 6. 实施后停止点

- 完成 `TASK_153` 后更新 `docs/task_board.md`，并停止等待你下一步指令，不自动推进新 phase。

