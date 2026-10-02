# 报告自动化：结果数据自动填充 + 照片自动插入 —— 设计方案

- 状态：**设计提案，尚未实施**。本文不是执行授权或任务看板；本次仅核对、更新并提交文档，不实施结果导入或照片写入。
- 版本：**v5**（2026-10-02，当前代码核对基线 `93442a6c`；含 v4.1 事实校正）。
  - v1（范围只含 IR/DWV 数据 + 照片）**未落盘**；
  - v2 并入 docm 宏核查结论后，数据侧由 1 类扩为 **4 类**；
  - v3 并入**完整真实样本**（`DL-2024-12-050 EK200`）实测证据，**关闭 D-1 与 D-7**，图片绑定单位修正为「**图组**」；
  - **v4 细化单据 B（§5）**：新增版式事实基线（§5.0）、三层绑定对象（§5.1）、**编号派生规则**（§5.2）、
    **三类图位的插入算法**（§5.3-A/B/C）、尺寸与分页预算（§5.4）、幂等标记方案（§5.5）、审计口径（§5.7）；
    新发现：所检查模板第 3 章自带 `Figure 1:` 图位，未补图生成样本保留裸图注及悬空引用（§5.0）。
  - v4.1 保留 v4 图位与三层对象设计，区分空白记录表与实测结果导入，校正客户报告清洗、数据集扩展面、版本身份、分页及验收断言。
  - **v5（本轮）**：并入 IR/DWV 记录表的**已交付链路事实**（`TASK_362` / `TASK_DOC_IR_DWV_CONTEXT_SYNC` / `TASK_IR_DWV_DOWNLOAD_NAME_AUTHORITY` 均已于 `93442a6c` 前关闭），
    新增 **§4.6 测量源解析**（三条命名 / 输出台账 / 归档覆盖风险 / 统计值自算）；把已接受的 **D-15 / D-16 / D-17** 写实；
    §8 增设 A2 的独立前置工单 **A0**。
- 必读参考：
  - `docs/plans/REPORT_AUTOMATION_REAL_SAMPLE_EVIDENCE.md` —— **完整真实项目样本**（申请 → 记录 xlsx → 内部报告 → 客户报告）的逐项实测。
  - `docs/plans/REPORT_AUTOMATION_VBA_REFERENCE_MAP.md` —— docm 宏（实验室当前人工工作流）的逐项行为映射。
  - `docs/report_generation_architecture.md` —— 报告边界参考；REPORT-001 的延迟阶段清单含历史条目，当前能力以代码与下表为准。
  - `docs/project_customer_report_progress.md` —— 客户报告后台作业进度。
- 版式实测件（只读探针产物）：`tmp/ek200_photo_layout.txt`（样本）、`tmp/e3707h_layout.txt`（模板）、
  `tmp/connlab_draft_layout.txt`（connlab 现产物）、`tmp/cap_tpl.xml.txt` / `tmp/cap_draft.xml.txt`（图注段落原始 XML）。

---

## 0. 一句话结论

**只做内部报告的写入点**（`E-3707_H`），分两条彼此独立的单据推进：

- **单据 A（结果数据自动填充）** —— 复用已交付 LLCR 的成熟机制，扩成数据驱动的通用原语，把 **IR/DWV、CR、MF/UMF、Contact Retention** 四类结果填进第 6 章结果表（+ 各自的附录）。**先做。**
- **单据 B（照片自动插入）** —— 全新能力，需要新建绑定模型、定义落位与尺寸、重做分页基线。**后做。**

**v4 前置发现**：`E-3707_H` 模板第 3 章**已自带**一个图注占位段落 `Figure 1:`，而 connlab 全链路从不处理它
（内部报告网关未专门处理 Figure）→ 所检查未补图产物保留**裸露图注**及引用 `illustrated in Figure 1.`。
这给出了单据 B 的第三类图位候选，但只证明所检查模板/产物的占位现象；不能外推所有模板版本、人工编辑成品。
实际插图仍需新增受控标记、绑定与审计，不能仅靠复制模板结构。

客户报告（下文称 Customer Report，避免与 Contact Resistance 的 CR 缩写混淆）不增加第二套结果写入逻辑：
它复制内部报告正文，再执行受控清洗与审计。客户可见的结果和图组应保留，附录、附录引用句及内部披露会删除，不能承诺所有正文原样继承。

### 当前已实现与未实现（2026-10-02）

| 能力 | 当前状态 | 代码锚点 |
|---|---|---|
| LLCR / CR 空白记录工作簿 | 已实现；不是 CR 实测结果导入 | `backend/infrastructure/office/llcr_cr_specialized_record_workbook_gateway.py` |
| IR/DWV 共享点位、空白记录工作簿 | 已实现；人工输入测量对，确认 Matrix 后成为权威；同组轮次横排，表间两列空隔，每 sheet 最多三轮；样品增至 6 不减少轮次容量 | `backend/application/matrix_editor_ir_dwv_record_projection.py`、`backend/infrastructure/office/ir_dwv_record_workbook_layout.py` |
| IR/DWV 保存与命名 | 屏幕 Matrix 与确认权威一致且正式目录可用时保存到 `Test results`，同名先确认归档（不覆盖已有历史项地移动旧表，见 §4.6-3）；否则下载。确认版 `{LTR} IR&DWV Record.xlsx`，草稿加 ` draft` | `backend/application/confirmed_matrix_llcr_cr_record_generation_service.py`、`backend/application/matrix_editor_ir_dwv_record_generation_service.py` |
| 项目输出台账 | 已登记 `IR_DWV_RECORD_FORM` 输出（路径 / sha256 / Matrix 版本签名），可作为测量源发现入口；**但它是登记，不读盘校验** | `backend/application/project_output_record_service.py`、`backend/domain/enums.py:193` |
| LLCR 实测导入、确认、Result/Comment、Appendix A | 已实现 | `backend/application/llcr_result_dataset_service.py`、`backend/infrastructure/office/test_report_document_gateway.py` |
| Section 7 Equipment List 更新、Customer Report 后台进度 | 已实现 | `backend/application/current_report_update_service.py`、`backend/application/project_customer_report_job_service.py` |
| IR/DWV、CR、MF/UMF、Retention 实测导入及报告同步 | 未实现；单据 A | `ResultDatasetRevision` 当前只允许 `llcr` |
| 报告照片选择、图组绑定与自动插入 | 未实现；单据 B | 图片归置与 Customer Report 既有图形保留不是绑定/插入能力 |

IR/DWV 生成保留模板 LOGO、默认 Instrument/Gage ID 与单位，电压、时间及要求取 Matrix；测量值和无确认来源的实测环境/签核留空。
规格书点位自动提取不在本设计范围，沿用 Matrix 人工输入与确认。

---

## 1. 目标与非目标

### 目标
1. 把已确认的测量结果自动写进内部报告第 6 章结果表的 `Result` / `Comment` 列。
2. 把与 Group/Step 绑定的项目照片（含夹具图、失效形貌图等）自动插进内部报告。
3. 全过程可预览、可追溯、幂等、fail-closed。

### 非目标（本设计明确不做）
- 不改 `D:\Source\Template` 下的模板文件本体（`E-3707_H` / `E-4515_F`）。
- 不改客户报告网关的投影规则。
- 不动 LLCR 结果同步、Appendix A、Equipment List 三个**已交付**适配器的现有行为与其测试。
- 不引入 AI 评审、多人权限、LAN 部署等未来范围。
- 不回退 connlab 已有的安全实践去向 VBA 对齐（见 §9）。

---

## 2. 事实基线（已核实的代码锚点）

### 2.1 内部报告写入机制（`backend/infrastructure/office/test_report_document_gateway.py`，python-docx）

| 事实 | 位置 |
|---|---|
| 结果表头契约 `Step/Test/Requirement/Step Description/Result/Comment` | `_RESULT_HEADERS:45-52` |
| 结果表定位锚点 = 表格**前一个段落** `Group N Test Results`（正则 `Group\s+(.+?)\s+Test Results`） | `_result_tables_by_group:755-775` |
| 组名归一化（去 `Group ` 前缀 + casefold） | `_report_group_key:778-779` |
| **占位符契约**：结果列在生成时写 `_default_result(requirement)`，把 `≤/≥` 后的数字段压成 `_` | `_fill_result_block:731-740`、`_default_result:1407-1415` |
| 填值（唯一匹配 → 换 `Result`/`Comment`；命中数 ≠ 1 即 `raise` fail-closed） | `synchronize_llcr_results:166-241` |
| LLCR 结果文本口径 `Initial ≤{max:.3f}mΩ` / `∆R ≤{max:.3f}mΩ` | `_llcr_report_result:782-784` |
| 同步后审计（逐条唯一匹配 + Appendix 现状 + 正文格式） | `_audit_llcr_sync:787-810` |
| 附录区域定位 / 整段删除后重建（幂等、可覆盖） | `_appendix_a_region:901-924`、`_replace_appendix_a:927-984` |
| Equipment List 同步（REPORT-003B，已交付） | `synchronize_equipment_list:243-301` |
| 章节标题全集 | `_REQUIRED_HEADINGS:66-76` |
| 正文格式统一 / 审计（Arial 11pt） | `_apply_report_body_format:1323`、`_audit_report_body_format:1365` |
| 输出 = 临时文件 → 审计 → `os.replace` 原子替换（**不原地覆盖**） | `:187`、`:238-240` |

