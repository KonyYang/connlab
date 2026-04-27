# ConnLab Phase 6 实施方案：Outlook Email Package Intake、Application Form Selection And Human Confirmation

> 本版根据真实业务补充进行更新：ConnLab 项目的真实起点通常不是单独的 Word 申请单，而是客户/内部 requestor 通过 Outlook 发送的一封邮件。邮件中可能包含申请单、规格书、图片、补充说明或多个候选申请单。Phase 6 应围绕“邮件包导入 → 附件列表 → 人工选择申请单 → 解析草稿 → 人工确认 → 创建项目”重构 intake 边界。

---

## 0. 本版关键修订

相较上一版 `Real Email/Word Intake And Human Confirmation`，本版做出以下调整：

1. **Phase 6 主线从“Email/Word Intake”细化为“Outlook 邮件包导入 + 申请单选择 + 人工确认”。**
2. **明确一份申请单创建一个项目**，不能简单设计成“一封邮件 = 一个项目”。
3. **新增 `IntakePackage → IntakeAsset → IntakeCase` 结构**，支持一封邮件里没有申请单、一个申请单、多个申请单三种情况。
4. **保留直接导入 Word 申请单的特殊入口**，但内部仍走统一 Intake 流程。
5. **新增 OfficeFacade / Office Integration Boundary**，统一管理 Outlook、Word、Excel 相关读取、提取、转换和后续 COM fallback，避免各功能模块各自操作 Office。
6. **Phase 6 暂不做 Outlook Inbox 自动扫描或 Outlook COM 自动读取当前邮箱**，先支持用户导入 `.msg` 文件，降低与用户正在使用的 Outlook 冲突风险。
7. **Parser hardening 仍是必要切片**，但它服务于邮件包 intake，而不是独立成为 Phase 6 主线。
8. **高风险任务必须拆小执行**：`.msg` 导入先做原文件入库和最小 metadata，再做附件提取，最后做真实样本兼容。
9. **Phase 6 UI 不一次性做完整 Intake Review**：Inbox、Package Detail、Case Review 分任务落地。
10. **TASK_026 只建立 Office 边界和 Word gateway 最小读取能力**，Excel 只保留边界占位，不提前实现测试结果或 workbook 业务读取。

---

## 1. 当前状态判断

根据当前项目计划，Phase 5 已完成，Phase 6A 已被明确批准并激活，当前 active task 为 `TASK_027B_OUTLOOK_MSG_ATTACHMENT_EXTRACTION`。

已完成主线能力：

- FastAPI + SQLite + SQLAlchemy 基础。
- Project / ApplicationForm / SampleInfo / Precheck / LTR / Folder 领域基础。
- DOCX application form parser 初版。
- deterministic precheck engine 初版。
- LTR 注册与 folder preview/generation。
- React + TypeScript 前端 shell、左侧导航、项目列表、项目 workbench stepper。
- Phase 5 文档、构建和测试守卫。

当前关键限制：

- 当前 intake 更接近“项目内上传 DOCX 后直接落库”，没有“解析结果只是草稿、人工确认后才成为权威数据”的边界。
- 当前 parser 对真实 Word 表单仍不够稳，特别是 header/footer、合并单元格、多标签同单元格、样品表头别名。
- 当前 FileAsset 强绑定 Project，无法自然表达“还没有项目、先收到一封邮件/一组附件”的 Intake Inbox。
- 当前流程没有表达“一封邮件多个附件、多份申请单候选、人工选择其中一份申请单开启项目”的业务规则。
- 当前 PrecheckEngine 支持 `registered_attachments` 参数，但 service 运行 precheck 时没有把项目附件传进去。
- 当前前端 `ProjectWorkbenchPage.tsx` 已较重，Phase 6 继续加 UI 前应拆出 Intake 页面与 review components。

---

## 2. 真实业务需求重述

真实业务入口如下：

```text
Outlook 邮件
  ├── 邮件主题 / 发件人 / 收件人 / 抄送人 / 正文
  ├── 附件 1：Word 申请单候选
  ├── 附件 2：PDF 规格书 / 客户规范 / supporting document
  ├── 附件 3：图片 / 邮件签名图 / 其他材料
  └── 可能存在多个 Word 申请单，或完全没有申请单
```

当前人工流程是：

```text
1. 人工从 Outlook 邮件中另存附件。
2. 人工判断哪一个 Word 文件是申请单。
3. 人工打开并确认 Word 申请单。
4. 一份申请单创建一个项目。
5. 再进入 LTR、文件夹、Precheck、Matrix、Test Record、Report 等后续流程。
```

期望软件流程是：

