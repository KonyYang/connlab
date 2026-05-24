# ConnLab 项目深度评估与前端状态管理改进方案

> Task: 深度评估 + 前端状态持久化方案设计  
> Date: 2026-05-03  
> Scope: 仅分析与方案设计，无运行时代码变更

## 1. 分析范围

本文档整合两部分内容：

1. **项目整体深度评估**：架构、代码质量、可维护性、测试覆盖
2. **Intake 界面状态持久化方案**：解决页面切换/浏览器刷新时状态丢失的核心痛点

---

## 2. 项目总体概况

| 维度 | 数据 |
|------|------|
| 项目阶段 | Phase 10A 完成，待进入下一阶段 |
| 后端 Python 文件 | 92 个（api/application/domain/infrastructure/modules） |
| 前端 TypeScript 文件 | 44 个（pages/components/api） |
| 测试文件 | 75 个，245+ 测试通过 |
| 前端技术栈 | React 19 + TypeScript + Vite（无 Router/状态库） |
| 后端技术栈 | FastAPI + SQLAlchemy 2 + Pydantic v2 + SQLite |

---

## 3. 项目优点

### 3.1 架构层次清晰

严格的六层架构（domain → application → infrastructure → modules → api → frontend），依赖方向完全遵守「上层依赖下层」原则。Office 操作全部隐藏在 `infrastructure/office/` 门面类后，API 层保持瘦身。

### 3.2 测试覆盖率高

75 个测试文件，245+ 测试通过。每个功能模块都有对应的 unit + integration 测试，同类项目罕见的测试水平。

### 3.3 文档体系完善

- `AGENTS.md` — AI 编码规则
- `task_board.md` — 项目执行看板
- `02_ARCHITECTURE_RULES.md` — 架构约束
- `frontend_architecture_rules.md` — 前端边界
- 每个 Phase 有 validation summary

### 3.4 严格的 MVP 范围控制

明确禁止 Matrix、Report、AI review、权限管理、LAN 部署等未来范围，这在 AI 驱动开发的项目中极其难得。

### 3.5 文件大小控制较好

大部分后端 Python 文件在 100-300 行之间，符合「目标 ≤300，硬限制 ≤500」的要求。

---

## 4. 核心待改进问题

### 4.1 [P0] 前端路由手动实现，脆弱且不可维护

**现状：** `App.tsx` 使用 `window.history.pushState` + `window.dispatchEvent(PopStateEvent)` + `pathname.match()` 手动实现路由。路由解析、导航、状态同步全部手写。

**风险：**
- 没有类型安全的路由参数（`packageId` 是 `match[1]` 字符串）
- 不支持嵌套路由和路由守卫（如"未确认 Intake 不能跳转到 Precheck"）
- 未来增加页面（如 Precheck 独立页、Folder 页）会越来越复杂

**建议：** 引入 React Router v7（兼容性最广，不用大改组件）：
```bash
npm install react-router-dom
```

路由改为声明式：
```tsx
<Routes>
  <Route path="/" element={<ProjectListPage />} />
  <Route path="/intake" element={<IntakeInboxPage />} />
  <Route path="/intake/:packageId/case-review" element={<IntakeCaseReviewPage />} />
</Routes>
```

接入成本低，约 30 分钟，长期收益巨大。

---

### 4.2 [P0] Intake Session 状态无持久化 — 刷新丢失、页面切换丢失

**这是本轮的核心关注点。详见第 5 节。**

---

### 4.3 [P0] Session 状态通过 Props 手动传递，产生 Prop Drilling

**现状：** `IntakeSessionState` 定义在 `IntakeInboxPage.tsx` 中，由 `App.tsx` 通过 `useState` 持有，再作为 props 传入所有子页面。子组件修改 session 必须通过 `onSessionChange` 回调层层上抛。

**影响：**
- `IntakePackageDetailPage`（第 93-99 行）**没有接收 session prop**，只能自行从 API 重新加载
- 未来增加子路由（如 Intake → Precheck → LTR 流程）需要更多层 props 传递
- Sidebar 等非 Page 组件无法访问 session