### 2.2 客户报告边界（决定性）

```python
# backend/infrastructure/office/customer_report_document_gateway.py:518
core = source.Range(int(purpose.Start), int(equipment.Start))   # 只取 1. PURPOSE → 7. EQUIPMENTS
```

- CR 只复制**正文第 1–6 章**；`8. REVISION RECORD` 另段单独复制（`:522-530`）。
- CR 审计在客户报告里发现 `EQUIPMENTS` 或任何 `Appendix A-Z:` 标题时**直接 raise**（`:1094-1097`）。
- 结论：
  - ✅ 第 1–6 章内的客户可见结果和图组保留；❌ `given in Appendix` 等内部披露即使在正文中也会清除。
  - ❌ **放在附录里的内容**（Appendix A/B/D/E）→ 不进 CR（这是既有设计，LLCR 亦然）。
  - → 「两种照片落位」必须**都在正文内**（详见 §5.2，决策 D-3）。

### 2.3 结果数据集（已通用于除类型校验外的全部环节）

| 事实 | 位置 |
|---|---|
| `ResultDatasetRevision` 领域模型 | `backend/domain/result_dataset_models.py:112-138` |
| 领域入口强制 `dataset_type == "llcr"`；payload、stage 与确认判定也都是 LLCR 专用 | `ResultDatasetRevision`、`LlcrResultEntry` |
| DB 列 `dataset_type String(64)`，payload 存 `payload_json Text` | `backend/infrastructure/storage/models_result_dataset.py:23`、`:39` |
| 仓储 `next_dataset_revision(project_id, dataset_type)` **已参数化** | `backend/infrastructure/storage/repositories/result_dataset.py:58-65` |
| 反序列化 `_dataset_domain` 硬编码构造 `LlcrDatasetPayload` / `LlcrResultEntry` | `result_dataset.py:123-202` |
| 报告草稿可关联 `result_dataset_id` | `models_result_dataset.py:62-64`、`ReportDraftRevision.result_dataset_id` |
| 已交付 LLCR 端到端路由 | `routes_report_workspace.py`：`llcr/inspect:465`、`llcr/confirm:489`、`llcr-drafts:559` |

→ 类型约束、payload、反序列化是三个底层起点，**不是完整改动清单**。导入/确认服务、来源留存、Matrix 版本校验、DTO/API/依赖装配、
前端预览与报告更新入口和测试也需扩展。空白表的 `record_type="ir_dwv"` 不能代替实测数据集的 `dataset_type="ir_dwv"`。

### 2.4 docm 宏参考实现（人工工作流的可执行事实标准）

完整映射见 `REPORT_AUTOMATION_VBA_REFERENCE_MAP.md`。三条直接影响设计：

1. **四步骨架**（每个"更新"宏同形）：
   ```
   ① 读 Test results\{项目编号} {PREFIX} Record.xlsx → 建「组别_步骤_参数 → 值」字典
   ② 写结果表：锚点 = 前一段落 "Group N Test Results"，按行匹配，只换 ≤/≥ 后面的数字
   ③ 在 "7. EQUIPMENTS" 前插正文引用句 "… are given in Appendix X."（Arial 11 下划线，带查重）
   ④ 把 xlsx 统计表贴成 Appendix X（锚点 *** End of Report *** 前）
   ```
2. VBA 与 `_default_result` 都生成数字占位符；但 ConnLab 的 `synchronize_llcr_results` 按确认数据集构造并替换整个 Result/Comment，**不要求原 Result 存在 `_`**。占位符是初始化呈现，不是实测导入接口。
3. 所保留的 19 个 VBA 模块没有 IR/DWV 更新入口，电阻族枚举只有 `CR=0, LLCR=1`。
   旧 TestFlowManager 的 TODO 是历史盘点；当前 ConnLab 已实现 IR/DWV 空白表与 LLCR 报告同步，不能据此断言全机无实现。

### 2.5 照片来源（已存在且已受治理）

| 事实 | 位置 |
|---|---|
| 项目文件夹有 `Photos` 目录 | `backend/modules/folder/evidence_placement_rules.py:172-173`（`evidence_root / "Photos"`） |
| 按扩展名自动归置图片：bmp/gif/heic/jpeg/jpg/png/tif/tiff/webp | `evidence_placement_rules.py:62-72`、`:154-155` |
| `FileAsset` 已登记项目文件（含 `sha256`），**但无 Group/Step 字段** | `backend/domain/models.py:286-298` |
| ⚠️ `.heic` 在扩展名白名单里，但 python-docx / PIL 默认**读不了 HEIC** → 潜在坑 | `evidence_placement_rules.py:65` |
| 分页 golden 基线：24 页内部报告 → 21 页客户报告 | `docs/report_generation_architecture.md:198-207` |

### 2.6 模板既有结构：第 3 章自带一个图位（v4 新核实）

| 事实 | 位置 / 证据 |
|---|---|
| `E-3707_H` 模板第 3 章有图注占位段落 **`Figure 1:`**（`NormalLatinArial`，居中，行距 1.5，run 带 `<w:b/>` + `<w:u w:val="single"/>`，**无 `w:sz`**） | 模板 body child #14（原始 XML：`tmp/cap_tpl.xml.txt`） |
| 同章叙述句 `… given in the table below and illustrated in Figure 1.` | 模板（`tmp/e3707h_template_dump.txt:43`） |
| 该图注上方**没有**图片段 → 是"空图位"，等人工贴图 | 同上 |
| **connlab 后端从不处理它**：`Figure` 在 `backend/**/*.py` **零命中**；`_fill_narrative:566-570` 只做占位符替换 | Grep + 代码 |
| 所检查模板生成的未补图产物保留裸图注及悬空引用；不外推所有模板/人工成品 | `tmp/connlab_draft_layout.txt`（保留解析件，不是本次新生成） |

**版式几何与图注格式的完整实测表见 §5.0**（页面 8.5×11in、正文内容宽 7.50in / 高 9.00in、结果表宽 7.556in 等）。

---

## 3. 原设计保留的业务决定（不是本次实施授权）

以下是原设计记录的业务方向，本次保留而不重新裁决；待选项仍列在 §7。文档核对和提交不授权实现全部方案。

| 编号 | 决策 |
|---|---|
| U-1 | 写入落点：**内部报告优先**（只做 `E-3707_H` 一个写入点，CR 自动继承） |
| U-2 | 照片来源：**自动扫 `Photos` 目录 + 人工确认绑定**（可追溯、可纠错） |
| U-3 | 绑定方式：**由本设计给出模型**（用户要求设计方案） |
| U-4 | 照片落位：**两种都做** —— 就地（第 6 章各 Group 结果表后）+ 独立汇总子章节 |
| U-5 | 数据来源路径：**三步** = xlsx 导入 → 预览确认 → 落 `ir_dwv` 数据集 → 填报告 |
| U-6 | 排序：**数据先行（单据 A），图片后做（单据 B）** |

---

## 4. 单据 A：结果数据自动填充

### 4.1 为什么不新增 `synchronize_ir_dwv_results` 之类的克隆

架构文档 `:184-185` 明确要求：*「未来报告工作应建在语义报告模型上，而不是往 Word 适配器加结果专用逻辑」*。若每类结果克隆一个 `synchronize_xxx_results`，适配器会立刻长出 4 份近乎相同的分支。

**建议（未实施）**：先保持现有 LLCR 行为与测试；新类型采用语义更新命令和类型专用呈现器。
确实消除重复且回归验证通过时，才将 LLCR 改为共享原语的薄包装；这涉及实现改动，不能同时承诺“一行不改”。

```python
# 拟新增（示意，非最终签名）
@dataclass(frozen=True, slots=True)
class ResultCellUpdate:
    group_label: str
    step_token: str          # 对应结果表第 1 列
    match_kind: str          # "llcr" | "ir" | "dwv" | "cr" | "mf" | "umf" | "retention"
    requirement: str         # 第 3 列精确匹配串
    result_text: str         # 写入第 5 列
    comment_text: str        # 写入第 6 列

def synchronize_result_cells(self, *, source_path, output_path, updates) -> Path:
    ...
```

- **匹配口径映射**（数据驱动，不写 if/else 分支结果类型）：
  - `match_kind` → 第 2 列测试项判定函数（现有 `is_llcr_test_item`，新增 `electrical_test_kind` 已能识别 IR/DWV）。
  - 沿用现有三元精确匹配（`step_token` + 测试项 + `requirement`）+ **命中数 ≠ 1 即 fail-closed**（照抄 `:210-214`）。
- **result_text / comment_text 由应用层的「结果呈现器」产出**，适配器只机械落字。每类结果一个呈现器（见 4.3），都产出 `≤/≥ + 值 + 单位` 或 `Pass` / `No detriment` 形态。

### 4.2 数据集扩展（底层起点，不是仅三处改动）

