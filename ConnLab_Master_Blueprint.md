# ConnLab Master Blueprint and AI Coding Guide

本文件是打包版，便于一次性提供给 AI 编程工具。实际开发时建议优先使用拆分文档。



---

<!-- Source: AGENTS.md -->


# AGENTS.md - ConnLab AI Coding Rules

本文件是给 Codex、IDE AI、自动化编码代理和人工开发者的最高优先级工程规则。

## 1. 项目定位

ConnLab 是面向电子连接器实验室的离线 Windows 本地工作台。

当前 MVP 目标：

1. 申请单预审 Precheck
2. LTR 单号申请/登记
3. 项目文件夹自动生成

当前不是完整 LIMS，不做完整 Matrix，不做完整报告生成，不做 AI 审核。

## 2. 技术栈锁定

后端：

- Python 3.11+
- FastAPI
- SQLite
- SQLModel 或 SQLAlchemy 2.x（二选一，默认 SQLModel）
- pydantic
- python-docx
- pywin32
- openpyxl
- pytest

前端：

- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui 可选

桌面壳：

- PyWebView

运行环境：

- Windows
- 离线
- Microsoft Office
- 公司内部单机使用，未来可升级局域网

## 3. 强制架构规则

### 3.1 依赖方向

只允许：

```text
frontend -> backend/api -> application -> domain
                           application -> infrastructure
```

禁止：

```text
domain -> infrastructure
domain -> api
domain -> frontend
infrastructure -> frontend
ui/frontend -> Office COM
```

### 3.2 UI 规则

- UI 不允许直接操作 Word/Excel/Outlook。
- UI 不允许直接复制项目文件夹。
- UI 不允许直接写 SQLite。
- UI 只能调用 API。
- UI 不允许通过新增工具按钮绕过项目生命周期。

### 3.3 Office 规则

所有 Office 操作必须通过：

```text
backend/infrastructure/office/
```

禁止在 application、domain、api、frontend 中直接调用 pywin32 COM。

### 3.4 文件大小规则

- 单个 Python 文件不超过 500 行。
- 单个 Service 类不超过 400 行。
- 单个 React 组件文件不超过 400 行。
- 超过阈值必须拆分。
- 禁止创建“万能 service”。

### 3.5 功能准入规则

新增任何功能前必须先回答：

1. 属于哪个 Project 阶段？
2. 输入是什么？
3. 输出是什么？
4. 改变哪个领域对象？
5. 是否影响报告？
6. 是否需要校验？
7. 是否属于 MVP？

如果不属于 MVP，默认不实现，只留接口或 TODO。

## 4. 当前 MVP 禁止事项

禁止实现：

- 完整 Matrix 自动生成
- 完整 Test Record 自动生成
- Excel 测试数据导入
- 图片自动插入报告
- Word 报告自动生成
- AI 报告审核
- 多人协作
- 权限系统
- 局域网服务部署
- 云端数据库

这些是后续阶段，不得在 MVP 中提前展开。

## 5. 目录结构必须遵守

```text
connlab/
├── backend/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   ├── modules/
│   └── api/
├── frontend/
├── apps/
│   └── desktop/
├── data/
├── config/
├── templates/
├── logs/
└── tests/
```

## 6. 开发前必须检查

在写代码前，AI 必须说明：

```text
当前任务编号：
当前阶段：
将修改/创建的文件：
不做哪些内容：
验收方式：
```

## 7. 每次任务完成必须输出

```text
完成内容：
修改文件：
测试命令：
是否触碰非 MVP 范围：
后续建议：
```

## 8. 测试要求

每个后端 use case 至少有单元测试。  
每个 parser 至少用一个真实或简化 fixture 测试。  
每个 API 至少有 happy path 和 error path 测试。

优先测试：

```text
ApplicationFormParser
PrecheckEngine
ProjectService
LtrService
ProjectFolderService
```

## 9. 数据原则

Word、Excel、图片、附件都是输入/输出文件，不是主数据源。

主数据应保存在 SQLite 中：

- Project
- ApplicationForm
- SampleInfo
- PrecheckResult
- PrecheckIssue
- LtrRecord
- FolderRecord
- FileAsset

## 10. 最高原则

ConnLab 的第一版只打通：

```text
申请单 -> 预审 -> LTR -> 项目文件夹
```

任何偏离这条链路的实现都必须停止。



---

<!-- Source: docs/00_CONN_LAB_BLUEPRINT.md -->


