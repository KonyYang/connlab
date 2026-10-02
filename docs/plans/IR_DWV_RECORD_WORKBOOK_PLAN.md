# IR/DWV Record Workbook — 实施工单（P1 → P2 → P3）

> 派发时间：2026-10-01 11:00
> 派发人：White（经 WorkBuddy 汇总）
> 执行者：Codex
> 仓库：`D:\PythonProject\connlab`，分支 `master`，工作区当前干净
> 设计依据：`C:\Users\White\WorkBuddy\2026-10-01-10-24-52\IR_DWV_Record_Button_Design.md`（v2，8 项决策已由用户拍板）

> 2026-10-01 恢复修订：White 在当前对话明确同意推荐验收口径。
> 历史成品作为排版、样式、合并区和公式参考；业务字段按当前 Matrix /
> Basic Information 的权威来源逐格校验，不复制历史实测日期、温湿度、
> 测量结果或错填组号。任何排版差异仍必须解释并验证，不能静默忽略。
> 本次仍在同一个 `TASK_362_IR_DWV_RECORD_WORKBOOK_20261001` 中完成 P1/P2/P3。
> 用户另已明确批准补入 `backend/infrastructure/files/project_folder_required_forms_gateway.py`，
> 仅使既有安全归档/恢复机制接受 `ir_dwv`，不改变 LLCR/CR 或 Create folder 行为。
> 2026-10-01 用户验收修订（优先于下述历史决策）：同一轮 IR/DWV 共用表格，
> 不因相邻步骤号不同拆表；下一轮才新增表格。不足五件保留五个物理槽并清空
> 多余槽，超过五件扩展两侧。保留用户当前模板中的 LOGO、Instrument/Gage ID
> 默认值；条件按 Matrix 填充，不复制历史测量结果、校准日期或环境值。
> 用户另批准补入 ProjectWorkbenchCloseConfirmation.tsx 及其同名测试，修复
> 新增输出类型的显示映射；独立 QA 的 72 项相关测试和生产构建已通过。
> 2026-10-02 用户明确确认：结果 UNITS 沿用登记模板（当前 GΩ / nA）；
> 电压、时间及判定要求取对应 Matrix 步骤，包含已有步骤文字覆盖。
> 判定要求不用于推断或替换结果单位，也不自动换算测量值。
> 2026-10-02 间距验收修订：同页每两份表格之间都必须有两列空白；
> 五槽三份表的起点为 B/O/AB，间隔为 M/N 与 Z/AA，第三份结束于 AL。
> 大样品布局原有容量与续页规则不变，不能因扩大页面边界而意外允许 18 件。

---

## 0. 需求一句话

在 **Matrix Editor → Test points → `IR / DWV test points` 卡片头部** 增加 `IR&DWV Form` 按钮，
**逻辑与现有 LLCR Form 按钮完全一致**（预览 → 冲突确认 → 归档发布），
产出依据 Matrix 构建的 IR/DWV 测试记录表 xlsx；
**不从零绘制**，而是加载登记模板，按「组别 = sheet」「IR/DWV 测量轮次 = 表格块」复制并填值；容量不足时增加该组的续页 sheet。

人工现状：多个组别就复制多份 sheet，一个组别有多个测试步骤就在 sheet 内复制粘贴多份表格。要实现的是这个复制过程的自动化。

---

## 1. 参考文件（真实存在，已解析）

下表尺寸和第 2 节结构记录的是初始历史模板调查，不是当前模板状态。
用户保存后的登记模板为一张原型表、22,997 B，SHA256
`07cf9e81e11fca5c1fb5d94a291aaba6851c0e748563384ef814aa8c048ef7cf`。
它包含必需 LOGO、设备默认值及 IR/DWV 四行统计公式；执行须读取当前模板，
不能恢复初始备份覆盖用户修改。最新实测证据见 GOLDEN_DIFF 文档。

