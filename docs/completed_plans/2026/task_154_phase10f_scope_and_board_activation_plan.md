# TASK_154 可执行方案（Phase 10F Scope And Board Activation）

## 0. 执行前声明（Anti-Skip）

- 当前 Phase：`Phase 10F - Real public-drive LTR workbook operational closure` proposed
- 当前 Active Task：`TASK_154_PHASE10F_SCOPE_AND_BOARD_ACTIVATION`
- 允许原因：`docs/task_board.md` 已将 `TASK_154` 标记为下一推荐任务，并明确要求在进入 `TASK_155` 前先完成本阶段激活。

---

## 1. 任务目标（Step 1）

1. 目标  
   正式激活 `Phase 10F`，把主线从“扩展性 Excel 能力”切回“真实公共盘 LTR 申请业务闭环”。

2. 输入数据  
   - 当前 `docs/task_board.md`
   - 新增的 `TASK_154` 到 `TASK_157` 任务定义
   - 已完成的 `Phase 10E` 结果与限制

3. 输出数据  
   - 更新后的 `docs/task_board.md`
   - `TASK_154` 状态完成记录
   - `TASK_155` 成为下一待批准实现任务

4. 涉及模块  
   - `docs/task_board.md`
   - 视需要轻微同步 `tasks/TASK_154_PHASE10F_SCOPE_AND_BOARD_ACTIVATION.md`

5. 不允许做什么  
   - 不改任何运行时代码
   - 不实现真实 workbook 兼容修复
   - 不推进 `TASK_155`、`TASK_156`、`TASK_157` 的实现
   - 不新增服务器化、报表、标准/设备 Excel 扩展逻辑

---

## 2. 设计方案（Step 2）

### 2.1 数据结构设计

本任务无运行时数据结构变更。

只涉及文档层状态调整：

- `Current Phase`
- `Current Active Task`
- `Next recommended action`
- `TASK_154` completed note
- `TASK_155` next implementation recommendation

### 2.2 文件列表

- 必改：
  - `docs/task_board.md`

- 仅在发现描述不一致时才改：
  - `tasks/TASK_154_PHASE10F_SCOPE_AND_BOARD_ACTIVATION.md`

### 2.3 API / 函数签名

无。

### 2.4 依赖关系

```text
Phase 10E completed
  -> TASK_154 board activation
      -> TASK_155 real workbook compatibility baseline
          -> TASK_156 real operator smoke / failure handling
              -> TASK_157 workbook / SQLite reconciliation
```

### 2.5 具体改动方向

1. 在 `docs/task_board.md` 中把：
   - `TASK_154` 标记为完成
   - `Current Active Task` 改为 `none; awaiting user approval for TASK_155`
   - `Current Phase` 改为 `Phase 10F` 已激活

2. 在 `Next recommended action` 区域明确：
   - 当前主线是“真实公共盘 LTR workbook 业务闭环”
   - 下一实现任务是 `TASK_155_REAL_PUBLIC_DRIVE_LTR_WORKBOOK_COMPATIBILITY_BASELINE`
   - 禁止跳到 `TASK_156` / `TASK_157`

3. 记录 `TASK_154` 完成说明：
   - 本阶段为何回到真实业务主线
   - 为何暂停标准/设备 Excel 扩展优先级

---

## 3. 风险与处理

1. 风险：看板文本与实际业务优先级再次偏移  
   - 处理：在 `TASK_154` 完成说明中明确“真实 LTR 申请是当前主线”。

2. 风险：后续任务继续沿扩展 Excel 方向发散  
   - 处理：在看板中直接写明 `TASK_155` 是唯一下一实现任务。

---

## 4. 验证计划（Step 5/7）

本任务是文档激活任务，不涉及运行时代码或 pytest。

验证方式：

1. 检查 `docs/task_board.md` 是否满足：
   - `Phase 10F` 已激活
   - `TASK_154` completed
   - `TASK_155` 为下一待批准任务

2. 人工确认看板主线表述：
   - 主线已回到真实公共盘 `LTR.XLS` / workbook 业务操作
   - 标准/设备 Excel 不再是当前优先实现项

---

## 5. 自检清单（对应 TASK_REVIEW_CHECKLIST）

- 架构：无代码层改动，无跨层风险。  
- 范围：仅做 board activation，不提前做 `TASK_155+`。  
- 设计：任务顺序明确，主线重新聚焦真实业务。  
- 质量：只改文档，不引入额外功能。  

---

## 6. 实施后停止点

- 完成 `TASK_154` 后停止。
- 不进入 `TASK_155`，等待你显式批准下一任务。

