# 报告自动化：VBA 参考实现映射（AutoInitialTestDocs Rev02_250318.docm）

- 状态：**历史调研记录 + 当前代码核对**。2026-10-02 按 ConnLab `93442a6c` 更新；本次仅提交文档，不实施后续自动化。
- 来源附件：`D:\LabOfficeAuto\AutoInitialTestDocs Rev02_250318.docm`
- 提取方式：`.docm` 是 OPC 包，VBA 在 `word/vbaProject.bin`（400 384 B，OLE 复合文件）。用
  `oletools.VBA_Parser.extract_macros()` 导出 19 个模块到 `tmp/vba_out/`（脚本：`tmp/extract_vba.py`）。
- 本文作用：所提取 docm 是历史人工工作流的行为对照，不是 ConnLab 的当前权威或安全策略。
  宏行号指保留的 `tmp/vba_out/` 提取件；当前能力以代码为准，不能将旧工具缺口外推到当前 ConnLab。

---

## 1. 这份文档是什么

`word/document.xml` 的 `<w:body>` 只有**一个空段落 + sectPr**（3 244 B）——即**文档正文是空的**。
所有内容由宏在运行时生成。入口：

| 位置 | 内容 |
|---|---|
| `ThisDocument.cls:11` | `Private Sub Document_Open()` → `frmFilePicker.Show vbModeless` |
| `frmFilePicker.frm:24` | `UserForm_Initialize()` → `InitializeGlobaVariables`（解析项目路径） |

`GlobalVars.bas:24 InitializePaths()` 的定位规则：

1. `ProjectNumberFolderPath = ThisDocument.Path`，`ProjectNumberFolderName = 该目录名`（= 项目编号）；
2. 在该目录的**子文件夹**里找名字包含项目编号的那个 → `ProjectFolderPath`；
3. `SubmittedMaterialFolderPath = ProjectFolderPath\Submitted material`（不存在就报错退出）；
4. `Equipment / material` 主表硬编码在 `GlobalVars.bas:12`：`T:\Equipment and material\Equipment\FCI Dongguan product test laboratory equipment list for report- Huan Revised.xls`。

→ 即"把 docm 放进项目编号目录，宏自己往上下找项目主文件夹"。

---

## 2. 九颗按钮 → 宏入口（`frmFilePicker.frm:19-69`）

| 按钮 | 调用的宏 | 性质 |
|---|---|---|
| `btnUploadFiles` | `SelectAndCopyToDestination` | 公共盘资料上传 |
| `btnInitReportandRecord` | `GenerateInitialReport` + `GenerateInitialRecordForm` | 生成内部报告 + 测试记录表 |
| **`btnUpdatedLLCR`** | `UpdateResistanceData(LLCR)` | **写数：Results + Appendix A** |
| **`btnUpdatedCR`** | `UpdateResistanceData(CR)` | **写数：Results + Appendix B** |
| **`btnUpdatedMFUMF`** | `UpdateMFUMFData` | **写数：Results + Appendix D** |
| **`btnUpdatedContactRetention`** | `UpdateContactRetentionForceData` | **写数：Results + Appendix E** |
| **`btnUpdateEquipmentList`** | `FillEquipmentTable` | **写数：Equipment 表** |
| `btnCustomerReport` | `GenerateCustomerReport` | 生成客户报告 |
| `btnSecured` | `SetExcelFilesModifyPasswordAndSaveAsSecured` | 加密（Word 侧加密调用被注释掉） |

**注意：这九颗按钮里没有 IR/DWV。** 全量 grep `IR&DWV|DWV|Dielectric|Insulation` 在 19 个模块中
**零命中**。电阻族只有两个成员（`Module_UpdateResistanceData.bas:6-9` 的枚举 `CR=0, LLCR=1`）。

---

## 3. 四个"更新"模块的共同骨架（四步）

每个"更新"宏 = `UpdateXxx()` 主流程，形状完全一致（以 `Module_UpdateResistanceData.bas:548` 为例）：

```
1. 打开数据源 xlsx（ReadOnly）         → ExtractMaxFromExcel(ws)     ' 建"组别→步骤→值"字典
2. 打开报告 docx，写 Result 单元格     → FillValuesToWord(doc)       ' 表格内落字
   SaveAs2
3. 在 "7. EQUIPMENTS" 前插一句引用语   → InsertSummaryText…(doc)     ' 正文陈述
   SaveAs2
4. 把 xlsx 统计表贴成附录              → Copy…TableToWord(doc)       ' 附录落表
   SaveAs2
```

### 3.1 数据源与定位（报告与记录表都靠命名约定）

