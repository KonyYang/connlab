# 讨论：项目测试执行链下一阶段需求

> 本文档整理自用户与 AI 的多轮讨论，用于向编程大模型传达完整需求和上下文。
> 日期：2026-06-09（更新于同日，基于 task_board.md 和实际代码核查）

---

## 一、当前项目实际状态（基于代码验证，非文档推测）

### 截至 TASK_304，task_board 显示：

```
TASK_285-TASK_292 fee-evaluation series complete
TASK_293 complete (Excel preview UI)
TASK_294 complete (direct file download)
TASK_295 complete (step-based preview)
TASK_296 complete (step order, no step column)
TASK_297 complete (step column + discount label)
TASK_298 complete (fee rule refresh/validation)
TASK_299 complete (editable pricing preview)
TASK_300 complete (edited values → fee form export)
TASK_301 complete (pricing draft persistence)
TASK_302 complete (reference update workflow)
TASK_303 complete (project registry summary UI)
TASK_304 complete (lab performing tests confirmation)
```

### 已完成的后端基础设施

| 模块 | 现状 | 关键文件 |
|------|:---:|------|
| Matrix Editor + Confirm Matrix | ✅ | 完整前后端 |
| Test Record .docx 生成（后端） | ✅ | `confirmed_matrix_test_record_document_generation_service.py` |
| Test Record header metadata fill | ✅ | TASK_281：自动填 LTR、Product Description、Applicable Specification |
| Fee Evaluation 独立页面 | ✅ | `/projects/:projectId/fee-evaluation`（TASK_292） |
| Fee Evaluation 预览表格（step-expanded） | ✅ | 含 Group/Step/Description/Unit Price/Units/Discount 等列（TASK_293-297） |
| Fee Evaluation 本地可编辑 | ✅ | Man-hour / Unit Price / Unit Type / Units / Base Fee / Discount / Notes 可编辑（TASK_299）|
| Fee Evaluation 编辑值导出 | ✅ | Fee Form 下载携带编辑值，写入 B/D/E/F/G/H 列，I 列公式，Notes→Excel 批注（TASK_300）|
| Fee Evaluation 编辑值持久化 | ✅ | 绑定 project + Confirmed Matrix id/revision + rule version，含 Save changes（TASK_301）|
| Fee Rule Seed 库 | ✅ | 12 条规则，`active_fee_rule_seed.json`，含 ALLOWED_UNIT_LABELS 验证（TASK_298）|
| Fee Rule 更新工作流基础 | ✅ | candidate 生成 / diff / activation validation（TASK_302）|
| Fee Export 超时保护 | ✅ | 生产级 subprocess + 90s timeout + 503 结构化响应（TASK_291）|
| Folder Service（后端） | ✅ | 预览/生成/冲突检测 API 完整 |
| Evidence Placement Service | ✅ | 后端完整：preview/place，分类 EMAIL/PHOTO/SPECIFICATION/LTR_EVIDENCE 等 |
| LTR 邮件附件解析 | ✅ | intake 阶段已提取到 `ImportedMailAttachment` |
| Application Form Section 2 字段 | ✅ | `received_date`、`estimated_completion_date`、`lab` 字段存在 |
| Matrix 计划字段 | ✅ | `sample_received_date`、`estimated_completion_date` |
| Project Registry Summary | ✅ | `/projects` 使用后端 registry DTO（TASK_303）|
| Lab Performing Tests 字段 | ✅ | Dongguan / Valley Green 选项，LTR 提交前写入 Section 2（TASK_304）|

### 已写好组件但未接入 Workbench 布局

| 组件 | 文件 | 行数 | 说明 |
|------|------|:---:|------|
| **ProjectFolderCreationPanel** | `frontend/src/features/project-workbench/` | 269 | 完整的预览/生成/冲突检测 UI，**未在 WorkbenchLayout 中引用** |
| **TestRecordDraftGenerationButton** | `frontend/src/features/project-workbench/` | 独立组件 | 完整的 "Generate Test Record Draft" 按钮 + 下载逻辑，**未在 WorkbenchLayout 中引用** |

### 尚未实现

| 模块 | 说明 |
|------|------|
| Fee Evaluation Confirm 版本 | 没有 "Confirm Fee" 机制（Fee 只有 read-only draft + export + persistence） |
| Application Form Section 2 从 Matrix 自动回写 | `sample_received_date` → `received_date` 等未自动联动 |
| Matrix Editor draft Test Record 按钮 | 组件中存在但 MatrixEditorWorkspace 中没有此按钮 |
| 一键出包编排器 | 不存在 |
| 客户反馈表生成 | 模板 `E-4243_D Customer Feedback Form.xlsx` 存在，无生成代码 |
| Clarizen 标记 | 只在讨论文档中提及，无代码 |
| 测试执行（StepInstance/TestResult） | 未实施 |
| 图片上传 | 不存在 |

---

## 二、用户期望的完整操作链

