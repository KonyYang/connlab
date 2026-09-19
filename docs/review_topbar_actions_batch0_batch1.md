# 提交审核：TopBar 插槽机制收敛（批次 0 / 批次 1）

- **仓库**：`D:\PythonProject\connlab`
- **分支 / HEAD**：`master` @ `68b1dbb1`（2026-09-19 20:33:21 +0800，"refactor(matrix-editor): 统一预览 PDF 生成流程并补充加载态"）
- **本次改动状态**：**全部未提交**，仍在工作区（见"第 8 节 待审核的实际工作区状态"）
- **审核对象**：批次 0（宿主发现时机）+ 批次 1（用 Context 取代 `document.querySelector`）
- **未包含**：批次 2（把 "Create project folder" 迁入 Folder Actions 卡片）——**尚未实施**，仅出了方案文档

---

## 1. 一句话摘要

改动前，三个页面组件各自用 `useEffect` + `document.querySelector("[data-top-bar-actions]")` 去全文档搜索 TopBar 的插槽容器，再把按钮 `createPortal` 进去。本次把它换成 React Context：`TopBar` 用回调 ref 把插槽元素注册给 `AppShell` 持有的 Provider，消费者从 context 读。顺带消除了首帧闪动、修掉了"全文档第一个宿主"的错配风险，并首次为"落位"这件事补上回归测试。

---

## 2. 背景：改动针对的既有机制

`68b1dbb1` 把 Workbench 的首行按钮搬到了全局 TopBar（用户原话："Workspace 的首行进行了修改，把原来它下面的按钮内容都移到这里了"）。其实现是一套**更早就存在的插槽约定**，被该提交推广到 Workbench 与 ProjectList：

**宿主**（`frontend/src/components/layout/TopBar.tsx`）——只有两列 grid：

```jsx
<header className={`top-bar top-bar-${activeRoute}`}>
  <div className="top-bar-title-slot"><h1 title={title}>{title}</h1></div>
  <div className="top-bar-actions" data-top-bar-actions="true" aria-label="Page actions">{actions}</div>
</header>
```

**注入侧**——三个使用方共用同一套三步契约：

```tsx
const [topBarActionsRoot, setTopBarActionsRoot] = useState<HTMLElement | null>(null);
useEffect(() => {
  setTopBarActionsRoot(document.querySelector<HTMLElement>("[data-top-bar-actions]"));
}, []);
...
{topBarActionsRoot ? createPortal(node, topBarActionsRoot) : node}
```

三个使用方：

| 组件 | portal 进去的内容 |
|---|---|
| `features/project-workbench/ProjectWorkbenchLayout.tsx` | 整条 workbench 命令栏（返回 + 项目身份 + Matrix Editor / Fee Evaluation / Basic Information / Create project folder / Test Report Draft） |
| `features/project-workbench/ProjectWorkbenchExecutionConsole.tsx` | "Show / Hide Actions" 开关 |
| `pages/ProjectListPage.tsx` | registry 工具条 `.register-toolbar` |

**改动前识别出的三个隐患**（用户要求一并消除）：

1. `AppShell` 有一个 `topBarActions?: ReactNode` prop，`App.tsx` 从未传它——两条并存的机制（prop 通道 + portal 通道）容易误导后来人。
2. 用的是 `useEffect` 而非 `useLayoutEffect`，且初始 state 为 `null` → **首帧按钮渲染在页面原位，绘制后才跳到首行**，存在可见布局闪动。
3. `document.querySelector` 取的是**全文档第一个**宿主，多 TopBar 场景会错配。

---

## 3. 调研阶段的关键发现（决定实施顺序）

**F1 — 落位行为零测试覆盖（改动前）。**
`ProjectWorkbenchLayout.test.tsx:1548` 的 `renderWorkbench` 只渲染 `ProjectWorkbenchLayout` 本身，**没有挂载 `AppShell`/`TopBar`**，因此 `querySelector("[data-top-bar-actions]")` 在该文件 55 个用例里**恒为 `null`**，全部走"查不到宿主就原地渲染"的兜底分支。而测试 helper 限定的 `aria-label="Project Workbench actions"` 是 portal 节点**内部**的 div，两种分支都能命中——测试结构上无法区分。

