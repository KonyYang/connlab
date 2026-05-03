# ConnLab Phase 7 手动冒烟测试指南

**版本**: 1.0  
**日期**: 2026-04-29  
**状态**: Phase 7 已完成，等待用户批准进入下一阶段

---

## 📋 测试概述

本测试套件用于验证 ConnLab Phase 7 的完整功能链路，从邮件导入到 LTR 注册、文件夹生成和证据放置。

### 前置条件

1. **后端服务运行中**
   ```powershell
   # 在项目根目录执行
   .\scripts\run_backend.ps1
   ```
   确认服务在 `http://localhost:8000` 运行

2. **前端服务运行中**（可选，如需 UI 测试）
   ```powershell
   cd frontend
   npm run dev
   ```
   确认前端在 `http://localhost:5173` 运行

3. **测试数据准备**
   - 至少 1 个真实的 `.msg` Outlook 邮件文件
   - 至少 1 个有效的申请表单 `.docx` 文件（Form No. E-3718 / Rev H）
   - 可选：规格书 PDF、图片等支撑附件

4. **数据库初始化**
   ```powershell
   .\scripts\init_db.ps1
   ```

---

## 🧪 测试清单

### 测试 1: 导入 MSG 包并确认源元数据和附件保留

**目标**: 验证 `.msg` 文件导入功能

**步骤**:
1. 准备一个真实的 `.msg` 文件（包含主题、发件人、收件人、附件）
2. 使用 API 或前端导入该文件
3. 检查返回的元数据是否完整

**API 测试命令**:
```powershell
# 假设 msg 文件路径为 D:\test_samples\request.msg
curl -X POST "http://localhost:8000/api/intake-packages/import-msg" ^
  -F "file=@D:\test_samples\request.msg"
```

**预期结果**:
- ✅ 返回 `package_id`
- ✅ 包含 `subject`, `sender_name`, `sender_email`, `recipients`
- ✅ 附件列表非空（如果有附件）
- ✅ 源文件保存在 `data/intake/{package_id}/source/`

**验证命令**:
```powershell
# 检查源文件是否保存
ls data\intake\{package_id}\source\
```

---

### 测试 2: 审查无表单和多表单包的异常结果

**目标**: 验证异常工作流处理

#### 2A: 无申请表单的邮件包

**步骤**:
1. 导入一个不包含 `.docx` 附件的 `.msg` 文件
2. 调用异常审查接口

**API 测试命令**:
```powershell
curl -X POST "http://localhost:8000/api/intake-packages/{package_id}/exceptions/review"
```

**预期结果**:
- ✅ 返回 `package_status`: `"needs_follow_up"`
- ✅ `issues` 列表包含 "No application form detected" 类型的问题
- ✅ `blocking: true` 标记

#### 2B: 多申请表单的邮件包

**步骤**:
1. 导入一个包含多个 `.docx` 文件的 `.msg` 文件
2. 调用异常审查接口

**预期结果**:
- ✅ 返回 `package_status`: `"multiple_forms_detected"`
- ✅ `case_ids` 列表包含多个案例 ID
- ✅ 每个案例对应一个候选表单

---

### 测试 3: 选择有效申请表单并创建审查案例

**目标**: 验证表单选择和案例创建

**步骤**:
1. 对于有有效表单的包，选择其中一个表单
2. 系统应自动创建 `IntakeCase` 和 `IntakeDraft`

**API 测试命令**:
```powershell
# 选择表单（假设 asset_id 已知）
curl -X POST "http://localhost:8000/api/intake-cases/{case_id}/select-form" ^
  -H "Content-Type: application/json" ^
  -d "{\"asset_id\": \"asset-xxx\"}"
```

**预期结果**:
- ✅ 返回 `case_id` 和 `draft_id`
- ✅ 案例状态变为 `"needs_review"`
- ✅ 草稿包含解析的字段（project_no, requester, samples 等）

**验证命令**:
```powershell
# 检查数据库中的案例记录
python -c "
from backend.infrastructure.storage.database import SessionLocal
from backend.infrastructure.storage.models import IntakeCaseModel
session = SessionLocal()
cases = session.query(IntakeCaseModel).all()
for c in cases:
    print(f'Case {c.case_id}: status={c.status}')
session.close()
"
```

---

### 测试 4: 确认缺少必需信息的案例阻止项目创建

**目标**: 验证缺失字段的阻塞行为

**步骤**:
1. 选择一个缺少关键信息（如 requester, phone, product_name）的表单
2. 尝试确认案例以创建项目

**API 测试命令**:
```powershell
curl -X POST "http://localhost:8000/api/intake-cases/{case_id}/confirm" ^
  -H "Content-Type: application/json" ^
  -d "{}"
```