# 00 ConnLab 系统蓝图

## 1. 系统定位

ConnLab 是面向电子连接器实验室的本地化项目启动、预审、LTR、项目文件夹、测试计划、测试数据、报告生成与报告校验工作台。

MVP 只做项目启动阶段：

```text
申请单 -> 预审 -> LTR -> 项目文件夹
```

## 2. 为什么不是重构旧系统

旧系统从 LTR 小工具开始，逐步加入项目文件夹、Matrix、测试记录、报告初始化、设备表、费用表、客户报告转换等功能。它的失败原因不是单个模块差，而是没有统一的 Project 生命周期和领域模型。

ConnLab 不继承旧架构，只继承经验：

保留：

- OfficeFacade / Word / Excel 处理经验
- LTR 编号关联经验
- 文件夹模板经验
- Matrix / Record / Report 的业务规则经验
- 报告校验和审核痛点

丢弃：

- 旧 MainWindow
- 菜单工具栏式 UI
- Matrix 作为系统中心
- 按功能堆按钮的设计
- UI 直接驱动业务逻辑
- Word/Excel 作为事实数据源

## 3. 长期系统主线

```text
Requirement Source
  - 申请单
  - 邮件
  - 微信沟通摘要
  - 产品规格书
  - EIA-364/UL/IEC 标准
  - 客户表格
  - 历史报告
      ↓
Project
      ↓
Precheck / Validation
      ↓
MatrixPlan
      ↓
TestRecord
      ↓
TestResult + TestAsset
      ↓
ReportDataset
      ↓
Word/PDF Report
```

## 4. 关键定位

- Project 是核心。
- 申请单是项目起点。
- Precheck 是第一道质量门。
- Matrix 是计划，不是系统核心。
- Word/Excel 是输入输出，不是主数据源。
- 报告是结构化数据的导出物。
- 图片、Excel、附件都是项目资产。
- AI 是辅助审核，不是最终判定。

## 5. 产品模块

```text
ConnLab Intake      申请单/邮件/附件导入
ConnLab Precheck    申请单预审
ConnLab LTR         LTR 编号申请/登记
ConnLab Folder      项目文件夹生成
ConnLab Plan        Matrix / 测试计划
ConnLab Record      测试记录
ConnLab Result      测试数据
ConnLab Asset       图片/附件资产
ConnLab Report      报告工作台
ConnLab Audit       报告校验
ConnLab Knowledge   标准/规格书/历史报告知识库
```

MVP 仅实现 Intake / Precheck / LTR / Folder 的最小闭环。



---

<!-- Source: docs/01_MVP_SCOPE_AND_ROADMAP.md -->


# 01 MVP 范围与路线图

## 1. MVP 目标

第一版只解决三个问题：

1. 申请单预审 Precheck
2. 项目文件夹自动生成
3. LTR 单号申请/登记

## 2. MVP 主流程

```text
导入申请单 Word
  ↓
解析申请单关键字段
  ↓
执行 Precheck
  ↓
显示问题清单
  ↓
人工确认
  ↓
登记/申请 LTR
  ↓
选择项目文件夹模板
  ↓
生成项目文件夹
  ↓
保存项目记录
```

## 3. MVP 不做内容

不做：

- 完整 Matrix 自动生成
- 完整 Test Record 自动生成
- Excel 测试数据解析
- 图片资产管理
- 报告自动生成
- 报告自动校验
- AI 接口
- 多人协作
- 权限
- 局域网部署

## 4. 版本路线

### v1.0 MVP

```text
申请单 -> 预审 -> LTR -> 文件夹
```

### v1.5

```text
规格书/附件登记
基础 MatrixPlan 数据结构
```

### v2.0

```text
MatrixPlan -> TestRecord 自动生成
```

### v2.5

```text
Excel 测试数据导入
TestResult 结构化
```

### v3.0

```text
图片资产 TestAsset
自动插入报告
```

### v3.5

```text
ReportDataset
Word 报告生成
```

### v4.0

```text
ReportAudit 规则审核
```

### v5.0

```text
KnowledgeBase + AI 辅助审核
```

### v6.0

```text
局域网版 / 轻量 LIMS
```

## 5. MVP 验收标准

上线前必须满足：