| 模块 | Excel 路径 | 工作表 |
|---|---|---|
| LLCR / CR | `{ProjectFolderPath}\Test results\{ProjectNumberFolderName} {LLCR\|CR} Record.xlsx`（`:560`） | `Summary`（`:472`） |
| MF / UMF | `…\Test results\{…} Mechanical Force Summary.xlsx`（`:447`） | `MF_UMF`（`:448`） |
| Contact Retention | 同上（`:442`） | `Retention`（`:443`） |
| 报告 | `FindWordReport(ProjectFolderPath)`：目录里第一个 `*report_rev*.docx`（`:443-461`） | — |

### 3.2 LLCR/CR 的 Excel 结构（`ExtractMaxFromExcel:43`）

- 第 1 行 = **参数组标题**（如 `Signal`、`Power`），从 **C 列**起，**每组占 4 列**，扫描步长 `+4`（`:65`）。
- 数据从**第 3 行**起；A 列 = 组别名（合并单元格，非空时更新），B 列 = 步骤描述（`:74-79`）。
- **Max 列 = 组起始列 + 1**（`:91`）。
- 键 = `currentStep & "_" & paramName`，例如 `Initial LLCR_Signal`（`:94`）。
- 值按源单元格 `NumberFormat` 格式化后存入（`:102`）。

### 3.3 报告侧落字（`FillValuesToWord:116`）

- 结果表**从第 4 个表格起**（`:138`，前 3 个是 Sample / Test Description / Method）。
- **表格的定位锚点 = 表格前一个段落**（`:143` `tbl.Range.Previous(1).Paragraphs(1)`），
  文本形如 `Group 7 Test Results`；`CleanGroupName` 去掉尾部 `Test Results`（`:484`）后与字典组名比对。
- 命中后按行处理：列 4 = 步骤描述，**列 5 = 含 `≤` 的目标单元格**（`:164-176`）。
- 替换规则：保留 `≤` 与单位，只换掉中间的数字。
  - 左边为空或 `ΔR` → 正则 `.*?≤\s*[0-9._]+\s*([a-zA-ZΩμ]+)`，结果 `≤{值}{单位}`（`:184-207`）。
  - 左边有参数名 → 正则 `([A-Za-z\s]+)\s*≤\s*[0-9._]+\s*([a-zA-ZΩμ]+)`，结果 `{参数名} ≤{值}{单位}`（`:220-242`）。
- 组匹配用 `processedGroups` 去重（`:129/:157`）。

### 3.4 MF/UMF 与 Contact Retention（同一骨架，键不同）

- MF/UMF：Excel 数据区**固定** `startRow=10, startCol=11`，每组 4 列；
  行内匹配 `InStr(cellText, "Mating/Un")`（`:155`），第一行写 Initial、第二行写 Final；
  `≤` 取 MF 最大值、`≥` 取 UMF 最小值（`:158-165`）——**一个单元格里两个符号**。
- Contact Retention：同样 `startRow=10, startCol=11`；行内匹配 `Contact retention force`（`:120`）；
  只认 `≥`，**按出现顺序消费 min 值数组** `contactRetentionMinValues(valueIndex)`（`:147-165`）。

### 3.5 引用句与附录

| 模块 | 正文引用句（插在 `7. EQUIPMENTS` 之前） | 附录标题（贴 xlsx 统计表） |
|---|---|---|
| LLCR | `Statistical summaries of LLCR measurements are given in Appendix A.`（`:289`） | `Appendix A: Statistical Summary of LLCR Measurements(Unit: mΩ)`（`:350`） |
| CR | 同上，字母换成 B | `Appendix B: …` |
| MF/UMF | `Details of mating and un-mating force measurements are given in Appendix D.`（`:288`） | `Appendix D: Details of Mating and Un-mating Force Measurements`（`:351`） |
| Retention | `Details of contact retention force measurements are given in Appendix E.`（`:223`） | `Appendix E: Details of Contact Retention Force Measurements`（`:320`） |

- 引用句统一格式：Arial / 非粗体 / 11pt / **下划线**，插在 `7. EQUIPMENTS` 前一个空白段落，
  且**先查重**（命中相似内容弹 MsgBox 询问是否替换，`Module_UpdateResistanceData.bas:292-316`）。
- 附录插入点 = `*** End of Report ***` 前一个段落、且限定在 `Note: Each new revision replaces/supersedes
  all previous revisions.` 之后（`:369-396`）；**已存在同名标题就报错并中止**（`:386-393`）——
  即"重复执行不会重复贴附录"，代价是要求人工先删。
- 附录表格 = 直接 `rng.Copy` + `PasteExcelTable`（`:432-433`），再 `AutoFitBehavior 2`。

---

## 4. VBA 报告/记录表生成：`≤/≥ 数字 → _` 的占位约定