**建议：** 使用 React Context 或 Zustand（比 Redux 轻量得多）：
```tsx
// 安装 zustand: npm install zustand
const useIntakeSession = create<IntakeSessionState & {
  setPackage: (pkg: IntakePackageImport) => void;
  setSelectedAsset: (id: string) => void;
  clearSession: () => void;
}>((set) => ({
  ...EMPTY_INTAKE_SESSION,
  setPackage: (pkg) => set({ packageImport: pkg }),
  setSelectedAsset: (id) => set({ selectedAssetId: id }),
  clearSession: () => set(EMPTY_INTAKE_SESSION),
}));
```

---

### 4.4 [P1] routes_intake.py 超过 500 行硬限制

**现状：** `backend/api/routes_intake.py` 共 707 行，其中大量 Response DTO 定义与 route handler 混在同一个文件中。

**建议：** 将 DTO 类提取到独立文件（如 `api/responses/intake.py`），只保留 route handler + response 转换函数。可立即降低到 300 行以内。

---

### 4.5 [P1] 大页面文件需拆分

| 文件 | 大小 | 问题 |
|------|------|------|
| `IntakeCaseReviewPage.tsx` | ~23 KB | 大页面，超过合理组件大小 |
| `IntakeInboxPage.tsx` | ~19 KB | 同上 |
| `client.ts` | 689 行 | 类型定义 + API 函数混在一起 |

**建议：** 按 `frontend_architecture_rules.md` 中已规划的 `features/` 目录结构拆分：
```
features/
  intake/
    IntakeCaseReviewPage.tsx     # 仅页面编排（约50行）
    intakeCaseReviewState.ts     # 状态提取
    ProjectFieldsSection.tsx     # 字段编辑区
    SampleTableSection.tsx       # Sample 表格区
    DispositionSection.tsx       # 处理方式区
```

---

### 4.6 [P1] 前端无测试覆盖

**现状：** `tests/unit/test_frontend_shell_files.py` 仅检查文件是否存在（~22 个断言）。没有 React 组件测试、没有页面交互测试、没有 API 调用模拟测试。

**风险：** 未来 UI 改动的回归风险完全靠手动验证。没有组件级保护。

**建议：** 添加 Vitest + @testing-library/react（和 Vite 生态一致）：
```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

写 2-3 个关键组件的测试覆盖核心交互（如 IntakeInboxPage 的文件选取流程、CaseReviewPage 的字段编辑保存），不用追求全覆盖，但核心流程必须有。

---

### 4.7 [P2] CSS 全局作用域，无隔离

**现状：** 6 个全局 CSS 文件（`styles.css`、`workbench.css`、`intake-inbox.css` 等），所有样式全局作用域，类名靠人工避免冲突。

**风险：**
- 不同页面的同名类名可能冲突
- 修改一个文件可能影响其他页面
- 难以实现主题切换

**建议（逐步引入）：**
- 方案 A（最小改动）：每页使用唯一前缀（如已做的 `.precheck-*` 规范）
- 方案 B（推荐）：对**新组件**使用 CSS Modules（`.module.css`），Vite 原生支持，不需要额外配置
- 方案 C（未来）：对**新功能**使用 Tailwind CSS，但需要评估学习成本

---

### 4.8 [P3] Lookup 选项管理缺乏操作界面

**现状：** `lookup_options_service.py` 中的默认值（Business Unit 有 40+ 个值、Mfg Site 有 80+ 个值）是硬编码在 Python 代码中。如果想要增删改，需要改代码再部署。

**建议（远期）：**
- 后端新增 CRUD API（`POST /api/lookups/{group_key}` 添加选项）
- 前端新增管理页面或管理员面板
- 开发优先级：低（日常运营可以通过直接操作数据库实现）

---

### 4.9 [P3] 前端无国际化准备

**现状：** 所有 UI 文字都是英文硬编码。虽然有 Chinese UI 的 WCAG 要求（`PRODUCT.md`），但没有 i18n 框架支持。

**建议（远期）：**
- 使用 `react-intl`（FormatJS）或简单自定义 hook
- 定义 `locales/zh-CN.json` 和 `locales/en.json`
- 开发优先级：低（当前用户群体英文 OK）

---

## 5. Intake Session 状态持久化方案（核心议题）

### 5.1 问题根因分析

当前 `App.tsx` 第 56-57 行的状态管理：

```tsx
const [intakeSession, setIntakeSession] =
  useState<IntakeSessionState>(EMPTY_INTAKE_SESSION);