1. 能导入真实申请单。
2. 能提取 DL 编号、申请人、项目号、产品、样品信息、测试描述、外包字段。
3. 能检查表单版本、必填字段、样品信息、测试描述、附件引用、Estimated Completion Date。
4. 能显示 error/warning/info。
5. 能人工确认或忽略问题。
6. 能登记 LTR 编号并绑定 Project。
7. 能根据模板生成项目文件夹。
8. 能重新打开项目。
9. 普通工程师不懂代码也能使用。



---

<!-- Source: docs/02_ARCHITECTURE_RULES.md -->


# 02 架构规则与红线

## 1. 总原则

ConnLab 必须是“项目生命周期系统”，不是“工具集合”。

## 2. 分层

```text
frontend
  ↓
api
  ↓
application
  ↓
domain
  ↓
infrastructure
```

application 可以调用 infrastructure。  
domain 不依赖任何外部技术。

## 3. 禁止事项

禁止：

1. UI 直接操作 Office。
2. UI 直接复制文件夹。
3. UI 直接写数据库。
4. 业务逻辑写在按钮事件里。
5. Office COM 出现在 application/domain/api/frontend。
6. 新功能直接加独立工具按钮。
7. Matrix 成为系统中心。
8. Word/Excel 成为唯一事实数据源。
9. 单个 Service 变成万能类。
10. MVP 阶段提前实现后续大功能。

## 4. 必须遵守

1. 所有功能挂到 Project 生命周期。
2. 所有输入文件都登记为 FileAsset。
3. 所有预审问题用 PrecheckIssue 表达。
4. 所有 Office 操作集中到 infrastructure/office。
5. 所有文件复制/模板替换集中到 infrastructure/templates 或 modules/folder。
6. 所有数据库访问通过 repository。
7. 所有 use case 放在 application。
8. 所有 API 只调用 application service。

## 5. 文件规模

- Python 文件 <= 500 行
- Service 类 <= 400 行
- React 组件 <= 400 行
- 单个函数建议 <= 60 行
- 复杂逻辑必须拆 helper 或 policy

## 6. 新功能准入清单

新增功能前必须回答：

```text
功能名称：
所属阶段：
输入：
输出：
修改的领域对象：
是否属于 MVP：
是否需要 Office：
是否需要数据库：
是否需要校验：
不做事项：
```

未回答清楚，不写代码。



---

<!-- Source: docs/03_DOMAIN_MODEL.md -->


# 03 领域模型

## 1. MVP 领域对象

### Project

```python
Project:
    id: str
    dl_number: str | None
    title: str
    product_name: str | None
    requestor: str | None
    business_unit: str | None
    status: ProjectStatus
    root_folder: str | None
    created_at: datetime
    updated_at: datetime
```

状态：

```text
Draft
PrecheckRequired
PrecheckPassed
LtrRequested
FolderCreated
Archived
```

### ApplicationForm

```python
ApplicationForm:
    id: str
    project_id: str
    source_file_id: str
    form_no: str | None
    form_rev: str | None
    reference_doc: str | None
    lab_test_request_number: str | None
    requested_by: str | None
    phone: str | None
    request_date: date | None
    email: str | None
    business_unit: str | None
    manufacturing_site: str | None
    project_no: str | None
    results_format: str | None
    requested_completion_date: date | None
    description_of_requested_testing: str | None
    additional_information: str | None
    subcontract_allowed: bool | None
    estimated_completion_date: date | None
    extracted_at: datetime
```

### SampleInfo

```python
SampleInfo:
    id: str
    application_form_id: str
    product_name: str | None
    part_number_revision: str | None
    traceability_lot: str | None
    contact_base_material: str | None
    contact_plating: str | None
    contact_lubricant: str | None
    housing_material: str | None
    quantity: str | None
```

### PrecheckResult

```python
PrecheckResult:
    id: str
    project_id: str
    application_form_id: str
    status: "passed" | "warning" | "failed"
    checked_at: datetime
    checker_version: str
```

### PrecheckIssue

```python
PrecheckIssue:
    id: str
    result_id: str
    level: "error" | "warning" | "info"
    category: str
    field: str | None
    message: str
    expected: str | None
    actual: str | None
    suggestion: str | None
    resolved: bool
    resolved_reason: str | None
```

### LtrRecord

```python
LtrRecord:
    id: str
    project_id: str
    ltr_number: str
    status: "draft" | "requested" | "approved" | "cancelled"
    requested_by: str | None
    requested_date: date | None
    application_form_file_id: str | None
    notes: str | None
```

### FolderRecord

