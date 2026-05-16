# 2026-05-08 Sidebar Brand 布局优化

## 任务描述
优化 Sidebar 顶部品牌区域布局，使 Logo 和收起/展开按钮始终在同一行，节省空间。

## 改动详情

### 1. `frontend/src/components/layout/Sidebar.tsx`

将 `<strong>ConnLab</strong>` 改为 `<span className="brand-text">ConnLab</span>`，便于样式控制：

```tsx
<div className="sidebar-brand">
  <img className="brand-mark" src="/connlab-icon.svg" alt="" aria-hidden="true" />
  <span className="brand-text">ConnLab</span>  {/* 原 <strong> */}
  <button className="sidebar-toggle" ...>
    <UiIcon name="columns" />
  </button>
</div>
```

### 2. `frontend/src/styles.css`

#### `.sidebar-brand`
```css
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;          /* 原 12px → 10px */
  padding: 6px 4px 14px;
  border-bottom: 1px solid var(--color-border);
}
```

#### `.sidebar-toggle`
```css
.sidebar-toggle {
  display: inline-grid;
  place-items: center;
  width: 28px;        /* 原 30px → 28px */
  height: 28px;       /* 原 30px → 28px */
  margin-left: auto;
  border: 1px solid #d6e2f3;
  border-radius: 6px; /* 原 8px → 6px */
  background: #f7fbff;
  color: #5578a8;
  cursor: pointer;
  flex-shrink: 0;     /* 新增：防止被压缩 */
}
```

#### `.brand-text`（新增，替换原 `.sidebar-brand strong`）
```css
.brand-text {
  font-size: 18px;
  font-weight: 700;
  flex: 1;            /* 占据剩余空间 */
  min-width: 0;
}
```

#### 收起状态 `.sidebar-collapsed`
```css
.sidebar-collapsed .sidebar-brand {
  justify-content: center;
  gap: 6px;           /* 原 0 → 6px，Logo 和按钮间距 */
  padding: 6px 4px 10px;  /* 底部 padding 减小 */
}

.sidebar-collapsed .brand-text {
  display: none;      /* 原 .sidebar-brand strong */
}

.sidebar-collapsed .brand-mark {
  width: 32px;
  height: 32px;
}

.sidebar-collapsed .sidebar-toggle {
  margin-left: 0;     /* 移除原 margin-top: 10px */
}
```

## 效果对比

| 状态 | 改动前 | 改动后 |
|------|--------|--------|
| 展开 | Logo + 文字 + 按钮（一行） | Logo + 文字 + 按钮（一行，更紧凑） |
| 收起 | Logo 和按钮上下两行 | Logo 和按钮同一行，更省高度 |

## 验证方法
1. 刷新浏览器页面
2. 观察展开状态：Logo、ConnLab 文字、收起按钮应在一行
3. 点击收起按钮：Logo 和展开按钮应在同一行，无文字
4. 确认整体高度更紧凑

## 风险
极低 — 纯样式调整，无业务逻辑变更。

## 回滚
恢复 `Sidebar.tsx` 的 `<span>` 为 `<strong>`，并回滚 `styles.css` 相关样式即可。

---
**实施时间**：2026-05-08
**状态**：已完成
