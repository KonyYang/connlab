# TASK_317C Temporary Project Planning Identity — 可执行方案

Status: Implemented. TASK_317C scope is complete.

Date: 2026-06-13

Post-completion amendment: clarify the first-version Projects overview table direction as `Project ID | Sample Description | Test Item | Status | Next Step | Action`. `Next Step` is informational text only, not a row-level action.

Implementation amendment: Projects overview now renders that first-version table structure. Because the registry DTO does not yet expose exact `next_step_label`, `Status` and `Next Step` are conservatively derived from the existing primary queue classification.

## 1. 范围

TASK_317C 是一个**身份展示和说明文案**任务。不新增操作入口、不实现 promotion workflow、不做月度序列号。

### In Scope

- 后端 registry DTO 新增最小只读身份字段
- 前端 Projects overview 行展示更新
- TASK_317B 队列分类语义保持对齐
- Workbench temporary planning 说明横幅

### Out of Scope

- 月度序列号 `TMP-YYYY-MM-NNNN`（未来改进）
- LTR 注册 promotion workflow
- 新 active action 按钮
- Official Project Folder, Submitted Material, Section 2, package execution, public-drive upload

## 2. 设计决策（已锁定）

### 2.1 临时 ID 策略

**V1 选择**: `TMP-<project_id 前 8 字符大写>`

```
示例:
  project_id = "2cd4b0e7ff6f4df99448c9ffdd78629f"
  → display_project_id = "TMP-2CD4B0E7"
```

**理由**: 稳定、确定性、无需迁移、无需持久化、无需并发规则、无需序列号膨胀。

**不在 V1 实现**: `TMP-YYYY-MM-NNNN`（需要月度计数器、迁移、并发控制 — 记为未来改进）。

### 2.2 Registry DTO 字段（最小集）

在 `ProjectRegistryRowResponse` 中新增以下只读字段：

| 字段 | 类型 | 含义 |
|------|------|------|
| `display_project_id` | `str` | 展示用的项目 ID：已注册 → LTR/DL 号；临时 → `TMP-XXXXXXXX` |
| `display_project_id_kind` | `str` | `"registered"` 或 `"temporary"` |
| `has_registered_ltr` | `bool` | 是否有已注册的 LTR 编号 |
| `temporary_project_id` | `str \| None` | 临时项目 ID（仅 kind=temporary 时有值） |
| `registered_ltr_number` | `str \| None` | 已注册 LTR 编号（仅 kind=registered 时有值） |

**明确不加入**: `lifecycle_mode`。它依赖 Matrix、folder、package 上下文，属于 Workbench selector/model，registry service 不应拼装。

### 2.3 队列分类边界

基于 TASK_317B 的最终业务队列，临时项目默认归入 `Planning`：

```ts
function classifyQueue(row: RegistryRow): QueueName {
  if (["closed", "folder_created"].includes(row.status)) return "completed";
  if (!hasRegisteredLtr(row)) return "planning";
  return "matrix_needed";
}
```

临时项目 `status !== "cancelled"` 且无 LTR → `planning`，不会仅因缺少 LTR 进入 `matrix_needed` 或 `folder_blocked`。

TASK_317C 不移动 TASK_317B 的队列责任。TASK_317B 负责 Projects overview 队列标签、排序、计数、过滤和分类语义；TASK_317C 负责临时规划身份、TMP display ID、注册/临时显示区分和 Workbench 临时规划文案。

TASK_317C 确保：
- 临时项目出现在 Planning
- 临时项目不出现在 Folder Blocked 或 Matrix Needed 仅因为缺少 LTR
- 不把身份字段工作提前塞进 TASK_317B

### 2.4 Workbench 行为

TASK_317C **只改文案，不新增按钮**：

- 无 LTR 项目 Workbench 显示 "Temporary Planning" 说明横幅
- 已有 Matrix/Fee 入口（如果当前 Workbench 已渲染）保持不变
- **不新增** "Register LTR Number" 按钮
- **不新增** 任何操作入口

## 3. 文件清单（确定的）

### 后端

| 文件 | 改动 |
|------|------|
| `backend/api/routes_project.py` | `ProjectRegistryRowResponse` 新增 5 个 identity 字段；`_to_registry_response()` 适配 |
| `backend/application/project_registry_summary_service.py` | `ProjectRegistryRow` dataclass 新增 5 字段；`list_rows()` 调用 identity resolver |
| `backend/application/project_identity.py` | `resolve_project_identity()` 返回类型扩展，加入 `display_project_id` / `display_project_id_kind` / `has_registered_ltr` |
| `tests/unit/test_project_registry_summary_service.py` | 新增临时项目身份测试 |
| `tests/unit/test_frontend_shell_files.py` | 新增 TASK_317C registry 字段静态守卫（可选，如已有 registry 测试则扩展） |

### 前端

