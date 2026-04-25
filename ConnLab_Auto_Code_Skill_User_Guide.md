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

# 🧠 你只需要记住 3 个命令

```powershell
.\scripts\run_task.ps1 TASK_XXX
.\scripts\run_tests.ps1
.\scripts\fix_tests.ps1 TASK_XXX
```

---

# 📁 一、你必须具备的文件结构

确保项目里有：

```text
connlab/
├── AGENTS.md
├── TASK_EXECUTION_SKILL.md
├── TESTING_SKILL.md
├── AUTO_FIX_SKILL.md
├── tasks/
├── tests/
├── logs/
├── scripts/
│   ├── run_task.ps1
│   ├── run_tests.ps1
│   └── fix_tests.ps1
```

---

# 🚀 二、标准操作流程（你每次都按这个来）

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

# 🔁 三、循环规则（非常重要）

```text
run_task
→ run_tests
→ 如果失败 → fix_tests
→ run_tests
→ 通过
```

👉 最多重复 3 次！

---

# 🧪 四、你如何判断“可以继续”

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

# 💾 五、通过后必须做

```powershell
git add .
git commit -m "feat: complete TASK_002_DATABASE"
```

👉 这是你的“安全点”

---

# 🚨 六、失败处理规则（非常关键）

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

# 🧱 七、绝对禁止的行为

```text
❌ 一次执行多个 Task
❌ 手动改大量代码
❌ 删除测试让它“通过”
❌ 跳过测试
❌ 修改 AGENTS.md（除非你明确知道）
```

---

# 🧠 八、你现在的角色

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

# 🏁 九、你的每日操作模板

复制这一段，每天照做👇

---

## 今日开发步骤

```text
1. 选择一个 TASK
2. run_task
3. run_tests
4. 如果失败 → fix_tests
5. 再 run_tests
6. 成功 → commit
7. 下一个 TASK
```

---

# 📌 十、一句话总结

> ❗你不用理解代码，只需要让“测试通过 + 不乱扩展”

---

# 👍 十一、当你卡住时

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