> 结论：**绿灯不代表 portal 路径被验证**；任何破坏落位的改动都不会被现有测试拦住。

结论中的一条重要推论：**不应针对旧的 `document.querySelector` 机制写落位测试**——批次 1 改为 Context 后，"组件脱离 provider 渲染"是设计而非缺陷，那种测试写完立刻失效。落位测试应当作为批次 1 的第一部分，对着新机制写。

**F2 — `Create project folder` 按钮忽略了自己派生的 label（既有缺陷，本次未修）。**
`ProjectWorkbenchLayout.tsx:291-302` 已经算出 `label`（folder 就绪时 `"Update project folder"`，否则 `"Create project folder"`），但第 522 行**硬编码** `"Create project folder"`，`label` 字段从未被读取 → **"Update project folder" 永远不会出现**。另：非 active-Matrix 分支的 `disabled: true` 是写死的（第 298 行）。→ 归入批次 2。

**F3 — 测试对首行按钮的耦合是硬耦合。**
`ProjectWorkbenchLayout.test.tsx:66` 的 helper：

```tsx
function getWorkbenchActionButton(name: string): HTMLButtonElement {
  const actionBar = screen.getByLabelText("Project Workbench actions");  // ← 限定作用域
  const button = Array.from(actionBar.querySelectorAll("button")).find(...)
  if (!button) throw new Error(`Project Workbench action button not found: ${name}`);
}
```

它被调用约 15 次（全是 `"Create project folder"`），另有约 7 处 `getByRole`、4 处断言 actionBar 文本顺序的正则。→ 批次 2 会打断约 26 处断言，这也是批次 2 成本高于批次 1 的原因。

**F4 — `AppShell.topBarActions` 其实已经接线**：`AppShell.tsx:49` 把它传给了 `TopBar.actions`，只是 `App.tsx:231-237` 没传该 prop。
→ 这直接决定了处理方式：**不要单独删掉它，它是批次 1 的落点**（换成 Context 后它从"公开的死接口"变为"内部实现"）。

---

## 4. 批次 0：宿主发现时机（已实施）

### 4.1 改动清单

| 文件 | 改动 |
|---|---|
| `frontend/src/features/project-workbench/ProjectWorkbenchExecutionConsole.tsx` | `useEffect` → `useLayoutEffect`（该文件唯一调用点，import 一并替换） |
| `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx` | import 追加 `useLayoutEffect`；调用点替换 |
| `frontend/src/pages/ProjectListPage.tsx` | **拆分 effect**：数据加载留在 `useEffect`，只把宿主查询抽到独立的 `useLayoutEffect` |
| `frontend/src/components/layout/TopBar.test.tsx` | `git add`（此前 untracked） |

### 4.2 一个刻意的选择

`ProjectListPage` 那处**没有整体替换**。原来的 `useEffect` 里混着三件事：

```tsx
useEffect(() => {
  void refreshProjects();
  setLastLtrApplyResult(readLastLtrApplyResult());
  setTopBarActionsRoot(document.querySelector<HTMLElement>("[data-top-bar-actions]"));
  return () => {refreshEpoch.current += 1;};
}, []);
```

整体替换会把 `refreshProjects()`（网络副作用）拖进 layout effect。因此只把宿主查询拆出来，网络请求留在原处。

---

## 5. 批次 1：用 Context 取代 document.querySelector（已实施）

### 5.1 新增文件：`frontend/src/components/layout/TopBarActionsContext.tsx`

> 这是本仓库**第一个 React Context**（改动前全库 `createContext` 零引用）。

```tsx
import {
  createContext, useCallback, useContext, useMemo, useState,
  type ReactElement, type ReactNode,
} from "react";

type TopBarActionsContextValue = {
  host: HTMLElement | null;
  registerHost: (node: HTMLElement | null) => void;
};

const TopBarActionsContext = createContext<TopBarActionsContextValue | null>(null);

export function TopBarActionsProvider({ children }: { children: ReactNode }): ReactElement {
  const [host, setHost] = useState<HTMLElement | null>(null);
  const registerHost = useCallback((node: HTMLElement | null) => setHost(node), []);
  const value = useMemo(() => ({ host, registerHost }), [host, registerHost]);
  return (
    <TopBarActionsContext.Provider value={value}>{children}</TopBarActionsContext.Provider>
  );
}

export function useTopBarActionsRoot(): HTMLElement | null {
  return useContext(TopBarActionsContext)?.host ?? null;
}

export function useTopBarHostRegistration(): ((node: HTMLElement | null) => void) | null {
  return useContext(TopBarActionsContext)?.registerHost ?? null;
}
```

