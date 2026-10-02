# 报告自动化：完整真实样本证据（DL-2024-12-050 EK200）

- 状态：**历史样本证据 + 当前代码核对**。2026-10-02 按 ConnLab `93442a6c` 校正；本次仅提交文档，不修改样本或业务代码。
- 样本根：`D:\TestFlowManager\Projects\DL-2024-12-050 EK200 Connector Qualification Testing`
- 样本属性：`NPD` / `Partial Qualification` / 实验室 `Dongguan` / 负责人 `Even Yang` / 内部报告 `Rev A` 日期 `04/Mar/2025`。
- 价值：这是**从申请到最终报告的一条完整闭环**，可用于定稿设计里的悬置项。本文与
  `REPORT_AUTOMATION_VBA_REFERENCE_MAP.md`（历史行为对照）互补：那份说"宏怎么做"，这份说"成品长什么样"。
- 解析工具（本仓库 `tmp/`）：`dump_docx.py`（docx 按文档序 + 图片/尺寸）、`dump_xlsx.py`、
  `unzip_docx.py`、`count_ooxml_tokens.py`、`find_body_objects.py`。
- 本次复核依据保留的样本解析件与当前代码，未重新打开 Office、转换报告或重新验算所有外部附件；历史观测、代码事实和推论须分开阅读。

### 当前 ConnLab 与历史样本的边界

- IR/DWV 人工共享测量对、确认 Matrix 后的点位权威、空白工作簿生成及正式/草稿保存已实现；**实测结果导入并写入内部报告尚未实现**。
- 当前空白表一个 Group 对应 sheet，同组轮次横排、间隔两列，每 sheet 最多三轮；样品增至 6 不减少轮次容量。本文历史文件是 Group × Stage 分 sheet，不能直接当作当前布局。
- 权威 Matrix 且正式目录可用时保存 `{LTR} IR&DWV Record.xlsx` 到 `Test results`，同名需先确认归档；否则下载。未确认草稿命名加 ` draft`。
- LLCR 实测导入/确认、报告 Result/Comment 与 Appendix A、Equipment List 更新及 Customer Report 后台进度已实现。CR/IR/DWV/机械力实测报告写回及照片绑定/插入仍是提案。
- 锚点：`backend/application/matrix_editor_ir_dwv_record_generation_service.py`、`confirmed_matrix_llcr_cr_record_generation_service.py`、
  `backend/infrastructure/office/ir_dwv_record_workbook_layout.py`、`test_report_document_gateway.py`、`backend/domain/result_dataset_models.py`。

---

## 0. 四条直接结论（先看这个）

1. **D-1 定稿**：IR 的 Result 是 `≥{min}GΩ`（或 `>{值}GΩ`），DWV 的 Result 是固定句式
   `No evidence of arc-over or insulation breakdown,` + 换行 + `leakage current ≤{max}nA`。
   **两者都不能由 Requirement 串替换 `_` 得到**（要求里写 `≥1,000MΩ (1GΩ)`，结果写 `≥170GΩ`，单位都不同）。
2. **D-7 历史检查结论**：所检查 E-3707_H 模板没有附录引用句，当前 LLCR 同步也不自动产出正文交叉引用。
   Customer Report 网关有删除该句的规则；“不产出”不是整个 backend 零命中。
3. **图片落位的真实单位是「图组」而非「单张照片」**：一个图组 = 2 张照片（**不等宽**）挤在同一个段落
   + 1 条图注，全文档连续编号（`Figure 3&4`）。落点 = 该 Group 结果表的**紧后一个段落**。
4. **（v4 新增）模板本身就有一个图位**：`E-3707_H` 第 3 章带图注占位段 `Figure 1:`，而 connlab 全链路从不处理
   （当前内部报告网关没有 Figure 处理）→ 所检查模板生成的未补图产物保留**裸图注**及悬空引用。不能外推所有模板或人工编辑成品。详见 §11。

---

## 1. 文件夹全貌（"从项目开始到最终完成报告"）

