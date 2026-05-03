# 测试工具包使用指南

## 🎯 快速开始（3 步）

### 第 1 步：启动后端服务

```powershell
# 在项目根目录
.\scripts\run_backend.ps1
```

等待看到 "Application startup complete" 消息。

---

### 第 2 步：准备测试数据

在 `D:\test_samples\` 目录中放置：
- `request.msg` - Outlook 邮件文件（必需）
- `application_form.docx` - 申请表单（推荐）

如果没有测试数据，参考 `TEST_DATA_PREPARATION.md`。

---

### 第 3 步：执行测试

**选项 A：使用快速命令（推荐）**
```powershell
code QUICK_TEST_COMMANDS.md
```
复制粘贴命令到 PowerShell 逐一执行。

**选项 B：阅读完整指南**
```powershell
code SMOKE_TEST_GUIDE.md
```
按照 13 个步骤手动测试。

**选项 C：验证已有数据**
```powershell
# 如果已经有项目，验证实体
python verify_entities.py --project-id {your_project_id}
python verify_ltr_record.py --project-id {your_project_id}
python check_folder_structure.py --project-id {your_project_id}
```

---

## 📚 文档说明

### 核心文档

1. **QUICK_TEST_COMMANDS.md** ⭐ 推荐先看这个
   - 所有 API 调用的即用型命令
   - 复制粘贴即可执行
   - 包含预期结果说明

2. **SMOKE_TEST_GUIDE.md**
   - 完整的 13 步测试流程
   - 详细的操作步骤和验证方法
   - 测试报告模板

3. **TEST_DATA_PREPARATION.md**
   - 如何准备测试数据
   - MSG 和 DOCX 文件要求
   - 测试场景示例

### 验证脚本

4. **verify_entities.py**
   ```powershell
   python verify_entities.py --project-id abc-123
   ```
   验证 Project, ApplicationForm, SampleInfo, FileAsset 等实体

5. **verify_ltr_record.py**
   ```powershell
   python verify_ltr_record.py --project-id abc-123
   ```
   验证 LTR 记录和审计信息

6. **check_folder_structure.py**
   ```powershell
   python check_folder_structure.py --project-id abc-123
   ```
   检查文件夹结构和证据放置

### 辅助文档

7. **README.md**
   - 总体介绍
   - 常见问题解答

8. **IMPLEMENTATION_SUMMARY.md**
   - 实现总结
   - 功能特性说明

---

## 🔧 常用命令速查

### 获取 project_id

```powershell
# 方法 1: 从确认案例的 API 响应中获取
# 方法 2: 查询数据库
python -c "
from backend.infrastructure.storage.database import SessionLocal
from backend.infrastructure.storage.models import ProjectModel
session = SessionLocal()
for p in session.query(ProjectModel).all():
    print(f'{p.project_id}: {p.product_name}')
session.close()
"
```

### 获取 package_id

```powershell
# 从导入 MSG 的 API 响应中获取
# 或查询数据库
python -c "
import sqlite3
conn = sqlite3.connect('data/connlab.sqlite3')
cursor = conn.cursor()
cursor.execute('SELECT package_id, source_original_name FROM intake_packages')
for row in cursor.fetchall():
    print(f'{row[0]}: {row[1]}')
conn.close()
"
```

### 查看数据库内容

```powershell
python -c "
import sqlite3
conn = sqlite3.connect('data/connlab.sqlite3')
cursor = conn.cursor()

# 列出所有表
cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")
print('Tables:', [r[0] for r in cursor.fetchall()])

# 统计记录数
for table in ['projects', 'application_forms', 'sample_infos', 'ltr_records']:
    cursor.execute(f'SELECT COUNT(*) FROM {table}')
    print(f'{table}: {cursor.fetchone()[0]} records')

conn.close()
"
```

---

## ✅ 测试通过标准

所有 13 个测试项必须全部通过：

1. ✅ MSG 导入成功，元数据和附件正确
2. ✅ 异常工作流正确识别问题
3. ✅ 表单选择创建案例
4. ✅ 缺失字段阻塞项目创建
5. ✅ 完整案例成功创建项目
6. ✅ LTR 就绪性检查识别 blockers
7. ✅ LTR 预览不写入工作簿
8. ✅ LTR 本地提交创建记录
9. ⚠️  工作簿写入仅在副本上测试
10. ✅ 文件夹生成无冲突
11. ✅ 证据放置不覆盖源文件
12. ✅ 生命周期守卫阻止无效操作
13. ✅ 查询端点返回正确数据

---

## 🐛 常见问题

### Q: PowerShell 脚本执行报错？

A: 使用 `QUICK_TEST_COMMANDS.md` 中的命令代替，或直接在浏览器中使用 Swagger UI：
```
http://localhost:8000/docs
```

### Q: 如何知道测试是否成功？

A: 每个 API 调用应该返回 HTTP 200 状态码和预期的 JSON 数据。使用验证脚本检查数据库记录。

### Q: 测试数据从哪里来？

A: 
1. 使用真实的业务文件（推荐）
2. 从 Outlook 导出 .msg 文件
3. 使用现有的 E-3718 表单模板

### Q: 可以跳过某些测试吗？

A: 建议完成所有测试以确保 Phase 7 功能完整。但至少应执行：
- Test 1: MSG 导入
- Test 6: LTR 就绪性
- Test 10: 文件夹预览
- Test 13: 查询端点

### Q: 测试后需要清理数据吗？

A: 可选。如需清理：
```powershell
# 删除测试项目（谨慎操作！）
python -c "
from backend.infrastructure.storage.database import SessionLocal
from backend.infrastructure.storage.models import ProjectModel
session = SessionLocal()
# 先查看
for p in session.query(ProjectModel).all():
    print(f'{p.project_id}: {p.product_name}')
# 确认后再删除
# session.query(ProjectModel).filter_by(project_id='xxx').delete()
# session.commit()
session.close()
"
```

---

## 📞 需要帮助？

1. 查看 `docs/phase7_validation_summary.md` - Phase 7 验证总结
2. 查看 `docs/task_board.md` - 任务看板
3. 查看 `AGENTS.md` - 项目规则

---

## 🎉 开始测试！

现在你已经准备好了，祝测试顺利！

```powershell
# 最简单的开始方式
code QUICK_TEST_COMMANDS.md
```

复制第一个命令，粘贴到 PowerShell，按回车，开始吧！🚀
