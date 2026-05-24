# TASK_252CI_MATRIX_EDITOR_IMPORT_MATRIX_LABEL_AND_LAYOUT_ALIGNMENT

## Status

Planned (awaiting user approval).

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_252CI_MATRIX_EDITOR_IMPORT_MATRIX_LABEL_AND_LAYOUT_ALIGNMENT`

## Why This Task Is Allowed Now

- User explicitly requested strict `Import Matrix` wording and TASK_252A/252B-aligned top action layout.
- This is a bounded UI refinement on top of restored import flow.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

## Objective

1. Top action button文案严格恢复为 `Import Matrix`。
2. 顶部动作区布局对齐 TASK_252A/252B 收敛结果：主操作区仅保留导入入口与 `Undo`。
3. 不改变导入能力：仍走 `.docx` 选择 -> 预览 -> `Replace/Append`。

## Scope

Allowed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/workbench.css`（仅必要样式）
- `tests/unit/test_frontend_shell_files.py`（如需补断言）

Forbidden:

- backend/API变更
- 解析逻辑变更
- 新流程或新格式支持

## Acceptance Criteria

- 顶部按钮显示 `Import Matrix`。
- 顶部布局仅保留导入主入口与 `Undo`（无占位控制项）。
- 点击 `Import Matrix` 仍可选择 `.docx` 并触发预览。
- 构建与相关前端测试通过。

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor or task252"
```