| 用途 | 路径 |
|---|---|
| 人工成品样例（黄金样例） | `C:\Users\White\Desktop\AI information\Projects\DL-2026-07-115 Custom Pwr 14P VH Qualification Testing\Test results\DL-2026-07-115 BTB 14P IR&DWV Results.xlsx` |
| 模板 | `D:\Source\Template\IR&DWV Template.xlsx`（39,372 B） |
| ⚠️ 锁文件 | 初次调查时 `D:\Source\Template\~$IR&DWV Template.xlsx` 存在；2026-10-01 恢复核实已不存在，执行生成/净化时仍须实时检查 |

---

## 2. 模板结构（已逐格解析，两个文件结构一致，80 个合并区坐标相同）

```
workbook
└─ sheet「Group N」          ← 1 个组别 = 1 张 sheet
   ├─ block A（列 B..L）      ← 1 轮 IR/DWV = 1 份表格，单侧未执行时留空
   │   ├─ B1:D2  «AP Product Test Laboratory»   E1:J1 «Equipment Used»   E2:J2 Instrument/Gage ID/Last Cal./Cal Due.
   │   ├─ B3:D3  Amphenol ICC，地址 B4:B7
   │   ├─ B8:D8 Start Date   B9:D9 Finish Date   K8:L8 Amb Temp   K9:L9 Rel.Hum.
   │   ├─ B10:H10 «Item/Process: Group 1  IR&DWV-Initial»   I10:L10 «Request No.: DL-…»   I11:L11 «Product Name: …»
   │   ├─ B11:H11 «Remarks:»   B12:D12 Tested By / E12:G12 Checked By / H12:J12 Approved By / K12:L12 Requestor
   │   ├─ B13:G13 + H13:L13 «Test/Test Condition» 两列标题
   │   ├─ B14:G18 = N 行 IR 条件（"1. IR testing/ 1# 500VDC 2min. mated"…）
   │   ├─ H14:L18 = N 行 DWV 条件（"6. DWV testing/ 1# 1500VDC 1min. Mated"…）
   │   ├─ 行19 = 序号 1..2N   |  行20 = UNITS（IR: GΩ ×N，DWV: nA ×N）  |  行21 = SAMPLE ID（1#..N# ×2）
   │   ├─ 行22..33 = 数据区（行 = 测量组合/点位，列 = 样品）
   │   └─ 行34..37 Min/Max/Average/Stdev（公式 `=MIN(H22:L33)`…，只在 DWV 侧）+ 行39..40 表单页脚 FDQF-E-033 / Rev G
   └─ block B（列 O..Y）= block A 的同构平移，列偏移 +13
```

- 基准样品列数 = **5**（IR 子表 `C..G`，DWV 子表 `H..L`）。
- 列宽表里残留 `Z/AA/AJ/AK` → 历史上存在第 3 个 block。
- 黄金样例组别/步骤组合：G1[Initial, after reseating] / G2[Initial, after Humidity&Temp. cycling] / G3[Initial, after reseating]。
- ⚠️ **模板的 Group 1/2/3 里还残留真实测量数据**（如 Group1 `C22:G22=>290`、`U22:Y22=2.8/1.2/0.9/4.3/18.3`），**不能假设模板是干净的**。

---

## 3. 已核实的现有实现（照搬对象）

