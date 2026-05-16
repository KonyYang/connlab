# New Project Intake 逻辑修复 - 执行摘要

**日期**: 2026-05-12  
**评审状态**: P0 修复完成，后续 Phase 2/3 停止  
**计划文档**: `tasks/TASK_178_NEW_PROJECT_INTAKE_LOGIC_FIXES.md`

---

## 评审结论

原分析报告中两个 P0 问题真实存在，已修复：

| 问题 | 结论 | 处理 |
|------|------|------|
| 自动选择触发 duplicate 异常 | 真实问题 | 已修复 |
| 重复确认对话框 | 真实问题 | 已修复 |
| replace_existing 路径不一致 | 暂无明确功能缺陷 | 停止 |
| 导入时重复检测时间点 | 属于产品生命周期选择 | 停止 |
| keep_manual_overrides 边界 | 暂无复现数据丢失 | 停止 |
| _can_reuse_case 注释 | 非功能缺陷 | 停止 |

---

## 已实施修复

### 1. 自动选择 duplicate 异常

最终策略：

- 优先复用已有 selected-form case/draft。
- 自动选择候选时不传 `resolution_action="create_separate"`。
- 遇到 `IntakeDraftDuplicateResolutionRequiredError` 时跳过该候选。
- 不在页面自动加载阶段静默创建 separate draft。

### 2. 重复确认对话框

最终策略：

- 后端 `select_form_asset()` 对已选中且未确认的同一 asset 直接返回现有 case/draft。
- 前端只在当前 loaded `activeCase.selected_form_asset_id` 等于点击 asset 时跳过导入。
- 不用 `session.selectedAssetId` 单独判断 loaded 状态，避免附件 focus 和实际 review 不一致。

---

## 后续阶段裁剪

Phase 2/3 不继续执行。原因：

- 统一 `replace_existing` 属于结构整理，当前风险高于收益。
- 导入时 SHA256 去重会改变 package 生命周期，应另开任务设计 API contract。
- `keep_manual_overrides` 缺少可复现数据丢失场景。
- `_can_reuse_case` 注释不应扩大当前修复范围。

---

## 验证命令

```powershell
py -m pytest tests\unit\test_new_project_auto_select_duplicate_handling.py tests\unit\test_select_already_selected_asset_shortcut.py tests\unit\test_new_project_application_draft_service.py tests\unit\test_intake_form_selection_service.py -q
npm run build
```
