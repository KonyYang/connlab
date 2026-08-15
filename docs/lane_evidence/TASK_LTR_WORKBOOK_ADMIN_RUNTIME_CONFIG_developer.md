# TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG Developer Evidence

TASK_ID: TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG
ROLE: Developer
STATUS: ready
SUBJECT: ff01fb1d725c98fb58a3e343cf241076853e8cfa
MODEL: gpt-5.6-sol
REASONING_EFFORT: medium
MODEL_ROUTE_REASON: risk:authority
ACTION_ID: 045bd2dd4567cc617b5250491178abe4bb6f89c25d15336ca871a732999b5695
ATTEMPT: 1
NEXT: Reviewer
BLOCKER: none

## Result

- Added the administrator-only runtime contract `connlab.admin.toml` with a committed secret-free `connlab.admin.example.toml` template.
- Development resolves the administrator file from `CONNLAB_ADMIN_CONFIG_PATH` or `<base_dir>\connlab.admin.toml`.
- Packaged runtime defaults to `%PROGRAMDATA%\ConnLab\config\connlab.admin.toml` through presence-preserving environment setup and does not create or mutate the file.
- `CONNLAB_LTR_WORKBOOK_PASSWORD` remains the highest-precedence source, including an explicitly present blank value.
- The legacy local-file password is inert while unrelated local settings continue to load.
- Removed the ordinary Settings password UI/client/API/write-service chain; existing workbook consumers and redacted summary behavior remain unchanged.
- Both release scripts ship only `config\connlab.admin.example.toml`.

## TDD And Validation

- Configuration slice: RED `3 failed / 9 passed`; GREEN `12 passed`.
- Packaged runtime slice: RED `1 failed / 3 passed`; GREEN `4 passed` after isolating environment state.
- API removal: RED because GET returned `200`; GREEN `1 passed` after unregistering and deleting the password-only route/service.
- Packaging slice: RED `2 failed / 13 passed`; GREEN in the final approved matrix.
- Complete approved backend and packaging matrix: `62 passed`.
- Focused Settings Vitest: `2 files / 4 tests passed`.
- Frontend production build: passed for 134 modules; existing non-blocking 569.61 kB chunk-size advisory only.
- `py_compile`: all 8 touched surviving Python files passed.
- `git diff --check`: passed.
- Exact implementation scope: all and only the approved 25 product/test paths, including three planned deletions and three planned creations.
- Deleted production, UI, and typed-client references are absent; the removed API path remains only in the negative integration assertion.
- `connlab.admin.toml` is ignored and untracked.
- Tracked TOML password assignments contain exactly one blank placeholder in the administrator example.

## Git And Safety

- Implementation subject: `ff01fb1d725c98fb58a3e343cf241076853e8cfa`.
- Task branch/worktree is clean at the exact subject.
- No role evidence or board file was written on the task branch.
- No real password, real ProgramData file, public-drive workbook, installed release, or external configuration was read, printed, created, changed, copied, or deleted.
- No push, cleanup, archive, retire, reset, restore, stash, rebase, cherry-pick, force update, branch/worktree movement, or resource deletion occurred.