| 层 | 文件 | 作用 |
|---|---|---|
| 元数据 | `application_data.json` | TestFlowManager 项目字段（DL / project_type / test_type / project_leader / status…） |
| 申请 | `E-mail/*.msg` ×4 | NPD 申请、规格更新、LTR 登记通知、Group 6 沿用 `DL-2024-10-004` |
| 申请 | `Submitted Material/EK200 Qualification Test Request-241022.docx` | 测试申请单 |
| 规格 | `Submitted Material/PRODSPEC GS-12-1993 …_4.doc` | 产品规格（报告第 1、2 章引用它） |
| 记录 | `Test results/DL-2024-12-050 LLCR Record_SECURED.xlsx` | LLCR 数据源 |
| 记录 | `Test results/DL-2024-12-050 EK200 Connector IR DWV Results_SECURED.xlsx` | **IR/DWV 数据源** |
| 记录 | `Test results/DL-2024-12-050 Mating_Unmating and Terminal Retention Record_SECURED.xlsx` | MF/UMF + Terminal Retention 数据源（**合表**） |
| 记录 | `Test results/DL-2024-12-050(0484) MFG Statistic data summary_secured-copy.xlsx` | MFG 统计（含设备清单） |
| 记录 | `Test results/*.pdf` ×5 | Vib / Shock 第三方分报告 |
| 记录 | `Test results/Final Examination/*.jpg` ×15 | **报告里图片的真正来源** |
| 照片池 | `Photos/*.jpg` ×22 | 各测试 setup 照片 + 样品照（**未进报告**） |
| 产出 | `DL-2024-12-050 EK200 Connector Qualification Testing Report_Rev_A.docx` / `.pdf` | **内部报告** |
| 产出 | `DL-2024-12-050-CR EK200 Connector Qualification Testing Report_Customer_Rev_A.docx` / `.pdf` | **客户报告** |
| 费用 | `DL-2024-12-050 Testing Fee Evaluation_Rev_D.xls`、`DL-2025-04-022 Form for Testing Fee Evaluation_Rev_E.xls` | 费用评估 |
| 其他 | `DL-2024-12-050 项目延迟原因.xlsx`、`DL-2024-12-050 Customer Feedback Form_Even.xlsx`、`Thumbs.db` | 延迟原因 / 反馈表 |

---

## 2. 内部报告实测结构（文档序）

| 段落 | 内容 | 形态 |
|---|---|---|
| `1. PURPOSE` | 1 段叙述 | 文本 |
| `2. CONCLUSIONS` | 1 段叙述 | 文本 |
| `3. SAMPLE DESCRIPTION` | 2 段 + 样例表（3 行数据）+ **图组 Figure 1&2** + 图注 | 表 + 图 |
| `4. TEST DESCRIPTION` | 20 行矩阵（Test Items × Group 1–8 + Sample size 行） | 表 |
| `5. TEST METHODS/REQUIREMENTS` | 19 行（Test Items / Test Method / Condition / Requirement） | 表 |
| `6. TEST RESULTS` | 导语 + **每 Group 一个「结果表 + 可选图组」** | 表 + 图 |
| `─ 结果表列` | `Step \| Test \| Requirement \| Step Description \| Result \| Comment` | 与 connlab `_RESULT_HEADERS` **一致** |
| `6 内表外` | `Table 1: Statistical Summary of Current Rating Testing (Unit: °C)`（18 行）+ T-rise 图表 | 表 + **图表** |
| `附录引用句` | `Statistical summaries of LLCR measurements are given in Appendix A.` / `Details of mating and un-mating force measurements are given in Appendix B.` | 文本（在 `7. EQUIPMENTS` 前） |
| `7. EQUIPMENTS` | 19 行设备表 | 表 |
| `8. REVISION RECORD` | `A / All / Original Release / 04/Mar/2025` | 表 |
| `Note` | `Each new revision replaces/supersedes all previous revisions.` | 文本 |
| `Appendix A` | `Statistical Summary of LLCR Measurements (unit: mΩ)`（17 行：Group × Stage × 1#–5# + Min/Max/Avg/Stdev） | 表 |
| `Appendix B` | `Mating and Un-mating Force Measurement`（12 行：S/N × Initial/Final × MF/UMF + Min/Max/Avg/Stdev） | 表 |
| `*** End of Report ***` | 结束标记 | 文本 |

Group 计数：结果表 **8 个**（Group 1–8）；图组 **7 个**（Group 1,2,3,4,5,7 各一 + 第 3 章样例一）；
附录 **2 个**（A、B）。Group 6 的注释句：`The testing of Group 6 was performed and results reported
under Lab project number DL-2024-10-004.`

---

## 3. ★ D-1 定稿：IR / DWV 的结果口径

### 3.1 数据源实测（`… IR DWV Results_SECURED.xlsx`）

