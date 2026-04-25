# ConnLab Code Review Checklist

Before accepting Codex/AI generated code, check:

- [ ] It only implements the assigned task.
- [ ] It does not implement future scope.
- [ ] It follows the backend layer structure.
- [ ] API route logic is thin.
- [ ] Business logic is in application/modules, not routes/UI.
- [ ] No direct Office COM access outside infrastructure gateway.
- [ ] Domain layer has no infrastructure imports.
- [ ] Files are reasonably small.
- [ ] Tests are added or updated.
- [ ] Error messages are clear.
- [ ] No hardcoded personal paths.
- [ ] No silent exception swallowing.