```python
FolderRecord:
    id: str
    project_id: str
    template_id: str
    root_path: str
    created_at: datetime
    created_by: str | None
    generated_files_json: str
```

### FileAsset

```python
FileAsset:
    id: str
    project_id: str | None
    file_type: str
    original_name: str
    path: str
    checksum: str | None
    created_at: datetime
```

## 2. 后续扩展领域对象

### MatrixPlan

```python
MatrixPlan:
    id
    project_id
    groups: list[TestGroup]
```

### TestGroup

```python
TestGroup:
    group_no
    sample_quantity
    steps: list[TestStep]
```

### TestStep

```python
TestStep:
    step_no
    test_item
    method
    condition
    requirement
    source_reference
```

### TestResult

```python
TestResult:
    project_id
    group_no
    step_no
    test_item
    raw_values
    statistics
    requirement
    pass_fail
    source_file_id
```

### TestAsset

```python
TestAsset:
    project_id
    group_no
    test_item
    asset_type
    file_path
    caption
    figure_no
```

### LabReport

```python
LabReport:
    project_id
    metadata
    sections
    appendices
    assets
    status
```

这些扩展对象现在只建文档，不在 MVP 实现。



---

<!-- Source: docs/04_MODULE_BOUNDARIES.md -->


# 04 模块边界

## 1. backend/domain

职责：

- 定义领域对象
- 定义 enum
- 定义纯业务 value object

禁止：

- 访问数据库
- 访问 Office
- 访问文件系统
- 导入 FastAPI
- 导入 React/前端概念

## 2. backend/application

职责：

- 编排 use case
- 调用 repository
- 调用 infrastructure gateway
- 管理事务边界
- 返回 DTO

主要服务：

```text
ProjectService
ApplicationFormImportService
PrecheckService
LtrService
ProjectFolderService
```

## 3. backend/modules

职责：

- 放具体业务模块内部实现
- Parser、Rule、Policy、Transformer

建议：

```text
modules/intake/ApplicationFormParser
modules/precheck/PrecheckEngine
modules/precheck/rules/*
modules/ltr/LtrNumberPolicy
modules/folder/ProjectFolderPlanner
modules/folder/PlaceholderRenderer
```

## 4. backend/infrastructure

职责：

- SQLite repository
- Office gateway
- 文件系统
- 模板复制
- checksum
- 日志
- AI provider 预留

禁止：

- 把业务判断写在 infrastructure 中
- 让 OfficeGateway 知道 UI

## 5. backend/api

职责：

- REST API
- 请求校验
- 调用 application service
- 错误映射

禁止：

- 业务逻辑
- Office 操作
- 文件复制细节

## 6. frontend

职责：

- 项目列表
- 项目详情
- Precheck 问题展示
- LTR 登记表单
- 文件夹生成预览

禁止：

- 直接读写本地 Office 文件
- 直接操作 SQLite
- 直接执行业务规则



---

<!-- Source: docs/05_API_CONTRACTS.md -->


# 05 API 契约草案

## 1. Project API

### POST /api/projects

创建空项目。

Request:

```json
{
  "title": "EK550A Qualification",
  "product_name": "EK550",
  "requestor": "Fu Yang"
}
```

Response:

```json
{
  "project_id": "uuid",
  "status": "Draft"
}
```

### GET /api/projects

返回项目列表。

### GET /api/projects/{project_id}

返回项目详情。

## 2. Application Form API

### POST /api/projects/{project_id}/application-form/import

导入申请单。

Request: multipart/form-data

Response:

```json
{
  "application_form_id": "uuid",
  "extracted_fields": {
    "lab_test_request_number": "DL-2025-09-054",
    "requested_by": "Fu Yang"
  }
}
```

## 3. Precheck API

### POST /api/projects/{project_id}/precheck/run

执行预审。

Response:

```json
{
  "result_id": "uuid",
  "status": "warning",
  "issue_count": 2
}
```

### GET /api/projects/{project_id}/precheck/latest

返回最近一次预审结果。

### PATCH /api/precheck/issues/{issue_id}

人工标记问题已确认/已忽略。

Request:

```json
{
  "resolved": true,
  "resolved_reason": "已人工确认附件存在于项目文件夹。"
}
```

## 4. LTR API

### POST /api/projects/{project_id}/ltr

登记 LTR。

Request:

```json
{
  "ltr_number": "DL-2025-09-054",
  "requested_date": "2025-09-11",
  "notes": ""
}
```