本历史样本工作表 = **`Group × Stage`**（不同于当前 ConnLab 的“Group = sheet、轮次 = 横向块”）：
`Group 2 Initial` / `Group 2 Final` / `Group 5 Initial` / `Group 5 Final`。

每张表布局：

| 位置 | 内容 |
|---|---|
| B1:D2 / E1:K1 | `AP Product Test Laboratory` / `Equipment Used` |
| E2:J2 | `Instrument` / `Gage ID` / `Last Cal.` / `Cal Due.` |
| B3:D3 | `Amphenol ICC`（实验室抬头） |
| B4:D7 | 地址（Nanwei, Qisha / Shatian Town / Dongguan City / Guangdong, PRC） |
| B8:D8, B9:D9 | `Start Date:2025/01/15` / `Finish Date: 2025/01/15` |
| B10:H10, I10 | `Item/Process:  IR DWV testing` / `Request  No.:  DL-2024-12-050` |
| B11:H11, I11 | `Remarks:` / `Product Name:EK200 Connector` |
| B12, E12, H12, K12 | `Tested By: Even Yang` / `Checked By:Peter Qiu` / `Approved By:Gentle` / `Requestor: Yi-Peng.Wu` |
| K7 / K8 | `Amb Temp: 23.8℃` / `Rel. Hum.:  38.5%RH` |
| B13 / H13 | `Test/Test Condition` ×2 |
| B14 / B15 | `1~5 IR Test results` / `6~10 DWV Test results` |
| B16 / B17 | `IR: 500VDC 2minutes` / `DWV: 3000VDC 1minute` |
| 第 20 行 | 列号 `1…10`（C20:L20） |
| 第 21 行 | `UNITS` + **C21:G21 = `GΩ`（IR）**、**H21:L21 = `nA`（DWV 漏电流）** |
| 第 22 行 | `SAMPLE ID  + & -` + `Group N-#1…-#5` |
| 第 23 行 | `P1` = 实测行 |
| 第 30 / 31 行 | `Min` / `Max` |
| B42 | `此表为DGLAB-LNP-11之附件` |

实测值：

| 表 | IR（GΩ，C23:G23） | DWV 漏电流（nA，H23:L23） |
|---|---|---|
| `Group 2 Initial` | `>290`, `>290`, `>290`, **170**, `>290` | 0.9, 0.4, 1, 0, 0.8 |
| `Group 2 Final` | `>290` ×5 | 4, **30.6**, 2, 2.9, 4.6 |
| `Group 5 Initial` | （IR 块整块为空，只做了 DWV） | 0.2, 0.3, 0, 0.5, 0 |
| `Group 5 Final` | （同上） | 0.7, 0.8, 0.3, 0, 0.1 |

### 3.2 报告 Result 单元格 vs 数据源（逐条反推）

| Group | Step Description | Requirement（第 3 列） | Result（第 5 列） | 反推口径 |
|---|---|---|---|---|
| 2 | `Insulation Resistance` | `≥1,000MΩ (1GΩ)` | `≥170GΩ` | IR 取 **Min** = 170 |
| 2 | `Dielectric Withstanding Voltage` | `No evidence of arc-over, insulation breakdown, or leakage current >5mA(5x106nA)` | `No evidence of arc-over or insulation breakdown,`↵`  leakage current ≤1nA` | DWV 取 **Max** = 1 |
| 2 | `Insulation Resistance` | 同上 | `>290GΩ` | 全部为文本 `>290` → 原样透出 |
| 2 | `Dielectric Withstanding Voltage` | 同上 | …`leakage current ≤30.6nA` | Max = 30.6 |
| 5 | `Initial Dielectric Withstanding Voltage` | 同上 | …`leakage current ≤0.5nA` | Max = 0.5 |
| 5 | `Final Dielectric Withstanding Voltage` | 同上 | …`leakage current ≤0.8nA` | Max = 0.8 |

### 3.3 结论

- **IR**：`≥{IR 最小值}{单位}`；单位取自记录表第 21 行（`GΩ`）。
  - 若源值是 `>290` 这类**文本式下限**（全部如此），结果照写 `>290GΩ`——**比较符跟随源文本**（`≥` 或 `>` 两种都出现过）。