从当前已注册 LTR 的项目出发，到项目进入实验室测试执行。

### 阶段 A：版本确认补齐

```
Matrix Editor  ── Confirm Matrix ──→  Confirmed Matrix Authority  ✅ 已有

Fee Evaluation ── Confirm Fee  ──→  Confirmed Fee Version         ❌ 缺失
```

Fee Evaluation 页面底部需要像 Matrix Editor 一样添加 "Confirm Fee" 按钮，
确认后锁定一个费用版本。当前 Fee 有 preview + editable + persistence + export，但缺版本锁定。

### 阶段 B：临时草稿导出按钮

两类页面互补：

| 页面 | 新增按钮 | 产物 | 说明 |
|------|---------|------|------|
| Matrix Editor | Generate Test Record (draft) | 临时 Word | 预览用，文件名标注 draft，**不含 DL 编号** |
| Fee Evaluation | －（已有导出） | 导出 .xls | TASK_294 直接下载已就位 |

关键要求：
- 临时文件供操作员预览效果，文件名不能包含 DL 编号（因为此时尚未注册版本）
- TestRecordDraftGenerationButton 组件已存在（含后端 API），只需在 MatrixEditorWorkspace 加按钮
- 正式导出才含 DL 编号

### 阶段 C：Matrix 确认后的联动效应

Matrix 版本确认（Confirm Matrix）成功后，Workbench/后端自动触发：

1. **更新申请表 Section 2**：
   - `Date Lab Received Samples` ← Matrix 的 `sample_received_date`
   - `Estimated Completion Date` ← Matrix 的 `estimated_completion_date`
   - 两个值已存在于 Matrix 确认后的数据中，需要回写

2. **复制模板生成客户反馈表**：
   - 源模板：`D:/Source/Template/E-4243_D Customer Feedback Form.xlsx`
   - 填充项目字段（DL 编号、产品名称等）

3. **激活 Fee Evaluation 确认功能**：
   - Matrix 未确认时，Fee Evaluation 只能预览+编辑
   - Matrix 确认后，"Confirm Fee" 按钮变为可用

### 阶段 D：一键生成项目文件夹

针对已有 LTR 编号、Matrix 已确认的项目：

```
操作员点击一次 → 自动产出:
  ├── Test Record .docx          （含 DL 编号，已确认版本）
  ├── Fee Form .xls              （含 DL 编号，Matrix basic fill + 持久化编辑值）
  ├── 客户反馈表 .xlsx            （从模板复制并填充字段）
  └── 移动已有资料到文件夹:
        ├── 申请邮件 .msg
        ├── 提取的附件
        ├── Application Form
        └── 其他 intake 阶段解析的资料
```

架构原则：
- 编排器（上层）调用下层独立服务
- 各服务之间保持解耦，互不感知
- Evidence Placement Service 后端已完整，可被编排器直接调用
- FolderService 后端已完整（preview + generate + conflict guard）

### 阶段 E：人工审批链

```
本地完成 → 上传项目文件夹到公共盘 → 打印纸质 → 提交上级审批
→ 批准后 → Clarizen 系统填写（需单独说明）
→ ConnLab 本地标记 "已注册 Clarizen"（建议 boolean 字段）
```

### 阶段 F：实验室测试执行

进入实际测试阶段：
- 为具体测试步骤制作测试表格
- 上传测试结果或图片
- 随时更新报告

需要新建 StepInstance 和 TestResult 模型。

---

## 三、架构评估（基于实际代码验证）

### 可复用现有模式

| 新需求 | 现有基础 | 缺口 |
|--------|---------|------|
| Confirm Fee | 照抄 Confirm Matrix 模式 | 新建 `ConfirmedFeeVersion` domain |
| Matrix Editor draft Test Record 按钮 | TestRecordDraftGenerationButton 组件已存在，后端 API 已有 | 在 MatrixEditorWorkspace 加按钮 + 文件名标注 draft |
| 更新申请表 Section 2 | `received_date`/`estimated_completion_date` 字段已存在 | sync service |
| 一键出包 | FolderService + FeeExportService + TestRecordService 已有 | 编排器（上层） |
| 客户反馈表 | `E-4243_D Customer Feedback Form.xlsx` 存在 | copy + fill service |
| 移动已解析资料 | EvidencePlacementService 后端完整（含 API） | 编排器调用即可 |
| Clarizen 标记 | － | Project 模型加 bool 字段 |
| Folder UI 接线 | ProjectFolderCreationPanel (269行) 已写好 | 接入 WorkbenchLayout |
| 图片上传 | － | 新建 |
| 测试执行 | － | 新建 StepInstance/TestResult domain + API + UI |

### 架构不支持的：无

---

## 四、策略决策：先跑通主线，后优化自动填充

### 决策

> **当前优先级：跑通"创建项目文件夹"的主线流程，含必要的版本确认步骤。**
> 延后的是 Matrix/Fee 的**自动匹配/填充默认值**（AI parser/matcher 优化），
> 版本确认（Confirm Fee + Matrix 联动）属于业务权威发布顺序，不延后。