```text
1. 用户导入 Outlook 邮件文件，优先支持 .msg。
2. 系统读取邮件元数据和正文。
3. 系统提取附件并形成附件列表。
4. 系统自动标记可能的申请单、规格书、图片、其他支撑附件。
5. 用户人工选择其中一份申请单。
6. 系统解析该申请单，生成项目草稿。
7. 用户人工确认 / 修正草稿。
8. 系统创建 Project + ApplicationForm + SampleInfo。
9. 系统把邮件、申请单、规格书和支撑附件登记为项目资产。
10. 项目进入现有 Precheck / LTR / Folder 流程。
```

特殊入口：

```text
用户也可以不导入邮件，直接导入 Word 申请单开启项目。
```

该特殊入口不应另起一套逻辑，而应在内部创建一个 `source_type = direct_application_form` 的 IntakePackage，并自动把该 Word 文件标记为 selected application form。

---

## 3. Phase 6 候选排序更新

| 候选 | 价值 | 风险 | 依赖 | 更新后建议 |
|---|---:|---:|---|---|
| 6A Real Email/Word Intake + Human Confirmation | 最高 | 中高 | 需要邮件包模型、附件选择、最小 parser 加固、review UI | **作为 Phase 6 主线，但命名和范围升级为 Outlook Email Package Intake + Application Form Selection** |
| 6B Application Form Parser Hardening | 高 | 中 | 依赖真实表单样本 | 抽取必要切片并入 6A；完整 6B 可作为 Phase 7 |
| 6C Folder Template Configuration UX | 中 | 低中 | 依赖确认后的项目数据更稳定 | Phase 6 后再做 |
| 6D Precheck Rule Expansion | 高 | 中 | 依赖邮件元数据、附件、parser 和确认数据可靠 | 不建议先做；Phase 6 只预留数据结构和少量 bridge |

推荐结论：

```text
Phase 6 = Outlook Email Package Intake
        + Application Form Selection
        + Human Confirmation
        + Direct Word Form Import
        + OfficeFacade Boundary
        + 最小 6B Parser Hardening 切片

Phase 7 = 完整 6B Parser Hardening 或 6C Folder Template Configuration UX
Phase 8 = 6D Precheck Rule Expansion
```

---

## 4. Phase 6 核心目标

Phase 6 只解决一个核心问题：

```text
真实请求材料进入系统后，必须先形成可审阅草稿；
只有经人工确认后，才创建/更新 Project + ApplicationForm + SampleInfo，
并进入 Precheck / LTR / Folder 流程。
```

同时，Phase 6 要建立长期可扩展的 intake 边界：

```text
Request Source
  ├── Outlook .msg email package
  ├── Direct Word application form
  └── Future: Outlook selected item / mailbox integration

统一进入：
IntakePackage -> IntakeAsset -> Application Form Selection -> IntakeCase -> Review Draft -> Confirm Project
```

当前流程将从：

```text
Create Project -> Upload DOCX -> Parsed data immediately persisted -> Precheck
```

升级为：

```text
Import Email Package / Import Word Form
      ↓
Extract Assets
      ↓
Select Application Form
      ↓
Parse Draft
      ↓
Human Review / Correction
      ↓
Confirm
      ↓
Create Project + ApplicationForm + SampleInfo + FileAssets
      ↓
Precheck -> LTR -> Folder
```

---

## 5. 关键架构原则

### 5.1 一封邮件不是一个项目

必须避免：

```text
EmailPackage = Project
```

真实规则是：

```text
一封邮件可以没有申请单。
一封邮件可以有一份申请单。
一封邮件可以有多份申请单。
一份被确认的申请单创建一个项目。
```

因此建议结构是：

```text
IntakePackage             # 一次导入的邮件包或直接申请单包
  ├── IntakeAsset[]       # 邮件原件、附件、直接上传文件
  └── IntakeCase[]        # 每个 case 对应一份被选中的申请单
        └── confirm 后创建 Project
```

### 5.2 Parser output 不是权威数据

Parser 的结果只能是 draft：

```text
parser output -> IntakeDraft -> human review -> confirm -> domain tables
```

禁止：

```text
parser output -> directly create ApplicationForm / SampleInfo
```

### 5.3 Office 操作必须集中在 OfficeFacade

禁止各模块直接操作 Office：

```text
Intake 模块自己读 Outlook
Report 模块自己开 Word
Matrix 模块自己开 Excel
Test Record 模块自己开 Excel
Precheck 模块自己读 Word
```

必须统一走：

```text
backend/infrastructure/office/
```

这样可以避免：

- Word/Excel/Outlook COM 实例泄漏。
- 文件被锁定。
- 程序误关闭用户正在打开的 Word/Excel/Outlook。
- 不同模块使用不同临时目录、备份目录、路径策略。
- Office 错误处理和日志分散。
- 打包后 Office 兼容性问题难以定位。

### 5.4 Phase 6 优先解析 `.msg` 文件，不直接控制 Outlook 客户端

Phase 6 支持：