## 5. Folder API

### POST /api/projects/{project_id}/folder/preview

预览文件夹生成计划。

### POST /api/projects/{project_id}/folder/create

根据模板创建项目文件夹。

Request:

```json
{
  "template_id": "default_dl_project",
  "target_root": "D:/ConnLab/Projects"
}
```

Response:

```json
{
  "folder_record_id": "uuid",
  "root_path": "D:/ConnLab/Projects/DL-2025-09-054 EK550A"
}
```



---

<!-- Source: docs/06_UI_WORKBENCH_SPEC.md -->


# 06 UI 工作台设计

## 1. 设计原则

用户不是程序员。  
UI 必须告诉用户“下一步做什么”，而不是展示一堆工具按钮。

## 2. 主布局

```text
┌────────────────────────────────────────┐
│ ConnLab   搜索项目   新建项目   设置     │
├───────────────┬────────────────────────┤
│ 项目列表       │ 当前项目工作台          │
│               │                        │
│ DL-2025-09... │ 状态卡片                │
│ DL-2025-06... │ 任务卡片                │
└───────────────┴────────────────────────┘
```

## 3. 项目卡片

显示：

- DL 编号
- 项目名称
- 申请人
- 当前状态
- 最后更新日期
- 是否有未解决 Precheck issue

## 4. 项目工作台

任务卡片：

```text
1. 申请单预审
2. LTR 单号
3. 项目文件夹
4. Matrix 计划（后续）
5. 测试记录（后续）
6. 报告工作台（后续）
```

MVP 只有前三个可用，后续显示 disabled 或 Coming Later。

## 5. Precheck 页面

区域：

1. 申请单基础信息
2. 样品信息表
3. 测试需求描述
4. 实验室填写区
5. 预审问题列表
6. 操作按钮

按钮：

```text
重新解析
运行预审
标记已确认
导出预审报告
```

## 6. LTR 页面

字段：

- LTR 编号
- 申请日期
- 申请人
- 关联申请单
- 备注

按钮：

```text
保存 LTR
打开申请单
```

## 7. 文件夹页面

区域：

- 模板选择
- 目标路径
- 生成预览树
- 占位符替换预览
- 创建按钮

创建前必须显示预览，不允许直接复制。



---

<!-- Source: docs/07_PRECHECK_ENGINE_SPEC.md -->


# 07 PrecheckEngine 设计

## 1. 目标

把人工预审经验转成系统规则，提前发现申请单问题。

## 2. 输入

- ApplicationForm
- SampleInfo[]
- FileAsset[]
- 配置中的表单版本规则
- 配置中的必填字段规则

## 3. 输出

- PrecheckResult
- PrecheckIssue[]

## 4. 规则清单 MVP

### R001 表单版本

检查：

- Form No. 应为 E-3718
- Rev 应为 H
- Reference doc 应存在

等级：

- Form No 错误：error
- Rev 不匹配：warning 或 error，由配置决定
- Reference doc 缺失：warning

### R002 申请人信息完整性

字段：

- Requested By
- Phone
- Date
- Email
- Business Unit
- Mfg. Site
- Project #

缺失时 error。

### R003 样品信息完整性

字段：

- Product Name
- Part Number / Revision
- Traceability / Lot Info
- Contact Base Material
- Contact Plating
- Housing Material
- Quantity

缺失时 warning 或 error。

### R004 Quantity 复杂表达式

如果数量包含：

```text
+
/
,
;
中文说明
```

提示 warning：

```text
样品数量不是单一数字，请确认主样品/备用样品/不同规格样品含义。
```

### R005 测试需求描述为空或模糊

如果 Description of Requested Testing：

- 为空
- 仅写“依附件”
- 仅写“参考附件”
- 没有 Applicable Specification

产生 warning。

### R006 引用附件但未登记

描述中出现：

```text
附件
attached
SOR
spec
表格
matrix
```

但 FileAsset 中没有附件登记，产生 warning。

### R007 外包字段

读取：

```text
Can testing be subcontracted?
```

输出到 ApplicationForm.subcontract_allowed。

### R008 实验室填写区

检查：

- Lab Performing the Tests
- Lab Personnel Assigned
- Date Lab Received Samples
- Estimated Completion Date
- Condition of Samples when Received

Estimated Completion Date 缺失时 warning。

## 5. 规则接口