| 位置 | 改动 |
|---|---|
| `result_dataset_models.py:131-132` | `dataset_type` 由 `== "llcr"` 改为受控集合 `{"llcr", "ir_dwv", "cr", "mechanical_force", "contact_retention"}` |
| `result_dataset_models.py:103-108` | `payload` 类型由 `LlcrDatasetPayload` 改为联合类型（或抽象 `ResultDatasetPayload` 协议） |
| `repositories/result_dataset.py:123-202` | `_dataset_domain` 按 `dataset_type` 分派到对应 payload 反序列化器 |

只增加类型和 JSON payload 时，现有列可能可复用；**不能预先保证无需迁移**。多数据集关联、图组绑定、历史兼容及索引需求须在实际任务中核对。
`ReportDraftRevision.result_dataset_id` 目前只关联一个数据集，新方案必须明确多类型结果的版本来源，不能只放开类型而遗漏报告追溯。

### 4.3 四类结果源（按实施顺序）—— 历史样本呈现参照

下表的文件名、sheet 名及极值来自历史研究，不代表所有当前产物的导入布局或已经实现的算法；IR/DWV 拟议支持范围以 D-15 与 §4.6 为准。

| 序 | 结果源 | 真实数据源（xlsx） | 报告落位 | **取值口径** | **Result 文本口径** |
|---|---|---|---|---|---|
| 1 | **IR**（Insulation Resistance） | `… IR DWV Results_SECURED.xlsx`，sheet = `Group N Initial` / `Group N Final` | 第 6 章结果表 | **Min**（要求是 `≥`） | `≥{min}GΩ`；源若为文本下限（如 `>290`）则照写 `>{值}GΩ` |
| 1 | **DWV**（Dielectric Withstanding Voltage） | 同 1（同 sheet 的 DWV 块） | 第 6 章结果表 | **Max**（漏电流，要求 ≤5mA） | `No evidence of arc-over or insulation breakdown,`↵`leakage current ≤{max}nA` |
| 2 | **CR**（Contact Resistance） | `{DL} CR Record.xlsx` | 第 6 章 + Appendix | **Max** | 同 LLCR 族（`≤{max}mΩ`） |
| 3 | **MF / UMF**（Mating/Un-mating Force） | `… Mating_Unmating and Terminal Retention Record_SECURED.xlsx` 的 `MF_UMF` 表 | 第 6 章 + Appendix | **MF 取 Max / UMF 取 Min** | 多行：`Mating Force`↵`≤{max}N;`↵`Un-mating Force`↵`≥{min}N` |
| 4 | **Contact Retention** | 同一 xlsx 的 `Terminal Retention` 表（**合表**） | 第 6 章 + Appendix | **Min**（要求是 `≥`） | `≥{min}N` |
| — | LLCR（已交付） | `{DL} LLCR Record_SECURED.xlsx` 的 `Summary` 表 | 第 6 章 + Appendix A | **Max** | `≤{max}mΩ` |

> **D-1 已关闭（v3）**。真实样本实测：IR 结果是 `≥170GΩ` / `>290GΩ`（取 5 个样品 IR 值的 **Min**）；
> DWV 结果是 `No evidence of arc-over or insulation breakdown,` + 换行 + `leakage current ≤1nA`（取漏电流 **Max**）。
>
> **关键推论：IR/DWV 不能复用 `_` 占位符替换。** Requirement 列写的是 `≥1,000MΩ (1GΩ)` /
> `…leakage current >5mA(5x106nA)`，Result 列写的是 `≥170GΩ` / `…leakage current ≤1nA` —— 单位与句式都被重写，
> 且 `>` 不在 `_default_result:1411-1415` 的正则（只处理 `≤`/`≥`）覆盖范围内。
> → IR/DWV 必须有**独立的结果呈现器**，从记录表数据 + 单位（记录表第 21 行 `GΩ` / `nA`）构造文本。
> VBA 的 LLCR/CR 数字占位替换可作呈现参考；当前 ConnLab LLCR 仍按确认数据集构造整格结果，不把 `_` 作为接口。
>
> **数据源命名有真实漂移**：VBA 期望的 `{DL} Mechanical Force Summary.xlsx` 在本样本并不存在，MF/UMF 实际躺在
> `Mating_Unmating and Terminal Retention Record_SECURED.xlsx` 里，且与 Terminal Retention **合表**。
> → 导入器必须"**发现 + 人工选择**"，不能硬编码单一文件名/表名。

上述文本与极值是历史样本验证的呈现口径，不是所有项目的完整判定算法。单位读取后要归一化；`>290` 是下限而非精确数值，
混合比较符、缺测、不完整覆盖需要诊断和人工确认。DWV 漏电流最大值不能证明“无电弧/无击穿”，必须有独立记录或人工确认，不能自动宣称通过。
**表形状有两种，本单只支持自己的那一种（D-15 已定）**：connlab 当前产物是“Group = sheet、轮次 = 横向块”——
`ROUNDS_PER_SHEET = 3`（`ir_dwv_record_workbook_layout.py:13`）、同组最多 3 轮横向排布、表间留 2 列 gutter
（`TABLE_GUTTER_COLUMN_COUNT = 2`，`block_origins:112-124`）、续页 sheet 名 `Group N (2)`、轮次标签写在行 10
`Item/Process: {group} IR&DWV-{step.label}`（`ir_dwv_record_workbook_gateway.py:581`）；
历史人工件（样本 `DL-2024-12-050 EK200`）是“Group × Stage = sheet”（`Group 2 Initial` / `Group 2 Final`），**两者不同形**。
→ 导入器**只支持 connlab 形状**；识别到历史形状即 **fail-closed** 并提示“属历史项目回填，另立一单”，
**不在此单内做双布局兼容**，也不固定读取第 21/23 行等历史行号。

> 数据源的**文件名与发现方式**另有专门一节（§4.6）—— 三种名字、台账入口、归档覆盖风险都在那里定稿。

### 4.4 正文引用句（新增受控区域）—— D-7 已关闭

- VBA 与真实样本都在 `7. EQUIPMENTS` 前插一句：`Statistical summaries of LLCR measurements are given in Appendix A.`（Arial / 非粗体 / 11pt / 下划线）。
- **D-7 实测结论（v3）**：
  - `D:\Source\Template\E-3707_H Laboratory Test Report -20260915.docx` 里**没有**任何 `Appendix` 标题、也**没有** `given in Appendix` 句；
  - 内部报告生成/LLCR 同步代码没有产出该句；Customer Report 网关**存在** `given in Appendix` 清洗和审计规则。
   - → 所检查模板与当前 LLCR 同步不会自动补入附录正文交叉引用；人工编辑的输入仍可能包含该句。缺口是自动生成行为，不是整个后端没有匹配规则。
- ⚠️ **但它不会进客户报告 —— 是设计而非缺陷**：`customer_report_document_gateway.py:71` 把
  `\bgiven\s+in\s+Appendix\s+[A-Z]\b` 列为**内部专用披露**，`:749-756` 整段删除，`:1101-1103` 审计发现残留即 `raise`。
  （真实样本的 CR 里那两句正是这样消失的。）同类规则还删 `performed and results reported under`。
- → 需要新增一个与"插页符"同级的受控区域（`_insert_page_break_before_heading(document, "7. EQUIPMENTS")` 同款锚定方式），
  由应用层给出"本报告存在哪些附录"的语义清单，适配器只负责按模板格式落字。

### 4.5 附录（受控区域，扩展现有 Appendix A 模式）

现有 `_appendix_a_region` / `_replace_appendix_a` 只更新 Appendix A，遇到 B–Z 时保护后续区域；其“锚定 + 删除重建”可作扩展参考，**尚不支持更新 B/D/E**：

- 区域边界逻辑需从"遇到 `Appendix [B-Z]:` 或 `*** End of Report ***` 停止"（`:919-923`）**泛化到任意字母**。
- 建议抽出 `_appendix_region(document, letter)` + `_replace_appendix(document, letter, rows)`，`Appendix A` 走同一实现（**行文等价重构**，用现有 LLCR 测试作回归护栏）。
- 附录**不进客户报告**，属既有设计，非缺陷。

---

### 4.6 IR/DWV 测量源解析（A2 的独立前置工单；D-15/16/17）

A2 的第一个问题不是“怎么填”，而是“**从哪个文件的哪一格拿数**”。IR/DWV 记录表**已由 connlab 自己生成**
（`IR&DWV Form`：preview → 下载 / 归档发布），但两件事使“读官方路径”这条最自然的做法不安全：
它的**落盘件会在正常业务操作中被换掉**，而且它**本身不含已审核的测量值**。

本节保留新增设计记录的 D-15/16/17 方向；源解析、历史候选提示及统计校验均未实施，不因本次提交变成已有功能。

#### （1）三种文件名，不等于三种数据权威