- **DWV**：固定前缀 `No evidence of arc-over or insulation breakdown,` + 换行 + `leakage current ≤{漏电流最大值}nA`。
- 以上是样本呈现口径，**不是已实现的导入算法**。数值与 `>290` 下限须区别，空白不是零；混合比较符、缺测、点位覆盖及单位换算需显式校验。
  漏电流极值只支撑数值部分，“无电弧/无击穿”须有独立记录或人工确认，不能自动推定。
- **不能复用 `_` 占位符替换**：Requirement 是 `≥1,000MΩ (1GΩ)` / `…leakage current >5mA(5x106nA)`，
  Result 是 `≥170GΩ` / `…leakage current ≤1nA`。**单位与句式都被重写**，且 `>` 不在
  connlab `_default_result:1411-1415` 的正则（只处理 `≤`/`≥`）覆盖范围内。
  → IR/DWV 必须有独立的"结果呈现器"，从记录表数据+单位构造文本。

---

## 4. ★ 图片落位的真实形态

| 编号 | 落点 | 张数 | 逐张尺寸（宽×高 in） | 组宽合计 | 图注 |
|---|---|---|---|---|---|
| `Figure 1&2` | 第 3 章样例表之后 | 2 | 2.662×1.631 / 1.670×3.578 | — | `Figure 1&2: EK200 Connector and Busbar/Plate Used for Testing` |
| `Figure 3&4` | Group 1 结果表之后 | 2 | 2.307×2.756 / 3.721×2.791 | 5.978in | `Figure 3&4: Final Inspection-Samples after Group #1 Testing` |
| `Figure 5&6` | Group 2 之后 | 2 | 2.464×2.645 / 3.515×2.636 | 5.962in | … `after Group #2 Testing` |
| `Figure 7&8` | Group 3 之后 | 2 | 2.097×2.797 / 2.779×2.084 | 4.868in | … `#3` |
| `Figure 9&10` | Group 4 之后 | 2 | 2.432×2.964 / 3.936×2.952 | 6.316in | … `#4` |
| `Figure 11&12` | Group 5 之后 | 2 | 2.631×3.106 / 4.104×3.078 | 6.712in | … `#5` |
| `Figure 13&14` | Group 7 之后 | 2 | 2.647×3.103 / 4.175×3.131 | 6.734in | … `#7` |

规则：

1. **图组 = 2 张照片挤在同一个段落**（`<w:p>` 内 2 个 `a:blip` / `pic:pic`，并排内联）。
   ⚠️ **v4 修正**：早先"同一图组内两图尺寸完全相同"的说法**是错的**（旧探针只读了每段第一个 `wp:extent`）。
   实测：**宽 1.67–4.18in、高 1.63–3.58in，组内并不等宽**；多数组呈"高度接近、宽度不等"，G3 是近似转置对。
2. **图注编号全文档连续**（1&2 → 13&14）；一个图组吃掉 2 个编号，因为它是 2 张图。
   编号是"1&2"这种**合并写法**，不是 `Figure 1` / `Figure 2`。
3. **组宽合计 4.87–6.73in ≤ 内容宽 7.50in** → 并排**不换行**（这是宽度硬约束的实测依据）。
   组高 = `max(单图高)` = 2.64–3.58in。
4. Result 列里用 `No detriment Details see Figure X&Y` 做**交叉引用**——图与 Group 的链接写在结果表里。
5. Group 6、Group 8 **没有图组**。
6. 图片源在 `Test results/Final Examination/`（15 张），**不是** `Photos/`（22 张 setup 照片一张都没进报告）。
   → 报告用的是**终检照片的一个精选子集**，不是"把项目图片全插进去"。
7. ⚠️ **计数口径**：判断"段落里有几张图"要用 `a:blip`/`pic:pic`，**不能用 `wp:extent` 计数** ——
   第 3 章图位段落有 2 个 blip 却有 5 个 `wp:extent`（混入 `mc:AlternateContent` 备用形状）。

> 对设计的直接影响：「一张照片 = 一条绑定」粒度太细。**绑定单位应当是"图组（Figure）"**：
> N 张有序照片 + 1 条图注 + 目标 Group + 落位；编号由文档顺序自动派生。

---

## 5. 数据源 xlsx 真实结构与命名漂移

### 5.1 `LLCR Record_SECURED.xlsx`（2 张表）

- `Summary`：A1:B2 = `Test Step(unit: mΩ)`，C1:F1 = `Statistics`，C2:F2 = `Min/Max/Avg/Stdev`，
  第 3–18 行 = Group × Step 的统计值。
  → **与报告 Appendix A 逐行逐值吻合**（如 Group 1 Initial：Min 0.060 / Max 0.062 / Avg 0.061 / Stdev 0.001）。