**设计要点（请重点审核）**：注册采用**回调 ref + provider state**，而不是"消费者在 layout effect 里读共享 ref 对象"。理由是后者依赖兄弟节点的 effect 执行顺序——若消费者 effect 先跑而 `slotRef.current` 尚未挂上，此后 effect 依赖不变，会导致**永久渲染在原地**。回调 ref 在 commit 阶段触发，`setState` 会被 React 在 paint 前同步冲掉，首帧闪动仍被消除。

### 5.2 `TopBar.tsx`：插槽挂 ref

```diff
+import { useTopBarHostRegistration } from "./TopBarActionsContext";
 ...
   const title = titleOverride ?? context.title;
+  const registerHost = useTopBarHostRegistration();
   return (
     <header className={`top-bar top-bar-${activeRoute}`}>
       <div className="top-bar-title-slot">
         <h1 title={title}>{title}</h1>
       </div>
-      <div className="top-bar-actions" data-top-bar-actions="true" aria-label="Page actions">{actions}</div>
+      <div
+        className="top-bar-actions"
+        ref={registerHost}
+        data-top-bar-actions="true"
+        aria-label="Page actions"
+      >
+        {actions}
+      </div>
     </header>
   );
```

### 5.3 `AppShell.tsx`：包 Provider + 删除无调用方的 prop ⚠️

```diff
 import { Sidebar } from "./Sidebar";
 import { TopBar } from "./TopBar";
+import { TopBarActionsProvider } from "./TopBarActionsContext";

 type AppShellProps = {
   activeRoute: string;
   topBarTitle?: string;
-  topBarActions?: ReactNode;
   children: ReactNode;
   ...
```

```diff
   return (
-    <div className={`app-shell${sidebarCollapsed ? " app-shell-sidebar-collapsed" : ""}`}>
-      <Sidebar ... />
-      <div className="app-workspace">
-        <TopBar activeRoute={activeRoute} titleOverride={topBarTitle} actions={topBarActions} />
-        <main className="main-work-area">{children}</main>
+    <TopBarActionsProvider>
+      <div className={`app-shell${sidebarCollapsed ? " app-shell-sidebar-collapsed" : ""}`}>
+        <Sidebar ... />
+        <div className="app-workspace">
+          <TopBar activeRoute={activeRoute} titleOverride={topBarTitle} />
+          <main className="main-work-area">{children}</main>
+        </div>
       </div>
-    </div>
+    </TopBarActionsProvider>
   );
```

> ⚠️ **这是本次唯一一处 API 删除**，请审核者重点判断：删除了导出组件 `AppShell` 的一个 prop。仓库内确认零调用方（`App.tsx:231-237` 从未传过），但若它对外部/其他分支有含义，则应改为保留兼容。

### 5.4 三个使用方：三件套 → 一行 hook

以 `ProjectWorkbenchLayout.tsx` 为例（另两个同构）：

```diff
 import { useEffect, useRef, useState, type ReactElement } from "react";
 import { createPortal } from "react-dom";
+import { useTopBarActionsRoot } from "../../components/layout/TopBarActionsContext";
 ...
-  const [topBarActionsRoot, setTopBarActionsRoot] = useState<HTMLElement | null>(null);
+  const topBarActionsRoot = useTopBarActionsRoot();
 ...
-  useEffect(() => {
-    setTopBarActionsRoot(document.querySelector<HTMLElement>("[data-top-bar-actions]"));
-  }, []);
```

```diff
 // ProjectWorkbenchExecutionConsole.tsx
 import { useState, type ReactElement, type ReactNode } from "react";
-import { useEffect } from "react";
+import { useTopBarActionsRoot } from "../../components/layout/TopBarActionsContext";
 ...
-  const [topBarActionsRoot, setTopBarActionsRoot] = useState<HTMLElement | null>(null);
+  const topBarActionsRoot = useTopBarActionsRoot();
```

