# TASK_249 Plan - Matrix Editor Seed And Header Simplification

## 1. Task Gate (Anti-Skip Protocol)

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task on board: `TASK_248_REVERT_MATRIX_EDITOR_GROUP_NAME_WRAP` (pending review)
- Why this plan is allowed now: user提出了新的 Matrix Editor UI 收敛需求，需要先形成可执行方案并等待明确批准，之后才能实施代码修改。

## 2. Requested Outcome

基于用户提供的目标图，收敛 Matrix Editor 编辑区：

1. 默认分组名从 `G1` 改为 `1`
2. 移除 `Selection: none` 及其说明文案（`Header and first five columns are structurally fixed.`）
3. 移除编辑区顶部过滤栏（`Matrix Version / Group / Filter / Section`）

## 3. Scope Boundary

### In Scope

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/workbench.css`（仅当删除顶部块后需要微调间距）
- `tests/unit/test_frontend_shell_files.py`（补充或更新静态断言）

### Out of Scope

- Backend/API/domain/persistence
- Matrix 编辑规则（行列操作、校验、上下文菜单、步骤预览逻辑）
- Workbench 其它页面和路由行为
- TASK_248 范围内的 group name wrap 回滚以外行为（除非用户将本任务明确设为当前激活任务）

## 4. Code-Level Change Design

## 4.1 Initial Seed Group Name

- 位置：`buildInitialGroupColumns()`
- 当前：`[{ id: "group-1", name: "G1" }]`
- 目标：`[{ id: "group-1", name: "1" }]`

## 4.2 Remove Top Filter Bar

- 位置：`MatrixEditorWorkspace` JSX 顶部控制区（包含 Matrix Version/Group/Filter/Section）
- 动作：
  - 删除该控制区 JSX
  - 清理仅用于该控制区的局部 state（若存在）
  - 保留与网格编辑直接相关的状态和交互

## 4.3 Remove Selection Status Hint Block

- 位置：显示 `Selection: none` / `Row selected` / `Group selected` 的提示条区域
- 动作：
  - 删除整块提示 JSX
  - 清理其依赖的仅显示用途变量（如存在）
  - 不影响当前行/列真实选中状态及高亮行为

## 4.4 Style Cleanup (If Needed)

- 如删除两个顶部区域后产生多余留白，仅做最小 CSS 清理：
  - 删除孤立 class
  - 微调编辑区上边距/间距

## 5. Risks And Mitigations

1. 风险：删除提示块误伤选中逻辑  
   - 规避：仅删除展示层 JSX，不删除 `selectedRowId`/`selectedGroupId` 的业务用途（高亮、右键目标）。
2. 风险：静态测试仍要求旧文案存在  
   - 规避：同步更新 `tests/unit/test_frontend_shell_files.py` 断言。
3. 风险：布局塌陷或顶部间距异常  
   - 规避：最小化 CSS 调整，并执行前端 build 验证。

## 6. Validation Plan

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor or task24"
```

手工验证（矩阵编辑页）：

1. 首屏不显示 `Matrix Version / Group / Filter / Section`
2. 不显示 `Selection: none` 及附属说明
3. 首行分组头默认为 `1`
4. 行选中、列选中高亮与右键菜单仍可用

## 7. Acceptance Criteria

- 页面不再渲染顶部过滤栏
- 页面不再渲染 `Selection` 状态提示条
- 初始分组名称默认为 `1`（非 `G1`）
- `npm run build` 通过
- 相关静态测试通过（至少覆盖本次 UI 变更断言）

