# Precheck Lower Panels 布局优化修改记录

**修改日期**: 2026-05-04  
**修改人**: AI Assistant  
**影响范围**: Precheck 页面下部面板布局

---

## 一、修改背景

根据计划文档 `docs/archive/historical_plans/precheck_lower_panels_editable_requested_testing_plan.md` 的最新更新要求，对 Precheck 页面下部面板进行布局和交互优化，使其更符合应用表单的原始结构和用户操作习惯。

---

## 二、修改内容

### 2.1 第一轮修改：实现可编辑功能

#### 修改文件清单

**后端文件**:
1. `backend/application/intake_form_selection_service.py`
2. `backend/application/intake_case_review_service.py`
3. `backend/api/routes_intake_review.py`

**前端文件**:
1. `frontend/src/api/client.ts`
2. `frontend/src/features/precheck/precheckFieldConfig.ts`
3. `frontend/src/features/precheck/precheckReviewSelectors.ts`
4. `frontend/src/pages/IntakeCaseReviewPage.tsx`
5. `frontend/src/features/precheck/PrecheckLowerPanels.tsx`
6. `frontend/src/intake-case-review.css`

**测试文件**:
1. `tests/unit/test_frontend_shell_files.py`

#### 详细修改说明

##### 2.1.1 后端数据结构扩展

**文件**: `backend/application/intake_form_selection_service.py`

**修改内容**:
- 在 `_draft_payload()` 方法中添加 `requested_testing_rows` 字段
- 将解析器输出的结构化请求测试行数据包含到 draft payload 中

```python
"requested_testing_rows": [
    {
        "test_to_be_performed": self._clean(row.test_to_be_performed),
        "applicable_specification": self._clean(row.applicable_specification),
    }
    for row in parsed.requested_testing_rows
],
```

**原因**: 前端需要结构化的数据来渲染可编辑的两列表格，而不是单一的文本字符串。

---

**文件**: `backend/application/intake_case_review_service.py`

**修改内容**:
1. 在 `_editable_fields` 集合中添加 `"requested_testing_rows"`
2. 在 `update_case_fields()` 方法中添加 `requested_testing_rows` 参数处理
3. 新增 `_normalized_requested_testing_rows()` 方法用于数据规范化
4. 自动同步更新扁平化的 `requested_testing` 字段以保持向后兼容

**原因**: 支持前端提交的结构化行数据，并确保与现有的 precheck blocker 检查逻辑兼容。

---

**文件**: `backend/api/routes_intake_review.py`

**修改内容**:
1. `UpdateIntakeCaseReviewFieldsRequest` 添加 `requested_testing_rows` 字段
2. `IntakeCaseReviewItemResponse` 添加 `requested_testing_rows` 字段
3. `update_intake_case_review_fields()` 路由传递新参数
4. 新增 `_requested_testing_rows()` 辅助函数提取数据

**原因**: API 层需要支持新的数据结构输入和输出。

---

##### 2.1.2 前端类型定义和工具函数

**文件**: `frontend/src/api/client.ts`

**修改内容**:
```typescript
export type RequestedTestingRowInput = {
  test_to_be_performed: string;
  applicable_specification: string;
};

export type UpdateIntakeCaseReviewFieldsInput = {
  fields: Record<string, string | null>;
  sample_rows?: Record<string, string>[];
  requested_testing_rows?: RequestedTestingRowInput[];
};

export type IntakeCaseReviewItem = {
  // ... 其他字段
  requested_testing_rows: Record<string, unknown>[];
};
```

**原因**: TypeScript 类型定义确保前后端数据契约的一致性。

---

**文件**: `frontend/src/features/precheck/precheckFieldConfig.ts`

**修改内容**:
```typescript
export type PrecheckRequestedTestingRow = {
  test_to_be_performed: string;
  applicable_specification: string;
};

export const PRECHECK_REQUESTED_TESTING_COLUMNS = [
  { key: "test_to_be_performed", label: "Tests to be Performed" },
  { key: "applicable_specification", label: "Applicable Specifications" }
] as const;

export function emptyPrecheckRequestedTestingRow(): PrecheckRequestedTestingRow {
  return {
    test_to_be_performed: "",
    applicable_specification: ""
  };
}
```

**原因**: 提供表格列定义和空行创建工具函数。

---

**文件**: `frontend/src/features/precheck/precheckReviewSelectors.ts`

