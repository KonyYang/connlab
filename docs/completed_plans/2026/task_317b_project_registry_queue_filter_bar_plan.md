# TASK_317B Project Registry Queue Filter Bar — 可执行方案

Status: Implemented. TASK_317B is complete. Post-completion semantic correction applied: final user-facing queues are All / Planning / Matrix Needed / Ready to Test / Folder Blocked / Completed.

Date: 2026-06-13

## 1. 范围

**仅前端**，修改 `ProjectListPage.tsx`、`project-dashboard.css` 和 `tests/unit/test_frontend_shell_files.py`。

无后端变更、无 API 变更、无路由变更。

## 2. 当前代码结构

### 数据流

```
GET /api/projects/registry
  → ProjectRegistryRow[] (8 字段: project_id, ltr_number, sample_description, test_item, requestor, business_unit, status, progress, notes)
    → ProjectListPage
      → scopedRows (showCancelled 过滤)
        → metrics (5 大卡片)
        → filteredRows (搜索过滤)
          → pagedRows (分页)
            → <table>
```

### 当前状态变量

| 变量 | 类型 | 用途 |
|------|------|------|
| `rows` | `RegistryRow[]` | 原始 API 数据 |
| `search` | `string` | 搜索文本 |
| `showCancelled` | `boolean` | 显示已取消项目 |
| `currentPage` | `number` | 当前页码 |

## 3. 目标数据流

```
GET /api/projects/registry
  → ProjectRegistryRow[]
    → ProjectListPage
      → scopedRows (showCancelled 过滤)
        → queueCounts (队列计数)
        → QueueFilterBar 渲染
        → queueFilteredRows (活动队列过滤)
          → filteredRows (搜索过滤)
            → pagedRows (分页)
              → <table>
```

### 新增状态

| 变量 | 类型 | 默认值 | 用途 |
|------|------|--------|------|
| `activeQueue` | `QueueName` | `"all"` | 当前活动队列 |

## 4. 具体改动

### 4.1 ProjectListPage.tsx 改动点

#### A. 删除代码

| 行号 | 内容 | 原因 |
|------|------|------|
| 53 | `const metrics = useMemo(...)` | 不再需要大卡片数据 |
| 79-92 | `<div className="project-metric-grid">...</div>` | 移除大卡片 UI |
| 300-344 | `buildMetrics()` 函数 | 不再需要 |

#### B. 新增代码

**新增类型和常量：**

```ts
type QueueName = "all" | "planning" | "matrix_needed" | "ready_to_test" | "folder_blocked" | "completed";

const QUEUE_LABELS: Record<QueueName, string> = {
  all: "All",
  planning: "Planning",
  matrix_needed: "Matrix Needed",
  ready_to_test: "Ready to Test",
  folder_blocked: "Folder Blocked",
  completed: "Completed",
};

const QUEUE_ORDER: QueueName[] = [
  "all",
  "planning",
  "matrix_needed",
  "ready_to_test",
  "folder_blocked",
  "completed",
];
```

**新增分类函数（插入到已有辅助函数区域，约在 `isPendingReview` 之后）：**

```ts
function classifyQueue(row: RegistryRow): ClassifiedQueueName | null {
  // Completed: closed or folder_created
  if (["closed", "folder_created"].includes(row.status)) {
    return "completed";
  }
  // Matrix Needed: current DTO can prove registration but not active Matrix
  if (row.status === "ltr_registered") {
    return "matrix_needed";
  }
  if (!hasRegisteredLtr(row)) {
    return "planning";
  }
  // Current DTO lacks active Matrix and folder readiness fields. Use the
  // safest registered-project queue rather than faking precision.
  return "matrix_needed";
}
```

**注意：** `Ready to Test` 和 `Folder Blocked` 当前不能精确分类，因为 registry DTO 未暴露 `has_active_matrix`、`matrix_readiness`、`folder_readiness`、`primary_blocker` 等字段。TASK_317B 只渲染最终业务队列和保守分类，不从 generic status 猜测 active Matrix 或 folder blockers。

**完成后语义修正：** 最终用户可见队列是：

```text
All / Planning / Matrix Needed / Ready to Test / Folder Blocked / Completed
```

无 LTR 的临时规划项目是有效规划状态，归入 `Planning`。不能仅因缺少 LTR 被归入 `Matrix Needed` 或 `Folder Blocked`。

TASK_317C 仍负责 Temporary Planning Project identity、temporary display ID 和 Workbench temporary planning copy；TASK_317B 不移动或提前实现这些身份工作。

**新增 useMemo — queueCounts：**

```ts
const queueCounts = useMemo(() => {
  const counts: Record<QueueName, number> = {
    all: scopedRows.length,
    planning: 0,
    matrix_needed: 0,
    ready_to_test: 0,
    folder_blocked: 0, // documented limitation until DTO exposes readiness fields
    completed: 0,
  };
  for (const row of scopedRows) {
    const queue = classifyQueue(row);
    if (queue) {
      counts[queue] += 1;
    }
  }
  return counts;
}, [scopedRows]);
```