- `P`：`unit: mΩ`；第 9 行表头 `S/N | 1#…5# | Min | Max | Avg | Stdev | Test Date | Amb Temp(°C) | Rel. Hum.:%`；
  第 10–25 行 = 逐样品原始值 + 环境记录。
- 报告 Result 取 **`Summary` 的 Max**：Group 1 Initial `≤0.062mΩ` = Max 0.062 ✓。
  Group 3 有两列 0（未测），报告 Appendix A 里也原样出现 `0.000`，Result 仍取 Max 0.064 ✓
  → 历史成品保留这些零值；不等于新导入器应把“未测”视作实测零值或通过，应保留来源并提示覆盖确认。

### 5.2 `Mating_Unmating and Terminal Retention Record_SECURED.xlsx`（2 张表）

- `MF_UMF`：数据区 `L7:P11` = 5 样品 ×（Initial MF / Initial UMF / Final MF / Final UMF）；
  `L12:P15` = `Min / Max / Avg / Stdev`。**与报告 Appendix B 逐值吻合**。
  - 该 sheet 内嵌 **2 张曲线图**（`Initial Curve` / `Final Curve`），**报告 Appendix B 未包含这些图**。
- `Terminal Retention`：`Crimping tensile strength` = `503 / 526.9 / 516 / 490.9 / 518`，`Min 490.9`。
  报告 Group 8 Result = **`≥490.9N`** → **消费 Min**（因为要求是 `≥150N`）。

### 5.3 MF/UMF 消费口径（用真实数值反推，与 VBA 描述一致）

| 单元格 | 报告值 | 反推 |
|---|---|---|
| Initial MF | `≤18.61N` | `Max(18.61, 17.73, 16.87, 17.83, 16.50)` ✓ |
| Initial UMF | `≥8.93N` | `Min(12.36, 8.93, 9.67, 12.93, 18.29)` ✓ |
| Final MF | `≤29.82N` | `Max(24.82, 29.82, 23.02, 27.20, 18.57)` ✓ |
| Final UMF | `≥19.29N` | `Min(22.46, 22.77, 23.73, 22.07, 19.29)` ✓ |

单元格是**多行**文本，形如：

```
Mating Force
≤18.61N;
Un-mating Force
≥8.93N
```

### 5.4 命名漂移（导入器不能硬编码文件名）

| VBA 期望 | 本样本实际 | 差异 |
|---|---|---|
| `{编号} {LLCR\|CR} Record.xlsx` | `DL-2024-12-050 LLCR Record_SECURED.xlsx` | 多 `_SECURED` 后缀，基本吻合 |
| `{编号} Mechanical Force Summary.xlsx`（sheet `MF_UMF`） | 实际 MF/UMF 在 `DL-2024-12-050 Mating_Unmating and Terminal Retention Record_SECURED.xlsx` 的 `MF_UMF` 表 | **文件名不同**；且与 Terminal Retention **合表** |
| `{编号} …Retention…` 独立文件 | 同上（同文件第 2 张表） | 合表 |
| 设备主表（VBA 硬编码 `T:\…equipment list…xls`） | MFG 文件里自带 `Equipment List` 表 | 设备来源多样，操作员会挑 |

→ **导入器必须"发现 + 人工确认"，不能假定唯一文件名/表名。**

---

## 6. 客户报告实测差异（内部 vs CR）

| 项 | 内部报告 | 客户报告 |
|---|---|---|
| `7. EQUIPMENTS` | 有（19 行） | **无** |
| `Appendix A` / `Appendix B` | 有 | **无** |
| 正文引用句 `… given in Appendix A/B.` | 有（2 句） | **无**；与当前清洗规则一致，但历史生成原因未单独复现 |
| 章节编号 | `1. PURPOSE` … | `PURPOSE` …（`ListFormat.RemoveNumbers()`） |
| 图组 Figure 1&2 – 13&14 | 7 组 | **7 组全保留** |
| 图片字节 | `image5.png` 814 713 / `image4.jpeg` 104 422 / `hdphoto1.wdp` 121 205 | 641 864 / 92 341 / 76 812（观测到字节差异，原因未单独复现） |
| 样例表 | 3 行（含 `C19210 for terminals` / `ZAMAK3` / `C1100R-1/2H`） | **1 行**（`Copper alloy` / `Ag` / `High Temperature Resin`，料号被简化） |
| `Table 1` 逐样品行 | 完整（1#-T1…3#-T4） | **逐样品行为空**，只留 `N# Max T-Rise` 行 |
| 首屏页眉 OLE 对象 | 2 个（各 2 691 584 B） | **原样保留** |

