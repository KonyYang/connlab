# ConnLab Task Review Checklist

在任务完成后，必须逐条检查：

---

## 🧱 架构检查

* [ ] 是否遵守 domain / application / infrastructure 分层？
* [ ] 是否有 UI 直接调用业务逻辑？
* [ ] 是否绕过 application 层？
* [ ] 是否直接操作 Office？

---

## 🎯 范围检查

* [ ] 是否只实现当前 Task？
* [ ] 是否提前实现 Matrix？
* [ ] 是否提前实现 Report？
* [ ] 是否添加额外功能？

---

## 🧠 设计检查

* [ ] 数据结构是否清晰？
* [ ] 是否可扩展？
* [ ] 是否避免重复逻辑？
* [ ] 是否有硬编码？

---

## ⚙️ 运行检查

* [ ] 是否可启动？
* [ ] 是否有异常？
* [ ] API 是否可调用？
* [ ] 输入输出是否正确？

---

## 🧹 代码质量

* [ ] 是否有类型标注？
* [ ] 是否有 docstring？
* [ ] 是否有未完成 TODO？
* [ ] 文件是否过大？

---

## 🚨 发现问题处理规则

如果发现任何问题：

→ 必须先修复
→ 不允许进入下一个 Task

## Deterministic Handoff Review

按 `ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md` 复核：证据 ref 的
commit/blob/SHA-256/status、exact lane HEAD/ancestry/clean 状态、May Touch/locks、合法事件、
一 turn 至多一次 transition/dispatch，以及 callback/capsule/read-set 字节预算。Reviewer/QA
不得凭 callback 直接授权下一角色。