**预期结果**:
- ❌ 返回 HTTP 400 错误
- ✅ 错误消息明确指出缺失字段（如 "Missing required field: requester"）
- ✅ 项目未创建

---

### 测试 5: 确认完整案例并验证实体关联

**目标**: 验证完整的项目创建工作流

**步骤**:
1. 选择一个信息完整的表单案例
2. 确认案例以创建项目

**API 测试命令**:
```powershell
curl -X POST "http://localhost:8000/api/intake-cases/{case_id}/confirm" ^
  -H "Content-Type: application/json" ^
  -d "{\"manual_overrides\": {}}"
```

**预期结果**:
- ✅ 返回 `project_id`
- ✅ 数据库中创建以下记录：
  - `Project` (status: "confirmed")
  - `ApplicationForm` (与 project_id 关联)
  - `SampleInfo` (至少 1 条，与 project_id 关联)
  - `FileAsset` (原始 .msg 和选定的 .docx)
  - `IntakeCase` (status: "confirmed", confirmed_project_id 已设置)

**验证命令**:
```powershell
python test_by_third\verify_entities.py --project-id {project_id}
```

---

### 测试 6: 运行 LTR 就绪性检查并验证缺失字段阻塞

**目标**: 验证 LTR 就绪性评估

**步骤**:
1. 使用刚创建的项目 ID
2. 调用 LTR 就绪性检查 API

**API 测试命令**:
```powershell
curl -X GET "http://localhost:8000/api/projects/{project_id}/ltr/readiness"
```

**预期结果**:
- ✅ 返回 `status`: `"blocked"` 或 `"review_required"`（取决于字段完整性）
- ✅ `blockers` 列表包含缺失的关键字段（如 phone, email, business_unit）
- ✅ 每个 blocker 有明确的 `operator_action` 说明

---

### 测试 7: 运行 LTR 预览并验证无工作簿写入

**目标**: 验证 LTR 预览的只读性质

**步骤**:
1. 调用 LTR 预览 API（使用 local_only 模式）

**API 测试命令**:
```powershell
curl -X POST "http://localhost:8000/api/projects/{project_id}/ltr/preview" ^
  -H "Content-Type: application/json" ^
  -d '{
    "year": 2026,
    "month": 4,
    "registration_type": "normal",
    "mode": "local_only"
  }'
```

**预期结果**:
- ✅ 返回预览对象
- ✅ `proposed_ltr_number` 可能为 `null`（正常模式下不预计算）
- ✅ `number_preflight_required: false`
- ✅ **没有 Excel 工作簿被打开或修改**
- ✅ `mode: "local_only"`

**验证命令**:
```powershell
# 确认没有 Excel 进程在运行
Get-Process | Where-Object {$_.ProcessName -like "*EXCEL*"}
# 应该返回空或仅显示你手动打开的 Excel
```

---

### 测试 8: 运行本地 LTR 提交并验证审计记录

**目标**: 验证本地 LTR 提交流程

**前置条件**: 
- LTR 预览状态不是 `"blocked"`
- 操作员明确确认

**API 测试命令**:
```powershell
curl -X POST "http://localhost:8000/api/projects/{project_id}/ltr/commit" ^
  -H "Content-Type: application/json" ^
  -d '{
    "year": 2026,
    "month": 4,
    "registration_type": "associated",
    "mode": "local_only",
    "proposed_ltr_number": "DL-2026-04-001A",
    "operator_confirmed": true,
    "requested_by": "Alice Engineer",
    "operator_note": "Approved by intake operator after review"
  }'
```

**预期结果**:
- ✅ 返回 `ltr` 对象，包含 `ltr_id` 和 `ltr_number`
- ✅ `preview` 对象回显
- ✅ 项目中 `LtrRecord` 创建，status: "registered"
- ✅ 项目状态更新为 `"ltr_registered"`
- ✅ `notes` 字段包含审计信息

**验证命令**:
```powershell
python test_by_third\verify_ltr_record.py --project-id {project_id}
```

---

### 测试 9: 工作簿写入配置测试（仅在副本上）

**⚠️ 警告**: 此测试仅在配置了工作簿写入且使用**副本**时执行

**步骤**:
1. 复制真实 LTR 工作簿到测试位置
2. 在 `connlab.local.toml` 中配置：
   ```toml
   [ltr.workbook]
   write_enabled = true
   workbook_path = "D:\\test_workbooks\\LTR_2026_copy.xls"
   password = "DGLAB"  # 或其他实际密码
   ```
3. 重启后端服务
4. 执行测试 8 的提交操作（不使用 `local_only` 模式）

**预期结果**:
- ✅ Excel 工作簿被打开并写入新行
- ✅ 写入后 Excel 进程正确释放
- ✅ 本地 LTR 记录同步更新
- ✅ 如果密码错误或路径无效，返回错误且不创建本地记录