| 名字 | 形态 | 权威性 |
|---|---|---|
| **官方落盘件** | `{official_folder}/Test results/{DL} IR&DWV Record.xlsx` | ✅ 业务权威 —— `confirmed_matrix_llcr_cr_record_generation_service.py:242`（`dl = workspace.dl_number`） |
| **浏览器下载名** | `{LTR} IR&DWV Record.xlsx`；草稿为 `{LTR} IR&DWV Record draft.xlsx` | 用户可见标签，不单凭文件名确认 Matrix 权威或测量值 —— `matrix_editor_ir_dwv_record_generation_service.py:63-65` |
| 内部 artifact | `{project}_ir_dwv_record_Preview_Unconfirmed_Matrix_draft_{id}.xlsx` | ❌ 操作过程文件，**名字有误导性**，不是正式件 |

→ 导入器**不得按文件名 glob 猜**：官方命名读取 `workspace.dl_number`，下载读取确认 LTR；业务上应对应同一编号，但来源与输出路径不同，文件名不能替代项目、Matrix 版本及测量确认。

#### （2）用项目输出台账发现文件，不做文件系统扫描

发布时已登记一条输出记录（`confirmed_matrix_llcr_cr_record_generation_service.py:474-488`）：

| 字段 | 值 |
|---|---|
| `output_kind` | `ProjectOutputKind.IR_DWV_RECORD_FORM`（`domain/enums.py:193`） |
| `source` / `status` | `SYSTEM_GENERATED` / `CURRENT` |
| `output_path` | 官方落盘绝对路径 |
| `output_sha256` | **发布当时**的产物哈希（即空白件哈希） |
| `source_context_signature` | `contact-record:ir_dwv\|matrix:{matrix_id}@{revision}\|{projection_fingerprint}` |
| `note` | 发生归档时写 `Previous form preserved at {archive}; sha256={旧表哈希}.` |

台账服务：`application/project_output_record_service.py`（`register_output:116`、`get_status_summary:159`）。

台账提供两个待导入器使用的校验依据，不会自动执行以下校验：

1. **矩阵版本一致性闸门** —— `source_context_signature` 里的 `matrix:{id}@{rev}` 可断言“这张表单是在**当前**确认版 Matrix 下生成的”。
   旧版 Matrix 下生成的表单 → 不许作为报告输入。
2. **内容变化探针** —— `output_sha256` 记的是**空白件**的哈希。磁盘当前哈希 ≠ 登记哈希只证明字节变化；可能是填写测量值、Excel 重存、其他编辑或替换，不能据此证明已测量或已审核。

> ⚠️ 台账是**登记**，不是**实时完整性校验**：`get_status_summary`（`project_output_record_service.py:208-279`）只用 draft 版本对齐
> 计算 `CURRENT/STALE/MISSING/MANUAL`，**不读盘、不重新哈希**。因此 `output_sha256` 必须由导入器**自己**与磁盘实测哈希比对，
> 不能把状态 `CURRENT` 当成“文件没被动过”。

#### （3）归档会把旧表移走 —— 本单最大的静默风险

同名冲突走 `conflict_action="archive"`，实际由 `RecoverableContactRecordPublisher` 把旧表移走，再发布新空白表；Windows 下使用不覆盖目标的 `Path.rename`，不是 `os.replace`：

```
{local_workspace_path}/History/Test results/{target.stem} {operation_id}{target.suffix}
```
（归档路径计算：`confirmed_matrix_llcr_cr_record_generation_service.py:472-473`；实际恢复/发布：`backend/infrastructure/files/project_folder_required_forms_gateway.py` 的 `_recover_one`、`_move_without_replace`。）
归档后发布中断由日志恢复，不是引用的普通 Test Record 网关立即回滚；恢复会复核原表、归档、暂存和目录身份，不覆盖人工文件。

→ 操作员填完测量值后**再点一次 `IR&DWV Form` 并批准归档**，`Test results` 里就换回一张**全空的新表**。
报告若按官方路径盲读，会**静默读到空白且不报错**（结构完好、数据区全空）。
**D-16 已定 —— 解析策略取“严格”**：

1. 只认**官方路径 + 台账登记**（`output_kind` 匹配）作为候选；
2. 磁盘实测哈希 ≠ 登记 `output_sha256` 时**不自动采信**，而提示“该表在生成后被修改过”，由操作员确认这是已填测量的版本；
3. 官方路径缺失 / 哈希不符 / 结构异常时，可**提示**本地 `History/Test results/` 下的归档候选（按 mtime 排序，并显示 `note` 里记录的旧哈希），
   但**必须人工指定，绝不自动采用**；
4. 官方件与历史归档件**同时都可能含数据**时 → **不猜**，列出全部候选让人选并记录选择。

#### （4）统计值是公式，不是值 —— 必须自算（D-17）

`ir_dwv_record_workbook_gateway.py:_template_statistic:667-677` 保留模板公式意图：把 `=MIN(C22:G33)` / `=MAX(H22:L33)`
的区间重写为**实际样品区间**后，**以字符串写回**（`:653-654`，经 `:642-644` 给出 `C22:G33` / `H22:L33` 两个源区间）；
测量格被**显式清空**（`:629-633`）；读模板用 `data_only=False`（`:58`）。

→ connlab 直生成的空白表不计算公式缓存；缓存须由 Excel 或其他支持公式计算的工具生成，不能假设仅打开/保存一定刷新缓存。
**D-17 已定**：导入器**读取原始测量格自算 Min/Max**（与 §4.3 取值口径一致：IR 取 **Min**、DWV 取漏电流 **Max**），
模板统计格里的缓存值**只作交叉校验**；二者不一致即 **fail-closed**，提示“表被改过或公式被破坏”，**不取其一**。

> 这也解释了为什么不能把 xlsx 当作“权威”直接读（§4.3）：**权威是人工确认过的测量值**，
> 表格只是它的容器 —— 而容器既能被换掉（(3)），也能被改（(4)）。

---

## 5. 单据 B：照片自动插入

### 5.0 本轮回填的版式事实基线（实测，2026-10-02）

| 项 | 实测值 | 来源 |
|---|---|---|
| 页面 / 节 | 8.5 × 11 in；`section 0` l/r = 0.70in、`section 1` l/r = 0.50in；t/b 均 1.00in | 探针 `tmp/probe_photo_layout.py` |
| **正文内容宽** | 首页节 7.10in / 正文节 **7.50in** | 同上 |
| **正文内容高** | **9.00in**（两节相同） | 同上 |
| 结果表总宽 | 10881 dxa = **7.556in**（模板与产物同值） | 同上 |
| 模板已存在的图位 | `3. SAMPLE DESCRIPTION` 内、`Above information was supplied by the requestor.` 之后，有段落 **`Figure 1:`** | `E-3707_H` 模板 body child #14 |
| 该图注格式 | `w:pStyle=NormalLatinArial`、`w:spacing w:line=360`（1.5 倍）、`w:jc=center`；run 带 `<w:b/>` + `<w:u w:val="single"/>`；**无 `w:sz`** | 同上（原始 XML 实测） |
| 该图位的正文引用 | 第 3 章另有叙述句 `… given in the table below and illustrated in Figure 1.` | 模板 |
| **connlab 后端对 `Figure` 的处理** | `backend/**/*.py` grep `Figure` → **零命中** | Grep |
| 样本图注格式 | `Arial 11pt / 加粗 / 下划线 / 居中 / 行距 1.5` | 样本 #27/#32/#47/#52/#60/#74 |
| 样本图片段格式 | 居中 / 行距 1.5 / 无文本 / **同一段落内并排 2 张内联图** | 样本 #26/#31/#46/#51/#59/#73 |
| 样本组内照片尺寸 | **不统一**：每组 2 张，宽 1.67–4.18in、高 1.63–3.58in；多数组"高度接近、宽度不等"（G3 是近似转置对） | 探针 `tmp/probe_pic_sizes.py` |
| 样本组宽合计 | **4.87–6.73in ≤ 7.50in** → 并排**不换行**（宽度硬约束的实测依据） | 同上 |
| 样本组高 | 终检图内部变换高度约 2.64–3.13in；第 3 章图含 3.58in。实际段落高另受排版占位及行距影响，不能直接等同此值 | 同上 |
| `7. EQUIPMENTS` 之前 | generate 时插入**显式分页段**（`generate:151` 调 `_insert_page_break_before_heading`） | 代码 |
| `keepNext` | 输出审计**明令禁止**（`_audit_report_body_format:1366`） | 代码 |
| 格式审计覆盖面 | 正文段 `run.text.strip()` 非空者字号必须 = 11pt（章节标题 12pt）；表格内一律 11pt | `_audit_report_body_format:1368-1389` |

> **本节最重要的一条新事实**：**模板本身就预留了第 3 章的一个图位（`Figure 1:`），而 connlab 全链路从未处理它**
> （`Figure` 在后端零命中，`_fill_narrative:566-570` 只会做占位符替换，不会动它）。
> 结果：所检查模板生成的未补图产物保留**裸露图注**（`Figure 1:` 之后无文字、上方无图），且第 3 章那句
> `illustrated in Figure 1.` 成为**悬空引用**。
> → 单据 B 不只是"往第 6 章插新图"，还必须**处置已存在的模板图位**（§5.3-C）。
> 这是现有图位证据，但自动插图仍需受控身份、标记和审计，不能直接复制或清理人工图形。

---

### 5.1 绑定模型（U-3 的核心，v4）