```text
用户从 Outlook 另存 .msg，或拖入 .msg 文件。
ConnLab 解析 .msg 文件、提取正文和附件。
```

Phase 6 不做：

```text
自动扫描 Outlook Inbox
自动读取当前选中邮件
自动标记邮件已处理
自动移动邮件
自动发送邮件
```

后续确实需要 Outlook COM 时，也必须从 OfficeFacade 的 Outlook gateway 进入。

---

## 6. OfficeFacade / Office Integration Boundary 设计

### 6.1 推荐目录

```text
backend/
  infrastructure/
    office/
      __init__.py
      office_facade.py
      office_lifecycle.py
      outlook_msg_gateway.py
      word_document_gateway.py
      excel_workbook_gateway.py
      models.py

  application/
    intake_package_service.py
    intake_confirmation_service.py

  domain/
    intake_models.py

  modules/
    intake/
      application_form_classifier.py
      application_form_parser.py
```

### 6.2 OfficeFacade 责任

OfficeFacade 应负责：

```text
1. 读取 .msg 邮件文件。
2. 提取 subject / sender / recipients / cc / sent time / body text。
3. 提取附件到受控 intake 目录。
4. 识别附件基础类型：docx / pdf / xlsx / image / unknown。
5. 读取 Word docx 的正文、表格、header、footer。
6. 仅保留 Excel workbook gateway 边界占位；完整 Excel 读取不属于 Phase 6A 主线。
7. 后续必要时统一管理 pywin32 COM 生命周期。
```

OfficeFacade 不负责：

```text
1. 不创建 Project。
2. 不写 ApplicationForm / SampleInfo。
3. 不决定业务上最终哪一份文件一定是申请单。
4. 不运行 Precheck。
5. 不生成 LTR 或项目文件夹。
6. 不从 UI 直接调用。
```

### 6.3 防冲突原则

```text
1. 优先使用文件级解析库，不启动 Office 程序。
   .docx -> python-docx
   .xlsx -> openpyxl
   .msg  -> msg / ole parser

2. 所有导入文件先复制到 data/intake，再解析副本。

3. Word/Excel/Outlook COM 只能作为 fallback。

4. COM 生命周期必须集中在 OfficeLifecycleManager。

5. 业务模块禁止直接 Dispatch Word/Excel/Outlook。

6. COM fallback 使用独立实例，不复用用户正在打开的 Office 应用。

7. 所有 COM 操作必须：
   Visible = False
   DisplayAlerts = False
   ReadOnly = True
   finally Quit

8. Phase 6 不直接控制用户 Outlook 客户端，只解析用户导入的 .msg 文件。
```

### 6.4 接口草案

```python
class OfficeFacade:
    def import_outlook_msg(self, source_path: Path, target_dir: Path) -> ImportedMailPackage:
        ...

    def read_word_document(self, source_path: Path) -> WordDocumentSnapshot:
        ...

    def classify_file(self, source_path: Path) -> OfficeFileClassification:
        ...
```

TASK_026 的落地边界：

```text
必须实现：
- OfficeFileClassification 数据结构。
- WordDocumentSnapshot 数据结构。
- WordDocumentGateway.read_word_document() 的 docx 文件级读取。
- OfficeFacade.classify_file()。
- OfficeFacade.read_word_document()。
- OutlookMsgGateway / ExcelWorkbookGateway 的受控边界占位。

不得实现：
- .msg 附件提取。
- intake 数据库表。
- Project / ApplicationForm / SampleInfo 创建。
- Excel 测试结果读取。
- Outlook COM 自动化。
```

```python
@dataclass(frozen=True, slots=True)
class ImportedMailPackage:
    subject: str | None
    sender_name: str | None
    sender_email: str | None
    recipients: list[str]
    cc: list[str]
    sent_at: datetime | None
    body_text: str | None
    attachments: list[ImportedMailAttachment]
```

```python
@dataclass(frozen=True, slots=True)
class ImportedMailAttachment:
    original_name: str
    stored_path: Path
    extension: str
    size_bytes: int
    sha256: str
    content_id: str | None = None
```

```python
@dataclass(frozen=True, slots=True)
class WordDocumentSnapshot:
    paragraphs: list[str]
    tables: list[list[list[str]]]
    headers: list[str]
    footers: list[str]
    raw_text: str
```

---

## 7. 建议新增领域对象

### 7.1 IntakePackage

表示一次导入的业务请求包，可来源于 Outlook `.msg`、直接 Word 申请单、后续 Outlook selected item 或人工登记。

建议字段：

```text
package_id
source_type: outlook_msg | direct_application_form | manual | future_outlook_item
status: imported | needs_application_form_selection | ready_for_review | partially_confirmed | confirmed | rejected
source_original_name
source_stored_path
subject
sender_name
sender_email
recipients_json
cc_json
received_at
body_text
created_at
updated_at
notes
```

