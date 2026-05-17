# TASK_211_PROJECT_WORKBENCH_RUNTIME_CONSOLE_BASELINE_REPLACEMENT

进入 TASK_211 single-task-file workflow。

创建：

```text
tasks/TASK_211_PROJECT_WORKBENCH_RUNTIME_CONSOLE_BASELINE_REPLACEMENT.md
```

不要创建额外 plan 文件。

当前任务目标：

正式开始：

```text
Project Workbench Runtime Console baseline replacement
```

注意：

TASK_211 不是：

- UI beautification
- CSS refinement
- current Workbench patching

而是：

```text
Runtime Console information architecture replacement
```

# 当前背景

TASK_201~210 已完成：

- runtime projection DTO foundation
- projection composition helper
- typed runtime snapshot API
- frontend read-only projection consumer prototype
- prototype isolation hardening

当前 Runtime projection consumption chain 已经成立：

```text
Step Token
→ Projection
→ Aggregation
→ Snapshot
→ Typed API
→ Frontend Consumer
```

因此：

Workbench UI 现在可以开始真正 Runtime-first replacement。

# TASK_211 核心原则

继续严格保持：

```text
Projection != Domain Identity
Runtime Projection is not source of truth.
Projection composition must remain independently evolvable.
```

Workbench 必须：

```text
consume runtime projection
```

不得：

```text
own runtime state
```

# TASK_211 真正目标

建立：

```text
Runtime Console Skeleton
```

而不是完整功能系统。

重点：

```text
replace Workbench IA
```

不是：

```text
finish Workbench product
```

# Runtime Console Skeleton 目标结构

目标方向：

```text
Top Runtime Summary
↓
Matrix Overview Runtime Surface
↓
Step Workspace Entry Surface
↓
Runtime Attention Surface
↓
Deferred Setup / Output Secondary Surface
```

# TASK_211 允许范围

允许：

- 新 Runtime Console layout skeleton
- Runtime Summary surface
- Matrix Overview projection surface
- Step Workspace entry/navigation surface
- Runtime Attention placeholder surface
- projection snapshot consumption wiring
- removing/replacing setup-heavy primary layout sections
- creating new Runtime Console-oriented components
- frontend routing/layout restructuring related to Workbench only

允许修改：

- ProjectWorkbenchPage
- related Workbench layout components
- runtime projection consumer hooks
- frontend layout structure
- related CSS modules/files

# TASK_211 禁止范围

禁止：

- Matrix Editor implementation
- execution engine
- orchestration system
- write/mutation flow
- report generation system
- evidence upload workflow
- websocket/background sync
- persistence redesign
- backend architecture expansion
- replacing runtime projection API contracts
- StepInstance ORM expansion
- approval/setup system redesign

# 特别重要

当前旧 Workbench：

```text
setup-first
```

必须转向：

```text
runtime-first
```

但：

不要一次性实现完整 Runtime Console。

TASK_211 只建立：

```text
Runtime Console baseline skeleton
```

# 当前 Workbench 处理原则

允许：

- 删除旧 setup-heavy primary hierarchy
- 降级 setup/output sections 为 secondary surfaces
- 移除明显与 Runtime Console 冲突的 IA

禁止：

- Big Bang full rewrite
- 全系统 UI 重构
- Matrix Editor 混入 Workbench

# Matrix Editor Boundary

继续保持：

```text
Workbench = Runtime Console
Matrix Editor = Definition Studio
```

Matrix definition editing 不得重新回到 Workbench。

# Validation

TASK_211 必须验证：

- frontend build passes
- runtime projection consumption still works
- Matrix Overview renders through projection
- Workbench no longer visually behaves like setup dashboard
- runtime surfaces become primary hierarchy
- no backend regression introduced

# Acceptance Direction

TASK_211 完成后：

用户应明显看到：

```text
旧 Workbench
→
Runtime Console skeleton
```

而不是：

```text
旧页面的小修小补
```

# Stop Condition

TASK_211 完成后停止。

不要自动进入：

- Matrix Editor implementation
- runtime engine
- attention orchestration
- report workflow redesign
- evidence system redesign

下一阶段将单独规划：

- Matrix Overview runtime interaction refinement
- Step Workspace interaction flow
- Runtime Attention aggregation
- Setup/Output secondary surface separation