**拟议绑定身份**包含 `project_id`、`confirmed_matrix_id` 和确认版 Group/Row/Step 标识；`group_label`、`step_token` 用于显示和报告定位校验。
组名和步骤号会变，不能单独作为跨版本稳定身份。新版 Matrix 的增删/重排须重新核对绑定，禁止只靠相同标签自动套用旧照片。

#### 5.1.1 三层对象

| 层 | 对象 | 内容 |
|---|---|---|
| 单张 | `ReportPhoto` | `relative_path`（相对项目文件夹，如 `Test results/Final Examination/xxx.jpg`）、`sha256`（文件被换掉能发现）、可选 `width_in`（人工覆盖宽度） |
| **绑定单位** | `ReportPhotoGroup` | `photos: tuple[ReportPhoto, ...]`（有序，**同段落并排**）、`placement`（三类图位之一）、`target`（Group / Step token / `template_sample`）、`caption_text`（**不含 `Figure n` 前缀**，前缀由渲染派生）、`order`（同落位内排序） |
| 版本 | `ReportPhotoBindingSetRevision` | `project_id` + `confirmed_matrix_id` + `revision` + `groups: tuple[ReportPhotoGroup, ...]` + `created_at` + `note`，**不可变**；target 需包含确认版组/步骤身份 |

**为什么绑定单位是「图组」而不是「单张照片」**：真实样本里一个图注覆盖 **2 张照片**（`Figure 3&4`），
两张图挤在**同一个段落**里并排，图注只有一条。若按单张绑定，就表达不出"这两张属于一个图注"。

> 为什么 `FileAsset`（`models.py:286`）不够：它既没有 Group/Step，也没有图组/图注/落位语义。绑定是**报告视图**，
> 与"文件登记"是两个关注点 → 新建独立表，不污染 `FileAsset`。
>
> **图片来源是精选子集，不是全量**：样本里 `Photos/` 有 22 张 setup 照**一张都没进报告**，报告的 14 张图全部来自
> `Test results/Final Examination/`（15 张里选了 14 张）→ 更加印证 U-2「自动扫 + 人工确认」，绝不能"把项目图片全插进去"。

**持久化**：整批确认后落成一版不可变 `ReportPhotoBindingSetRevision`（照抄现有数据集表的存法：DB 列 + JSON payload），
拟议报告草稿加 `photo_binding_set_id`；具体 schema/迁移待实施任务明确。相同绑定集和哈希只是幂等的输入条件，
还需验证受控区域清除、排序、图注及人工图片保留，不能直接视为幂等证明。
`figure_numbers` **不入库**：它是渲染产物，每次由文档序派生（§5.2）。

#### 5.1.2 图位（figure slot）——三类，不是两类

| 图位 | 位置 | 进 CR？ | 当前状态 |
|---|---|---|---|
| `template_sample` | **第 3 章**：模板 `Figure 1:` 图注**之前** | ✅ | **模板自带**，connlab 从未处理（裸露） |
| `inline` | 第 6 章某 Group 结果表**紧后** | ✅ | 全新 |
| `chapter_section` | 第 6 章**内**、`7. EQUIPMENTS` **之前**的新子标题下 | ✅ | 全新 |
| ~~`appendix`~~ | ~~附录~~ | ❌ **被 CR 投影整段丢弃**（`customer_report_document_gateway.py:518`） | 不做（D-3） |

**D-3 维持**：「两种落位」= `inline` + `chapter_section`，**都在正文内**。
但 §5.0 的新事实把 `template_sample` 拉进了范围（U-4 的两种落位是 2026-10-02 用户确认的，
`template_sample` 是模板既有的第三种图位，属**新增发现**，见 D-11）。

#### 5.1.3 图注文本契约

```
caption_full = "Figure " + "&".join(str(n) for n in figure_numbers) + ": " + caption_text
例：figure_numbers = (3, 4), caption_text = "Final Inspection-Samples after Group #1 Testing"
    → "Figure 3&4: Final Inspection-Samples after Group #1 Testing"
单张：figure_numbers = (7,) → "Figure 7: ..."
```
- 图注**编号由渲染派生**，操作员只填 `caption_text`（真实样本的图注句式不统一：有 `Final Inspection-Samples`、
  也有 `Inspection-Samples`（漏了 Final）、有的双空格、有的带尾随空格 → **不要试图规范化历史文案**，
  我们只保证自己产出的部分格式统一）。
- 目标格式：`Arial 11pt / 加粗 / 下划线 / 居中 / 行距 1.5`（与模板 run 属性 `<w:b/><w:u w:val="single"/>` 一致）。
- ⚠️ 与现有审计的关系：`_audit_report_body_format:1368-1379` 要求正文段字号 11pt（章节标题 12pt）。
  图注文本 `Figure 3&4: ...` **不匹配** `_is_report_chapter_heading:1344`（不是 `N. ` 编号章、不是
  `Group X Test Results`、不是 `Appendix X:`）→ 必须是 **11pt**。
  `_apply_report_body_format` 统一字号并删除直接 `keepNext`，不改粗体/下划线；新图注 run 仍需自行设置相应格式
  → 粗体与下划线必须由写入器自己设。

---

### 5.2 编号派生：文档序的确定性函数（不是配置项、不由操作员填）

```
输入：document（内部报告草稿）+ binding_set（含 groups，按 placement/order 排序）
输出：每个「我们的图位」的 figure_numbers（仅存在于内存与产物文本）

step 1  顺序扫描 body（document.element.body.iterchildren()），识别「图位」：
        图位 = （含 >=1 个 a:blip 的段落）+（其后紧邻、文本匹配 ^Figure\s+ 的图注段）
        特例：「空图位」= 只有图注段（匹配 ^Figure\s+\d+...）而上方无图片段 → 仍是图位（模板第 3 章就是）
step 2  n := 1
step 3  按文档序处理每个图位：
        (a) 我们的图位（placement ∈ {inline, chapter_section, template_sample} 且已绑定 k 张）
            → figure_numbers = (n, n+1, …, n+k−1)；n += k
        (b) 既有图位（非本系统插入，如人工粘贴）
            → 解析其现有编号 (a..b)；要求 a == n 且 b == n + (实际图片数) − 1
              不满足 → raise（"文档图编号不连续"）
        (c) 空图位且未绑定
            → 交给 §5.3-C 的处置决策（清除 / 保留）；若清除则不占编号，n 不前进
step 4  产出 figure_numbers（不回写 DB）
```

**不变式（可直接作为审计断言）**

1. 全文档图编号 **1..N 连续且唯一**（D-9 强校验）。
2. 每个"有结果图"的 Group：若 Result 列出现 `Details see Figure X&Y`，则 `(X, Y)` 必须等于该 Group 图位的编号。
3. 重跑同一 binding set + 同一文件 sha256 → **同一编号**（幂等）。
4. 编号**随内容变化**是正确的：模板 `Figure 1:` 在被分配 2 张图后必须变成 `Figure 1&2`（样本正是如此）。

**边界（fail-closed，不静默）**：若人工在草稿里插了一个带 `Figure 7:` 图注的图而 `n` 走到 5，
→ 直接 raise 并提示"文档图编号不连续，需人工确认"，**不做自动重排**（重排会静默改掉别人的编号）。

---

### 5.3 插入算法（三类图位）

**共用原语（全部复用既有技巧，不引新依赖）**

| 需要 | 原语 |
|---|---|
| 造段落 | `document.add_paragraph()`（落到 body 末尾）→ 再用 `element.addnext()` / `anchor.addprevious()` **搬到目标位**（照抄 `_replace_appendix_a:967-979` 的手法） |
| 插图 | `paragraph.add_run().add_picture(path, width=Inches(w))`；**同一段落多个 run = 并排** |
| 显式分页 | `_page_break_paragraph():1355`（审计认可的既有原语） |
| 定位结果表 | `_result_tables_by_group(document):755-775`（**命中数 ≠ 1 → raise**） |

#### A. `inline`（第 6 章 Group 结果表紧后）

```
for group in binding_set.groups where placement == "inline":
    tables = _result_tables_by_group(document)[_report_group_key(group.group_label)]
    if len(tables) != 1: raise                       # 唯一匹配校验
    anchor = tables[0]._tbl                          # 表格元素本身
    _remove_previous_photo_block(anchor)             # 幂等：先清（§5.5）
    img_para = _build_photo_paragraph(document, group)     # 居中、无文本、k 张图
    cap_para = _build_caption_paragraph(document, group)   # 居中、11pt、粗体+下划线
    anchor.addnext(cap_para._p)                      # 先挂图注
    cap_para._p.addprevious(img_para._p)             # 再插图片段到图注之前
    # 结果序：table → img → caption（与样本 #26/#27 一致）
```

- **必须用 `addnext` 链式**（`_fill_result_blocks:687-694` 的既有手法）：图片段与图注段都诞生在 body 末尾，
  不用 `addnext` 会跑到文档最后。
- 无绑定的 Group → **不插任何东西**（样本 Group 6/8 无空占位）。

#### B. `chapter_section`（第 6 章内、`7. EQUIPMENTS` 之前）