**清理**:
```powershell
# 测试后恢复配置
# 将 write_enabled 改回 false
```

---

### 测试 10: 运行文件夹预览/生成并验证冲突阻止

**目标**: 验证文件夹生成的安全性

**步骤**:
1. 调用文件夹预览 API

**API 测试命令**:
```powershell
curl -X POST "http://localhost:8000/api/projects/{project_id}/folder/preview" ^
  -H "Content-Type: application/json" ^
  -d '{
    "template_path": "templates/project_template",
    "target_root": "data/projects",
    "dl_number": "DL-2026-04-001",
    "plan_date": "2026-04-29"
  }'
```

**预期结果**:
- ✅ 返回 `FolderPlan`，包含要创建的目录和文件列表
- ✅ 如果目标文件夹已存在，`conflict: true`

**步骤 2**: 执行文件夹生成

```powershell
curl -X POST "http://localhost:8000/api/projects/{project_id}/folder/generate" ^
  -H "Content-Type: application/json" ^
  -d '{
    "template_path": "templates/project_template",
    "target_root": "data/projects",
    "dl_number": "DL-2026-04-001",
    "plan_date": "2026-04-29"
  }'
```

**预期结果**:
- ✅ 返回 `folder_id` 和 `project_folder_path`
- ✅ 文件夹结构在磁盘上创建
- ✅ 项目状态更新为 `"folder_created"`
- ✅ 再次尝试生成相同文件夹时返回冲突错误

**验证命令**:
```powershell
# 检查文件夹是否创建
ls "data\projects\DL-2026-04-001\"
```

---

### 测试 11: 运行证据放置预览/执行并验证源文件不被覆盖

**目标**: 验证证据放置的无覆盖复制行为

**步骤**:
1. 调用证据放置预览 API

**API 测试命令**:
```powershell
curl -X POST "http://localhost:8000/api/projects/{project_id}/evidence/placement-preview"
```

**预期结果**:
- ✅ 返回 `EvidencePlacementPlan`
- ✅ 列出所有要复制的证据文件（.msg, .docx, 附件等）
- ✅ 每个 item 显示 `source_path`, `target_path`, `target_exists`
- ✅ 如果目标已存在，`conflict: true`

**步骤 2**: 执行证据放置

```powershell
curl -X POST "http://localhost:8000/api/projects/{project_id}/evidence/place"
```

**预期结果**:
- ✅ 返回 `copied_paths` 列表
- ✅ 证据文件复制到项目文件夹的正确子目录：
  - `.msg` → `E-mail/`
  - 选定表单 → `Submitted Material/`
  - 支撑附件 → `Submitted Material/`
  - 规格书 → `Submitted Material/Specifications/`
- ✅ **源文件未被删除或修改**
- ✅ 目标文件夹中无文件被覆盖

**验证命令**:
```powershell
# 检查源文件仍然存在
ls "data\intake\{package_id}\source\"
ls "data\intake\{package_id}\attachments\"

# 检查证据已放置
ls "data\projects\DL-2026-04-001\DL-2026-04-001*\E-mail\"
ls "data\projects\DL-2026-04-001\DL-2026-04-001*\Submitted Material\"
```

---

### 测试 12: 尝试无效的生命周期操作并验证业务可读消息

**目标**: 验证生命周期守卫

#### 12A: 在 LTR 注册前尝试生成文件夹

**API 测试命令**:
```powershell
# 创建一个仅有 confirmed 状态但未注册 LTR 的项目
curl -X POST "http://localhost:8000/api/projects/{project_id}/folder/preview" ^
  -H "Content-Type: application/json" ^
  -d '{...}'
```

**预期结果**:
- ❌ 返回 HTTP 400
- ✅ 错误消息: `"Project folder generation requires a registered LTR first. Current project status is confirmed."`

#### 12B: 在文件夹生成前尝试放置证据

**API 测试命令**:
```powershell
# 在 ltr_registered 但未 folder_created 的项目上
curl -X POST "http://localhost:8000/api/projects/{project_id}/evidence/place"
```

**预期结果**:
- ❌ 返回 HTTP 400
- ✅ 错误消息: `"Evidence placement requires a generated project folder first. Current project status is ltr_registered."`

#### 12C: 尝试修改已关闭的项目

**API 测试命令**:
```powershell
# 先关闭项目（如果有此 API）
# 然后尝试 LTR 预览
curl -X GET "http://localhost:8000/api/projects/{closed_project_id}/ltr/readiness"
```

**预期结果**:
- ❌ 返回 HTTP 400
- ✅ 错误消息: `"Closed projects are read-only."`

---

### 测试 13: 使用查询端点验证结构化记录审查

**目标**: 验证只读查询功能

#### 13A: 项目搜索