### 两条线，不同策略

**主线（不延后）：**
```
导入 Matrix → 手动编辑 → Confirm Matrix → 
Fee 编辑/持久化 → Confirm Fee → 生成项目文件夹
```
这是"数据权威发布"链：版本确认（Confirm）不能跳过，否则下游消费的是未锁定的数据。

**自动填充线（延后）：**
```
规格书自动提取 Method/Condition/Requirement → 预填 Matrix 单元格
Rule seed 自动匹配 Unit Price/Unit Type → 预填 Fee 单元格
```
这是"减少手动输入"的优化，不影响数据权威链的正确性。

### 理由

```
主线需要：
  Confirm Fee 机制 + Matrix 联动 + UI 接线 + 编排器

主线不需要：
  Matrix Editor autofill（TASK_282-283 已有基础，但尚未应用到 Editor 默认值）
  Fee auto-matching（rule seed 已有，但未自动填到 Fee 预览表格）
```

- Confirm Fee 是草案 → 权威版本的必经之路，符合实际业务。
- Matrix 确认联动（Section 2 回写、激活 Fee Confirm）是版本间数据一致性的保障。
- 自动填充是"操作员少打几个字"的体验优化，不阻塞任何人。

### 聚焦主线的任务

| # | 任务 | 本质 | 工作量 |
|---|------|------|:---:|
| ① | `ProjectFolderCreationPanel` 接入 WorkbenchLayout | 接线 | 小 |
| ② | `TestRecordDraftGenerationButton` 接入 WorkbenchLayout | 接线 | 小 |
| ③ | Confirm Fee 机制（仿 Matrix Confirm） | 新增 domain + API | 中 |
| ④ | Matrix 确认联动（Section 2 回写 + 客户反馈表 + 激活 Fee Confirm） | 新增 sync service | 中 |
| ⑤ | 一键生成项目文件夹编排器 | 调已有 API | 中 |

### 延后到主线跑通后的功能

- Matrix Editor 自动从规格书提取 Method/Condition/Requirement 默认值
- Fee Evaluation 自动从 rule seed 匹配 Unit Price/Unit Type
- Clarizen 标记
- 测试执行（StepInstance/TestResult）

---

## 五、推荐执行顺序

```
① Folder UI 接线（组件已写好，零风险，解锁 Folder 创建入口）
    ↓
② TestRecordDraftGenerationButton 接线（组件和 API 已有，解锁 draft Test Record）
    ↓
③ Confirm Fee 机制（新增 domain，仿 Matrix Confirm 版本锁定逻辑）
    ↓
④ Matrix 确认联动（Section 2 回写 + 客户反馈表 + 激活 Fee Confirm）
    ↓
⑤ 一键生成项目文件夹（编排器，依赖 ①②③④）
    ↓
⑥ 客户反馈表生成（copy 模板 + 占位符替换，可并入⑤或独立）
    ↓
———— 主线跑通后 ————
    ↓
⑦ Matrix/Fee 自动填充默认值优化
    ↓
⑧ Clarizen 标记 + 测试执行
```

理由：
- ①② 接线即可，不依赖任何新机制
- ③④ 建立版本权威链：Confirm Fee 锁定版本 → Matrix 联动保障一致性
- ⑤ 依赖 ③④ 就位后才能拿到已确认的 Fee 版本和联动数据
- ⑦⑧ 是纯优化/新功能，等主线稳定后做

---

## 六、TASK_298-TASK_302 系列状态

| 任务 | 状态 | 说明 |
|------|:---:|------|
| TASK_298 (rule seed refresh/validation) | ✅ complete | 纯后端 |
| TASK_299 (editable pricing preview) | ✅ complete | 第一个 UI 改动 |
| TASK_300 (edited values → export) | ✅ complete | 编辑值 → Excel |
| TASK_301 (pricing draft persistence) | ✅ complete | Save/Load 编辑值 |
| TASK_302 (reference update workflow) | ✅ complete | candidate/diff/activation 基础 |

**全系列已完成。** Fee Evaluation 的 edit → export → persist → rule update 闭环已就位。

---

## 七、关键技术边界

1. **解耦原则**：服务之间不互相调用，编排器在上层组装
2. **不自动触发**：不修改 FolderService 让它自动调用 Fee Export
3. **临时文件命名**：draft 文件不含 DL 编号，与正式导出区分
4. **版本锁定**：Fee Evaluation 需要独立的 Confirm 机制，仿 Matrix Confirm
5. **模板不覆盖**：复制模板到项目文件夹，不对原始模板做修改
6. **COM 防护**：Excel COM 操作已有 timeout 保护（TASK_291）
7. **Evidence Placement**：后端已完整，分类为 EMAIL/PHOTO/SPECIFICATION/LTR_EVIDENCE/CORRECTION/SUPPORTING_ATTACHMENT/APPLICATION_FORM