```
anchor = 唯一定位 "7. EQUIPMENTS" 段落（_heading_key 精确匹配；命中数 ≠ 1 → raise）
# ⚠️ 关键：generate 已在 EQUIPMENTS 前插了显式分页段（generate:151）。
#    必须插在该分页段之前，否则照片会跑到 EQUIPMENTS 那一页：
prev = anchor._p.getprevious()
if prev is not None and prev.xpath('.//w:br[@w:type="page"]'):
    insertion_point = prev          # 插在分页段之前 → 照片仍在第 6 章
else:
    insertion_point = anchor._p     # 无分页段时，若希望独立起页，在此前补 _page_break_paragraph()
for element in block:               # block = [sub_heading, g1_img, g1_cap, g2_img, g2_cap, …]
    insertion_point.addprevious(element)
```

- 子标题文本**必须不匹配** `_is_report_chapter_heading:1344`（不能是 `N. ` 编号章、不能是 `Group X Test Results`、
  不能是 `Appendix X:`），否则会被判为 12pt 章节标题。建议 `Photographs`（11pt 正文级）。
- 整个 block 用**整段删除后重建**实现幂等（照抄 Appendix 范式 `_replace_appendix_a:927`）→ 落位 B 天然幂等。
- 该子标题在第 6 章正文内 → **会进 CR**（正确）。

#### C. `template_sample`（第 3 章模板自带图位）——新增，需裁决（D-11）

模板第 3 章已有 `Figure 1:` 图注段（位于 `Above information was supplied by the requestor.` 之后），
且上方无图片段。三种处置：

| 选项 | 做法 | 影响 |
|---|---|---|
| **C1 填充**（推荐） | 把绑定到 `template_sample` 的照片段插到 `Figure 1:` **之前**；图注补全为 `Figure 1&2: {caption_text}` | 与样本完全一致；第 3 章那句 `illustrated in Figure 1.` 保留（样本也没改这句，即使实际是 2 张图） |
| **C2 清除** | 未绑定时删掉 `Figure 1:` 段（避免裸露图注与悬空引用） | 可能改变 golden 分页（须实测，删一个空段通常不改页数）；但产生"改产物"的额外 diff |
| **C3 保留原样** | 什么都不做（现状） | 所检查未补图产物保留裸露 `Figure 1:` 与悬空引用；保留行为须在交付中说明 |

**建议**：`C1 + C2 的组合语义` —— **绑定集里有 `template_sample` → 填充；没有 → 清除裸图注**（避免悬空引用）。
但"清除"会改产物，属保存行为变化 → 必须由 D-11 明确拍板，并同步决定
"第 3 章那句 `… illustrated in Figure 1.` 在无图时是否也要删/改写"（属同一决策的两半）。

---

### 5.4 尺寸与分页预算（D-5 的具体化）

**宽度预算（防自动换行）**：同一段落并排 `k` 张图，必须
`Σ width_i + (k−1)·gap ≤ content_width`，其中 `content_width` 取该图位**所属节**的
`page_width − left_margin − right_margin`（第 3/6 章都属正文节 → **7.50in**；首页节 7.10in）。
- 若绑定给了 `width_in` → 等比缩放到满足上式；未给 → 按自然尺寸等比缩放到上限。
- `gap` 建议 0.10in（样本里只有空格字符，不必精确）。
- **禁止依赖 Word 自动换行**：超宽会让段落变成两行 → 高度翻倍 → 分页漂移。

**高度预算（防组内拆分）**：并排段高 = `max(h_i)`；组预算
`图段高 + 图注段高(≈1 行 ≈0.25in) ≤ usable_height × 0.85`（= **7.65in**）。
样本最坏情况 ≈ 3.5in，余量充足。

⚠️ **`keepNext` 被审计禁止**（`_audit_report_body_format:1366`）→ **无法用 Word 的"图与图注同页"控制**。
整页尺寸预算不保证当前位置剩余页高足够，图注换行/段落行距也影响高度；同页需实测 Word 分页。候选补救为**在该图组前插显式分页**
（`_page_break_paragraph()`），代价是页数增加（决策 D-12）。

**几何必须从文档自身读**（`section.page_width/margins`），不要硬编码 7.5/9.0 —— 模板若改边距，规则要跟着走。

**不要试图复刻人工的尺寸选择**：实测人工选出的组内尺寸没有可归纳规则（多数组"等高不等宽"，G3 却是近似转置对；
高度 1.63–3.58in 全覆盖）。→ 自动化只遵守一条**确定性规则**：
`等比缩放使 Σ width_i + (k−1)·gap ≤ content_width` 且 `max(height_i) ≤ 高度上限`，然后居中。
人工的目视偏好不在自动化范围内（也就不会被验收为"必须像样本一样"）。

**计数口径**：判断"这个段落有几张图"要用 `a:blip` / `pic:pic` 数，**不要用 `wp:extent` 数**
（样本第 3 章图位段落有 2 个 blip 却有 5 个 `wp:extent` —— 混入了 `mc:AlternateContent` 的备用形状）。

图片内部 `a:xfrm/a:ext` 与文档占位 `wp:extent` 是不同字段；版宽预算须取有效 drawing 的占位并验证渲染，不能把内变换尺寸直接当页面占位。

---

### 5.5 幂等与"上次插入"的识别（D-6 的具体化）

落位 B 用"整段删除重建"（天然幂等）；落位 A/C **没有可依赖的固定边界**，必须能识别"上次插入的块"。三种候选：

| 方案 | 做法 | 优点 | 缺点 |
|---|---|---|---|
| **A1 书签标记**（推荐） | 图片段与图注段内各放 `w:bookmarkStart/End`，名 `CLPHOTO_{group}_{seq}` | OOXML 标准；随段落一起被删/复制；不污染可见文本 | CR 的 `FormattedText` 复制可能把书签带进客户文档（无害，但需实测确认不触发 CR 审计） |
| A2 结构判定 | 删"结果表紧后、且图注匹配 `^Figure\s+\d`"的连续段 | 零标记、兼容历史产物 | 会连带删除人工粘贴的同形内容（草稿被人工编辑过时风险真实） |
| A3 自定义段落样式 | 段落用 `CL Photo Group` 样式 | 标记稳定 | `E-4515_F` 模板没有该样式 → CR 侧样式引用悬空，可能微调分页 |

**推荐 A1**，并加交叉校验：**标记存在 ⇒ 其紧邻应有匹配图注段**，否则 raise（fail-closed）。

拟议幂等语义：
```
先按标记清除该图位上的旧块（无标记则不动）→ 再按 binding set 重建
```
- 同一 binding set + 同一文件 sha256 → 受控内容、编号和落位等价、不累积图组；不强求 ZIP 时间戳或运行元数据逐字节相等。
- ✗ 不要用"图注文本"当幂等主键（与编号耦合，编号会变）。

---

### 5.6 格式白名单与解码（D-4）

- 白名单：`jpg/jpeg/png/bmp/tif/tiff`（python-docx 内联图支持这些）。
- **`.heic` 在项目的图片归置白名单里**（`evidence_placement_rules.py:65`），但 python-docx/PIL 默认读不了
  → 绑定确认阶段若命中 HEIC，**默认 fail-closed** 并提示"需先转码为 jpg"，**不引入新依赖**（D-4 建议）。
- 另加单图硬上限（建议 `width ≤ 7.5in`、`height ≤ 6.0in`）防畸形输入。

---

### 5.7 审计与验收（单据 B 特有）

1. **编号连续性**：产物图注编号 1..N 连续唯一（§5.2 不变式 1）。
2. **交叉引用一致**：Result 列的 `Details see Figure X&Y` 与图位编号一一对应（§5.2 不变式 2，D-9）。
3. **形状审计**：有效图形分支的图片数等于绑定数；验证合计占位宽、间距、纵横比与居中，避免备用分支重复计数，同时核对视觉内容。
4. **裸图注处置**：D-11 获确认后，验收授权范围内空图注及正文引用同步处理；不能未获决定就删除模板占位或人工图注。
5. **非图片图形未被破坏**：正文图表数与页眉 OLE 数不变（§6 红线 6）。
6. **分页基线**：给出**新的**内部/客户报告页数基线（旧 24→21 作废）。
7. **Customer Report 侧断言**：数量、顺序、图注、占位/纵横比与视觉内容；不要求成品媒体 sha256 相等（D-10）。

---

### 5.8 CR 侧的必验边界

CR 清洗会删除「`Type=5` 线形 + 宽 > 520pt + 高 < 1pt」的页脚残留图形（`customer_report_document_gateway.py:864-877`）。
照片锚点是 `Type≈13`，理论上不受影响 —— **但必须实测验证**，这是单据 B 的一条硬性验收项。
历史 Internal/Customer 成品图片字节不同，但不是严格同源修订，不能据此证明 Word 必然重压缩；验收见 §10-5 与 D-10。

---

## 6. 边界与红线

1. **不改模板文件本体**（`E-3707_H` / `E-4515_F`）。
2. **加密文档**一律走 `ProtectedWordPackageGateway.stage_editable_copy` / `restore_password_protection`（现有一致做法）。
3. **不动** LLCR 结果同步、Appendix A、Equipment List 的既有行为与测试；若做 §4.5 的泛化重构，必须用现有 LLCR 测试作护栏。
4. 复用项目报告服务与 `report_publication_gateway.py`：预览指纹 → 临时生成/审计/恢复保护 → 重验当前报告 → 归档 → 原子发布。
   Word 网关的 `os.replace` 只产出新 staging 文件，不得绕过应用层直接覆盖正式报告。