状态说明：

```text
imported
  邮件或文件已导入，资产已保存。

needs_application_form_selection
  已有附件列表，但还没有选定申请单；可能没有候选，也可能有多个候选。

ready_for_review
  已选定申请单并生成 IntakeCase / IntakeDraft。

partially_confirmed
  一封邮件中已有部分申请单生成项目，但仍有其他候选可继续处理。

confirmed
  所有需要处理的 case 已确认。

rejected
  该邮件包或申请单被人工标记为不处理。
```

### 7.2 IntakeAsset

IntakeAsset 用于“项目尚未确认前”的文件登记，不直接复用 Project-scoped FileAsset。

建议字段：

```text
asset_id
package_id
original_name
stored_path
extension
mime_type
size_bytes
sha256
asset_role: unknown | email_source | application_form_candidate | selected_application_form | specification | supporting_attachment | inline_image | ignored
candidate_score
content_id
created_at
```

典型角色：

```text
Word 申请单候选 -> application_form_candidate
被人工选中的 Word 申请单 -> selected_application_form
PDF 规格书 -> specification
邮件签名图片 -> inline_image / ignored
其他材料 -> supporting_attachment
原始 .msg -> email_source
```

### 7.3 IntakeCase

一份被选中的申请单对应一个 IntakeCase；confirm 后创建一个 Project。

建议字段：

```text
case_id
package_id
selected_form_asset_id
status: draft_created | needs_review | confirmed | rejected
confirmed_project_id
created_at
updated_at
reviewer_notes
```

重要规则：

```text
一封邮件可以创建多个 IntakeCase。
每个 IntakeCase 最多 confirm 成一个 Project。
Project 不直接绑定整封邮件，而是绑定确认后的 IntakeCase。
```

### 7.4 IntakeDraft

保存 parser 输出和人工修正草稿。

建议字段：

```text
draft_id
case_id
parsed_fields_json
sample_rows_json
requested_testing_json
field_confidence_json
parser_warnings_json
manual_overrides_json
updated_at
```

Phase 6 可以先用 JSON 存 draft，避免过早设计复杂表结构；确认时再映射到现有 ApplicationForm 和 SampleInfo 表。

---

## 8. 文件存储设计

导入阶段：

```text
data/
  intake/
    {package_id}/
      source/
        original.msg
      attachments/
        {asset_id}__Coolpower HD3.5MM product qualification test Request.docx
        {asset_id}__GS-12-1941_Rev1 CoolPower HD.pdf
        {asset_id}__image003.jpg
      snapshots/
        mail_body.txt
        imported_mail.json
        word_snapshot_{asset_id}.json
```

确认项目后：

```text
data/
  projects/
    {project_id}/
      assets/
        original_email.msg
        selected_application_form.docx
        specification.pdf
        supporting_attachment...
```

建议策略：

```text
1. intake 阶段保留原始导入材料，不修改原文件。
2. confirm 后复制或登记到 project assets。
3. 使用 sha256 去重，但不要因为重名覆盖文件。
4. 所有用户上传或邮件附件都要经过安全文件名清洗。
5. 后续如果引入文件版本管理，IntakeAsset 和 FileAsset 都可复用 checksum。
```

### 8.1 IntakeStorage / StorageService 边界

为避免后续每个 task 自己拼路径，Phase 6 应在进入 `.msg` 附件提取和 intake persistence 前建立一个很薄的文件存储边界。

建议在 `TASK_028A` 落地：

```text
IntakeStorage
  - sanitize_filename(original_name)
  - package_root(package_id)
  - source_dir(package_id)
  - attachments_dir(package_id)
  - snapshots_dir(package_id)
  - copy_source_file(package_id, source_path)
  - copy_attachment(package_id, asset_id, source_path, original_name)
  - sha256(path)
```

原则：

```text
1. 所有导入文件先复制到受控 data/intake。
2. 不覆盖同名文件。
3. 不让业务 service 散落硬编码路径。
4. confirm 到 Project assets 时复用同一套安全文件名和 checksum 逻辑。
```

---

## 9. Application Form Candidate Detection

系统应自动给附件打候选分，但不应绕过人工选择。

规则草案：

```text
.docx + 文档内容包含 Laboratory Testing Request        +40
.docx + 文档内容包含 SECTION 1 TO BE COMPLETED          +30
.docx + footer/header 包含 Form No. E-3718              +30
.docx + 文件名包含 request / application / form          +10
.docx + 能解析出 requested_by / sample table             +20
.pdf  + 文件名包含 GS / spec / specification             -> specification
.jpg/.png + content_id 或文件名类似 image003             -> inline_image
其他附件                                                   -> supporting_attachment / unknown
```

输出：

```text
asset_role
candidate_score
candidate_reasons[]
```

