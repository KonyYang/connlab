# ConnLab 自动修复 Skill 用户指南（行动版）

本指南用于指导你在 **不会编程 / 不熟悉代码细节** 的情况下，
依然可以安全、高效地使用 AI 完成开发。

---

# 🎯 你的核心目标

你不是在写代码，而是在执行：

```text
AI 写代码 → 自动测试 → 自动修复 → 稳定通过
```

---

# 🧠 你只需要记住 4 个命令

```powershell
.\scripts\run_task.ps1 TASK_XXX
.\scripts\run_tests.ps1
.\scripts\fix_tests.ps1 TASK_XXX
.\scripts\dev_cycle.ps1 TASK_XXX
```

---

# 📁 一、你必须具备的文件结构

确保项目里有：

```text
connlab/
├── AGENTS.md
├── docs/project_management/TASK_EXECUTION_SKILL.md
├── docs/project_management/TESTING_SKILL.md
├── docs/skills_guides/AUTO_FIX_SKILL.md
├── tasks/
├── tests/
├── logs/
├── scripts/
│   ├── run_task.ps1
│   ├── run_tests.ps1
│   ├── fix_tests.ps1
│   └── dev_cycle.ps1
```

---

# ⚡ 二、最快捷用法

如果你想让 Codex CLI 自动完成一轮：

```powershell
.\scripts\dev_cycle.ps1 TASK_002_CONFIG_LOGGING
```

它会按以下顺序执行：

```text
run_task
→ run_tests
→ 如果失败 → fix_tests
→ run_tests
→ 最多自动修复 3 次
```

注意：

- 它不会跳到下一个 Task
- 它会检查 `docs/task_board.md`，只允许执行当前 active task
- 如果任务编号不匹配，会直接停止
- 脚本会自动为外部 Codex CLI 准备独立 runtime home，避免和当前会话争用默认 `~/.codex`

---

# 🚀 三、标准操作流程（你每次都按这个来）

---

## Step 1：执行一个任务

```powershell
.\scripts\run_task.ps1 TASK_002_DATABASE
```

👉 作用：

```text
AI 根据任务写代码 + 自动生成测试
```

---

## Step 2：运行测试

```powershell
.\scripts\run_tests.ps1
```

👉 结果只有两种：

```text
✅ All tests passed → 进入下一步
❌ Tests failed → 进入 Step 3
```

---

## Step 3：自动修复

```powershell
.\scripts\fix_tests.ps1 TASK_002_DATABASE
```

👉 AI 会：

```text
读取失败日志
分析问题
只修复错误代码
```

---

## Step 4：再次测试

```powershell
.\scripts\run_tests.ps1
```

---

# 🔁 四、循环规则（非常重要）

```text
run_task
→ run_tests
→ 如果失败 → fix_tests
→ run_tests
→ 通过
```

👉 最多重复 3 次！

---

# 🧪 五、你如何判断“可以继续”

你不需要看懂代码，只检查这 3 件事：

---

## ✅ 1. 测试是否通过

```text
看到：
✅ All tests passed
```

---

## ✅ 2. AI 是否乱改

简单看：

```text
是否修改了很多无关文件？
是否新增奇怪功能？
```

如果是 → 停止

---

## ✅ 3. 是否提前实现未来功能

```text
❌ 不允许出现：
Matrix
Report
AI自动分析
复杂UI
```

---

# 💾 六、通过后必须做

```powershell
git add .
git commit -m "feat: complete TASK_002_DATABASE"
```

👉 这是你的“安全点”

---

# 🚨 七、失败处理规则（非常关键）

---

## ❌ 情况 1：修复 3 次仍失败

你停止操作，然后准备这 3 个内容：

```text
1. 当前 Task 文件
2. logs/pytest_last.log
3. AI 修改的代码
```

👉 发给专家（或我）

---

## ❌ 情况 2：AI 开始乱写

表现：

```text
改很多文件
写不相关功能
代码越来越复杂
```

👉 立刻停止！

---

# 🧱 八、绝对禁止的行为

```text
❌ 一次执行多个 Task
❌ 手动改大量代码
❌ 删除测试让它“通过”
❌ 跳过测试
❌ 修改 AGENTS.md（除非你明确知道）
```

---

# 🧠 九、你现在的角色

你不是程序员，你是：

```text
AI 工程管理者
```

你的工作是：

```text
给任务
跑测试
看结果
决定是否继续
```

---

# 🏁 十、你的每日操作模板

复制这一段，每天照做👇

---

## 今日开发步骤

```text
1. 选择一个 TASK
2. 优先使用 dev_cycle
3. 如果需要手动控制，再分别 run_task / run_tests / fix_tests
4. 成功 → commit
5. 下一个 TASK
```

---

# 📌 十一、一句话总结

> ❗你不用理解代码，只需要让“测试通过 + 不乱扩展”

---

# 👍 十二、当你卡住时

直接说：

```text
我在 TASK_XXX 卡住
pytest 日志如下：
...
```

👉 可以快速帮你定位问题

---

# 🎉 最终效果

做到这一点，你将实现：

```text
不会编程 → 也能稳定开发系统
```