**修改内容**:
```typescript
export function normalizedRequestedTestingRows(raw: unknown): PrecheckRequestedTestingRow[] {
  if (!Array.isArray(raw)) {
    return [emptyPrecheckRequestedTestingRow()];
  }
  const rows = raw
    .map((row) => ({
      test_to_be_performed: String((row as Record<string, unknown>).test_to_be_performed ?? ""),
      applicable_specification: String((row as Record<string, unknown>).applicable_specification ?? "")
    }))
    .filter((row) => row.test_to_be_performed || row.applicable_specification);
  return rows.length > 0 ? rows : [emptyPrecheckRequestedTestingRow()];
}

export function requestedTestingText(rows: PrecheckRequestedTestingRow[]): string {
  return rows
    .map((row) => row.test_to_be_performed.trim())
    .filter(Boolean)
    .join("\n");
}
```

**原因**: 数据格式转换工具，用于后端数据和前端状态之间的映射。

---

##### 2.1.3 页面状态管理

**文件**: `frontend/src/pages/IntakeCaseReviewPage.tsx`

**修改内容**:
1. 添加 `requestedTestingRows` 状态
2. 在 `activeCase` 变化时初始化行数据
3. 添加 `requestedTestingRowsChanged` 变更检测
4. 在 `handleSaveFields()` 中提交结构化数据
5. 实现所有行操作回调函数

**原因**: 页面协调器需要管理行数据和同步到后端。

---

##### 2.1.4 组件重构

**文件**: `frontend/src/features/precheck/PrecheckLowerPanels.tsx`

**修改内容**:
1. 重构为受控组件，添加所有编辑回调 props
2. Radio buttons 移除 `readOnly`，改为可编辑
3. RequestedTestingPanel 渲染可编辑表格
4. AdditionalInfoPanel textarea 可编辑

**原因**: 实现计划中要求的所有编辑功能。

---

##### 2.1.5 样式更新

**文件**: `frontend/src/intake-case-review.css`

**修改内容**:
- `.precheck-lower-grid`: 三列并行布局
- `.radio-line`: 紧凑的 radio 行样式
- `.requested-testing-edit-table`: 可编辑表格样式
- `.requested-testing-cell-input`: 表格单元格输入框样式

**原因**: 支持新的可编辑组件视觉呈现。

---

### 2.2 第二轮修改：布局优化（Actions 列）

#### 修改文件

**前端文件**:
1. `frontend/src/features/precheck/PrecheckLowerPanels.tsx`
2. `frontend/src/pages/IntakeCaseReviewPage.tsx`
3. `frontend/src/intake-case-review.css`

**测试文件**:
1. `tests/unit/test_frontend_shell_files.py`

#### 详细修改说明

##### 2.2.1 布局重构

**文件**: `frontend/src/features/precheck/PrecheckLowerPanels.tsx`

**修改内容**:
1. 移除 `ConsentPanel` 子组件，直接在主组件中渲染
2. 添加 `onRequestedTestingRowEdit` 和 `onRequestedTestingRowCopy` 回调
3. RequestedTestingPanel 添加 Actions 列（Edit/Copy/Delete 图标按钮）
4. 使用 `UiIcon` 组件渲染操作图标

**原因**: 根据计划更新，需要使用图标按钮而非文本按钮，与 Sample Table 保持一致的 UX。

---

**文件**: `frontend/src/pages/IntakeCaseReviewPage.tsx`

**修改内容**:
```typescript
onRequestedTestingRowCopy={(rowIndex) => {
  setRequestedTestingRows((current) => {
    const copied = { ...(current[rowIndex] ?? emptyPrecheckRequestedTestingRow()) };
    return [...current.slice(0, rowIndex + 1), copied, ...current.slice(rowIndex + 1)];
  });
  setFieldSaveMessage(null);
}}
onRequestedTestingRowEdit={(rowIndex) => {
  document
    .querySelector<HTMLTextAreaElement>(
      `.requested-testing-edit-table tbody tr:nth-child(${rowIndex + 1}) textarea:first-child`
    )
    ?.focus();
}}
```

**原因**: 实现 Copy 和 Edit 功能逻辑。

---

**文件**: `frontend/src/intake-case-review.css`

**修改内容**:
```css
.precheck-lower-grid {
  display: grid;
  grid-template-columns: 1fr;  /* 改为单列垂直布局 */
  gap: 14px;
}

.precheck-consent-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(260px, 1fr));
  /* 双列水平布局，窄屏自动堆叠 */
}

.requested-testing-row-actions {
  display: inline-grid;
  grid-auto-flow: column;
  gap: 8px;
}

.requested-testing-row-actions button {
  width: 28px;
  height: 28px;
  /* 图标按钮样式 */
}
```

**原因**: 实现计划中的垂直堆叠布局，Consent Row 水平排列，Requested Testing 和 Additional Info 全宽显示。

---

**文件**: `tests/unit/test_frontend_shell_files.py`

**修改内容**:
```python
# 从
"ConsentPanel"
# 改为
"precheck-consent-row"
```

**原因**: `ConsentPanel` 组件已被移除，改为内联渲染。

---

