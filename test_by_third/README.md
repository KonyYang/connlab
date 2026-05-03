# ConnLab Phase 7 手动冒烟测试工具包

本目录包含 Phase 7 功能的手动冒烟测试工具和自动化脚本。

## 📁 文件说明

| 文件 | 用途 |
|------|------|
| `SMOKE_TEST_GUIDE.md` | 完整的 13 步手动测试指南 |
| `QUICK_TEST_COMMANDS.md` | 快速复制粘贴的测试命令（推荐） |
| `TEST_DATA_PREPARATION.md` | 测试数据准备指南 |
| `verify_entities.py` | 验证项目实体（Project, ApplicationForm, SampleInfo, FileAsset） |
| `verify_ltr_record.py` | 验证 LTR 记录和审计信息 |
| `check_folder_structure.py` | 检查生成的文件夹结构和证据放置 |
| `IMPLEMENTATION_SUMMARY.md` | 实现总结文档 |

## 🚀 快速开始

### 前置条件

1. **启动后端服务**
   ```powershell
   # 在项目根目录
   .\scripts\run_backend.ps1
   ```

2. **准备测试数据**
   - 至少 1 个真实的 `.msg` Outlook 邮件文件
   - 至少 1 个有效的申请表单 `.docx` 文件
   - 将这些文件放在 `D:\test_samples\` 或修改脚本中的路径

3. **初始化数据库**（如果尚未初始化）
   ```powershell
   .\scripts\init_db.ps1
   ```

### 方式 1: 快速命令测试（推荐）

```powershell
# 查看快速测试命令
code QUICK_TEST_COMMANDS.md

# 复制粘贴命令到 PowerShell 执行
```

这提供了所有 API 调用的即用型命令。

### 方式 2: 手动测试（完整覆盖）

按照 `SMOKE_TEST_GUIDE.md` 中的 13 个测试步骤逐一执行。

使用 curl 或 Postman 调用 API，例如：

```powershell
# 测试 1: 导入 MSG
curl -X POST "http://localhost:8000/api/intake-packages/import-msg" ^
  -F "file=@D:\test_samples\request.msg"

# 测试 6: LTR 就绪性
curl -X GET "http://localhost:8000/api/projects/{project_id}/ltr/readiness"

# 测试 13A: 项目搜索
curl -X GET "http://localhost:8000/api/projects/lookup?q=DL-2026-04-001"
```

### 方式 3: 使用验证脚本

在完成某些步骤后，使用 Python 脚本验证实体：

```powershell
# 验证项目实体
python verify_entities.py --project-id {your_project_id}

# 验证 LTR 记录
python verify_ltr_record.py --project-id {your_project_id}

# 检查文件夹结构
python check_folder_structure.py --project-id {your_project_id}
```

## 📋 测试清单概览

1. ✅ 导入 MSG 包并确认源元数据和附件保留
2. ✅ 审查无表单和多表单包的异常结果
3. ✅ 选择有效申请表单并创建审查案例
4. ✅ 确认缺少必需信息的案例阻止项目创建
5. ✅ 确认完整案例并验证实体关联
6. ✅ 运行 LTR 就绪性检查并验证缺失字段阻塞
7. ✅ 运行 LTR 预览并验证无工作簿写入
8. ✅ 运行本地 LTR 提交并验证审计记录
9. ⚠️  工作簿写入配置测试（仅在副本上）
10. ✅ 运行文件夹预览/生成并验证冲突阻止
11. ✅ 运行证据放置预览/执行并验证源文件不被覆盖
12. ✅ 尝试无效的生命周期操作并验证业务可读消息
13. ✅ 使用查询端点验证结构化记录审查

## 🔍 常见问题

### Q1: 如何获取 project_id？

**A**: 在完成测试 5（确认完整案例）后，API 会返回 `project_id`。或者查询数据库：

```powershell
python -c "
from backend.infrastructure.storage.database import SessionLocal
from backend.infrastructure.storage.models import ProjectModel
session = SessionLocal()
projects = session.query(ProjectModel).all()
for p in projects:
    print(f'{p.project_id}: {p.product_name}')
session.close()
"
```

### Q2: 如何获取 package_id？

**A**: 在完成测试 1（导入 MSG）后，API 会返回 `package_id`。

### Q3: 测试 9（工作簿写入）安全吗？

**A**: ⚠️ **仅在副本上测试**！
1. 复制真实 LTR 工作簿到测试位置
2. 在 `connlab.local.toml` 中配置测试路径
3. 设置 `write_enabled = true`
4. 测试完成后立即改回 `false`

### Q4: 自动化脚本为什么跳过很多测试？

**A**: 因为某些测试需要：
- 前端 UI 交互（表单选择、案例确认）
- 特定的项目状态（LTR 注册后才能生成文件夹）
- 复杂的多步骤流程

自动化脚本主要测试独立的 API 端点。完整流程建议手动测试或使用前端界面。

### Q5: 如何查看数据库中的所有记录？

**A**: 使用 SQLite 浏览器打开 `data/connlab.sqlite3`，或运行：

```powershell
python -c "
import sqlite3
conn = sqlite3.connect('data/connlab.sqlite3')
cursor = conn.cursor()

# 列出所有表
cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")
print('Tables:', [row[0] for row in cursor.fetchall()])

# 查询项目数量
cursor.execute('SELECT COUNT(*) FROM projects')
print('Projects:', cursor.fetchone()[0])

# 查询 LTR 数量
cursor.execute('SELECT COUNT(*) FROM ltr_records')
print('LTR Records:', cursor.fetchone()[0])

conn.close()
"
```

## 📊 测试报告

测试完成后，请填写 `SMOKE_TEST_GUIDE.md` 末尾的测试报告模板，记录：
- 每个测试的结果（✅/❌）
- 发现的问题
- 总体评价和建议

## 🎯 通过标准

- **必须**: 所有 13 个测试全部通过
- **关键指标**:
  - 成功率: 100%
  - 数据完整性: 所有实体正确关联
  - 安全性: 无源文件覆盖，无意外工作簿写入
  - 用户体验: 错误消息清晰可读

## 📞 需要帮助？

参考文档：
- `docs/phase7_validation_summary.md` - Phase 7 验证总结
- `docs/task_board.md` - 任务看板
- `AGENTS.md` - 项目规则

## ⚠️ 注意事项

1. **不要**在生产数据上测试
2. **不要**在真实 LTR 工作簿上测试写入功能
3. **始终**先备份重要数据
4. 测试完成后清理测试数据（可选）

---

**祝测试顺利！** 🚀
