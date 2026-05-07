# Email Source Panel 卡片合并与拖拽支持

> 日期: 2026-05-07  
> 需求: 将 New Project 页面左侧的两个功能卡片（Import source + Email information）合并为一个

## 问题回溯

初次实现因 `import type { ... useState }` 使用 `import type` 导入 `useState`（hook 值不是类型），导致运行时崩溃，页面不显示。

## 变更文件

| 文件 | 变更类型 |
|------|----------|
| `frontend/src/features/intake/IntakeSourcePanel.tsx` | 重构（合并卡片 + 拖拽） |
| `frontend/src/intake-inbox.css` | 新增样式 |

## IntakeSourcePanel.tsx 变更

### 导入修正

```typescript
// ❌ 之前（导致崩溃）
import type { ChangeEvent, ReactElement, RefObject, useState } from "react";

// ✅ 修正后
import { useState, type ChangeEvent, type DragEvent, type ReactElement, type RefObject } from "react";
```

**关键：** `useState` 是 hook 函数值，必须用 `import { useState }`（值导入），不能用 `import type`。

### 组件结构变更

**删除**:
- 两个独立 `<section className="intake-panel">` 卡片
  - "Import source" 卡片（按键 "Import from Outlook"）
  - "Email information" 卡片（From/Subject/Date）

**新增**:
- **统一卡片**：标题 "Email source"
- **动态按钮文案**：
  - `packageImport === null` → "Import msg"
  - `importing === true` → "Importing from Outlook..."（disabled）
  - `packageImport !== null` → "Replace msg"
- **拖拽区域**（`<div className="email-drop-zone">`）：
  - 未导入：显示 "Drop a .msg email file here" + upload 图标
  - 拖拽激活：蓝色虚线边框 + 浅蓝背景
  - 已导入：显示 Email 信息（From/Subject/Date）
- **拖拽逻辑**：
  - `onDragOver` / `onDragLeave`：控制视觉反馈
  - `onDrop`：校验 `.msg` 扩展名，构造合成 ChangeEvent 触发 `onMsgFileChange`

## intake-inbox.css 新增样式

| 选择器 | 用途 |
|--------|------|
| `.email-source-panel` | 合并卡片的 grid 容器 |
| `.email-source-header` | 卡片头部（标题 + 按钮）Flex 布局 |
| `.email-drop-zone` | 拖拽区域（虚线边框） |
| `.email-drop-zone-prompt` | 未导入时的提示文字样式 |
| `.email-drop-zone-active` | 拖拽悬停状态（蓝色边框） |
| `.email-drop-zone-filled` | 已导入时区域样式（实线边框） |

## 验证

- TypeScript 编译：✅ 零错误
- 0 lint 错误

## UI 变化对比

### 变更前
```
┌──────────────────────────────┐
│ Import source                │
│  [Import from Outlook]       │
└──────────────────────────────┘
┌──────────────────────────────┐
│ Email information            │
│ From:    xxx@xxx.com         │
│ Subject: xxx                 │
│ Date:    2026-05-07          │
└──────────────────────────────┘
```

### 变更后
```
┌──────────────────────────────┐
│ Email source          [Import msg] │
│ ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐ │
│ │  ↑ Drop a .msg email     │ │
│ │     file here             │ │
│ └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘ │
└──────────────────────────────┘
          ↓ 导入后 ↓
┌──────────────────────────────┐
│ Email source          [Replace msg] │
│ ┌──────────────────────────┐ │
│ │ From:    xxx@xxx.com      │ │
│ │ Subject: xxx               │ │
│ │ Date:    2026-05-07       │ │
│ └──────────────────────────┘ │
└──────────────────────────────┘
```

---

# 后续修改记录（同一次对话）

> 以下修改均发生在 2026-05-07 同一次对话中。

---

## 2. Import 按钮文案简化

**修改前**：`"Import msg"` / `"Replace msg"` / `"Importing from Outlook..."`（动态切换）

**修改后**：始终显示 `"Import"`，因为信封图标已足够表达含义

**涉及文件**：`frontend/src/features/intake/IntakeSourcePanel.tsx`

---

## 3. 附件文件类型图标：文字 → SVG 图标

**修改前**：附件列表中文件类型用文字标签（`W` / `PDF` / `MSG` / `IMG`）显示

**修改后**：替换为 16x16 的 SVG 图标

| 类型 | 图标 | 颜色 |
|------|------|------|
| Word | 文档折页 + 线条标记 | 蓝色 |
| PDF | 文档折页 + 圆形标记 | 红色 |
| Image | 风景画（矩形 + 山/太阳） | 绿色 |
| MSG | 信封轮廓 | 黄色 |
| 其他 | 文档折页 | 灰色 |

**涉及文件**：
- `frontend/src/features/intake/AttachmentList.tsx` — 新增 `fileChipIcon()` 函数
- `frontend/src/intake-inbox.css` — `.file-chip` 从文字样式改为 32x28px 图标容器

---

## 4. 附件图标背景框移除

**修改前**：每个文件图标有 32x28px 的背景色框，预留 `42px` 列宽