UI 只显示推荐，不自动创建项目。

---

## 10. 建议 API 合同

### 10.1 导入入口

```text
POST /api/intake-packages/import
```

根据文件类型分流：

```text
.msg  -> Outlook email package
.docx -> Direct Word application form package
其他  -> supporting package / rejected with message
```

### 10.2 Package 查询

```text
GET /api/intake-packages
GET /api/intake-packages/{package_id}
GET /api/intake-packages/{package_id}/assets
```

### 10.3 选择申请单

```text
POST /api/intake-packages/{package_id}/assets/{asset_id}/select-application-form
```

行为：

```text
1. 将该 IntakeAsset 标记为 selected_application_form。
2. 调用 Word parser 生成 draft。
3. 创建 IntakeCase。
4. 返回 case_id。
```

### 10.4 Case Review

```text
GET   /api/intake-cases/{case_id}
PATCH /api/intake-cases/{case_id}/draft
POST  /api/intake-cases/{case_id}/confirm
POST  /api/intake-cases/{case_id}/reject
```

确认动作返回：

```json
{
  "case_id": "...",
  "package_id": "...",
  "project_id": "...",
  "application_form_id": "...",
  "status": "confirmed"
}
```

### 10.5 兼容现有接口

保留现有接口：

```text
POST /api/projects/{project_id}/application-form
POST /api/application-forms/{application_form_id}/precheck/run
```

但新流程应优先从 Intake confirm 创建 ApplicationForm。

---

## 11. Parser 最小加固范围

Phase 6 不做“无限泛化 parser”，只解决真实样本中已暴露的问题：

1. 读取 Word header/footer。
2. 从 footer 中识别：`Form No. E-3718`、`Rev F/Rev H`、`Reference doc.`、`GS-03-008`。
3. 支持同一单元格内的 `Label: value`。
4. 支持相邻单元格 label/value，但跳过合并单元格重复值。
5. 支持样品表别名：
   - `Part Number / Revision`
   - `Traceability / Manufacturing Lot Info`
   - `Contact Base Material`
   - `Contact Plating`
   - `Contact Lubricant`
   - `Housing Material`
   - `Quantity`
6. 对每个字段输出 confidence：`high | medium | low | missing`。
7. 输出 parser warnings，例如：
   - 字段疑似错位。
   - 表格重复或合并单元格干扰。
   - 值来自 footer/header。
   - 样品表头部分识别。
   - 日期与邮件日期差距异常。
8. 支持 requested testing 区域中 `Tests to be Performed` 与 `Applicable Specifications` 的成对提取。

Parser 输出不得直接落到 ApplicationForm / SampleInfo，只能进入 IntakeDraft。

---

## 12. Frontend UX 范围

### 12.1 导航

左侧导航建议：

```text
Projects
Intake
Precheck
LTR
Folder
Settings
```

### 12.2 Intake Inbox 页面

路径：

```text
/intake
```

功能：

```text
1. Import Outlook Email (.msg)
2. Import Application Form (.docx)
3. Package list
4. Status filter
5. Search by subject / sender / file name
```

列表字段：

```text
导入时间 | 来源类型 | 主题/文件名 | 发件人 | 附件数 | 申请单候选数 | 状态 | 操作
```

### 12.3 Intake Package Detail 页面

路径：

```text
/intake/packages/{package_id}
```

布局：

```text
[邮件信息]
Subject
Sender
Recipients / CC
Received Time
Body Preview

[附件列表]
文件名 | 类型 | 大小 | 系统判断 | 候选分 | 操作

操作：
- 选择为申请单
- 标记为规格书
- 标记为支撑附件
- 忽略
- 预览 / 下载
```

### 12.4 Intake Case Review 页面

路径：

```text
/intake/cases/{case_id}
```

布局：

```text
[基础信息 Review]
Requested By
Phone
Date
Email
Business Unit
Mfg Site
Project #
Requested Completion Date

[样品信息 Review]
Product Name
Part Number
Traceability / Lot
Contact Base Material
Contact Plating
Contact Lubricant
Housing Material
Quantity

[测试需求 Review]
Tests to be Performed
Applicable Specification
Email Body Reference
Supporting Attachments

[系统提示]
Parser warnings
Low-confidence fields
Attachment summary
Date mismatch warning

[动作]
Save Draft
Confirm And Create Project
Reject
```

确认后跳转：

```text
/projects/{project_id}
```

---

## 13. Attachment-Aware Precheck Bridge

当前 PrecheckEngine 已有 `registered_attachments` 的概念，但上层 service 没有把 Intake/Project 附件传入。Phase 6 应补齐这个桥。

目标：

```text
如果 requested testing 或 email body 中出现 see attachment / refer to attachment / 依附件，
且 IntakePackage 或 Project 已登记 supporting attachment / specification，
则不再报 attachment missing warning。
```