**新增 useMemo — queueFilteredRows（替换现有 filteredRows 在管道中的位置）：**

```ts
const queueFilteredRows = useMemo(() => {
  if (activeQueue === "all") {
    return scopedRows;
  }
  return scopedRows.filter((row) => row.status !== "cancelled" && classifyQueue(row) === activeQueue);
}, [activeQueue, scopedRows]);
```

**修改 filteredRows 依赖（从 scopedRows 改为 queueFilteredRows）：**

```ts
const filteredRows = useMemo(
  () => filterRows(queueFilteredRows, deferredSearch),  // 原来是 scopedRows
  [deferredSearch, queueFilteredRows],                    // 原来是 [deferredSearch, scopedRows]
);
```

**修改分页重置 useEffect（新增 activeQueue 依赖）：**

```ts
useEffect(() => {
  setCurrentPage(1);
}, [deferredSearch, showCancelled, activeQueue]);  // 新增 activeQueue
```

**新增 JSX — QueueFilterBar（插入到 LTR banner 之后、register-toolbar 之前）：**

```tsx
<div className="queue-filter-bar" role="tablist" aria-label="Project queue filter">
  {QUEUE_ORDER.map((queue) => (
    <button
      key={queue}
      className={`queue-filter-button${activeQueue === queue ? " queue-filter-button-active" : ""}`}
      role="tab"
      aria-selected={activeQueue === queue}
      type="button"
      onClick={() => setActiveQueue(queue)}
    >
      <span className="queue-filter-label">{QUEUE_LABELS[queue]}</span>
      <span className="queue-filter-count">{queueCounts[queue]}</span>
    </button>
  ))}
</div>
```

**Active queue display：**

不再新增 `ActiveQueueLabel`。当前队列只通过选中队列按钮的 active state 表达，避免在队列栏下方重复显示 `Showing: <Queue> Projects`。

**修改空状态（当 queueFilteredRows 为空但 scopedRows 不为空时）：**

在现有空状态判断中，在 `scopedRows.length > 0 && filteredRows.length === 0` 的情况下，如果是因为队列过滤导致的空结果（activeQueue !== "all"），应显示 "No projects in this queue" 而不是 "No matching projects"。

当前代码第 190-195 行的条件会混淆"搜索无结果"和"队列无结果"。需要区分：

```tsx
{!loading && !error && scopedRows.length > 0 && queueFilteredRows.length === 0 && activeQueue !== "all" && (
  <EmptyState
    title="No projects in this queue"
    message="Select All or another queue to see more projects."
  />
)}
{!loading && !error && queueFilteredRows.length > 0 && filteredRows.length === 0 && (
  <EmptyState
    title="No matching projects"
    message="Adjust the search text to return to the current queue view."
  />
)}
```

### 4.2 project-dashboard.css 改动点

#### A. 删除样式

删除以下 CSS 规则块（共约 92 行）：
- `.project-metric-grid`（第 13-17 行）
- `.project-metric-card`（第 19-27 行，注意第 7 行 `.project-register-panel, .project-metric-card` 需改为仅 `.project-register-panel`）
- `.project-metric-card strong, .project-metric-card span, .project-metric-card small, .register-toolbar h3, .register-toolbar p`（第 29-35 行）
- `.project-metric-card strong`（第 37-42 行）
- `.project-metric-card span:not(.metric-icon)`（第 44-50 行）
- `.project-metric-card small, .register-toolbar p`（第 52-58 行，保留 `.register-toolbar p` 部分）
- `.metric-icon`（第 60-66 行）
- `.metric-icon .ui-icon`（第 68-71 行）
- `.metric-icon-total`（第 73-76 行）
- `.metric-icon-progress`（第 78-81 行）
- `.metric-icon-review`（第 83-86 行）
- `.metric-icon-completed`（第 88-91 行）
- `.metric-icon-draft`（第 93-96 行）
- 响应式中的 `.project-metric-grid` 引用（第 412-413 行，第 432-433 行，第 463 行）

#### B. 新增样式

```css
/* Queue Filter Bar */
.queue-filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.queue-filter-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 34px;
  padding: 5px 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-surface);
  color: var(--color-ink);
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
  transition: border-color 0.15s, background 0.15s;
}

.queue-filter-button:hover {
  border-color: var(--color-primary);
}

.queue-filter-button-active {
  border-color: var(--color-primary);
  background: #eef6ff;
  color: var(--color-primary);
  font-weight: 800;
}

.queue-filter-label {
  white-space: nowrap;
}

.queue-filter-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 5px;
  border-radius: 999px;
  background: var(--color-surface-muted);
  color: var(--color-ink-muted);
  font-size: 11px;
  font-weight: 700;
}

.queue-filter-button-active .queue-filter-count {
  background: #d0e8ff;
  color: var(--color-primary);
}

/* Do not add .active-queue-label; the selected queue button is the only active queue indicator. */
```

### 4.3 test_frontend_shell_files.py 改动点

