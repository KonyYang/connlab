# TASK_178: New Project Intake Logic Fixes

**任务ID**: TASK_178  
**任务名称**: New Project Intake 逻辑矛盾修复  
**创建日期**: 2026-05-12  
**来源文档**: `docs/archive/external_ai/new_project_intake_logic_analysis_and_contradictions.md`  
**状态**: 完成，后续 Phase 2/3 停止  

---

## 执行摘要

本任务基于专家评估文档复核 New Project 邮件导入与申请表选择逻辑，只修复已证实影响页面加载和重复确认体验的 P0 问题。

已确认并修复：

- 矛盾 2：`_auto_select_application_form` 页面加载时可能触发未处理 duplicate 异常。
- 重复确认问题：用户重复点击已加载申请表时不应再次触发 duplicate 决策。

复审后停止：

- 矛盾 1：`replace_existing` 路径统一重构，停止。
- 矛盾 3：导入 `.msg` 时 SHA256 预检测，停止。
- 矛盾 4：`keep_manual_overrides` 深化调整，停止。
- 矛盾 5：`_can_reuse_case` 文档化，停止。

停止原因：这些后续项目前缺少可复现业务缺陷，继续做会扩大 New Project duplicate 生命周期和 selection service 的影响范围，收益低于风险。

---

## Phase 1.1: P0 修复自动选择 duplicate 异常

### 问题

`_auto_select_application_form` 在页面加载时调用 `select_form_asset()`，可能遇到已有重复草稿并抛出 `IntakeDraftDuplicateResolutionRequiredError`。页面自动加载不是用户主动选择，不能要求用户在此时做 duplicate 决策，也不能静默创建 separate draft。

### 最终方案

- 先检查可复用且已有 `selected_form_asset_id` 的 case。
- 如果存在对应 draft，直接返回该 case/draft。
- 自动选择候选申请表时不传 `resolution_action="create_separate"`。
- 如果候选触发 `IntakeDraftDuplicateResolutionRequiredError`，跳过该候选，继续尝试下一个。
- 如果全部候选失败，返回 `None`，由原有 blank draft 路径处理。

### 关键边界

`create_separate` 是显式 duplicate resolution 动作，不是“跳过”。自动页面加载不得使用它，否则会静默创建额外 Case/Draft。

### 修改文件

- `backend/application/new_project_application_draft_service.py`
- `tests/unit/test_new_project_auto_select_duplicate_handling.py`

---

## Phase 1.2: P0 修复重复确认对话框

### 问题

用户已加载某个申请表后再次点击同一附件，不应重复调用选择接口并再次触发 duplicate 检测。

### 最终方案

后端：

- `select_form_asset()` 开始处检查当前 package 中是否已有未确认 case 绑定同一 asset。
- 如果已有 draft，直接返回现有 `FormSelectionResult`。
- 显式 replace/reinitialize 请求不走 shortcut。

前端：

- `handleImportApplicationForm()` 只在当前 loaded `activeCase.selected_form_asset_id` 等于点击 asset 时跳过。
- 不使用 `session.selectedAssetId` 单独判断，因为附件列表点击会先改变 selected asset，但不会同步切换 loaded review。

### 修改文件

- `backend/application/intake_form_selection_service.py`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `tests/unit/test_select_already_selected_asset_shortcut.py`
- `tests/unit/test_intake_form_selection_service.py`

---

## 后续任务评估

### 矛盾 1: 统一 `replace_existing` 逻辑，停止

不继续执行。

原因：

- 同 package reinitialize 与跨 package replace/delete 是不同业务动作，不必为了形式统一做重构。
- 当前已有测试覆盖显式 replace 行为。
- 大范围重构 `select_form_asset()` 会同时影响 duplicate detection、case 复用、manual override、package delete，风险高于收益。

### 矛盾 3: 导入时 SHA256 预检测，停止

不继续执行。

原因：

- 当前产品决策是 duplicate resolution 发生在 draft 创建/申请表选择阶段。
- 导入阶段去重会改变 package 生命周期、附件检查、无表单草稿和 duplicate recovery 行为。
- 历史冗余已有 TASK_172 cleanup 路径。若未来真实数据量证明需要导入时去重，应另开任务定义 API contract。

### 矛盾 4: `keep_manual_overrides` 深化调整，停止

不继续执行。

原因：

- 当前没有可复现证据证明 P0 修复后仍会丢失 manual overrides。
- 已选中 asset shortcut 已减少重复 re-parse 的主要触发点。
- 未来若出现明确数据丢失场景，应作为数据保护 bug 单独处理。

### 矛盾 5: `_can_reuse_case` 文档澄清，停止

不继续执行。

原因：

- 这是注释澄清，不是功能缺陷。
- 当前任务目标是修复真实 P0 行为问题，继续扩大范围不符合任务控制。

---

## 验证计划

```powershell
py -m pytest tests\unit\test_new_project_auto_select_duplicate_handling.py tests\unit\test_select_already_selected_asset_shortcut.py tests\unit\test_new_project_application_draft_service.py tests\unit\test_intake_form_selection_service.py -q
npm run build
```

Additional checks:

```powershell
git diff --check
```

---

## 停止条件

- P0 修复验证通过。
- 任务板更新为 `TASK_178_NEW_PROJECT_INTAKE_LOGIC_FIXES` complete。
- 不继续 Phase 2/3。
- 不自动进入 Section 2 write-back 或其他后续任务。