建议数据来源：

```text
1. selected_application_form
2. specification assets
3. supporting_attachment assets
4. email body text
```

Phase 6 只做最小桥接，不展开复杂规则库。完整规则扩展放到 6D / Phase 8。

---

## 14. 任务拆分

### TASK_025 — Phase 6 Scope Revision And Board Activation

目标：正式打开 Phase 6，并把范围修订为真实业务入口。

更新 Phase 6 名称：

```text
Phase 6A - Outlook Email Package Intake, Application Form Selection And Human Confirmation
```

验收：

- `docs/task_board.md` 当前阶段改为 Phase 6A。
- 新增 / 更新 Phase 6 实施计划文档。
- 明确入口包括 `.msg` 邮件导入和直接 `.docx` 申请单导入。
- 明确一份申请单创建一个项目。
- 明确 OfficeFacade 为 Phase 6 基础设施边界。
- 只激活 TASK_026，不直接编码后续任务。

### TASK_026 — Office Integration Boundary

目标：建立 OfficeFacade / Office gateway 基础边界。

新增：

```text
backend/infrastructure/office/
  __init__.py
  office_facade.py
  office_lifecycle.py
  outlook_msg_gateway.py
  word_document_gateway.py
  excel_workbook_gateway.py
  models.py
```

验收：

- application/api/frontend 不直接 import win32com。
- application/api/frontend 不直接 import python-docx。
- 所有 Office 文件读取从 gateway 进入。
- OfficeFacade 仅负责读取、提取、分类，不负责创建项目。
- 单元测试覆盖 WordDocumentSnapshot 和基础 file classification。

### TASK_027A — Outlook `.msg` Source Import And Minimal Metadata

目标：实现 `.msg` 原文件导入和最小 metadata 读取；失败时保留原文件并返回明确错误。

输出：

```text
ImportedMailPackage
  subject
  sender_name
  sender_email
  recipients
  cc
  sent_at / received_at
  body_text
  attachments[]  # 本任务可为空或仅保留占位，不要求真实提取
```

验收：

- 能复制 `.msg` 原文件到 `data/intake/{package_id}/source/`。
- 能读取 subject / sender / body preview 的最小集合；如果解析库不支持某个真实样本，必须保留原文件并给出明确错误。
- 不创建 Project。
- 不要求附件提取。

### TASK_027B — Outlook `.msg` Attachment Extraction

目标：在 `TASK_027A` 基础上提取附件并形成基础 asset 清单。

验收：

- 能提取附件到 `data/intake/{package_id}/attachments/`。
- 能识别 docx / pdf / jpg/png / xlsx / unknown 等基础类型。
- 能记录原始文件名、扩展名、size、sha256。
- 不自动选择申请单。
- 不创建 Project。

### TASK_027C — Real `.msg` Sample Compatibility

目标：用真实 `.msg` 样本验证编码、嵌入附件、签名图片、OLE 差异等兼容问题。

验收：

- 至少一个真实样本可导入并形成附件清单。
- 失败样本有明确错误和保留策略。
- 不扩大到 Outlook inbox 自动扫描。

### TASK_028A — Intake Storage Boundary

目标：建立受控 `data/intake/{package_id}` 文件存储边界，避免路径逻辑散落。

验收：

- 提供安全文件名清洗。
- 提供 package/source/attachments/snapshots 目录解析。
- 提供 copy + sha256 helper。
- 不写数据库。

### TASK_028B — IntakePackage / IntakeAsset / IntakeCase Storage

目标：新增 intake domain + SQLAlchemy + repositories。

新增表：

```text
intake_packages
intake_assets
intake_cases
intake_drafts
```

验收：

- 新表可由 init_db 创建。
- repository tests 覆盖 create/get/list/update。
- 不破坏现有 Project/FileAsset 语义。
- `.msg` 导入后能保存 package + assets metadata。
- 直接 `.docx` 导入后也能保存 package + selected form asset metadata。

### TASK_029 — Application Form Candidate Detection

目标：对邮件附件进行候选识别和打分。

验收：

- Word 申请单能标记为 `application_form_candidate`。
- PDF 规格书能标记为 `specification`。
- 邮件签名图片能标记为 `inline_image` 或 `ignored`。
- 输出 candidate_score 和 candidate_reasons。
- 多个候选时不自动选择，必须由用户确认。

### TASK_030 — Form Selection And Draft Creation

目标：用户选择某个附件作为申请单后，创建 IntakeCase 并生成 IntakeDraft。

流程：

```text
selected IntakeAsset
  -> WordDocumentGateway.read_word_document
  -> ApplicationFormParser.parse
  -> IntakeDraft
  -> IntakeCase(status = needs_review)
```

验收：