```python
class PrecheckRule(Protocol):
    rule_id: str
    name: str
    def check(self, context: PrecheckContext) -> list[PrecheckIssue]:
        ...
```

## 6. Engine 伪代码

```python
class PrecheckEngine:
    def __init__(self, rules: list[PrecheckRule]):
        self.rules = rules

    def run(self, context: PrecheckContext) -> PrecheckResult:
        issues = []
        for rule in self.rules:
            issues.extend(rule.check(context))
        return PrecheckResult.from_issues(issues)
```

## 7. 测试要求

每条规则必须有测试：

- 正常情况
- 缺失情况
- 边界情况

必须包含一个真实申请单 fixture 的集成测试。



---

<!-- Source: docs/08_LTR_AND_FOLDER_SPEC.md -->


# 08 LTR 与项目文件夹设计

## 1. LTR 模块 MVP

### 目标

- 登记 LTR 编号
- 绑定 Project
- 保存申请单路径
- 支持历史查询

### 暂不做

- 自动申请 LTR
- 自动登录外部系统
- 自动邮件发送
- LTR 审批流

### LTR 编号校验

默认格式：

```text
DL-YYYY-MM-NNN
```

允许配置。

## 2. 文件夹生成模块 MVP

### 目标

从模板目录生成项目目录。

### 输入

- Project
- LtrRecord
- ApplicationForm
- 模板路径
- 目标根目录

### 输出

- 项目根目录
- FolderRecord
- 生成文件列表

## 3. 推荐项目目录结构

```text
{DL_NUMBER} {PROJECT_NO}/
├── 00_Request/
│   ├── original_application.docx
│   ├── attachments/
│   └── precheck_report.json
├── 01_LTR/
├── 02_Specifications/
│   ├── product_spec/
│   ├── standards/
│   └── customer_requirements/
├── 03_Matrix/
├── 04_Test_Record/
├── 05_Raw_Data/
│   ├── LLCR/
│   ├── IR_DWV/
│   ├── Mechanical/
│   └── Temperature_Rise/
├── 06_Images/
├── 07_Report/
│   ├── draft/
│   ├── review/
│   └── released/
├── 08_Customer_Report/
└── 99_Archive/
```

## 4. 占位符

支持：

```text
{DL_NUMBER}
{PROJECT_NO}
{PRODUCT_NAME}
{REQUESTOR}
{BUSINESS_UNIT}
{DATE}
{YEAR}
{MONTH}
```

## 5. 安全规则

- 创建前必须 preview。
- 如果目标目录存在，不覆盖，除非用户明确选择。
- 文件复制失败必须回滚或记录部分失败。
- 所有生成结果写入 FolderRecord。



---

<!-- Source: docs/09_OFFICE_INTEGRATION_RULES.md -->


# 09 Office 集成规则

## 1. 目标

ConnLab 必须支持 Windows + Office。  
Office 是输入输出工具，不是业务逻辑层。

## 2. Gateway

所有 Office 操作通过：

```text
backend/infrastructure/office/
```

文件：

```text
word_gateway.py
excel_gateway.py
outlook_gateway.py
office_lifecycle.py
```

## 3. Word 处理

MVP 需要：

- 读取申请单 docx
- 提取表格文本
- 提取页脚 Form No / Rev / Reference doc
- 后续支持 doc / pdf

优先：

```text
python-docx -> 解析 docx
pywin32 -> 处理复杂 Word / .doc / header/footer / 格式
```

## 4. Excel 处理

MVP 不处理测试 Excel。  
后续 Result 模块用 openpyxl 解析，必要时用 Excel COM 保留宏和格式。

## 5. COM 生命周期

- 禁止各处单独启动 Word/Excel。
- 必须统一生命周期管理。
- 失败时必须释放 COM。
- 所有 Office 错误写日志。

## 6. 禁止

- application service 直接 import win32com
- frontend 直接调用 Office
- parser 中混入 UI 消息框



---

<!-- Source: docs/10_VALIDATION_AUDIT_AI_EXTENSION.md -->


# 10 Validation / Audit / AI 扩展设计

## 1. 未来目标

先用确定性规则排除数据错误，再用 AI 做语义辅助审核。

## 2. Report Audit 未来检查

- 规格书 requirement 与报告 requirement 是否一致
- Matrix 与 Record 是否一致
- Record 与 TestResult 是否一致
- TestResult 与 Report 正文是否一致
- Pass/Fail 判断是否正确
- 单位是否一致
- 图片编号是否连续
- 表格编号是否连续
- 结论是否与结果冲突