| 文件 | 改动 |
|------|------|
| `frontend/src/api/client.ts` | `ProjectRegistryRow` 类型新增 5 字段 |
| `frontend/src/pages/ProjectListPage.tsx` | 表格第一列从 `businessIdentifier()` 改为 `display_project_id`，新增身份描述行；保持 TASK_317B 的业务队列语义：临时项目归入 Planning |
| `frontend/src/features/project-workbench/` | Workbench 无 LTR 时显示 "Temporary Planning" 横幅文案（如当前已有 no-LTR 分支则修改文案；如没有则新增条件渲染） |

### 文档

| 文件 | 改动 |
|------|------|
| `docs/task_board.md` | 已完成（TASK_317C proposed） |
| `tasks/TASK_317C_TEMPORARY_PROJECT_PLANNING_IDENTITY.md` | 已更新 |

## 4. 具体改动

### 4.1 project_identity.py

`resolve_project_identity()` 返回类型 `ProjectIdentity` 新增字段：

```python
@dataclass(frozen=True, slots=True)
class ProjectIdentity:
    ltr_number: str | None
    sample_description: str | None
    test_item: str | None
    operator_note: str | None
    # TASK_317C 新增:
    display_project_id: str
    display_project_id_kind: str          # "temporary" | "registered"
    has_registered_ltr: bool
    temporary_project_id: str | None
    registered_ltr_number: str | None
```

计算逻辑：
- 若 `ltr_number` 非空 → `kind="registered"`, `display_project_id=ltr_number`, `has_registered_ltr=True`, `registered_ltr_number=ltr_number`, `temporary_project_id=None`
- 若 `ltr_number` 为空 → `kind="temporary"`, `display_project_id="TMP-"+project_id[:8].upper()`, `has_registered_ltr=False`, `temporary_project_id=display_project_id`, `registered_ltr_number=None`

### 4.2 project_registry_summary_service.py

`ProjectRegistryRow` dataclass 新增 5 字段：

```python
@dataclass(frozen=True, slots=True)
class ProjectRegistryRow:
    project_id: str
    ltr_number: str | None
    sample_description: str | None
    test_item: str | None
    requestor: str
    business_unit: str | None
    status: str
    progress: int
    notes: str | None
    # TASK_317C 新增:
    display_project_id: str
    display_project_id_kind: str
    has_registered_ltr: bool
    temporary_project_id: str | None
    registered_ltr_number: str | None
```

`list_rows()` 中从 `identity` 取值填充。

### 4.3 routes_project.py

`ProjectRegistryRowResponse` 新增 5 字段，`_to_registry_response()` 适配。

### 4.4 client.ts

```ts
export type ProjectRegistryRow = {
  // ... 现有字段 ...
  display_project_id: string;
  display_project_id_kind: "temporary" | "registered";
  has_registered_ltr: boolean;
  temporary_project_id?: string | null;
  registered_ltr_number?: string | null;
};
```

### 4.5 ProjectListPage.tsx

表格第一列：

```tsx
// 替换 businessIdentifier(row) 调用:
<td className="project-no">
  {row.display_project_id}
  {row.display_project_id_kind === "temporary" && (
    <span className="registry-temp-badge">Temporary Planning</span>
  )}
</td>
```

新增 CSS：

```css
.registry-temp-badge {
  display: block;
  margin-top: 2px;
  color: var(--color-ink-muted);
  font-size: 11px;
  font-weight: 600;
}
```

表头第一列从 `LTR Number` 改为 `Project ID`。`Project ID` 显示注册 LTR/DL 编号或临时规划 ID；临时规划 ID 必须配合 `Temporary Planning` 次级标签，避免被误认为正式 LTR/DL。

**注意**: 搜索 `filterRows()` 中的 `businessIdentifier(row)` 改为 `row.display_project_id`。

#### Projects overview table direction

推荐的 first-version 表格结构：

```text
Project ID | Sample Description | Test Item | Status | Next Step | Action
```

列语义：

- `Project ID`: 替代旧 `LTR Number` 列。已注册项目显示正式 LTR/DL；临时规划项目显示 `TMP-XXXXXXXX` 和 `Temporary Planning` 次级标签。
- `Status`: 应与 TASK_317B 业务队列/状态语义对齐：`Planning`, `Matrix Needed`, `Ready to Test`, `Folder Blocked`, `Completed`。如果已有更好的 registry business status，不应只依赖 `LTR Number Registered`。
- `Next Step`: 替代早期 `Readiness / Reason` wording，用更贴近用户决策的文字说明打开 Workbench 后的可能下一步。
- `Action`: 只保留现有 `Open` 按钮。不要新增 Matrix/Fee/Test Record/Execution/Project Folder repair 等 row-level action。

`Next Step` 示例：

| Business state | Next Step example |
|----------------|-------------------|
| Temporary Planning | Continue planning |
| Matrix Needed | Open Matrix authority |
| Ready to Test | Open Execution map |
| Folder Blocked | Confirm Fee / Review request material / Complete Section 2 dates |
| Completed | No action |

`Progress` 不应在有可靠 `Next Step` 后继续作为主要用户-facing planning indicator。`Notes` 可以在后续/近旁 UI refinement 中被 `Next Step` 替代或重新定位为更具体的备注字段。

