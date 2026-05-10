# TASK_159 执行方案（New Project 结果可见性 + Project Registry 分页热修）

## 1. 目标

1. New Project 点击申请 LTR 后，用户可在跳转后的 Project Registry 明确看到本次申请结果。
2. Project Registry 当前“20 / page”改为真实可翻页行为。

## 2. 最小改动策略

- 不改后端业务流程，仅补前端展示与状态传递。
- 使用 `sessionStorage` 做一次性结果传递（New Project -> Project Registry）。
- Project Registry 实现前端分页，不改后端接口参数。

## 3. 文件级改动

- `frontend/src/api/client.ts`
  - 完成结果类型补齐 workbook 元数据字段。
- `frontend/src/features/new-project/useNewProjectCompletion.ts`
  - 成功后写入 `sessionStorage` 快照。
- `frontend/src/pages/ProjectListPage.tsx`
  - 读取/展示结果 banner。
  - 实现分页状态、页码切换、footer 信息。
- `frontend/src/project-dashboard.css`
  - 增加结果 banner 与分页控件样式。

## 4. 验收标准

1. 申请 LTR 后进入 Project Registry 能看到明确结果（LTR 编号 + workbook 行位置信息）。
2. 列表超过 20 条时可翻页（上一页/下一页）。
3. 前端构建通过。