```

**状态丢失的 3 个场景：**

| 场景 | 根因 | 影响程度 |
|------|------|---------|
| **F5 刷新网页** | `useState` 存储在内存中，刷新即清空 | 🔴 严重 |
| **切换 UI 页面** | 取决于路由：`IntakePackageDetailPage` 未接收 session prop，需自行从 API 加载 | 🟡 中等 |
| **Back/前进** | 同 UI 页面间切换，state 保留在 App 组件中 | ✅ 正常 |

**当前状态流向图：**

```
App.tsx 持有 intakeSession (useState)
   │
   ├──→ IntakeInboxPage ✅ 接收 session + onSessionChange
   │
   ├──→ IntakePackageDetailPage ❌ 未接收 session（自行从 API 加载）
   │
   ├──→ IntakeCaseReviewPage ⚠️ 仅接收 packageId + initialCaseId
   │
   └──→ ProjectWorkbenchPage ✅ 从 API 加载，无 session 问题
```

### 5.2 设计原则

> **"没有导入新的 msg 或申请单，还在当前任务时就不应该清空。"**

| 存储方案 | 刷新网页 | 关闭标签页 | 手动清除 |
|----------|---------|-----------|---------|
| `useState` | ❌ 丢失 | ❌ 丢失 | — |
| `sessionStorage` | ✅ 恢复 | ❌ 自动清空 | ✅ 代码清除 |
| `localStorage` | ✅ 恢复 | ✅ 保留 | ❌ 永久保留 |

**选择 `sessionStorage`** 的原因：关闭标签页自动清空，符合「当前任务生命周期」语义；刷新页面自动恢复，符合「页面刷新不丢数据」需求。

---

### 5.3 方案 A（推荐，最小改动）：sessionStorage 持久化

仅修改 `App.tsx` 约 5-8 行代码 + 新建一个工具文件，**0 依赖新增**。

**Step 1：** 新建 `frontend/src/utils/sessionStore.ts`

```ts
import {
  type IntakeSessionState,
  EMPTY_INTAKE_SESSION,
} from "../pages/IntakeInboxPage";

const STORAGE_KEY = "connlab_intake_session";

export function loadIntakeSession(): IntakeSessionState {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return EMPTY_INTAKE_SESSION;
    return JSON.parse(raw) as IntakeSessionState;
  } catch {
    return EMPTY_INTAKE_SESSION;
  }
}

export function saveIntakeSession(session: IntakeSessionState): void {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  } catch {
    // sessionStorage 满或不可用时静默失败
  }
}

export function clearIntakeSession(): void {
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    // 静默失败
  }
}
```

**Step 2：** 修改 `App.tsx` 的初始化逻辑

```diff
- const [intakeSession, setIntakeSession] =
-   useState<IntakeSessionState>(EMPTY_INTAKE_SESSION);
+ const [intakeSession, setIntakeSession] =
+   useState<IntakeSessionState>(loadIntakeSession);
```

**Step 3：** 添加自动同步 effect

```tsx
useEffect(() => {
  saveIntakeSession(intakeSession);
}, [intakeSession]);
```

**Step 4：** 任务完成时清除（在确认项目创建成功后）

```tsx
// 在 IntakeCaseReviewPage 的确认成功后调用
clearIntakeSession();
```

---

### 5.4 方案 B（推荐，中改动）：React Context + sessionStorage

**解决 Prop Drilling + 持久化**两个问题。新增 Context 层，所有 Intake 页面直接使用 `useIntakeSession()` hook，无需 props 传递。

新增 `frontend/src/contexts/IntakeSessionContext.tsx`：

```tsx
import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
  type ReactElement,
} from "react";
import {
  type IntakeSessionState,
  EMPTY_INTAKE_SESSION,
} from "../pages/IntakeInboxPage";
import { loadIntakeSession, saveIntakeSession, clearIntakeSession }
  from "../utils/sessionStore";

// ----- Context 类型 -----

interface IntakeSessionContextValue {
  session: IntakeSessionState;
  updateSession: (update: Partial<IntakeSessionState>) => void;
  clearSession: () => void;
}

// ----- Context 定义 -----

const IntakeSessionContext = createContext<IntakeSessionContextValue | null>(null);

// ----- Provider 组件 -----

