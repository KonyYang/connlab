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