```diff
 // ProjectListPage.tsx
 import { useDeferredValue, useEffect, useMemo, useRef, useState, type ReactElement } from "react";
 import { createPortal } from "react-dom";
+import { useTopBarActionsRoot } from "../components/layout/TopBarActionsContext";
 ...
-  const [topBarActionsRoot, setTopBarActionsRoot] = useState<HTMLElement | null>(null);
+  const topBarActionsRoot = useTopBarActionsRoot();
 ...
   useEffect(() => {
     void refreshProjects();
     setLastLtrApplyResult(readLastLtrApplyResult());
-    setTopBarActionsRoot(document.querySelector<HTMLElement>("[data-top-bar-actions]"));
     return () => {refreshEpoch.current += 1;};
   }, []);
```

**"无宿主则原地渲染"的兜底分支全部保留**（`topBarActionsRoot ? createPortal(node, root) : node`），这正是这些组件能脱离 AppShell 单测的原因。

### 5.5 测试改动

**(a) `ProjectWorkbenchLayout.test.tsx`** — `renderWorkbench` 增加第 4 个可选参数 `wrapper`，新增 `AppShellWrapper`，并补 2 个用例：

```tsx
function AppShellWrapper({ children }: { children: ReactNode }): ReactElement {
  return (
    <AppShell activeRoute="workbench" interactionLocked={false}>
      {children}
    </AppShell>
  );
}

describe("ProjectWorkbenchLayout top bar action slot", () => {
  it("renders the workbench command bar inside the shell slot when the app shell is mounted", () => {
    renderWorkbench({}, {}, {}, AppShellWrapper);
    const slot = document.querySelector<HTMLElement>("[data-top-bar-actions]");
    expect(slot).not.toBeNull();
    expect(slot?.querySelector('[aria-label="Project Workbench actions"]')).toBeTruthy();
    expect(document.querySelector(".runtime-console-shell > .runtime-console-topbar")).toBeNull();
  });

  it("renders the workbench command bar in place when no shell slot is mounted", () => {
    renderWorkbench();
    expect(document.querySelector("[data-top-bar-actions]")).toBeNull();
    expect(
      screen.getByLabelText("Project Workbench actions").closest(".runtime-console-topbar")
    ).not.toBeNull();
  });
});
```

**(b) `ProjectListPage.test.tsx`** — 原落位用例**从"手工造宿主 div"改写为渲染真 `AppShell`**：

```diff
-  it("places registry controls in the shell top-bar action slot when available", async () => {
-    const topBarActions = document.createElement("div");
-    topBarActions.dataset.topBarActions = "true";
-    document.body.appendChild(topBarActions);
-    try {
-      mockRows([]);
-      render(<ProjectListPage onOpenProject={vi.fn()} />);
-      await screen.findByRole("button", { name: "Active" });
-      expect(topBarActions.querySelector(".register-toolbar")).not.toBeNull();
-      ...
+  it("places registry controls in the shell top-bar action slot", async () => {
+    mockRows([]);
+    render(
+      <AppShell activeRoute="projects" interactionLocked={false}>
+        <ProjectListPage onOpenProject={vi.fn()} />
+      </AppShell>
+    );
+    await screen.findByRole("button", { name: "Active" });
+    const slot = document.querySelector<HTMLElement>("[data-top-bar-actions]");
+    expect(slot).not.toBeNull();
+    expect(slot?.querySelector(".register-toolbar")).toBeTruthy();
```

> 说明：这个用例原本是**手工造一个带 `data-top-bar-actions` 的裸 div**，依赖属性发现机制；机制换成 context 后它必然失败，所以改写为走真实 Shell。改写后它验的是真实落位路径，比原来更强。

---

## 6. 验证证据

命令统一形式：`cd frontend && node node_modules/vitest/vitest.mjs run <paths>`（受管 Node 22.22.2；jsdom + globals，配置在 `frontend/vite.config.ts`）。