当前 TASK_317C 实现保持保守：registry DTO 尚未提供可靠的 `next_step_label`，不要在前端通过解析 Workbench、Matrix、Fee、Folder 细节来伪造精确下一步。V1 使用当前 primary queue 分类提供保守文案：`Planning -> Continue planning`, `Matrix Needed -> Open Matrix authority`, `Ready to Test -> Open Execution map`, `Folder Blocked -> Review request material`, `Completed/Cancelled -> No action`。更精确的下一步仍记录为 future DTO/read-model improvement。

未来 DTO/read-model 字段可包括：

- `primary_queue`
- `next_step_label`
- `primary_blocker`
- `has_active_matrix`
- `folder_readiness`
- `testing_readiness`

### 4.6 Workbench 横幅

**身份来源**: Workbench temporary planning banner 使用 Workbench 现有的 `latestLtr` / `hasLtr` 判定（来自 `getProject()` + `listProjectLtrs()`），不从 registry DTO 反向引入 Workbench 数据流。registry DTO 新增的 identity 字段仅供 Projects overview 页消费，Workbench 保持自己的身份判定路径。

在 Workbench 渲染中，当项目无 LTR（即 Workbench 自己判定 `hasLtr === false` 或等效条件）时，渲染说明横幅：

```tsx
{!hasRegisteredLtr && (
  <div className="temp-planning-banner">
    <strong>Temporary Planning</strong>
    <p>This project has no registered LTR Number yet. Matrix and Fee planning tools are available for feasibility, duration, and cost estimation. Official package actions require LTR registration.</p>
  </div>
)}
```

### 4.7 TASK_317B 队列分类

保持 TASK_317B 队列语义。确认：
- `status=cancelled` → 被 `queueCounts`/`queueFilteredRows` 跳过
- 无 LTR 状态 → `planning`
- 注册 LTR 但 registry DTO 尚无 active Matrix 字段 → `matrix_needed`
- `status=closed/folder_created` → `completed`
- `ready_to_test` 和 `folder_blocked` 需要未来 explicit DTO readiness 字段支持

### 4.8 测试文件

**后端新增测试**（`tests/unit/test_project_registry_summary_service.py` 扩展或新文件）:

```python
def test_temporary_project_has_temporary_identity():
    """无 LTR 项目 → display_project_id_kind=temporary, has_registered_ltr=False"""

def test_registered_project_has_registered_identity():
    """有 LTR 项目 → display_project_id_kind=registered, has_registered_ltr=True"""

def test_temporary_id_is_stable_and_derived_from_project_id():
    """TMP-XXXXXXXX 基于 project_id 前缀派生，稳定不变"""
```

**前端静态测试**（`tests/unit/test_frontend_shell_files.py` 扩展）:

```python
def test_task317c_temporary_project_identity_fields_are_wired():
    """TASK_317C: client.ts 包含 display_project_id 等新字段"""
```

## 5. 不变更清单

| 内容 | 原因 |
|------|------|
| TASK_317B 队列责任 | 由 TASK_317B 维护；TASK_317C 不重写队列标签/排序 |
| TASK_317B 队列 UI | 按钮文案、数量、行为不变 |
| `lifecycle_mode` 进入 DTO | 依赖 Workbench 上下文，registry 不应拼装 |
| `TMP-YYYY-MM-NNNN` | 需要序列号系统，V1 不实现 |
| promotion workflow | 需要单独的 TASK |
| "Register LTR Number" 按钮 | 不新增 active action |
| TASK_318 | 保留，未被消费 |

## 6. 验证步骤

```bash
# 后端测试
py -m pytest tests/unit/test_project_registry_summary_service.py -q
py -m pytest tests/integration/test_project_registry_summary_api.py -q

# 前端构建 + 静态测试
cd frontend; npm run build
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "project_dashboard or task303_project_registry or task317c"

# git 检查
git diff --check
```

## 7. 文件变更汇总

| 文件 | 操作 | 预估行数变更 |
|------|------|-------------|
| `backend/application/project_identity.py` | 编辑 | `ProjectIdentity` +5 字段，计算逻辑 ~20 行 |
| `backend/application/project_registry_summary_service.py` | 编辑 | `ProjectRegistryRow` +5 字段，`list_rows()` 取值 ~5 行 |
| `backend/api/routes_project.py` | 编辑 | `ProjectRegistryRowResponse` +5 字段，适配 ~5 行 |
| `frontend/src/api/client.ts` | 编辑 | 类型 +5 字段 |
| `frontend/src/pages/ProjectListPage.tsx` | 编辑 | 表格列改装 ~15 行 |
| `frontend/src/project-dashboard.css` | 编辑 | `.registry-temp-badge` ~6 行 |
| `frontend/src/features/project-workbench/` | 编辑 | 临时横幅 ~15 行 |
| `tests/unit/test_project_registry_summary_service.py` | 编辑 | 3 个新测试 ~30 行 |
| `tests/unit/test_frontend_shell_files.py` | 编辑 | 1 个新静态守卫 ~10 行（可选） |