- 一封邮件可以创建多个 IntakeCase。
- 每个 IntakeCase 对应一份 selected application form。
- parser 输出 confidence/warnings。
- draft 可被 PATCH 修改。
- 不创建 Project，直到 confirm。

### TASK_031A — Intake Inbox Frontend UX

目标：激活 Intake 导航，提供 Inbox 和导入入口。

验收：

- 用户能导入 `.msg`。
- 用户能导入 `.docx` 直接申请单。
- 用户能看到 package list。
- 支持按 subject / sender / file name 搜索。
- 不实现 case review 表单。

### TASK_031B — Intake Package Detail Frontend UX

目标：提供邮件信息和附件列表页面。

验收：

- 用户能看到邮件信息和附件列表。
- 用户能看到系统推荐的申请单候选。
- 用户能人工选择申请单。
- 不实现完整 draft editing。

### TASK_031C — Intake Case Review Frontend UX

目标：提供 draft review / edit / confirm 页面。

验收：

- 用户能看到 parser warnings 和 low-confidence 字段。
- 用户能修改字段/样品行。
- 用户点击 Confirm 后进入 project workbench。

### TASK_032 — Confirm Intake Case To Project

目标：人工确认后才真正创建项目数据。

confirm 后创建：

```text
Project
ApplicationForm
SampleInfo
FileAsset
```

需要登记为 Project FileAsset 的内容：

```text
原始 .msg
选中的申请单 docx
规格书 PDF
其他 supporting attachments
```

验收：

- Confirm 前没有 Project。
- Confirm 后生成 Project 并跳转到 Project Workbench。
- ApplicationForm / SampleInfo 来自人工确认后的 draft，而不是 parser raw output。
- IntakeCase 记录 confirmed_project_id。
- 同一封邮件多个 IntakeCase 可以分别 confirm 成多个 Project。

### TASK_033 — Direct Word Application Form Import

目标：支持绕过邮件，直接导入 Word 申请单开启项目草稿。

内部流程：

```text
.docx upload
  -> IntakePackage(source_type = direct_application_form)
  -> IntakeAsset(role = selected_application_form)
  -> IntakeCase
  -> IntakeDraft
  -> Review UI
  -> Confirm Project
```

验收：

- 直接上传 `.docx` 不走旧的 project-scoped upload 入口。
- 直接申请单和邮件申请单使用同一个 review / confirm 流程。
- 后续 Precheck/LTR/Folder 与邮件入口一致。

### TASK_034 — Attachment-Aware Precheck Bridge

目标：把 Intake / Project attachments 连接到 PrecheckEngine 的 `registered_attachments`。

验收：

- 如果 requested testing 或 email body 包含附件引用，且附件已登记，不再误报缺失附件。
- 如果无附件，仍保留 warning。
- API 和 unit tests 覆盖。
- 不扩展大规模规则库。

### TASK_035 — Phase 6 Validation And Docs Sync

目标：收尾 Phase 6 文档、测试、手动 smoke checklist。

验收：

- backend pytest 通过。
- frontend build 通过。
- manual frontend smoke checklist 更新。
- `docs/task_board.md` 标记 Phase 6A 完成或准确 blocked。
- 给出 Phase 7 推荐。

---



## 15. 明确不做

Phase 6 不做：

- Outlook COM 自动读取邮箱。
- Outlook Inbox 自动扫描。
- 自动标记邮件已处理。
- 自动发送邮件。
- Matrix。
- Test Record。
- Report。
- AI Review。
- Excel 测试结果导入。
- 多用户权限或 LAN 部署。
- 完整 folder template registry UX。
- 大规模 precheck rule expansion。
- 复杂迁移系统；当前仍可使用 init_db + SQLite dev flow。

---

## 16. Phase 6 完成定义

Phase 6 完成时，系统应支持以下手动业务闭环：

```text
1. 用户导入一封 Outlook .msg 邮件。
2. 系统显示邮件主题、发件人、正文预览和附件列表。
3. 系统推荐申请单候选和规格书附件。
4. 用户选择一份 Word 申请单。
5. 系统解析申请单并生成可编辑草稿。
6. 用户修正字段和样品行。
7. 用户点击 Confirm。
8. 系统创建 Project + ApplicationForm + SampleInfo。
9. 系统登记原始邮件、申请单、规格书和支撑附件。
10. 用户进入 Project Workbench 并继续 Precheck / LTR / Folder。
```

同时支持：

```text
用户直接导入 Word 申请单，也能进入同一个 Review / Confirm / Create Project 流程。
```

---

## 17. Phase 7 推荐方向

Phase 6 完成后，推荐 Phase 7 二选一：

### 方向 A：完整 Phase 6B Parser Hardening

适合在真实样本增加后做：

```text
1. 更多申请单版本兼容。
2. 更强表格结构识别。
3. 字段冲突检测。
4. 多语言 / 中英文混合 label。
5. parser fixture library。
```