**API 测试命令**:
```powershell
# 按 LTR 号码搜索
curl -X GET "http://localhost:8000/api/projects/lookup?q=DL-2026-04-001"

# 按零件号搜索
curl -X GET "http://localhost:8000/api/projects/lookup?q=PN-100"

# 按产品名称搜索
curl -X GET "http://localhost:8000/api/projects/lookup?q=Connector"

# 按请求人搜索
curl -X GET "http://localhost:8000/api/projects/lookup?q=Alice"
```

**预期结果**:
- ✅ 返回匹配的项目列表
- ✅ 每个项目包含 `matched_fields` 说明匹配原因

#### 13B: 样本摘要

**API 测试命令**:
```powershell
curl -X GET "http://localhost:8000/api/projects/{project_id}/sample-summary"
```

**预期结果**:
- ✅ 返回 `SampleSummary` 对象
- ✅ 包含 `ltr_numbers` 列表
- ✅ `samples` 列表包含所有样本行，字段包括：
  - `product_name`, `part_number`, `revision`
  - `lot_or_traceability`, `material`, `plating`
  - `housing_material`, `quantity`

#### 13C: 测试条件和方法摘要

**API 测试命令**:
```powershell
curl -X GET "http://localhost:8000/api/projects/{project_id}/testing-summary"
```

**预期结果**:
- ✅ 返回 `TestingSummary` 对象
- ✅ 包含：
  - `requested_testing`: 测试描述文本
  - `test_type`: 测试类型
  - `sample_condition`: 样本状态
  - `requested_completion_date`: 期望完成日期
  - `applicable_specifications`: 规格书文件名列表
  - `lab`: 实验室名称
  - `assigned_personnel`: 负责人

---

## 🔍 自动化验证脚本

我们提供了以下 Python 脚本来辅助验证：

### 1. verify_entities.py
验证项目相关实体是否正确创建和关联

```powershell
python test_by_third\verify_entities.py --project-id {project_id}
```

### 2. verify_ltr_record.py
验证 LTR 记录和审计信息

```powershell
python test_by_third\verify_ltr_record.py --project-id {project_id}
```

### 3. check_folder_structure.py
检查生成的文件夹结构和证据放置

```powershell
python test_by_third\check_folder_structure.py --project-id {project_id}
```

### 4. run_all_smoke_tests.ps1
一键运行所有 API 冒烟测试（需要配置测试数据路径）

```powershell
.\test_by_third\run_all_smoke_tests.ps1
```

---

## ✅ 通过标准

所有 13 个测试必须全部通过，才能认为 Phase 7 功能完整可用。

### 关键指标

- **成功率**: 100% (13/13)
- **数据完整性**: 所有实体正确关联
- **安全性**: 无源文件覆盖，无意外工作簿写入
- **用户体验**: 错误消息清晰可读

---

## 📝 测试报告模板

测试完成后，请填写以下报告：

```markdown
# Phase 7 手动冒烟测试报告

**测试日期**: YYYY-MM-DD  
**测试人员**: [姓名]  
**环境**: Windows XX, Python 3.11, ConnLab vX.X

## 测试结果汇总

| 测试编号 | 测试名称 | 结果 | 备注 |
|---------|---------|------|------|
| 1 | MSG 导入 | ✅/❌ | |
| 2A | 无表单异常 | ✅/❌ | |
| 2B | 多表单异常 | ✅/❌ | |
| 3 | 表单选择 | ✅/❌ | |
| 4 | 缺失字段阻塞 | ✅/❌ | |
| 5 | 完整案例确认 | ✅/❌ | |
| 6 | LTR 就绪性 | ✅/❌ | |
| 7 | LTR 预览 | ✅/❌ | |
| 8 | LTR 本地提交 | ✅/❌ | |
| 9 | 工作簿写入 | ⚠️ 跳过/✅/❌ | |
| 10 | 文件夹生成 | ✅/❌ | |
| 11 | 证据放置 | ✅/❌ | |
| 12 | 生命周期守卫 | ✅/❌ | |
| 13 | 查询端点 | ✅/❌ | |

## 发现的问题

1. [问题描述]
   - 严重程度: [高/中/低]
   - 复现步骤: [...]
   - 建议修复: [...]

## 总体评价

[对 Phase 7 功能的评价]

## 建议

[对下一阶段的建议]
```

---

## 🚀 下一步

测试通过后，根据 `phase7_validation_summary.md` 的建议：

- **Phase 8A**: 前端操作员工作流接线（使用 `$impeccable` UI 规则）
- **Phase 8B**: 受控 LTR 工作簿写入的操作强化

**注意**: 不要自动激活任何阶段，需等待用户明确批准。

---

## 📞 支持

如有问题，请参考：
- `docs/phase7_validation_summary.md`
- `docs/task_board.md`
- `AGENTS.md`