### 2.3 第三轮修改：UI 细节优化

#### 修改文件

1. `frontend/src/features/precheck/PrecheckLowerPanels.tsx`
2. `frontend/src/intake-case-review.css`

#### 详细修改说明

##### 2.3.1 Add Row 按钮位置调整

**文件**: `frontend/src/features/precheck/PrecheckLowerPanels.tsx`

**修改内容**:
```tsx
<div className="requested-testing-header">
  <h4>Description of Requested Testing</h4>
  <button className="requested-testing-add-button">
    + Add Row
  </button>
</div>
```

**原因**: 用户要求将 "+ Add Row" 按钮移到与标题同行，并缩小按钮尺寸，节省垂直空间。

---

**文件**: `frontend/src/intake-case-review.css`

**修改内容**:
```css
.requested-testing-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.requested-testing-add-button {
  min-height: 32px;
  padding: 6px 14px;
  font-size: 12px;
  /* 紧凑按钮样式 */
}

.requested-testing-edit-table th:first-child {
  width: 80%;  /* 从 58% 扩展 */
}

.requested-testing-edit-table th:nth-child(2) {
  width: auto;  /* 自动填充 */
}
```

**原因**: 
1. 扩展 "Tests to be Performed" 列宽约 40%
2. 标题和按钮水平布局

---

### 2.4 第四轮修改：修复间距问题

#### 修改文件

1. `frontend/src/intake-case-review.css`

#### 详细修改说明

**问题描述**: 
"Confidential test or samples?*" 标签与 "Yes/No" 选项之间出现巨大空白间隔。

**根本原因**:
```css
.radio-line {
  grid-template-columns: minmax(0, 1fr) max-content max-content;
  /*         ↑ 第一列占据所有可用空间 */
}
```

**文件**: `frontend/src/intake-case-review.css`

**修改内容**:
```css
.radio-line {
  grid-template-columns: auto max-content max-content;
  /* 改为 auto，只占用标签实际宽度 */
}
```

**原因**: `1fr` 会让第一列拉伸占据所有空间，导致标签被推到最左，Yes/No 被挤到最右。改为 `auto` 后，标签和选项紧密排列。

---

## 三、修改影响分析

### 3.1 功能影响

**新增功能**:
- ✅ Confidential/Subcontracted Yes/No 可编辑
- ✅ Requested Testing 两列表格可编辑
- ✅ 支持添加/删除/复制行
- ✅ Additional Information 可编辑
- ✅ 所有更改通过 Save Draft 持久化

**修改功能**:
- 布局从三列并行改为垂直堆叠
- Consent Row 水平排列
- 表格 Actions 列使用图标按钮

### 3.2 数据影响

**新增字段**:
- `requested_testing_rows`: 结构化行数据
- 保持向后兼容的 `requested_testing` 扁平字段

**数据流**:
1. 后端解析 → draft payload 包含结构化数据
2. 前端展示 → 渲染可编辑表格
3. 用户编辑 → 提交结构化数据
4. 后端保存 → 更新 manual_overrides
5. 同步更新 → flattened 兼容性字段

### 3.3 测试影响

**修改的测试**:
- `test_task081_precheck_selects_use_backend_lookup_options`: 更新期望的组件名

**测试结果**:
- ✅ 46 个单元测试全部通过
- ✅ 前端构建成功无错误

---

## 四、验证方式

### 4.1 自动化测试

```powershell
# 运行相关测试
py -m pytest tests\unit\test_intake_case_review_service.py `
  tests\integration\test_manual_intake_api.py `
  tests\unit\test_frontend_shell_files.py -q

# 前端构建
cd frontend
npm run build
```

### 4.2 手动冒烟测试

1. **布局验证**:
   - [x] Consent Row 两个问题水平排列
   - [x] 标签和 Yes/No 选项紧密排列（无巨大间隔）
   - [x] Requested Testing 全宽表格
   - [x] "+ Add Row" 按钮与标题同行
   - [x] Additional Information 全宽文本域

2. **功能验证**:
   - [x] Radio buttons 可点击切换
   - [x] 表格单元格可编辑
   - [x] Add Row 添加新行
   - [x] Edit 图标聚焦到行
   - [x] Copy 图标复制行
   - [x] Delete 图标删除行
   - [x] Save Draft 持久化所有更改

3. **响应式验证**:
   - [x] 宽屏：Consent Row 水平双列
   - [x] 窄屏（<900px）：Consent Row 垂直堆叠

---

## 五、已知限制

1. **表格单元格高度**: 使用 `rows={1}` 的 textarea，长文本会自动扩展，但初始高度较紧凑
2. **删除限制**: 至少保留一行，防止空表格
3. **兼容性**: 保持 `requested_testing` 扁平字段以支持现有的 precheck blocker 检查