⚠️ 两份文档**不是同一个内部修订**：内部写 `Durability(Pre.)`，CR 写 `Durability(Pre-)`；图注空格也不同。
→ 只证明历史成品存在这些差异，**不能证明差异由当前 ConnLab 投影或 Word 重压缩造成**。
清洗行为以代码为准（见 §7）；图片验收看视觉、数量、顺序和尺寸，不能要求跨成品媒体哈希相等。

---

## 7. ★ CR 清洗确证（代码级）

`backend/infrastructure/office/customer_report_document_gateway.py:68-80`：

```python
_INTERNAL_DISCLOSURE_PATTERNS = (
    re.compile(r"^\s*[#*]\s*[.:]", flags=re.IGNORECASE),
    re.compile(r"performed\s+and\s+results\s+reported\s+under", flags=re.IGNORECASE),
    re.compile(r"\bgiven\s+in\s+Appendix\s+[A-Z]\b", flags=re.IGNORECASE),
    re.compile(r"^This Laboratory Test Report shall not be reproduced except in full", flags=re.IGNORECASE),
    re.compile(r"^The contents are guaranteed to be originals \(not modified\)", flags=re.IGNORECASE),
)
```

- `:749-756`：命中的段落**整段删除**（除非它是受保护图形的锚点）。
- `:1101-1103`：审计时若仍能匹配 → `raise ValueError("Generated customer report retained internal-only disclosures.")`

→ 这证明当前 ConnLab 会清除此类披露，与历史成品差异相符；**不能证明历史成品使用了当前代码**。
同类规则也处理 `performed and results reported under`（样本 Group 6 的注释）。同时说明：

- 这两句在设计上属于**内部专用披露**：内部报告**应当**有，客户报告**必须**没有。
- 内部报告生成/LLCR 同步未自动产出附录引用句，但人工编辑或历史内部报告可以包含它，**清洗规则仍会命中**，不能删作死代码。

---

## 8. ★ D-7 定稿：正文引用句不在模板里

| 检查处 | 结果 |
|---|---|
| `D:\Source\Template\E-3707_H Laboratory Test Report -20260915.docx` | **无** `Appendix` 标题、**无** `given in Appendix` 句、**无** `are given in` |
| 当前内部报告生成/LLCR 同步 | 未产出附录正文引用句；Customer Report 网关有清洗与审计规则，不是整个 backend 零命中 |
| 模板内容确认 | 只有 `Group # Test Results` 锚点 + 空结果表（`Step\|Test\|Requirement\|Step Description\|Result\|Comment`），**没有附录结构** |

→ 结论：所检查模板与当前 LLCR 同步不自动产出正文引用句；生成的 Appendix A 没有由该动作补入正文交叉引用
（内部报告保真度缺口）。CR 侧不受影响（本来就会被删）。

这里“模板”指历史检查的 E-3707_H 与保留解析件，“不在代码”指没有自动产出该句；不包括 Customer Report 删除规则。
本次未重解析配置中的外部模板，不能保证任意版本模板都没有该句。

---

## 9. 报告里的"非图片"图形资产（网关必须保留）

| 资产 | 位置 | 要点 |
|---|---|---|
| **Excel 图表** ×1 | 正文 Group 6 `Table 1` 之后（段落序 #69） | `word/charts/chart1.xml`；其 `chart1.xml.rels` 指向**外部网络路径** `<file:///\\AP-DON-ENG01\DG Product Test Laboratory\…\DL-2024-10-004 T-rise&Derating.xlsx>`（`TargetMode="External"`） |
| **OLE 对象** ×2 | 首屏页眉 `header2.xml` / `header3.xml` | `embeddings/oleObject1.bin` / `oleObject2.bin`，各 2 691 584 B；各配 1 张 `media/image1.png` logo（43 747 B，内部/CR 未变） |

