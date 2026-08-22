# ConnLab Project Instructions

Keep this file small: it is loaded for every task. The User's current request defines scope. Real
code and observable behavior outrank historical plans.

## Read only what the task needs

- Inspect the relevant code and tests. Read the `docs/task_board.md` control block for repository
  changes, task status, or interruption recovery—not for unrelated explanation or advice.
- For repository changes, use the tier summary below. Read
  `docs/project_management/SOL_NATIVE_WORKFLOW.md` only for standard/high-risk execution, board
  operations, or interruption recovery.
- Read `docs/PROJECT_CONTEXT.md` when product authority, domain ownership, architecture, Office, or
  external-file behavior matters.
- For substantive UI behavior or structure, also read `PRODUCT.md`, `DESIGN.md`, `DESIGN.json`, and
  `docs/FRONTEND_GUIDE.md`. A literal/default/copy fix does not require the full design set.
- Read `docs/packaging_notes.md` only for startup, packaging, release, or runtime-path work.
- `docs/archive/**`, `docs/completed_plans/**`, `docs/lane_evidence/**`, and legacy `tasks/**/*.md` are
  history, never execution authority. Consult them only for a specifically relevant past decision.

## Efficient discovery and commands

- Start repository work with one bounded discovery batch that obtains Git status, real candidate
  paths from `rg --files`, and relevant symbol/test matches. Resolve discoverable paths before opening
  files or running path-specific commands; do not spend tool rounds guessing directory names.
- Treat Vitest/esbuild child-process spawning on this Windows Codex host as a known permission case:
  request the narrowest boundary for the complete intended command before its first run. Apply the
  same rule to pytest temporary directories, browsers, or other child processes only after the
  environment has proved the need. Do not knowingly run a setup-only `EPERM` probe; when permission
  needs are genuinely unknown, an ordinary first run remains appropriate.

## Autonomy and scope

- For explanation, diagnosis, review, or planning, inspect and report; do not implement unless asked.
- For change, build, fix, or refactor requests, make the in-scope local changes and run relevant
  non-destructive validation without routine approval pauses.
- Ask only for material scope expansion, an unresolved product choice with meaningfully different
  outcomes, new external/destructive authority, or an action that cannot be made safely reversible.
- Make ordinary technical decisions—implementation, naming, module placement, tests, and tools—using
  the current code and the smallest coherent change.
- Preserve unrelated User work. Never silently reset, restore, stash, clean, rebase, push, delete
  unrelated files, or overwrite external data.

## Durable product facts

- ConnLab is an offline, Windows-first workbench for an electronic connector laboratory.
- Project is the lifecycle and traceability container. Matrix is the authoritative test-execution map.
- Test records, reports, fee evaluation, and approval packages are derived outputs.
- Public-drive LTR workbooks and approved Word/Excel templates retain their existing business
  authority until an explicit migration changes it. SQLite does not silently replace them.
- Word and Excel are formats and external authorities where configured, not the primary domain model.
- Do not introduce future scope—AI review, multi-user permissions, LAN deployment, or new execution
  persistence—unless the current request requires it.

## Engineering rules

- Dependency direction is `frontend -> API -> application -> domain/interfaces <- infrastructure`.
- Keep domain independent of API, UI, SQLAlchemy, Office, and concrete infrastructure.
- Keep routes and UI handlers thin; place business decisions in the deepest existing module whose
  interface owns them. Prefer explicit dependencies and one state channel.
- Keep Word/Excel/Outlook and filesystem details behind infrastructure adapters. Release COM objects,
  file handles, temporary resources, and child processes deterministically.
- Preserve compatibility unless the User requests a breaking change. Do not add a framework,
  dependency, abstraction, or compatibility layer without a present need.
- Prefer cohesive modules and practical seams. Split by responsibility or change reason, not arbitrary
  line-count targets.

## Validation and completion

- Add regression protection for substantive behavior when a practical public seam exists.
- Test observable behavior, public contracts, and durable risk boundaries. Do not freeze historical
  task IDs, private symbol names, source wording, file layout, or CSS literals unless that artifact is
  itself the supported contract.
- Validate proportional to risk. After the final implementation or test byte changes, rerun affected
  validation on that exact state; old results no longer count.
- Review the exact diff for requirement fit, safety, regressions, and scope creep. Do not duplicate a
  full passing matrix without a risk-based reason.
- Finish with the outcome, exact changed paths, validation results, material findings, and residual
  risk. Omit duplicated plans, board JSON, full logs, and role ceremony.

## Task tiers

- **Micro:** localized and unambiguous; Sol implements, self-reviews, and runs targeted validation.
- **Standard:** substantive but not high risk; one Sol work unit plans, implements, self-reviews, and
  runs targeted feedback checks; one focused review follows, then QA runs the complete matrix once.
- **High risk:** database/schema migration, permissions/security, authoritative external mutation,
  destructive work, broad architecture change, or unresolved product choice; use independent
  Planner, Developer, Reviewer, QA, and Integrator contexts with automatic handoffs.

Do not request routine Plan approval. The normal User interactions are the request and final `关闭`.
Use `scripts/connlab_sol_task.py` as the sole board writer; persist only useful recovery checkpoints.