| 步骤 | 范围 | 结果 |
|---|---|---|
| 批次 0 定向 | 6 个文件（TopBar / Sidebar / ProjectListPage / ProjectWorkbenchLayout / ProjectFolderTaskList / ProjectRegistryManagementDialog） | **86 passed / 6 files, 12.57s** |
| 批次 1 定向 | 7 个文件（上一行 + RouteLoadBoundary） | **91 passed**（`ProjectWorkbenchLayout` 55 → 57，正是新增的 2 个） |
| **负向验证** | 临时把 `useTopBarActionsRoot` 改成 `return null`，只跑 ProjectListPage + ProjectWorkbenchLayout | **恰好 2 个落位用例失败**；兜底用例仍通过；**无任何连带失败** → 证明新测试确实测到了落位，不是空测 |
| 批次 1 全量 | 前端全量 | **88 文件 / 638 passed / 2 failed** |
| 全量失败复跑 | 2 个失败文件，加 `--testTimeout=30000` | **19 passed 全绿**（`ContactMeasurementSetupWorkspace` 耗时从 8769ms 降到 1544ms） |

负向验证后已还原，并 grep 确认无残留标记。

### 6.1 全量那 2 个失败的判定（**证据强度请审核者自行评估**）

失败用例：
- `ContactMeasurementSetupWorkspace > disables Add row at the 256-category limit`（5000ms 超时）
- `ReportWorkspace > recovers real progress above the disabled generation button`（等 "19 seconds elapsed" 计时文本）

判定为**主机时序/性能敏感，非本批回归**，依据两条：

1. **静态**：两个模块的依赖图**都到不了** `TopBarActionsContext` / `AppShell` / `TopBar`（逐行核对 import；`ReportWorkspace` 的 DOM 里根本没有 AppShell/TopBar）。
2. **经验**：加长超时后全绿，且耗时大幅下降，符合主机负载特征。

> ⚠️ **诚实披露**：我原计划用 `git stash` 建"改动前基线"来直接证明这 2 个失败是既有的——**该实验失败了**（见第 7 节）。所以第 2 条证据目前只有"加长超时即通过"，**没有"改动前也失败"的直接对照**。如果审核者认为这个缺口重要，需要补一次基线实验（建议用 `git worktree` 或临时 clone，**不要再用 stash**）。

---

## 7. ⚠️ 事故与修复：`git stash` 段错误导致对象库受损

这一节必须完整呈现，因为它直接影响"本次改动是否可信"。

### 7.1 发生了什么

为做上述基线实验，执行：

```
git stash push -u -m "batch1-wip-verify" -- frontend/src
```

**该命令段错误崩溃**（`Segmentation fault`）。此后 `git status` / `git diff --cached` 全部 `fatal: bad object HEAD`（退出码 128）。

### 7.2 首要确认：工作区未受损

改动前后对 8 个文件做 sha256 指纹比对，**全部 SAME**——stash 崩在"创建 stash commit"阶段，还没走到回滚工作区那一步。

### 7.3 受损范围（实测）

| 项目 | 状态 |
|---|---|
| 工作区文件 | ✅ 完好（sha256 逐一比对 SAME） |
| `HEAD` = `68b1dbb1` 及其约 10 个祖先提交对象 | ❌ 既不在 44 个 pack 中，也不在松散对象里 |
| pack / idx 文件 | ✅ 44 组**完全配对、无文件被删除** |
| 崩溃残留 | 0 字节 `.git/index.lock`、1 个孤儿 tree 对象 |

### 7.4 因果判断（两种解释都列出，不替自己开脱）

**对我方不利的证据**：`git status` 在 21:13:50 还正常（并写回 4.4MB index），崩溃后即失效；窗口里只有我这条 stash。

**指向"外部早已损坏"的证据**：
- `git stash` 的代码路径**不删除对象**；packs 完好。
- `gc.auto` 未设（默认 6700），而松散对象仅 27 个 → **不可能触发 auto-gc**。
- **35/44 个 pack 的 `.pack` mtime 远新于其 `.idx`**（偏差 11 分钟 ~ 79 天），多个 pack 共享同一毫秒写入时刻，另有 2026-07-01 遗留的 `.mtimes` 文件 → 这是**外部批量拷贝/还原**的痕迹，不是 git 自身会产生的状态。
- 损坏横跨约 10 个提交、两天时间。

**结论**：更可能是"对象库早已被外部操作损坏，`stash` 只是本会话第一个真正需要读这些 commit 对象的命令，撞上后崩溃"。但**无法从磁盘证据完全判定**，两种解释都不排除。

### 7.5 修复动作与验证