- 图表在**客户报告里也原样保留**（含那条内网路径）→ 客户文档仍带内网引用，属既有风险。
- 正文 `<w:drawing>` 共 18 个、`a:blip` 28 个、`w:pict` 6 个（含 VML 回退，故计数大于图片张数）；
  图表段落只有 1 个（#69），其余 7 个 drawing 段落 = 7 个图组。

---

## 10. 对设计的影响（逐条）

| # | 影响 | 对应设计文档条目 |
|---|---|---|
| 1 | **D-1 关闭**：IR = `≥{min}GΩ`（或 `>{值}GΩ`）、DWV = 固定句式 + `leakage current ≤{max}nA` | §4.3 / §7 |
| 2 | IR/DWV **不能**复用 `_` 占位符替换；需要独立"结果呈现器"（从记录表数据 + 单位造文本） | §4.1 / §4.3 |
| 3 | 绑定单位从"单张照片"改为 **图组（N 张 + 1 图注 + 连续编号）** | §5.1 |
| 4 | 图组落点 = 该 Group 结果表**紧后段落**；Result 列可有 `Details see Figure X&Y` 交叉引用 | §5.2 |
| 5 | 图片来源是**精选子集**（`Test results/Final Examination/`），不是全量 `Photos/` → 必须人工确认 | §5.1 / U-2 |
| 6 | 图组内两图**不等宽**（宽 1.67–4.18in）；**组宽合计 4.87–6.73in ≤ 内容宽 7.50in** → 分页基线应以此为准 | §5.0 / §5.4 / D-5 |
| 7 | 数据源**文件名/表名有真实漂移**，导入器需发现 + 人工确认 | §4.3 |
| 8 | MF/UMF 与 Retention **合表**在同一个 xlsx → 一个导入器要能读多张表 | §4.3 |
| 9 | 本样本支持 LLCR/MF/DWV 取 **Max**、IR/UMF/Retention 取 **Min/下限**；CR 的 Max 来自 VBA 参照，不是本样本实测确证 | §4.3 |
| 10 | **D-7 关闭**：引用句缺位需新增受控区域（低优先，CR 会删） | §4.4 / §7 |
| 11 | 网关须**保留**图表与 OLE 对象；不要把 `a:blip` 之外的图形当垃圾清理 | §6 红线 |
| 12 | 历史 Internal/Customer 图片字节不同，原因未单独复现；验收看视觉和结构，不要求媒体字节相同 | §10 验收 |

---

## 11. ★ 版式几何与模板图位（v4 补充实测）

### 11.1 页面几何（探针 `tmp/probe_photo_layout.py`）

| 项 | 样本报告 | `E-3707_H` 模板 | connlab 产物 |
|---|---|---|---|
| 页面 | 8.5 × 11 in | 同 | 同 |
| `section 0` 边距 l/r/t/b | 0.70 / 0.70 / 1.00 / 1.00 in | 同 | 同 |
| `section 1` 边距 l/r/t/b | 0.50 / 0.50 / 1.00 / 1.00 in | 同 | 同 |
| **正文内容宽** | 首页节 7.10in / 正文节 **7.50in** | 同 | 同 |
| **正文内容高** | **9.00in** | 同 | 同 |
| 结果表总宽 | 10772–11021 dxa（≈7.48–7.65in） | 10881 dxa = **7.556in** | 10881 dxa（每张表同值） |

### 11.2 图注与图片段的排版属性

| 元素 | 属性（样本 / 模板一致处） |
|---|---|
| 图注段落 | `w:pStyle=NormalLatinArial`、`w:jc=center`、`w:spacing w:line=360`（1.5 倍）；run：`<w:b/>` + `<w:u w:val="single"/>` + `Arial 11pt` |
| 图片段落 | 居中、行距 1.5、**无文本**、若干 run 承载 `wp:inline` 图片 |
| 图片尺寸 | `pic:spPr/a:xfrm/a:ext` 为图片内部变换，`wp:inline/wp:extent` 为文档排版占位；二者须区分。保留解析件中最大差约 0.07in，不能写成均小于 0.02in |

### 11.3 ★ 模板已有图位，connlab 从未处理

`E-3707_H` 模板 body child **#14**：

```xml
<w:p>
  <w:pPr>
    <w:pStyle w:val="NormalLatinArial"/>
    <w:spacing w:line="360" w:lineRule="auto"/>
    <w:jc w:val="center"/>
  </w:pPr>
  <w:r><w:rPr><w:b/><w:u w:val="single"/></w:rPr><w:t>Figure 1</w:t></w:r>
  <w:r><w:rPr><w:b/><w:u w:val="single"/></w:rPr><w:t>:</w:t></w:r>
</w:p>
```