5. **fail-closed**：任何"无法唯一匹配"一律 raise，不静默跳过。
6. **保留非图片图形资产**：真实样本的正文含 1 个 **Excel 图表**（`word/charts/chart1.xml`，其 rels 指向外部网络 xlsx）、
   首屏页眉含 2 个 **OLE 对象**（`embeddings/oleObject*.bin`，各 2.69 MB）。任何"清理图形"的逻辑
   **只允许**按现有断言删页脚残留（`Type=5` 且宽 >520pt 且高 <1pt 且锚点无文本），不得按 `a:blip` 之外的条件误删图表/OLE。
7. 立项以当前 `docs/task_board.md` 和 `SOL_NATIVE_WORKFLOW.md` 为准：legacy v1 单任务，idle 隔离 Submit 才升级为 main + 独立 micro。
   不依赖旧任务编号，不因本文存在而自动实施或占 WIP。
8. 不引入未来范围（AI 评审、多用户权限、LAN 部署、新执行持久化）。

---

## 7. 待裁决事项

| 编号 | 事项 | 状态 / 建议 |
|---|---|---|
| ~~D-1~~ | IR/DWV 的 Result 单元格口径 | ✅ **已关闭（v3）**：IR = `≥{min}GΩ`（或 `>{值}GΩ`）、DWV = 固定句式 + `leakage current ≤{max}nA`。见 §4.3 |
| D-2 | `synchronize_llcr_results` 是否改为通用原语的薄包装 | 倾向**是**（消除重复），但须以现有测试全绿为前提 |
| D-3 | 照片章节落位 | ✅ **已定**：A（就地）+ B（第 6 章内汇总），不做附录 |
| D-4 | HEIC 是阻断还是加转码依赖 | 建议阻断不支持的 HEIC 绑定、提示先转码，不阻断其他合法图片候选；不引入新依赖。待定，见 §5.6 |
| D-5 | 图片尺寸上限 / 方向 | **已具体化为 §5.4**（宽度预算 Σw+g ≤ `content_width`；高度预算组高 ≤ 可用高 ×0.85；几何从文档读；**不复刻人工尺寸**）。**仍待拍板**：单图硬上限（建议 `w ≤ 7.5in`、`h ≤ 6.0in`）与系数 0.85 |
| D-6 | 落位 A/C 的"上次插入识别"标记方式 | **已给三方案，推荐 A1（书签标记 `CLPHOTO_*`）**，见 §5.5；待拍板 |
| ~~D-7~~ | 正文引用句是否已在 E-3707_H 模板里 | 所检查模板无此句，当前内部报告同步未自动产出；Customer Report 有清洗规则。后续若新增须受控发布，见 §4.4 |
| D-8 | 绑定关系是否提供"从文件名自动预填"助手 | 可选增强；默认人工确认（依据 U-2） |
| **D-9** | 图组编号的落位校验强度 | 建议**强校验**（§5.2 不变式 1/2）：全文档图编号 1..N 连续唯一；Result 列的 `Details see Figure X&Y` 必须与图位编号一一对应，否则 fail-closed。待拍板 |
| **D-10** | 历史 Internal/Customer 图片字节不同，不足以证明必然由 Word 重压缩造成 | 建议验收数量、顺序、图注、排版占位/纵横比与视觉内容；来源哈希用于追溯，不要求两个成品媒体字节相等。待拍板 |
| **D-11** | **模板第 3 章自带图位 `Figure 1:` 怎么处置**（v4 新发现，见 §5.3-C） | 建议 **C1 填充 + 无绑定时清除裸图注**；同时决定第 3 章那句 `… illustrated in Figure 1.` 在无图时是否删/改写。**改产物，需拍板** |
| **D-12** | 现有审计禁止直接 `keepNext`；尺寸预算不保证剩余页高 | 候选为受控显式分页并实测 Word/PDF 页数及图注同页；其他分页策略仍待定，不能把预算视为保证 |
| **D-13** | 一个图组内的照片数量上限 `k` | 样本恒为 2。`k` 过大 → 合计宽超 `content_width` → 被迫换行 → 破分页。建议**硬上限 k ≤ 4**，且**缩放优先于换行**。待拍板 |
| **D-15** | 是否兼容历史“1 轮 1 sheet / Group × Stage”表形状 | ✅ **已定（v5，用户 2026-10-02 接受建议）**：**不兼容**。导入器只支持 connlab 当前形状；识别到历史形状即 fail-closed 并提示另立“历史项目回填”单。见 §4.3 |
| **D-16** | IR/DWV 测量源解析策略 | ✅ **已定（v5）**：**严格**。官方路径 + 台账登记 sha 校验；磁盘哈希不符时不自动采信；回退本地 `History/Test results/` **只作提示、需人工指定**，绝不静默采用。见 §4.6-3 |
| **D-17** | 自算 Min/Max 与模板统计格缓存值冲突 | ✅ **已定（v5）**：**fail-closed** 并提示“表被改过或公式被破坏”，**不取其一**。见 §4.6-4 |

---

## 8. 工单切分与顺序（建议）

| 序 | 工单 | 级别 | 内容 | 前置 |
|---|---|---|---|---|
| ~~0~~ | ~~证据准备~~ | — | ✅ **v3 已完成**：真实样本已取得并核对（见证据文档）。D-1 / D-7 关闭 | — |
| A1 | 数据集类型放开 + 通用同步原语 | high_risk | §4.1 + §4.2 + 现有测试作护栏 | — |
| **A0** | **IR/DWV 测量源解析**（台账发现 → sha/矩阵版本校验 → 归档回退只提示 → 自算 Min/Max） | high_risk | §4.6（D-16/D-17 已定） | —（与 A1 无耦合，且**必须早于 A2**） |
| A2 | IR/DWV 导入器 + 填报告 | high_risk | §4.3-1（含**独立结果呈现器**，不走 `_` 替换）；输入取自 A0 | **A0** + A1 |
| A3 | CR 结果 + 其附录 | high_risk | §4.3-2 | A1 |
| A4 | MF/UMF + Contact Retention（**合表导入**）+ 各自附录 | high_risk | §4.3-3/4 | A1 |
| A5 | 附录正文引用句受控区域 | high_risk（正式报告写入） | §4.4；先覆盖已有 LLCR Appendix A，再随新类型扩展 | 安全发布及附录语义清单 |
| B1 | 图组绑定模型（三层对象）+ **编号派生规则** + 幂等标记 + 预览/确认 UI | high_risk | §5.1 + §5.2 + §5.5 | A 全绿 |
| B2 | 图位插入算法 + 尺寸/分页预算（先做 A `inline` + B `chapter_section`） | high_risk | §5.3-A/B + §5.4 | B1 |
| B2c | 模板第 3 章图位 `template_sample` 处置（**改产物，独立成单**） | high_risk | §5.3-C | B2、**D-11 已拍板** |
| B3 | 审计口径 + **新分页基线** + CR 继承实测 | high_risk | §5.7 + §5.8 | B2（B2c 若做则一起） |

> ⚠️ **附录字母不是固定的**：VBA 的分配是 `A=LLCR / B=CR / D=MF-UMF / E=Retention`；
> 而真实样本用的是 `A=LLCR / B=Mating and Un-mating Force`，**没有** CR 附录，也**没有** D/E。
> （样本报告日期 04/Mar/2025，早于 docm 的 `Rev02_250318`，属工具演进期的差异。）
> → 新类型的附录字母建议由应用层的语义清单决定并记录来源；`ReportDataset` 若采用是拟议模型，不是当前已有的类型。
> 当前 LLCR 的固定 Appendix A 保持兼容，不因本文自动变更。

- **A0 为何独立成单**：它决定“A2 能不能拿到输入、拿到的是不是人填过的那张”。混进 A2 会让“导入逻辑对不对”与“源文件找没找对”
  两个失败面纠缠在一起，无法判断失败原因。它不改数据集、不改报告网关 → 与 A1 无耦合，可并行前置，但**必须早于 A2**。
- A1 是 A2–A4 的共同地基；A0 与 A1 可分别前置，A2 必须等待二者完成。
- A3/A4 默认串行：共用数据集、报告及附录模块，不能仅因结果类型不同就认定 scope 独立；实际边界独立时再按当前流程决定隔离工作方式。
- B 的每一个工单都是 high_risk（碰权威文档 + 分页基线）。

---

## 9. 与 VBA 的偏离（有意为之，不向 VBA 对齐）

| 维度 | VBA | connlab | 判断 |
|---|---|---|---|
| 写入方式 | `SaveAs2` 逐步原地覆盖 | 临时文件 + 审计 + `os.replace` 原子替换 | **connlab 更好，保持** |
| 附录重复 | 发现同名标题**报错并中止**，要求人工先删 | 整段删除后重建（幂等） | **connlab 更好，保持** |
| 行匹配 | `InStr` 包含匹配 | 三元精确 + 命中数 ≠ 1 即 fail-closed | **connlab 更严，保持** |
| 数据权威 | 直接读 `Test results\*.xlsx` | 先导入 → 预览确认 → 落不可变数据集 → 再填 | **connlab 更可追溯，保持** |