`Module_FillTestResultsandRecord.bas` 揭示了**模板与写入器之间的数据契约**：

- `FillTestResultFromDict:91-98` 把矩阵派生的步骤写进结果表：
  列 1 = Step、列 2 = Test、列 3 = Requirement、列 4 = StepDescription、
  **列 5 = `ReplaceTextForGreaterOrLesser(Requirement)`、列 6 = `"Pass"`（默认）**。
- `ReplaceTextForGreaterOrLesser:197-232`：遇到 `≥`/`≤` 后，把**紧随的数字/小数点连续段整体压缩成一个 `_`**。
  例：`Initial ≤0.5mΩ` → `Initial ≤_mΩ`，`ΔR ≤10mΩ` → `ΔR ≤_mΩ`。
- VBA 的数字替换依赖此占位约定；ConnLab 的 LLCR 同步按数据集构造并替换整个 Result/Comment，**不要求原单元格必须有 `_`**。
  两者呈现相似，不能把 VBA 的替换算法当作 ConnLab 的实测导入接口。

`LibraryDictionary.bas:18 ExtractAllGroupStepData` 是矩阵 → 报告步骤的转换器：
组名取第 1 行第 6 列起的列；步骤号在对应列、逗号分隔、非数字字符被剥掉；步骤描述/测试方法/条件/要求
分别取该行第 1/3/4/5 列；并按 `Requirement` 是否同时含 `Initial` 与 `After test`，把一串步骤拆成
`Initial …` / `After …` / `Final …`（`:126-206`）。样品数量来自表格最后一行（`:48`）。

---

## 5. 与 connlab 现状对照

connlab 对应实现全部在 `backend/infrastructure/office/test_report_document_gateway.py`（python-docx）。

| VBA 能力 | connlab 对应 | 状态 |
|---|---|---|
| 结果表头契约（Step/Test/Requirement/StepDescription/Result/Comment） | `_RESULT_HEADERS:45-52` | ✅ 一致 |
| `≤/≥ 数字 → _` 占位符 | `_default_result:1407-1415`（且额外把 `No detrimental condition` → `No detriment`） | ✅ 一致 |
| 表格定位锚点 = 前一段 `Group N Test Results` | `_result_tables_by_group:755-775`（正则 `Group\s+(.+?)\s+Test Results`） | ✅ 一致 |
| 行匹配 | LLCR：`(Step token, 测试项, Requirement)` 三元**精确**匹配，命中数 ≠ 1 即 fail-closed（`:196-214`） | ✅ 更严格（VBA 是 `InStr` 包含匹配） |
| 填 Result / Comment | `synchronize_llcr_results:166-241`；`_llcr_report_result:782` 产出 `Initial ≤{v}mΩ` / `∆R ≤{v}mΩ`；Comment 写 `confirmed_outcome.title()` | ✅ LLCR 已交付 |
| 附录 A（LLCR 统计表） | `_APPENDIX_A_HEADING:94`、`_appendix_a_region:901`、`_replace_appendix_a:927`（整段删后重建 → 天然幂等、可覆盖） | ✅ 已交付（比 VBA 的"重复即报错"更好） |
| Equipment 表 | `synchronize_equipment_list:243-301` | ✅ 已交付 |
| **CR 结果 + Appendix B** | — | ❌ 未实施 |
| **MF/UMF 结果 + Appendix D** | — | ❌ 未实施 |
| **Contact Retention 结果 + Appendix E** | — | ❌ 未实施 |
| **IR/DWV 结果** | — | ❌ 未实施（**VBA 里也不存在**，见 §2） |
| **IR/DWV 空白记录工作簿** | `matrix_editor_ir_dwv_record_generation_service.py`、`ir_dwv_record_workbook_gateway.py` | ✅ 已实现；与上行的实测结果导入/写回是两个功能 |
| 正文引用句（`… are given in Appendix X.`） | 内部报告生成和 LLCR 同步未产出；Customer Report 有匹配该句的清洗规则 | 已查阅模板解析件，未见此句；不是整个 backend 零命中，见真实样本证据 §8 |
| **图片插入** | `test_report_document_gateway.py` 无任何 `add_picture`/`add_image`；`customer_report_document_gateway.py:638-645` 的 `Shapes`/`InlineShapes` 只用于**保护既有图形不被删**，不是插入 | ❌ 未实施 |

### IR/DWV 的结论

1. **历史参考工具未实现 IR/DWV 报告写回**：所提取 VBA 没有此按钮；旧 TestFlowManager 的
   `src/features/matrix/service/export/service/ir_dwv_export_service.py:22` 是 `# TODO: 实现IR&DWV特定的导出逻辑` 空壳。
   （对照：同目录 `llcr_cr/` 有 5 个真实服务（export / formula / styling / summary / table_structure），
   `mating_unmating_export_service.py` 也是真实实现。）