- 位置：第 3 章 `3. SAMPLE DESCRIPTION`，紧跟 `Above information was supplied by the requestor.`。
- **上方没有图片段** → 这是一个"空图位"，等人贴图。
- 同章叙述句：`… given in the table below and illustrated in Figure 1.`
- **connlab 侧**：`backend/**/*.py` grep `Figure` → **零命中**；`_fill_narrative:566-570` 只做占位符替换
  → 产物里这段**与模板字节一致**（已用 `tmp/cap_draft.xml.txt` 与 `tmp/cap_tpl.xml.txt` 比对确认）。
- → 所检查模板生成的未补图报告保留裸 `Figure 1:` 和悬空引用；不是所有模板版本或人工成品的普遍断言。
  样本报告里这段被人工补成了 `Figure 1&2: EK200 Connector and Busbar/Plate Used for Testing`（并贴了 2 张图）。

### 11.4 对设计的追加影响

| # | 影响 | 设计文档条目 |
|---|---|---|
| 13 | 图位有**三类**（模板第 3 章 / 第 6 章就地 / 第 6 章汇总），不是两类 | §5.1.2 / §5.3-C |
| 14 | 编号按文档序派生；第 3 章实际绑定两图时占 1&2、第 6 章从 3 起；未绑定占位如何处理仍待决定 | §5.2 |
| 15 | 插入算法需要处理 `7. EQUIPMENTS` 前的**既有分页段**（generate:151 插入） | §5.3-B |
| 16 | 尺寸规则只能定"确定性缩放"，**不能复刻人工目视选择** | §5.4 |
| 17 | 现有审计禁止直接 `keepNext`；整页尺寸预算不能保证剩余页高足够，须验证显式分页等方案及真实 Word 分页 | §5.4 / D-12 |
| 18 | 产物中"无裸图注"应作为单据 B 的验收项 | §5.7-4 / §10-9 |

---

## 附：历史解析命令（源文件只读，会写入 tmp 产物）

```bash
# 报告结构（含图片位置与尺寸）
C:/PythonEnvs/connlab/.venv/Scripts/python.exe tmp/dump_docx.py "<报告 docx>" tmp/ek200_report_dump.txt
# 数据源结构
C:/PythonEnvs/connlab/.venv/Scripts/python.exe tmp/dump_xlsx.py "<记录 xlsx>" tmp/ek200_xlsx_<名>.txt
# 图形资产盘点
C:/PythonEnvs/connlab/.venv/Scripts/python.exe tmp/unzip_docx.py "<报告 docx>" tmp/ek200_docx
C:/PythonEnvs/connlab/.venv/Scripts/python.exe tmp/count_ooxml_tokens.py tmp/ek200_docx
C:/PythonEnvs/connlab/.venv/Scripts/python.exe tmp/find_body_objects.py "<报告 docx>"
# 版式几何 / 图注格式 / 图位（v4）
C:/PythonEnvs/connlab/.venv/Scripts/python.exe tmp/probe_photo_layout.py "<docx>" tmp/<名>_layout.txt
# 逐张图显示尺寸（v4）
C:/PythonEnvs/connlab/.venv/Scripts/python.exe tmp/probe_pic_sizes.py "<docx>" tmp/ek200_pic_sizes.txt
# 图注段落原始 XML（v4）
C:/PythonEnvs/connlab/.venv/Scripts/python.exe tmp/probe_caption_xml.py "<docx>" tmp/cap_<名>.xml.txt
```

产出件：`tmp/ek200_report_dump.txt`、`tmp/ek200_cr_dump.txt`、`tmp/ek200_xlsx_*.txt`、
`tmp/ek200_body_objects.txt`、`tmp/ek200_tokens.txt`、`tmp/e3707h_template_dump.txt`、
`tmp/ek200_photo_layout.txt`、`tmp/e3707h_layout.txt`、`tmp/connlab_draft_layout.txt`、
`tmp/ek200_pic_sizes.txt`、`tmp/cap_tpl.xml.txt`、`tmp/cap_draft.xml.txt`。

脚本/解析件及外部样本不随本次三份 Markdown 提交，跨电脑复现须另行取得文件并核对来源版本。
行号只作该核对基线的导航；当前能力以真实入口、服务与测试为准。