**修改后**：去掉背景框、固定宽高和圆角，图标仅占用自身的 16x16 空间；网格列宽从 `42px` 改为 `auto`

**涉及文件**：
- `frontend/src/intake-inbox.css` — `.file-chip` 改为 `inline-flex` 仅保留颜色；拆分 `.file-chip-*` 与 `.detail-file-icon-*` 选择器；网格 `42px` → `auto`

---

## 5. 附件 Import 按钮：文字 → `>` 图标

**修改前**：`.docx` 附件右侧显示 "Import" 文字按钮

**修改后**：替换为 26x26px 的 `>` 右箭头 SVG 图标按钮，`aria-label="Import into editor"`

**修改前**：
```
[  Import  ]  (约 60px + padding)
```

**修改后**：
```
[>]  (26x26 紧凑按钮)
```

**涉及文件**：
- `frontend/src/features/intake/AttachmentList.tsx` — 替换按钮内容为 SVG
- `frontend/src/intake-inbox.css` — `.attachment-import-button` 改为 26x26px 极简样式

---

## 6. Import 图标按钮样式简化

**修改前**：自定义边框 + 背景色 + hover 蓝色边框

**修改后**：无边框、透明背景、灰色图标（继承上层样式），与原来 "Import" 文字按钮风格一致

**涉及文件**：`frontend/src/intake-inbox.css`

---

## 7. Test Sample Information 表格：删除 Actions 列

### 修改前
- 表格 8 列数据 + "Actions" 列（10%宽度）
- 每行右侧有复制/删除两个图标按钮
- "Add Row" 文字按钮在标题栏

### 修改后
- 删除 `<col className="sample-col-actions" />`、`<th>Actions</th>`、每行的 `<td>` 操作列
- Contact Base Material + Contact Plating 列宽从各 `9%` → 各 `14%`
- 新增 `selectedRowIndex` 本地状态，点击行选中（蓝色高亮 `.sample-row-selected`）
- 标题栏工具栏：`[复制] [删除] [+]` 三个图标按钮
  - 复制：有选中行时可用
  - 删除：有选中行且行数 >1 时可用，删除后清除选中
  - `+`：替代原来的 "Add Row" 文字按钮

### 涉及文件
- `frontend/src/features/precheck/PrecheckSampleTable.tsx` — 组件重构
- `frontend/src/intake-case-review.css` — 删除 `.sample-col-actions`、`.sample-row-actions`；新增 `.sample-table-toolbar`、`.sample-tool-button`、`.sample-row-selected`；更新列宽和 `.sample-add-button` 样式

---

## 8. Description of Requested Testing 表格：相同改动

与 Test Sample Information 表格完全一致的改动：
- 删除 `<th>Actions</th>` 和每行的 `<td>` 操作按钮
- 新增 `selectedRowIndex` 状态 + 选中行高亮
- 标题栏工具栏复用 `.sample-table-toolbar` / `.sample-tool-button` / `.sample-add-button` 样式
- 两列宽度重分配：`60%` + `40%`（原 `58%` + `30%` + `112px`）
- 删除 `.requested-testing-row-actions` 样式（约 30 行 CSS）

### 涉及文件
- `frontend/src/features/precheck/PrecheckLowerPanels.tsx` — `RequestedTestingPanel` 组件重构
- `frontend/src/intake-case-review.css` — 列宽调整、删除旧样式

---

## 9. 导入新邮件后残留旧文件名显示 Bug 修复

**问题**：当导入一个新邮件时，右侧"Application information"区域有时仍显示上一封邮件的申请单文件名或其他附件的文件名。

**根因**：`handleMsgFileChange` 导入新邮件时没有清除 `importMessage` 状态，`importedFormDisplayName` 的 memo 因 `importMessage` 非空而优先返回旧值。

**修复 1**：在 `handleMsgFileChange` 中导入新邮件前调用 `setImportMessage(null)`

**修复 2**：删除 `importedFormDisplayName` memo 中的 `selectedAssetId` 回退查找逻辑（之前当 `selectedWordAssetId` 为 null 时，会取第一个附件名称显示）。现在语义清晰：只有用户主动通过 Import 按钮导入了 Word 申请表后，才显示申请表名，否则不显示任何内容。

### 涉及文件
- `frontend/src/pages/IntakeInboxPage.tsx`

---

## 汇总：本次会话修改的所有文件

| 文件 | 修改内容 |
|------|----------|
| `frontend/src/features/intake/IntakeSourcePanel.tsx` | 合并卡片 + 拖拽 + 按钮简化 |
| `frontend/src/features/intake/AttachmentList.tsx` | SVG 图标 + 图标按钮 |
| `frontend/src/features/precheck/PrecheckSampleTable.tsx` | 删除 Actions 列 + 工具栏 |
| `frontend/src/features/precheck/PrecheckLowerPanels.tsx` | 删除 Actions 列 + 工具栏 |
| `frontend/src/pages/IntakeInboxPage.tsx` | 修复 importMessage 残留 bug |
| `frontend/src/intake-inbox.css` | 多组样式新增/调整 |
| `frontend/src/intake-case-review.css` | 多组样式新增/调整 |