2. **当前 ConnLab 空白表已实现**：Matrix 中 IR/DWV 共用人工输入的测量对；确认后成为点位权威。
   同组轮次横向排列（每 sheet 最多三轮，表间两列），保留 LOGO/设备与单位默认值，电压、时间和要求来自 Matrix；不写入历史实测值。
   权威 Matrix 且正式目录可用时保存到 `Test results`，同名先确认归档；否则下载。命名 `{LTR} IR&DWV Record.xlsx`，草稿加 ` draft`。
3. **报告写回仍待实施，但已有历史样本口径**：真实样本证据 §3 的 IR 取下限/Min，DWV 漏电流取 Max，二者需要专用呈现器，
   不能只替换 Requirement 中的数字。DWV“无电弧/无击穿”不能由漏电流极值推出，需独立记录或人工确认；缺测和混合比较符仍需显式处理。

### TestFlowManager 历史盘点（不代表当前 ConnLab）

- ✅ 有：LLCR/CR Record.xlsx 生成（`llcr_cr/`）、MF/UMF 导出、客户报告生成（`customer_report_generator/`）、
  报告向导（`report_wizard/`）、加密/解析等。
- ❌ 报告更新器 `report_updater/` **只做 Equipment List**（`report_updater_service.py:95 update_equipment_list`），
  没有任何结果数据写回。
- ❌ `ir_dwv_export_service.py` 是 TODO 空壳。
- → 结论：**TestFlowManager 里没有 IR/DWV 的报告写入实现，也没有 LLCR 的结果写回实现**。
  在该旧工具与 VBA 的已检查范围内，结果写回主要见 VBA；当前 ConnLab 的 LLCR 实测结果写回已经交付。

---

## 6. 对 connlab 设计的直接影响

1. 复用当前 ConnLab 的 LLCR 导入、预览确认、Matrix 版本校验、受控写入与安全发布边界；VBA 仅作行为对照，不能替代权威和追溯规则。
2. 回归保护初始化占位及 LLCR 整格同步，不把 `_` 存在写成导入前提；IR/DWV 使用独立呈现器。
3. VBA 的 `SaveAs2` 逐步覆盖 vs connlab 的"临时文件 + 审计 + `os.replace` 原子替换"：
   connlab 更安全，**不要为了对齐 VBA 而退回原地覆盖**。
4. VBA 的附录"重复即报错"人工介入 vs connlab 的整段删后重建（幂等）：
   connlab 的做法更优，应保持。
5. IR/DWV、CR、MF/UMF、Retention 的共同缺口是实测数据集及其导入/确认/报告同步链路，不是空白表生成。
   扩展不止三处类型修改，还要核对 API/UI、报告多数据集追溯及版本兼容。图片侧需要新绑定、幂等标记和分页验证。

### 核对边界

- 本次核对仓库代码、已有测试与保留的 VBA/样本解析文本；未重新运行 docm、未执行 Word 转换、未确认外部文件仍与历史解析时字节相同。
- `tmp/` 提取件与外部附件不是本次 Git 提交内容，可能在别的电脑不可用；行号只作该核对基线的导航，不作永久接口。
- 方法细节与后续提案见 [设计方案](REPORT_RESULT_PHOTO_AUTOMATION_DESIGN.md) 和 [真实样本证据](REPORT_AUTOMATION_REAL_SAMPLE_EVIDENCE.md)。

---

## 附：提取件位置

- 全量索引：`tmp/vba_out/_index.txt`
- 与本文最相关的模块：`Module_UpdateResistanceData.bas.txt`、`Module_UpdateMFUMFData.bas.txt`、
  `Module_UpdateContactReForceData.bas.txt`、`Module_FillTestResultsandRecord.bas.txt`、
  `LibraryDictionary.bas.txt`、`GlobalVars.bas.txt`、`frmFilePicker.frm.txt`、`ThisDocument.cls.txt`
- 提取脚本：`tmp/extract_vba.py`（需 `oletools`，已装入受管环境
  `~/.workbuddy/binaries/python/envs/default`）
- 未逐一细读的模块（本次未涉及）：`GetCustomerReport.bas`、`InitialInternalReport.bas`、
  `InitialTestRecordForm.bas`、`Module_FillContentInBody.bas`、`Module_FillEquipmentTable.bas`、
  `Module_FillHeadersandRevDate.bas`、`Module_FillSampleDescriptionTbl.bas`、`Module_FillTestSpecTables.bas`、
  `Module_FilesSecured.bas`、`Module_BackUpFiles.bas`、`CommonUtilities.bas`。