1. **`git fetch --refetch origin`**（后台，30 分 39 秒）。
   - 关键：本地 `master` 与 `origin/master` **都指向 `68b1dbb1`**，普通 `git fetch` 会协商"我已有该对象"而**什么都不下载**，必须用 `--refetch`。
   - **退出码 1**，但失败点在末尾 maintenance 步骤（`failed to perform geometric repack`，根因是 4 个 codex 断链引用）——**数据接收本身成功**。
2. **后续挖出并修复两处此前未察觉的残留**：
   - **缺失 blob `95ad1115` = 正是批次 0 暂存的 `frontend/src/components/layout/TopBar.test.tsx`**。index 记着这个 blob，对象库里没有（`git ls-files -s` 有它、`cat-file -e` 失败）→ **这种状态会导致提交失败**。
     - 陷阱：**`git add <file>` 是空操作**（index stat 缓存判定"未变更"，git 跳过 blob 写入；实测 add 后 `cat-file -e` 仍失败）。
     - 正解：`git hash-object -w <file>` → 写入 1254 字节，与工作区文件**逐字节一致**（`Buffer.compare === 0`），零数据损失。
   - **`invalid sha1 pointer in cache-tree of .git/index`（tree `3124e0e9`）**：`git write-tree` 直接把该 tree 物化出来（返回值就是 `3124e0e9`），fsck 报错随即归零。**不能用 `git read-tree HEAD` 修**——会丢掉已暂存条目。
3. **删除崩溃遗留的 0 字节 `.git/index.lock`**（mtime 21:15:09）：删前用 `Get-Process` 确认无 git/ssh 进程持有；git 自身报错信息即指示"remove the file manually to continue"。删后 `git add -n` 从 exit 128 恢复正常。

### 7.6 修复后的最终校验

| 校验项 | 结果 |
|---|---|
| reflog 全部提交（542 个 sha）经单进程 `git cat-file --batch-check` | **readable = 542 / MISSING = 0** |
| `git cat-file -t 68b1dbb1` | `commit` ✅ |
| `git log -3` | `68b1dbb1` / `46a9812a` / `c8970d12` 全部可读 ✅ |
| `git rev-list --objects HEAD` | 成功，**20217 个对象**，无 stderr |
| `git status` / `git diff --stat` | 退出码 0；diff 正确输出本批 **7 files, +86/−45** |
| `git fsck --connectivity-only` | **`missing = 0`**、`invalid sha1 pointer = 4`（全部是 codex 断链引用）、`dangling = 4024`（`--refetch` 的正常副产物，无害） |
| 8 个改动文件 sha256 | **全部 SAME**（修复前后一致） |

**唯一遗留问题**：4 个 `refs/codex/turn-diffs/checkpoints/**` 引用指向本地与远端**都不存在**的对象（`2cacffa3` / `5ab72228` / `7f768c63` / `dc68c1ef`）。它们使 `git gc` / repack 持续失败（**不影响** add/commit/push/fetch 的数据传输）。属**不可恢复的孤立引用**，清理方式 `git update-ref -d <refname>`——**尚未执行，等用户授权**。

---

## 8. 待审核的实际工作区状态

```
$ git status --porcelain -- frontend/src
 M frontend/src/components/layout/AppShell.tsx
A  frontend/src/components/layout/TopBar.test.tsx
 M frontend/src/components/layout/TopBar.tsx
 M frontend/src/features/project-workbench/ProjectWorkbenchExecutionConsole.tsx
 M frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx
 M frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx
 M frontend/src/pages/ProjectListPage.test.tsx
 M frontend/src/pages/ProjectListPage.tsx
?? frontend/src/components/layout/TopBarActionsContext.tsx
```

- `A ` = 批次 0 时 `git add` 的 `TopBar.test.tsx`（此前一直 untracked）
- `??` = 新增的 Context 文件，**尚未 add**
- 其余 7 个为已跟踪文件的修改
- **全部未提交**。工作区另有 84 个 `docs/` 下的未跟踪中间产物（历史遗留，与本批无关）

---

## 9. 请审核者重点判断的问题