### 方向 B：Phase 6C Folder Template Configuration UX

适合在 intake 稳定后做：

```text
1. folder template registry。
2. LTR/project naming preview。
3. 客户/BU 维度配置。
4. 生成路径可视化。
```

不建议 Phase 7 直接做 6D 大规模规则扩展，除非 parser 和 intake confirmation 已经稳定。

---

## 18. 推荐批准语

可以把下一条给 Codex / AI 工具：

```text
Read AGENTS.md first, then docs/task_board.md.

We are revising Phase 6 based on the real business workflow:
projects usually start from an Outlook email containing one or more attachments.
One selected application form creates one project.
Sometimes users directly import a Word application form without an email.

Approve and start only TASK_025:
Phase 6 Scope Revision for Outlook Email Package Intake,
Application Form Selection,
Human Confirmation,
Direct Word Form Import,
and OfficeFacade Boundary.

Do not implement Matrix, Report, Excel result ingestion, AI review,
Outlook inbox auto scan, email sending, or folder template UX.

Before coding, state:
- current phase
- current active task ID
- why this task is allowed now

After finishing TASK_025, update docs/task_board.md and stop.
```

---

## 19. TASK_026 推荐启动提示词

TASK_025 完成并更新 task board 后，可以启动 TASK_026：

```text
Read AGENTS.md first, then docs/task_board.md and docs/ConnLab_Phase6_Implementation_Plan.md.

Start TASK_026 - Office Integration Boundary only.

Implement the infrastructure boundary for Office-related reading/extraction:
- backend/infrastructure/office/office_facade.py
- backend/infrastructure/office/office_lifecycle.py
- backend/infrastructure/office/outlook_msg_gateway.py
- backend/infrastructure/office/word_document_gateway.py
- backend/infrastructure/office/excel_workbook_gateway.py
- backend/infrastructure/office/models.py

Do not create Project, ApplicationForm, SampleInfo, IntakePackage tables, UI, Matrix, Report, or Outlook COM automation.

Use file-level parsing first. COM fallback must be centralized and must not touch user-opened Office instances.

Add focused unit tests for file classification and WordDocumentSnapshot extraction.
Update docs/task_board.md when done and stop.
```

---

## 20 Server Upgrade Readiness Principles

虽然当前 ConnLab 仍以本地单人使用为主，但 Phase 6 之后的核心业务模型、API、文件管理和 Office 集成边界，必须按照未来可升级为局域网服务器 / 多人在线系统的方向设计。

本阶段不实现服务器部署、多用户登录、权限系统或在线协同，但必须避免把系统写死为单机专用程序。

原则如下：

1. 所有业务能力必须从 API / Application Service 进入，禁止前端或 UI 直接操作数据库、Office、项目目录或业务文件。
2. 所有 Office 操作必须统一走 OfficeFacade，禁止 Intake、Report、Matrix、Test Record、Precheck 等模块各自直接调用 Word、Excel 或 Outlook。
3. 所有文件必须先进入受控 StorageService / AssetRepository 管理，禁止业务代码散落硬编码本地路径。
4. 所有数据库访问必须走 Repository，不允许业务层依赖 SQLite 专有行为。
5. SQLite 只作为 local desktop 模式数据库；未来 lan_server / web_server 模式应可切换到 PostgreSQL、MySQL 或 SQL Server。
6. 所有确认类动作必须预留 actor、timestamp 和 audit log 扩展点，例如选择申请单、修改草稿、确认项目、申请 LTR、生成文件夹。
7. 新增业务表应尽量预留 created_at、updated_at、created_by、updated_by、version 字段。
8. Phase 6 不实现权限系统，但不能在业务逻辑中假设永远只有一个用户。
9. Phase 6 不实现服务器部署，但后端 service 应尽量保持无状态，避免依赖某个前端页面或某个本地窗口状态。
10. 解析结果永远先进入 draft，经人工确认后才成为正式 Project / ApplicationForm / SampleInfo 数据。

---

## 20. Future Server Upgrade Readiness

ConnLab 当前阶段仍然按照 local desktop / local web app 模式交付，即单机、本地数据、本地文件、本地 Office 环境。但系统目标上应保留未来升级为局域网服务器和多人在线系统的能力。

推荐演进路线：

```text
阶段 1：Local Desktop / Local Web App
- 单人使用
- SQLite
- 本地 data/ 文件夹
- 本机 OfficeFacade
- 手动导入 .msg / .docx

阶段 2：LAN Server
- 多人浏览器访问
- PostgreSQL / MySQL / SQL Server
- 共享文件存储
- 用户、角色、权限
- 操作日志
- 后台任务

阶段 3：Full LIMS Server
- 多实验室 / 多部门
- 审批流
- 报告在线协作
- 队列化任务处理
- 集中备份
- SSO / LDAP / OAuth
