# Sidebar 固定滚动方案

## 问题描述
当前页面滚动时，左侧导航栏（Sidebar）会随页面一起滚动。用户希望左侧导航栏保持固定，只有右侧内容区滚动。

## 当前布局结构

```
.app-shell (grid)
├── .sidebar (左侧导航栏)
└── .app-workspace (右侧工作区)
    ├── .top-bar (顶部栏)
    └── .main-work-area (主内容区)
```

## 方案设计

### 核心思路
使用 CSS `position: sticky` 让 Sidebar 固定在视口左侧，同时让 `.app-workspace` 成为独立的滚动容器。

### 改动点

#### 1. styles.css - Sidebar 样式修改

```css
.sidebar {
  /* 新增 sticky 定位 */
  position: sticky;
  top: 0;
  align-self: start;
  /* 移除 min-height: 100vh，改为 height: 100vh */
  height: 100vh;
  /* 其他样式保持不变 */
}
```

#### 2. styles.css - App Workspace 样式修改

```css
.app-workspace {
  min-width: 0;
  /* 新增：成为独立滚动容器 */
  height: 100vh;
  overflow-y: auto;
}
```

### 技术细节

| 属性 | 作用 |
|------|------|
| `position: sticky` | 让 Sidebar 在滚动时固定在视口顶部 |
| `top: 0` | 固定位置为视口顶部 |
| `align-self: start` | 在 Grid 布局中防止 Sidebar 被拉伸 |
| `height: 100vh` | 限制高度为视口高度 |
| `overflow-y: auto` | 让右侧内容区独立滚动 |

### 兼容性考虑

- `position: sticky` 在现代浏览器中支持良好（Chrome 56+, Firefox 52+, Safari 13+, Edge 79+）
- 项目使用 Vite + React，目标为现代桌面环境（Windows），无需担心兼容性

### 验证方法

1. 启动前端开发服务器
2. 打开 New Project 页面（内容较长的页面）
3. 滚动鼠标滚轮
4. 验证：左侧导航栏保持不动，右侧内容区正常滚动

## 风险与回滚

- **风险**：极低，纯 CSS 改动，不影响业务逻辑
- **回滚**：删除新增的 3 行 CSS 即可恢复

## 文件变更

| 文件 | 变更类型 |
|------|----------|
| `frontend/src/styles.css` | 修改 `.sidebar` 和 `.app-workspace` 样式 |

---

**状态**：待审批