1. **API 删除是否可接受**：`AppShell` 的 `topBarActions?: ReactNode` prop 被删除。仓库内零调用方，但这是导出组件的公开 prop。是"收敛为一条通道"的正确做法，还是应当保留为兼容层？
2. **Context 设计是否正确**：回调 ref + provider state（而非消费者读共享 ref）。是否还有其他风险场景——例如同页多个 `TopBar`、Provider 外再套 Provider、`AppShell` 重渲染时的注册抖动？
3. **`TopBar` 的 `useTopBarHostRegistration()` 可能返回 `null`**（无 Provider 时的独立渲染）。此时 `ref={null}`——是否需要在无 Provider 时给出更明确的语义或开发期告警？
4. **全量测试那 2 个失败的判定**：目前只有"静态依赖隔离 + 加长超时即通过"两条证据，**缺"改动前也失败"的直接对照**（基线实验因 stash 崩溃而失败）。是否接受该判定？若不接受，建议补基线实验的方式。
5. **`useMemo` 的 value 是否必要**：`{ host, registerHost }` 每次 host 变化都会新建对象；消费者仅读 `host`，是否有更优写法（如拆成两个 context，或让注册函数读 ref）？
6. **是否遗漏了后续清理**：仓库内有两个**全库无引用**的 folder 相关组件——`OfficialWorkspaceActionPanel.tsx`（内含**另一份 "Create project folder" 实现**）与 `ProjectFolderCreationPanel.tsx`（测试里仍在 mock 它）。是否应在本批或批次 2 一并清理，以免出现第三个同名入口？

---

## 10. 未实施 / 待决策（不在本次审核范围，供上下文）

**批次 2：把 "Create project folder" 迁入 Folder Actions 卡片**，方案文档：`docs/workbench_topbar_actions_and_folder_create_migration_plan.md`。三个待决策点：

- **D1 落在哪个面**：做成一条 task 行（`ProjectFolderTaskActionTarget` 已预留 `"folder"`，`ProjectWorkbenchLayout.tsx:385` 的 handler 分支早就接好，只需让 `deriveProjectFolderTasks` 产出该 key → 复用既有 blocker 机制、无需新 prop/CSS，但位置是列表行不是角标），还是塞卡片 header 右上角（符合原意，代价是新 prop + 新 CSS + 两处调用点）。**推荐先做 A**。
- **D2 主按钮权重**：移走后命令栏只剩次级按钮，唯一主按钮是否交给 Folder Actions 卡片？若是，`.is-primary` 当前只作用于 `.runtime-console-commandbar-actions button`，选择器需放宽。
- **D3 可达性**：卡片在 `sideColumnAfter` 里，无 Matrix 模式下位于空状态内部，`readonly_archive` 下位置又不同；首行原本常驻，挪进卡片后窄屏可能滑出视口。

另需注意 **F2**（按钮 label 被硬编码忽略，`"Update project folder"` 永不出现）——这是既有缺陷，若批次 2 要改名，应复用既有 `label` 字段而不是再加字面量。

---

## 附：本报告的证据文件位置

| 内容 | 路径 |
|---|---|
| 本批完整 diff | `tmp/report_diff.txt`（315 行，含 CRLF 警告行） |
| 批次 0 测试日志 | `tmp/vitest_batch0.log` |
| 批次 1 定向测试日志 | `tmp/vitest_batch1.log` |
| 负向验证日志 | `tmp/vitest_redcheck.log` / `tmp/vitest_redcheck_summary.txt` |
| 全量测试日志与汇总 | `tmp/vitest_batch1_full.log` / `tmp/vitest_batch1_full_summary.txt` |
| 全量失败复跑（长超时） | `tmp/vitest_isolated2_long.log` |
| 改动文件 sha256 基线 / 比对 | `tmp/batch1_hashes_before.json` / `tmp/batch1_integrity.txt` |
| 仓库损坏探查记录 | `tmp/git_damage_probe.txt`、`tmp/git_probe2.txt`~`git_probe4.txt`、`tmp/pack_skew.txt`、`tmp/loose_objects.txt` |
| 修复与最终校验 | `tmp/git_fetch_repair.log`、`tmp/repair_verify2.txt`、`tmp/ref_audit.txt`、`tmp/fsck_final.txt`、`tmp/git_fsck3.log` |
| 方案文档（批次 1 设计 + 批次 2 三决策点） | `docs/workbench_topbar_actions_and_folder_create_migration_plan.md` |
