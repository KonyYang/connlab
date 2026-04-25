# ConnLab Codex Starter Pack v1.0

This package is designed to be copied into the root of a new ConnLab repository and used as persistent context for Codex / IDE AI coding agents.

Recommended usage:

```bash
mkdir connlab
cd connlab
git init
# copy all files from this package here
codex
```

Then give Codex one task at a time, for example:

```text
Read AGENTS.md and implement tasks/TASK_001_REPOSITORY_SCAFFOLD.md only. Do not implement anything outside the task.
```

Important rule: do not ask Codex to build the whole system at once. The MVP must advance by small, reviewable tasks.