---

## 10. 验收策略（设计层面约定）

1. 回归保护 `_default_result` 初始化呈现及 LLCR 整格同步的可观察行为，不把 `_` 存在固化为实测导入前提。
   IR/DWV 采用专用呈现器，不从 Requirement 机械推导测量结果（§4.3）。
2. **唯一匹配 fail-closed** 必须有反例测试（重复行 / 缺行 → raise）。
3. **原子替换与审计**：产物审计失败时不得留下半成品（复用 `_audit_*` 模式）。
4. **分页基线**：单据 B 交付时给出**新的**内部/客户报告页数基线（旧的 24→21 会被图片改变）。
   真实样本可作**结构基线**（而非字节基线）：图组数 = 有图图位数、编号 1..N 连续唯一、
   **组宽合计 ≤ `content_width`**、组高 ≤ 可用高 ×0.85。
   （v4 修正：原先写的"同组同尺寸"是**错的** —— 实测组内两图宽度不等，见 §5.0。）
5. **CR 继承**：单据 A/B 完成后，需实测客户报告确实继承了结果与图组（§2.2 + §5.5）。
   不将历史字节差异归因为已验证的重压缩；比较图组数量、顺序、图注、排版占位、纵横比及视觉内容，并确认内部披露和附录不泄入客户报告。
6. **幂等**：同一输入重跑，不累积图组、引用或附录，不改变未授权区域；比对受控内容与结构，不强求 OOXML ZIP 元数据逐字节相等。
7. **真实样本回归参照**：`DL-2024-12-050 EK200` 的已交付成品可作为人读参照物，
   用于人工核对"我们产出的报告像不像实验室真正发出去的那份"（见证据文档）。
8. **单据 B 结构审计**（§5.7 全量）：图编号连续唯一、Result 交叉引用一致、`a:blip` 数 = 绑定照片数、
   有效图形分支的组宽合计 ≤ `content_width`，D-11 获确认后的授权范围内**不存在裸图注**，
   正文图表数与页眉 OLE 数不变。
9. 模板裸 `Figure 1:` 的处置须先落实 D-11；未授权 B2c 时不自动删改图注或第 3 章叙述，交付时明确报告该已知限制。
10. **测量源解析的负例**（单据 A0，§4.6）必须逐一有测试，且**每一例都不得静默取数**：
    ① 官方件已被归档 → `Test results` 换成空白新表（结构完好、数据区全空）；
    ② 磁盘实测哈希 ≠ 台账登记 `output_sha256`（字节变化，不自动推断已测量）；
    ③ `source_context_signature` 里的 `matrix:{id}@{rev}` 与当前确认版 Matrix 不一致（表单出自旧版 Matrix）；
    ④ 表形状是历史 `Group × Stage`（sheet 名含 `Initial`/`Final`）→ 按 D-15 拒绝并提示另立回填单；
    ⑤ 统计格缓存值与自算 Min/Max 不一致 → 按 D-17 fail-closed。
    正向用例须覆盖：官方路径 + 版本/结构匹配 + 已确认的测量源 → 自算极值；人工填写后哈希变化，经确认并快照留存仍可导入。全空新表不得因哈希匹配而通过；统计缓存缺失与有效缓存冲突应区分。
11. **A0 与 A2 的验收边界必须分开**：A0 只证明“源文件的身份、版本、完整性与极值口径正确”，
    不证明“写进报告的文本正确”；后者属 A2（§4.3）。

---

## 附：本设计引用的关键代码位置速查

```
内部报告网关      backend/infrastructure/office/test_report_document_gateway.py
  占位符契约        _default_result:1407-1415   _fill_result_block:731-740
  同步范式          synchronize_llcr_results:166-241
  表格锚点          _result_tables_by_group:755-775
  附录范式          _appendix_a_region:901-924   _replace_appendix_a:927-984
  审计              _audit_llcr_sync:787-810
  结果块克隆手法    _fill_result_blocks:678-699（addnext 链式插入 —— 插图算法照抄这个）
  显式分页          _page_break_paragraph:1355-1362 / _insert_page_break_before_heading:1285-1302（generate:151 调用）
  正文格式          _apply_report_body_format（统一字号、清除直接 keepNext）/ _audit_report_body_format（禁 keepNext）
  章节标题判定      _is_report_chapter_heading:1344-1352（决定 11pt 还是 12pt）
  模板契约校验      _validate_template_contract:323-368（`Group # Test Results` 锚点在 :335）
  报告生成主流程    TestReportDocumentGateway.generate:111-165（:151 插 EQUIPMENTS 分页、:156 统一正文格式）
客户报告边界      backend/infrastructure/office/customer_report_document_gateway.py:518（PURPOSE→EQUIPMENTS）
                  :1094-1097（发现附录/EQUIPMENTS 即 raise）
数据集领域模型    backend/domain/result_dataset_models.py:112-138（硬校验在 :131）
数据集存储        backend/infrastructure/storage/models_result_dataset.py:11-39
                  backend/infrastructure/storage/repositories/result_dataset.py:58-65,123-202
照片归置规则      backend/modules/folder/evidence_placement_rules.py:62-72,154-155,172-173
文件资产模型      backend/domain/models.py:286-298（无 Group/Step）
报告工作台路由    backend/api/routes_report_workspace.py（llcr/inspect:465, confirm:489, llcr-drafts:559）
```

IR/DWV 测量源链路（§4.6）：

```
输出种类枚举      backend/domain/enums.py:193   IR_DWV_RECORD_FORM = "ir_dwv_record_form"
官方落盘路径      backend/application/confirmed_matrix_llcr_cr_record_generation_service.py:241-242
                  （label = "IR&DWV"；target = official_folder/Test results/{DL} IR&DWV Record.xlsx）
归档移动语义      :472-473（archive = {local_workspace_path}/History/Test results/{stem} {operation_id}{suffix}）
                  backend/infrastructure/files/project_folder_required_forms_gateway.py
                  （_recover_one / _move_without_replace；不覆盖历史项的移动、日志恢复、身份复核）
台账登记          :474-488（output_kind / output_sha256 / source_context_signature / note）
台账服务          backend/application/project_output_record_service.py（register_output:116, get_status_summary:159,
                  状态判定 :208-279 —— 只用 draft 版本对齐，不读盘不重新哈希）
浏览器下载名      backend/application/matrix_editor_ir_dwv_record_generation_service.py:62-66
工作簿布局        backend/infrastructure/office/ir_dwv_record_workbook_layout.py（ROUNDS_PER_SHEET:13,
                  TABLE_GUTTER_COLUMN_COUNT:12, block_origins:112-124）
工作簿写入        backend/infrastructure/office/ir_dwv_record_workbook_gateway.py
                  读模板 data_only=False :58       轮次标签(行10) :581
                  测量格清空 :629-633             统计格写回公式 :642-654   _template_statistic:667-677
```

- VBA 参考映射：`docs/plans/REPORT_AUTOMATION_VBA_REFERENCE_MAP.md`
- **完整真实样本证据**：`docs/plans/REPORT_AUTOMATION_REAL_SAMPLE_EVIDENCE.md`
- VBA 源码提取件：`tmp/vba_out/`
- 真实样本解析件：`tmp/ek200_report_dump.txt`、`tmp/ek200_cr_dump.txt`、`tmp/ek200_xlsx_*.txt`、
  `tmp/ek200_body_objects.txt`、`tmp/e3707h_template_dump.txt`
- **版式/图位实测件（v4 新增，脚本均在 `tmp/`）**：
  - `tmp/probe_photo_layout.py` → `tmp/ek200_photo_layout.txt` / `tmp/e3707h_layout.txt` / `tmp/connlab_draft_layout.txt`
  - `tmp/probe_pic_sizes.py` → `tmp/ek200_pic_sizes.txt`（逐张图的显示尺寸）
  - `tmp/probe_caption_xml.py` → `tmp/cap_tpl.xml.txt` / `tmp/cap_draft.xml.txt`（图注段落原始 XML）

这些外部附件与 `tmp/` 解析件不随三份 Markdown 提交；本次核对代码和保留文本，没有重新运行宏、Office 转换或外部模板生成。
行号是该基线的导航，符号/真实行为优先。后续实施须按高风险流程重新登记、确认具体待选项和范围，不能将本提案当作已实现能力。

CR 侧补充速查（`backend/infrastructure/office/customer_report_document_gateway.py`）：

```
正文投影区间      :518   core = source.Range(purpose.Start, equipment.Start)
修订记录另段复制  :522-530
内部专用披露规则  :68-80   _INTERNAL_DISCLOSURE_PATTERNS（含 \bgiven\s+in\s+Appendix\s+[A-Z]\b）
披露段落删除      :749-756
清洗审计（命中即 raise）  :1101-1103
页脚残留删除判据  :864-877 （Type=5 且 width>520pt 且 height<1pt 且锚点无文本）
```
