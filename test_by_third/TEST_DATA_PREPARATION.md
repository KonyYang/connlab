# 测试数据准备指南

本指南说明如何准备 ConnLab Phase 7 冒烟测试所需的测试数据。

## 📦 必需文件

### 1. Outlook MSG 文件（必需）

**要求**:
- 真实的 `.msg` Outlook 邮件文件
- 包含以下字段（至少部分）:
  - Subject（主题）
  - From/Sender（发件人）
  - To/Recipients（收件人）
  - 可选：CC, Sent Date, Body

**示例内容**:
```
Subject: Connector Qualification Request
From: Alice Engineer <alice@example.com>
To: lab@example.com
Cc: manager@example.com
Sent: 2026-04-29 10:30 AM
Body: Please find attached the application form for connector testing.
```

**如何获取**:
1. 从 Outlook 导出真实邮件：
   - 打开 Outlook
   - 选择一封邮件
   - 文件 → 另存为 → 选择 "Outlook 消息格式 (*.msg)"
   
2. 或使用现有的测试 MSG 文件

**放置位置**:
```
D:\test_samples\request.msg
```

---

### 2. 申请表单 DOCX 文件（推荐）

**要求**:
- Form No.: E-3718
- Revision: H
- 包含以下字段（越完整越好）:

**必需字段**:
- Requester（请求人姓名）
- Phone（电话号码）
- Date（日期）
- Email（邮箱）
- Business Unit（业务单元）
- Manufacturing Site（制造地点）
- Project Number（项目编号，可选）

**样品信息**（至少 1 行）:
- Product Name（产品名称）
- Part Number（零件号）
- Revision（版本）
- Lot/Traceability（批次）
- Material（材料）
- Plating（镀层）
- Housing Material（外壳材料）
- Quantity（数量）

**测试描述**:
- Requested Testing（请求的测试）
- Test Type（测试类型）
- Sample Condition（样品状态）

**实验室信息**:
- Lab（实验室名称，如 DGLAB）
- Assigned Personnel（负责人）
- Received Date（接收日期）
- Estimated Completion Date（预计完成日期）

**如何获取**:
1. 使用真实的 E-3718 Rev H 表单模板
2. 填写完整信息
3. 保存为 `.docx` 格式

**放置位置**:
```
D:\test_samples\application_form.docx
```

---

### 3. 支撑附件（可选）

用于测试多附件场景：

- **规格书 PDF**: `specification.pdf`
- **图纸**: `drawing.pdf`
- **图片**: `photo.jpg` 或 `photo.png`
- **Excel 文件**: `data.xlsx`

**放置位置**:
```
D:\test_samples\attachments\
```

---

## 🧪 测试场景文件

为了全面测试，建议准备以下场景的文件：

### 场景 A: 完整有效的邮件包

**文件**:
- `complete_request.msg` - 包含一个完整的 .docx 申请表单附件

**预期结果**:
- 成功导入
- 自动检测到 1 个候选表单
- 可以顺利创建项目

---

### 场景 B: 无表单的邮件

**文件**:
- `no_form_request.msg` - 只包含文本，没有 .docx 附件

**预期结果**:
- 导入成功
- 异常审查显示 "No application form detected"
- 阻塞项目创建

---

### 场景 C: 多表单的邮件

**文件**:
- `multiple_forms.msg` - 包含 2+ 个 .docx 文件

**预期结果**:
- 导入成功
- 异常审查显示 "Multiple forms detected"
- 需要操作员选择其中一个

---

### 场景 D: 信息不完整的表单

**文件**:
- `incomplete_form.docx` - 缺少 requester, phone 等关键字段

**预期结果**:
- 可以解析
- LTR 就绪性检查显示 blockers
- 阻止 LTR 注册直到补全

---

## 📂 推荐的目录结构

```
D:\test_samples\
├── request.msg                      # 主要测试用的 MSG 文件
├── application_form.docx            # 主要测试用的表单
├── complete_request.msg             # 场景 A
├── no_form_request.msg              # 场景 B
├── multiple_forms.msg               # 场景 C
├── incomplete_form.docx             # 场景 D
└── attachments\                     # 可选附件
    ├── specification.pdf
    ├── drawing.pdf
    └── photo.jpg
```

---

## 🔧 修改脚本路径

如果使用不同的目录，需要修改 `run_all_smoke_tests.ps1`:

```powershell
# 在脚本顶部修改
$TEST_DATA_DIR = "你的测试数据目录"  # 例如: "C:\MyTestData"
```

---

## ✅ 验证测试数据

在开始测试前，运行以下命令验证文件是否存在：

```powershell
# 检查 MSG 文件
Test-Path "D:\test_samples\request.msg"

# 检查 DOCX 文件
Test-Path "D:\test_samples\application_form.docx"

# 列出所有测试文件
Get-ChildItem "D:\test_samples\" -Recurse | Select-Object FullName, Length
```

---

## 💡 提示

1. **文件大小**: MSG 文件通常几 KB 到几 MB，DOCX 文件通常几十 KB
2. **编码**: 确保文件使用 UTF-8 编码（特别是包含中文时）
3. **备份**: 保留原始文件的备份，测试可能会复制它们
4. **真实性**: 尽量使用真实业务文件，这样测试结果更有意义
5. **隐私**: 如果包含敏感信息，请脱敏后再用于测试

---

## 🆘 没有真实文件怎么办？

如果没有真实的 Outlook MSG 和 E-3718 表单：

1. **联系项目团队**获取样例文件
2. **创建模拟文件**:
   - MSG: 可以使用 Python 的 `olefile` 库创建简单的 OLE2 文件
   - DOCX: 使用 Microsoft Word 创建符合格式的文档
3. **使用测试夹具**: 查看 `tests/fixtures/` 目录是否有可用的示例

---

准备好测试数据后，就可以开始执行冒烟测试了！🚀