```
前端  frontend/src/features/matrix-editor/LlcrCrRecordDownloadAction.tsx          按钮 + 冲突确认弹窗
      frontend/src/features/matrix-editor/useLlcrCrSpecializedRecordWorkbookModel.ts  preview → download / archive+publish
      frontend/src/api/client.ts                                                  3 个 API 函数
      frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx:2243-2260      recordActions={{llcr, cr}}
      frontend/src/features/contact-measurement-plan/MatrixTestPointsEditor.tsx:56  recordActions?: {llcr, cr}
                                                                          :84      LLCR/CR 卡片的 actions 容器
                                                                          :103-109 ★目标卡片「IR / DWV test points」header（无插槽）
─────
API   backend/api/routes_matrix_editor_llcr_cr_record_generation.py
        POST …/llcr-cr-record-draft/generate            → FileResponse(.xlsx)
        POST …/llcr-cr-record-publication/preview       → target_path / blockers / preview_token
        POST …/llcr-cr-record-publication/publish       → require_project_folder_write_slot
应用  backend/application/matrix_editor_llcr_cr_record_projection.py
      backend/application/matrix_editor_llcr_cr_record_generation_service.py
      backend/application/confirmed_matrix_llcr_cr_record_generation_service.py
        → MatrixEditorLlcrCrRecordPublicationService（preview / publish_under_folder_write_slot，冲突归档到 History/Test results）
设施  backend/infrastructure/office/llcr_cr_specialized_record_workbook_gateway.py  ★ 真正写 xlsx（openpyxl 原生绘制）
      backend/infrastructure/office/llcr_cr_record_workbook_layout.py
      backend/infrastructure/files/llcr_cr_specialized_record_artifact_store.py
DI    backend/api/dependencies.py
落盘  data/generated_llcr_cr_record_drafts/  →  项目 Test results/（冲突时旧文件归档 History/Test results）
```

历史实现按单侧步骤复用了下述 LLCR 描述规则；本次修订按配对后的轮次计算，
避免产生 `After IR` 或两侧重复阶段。显式 description override 仍优先，且不改变 LLCR 实现。

```python
if index == 0:                   label = "Initial"
elif index == len(matching) - 1: label = "Final"
else:                            label = f"After {previous_row.test_item.strip() or f'Step {quantity.step_sequence - 1}'}"
# 存在 test-point 文本 override 时：label = override.description，并置 description_is_override=True
```

IR/DWV 步骤筛选沿用既有判定（`test_item` 含 `Insulation Resistance` / `Dielectric Withstanding Voltage`，参见 `confirmed_matrix_llcr_cr_record_projection.py` 的 `matrix_record_type`），按 `step_sequence` 排序。

---

## 4. 决策（**已由 White 拍板，不要再讨论或重新提案**）