export function IntakeSessionProvider({
  children,
}: {
  children: ReactNode;
}): ReactElement {
  const [session, setSession] = useState<IntakeSessionState>(loadIntakeSession);

  useEffect(() => {
    saveIntakeSession(session);
  }, [session]);

  const updateSession = (update: Partial<IntakeSessionState>) =>
    setSession((prev) => ({ ...prev, ...update }));

  const clearSession = () => {
    setSession(EMPTY_INTAKE_SESSION);
    clearIntakeSession();
  };

  return (
    <IntakeSessionContext.Provider value={{ session, updateSession, clearSession }}>
      {children}
    </IntakeSessionContext.Provider>
  );
}

// ----- 使用 hook -----

export function useIntakeSession(): IntakeSessionContextValue {
  const ctx = useContext(IntakeSessionContext);
  if (!ctx)
    throw new Error("useIntakeSession must be inside IntakeSessionProvider");
  return ctx;
}
```

然后在 `App.tsx` 中包裹：

```tsx
<IntakeSessionProvider>
  <AppShell ...>
    {/* 所有页面组件 */}
  </AppShell>
</IntakeSessionProvider>
```

所有页面组件中直接使用：

```tsx
// IntakeInboxPage、IntakePackageDetailPage、IntakeCaseReviewPage 通用
const { session, updateSession } = useIntakeSession();
```

---

### 5.5 方案 C（远期推荐）：Zustand + persist

最现代化方案，需安装依赖 `npm install zustand`。

新增 `frontend/src/stores/intakeSessionStore.ts`：

```ts
import { create } from "zustand";
import { persist } from "zustand/middleware";
import {
  EMPTY_INTAKE_SESSION,
  type IntakeSessionState,
} from "../pages/IntakeInboxPage";

interface IntakeSessionStore {
  session: IntakeSessionState;
  setSession: (session: IntakeSessionState) => void;
  clearSession: () => void;
}

export const useIntakeSessionStore = create<IntakeSessionStore>()(
  persist(
    (set) => ({
      session: EMPTY_INTAKE_SESSION,
      setSession: (session) => set({ session }),
      clearSession: () => set({ session: EMPTY_INTAKE_SESSION }),
    }),
    { name: "connlab-intake-session" } // 自动序列化到 localStorage
  )
);
```

使用方式——任何组件中直接调用：

```tsx
const session = useIntakeSessionStore((s) => s.session);
const setSession = useIntakeSessionStore((s) => s.setSession);
```

无需 Provider、无需 props、自动持久化。

---

### 5.6 三方案对比

| 维度 | 方案 A：sessionStorage | 方案 B：Context | 方案 C：Zustand |
|------|----------------------|----------------|----------------|
| **依赖新增** | 0 | 0 | `zustand` |
| **代码修改量** | ~15 行 | ~50 行 | ~30 行 |
| **解决刷新丢失** | ✅ | ✅ | ✅ |
| **解决 Prop Drilling** | ❌ | ✅ | ✅ |
| **可测试性** | 一般 | 较好 | 最佳 |
| **未来扩展性** | 低 | 中 | 高 |
| **迁移到其他页面复用** | 需重复编码 | 需新建 Context | 可复用 persist |

---

## 6. 推荐实施路线

| 优先级 | 任务 | 方案 | 预估工作量 |
|--------|------|------|-----------|
| **P0** | Intake Session 持久化（解决刷新丢失） | 方案 A | 0.5 天 |
| **P1** | 引入 Context 消除 Prop Drilling | 方案 B | 0.5 天 |
| **P2** | 拆分 `routes_intake.py`（DTO 分离） | — | 0.5 天 |
| **P2** | 添加 Vitest + 关键组件测试 | — | 1 天 |
| **P3** | 按 `features/` 目录拆分大页面 | — | 2 天 |
| **P4** | React Router 替换手写路由 | — | 0.5 天 |
| **P5** | 新组件使用 CSS Modules | 随新功能做 | — |

---

## 7. 不在此方案范围内

以下内容不属于本次评估与分析的范围：

- 后端架构重大调整
- Matrix、Report、AI review 等未来功能
- 权限管理、LAN 部署、多用户协作
- Outlook 收件箱自动扫描
- LTR 工作簿直接写入
- 完整的前端国际化