## 3. AuditIssue

```python
AuditIssue:
    level: "error" | "warning" | "suggestion"
    category: "data" | "logic" | "format" | "language"
    location: str
    message: str
    expected: str | None
    actual: str | None
    source: str | None
```

## 4. AIProvider 接口预留

```python
class AIProvider(Protocol):
    def review_text(self, context: AIReviewContext) -> AIReviewResult: ...
    def extract_requirements(self, document: FileAsset) -> list[RequirementCandidate]: ...
    def suggest_report_section(self, context: ReportContext) -> ReportSectionDraft: ...
    def compare_with_old_report(self, current, historical) -> ComparisonResult: ...
```

## 5. AI 使用边界

AI 可以：

- 检查文字描述是否矛盾
- 建议报告语言
- 推荐旧报告片段
- 提取规格书候选要求
- 提醒可能遗漏

AI 不可以：

- 直接决定 Pass/Fail
- 绕过规格书规则
- 自动批准报告
- 修改原始数据

最终判定必须来自：

```text
规格书规则 + 测试数据 + 人工确认
```



---

<!-- Source: docs/11_DEVELOPMENT_TASKS.md -->


# 11 开发任务清单

## Phase 0 项目初始化

### TASK-0001 初始化仓库结构

目标：

- 创建 backend/frontend/apps 结构
- 建立 pyproject.toml
- 建立 package.json
- 建立 README
- 建立 AGENTS.md

不做：

- 不实现业务功能

验收：

- 后端 pytest 可运行
- 前端 npm install 可运行

### TASK-0002 建立配置与日志

目标：

- config/settings.yaml
- logs/
- Python logging

验收：

- 应用启动时写日志
- 配置可读取

## Phase 1 Project 基础

### TASK-0101 建立 SQLite schema

目标：

- projects
- file_assets
- application_forms
- sample_infos
- precheck_results
- precheck_issues
- ltr_records
- folder_records

验收：

- 能创建数据库
- 能插入/查询 Project

### TASK-0102 Project API

目标：

- POST /api/projects
- GET /api/projects
- GET /api/projects/{id}

验收：

- API 测试通过

## Phase 2 申请单解析

### TASK-0201 ApplicationFormParser 骨架

目标：

- 接收 docx path
- 输出 ApplicationFormDraft
- 提取纯文本和表格

验收：

- 能读取真实申请单 fixture

### TASK-0202 提取申请单关键字段

目标：

- DL 编号
- Requested By
- Date
- Email
- Business Unit
- Project #
- Requested Completion Date
- Description
- Additional Information
- Subcontracted
- Section 2

验收：

- 测试 fixture 字段匹配

### TASK-0203 提取 SampleInfo

目标：

- 从 Test Sample Information 表格提取多行样品

验收：

- 能提取至少 3 行样品

## Phase 3 Precheck

### TASK-0301 PrecheckRule 接口

目标：

- 定义 PrecheckContext
- 定义 PrecheckRule
- 定义 PrecheckIssue factory

验收：

- 可注册规则并运行

### TASK-0302 实现 MVP 规则 R001-R008

验收：

- 每条规则至少 2 个测试
- 集成测试能返回 issues

### TASK-0303 Precheck API 和 UI

目标：

- 运行预审
- 显示问题
- 标记 resolved

验收：

- 用户可在 UI 中看到 warning/error

## Phase 4 LTR

### TASK-0401 LTR 模型和 API

目标：

- 登记 LTR
- 查询 LTR

验收：

- 一个项目可绑定 LTR

### TASK-0402 LTR UI

目标：

- LTR 输入表单
- 保存
- 状态显示

## Phase 5 文件夹生成

### TASK-0501 Folder preview

目标：

- 读取模板
- 生成预览树
- 替换占位符预览

### TASK-0502 Folder create

目标：

- 复制模板
- 创建项目文件夹
- 写 FolderRecord
- 复制申请单到 00_Request

验收：

- 实际生成目录
- 不覆盖已有目录

## Phase 6 MVP 封版

### TASK-0601 打包

目标：

- PyWebView + FastAPI + React 本地启动
- Windows 可运行

### TASK-0602 用户文档

目标：

- 快速开始
- 申请单预审操作
- LTR 操作
- 文件夹生成操作



---

<!-- Source: docs/12_CODEX_EXECUTION_GUIDE.md -->


