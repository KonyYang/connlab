# Markdown 文件整理报告

## 1. 整理目的

- 清理项目根目录，减少混乱
- 按照功能对文档进行分类
- 提高项目的可维护性
- 便于团队成员查找和维护

## 2. 整理前状态

- 项目根目录共有 9 个 Markdown 文件
- 文件类型混杂，缺乏组织
- "遵循了 `docs/markdown_management_rules.md` 中的分类原则"  

## 3. 整理后结构

### 3.1 项目根目录 (保持核心文档)
- `AGENTS.md` - AI 编码规则和项目指导方针（核心文档）
- `DESIGN.md` - 设计规范（核心文档）
- `PRODUCT.md` - 产品定义和需求（核心文档）
- `README.md` - 项目简介

### 3.2 docs/project_management/ （项目管理文档）
- `docs/project_management/TASK_EXECUTION_SKILL.md` - 任务执行技能指南
- `docs/project_management/TASK_REVIEW_CHECKLIST.md` - 任务审查清单
- `docs/project_management/TESTING_SKILL.md` - 测试技能指南

### 3.3 docs/engineering_standards/ （工程技术标准）
- `AGENTS.md` - AI 编码规则和项目指导方针（移回根目录，因为是核心文档）
- `DESIGN.md` - 设计规范（移回根目录，因为是核心文档）
- `PRODUCT.md` - 产品定义和需求（移回根目录，因为是核心文档）

### 3.4 docs/skills_guides/ （技能指南）
- `docs/skills_guides/AUTO_FIX_SKILL.md` - 自动修复技能指南
- `docs/skills_guides/ConnLab_Auto_Code_Skill_User_Guide.md` - 自动编码技能用户指南

## 4. 整理效果

- 遵循了 `docs/markdown_management_rules.md` 中的分类原则
- 相关文档按照功能进行了合理分组
- 项目根目录保留了最重要的核心文档 (`AGENTS.md`, `DESIGN.md`, `PRODUCT.md`, `README.md`)
- 文档结构更加清晰，便于查找和维护