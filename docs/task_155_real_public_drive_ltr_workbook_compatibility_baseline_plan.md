# TASK_155 可执行方案（Real Public-Drive LTR Workbook Compatibility Baseline）

## 0. 执行前声明（Anti-Skip）

- 当前 Phase：`Phase 10F - Real public-drive LTR workbook operational closure`
- 当前 Active Task：`TASK_155_REAL_PUBLIC_DRIVE_LTR_WORKBOOK_COMPATIBILITY_BASELINE`
- 允许原因：`docs/task_board.md` 已将 `TASK_154` 标记完成，并将 `TASK_155` 设为下一待批准实现任务。

---

## 1. 任务目标（Step 1）

1. 目标  
   在真实业务环境下确认 ConnLab 对公共盘 `LTR.XLS`（或当前生产 workbook）的可兼容性，找出阻断真实 `Apply LTR Number` 的结构/格式差异，并在 workbook authority 路径内做最小修补。

2. 输入数据  
   - Settings 中配置的真实 `ltr_workbook` 路径（公共盘）
   - 当前 workbook authority 代码路径（`LtrWorkbookTransactionGateway` / `ExcelComLTRWorkbookGateway` / `LtrWorkbookWriteCommitService`）
   - 一组最小真实业务样例（至少包含目标年份 sheet）

3. 输出数据  
   - 兼容性结论：当前可用 / 不可用
   - 若不可用：明确阻断点与代码修补项
   - 兼容后验证记录：能否完成最小写入前提检查（不要求在本任务做真实业务写入冒烟）

4. 涉及模块  
   - `backend/infrastructure/office/*`（主要是 workbook 打开、sheet 探测、行定位）
   - `backend/application/ltr_workbook_write_commit_service.py`
   - `backend/api/routes_ltr_workbook.py`（仅在错误映射必要时）
   - 对应 unit/integration tests

5. 不允许做什么  
   - 不做 server authority
   - 不扩展标准/设备 Excel 功能
   - 不改 UI 流程
   - 不把业务逻辑移出既有 authority 边界

---

## 2. 设计方案（Step 2）

### 2.1 数据结构设计

本任务以兼容修补为主，默认不新增持久化模型。

如需新增，仅限“诊断型返回字段/错误类型”，用于表达真实 workbook 结构差异（例如缺失年份 sheet、header 不匹配、受保护写入失败）。

### 2.2 文件级改动（预期）

1. 只读兼容探测（必要时增强）
   - `backend/infrastructure/office/excel_com_ltr_workbook_gateway.py`
   - `backend/infrastructure/office/ltr_workbook_transaction_gateway.py`
   - 目标：容忍真实 workbook 的可接受结构差异，拒绝不可控差异并给出业务可读错误。

2. 提交编排容错（必要时增强）
   - `backend/application/ltr_workbook_write_commit_service.py`
   - 目标：对真实结构差异的错误分类更明确，避免“看似成功但无效”。

3. 测试
   - `tests/unit/test_excel_com_ltr_workbook_gateway.py`
   - `tests/unit/test_ltr_workbook_write_commit_service.py`
   - `tests/unit/test_ltr_workbook_transaction_gateway.py`
   - 如需要：新增 `tests/integration/test_ltr_real_workbook_compatibility_baseline.py`（仅本地可控样本，不写公共盘）

### 2.3 API/函数签名

默认不变。除非真实 workbook 差异要求暴露更精确的失败原因，才在现有错误消息/错误类型上做最小增强。

### 2.4 依赖关系

```text
TASK_155 compatibility baseline
  -> confirms workbook structure assumptions
    -> feeds TASK_156 real operator smoke
      -> feeds TASK_157 workbook/SQLite reconciliation
```

---

## 3. 实施步骤

1. 读取当前 `ltr_workbook` 配置与真实路径存在性（只读）。
2. 用现有 Office 边界做结构探测（sheet、关键列、受保护打开模式）。
3. 记录真实差异并分类：
   - 可容忍（代码可兼容）
   - 阻断（需修补）
4. 在 workbook authority 路径内做最小修补（如果有阻断）。
5. 补测试覆盖修补点。
6. 输出兼容基线结论并更新 `docs/task_board.md`。

---

## 4. 关键风险与处理

1. 风险：真实公共盘不可直接在自动测试中写入  
   - 处理：本任务以结构兼容基线为主，公共盘写入冒烟放到 `TASK_156`。

2. 风险：真实文件为历史 `.xls` 且结构不规则  
   - 处理：优先通过现有 Excel COM 写入边界兼容；如不可控，明确阻断并给迁移建议（不在本任务做迁移工具）。

3. 风险：路径/权限/锁定由运维环境决定  
   - 处理：输出可操作诊断信息（路径、权限、锁等待、只读状态）而不是泛化报错。

---

## 5. 验证计划（Step 5/7）

优先验证命令：

```powershell
py -m pytest tests\unit\test_excel_com_ltr_workbook_gateway.py tests\unit\test_ltr_workbook_transaction_gateway.py tests\unit\test_ltr_workbook_write_commit_service.py -q
py -m pytest tests\integration\test_ltr_workbook_write_commit_api.py tests\integration\test_new_project_completion_api.py -q
```

人工验证（本任务只做兼容基线，不执行正式编号申请）：

1. 在 Settings 确认 `ltr_workbook` 指向真实公共盘文件。
2. 运行兼容探测/预检路径，确认是否存在结构阻断。
3. 若无阻断，记录“可进入 TASK_156 冒烟”。
4. 若有阻断，记录“阻断项 + 修补后复测结果”。

---

## 6. 自检（Step 4）

- 是否违反 AGENTS.md：否（只处理 workbook authority 主线）。
- 是否实现未请求功能：否。
- 是否跨层：否（仍在 application/infrastructure 边界内）。
- 是否吞异常：否，要求保持可操作错误信息。
- 是否硬编码路径：否，使用 Settings 资源配置路径。
- 是否有未完成 TODO：实现阶段不得遗留 TODO。

---

## 7. 停止点（Step 8）

- 完成 `TASK_155` 后停止，不进入 `TASK_156`。
- 等待你确认后再推进真实 `Apply LTR Number` 冒烟任务。