# 12 Codex / IDE AI 执行指南

## 1. 如何让 AI 开始

推荐第一条指令：

```text
请先读取并遵守：
1. AGENTS.md
2. docs/00_CONN_LAB_BLUEPRINT.md
3. docs/01_MVP_SCOPE_AND_ROADMAP.md
4. docs/02_ARCHITECTURE_RULES.md
5. docs/11_DEVELOPMENT_TASKS.md

当前只执行 TASK-0001：初始化仓库结构。
不要实现任何业务功能。
开始前先说明：
- 当前任务编号
- 将创建的目录和文件
- 明确不做内容
- 验收命令
```

## 2. 单任务执行模板

```text
当前任务：TASK-XXXX

请按以下要求执行：
1. 只实现本任务，不扩展范围。
2. 遵守 AGENTS.md。
3. 不实现未激活阶段。
4. 修改前先列出计划。
5. 完成后给出测试命令。
6. 如果发现需要改架构，先停止并说明。
```

## 3. 任务拆分原则

每次只让 AI 做一个 TASK。  
不要一次让 AI 做完整 MVP。  
不要同时做后端和前端复杂业务。

推荐节奏：

```text
数据库 -> 后端模型 -> API -> 后端测试 -> 前端页面 -> 集成
```

## 4. 禁止对 AI 下的指令

不要说：

```text
帮我把 ConnLab 做出来
把所有功能实现一下
顺便把 Matrix 也做了
顺便加报告生成
```

这些会导致范围失控。

## 5. 推荐上下文注入

每次任务只给 AI：

- AGENTS.md
- 当前 TASK 文档
- 相关模块文档
- 相关代码文件

不要一次给所有旧系统代码。

## 6. 代码审查提示词

```text
请审查当前改动是否违反：
1. UI 是否直接操作 Office
2. 是否绕过 application 层
3. 是否引入非 MVP 功能
4. 是否有文件超过 500 行
5. 是否有业务逻辑进入 infrastructure
6. 是否有 domain 依赖外部技术
7. 是否缺少测试
```

## 7. 失败时处理

如果 AI 写偏了：

1. 不继续补丁式修改。
2. 回到任务边界。
3. 删除越界实现。
4. 重新让 AI 只实现最小版本。

## 8. 每阶段完成后要求 AI 输出

```text
阶段：
完成任务：
新增文件：
修改文件：
测试结果：
已知限制：
下一任务建议：
是否违反 MVP 范围：
```



---

<!-- Source: docs/13_LESSONS_FROM_LEGACY_SYSTEM.md -->


# 13 旧系统经验教训

## 1. 根本失败原因

旧系统从自动申请 LTR 的小程序开始，逐步增加项目文件夹、Matrix、测试记录、报告初始化、设备表、费用表、客户报告等功能。每个单点功能能用，但整体越来越复杂。

根本原因：

```text
没有先设计 Project 生命周期
没有统一领域模型
没有明确模块边界
没有统一数据源
UI 以工具按钮为中心
Matrix 被迫成为系统中心
```

## 2. 可保留资产

旧系统的价值：

- OfficeFacade 思路
- Word/Excel COM 经验
- 文件夹模板经验
- Matrix 业务理解
- 报告表头填充经验
- 设备表/费用表/客户报告转换经验
- 启动性能优化经验
- import guard / 架构红线经验

## 3. 必须避免的问题

### 3.1 UI 过重

旧系统 MainWindow 曾承载过多业务逻辑。新系统 UI 只能展示和调用 API。

### 3.2 功能堆叠

不要新增一个需求就新增一个按钮。所有功能必须挂到 Project 阶段。

### 3.3 Matrix 中心化

Matrix 是计划，不是系统核心。核心是 Project。

### 3.4 Service 膨胀

report_updater_service 这类巨型文件必须避免。超过 400 行就拆。

### 3.5 反向依赖

工具层不能依赖业务层。domain 不能依赖 infrastructure。

### 3.6 Word/Excel 数据孤岛

Word/Excel 只能作为输入输出。系统主数据必须结构化。

## 4. 新系统防崩机制

1. AGENTS.md 作为最高规则。
2. MVP 严格收敛。
3. 每个阶段有任务编号。
4. 每个任务有“不做事项”。
5. 文件大小限制。
6. Office Gateway 集中管理。
7. Application Service 统一编排。
8. Precheck 作为第一道质量门。