---

## 六、后续建议

1. **表格优化**: 考虑为长文本实现自动高度调整
2. **键盘导航**: 增强表格内的 Tab 键导航体验
3. **撤销功能**: 考虑添加行级别的撤销操作
4. **批量操作**: 未来可支持批量添加/删除行

---

## 七、相关文件索引

**核心实现文件**:
- `backend/application/intake_form_selection_service.py`
- `backend/application/intake_case_review_service.py`
- `backend/api/routes_intake_review.py`
- `frontend/src/features/precheck/PrecheckLowerPanels.tsx`
- `frontend/src/pages/IntakeCaseReviewPage.tsx`
- `frontend/src/intake-case-review.css`

**类型定义文件**:
- `frontend/src/api/client.ts`
- `frontend/src/features/precheck/precheckFieldConfig.ts`
- `frontend/src/features/precheck/precheckReviewSelectors.ts`

**测试文件**:
- `tests/unit/test_frontend_shell_files.py`
- `tests/unit/test_intake_case_review_service.py`
- `tests/integration/test_manual_intake_api.py`

**计划文档**:
- `docs/archive/historical_plans/precheck_lower_panels_editable_requested_testing_plan.md`

---

**文档生成时间**: 2026-05-04  
**文档版本**: v1.1  
**状态**: 已完成并验证（包含审核修复）

---

## 八、审核修复记录

### 审核日期：2026-05-04

#### 问题 1（高优先级）：761-1366px 的旧三列布局覆盖

**问题描述**：
在 `intake-case-review.css:923` 存在旧的 media query 覆盖：
```css
@media (min-width: 761px) and (max-width: 1366px) {
  .precheck-lower-grid {
    grid-template-columns: 0.78fr 0.96fr 1.55fr;  /* 旧三列布局 */
  }
}
```

这会导致在常见的笔记本宽度（761-1366px）下，Precheck lower panels 重新变成三列并排，违背最新计划的"三段分别成行"要求。

**修复方案**：
```css
@media (min-width: 761px) and (max-width: 1366px) {
  .precheck-lower-grid {
    grid-template-columns: 1fr;  /* 改为单列垂直布局 */
  }
}
```

**修改文件**：
- `frontend/src/intake-case-review.css` (line 923)

---

#### 问题 2（中优先级）：requested_testing_rows 后端/API 持久化缺少测试

**问题描述**：
虽然 Save Draft 持久化功能已实现，但缺少针对 `requested_testing_rows` 的专项测试，无法证明结构化 rows 被正确保存和回传。

**修复方案**：
补充以下测试：

**1. 单元测试** (`tests/unit/test_intake_case_review_service.py`)

```python
def test_review_service_updates_requested_testing_rows_as_manual_overrides(tmp_path: Path) -> None:
    """Operator requested-testing row corrections are persisted and sync compatibility field."""
    # 验证：
    # 1. rows 被持久化到 parsed_fields["requested_testing_rows"]
    # 2. 兼容性字段 requested_testing 被同步更新
    # 3. 多行数据正确处理
```

```python
def test_review_service_requested_testing_rows_syncs_to_compatibility_field(tmp_path: Path) -> None:
    """When only rows are provided, requested_testing compatibility field is updated."""
    # 验证：
    # 1. 任何有值的行都被保留（不只是 test_to_be_performed 非空）
    # 2. 兼容性字段只包含非空的 test_to_be_performed
    # 3. 过滤逻辑正确
```

**2. 集成测试** (`tests/integration/test_manual_intake_api.py`)

```python
def test_review_fields_persists_requested_testing_rows(tmp_path: Path) -> None:
    """PATCH /review-fields with requested_testing_rows persists and returns rows."""
    # 验证：
    # 1. API 响应包含 requested_testing_rows
    # 2. 兼容性字段 requested_testing 正确同步
    # 3. draft.manual_overrides_json 包含结构化 rows
    # 4. 数据完整性（行数、内容）
```

**修改文件**：
- `tests/unit/test_intake_case_review_service.py` (+80 lines)
- `tests/integration/test_manual_intake_api.py` (+130 lines)

---

### 验证结果

**测试通过情况**：
```
49 passed in 1.04s
```

包括：
- ✅ 10 个 unit tests（含 2 个新增的 requested_testing_rows 测试）
- ✅ 4 个 integration tests（含 1 个新增的 API 持久化测试）
- ✅ 35 个 frontend shell tests

**前端构建**：
```
✓ built in 736ms
✓ 77 modules transformed
```

**修复确认**：
- ✅ 761-1366px 宽度下不再出现三列布局
- ✅ requested_testing_rows 完整持久化测试覆盖
- ✅ 兼容性字段同步机制验证
- ✅ API 层数据回传验证