**修改函数**: `test_project_dashboard_uses_dense_registry_components`（行 703-752）

**删除的断言**（旧 metric cards 已移除）：

```python
# 删除以下 7 行断言：
assert "project-metric-grid" in list_page_source          # line 719
assert "Total projects" in list_page_source               # line 721
assert "In progress" in list_page_source                  # line 722
assert "Pending review" in list_page_source               # line 723
assert ".project-metric-card" in styles_source            # line 746
# 以下两行因 "Completed" / "Draft" 也被用于表格列名，需用更精确断言替换：
assert "Completed" in list_page_source                    # line 724 → 替换
assert "Draft" in list_page_source                        # line 725 → 替换
```

**新增的断言**（TASK_317B Queue Filter Bar）：

```python
# 替换旧的 metric 断言为 TASK_317B 新预期：
assert "queue-filter-bar" in list_page_source
assert "queue-filter-button" in list_page_source
assert "queue-filter-button-active" in list_page_source
assert "Need Action" not in list_page_source
assert "Needs Attention" not in list_page_source
assert "Package Blocked" not in list_page_source
assert "Planning" in list_page_source
assert "Matrix Needed" in list_page_source
assert "hasRegisteredLtr" in list_page_source
assert '"Ready to Test"' in list_page_source or "'Ready to Test'" in list_page_source
assert "Folder Blocked" in list_page_source
assert "Completed" in list_page_source   # 仍保留，作为队列标签
assert "active-queue-label" not in list_page_source
assert "Showing: {QUEUE_LABELS[activeQueue]} Projects" not in list_page_source
# 确认旧 cards 已移除：
assert "project-metric-grid" not in list_page_source
assert "Total projects" not in list_page_source
assert "In progress" not in list_page_source
assert "Pending review" not in list_page_source
assert "Draft" not in list_page_source
assert ".project-metric-card" not in styles_source
```

**保留的断言**（TASK_303 及 registry 核心守卫不变）：
- `ProjectStatusBadge`, `EmptyState`, `ErrorMessage`, `LoadingState`
- `listProjectRegistryRows`, `listProjectLtrs` not in
- `<table`, `LTR Number`, `Sample Description`, `Test Item`, `Status`, `Progress`, `Notes`
- `New Project`, `Filter`, `Columns`, `view-toggle`
- `showCancelled`, `visibleRowsForScope`, `cancelledRowCount`, `Show cancelled`
- `.project-table`, `.progress-cell`, `.registry-tools`, `.toolbar-button`, `.registry-scope-toggle`, `.registry-scope-note`
- `@media` responsive rules

## 5. 不变更清单

| 内容 | 原因 |
|------|------|
| `App.tsx` 路由 | 不需要 |
| 后端 API/DTO | 纯前端任务 |
| `ProjectStatusBadge` 组件 | 不需要 |
| `api/client.ts` | 不需要 |
| `showCancelled` 行为 | 保持现有逻辑 |
| 搜索逻辑 `filterRows()` | 保持现有逻辑 |
| 分页逻辑 | 保持现有逻辑 |
| Filter/Columns 按钮 | 保持 disabled 状态 |
| Open 按钮 | 保持现有行为 |
| 刷新按钮 | 保持现有行为 |
| New Project 按钮 | 保持现有行为 |
| LTR apply result banner | 保持现有行为 |

## 6. 风险

| 风险 | 缓解措施 |
|------|----------|
| Folder Blocked 始终为 0 让用户困惑 | 文档化限制；未来 TASK 可扩展 DTO |
| `ltr_registered` 项目可能还没有 active Matrix 字段 | 保守分类为 Matrix Needed，未来 DTO 再提升到 Ready to Test |
| 删除 CSS 可能影响其他页面 | 检查所有 `.project-metric-*` / `.metric-icon-*` 引用范围 |
| 静态测试 `test_project_dashboard_uses_dense_registry_components` 断言 metric grid 存在 | 方案已纳入该测试的断言更新 |

## 7. 验证步骤

```bash
# 1. TypeScript 编译
cd frontend; npm run build

# 2. 静态 shell 测试（更新后的 metric→queue 断言 + TASK_303 registry 守卫）
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "project_dashboard or task303_project_registry"
```

## 8. 文件变更汇总

| 文件 | 操作 | 预估行数变更 |
|------|------|-------------|
| `tasks/TASK_317B_PROJECT_REGISTRY_QUEUE_FILTER_BAR.md` | 新建 | +155 |
| `docs/task_317b_project_registry_queue_filter_bar_plan.md` | 新建 | +220（本文档） |
| `docs/task_board.md` | 编辑 | 行 3-6 更新 |
| `frontend/src/pages/ProjectListPage.tsx` | 编辑 | -50 行删除，+40 行新增 |
| `frontend/src/project-dashboard.css` | 编辑 | -95 行删除，+70 行新增 |
| `tests/unit/test_frontend_shell_files.py` | 编辑 | `test_project_dashboard_uses_dense_registry_components` 更新断言 |