| # | 议题 | 决策 |
|---|---|---|
| **D1** | 按钮落点 | `IR / DWV test points` 卡片 header（`MatrixTestPointsEditor.tsx:103-109`），文案 `IR&DWV Form`，忙碌态 `Checking IR&DWV...`，禁用条件同 LLCR |
| **D2** | block 判定与描述 | **用户修订**：以组内实际执行顺序和非电气工序边界识别测量轮次，兼容相同步骤号及连续的 IR/DWV 步骤；不按两侧第几次出现盲目配对。单侧缺失留空，重复身份报错。按轮次生成 `Initial` / `After {上一工序}` / `Final`，override 优先；不新增工艺字段，不改变 LLCR |
| **D3** | 模板注册 | 走既有 `ExternalResourceType` 机制，新增 `IR_DWV_RECORD_TEMPLATE = "ir_dwv_record_template"`（`backend/domain/enums.py:149`），**禁止把 `D:\Source\Template` 硬编码进代码**；资源值可在设置页改。先确认现有"模板目录"资源指向哪里，能复用就复用 |
| **D4** | block 复制实现 | openpyxl 自研 `copy_block`（值 + 样式 + 合并区 + 行高 + 数字格式 + 公式偏移）。**明确排除 Excel COM/Win32COM**（本机已知 COM 崩溃 `0x800706be`，且 LLCR 链路是纯 openpyxl） |
| **D5** | 步骤数排版 | **同一 sheet 内往右并排**，block 原点 `B → O → Z`（偏移 +13）；**放不下（或超过容量）就重新生成一张新表格（新 sheet）**，从模板 sheet 复制，命名 `Group 1 (2)`、`Group 1 (3)`…。**不做"换行到下方"**。⚠️ 样品数 ≠ 5 时 block 宽度会变，单 sheet 容量按实际宽度动态算，不能写死 3 |
| **D6** | 样品数 ≠ 5 | **用户修订**：物理槽数 `max(5,N)`；N > 5 两侧各增加 N-5 槽，N < 5 保留五槽且多余条件/编号/单位/样品标识/数据为空。统计和 Fee 数量使用实际 N，不使用物理槽数；合并区和分页随物理宽度重算。`5+5(d)` 只取首个数字并提示；N < 1 或非整数 blocked |
| **D7** | 输出与文件名 | **`{项目}/Test results/{DL} IR&DWV Record.xlsx`**（用 `Record`，对齐 LLCR 惯例，不用样例里的 `Results`）。冲突 → 旧文件归档 `History/Test results`；`preview_token` + `require_project_folder_write_slot` 同 LLCR；未确认 Matrix / 文件夹不可用时降级为浏览器下载。草稿目录 `data/generated_ir_dwv_record_drafts/` |
| **D8** | preview/publish 复用 | 复用 `MatrixEditorLlcrCrRecordPublicationService` 的机制，把 `record_type` 从 `Literal["llcr","cr"]` 放开为受控集合（新增 `ir_dwv`），artifact store / 文件名 / 目标路径按 `record_type` 分支 |
| **D9** | 表头字段来源 | Request No. / Product Name / Requestor / Start-Finish Date 与现有权威来源一致；无执行来源的人员、环境留空。**用户修订**：未提供明确设备选择时，Instrument/Gage ID 使用当前模板的默认值；不复制模板历史校准日期。每块及续页保留首块 LOGO，登记模板生成前后字节不变 |
| **D10** | 条件文案（行14..18） | `{n}. {IR|DWV} testing/ {i}# {矩阵行 condition 原文}`，编号 `1..N` = IR、`N+1..2N` = DWV；`mated` / `unmated` **仅当 condition 原文含该词时才附加**，不固定拼接 |
| **D11** | 数据行 | IR/DWV **共用测量组合文本**（`point_profile.electrical_point_pairs`，即刚交付的共用文本框）→ 每个非空组合一行，行首列写组合原文（如 `Odd&Even`），不拆分 `&` / `and` / `-` |
| **D12** | 模板可否修改 | **允许净化**（清数据、清冗余列宽），但**必须先备份原件**到 `D:\Source\Template\backup\` 再改（本机回收站 API 不可用，用 `Move-Item`，不要真删） |

---

## 5. 实施阶段

### P1 — 模板与写入内核（**含验收闸门**）

1. 备份模板原件到 `D:\Source\Template\backup\IR&DWV Template.xlsx`（`Move-Item`/`Copy-Item`，不要删除原文件）。
2. 写「模板资产清单」脚本，输出全部单元格值 / 合并区 / 行高列宽 / 公式 / 条件格式 / 数据验证 / 打印设置，固化为 fixture 作回归基线。
3. 新增 `backend/infrastructure/office/ir_dwv_record_workbook_layout.py` —— **布局计算器**：所有锚点（block 原点、样品区边界、IR/DWV 子表、行锚点 1/3/8/9/10/11/12/13/14/19/20/21/22/34/37/39/40、统计公式模板）由它统一产出，**禁止在别处硬编码列号**。
4. 新增 `backend/infrastructure/office/ir_dwv_record_workbook_gateway.py` —— 模板驱动写入：`load_workbook(template)` → 组别复制 sheet → 轮次 `copy_block` → **样品槽保留/扩展** → 填值 → 公式重算；每块单独克隆首块 LOGO。
5. 新增 `backend/infrastructure/files/ir_dwv_record_artifact_store.py`（照抄 LLCR 那份：uuid 命名 + containment 校验）。
6. 单测：
   - `tests/unit/test_ir_dwv_record_workbook_gateway.py` —— block 复制保真度（合并区/行高/字体/边框/公式偏移）、**样品数 3 / 5 / 7 三档逐格回归**、2/3/4 个步骤、空组合。
   - 模板指纹校验（关键锚点单元格文本比对，不匹配则 blocked）。
7. **黄金样例比对**：用 DL-2026-07-115 的输入（3 组 × 2 步骤 × 5 样品 × 1 组合）生成，与人工那份 xlsx 做**逐单元格 diff**。历史成品用来核对排版、实际样式属性、合并区和公式；动态字段逐格校验当前权威输入。保留全部差异，区分空白测量区、历史执行值/人工错误和真实格式缺陷。跨工作簿不得用样式内部索引判定格式差异；分组列宽按覆盖范围和工作表缺省宽度比较，不创建缺失列维度来读取。
8. **闸门**：把 diff 报告写进 `docs/plans/`。**真实格式缺陷或当前权威输入校验失败时，不要继续 P2/P3。** 历史成品的分阶段实测值、错填组号和手工列宽不作为产品硬编码来源；有意的模板驱动差异必须有说明及回归验证。
9. 通过 P1 闸门后记录恢复检查点，继续同一任务的 P2/P3；仅全部验收完成才进入 `ready_for_close`。

### P2 — 后端链路

- B1 `backend/application/matrix_editor_ir_dwv_record_projection.py`
- B2 `backend/application/matrix_editor_ir_dwv_record_generation_service.py`
- B6 `backend/api/routes_matrix_editor_ir_dwv_record_generation.py`（3 个端点，与 LLCR 同构）
- B7 `backend/domain/enums.py` 新增 `IR_DWV_RECORD_TEMPLATE`
- B8 `backend/application/external_resource_service.py` 纳入路径校验
- B9 `backend/api/dependencies.py` 两个 provider + 注册路由到 `backend/api/main.py`
- B10 放开 `record_type` 受控集合
- 集成测试：3 个端点 + token 校验 + 降级下载 + Test results 落盘 + 冲突归档 History + 写槽冲突

### P3 — 前端接入

- F1 `MatrixTestPointsEditor.tsx`：`recordActions` 加 `ir_dwv: ReactNode`，在 `:104` header 内渲染
- F2 `MatrixEditorWorkspace.tsx`：`recordActions` 里注入 `<IrDwvRecordDownloadAction …/>`
- F3 `frontend/src/api/client.ts`：3 个 API 函数
- 前端测试：按钮渲染、禁用态、preview→confirm 状态机
- 端到端人工核对：localhost:5173 → 按钮 → 预览 → 下载/落盘 → 冲突归档

---

## 6. 红线（违反即视为失败）

1. **不得改动 LLCR / CR 的既有行为与既有测试**（`tests/integration/test_matrix_editor_test_record_generation_api.py`、`test_llcr_cr_specialized_record_workbook_api.py` 必须通过）。
2. **不得引入 Excel COM / Win32COM**。
3. **不得把 `D:\Source\Template` 绝对路径硬编码进产品代码**（走外部资源类型）。
4. **不得依赖"模板是干净的"** —— 生成时显式清空数据区/表头区。
5. 生成前**检测 `~$` 锁文件**，命中则返回 blocked 并提示"请关闭 Excel 中的 IR&DWV Template.xlsx"。
6. 与 Fee 数量做一致性断言（samples × pairs），不一致则 blocked。
7. 模板净化前**先备份**，不要删除原文件。
8. 公共盘写入沿用 LLCR 的 `archive` 语义（先归档旧文件再写新）。
9. 用户本次已修改登记模板；不得用原 backup 覆盖它。写入器只读取模板，
   输出必须保留其 LOGO 和明确授权的设备默认值，同时清空历史执行数据。
   无法定位首块 LOGO 时明确 blocked，不静默产出缺 LOGO 的表单。

### 用户修订的实际回归输入

- 项目 `1fb51ecaf71d4a10a95bf08ccca7b369`，Group 2：IR 2/5/8，DWV 3/6/9，
  中间工序 Thermal Shock 4、Cyclic Temperature and Humidity 7，应生成三块而非六块。
- 历史 PDF 的 Group 1 IR 4/11、DWV 5/12；Group 2 IR 3/9、DWV 4/10；
  Group 3 IR 3/11、DWV 4/12，应各两块；历史实测值不是新记录来源。
- 用户编辑模板首次核对 SHA256：`389c3fe570e1f5f8ec291d1987ba6a7dd06156eb95d79fb11f1855010b699e4a`；
  原 backup SHA256：`e577747e7e18047e2e5d50062ef73d790d10312731c5c50f02862f15b093bafa`。
- 用户在 23:22 保存并关闭 Excel 后重新核对：模板 22,997 字节，SHA256
  `07cf9e81e11fca5c1fb5d94a291aaba6851c0e748563384ef814aa8c048ef7cf`，
  锁文件已不存在；仍有一个 LOGO、默认设备/编号、空校准日期和 GΩ/nA 单位。
- 该当前模板的 IR 统计区是四行独立公式（`C36:G36` / `C37:G37`），不是
  历史 `C36:G37` 合并的 `/`。需兼容这两种真实布局，并保留模板每侧的
  统计方式；公式范围按实际样品数生成，不能把新模板修改回旧拓扑。
- 2026-10-02 用户已确认结果 UNITS 沿用登记模板；电压、时间及判定要求取 Matrix。
  判定要求输出到既有 Remarks，保留步骤文字覆盖；电压和时间单位不能作为结果单位。

---

## 7. 运行环境与测试

- **Python**：项目专用环境 `C:/PythonEnvs/connlab/.venv/Scripts/python.exe`（Python 3.11.9）。**不要用系统 Python 3.13**，项目已在 TASK_361B 明确对齐过解释器。
- **测试入口**：`scripts/run_tests.ps1`（默认用上面的 venv，支持 `-PythonExe` 覆盖，含 normal/Office 分流，Office 测试默认 deselect）。
- **前端**：Vite `localhost:5173`；后端 `127.0.0.1:8000`。
- 命中 Office/COM 依赖的测试要隔离到 `office` marker，默认跳过（已知 `tests/integration/test_project_test_plan_preview_api.py` 会触发 Word COM 并崩溃整个 pytest 进程）。

---

## 8. 治理要求（按项目既有流程）

1. 前置点位任务已关闭；本工单的 P1/P2/P3 在同一高风险任务 `TASK_362_IR_DWV_RECORD_WORKBOOK_20261001` 中执行，维持 `wip_limit: 1`。
2. 通过唯一看板 writer 保存有用的阶段恢复检查点；测试、独立审查和验收事实保留在本工单、黄金差异报告及最终看板结果，不重复创建 lane 证据。
3. 提交信息用英文、说明改动范围与验证结果（沿用仓库既有风格）。
4. **未经验证不标记 accepted**；P1 的黄金样例 diff 未通过则停在该阶段。
5. 涉及公共盘/项目文件夹的写操作，遵循既有 folder write slot 机制，不要绕过。

---

## 9. 完成定义（DoD）

- [x] 模板已备份并登记为外部资源 `IR_DWV_RECORD_TEMPLATE`，公开 validate API 返回 valid；当前用户修改的模板保持不变，SHA 与保真核对见 GOLDEN_DIFF
- [x] 布局计算器覆盖样品数 3/5/7、多轮 IR/DWV 共表与容量续页（容量依据实际表宽）
- [x] 受影响单测与 API 验证全绿，含 block 保真度、样品数三档、判定要求及两列间隔回归；最终间距修订 QA 85 项通过
- [x] 黄金样例 diff 报告完成；当前模板/权威输入、历史执行值清空及有意差异有明细与验证
- [x] 3 个后端端点可用，落盘/归档/降级行为与 LLCR 一致
- [x] `IR&DWV Form` 位于 `IR / DWV test points` 卡片 header，隔离浏览器全流程已核对
- [x] LLCR/CR 既有相关测试通过，未改变既有发布行为
- 看板最终提交与 `ready_for_close` 以唯一 writer 的实际结果为准；独立集成核对后完成，不提前宣称关闭。
